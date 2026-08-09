"""Integration mutations M7-M15a — each flips exactly one hook in the shared shell.

Judgment-semantic mutations M1-M6 are mutated PACK bytes (scenarios/mutations/packs/,
produced by harness/mutate_packs.py) evaluated through the UNMUTATED shell via
pack_override. The mutations here are the reverse: correct packs, defective
integration. MATRIX.json registers, per mutation, the target cases and which
detection layer (J = judgment tooling, F = Forge deterministic scorers,
G = study gate) is expected to catch it.
"""

import copy
import os

from shell import PROTECTED_TOOL


def _default_execute(action_map):
    outcome = sorted(o for o, m in action_map.items() if m.startswith("execute:"))[0]
    return outcome, action_map[outcome].split(":", 1)[1]


def _execute_anyway(case, action_map):
    outcome, name = _default_execute(action_map)
    return {
        "tool": PROTECTED_TOOL,
        "args": {"case_id": case["id"], "action": name, "outcome": outcome},
    }


def m07_wrong_source_fact(case, facts):
    """Wrong source field wired to the appropriateness input (triage packs)."""
    facts = copy.deepcopy(facts)
    if "request" in facts and "completeness" in facts["request"]:
        facts["request"]["appropriateness"] = facts["request"]["completeness"]
    return facts


def m08_wrong_path(case, facts):
    """Correct facts nested under the wrong root pointer."""
    return {"req": copy.deepcopy(facts.get("request", facts))}


def m08b_number_amount(case, facts):
    """Decimal-string amount emitted as a JSON number (fee pack)."""
    facts = copy.deepcopy(facts)
    amount = facts.get("request", {}).get("amount")
    if isinstance(amount, str):
        facts["request"]["amount"] = float(amount)
    return facts


def m09_unknown_collapsed_to_absent(case, evidence):
    """Evidence mapper collapses unknown to absent (triage requirement ids)."""
    if evidence is None:
        return {"intake-form": "absent", "sponsor-endorsement": "absent"}
    return {k: ("absent" if v == "unknown" else v) for k, v in evidence.items()}


def m10_ignore_unresolved(case, disposition, action, action_map):
    if disposition and disposition["kind"] == "unresolved":
        return _execute_anyway(case, action_map)
    return action


def m11_ignore_handoff(case, disposition, action, action_map):
    if disposition and disposition.get("handoff", {}).get("state") == "requested":
        return _execute_anyway(case, action_map)
    return action


def m12_execute_despite_nonproceed(case, disposition, action, action_map):
    if disposition and disposition["kind"] == "outcome" and action["tool"] == "record_decision":
        return _execute_anyway(case, action_map)
    return action


def m13_wrong_tool(case, disposition, action, action_map):
    if action["tool"] == "record_decision":
        return {"tool": "open_review", "args": dict(action["args"], target="unspecified")}
    return action


def m14_wrong_args(case, disposition, action, action_map):
    if action["tool"] == PROTECTED_TOOL:
        action = {"tool": action["tool"], "args": dict(action["args"])}
        action["args"]["action"] = action["args"]["action"] + "-wrong"
    return action


def m15a_stale_pack(case, pack_path):
    """Evaluate a byte-frozen pack re-declared under 0.1.0-draft (preflight refusal)."""
    return os.path.join(
        os.path.dirname(os.path.dirname(pack_path)),
        "scenarios", "mutations", "packs", "m15a-" + os.path.basename(pack_path),
    )


CONFIGS = {
    "m01": {"arm": "b", "pack_mutation": "m01"},
    "m02": {"arm": "b", "pack_mutation": "m02"},
    "m03": {"arm": "b", "pack_mutation": "m03"},
    "m04": {"arm": "b", "pack_mutation": "m04"},
    "m05": {"arm": "b", "pack_mutation": "m05"},
    "m06": {"arm": "b", "pack_mutation": "m06"},
    "m07": {"arm": "b", "hooks": {"pre_facts": m07_wrong_source_fact}},
    "m08": {"arm": "b", "hooks": {"pre_facts": m08_wrong_path}},
    "m08b": {"arm": "b", "hooks": {"pre_facts": m08b_number_amount}},
    "m09": {"arm": "b", "hooks": {"pre_evidence": m09_unknown_collapsed_to_absent}},
    "m10": {"arm": "b", "hooks": {"post_action": m10_ignore_unresolved}},
    "m11": {"arm": "b", "hooks": {"post_action": m11_ignore_handoff}},
    "m12": {"arm": "b", "hooks": {"post_action": m12_execute_despite_nonproceed}},
    "m13": {"arm": "b", "hooks": {"post_action": m13_wrong_tool}},
    "m14": {"arm": "b", "hooks": {"post_action": m14_wrong_args}},
    "m15a": {"arm": "b", "hooks": {"pack_override": m15a_stale_pack}},
}


def pack_mutation_override(mutation):
    def override(case, pack_path):
        return os.path.join(
            os.path.dirname(os.path.dirname(pack_path)),
            "scenarios", "mutations", "packs", mutation + "-" + os.path.basename(pack_path),
        )
    return override


def build_config(mutation):
    config = dict(CONFIGS[mutation])
    config["mutation"] = mutation
    if "pack_mutation" in config:
        config["hooks"] = {"pack_override": pack_mutation_override(mutation)}
    return config
