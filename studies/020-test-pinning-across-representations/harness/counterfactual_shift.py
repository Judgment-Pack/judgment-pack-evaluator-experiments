"""Section 3.2(iv): the counterfactual per-member shift, as a registered script.

WHAT THIS COMPUTES, AND UNDER WHOSE DEFINITIONS
-----------------------------------------------
Section 3.2's power-analysis obligation (iv): "every one of section 5.2's
eighteen members recomputed with the flagged runs coded
`presence-idiom-unsound`, published beside the unflagged figures, so the code's
effect on the family is a measured quantity rather than an assumption." The
family scorer is `e4lib/family.py` — section 7 delta 5, `harness/SCAFFOLD.md`
item S4 — and this script is the registered code path that the (iv) row of
`harness/POWER-PRESENCE-IDIOM.md` said did not exist. It exists now, and every
number it prints is reproduced by `harness/tests/test_counterfactual_shift.py`.

THE RECODE, DERIVED FROM THE REGISTRATION AND NOT CHOSEN HERE
-------------------------------------------------------------
Section 3.2 registers what the code DOES: a flagged run is "valid, counted, and
scoring zero on every endpoint it reaches, exactly as the other authoring codes
do." On Study 019's batch every authoring-coded record carries
`identityPass: false`, and eighteen of the twenty-four carry no kill block at
all; the other six (section 5.2 pin 4's runs) carry a DEFECTIVE block with no
survivor vector, which the adapter routes to the same unscoreable state — so
"no scoring information and no per-protocol membership" is the uniform
presentation, reached through two record shapes (R1-11 corrected this
paragraph: its first printing claimed all 24 lacked kill blocks). And `e4lib/admit.py` makes both properties structural rather than
incidental: a flagged run's `admit_arm_rego()` returns no policy path, so
nothing downstream can run the identity control or a suite. The counterfactual
unit for a flagged run is therefore

    family.unit_from_kill_record(run_id, arm, identity_pass=False,
                                 case_count, kill=None, corpus)

— admitted, in every ITT denominator, scoring zero, taking no offset under
either of R1-3's predicates, out of the per-protocol population — which is
`family.py`'s registered meaning of a run with no kill record. Nothing else
about any unit changes: the 28 admitted-but-unflagged B/C runs, all 36 arm-A
units and all 24 already-coded records pass through byte-identically.

THE FLAGGED SET IS DERIVED, NOT TRANSCRIBED
-------------------------------------------
The 32 flagged runs are re-derived here by running the certified detector
(`e4lib/presence_idiom.py`, power analysis at `harness/POWER-PRESENCE-IDIOM.md`)
over the policies extracted from Study 019's retained completion bytes with the
pinned OPA binary — the same registered operating set, "each admitted
arm-B/arm-C policy". The script then REFUSES to publish unless the derivation
reproduces the certified partition exactly — the counts (32 flagged of the 60
admitted, arm B 19 of 30, arm C 13 of 30; this sentence's first printing
carried the corrected-away B 15 / C 17, caught by R1-11) AND, per R1-11, the
IDENTITY of the set: the sha256 over the sorted run ids, pinned below, so a
drift that swaps a true positive for a same-arm false positive cannot pass on
arithmetic alone. A wrong count or a wrong digest means the detector, the
extractor or the 019 tree has drifted from what the power analysis certified,
and a shift computed over a drifted set would be a new measurement wearing a
certified one's name.

WHAT IS PUBLISHED
-----------------
Four full `family.family_report()` blocks — {unflagged, counterfactual} x
{A-C, A-B} — and a per-member distillation: both point estimates, the shift,
both unadjusted-scheme p-values, and whether the alpha = 0.05 reject/not-reject
decision flips. `--write` lands the whole block at
`harness/COUNTERFACTUAL-SHIFT.json`; the table on stdout is the one
`harness/POWER-PRESENCE-IDIOM.md` reprints. The JSON embeds no clock, no path
outside the two study trees and no environment detail beyond the pinned digests
already in `harness/PINS.json`, so two runs over the same trees emit the same
bytes — except for the six ANCOVA members' p-values, which finding F-2 already
records as scheme-reproducible but not byte-reproducible against 019's
published figures; against THIS script's own output they are exact, because the
seed and stream are fixed here.

WHAT THIS SCRIPT REFUSES
------------------------
- a missing or unpinnable toolchain (`JPACK_BIN`/`OPA_BIN`/`OPA_CAPS` must
  resolve and hash to the registry's non-null digests);
- a 019 tree without its frozen attempt, or a completion a registered admitted
  record names that is not on disk;
- an admitted arm-B/arm-C record whose policy does not extract or does not
  parse (019's admission already guarantees both; a violation is drift);
- a flagged set that is not the certified one (the gate above);
- publishing over an existing `COUNTERFACTUAL-SHIFT.json` without `--force` —
  a silent overwrite is how a stale figure survives a recomputation.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from e4lib import e4          # noqa: E402
from e4lib import engines     # noqa: E402
from e4lib import extract     # noqa: E402
from e4lib import family      # noqa: E402
from e4lib import presence_idiom  # noqa: E402

HARNESS = HERE
STUDY = os.path.dirname(HARNESS)
#: The source study, resolved exactly as `harness/tests/test_family.py` resolves
#: it: one sibling, not two.
NINETEEN = os.path.normpath(
    os.path.join(STUDY, "..", "019-authorship-across-representations"))
NINETEEN_RESULTS = os.path.join(
    NINETEEN, "results", "primary-attempt-001", "RESULTS.json")

OUTPUT_NAME = "COUNTERFACTUAL-SHIFT.json"

#: `harness/POWER-PRESENCE-IDIOM.md`'s certified counts — the gate, not the
#: answer. The derivation below must land on these exactly or nothing is
#: published. The per-arm split is the MEASURED one from that document's
#: pre-freeze correction note: its first printing said B 15 / C 17, which was
#: unmeasured arithmetic; this gate refused it, and the measurement is B 19 /
#: C 13 with the same certified total of 32.
CERTIFIED_FLAGGED = {"B": 19, "C": 13}
CERTIFIED_ADMITTED = {"B": 30, "C": 30}
#: R1-11: the certified set's IDENTITY, not only its arithmetic — sha256 over
#: "\n".join(sorted(run ids)). Pinned from the certified derivation; a
#: same-arm substitution passes the counts and fails this.
CERTIFIED_FLAGGED_SHA256 = "759b0ddcf8c5eb23b4bd3a8a98d927ca0b73f43873480fa5168a4afc6a25b2da"

#: 019's `run` ids restart per arm (fixture finding in `test_family.py`), so
#: every id in this module is `ARM/run-NNN`.


# VOCABULARY BOUNDARY (R1-13). This module READS Study 019's frozen
# RESULTS.json, where `identityPass` is 019's own (and only) identity member;
# 020's rename to `referenceIdentityPass` is 020's run-record vocabulary and
# deliberately does not reach a frozen predecessor's bytes.


class ShiftError(Exception):
    """A refusal. The message says which precondition failed and where."""


def load_pins() -> dict:
    with open(os.path.join(HARNESS, "PINS.json"), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def toolchain(pins: dict) -> engines.Toolchain:
    tools = engines.Toolchain(pins)
    if tools.problems:
        raise ShiftError(
            "SHIFT-TOOLCHAIN the pinned toolchain did not resolve: %s"
            % "; ".join(tools.problems))
    return tools


def load_batch() -> dict:
    if not os.path.exists(NINETEEN_RESULTS):
        raise ShiftError(
            "SHIFT-NO-ORACLE Study 019's frozen attempt is not beside this "
            "study at %s; the shift has nothing to be computed over"
            % os.path.relpath(NINETEEN_RESULTS, STUDY))
    with open(NINETEEN_RESULTS, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def load_corpus():
    """020's frozen corpus, exactly as `test_family.py`'s fixture builds it."""
    mutants = e4.load_mutants(
        os.path.join(STUDY, "mutants", "MANIFEST-jps.json"),
        os.path.join(STUDY, "mutants", "MANIFEST-rego.json"),
        os.path.join(STUDY, "mutants", "jps"),
        os.path.join(STUDY, "mutants", "rego"))
    table, _ = e4.build_pairing(mutants)
    supplied = dict((language, e4.engine_supplied_ids(mutants, language))
                    for language in family.LANGUAGES)
    return family.build_corpus(table, supplied)


def build_units(batch: dict, corpus, recode_flagged=frozenset()) -> dict:
    """019's per-run records -> `family.Unit`s, the fixture adapter's three
    defect branches reproduced as refusal-checked code.

    `recode_flagged` is the counterfactual switch: run ids in it are built as
    coded runs — identity false, no kill record — BEFORE their recorded kill
    block is read, because the admission code preempts scoring (`e4lib/
    admit.py`'s order). With the default empty set this function must
    reproduce `test_family.py`'s adapter exactly; the suite asserts it does by
    reproducing Reprint 1's anchors through this code path."""
    units = []
    repaired_empty = []
    missing_vector = []
    no_kill_block = []
    recoded = []
    for record in batch["perArmRuns"]:
        run_id = "%s/%s" % (record["arm"], record["run"])
        if run_id in recode_flagged:
            recoded.append(run_id)
            units.append(family.unit_from_kill_record(
                run_id, record["arm"], False, record.get("caseCount"),
                None, corpus))
            continue
        kill = record.get("kill")
        if kill is None:
            no_kill_block.append(run_id)
            units.append(family.unit_from_kill_record(
                run_id, record["arm"], record["identityPass"],
                record.get("caseCount"), None, corpus))
            continue
        try:
            units.append(family.unit_from_kill_record(
                run_id, record["arm"], record["identityPass"],
                record.get("caseCount"), kill, corpus))
            continue
        except family.EmptySurvivorAmbiguity:
            # Section 5.2 Fact-1, re-read under R1-3: 019 gated mutant
            # execution on identity, so this state means NOTHING RAN — the
            # unit carries the record and is not evaluated, exactly as
            # `test_family.py`'s adapter now builds it.
            if kill.get("killedPaired") != 0:
                raise ShiftError(
                    "SHIFT-ADAPTER %s: an ambiguous survivor vector with a "
                    "non-zero kill count is not the Fact-1 defect and has no "
                    "registered repair" % run_id)
            if record["identityPass"] is not False:
                raise ShiftError(
                    "SHIFT-ADAPTER %s: an identity-passing run in the "
                    "empty-survivor state breaks the R1-3 inference" % run_id)
            repaired_empty.append(run_id)
            units.append(family.unit_not_evaluated(
                run_id, record["arm"], record["identityPass"],
                record.get("caseCount")))
        except family.FamilyError as refusal:
            # Section 5.2 pin 4: a kill block with no survivor vector at all.
            if "FAMILY-NO-SURVIVOR-VECTOR" not in str(refusal):
                raise
            missing_vector.append(run_id)
            units.append(family.unit_from_kill_record(
                run_id, record["arm"], record["identityPass"],
                record.get("caseCount"), None, corpus))
    return {"units": tuple(units), "repairedEmpty": tuple(repaired_empty),
            "missingVector": tuple(missing_vector),
            "noKillBlock": tuple(no_kill_block), "recoded": tuple(recoded)}


def derive_flagged(tools: engines.Toolchain, batch: dict, scratch: str) -> dict:
    """The certified detector over the certified operating set, gated.

    Returns per-run detail for every admitted arm-B/arm-C record — flagged or
    not — so the published block shows the whole partition, not only the
    positives."""
    rows = []
    counts = {"B": {"admitted": 0, "flagged": 0},
              "C": {"admitted": 0, "flagged": 0}}
    for record in batch["perArmRuns"]:
        if record["arm"] not in ("B", "C") or not record.get("admitted"):
            continue
        run_id = "%s/%s" % (record["arm"], record["run"])
        counts[record["arm"]]["admitted"] += 1
        completion = os.path.join(NINETEEN, "arms", record["arm"], "authoring",
                                  record["run"], "completion.txt")
        if not os.path.isfile(completion):
            raise ShiftError(
                "SHIFT-NO-COMPLETION %s: the admitted record names a run whose "
                "completion is not at %s"
                % (run_id, os.path.relpath(completion, STUDY)))
        with open(completion, "r", encoding="utf-8") as handle:
            text = handle.read()
        pair = extract.extract_pair(text, record["arm"])
        if not pair["policy"]:
            raise ShiftError(
                "SHIFT-NO-POLICY %s: an admitted run's policy did not extract "
                "(%s); 019's admission guarantees it does, so the tree has "
                "drifted" % (run_id, pair["policyCode"]))
        workdir = os.path.join(scratch, record["arm"], record["run"])
        os.makedirs(workdir, exist_ok=True)
        path = os.path.join(workdir, "policy.rego")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(pair["policy"])
        try:
            report = presence_idiom.scan(tools, "policy.rego", workdir)
        except presence_idiom.PresenceIdiomError as refusal:
            raise ShiftError(
                "SHIFT-UNPARSEABLE %s: an admitted run's policy was refused by "
                "the pinned parser (%s); 019's admission ran `opa check` on "
                "these bytes, so the tree has drifted" % (run_id, refusal))
        if report["flagged"]:
            counts[record["arm"]]["flagged"] += 1
        rows.append({"run": run_id, "flagged": report["flagged"],
                     "flaggedUses": len(report["findings"]),
                     "memberships": report["memberships"],
                     "identityPassAsScored": bool(record["identityPass"]),
                     "hadKillRecord": record.get("kill") is not None})
    certify_counts(counts)
    flagged = tuple(sorted(row["run"] for row in rows if row["flagged"]))
    certify_identity(flagged)
    return {"rows": rows, "counts": counts, "flagged": flagged}


def certify_identity(flagged) -> None:
    """R1-11's other half: the set itself, not its row sums."""
    import hashlib
    digest = hashlib.sha256("\n".join(flagged).encode("utf-8")).hexdigest()
    if digest != CERTIFIED_FLAGGED_SHA256:
        raise ShiftError(
            "SHIFT-NOT-CERTIFIED the derived flagged set hashes to %s, not "
            "the certified %s: the counts alone cannot tell a certified set "
            "from a same-arm substitution, and this gate exists so they do "
            "not have to" % (digest, CERTIFIED_FLAGGED_SHA256))


def certify_counts(counts: dict) -> None:
    """The certified-counts gate, alone, so the suite can show it discriminates
    without invoking the pinned binary. It refused this module's own first
    printing of the per-arm split (B 15 / C 17), which is how the correction
    note in `harness/POWER-PRESENCE-IDIOM.md` came to exist."""
    for arm in ("B", "C"):
        if counts[arm]["admitted"] != CERTIFIED_ADMITTED[arm] \
                or counts[arm]["flagged"] != CERTIFIED_FLAGGED[arm]:
            raise ShiftError(
                "SHIFT-NOT-CERTIFIED arm %s derived %d flagged of %d admitted; "
                "harness/POWER-PRESENCE-IDIOM.md certifies %d of %d. The shift "
                "is not computed over a set the power analysis did not certify."
                % (arm, counts[arm]["flagged"], counts[arm]["admitted"],
                   CERTIFIED_FLAGGED[arm], CERTIFIED_ADMITTED[arm]))


def family_kwargs(pins: dict) -> dict:
    """ROUND-2 FINDING R2-2 / R2-3: the four reports are computed under the
    REGISTERED estimand — `family.outcomeWeighting` / `family.offsetWeighting`
    from `harness/PINS.json`, the same members `harness/score.py` reads — and
    the same registered seed and BCa pair, so the shift is a shift in the
    quantity the decision reads rather than in a default that happened to
    agree with it. A registry without the members falls through to
    `e4lib/family.py`'s own defaults, and the block PUBLISHES the pair it
    used (`estimand`), so the reading is legible from the file alone."""
    fam = (pins or {}).get("family") or {}
    kwargs = {}
    for member, name in (("outcomeWeighting", "weighting"),
                         ("offsetWeighting", "offset_weighting"),
                         ("bcaResamples", "bca_resamples"),
                         ("bcaSeed", "bca_seed"),
                         ("permutationSeed", "seed")):
        if fam.get(member) is not None:
            kwargs[name] = fam[member]
    return kwargs


def shift_block(corpus, batch: dict, flagged: dict, pins: dict = None) -> dict:
    """The published block: four reports and the per-member distillation."""
    as_scored = build_units(batch, corpus)
    recoded = build_units(batch, corpus,
                          recode_flagged=frozenset(flagged["flagged"]))
    kwargs = family_kwargs(pins)
    reports = {}
    for coding, adapter in (("unflagged", as_scored),
                            ("counterfactual", recoded)):
        for left, right in (("A", "C"), ("A", "B")):
            reports["%s/%s-%s" % (coding, left, right)] = family.family_report(
                adapter["units"], corpus, left, right, **kwargs)
    members = []
    for contrast in ("A-C", "A-B"):
        before = dict((row["id"], row)
                      for row in reports["unflagged/" + contrast]["members"])
        after = dict((row["id"], row)
                     for row in reports["counterfactual/" + contrast]["members"])
        for member_id in family.MEMBER_IDS:
            b, a = before[member_id], after[member_id]
            members.append({
                "id": member_id, "contrast": contrast,
                "level": b["level"], "engine": b["engine"],
                "population": b["population"], "adjustment": b["adjustment"],
                "unflagged": b["difference"], "counterfactual": a["difference"],
                "shift": a["difference"] - b["difference"],
                "pUnflagged": b["p"], "pCounterfactual": a["p"],
                "rejectFlips": b["rejects"] != a["rejects"],
                "nUnflagged": b["n"], "nCounterfactual": a["n"],
            })
    return {
        "obligation": "PREREGISTRATION.md section 3.2 (iv)",
        # R2-2 / R2-3: the estimand the four reports were computed under —
        # one block, taken from the reports themselves so it cannot disagree
        # with the rows it labels.
        "estimand": dict(reports["unflagged/A-C"]["estimand"]),
        "recode": {
            "code": presence_idiom.CODE,
            "semantics": "identityPass false, no kill record — 'valid, "
                         "counted, and scoring zero on every endpoint it "
                         "reaches, exactly as the other authoring codes do' "
                         "(section 3.2), as e4lib/admit.py's order makes "
                         "structural",
            "runs": list(flagged["flagged"]),
            "counts": flagged["counts"],
        },
        "detectorCensus": flagged["rows"],
        "adapter": {
            "repairedEmpty": list(as_scored["repairedEmpty"]),
            "missingVector": list(as_scored["missingVector"]),
            "noKillBlock": list(as_scored["noKillBlock"]),
        },
        "members": members,
        "reports": reports,
    }


def render_table(block: dict) -> str:
    """The markdown `harness/POWER-PRESENCE-IDIOM.md` reprints, one row per
    member per contrast, A-C first as the family's primary contrast."""
    lines = [
        "| member | contrast | cell | unflagged | counterfactual | shift | p (unfl.) | p (cf.) | reject flips |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in block["members"]:
        cell = "%s/%s/%s%s" % (row["level"], row["engine"], row["population"],
                               "/ANCOVA" if row["adjustment"] else "")
        lines.append(
            "| %s | %s | %s | %+.4f | %+.4f | %+.4f | %.4f | %.4f | %s |"
            % (row["id"], row["contrast"], cell, row["unflagged"],
               row["counterfactual"], row["shift"], row["pUnflagged"],
               row["pCounterfactual"],
               "**YES**" if row["rejectFlips"] else "no"))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Section 3.2(iv): the counterfactual per-member shift.")
    parser.add_argument("--scratch", default=None,
                        help="parent for the per-policy parse workdirs "
                             "(default: a temporary directory)")
    parser.add_argument("--write", action="store_true",
                        help="write harness/%s" % OUTPUT_NAME)
    parser.add_argument("--force", action="store_true",
                        help="allow --write to replace an existing output")
    args = parser.parse_args(argv)

    output = os.path.join(HARNESS, OUTPUT_NAME)
    if args.write and os.path.exists(output) and not args.force:
        raise ShiftError(
            "SHIFT-EXISTS %s exists; a recomputation replaces it only under "
            "--force so a stale figure cannot survive silently"
            % os.path.relpath(output, STUDY))

    pins = load_pins()
    tools = toolchain(pins)
    batch = load_batch()
    corpus = load_corpus()
    if args.scratch:
        os.makedirs(args.scratch, exist_ok=True)
        flagged = derive_flagged(tools, batch, args.scratch)
    else:
        with tempfile.TemporaryDirectory() as scratch:
            flagged = derive_flagged(tools, batch, scratch)
    block = shift_block(corpus, batch, flagged, pins)
    sys.stdout.write(render_table(block))
    if args.write:
        with open(output, "w", encoding="utf-8") as handle:
            json.dump(block, handle, indent=2, sort_keys=True)
            handle.write("\n")
        sys.stdout.write("\nwrote %s\n" % os.path.relpath(output, STUDY))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ShiftError as refusal:
        sys.stderr.write("%s\n" % refusal)
        sys.exit(1)
