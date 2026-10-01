#!/usr/bin/env python3
"""The post-pilot, pre-freeze analysis pass — ONE walk over the sealed pilot
slots, TWO sealed artifacts (round-2 findings R2-11 and R2-13, built as the
shared pass the maintainer ruled for).

    harness/pilot_analysis.py --label <UTC date>-pilot --write

publishes, under `calibration/<label>/`:

* `C4-REFERENCE.json` — the PILOT side of §2a.5's transfer gate: the eight
  exact-equality rows and the per-arm medians of the two band rows (plus the
  descriptive reasoning-token median), read from every executed pilot slot's
  sealed CALL.json / completion / session through `e4lib/transfer.py`, the
  same module `harness/score.py` reads the BATCH side with. Pinned at
  `calibration.c4ReferenceSha256` before the freeze; the attempt refuses
  (row 1) if the file is absent or the digest does not match.

* `PILOT-DISPERSION.json` — §2a.6's registered re-derivation of §5.6's
  dispersion at the pinned effort: for each of the eighteen registered
  members, sigma on its own basis (pooled within-arm, or residual for the
  adjusted members), the degrees of freedom, the exact chi-square 95 %
  interval for sigma, and the minimum detectable effect at the pilot's own n
  and at the registered N. Pinned at `calibration.dispersionSha256`.

WHAT THIS PASS COMPUTES AND WHAT IT REFUSES TO
----------------------------------------------
The dispersion table needs per-run KILL RECORDS, which `pilot_rates.py`
deliberately stops short of (§2a.2's "no kill quantity, by construction" is
scoped to the go/no-go's publisher). So this pass scores the apparatus-clean
pilot slots through the ONE scoring path, `score.score_run()`, and builds
family units exactly as `score.registered_family()` does — and then reads
only `family.member_outcomes()`, `pooled_within_arm_sd()`, `residual_sd()`
and `minimum_detectable_effect()`. It NEVER calls `family.score_member()` or
`family.family_report()`: both compute a CONTRAST, and a pre-freeze contrast
over the pilot would be exactly the informal peek §2a keeps out of the
go/no-go. The published schema is CLOSED and a NO-PEEK gate refuses
publication if any key at any depth is one of `FORBIDDEN_MEMBERS` — a
direction cannot leave this file by accident.

PRECONDITIONS, refused by name: the pilot's rates record must exist, pass the
sealed deriver's `validate_record()`, and be GO (a dispersion table over an
aborted pilot is a number with no study — M-9); the ledger must replay and
every slot's seal must verify (the same pre-step `pilot_rates.py` runs);
the golden capture must be on disk (the transcript binding is recomputed).

SIGMA STANDS BESIDE THE PRIOR (maintainer ruling, round 2, R2-13). §5.6's
019 table stays as published, labelled the fallback prior; the recomputed
table is APPENDED to §5.6 by the ceremony from this file's bytes, with df and
interval per row, because the pilot estimate is materially less precise
(chi-square factors [0.739, 1.548] at the PP floor against [0.876, 1.171] on
019's 88 runs) and "recomputed" is not "better".
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import batch                           # noqa: E402
import integrity                       # noqa: E402
import pilot_rates                     # noqa: E402
import score                           # noqa: E402
import sweep_rates                     # noqa: E402
from e4lib import dispersion           # noqa: E402
from e4lib import engines              # noqa: E402
from e4lib import family               # noqa: E402
from e4lib import transfer             # noqa: E402

STUDY = os.path.dirname(HERE)
CALIBRATION_ROOT = os.path.join(STUDY, "calibration")
REFERENCE_NAME = transfer.REFERENCE_NAME
DISPERSION_NAME = "PILOT-DISPERSION.json"
ARMS = ("A", "B", "C")

#: §2.1's registered N, read from the registry at run time; the constant is
#: the fallback the registry check refuses against.
REGISTERED_N_MEMBER = ("batch", "n")

#: The no-peek gate: a key that would carry a direction, a test or a contrast.
FORBIDDEN_MEMBERS = frozenset((
    "difference", "sign", "p", "pValue", "rejects", "interval", "mean",
    "perArmMean", "contrast", "verdict", "claim", "adjustedDifference",
    "permutationCount", "signUnanimous", "allReject",
))


class AnalysisError(Exception):
    """A refusal. The message names the precondition that failed."""


def _digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def _load(path: str):
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"), **integrity.LOAD_KWARGS)


def forbidden_members(payload, path="") -> list:
    """Every forbidden key at any depth, with its path."""
    found = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in FORBIDDEN_MEMBERS:
                found.append("%s/%s" % (path, key))
            found.extend(forbidden_members(value, "%s/%s" % (path, key)))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            found.extend(forbidden_members(value, "%s[%d]" % (path, index)))
    return found


def require_go(label: str, floor) -> dict:
    """The rates record exists, validates, and is GO."""
    path = os.path.join(CALIBRATION_ROOT, label, pilot_rates.RATES_LEDGER_NAME)
    if not os.path.isfile(path):
        raise AnalysisError(
            "ANALYSIS-NO-RATES calibration/%s/%s is absent: the analysis pass "
            "runs AFTER harness/pilot_rates.py, over a GO pilot"
            % (label, pilot_rates.RATES_LEDGER_NAME))
    record = _load(path)
    try:
        floor.validate_record(record)
    except floor.FloorError as refusal:
        raise AnalysisError("ANALYSIS-RATES the sealed deriver refuses the "
                            "rates record: %s" % refusal)
    verdict = record.get("goNoGo") or {}
    if verdict.get("go") is not True:
        raise AnalysisError(
            "ANALYSIS-NO-GO the pilot's go/no-go is not GO (%s): under M-9 the "
            "below-minimum branch ABORTS, and a dispersion table over an "
            "aborted pilot is a number with no study"
            % (verdict.get("consequence") or "no verdict"))
    return record


def walk_sealed_pilot(label: str, pins: dict) -> tuple:
    """(ledger, [(record, slot_dir, prior_code, prior_side, transcript)]) —
    the pilot's slots through `pilot_rates.slot_pre_step()`, the primary
    path's pre-scoring order, over a ledger that replays and seals that
    verify."""
    ledger_path = os.path.join(CALIBRATION_ROOT, label, batch.PILOT_LEDGER_NAME)
    if not os.path.isfile(ledger_path):
        raise AnalysisError("ANALYSIS-NO-PILOT no ledger at calibration/%s/%s"
                            % (label, batch.PILOT_LEDGER_NAME))
    ledger = _load(ledger_path)
    records = ledger.get("records") or []
    if not records or ledger.get("label") != label:
        raise AnalysisError("ANALYSIS-LEDGER calibration/%s/%s carries no "
                            "chained records for this label"
                            % (label, batch.PILOT_LEDGER_NAME))
    try:
        batch.pilot_replay(records, label)
    except batch.BatchError as error:
        raise AnalysisError("ANALYSIS-REPLAY %s" % error)
    if not ledger.get("complete") or ledger.get("short"):
        raise AnalysisError("ANALYSIS-INCOMPLETE the pilot is incomplete or "
                            "short; no analysis is published over it")
    walked = []
    for record in records:
        try:
            slot_dir, prior_code, prior_side, transcript = \
                pilot_rates.slot_pre_step(record, ledger, pins, label)
        except pilot_rates.RatesError as error:
            raise AnalysisError("ANALYSIS-SLOT %s" % error)
        walked.append((record, slot_dir, prior_code, prior_side, transcript))
    return ledger, walked


# --- the C4 reference --------------------------------------------------------

def c4_reference(label: str, walked: list) -> dict:
    """The pilot side of the transfer gate, over the EXECUTED slots."""
    by_arm = {arm: [] for arm in ARMS}
    for record, slot_dir, prior_code, _side, _transcript in walked:
        call_path = os.path.join(slot_dir, "CALL.json")
        call = _load(call_path) if os.path.isfile(call_path) else None
        completion_path = os.path.join(slot_dir, "completion.txt")
        completion_bytes = (os.path.getsize(completion_path)
                            if os.path.isfile(completion_path) else None)
        by_arm[record["arm"]].append({
            "call": transfer.call_members(call),
            "completionBytes": completion_bytes,
            "reasoningOutputTokens": batch.reasoning_output_tokens(
                os.path.join(slot_dir, "session.jsonl")),
        })
    document = transfer.reference_document(label, transfer.observables(by_arm))
    transfer.validate_reference(document)
    return document


# --- the dispersion table -----------------------------------------------------

def _registered_n(pins: dict) -> int:
    node = pins
    for key in REGISTERED_N_MEMBER:
        node = node.get(key) if isinstance(node, dict) else None
    if not isinstance(node, int) or isinstance(node, bool) or node < 1:
        raise AnalysisError("ANALYSIS-N harness/PINS.json's batch.n is %r; "
                            "the registered N is the registry's" % (node,))
    return node


def score_pilot_runs(tools, pins: dict, walked: list, scratch: str) -> dict:
    """The apparatus-clean pilot slots through `score.score_run()` — the ONE
    scoring path — with a per-run workdir (R2-5). Returns {arm: [run, ...]}
    over the SCORED runs and the counts of what was excluded and why."""
    refusals = {}
    context = score.scoring_context(tools, pins, refusals, scratch)
    if refusals:
        raise AnalysisError("ANALYSIS-CONTEXT the scoring context refused: %s"
                            % "; ".join("%s: %s" % item
                                        for item in sorted(refusals.items())))
    per_arm = {arm: [] for arm in ARMS}
    excluded = {arm: {} for arm in ARMS}
    for record, slot_dir, prior_code, prior_side, _transcript in walked:
        arm = record["arm"]
        if prior_code is not None and prior_side == "apparatus":
            excluded[arm][prior_code] = excluded[arm].get(prior_code, 0) + 1
            continue
        completion_path = os.path.join(slot_dir, "completion.txt")
        completion = None
        if os.path.isfile(completion_path):
            with open(completion_path, "rb") as handle:
                completion = handle.read().decode("utf-8", "replace")
        slot = {"arm": arm, "slotIndex": record["slotIndex"],
                "globalIndex": record["globalIndex"], "round": record["round"],
                "position": record["position"], "present": True,
                "code": prior_code if prior_side == "authoring" else None,
                "durationSeconds": None, "completion": completion}
        run_dir = os.path.join(scratch, arm, "run-%03d" % record["slotIndex"])
        os.makedirs(run_dir, exist_ok=True)
        run = score.score_run(tools, arm, slot, context, run_dir)
        if run.get("code") == "engine-invocation-refused":
            excluded[arm]["engine-invocation-refused"] = \
                excluded[arm].get("engine-invocation-refused", 0) + 1
            continue
        per_arm[arm].append(run)
    return {"runs": per_arm, "excluded": excluded, "context": context}


def dispersion_table(label: str, pins: dict, scored: dict) -> dict:
    """Eighteen rows, arm-blind, no contrast."""
    family_pins = pins.get("family") or {}
    # ROUND-2 R2-2: ONE universe. Both weightings are the registry's
    # `family` pair (native-for-both under the maintainer's ruling); a registry
    # without the members falls to the family's own defaults, which are the
    # same pair — never to a mixed seat, which `member_outcomes()` refuses.
    weighting = family_pins.get("outcomeWeighting", "native")
    offset_weighting = family_pins.get("offsetWeighting", "native")
    context = scored["context"]
    corpus = family.build_corpus(context["pairing"], context["engineSupplied"])
    units = []
    not_answered = []
    for arm in ARMS:
        for run in scored["runs"][arm]:
            # R2-1's tri-state, read explicitly: a run the relation was never
            # evaluated for is apparatus and is not a unit.
            if run.get("referenceIdentityPass") is None:
                not_answered.append("%s/%s" % (arm, run["run"]))
                continue
            units.append(family.unit_from_kill_record(
                run["run"], arm, run.get("referenceIdentityPass") is True,
                run.get("caseCount"), run.get("kill"), corpus))
    registered_n = _registered_n(pins)
    per_member = []
    for member in family.MEMBERS:
        rows = family.member_outcomes(member, units, corpus, weighting,
                                      offset_weighting)
        by_arm = {}
        for arm, _value, _covariate in rows:
            by_arm[arm] = by_arm.get(arm, 0) + 1
        n = {arm: by_arm.get(arm, 0) for arm in ARMS}
        if member.adjusted:
            sigma = family.residual_sd(rows)
            df = sum(n.values()) - 4
        else:
            sigma = family.pooled_within_arm_sd(rows)
            df = sum(n.values()) - len([arm for arm in ARMS if n[arm]])
        # The realised n at the registered N, derived from the pilot's OWN
        # per-arm membership rate for this member's population: an ITT member
        # keeps every admitted run; a per-protocol member keeps the identity
        # passing fraction. Arm-blind: a size, not a direction.
        pilot_total = {arm: len(scored["runs"][arm]) for arm in ARMS}
        realised = {arm: int(round(registered_n * n[arm] / pilot_total[arm]))
                    if pilot_total[arm] else 0 for arm in ARMS}
        per_member.append({
            "id": member.id,
            "level": member.level,
            "engine": member.column,
            "population": member.population,
            "adjustment": "ANCOVA" if member.adjusted else None,
            "sigmaBasis": "residual" if member.adjusted else "pooledWithinArm",
            "sigma": sigma,
            "n": n,
            "df": df,
            "sigmaCI95": dispersion.sigma_interval(sigma, df),
            "mdeAtPilotN": family.minimum_detectable_effect(sigma, n["A"],
                                                            n["C"]),
            "realisedNAtRegisteredN": realised,
            "mdeAtRegisteredN": family.minimum_detectable_effect(
                sigma, max(realised["A"], 1), max(realised["C"], 1)),
        })
    return {
        "label": label,
        "citable": False,
        "obligation": "PREREGISTRATION.md section 2a.6 — the dispersion "
                      "re-derived from the pilot at the pinned effort; "
                      "sigma STANDS BESIDE section 5.6's 019 prior (round-2 "
                      "ruling on R2-13), read by no decision",
        "goNoGo": "GO",
        "registeredN": registered_n,
        "weighting": {"outcome": weighting, "offset": offset_weighting},
        "unitsBuilt": len(units),
        "apparatusExcludedAtScoring": scored["excluded"],
        "identityNotAnswered": sorted(not_answered),
        "sigmaIntervalRule": "df * s^2 / sigma^2 ~ chi-square(df); two-sided "
                             "95 %; e4lib/dispersion.py, exact",
        "realisedNRule": "registeredN times this member's pilot membership "
                         "fraction per arm, rounded",
        "perMember": per_member,
    }


def publish(tools, label: str, pins: dict, scratch: str) -> tuple:
    """(reference document, dispersion document), computed and no-peek gated,
    not yet written."""
    floor = pilot_rates.derive_floor_module()
    require_go(label, floor)
    _ledger, walked = walk_sealed_pilot(label, pins)
    reference = c4_reference(label, walked)
    scored = score_pilot_runs(tools, pins, walked, scratch)
    table = dispersion_table(label, pins, scored)
    leaked = forbidden_members(table)
    if leaked:
        raise AnalysisError(
            "ANALYSIS-NO-PEEK the dispersion table carries %s: a direction, a "
            "test or a contrast cannot leave this pass (section 2a)"
            % ", ".join(leaked[:5]))
    return reference, table


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Section 2a's post-pilot analysis pass: the C4 reference "
                    "and the dispersion table.")
    parser.add_argument("--label", required=True)
    parser.add_argument("--scratch", default=None)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    batch.require_pilot_label(args.label)
    root = os.path.join(CALIBRATION_ROOT, args.label)
    targets = [os.path.join(root, REFERENCE_NAME),
               os.path.join(root, DISPERSION_NAME)]
    if args.write and not args.force:
        for target in targets:
            if os.path.exists(target):
                raise AnalysisError("ANALYSIS-EXISTS %s exists; recomputation "
                                    "replaces it only under --force"
                                    % os.path.relpath(target, STUDY))
    pins = sweep_rates.load_pins()
    tools = sweep_rates.toolchain(pins)
    if args.scratch:
        os.makedirs(args.scratch, exist_ok=True)
        reference, table = publish(tools, args.label, pins, args.scratch)
    else:
        with tempfile.TemporaryDirectory(prefix="s020-analysis-") as scratch:
            reference, table = publish(tools, args.label, pins, scratch)
    sys.stdout.write(json.dumps({"c4Reference": reference["exact"],
                                 "perArmExecuted": {
                                     arm: reference["perArm"][arm]["executed"]
                                     for arm in ARMS},
                                 "dispersionMembers": len(table["perMember"])},
                                indent=2, sort_keys=True) + "\n")
    if args.write:
        for target, body in zip(targets, (reference, table)):
            with open(target, "w", encoding="utf-8") as handle:
                json.dump(body, handle, indent=2, sort_keys=True)
                handle.write("\n")
            sys.stdout.write("wrote %s (%s)\n"
                             % (os.path.relpath(target, STUDY), _digest(target)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AnalysisError, sweep_rates.RatesError) as refusal:
        sys.stderr.write("%s\n" % refusal)
        sys.exit(1)
