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


# --- ROUND-3 FINDING R3-10: the reader-facing status headers ---------------

_ROUND = re.compile(r"^## Round (\d+) — ", re.MULTILINE)
_ORDINALS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
_REVISIONS = ("first", "second", "third", "fourth", "fifth", "sixth",
              "seventh", "eighth", "ninth", "tenth")


def _review_record():
    with open(os.path.join(_study(), "PREREG-REVIEW.md"), "rb") as handle:
        return handle.read().decode("utf-8")


_VERDICT = re.compile(r"^- Verdict: \*\*(.+?)\*\*", re.MULTILINE)


_SEVERITY_COUNTS = re.compile(r"(\d+)\s+(BLOCKER|MAJOR|MINOR)")
_ID_RANGE = re.compile(r"\(R(\d+)-(\d+)\s*(?:…|\.\.\.)\s*R(\d+)-(\d+)\)")


def _round_records():
    """`{round number: {...}}`, read from the review record itself.

    A round is DISPOSITIONED when its section carries a disposition table row
    for its own findings (`| R3-1 |`); the record spells the other state out as
    "no R3 finding has been dispositioned yet". ROUND-4 FINDING R4-3 adds the
    VERDICT, because round 4's is the first that is not DO NOT FREEZE and both
    front doors said "all three returned DO NOT FREEZE" while a fourth round
    with a different verdict sat on the record beneath them.

    ROUND-5 FINDING R5-3 adds the FINDINGS, in both directions. `dispositioned`
    used to be true on finding any one `R<n>-<m>` row, while the regime's
    requirement (this record's own opening paragraph) is a written disposition
    PER FINDING — so a two-finding round with one row read as closed. The
    registered id set comes from the round's own verdict line, whose severity
    counts and id range are two independent statements of the same number, and
    is cross-checked against the round's verbatim review in `reviews/round-N/`
    where that file names its findings."""
    text = _review_record()
    numbers = [int(match.group(1)) for match in _ROUND.finditer(text)]
    assert numbers == sorted(numbers) and numbers, numbers
    sections = _ROUND.split(text)[1:]
    state = {}
    for index in range(0, len(sections), 2):
        number = int(sections[index])
        body = sections[index + 1]
        verdicts = _VERDICT.findall(body)
        assert len(verdicts) == 1, (
            "round %d's section must record exactly one verdict line, found %s"
            % (number, verdicts))
        bullet = re.search(r"^- Verdict:.*?(?=\n- |\n\n|\n#)", body,
                           re.MULTILINE | re.DOTALL)
        assert bullet, "round %d has no verdict bullet" % number
        line = " ".join(bullet.group(0).split())
        severities = {name: int(count)
                      for count, name in _SEVERITY_COUNTS.findall(line)}
        span = _ID_RANGE.search(line)
        assert span, (
            "round %d's verdict line must name its finding-id range as "
            "`(R%d-1 … R%d-N)`: %r" % (number, number, number, line))
        first, last = int(span.group(2)), int(span.group(4))
        assert int(span.group(1)) == int(span.group(3)) == number and first == 1, line
        state[number] = {
            "verdict": verdicts[0].split(" —")[0].split(" --")[0].strip(),
            "severities": severities,
            "findings": ["R%d-%d" % (number, n) for n in range(first, last + 1)],
            "dispositionedIds": sorted(
                set(re.findall(r"\|\s*(R%d-\d+)\s*\|" % number, body)),
                key=lambda name: int(name.split("-")[1])),
        }
        state[number]["dispositioned"] = bool(state[number]["dispositionedIds"])
    return state


def _review_finding_ids(number):
    """The finding ids the round's verbatim review actually carries, or None
    when the review states them in a form this cannot read. Rounds 1, 3 and 4
    head their findings with bold runs rather than markdown headings, so the ids
    are collected from the whole file and filtered to the round's own."""
    path = os.path.join(_study(), "reviews", "round-%d" % number, "REVIEW.md")
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as handle:
        text = handle.read().decode("utf-8")
    found = {name for name in re.findall(r"\bR%d-(\d+)\b" % number, text)}
    return sorted(("R%d-%d" % (number, int(name)) for name in found),
                  key=lambda name: int(name.split("-")[1]))


def _rounds():
    """`{round number: dispositioned?}` — the shape the R3-10 tests read."""
    return {number: record["dispositioned"]
            for number, record in _round_records().items()}


def test_the_readme_status_header_names_the_latest_round_and_its_state():
    """ROUND-3 FINDING R3-10, and this is the test the README did not have.

    The README said "Round 1's twenty findings are dispositioned and round 2's
    fourteen are open" after every one of round 2's fourteen had been
    dispositioned in the record beside it, and counted "Two cross-vendor review
    rounds" while three had run. The existing README test searches for the words
    "review rounds" and "DO NOT FREEZE" and passes on both errors, because a
    marker word cannot carry a number.

    This reads the state out of `PREREG-REVIEW.md` — the record is the
    authority — and requires the banner to agree with it: the round COUNT, and
    no claim that a dispositioned round is still open."""
    rounds = _rounds()
    latest = max(rounds)
    with open(os.path.join(_study(), "README.md"), "rb") as handle:
        readme = flatten(handle.read().decode("utf-8"))
    assert "%s cross-vendor review rounds" % _ORDINALS[latest] in readme.lower(), (
        "the record carries %d review rounds and the README's status banner "
        "must say so: expected the words \"%s cross-vendor review rounds\""
        % (latest, _ORDINALS[latest]))
    for number, dispositioned in sorted(rounds.items()):
        if not dispositioned:
            continue
        stale = re.search(r"round %d's [a-z]+ (?:findings )?are open" % number,
                          readme.lower())
        assert stale is None, (
            "round %d's findings are dispositioned in PREREG-REVIEW.md and the "
            "README still calls them open: %r" % (number, stale.group(0)))


def test_the_registration_header_names_the_round_it_responds_to():
    """The same contradiction in the other header: the preregistration still
    described itself as "(post-round-1)" with three rounds on the record. The
    revision a reader is holding is only meaningful against the round it
    answers."""
    rounds = _rounds()
    latest = max(rounds)
    with open(os.path.join(_study(), "PREREGISTRATION.md"), "rb") as handle:
        header = flatten(handle.read().decode("utf-8").split("\n## ")[0])
    found = re.findall(r"post-round-(\d+)", header)
    assert found, (
        "the registration's status header must name the round this revision "
        "responds to, as `post-round-N`")
    assert [int(number) for number in found] == [latest] * len(found), (
        "the latest round on the record is %d and the registration header says "
        "post-round-%s" % (latest, "/".join(found)))


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


# --- ROUND-4 FINDING R4-3: the headers state the round STATE, both of them ---

def _status_headers():
    """Both front doors' status headers, flattened and lowercased."""
    out = {}
    for relative in ("README.md", "PREREGISTRATION.md"):
        with open(os.path.join(_study(), relative), "rb") as handle:
            text = handle.read().decode("utf-8")
        out[relative] = flatten(text.split("\n## ")[0]).lower()
    return out


def test_both_headers_state_every_verdict_on_the_record():
    """R4-3. The R3-10 tests asserted the round COUNT and the ABSENCE of a stale
    "round N's findings are open"; they did not assert that the headers describe
    the verdicts, so "all three returned DO NOT FREEZE" survived a fourth round
    that returned something else. Every DISTINCT verdict on the record must
    appear in both headers, so a new kind of verdict cannot land unmentioned."""
    records = _round_records()
    verdicts = {record["verdict"].lower() for record in records.values()}
    latest = max(records)
    for relative, header in _status_headers().items():
        for verdict in sorted(verdicts):
            assert verdict in header, (
                "%s's status header does not state the verdict %r, which is on "
                "the record" % (relative, verdict))
        assert "round %d" % latest in header, (
            "%s's status header must name the latest round (%d)"
            % (relative, latest))
        if len(verdicts) > 1:
            assert "all %s returned" % _ORDINALS[latest] not in header, (
                "%s's header says every round returned one verdict and the "
                "record carries %s" % (relative, sorted(verdicts)))


def test_both_headers_state_the_open_or_closed_state_of_every_round():
    """R4-3, the half R3-10's tests only did negatively and only for the README.
    A dispositioned round may not be called open in EITHER header, and an
    undispositioned one must be called open in BOTH — the state a reader needs
    is which findings are still live, and silence read as "closed" is exactly
    the failure R3-10 was raised for."""
    records = _round_records()
    for relative, header in _status_headers().items():
        for number, record in sorted(records.items()):
            stale = re.search(r"round %d's [a-z]+ (?:findings )?are open" % number,
                              header)
            if record["dispositioned"]:
                assert stale is None, (
                    "%s: round %d is dispositioned in PREREG-REVIEW.md and the "
                    "header still calls it open: %r"
                    % (relative, number, stale.group(0)))
            else:
                assert stale is not None, (
                    "%s: round %d carries no disposition table and the header "
                    "must say its findings are open" % (relative, number))


# --- ROUND-5 FINDING R5-3: per ROUND and per FINDING, not per round ---------

def test_every_rounds_finding_count_is_stated_three_ways_and_they_agree():
    """R5-3's first half. The record's verdict line states each round's findings
    twice over — as severity counts and as an id range — and the round's verbatim
    review states them a third time by naming them. All three must agree, or the
    count every other test derives is a number somebody typed."""
    for number, record in sorted(_round_records().items()):
        total = sum(record["severities"].values())
        assert record["severities"], (
            "round %d's verdict line must state its severity counts" % number)
        assert total == len(record["findings"]), (
            "round %d's verdict line says %d findings by severity (%s) and "
            "%d by id range" % (number, total, record["severities"],
                                len(record["findings"])))
        from_review = _review_finding_ids(number)
        if from_review is None:
            continue
        assert from_review == record["findings"], (
            "round %d's verbatim review names %s and the record registers %s"
            % (number, from_review, record["findings"]))


def test_a_round_is_closed_only_when_every_one_of_its_findings_is_dispositioned():
    """R5-3's second half, and the property the regime states in this record's
    own opening paragraph: a written maintainer disposition PER FINDING. The R4-3
    reading marked a round closed on finding any one `R<n>-<m>` row, so a
    two-finding round with only `R5-1` dispositioned passed as closed and its
    second finding vanished between the tables."""
    for number, record in sorted(_round_records().items()):
        dispositioned = record["dispositionedIds"]
        if not dispositioned:
            continue
        assert dispositioned == record["findings"], (
            "round %d dispositions %s and its findings are %s — a partly "
            "dispositioned round is an OPEN round, and the headers read this"
            % (number, dispositioned, record["findings"]))


_HEADER_ATTRIBUTION = r"\brounds?\s+([0-9][0-9\s,–—\-]*(?:and\s+[0-9]+\s*)?)returned\s+"


def _header_verdict_map(header, verdicts):
    """`{round number: verdict}` as a HEADER states it, parsed from affirmative
    "round(s) N … returned <verdict>" clauses. A verdict that merely occurs in
    the header attributes itself to nothing, which is how a synthetic round 5
    repeating an earlier verdict passed R4-3's test while the header never said
    round 5 returned anything."""
    mapping = {}
    for verdict in verdicts:
        for match in re.finditer(_HEADER_ATTRIBUTION + re.escape(verdict), header):
            for number in _expand_round_list(match.group(1)):
                assert number not in mapping or mapping[number] == verdict, (
                    "the header attributes two verdicts to round %d" % number)
                mapping[number] = verdict
    return mapping


def _expand_round_list(text):
    """"1-3", "1–3 and 5", "4" → the round numbers they name."""
    numbers = set()
    for part in re.split(r",|\band\b", text):
        part = part.strip()
        if not part:
            continue
        span = re.match(r"^(\d+)\s*[–—\-]\s*(\d+)$", part)
        if span:
            numbers.update(range(int(span.group(1)), int(span.group(2)) + 1))
        elif part.isdigit():
            numbers.add(int(part))
    return numbers


def test_both_headers_attribute_every_round_to_the_verdict_it_returned():
    """R5-3's third half. R4-3 required every DISTINCT verdict to appear in both
    headers, which a header satisfies without saying which round returned which —
    a synthetic round 5 repeating round 1's verdict passed it while the header
    attributed nothing to round 5. This parses the header's own attribution
    clauses and requires the mapping to be the record's, round by round."""
    records = _round_records()
    expected = {number: record["verdict"].lower()
                for number, record in records.items()}
    verdicts = sorted(set(expected.values()))
    for relative, header in _status_headers().items():
        mapping = _header_verdict_map(header, verdicts)
        assert mapping == expected, (
            "%s's status header attributes %s and the record says %s — every "
            "round must be named with the verdict it returned, in the form "
            "\"round(s) N returned <verdict>\"" % (relative, mapping, expected))


def test_the_policy_drafts_lifecycle_paragraph_is_the_records_lifecycle():
    """ROUND-5 FINDING R5-7, under the same machinery as the two front doors.

    `POLICY-DRAFT.md` is a frozen reader's document — the freeze procedure copies
    it wholesale to `policy/POLICY.md` — and its status paragraph said two review
    rounds had run and both had returned DO NOT FREEZE, through rounds 3, 4 and 5.
    Round 4 explicitly ordered it reconciled and it was not. The class has
    recurred, so the sentence stops being a sentence somebody remembers: the round
    COUNT is derived from `reviews/`, and the per-round verdicts are parsed by the
    header parser and compared to the record."""
    records = _round_records()
    expected = {number: record["verdict"].lower()
                for number, record in records.items()}
    on_disk = sorted(int(name.split("-")[1])
                     for name in os.listdir(os.path.join(_study(), "reviews"))
                     if re.fullmatch(r"round-\d+", name))
    with open(os.path.join(_study(), "design", "POLICY-DRAFT.md"), "rb") as handle:
        status = flatten(handle.read().decode("utf-8").split("\n---", 1)[0]).lower()

    count = len(on_disk)
    assert ("%s rfc 0009 review rounds" % _ORDINALS[count] in status
            or "%d rfc 0009 review rounds" % count in status), (
        "reviews/ carries %d rounds and the policy draft's status paragraph must "
        "say so" % count)
    mapping = _header_verdict_map(status, sorted(set(expected.values())))
    assert mapping == expected, (
        "POLICY-DRAFT.md attributes %s and the record says %s" % (mapping, expected))
    assert "still open for gold authoring" not in status


def test_the_review_directory_and_the_record_carry_the_same_rounds():
    """The round count derived from the tree rather than from a sentence. A round
    whose verbatim record landed under `reviews/` without a section here — or the
    reverse — is the drift R3-10, R4-3 and R5-3 have each caught one spelling
    of."""
    on_disk = sorted(int(name.split("-")[1])
                     for name in os.listdir(os.path.join(_study(), "reviews"))
                     if re.fullmatch(r"round-\d+", name))
    assert on_disk == sorted(_round_records()), (
        "reviews/ carries rounds %s and PREREG-REVIEW.md carries %s"
        % (on_disk, sorted(_round_records())))


def test_the_review_records_own_round_sections_do_not_contradict_their_tables():
    """R4-3 on the record itself. The round-4 section said "no R4 finding has
    been dispositioned yet" as a heading line; if a disposition table is then
    appended beneath it, the two disagree and `_round_records()` — which every
    header test reads — believes the table. The pending sentence must go when
    the table lands."""
    text = _review_record()
    sections = _ROUND.split(text)[1:]
    offenders = []
    for index in range(0, len(sections), 2):
        number = int(sections[index])
        body = sections[index + 1]
        dispositioned = bool(re.search(r"\|\s*R%d-\d+\s*\|" % number, body))
        pending = re.search(
            r"no R%d finding has been dispositioned yet" % number, body)
        if dispositioned and pending:
            offenders.append("round %d carries a disposition table and still "
                             "says nothing has been dispositioned" % number)
        if not dispositioned and not pending:
            offenders.append("round %d has neither a disposition table nor the "
                             "pending sentence; its state is unreadable" % number)
    assert offenders == [], "\n  ".join([""] + offenders)


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


# A stated difference count, in either spelling a document uses. Non-overlapping
# by construction, so "0 differences from the primary transcription" yields one
# reading of one number and not a second from the words after it.
_STATED_DIFFERENCES = re.compile(
    r"\b(?:(\d[\d,]*)|(zero|no))\s+(?:[a-z-]+\s+){0,4}?differences?\b",
    re.IGNORECASE)


def _stated_difference_counts(text):
    counts = []
    for match in _STATED_DIFFERENCES.finditer(text):
        digits, word = match.group(1), match.group(2)
        counts.append((0 if digits is None else int(digits.replace(",", "")),
                       match.group(0)))
    return counts


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
    them, and no surface may state a count the measurement denies."""
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
        # POSITIVE: at least one block must carry the WHOLE description — all
        # three metrics, each with its own anchor, so a surface cannot publish
        # the live count and quietly drop the zeros.
        complete = []
        for block in blocks:
            lowered = block.lower()
            counts = [count for count, _ in _stated_difference_counts(block)]
            if live not in block or checked not in block:
                continue
            if "scored surface" not in lowered:
                continue
            if not re.search(r"\b(second|both)\b[^.]{0,90}transcriptions?",
                             lowered) and "adequacy_crosscheck" not in lowered:
                continue
            if "pinned" not in lowered:
                continue
            if counts.count(measured["scoredDifferences"]) < 1:
                continue
            complete.append(block)
        assert complete, (
            "%s must state m-a-183's three measured metrics together — %s "
            "trace-live cells, the scored surface identical on both "
            "transcriptions, and %s differences over the %s pinned-engine "
            "samples — in one block; no block does"
            % (surface, live, measured["engineDifferences"], checked))


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


_NUMBER_WORDS = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four",
                 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
                 10: "ten", 11: "eleven", 12: "twelve"}

# The two ROLES the split assigns, as the documents phrase them. A number in a
# role is the claim; the number alone is not.
_MARGINAL_ROLE = (r"the repair's (?:marginal )?price"
                  r"|marginally because of the repair"
                  r"|exist only because of the repair"
                  r"|are the repair's marginal"
                  r"|marginal to the repair")
_PRE_EXISTING_ROLE = (r"already unkillable"
                      r"|already dropped"
                      r"|corpus had already"
                      r"|were already"
                      r"|already before it")


_NUMBER_TOKEN = r"(?<![\w-])(\d+|%s)\b" % "|".join(_NUMBER_WORDS.values())


def _claim_sentences(text, gross):
    """The sentences that make a claim about THIS class: the ones that state its
    size. Scoping matters — "whose round-1 counterparts were already drops" is a
    sentence about a different class entirely, and a document-wide role search
    reads its `1` as an attribution."""
    return [sentence for sentence in re.split(r"(?<=\.)\s+", text)
            if re.search(r"(?<![\w-])(%s|%d)\b" % (_NUMBER_WORDS[gross], gross),
                         sentence)]


def _role_numbers(sentences, role, gross):
    """Every number stated IN a role, with the phrase that carries it.

    The gap may not cross a sentence boundary, carry a negation, or contain
    another number: "three ... and are not the repair's price" is a denial and
    "six of the nine are the repair's marginal price" is one claim about six,
    not two claims — so the partitive is stripped first, per sentence, after the
    sentence has been selected by it."""
    partitive = re.compile(r"\bof (?:the )?(?:%s|%d)\b"
                           % (_NUMBER_WORDS[gross], gross))
    pattern = re.compile(r"%s([^.;:]{0,40}?)(%s)" % (_NUMBER_TOKEN, role))
    out = []
    for sentence in sentences:
        stripped = partitive.sub(" ", sentence)
        for match in pattern.finditer(stripped):
            gap = match.group(2)
            if " not " in gap or gap.strip().startswith("not "):
                continue
            if re.search(_NUMBER_TOKEN, gap):
                continue
            token = match.group(1)
            value = (int(token) if token.isdigit()
                     else [k for k, v in _NUMBER_WORDS.items() if v == token][0])
            out.append((value, " ".join(match.group(0).split())))
    return out


def test_the_documents_state_the_marginal_price_and_not_only_the_class_size(
        adequacy_text, flat):
    """R4-2 on the reader-facing surfaces, rebuilt for ROUND-5 FINDING R5-2.

    The class size and the repair's price are different quantities, and every
    registered surface must publish both, in their roles. The R4-2 guard searched
    each document for the two NUMBERS and skipped any document that did not quote
    the class at all — so "nine marginal, none pre-existing" plus an unrelated six
    somewhere in the file passed it, which is the false attribution the finding
    exists to forbid.

    So: no surface is skipped, and each number is required in its ROLE — the
    marginal count attributed to the repair, the pre-existing count withheld from
    it — with every role statement in the document checked, not just one."""
    price = _load("design/mutants/adequacy_region_lemma_price.json")
    gross = price["grossClassSize"]
    marginal = price["marginalToRepairCount"]
    pre_existing = price["preExistingDropCount"]
    assert gross == marginal + pre_existing and pre_existing, price

    with open(os.path.join(_study(), "design", "POLICY-DRAFT.md"), "rb") as handle:
        policy = flatten(handle.read().decode("utf-8"))
    surfaces = (("ADEQUACY.md", " ".join(adequacy_text.split())),
                ("PREREGISTRATION.md", flat),
                ("POLICY-DRAFT.md", policy))
    for name, text in surfaces:
        lowered = text.lower()
        assert price["class"] in lowered, (
            "%s must name the %s class it is attributing" % (name, price["class"]))
        sentences = _claim_sentences(lowered, gross)
        assert sentences, (
            "%s must state the class size (%d) where it attributes the class"
            % (name, gross))

        stated_marginal = _role_numbers(sentences, _MARGINAL_ROLE, gross)
        assert stated_marginal, (
            "%s attributes the %s class to the repair and never says how much of "
            "it the repair actually bought (%d)" % (name, price["class"], marginal))
        for value, phrase in stated_marginal:
            assert value == marginal, (
                "%s says %r; the repair's marginal price is %d, not %d"
                % (name, phrase, marginal, value))

        stated_pre = _role_numbers(sentences, _PRE_EXISTING_ROLE, gross)
        assert stated_pre, (
            "%s must state that %d of the %d were already unkillable before the "
            "repair; without it the class reads as the repair's whole price"
            % (name, pre_existing, gross))
        for value, phrase in stated_pre:
            assert value == pre_existing, (
                "%s says %r; %d members predate the repair, not %d"
                % (name, phrase, pre_existing, value))


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
    return jobs


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


def test_the_ci_interpreter_rationale_matches_what_the_registry_actually_pins():
    """R5-5's third residual. The job's comment said `PINS.json` records 3.12.11 and
    that the scorer refuses any other patch; the registry pins the SERIES 3.12 by
    design (Study 012 round-3 finding 20 — the running patch level is reported, not
    required) and `integrity.verify_interpreter()` compares major and minor only. The
    exact patch in CI is a REPRODUCIBILITY choice for the runner, and the file must say
    that rather than claim an enforcement that does not exist."""
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
    for false_claim in ("harness/PINS.json records 3.12.11",
                        "PINS.json records the patch level",
                        "refuses to adjudicate under anything else"):
        assert false_claim not in raw, (
            "the workflow claims %r and the registry pins only the %s series"
            % (false_claim, entry["series"]))
    assert entry["series"] in raw, (
        "the job must name the series the registry actually pins (%s)"
        % entry["series"])


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
    (scratch / "harness" / "SCAFFOLD.md").unlink()
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
