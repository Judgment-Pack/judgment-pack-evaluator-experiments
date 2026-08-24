"""Admission — and the reconciliation the pilot's three codes owed section 1a.

ASSEMBLED FROM `design/pilot/pilot_run.py`
(sha256 `09da06b334f6b3ae3224b03f6e49e2f0f3c5519401e94e72f23df7333cffd295`),
`admit_arm_a()` (242-275) and `admit_arm_rego()` (276-315). `harness/PORTS.md`
carries the two-sided row.

THE RECONCILIATION (harness/SCAFFOLD.md item S2, and it is not mechanical)
--------------------------------------------------------------------------
The prototype's `DROP_ORDER` has THREE codes — `no-marker`, `unparseable`,
`invalid-artifact` — and PREREGISTRATION.md section 1a registers SIX authoring
outcomes. `invalid-artifact` is the one that splits, and it splits by WHICH
CHECK REFUSED, not by a judgement about the artifact:

| section 1a code | arm A | arms B/C |
|---|---|---|
| `no-marker-block` | no governing `PACK:` fence | no governing `POLICY:` fence |
| `unparseable-artifact` | the block is not JSON | `opa check` fails with only `rego_parse_error`, AND the same bytes also fail under `--v0-compatible` |
| `schema-invalid-pack` | `jpack spec validate` reports `status != "valid"` | — (arm-structural: a Rego file has no pack schema) |
| `opa-check-failed` | — (arm-structural) | `opa check` fails with any non-parse error (type / compile / capability) |
| `v0-syntax` | — (arm-structural) | `opa check` fails with only `rego_parse_error` AND the same bytes pass under `--v0-compatible` |
| `unreadable-output-shape` | the validator emitted no JSON payload at all | `opa check` emitted no readable error document |

The `v0-syntax` discriminator is the one piece with no prototype, and it is
built to be MECHANICAL rather than prose-reading. Section 2 pins Rego v1 in both
the prompt and the invocation, so a v0 policy is a registered authoring outcome
distinct from a garbled one — but at v1.19.0 both surface as
`rego_parse_error`, and the messages that distinguish them ("`if` keyword is
required before rule body") are upstream's wording, which this study does not
put in its published record. What the pinned binary offers instead is a second
compilation: `opa check --v0-compatible` on the same bytes. Bytes that fail
under v1 and compile under v0 ARE v0 syntax, by the compiler's own reading; a
second failure means the artifact is unparseable in either dialect. The
discriminator is therefore two invocations of the pinned binary and no string
matching, and `tests/test_score.py` exercises both branches.

Two arm-structural absences are deliberate, and PREREGISTRATION.md section 5
requires them to be enforced rather than merely unlikely: `schema-invalid-pack`
cannot arise in arms B/C and `opa-check-failed`/`v0-syntax` cannot arise in arm
A. `ARM_REACHABLE_CODES` states that, and `admit()` refuses to return a code its
own arm cannot reach — an arm-structural category leaking across arms would make
the E2 table compare two different partitions.

NO REPAIR OF ANY KIND, EVER (section 3: "single-shot, no tools, no repair"). If
a block is not admitted it is not fixed, retried, or re-fenced; it scores zero
on every endpoint it reaches and stays in the denominator (section 1a).

STUDY 020, §7 DELTA 3 — THE SEVENTH CODE, AND WHY IT IS NOT ON BY DEFAULT
-------------------------------------------------------------------------
§3.2 registers `presence-idiom-unsound` as an eighth authoring outcome in §1a's
table and the seventh ADMISSION code here: an arm-B/arm-C policy whose `in`
operand is an object on the syntax tree tests values, not keys, and the run is
valid, counted, and scores zero. It is the only code decided AFTER the artifact
was admitted — `opa check` has already passed — so it is last in `DROP_ORDER`
and it is decided by a detector this module does not own (`e4lib/presence_idiom`).

The guard arrives as an OBJECT, not as a flag: §3.2 makes it a
`GATE(pre-freeze)` and its `TODO(prereg)` block is still open, so
`presence_idiom.attempt_guard()` hands back `None` and `admit()` cannot return
the code. A caller who passes anything other than `None` or an activated
`Guard` is refused here rather than accommodated — the registration's condition
for the code entering the population is the gate, and a duck-typed stand-in
would route around it. §11.11's arm asymmetry is carried the way every other
arm-structural category is: the code is in B's and C's reachable sets and not
in A's, so a leak is the existing `ADMIT-ARM-STRUCTURAL-LEAK` refusal.
"""
from __future__ import annotations

import json
import os

from . import engines
from . import presence_idiom

# Section 1a's authoring outcomes in the ORDER the E2 table publishes them,
# which is also the order `admit()` decides in: an artifact that is both
# unparseable and schema-invalid is unparseable, because the earlier check is
# the one that actually refused.
DROP_ORDER = (
    "no-marker-block",
    "unparseable-artifact",
    "v0-syntax",
    "schema-invalid-pack",
    "opa-check-failed",
    "unreadable-output-shape",
    # §7 delta 3. LAST, and the position is the decision rather than a
    # preference: every code above is a reason the artifact was never admitted,
    # and this one is read off a policy `opa check` already accepted.
    presence_idiom.CODE,
)

# Which of those an arm can structurally reach. Section 5: "arm-structural
# categories within-arm-only, enforced in the scorer."
ARM_REACHABLE_CODES = {
    "A": ("no-marker-block", "unparseable-artifact", "schema-invalid-pack",
          "unreadable-output-shape"),
    "B": ("no-marker-block", "unparseable-artifact", "v0-syntax",
          "opa-check-failed", "unreadable-output-shape", presence_idiom.CODE),
    "C": ("no-marker-block", "unparseable-artifact", "v0-syntax",
          "opa-check-failed", "unreadable-output-shape", presence_idiom.CODE),
}

PARSE_ERROR_CODE = "rego_parse_error"
UNREADABLE_CHECK_OUTPUT = "unparseable-check-output"


class AdmissionError(Exception):
    """A refusal about the admission layer itself — never about an artifact."""


def admit_arm_a(tools: engines.Toolchain, block: str, workdir: str) -> tuple:
    """`(pack_path or None, code or None, detail)` for a Judgment Pack.

    Two checks in the registered order: JSON, then `jpack spec validate
    --format json` read through the payload's `status` and never through the
    exit code (section 2). Diagnostics are recorded as CODES, LAYERS and
    INSTANCE PATHS only — never message prose, for the same reason the Rego side
    records error codes only."""
    detail = {}
    try:
        json.loads(block)
    except ValueError as error:
        detail["parseError"] = type(error).__name__
        return None, "unparseable-artifact", detail
    path = os.path.join(workdir, "pack.json")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(block)
    payload, code, _out, _err = engines.jpack_json(
        tools, ["spec", "validate", path, "--format", "json"], workdir)
    if payload is None:
        detail["validateExit"] = code
        return None, "unreadable-output-shape", detail
    detail["validateStatus"] = payload.get("status")
    if payload.get("status") != "valid":
        detail["diagnostics"] = [
            {key: entry.get(key)
             for key in ("code", "layer", "instancePath") if key in entry}
            for entry in (payload.get("diagnostics") or [])
            if entry.get("severity") == "error"
        ][:10]
        detail["failedLayers"] = [
            layer.get("name") for layer in (payload.get("layers") or [])
            if layer.get("status") == "failed"
        ]
        return None, "schema-invalid-pack", detail
    return path, None, detail


def admit_arm_rego(tools: engines.Toolchain, block: str, workdir: str) -> tuple:
    """`(policy_path or None, code or None, detail)` for a Rego v1 policy."""
    detail = {}
    if not block.strip():
        return None, "unparseable-artifact", detail
    path = os.path.join(workdir, "policy.rego")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(block)
    code, codes = engines.opa_check(tools, path, workdir)
    detail["checkExit"] = code
    detail["checkErrorCodes"] = codes
    if code == 0:
        return path, None, detail
    if codes == [UNREADABLE_CHECK_OUTPUT]:
        return None, "unreadable-output-shape", detail
    if codes and all(one == PARSE_ERROR_CODE for one in codes):
        v0_code, v0_codes = engines.opa_check(tools, path, workdir,
                                              v0_compatible=True)
        detail["v0CompatibleExit"] = v0_code
        detail["v0CompatibleErrorCodes"] = v0_codes
        if v0_code == 0:
            return None, "v0-syntax", detail
        return None, "unparseable-artifact", detail
    return None, "opa-check-failed", detail


def admit(tools: engines.Toolchain, arm: str, block, workdir: str,
          guard=None) -> tuple:
    """The one admission entry point. `block` may be `None`, which is the
    extraction layer's `no-marker-block` reaching admission unchanged.

    `guard` is §3.2's presence-idiom guard, and `None` — the state this study is
    registered in until the pre-freeze power analysis lands — means the seventh
    code is unreachable. Anything else must be an activated
    `presence_idiom.Guard`; see this module's header for why the type is the
    check.

    The returned code is checked against the arm's structurally reachable set
    before it is returned, so a cross-arm leak is a refusal here rather than a
    row in the published E2 table."""
    if arm not in ARM_REACHABLE_CODES:
        raise AdmissionError("ADMIT-UNKNOWN-ARM %r is not one of %s"
                             % (arm, ", ".join(sorted(ARM_REACHABLE_CODES))))
    if guard is not None and not isinstance(guard, presence_idiom.Guard):
        raise AdmissionError(
            "ADMIT-UNACTIVATED-GUARD the presence-idiom guard is a %s and not "
            "an activated presence_idiom.Guard; §3.2 registers the code behind "
            "a GATE(pre-freeze), and an object that merely answers like a guard "
            "would put %r into the population without the power analysis the "
            "gate is" % (type(guard).__name__, presence_idiom.CODE))
    if block is None:
        return None, "no-marker-block", {}
    if arm == "A":
        artifact, code, detail = admit_arm_a(tools, block, workdir)
    else:
        artifact, code, detail = admit_arm_rego(tools, block, workdir)
    if code is None and guard is not None and arm in presence_idiom.ARMS:
        # NO REPAIR: the verdict adds a code, and never a rewritten operator.
        # The artifact is discarded with the code exactly as every branch above
        # discards it, because a flagged run scores zero rather than evaluating.
        code, report = guard.verdict(tools, arm, artifact, workdir)
        detail["presenceIdiom"] = report
        if code is not None:
            artifact = None
    if code is not None and code not in ARM_REACHABLE_CODES[arm]:
        raise AdmissionError(
            "ADMIT-ARM-STRUCTURAL-LEAK arm %s returned %r, which section 5 makes "
            "an arm-structural category of another arm; the E2 tables would then "
            "compare two different partitions" % (arm, code))
    return artifact, code, detail
