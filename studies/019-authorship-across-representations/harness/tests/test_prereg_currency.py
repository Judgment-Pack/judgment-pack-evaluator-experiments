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
    assert "STILL OPEN" not in oc_text, (
        "the OC table still reports a settled question as open")
    assert "CLOSED, denominator-in" in oc_text
    assert "(two closed, one open)" not in oc_text
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
_REVISIONS = ("first", "second", "third", "fourth", "fifth", "sixth")


def _review_record():
    with open(os.path.join(_study(), "PREREG-REVIEW.md"), "rb") as handle:
        return handle.read().decode("utf-8")


def _rounds():
    """`{round number: dispositioned?}` read from the review record itself.

    A round is DISPOSITIONED when its section carries a disposition table row
    for its own findings (`| R3-1 |`); the record spells the other state out as
    "no R3 finding has been dispositioned yet"."""
    text = _review_record()
    numbers = [int(match.group(1)) for match in _ROUND.finditer(text)]
    assert numbers == sorted(numbers) and numbers, numbers
    sections = _ROUND.split(text)[1:]
    state = {}
    for index in range(0, len(sections), 2):
        number = int(sections[index])
        body = sections[index + 1]
        state[number] = bool(re.search(r"\|\s*R%d-\d+\s*\|" % number, body))
    return state


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
