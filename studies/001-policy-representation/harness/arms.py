"""Prompt construction and output parsing for study 001 arms A and A-prime.

WHAT THIS FILE DOES
-------------------
* Renders the **one** canonical, gold-redacted facts document that every arm
  receives, byte for byte (``canonical_facts_json``). Arm B hands the same bytes
  to the judgment-pack runtime; arms A and A-prime embed the same bytes in a
  prompt. If the two ever diverge the study is confounded, so there is exactly
  one renderer and both call sites use it.
* ``build_prompt_A``      : the RuleArena CBA policy text, verbatim, + the facts.
* ``build_prompt_Aprime`` : the judgment pack's semantic content rendered as
                            prose, + the identical facts.
* States the shared output contract --- a strict JSON object
  ``{"decision", "cited_rules", "reason"}`` and nothing else --- once, so both
  prompts are asked for exactly the same thing.
* ``parse_prediction``    : a tolerant-but-strict parser. Tolerant about
                            packaging (code fences, a prose preamble, trailing
                            chatter); strict about shape. Anything it cannot
                            parse is reported as a parse failure and is never
                            coerced into a decision.
* ``rule_catalog_from_rulearena`` : extracts the 61 rule identifiers and their
                            descriptions from RuleArena's read-only
                            ``micro_evaluation.py`` so that both prompt arms are
                            told the citation vocabulary the gold
                            ``relevant_rules`` field is drawn from. Without this
                            the citation metric would be measuring the model's
                            ability to guess RuleArena's internal naming, not its
                            ability to identify the governing rules.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
* No arithmetic and no fact derivation. Derived quantities arrive precomputed in
  ``facts.derived`` from the published preprocessor; the prompts present them and
  say so.
* No arm B. Arm B is not a prompt --- see ``arm_b.py``.
* No repair of malformed model output: no "extract the first legal/illegal word
  you can find" fallback, no defaulting of missing keys. A response that does not
  satisfy the contract is a parse failure, full stop.
* No hidden leniency knobs: the accepted shape is fixed and documented below.
* No model-side structured-output enforcement (that lives in ``backends.py`` and
  is deliberately unused).

THE ACCEPTED RESPONSE SHAPE
---------------------------
A single JSON object with exactly these semantics:

    decision     : one of "legal", "illegal", "cannot_decide"   (required)
    cited_rules  : JSON array whose every element is a string   (required)
    reason       : string                                       (required)

Extra keys are permitted and preserved under ``prediction["extra"]``; they do not
affect scoring. Everything else --- a missing key, a null, a non-list
``cited_rules``, a non-string element, an out-of-vocabulary ``decision`` --- is a
parse failure with a machine-readable reason code.

The one documented leniency about *placement*: the parser takes the first
balanced ``{...}`` span anywhere in the response, which is what lets a fenced or
prose-wrapped object through. A response like ``[{...}]`` is therefore judged on
the inner object's shape rather than rejected for being wrapped in an array.
Shape is never relaxed.

Python 3.10+ (``from __future__ import annotations`` keeps it importable on 3.8).
Standard library only.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

__all__ = [
    "DECISIONS",
    "OUTPUT_CONTRACT",
    "SYSTEM_PROMPT",
    "DEFAULT_RENDER_POLICY",
    "apply_render_policy",
    "instance_key",
    "redact_gold",
    "canonical_facts_json",
    "facts_sha256",
    "build_prompt_A",
    "build_prompt_Aprime",
    "parse_prediction",
    "ParseResult",
    "rule_catalog_from_rulearena",
    "load_rule_catalog",
    "merge_rule_vocabulary",
    "prompt_sha256",
]

DECISIONS = ("legal", "illegal", "cannot_decide")

SYSTEM_PROMPT = (
    "You are an expert analyst applying a written policy to a fully specified set "
    "of facts. You answer only from the policy text and the facts you are given. "
    "You never invent facts, and you never perform arithmetic that the facts "
    "document has not already done for you."
)

OUTPUT_CONTRACT = """OUTPUT CONTRACT (identical for every condition in this study)

Reply with a single JSON object and nothing else. No preamble, no explanation
outside the object, no markdown prose around it.

{
  "decision": "legal" | "illegal" | "cannot_decide",
  "cited_rules": ["<rule identifier>", ...],
  "reason": "<one or two sentences>"
}

Field meanings:
* "decision" is "illegal" if ANY operation in the scenario violates the policy,
  "legal" if no operation violates it, and "cannot_decide" if the policy or the
  facts you were given are insufficient to determine the answer. Choose
  "cannot_decide" only when you genuinely cannot decide; guessing and abstaining
  are both scored, and abstaining on a decidable instance counts against you.
* "cited_rules" lists the identifiers of the rules that govern this scenario,
  drawn from the rule identifier vocabulary given above. List every rule you
  actually relied on and no others.
* "reason" is a short justification. Keep it to one or two sentences."""

_FACTS_PREAMBLE = """FACTS

The facts below are the complete, authoritative description of the scenario. They
are supplied as a JSON document; every value is addressable by RFC 6901 JSON
Pointer. Monetary and numeric quantities are given as decimal STRINGS, not JSON
numbers; compare them as numbers.

The object at "facts/derived" holds quantities that have already been computed
for you by a deterministic preprocessor (for example, post-transaction team
salaries and their relation to the cap and apron thresholds). Use those values as
given. Do not recompute them, and do not second-guess them: the study is about
policy interpretation, not arithmetic."""


# --------------------------------------------------------------------------- #
# The one canonical facts rendering
# --------------------------------------------------------------------------- #


#: Applied when a document declares no ``render_policy`` of its own. It is the
#: subset of ``redact.py``'s policy that is a leak under any circumstances: the
#: answer itself, and the provenance block that carries RuleArena's original
#: prose verbatim.
DEFAULT_RENDER_POLICY: Dict[str, List[str]] = {
    "excluded_pointer_prefixes": ["/gold", "/provenance"],
    "excluded_pointer_globs": [],
}


def _glob_to_re(glob: str) -> re.Pattern:
    parts = [re.escape(seg) if seg != "*" else r"[^/]*" for seg in glob.split("/")]
    return re.compile("^" + "/".join(parts) + "(/.*)?$")


def _prune(node: Any, prefix: str, excluded: Sequence[str],
           globs: Sequence[re.Pattern]) -> Any:
    """Recursively drop every member whose RFC 6901 pointer the policy excludes."""
    def blocked(pointer: str) -> bool:
        if any(pointer == p or pointer.startswith(p + "/") for p in excluded):
            return True
        return any(g.match(pointer) for g in globs)

    if isinstance(node, dict):
        out: Dict[str, Any] = {}
        for key in node:
            child = prefix + "/" + str(key).replace("~", "~0").replace("/", "~1")
            if blocked(child):
                continue
            out[key] = _prune(node[key], child, excluded, globs)
        return out
    if isinstance(node, list):
        out_list = []
        for idx, item in enumerate(node):
            child = "%s/%d" % (prefix, idx)
            if blocked(child):
                continue
            out_list.append(_prune(item, child, excluded, globs))
        return out_list
    return node


def apply_render_policy(instance: Mapping[str, Any],
                        policy: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Return a deep copy of the document with every render-excluded pointer removed.

    ``redact.py`` stamps a ``render_policy`` member into both twins of every pair,
    identical across variants and arms. Honouring it is load-bearing, not
    cosmetic: the facts document echoes RuleArena's original English in
    ``facts.operations[].raw`` and carries ``gold``, ``provenance`` and the
    ``redaction`` record (which names the deleted pointer and its value). Render
    any of those and a redacted twin is handed its deleted fact back in prose, or
    the answer outright.

    The policy travels with the document, so all three arms strip the same
    pointers and ``facts_sha256`` stays identical across arms.
    """
    doc = copy.deepcopy(dict(instance))
    pol = policy if policy is not None else doc.get("render_policy")
    if not isinstance(pol, Mapping):
        pol = DEFAULT_RENDER_POLICY
    excluded = [p for p in (pol.get("excluded_pointer_prefixes") or []) if isinstance(p, str)]
    globs = [_glob_to_re(g) for g in (pol.get("excluded_pointer_globs") or [])
             if isinstance(g, str)]
    pruned = _prune(doc, "", excluded, globs)
    # The policy itself is metadata about the rendering, never part of it.
    pruned.pop("render_policy", None)
    return pruned


def redact_gold(instance: Mapping[str, Any]) -> Dict[str, Any]:
    """Backwards-compatible alias for :func:`apply_render_policy`.

    Removing ``gold`` alone is not enough --- see ``apply_render_policy`` --- so this
    name now delegates. It is kept because ``run.py`` and ``arm_b.py`` import it.
    """
    return apply_render_policy(instance)


def instance_key(instance: Mapping[str, Any]) -> str:
    """The identifier a result row is keyed by.

    ``redact.py`` emits two twins per instance that deliberately share
    ``instance_id`` (they are the same problem) and are told apart by ``twin_id``
    and ``variant``. Keying rows on ``instance_id`` alone would collide the pair:
    the resumable run would skip half of it and the scorer would collapse the
    answerable and redacted conditions into one. ``twin_id`` wins when present.
    """
    twin = instance.get("twin_id")
    if isinstance(twin, str) and twin:
        return twin
    return str(instance.get("instance_id", ""))


def canonical_facts_json(instance: Mapping[str, Any]) -> str:
    """Render the render-policy-redacted instance document to canonical, stable bytes.

    ``sort_keys=True`` plus a fixed indent makes the rendering independent of dict
    insertion order, so two arms built from the same instance are byte-identical
    and the run is reproducible.
    """
    return json.dumps(apply_render_policy(instance), sort_keys=True, indent=2,
                      ensure_ascii=False)


def facts_sha256(instance: Mapping[str, Any]) -> str:
    """Digest of the canonical facts rendering; recorded in every result row."""
    return hashlib.sha256(canonical_facts_json(instance).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# Rule identifier vocabulary
# --------------------------------------------------------------------------- #

_RULE_FIELD_RE = re.compile(
    r"^\s{4}(?P<name>[a-z0-9_]+)\s*:\s*bool\s*=\s*\\?\s*$\n"
    r"\s*Field\(description=\s*(?P<quote>\"|')(?P<desc>.*?)(?P=quote)\)",
    re.MULTILINE | re.DOTALL,
)


def rule_catalog_from_rulearena(micro_evaluation_py: str) -> Dict[str, str]:
    """Extract ``{rule_id: description}`` from RuleArena's ``micro_evaluation.py``.

    RuleArena's gold ``relevant_rules`` field names rules by the field names of the
    ``RuleExtraction`` pydantic model; those identifiers appear nowhere in
    ``reference_rules.txt``. This reads them straight out of the pinned, read-only
    checkout so the harness has no hidden vendored copy that could drift.

    Deterministic: dict insertion order follows source order.
    """
    with open(micro_evaluation_py, "r", encoding="utf-8") as fh:
        source = fh.read()
    catalog: Dict[str, str] = {}
    for match in _RULE_FIELD_RE.finditer(source):
        desc = match.group("desc").strip()
        desc = re.sub(r"\s+", " ", desc)
        catalog[match.group("name")] = desc
    if not catalog:
        raise ValueError("no rule identifiers found in %s" % micro_evaluation_py)
    return catalog


def load_rule_catalog(path: str) -> Dict[str, str]:
    """Load a rule catalog from ``micro_evaluation.py`` or from a JSON mapping."""
    if path.endswith(".py"):
        return rule_catalog_from_rulearena(path)
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        return {str(k): str(v) for k, v in data.items()}
    if isinstance(data, list):
        return {str(k): "" for k in data}
    raise ValueError("rule catalog %s must be a JSON object or array" % path)


def merge_rule_vocabulary(
    catalog: Optional[Mapping[str, str]], extra_ids: Sequence[str]
) -> Dict[str, str]:
    """Extend a rule catalog with identifiers observed in the gold label column.

    RuleArena's annotated ``relevant_rules`` contains nine identifiers that do not
    appear as fields of the ``RuleExtraction`` model (a mix of near-duplicates such
    as ``nontaxpayer_...`` for ``non_taxpayer_...`` and genuinely distinct
    combinations such as ``taxpayer_mid_level_exception_hard_cap_first_apron_level``).
    Presenting only the ``RuleExtraction`` field names would make part of the gold
    citation set unreachable by construction and would measure spelling rather than
    rule identification.

    This is a *label-space* disclosure, not a per-instance leak: the union is
    computed once over the whole instance set and is identical for every instance
    and every arm, exactly as RuleArena hands the model its full rule schema.
    Descriptions are empty for identifiers that exist only in the gold column.
    """
    merged: Dict[str, str] = dict(catalog or {})
    for rule_id in extra_ids:
        merged.setdefault(str(rule_id), "")
    return dict(sorted(merged.items()))


def _render_rule_vocabulary(catalog: Optional[Mapping[str, str]]) -> str:
    if not catalog:
        return (
            "RULE IDENTIFIER VOCABULARY\n\n"
            "No fixed vocabulary was supplied. Cite rules using the identifiers or "
            "section references that appear in the policy above."
        )
    lines = [
        "RULE IDENTIFIER VOCABULARY",
        "",
        "Cite rules using EXACTLY these identifiers, spelled exactly as written.",
        "Do not invent identifiers and do not cite section numbers instead.",
        "",
    ]
    for rule_id, desc in catalog.items():
        lines.append("- %s: %s" % (rule_id, desc) if desc else "- %s" % rule_id)
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Prompt builders
# --------------------------------------------------------------------------- #


def _assemble(policy_heading: str, policy_body: str, instance: Mapping[str, Any],
              catalog: Optional[Mapping[str, str]]) -> Tuple[str, str]:
    user = "\n\n".join(
        [
            policy_heading,
            policy_body.strip(),
            _render_rule_vocabulary(catalog),
            _FACTS_PREAMBLE,
            canonical_facts_json(instance),
            OUTPUT_CONTRACT,
        ]
    )
    return SYSTEM_PROMPT, user


def build_prompt_A(
    instance_facts: Mapping[str, Any],
    policy_text: str,
    *,
    rule_catalog: Optional[Mapping[str, str]] = None,
) -> Tuple[str, str]:
    """Arm A: the benchmark's own condition --- the CBA policy text, verbatim.

    Returns ``(system, user)``.
    """
    heading = (
        "POLICY\n\n"
        "The following is the governing policy text, reproduced verbatim. It is the "
        "only policy you may apply."
    )
    return _assemble(heading, policy_text, instance_facts, rule_catalog)


def build_prompt_Aprime(
    instance_facts: Mapping[str, Any],
    pack_prose: str,
    *,
    rule_catalog: Optional[Mapping[str, str]] = None,
) -> Tuple[str, str]:
    """Arm A-prime: the judgment pack's semantic content rendered as prose.

    Same disambiguation work as the pack, none of the pack machinery, and the
    byte-identical facts document. This arm exists so that a win for arm B cannot
    be attributed to "a human carefully analysed the policy".

    Returns ``(system, user)``.
    """
    heading = (
        "POLICY\n\n"
        "The following is the governing policy, restated in a disambiguated form: "
        "the conditions, exceptions and outcomes have been made explicit, but no "
        "rule has been added, removed or changed in effect. It is the only policy "
        "you may apply."
    )
    return _assemble(heading, pack_prose, instance_facts, rule_catalog)


def prompt_sha256(system: str, user: str) -> str:
    h = hashlib.sha256()
    h.update(system.encode("utf-8"))
    h.update(b"\x00")
    h.update(user.encode("utf-8"))
    return h.hexdigest()


# --------------------------------------------------------------------------- #
# Strict output parsing
# --------------------------------------------------------------------------- #


class ParseResult:
    """Outcome of parsing one model response.

    ``ok`` is True only when the response satisfies the documented contract.
    When ``ok`` is False, ``prediction`` is ``None`` and ``error`` carries a short
    machine-readable reason code. There is no partial success.
    """

    __slots__ = ("ok", "prediction", "error")

    def __init__(self, ok: bool, prediction: Optional[Dict[str, Any]], error: Optional[str]):
        self.ok = ok
        self.prediction = prediction
        self.error = error

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "ParseResult(ok=%r, prediction=%r, error=%r)" % (
            self.ok, self.prediction, self.error)

    def as_dict(self) -> Dict[str, Any]:
        return {"ok": self.ok, "prediction": self.prediction, "error": self.error}


_FENCE_RE = re.compile(r"```[a-zA-Z0-9_+-]*\s*\n(?P<body>.*?)(?:\n)?```", re.DOTALL)


def _strip_fences(text: str) -> str:
    """Return the contents of the first fenced block, or the text unchanged."""
    match = _FENCE_RE.search(text)
    if match:
        return match.group("body")
    return text


def _first_json_object(text: str) -> Optional[str]:
    """Return the first balanced ``{...}`` span, respecting strings and escapes."""
    depth = 0
    start = -1
    in_string = False
    escaped = False
    for idx, ch in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            if depth == 0:
                start = idx
            depth += 1
        elif ch == "}":
            if depth == 0:
                continue
            depth -= 1
            if depth == 0 and start >= 0:
                return text[start: idx + 1]
    return None


def parse_prediction(text: Optional[str]) -> ParseResult:
    """Parse a model response into the shared output contract.

    Tolerant about packaging: a leading/trailing prose wrapper, a ```json fence, or
    surrounding whitespace are all accepted, and the first balanced JSON object in
    the response is taken.

    Strict about shape: see the module docstring. A response that does not satisfy
    the contract yields ``ok=False`` and is never coerced into a decision.
    """
    if text is None or not text.strip():
        return ParseResult(False, None, "empty-response")

    candidate = _strip_fences(text).strip()
    blob = candidate if candidate.startswith("{") else None
    if blob is None:
        blob = _first_json_object(candidate)
    if blob is None:
        blob = _first_json_object(text)
    if blob is None:
        return ParseResult(False, None, "no-json-object")

    try:
        obj = json.loads(blob)
    except (ValueError, TypeError) as exc:
        return ParseResult(False, None, "json-decode-error: %s" % (str(exc)[:200],))

    if not isinstance(obj, dict):
        return ParseResult(False, None, "not-a-json-object")

    for key in ("decision", "cited_rules", "reason"):
        if key not in obj:
            return ParseResult(False, None, "missing-key:%s" % key)

    decision = obj["decision"]
    if not isinstance(decision, str) or decision not in DECISIONS:
        return ParseResult(False, None, "bad-decision:%s" % (repr(decision)[:80],))

    cited = obj["cited_rules"]
    if not isinstance(cited, list):
        return ParseResult(False, None, "cited_rules-not-a-list")
    for element in cited:
        if not isinstance(element, str):
            return ParseResult(False, None, "cited_rules-non-string-element")

    reason = obj["reason"]
    if not isinstance(reason, str):
        return ParseResult(False, None, "reason-not-a-string")

    extra = {k: v for k, v in obj.items() if k not in ("decision", "cited_rules", "reason")}
    prediction: Dict[str, Any] = {
        "decision": decision,
        "cited_rules": list(cited),
        "reason": reason,
    }
    if extra:
        prediction["extra"] = extra
    return ParseResult(True, prediction, None)


def dedupe_preserving_order(items: Sequence[str]) -> List[str]:
    """Small shared helper; citation metrics treat cited_rules as a set."""
    seen: Dict[str, None] = {}
    for item in items:
        seen.setdefault(item, None)
    return list(seen)
