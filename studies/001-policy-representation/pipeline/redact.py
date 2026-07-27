#!/usr/bin/env python3
"""Redaction operator: manufacture answerable/redacted twin pairs from facts documents.

WHAT THIS DOES
--------------
RuleArena contains no abstention condition -- every one of its 216 NBA instances is
decidable from the facts it ships. This study needs a "cannot decide, a required fact is
missing" condition in order to measure escalation. This module manufactures one, in the
manner of SQuAD 2.0 contrast sets / AbstentionBench / HiL-Bench: for each parsed facts
document it emits a PAIR of twins,

    <id>__answerable.json  facts unchanged, expected decision = the gold answer
    <id>__redacted.json    exactly ONE load-bearing fact pointer deleted,
                           expected decision = "cannot_decide"

Exactly one answerable and one redacted twin per instance, so an always-escalate agent and
a never-escalate agent both score at chance. Pairs are emitted or skipped as a unit; a
lone twin is never written.

WHICH fact is deleted is not the author's judgment. It is read off the benchmark's own
artifacts: the instance's gold `relevant_rules` names the provisions that govern it, and
loadbearing_map.json (generated from RuleArena's nba/micro_evaluation.py rule text and
nba/reference_rules.txt) says which fact ROLES each such provision must read in order to
be evaluated at all. The union of those roles, resolved against the actual document and
filtered by the guards below, is the candidate set. Among the surviving candidates the
ones required by the most cited rules are preferred, and a seeded RNG keyed on
sha256(seed | instance_id) picks one -- so the choice is reproducible exactly and does not
depend on how many instances are processed or in what order.

GUARDS (a twin that had to relax any of these is still emitted, but marked weak and
excluded from the primary analysis):
  G1  the pointer must actually resolve in the answerable document -- never delete a fact
      that was absent anyway, which would produce an identical pair;
  G2  the fact must belong to an entity that actually takes part in an operation; a bench
      player's contract term is cited-rule-shaped but decides nothing here;
  G3  when the gold answer is "illegal", the deleted fact must be scoped to the gold
      problematic_team, to the gold illegal_operation, or to a player participating in it
      -- deleting a fact somewhere else plainly leaves the violation decidable;
  G4  the fact must not survive elsewhere: not duplicated under another name in the same
      scope, not implied by a declared sibling key (a contract's `salary_kind: "explicit"`
      tells you nothing once `first_year_salary` is sitting next to it), not superseded by
      a facts.derived leaf scoped to the same entity whose name carries one of the role's
      supersession tokens (if the preprocessor already published the post-transaction
      number, deleting its raw input decides nothing), and not legible verbatim in any
      other renderable string in the document.

RENDER POLICY. The facts document echoes RuleArena's original prose in
`facts.operations[].raw` and carries `gold` and `provenance`. Rendering any of those into
a prompt would hand a redacted twin its deleted fact back in English and would leak the
answer outright. loadbearing_map.json declares the excluded pointers; every twin carries
that policy in its `render_policy` member, identical across both variants and all three
arms, and the leak audit below is evaluated only over what remains renderable.

Among the candidates that clear the guards the choice is UNIFORM under the seeded RNG --
no preference for "most load-bearing" -- so the redacted arm exercises a spread of fact
kinds rather than always hiding the same field, which a system could learn to pattern-match
without reasoning about the policy.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
* It does not evaluate the CBA. It cannot prove that no OTHER cited rule independently
  establishes the same operation's illegality after the deletion; establishing that would
  require re-implementing the policy, which is the thing the study is testing. Twins whose
  answerable gold is `false` (legal) carry no such residue -- a "legal" verdict requires
  every cited rule to be checkable, so removing any one required fact blocks it -- and are
  tagged strength_basis "universal". Twins whose gold is `true` and that pass G3 are tagged
  "localized". Both are strong; analyses that want the airtight subset filter to universal.
* It does not compute or repair derived quantities, and it never deletes one: facts.derived
  is recomputable from surviving raw facts by any arm that can do arithmetic.
* It does not rewrite prose, reorder facts, or touch anything but the single deleted key.
* It does not invent facts, and it does not renumber or remove array elements.

Python 3.10+, standard library only. Same inputs and seed produce byte-identical output.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import random
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator

DEFAULT_SEED = 20260727
BIND_RE = re.compile(r"^\{(\w+)\}$")
SAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")
DERIVED_PREFIX = "/facts/derived"


# --------------------------------------------------------------------------- #
# RFC 6901 JSON Pointer                                                        #
# --------------------------------------------------------------------------- #
def ptr_escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def ptr_unescape(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def ptr_build(tokens: Iterable[str]) -> str:
    return "".join("/" + ptr_escape(t) for t in tokens)


def ptr_tokens(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise ValueError(f"not an RFC 6901 pointer: {pointer!r}")
    return [ptr_unescape(t) for t in pointer.split("/")[1:]]


def ptr_get(doc: Any, pointer: str, default: Any = None) -> Any:
    node = doc
    for tok in ptr_tokens(pointer):
        if isinstance(node, dict):
            if tok not in node:
                return default
            node = node[tok]
        elif isinstance(node, list):
            if not tok.lstrip("-").isdigit() or not (0 <= int(tok) < len(node)):
                return default
            node = node[int(tok)]
        else:
            return default
    return node


_MISSING = object()


def ptr_exists(doc: Any, pointer: str) -> bool:
    return ptr_get(doc, pointer, _MISSING) is not _MISSING


def ptr_delete(doc: Any, pointer: str) -> Any:
    """Delete the member at `pointer`, returning the removed value.

    Only object members are deletable. Deleting an array element would renumber its
    siblings and change the cardinality of the scenario, which is a different edit than
    "one fact is missing", so it is refused.
    """
    tokens = ptr_tokens(pointer)
    if not tokens:
        raise ValueError("refusing to delete the whole document")
    parent = ptr_get(doc, ptr_build(tokens[:-1]), _MISSING)
    if parent is _MISSING:
        raise KeyError(f"parent of {pointer} does not exist")
    last = tokens[-1]
    if isinstance(parent, list):
        raise ValueError(f"refusing to delete array element {pointer}")
    if not isinstance(parent, dict) or last not in parent:
        raise KeyError(f"{pointer} does not exist")
    return parent.pop(last)


def iter_leaves(node: Any, prefix: str = "") -> Iterator[tuple[str, Any]]:
    """Yield (pointer, value) for every scalar leaf under `node`."""
    if isinstance(node, dict):
        for k in node:
            yield from iter_leaves(node[k], prefix + "/" + ptr_escape(str(k)))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_leaves(v, prefix + "/" + str(i))
    else:
        yield prefix, node


# --------------------------------------------------------------------------- #
# Pointer-template expansion                                                   #
# --------------------------------------------------------------------------- #
def expand_template(doc: Any, template: str) -> list[str]:
    """Resolve one pointer template against `doc`, returning existing pointers, sorted.

    Segment forms: literal, `{name}` (bind any key/index at that position), or an fnmatch
    glob. Results are deterministic: keys are visited in sorted order.
    """
    segs = template.split("/")[1:]
    out: list[str] = []

    def walk(node: Any, i: int, acc: list[str]) -> None:
        if i == len(segs):
            out.append(ptr_build(acc))
            return
        seg = segs[i]
        bind = BIND_RE.match(seg)
        if isinstance(node, dict):
            if bind or ("*" in seg or "?" in seg):
                pat = None if bind else seg
                for key in sorted(node, key=str):
                    if pat is None or fnmatch.fnmatchcase(str(key), pat):
                        walk(node[key], i + 1, acc + [str(key)])
            else:
                key = ptr_unescape(seg)
                if key in node:
                    walk(node[key], i + 1, acc + [key])
        elif isinstance(node, list):
            if bind or seg in ("*", "?"):
                for idx in range(len(node)):
                    walk(node[idx], i + 1, acc + [str(idx)])
            elif seg.isdigit() and int(seg) < len(node):
                walk(node[int(seg)], i + 1, acc + [seg])

    walk(doc, 0, [])
    return sorted(out)


# --------------------------------------------------------------------------- #
# Instance introspection                                                       #
# --------------------------------------------------------------------------- #
def team_keys(doc: dict) -> list[str]:
    node = ptr_get(doc, "/facts/teams", {})
    return sorted(node) if isinstance(node, dict) else []


def player_keys(doc: dict) -> list[str]:
    node = ptr_get(doc, "/facts/players", {})
    return sorted(node) if isinstance(node, dict) else []


def op_label(doc: dict, index: int) -> str:
    node = ptr_get(doc, "/facts/operations", [])
    if isinstance(node, list) and 0 <= index < len(node):
        op = node[index]
        if isinstance(op, dict):
            for key in ("label", "id", "name", "operation"):
                if isinstance(op.get(key), str):
                    return op[key]
    return str(index)


def op_index_by_label(doc: dict, label: str | None) -> int | None:
    if label is None:
        return None
    node = ptr_get(doc, "/facts/operations", [])
    if isinstance(node, list):
        for i in range(len(node)):
            if op_label(doc, i) == label:
                return i
    return None


def strings_in(node: Any) -> set[str]:
    """Every string appearing anywhere in `node` (values and dict keys)."""
    found: set[str] = set()
    if isinstance(node, dict):
        for k, v in node.items():
            found.add(str(k))
            found |= strings_in(v)
    elif isinstance(node, list):
        for v in node:
            found |= strings_in(v)
    elif isinstance(node, str):
        found.add(node)
    return found


def scope_of(doc: dict, pointer: str) -> tuple[str, str | None]:
    """('team'|'player'|'operation'|'derived'|'global', entity key or None)."""
    toks = ptr_tokens(pointer)
    if len(toks) >= 3 and toks[0] == "facts":
        if toks[1] == "teams":
            return ("team", toks[2])
        if toks[1] == "players":
            return ("player", toks[2])
        if toks[1] == "operations" and toks[2].isdigit():
            return ("operation", op_label(doc, int(toks[2])))
    if len(toks) >= 2 and toks[0] == "facts" and toks[1] == "derived":
        return ("derived", None)
    return ("global", None)


# --------------------------------------------------------------------------- #
# Candidate construction                                                       #
# --------------------------------------------------------------------------- #
class Candidate:
    __slots__ = ("pointer", "role", "scope_kind", "scope_key", "rules", "redundant_reasons")

    def __init__(self, pointer: str, role: str, scope_kind: str, scope_key: str | None):
        self.pointer = pointer
        self.role = role
        self.scope_kind = scope_kind
        self.scope_key = scope_key
        self.rules: list[str] = []
        self.redundant_reasons: list[str] = []

    @property
    def fan_in(self) -> int:
        return len(self.rules)


def resolve_role(doc: dict, role_def: dict) -> list[str]:
    """First pointer alternative that resolves to anything wins; returns its pointers."""
    for template in role_def.get("pointer_alternatives", []):
        hits = [p for p in expand_template(doc, template) if not p.startswith(DERIVED_PREFIX)]
        if hits:
            return hits
    return []


def is_renderable(pointer: str, policy: dict) -> bool:
    """Would a prompt renderer show this pointer to a model?"""
    for prefix in policy.get("excluded_pointer_prefixes", []):
        if pointer == prefix or pointer.startswith(prefix + "/"):
            return False
    for glob in policy.get("excluded_pointer_globs", []):
        gsegs = glob.split("/")[1:]
        psegs = pointer.split("/")[1:]
        if len(psegs) >= len(gsegs) and all(
            fnmatch.fnmatchcase(p, g) for p, g in zip(psegs, gsegs)
        ):
            return False
    return True


MIN_LEAK_LEN = 3


def leak_audit(twin: dict, removed_value: Any, policy: dict) -> tuple[list[str], list[str]]:
    """Where is the deleted value still legible? Returns (renderable hits, excluded hits).

    A hit means the value is spelled out inside a PROSE string -- a multi-word field that
    states the fact in English. Prose is detected by the presence of a space, which in this
    facts contract distinguishes the parser's narrative echoes ("during 2023-2024 Regular
    Season", "minimum applicable player salary") from structured scalars. A structured
    scalar elsewhere that happens to contain the same digits ("8000000" inside a team
    salary of "158000000", "2023" inside a cap year of "2023-24") is a coincidence, not a
    recovery path, and is not counted. Hits in the excluded zone are informational: they
    are the reason the render policy exists, not a defect in the twin.
    """
    if not isinstance(removed_value, (str, int, float)) or isinstance(removed_value, bool):
        return [], []
    needle = str(removed_value)
    if len(needle) < MIN_LEAK_LEN:
        return [], []
    rendered: list[str] = []
    excluded: list[str] = []
    for pointer, value in iter_leaves(twin):
        if not isinstance(value, str) or " " not in value or needle not in value:
            continue
        (rendered if is_renderable(pointer, policy) else excluded).append(pointer)
    return sorted(rendered), sorted(excluded)


def derived_leaves(doc: dict) -> list[str]:
    node = ptr_get(doc, "/facts/derived", None)
    if node is None:
        return []
    return [DERIVED_PREFIX + p for p, _ in iter_leaves(node)]


def derived_supersedes(
    doc: dict, cand: Candidate, role_def: dict, leaves: list[str]
) -> str | None:
    """Is the deleted fact still readable off a derived value scoped to the same entity?"""
    tokens = [t.lower() for t in role_def.get("derived_supersede_tokens", [])]
    if not tokens or not leaves:
        return None
    entity = cand.scope_key
    for leaf in leaves:
        toks = ptr_tokens(leaf)
        # Same-entity test: the entity key appears as a path segment, or the derived
        # subtree is not keyed by entity at all (then every leaf is in scope).
        if entity is not None and entity not in toks[2:]:
            if any(k in toks[2:] for k in (team_keys(doc) + player_keys(doc))):
                continue
        name = toks[-1].lower() if toks else ""
        for tok in tokens:
            if tok in name:
                return f"{leaf} (token {tok!r})"
    return None


def build_candidates(doc: dict, mapping: dict, cited: list[str]) -> tuple[list[Candidate], dict]:
    roles = mapping["roles"]
    rules = mapping["rules"]
    by_pointer: dict[str, Candidate] = {}
    role_hits: dict[str, list[str]] = {}
    referenced_roles: set[str] = set()
    unknown_rules: list[str] = []

    for rule_id in cited:
        rule = rules.get(rule_id)
        if rule is None:
            unknown_rules.append(rule_id)
            continue
        for role in rule["required_roles"]:
            role_def = roles[role]
            referenced_roles.add(role)
            if role not in role_hits:
                role_hits[role] = resolve_role(doc, role_def)
            for pointer in role_hits[role]:
                cand = by_pointer.get(pointer)
                if cand is None:
                    kind, key = scope_of(doc, pointer)
                    cand = Candidate(pointer, role, kind, key)
                    by_pointer[pointer] = cand
                if rule_id not in cand.rules:
                    cand.rules.append(rule_id)

    # G4a: the same role resolving to several pointers in the same scope means the fact is
    # written down more than once; deleting one copy leaves the other.
    per_role_scope: dict[tuple[str, str, str | None], list[str]] = {}
    for cand in by_pointer.values():
        per_role_scope.setdefault((cand.role, cand.scope_kind, cand.scope_key), []).append(
            cand.pointer
        )
    for (role, _, _), pointers in per_role_scope.items():
        if len(pointers) > 1:
            for pointer in pointers:
                others = [p for p in sorted(pointers) if p != pointer]
                by_pointer[pointer].redundant_reasons.append(
                    f"role {role} also readable at {others[0]}"
                )

    # G4b: implied by a sibling key the map declares as carrying the same information.
    for cand in by_pointer.values():
        siblings = roles[cand.role].get("redundant_if_sibling_keys") or []
        if not siblings:
            continue
        toks = ptr_tokens(cand.pointer)
        parent = ptr_get(doc, ptr_build(toks[:-1]), None)
        if isinstance(parent, dict):
            present = [k for k in siblings if k in parent and k != toks[-1]]
            if present:
                cand.redundant_reasons.append(
                    f"implied by sibling key(s) {', '.join(sorted(present))}"
                )

    # G4c: superseded by a published derived quantity.
    leaves = derived_leaves(doc)
    for cand in by_pointer.values():
        hit = derived_supersedes(doc, cand, roles[cand.role], leaves)
        if hit is not None:
            cand.redundant_reasons.append(f"superseded by derived value {hit}")

    diagnostics = {
        "referenced_roles": sorted(referenced_roles),
        "resolved_roles": sorted(r for r, hits in role_hits.items() if hits),
        "unknown_cited_rules": sorted(set(unknown_rules)),
        "derived_is_empty": not leaves,
    }
    return sorted(by_pointer.values(), key=lambda c: c.pointer), diagnostics


def operation_participants(doc: dict, index: int | None = None) -> set[str]:
    """Every team/player label named by an operation (all operations when index is None)."""
    ops = ptr_get(doc, "/facts/operations", [])
    if not isinstance(ops, list):
        return set()
    chosen = ops if index is None else ([ops[index]] if 0 <= index < len(ops) else [])
    names: set[str] = set()
    for op in chosen:
        names |= strings_in(op)
    return names & (set(team_keys(doc)) | set(player_keys(doc)))


def participates(doc: dict, cand: Candidate) -> bool:
    """G2 -- does the candidate's entity take part in any operation at all?"""
    if cand.scope_kind == "operation":
        return True
    if cand.scope_kind in ("team", "player"):
        return cand.scope_key in operation_participants(doc)
    return False


def is_local(doc: dict, cand: Candidate, gold: dict) -> bool:
    """G3 -- is the candidate scoped to where gold says the violation is?"""
    problematic = gold.get("problematic_team")
    illegal = gold.get("illegal_operation")
    if cand.scope_kind == "team":
        return cand.scope_key == problematic
    if cand.scope_kind == "operation":
        return cand.scope_key == illegal
    if cand.scope_kind == "player":
        idx = op_index_by_label(doc, illegal)
        if idx is None:
            return False
        return cand.scope_key in operation_participants(doc, idx)
    return False


# --------------------------------------------------------------------------- #
# Selection                                                                    #
# --------------------------------------------------------------------------- #
def rng_for(seed: int, instance_id: str) -> tuple[random.Random, str]:
    digest = hashlib.sha256(f"{seed}|{instance_id}".encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16)), digest


def select(
    doc: dict, gold: dict, candidates: list[Candidate], seed: int, instance_id: str
) -> tuple[Candidate | None, list[str], str, dict]:
    """Pick the fact to delete. Returns (candidate, weak_reasons, basis, trace)."""
    rng, digest = rng_for(seed, instance_id)
    answer_is_illegal = bool(gold.get("answer"))
    weak: list[str] = []
    pool = sorted(candidates, key=lambda c: c.pointer)
    trace: dict = {
        "rng_key": f"sha256({seed}|{instance_id})={digest[:16]}",
        "candidates_total": len(pool),
    }

    # G2 -- entity must take part in an operation.
    stage = [c for c in pool if participates(doc, c)]
    trace["after_participation_guard"] = len(stage)
    if stage:
        pool = stage
    elif pool:
        weak.append(
            "no candidate fact belongs to a team or player taking part in any operation"
        )

    # G3 -- when gold says a team acted illegally, stay where the violation is.
    if answer_is_illegal:
        stage = [c for c in pool if is_local(doc, c, gold)]
        trace["after_locality_guard"] = len(stage)
        if stage:
            pool = stage
            basis = "localized"
        else:
            weak.append(
                "no candidate fact is scoped to the gold problematic_team / illegal_operation, "
                "so the cited violation may remain decidable"
            )
            basis = "unlocalized"
    else:
        trace["after_locality_guard"] = len(pool)
        basis = "universal"

    # G4 -- the fact must not survive elsewhere.
    stage = [c for c in pool if not c.redundant_reasons]
    trace["after_redundancy_guard"] = len(stage)
    if stage:
        pool = stage
    elif pool:
        weak.append(
            "every remaining candidate fact survives elsewhere (duplicated under another "
            "name, or superseded by a published derived value), so the deletion may not "
            "block the decision"
        )

    if not pool:
        return None, weak, basis, trace

    # Uniform seeded choice over what cleared the guards.
    chosen = pool[rng.randrange(len(pool))]
    trace["eligible_at_selection"] = len(pool)
    trace["fan_in_of_choice"] = chosen.fan_in
    if chosen.redundant_reasons:
        weak.extend(chosen.redundant_reasons)
    return chosen, weak, basis, trace


# --------------------------------------------------------------------------- #
# Twin emission                                                                #
# --------------------------------------------------------------------------- #
def expected_decision(gold: dict) -> str:
    return "illegal" if bool(gold.get("answer")) else "legal"


def safe_id(instance_id: str) -> str:
    return SAFE_RE.sub("-", instance_id).strip("-")


def make_twins(
    doc: dict, instance_id: str, chosen: Candidate, weak: list[str], basis: str,
    trace: dict, seed: int, mapping_sha: str, policy: dict,
) -> tuple[dict, dict]:
    base_id = safe_id(instance_id)

    common = {
        "pair_id": instance_id,
        "instance_id": instance_id,
        "gold": doc.get("gold", {}),
        "provenance": doc.get("provenance", {}),
        "render_policy": policy,
    }

    redacted_facts = json.loads(json.dumps(doc["facts"]))
    removed_value = ptr_delete({"facts": redacted_facts}, chosen.pointer)
    probe = dict(common, facts=redacted_facts)
    leaks, echoes = leak_audit(probe, removed_value, policy)
    weak = list(weak)
    if leaks:
        weak.append(
            "the deleted value is still spelled out in renderable field(s): "
            + ", ".join(leaks[:4]) + ("..." if len(leaks) > 4 else "")
        )
    strength = "weak" if weak else "strong"
    shared_redaction = {
        "pointer": chosen.pointer,
        "role": chosen.role,
        "role_label": trace.get("role_label"),
        "scope": {"kind": chosen.scope_kind, "key": chosen.scope_key},
        "required_by_cited_rules": sorted(chosen.rules),
        "fan_in": chosen.fan_in,
        "strength": strength,
        "strength_basis": basis,
        "weak_reasons": weak,
        "leaks_into_renderable_fields": leaks,
        "echoed_in_render_excluded_fields": echoes,
        "in_primary_analysis": strength == "strong",
        "seed": seed,
        "selection": trace,
        "loadbearing_map_sha256": mapping_sha,
    }

    answerable = dict(common)
    answerable["twin_id"] = f"{base_id}__answerable"
    answerable["variant"] = "answerable"
    answerable["expected_decision"] = expected_decision(doc.get("gold", {}))
    answerable["expected_answer"] = bool(doc.get("gold", {}).get("answer"))
    answerable["facts"] = json.loads(json.dumps(doc["facts"]))
    answerable["redaction"] = dict(shared_redaction, applied=False,
                                   counterpart_removed_pointer=chosen.pointer)

    redacted = dict(common)
    redacted["twin_id"] = f"{base_id}__redacted"
    redacted["variant"] = "redacted"
    redacted["expected_decision"] = "cannot_decide"
    redacted["expected_answer"] = None
    redacted["facts"] = redacted_facts
    redacted["redaction"] = dict(shared_redaction, applied=True,
                                 removed_pointer=chosen.pointer,
                                 removed_value=removed_value)
    return answerable, redacted


# --------------------------------------------------------------------------- #
# I/O                                                                          #
# --------------------------------------------------------------------------- #
def load_facts_documents(path: Path) -> list[dict]:
    """Load every facts document under `path` (a directory, .json, or .jsonl file)."""
    files: list[Path] = []
    if path.is_dir():
        files = sorted(p for p in path.rglob("*") if p.suffix in (".json", ".jsonl"))
    elif path.exists():
        files = [path]
    else:
        raise SystemExit(f"--facts path does not exist: {path}")

    docs: list[dict] = []
    for file in files:
        text = file.read_text(encoding="utf-8")
        payloads: list[Any] = []
        if file.suffix == ".jsonl":
            payloads = [json.loads(line) for line in text.splitlines() if line.strip()]
        else:
            payloads = [json.loads(text)]
        for payload in payloads:
            for item in payload if isinstance(payload, list) else [payload]:
                if isinstance(item, dict) and isinstance(item.get("facts"), dict):
                    item.setdefault("_source_file", str(file))
                    docs.append(item)
    return docs


def instance_id_of(doc: dict) -> str:
    if isinstance(doc.get("instance_id"), str):
        return doc["instance_id"]
    prov = doc.get("provenance", {})
    stem = str(prov.get("file", "unknown")).removesuffix(".json")
    return f"{stem}#{int(prov.get('index', 0)):03d}"


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# Driver                                                                       #
# --------------------------------------------------------------------------- #
def run(facts_dir: Path, out_dir: Path, seed: int, map_path: Path, examples: int = 2) -> dict:
    map_bytes = map_path.read_bytes()
    mapping = json.loads(map_bytes.decode("utf-8"))
    mapping_sha = hashlib.sha256(map_bytes).hexdigest()
    policy = mapping.get("render_policy", {})

    docs = load_facts_documents(facts_dir)
    docs.sort(key=instance_id_of)

    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    skipped: list[dict] = []
    referenced_roles: set[str] = set()
    resolved_roles: set[str] = set()
    unknown_rules: set[str] = set()
    empty_derived = 0
    examples_out: list[dict] = []

    for doc in docs:
        instance_id = instance_id_of(doc)
        gold = doc.get("gold") or {}
        cited = [r for r in gold.get("relevant_rules") or [] if isinstance(r, str)]
        if not cited:
            skipped.append({"instance_id": instance_id,
                            "reason": "gold.relevant_rules is empty or absent"})
            continue

        candidates, diag = build_candidates(doc, mapping, cited)
        referenced_roles |= set(diag["referenced_roles"])
        resolved_roles |= set(diag["resolved_roles"])
        unknown_rules |= set(diag["unknown_cited_rules"])
        empty_derived += 1 if diag["derived_is_empty"] else 0
        if not candidates:
            skipped.append({
                "instance_id": instance_id,
                "reason": "no fact required by any cited rule resolves in this document",
                "cited_rules": sorted(set(cited)),
                "roles_that_did_not_resolve": sorted(
                    set(diag["referenced_roles"]) - set(diag["resolved_roles"])
                ),
            })
            continue

        chosen, weak, basis, trace = select(doc, gold, candidates, seed, instance_id)
        if chosen is None:
            skipped.append({"instance_id": instance_id,
                            "reason": "no candidate survived guard filtering"})
            continue
        trace["role_label"] = mapping["roles"][chosen.role].get("label")

        answerable, redacted = make_twins(
            doc, instance_id, chosen, weak, basis, trace, seed, mapping_sha, policy
        )
        weak = redacted["redaction"]["weak_reasons"]
        if answerable["facts"] == redacted["facts"]:
            skipped.append({"instance_id": instance_id,
                            "reason": "deletion produced an identical pair (should be "
                                      "unreachable; treated as a hard failure)"})
            continue

        base = safe_id(instance_id)
        write_json(out_dir / f"{base}__answerable.json", answerable)
        write_json(out_dir / f"{base}__redacted.json", redacted)

        rows.append({
            "pair_id": instance_id,
            "answerable_file": f"{base}__answerable.json",
            "redacted_file": f"{base}__redacted.json",
            "gold_answer": bool(gold.get("answer")),
            "answerable_expected_decision": answerable["expected_decision"],
            "redacted_expected_decision": "cannot_decide",
            "removed_pointer": chosen.pointer,
            "removed_role": chosen.role,
            "fan_in": chosen.fan_in,
            "required_by_cited_rules": sorted(chosen.rules),
            "strength": redacted["redaction"]["strength"],
            "strength_basis": basis,
            "weak_reasons": weak,
            "echoed_in_render_excluded_fields":
                redacted["redaction"]["echoed_in_render_excluded_fields"],
            "in_primary_analysis": redacted["redaction"]["in_primary_analysis"],
        })
        if len(examples_out) < examples and not weak:
            examples_out.append({
                "instance_id": instance_id,
                "pointer": chosen.pointer,
                "role": chosen.role,
                "removed_value": redacted["redaction"]["removed_value"],
                "required_by_cited_rules": sorted(chosen.rules),
                "strength_basis": basis,
            })

    strong = [r for r in rows if r["strength"] == "strong"]
    role_histogram: dict[str, int] = {}
    for row in rows:
        role_histogram[row["removed_role"]] = role_histogram.get(row["removed_role"], 0) + 1
    manifest = {
        "generator": "pipeline/redact.py",
        "seed": seed,
        "facts_dir": str(facts_dir),
        "out_dir": str(out_dir),
        "loadbearing_map": str(map_path),
        "loadbearing_map_sha256": mapping_sha,
        "render_policy": policy,
        "counts": {
            "facts_documents_read": len(docs),
            "pairs_emitted": len(rows),
            "twins_emitted": 2 * len(rows),
            "strong_pairs": len(strong),
            "weak_pairs_excluded_from_primary": len(rows) - len(strong),
            "strong_universal": sum(1 for r in strong if r["strength_basis"] == "universal"),
            "strong_localized": sum(1 for r in strong if r["strength_basis"] == "localized"),
            "instances_skipped": len(skipped),
            "answerable_twins": len(rows),
            "redacted_twins": len(rows),
            "pairs_whose_deleted_value_is_echoed_in_render_excluded_fields":
                sum(1 for r in rows if r["echoed_in_render_excluded_fields"]),
        },
        "removed_role_histogram": dict(sorted(role_histogram.items())),
        "diagnostics": {
            "roles_referenced_by_cited_rules": sorted(referenced_roles),
            "roles_that_never_resolved_anywhere": sorted(referenced_roles - resolved_roles),
            "cited_rules_absent_from_map": sorted(unknown_rules),
            "documents_with_empty_facts_derived": empty_derived,
            "note_on_empty_derived": (
                "The derived-supersession guard (G4b) can only fire where facts.derived is "
                "populated. Re-run this operator after the deterministic preprocessor lands "
                "so that twins whose deleted fact is recoverable from a published derived "
                "quantity are reclassified as weak."
            ) if empty_derived else None,
        },
        "skipped": skipped,
        "pairs": rows,
        "examples": examples_out,
    }
    write_json(out_dir / "manifest.json", manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(
        description="Emit answerable/redacted twin pairs from parsed facts documents."
    )
    ap.add_argument("--facts", type=Path, default=here / "out" / "facts",
                    help="directory of facts documents (or a .json/.jsonl file)")
    ap.add_argument("--out", type=Path, default=here / "out" / "twins",
                    help="output directory for twins and manifest.json")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--map", type=Path, default=here / "loadbearing_map.json",
                    help="rule -> required-fact table")
    ap.add_argument("--examples", type=int, default=2,
                    help="how many before/after examples to print")
    args = ap.parse_args(argv)

    manifest = run(args.facts, args.out, args.seed, args.map, args.examples)
    counts = manifest["counts"]
    print(f"seed                       : {manifest['seed']}")
    print(f"loadbearing_map sha256     : {manifest['loadbearing_map_sha256'][:16]}...")
    print(f"facts documents read       : {counts['facts_documents_read']}")
    print(f"pairs emitted              : {counts['pairs_emitted']} "
          f"({counts['twins_emitted']} twins: "
          f"{counts['answerable_twins']} answerable / {counts['redacted_twins']} redacted)")
    print(f"strong pairs (primary)     : {counts['strong_pairs']} "
          f"(universal {counts['strong_universal']}, localized {counts['strong_localized']})")
    print(f"weak pairs (excluded)      : {counts['weak_pairs_excluded_from_primary']}")
    print(f"instances skipped          : {counts['instances_skipped']}")
    diag = manifest["diagnostics"]
    hist = manifest["removed_role_histogram"]
    print(f"distinct fact roles deleted: {len(hist)}")
    for role, n in sorted(hist.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"    {n:4d}  {role}")
    if diag["roles_that_never_resolved_anywhere"]:
        print("roles that never resolved  : "
              f"{', '.join(diag['roles_that_never_resolved_anywhere'])}")
    if diag["cited_rules_absent_from_map"]:
        print(f"cited rules absent from map: {', '.join(diag['cited_rules_absent_from_map'])}")
    echoed = counts["pairs_whose_deleted_value_is_echoed_in_render_excluded_fields"]
    if echoed:
        print(f"REQUIRED OF THE HARNESS: {echoed} pair(s) echo the deleted value in prose "
              "under the render-excluded pointers (operations[].raw, provenance). A renderer "
              "that shows those fields invalidates every redacted twin.")
    if diag["documents_with_empty_facts_derived"]:
        print("WARNING: facts.derived is empty in "
              f"{diag['documents_with_empty_facts_derived']} document(s); the "
              "derived-supersession guard could not fire. Re-run after the preprocessor lands.")
    for ex in manifest["examples"]:
        print()
        print(f"example  {ex['instance_id']}  [{ex['strength_basis']}]")
        print(f"  before : {ex['pointer']} = {json.dumps(ex['removed_value'], ensure_ascii=False)}")
        print(f"  after  : {ex['pointer']} absent  (role {ex['role']})")
        print(f"  needed by: {', '.join(ex['required_by_cited_rules'])}")
    if not manifest["examples"]:
        print("\n(no strong pair available to show as an example)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
