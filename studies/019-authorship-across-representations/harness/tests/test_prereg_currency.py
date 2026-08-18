"""The registration, checked against the artifacts and against itself.

ROUND-1 FINDINGS R1-15, R1-17, R1-18, R1-19 and R1-20 were all prose findings,
and a prose finding closed by a prose edit closes for exactly as long as nobody
edits the prose again. This module is what makes them stay closed:

* **R1-19 — counts.** Every count the registration states about a committed
  artifact is RECOMPUTED here from that artifact and compared. Gold rows, the
  gold digest, the mutant totals, the kill census, the undispositioned
  remainders, the pairing (total groups, shared groups, both paired subsets,
  both unpairable counts), both integer cuts and the off-gold certificate's
  cells and divergences. A number that drifts in either the document or the
  artifact fails here rather than in a review round.
* **R1-15 — one form of words for the decision.** The governing clause appears
  in section 1 and in section 5, and this asserts it is the SAME clause, that
  alpha is stated with it, and that no decision statement anywhere qualifies
  zero-exclusion by delta.
* **R1-17 — the bundled estimand.** No formality-only claim survives, and the
  bundle is registered in all three places the maintainer's decision requires
  (sections 1, 5 and 9), with the no-component-attribution rule stated.
* **R1-18 — the provenance discloses the conditioning.** The pilot's arm-A
  identity-control episode and the off-protocol conditioning of the numbers the
  second revision quoted are in the governing provenance section, and the
  current anchor is named.
* **R1-20 — the ports table's PROSE agrees with the code it describes.** The
  reviewer verified every table cell and found only the surrounding sentences
  stale; these read the code's own constants and the row's own enumeration.

Nothing here is a copy of anything: every expected value is computed from the
committed bytes at test time.
"""
import json
import os
import re

import pytest

import batch
import integrity


# --- helpers ---------------------------------------------------------------

def flatten(text):
    """One line, emphasis and code ticks removed — `tests/test_partition.py`'s
    treatment of section 1a, for the same reason: the registration's wrapping
    and bolding are not differences."""
    return " ".join(text.replace("*", "").replace("`", "").split())


@pytest.fixture(scope="module")
def flat(request):
    with open(os.path.join(_study(), "PREREGISTRATION.md"), "rb") as handle:
        return flatten(handle.read().decode("utf-8"))


def _study():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(here))


def _load(relative):
    with open(os.path.join(_study(), relative), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


@pytest.fixture(scope="module")
def artifacts():
    """The committed artifacts the registration makes claims about, loaded once
    and recomputed rather than read out of any summary file."""
    from e4lib import e4
    design = os.path.join(_study(), "design", "mutants")
    mutants = e4.load_mutants(os.path.join(design, "refA", "MANIFEST.json"),
                              os.path.join(design, "refB", "MANIFEST.json"),
                              os.path.join(design, "refA"),
                              os.path.join(design, "refB"))
    pairing, paired_ids = e4.build_pairing(mutants)
    gold = _load("design/gold/gold.json")
    return {
        "gold": gold,
        "goldRows": len(gold["rows"]),
        "mutants": mutants,
        "pairing": pairing,
        "pairedIds": paired_ids,
        "cuts": e4.high_kill_cuts(paired_ids),
        "unpairable": e4.unpairable(mutants, paired_ids),
        "engineSupplied": {language: len(e4.engine_supplied_ids(mutants, language))
                           for language in ("jps", "rego")},
        "offGold": _load("design/reference/OFFGOLD-CERT.json"),
    }


# --- R1-19: every stated count, recomputed ---------------------------------

def test_the_gold_row_count_and_digest_are_the_committed_suites(flat, artifacts):
    rows = artifacts["goldRows"]
    assert "Gold: %d rows" % rows in flat
    assert "agrees %d/%d on gold" % (rows, rows) in flat
    assert "109 at this revision" in flat and rows == 109, (
        "the census stimulus sentence names the gold count; it and the suite "
        "must move together")
    digest = integrity.digest(os.path.join(_study(), "design/gold/gold.json"))
    assert digest[:8] in flat, (
        "section 4 pins the gold suite by a digest prefix and it is %s" % digest)


def test_the_mutant_totals_and_kill_census_are_the_committed_manifests(
        flat, artifacts):
    mutants = artifacts["mutants"]
    jps, rego = mutants["jps"], mutants["rego"]
    generated_rego = len(_load("design/mutants/refB/MANIFEST.json")["mutants"])
    assert "%d JPS" % len(jps) in flat
    assert "%d generated / %d valid Rego" % (generated_rego, len(rego)) in flat
    adequate = {language: sum(1 for record in mutants[language]
                              if not record["notAdequate"])
                for language in ("jps", "rego")}
    assert "%d/%d JPS and %d/%d Rego killed by gold" % (
        adequate["jps"], len(jps), adequate["rego"], len(rego)) in flat
    assert "%d JPS and %d Rego empty-witness mutants undispositioned" % (
        len(jps) - adequate["jps"], len(rego) - adequate["rego"]) in flat


def test_the_pairing_counts_are_recomputed_from_the_manifests(flat, artifacts):
    pairing = artifacts["pairing"]
    shared = sum(1 for row in pairing if row["countedInPairedSubset"])
    degenerate = sum(1 for row in pairing if row["degenerate"])
    assert ("%d witness groups in total, of which %d are shared and "
            "non-degenerate" % (len(pairing), shared)) in flat
    assert "(%d degenerate group excluded)" % degenerate in flat
    assert "covering %d JPS and %d Rego paired adequate mutants" % (
        len(artifacts["pairedIds"]["jps"]),
        len(artifacts["pairedIds"]["rego"])) in flat
    assert "%d adequate JPS and %d adequate Rego mutants are unpairable" % (
        len(artifacts["unpairable"]["jps"]),
        len(artifacts["unpairable"]["rego"])) in flat


def test_both_integer_cuts_are_the_ones_the_scorer_derives(flat, artifacts):
    """R1-1's prose half. One cut per language, from that language's own
    denominator, and the registration must carry BOTH — a single cut in the
    prose is how the endpoint became impossible for two arms."""
    cuts = artifacts["cuts"]
    assert "%d of %d for JPS (arm A) and %d of %d for Rego (arms B and C)" % (
        cuts["jps"]["integerCut"], cuts["jps"]["pairedAdequateMutants"],
        cuts["rego"]["integerCut"], cuts["rego"]["pairedAdequateMutants"]) in flat
    assert "Two integer cuts, one per language." in flat
    for block in cuts.values():
        assert block["cutReachable"]


def test_the_engine_supplied_class_is_the_marked_one(flat, artifacts):
    assert "%d JPS mutants" % artifacts["engineSupplied"]["jps"] in flat
    assert artifacts["engineSupplied"]["rego"] == 0
    assert "registered EMPTY class for Rego" in flat
    assert "for the %d JPS mutants the manifest marks engineSuppliedKill" % \
        artifacts["engineSupplied"]["jps"] in flat


def test_the_off_gold_certificate_numbers_are_the_certificates(flat, artifacts):
    cert = artifacts["offGold"]
    divergences = sum(cert.get("divergenceCountsByClass", {}).values()) \
        if cert.get("divergenceCountsByClass") else 0
    assert cert["status"] == "PASS"
    assert "{:,}-cell registered derived space".format(cert["cells"]) in flat
    assert "exactly %d divergences" % divergences in flat
    assert divergences == 0, (
        "the registration says the references agree everywhere; the "
        "certificate must too")


def test_the_gates_say_what_they_are(flat):
    """R1-19 again: a satisfied gate and an open one read differently, and the
    second revision said SATISFIED about a gate the repair had re-opened."""
    assert "Adequacy gate: GATE(pre-freeze) — OPEN" in flat
    assert "Off-gold equivalence: SATISFIED" in flat
    assert "Review flag A1: CONFIRMED, not live." in flat
    assert "zero empty witness sets remain" not in flat, (
        "the phrase is false and was the exact wording the review flagged")
    assert "undispositioned" in flat


def test_the_harness_is_described_as_existing(flat):
    assert "The harness exists and is under test." in flat
    assert "does not exist yet" not in flat


def test_the_registration_carries_no_x1_filter_any_more(flat):
    assert "X1: RETIRED" in flat
    assert "The registered exclusion registry is EMPTY" in flat
    assert "excluded from identity and kill evaluation" not in flat


# --- R1-15: one form of words -----------------------------------------------

DECISION_CLAUSE = ("the A−C difference interval excludes zero at two-sided "
                   "α = 0.05")


def test_the_decision_clause_is_one_clause_stated_in_section_1_and_section_5(
        flat):
    """R1-15. Section 1's R1 sentence used to end "excludes zero, at the
    registered δ" while section 5 said delta is interpretation and power only —
    two materially different procedures, and the OC table says they disagree on
    every interesting cell. One clause now, and it appears in both places."""
    occurrences = flat.count(DECISION_CLAUSE)
    assert occurrences >= 2, (
        "the governing clause appears %d times; section 1 and section 5 must "
        "both carry it verbatim" % occurrences)
    assert "at the registered δ" not in flat
    assert "excludes zero, at the registered" not in flat


def test_delta_is_registered_as_not_part_of_the_decision_rule(flat):
    assert ("δ = 0.20 is the registered minimum meaningful difference — an "
            "interpretation and power quantity, not part of the decision rule"
            in flat)
    assert "no decision statement in this document qualifies zero-exclusion by δ" \
        in flat
    from e4lib import stats
    assert stats.DELTA is not None


def test_alpha_is_stated_with_the_clause_and_nowhere_contradicted(flat):
    assert "α = 0.05" in flat
    assert not re.search(r"α\s*=\s*0\.0(?!5)", flat), \
        "the registration states exactly one alpha"


def test_direction_is_registered_as_coming_from_the_rates(flat):
    """R1-13's prose half: unequal denominators are the registered expectation,
    so a direction read off raw counts can reverse the study's conclusion."""
    assert "Direction is derived from the two arms' rates" in flat
    assert "never from their raw counts" in flat


def test_the_interval_is_published_under_its_honest_name(flat):
    """R1-16's prose half. The published artifact is a mesh-inversion hull and
    the registration must not call it an exact confidence interval."""
    assert "exact-arithmetic mesh-inversion hull" in flat
    assert "levelCertifiedOverContinuum: false" in flat
    assert "it is not claimed to be an exact 95% confidence interval" in flat


# --- R1-17: the bundled estimand --------------------------------------------

def test_no_formality_only_claim_survives(flat):
    assert "formality only" not in flat
    assert "B and C differ in two things, and the difference is substantive" \
        in flat


def test_arm_b_is_the_result_shape_only_floor_and_arm_c_the_full_convention(
        flat):
    assert "result-shape-only floor contract" in flat
    assert "the full prescribed judgment convention" in flat
    for convention in ("a registered default decision", "totality",
                       "explicit precedence", "unresolved handling",
                       "grounds behaviour"):
        assert convention in flat, "arm C's convention list is incomplete: %s" \
            % convention


def test_the_bundle_is_registered_in_sections_1_5_and_9(flat):
    """The maintainer's decision of 2026-08-18: A−C is the bundled
    representation-plus-convention treatment, said in the question, in the
    endpoint section and in the limits section, with no component attribution
    licensed anywhere."""
    assert ("A−C therefore compares the pack format against "
            "Rego-plus-the-full-convention, as bundles." in flat)
    assert "A−C is a bundled treatment and nothing inside the bundle is separable" \
        in flat
    assert ("no attribution of any part of an A−C result to any component of "
            "the bundle" in flat)
    assert ("No A−C or A−B result licenses any statement about which component "
            "of the bundle produced it" in flat)
    assert "part of the registered bundle A−C contrasts against" in flat


# --- R1-18: the provenance discloses the conditioning ------------------------

def test_the_provenance_discloses_the_identity_control_episode(flat):
    assert "all five arm-A suites failed the registered identity control" in flat
    assert "arm A therefore had no E4 denominator at all in the pilot" in flat
    assert "were off-protocol" in flat
    assert "design/mutants/E4-PILOT-v2.json" in flat


def test_the_provenance_cites_the_current_anchor_and_withdraws_the_direction(
        flat):
    pilot = _load("design/mutants/E4-PILOT-v2.json")
    means = {arm: pilot["perArm"][arm]["meanKillRatePaired"] for arm in "ABC"}
    assert "A %.3f, B %.3f, C %.3f" % (means["A"], means["B"], means["C"]) in flat
    fractions = {arm: (pilot["perArm"][arm]["highKill"]["highKillRuns"],
                       pilot["perArm"][arm]["highKill"]["admittedRuns"])
                 for arm in "ABC"}
    assert "A %d/%d, B %d/%d, C %d/%d" % (
        fractions["A"][0], fractions["A"][1],
        fractions["B"][0], fractions["B"][1],
        fractions["C"][0], fractions["C"][1]) in flat
    assert "R1 registers no expected direction" in flat
    assert "no surviving empirical anchor" in flat


# --- R1-20: the ports table's prose agrees with the code --------------------

@pytest.fixture(scope="module")
def ports_text():
    with open(os.path.join(_study(), "harness", "PORTS.md"), "rb") as handle:
        return handle.read().decode("utf-8")


def test_the_required_ports_sentence_counts_what_the_code_registers(ports_text):
    """R1-20. The prose said `REQUIRED_PORTS` names five files and "must grow";
    the code has named seven since M1 closed. The count comes from the constant
    so the sentence cannot go stale again."""
    count = len(integrity.REQUIRED_PORTS)
    spelled = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
               7: "seven", 8: "eight", 9: "nine", 10: "ten"}[count]
    # The needle is compared against the WHITESPACE-NORMALISED file, because
    # PORTS.md is a hard-wrapped document and the sentence spans a line break:
    # a raw substring test would pass or fail on where the paragraph happened to
    # wrap rather than on what it says. Normalising loses no power — the word
    # sequence is still required exactly, and the negative below now also catches
    # a wrapped occurrence a raw test would have missed.
    flat_ports = " ".join(ports_text.split())
    sentence = "`REQUIRED_PORTS` fixes the destination set at exactly the %s files it names"
    assert (sentence % spelled) in flat_ports or (sentence % count) in flat_ports
    assert "must grow to the seven" not in flat_ports
    rows = integrity.parse_ports(os.path.join(_study(), "harness", "PORTS.md"))
    assert len(rows) == count
    assert {row[2] for row in rows} == set(integrity.REQUIRED_PORTS)


def test_the_wrapper_rows_difference_count_is_the_number_it_enumerates(
        ports_text):
    """R1-20's other half: the row announced four differences and then described
    a fifth. The announced count is read out of the row and compared with the
    parenthesised enumeration the row itself carries."""
    row = [line for line in ports_text.splitlines()
           if line.startswith("| `transcription/authoring_call.sh`")]
    assert len(row) == 1, "one wrapper row"
    row = row[0]
    words = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5, "SIX": 6,
             "SEVEN": 7, "EIGHT": 8, "NINE": 9, "TEN": 10}
    announced = re.search(r"\*\*complete port, ([A-Z]+) registered differences",
                          row)
    assert announced, "the wrapper row announces its difference count"
    claimed = words[announced.group(1)]
    enumerated = set(int(match) for match
                     in re.findall(r"\((\d+)\)", row))
    assert enumerated == set(range(1, claimed + 1)), (
        "the row announces %d differences and enumerates %s"
        % (claimed, sorted(enumerated)))


def test_the_partition_the_registration_names_is_the_one_the_code_enforces():
    """A last cross-check with no prose in it: R1-4's fail-shut property, so a
    later prose edit cannot quietly widen the partition."""
    for status, (code, _gloss) in batch.WRAPPER_EXIT_MEANINGS.items():
        if code == "complete":
            continue
        assert code in batch.CODE_PARTITION
        assert batch.CODE_PARTITION[code][0] == "apparatus"
