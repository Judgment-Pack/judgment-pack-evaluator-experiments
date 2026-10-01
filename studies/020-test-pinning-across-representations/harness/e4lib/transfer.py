"""Section 2a.5's transfer gate, C4 — the pilot-versus-batch comparison that
decides §5.9's row 1 (pipeline-invalid) or row 3 (calibration-invalid).

ROUND-2 FINDING R2-11: `decision.CONTROL_GATES` required
`c4-transfer-calibration`, `score.py` never created it, and no production code
read the pilot at attempt time — so EVERY attempt failed as "not evaluated"
and neither registered branch could occur. This module is the producer that
did not exist. It carries NO number of its own choosing: the eight exact rows
and the two band rows are transcribed from §2a.5's table, quoted here.

    | model, CLI version, binary sha256, reasoning effort | exact equality |
    | sandbox policy, codexHomeIsolated, environmentScrubbed, isolation
      inventory | exact equality |
    | per-arm median call duration | [0.80x, 1.25x] |
    | per-arm median completion bytes | [0.80x, 1.25x] |

THE REASONING-TOKEN BAND ROW IS NOT TAKEN (maintainer ruling, round 2,
R2-11(A)). §2a.5's first printing registered a third band row, per-arm median
`reasoning_output_tokens` in [0.65x, 1.55x], and §2.1's M-24 fill registered
the self-report band as "NOT taken" once the witness resolution landed on the
gate-5-extension branch — the two sentences contradicted each other about a
registered quantity. The ruling: two band rows. The per-arm token median is
still PUBLISHED on both sides as a descriptive quantity that no gate reads,
so the comparison a reader may want is on the record without deciding
anything.

THREE CONVENTIONS §2a.5 DID NOT CARRY IN ITS OWN BYTES, fixed here and
amended into the section (R2-11(B)):

* the COHORT is executed calls only — a slot whose wrapper wrote a CALL.json
  with a resolvable duration (`durationSeconds`, or `startedAt`/`endedAt`).
  design/BRIEF.md's own cohort definition: the exit-126 records carried
  `durationSeconds: null` and were outside the triple;
* the MEDIAN at even n is the mean of the two middles (`statistics.median`),
  stated because the pilot's n is 12;
* the RATIO is pilot ÷ batch, so the 019 mismatch reads 8.3-10.7x for
  duration exactly as §2a.5's power column prints it. The band is CLOSED at
  both ends.

TWO-SIDED ROUTING, in this order: any exact row unequal (or a side that
disagrees with ITSELF on an exact row) is `pipeline-invalid` — the BATCH is
suspect, row 1 — and the band rows are still computed and published, never
suppressed; otherwise any band cell out of band OR not evaluable is
`calibration-invalid` — the PILOT is suspect, row 3; otherwise `hold`.

The pilot side of the comparison is `calibration/<label>/C4-REFERENCE.json`,
published by `harness/pilot_analysis.py` after the pilot and pinned at
`calibration.c4ReferenceSha256` before the freeze, because the pilot's
CALL.json bytes were pinned by nothing and the gate's reference would
otherwise be unpinned bytes.
"""
from __future__ import annotations

import datetime
import statistics

ARMS = ("A", "B", "C")

#: §2a.5's exact-equality rows, in the table's order. Each is a name and the
#: CALL.json member it is read from (`sandboxPolicy` is the argv token after
#: `--sandbox`; the wrapper emits it only inside `argv`).
REGISTERED_EXACT_ROWS = (
    "model", "cliVersion", "binarySha256", "reasoningEffort",
    "sandboxPolicy", "codexHomeIsolated", "environmentScrubbed",
    "isolatedHomeInventory",
)

#: §2a.5's band rows, as amended (two rows): name, (low, high), closed.
REGISTERED_BANDS = (
    ("callDurationSeconds", (0.80, 1.25)),
    ("completionBytes", (0.80, 1.25)),
)

#: Published beside the band rows, read by no gate (R2-11(A)'s ruling).
DESCRIPTIVE_MEDIANS = ("reasoningOutputTokens",)

OUTCOME_HOLD = "hold"
OUTCOME_PIPELINE_INVALID = "pipeline-invalid"
OUTCOME_CALIBRATION_INVALID = "calibration-invalid"

REFERENCE_NAME = "C4-REFERENCE.json"


class TransferError(Exception):
    """A refusal about the gate's inputs — never a verdict about the arms."""


def _parse_iso(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None


def duration_seconds(call):
    """The call's duration, from `durationSeconds` when the record carries one
    and from `startedAt`/`endedAt` otherwise; None when neither resolves."""
    if not isinstance(call, dict):
        return None
    value = call.get("durationSeconds")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    started, ended = _parse_iso(call.get("startedAt")), _parse_iso(
        call.get("endedAt"))
    if started is None or ended is None:
        return None
    return (ended - started).total_seconds()


def executed(call) -> bool:
    """The registered cohort: executed calls only."""
    return duration_seconds(call) is not None


def call_members(call) -> dict:
    """The exact-row values of one CALL.json, in a JSON-stable form, plus the
    duration. Everything the gate reads from a slot's wrapper record, read in
    ONE place so `score.read_slot()` and `pilot_analysis.py` cannot hold two
    readings of the same member."""
    if not isinstance(call, dict):
        return None
    argv = call.get("argv") or []
    sandbox = None
    if isinstance(argv, list):
        for index, token in enumerate(argv[:-1]):
            if token == "--sandbox":
                sandbox = argv[index + 1]
                break
    inventory = call.get("isolatedHomeInventory")
    if isinstance(inventory, list):
        inventory = sorted(str(item) for item in inventory)
    return {
        "model": call.get("model"),
        "cliVersion": call.get("cli"),
        "binarySha256": call.get("binarySha256"),
        "reasoningEffort": call.get("reasoningEffort"),
        "sandboxPolicy": sandbox,
        "codexHomeIsolated": call.get("codexHomeIsolated"),
        "environmentScrubbed": call.get("environmentScrubbed"),
        "isolatedHomeInventory": inventory,
        "durationSeconds": duration_seconds(call),
    }


def median(values):
    """`statistics.median` — the mean of the two middles at even n."""
    values = [float(value) for value in values if value is not None]
    if not values:
        return None
    return float(statistics.median(values))


def observables(slots_by_arm: dict) -> dict:
    """One side's observables. `slots_by_arm` maps an arm to records carrying
    `call` (the `call_members()` block or None), `completionBytes` (int or
    None) and `reasoningOutputTokens` (int or None).

    The exact tuple must be internally CONSTANT across every executed call on
    the side; a side that disagrees with itself is its own named problem, and
    it is published as one rather than resolved by picking a value."""
    exact = {}
    problems = []
    per_arm = {}
    for arm in ARMS:
        records = [record for record in (slots_by_arm.get(arm) or [])
                   if executed(record.get("call"))]
        for record in records:
            for row in REGISTERED_EXACT_ROWS:
                value = record["call"].get(row)
                if row not in exact:
                    exact[row] = value
                elif exact[row] != value:
                    problems.append(
                        "exact row %s disagrees within this side: %r vs %r "
                        "(arm %s)" % (row, exact[row], value, arm))
        per_arm[arm] = {
            "executed": len(records),
            "medians": {
                "callDurationSeconds": median(
                    record["call"]["durationSeconds"] for record in records),
                "completionBytes": median(
                    record.get("completionBytes") for record in records),
                "reasoningOutputTokens": median(
                    record.get("reasoningOutputTokens") for record in records),
            },
        }
    for row in REGISTERED_EXACT_ROWS:
        exact.setdefault(row, None)
    return {"exact": exact, "exactProblems": sorted(set(problems)),
            "perArm": per_arm}


def reference_document(label: str, obs: dict) -> dict:
    """`C4-REFERENCE.json`'s shape: the pilot side, labelled and uncitable."""
    return {
        "label": label,
        "citable": False,
        "obligation": "PREREGISTRATION.md section 2a.5 — the pilot side of the "
                      "transfer gate C4, published after the pilot and pinned "
                      "at calibration.c4ReferenceSha256 before the freeze "
                      "(round-2 finding R2-11)",
        "exactRows": list(REGISTERED_EXACT_ROWS),
        "bands": [{"row": row, "low": low, "high": high, "closed": True}
                  for row, (low, high) in REGISTERED_BANDS],
        "descriptiveMedians": list(DESCRIPTIVE_MEDIANS),
        "exact": obs["exact"],
        "exactProblems": obs["exactProblems"],
        "perArm": obs["perArm"],
    }


def validate_reference(document) -> dict:
    """The reference's registered shape, refused by name."""
    if not isinstance(document, dict):
        raise TransferError("C4-REFERENCE the reference is not an object")
    if document.get("citable") is not False:
        raise TransferError("C4-REFERENCE the reference must say citable: false")
    if not isinstance(document.get("label"), str) or not document["label"]:
        raise TransferError("C4-REFERENCE the reference names no pilot label")
    exact = document.get("exact")
    if not isinstance(exact, dict):
        raise TransferError("C4-REFERENCE the reference carries no exact block")
    for row in REGISTERED_EXACT_ROWS:
        if exact.get(row) is None:
            raise TransferError(
                "C4-REFERENCE exact row %s is null on the pilot side: a gate "
                "the scorer cannot evaluate fails (section 6)" % row)
    if document.get("exactProblems"):
        raise TransferError(
            "C4-REFERENCE the pilot side disagrees with itself on an exact "
            "row: %s" % "; ".join(document["exactProblems"]))
    per_arm = document.get("perArm")
    if not isinstance(per_arm, dict) or sorted(per_arm) != sorted(ARMS):
        raise TransferError("C4-REFERENCE the reference's arms are not A, B, C")
    for arm in ARMS:
        cell = per_arm[arm]
        if not isinstance(cell.get("executed"), int) or cell["executed"] < 1:
            raise TransferError(
                "C4-REFERENCE arm %s has no executed pilot call; every band "
                "row would be unevaluable there" % arm)
        for row, _band in REGISTERED_BANDS:
            if (cell.get("medians") or {}).get(row) is None:
                raise TransferError(
                    "C4-REFERENCE arm %s's %s median is null on the pilot side"
                    % (arm, row))
    return document


def compare(reference: dict, batch_obs: dict) -> dict:
    """The two-sided comparison. `reference` is the validated pilot document;
    `batch_obs` is `observables()` over the attempt's present slots."""
    exact_rows = []
    for row in REGISTERED_EXACT_ROWS:
        pilot = (reference.get("exact") or {}).get(row)
        batch = (batch_obs.get("exact") or {}).get(row)
        exact_rows.append({"row": row, "pilot": pilot, "batch": batch,
                           "equal": pilot is not None and pilot == batch})
    band_rows = []
    for row, (low, high) in REGISTERED_BANDS:
        for arm in ARMS:
            pilot = ((reference.get("perArm") or {}).get(arm) or {}) \
                .get("medians", {}).get(row)
            batch = ((batch_obs.get("perArm") or {}).get(arm) or {}) \
                .get("medians", {}).get(row)
            evaluated = (pilot is not None and batch is not None
                         and batch > 0)
            ratio = (pilot / batch) if evaluated else None
            band_rows.append({
                "row": row, "arm": arm, "pilot": pilot, "batch": batch,
                "ratio": ratio, "band": [low, high], "evaluated": evaluated,
                "inBand": bool(evaluated and low <= ratio <= high),
            })
    descriptive = []
    for row in DESCRIPTIVE_MEDIANS:
        for arm in ARMS:
            pilot = ((reference.get("perArm") or {}).get(arm) or {}) \
                .get("medians", {}).get(row)
            batch = ((batch_obs.get("perArm") or {}).get(arm) or {}) \
                .get("medians", {}).get(row)
            descriptive.append({"row": row, "arm": arm, "pilot": pilot,
                                "batch": batch,
                                "ratio": (pilot / batch)
                                if pilot is not None and batch else None,
                                "gates": False})
    pipeline_problems = []
    for entry in exact_rows:
        if not entry["equal"]:
            pipeline_problems.append(
                "C4 exact row %s differs: pilot %r, batch %r — the batch is "
                "suspect (section 2a.5, row 1)"
                % (entry["row"], entry["pilot"], entry["batch"]))
    for problem in batch_obs.get("exactProblems") or []:
        pipeline_problems.append("C4 batch side: %s" % problem)
    gate_causes = []
    for entry in band_rows:
        if not entry["evaluated"]:
            gate_causes.append(
                "C4 band row %s, arm %s: not evaluable (pilot %r, batch %r) — a "
                "gate the scorer did not evaluate fails (section 6)"
                % (entry["row"], entry["arm"], entry["pilot"], entry["batch"]))
        elif not entry["inBand"]:
            gate_causes.append(
                "C4 band row %s, arm %s: ratio %.4f outside [%.2f, %.2f] — the "
                "pilot is suspect (section 2a.5, row 3)"
                % (entry["row"], entry["arm"], entry["ratio"],
                   entry["band"][0], entry["band"][1]))
    if pipeline_problems:
        outcome = OUTCOME_PIPELINE_INVALID
    elif gate_causes:
        outcome = OUTCOME_CALIBRATION_INVALID
    else:
        outcome = OUTCOME_HOLD
    return {
        "gate": "c4-transfer-calibration",
        "registration": "PREREGISTRATION.md section 2a.5 (two-sided; two band "
                        "rows under the round-2 R2-11(A) ruling)",
        "referenceLabel": reference.get("label"),
        "exactRows": exact_rows,
        "bandRows": band_rows,
        "descriptiveMedians": descriptive,
        "ratioDirection": "pilot / batch",
        "medianConvention": "statistics.median (mean of the two middles at "
                            "even n)",
        "cohort": "executed calls only (a CALL.json with a resolvable "
                  "duration)",
        "outcome": outcome,
        "pipelineProblems": pipeline_problems,
        "gateCauses": gate_causes,
    }
