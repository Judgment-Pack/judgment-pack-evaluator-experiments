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

ROUND-2 FINDINGS R2-1 and R2-13 extend the same idea to two artifacts this
module did not reach, and both were caught by a reviewer doing what a test must:

* **R2-1 — the manifest is a currency property.** The committed manifest went
  stale because writing a disposition after regenerating it leaves it describing
  a tree that no longer exists. `tests/test_manifest.py` already fails on it; it
  fails HERE too, under a different name, because a single failing test in a
  669-test suite is easy to read as one test's problem and a currency failure is
  not that. **ROUND-3 R3-1 changes the root cause rather than the property**: the
  recurrence was not a forgotten step but a covered appendable file, so
  `PREREG-REVIEW.md` leaves the covered set by named constant (ADR 0004) and this
  module asserts the EXCLUSION. Manifest currency itself is still asserted, and
  still twice.
* **R2-13 — the generated OC artifact is a currency property.** The published
  OC table retained withdrawn exactness claims and stale pilot anchors, and its
  GENERATOR would have re-emitted them. Prose findings closed by hand-editing a
  generated file reopen on the next run, so the test regenerates the document
  and byte-compares, then parses the claims out of it.

Nothing here is a copy of anything: every expected value is computed from the
committed bytes at test time.
"""
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

import pytest

import batch
import integrity
import make_manifest
import render_round_status


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


def _sibling_test_module(name):
    """Another test module in this directory, imported by path.

    There is no `tests` package (deliberately — the suite is run from the
    harness root with `harness/` on the path), so a sibling is reached the same
    way `_oc_module()` reaches the OC generator. Used where a property belongs to
    ONE module and two modules must assert it: re-implementing the AST walk here
    would make the two assertions independent, which is the opposite of what is
    wanted."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    written = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("_s019_" + name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = written


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
    # ROUND-3 R3-2. This used to pin the literal 109 as well as the sentence,
    # which made the pin fail the moment gold legitimately grew — and a literal
    # in a test is not a second opinion about the gold suite, it is the same
    # opinion written twice. What the sentence has to do is name THIS suite's
    # count, so that is what is asserted; §5's census stimulus and §4's suite
    # still cannot drift apart, and neither can drift from the file.
    assert "%d at this revision" % rows in flat, (
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
    # ROUND-3 R3-2. The registration used to state the empty-witness remainder as
    # UNDISPOSITIONED, which was true while §4's gate was open and is the number
    # the gate closure had to move. The remainder itself did not go away — 26 JPS
    # and 34 Rego mutants no gold row can kill are registered DROPS with their
    # mechanisms — so both halves are asserted: the drop count is the remainder,
    # and the undispositioned count is whatever the drop registry's own two-way
    # check says it is, which is the number the gate is closed on.
    registry = _load("design/mutants/adequacy_drop_registry.json")
    undispositioned = len(registry["unregisteredEmptyWitness"])
    assert "%d JPS and %d Rego are registered as dropped with their mechanisms" % (
        len(jps) - adequate["jps"], len(rego) - adequate["rego"]) in flat
    assert "%d JPS and %d Rego empty-witness mutants undispositioned" % (
        undispositioned, undispositioned) in flat
    assert undispositioned == 0 and not registry["staleRegistryEntries"], (
        "the gate is claimed closed; the drop registry must carry neither an "
        "unregistered empty-witness mutant nor a stale entry")
    assert len(registry["registeredDrops"]) == (
        len(jps) - adequate["jps"] + len(rego) - adequate["rego"])


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
    second revision said SATISFIED about a gate the repair had re-opened.

    ROUND-3 R3-2 makes the gate's STATE a derived claim rather than a spelling.
    The round-2 response said the adequacy disposition was accepted while the
    registration said OPEN and the regeneration record said `pass: false` — three
    surfaces, and the only one under test was the prose. So the sentence the
    registration is allowed to carry is chosen HERE by reading
    `REGENERATION-CHECK.json`: claim CLOSED and the record must stamp both arms
    and pass; claim OPEN and it must not. A prose edit in either direction
    without the artifact behind it fails."""
    record = _load("design/mutants/REGENERATION-CHECK.json")
    closed = (record.get("pass") is True
              and all(record.get("adequacyStampPresent", {}).values())
              and not any(record.get("undispositionedEmptyWitnessMutants",
                                     {}).values()))
    assert ("Adequacy gate: GATE(pre-freeze) — %s" % ("CLOSED" if closed
                                                      else "OPEN")) in flat, (
        "the regeneration record says the gate is %s and the registration must "
        "say the same" % ("closed" if closed else "open"))
    assert "Off-gold equivalence: SATISFIED" in flat
    assert "Review flag A1: CONFIRMED, not live." in flat
    assert "zero empty witness sets remain" not in flat, (
        "the phrase was asserted while it was false and stays banned; state the "
        "census instead")
    assert "undispositioned" in flat


def test_the_registration_states_the_regeneration_count_the_record_measured(flat):
    """ROUND-5 FINDING R5-7. §7 said the check was 375/375 while the record and the
    round-4 post-state both said 376/376 — the round-4 response added a derived file to
    the chain and updated two of the three surfaces. The count is read from the record
    here, in both of the forms the registration uses it."""
    record = _load("design/mutants/REGENERATION-CHECK.json")
    compared, identical = record["filesCompared"], record["identical"]
    assert compared == identical, (
        "the record reports %d/%d; a non-identical run is not a state this "
        "sentence can describe" % (identical, compared))
    assert "%d/%d byte-identical" % (identical, compared) in flat, (
        "the registration must state the regeneration check as the record "
        "measured it (%d/%d)" % (identical, compared))
    stale = re.findall(r"(\d+)/(\d+) byte-identical", flat)
    assert all(pair == (str(identical), str(compared)) for pair in stale), (
        "the registration states a byte-identical count the record denies: %s "
        "against %d/%d" % (stale, identical, compared))


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
    """ROUND-3 R3-5 changed where the pilot comes from. This test used to name
    `E4-PILOT-v2.json` in its own source, which meant the registration could be
    checked against a superseded issue forever and pass. The pilot is now
    whichever file `oc_table.PILOT_FILE` names — the single constant — and the
    chain tests below are what stop that constant from naming a stale file."""
    pilot = _load("design/mutants/%s" % _oc_module().PILOT_FILE)
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


# --- R2-1: the study manifest is a currency property ------------------------

def test_the_committed_manifest_is_current_with_the_tree():
    """R2-1. Deliberately duplicates `tests/test_manifest.py`'s assertion under a
    currency name. The manifest went stale because the maintainer's own
    post-verification commits touched `PREREG-REVIEW.md`, which the manifest
    covers, AFTER the manifest was regenerated — and the recorded suite of
    record said 575 green while this was red. The regeneration order is:
    everything else first, `harness/make_manifest.py` last, then the suite."""
    problems = make_manifest.manifest_problems()
    assert problems == [], (
        "the committed study manifest does not describe this tree; regenerate it "
        "LAST, after every other edit:\n  " + "\n  ".join(problems))


def test_the_review_record_is_out_of_the_covered_set_by_construction():
    """ROUND-3 R3-1, and this test is REVERSED from what it asserted.

    R2-1's disposition read the recurrence as a procedure failure and answered
    it with a procedure ("regenerate the manifest LAST") plus this test, which
    required `PREREG-REVIEW.md` to be COVERED and CURRENT. Round 3 found it
    stale again — the third round running — with this very test among the three
    that were red while the response reported 669/669 green.

    ADR 0004 already decides the case: a file whose purpose is to be appended to
    after the freeze is not a file that must not change. The review record grows
    by one disposition table per round, so it is that file, and the safeguard
    that works is exclusion by named constant rather than a step someone has to
    remember. What is asserted now is the exclusion; `tests/test_manifest.py`
    carries the same assertion under its own name, for the same reason two
    failures were wanted here — a currency failure must not read as one test's
    problem."""
    entries = make_manifest.manifest_entries()
    assert "PREREG-REVIEW.md" not in entries, (
        "the review record is appendable by design (ADR 0004, R3-1) and must "
        "not be covered: covering it re-stales the manifest on every round")
    assert "PREREG-REVIEW.md" in make_manifest.EXCLUDED_DOCUMENTS, (
        "the exclusion must be by NAMED CONSTANT, not by omission")
    committed = dict(
        line.split("  ", 1)[::-1]
        for line in open(os.path.join(_study(), "harness", "STUDY-MANIFEST.sha256"),
                         encoding="utf-8").read().splitlines() if line.strip())
    assert "PREREG-REVIEW.md" not in committed


def test_the_preregistration_itself_is_still_covered_and_current():
    """The other side of R3-1: excluding the review record must not become an
    argument for excluding the document that carries the claims. The
    registration is not appendable — it is the frozen registered text — so it
    stays covered, and its digest stays current with the tree."""
    entries = make_manifest.manifest_entries()
    assert "PREREGISTRATION.md" in entries
    committed = dict(
        line.split("  ", 1)[::-1]
        for line in open(os.path.join(_study(), "harness", "STUDY-MANIFEST.sha256"),
                         encoding="utf-8").read().splitlines() if line.strip())
    with open(os.path.join(_study(), "PREREGISTRATION.md"), "rb") as handle:
        actual = hashlib.sha256(handle.read()).hexdigest()
    assert committed["PREREGISTRATION.md"] == actual


def test_the_sealed_reviewer_set_is_covered_while_it_exists():
    """The set lands during the review rounds and must not move afterwards. It
    was committed in round 2 and the manifest was not regenerated over it — six
    payloads plus a manifest, uncovered."""
    root = os.path.join(_study(), "controls", "reviewer-mutants")
    if not os.path.isdir(root):
        pytest.skip("the sealed reviewer set has not landed yet")
    present = sorted(name for name in os.listdir(root)
                     if name.endswith((".json", ".rego")))
    entries = set(make_manifest.manifest_entries())
    for name in present:
        assert "controls/reviewer-mutants/" + name in entries, (
            "%s is a sealed control payload and is not covered" % name)


# --- R2-13: the generated OC artifact is a currency property ----------------

def _oc_module():
    path = os.path.join(_study(), "design", "mutants", "oc_table.py")
    # Bytecode writing is suppressed: `integrity.verify_bytecode()` refuses stale
    # caches, and a test must not manufacture one under `design/mutants/`.
    written = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("_s019_oc_table", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = written


_OC_DEFECT = re.compile(r"^\*\*(D\d) -- (.+)\. ([A-Z][^.*]*)\.\*\*", re.MULTILINE)


def _oc_defect_states(text):
    """`({id: status}, summary sentence, §9 heading)` parsed out of the generated OC
    document — ROUND-4 FINDING R4-5. The previous assertion banned two exact phrasings
    of "one is still open" and the document said it a third way, so the state is parsed
    now and the two surfaces that report it are compared to it."""
    states = {did: status for did, _title, status in _OC_DEFECT.findall(text)}
    assert states, "no D-numbered defect entries parsed out of the OC document"
    summary = [line for line in text.splitlines()
               if "gate found in the preregistration" in line and
               not line.startswith("## ")]
    heading = [line for line in text.splitlines()
               if line.startswith("## ") and "defects this gate found" in line]
    assert len(summary) == 1 and len(heading) == 1, (summary, heading)
    return states, summary[0], heading[0]


@pytest.fixture(scope="module")
def oc_text():
    with open(os.path.join(_study(), "design", "mutants", "OC-TABLE.md"),
              "rb") as handle:
        return handle.read().decode("utf-8")


def test_the_published_oc_table_is_what_its_generator_emits_today(tmp_path):
    """R2-13, the load-bearing one. The committed table had been hand-edited to
    banner its own staleness while the generator still held the superseded text
    and the superseded pilot path: the next `python3 oc_table.py` would have
    silently reverted every correction. Byte-comparing the artifact against a
    fresh run is the only assertion that closes that, and it is why the other
    tests in this section may then read the committed bytes."""
    oc = os.path.join(_study(), "design", "mutants", "oc_table.py")
    proc = subprocess.run([sys.executable, oc, "--stdout"],
                          capture_output=True, cwd=os.path.dirname(oc))
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")[-2000:]
    with open(os.path.join(_study(), "design", "mutants", "OC-TABLE.md"),
              "rb") as handle:
        committed = handle.read()
    assert proc.stdout == committed, (
        "OC-TABLE.md is not what oc_table.py emits; a hand edit to the generated "
        "document reverts on the next run — correct the generator and rebuild")


# The exactness vocabulary round-1 finding R1-16 WITHDREW. A line may mention a
# withdrawn phrase only to say it is withdrawn, so each occurrence must carry a
# withdrawal marker on the same line; anything else is the claim re-asserted.
WITHDRAWN_CLAIMS = ("exact unconditional", "exact test",
                    "exact confidence interval", "true worst-case",
                    "95% coverage", "coverage guarantee", "nominal coverage")
WITHDRAWAL_MARKERS = ("withdrawn", "R1-16", "not a coverage certificate",
                      "does not certify", "**not**")


def test_no_withdrawn_exactness_claim_is_asserted_in_the_oc_table(oc_text):
    """R2-13. The published artifact called the object an exact unconditional
    confidence interval and claimed 95% coverage for every true rate, months
    after the preregistration relabelled it. The relabelling is not a matter of
    taste: the nuisance supremum is a maximum over a finite mesh, hence a LOWER
    bound on the continuum supremum, so a coverage claim is not merely
    unsupported but pointed the wrong way."""
    offenders = []
    for number, line in enumerate(oc_text.splitlines(), 1):
        for claim in WITHDRAWN_CLAIMS:
            if claim in line and not any(m in line for m in WITHDRAWAL_MARKERS):
                offenders.append("%d: %s … %s" % (number, claim, line[:110]))
    assert offenders == [], (
        "withdrawn exactness claims asserted in OC-TABLE.md:\n  "
        + "\n  ".join(offenders))


def test_the_oc_table_publishes_the_honest_name_and_both_error_directions(
        oc_text, flat):
    """The positive half: relabelling that only deletes is not relabelling."""
    assert "exact-arithmetic mesh-inversion hull" in oc_text
    assert "exact-arithmetic mesh-inversion hull" in flat, (
        "the registration and the artifact must use the same name")
    assert "levelCertifiedOverContinuum: false" in oc_text
    assert "**lower** bound on the continuum supremum" in oc_text
    assert "**inner** approximation" in oc_text


def test_the_oc_table_reads_the_pilot_the_registration_names(oc_text, flat):
    """R2-13's other half. The generator read `E4-PILOT.json` while a hand-edited
    §7 claimed `E4-PILOT-v2.json`; one constant now names it, the emitted
    document prints that constant, and the registration must name the same file —
    so a superseded pilot cannot survive in the artifact the study publishes."""
    pilot = _oc_module().PILOT_FILE
    assert "Read from `%s`" % pilot in oc_text
    assert "design/mutants/%s" % pilot in flat, (
        "the registration's Design provenance must name the pilot the OC table "
        "reads, and it names something else")
    assert "E4-PILOT.json`" not in oc_text, (
        "the superseded pilot must not be a source in the published table")


def test_the_oc_tables_pilot_fractions_are_recomputed_from_that_pilot(oc_text):
    """Every fraction the artifact states about the pilot, recomputed from the
    pilot's own bytes. The superseded artifact stated 0.20 / 0.80 / 1.00 against
    a pilot that says 1/5, 0/5, 0/5 — and the direction, not just the magnitude,
    was wrong."""
    module = _oc_module()
    anchor = module.pilot_anchor(
        os.path.join(_study(), "design", "mutants", module.PILOT_FILE))
    pilot = _load("design/mutants/%s" % module.PILOT_FILE)
    for arm in ("A", "B", "C"):
        assert "**high-kill fraction: %d/%d" % (anchor[arm]["k"],
                                                anchor[arm]["n"]) in oc_text
        # ROUND-3 R3-4/R3-6, and this assertion is REVERSED from what it was.
        # It used to require every arm to record zero identity failures, with a
        # message saying §7's caveat and the denominator rule needed re-reading
        # first. The domain check made the guard fire — arm C records four — so
        # the re-reading happened, and what is asserted now is the thing that
        # actually matters: whatever the identity failures are, the published
        # denominator is §1a/§5's ADMITTED runs, i.e. it does NOT shrink by them.
        block = pilot["perArm"][arm]["highKill"]
        assert anchor[arm]["n"] == block["admittedRuns"], (
            "arm %s: the OC table's denominator must be the pilot's published "
            "admitted-run count, not its scored-run count" % arm)
        assert (block["admittedRuns"]
                == len(anchor[arm]["runs"]) + anchor[arm]["identityFail"]), (
            "arm %s: identity-failing runs must be IN the denominator" % arm)
        if anchor[arm]["identityFail"]:
            assert "identity FAIL -- not asked" in oc_text
            assert "`highKill: null`, in the denominator" in oc_text
    assert "**Current fractions: A %d/%d" % (anchor["A"]["k"],
                                             anchor["A"]["n"]) in oc_text


def test_the_oc_table_carries_no_located_operating_point(oc_text):
    """R1-18 and R2-13 together: five runs per arm locate nothing, R1 registers
    no expected direction, and the artifact used to be written around a point."""
    assert "Pilot-anchored band" not in oc_text
    assert "pilot anchor is `p_A ~ 0.2`" not in oc_text
    assert "the gap the pilot points at" not in oc_text
    assert "No operating point is located" in oc_text
    assert "the pilot puts arm C at" not in oc_text


def test_the_oc_table_does_not_teach_the_retired_x1_gate(oc_text):
    """R2-14 reaching into the same artifact: the OC table's §8 and §9 read the
    identity control through a 5/5 arm-A exclusion and a *proposed* X1-exclusion
    amendment. X1 is retired, the registry is empty, and the current pilot fails
    identity nowhere."""
    for line in oc_text.splitlines():
        if "X1" not in line:
            continue
        assert any(word in line for word in
                   ("retired", "historical", "superseded")), (
            "OC-TABLE.md line still treats X1 as live: " + line[:140])


# --- ROUND-3 FINDING R3-7: §7's integrity claim, frozen at the honest one ----

def test_the_registration_states_the_integrity_bootstrap_and_not_the_stronger_claim(
        flat):
    """R3-7. The immutable registration said integrity "runs before the scorer
    imports a single study module" while `score.py` imports study-local
    `integrity` at module scope — a claim its own code comment already
    contradicted, calling itself a drift gate rather than a root of trust.

    The sentence is withdrawn and the replacement is frozen HERE, because a
    prose repair that nothing asserts is a prose repair for one round. Each
    clause below is also a property the code tests separately
    (`tests/test_score_attempt.py`), so the registration and the harness state
    one thing between them."""
    assert "Integrity is a gate against drift, not a root of trust" in flat
    assert "the only study-local module the scorer imports at module scope" in flat
    assert "code that must run in order to check itself cannot check itself first" \
        in flat
    assert "before the scorer imports a single study module" not in flat, (
        "the withdrawn claim is back in the registration")


def test_the_integrity_clause_the_registration_freezes_is_true_of_the_code(flat):
    """The other half, and the reason the wording above is worth freezing: the
    sentence is re-derived from the scorer's own imports rather than trusted.
    A future `import batch` at module scope in `score.py` makes the registration
    false, and this fails."""
    import score
    attempt = _sibling_test_module("test_score_attempt")
    local = attempt._study_local_module_names()
    assert attempt._module_scope_imports(score.__file__) & local == {"integrity"}
    assert attempt._module_scope_imports(score.integrity.__file__) & local == set()


# --- ROUND-3 FINDING R3-8: §10 promises only what §5 permits -----------------

def test_the_publication_commitment_does_not_promise_a_forbidden_interval(flat):
    """R3-8's prose half. §10 said all intervals are published "whichever way
    they land" while §5 forbids computing one at or above the gate rows, so the
    two sections registered incompatible obligations and the stronger-sounding
    one was the one a reader would hold the study to.

    §10 keeps its commitment and states its scope: what exists is published, and
    a contrast the registered rule forbids does not exist to be published."""
    assert "published whichever way they land" in flat
    assert "an outcome that reaches a gate row has no A−C or A−B interval to " \
        "publish" in flat
    assert "A blocked contrast is published as blocked, with its cause" in flat
    assert "Publishing a number the registered rule says must not be computed " \
        "is not a stronger publication commitment" in flat
    # §5's side of the same rule, unchanged and still required.
    assert "No inferential quantity is computed, let alone published, at or " \
        "above row 3." in flat


# --- ROUND-3 FINDING R3-5: the pilot's supersession CHAIN --------------------
#
# The old safeguard was mutual agreement: the registration, `oc_table.PILOT_FILE`
# and the generated table all had to name the same pilot. Three surfaces agreeing
# on a stale file is exactly what the reviewer found — all three said v2 while the
# response's own disposition called v3 current — and no amount of agreement can
# detect it, because staleness is not a property any of the three carries.
#
# It is a property of the FILES. Every superseded issue names its successor, so
# there is a chain; the current issue is the one at the end of it. These tests
# walk that chain and require the named constant to be its terminus.

def _pilot_issues():
    """Every `E4-PILOT*.json` on disk, loaded."""
    design = os.path.join(_study(), "design", "mutants")
    return {name: _load("design/mutants/" + name)
            for name in sorted(os.listdir(design))
            if name.startswith("E4-PILOT") and name.endswith(".json")}


def test_the_pilot_supersession_chain_is_walkable_and_complete():
    """One chain, no forks, no orphans, every link resolving to a file."""
    issues = _pilot_issues()
    assert len(issues) >= 2, sorted(issues)
    successors = {name: doc.get("supersededBy") for name, doc in issues.items()}
    for name, successor in successors.items():
        if successor is None:
            continue
        assert successor in issues, (
            "%s names `%s` as its successor and that file does not exist"
            % (name, successor))
        assert issues[name].get("SUPERSEDED") is True, (
            "%s names a successor without marking itself SUPERSEDED" % name)
        assert issues[name].get("supersededBecause"), (
            "%s is superseded and does not say why" % name)
    terminal = [name for name, successor in successors.items()
                if successor is None]
    assert len(terminal) == 1, (
        "exactly one pilot issue is current; these have no successor: %s"
        % sorted(terminal))
    # No two issues may name the same successor, and following the links from
    # any starting point must reach the terminus without a cycle.
    named = [s for s in successors.values() if s]
    assert len(named) == len(set(named)), named
    for start in issues:
        seen, node = set(), start
        while successors[node] is not None:
            assert node not in seen, "cycle through %s" % node
            seen.add(node)
            node = successors[node]
        assert node == terminal[0]


def test_the_named_pilot_is_the_end_of_the_chain_and_not_merely_the_agreed_one(
        flat, oc_text):
    """R3-5's load-bearing assertion. The constant, the registration and the
    generated table must still agree — and the file they agree on must be the
    one nothing supersedes."""
    issues = _pilot_issues()
    current = _oc_module().PILOT_FILE
    assert current in issues, current
    assert issues[current].get("supersededBy") is None, (
        "`oc_table.PILOT_FILE` names %s, which is superseded by %s: three "
        "surfaces agreeing on a stale pilot is the round-3 R3-5 defect"
        % (current, issues[current].get("supersededBy")))
    assert issues[current].get("SUPERSEDED") is not True
    assert "design/mutants/%s" % current in flat
    assert "Read from `%s`" % current in oc_text
    for name, doc in issues.items():
        if name == current:
            continue
        assert doc.get("SUPERSEDED") is True, (
            "%s is not the current pilot and is not bannered" % name)


def test_every_superseded_pilot_is_bannered_reciprocally():
    """The other direction of R3-5: v3 said "v2 is bannered" while v2 carried no
    `SUPERSEDED`/`supersededBy` member at all. A claim about another file is
    checked against that file."""
    issues = _pilot_issues()
    current = _oc_module().PILOT_FILE
    claimed = set(issues[current].get("supersedes") or [])
    assert claimed, "the current pilot must name what it supersedes"
    on_disk = {name for name, doc in issues.items()
               if doc.get("SUPERSEDED") is True}
    assert claimed == on_disk, (
        "%s claims to supersede %s and the files bannered SUPERSEDED are %s"
        % (current, sorted(claimed), sorted(on_disk)))


# --- ROUND-3 FINDING R3-6: ONE denominator, stated in three places -----------

def test_the_admitted_run_denominator_is_one_rule_across_scorer_pilot_and_oc(
        flat, oc_text):
    """R3-6. The OC table reported D3 — what a run that fails identity does to
    the E4 denominator — as STILL OPEN after the response had settled it
    denominator-in, and §7's fractions were computed the other way while it did.

    The rule is asserted SEMANTICALLY here rather than by phrase-matching: the
    primary scorer's registered denominator rule, the pilot's published
    `highKill` block and the OC table's fractions must all be the admitted-run
    reading, and the current pilot is a live witness because the two readings
    give different answers on it."""
    import score
    # (a) THE SCORER. The reviewer's own two-run probe, run here as well as in
    # `test_score_attempt.py`, because R3-6 is the finding that the three
    # surfaces can drift apart — so the three are asserted in one place.
    attempt = _sibling_test_module("test_score_attempt")
    endpoint = score.e4_endpoint(
        "A", [attempt.run("run-001", killed=39),
              attempt.run("run-002", identity=False, killed=39)],
        {"integerCut": 38})
    assert (endpoint["highKill"], endpoint["denominator"]) == (1, 2), (
        "the registered denominator is admitted runs: one identity-passing "
        "high-kill run and one identity failure is 1/2, not 1/1")
    assert "admitted runs" in endpoint["denominatorRule"]
    # (b) THE PILOT and (c) THE OC TABLE.
    pilot = _load("design/mutants/%s" % _oc_module().PILOT_FILE)
    witness = False
    for arm in ("A", "B", "C"):
        block = pilot["perArm"][arm]
        high = block["highKill"]
        assert high["admittedRuns"] == len(block["perRun"]), (
            "arm %s: the pilot's denominator must be every admitted run" % arm)
        assert high["identityFailingRunsInDenominator"] == block["identityFail"]
        for run in block["perRun"]:
            if not run.get("identityPass"):
                assert run["highKill"] is None, (
                    "an identity-failing run is in the denominator and was "
                    "never asked: `highKill` is null, never false")
                witness = True
    assert witness, (
        "no identity-failing run exists in the current pilot, so this test "
        "cannot tell the two denominator readings apart; if the pilot is "
        "re-scored to one with none, keep the primary scorer's mixed-arm probe "
        "as the discriminating case and say so here")
    # (c) THE OC TABLE, at its own anchor function rather than only in its prose:
    # the denominator it publishes must be the pilot's admitted-run count, which
    # is the surface R3-6 found computing the other reading while §9 called the
    # question open.
    module = _oc_module()
    anchor = module.pilot_anchor(
        os.path.join(_study(), "design", "mutants", module.PILOT_FILE))
    for arm in ("A", "B", "C"):
        assert anchor[arm]["n"] == pilot["perArm"][arm]["highKill"]["admittedRuns"]
    # R4-5 replaces two banned strings with the parsed state: the document said
    # "two are closed, one is still open" in its opening paragraph while §9's own
    # heading said all three were closed, and neither banned phrasing matched.
    states, summary, heading = _oc_defect_states(oc_text)
    module = _oc_module()
    assert states == {did: status for did, status, _ in module.DEFECTS}, (
        "the OC document's parsed D-statuses are %s and its generator's register "
        "says %s" % (states, module.DEFECTS))
    assert states["D3"].startswith("CLOSED"), (
        "the OC table still reports the settled denominator question as open")
    assert "denominator-in" in states["D3"]
    closed = sum(1 for status in states.values() if status.startswith("CLOSED"))
    for surface, text in (("the opening summary", summary),
                          ("§9's heading", heading)):
        if closed == len(states):
            assert "all three are closed" in text or "all three closed" in text, (
                "%s must agree with the parsed statuses (%d of %d closed): %r"
                % (surface, closed, len(states), text))
            assert "open" not in text, (
                "%s calls a closed defect open: %r" % (surface, text))
        else:
            assert "open" in text, (
                "%s must say a defect is open when one is: %r" % (surface, text))
    # And the registration must not have the attrition reading either: an
    # identity failure does not shrink N.
    assert "identity-control exclusions are reported, never silently dropped" \
        in flat
    assert "the high-kill denominator does not move" in flat


# --- R2-14: the reader-facing corpus states the current question ------------

@pytest.fixture(scope="module")
def readme():
    with open(os.path.join(_study(), "README.md"), "rb") as handle:
        return flatten(handle.read().decode("utf-8"))


def test_the_readme_states_the_registered_question_and_not_the_superseded_one(
        readme):
    """R2-14. The README described the study as measuring how reliably a model
    AUTHORS AN EXECUTABLE POLICY and read A−C as what "the language investment"
    buys — the policy-correctness endpoint the design phase pivoted away from,
    and the component attribution R1-17 prohibits."""
    assert "what its accompanying test suite pins" in readme
    assert "change how reliably a model authors an executable policy" not in readme
    assert "what the language investment buys" not in readme
    assert "as bundles" in readme
    assert "no attribution of any part of an A−C result to any component of the " \
        "bundle is licensed" in readme


def test_the_readme_does_not_claim_the_study_is_unreviewed(readme):
    """It said "No review round has read this study" and "the cross-vendor review
    regime … has not begun" after two rounds had returned DO NOT FREEZE."""
    assert "No review round has read this study" not in readme
    assert "has not begun" not in readme
    assert "review rounds" in readme and "DO NOT FREEZE" in readme


def test_the_readme_records_x1_as_retired(readme):
    assert "is retired" in readme
    assert "the registered exclusion registry is empty" in readme


def test_no_current_facing_document_teaches_x1_as_a_live_exclusion():
    """R2-14's sweep, kept as a test rather than as a one-off grep. Each file
    below is read by someone deciding what this study currently does. A mention
    of X1 is allowed only where its own PARAGRAPH marks it retired, withdrawn or
    archived — the record of a retracted claim is worth keeping, and a live
    instruction to filter by it is not. Paragraphs, not lines, because every
    document here is hard-wrapped and a line test would pass or fail on where a
    sentence happened to break."""
    marked = ("retired", "RETIRED", "withdrawn", "WITHDRAWN", "archived",
              "ARCHIVED", "Archived", "historical", "superseded", "SUPERSEDED",
              "former X1", "no X1", "empty", "EMPTY", "did not survive",
              "retirement", "no longer exist")
    offenders = []
    for relative in ("README.md", "PREREGISTRATION.md", "design/POLICY-DRAFT.md",
                     "harness/PINS.json", "harness/SCAFFOLD.md",
                     "harness/tests/E2E-SMOKE.md"):
        path = os.path.join(_study(), relative)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as handle:
            text = handle.read().decode("utf-8")
        line_number = 1
        for paragraph in text.split("\n\n"):
            if re.search(r"\bX1\b", paragraph) and \
                    not any(m in paragraph for m in marked):
                offenders.append("%s:%d %s"
                                 % (relative, line_number,
                                    " ".join(paragraph.split())[:130]))
            line_number += paragraph.count("\n") + 2
    assert offenders == [], (
        "current-facing documents still teach the retired X1 exclusion:\n  "
        + "\n  ".join(offenders))


def test_the_partition_the_registration_names_is_the_one_the_code_enforces():
    """A last cross-check with no prose in it: R1-4's fail-shut property, so a
    later prose edit cannot quietly widen the partition."""
    for status, (code, _gloss) in batch.WRAPPER_EXIT_MEANINGS.items():
        if code == "complete":
            continue
        assert code in batch.CODE_PARTITION
        assert batch.CODE_PARTITION[code][0] == "apparatus"


# --- ROUND-3 FINDING R3-9: a claim of nonexistence is checkable -------------

_CURRENT_FACING = ("README.md", "PREREGISTRATION.md", "design/POLICY-DRAFT.md",
                   "harness/PINS.json", "harness/SCAFFOLD.md",
                   "harness/tests/E2E-SMOKE.md")

# The claim, matched as a PHRASE rather than by paragraph proximity: a name and
# a statement that it is gone, with at most a clause between them and no
# sentence boundary. Paragraph proximity cannot tell "`partition_x1()` no longer
# exists, and `in_x1()` survives" from a claim about both.
_CLAIMED_GONE = re.compile(
    r"`e4\.([A-Za-z_][A-Za-z_0-9]*)\(\)`[^.]{0,60}?"
    r"(no longer exists?|does not exist|do not exist|never exists)")


def test_no_document_claims_a_harness_object_is_gone_while_it_is_present():
    """R3-9, and it is the exact assertion the marker-word sweep could not be.

    The sweep above allows a paragraph mentioning X1 when the paragraph carries
    a retirement word. That is a test of TONE: it cannot tell a true retirement
    from a false one, and it passed a smoke record saying "`e4.in_x1()` no
    longer exist[s]" while `in_x1()` was implemented and exported — beside a
    scorer that was still publishing `x1Excluded` and `x1ExcludedCases`.

    So every `e4.<name>()` a current-facing paragraph says is GONE is looked up
    in the module. The rule is symmetric and has no X1 in it: a document may
    describe a retirement, and it may not describe one that did not happen."""
    from e4lib import e4
    offenders = []
    for relative in _CURRENT_FACING:
        path = os.path.join(_study(), relative)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as handle:
            text = handle.read().decode("utf-8")
        flat_text = " ".join(text.split())
        for name, _phrase in _CLAIMED_GONE.findall(flat_text):
            if hasattr(e4, name):
                offenders.append("%s: says `e4.%s()` is gone and it is not"
                                 % (relative, name))
    assert offenders == [], "\n  ".join([""] + offenders)


def test_the_scorer_publishes_no_x1_member_under_any_spelling():
    """The same finding on the other surface. §4: "There is no exclusion class,
    no per-case X1 filter and no per-run excluded-case count." Asserted over the
    scorer's own source rather than over one endpoint, because the members were
    written in three places — the run, the arm aggregation and the report."""
    with open(os.path.join(_study(), "harness", "score.py"), "rb") as handle:
        source = handle.read().decode("utf-8")
    emitted = re.findall(r'"(x1[A-Za-z0-9]*)"', source)
    assert emitted == [], (
        "harness/score.py still publishes %s; §4 registers no per-case filter "
        "and no per-run excluded-case count" % sorted(set(emitted)))
    assert "Excluded cases" not in source


# --- ROUND-7 FINDINGS R7-2, R7-3, R7-4 and R7-7: the lifecycle is DATA ------
#
# R3-10 caught a status header that contradicted the record, and every round
# since widened a parser over the same English. Round 4 required the verdicts to
# appear; round 5 required them per round; round 6 added enclosing-negation
# rejection and a disposition-cell reading. Each was defeated by the next round:
# a negated attribution read as an assertion, a denial of the open-state
# sentence satisfied the open-state regex, a TRUE sentence was rejected for its
# polarity, `round-7` and `round-07` collapsed into one key, and a Setext
# heading walked past a heading guard.
#
# The maintainer decision registered in `PREREG-REVIEW.md`'s round-7 section is
# that this layer is DESCOPED rather than escalated a fifth time. What replaces
# it is this program's own baseline (ADR 0004: navigation is not where claims
# live), in three parts:
#
#   1. the lifecycle is DATA — one HTML-comment-fenced JSON block in the record,
#      carrying per round its number, its state, the verdict it returned, its
#      severity counts and its finding-id range;
#   2. the three front doors carry ONE sentence RENDERED from that block by
#      `harness/render_round_status.py`, and this module requires the rendered
#      string of each of them VERBATIM — exact equality on the
#      whitespace-collapsed text, with no parsing and no polarity analysis. A
#      document that quotes its own attestation and then denies it is REVIEW's
#      problem, which is where the truth of free prose rests in every
#      predecessor study;
#   3. the block is cross-checked STRUCTURALLY against the tree: the
#      `reviews/round-N/` directories with duplicate identities REFUSED rather
#      than normalised away, each verbatim review's finding ids, and the
#      record's own disposition rows and severity column.
#
# Deleted with the decision, and named here so a later reader knows they were
# removed on purpose rather than lost: the negation cue list and `_negated()`,
# the verdict-attribution sentence parser (`_header_verdict_map()`,
# `_expand_round_list()`), the role-claim clause reader (`_role_claims()` and
# its two role vocabularies), the open-state and any-open-claim sentence
# regexes, the ordinal round-count sentence, and the 24-character disposition
# heuristic. Window sweeps survive ONLY as banned-claim detection for specific
# false numbers and spellings already caught historically (`_ZERO_LIVE`,
# `_STATED_DIFFERENCES`, the stale gold heading, the X1 sweeps, the patch-pin
# sweep), where a false negative costs a missed offender rather than a false
# attestation.

_ROUND = re.compile(r"^## Round (\d+) — ", re.MULTILINE)
_REVISIONS = ("first", "second", "third", "fourth", "fifth", "sixth",
              "seventh", "eighth", "ninth", "tenth",
              "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth")

# ROUND-8 FINDINGS R8-5 AND R8-7: ONE reading of what a Markdown document
# actually presents, shared by the two structural readers that needed it.
#
# Both findings are the same defect at two surfaces. `_disposition_rows()` read
# every `|`-shaped line, so wrapping all nine of round 7's rows in a multiline
# HTML comment left the round reading `complete` with its whole table commented
# out; `_heading_lines()` read every `#`-prefixed line, so the exact required
# heading placed inside a fenced code block or a multiline comment satisfied the
# heading requirement while a Setext heading beside it carried the stale words.
# A structural reader that counts inactive content is not reading structure.
#
# `_live_lines()` returns one entry per input line with everything the document
# does NOT present replaced by the empty string: fenced code (``` or ~~~) and
# HTML comments, including comments that open and close mid-line and comments
# that span lines. The line COUNT is preserved because the Setext reading looks
# at the following line, and an inactive line must be a blank there rather than
# absent. Fenced code wins over comments, because inside a fence a `<!--` is
# literal text.
#
# The direction of every error this makes is the closed one: content wrongly
# read as inactive leaves a finding undispositioned (its round stays open) and a
# heading unread (the corrected-heading requirement fails). Neither can
# manufacture a pass.
_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def _live_lines(text):
    """Every line of `text`, with fenced-code and HTML-comment content blanked."""
    out, fence, in_comment = [], None, False
    for raw in text.split("\n"):
        if fence is not None:
            stripped = raw.strip()
            if stripped.startswith(fence) and set(stripped) == set(fence):
                fence = None
            out.append("")
            continue
        live, rest = "", raw
        while rest:
            if in_comment:
                index = rest.find("-->")
                if index < 0:
                    rest = ""
                else:
                    rest, in_comment = rest[index + 3:], False
            else:
                index = rest.find("<!--")
                if index < 0:
                    live, rest = live + rest, ""
                else:
                    live, rest = live + rest[:index], rest[index + 4:]
                    in_comment = True
        opening = _FENCE.match(live)
        if opening:
            fence = opening.group(1)
            out.append("")
            continue
        out.append(live)
    return out


def _review_record():
    with open(os.path.join(_study(), "PREREG-REVIEW.md"), "rb") as handle:
        return handle.read().decode("utf-8")


COMPLETE = render_round_status.COMPLETE
AWAITING_REVIEW = render_round_status.AWAITING_REVIEW
AWAITING_RESPONSE = render_round_status.AWAITING_RESPONSE
OPEN_STATES = render_round_status.OPEN_STATES
MALFORMED = "malformed"

# ROUND-7 FINDING R7-3. A disposition cell is a disposition iff it is non-empty
# after stripping and is not one of these LITERAL placeholders — the table's own
# ways of writing nothing, and the words a response in progress writes. Round 6
# added a 24-character minimum on top of the list, on the reasoning that no
# written disposition is shorter than a sentence; the reviewer wrote
# `PENDING — maintainer response to follow`, which is thirty-nine characters,
# and the heuristic counted it. Length is not a property of a disposition, so
# the rule is DELETED rather than tuned. Whether written words dispose of a
# finding is review's question.
_PLACEHOLDER_CELLS = frozenset((
    "", "-", "--", "---", "—", "–", "*", "_", ".", "...", "…",
    "pending", "tbd", "todo", "to be written", "open", "none", "n/a", "na",
    "?", "??", "???"))


def _is_disposition(cell):
    return cell.strip().lower() not in _PLACEHOLDER_CELLS


def _finding_order(name):
    return int(name.split("-")[1])


def _reviews_dir(study=None):
    return os.path.join(study or _study(), "reviews")


def _rounds_on_disk(reviews=None):
    """`({number: {'prompt': bool, 'review': bool}}, problems)`.

    ROUND-7 FINDING R7-4: a directory NAME is an identity. The round-6 reading
    turned every name into `int(name.split("-")[1])`, so `round-7` and
    `round-07` produced the same dictionary key and one silently overwrote the
    other — the reviewer added a second round-5 section and the whole reading
    returned `problems=[]`. The canonical name is the only accepted one, a
    non-canonical spelling is REPORTED rather than normalised away, and a
    numeric collision is refused rather than resolved."""
    reviews = reviews or _reviews_dir()
    problems, canonical, others = [], {}, []
    if not os.path.isdir(reviews):
        return {}, ["there is no reviews/ directory at %s" % reviews]
    for name in sorted(os.listdir(reviews)):
        if not name.startswith("round-"):
            continue
        if not os.path.isdir(os.path.join(reviews, name)):
            problems.append("reviews/%s is not a directory" % name)
            continue
        loose = re.fullmatch(r"round-(\d+)", name)
        if not loose:
            problems.append(
                "reviews/%s is not a round directory; the registered name is "
                "`round-<n>`" % name)
            continue
        number = int(loose.group(1))
        if name == "round-%d" % number:
            canonical[number] = name
        else:
            others.append((number, name))
    # The canonical directories are the rounds. A non-canonical spelling is
    # never adopted as one — it is reported, and reported AGAIN as a collision
    # when a round of that number also exists, which is the whole of R7-4.
    for number, name in others:
        problems.append(
            "reviews/%s is a non-canonical spelling of round %d (round-%d); two "
            "spellings are two identities to a reader and one to a parser that "
            "normalises them" % (name, number, number))
        if number in canonical:
            problems.append("reviews/%s and reviews/%s are both round %d"
                            % (canonical[number], name, number))
    out = {}
    for number, name in sorted(canonical.items()):
        out[number] = {
            "prompt": os.path.isfile(os.path.join(reviews, name, "PROMPT.md")),
            "review": os.path.isfile(os.path.join(reviews, name, "REVIEW.md")),
        }
    return out, problems


def _record_sections(text):
    """`({number: body}, problems)` — the record's own `## Round N` sections.

    R7-4's other half: the round-6 reading checked that the heading numbers were
    ASCENDING and then stored them in a dictionary, so two adjacent `## Round 5`
    headings passed the ordering check and one section overwrote the other.

    ROUND-8 FINDING R8-5: the sections are cut out of the document's LIVE text,
    so a `## Round N` heading inside a fence or a comment is not a section and a
    section's commented-out body is not read as content."""
    text = "\n".join(_live_lines(text))
    numbers = [int(match.group(1)) for match in _ROUND.finditer(text)]
    problems = []
    if numbers != sorted(numbers):
        problems.append("the record's round sections are out of order: %s"
                        % numbers)
    seen = set()
    for number in numbers:
        if number in seen:
            problems.append("the record carries more than one `## Round %d` "
                            "section" % number)
        seen.add(number)
    sections = {}
    pieces = _ROUND.split(text)[1:]
    for index in range(0, len(pieces), 2):
        sections.setdefault(int(pieces[index]), pieces[index + 1])
    return sections, problems


def _disposition_rows(number, body):
    """`({id: cell}, [ids whose cell is a placeholder], {id: severity},
    [ids named by more than one row])`.

    The table is a STRUCTURED surface and is parsed as one: a leading pipe,
    three cells — id, severity, disposition — and a closing pipe. A row of any
    other shape is not read as a row at all, so its finding stays
    undispositioned and its round stays open, which is the fail-closed
    direction. `strip("|")` is the reading this cannot use: it eats BOTH
    trailing pipes of `| R6-1 | BLOCKER ||` and turns an empty disposition cell
    into a two-cell line.

    ROUND-8 FINDING R8-5, in its two halves:

    * **identity.** Rows went into dictionaries with no duplicate check, and
      completion was key-set equality, so a SECOND row for a finding — with a
      different severity and a contradictory disposition — silently replaced the
      first and the round still read `complete`. A finding named twice has no
      disposition: it has two, and which one the record means is not something a
      later reader can recover. Duplicates are reported and the round is
      malformed.
    * **liveness.** Rows were read out of the raw text, so wrapping all nine of
      round 7's rows in one multiline HTML comment left the table `complete`
      with nothing in it. The body is read through `_live_lines()`, the same
      helper R8-7's heading reader uses.
    """
    written, pending, severities, duplicates = {}, [], {}, []
    for line in _live_lines(body):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        parts = stripped.split("|")
        if len(parts) != 5 or parts[0].strip() or parts[-1].strip():
            continue
        cells = [cell.strip() for cell in parts[1:4]]
        match = re.fullmatch(r"R(\d+)-(\d+)", cells[0])
        if not match or int(match.group(1)) != number:
            continue
        name = "R%d-%d" % (number, int(match.group(2)))
        if name in severities:
            if name not in duplicates:
                duplicates.append(name)
            continue
        severities[name] = cells[1]
        if _is_disposition(cells[2]):
            written[name] = cells[2]
        else:
            pending.append(name)
    return (written, sorted(pending, key=_finding_order), severities,
            sorted(duplicates, key=_finding_order))


def _review_finding_ids(number, reviews=None):
    """The finding ids the round's VERBATIM review carries, or None when no
    review has landed. Rounds 1, 3 and 4 head their findings with bold runs
    rather than markdown headings, so the ids are collected from the whole file
    and filtered to the round's own."""
    path = os.path.join(reviews or _reviews_dir(), "round-%d" % number,
                        "REVIEW.md")
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as handle:
        text = handle.read().decode("utf-8")
    found = {name for name in re.findall(r"\bR%d-(\d+)\b" % number, text)}
    return sorted(("R%d-%d" % (number, int(name)) for name in found),
                  key=_finding_order)


# ROUND-8 FINDING R8-3. The verdict, read from the reviewer's own bytes.
#
# The block's verdict was any non-empty string and nothing compared it to
# anything: changing round 7's block verdict to `FREEZABLE AS WRITTEN` passed
# every structural predicate in this module while the verbatim review still
# ended `DO NOT FREEZE`. The freeze rule reads that token, so this is the one
# datum in the block that could authorise a freeze the record refuses.
#
# The comparison is PROTOCOL PARSING, not English semantics. The review prompt's
# output contract is "then one line exactly: `freezable as written`,
# `freezable after listed fixes`, or `DO NOT FREEZE`", so the review's final
# non-blank line is a token from a closed set, and it must be the token the
# block records. Nothing here reads a sentence for its meaning.
_VERDICT_OF_LINE = {line.casefold(): token for token, line
                    in render_round_status.VERDICT_LINES.items()}
# R9-1: the freeze-authorizing reading is exact — the line as the reviewer
# wrote it, byte for byte. The case-folded map above survives only for the
# diagnostic message that names a near-miss as a near-miss.
_VERDICT_OF_LINE_EXACT = {line: token for token, line
                          in render_round_status.VERDICT_LINES.items()}


def _review_verdict(number, reviews=None):
    """`(token, final line)` for the round's verbatim review, `(None, None)`
    when no review has landed, and `(None, line)` when the final line is not one
    of the three contract tokens."""
    path = os.path.join(reviews or _reviews_dir(), "round-%d" % number,
                        "REVIEW.md")
    if not os.path.isfile(path):
        return None, None
    with open(path, "rb") as handle:
        text = handle.read().decode("utf-8")
    lines = [line for line in (raw.rstrip("\r") for raw in text.split("\n"))
             if line.strip()]
    if not lines:
        return None, ""
    # ROUND-9 FINDING R9-1: RFC 0009 requires the final line to be EXACTLY the
    # verdict — the freeze-authorizing token is a registered freeze condition,
    # so the reading is byte-exact on the line (no case folding, no
    # indentation forgiveness). A review whose final line is "Freezable As
    # Written" or "  freezable as written" has not returned the exact words.
    return _VERDICT_OF_LINE_EXACT.get(lines[-1]), lines[-1]


def _tree_states(record_text=None, reviews=None):
    """`({number: facts}, problems)` — the state each round's ARTIFACTS show.

    This is the structural half of the cross-check and it is derived
    INDEPENDENTLY of the block: the prompt file, the verbatim review, the
    record's section, the finding ids the review itself carries, the verdict
    token its final line spells, and the disposition cells and severity column
    beside them. Nothing here reads a sentence for its meaning.
    `_block_states()` below declares the same things, and
    `test_the_state_the_block_declares_is_the_state_the_artifacts_show` is where
    the two must agree.

        complete            prompt + review + section + a written disposition
                            cell for every finding the review carries
        awaiting-review     prompt only
        awaiting-response   prompt + review + section, dispositions incomplete
        malformed           anything else

    ROUND-8 FINDING R8-3: the derived facts are now EVERY member the block
    declares — `state`, `verdict`, `severities` and `findings` — because the
    comparison used to be over `state` alone and the other three were declared
    against nothing.
    """
    text = _review_record() if record_text is None else record_text
    reviews = reviews or _reviews_dir()
    on_disk, problems = _rounds_on_disk(reviews)
    sections, section_problems = _record_sections(text)
    problems = list(problems) + section_problems

    states = {}
    for number in sorted(set(sections) | set(on_disk)):
        artifacts = on_disk.get(number, {"prompt": False, "review": False})
        body = sections.get(number)
        verdict, final_line = _review_verdict(number, reviews)
        facts = {
            "prompt": artifacts["prompt"],
            "review": artifacts["review"],
            "section": body is not None,
            "findings": _review_finding_ids(number, reviews) or [],
            "verdict": verdict,
            "finalLine": final_line,
            "dispositions": {},
            "pendingRows": [],
            "rowSeverities": {},
            "duplicateRows": [],
        }
        if body is not None:
            written, pending, row_severities, duplicates = _disposition_rows(
                number, body)
            facts["dispositions"] = written
            facts["pendingRows"] = pending
            facts["rowSeverities"] = row_severities
            facts["duplicateRows"] = duplicates
        # R8-3: the severity counts the TABLE states, comparable with the
        # block's map — counted only when the table's row set is exactly the
        # review's finding set, because a partial table counts nothing.
        facts["severities"] = None
        if facts["findings"] and \
                sorted(facts["rowSeverities"], key=_finding_order) == facts["findings"]:
            counted = {}
            for name in facts["findings"]:
                counted[facts["rowSeverities"][name]] = \
                    counted.get(facts["rowSeverities"][name], 0) + 1
            facts["severities"] = counted
        facts["range"] = ({"first": 1, "last": len(facts["findings"])}
                          if facts["findings"] else None)

        if not facts["prompt"]:
            facts["state"] = MALFORMED
            problems.append(
                "round %d has no committed reviews/round-%d/PROMPT.md; the "
                "regime commits the prompt before the reviewer reads"
                % (number, number))
        elif facts["duplicateRows"]:
            # R8-5: a finding named by two rows has two dispositions and two
            # severities, and which one the record means is not recoverable.
            facts["state"] = MALFORMED
            problems.append(
                "round %d's disposition table carries more than one row for %s; "
                "a finding named twice has no disposition"
                % (number, ", ".join(facts["duplicateRows"])))
        elif facts["review"] and verdict is None:
            # R8-3: a landed review whose final line is not one of the three
            # contract tokens is a review nothing can be bound to.
            facts["state"] = MALFORMED
            problems.append(
                "round %d's verbatim review ends %r and the output contract "
                "registers exactly %s"
                % (number, final_line,
                   ", ".join(render_round_status.VERDICT_LINES.values())))
        elif facts["review"] != facts["section"]:
            facts["state"] = MALFORMED
            problems.append(
                "round %d has %s and %s; a landed review and a record section "
                "arrive together"
                % (number,
                   "a verbatim review" if facts["review"] else "no verbatim review",
                   "a record section" if facts["section"] else "no record section"))
        elif not facts["review"]:
            facts["state"] = AWAITING_REVIEW
        elif not facts["findings"]:
            # THE CLEAN ROUND (round 12, 2026-08-19): a verbatim review that
            # carries no finding ids and ends on a contract token is a
            # zero-finding round. It is COMPLETE exactly when its section
            # exists and its table is as empty as the review — a row or a
            # pending cell would name a finding the review never returned.
            if facts["dispositions"] or facts["pendingRows"]:
                facts["state"] = MALFORMED
                problems.append(
                    "round %d's review carries no finding ids and its table "
                    "names %s" % (number, ", ".join(
                        sorted(list(facts["dispositions"])
                               + facts["pendingRows"]))))
            else:
                facts["state"] = COMPLETE
                facts["severities"] = {}
        elif (sorted(facts["dispositions"], key=_finding_order) == facts["findings"]
              and not facts["pendingRows"]):
            facts["state"] = COMPLETE
        else:
            facts["state"] = AWAITING_RESPONSE
        states[number] = facts
    return states, problems


def _block(record_text=None):
    """The record's round-state block, parsed and validated by the renderer's
    own loader — one implementation, so the sentence the documents carry and the
    data this module checks can never be read two different ways."""
    return render_round_status.parse_block(
        _review_record() if record_text is None else record_text)


def _block_states(record_text=None):
    return {entry["number"]: entry for entry in _block(record_text)["rounds"]}


# --- the block, and the tree it describes -----------------------------------

def test_the_round_state_block_is_the_registered_shape():
    """The block is the single machine-readable source, so its own shape is
    asserted before anything reads it: exactly one fenced block, rounds 1..N
    contiguous and ascending, no repeated number, at most one open round and it
    the highest, and every round that has returned a verdict carrying severity
    counts that sum to its finding range."""
    block = _block()
    numbers = [entry["number"] for entry in block["rounds"]]
    assert numbers == list(range(1, len(numbers) + 1)), numbers
    for entry in block["rounds"]:
        if entry["state"] == AWAITING_REVIEW:
            continue
        if sum(entry["severities"].values()) == 0:
            # THE CLEAN ROUND (round 12): zero findings, range null.
            assert entry["findings"] is None, entry
            continue
        assert sum(entry["severities"].values()) == entry["findings"]["last"]


def test_the_blocks_own_refusals_bite():
    """The shape rules have power in the other direction, run as mutations of
    the real block: a repeated round number, a section out of order, two open
    rounds, and a severity total that disagrees with the finding range must each
    be REFUSED rather than resolved. A validator nobody has seen refuse is a
    validator nobody has tested."""
    text = _review_record()
    block = _block(text)
    rounds = block["rounds"]
    highest = rounds[-1]

    def _record_with(new_rounds):
        body = json.dumps({"blockVersion": 1, "rounds": new_rounds}, indent=2)
        head, _, rest = text.partition(render_round_status.BLOCK_OPEN)
        _, _, tail = rest.partition(render_round_status.BLOCK_CLOSE)
        return "%s%s\n%s\n%s%s" % (head, render_round_status.BLOCK_OPEN, body,
                                   render_round_status.BLOCK_CLOSE, tail)

    duplicate = rounds + [dict(highest)]
    out_of_order = rounds[:-2] + [rounds[-1], rounds[-2]]
    second_open = [dict(entry) for entry in rounds]
    second_open[0]["state"] = AWAITING_RESPONSE
    miscounted = [dict(entry) for entry in rounds]
    # The miscount lands on the last round that CARRIES findings — an open
    # awaiting-review round holds none yet, and that is its correct shape.
    countable = max(i for i, entry in enumerate(miscounted)
                    if entry.get("findings"))
    miscounted[countable] = dict(
        miscounted[countable],
        findings={"first": 1,
                  "last": miscounted[countable]["findings"]["last"] + 1})
    for label, mutated in (("a repeated round number", duplicate),
                           ("two sections out of order", out_of_order),
                           ("a second open round", second_open),
                           ("a severity total that disagrees", miscounted)):
        with pytest.raises(render_round_status.BlockError):
            render_round_status.parse_block(_record_with(mutated))
    # and the real block still parses, so the refusals are not simply wide
    assert render_round_status.parse_block(_record_with(rounds))


def test_the_block_and_the_reviews_directory_carry_the_same_rounds():
    """The round set derived from the TREE rather than from a sentence, with
    ROUND-7 FINDING R7-4's duplicate-identity refusal asserted in both
    directions: the real tree is clean, and a `round-07` beside `round-7` is
    reported rather than collapsed onto it."""
    on_disk, problems = _rounds_on_disk()
    assert problems == [], "\n  ".join([""] + problems)
    assert sorted(on_disk) == sorted(_block_states()), (
        "reviews/ carries rounds %s and the block declares %s"
        % (sorted(on_disk), sorted(_block_states())))


def test_a_duplicate_round_identity_is_refused_and_not_normalised(tmp_path):
    """R7-4, run as the reviewer ran it. `round-7` and `round-07` are two
    directories and one integer; the round-6 reading kept whichever `os.listdir`
    returned last and reported no problem at all."""
    reviews = tmp_path / "reviews"
    for name in ("round-1", "round-2"):
        (reviews / name).mkdir(parents=True)
        (reviews / name / "PROMPT.md").write_text("p\n")
        (reviews / name / "REVIEW.md").write_text("r\n")
    clean, problems = _rounds_on_disk(str(reviews))
    assert problems == [] and sorted(clean) == [1, 2]

    (reviews / "round-02").mkdir()
    (reviews / "round-02" / "PROMPT.md").write_text("p\n")
    collided, problems = _rounds_on_disk(str(reviews))
    assert any("non-canonical" in problem for problem in problems), problems
    assert any("both round 2" in problem for problem in problems), problems
    assert collided[2]["review"] is True, (
        "the canonical round-2 must not be overwritten by the collision")

    (reviews / "round-three").mkdir()
    _ignored, problems = _rounds_on_disk(str(reviews))
    assert any("round-three" in problem for problem in problems), problems


def test_a_duplicate_record_section_is_refused_and_not_collapsed():
    """R7-4 on the record's own headings: the reviewer inserted a second
    adjacent `## Round 5` section and the reading returned `problems=[]` with an
    unchanged state map, because ascending order was the only thing checked
    before the sections went into a dictionary."""
    text = _review_record()
    sections, problems = _record_sections(text)
    assert problems == [], problems
    highest = max(sections)
    heading = "## Round %d — " % highest
    assert text.count(heading) == 1
    mutated = text.replace(heading, heading + "\n\n" + heading, 1)
    _sections, problems = _record_sections(mutated)
    assert any("more than one `## Round %d` section" % highest in problem
               for problem in problems), problems


def test_every_rounds_finding_range_is_the_one_its_verbatim_review_carries():
    """The block's finding range against the reviewer's own text: the ids the
    review names ARE `R<n>-1 … R<n>-<last>`, contiguous, with nothing missing
    and nothing invented. The severity counts sum to the same number
    (`parse_block()`), so a round states its size three ways — the block's
    range, the block's severities, and the review — and they must agree."""
    for number, entry in sorted(_block_states().items()):
        ids = _review_finding_ids(number)
        if entry["state"] == AWAITING_REVIEW:
            assert ids is None, (
                "round %d is awaiting review and a verbatim review has landed"
                % number)
            continue
        assert ids is not None, (
            "round %d has returned a verdict and carries no verbatim review"
            % number)
        expected = ([] if entry["findings"] is None else
                    ["R%d-%d" % (number, index)
                     for index in range(1, entry["findings"]["last"] + 1)])
        assert ids == expected, (
            "round %d's verbatim review names %s and the block registers %s"
            % (number, ids, expected))


def test_every_rounds_disposition_table_agrees_with_the_block():
    """The record's own table against the block: a complete round carries a
    written disposition cell for every finding, and its severity COLUMN counts
    what the block's severity map counts. A round whose table calls a MAJOR
    finding a MINOR one is a table that no longer describes the review it
    answers."""
    sections, problems = _record_sections(_review_record())
    assert problems == [], problems
    for number, entry in sorted(_block_states().items()):
        if entry["state"] == AWAITING_REVIEW:
            continue
        written, pending, severities, duplicates = _disposition_rows(
            number, sections[number])
        assert duplicates == [], (
            "round %d's table names %s more than once" % (number, duplicates))
        expected = ([] if entry["findings"] is None else
                    ["R%d-%d" % (number, index)
                     for index in range(1, entry["findings"]["last"] + 1)])
        if entry["state"] == COMPLETE:
            assert sorted(written, key=_finding_order) == expected, (
                "round %d is complete and its table disposes of %s"
                % (number, sorted(written, key=_finding_order)))
            assert pending == [], (
                "round %d is complete and carries placeholder cells %s"
                % (number, pending))
        if sorted(severities, key=_finding_order) == expected:
            counted = {}
            for name in expected:
                counted[severities[name]] = counted.get(severities[name], 0) + 1
            stated = {name: count
                      for name, count in entry["severities"].items() if count}
            assert counted == stated, (
                "round %d's block counts %s and its table's severity column "
                "counts %s" % (number, stated, counted))


def test_the_state_the_block_declares_is_the_state_the_artifacts_show():
    """The two halves, compared — EVERY declared member, not the state alone.

    The block DECLARES a state, a verdict, severity counts and a finding range;
    `_tree_states()` DERIVES all four from the prompt, the review, its final
    line, its finding ids, the section and the cells. ROUND-8 FINDING R8-3 is
    that only `state` was ever compared, so the other three were declarations
    nothing checked — which is the failure mode this whole layer exists for."""
    states, problems = _tree_states()
    assert problems == [], "\n  ".join([""] + problems)
    declared = _block_states()
    assert sorted(states) == sorted(declared), (
        "the tree shows rounds %s and the block declares %s"
        % (sorted(states), sorted(declared)))
    for number in sorted(states):
        facts, entry = states[number], declared[number]
        assert facts["state"] == entry["state"], (
            "round %d's artifacts show %s and the block declares %s"
            % (number, facts["state"], entry["state"]))
        assert facts["verdict"] == entry["verdict"], (
            "round %d's verbatim review ends %r, which is the verdict %r, and "
            "the block declares %r"
            % (number, facts["finalLine"], facts["verdict"], entry["verdict"]))
        assert facts["range"] == entry["findings"], (
            "round %d's review carries %d finding ids and the block declares "
            "the range %r"
            % (number, len(facts["findings"]), entry["findings"]))
        if facts["severities"] is None:
            assert facts["state"] != COMPLETE, (
                "round %d is complete and its table's severity column does not "
                "cover its findings" % number)
            assert entry["severities"] is None or facts["state"] in OPEN_STATES
            continue
        stated = {name: count for name, count
                  in (entry["severities"] or {}).items() if count}
        assert facts["severities"] == stated, (
            "round %d's table counts %s by severity and the block declares %s"
            % (number, facts["severities"], stated))


# --- ROUND-8 FINDING R8-3: the verdict is bound to the review ----------------

def test_every_rounds_block_verdict_is_the_token_its_review_returned():
    """The positive attestation, over the real tree: every round that has
    returned a verdict ends its verbatim review with one of the output
    contract's three lines, and the block records that line's token."""
    for number, entry in sorted(_block_states().items()):
        verdict, final_line = _review_verdict(number)
        if entry["state"] == AWAITING_REVIEW:
            assert verdict is None and final_line is None, (
                "round %d is awaiting review and a verbatim review has landed"
                % number)
            continue
        assert verdict is not None, (
            "round %d's verbatim review ends %r, which is not one of the output "
            "contract's three lines" % (number, final_line))
        assert entry["verdict"] == verdict, (
            "round %d's review ends %r and the block records %r"
            % (number, final_line, entry["verdict"]))


def test_a_block_verdict_the_review_did_not_return_is_refused():
    """R8-3, run as the reviewer ran it: round 7's block verdict changed to
    `FREEZABLE AS WRITTEN` — the one token that would authorise a freeze —
    while its verbatim review still ends `DO NOT FREEZE`. Every structural
    predicate passed. Two things must refuse it now: the closed vocabulary (a
    verdict outside the contract is not a verdict) and the binding to the
    reviewer's own final line."""
    text = _review_record()
    block = _block(text)
    rounds = block["rounds"]

    def _record_with(new_rounds):
        body = json.dumps({"blockVersion": 1, "rounds": new_rounds}, indent=2)
        head, _, rest = text.partition(render_round_status.BLOCK_OPEN)
        _, _, tail = rest.partition(render_round_status.BLOCK_CLOSE)
        return "%s%s\n%s\n%s%s" % (head, render_round_status.BLOCK_OPEN, body,
                                   render_round_status.BLOCK_CLOSE, tail)

    refusing = [number for number, entry in _block_states().items()
                if entry["verdict"] == render_round_status.DO_NOT_FREEZE]
    assert refusing, "no round returned DO NOT FREEZE; the mutation is vacuous"
    number = max(refusing)
    flipped = [dict(entry) for entry in rounds]
    flipped[number - 1]["verdict"] = render_round_status.FREEZABLE
    mutated = _record_with(flipped)
    # the block still parses — `FREEZABLE AS WRITTEN` is a contract token — and
    # the BINDING is what catches it
    declared = {entry["number"]: entry
                for entry in render_round_status.parse_block(mutated)["rounds"]}
    verdict, final_line = _review_verdict(number)
    assert verdict == render_round_status.DO_NOT_FREEZE, final_line
    assert declared[number]["verdict"] != verdict, (
        "the mutation must move the declared verdict")

    # and a verdict outside the contract is refused one layer earlier
    invented = [dict(entry) for entry in rounds]
    invented[number - 1]["verdict"] = "FREEZABLE, PROBABLY"
    with pytest.raises(render_round_status.BlockError):
        render_round_status.parse_block(_record_with(invented))
    for empty in ("", "   "):
        blanked = [dict(entry) for entry in rounds]
        blanked[number - 1]["verdict"] = empty
        with pytest.raises(render_round_status.BlockError):
            render_round_status.parse_block(_record_with(blanked))
    # …and the unmutated block still parses, so the refusals are not simply wide
    assert render_round_status.parse_block(_record_with(rounds))


def test_the_freeze_verdict_was_returned_by_a_clean_round_exactly():
    """The R8-1 tripwire, RETIRED BY FIRING — its designed successor.

    Its predecessor asserted that no round had returned the freeze verdict, so
    that the first round to do so would force this deliberate revisit instead
    of a sentence somebody forgot to update. Round 12 returned `freezable as
    written` on 2026-08-19 and the tripwire fired exactly as registered. What
    stands in its place is the positive attestation the event now supports:
    the freeze verdict on the record was returned by a COMPLETE round with
    ZERO findings, whose verbatim review's final line is the token byte-exact,
    and by no round that carries findings — a freeze authorized any other way
    fails here."""
    assert render_round_status.FREEZE_VERDICT in render_round_status.VERDICTS
    states, problems = _tree_states()
    assert problems == [], "\n  ".join([""] + problems)
    freeze_rounds = [n for n, entry in _block_states().items()
                     if entry["verdict"] == render_round_status.FREEZE_VERDICT]
    assert freeze_rounds, (
        "no round has returned the freeze verdict; if that is again the state "
        "of the record, restore the predecessor tripwire from round 12's "
        "history rather than weakening this attestation")
    for number in freeze_rounds:
        facts = states[number]
        assert facts["state"] == COMPLETE, (number, facts["state"])
        assert facts["findings"] == [], (number, facts["findings"])
        assert facts["finalLine"] == \
            render_round_status.VERDICT_LINES[render_round_status.FREEZE_VERDICT]


# --- ROUND-8 FINDING R8-4: the block is schema-closed at every depth ---------

def test_a_block_readable_two_ways_is_refused():
    """R8-4, in the three constructions the reviewer ran. The block's own
    docstring promised to refuse anything readable two ways and then used the
    ordinary decoder: a duplicate `blockVersion`, a duplicate `verdict` inside a
    round entry, and a surplus TOP-LEVEL member were all accepted, the first two
    resolving last-one-wins while a human reader saw the first."""
    text = _review_record()
    block = _block(text)
    body = json.dumps(block, indent=1)

    def _record_with_body(new_body):
        head, _, rest = text.partition(render_round_status.BLOCK_OPEN)
        _, _, tail = rest.partition(render_round_status.BLOCK_CLOSE)
        return "%s%s\n%s\n%s%s" % (head, render_round_status.BLOCK_OPEN,
                                   new_body, render_round_status.BLOCK_CLOSE,
                                   tail)

    assert render_round_status.parse_block(_record_with_body(body))

    duplicate_top = body.replace('{\n "blockVersion": 1,',
                                 '{\n "blockVersion": 1,\n "blockVersion": 2,', 1)
    assert duplicate_top != body
    with pytest.raises(render_round_status.BlockError) as caught:
        render_round_status.parse_block(_record_with_body(duplicate_top))
    assert "twice" in str(caught.value)

    duplicate_nested = body.replace('"verdict": "%s"'
                                    % block["rounds"][0]["verdict"],
                                    '"verdict": "%s",\n   "verdict": "%s"'
                                    % (block["rounds"][0]["verdict"],
                                       render_round_status.FREEZABLE), 1)
    assert duplicate_nested != body
    with pytest.raises(render_round_status.BlockError) as caught:
        render_round_status.parse_block(_record_with_body(duplicate_nested))
    assert "twice" in str(caught.value)

    surplus_top = json.dumps(dict(block, note="a member nothing reads"), indent=1)
    with pytest.raises(render_round_status.BlockError) as caught:
        render_round_status.parse_block(_record_with_body(surplus_top))
    assert "note" in str(caught.value)

    missing_top = json.dumps({"rounds": block["rounds"]}, indent=1)
    with pytest.raises(render_round_status.BlockError):
        render_round_status.parse_block(_record_with_body(missing_top))

    # and the nested objects are closed too: a surplus member in `findings`
    surplus_range = [dict(entry) for entry in block["rounds"]]
    surplus_range[0] = dict(surplus_range[0],
                            findings=dict(surplus_range[0]["findings"],
                                          note="x"))
    with pytest.raises(render_round_status.BlockError):
        render_round_status.parse_block(_record_with_body(
            json.dumps({"blockVersion": 1, "rounds": surplus_range}, indent=1)))


# --- ROUND-8 FINDING R8-5: the disposition table's identities and liveness ---

def test_a_duplicate_disposition_row_is_refused_and_not_overwritten():
    """R8-5's first half, run as the reviewer ran it: a SECOND row for a finding,
    carrying a different severity and a contradictory disposition. The rows went
    into dictionaries with no duplicate check and completion was key-set
    equality, so the later row silently won and the round still read `complete`."""
    text = _review_record()
    states, _problems = _tree_states(text)
    complete = [number for number, facts in states.items()
                if facts["state"] == COMPLETE and facts["findings"]]
    assert complete, "no complete round with findings to mutate"
    number = max(complete)
    name = states[number]["findings"][0]
    row = re.search(r"^\|\s*%s\s*\|[^|]*\|.*\|\s*$" % name, text, re.MULTILINE)
    assert row, name
    contradiction = "| %s | MINOR | **Rejected.** The finding does not hold. |" \
        % name
    mutated = text.replace(row.group(0), row.group(0) + "\n" + contradiction, 1)
    assert mutated != text

    written, _pending, severities, duplicates = _disposition_rows(
        number, _record_sections(mutated)[0][number])
    assert duplicates == [name], duplicates
    assert severities[name] != "MINOR", (
        "the first row must not be overwritten by the duplicate")
    assert "does not hold" not in written.get(name, ""), (
        "the contradictory later row must not become the disposition")

    after, problems = _tree_states(mutated)
    assert after[number]["state"] == MALFORMED, (
        "a round whose table names a finding twice is not a complete round")
    assert any("more than one row for %s" % name in problem
               for problem in problems), problems


def test_a_commented_out_disposition_table_does_not_complete_a_round():
    """R8-5's second half, the reviewer's construction exactly: wrapping ALL of
    a round's rows in one multiline HTML comment left the round reading
    `complete` with its whole table inactive. A fenced code block is the same
    defect in the other inactive context."""
    text = _review_record()
    states, _problems = _tree_states(text)
    complete = [number for number, facts in states.items()
                if facts["state"] == COMPLETE and facts["findings"]]
    number = max(complete)
    rows = re.findall(r"^\|\s*R%d-\d+\s*\|.*\|\s*$" % number, text, re.MULTILINE)
    assert len(rows) == len(states[number]["findings"]), (rows, number)
    block_of_rows = "\n".join(rows)
    assert block_of_rows in text

    for label, wrapper in (
            ("an HTML comment", "<!--\n%s\n-->"),
            ("a fenced code block", "```\n%s\n```")):
        mutated = text.replace(block_of_rows, wrapper % block_of_rows, 1)
        assert mutated != text, label
        after, _problems = _tree_states(mutated)
        assert after[number]["dispositions"] == {}, (
            "%s is not a disposition table: %s" % (label, after[number]))
        assert after[number]["state"] != COMPLETE, (
            "round %d stayed complete with its whole table inside %s"
            % (number, label))


# --- ROUND-8 FINDING R8-7: an inactive heading is not a heading --------------

def test_a_heading_inside_a_fence_or_a_comment_is_not_a_heading():
    """R8-7, in the reviewer's two constructions: the real corrected heading
    replaced by a generic one, with the exact required line placed inside a
    fenced code block, and the same inside a multiline HTML comment. Both
    passed both predicates — the ban saw no stale heading and the requirement
    saw its heading."""
    with open(os.path.join(_study(), "design", "POLICY-DRAFT.md"), "rb") as handle:
        whole = handle.read().decode("utf-8")
    assert _heading_lines(whole).count(_GOLD_SECTION_HEADING) == 1

    for label, replacement in (
            ("a fenced code block",
             "### Verification items\n\n```\n%s\n```" % _GOLD_SECTION_HEADING),
            ("a multiline HTML comment",
             "### Verification items\n\n<!--\n%s\n-->" % _GOLD_SECTION_HEADING),
            ("a tilde-fenced code block",
             "### Verification items\n\n~~~\n%s\n~~~" % _GOLD_SECTION_HEADING)):
        mutated = whole.replace(_GOLD_SECTION_HEADING, replacement, 1)
        assert mutated != whole, label
        assert _GOLD_SECTION_HEADING in mutated, (
            "the construction keeps the exact text in the file, which is why a "
            "raw substring requirement passed it (%s)" % label)
        assert _heading_lines(mutated).count(_GOLD_SECTION_HEADING) == 0, (
            "the corrected heading is inside %s and is not a heading" % label)

    # …and the same liveness must not hide a STALE heading that is live: the
    # ban still fires when the stale words sit outside every inactive context
    stale = "### Still open for gold authoring"
    fenced_decoy = whole.replace(
        _GOLD_SECTION_HEADING,
        "%s\n\n```\n%s\n```" % (stale, _GOLD_SECTION_HEADING), 1)
    assert _stale_gold_heading(fenced_decoy) == stale


def test_the_live_line_reader_keeps_the_documents_own_line_count():
    """`_live_lines()` is shared by the table reader and the heading reader, and
    the Setext half of the second one looks at the FOLLOWING line — so blanking
    inactive content must never change how many lines there are."""
    for relative in ("PREREG-REVIEW.md", "PREREGISTRATION.md",
                     os.path.join("design", "POLICY-DRAFT.md")):
        with open(os.path.join(_study(), relative), "rb") as handle:
            text = handle.read().decode("utf-8")
        assert len(_live_lines(text)) == len(text.split("\n")), relative
    sample = "a\n<!-- b\nc -->\nd\n```\n# e\n```\n# f\n"
    assert _live_lines(sample) == ["a", "", "", "d", "", "", "", "# f", ""]


def test_a_placeholder_disposition_cell_reopens_its_round():
    """R6-3's construction, kept, with ROUND-7 FINDING R7-3's length heuristic
    removed from underneath it. Each mutation of a real disposition cell must
    move the round the artifacts show from `complete` to `awaiting-response`."""
    text = _review_record()
    states, _problems = _tree_states(text)
    complete = [number for number, facts in states.items()
                if facts["state"] == COMPLETE and facts["findings"]]
    assert complete, "no complete round with findings to mutate"
    number = max(complete)
    name = states[number]["findings"][0]
    row = re.search(r"^\|\s*%s\s*\|([^|]*)\|(.*)\|\s*$" % name, text,
                    re.MULTILINE)
    assert row, name
    for replacement in ("", " ", " PENDING ", " — ", " pending ", " TBD ",
                        " n/a "):
        mutated = text.replace(
            row.group(0), "| %s |%s|%s|" % (name, row.group(1), replacement), 1)
        assert mutated != text
        after, problems = _tree_states(mutated)
        assert problems == [], problems
        assert name in after[number]["pendingRows"], (
            "%r read as a written disposition for %s" % (replacement, name))
        assert after[number]["state"] == AWAITING_RESPONSE, (
            "round %d stayed closed with %s's cell %r"
            % (number, name, replacement))


def test_a_prompt_only_round_reads_as_open_and_not_as_a_broken_tree(tmp_path):
    """R6-1's construction, kept: the round-opening commit, where
    `reviews/round-N/PROMPT.md` is committed and nothing else exists yet. That
    tree is the regime working correctly and the model must say so.

    ROUND-7 FINDING R7-1 is what happens when the model says so and the
    maintainer's ceremony does not: the round-7 prompt-only commit did not carry
    the rendered sentence, so the lifecycle tests were red on the commit whose
    greenness the prompt asserted. `harness/render_round_status.py --write` is
    the answer to that half, and this is the answer to this one."""
    text = _review_record()
    states, _problems = _tree_states(text)
    highest = max(states)
    reviews = tmp_path / "reviews"
    for number in states:
        (reviews / ("round-%d" % number)).mkdir(parents=True)
        (reviews / ("round-%d" % number) / "PROMPT.md").write_text("p\n")
        # A review lands only where the record carries the round's section —
        # the live tree may itself hold a prompt-only round, and giving it a
        # scratch review would manufacture exactly the mismatch under test.
        if states[number]["section"]:
            # A scratch review carries a finding id and ends with one of the
            # output contract's three tokens (R8-3), because a review that ends
            # any other way is malformed and this construction is about a
            # PROMPT-ONLY round, not about a malformed one.
            (reviews / ("round-%d" % number) / "REVIEW.md").write_text(
                "R%d-1\n\n%s\n"
                % (number, render_round_status.VERDICT_LINES[
                    render_round_status.DO_NOT_FREEZE]))
    opened = highest + 1
    (reviews / ("round-%d" % opened)).mkdir()
    (reviews / ("round-%d" % opened) / "PROMPT.md").write_text("prompt\n")

    after, problems = _tree_states(text, str(reviews))
    assert problems == [], "\n  ".join([""] + problems)
    assert after[opened]["state"] == AWAITING_REVIEW, after[opened]

    # and a review landing WITHOUT a record section is still malformed
    (reviews / ("round-%d" % opened) / "REVIEW.md").write_text(
        "R%d-1\n\nDO NOT FREEZE\n" % opened)
    _after, problems = _tree_states(text, str(reviews))
    assert any("a record section" in problem for problem in problems), (
        "a landed review with no section in the record must be reported: %s"
        % problems)


# --- the rendered sentence, required verbatim -------------------------------

def test_the_three_front_doors_carry_the_rendered_sentence_verbatim():
    """The whole positive attestation, and it is an EXACT COMPARISON rather than
    a search: the sentence is rendered from the block here, at test time, and
    each front door must carry that string exactly once.

    Nothing about its surroundings is examined. A header that reproduces the
    sentence and then denies it in the next paragraph passes this test and fails
    review — which is the registered decision, and the same place the truth of
    every other paragraph in these documents rests."""
    wanted = render_round_status.flat(render_round_status.sentence(_study()))
    for relative in render_round_status.SURFACES:
        with open(os.path.join(_study(), relative), "rb") as handle:
            text = handle.read().decode("utf-8")
        assert render_round_status.flat(text).count(wanted) == 1, (
            "%s must carry the rendered round-status sentence exactly once, "
            "verbatim; run `python harness/render_round_status.py --write`:\n"
            "  %s" % (relative, wanted))
    assert render_round_status.surface_problems(_study()) == [], (
        "the renderer's own --check disagrees with this test")


def test_the_rendered_sentence_moves_when_the_block_moves():
    """The property a remembered sentence can never have. Four mutations of the
    real block — a verdict changed, a round's state opened, a round added, the
    open round closed — must each change the rendered string, and the documents
    carry only the unmutated one."""
    block = _block()
    rendered = render_round_status.render(block)
    mutations = {}

    changed_verdict = json.loads(json.dumps(block))
    changed_verdict["rounds"][0]["verdict"] = "FREEZABLE AS WRITTEN"
    mutations["a changed verdict"] = changed_verdict

    closed = json.loads(json.dumps(block))
    for entry in closed["rounds"]:
        entry["state"] = COMPLETE
    if closed != block:
        # Between rounds every state is already complete, and closing nothing
        # is not a mutation — the round-close commit is exactly that state.
        mutations["the open round closed"] = closed

    opened = json.loads(json.dumps(block))
    opened["rounds"][-1]["state"] = AWAITING_RESPONSE
    opened["rounds"][-1]["verdict"] = block["rounds"][-1]["verdict"]
    if opened["rounds"][-1]["state"] == block["rounds"][-1]["state"]:
        opened["rounds"][-1]["state"] = COMPLETE
    mutations["the open round's state"] = opened

    added = json.loads(json.dumps(block))
    added["rounds"].append({"number": len(added["rounds"]) + 1,
                            "state": AWAITING_REVIEW, "verdict": None,
                            "severities": None, "findings": None})
    mutations["a round added"] = added

    texts = {}
    for relative in render_round_status.SURFACES:
        with open(os.path.join(_study(), relative), "rb") as handle:
            texts[relative] = render_round_status.flat(
                handle.read().decode("utf-8"))
    for label, mutated in sorted(mutations.items()):
        moved = render_round_status.render(mutated)
        assert moved != rendered, label
        for relative, text in texts.items():
            assert render_round_status.flat(moved) not in text, (
                "%s carries the sentence %s would render" % (relative, label))


# --- ROUND-8 FINDING R8-6: the markers are bound to what they enclose --------

def test_the_markers_must_enclose_the_sentence_and_not_merely_coexist_with_it(
        tmp_path):
    """R8-6, in the reviewer's constructions. `surface_problems()` counted the
    sentence and counted the markers and never required
    `BEGIN < the sentence < END`, so a document with a correct sentence
    ANYWHERE and a marker pair ANYWHERE passed — including a pair in the wrong
    order, and including markers enclosing something else entirely."""
    wanted = render_round_status.sentence(_study())
    good = ("# doc\n\n%s\n%s\n%s\n\ntail\n"
            % (render_round_status.BEGIN, wanted, render_round_status.END))

    def _problems(text):
        surface = tmp_path / render_round_status.SURFACES[0]
        surface.parent.mkdir(parents=True, exist_ok=True)
        for relative in render_round_status.SURFACES:
            path = tmp_path / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(good, encoding="utf-8")
        surface.write_text(text, encoding="utf-8")
        # the block is read from the real record; only the surfaces are scratch
        (tmp_path / "PREREG-REVIEW.md").write_text(_review_record(),
                                                   encoding="utf-8")
        return render_round_status.surface_problems(str(tmp_path))

    assert _problems(good) == []

    reversed_pair = ("# doc\n\n%s\n%s\n%s\n\ntail\n"
                     % (render_round_status.END, wanted,
                        render_round_status.BEGIN))
    assert any("order" in problem for problem in _problems(reversed_pair)), (
        "markers in the order END … BEGIN must be named, not partitioned")

    out_of_band = ("# doc\n\n%s\n\n%s\nsomething else\n%s\n\ntail\n"
                   % (wanted, render_round_status.BEGIN,
                      render_round_status.END))
    problems = _problems(out_of_band)
    assert any("markers enclose" in problem for problem in problems), problems

    second_copy = ("# doc\n\n%s\n%s\n%s\n\n%s\n"
                   % (render_round_status.BEGIN, wanted,
                      render_round_status.END, wanted))
    problems = _problems(second_copy)
    assert any("second copy" in problem for problem in problems), problems


def test_write_refuses_a_malformed_marker_pair_rather_than_rewriting_over_it(
        tmp_path):
    """R8-6's destructive half. `write()` partitioned on the first `BEGIN` and
    then on the first `END` in what followed, so on a REVERSED pair the middle
    was empty and the tail began after the `END` — writing it DISCARDED
    everything between the two markers. The refusal is asserted to leave the
    bytes untouched, which is the property that matters."""
    wanted = render_round_status.sentence(_study())
    reversed_pair = ("# doc\n\n%s\nload-bearing body\n%s\n\ntail\n"
                     % (render_round_status.END, render_round_status.BEGIN))
    for relative in render_round_status.SURFACES:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(reversed_pair, encoding="utf-8")
    (tmp_path / "PREREG-REVIEW.md").write_text(_review_record(),
                                               encoding="utf-8")
    with pytest.raises(render_round_status.BlockError) as caught:
        render_round_status.write(str(tmp_path))
    assert "order" in str(caught.value)
    for relative in render_round_status.SURFACES:
        assert (tmp_path / relative).read_text(encoding="utf-8") == \
            reversed_pair, "a refused write must not touch the document"

    # and an ORDERED pair is rewritten in place, keeping head and tail
    ordered = ("# doc\n\n%s\nstale\n%s\n\ntail\n"
               % (render_round_status.BEGIN, render_round_status.END))
    for relative in render_round_status.SURFACES:
        (tmp_path / relative).write_text(ordered, encoding="utf-8")
    moved = render_round_status.write(str(tmp_path))
    assert sorted(moved) == sorted(render_round_status.SURFACES)
    for relative in render_round_status.SURFACES:
        after = (tmp_path / relative).read_text(encoding="utf-8")
        assert after.startswith("# doc\n\n") and after.endswith("\n\ntail\n")
        assert wanted in after and "stale" not in after
    assert render_round_status.surface_problems(str(tmp_path)) == []


def test_the_registration_header_names_the_round_it_responds_to():
    """The revision a reader is holding is only meaningful against the round it
    answers: the highest COMPLETE round in the block. An open round is one this
    revision has not answered yet, by definition, so it does not move this
    number and the header does not have to lie while the round is open."""
    complete = [number for number, entry in _block_states().items()
                if entry["state"] == COMPLETE]
    assert complete, "no round is complete; the header names no response"
    answered = max(complete)
    with open(os.path.join(_study(), "PREREGISTRATION.md"), "rb") as handle:
        header = flatten(handle.read().decode("utf-8").split("\n## ")[0])
    found = re.findall(r"post-round-(\d+)", header)
    assert found, (
        "the registration's status header must name the round this revision "
        "responds to, as `post-round-N`")
    assert [int(number) for number in found] == [answered] * len(found), (
        "the highest round this revision has dispositioned is %d and the "
        "registration header says post-round-%s"
        % (answered, "/".join(found)))


def test_the_two_headers_agree_on_the_revision_ordinal():
    """A cheap cross-check with no external authority: whatever revision the
    study is on, its two front doors must say the same one."""
    pattern = re.compile(r"(%s) major revision" % "|".join(_REVISIONS))
    seen = {}
    for relative in ("README.md", "PREREGISTRATION.md"):
        with open(os.path.join(_study(), relative), "rb") as handle:
            header = flatten(handle.read().decode("utf-8").split("\n## ")[0])
        found = pattern.findall(header.lower())
        assert found, "%s's status header states no revision ordinal" % relative
        seen[relative] = found[0]
    assert len(set(seen.values())) == 1, seen


# --- R5-7 / R6-6 / R7-7: the policy draft's verification heading ------------
#
# This survives the descope as BANNED-CLAIM detection for one specific stale
# spelling already caught historically, plus one structural requirement. It
# adjudicates no English: the stale words are forbidden on a heading, the
# corrected heading is required AS A HEADING, and ROUND-7 FINDING R7-7's Setext
# construction is closed by reading Setext underlines rather than by parsing
# Markdown.
_GOLD_SECTION_HEADING = ("### Still open at this revision — verification items, "
                         "not authoring")
_STALE_GOLD_HEADING = re.compile(r"open for gold authoring", re.IGNORECASE)


def _heading_lines(text):
    """Every line this document presents as a heading: ATX (`#`-prefixed) and
    Setext (a line underlined by `=` or `-`).

    R7-7: the round-6 guard recognised ATX only, so a Setext
    `Still open for gold authoring` heading was invisible to the ban while the
    corrected ATX text, hidden inside an HTML comment, satisfied the raw
    substring requirement beside it. Both halves are structural now.

    ROUND-8 FINDING R8-7: and INACTIVE `#` lines were still counted. A generic
    heading in place of the real one, with the exact required line placed inside
    a fenced code block or a multiline HTML comment, satisfied both predicates —
    the ban saw no stale heading and the requirement saw its heading. The lines
    come through `_live_lines()` now, the same helper R8-5's table reader uses,
    so a heading is a heading only where the document presents one."""
    lines = _live_lines(text)
    out = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            out.append(stripped)
            continue
        following = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if stripped and len(following) >= 2 and (
                set(following) == {"="} or set(following) == {"-"}):
            out.append(stripped)
    return out


def _stale_gold_heading(text):
    for line in _heading_lines(text):
        if _STALE_GOLD_HEADING.search(line):
            return line
    return None


def test_the_policy_draft_carries_the_corrected_verification_heading():
    """Gold IS authored; V7 and V8 are verification items. The corrected heading
    must be a HEADING of the document — not a string somewhere in it — and the
    stale spelling must appear on no heading at all."""
    with open(os.path.join(_study(), "design", "POLICY-DRAFT.md"), "rb") as handle:
        whole = handle.read().decode("utf-8")
    headings = _heading_lines(whole)
    assert headings.count(_GOLD_SECTION_HEADING) == 1, (
        "POLICY-DRAFT.md must carry the corrected heading exactly once, as a "
        "heading: %r" % _GOLD_SECTION_HEADING)
    assert _stale_gold_heading(whole) is None, (
        "POLICY-DRAFT.md still calls its verification section open for gold "
        "authoring: %r" % _stale_gold_heading(whole))


def test_restoring_the_stale_gold_authoring_heading_fails_the_guard():
    """R6-6 and ROUND-7 FINDING R7-7, run as the reviewer ran them: the stale
    heading restored as ATX, restored as SETEXT, and the corrected text buried
    in an HTML comment while a Setext heading carries the stale words. Every one
    must be found, and the truncated read the R5-7 guard used must not."""
    with open(os.path.join(_study(), "design", "POLICY-DRAFT.md"), "rb") as handle:
        whole = handle.read().decode("utf-8")
    stale = "### Still open for gold authoring"
    atx = whole.replace(_GOLD_SECTION_HEADING, stale, 1)
    assert atx != whole
    assert _stale_gold_heading(atx) == stale

    setext = whole.replace(
        _GOLD_SECTION_HEADING,
        "Still open for gold authoring\n-----------------------------\n\n"
        "<!-- %s -->" % _GOLD_SECTION_HEADING, 1)
    assert setext != whole
    assert _stale_gold_heading(setext) == "Still open for gold authoring", (
        "a Setext heading is a heading; R7-7 is the guard that could not see one")
    assert _GOLD_SECTION_HEADING in setext, (
        "the reviewer's construction keeps the corrected text in the file, which "
        "is why a raw substring requirement passed it")
    assert _heading_lines(setext).count(_GOLD_SECTION_HEADING) == 0, (
        "the corrected heading is inside an HTML comment and is no longer a "
        "heading; requiring it as a HEADING is what closes R7-7")

    truncated = atx.split("\n---", 1)[0]
    assert _stale_gold_heading(truncated) is None, (
        "the heading is below the first `---`; a guard that truncates there "
        "cannot see this mutation, which is what R6-6 found")


# --- ROUND-4 FINDINGS R4-1 and R4-2: the adequacy lemma's own measurement ---
#
# R4-1: `m-a-183` was described everywhere as having "0 live-edit cells" while the
# committed measurement reports 419,904 live cells, 120 pinned-engine checks and zero
# differences. The lemma held; the description of what was measured did not. R4-2: the
# `subsumed-region-lemma` class has nine members and only six are the X1 repair's
# MARGINAL price — three were already unkillable in the pre-repair corpus.
#
# Both are cross-artifact properties, so both are asserted against the artifacts rather
# than against a remembered sentence.

def _adequacy_module():
    """`adequacy_search.py`, imported by path (see `_oc_module`). Cheap: the dense space
    is built lazily, not at import."""
    path = os.path.join(_study(), "design", "mutants", "adequacy_search.py")
    written = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("_s019_adequacy", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = written


@pytest.fixture(scope="module")
def adequacy_text():
    with open(os.path.join(_study(), "design", "mutants", "ADEQUACY.md"),
              "rb") as handle:
        return handle.read().decode("utf-8")


def _drop_measurements():
    return {record["id"]: record
            for record in _load("design/mutants/adequacy_drops.json")["mutants"]}


def _manifest_a_by_id():
    return {record["id"]: record for record in _load("design/mutants/refA/MANIFEST.json")}


_ZERO_LIVE = re.compile(r"live-edit cells: 0\b|\b0 live-edit cells")


def test_no_drop_mechanism_claims_zero_live_cells_the_measurement_denies():
    """R4-1, in the general form. A drop mechanism may say the edit is nowhere live —
    eleven of the twenty-six truly are — but only where `adequacy_drops.json` measured
    it. The committed manifest said it of `m-a-183`, whose edit is live at every cell of
    the space."""
    measured = _drop_measurements()
    manifest = _manifest_a_by_id()
    offenders = []
    for mid, record in sorted(measured.items()):
        mechanism = manifest[mid].get("adequacy", {}).get("dropMechanism", "")
        if _ZERO_LIVE.search(mechanism) and record["liveCells"]:
            offenders.append("%s: mechanism says zero live-edit cells; "
                             "adequacy_drops.json measured %d"
                             % (mid, record["liveCells"]))
    assert offenders == [], "\n  ".join([""] + offenders)


def test_no_adequacy_prose_claims_zero_live_cells_the_measurement_denies(
        adequacy_text):
    """The same property on the prose surface, and the reason it is a window search
    rather than a banned string: the sentence R4-1 caught was spelled two different ways
    in the same document ("`m-a-183`: 0 live-edit cells of 419,904" and "deletes the rule
    outright, with 0 live-edit cells"), and a third spelling would have passed a
    banned-string test."""
    flat_text = " ".join(adequacy_text.split())
    offenders = []
    for mid, record in sorted(_drop_measurements().items()):
        if not record["liveCells"]:
            continue
        for match in re.finditer(re.escape(mid), flat_text):
            window = flat_text[match.start():match.start() + 240]
            if _ZERO_LIVE.search(window):
                offenders.append("%s (live cells %d): %r"
                                 % (mid, record["liveCells"], window[:160]))
    assert offenders == [], "\n  ".join([""] + offenders)


def _lemma_measurements():
    """`m-a-183`'s four measured quantities, each read from the artifact that
    measured it. Returned together because the reader-facing guards below check
    every one of them against every surface, and a guard that reads three of the
    four is how round 5's R5-2 happened."""
    record = _drop_measurements()["m-a-183"]
    search = _load("design/mutants/adequacy_search.json")
    crosscheck = {row["id"]: row
                  for row in _load("design/mutants/adequacy_crosscheck.json")}
    return {
        "liveCells": record["liveCells"],
        "engineCheckedCells": record["engineCheckedCells"],
        "engineDifferences": len(record["engineDifferences"]),
        "scoredDifferences": search["armA"]["m-a-183"]["diffCellsOutsideX1"],
        "secondTranscriptionDifferences":
            crosscheck["m-a-183"]["differingCellsSecondTranscription"],
        "space": search["space"]["cells"],
        "sampleSize": _load(
            "design/mutants/adequacy_drops.json")["liveCellSampleSize"],
    }


# A stated difference count, in every spelling these documents use.
# ROUND-6 FINDING R6-2: the round-5 reading recognised only a count syntactically
# PRECEDING the word "differences", and in both reader sentences only the primary
# zero carried that noun — "0 from the second independently written
# transcription" and "0 over the 120 cells" were invisible to it, so changing
# them to seven passed. Three alternatives now, in the three shapes a difference
# count is written in here: before the noun, elliptically after a preposition,
# and after a LABEL. This is banned-claim detection — the positive attestation is
# the rendered clause below, not a window search.
_STATED_DIFFERENCES = re.compile(
    r"\b(?:(?P<n1>\d[\d,]*)|(?P<w1>zero|no))\s+(?:[a-z-]+\s+){0,4}?differences?\b"
    r"|\b(?:(?P<n2>\d[\d,]*)|(?P<w2>zero|no))\s+(?:from|by|across|over)\s+"
    r"(?:the\s+)?(?:[a-z0-9,()'’\-]+\s+){0,5}?"
    r"(?:transcriptions?|samples?|packs?|cells)\b"
    r"|\bdifferences?\b[^.;:]{0,44}?:\s*(?P<n3>\d[\d,]*)",
    re.IGNORECASE)


def _stated_difference_counts(text):
    counts = []
    for match in _STATED_DIFFERENCES.finditer(text):
        digits = match.group("n1") or match.group("n2") or match.group("n3")
        value = 0 if digits is None else int(digits.replace(",", ""))
        counts.append((value, " ".join(match.group(0).split())))
    return counts


def _measured_clause(measured):
    """The lemma's three outcomes as ONE labelled clause, RENDERED from the
    measurement — the form both reader surfaces must carry verbatim.

    ROUND-6 FINDING R6-2's fix, and the method it names: stop trying to
    out-regex a reader over free prose. Each of the three outcomes carries its
    own label, the whole clause is built here from the artifacts that measured
    it, and the surfaces are required to reproduce it exactly — so a measurement
    that moves moves the required sentence, and a sentence that moves without the
    measurement fails."""
    return ("MEASURED — trace-live cells: {live} of {space}; "
            "scored-surface differences (primary transcription): {scored}; "
            "scored-surface differences (second transcription): {second}; "
            "pinned-engine differences: {engine} of {checked} sampled cells "
            "(adequacy_drops.json, adequacy_crosscheck.json).").format(
        live="{:,}".format(measured["liveCells"]),
        space="{:,}".format(measured["space"]),
        scored=measured["scoredDifferences"],
        second=measured["secondTranscriptionDifferences"],
        engine=measured["engineDifferences"],
        checked=measured["engineCheckedCells"])


def _plain(text):
    """Markdown emphasis and code ticks removed, whitespace flattened: the form
    in which one rendered clause can be required of a JSON string and a Markdown
    paragraph at once."""
    return " ".join(text.replace("*", "").replace("`", "").split())


def _mentioning_paragraphs(text, needle):
    """The paragraphs of a markdown document that mention `needle`, flattened.
    A paragraph is the unit a claim is made in; a fixed-width window around the
    id cuts the sentence that carries the metrics in half."""
    return [" ".join(block.split())
            for block in re.split(r"\n\s*\n", text)
            if needle in block]


def test_the_deletion_lemma_publishes_all_three_of_its_measured_metrics(
        adequacy_text):
    """R4-1's positive half, and ROUND-5 FINDING R5-2 is why it now reads five
    numbers rather than two.

    Three DISTINCT metrics were measured for `m-a-183`, because each answers a
    different question: how much of the space the edit touches (trace-live cells),
    how much of it the two independent transcriptions agreed on (scored-surface
    differences, twice), and how much of it an ENGINE saw (the pinned sample and
    its differences). The R4-1 guard required only the live-cell count and the
    sample size, so replacing both reader surfaces with "seven scored and seven
    engine differences" passed every one of its three assertions — the zero that
    the whole lemma rests on was the number nothing bound.

    Every expected value is read out of the measurement at test time, and the
    zero-difference claims are bound in both directions: each surface must state
    them, and no surface may state a count the measurement denies.

    ROUND-6 FINDING R6-2 rebuilds the positive half. R5-2's version asked each
    surface for the live count, the sample size, some words, and ONE zero — so
    the second-transcription and engine outcomes could both be changed from 0 to
    7 on both surfaces and every assertion still passed. The positive half is now
    a clause RENDERED from the three measurements and required verbatim, with
    each outcome under its own label; the window search that remains is the
    negative half, where it belongs."""
    measured = _lemma_measurements()

    # the measurement itself, first: a description can only be checked against a
    # measurement that says what it is thought to say.
    assert measured["liveCells"] == measured["space"] == 419904, (
        "the deletion's edit is live at every cell of the dense space; if that "
        "changed, every sentence below has to change with it")
    assert measured["engineCheckedCells"] == measured["sampleSize"]
    difference_metrics = ("scoredDifferences", "secondTranscriptionDifferences",
                          "engineDifferences")
    assert [measured[name] for name in difference_metrics] == [0, 0, 0], (
        "this test's shape assumes the lemma holds on all three surfaces; if a "
        "future measurement finds a difference, the documents must state ITS "
        "count and this assertion is the place to say so")

    live = "{:,}".format(measured["liveCells"])
    checked = str(measured["engineCheckedCells"])
    mechanism = _manifest_a_by_id()["m-a-183"]["adequacy"]["dropMechanism"]
    surfaces = [("refA/MANIFEST.json's dropMechanism",
                 [" ".join(mechanism.split())]),
                ("ADEQUACY.md",
                 _mentioning_paragraphs(adequacy_text, "m-a-183"))]

    clause = _measured_clause(measured)
    for surface, blocks in surfaces:
        assert blocks, "%s says nothing about m-a-183" % surface
        # NEGATIVE, over every block: no stated difference count may be one the
        # measurement denies. This is what the seven-difference mutation trips.
        for block in blocks:
            for count, phrase in _stated_difference_counts(block):
                assert count in set(measured[name]
                                    for name in difference_metrics), (
                    "%s states %r about m-a-183 and the measured differences "
                    "are %s" % (surface, phrase,
                                [measured[name] for name in difference_metrics]))
        # POSITIVE: exactly one block carries the rendered clause, verbatim.
        #
        # ROUND-7 FINDING R7-2, and the registered decision descopes it rather
        # than escalating it. The round-6 version also asked whether the words
        # BEFORE the clause negated it, which the reviewer defeated from the
        # other side (`It is false that …` enclosing the whole block) and which
        # rejected the true sentence "there are not 7 differences" from a third.
        # The polarity analysis is deleted: what remains is exact reproduction of
        # a clause RENDERED from the measurement, and a surface that reproduces
        # its own attestation and then denies it is review's problem.
        carrying = [block for block in blocks if clause in _plain(block)]
        assert len(carrying) == 1, (
            "%s must carry m-a-183's measured clause exactly once, verbatim:\n"
            "  %s\nfound %d block(s) that do"
            % (surface, clause, len(carrying)))
        text = _plain(carrying[0])
        assert live in text and checked in text


def test_moving_any_of_the_three_outcomes_off_zero_fails_on_both_surfaces(
        adequacy_text):
    """ROUND-6 FINDING R6-2's construction, run rather than argued.

    The reviewer changed the second-transcription and engine outcomes from 0 to
    7 on both reader surfaces and every R5-2 assertion passed, because only the
    primary zero carried the noun the guard looked for. Two directions here: the
    rendered clause moves when any one of the three measurements moves (so a
    surface that keeps the old sentence fails), and each of the four spellings a
    seven could be written in is caught by the negative sweep."""
    measured = _lemma_measurements()
    clause = _measured_clause(measured)
    for name in ("scoredDifferences", "secondTranscriptionDifferences",
                 "engineDifferences"):
        moved = dict(measured)
        moved[name] = 7
        assert _measured_clause(moved) != clause, name

    for phrase in ("7 differences from the primary transcription",
                   "7 from the second independently written transcription",
                   "7 across the 120 pinned-jpack samples",
                   "scored-surface differences (second transcription): 7"):
        counts = [count for count, _ in _stated_difference_counts(phrase)]
        assert 7 in counts, (
            "the negative sweep cannot read %r; a seven written that way would "
            "pass" % phrase)

    # and over the real surfaces: the clause is what makes them pass, so a
    # surface with any outcome moved carries no block that reproduces it
    mechanism = _manifest_a_by_id()["m-a-183"]["adequacy"]["dropMechanism"]
    for surface, text in (("ADEQUACY.md", adequacy_text),
                          ("refA/MANIFEST.json", mechanism)):
        assert clause in _plain(text), surface
        mutated = _plain(text).replace("(second transcription): 0",
                                       "(second transcription): 7")
        assert clause not in mutated, surface
        assert 7 in [count for count, _ in _stated_difference_counts(mutated)]


def test_the_region_lemma_price_separates_the_class_from_the_repairs_cost():
    """R4-2. The published split is re-derived here from the same two committed inputs
    the generator reads — the stamped manifest's edits and ADEQUACY.md's 2026-08-15
    table — rather than compared to a remembered 9/6/3, so a re-keyed id or a rewritten
    historical row moves the test and the artifact together or fails."""
    module = _adequacy_module()
    committed = _load("design/mutants/adequacy_region_lemma_price.json")
    history = module.historical_dispositions()
    manifest = _manifest_a_by_id()

    gross = sorted(mid for mid, (cls, _) in module.DROPS.items()
                   if cls == module.REGION_LEMMA_CLASS)
    pre_existing, marginal = [], []
    for mid in gross:
        row = history.get(module.norm_edit(manifest[mid]["edit"]))
        (pre_existing if row and row["preRepairDisposition"] == "dropped"
         else marginal).append(mid)

    assert committed["members"] == gross
    assert committed["grossClassSize"] == len(gross)
    assert committed["preExistingDropCount"] == len(pre_existing)
    assert committed["marginalToRepairCount"] == len(marginal)
    assert committed["marginalToRepair"] == sorted(marginal)
    assert [row["current"] for row in committed["preExistingDrops"]] == \
        sorted(pre_existing)
    assert committed["grossClassSize"] == (committed["marginalToRepairCount"]
                                           + committed["preExistingDropCount"])
    assert pre_existing, (
        "the split is only informative while some member predates the repair; if a "
        "future corpus has none, say so here rather than deleting the distinction")
    # every pre-existing member must name the pre-repair mutant it was, and that
    # mutant must have been a DROP then — the whole content of "not the repair's price".
    for row in committed["preExistingDrops"]:
        assert row["preRepairId"] and row["preRepairDropMechanism"]
        assert row["preRepairDisposition"] == "dropped"


# ROUND-4 FINDING R4-2's reader-facing half, DESCOPED at round 7.
#
# R5-2 and R6-2 each rebuilt a prose sweep over the two ROLES the split assigns
# — "the repair's marginal price", "already unkillable" — with a number read out
# of the words around them and a polarity judged over an enclosing clause. Round
# 7's registered decision retires that layer with the rest of the
# English-semantics guards: `_role_claims()`, `_MARGINAL_ROLE`,
# `_PRE_EXISTING_ROLE`, `_NUMBER_TOKEN`, `_CLAUSE_BREAK` and `_NUMBER_WORDS` are
# deleted, and with them the test that ran the reviewer's false and negated role
# constructions.
#
# What remains is the POSITIVE attestation, which is the half that never
# depended on reading English: one labelled line, RENDERED from the derived
# artifact, required VERBATIM of all three registered surfaces. A surface whose
# counts move without the artifact fails; a surface that reproduces the line and
# then argues against it in the next sentence passes here and fails review.


def _split_price_line(price):
    """The split as ONE labelled line, rendered from the derived artifact.

    Every registered surface must carry this verbatim, so the counts a reader
    sees are the counts `adequacy_region_lemma_price.json` derived, and a
    surface that states them in some other form fails rather than being searched
    for."""
    return ("Gross class size: %d; marginal to the X1 repair: %d; already "
            "unkillable before it: %d"
            % (price["grossClassSize"], price["marginalToRepairCount"],
               price["preExistingDropCount"]))


def test_the_documents_state_the_marginal_price_and_not_only_the_class_size(
        adequacy_text, flat):
    """R4-2 on the reader-facing surfaces. The class size and the repair's price
    are different quantities, and every registered surface must publish both —
    in the one labelled form the artifact renders, exactly once each, so that
    the numbers a reader sees and the numbers the generator derived cannot drift
    apart. The surface must also NAME the class it is attributing, because a
    labelled line about an unnamed class attributes nothing."""
    price = _load("design/mutants/adequacy_region_lemma_price.json")
    gross = price["grossClassSize"]
    marginal = price["marginalToRepairCount"]
    pre_existing = price["preExistingDropCount"]
    assert gross == marginal + pre_existing and pre_existing, price
    line = _split_price_line(price)

    with open(os.path.join(_study(), "design", "POLICY-DRAFT.md"), "rb") as handle:
        policy = handle.read().decode("utf-8")
    surfaces = (("ADEQUACY.md", adequacy_text),
                ("PREREGISTRATION.md", flat),
                ("POLICY-DRAFT.md", policy))
    for name, raw in surfaces:
        text = _plain(raw)
        assert price["class"] in text.lower(), (
            "%s must name the %s class it is attributing" % (name, price["class"]))
        assert text.count(line) == 1, (
            "%s must carry the derived split exactly once, verbatim:\n  %s"
            % (name, line))


def test_the_split_line_moves_when_the_derived_split_moves():
    """The property that makes the line worth requiring: it is RENDERED, so a
    corpus whose split changes changes the sentence every surface owes, and a
    surface that keeps the old one fails the test above rather than passing a
    search that never noticed."""
    price = _load("design/mutants/adequacy_region_lemma_price.json")
    line = _split_price_line(price)
    for member in ("grossClassSize", "marginalToRepairCount",
                   "preExistingDropCount"):
        moved = dict(price)
        moved[member] = price[member] + 1
        assert _split_price_line(moved) != line, member
    with open(os.path.join(_study(), "design", "mutants", "ADEQUACY.md"),
              "rb") as handle:
        text = _plain(handle.read().decode("utf-8"))
    assert text.count(line) == 1
    moved = dict(price,
                 marginalToRepairCount=price["marginalToRepairCount"] + 1)
    assert _split_price_line(moved) not in text


def test_the_adequacy_record_names_the_members_of_both_halves_of_the_split():
    """R5-2's other half: the IDENTITIES, not only the counts. The published
    split is only checkable by a reader who can see which mutants are on each
    side, and `ADEQUACY.md` is the document that carries the class table — so the
    six marginal ids and the three pre-existing ones are read out of the derived
    artifact and required in it, with each pre-existing member's PRE-REPAIR id
    beside it (the whole content of "the repair did not buy this one")."""
    price = _load("design/mutants/adequacy_region_lemma_price.json")
    with open(os.path.join(_study(), "design", "mutants", "ADEQUACY.md"),
              "rb") as handle:
        text = " ".join(handle.read().decode("utf-8").split())
    for mid in price["marginalToRepair"]:
        assert mid in text, (
            "ADEQUACY.md must name the marginal member %s" % mid)
    for row in price["preExistingDrops"]:
        assert row["current"] in text, (
            "ADEQUACY.md must name the pre-existing member %s" % row["current"])
        assert row["preRepairId"] in text, (
            "%s was %s before the repair and ADEQUACY.md must say so — the "
            "match is by edit, and the pre-repair id is what makes it readable"
            % (row["current"], row["preRepairId"]))


def test_no_document_claims_every_boundary_edit_of_the_rule_is_invisible(
        adequacy_text, flat):
    """R4-2's second half. `m-a-076` moves this rule's lower risk edge and gold kills
    it, so 'no boundary edit is observable' is false. The killed set is derived from the
    manifest, not listed here."""
    price = _load("design/mutants/adequacy_region_lemma_price.json")
    manifest = _manifest_a_by_id()
    killed = [mid for mid in price["editsOnTheRule"] if manifest[mid].get("witnessSet")]
    assert price["editsOnTheRuleKilled"] == sorted(killed)
    assert price["boundaryEditsOnTheRuleKilled"], (
        "at least one boundary edit of the subsumed rule is killed by gold; the "
        "documents' narrowed claim depends on it")
    for name, text in (("ADEQUACY.md", " ".join(adequacy_text.split())),
                       ("PREREGISTRATION.md", flat)):
        lowered = " ".join(text.replace("*", "").replace("`", "").split()).lower()
        for claim in ("every edit that moves its boundaries is invisible",
                      "no gold suite can see an edit to its boundaries",
                      "mutants of that rule's boundaries change no cell"):
            assert claim not in lowered, (
                "%s still claims every boundary edit of the subsumed rule is "
                "unobservable, and %s is killed"
                % (name, ", ".join(price["boundaryEditsOnTheRuleKilled"])))


# --- ROUND-4 FINDING R4-4: admitted is not identity-passing -----------------

def test_the_pilot_banner_names_both_cohorts_with_the_arms_own_counts():
    """R4-4. The v4 banner said every identity count, identity-failing run list and kill
    rate was over runs that passed both controls, and called arm C "the one admitted
    run". Arm C has five admitted runs and one identity-passing one; the identity counts
    are over the five and the kill rates over the one. The banner's numbers are now
    rendered from the arm they describe, so this reads them back out of the arm."""
    pilot = _load("design/mutants/%s" % _oc_module().PILOT_FILE)
    banner = pilot["supersedingBanner"]
    block = pilot["perArm"]["C"]
    admitted = block["highKill"]["admittedRuns"]
    passing = block["identityPass"]
    assert admitted != passing, (
        "this test discriminates only while some arm's two cohorts differ; on a pilot "
        "with no identity failure anywhere, keep the distinction and say so here")
    assert "%d runs, of which %d passed" % (admitted, passing) in banner, (
        "the banner must state arm C's admitted and identity-passing counts as the "
        "arm publishes them")
    assert "%d admitted runs" % admitted in banner
    assert "one admitted run" not in banner.lower()
    for wrong in ("identity count, identity-failing run list and kill rate below is "
                  "therefore over runs that passed BOTH",):
        assert wrong not in banner, (
            "the banner again puts the identity counts over the identity-passing "
            "cohort; they are over the admitted one")
    # the counts the banner quotes must be the ones the arm publishes, not a memory
    assert len(block["perRun"]) == admitted
    assert block["identityFail"] + passing == admitted


def test_the_pilot_anchors_docstring_states_the_arms_the_artifact_publishes():
    """ROUND-5 FINDING R5-4. R4-4 fixed the banner and said it had fixed
    `pilot_anchor()`'s docstring with it; the docstring still called the rate a
    fraction of "scored runs" (the denominator-OUT reading the function stopped
    taking in round 3), still said zero identity failures were "no longer true of
    any arm" while A and B record zero, and still said an identity failure makes
    the registered denominator SMALLER than the identity-passing count when it
    makes it larger. Three sentences, one mistake, and all three survived because
    nothing read the docstring against the artifact.

    So the docstring's per-arm sentence is REBUILT here from the pilot and
    required verbatim: a reissued pilot that moves any arm fails this rather than
    leaving a generator describing a superseded issue. The relation itself is
    asserted as prose because it is the thing that must never be spelled wrong
    again."""
    module = _oc_module()
    pilot = _load("design/mutants/%s" % module.PILOT_FILE)
    doc = " ".join(module.pilot_anchor.__doc__.split())

    expected = "; ".join(
        "%s %d admitted, %d identity failures, %d identity-passing" % (
            arm,
            pilot["perArm"][arm]["highKill"]["admittedRuns"],
            pilot["perArm"][arm]["identityFail"],
            pilot["perArm"][arm]["identityPass"])
        for arm in "ABC") + "."
    assert expected in doc, (
        "pilot_anchor()'s docstring must state the current pilot's cohorts as "
        "the artifact publishes them:\n  %s\ngot:\n  %s" % (expected, doc))

    for arm in "ABC":
        block = pilot["perArm"][arm]
        assert block["highKill"]["admittedRuns"] == \
            block["identityPass"] + block["identityFail"], arm
    assert "ADMITTED = IDENTITY-PASSING + IDENTITY FAILURES" in doc, (
        "the docstring must state the relation, not only the numbers")

    # the three false sentences, each forbidden against what the artifact says
    zero_failure_arms = sorted(arm for arm in "ABC"
                               if not pilot["perArm"][arm]["identityFail"])
    if zero_failure_arms:
        assert "no longer true of any arm" not in doc, (
            "arms %s record zero identity failures and the docstring says that "
            "is true of no arm" % zero_failure_arms)
    failing_arms = sorted(arm for arm in "ABC"
                          if pilot["perArm"][arm]["identityFail"])
    if failing_arms:
        assert "denominator is smaller" not in doc, (
            "an identity failure makes the registered denominator LARGER than "
            "the identity-passing count (arms %s); the docstring says smaller"
            % failing_arms)
    anchor_sentence = doc.split(".")[0].lower()
    assert "admitted" in anchor_sentence and "scored runs" not in anchor_sentence, (
        "the anchor's denominator is admitted runs (§1a/§5), and naming it "
        "\"scored runs\" is the reading round 3 removed from the code: %r"
        % anchor_sentence)


def test_no_document_calls_arm_c_a_single_admitted_run():
    """R4-4 on every surface that quotes the pilot, including the review record — which
    is manifest-excluded but is still a document a frozen reader reads."""
    pilot = _load("design/mutants/%s" % _oc_module().PILOT_FILE)
    block = pilot["perArm"]["C"]
    admitted = block["highKill"]["admittedRuns"]
    surfaces = ("PREREG-REVIEW.md", "PREREGISTRATION.md", "README.md",
                "design/mutants/OC-TABLE.md", "design/mutants/ADEQUACY.md")
    offenders = []
    for relative in surfaces:
        path = os.path.join(_study(), relative)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as handle:
            text = flatten(handle.read().decode("utf-8")).lower()
        for phrase in ("one admitted run", "1 admitted run",
                       "arm c one admitted run"):
            if phrase in text:
                offenders.append("%s: %r (arm C has %d admitted runs)"
                                 % (relative, phrase, admitted))
    assert offenders == [], "\n  ".join([""] + offenders)


# --- ROUND-4 FINDING R4-5: the archived D3 question is archived -------------

def test_the_retained_d3_question_is_archived_and_past_tense(oc_text):
    """R4-5's second half. The superseded statement of D3 was retained in the present
    tense — "Two readings, and they move `N`" — under a closure that had chosen one of
    them. It is kept (the reasoning is the reason for the answer) and marked, and the
    live-sounding sentences are gone."""
    body = oc_text.split("### D3 as the gate originally put it")
    assert len(body) == 2, (
        "the retained D3 question must sit under its own ARCHIVED subsection")
    archived = body[1].split("\n## ")[0]
    heading = [line for line in oc_text.splitlines()
               if line.startswith("### D3 as the gate originally put it")]
    assert len(heading) == 1 and "ARCHIVED" in heading[0], heading
    assert "Nothing in this subsection is open" in archived
    for live in ("Two readings, and they move `N`",
                 "The pilot supplies no evidence either way",
                 "So authoring validity is not the threat"):
        assert live not in archived, (
            "the archived question still reads as live: %r" % live)


# --- ROUND-4 FINDING R4-6: the registered CI enforcement exists --------------

def _workflow():
    """The repository workflow, reached from the study. Returns None when the study
    tree is read outside the repository that carries the workflow."""
    path = os.path.join(os.path.dirname(os.path.dirname(_study())),
                        ".github", "workflows", "ci.yml")
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as handle:
        return handle.read().decode("utf-8")


def _parse_workflow_jobs(text):
    """The workflow's `jobs:` mapping, parsed structurally.

    ROUND-5 FINDING R5-5: the R4-6 test was raw substring matching over the file,
    and a COMMENT block carrying the expected strings passed it without defining
    an executable job. A comment cannot run the controls, so comments are
    stripped before anything here is believed — while the raw block is kept
    beside it, because one of the job's requirements (that it says in the file
    the matrix adjudication is an attempt) is a comment by design.

    Deliberately small: two-space-indented job keys under `jobs:`, four-space
    keys inside a job, a `steps:` list at six spaces with eight-space keys and
    ten-space `env:` members. That is this file's whole shape, and anything
    outside it reads as absent rather than as accepted."""
    lines = text.split("\n")
    live = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            live.append(None)               # keep the index, drop the content
            continue
        live.append(line)
    start = None
    for index, line in enumerate(live):
        if line is not None and re.match(r"^jobs:\s*$", line):
            start = index
            break
    if start is None:
        return {}
    jobs, current, raw_start = {}, None, None
    for index in range(start + 1, len(live)):
        line = live[index]
        if line is None:
            continue
        if re.match(r"^\S", line):
            break                            # left the jobs mapping
        name = re.match(r"^  (\S[^:]*):\s*$", line)
        if name:
            if current is not None:
                jobs[current]["rawEnd"] = index
            current = name.group(1)
            jobs[current] = {"lines": [], "rawStart": index, "rawEnd": len(lines)}
            continue
        if current is not None:
            jobs[current]["lines"].append(line)
    for name, job in jobs.items():
        job["raw"] = "\n".join(lines[job["rawStart"]:job["rawEnd"]])
        job["steps"] = _parse_steps(job["lines"])
        job["keys"] = {match.group(1): match.group(2).strip()
                       for match in (re.match(r"^    ([\w-]+):\s*(.*)$", line)
                                     for line in job["lines"]) if match}
        job["problems"] = _strict_job_problems(job["lines"])
    return jobs


# ROUND-7 FINDING R7-5: refuse on unparseable, never skip.
_JOB_KEY = re.compile(r"^    ([A-Za-z][\w-]*):\s*(.*)$")
_STEP_ITEM = re.compile(r"^      - ([A-Za-z][\w-]*):\s*(.*)$")
_STEP_KEY = re.compile(r"^        ([A-Za-z][\w-]*):\s*(.*)$")
_STEP_MEMBER = re.compile(r"^          ([A-Za-z][\w-]*):\s*(.*)$")
_BLOCK_SCALARS = ("|", ">", "|-", ">-", "|+", ">+")


def _strict_job_problems(lines):
    """Every construct this reading does not RECOGNISE, as a problem.

    ROUND-7 FINDING R7-5. The round-6 parser matched unquoted `[\\w-]+` keys and
    silently dropped every line that did not match, so valid YAML `"if": false`
    — the same mapping, quoted — disappeared from the parsed job and
    `_disabling_conditions()` returned nothing at all. A guard whose blind spot
    is a syntactic variant of the thing it forbids is not a guard.

    So the job's own lines are walked and anything outside the registered shape
    is REPORTED rather than ignored. The enforcement then fails closed over a
    workflow this reading cannot vouch for, and the answer to a legitimate new
    construct is to widen this grammar deliberately — which is a decision
    somebody makes — rather than to inherit a silent hole."""
    problems, in_steps, block_indent = [], False, None
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if block_indent is not None and indent >= block_indent:
            continue                     # the body of a block scalar
        block_indent = None
        match = _JOB_KEY.match(line)
        if match:
            in_steps = (match.group(1) == "steps"
                        and match.group(2).strip() == "")
            if match.group(2).strip() in _BLOCK_SCALARS:
                block_indent = 6
            continue
        if not in_steps:
            problems.append(
                "the job carries a construct this reading does not recognise, "
                "and an unrecognised construct is a refusal rather than a skip "
                "(R7-5): %r" % line)
            continue
        for pattern, body in ((_STEP_ITEM, 10), (_STEP_KEY, 10),
                              (_STEP_MEMBER, 12)):
            match = pattern.match(line)
            if match:
                if match.group(2).strip() in _BLOCK_SCALARS:
                    block_indent = body
                break
        else:
            problems.append(
                "the job's steps carry a construct this reading does not "
                "recognise, and an unrecognised construct is a refusal rather "
                "than a skip (R7-5): %r" % line)
    return problems


def _parse_steps(lines):
    """The `steps:` list of one job: each item's eight-space scalar keys, its
    `env:` members, and the body of a block scalar `run:`."""
    steps, step, key = [], None, None
    for line in lines:
        item = re.match(r"^      - ([\w-]+):\s*(.*)$", line)
        if item:
            step = {"env": {}}
            steps.append(step)
            step[item.group(1)] = item.group(2).strip()
            key = item.group(1)
            continue
        if step is None:
            continue
        scalar = re.match(r"^        ([\w-]+):\s*(.*)$", line)
        if scalar:
            key = scalar.group(1)
            value = scalar.group(2).strip()
            if key == "env" and not value:
                continue                     # the mapping opened above stands
            step[key] = value
            continue
        member = re.match(r"^          ([\w-]+):\s*(.*)$", line)
        if member:
            if key == "env":
                step["env"][member.group(1)] = member.group(2).strip().strip('"')
            else:
                step.setdefault(key + "Members", {})[member.group(1)] = \
                    member.group(2).strip()
            continue
        block = re.match(r"^        (\S.*)$", line)
        if block and key in ("run",):
            step[key] = (step.get(key, "") + " " + block.group(1)).strip()
    return steps


def _study_019_job():
    """The Study 019 job as a structure, or a skip reason."""
    workflow = _workflow()
    if workflow is None:
        return None, "the study tree is not inside the repository carrying ci.yml"
    jobs = _parse_workflow_jobs(workflow)
    if "study-019-harness" not in jobs:
        return None, None
    return jobs["study-019-harness"], None


def test_the_registered_ci_job_exists_and_runs_the_deterministic_controls(flat):
    """R4-6. §7 says CI runs the deterministic controls; the scaffold specified the job
    to add after T3; T3 closed and the job never landed, so the registration described
    enforcement that did not exist. This asserts the job the registration claims — by
    shape, not by a whole-file comparison, because the workflow carries other studies.

    ROUND-5 FINDING R5-5 makes the shape a PARSED one. This test reads `ci.yml`
    directly and depends on no other file, so the scaffold's registered deletion
    at the freeze cannot take the requirement with it."""
    assert "CI runs the deterministic controls only" in flat, (
        "§7 must still register what CI does; if that claim is withdrawn, this test "
        "goes with it rather than the other way round")
    workflow = _workflow()
    if workflow is None:
        pytest.skip("the study tree is not inside the repository carrying ci.yml")
    job, _ = _study_019_job()
    assert job is not None, (
        "the registration says CI runs the deterministic controls and no executable "
        "study-019-harness job exists in .github/workflows/ci.yml (a comment naming "
        "one is not one)")
    assert job["keys"].get("runs-on"), "the job defines no runner"
    steps = job["steps"]
    assert steps, "the job defines no steps"
    # ROUND-6 FINDING R6-4: a present job that cannot fail is not enforcement.
    assert _disabling_conditions(job) == [], _disabling_conditions(job)

    setup = [step for step in steps
             if step.get("uses", "").startswith("actions/setup-python@")]
    assert len(setup) == 1, "the job must set up exactly one interpreter"
    version = setup[0].get("withMembers", {}).get("python-version", "").strip('"')
    pins = _load("harness/PINS.json")
    series = pins["python"]["series"]
    assert version.startswith(series + "."), (
        "the job's interpreter (%r) must be a patch of the registered %s series"
        % (version, series))

    working = "studies/019-authorship-across-representations"
    wanted = {"python harness/integrity.py": {"PYTHONSAFEPATH", "PYTHONDONTWRITEBYTECODE"},
              "python -m pytest harness/tests -q": {"PYTHONDONTWRITEBYTECODE"}}
    for command, environment in wanted.items():
        matching = [step for step in steps if step.get("run", "") == command]
        assert len(matching) == 1, (
            "the job must run %r in exactly one step; found %d"
            % (command, len(matching)))
        step = matching[0]
        assert step.get("working-directory") == working, (
            "%r must run in %s, not %r" % (command, working,
                                           step.get("working-directory")))
        for name in environment:
            assert step["env"].get(name) == "1", (
                "%r must run under %s=1 (integrity.py refuses without "
                "PYTHONSAFEPATH; a run that writes bytecode breaks the integrity "
                "step on the next one)" % (command, name))

    # the pinned action SHAs are the workflow's own, copied rather than invented
    for action in ("actions/checkout@", "actions/setup-python@"):
        used = {line.split(action, 1)[1].split()[0]
                for line in workflow.splitlines()
                if action in line and not line.strip().startswith("#")}
        assert len(used) == 1, (
            "the workflow pins %s at more than one SHA (%s); the Study 019 job must "
            "copy the file's pin, not introduce another" % (action, sorted(used)))
    # and the attempt is stated to be an attempt — a comment, by design
    assert "ATTEMPT, not a test" in job["raw"] or "attempt, not a test" in job["raw"], (
        "the job must say in the file that the matrix adjudication never runs in CI")


def test_a_comment_shaped_like_the_job_is_not_the_job():
    """R5-5's discriminating case, and the reason the parse above exists. The
    retained R4-6 test passed on a workflow whose Study 019 job was commented
    out in its entirety — every expected substring present, nothing executable.
    This runs that mutation over the real file."""
    workflow = _workflow()
    if workflow is None:
        pytest.skip("the study tree is not inside the repository carrying ci.yml")
    jobs = _parse_workflow_jobs(workflow)
    assert "study-019-harness" in jobs, "no job to mutate; see the test above"
    commented = "\n".join(
        ("# " + line) if line.strip() else line
        for line in jobs["study-019-harness"]["raw"].split("\n"))
    mutated = workflow.replace(jobs["study-019-harness"]["raw"], commented)
    assert mutated != workflow
    assert "study-019-harness" not in _parse_workflow_jobs(mutated), (
        "a commented-out job still parses as a job; the shape check has no power")
    # and every substring the old test looked for survives the mutation, which is
    # exactly why the old test passed it
    for phrase in ("study-019-harness:", "python harness/integrity.py",
                   "python -m pytest harness/tests -q", 'PYTHONSAFEPATH: "1"'):
        assert phrase in mutated


def _disabling_conditions(job):
    """ROUND-6 FINDING R6-4. Every way this workflow's shape lets a job be
    present and not run.

    The R5-5 parser recorded the job's keys and its steps and then asserted only
    that a runner and the two commands were there, so `if: false` on the job —
    or on either required step — left every assertion passing over a job that
    never executes. A job that cannot fail is not enforcement, and the
    registration's claim is that CI RUNS the deterministic controls.

    ROUND-7 FINDING R7-5 adds the parser's own refusals to the list. A job this
    reading cannot fully account for is a job whose disabling conditions this
    reading cannot have counted, so the unparseable construct IS a disabling
    condition as far as the enforcement is concerned."""
    problems = list(job.get("problems", []))
    for key in ("if", "continue-on-error"):
        if key in job["keys"]:
            problems.append("the job carries a job-level %s: %r"
                            % (key, job["keys"][key]))
    for index, step in enumerate(job["steps"]):
        for key in ("if", "continue-on-error"):
            if key in step:
                problems.append("step %d (%s) carries %s: %r"
                                % (index, step.get("name") or step.get("run")
                                   or step.get("uses"), key, step[key]))
    return problems


def test_the_registered_ci_job_carries_no_condition_that_disables_it():
    """R6-4's construction, run over the real workflow: the job with `if: false`
    at the job level, at the step level, and `continue-on-error: true` on the
    step that runs the suite. Each must be reported, and the real job must carry
    none of them."""
    workflow = _workflow()
    if workflow is None:
        pytest.skip("the study tree is not inside the repository carrying ci.yml")
    job, _reason = _study_019_job()
    assert job is not None, "no Study 019 job in the workflow"
    assert _disabling_conditions(job) == [], _disabling_conditions(job)

    raw = job["raw"]
    mutations = (
        ("job-level if", raw.replace("    runs-on:", "    if: false\n    runs-on:", 1)),
        ("job-level continue-on-error",
         raw.replace("    runs-on:", "    continue-on-error: true\n    runs-on:", 1)),
        ("step-level if",
         raw.replace("        run: python -m pytest harness/tests -q",
                     "        if: false\n        run: python -m pytest harness/tests -q",
                     1)),
        ("step-level continue-on-error",
         raw.replace("        run: python harness/integrity.py",
                     "        continue-on-error: true\n"
                     "        run: python harness/integrity.py", 1)),
    )
    for label, mutated_raw in mutations:
        assert mutated_raw != raw, label
        jobs = _parse_workflow_jobs(workflow.replace(raw, mutated_raw, 1))
        assert "study-019-harness" in jobs, label
        assert _disabling_conditions(jobs["study-019-harness"]) != [], (
            "%s left the job looking enforced" % label)


def test_a_construct_the_ci_reading_cannot_parse_is_a_refusal_and_not_a_skip():
    """ROUND-7 FINDING R7-5, run as the reviewer wrote it, plus the general
    rule it is an instance of.

    `"if": false` is valid YAML and means exactly what `if: false` means. The
    round-6 mini-parser accepted only unquoted keys, so the quoted spelling was
    not "rejected" — it was INVISIBLE, and the job it disabled passed every
    assertion about the job's shape. Four constructions here: the reviewer's
    quoted `if` at the job level, the same at the step level, a quoted
    `continue-on-error`, and a plain unknown line. Each must make the job
    unvouchable, and the real job must be parsed with no problem at all."""
    workflow = _workflow()
    if workflow is None:
        pytest.skip("the study tree is not inside the repository carrying ci.yml")
    job, _reason = _study_019_job()
    assert job is not None, "no Study 019 job in the workflow"
    assert job["problems"] == [], (
        "the real job must parse cleanly; if this fails the grammar is too "
        "narrow and the answer is to widen it deliberately, not to skip")
    assert _disabling_conditions(job) == []

    raw = job["raw"]
    mutations = (
        ('quoted job-level "if"',
         raw.replace("    runs-on:", '    "if": false\n    runs-on:', 1)),
        ('quoted job-level "continue-on-error"',
         raw.replace("    runs-on:",
                     '    "continue-on-error": true\n    runs-on:', 1)),
        ('quoted step-level "if"',
         raw.replace("        run: python -m pytest harness/tests -q",
                     '        "if": false\n'
                     "        run: python -m pytest harness/tests -q", 1)),
        ("an unknown job-level construct",
         raw.replace("    runs-on:", "    <<: *disable\n    runs-on:", 1)),
    )
    for label, mutated_raw in mutations:
        assert mutated_raw != raw, label
        jobs = _parse_workflow_jobs(workflow.replace(raw, mutated_raw, 1))
        assert "study-019-harness" in jobs, label
        mutated = jobs["study-019-harness"]
        assert mutated["problems"] != [], (
            "%s parsed as if it were not there" % label)
        assert _disabling_conditions(mutated) != [], (
            "%s left the job looking enforced" % label)


def test_the_ci_interpreter_rationale_matches_what_the_registry_actually_pins():
    """R5-5's third residual. The job's comment said the registry recorded the exact
    patch and that the scorer refused any other; the registry pins the SERIES by
    design (Study 012 round-3 finding 20 — the running patch level is reported, not
    required) and `integrity.verify_interpreter()` compares major and minor only. The
    exact patch in CI is a REPRODUCIBILITY choice for the runner, and the file must say
    that rather than claim an enforcement that does not exist.

    ROUND-6 FINDING R6-4: the banned claims are ASSEMBLED from the registry rather
    than quoted, because this file is itself inside the swept scope and a test that
    carries the sentence it forbids is an offender."""
    job, reason = _study_019_job()
    if job is None:
        pytest.skip(reason or "no Study 019 job in the workflow")
    pins = _load("harness/PINS.json")
    entry = pins["python"]
    assert set(entry) == {"implementation", "note", "series"}, (
        "the registry's python member registers an implementation and a SERIES; if a "
        "patch level is ever registered, this test and the workflow comment move "
        "together: %s" % sorted(entry))
    raw = job["raw"]
    registry = _REGISTRY_TOKENS[0]
    for false_claim in ("harness/%s records %s.11" % (registry, entry["series"]),
                        "%s records the patch level" % registry,
                        "refuses to adjudicate under anything else"):
        assert false_claim not in raw, (
            "the workflow claims %r and the registry pins only the %s series"
            % (false_claim, entry["series"]))
    assert entry["series"] in raw, (
        "the job must name the series the registry actually pins (%s)"
        % entry["series"])


# ROUND-6 FINDING R6-4: the patch-pin claim, swept over the WHOLE live tree.
#
# R5-5 corrected the false rationale in `ci.yml` and left the same sentence
# standing in `SCAFFOLD.md` — a live ceremony surface an operator reads at the
# freeze. One surface was fixed because one surface was named; the class is the
# claim, not the file, so the check is a sweep with a DERIVED scope.
#
# The rule is structural rather than a list of spellings: the registry records a
# SERIES and no patch, so no true sentence needs to name the registry (or the
# function that enforces it) and a full patch level together. A sentence that
# does is claiming an enforcement that does not exist, whatever words it uses to
# claim it.
_REGISTRY_TOKENS = ("PINS.json", "verify_interpreter")
# Historical surfaces, out of scope by construction: the verbatim reviews are
# another party's text and the review record is the append-only history, which
# must be able to quote a claim in order to record its correction.
_HISTORICAL = ("PREREG-REVIEW.md", "reviews/")


def _live_surfaces(study):
    """Every live text surface of the study, plus the workflow. Derived by walk
    rather than enumerated, so a new document enters the sweep by existing."""
    out = []
    for base, directories, files in os.walk(study):
        directories[:] = [name for name in directories
                          if name not in (".git", "__pycache__", "reviews")]
        for name in sorted(files):
            if not name.endswith((".md", ".py", ".json", ".yml", ".yaml",
                                  ".sh", ".rego")):
                continue
            relative = os.path.relpath(os.path.join(base, name), study)
            relative = relative.replace(os.sep, "/")
            if any(relative.startswith(skip) for skip in _HISTORICAL):
                continue
            out.append((relative, os.path.join(base, name)))
    return out


def _swept_texts(study):
    """`(name, text, prose?)` for the sweep: every live surface of the study,
    plus THIS STUDY'S CI job.

    The workflow carries other studies' jobs, other studies' registries and
    other studies' claims about them, which this study's tests have no standing
    over and no way to check — 016, 017 and 018 each pin their own interpreter
    their own way. The scope of the sweep is 019's own claims, so it is 019's own
    parsed job block that is read and not the whole file."""
    out = []
    for relative, path in _live_surfaces(study):
        with open(path, "rb") as handle:
            try:
                text = handle.read().decode("utf-8")
            except UnicodeDecodeError:
                continue
        out.append((relative, text, relative.endswith(".md")))
    job, _reason = _study_019_job()
    if job is not None:
        out.append((".github/workflows/ci.yml (study-019-harness)",
                    job["raw"], False))
    return out


def _claim_units(text, prose):
    """The units a claim is made in.

    Markdown prose wraps across lines, so its unit is the PARAGRAPH; a table row
    and a heading are their own units, and in YAML, JSON and source every line
    is. Getting this wrong in either direction breaks the sweep: flattening a
    whole workflow into one "sentence" makes every file an offender, and reading
    prose line by line lets a claim escape by wrapping."""
    units, paragraph = [], []
    for line in text.split("\n"):
        stripped = line.strip()
        own_unit = (not prose) or stripped.startswith(("|", "#", "```"))
        if not stripped or own_unit:
            if paragraph:
                units.append(" ".join(paragraph))
                paragraph = []
            if stripped and own_unit:
                units.append(stripped)
            continue
        paragraph.append(stripped)
    if paragraph:
        units.append(" ".join(paragraph))
    out = []
    for unit in units:
        out.extend(re.split(r"(?<=[.!?])\s+", unit))
    return out


def _patch_pin_offenders(study, series):
    patch = re.compile(r"(?<![\w.])%s\.\d+" % re.escape(series))
    offenders = []
    for relative, text, prose in _swept_texts(study):
        for sentence in _claim_units(text, prose):
            if not patch.search(sentence):
                continue
            for token in _REGISTRY_TOKENS:
                if token in sentence:
                    offenders.append("%s: %r" % (relative, sentence[:200]))
                    break
    return offenders


def test_no_live_surface_claims_the_registry_pins_a_patch_level():
    """R6-4. `harness/PINS.json` registers the CPython SERIES and
    `integrity.verify_interpreter()` compares implementation and series only —
    Study 012's round-3 finding 20 keeps the running patch REPORTED and not
    required. Round 5 corrected the one surface the reviewer had named and left
    `SCAFFOLD.md` saying the registry records the patch and the scorer refuses
    anything else, on the page an operator reads at the freeze.

    Both halves are asserted: the registry really does register a series and no
    patch, and no live surface puts the registry and a patch level in one
    sentence. If a patch level is ever registered, this test and every one of
    those sentences move together."""
    entry = _load("harness/PINS.json")["python"]
    assert set(entry) == {"implementation", "note", "series"}, sorted(entry)
    assert re.fullmatch(r"\d+\.\d+", entry["series"]), entry["series"]
    offenders = _patch_pin_offenders(_study(), entry["series"])
    assert offenders == [], (
        "the registry pins the %s series and these live sentences claim a patch "
        "level with it:\n  %s" % (entry["series"], "\n  ".join(offenders)))


def test_the_patch_pin_sweep_finds_the_claim_round_five_left_standing():
    """The sweep's own discriminating case: the sentence R6-4 found, restored
    into the file it was found in. A guard that passes over a tree it has never
    been shown to fail on is a guard nobody has tested."""
    entry = _load("harness/PINS.json")["python"]
    # Assembled from the registry rather than quoted, so this file — which is
    # itself inside the swept scope — does not carry the banned pairing.
    stale = ("the exact pinned interpreter `python-version: \"%s.11\"` — not "
             "`\"%s\"`; `harness/%s` records the patch level and the scorer "
             "refuses anything else"
             % (entry["series"], entry["series"], _REGISTRY_TOKENS[0]))
    hit = [sentence for sentence in _claim_units(stale, True)
           if re.search(r"(?<![\w.])%s\.\d+" % re.escape(entry["series"]),
                        sentence)
           and any(token in sentence for token in _REGISTRY_TOKENS)]
    assert hit, (
        "the sweep cannot see the sentence it exists to forbid: %r" % stale)


# The stale-lifecycle register, and the one file on it that the freeze DELETES.
# ROUND-5 FINDING R5-5: the retained R4-6 test opened every one of these
# unconditionally, so the first post-freeze commit — which deletes `SCAFFOLD.md`
# by the scaffold's own step 9 — turned this guard into a `FileNotFoundError`.
# A registered deletion must not be able to fail the suite, and it must not be
# able to take the OTHER files' assertions with it either.
_DELETED_AT_FREEZE = ("harness/SCAFFOLD.md",)
_STALE_LIFECYCLE_NOTES = (
    ("harness/SCAFFOLD.md", ("What remains owed in this file is T3 alone",
                             "THIS IS THE ONLY ITEM LEFT IN THIS FILE",
                             "Do not add the job until T3 is done")),
    ("harness/batch.py", ("item T3 records that `design/` still",)),
    ("harness/PINS.json", ("not yet assembled",)),
    ("harness/e4lib/census.py", ("109 at the current revision",)),
    # ROUND-5 FINDING R5-7's class, at the place it bit hardest: §7's own gate
    # sentence said the tree still owed committed design sources and carried
    # stale caches that "must be committed" — which is the round-4 defect
    # written down as an instruction.
    ("PREREGISTRATION.md", ("stale bytecode caches that "
                            "`integrity.verify_bytecode()` refuses must be "
                            "committed",)),
)


def _stale_lifecycle_offenders(study):
    """The register applied to a tree. A file registered as deleted at the
    freeze is skipped when it is absent; every other file must be there."""
    offenders = []
    for relative, stale in _STALE_LIFECYCLE_NOTES:
        path = os.path.join(study, relative)
        if not os.path.isfile(path):
            if relative in _DELETED_AT_FREEZE:
                continue
            offenders.append("%s: registered for this check and absent" % relative)
            continue
        with open(path, "rb") as handle:
            text = flatten(handle.read().decode("utf-8"))
        for phrase in stale:
            if flatten(phrase) in text:
                offenders.append("%s: %r" % (relative, phrase))
    return offenders


def test_no_lifecycle_note_still_calls_a_landed_item_outstanding():
    """R4-6's other half: the notes that describe the study's own state. Each of these
    said something true when it was written and false when the reviewer read it — the
    scaffold's "T3 alone remains", the batch tripwire's "design/ still holds untracked
    sources", the pins registry's "the scorer, not yet assembled", and the census's
    quotation of a §5 row count that had moved."""
    assert _stale_lifecycle_offenders(_study()) == [], \
        "\n  ".join([""] + _stale_lifecycle_offenders(_study()))
    # the untracked-source condition itself, asserted rather than described
    import subprocess as _subprocess
    tracked = set(_subprocess.run(["git", "ls-files", "-z", "--", "."],
                                  cwd=_study(), capture_output=True,
                                  check=True).stdout.decode("utf-8").split("\0"))
    untracked, caches = [], []
    for base, _dirs, files in os.walk(_study()):
        if os.path.basename(base) == "__pycache__":
            caches.append(os.path.relpath(base, _study()))
        for name in files:
            if not name.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(base, name), _study())
            if rel.replace(os.sep, "/") not in tracked:
                untracked.append(rel)
    assert untracked == [], (
        "SCAFFOLD T3 is recorded LANDED and these sources are untracked: %s"
        % sorted(untracked))
    assert caches == [], (
        "T3 is recorded LANDED and these bytecode caches exist: %s" % sorted(caches))


def test_the_lifecycle_check_survives_the_scaffolds_registered_deletion(tmp_path):
    """R5-5's first residual, run rather than argued. `SCAFFOLD.md` §9 records
    that the file is deleted in the first post-freeze commit; simulating its
    absence raised `FileNotFoundError` out of the retained R4-6 guard, so the
    freeze the scaffold describes broke the test that enforces the scaffold's
    own closed items.

    The register is applied to a scratch tree with the scaffold removed and
    every other registered file copied — so the deletion is tolerated and the
    remaining assertions still bite, which is the property that matters."""
    import shutil
    scratch = tmp_path / "post-freeze"
    for relative, _stale in _STALE_LIFECYCLE_NOTES:
        source = os.path.join(_study(), relative)
        if not os.path.isfile(source):
            continue
        target = scratch / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    # The scaffold's deletion LANDED in the first post-freeze commit, so on the
    # live tree there is nothing to copy and nothing to unlink: the scratch
    # tree is already the post-deletion shape this test simulates. Pre-freeze
    # checkouts (and history) still carry the file, and there the simulation
    # deletes the copy as before.
    scaffold_copy = scratch / "harness" / "SCAFFOLD.md"
    if scaffold_copy.exists():
        scaffold_copy.unlink()
    assert _stale_lifecycle_offenders(str(scratch)) == [], (
        "the lifecycle check must pass over a post-freeze tree; the scaffold's "
        "deletion is registered, not a defect")

    # and it must still have power over what remains
    with open(scratch / "harness" / "PINS.json", "a", encoding="utf-8") as handle:
        handle.write("\nnot yet assembled\n")
    assert _stale_lifecycle_offenders(str(scratch)) != [], (
        "with the scaffold gone the check stopped reading the other files")

    # a file that is NOT registered as deleted may not simply vanish
    shutil.copyfile(os.path.join(_study(), "harness", "PINS.json"),
                    scratch / "harness" / "PINS.json")
    (scratch / "harness" / "e4lib" / "census.py").unlink()
    assert any("census.py" in offender
               for offender in _stale_lifecycle_offenders(str(scratch))), (
        "an unregistered disappearance must fail rather than skip")


def test_the_gold_row_count_in_the_pins_note_is_the_committed_suites():
    """The stale-count class, closed at the two places R4-6 names. `goldSuite.rows` is
    null until the freeze, so the NOTE beside it is what a pre-freeze reader gets, and
    it said 109 after the suite reached 117."""
    pins = _load("harness/PINS.json")
    rows = len(_load("design/gold/gold.json")["rows"])
    note = pins["goldSuite"]["note"]
    assert "%d at this revision" % rows in note, (
        "harness/PINS.json's goldSuite note must state the committed suite's row "
        "count (%d): %r" % (rows, note))
    with open(os.path.join(_study(), "harness", "e4lib", "census.py"),
              "rb") as handle:
        census_source = handle.read().decode("utf-8")
    assert "at the current revision" not in census_source, (
        "census.py quotes §5's registered stimulus; the quotation must elide the row "
        "count rather than restate it, or it goes stale with the suite")


def test_a_near_miss_verdict_line_does_not_authorize(tmp_path):
    """ROUND-9 FINDING R9-1: RFC 0009 requires the final line to be EXACTLY
    the verdict. A case-folded or indented rendition is a near-miss, not an
    authorization — the freeze token is a registered freeze condition and its
    reading is byte-exact."""
    reviews = tmp_path / "reviews"
    (reviews / "round-1").mkdir(parents=True)
    (reviews / "round-1" / "PROMPT.md").write_text("p\n")
    exact = render_round_status.VERDICT_LINES[render_round_status.FREEZABLE]
    for near_miss in (exact.upper(), exact.title(), "  " + exact,
                      exact.replace(" ", "  ")):
        (reviews / "round-1" / "REVIEW.md").write_text(
            "R1-1 finding\n%s\n" % near_miss)
        token, line = _review_verdict(1, str(reviews))
        assert token is None, (near_miss, token)
        assert line.strip() == near_miss.strip()
    (reviews / "round-1" / "REVIEW.md").write_text("R1-1 finding\n%s\n" % exact)
    token, _line = _review_verdict(1, str(reviews))
    assert token == render_round_status.FREEZABLE
