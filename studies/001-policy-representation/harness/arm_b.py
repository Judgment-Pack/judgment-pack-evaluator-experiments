"""Arm B: consult a Judgment Pack through the judgment-pack runtime.

WHAT THIS FILE DOES
-------------------
For one instance it invokes::

    judgment-pack experimental evaluate <pack> --facts <facts.json> \\
        [--evidence <ev.json>] [--supported-extension <name> ...] --format json

and maps the returned *disposition* onto the same output contract every other arm
answers in --- ``{"decision", "cited_rules", "reason"}``:

* ``kind == "outcome"``        -> ``decision`` obtained from ``outcomeId`` via the
                                  outcome map (see below).
* ``kind == "unresolved"``     -> ``"cannot_decide"``
* ``kind == "not-applicable"`` -> ``"cannot_decide"``

``cited_rules`` is the set of *fired* rule ids: entries of the runtime trace whose
``stage`` is ``"rule"`` and whose ``condition`` is ``"true"``, in trace order.
``reason`` is assembled from the disposition kind, its retained reasons and the
configured handoff state.

The facts document handed to the runtime is produced by
``arms.canonical_facts_json`` --- the byte-identical, gold-redacted document that
arms A and A-prime receive --- so the three arms cannot diverge on facts.

PREREGISTERED RULE, IMPLEMENTED HERE
------------------------------------
**An engine refusal is an arm-B FAILURE and is recorded as one. It is never
silently skipped, retried into success, or converted into an abstention.**
A refusal is any of:

* the CLI exits non-zero, times out, or emits unparseable output;
* the JSON envelope reports ``status != "evaluated"`` --- this covers a
  non-conformant pack (``JPS-EVALUATION-PACK-NOT-CONFORMANT``), malformed input,
  and an undeclared evidence key (``JPS-EVALUATION-EVIDENCE-KEY``);
* the disposition names an ``outcomeId`` that the outcome map cannot resolve to a
  decision in the shared vocabulary.

All of these yield ``ok=False``, ``prediction=None`` and a populated ``error``
beginning with ``engine-refusal:`` or ``outcome-map-failure:``. The scorer counts
such a row as an incorrect, non-escalating answer. Suppressing them would let arm
B quietly discard its hardest instances.

A **non-zero exit is a refusal on the exit code alone**, whatever the process
wrote to stdout. An earlier revision rejected a non-zero exit only when stdout was
also empty, so a runtime that printed a well-formed envelope and then failed could
be scored as a success; the adversarial review recorded that in ``DEVIATIONS.md``
section 3, and the rule was tightened here on 2026-08-06. So that "N engine
refusals" can be checked against the retained rows rather than taken on trust,
*every* return path of ``evaluate_instance`` carries the child process's
``returncode`` and its ``stderr`` verbatim --- including the paths where no
process completed, which record ``returncode=None``.

**What that does NOT do is make the study's published arm-B numbers auditable.**
The change is to the harness, not to the data: every row in
``results/pilot-B-runtime.jsonl`` was written before it, is
``jps-study-001-result/1``, carries no ``engine_returncode`` and no
``engine_stderr``, and was scored under the permissive rule. Arm B has **not**
been re-run, so ``RESULTS-FIRST-PROMPT-ARMS.md``'s "0 errors" for arm B rests on
the old rule and on the same unauditable retained rows as before --- the new keys
audit runs made from now on and nothing earlier. Nor was the rule change
registered in advance: it was made after the result was read, which is recorded
in ``DEVIATIONS.md`` section 4 along with the direction it can move a number
(strictly down for arm B, never up). The stricter rule does not catch a
legitimate abstention: the current runtime's ``internal/cli/app.go`` documents
that producing *any* disposition exits 0, so ``unresolved`` and
``not-applicable`` come back through the normal path.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
* No arithmetic and no fact synthesis. JPS compares facts; it does not compute
  them. Derived quantities are already in ``facts.derived``.
* No pack authoring, no pack repair, no validation pass of its own --- the runtime
  is the authority on conformance and its refusal is the observation.
* No retries. The runtime is deterministic; a second identical call would produce
  the same bytes, so a retry could only mask a real refusal.
* No inference of the outcome vocabulary from the pack file. The mapping from the
  pack's ``outcomeId`` values to ``legal``/``illegal``/``cannot_decide`` is study
  configuration, supplied explicitly (``--outcome-map``) or resolved by the
  documented conservative heuristic below, and an unresolvable id is a recorded
  failure rather than a guess.

THE OUTCOME MAP
---------------
``resolve_outcome`` consults, in order:

1. an explicit ``{outcomeId: decision}`` mapping, if supplied;
2. exact match against the shared vocabulary (``legal``/``illegal``/
   ``cannot_decide``);
3. a conservative substring heuristic --- an id containing ``illegal``,
   ``violat``, ``prohibit``, ``disallow``, ``noncompliant`` or ``not-permitted``
   maps to ``illegal``; one containing ``legal``, ``compliant``, ``permitted``,
   ``allowed`` or ``approve`` maps to ``legal``; one containing ``escalat``,
   ``review``, ``undetermined`` or ``cannot`` maps to ``cannot_decide``. The
   ``illegal``/``not-permitted`` tests run before the ``legal``/``permitted``
   tests so that ``illegal`` is not misread as ``legal``.
4. otherwise: failure.

Supply ``--outcome-map`` for the preregistered run rather than relying on (3).

Python 3.10+ (``from __future__ import annotations`` keeps it importable on 3.8).
Standard library only.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Mapping, Optional, Sequence

from arms import DECISIONS, canonical_facts_json

__all__ = [
    "ArmBConfig",
    "resolve_outcome",
    "map_envelope",
    "evaluate_instance",
    "fired_rule_ids",
]

_ILLEGAL_MARKERS = ("illegal", "violat", "prohibit", "disallow", "noncompliant",
                    "non-compliant", "not-permitted", "not_permitted", "reject", "deny")
_LEGAL_MARKERS = ("legal", "compliant", "permitted", "permit", "allowed", "allow", "approve")
_ABSTAIN_MARKERS = ("escalat", "review", "undetermined", "cannot", "unknown", "refer")


class ArmBConfig:
    """Everything arm B needs, gathered so a run is self-describing."""

    __slots__ = ("pack_path", "cli", "outcome_map", "supported_extensions",
                 "facts_root", "evidence_dir", "timeout_s")

    def __init__(
        self,
        pack_path: str,
        *,
        cli: str = "judgment-pack",
        outcome_map: Optional[Mapping[str, str]] = None,
        supported_extensions: Sequence[str] = (),
        facts_root: str = "instance",
        evidence_dir: Optional[str] = None,
        timeout_s: float = 120.0,
    ) -> None:
        if facts_root not in ("instance", "facts"):
            raise ValueError("facts_root must be 'instance' or 'facts', got %r" % facts_root)
        self.pack_path = pack_path
        self.cli = cli
        self.outcome_map = dict(outcome_map or {})
        self.supported_extensions = list(supported_extensions)
        self.facts_root = facts_root
        self.evidence_dir = evidence_dir
        self.timeout_s = float(timeout_s)

    def describe(self) -> Dict[str, Any]:
        return {
            "pack_path": self.pack_path,
            "cli": self.cli,
            "outcome_map": dict(sorted(self.outcome_map.items())),
            "supported_extensions": list(self.supported_extensions),
            "facts_root": self.facts_root,
            "evidence_dir": self.evidence_dir,
            "timeout_s": self.timeout_s,
        }


def resolve_outcome(outcome_id: str, outcome_map: Mapping[str, str]) -> Optional[str]:
    """Map a pack outcome id to the shared decision vocabulary, or ``None``."""
    if outcome_id in outcome_map:
        mapped = outcome_map[outcome_id]
        return mapped if mapped in DECISIONS else None
    if outcome_id in DECISIONS:
        return outcome_id
    lowered = outcome_id.lower()
    if any(marker in lowered for marker in _ILLEGAL_MARKERS):
        return "illegal"
    if any(marker in lowered for marker in _LEGAL_MARKERS):
        return "legal"
    if any(marker in lowered for marker in _ABSTAIN_MARKERS):
        return "cannot_decide"
    return None


def fired_rule_ids(trace: Optional[Sequence[Mapping[str, Any]]]) -> List[str]:
    """Rule ids that evaluated true, in trace order, de-duplicated."""
    out: Dict[str, None] = {}
    for entry in trace or []:
        if not isinstance(entry, Mapping):
            continue
        if entry.get("stage") == "rule" and entry.get("condition") == "true":
            rule_id = entry.get("id")
            if isinstance(rule_id, str):
                out.setdefault(rule_id, None)
    return list(out)


def map_envelope(envelope: Mapping[str, Any], outcome_map: Mapping[str, str]) -> Dict[str, Any]:
    """Map one ``experimental evaluate --format json`` envelope onto the contract.

    Returns ``{"ok", "prediction", "error"}``. ``ok`` is False for every engine
    refusal and for every unresolvable outcome id.
    """
    status = envelope.get("status")
    if status != "evaluated":
        diags = envelope.get("diagnostics") or []
        first = diags[0] if diags and isinstance(diags[0], Mapping) else {}
        return {
            "ok": False,
            "prediction": None,
            "error": "engine-refusal:status=%s:%s:%s" % (
                status,
                first.get("code", "no-code"),
                str(first.get("message", ""))[:400],
            ),
        }

    disposition = envelope.get("disposition")
    if not isinstance(disposition, Mapping):
        return {"ok": False, "prediction": None,
                "error": "engine-refusal:missing-disposition"}

    kind = disposition.get("kind")
    reasons = [str(r) for r in (disposition.get("reasons") or [])]
    handoff = disposition.get("handoff") or {}
    handoff_state = handoff.get("state") if isinstance(handoff, Mapping) else None
    cited = fired_rule_ids(envelope.get("trace"))

    if kind == "outcome":
        outcome_id = disposition.get("outcomeId")
        if not isinstance(outcome_id, str):
            return {"ok": False, "prediction": None,
                    "error": "engine-refusal:outcome-without-id"}
        decision = resolve_outcome(outcome_id, outcome_map)
        if decision is None:
            return {
                "ok": False,
                "prediction": None,
                "error": "outcome-map-failure:%s" % outcome_id,
            }
        reason = "Pack resolved outcome %r." % outcome_id
        if reasons:
            reason += " Reasons: %s." % ", ".join(reasons)
    elif kind in ("unresolved", "not-applicable"):
        decision = "cannot_decide"
        reason = "Pack disposition %r." % kind
        if reasons:
            reason += " Reasons: %s." % ", ".join(reasons)
        if handoff_state:
            reason += " Handoff: %s." % handoff_state
    else:
        return {"ok": False, "prediction": None,
                "error": "engine-refusal:unknown-disposition-kind:%s" % (kind,)}

    prediction = {
        "decision": decision,
        "cited_rules": cited,
        "reason": reason,
        "extra": {
            "disposition_kind": kind,
            "outcome_id": disposition.get("outcomeId"),
            "reasons": reasons,
            "handoff_state": handoff_state,
        },
    }
    return {"ok": True, "prediction": prediction, "error": None}


def _facts_payload(instance: Mapping[str, Any], facts_root: str) -> str:
    """Render the facts document the runtime will read.

    ``instance`` (the default) hands the runtime the byte-identical gold-redacted
    document the prompt arms see, so pack pointers read ``/facts/derived/...``.
    ``facts`` hands it only the ``facts`` sub-object, for a pack whose pointers are
    rooted there. Which one the study uses is a property of the authored pack and
    is recorded in every result row.
    """
    if facts_root == "facts":
        sub = instance.get("facts", {})
        return json.dumps(sub, sort_keys=True, indent=2, ensure_ascii=False)
    return canonical_facts_json(instance)


def _evidence_path_for(instance_id: str, evidence_dir: Optional[str]) -> Optional[str]:
    if not evidence_dir:
        return None
    safe = instance_id.replace("/", "_").replace("#", "_")
    candidate = os.path.join(evidence_dir, safe + ".json")
    return candidate if os.path.exists(candidate) else None


def _decoded(stream: Any) -> str:
    """Decode one captured stderr stream to text; ``""`` when nothing was captured.

    ``TimeoutExpired.stderr`` is ``bytes`` when the child wrote before the timeout
    expired and ``None`` when it wrote nothing at all. Both are recorded --- as
    text and as the empty string respectively --- rather than dropped, because the
    partial stderr of a timed-out runtime is often the only account of it.
    """
    if stream is None:
        return ""
    if isinstance(stream, bytes):
        return stream.decode("utf-8", "replace")
    return str(stream)


def evaluate_instance(instance: Mapping[str, Any], config: ArmBConfig) -> Dict[str, Any]:
    """Run the pack against one instance.

    Returns ``{"ok", "prediction", "error", "raw_text", "raw", "latency_ms",
    "argv", "returncode", "stderr"}``. ``raw_text`` is the runtime's stdout
    verbatim, kept so an arm-B refusal is as auditable as a model's malformed
    reply. ``returncode`` is the child's exit status, or ``None`` on the two paths
    where no process completed (timeout, and a CLI that could not be executed);
    ``stderr`` is the child's stderr decoded verbatim, ``""`` where none was
    captured. Both are present on every return path, success included.
    """
    instance_id = str(instance.get("instance_id", "<unknown>"))
    payload = _facts_payload(instance, config.facts_root)
    evidence_path = _evidence_path_for(instance_id, config.evidence_dir)

    tmpdir = tempfile.mkdtemp(prefix="jps-armb-")
    facts_path = os.path.join(tmpdir, "facts.json")
    with open(facts_path, "w", encoding="utf-8") as fh:
        fh.write(payload)

    argv = [config.cli, "experimental", "evaluate", config.pack_path,
            "--facts", facts_path, "--format", "json"]
    if evidence_path:
        argv.extend(["--evidence", evidence_path])
    for ext in config.supported_extensions:
        argv.extend(["--supported-extension", ext])

    started = time.monotonic()
    try:
        proc = subprocess.run(  # noqa: S603 - argv list, no shell
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=config.timeout_s,
        )
    except OSError as exc:
        # FileNotFoundError on most platforms; some environments surface a bare
        # PermissionError for an unresolvable name. Either way it is a refusal to
        # be recorded, never a crash that silently drops the instance.
        latency_ms = int((time.monotonic() - started) * 1000)
        _cleanup(tmpdir, facts_path)
        # No process ran, so there is no exit status to record and none is
        # invented: returncode is None, which is distinguishable from 0.
        return {"ok": False, "prediction": None,
                "error": "engine-refusal:cli-not-found:%s:%s" % (config.cli, exc.__class__.__name__),
                "raw_text": "", "raw": None, "latency_ms": latency_ms, "argv": argv,
                "returncode": None, "stderr": ""}
    except subprocess.TimeoutExpired as exc:
        latency_ms = int((time.monotonic() - started) * 1000)
        _cleanup(tmpdir, facts_path)
        return {"ok": False, "prediction": None,
                "error": "engine-refusal:timeout after %ss" % config.timeout_s,
                "raw_text": "", "raw": None, "latency_ms": latency_ms, "argv": argv,
                "returncode": None, "stderr": _decoded(exc.stderr)}
    latency_ms = int((time.monotonic() - started) * 1000)
    _cleanup(tmpdir, facts_path)

    stdout = proc.stdout.decode("utf-8", "replace")
    stderr = proc.stderr.decode("utf-8", "replace")

    # The registered rule, implemented literally: a non-zero exit is a refusal.
    # stdout is not consulted, because a runtime that printed an envelope and then
    # failed has not answered the instance --- it has told us it could not.
    if proc.returncode != 0:
        return {"ok": False, "prediction": None,
                "error": "engine-refusal:exit=%d:%s" % (proc.returncode, stderr.strip()[:400]),
                "raw_text": stdout, "raw": None, "latency_ms": latency_ms, "argv": argv,
                "returncode": proc.returncode, "stderr": stderr}

    try:
        envelope = json.loads(stdout)
    except (ValueError, TypeError) as exc:
        return {"ok": False, "prediction": None,
                "error": "engine-refusal:unparseable-output:%s" % (str(exc)[:200],),
                "raw_text": stdout, "raw": None, "latency_ms": latency_ms, "argv": argv,
                "returncode": proc.returncode, "stderr": stderr}

    if not isinstance(envelope, dict):
        return {"ok": False, "prediction": None,
                "error": "engine-refusal:output-not-an-object",
                "raw_text": stdout, "raw": None, "latency_ms": latency_ms, "argv": argv,
                "returncode": proc.returncode, "stderr": stderr}

    mapped = map_envelope(envelope, config.outcome_map)
    mapped.update({
        "raw_text": stdout,
        "raw": envelope,
        "latency_ms": latency_ms,
        "argv": argv,
        "returncode": proc.returncode,
        "stderr": stderr,
    })
    return mapped


def _cleanup(tmpdir: str, *paths: str) -> None:
    for path in paths:
        try:
            os.unlink(path)
        except OSError:
            pass
    try:
        os.rmdir(tmpdir)
    except OSError:
        pass
