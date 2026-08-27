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

(R1-1: `unreadable-output-shape` — the validator emitting no payload, `opa check` emitting no
readable error document — is RETIRED from this table: every such state is the pinned engine
failing to ANSWER, which is apparatus, raised from here as `engines.EngineError` and filed by
the scorer under `engine-invocation-refused`.)

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
"""
from __future__ import annotations

import json
import os

from . import engines, presence_idiom

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
    # NEW IN 020 (§3.2, ruling M-14). It is LAST in the order for a reason that
    # is not cosmetic: the detector runs on a policy the pinned binary has
    # already accepted, so every earlier code describes an artifact that never
    # reached it. An artifact that is both unparseable and presence-idiom-
    # unsound is unparseable, because the earlier check is the one that refused.
    presence_idiom.CODE,
)

# Which of those an arm can structurally reach. Section 5: "arm-structural
# categories within-arm-only, enforced in the scorer."
ARM_REACHABLE_CODES = {
    "A": ("no-marker-block", "unparseable-artifact", "schema-invalid-pack"),
    # `presence-idiom-unsound` is B/C only, and §11.11 registers that asymmetry
    # as a CEILING rather than repairing it: arm A's format has no analogous
    # single-operator trap on this surface, so the code is structurally
    # unreachable there and `admit()` refuses it as an arm-structural leak.
    "B": ("no-marker-block", "unparseable-artifact", "v0-syntax",
          "opa-check-failed", presence_idiom.CODE),
    "C": ("no-marker-block", "unparseable-artifact", "v0-syntax",
          "opa-check-failed", presence_idiom.CODE),
}

PARSE_ERROR_CODE = "rego_parse_error"
UNREADABLE_CHECK_OUTPUT = "unparseable-check-output"


def _refuse_json_constant(token: str):
    """ROUND-2 FINDING R2-9: JSON has no `NaN`/`Infinity` literal and
    Python's decoder accepts all three anyway. A non-finite value
    silently defeats every comparison a gate makes against it, so no
    reader of a registered document accepts one. `integrity.py` carries
    the same rule for the modules that can import it."""
    raise ValueError(
        "JSON-NONFINITE a registered document carries the JSON-invalid "
        "token %r" % (token,))


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
    payload, code, _out, _err, refusal = engines.jpack_json(
        tools, ["spec", "validate", path, "--format", "json"], workdir)
    if refusal is not None:
        # R1-1: no answer at all — apparatus, never an authoring code.
        raise engines.EngineError(
            "ENGINE-INVOCATION-REFUSED jpack spec validate produced no answer "
            "(%s, exit %s): §1a files an invocation the engine never answered "
            "on the apparatus side" % (refusal, code))
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


def admit_arm_rego(tools: engines.Toolchain, block: str, workdir: str,
                   guard_registered: bool = None) -> tuple:
    """`(policy_path or None, code or None, detail)` for a Rego v1 policy.

    `guard_registered` is §3.2's kill switch, read as data rather than as a
    comment: the presence-idiom detector produces a REGISTERED authoring code
    only if its pre-freeze power analysis met (i) and (ii) exactly. When the
    switch is off the detector still RUNS and its census still lands in
    `detail`, because §3.2's fallback is that the mechanism is carried as a
    Tier D descriptive finding — what is withheld is the CODE, not the
    measurement. `None` resolves the switch from the registry."""
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
        # §3.2, and the ORDER is load-bearing: the detector reads a policy the
        # pinned binary has already accepted, so it can never turn a compile
        # failure into a presence-idiom verdict. It is a detector and not a
        # repair — the artifact is not rewritten, the run is not excluded, and a
        # flagged run stays in every ITT denominator scoring zero.
        # ROUND-2 FINDING R2-1: the detector's own refusal is APPARATUS. Every
        # no-answer exit already raises `engines.EngineError` inside
        # `opa_parse_tree()`; what reaches here as a `PresenceIdiomError` is the
        # residual disagreement — `opa check` accepted these bytes and
        # `opa parse` refused them — and a disagreement between the study's two
        # pinned invocations about one artifact yields no verdict about the
        # AUTHOR either. It leaves by the same typed door, so §1a's partition
        # sees one apparatus state and not two.
        try:
            report = presence_idiom.scan(tools, path, workdir)
        except presence_idiom.PresenceIdiomError as refusal:
            raise engines.EngineError(
                "ENGINE-INVOCATION-REFUSED the two pinned invocations disagree "
                "about the same bytes: `opa check` accepted the policy and "
                "`opa parse` refused it, so no verdict about the author's "
                "artifact survives (%s)" % refusal)
        detail["presenceIdiom"] = {
            "flagged": report["flagged"],
            "memberships": report["memberships"],
            "findings": report["findings"][:10],
            "lawful": len(report["lawful"]),
            "unclassified": report["unclassified"][:10],
        }
        registered = (guard_is_registered() if guard_registered is None
                      else bool(guard_registered))
        detail["presenceIdiom"]["guardRegistered"] = registered
        if report["flagged"] and registered:
            return None, presence_idiom.CODE, detail
        return path, None, detail
    if codes == [UNREADABLE_CHECK_OUTPUT]:
        # R1-1: a nonzero `opa check` whose streams carry no readable error
        # document is the pinned binary failing to render its own verdict —
        # apparatus, never an authoring code.
        raise engines.EngineError(
            "ENGINE-INVOCATION-REFUSED opa check exited %s with no readable "
            "error document: the invocation rendered no verdict about the "
            "artifact (R1-1)" % code)
    if codes and all(one == PARSE_ERROR_CODE for one in codes):
        v0_code, v0_codes = engines.opa_check(tools, path, workdir,
                                              v0_compatible=True)
        detail["v0CompatibleExit"] = v0_code
        detail["v0CompatibleErrorCodes"] = v0_codes
        if v0_code == 0:
            return None, "v0-syntax", detail
        return None, "unparseable-artifact", detail
    return None, "opa-check-failed", detail


GUARD_PIN_PATH = ("presenceIdiomGuard", "registered")


def guard_is_registered(pins: dict = None) -> bool:
    """§3.2's kill switch, from `harness/PINS.json`.

    The preregistration registers the guard CONDITIONALLY — "if the detector
    cannot meet (i) and (ii) exactly, the guard is not registered at all" — and
    a conditional registration whose condition lives in prose is a condition
    nothing enforces. `PINS.json`'s `presenceIdiomGuard.registered` carries the
    power analysis's verdict as data, and this is the only place it is read.

    FAIL-SHUT toward NOT REGISTERED: a registry with no such member, or one
    whose member is anything other than `true`, does not emit the code. A guard
    is registered by a published power analysis, never by a missing key."""
    if pins is None:
        pins = _registry()
    node = pins
    for key in GUARD_PIN_PATH:
        node = node.get(key) if isinstance(node, dict) else None
    return node is True


def _registry() -> dict:
    """`harness/PINS.json`, read once and cached. Local import so this module
    keeps its one-way dependency on `engines` and adds no import-time cost to a
    scorer that never reaches admission."""
    global _REGISTRY
    if _REGISTRY is None:
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(here, "PINS.json"), "rb") as handle:
            _REGISTRY = json.loads(handle.read().decode("utf-8"),
                                   parse_constant=_refuse_json_constant)
    return _REGISTRY


_REGISTRY = None


def admit(tools: engines.Toolchain, arm: str, block, workdir: str,
          guard_registered: bool = None) -> tuple:
    """The one admission entry point. `block` may be `None`, which is the
    extraction layer's `no-marker-block` reaching admission unchanged.

    The returned code is checked against the arm's structurally reachable set
    before it is returned, so a cross-arm leak is a refusal here rather than a
    row in the published E2 table."""
    if arm not in ARM_REACHABLE_CODES:
        raise AdmissionError("ADMIT-UNKNOWN-ARM %r is not one of %s"
                             % (arm, ", ".join(sorted(ARM_REACHABLE_CODES))))
    if block is None:
        return None, "no-marker-block", {}
    if arm == "A":
        artifact, code, detail = admit_arm_a(tools, block, workdir)
    else:
        artifact, code, detail = admit_arm_rego(tools, block, workdir,
                                                guard_registered)
    if code is not None and code not in ARM_REACHABLE_CODES[arm]:
        raise AdmissionError(
            "ADMIT-ARM-STRUCTURAL-LEAK arm %s returned %r, which section 5 makes "
            "an arm-structural category of another arm; the E2 tables would then "
            "compare two different partitions" % (arm, code))
    return artifact, code, detail
