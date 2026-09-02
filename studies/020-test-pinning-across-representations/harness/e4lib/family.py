"""The registered sensitivity family — PREREGISTRATION.md section 5, delta 5.

NEW IN STUDY 020. This module is not a port: section 7's delta 5 registers it as
day-one work ("The family scorer. New: the eighteen members, L2c's offset
estimator, the two permutation schemes with their pinned B and seed, the IU
verdict, the drop-a-pole table, the BCa intervals, and the **refusal** rather
than fallback on the ITT x ANCOVA cell"). Study 019 had one endpoint and one
cut; nothing in its harness computes any of this, so there is no two-sided
`PORTS.md` row to write and none is written.

WHAT THIS FILE DOES
-------------------
1. `build_corpus()` turns `e4.build_pairing()`'s table plus the two
   engine-supplied-kill lists into the two COLUMNS section 5.2 registers — the
   engine-included corpus (33 shared classes, 69 JPS / 62 Rego paired members)
   and the engine-excluded corpus (29 shared classes, 57 / 55) — and derives
   every denominator from the manifests rather than transcribing a number.
2. `Unit` carries one admitted run as the family reads it: its arm, its
   language, its EXPLICIT per-mutant survivor set, its `killedPaired` in each
   column, its `caseCount`, and whether it carries a kill record at all.
   `unit_from_kill_record()` is where section 7 delta 1's token collision is
   refused: coverage is derived from the survivor vector AND cross-checked
   against `killedPaired`, so `survivorsPaired: []` with `killedPaired: 0`
   raises `EmptySurvivorAmbiguity` instead of scoring a perfect 33/33.
3. `MEMBERS` is section 5.2's crossing, {L1, L3, L2c} x {included, excluded} x
   {ITT-unadjusted, PP-unadjusted, PP-adjusted}, in the M1..M18 order of section
   5.5's Reprint 1. `member_outcomes()` produces one (arm, outcome, caseCount)
   row per unit of the member's population.
4. `offset()` is L2c's registered de-biasing estimator: off^ = sum_g pi^_g
   (w^A_g - w^C_g), pi^ the pooled ARM-LABEL-FREE coverage marginal over the
   SCOREABLE runs of that member's own analysis population.
5. `permutation_test()` is section 5.3's two schemes — label permutation at
   B = 20,000 for the unadjusted members, whole-record permutation at B = 4,000
   for the adjusted ones, one seed, Monte-Carlo p in the (count+1)/(B+1) form.
6. `family_report()` computes every member, the drop-a-pole table and the IU
   verdict, and returns the SAME key set whatever the verdict is (section 4.2.4
   of the brief: "the published quantity set is identical in every branch").
7. `bca_interval()` is section 5.3's Tier D interval. It REFUSES unless the
   caller hands it a pinned resample count and seed, because section 5 registers
   neither (see THE FINDINGS below).

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
- **It does not decide anything.** Section 5.9's decision rule is ordered and
  exhaustive and "no inferential quantity is computed, let alone published, at
  or above row 3". This module is a pure function of the units it is handed; the
  caller (`harness/score.py` through `e4lib/decision.py`) is what must not call
  it above row 3. Nothing here reads a control gate, and calling `verdict()`
  cannot be mistaken for adjudicating R1: it returns section 5.9 row 4's
  antecedent, not a row.
- **It does not fall back.** The ITT x ANCOVA cell is refused by name
  (`IttAncovaRefused`); it never silently drops the covariate-less runs, which
  is exactly the "hidden collapse of the family" section 5.2 names. An empty
  per-arm denominator is refused (`EmptyArmDenominator`); section 5.1 registers
  that "a contrast over an empty arm is not INDETERMINATE, it is not computed at
  all".
- **It does not remove a member.** Section 5.2's membership is append-only after
  registration. `verdict()` refuses a result set missing any registered id, and
  `extend_family()` refuses anything but an addition.
- **It does not invent a pin.** The permutation B values and the seed are
  section 5.3's and section 5.5's own registered numbers and are transcribed
  here with their citation. The BCa resample count and seed are NOT registered
  anywhere in section 5, so this module has none and refuses rather than
  choosing one.
- **It does not read a file, a clock, an environment variable or a study path.**
  It is handed a pairing table and a list of units. `harness/PINS.json`,
  `RESULTS.json` and the 019 tree are the caller's business; the suite's
  fixture adapter lives in `harness/tests/test_family.py`.
- It does not compute section 5.6's operating characteristics. `oc18.py` is a
  separate registered script and is not this file.

DETERMINISM
-----------
Every sum is taken over a fixed ordering (class index order, then unit order as
given), so a float total is bit-reproducible. `random.Random` is seeded per
test and never shared between two tests, so a member's p-value does not depend
on which members were computed before it. No `set` iteration order reaches a
number: every set is turned into a sorted tuple first.

THE FINDINGS — read these before trusting a figure this module prints
---------------------------------------------------------------------
This module reproduces section 5.5's Reprint 1 exactly on Study 019's frozen
batch: all 18 A-C point estimates, all 18 A-B point estimates, all 24 unadjusted
p-values, all 18 sigmas, all 18 MDEs at 019's n, both offset columns, the
naive/corrected pair, the ITT x ANCOVA Tier D quantities and all nine rows of
Reprint 2. `harness/tests/test_family.py` is that reproduction. Three things do
NOT reproduce and are recorded here rather than in a commit message:

F-1. **Section 5.2's Fact-2 table misstates the engine-excluded Rego weight.**
     The row reads `|J^ex_g|/57 vs |R_g|/62` and publishes offset -0.0492 /
     -0.0481 in the same row. Those two cells are not consistent: -0.0492 is
     only obtainable with `|R^ex_g|/55` (the shared-class denominator), while
     the OUTCOME behind Reprint 3's `+0.0783` / `+0.1867` and behind M16/M17/M18
     is only obtainable with `/62` (the language-native denominator, which for
     Rego is unchanged by an exclusion that removes nothing). This module
     therefore keeps the two denominators as two NAMED quantities —
     `native_denominator()` for the outcome, `shared_denominator()` for the
     offset — and reproduces the registered table.
     Worse than a disagreement: the Fact-2 row taken literally is ILL-POSED.
     The exclusion empties arm A's side of four classes, so arm A has no
     measurable coverage on them, and the marginal can pool arm A's VACUOUS
     coverage of those four or restrict itself to the 29 classes both languages
     can still be scored on. On 019 the excluded-column offset is then

         registered (shared denominators)   -0.04922 (PP)  -0.04813 (ITT)
         native, vacuous coverage pooled    -0.00567 (PP)  -0.00554 (ITT)
         native, marginal over the 29       +0.03795 (PP)  +0.03711 (ITT)

     (The pooled-vacuous ITT cell first measured -0.00805 under the old
     adapter's all-survivor synthesis for the two never-evaluated runs —
     pooled-vacuous is the one reading that pays vacuous coverage, so it
     alone moved when R1-3 recoded them; no cell here ever reproduced a
     published 019 figure.)

     — three values for one registered symbol, two of them of the wrong sign to
     reproduce M16/M17/M18. `offset(..., weighting="native")` computes the
     second and `harness/tests/test_family.py` computes the third through the
     public API, so all three are measurements rather than sentences. A
     maintainer must rule before the freeze: the choice moves M17 between
     +0.1275 and roughly +0.0403, a factor of three on the family's largest
     member.
     RULED 2026-08-24 (round-1 finding R1-4, the maintainer decision this
     note demanded): the registered estimand is the HYBRID this module
     implements — the OUTCOME over language-native denominators (Rego /62 in
     the excluded column) and L2c's OFFSET over the shared-class denominators
     (57/55) — because the outcome measures what an arm's own language can
     reach while the offset de-biases over the support both arms share, and
     because it is the only reading that reproduces every published reprint
     figure. The two single-universe alternatives stay published beside it in
     `family_report()`'s offsets block. The ruling's registered text is in
     PREREGISTRATION.md §5.2, beside the M-16(d) ceilings; round 2 verifies.
F-2. **The six adjusted members' p-values are not byte-reproducible.** The
     twelve unadjusted members reproduce to the last published digit under
     `random.Random(11)` with repeated `shuffle()` of one persistent payload
     list and the two-sided `|d*| >= |d_obs|` count, which fixes the scheme
     beyond reasonable doubt. The same stream at B = 4,000 gives M3/M6 0.2462
     against the registered 0.2309, M9 0.8883 against 0.8823, M12 0.7891 against
     0.7881, M15 0.8395 against 0.8263 (M18's 0.0002 is exact). The generating
     script is not in the tree, so the residual is a different Monte-Carlo
     stream, not a different estimator: the point estimates, the sigmas and
     EVERY reject/not-reject decision at alpha = 0.05 agree, so Reprint 1's
     "10 of 18 reject", its 16/2 sign split and all nine Reprint 2 rows are
     reproduced exactly. Section 5.3's "seed pinned in `PINS.json`" is not yet
     satisfiable either: `harness/PINS.json` carries no family member at all.
F-3. **Section 5.2's "unscoreable runs ... take no offset" needs one more
     word.** Reprint 1's M13 and M16 are reproducible only if the offset's
     population is the runs carrying a KILL RECORD (90 on 019's ITT, 88 on its
     per-protocol set) and the offset is subtracted from the 36 arm-A runs that
     carry one — not from the 34 that also pass the identity control. The two
     empty-survivor runs are therefore SCOREABLE-WITH-ZERO, not unscoreable:
     `killedPaired: 0` is a measurement, and 019's published figures select the
     offset marginal on "carries a kill record". RESOLVED BY SPLIT, 2026-08-24
     (round-1 finding R1-3): 019's scorer gated mutant execution on identity,
     so those two runs EVALUATED NOTHING, and one flag cannot carry both "the
     record exists" (019's marginal, size 90, reproduces every published
     offset) and "something ran" (size 88, the corrected marginal). `Unit`
     now carries `carries_kill_record` and `evaluated` separately, `offset()`
     takes the predicate as an argument, `family_report()` publishes both ITT
     readings side by side, and the preregistration's §5.2 carries the marked
     correction of 019's four affected member figures (M13/M16, both
     contrasts; no decision moves at alpha = 0.05).
"""
from __future__ import annotations

import math
import random

# ---------------------------------------------------------------------------
# Section 5.3 and section 5.5's registered constants. Transcribed with their
# citation; nothing here is chosen by this file.
# ---------------------------------------------------------------------------

#: Section 5.3, unadjusted members: "**20,000 permutations**, seed pinned in
#: `PINS.json`, Monte-Carlo p in the (count+1)/(B+1) form."
PERMUTATIONS_UNADJUSTED = 20000
#: Section 5.3, adjusted members: "**4,000 permutations**, same seed rule."
PERMUTATIONS_ADJUSTED = 4000
#: Section 5.5's reprint header: "Unadjusted members: label permutation,
#: B = 20,000, seed 11. Adjusted members: whole-record permutation, B = 4,000,
#: seed 11." `PINS.json` carries no family member yet (finding F-2); when delta 6
#: adds one, `family_report(seed=...)` takes it from there and this constant
#: becomes the fallback the registration already states.
PERMUTATION_SEED = 11
#: Section 5.4 item 4: "alpha = 0.05 per member, two-sided, no correction".
ALPHA = 0.05
#: Section 5.9 row 4's two outcomes, and section 4.2.4's ruling that there is
#: exactly one verdict vocabulary. UNSUPPORTED is not a value here on purpose.
CLAIM = "CLAIM"
INDETERMINATE = "INDETERMINATE-BY-DISAGREEMENT"

LEVELS = ("L1", "L3", "L2c")
COLUMNS = ("included", "excluded")
LANGUAGES = ("jps", "rego")
#: Which language each arm authors in. Arm A is the JPS arm; arms B and C are
#: the two Rego prompts. The engine-supplied-kill exclusion is one-sided because
#: of this map, which is why it is spelled out rather than inferred.
ARM_LANGUAGE = {"A": "jps", "B": "rego", "C": "rego"}


class FamilyError(Exception):
    """A refusal in the family scorer, with a named code as its first word."""


class EmptySurvivorAmbiguity(FamilyError):
    """Section 7 delta 1: "nothing evaluated" and "everything killed" collide.

    Raised when a kill record's survivor vector and its `killedPaired` cannot
    both be true. On Study 019's batch this fires on exactly `run-025` and
    `run-046` and on no other run, which is the whole of section 5.2's Fact-1
    box reproduced as a refusal."""


class MixedUniverseRefused(FamilyError):
    """ROUND-2 FINDING R2-2 (maintainer ruling: NATIVE-FOR-BOTH). A member
    seat whose outcome is weighted in one universe and whose offset in another
    is refused BEFORE any number exists: de-biasing an estimand with another
    universe's null offset leaves a residual computable from the frozen corpus
    alone (+0.043552 PP / +0.042584 ITT on 019), which is exactly what §5.2
    criterion (iii) forbids a member to carry. The two single-universe
    readings and the superseded hybrid are Tier D, computed by
    `alternative_outcomes()`, never by a member seat."""


class IttAncovaRefused(FamilyError):
    """Section 5.2: the scorer must REFUSE rather than fall back.

    The naive implementation drops the covariate-less runs and silently
    reproduces the artifact-bearing complete-case cell. That is a covert change
    of population, so this cell has no code path at all."""


class EmptyArmDenominator(FamilyError):
    """Section 5.1: "a contrast over an empty arm is not INDETERMINATE, it is
    not computed at all, and the outcome falls to the rows above"."""


class MembershipError(FamilyError):
    """Section 5.2: membership is append-only, and every member is published."""


class IntervalUnpinned(FamilyError):
    """Section 5.3 registers a BCa interval and pins neither B nor a seed."""


# ---------------------------------------------------------------------------
# The corpus — the two columns, derived from the manifests
# ---------------------------------------------------------------------------

class Corpus(object):
    """The shared-class structure of both engine columns.

    `classes` is the master list: section 4's shared (paired, non-degenerate)
    witness classes, in `build_pairing()`'s own order, each carrying its JPS and
    its Rego member ids in both columns. Every denominator below is SUMMED from
    that list or from the language's whole paired set; no count is transcribed.

    TWO DENOMINATORS, DELIBERATELY NOT ONE (finding F-1).
    `native_denominator(language, column)` is the language's own paired set
    after that language's engine-supplied mutants are removed — 69/62 included,
    57/**62** excluded, because the Rego engine-supplied class is registered
    EMPTY and an exclusion that removes nothing changes no denominator. It is
    what "the native-denominator paired kill fraction" means and it is what
    L2/L2c's outcome divides by.
    `shared_denominator(language, column)` sums the column's own class list —
    69/62 included, 57/**55** excluded, the four classes whose JPS side is
    entirely engine-supplied having left the shared set and taken their seven
    Rego members with them. It is what section 5.2's offset row was computed
    with. The two differ only in the excluded column and only on the Rego side."""

    def __init__(self, classes, engine_supplied):
        self.classes = tuple(classes)
        self.engine_supplied = {
            language: frozenset(engine_supplied.get(language, ()))
            for language in LANGUAGES}
        self._paired = {}
        for language in LANGUAGES:
            members = []
            for entry in self.classes:
                members.extend(entry[language])
            self._paired[language] = tuple(members)

    # -- membership -------------------------------------------------------
    def members(self, index, language, column):
        """The class's members of one language in one column, sorted."""
        entry = self.classes[index]
        if column == "included":
            return entry[language]
        excluded = self.engine_supplied[language]
        return tuple(m for m in entry[language] if m not in excluded)

    def paired_members(self, language, column="included"):
        """Every paired member of one language in one column, class order.

        The reconstruction a caller needs when a kill record says `killedPaired:
        0`: nothing was killed, so every paired mutant survived, and THAT is the
        survivor vector the collided token was standing in for."""
        members = []
        for index in range(len(self.classes)):
            members.extend(self.members(index, language, column))
        return tuple(members)

    def in_column(self, index, column):
        """Is this class SHARED in this column? Both sides must be non-empty.

        Section 5.2: excluding engine-supplied kills takes "the shared class set
        from **33 to 29**". A class whose JPS side is entirely engine-supplied
        is no longer a class both languages can be scored on, so it leaves — and
        its Rego members leave the shared denominator with it."""
        return all(self.members(index, language, column)
                   for language in LANGUAGES)

    def column_indices(self, column):
        return tuple(i for i in range(len(self.classes))
                     if self.in_column(i, column))

    # -- denominators -----------------------------------------------------
    def native_denominator(self, language, column):
        if column == "included":
            return len(self._paired[language])
        excluded = self.engine_supplied[language]
        return sum(1 for m in self._paired[language] if m not in excluded)

    def shared_denominator(self, language, column):
        return sum(len(self.members(i, language, column))
                   for i in self.column_indices(column))

    def symmetrised_denominator(self, column):
        """L3's denominator: the two languages' shared members added."""
        return sum(self.shared_denominator(language, column)
                   for language in LANGUAGES)

    # -- weights ----------------------------------------------------------
    def weights(self, level, column, weighting="native"):
        """`{index: (w_jps, w_rego)}` for the classes this level scores over.

        L1 and L3 are symmetric by construction and score over the column's
        shared classes only. L2 is the asymmetric one and scores over EVERY
        master class, because a class outside the column's shared set can still
        carry members of one language, and the native kill fraction counts
        them. `weighting` selects finding F-1's two readings; it is meaningful
        for L2c only, and the caller that publishes both is Tier D."""
        if level in ("L1", "L3"):
            indices = self.column_indices(column)
            if level == "L1":
                size = len(indices)
                return dict((i, (1.0 / size, 1.0 / size)) for i in indices)
            total = self.symmetrised_denominator(column)
            table = {}
            for i in indices:
                weight = (len(self.members(i, "jps", column))
                          + len(self.members(i, "rego", column))) / total
                table[i] = (weight, weight)
            return table
        if level != "L2c":
            raise FamilyError("FAMILY-UNKNOWN-LEVEL %r" % (level,))
        if weighting == "native":
            denominator = dict(
                (language, self.native_denominator(language, column))
                for language in LANGUAGES)
            indices = range(len(self.classes))
        elif weighting == "shared":
            denominator = dict(
                (language, self.shared_denominator(language, column))
                for language in LANGUAGES)
            indices = self.column_indices(column)
        else:
            raise FamilyError("FAMILY-UNKNOWN-WEIGHTING %r" % (weighting,))
        return dict(
            (i, (len(self.members(i, "jps", column)) / denominator["jps"],
                 len(self.members(i, "rego", column)) / denominator["rego"]))
            for i in indices)


def build_corpus(pairing_table, engine_supplied):
    """Section 4's pairing table plus the two engine-supplied lists -> `Corpus`.

    `pairing_table` is `e4.build_pairing()`'s first return value verbatim; only
    the rows it marks `countedInPairedSubset` are shared classes, which is
    section 4's registered pairing rule and not a reading of it. `engine_supplied`
    is `{'jps': [...], 'rego': [...]}` from `e4.engine_supplied_ids()`, whose own
    contract is that a language with no engine-supplied mutants supplies an
    EMPTY list rather than nothing at all."""
    for language in LANGUAGES:
        if language not in engine_supplied:
            raise FamilyError(
                "FAMILY-ENGINE-SUPPLIED-MISSING %s: a language that supplies no "
                "list at all is an absence, not an empty class" % language)
    classes = []
    for row in pairing_table:
        if not row.get("countedInPairedSubset"):
            continue
        classes.append({"witnessSet": tuple(row["witnessSet"]),
                        "jps": tuple(row["jpsMutants"]),
                        "rego": tuple(row["regoMutants"])})
    if not classes:
        raise FamilyError("FAMILY-NO-SHARED-CLASSES the pairing table shares "
                          "no class; there is no endpoint to compute")
    return Corpus(classes, engine_supplied)


# ---------------------------------------------------------------------------
# The unit — one admitted run as the family reads it
# ---------------------------------------------------------------------------

class Unit(object):
    """One section-1a admitted run.

    ROUND-1 FINDING R1-3, IMPLEMENTED AS TWO PREDICATES WHERE ONE FLAG USED TO
    CONFLATE THEM. `carries_kill_record` is finding F-3's predicate — the run
    carries a kill record, which is what Study 019's published offsets select
    the marginal on (90 of its 90 admitted runs) — and `evaluated` is the
    stricter fact that at least one mutant actually ran against the suite.
    They differ on exactly two frozen 019 runs (`A/run-025`, `A/run-046`:
    identity failed, so 019's scorer evaluated no mutant, yet the records
    carry a kill block), and `offset()` takes the predicate as an argument so
    both readings are computations rather than sentences. Neither predicate
    means the run passed `referenceIdentity`; that is `identity_pass`, and it
    is what the per-protocol population selects on. The old single flag
    (`scoreable`) is DELETED rather than aliased, so no call site can keep a
    third reading alive by accident."""

    __slots__ = ("run_id", "arm", "language", "carries_kill_record",
                 "evaluated", "identity_pass", "case_count", "survivors",
                 "killed_paired")

    def __init__(self, run_id, arm, carries_kill_record, evaluated,
                 identity_pass, case_count, survivors, killed_paired):
        if arm not in ARM_LANGUAGE:
            raise FamilyError("FAMILY-UNKNOWN-ARM %r" % (arm,))
        if evaluated and not carries_kill_record:
            raise FamilyError(
                "FAMILY-PREDICATE-ORDER %s: an evaluated run without a kill "
                "record is not a state 019's scorer or this study's can emit"
                % (run_id,))
        self.run_id = run_id
        self.arm = arm
        self.language = ARM_LANGUAGE[arm]
        self.carries_kill_record = bool(carries_kill_record)
        self.evaluated = bool(evaluated)
        self.identity_pass = bool(identity_pass)
        self.case_count = case_count
        self.survivors = frozenset(survivors or ())
        self.killed_paired = dict(killed_paired or {})

    def covered(self, corpus, column):
        """The class indices this run's suite reaches, in this column.

        A class is covered iff the suite kills ALL of its members in the run's
        own language (section 5.2's pinned coverage rule). A class with no
        members of that language in this column is covered VACUOUSLY and carries
        weight zero, so the vacuity never reaches a number. Gated on
        `evaluated`: a run that evaluated nothing reaches nothing (for the two
        R1-3 runs this is numerically identical to the old gate — their
        synthesized all-survivor vector already covered no class — and the
        gate now says why)."""
        if not self.evaluated:
            return ()
        language = self.language
        return tuple(
            i for i in range(len(corpus.classes))
            if not (set(corpus.members(i, language, column)) & self.survivors))


def unit_not_evaluated(run_id, arm, identity_pass, case_count):
    """A run whose kill record exists and says NOTHING RAN (R1-3).

    Study 019's two identity-failing admitted runs are this state: the frozen
    record carries a kill block (`killedPaired: 0` beside an empty survivor
    vector), and 019's scorer — mutant execution gated on identity — evaluated
    no mutant. The unit carries the record (F-3's marginal keeps its 90-run
    denominator under the `kill-record` predicate) and is not evaluated (the
    `evaluated` marginal and every outcome read zero)."""
    return Unit(run_id, arm, True, False, identity_pass, case_count, (), {})


def unit_from_kill_record(run_id, arm, identity_pass, case_count, kill,
                          corpus):
    """Build a `Unit` from a run's `kill` block, refusing the token collision.

    SECTION 7 DELTA 1, IMPLEMENTED AS A REFUSAL. Coverage is derived from the
    explicit per-mutant survivor vector; the derived kill count is then
    cross-checked against the record's own `killedPaired` in BOTH columns. A
    record carrying `survivorsPaired: []` with `killedPaired: 0` fails that
    check — the survivor vector says "everything killed", the count says
    "nothing evaluated" — and raises rather than scoring a perfect 33/33.

    `kill` of `None` is a run with no kill record: it is admitted, it is in the
    ITT denominator, it scores 0, it takes no offset under EITHER predicate,
    and neither `carries_kill_record` nor `evaluated` holds."""
    if kill is None:
        return Unit(run_id, arm, False, False, identity_pass, case_count,
                    (), {})
    if "survivorsPaired" not in kill:
        raise FamilyError(
            "FAMILY-NO-SURVIVOR-VECTOR %s carries a kill block with no "
            "survivorsPaired; section 5.1 requires an explicit per-mutant "
            "survivor vector for every admitted run" % run_id)
    survivors = kill["survivorsPaired"]
    if survivors is None:
        raise FamilyError(
            "FAMILY-NO-SURVIVOR-VECTOR %s carries survivorsPaired: null" % run_id)
    unit = Unit(run_id, arm, True, True, identity_pass, case_count, survivors,
                {"included": kill.get("killedPaired"),
                 "excluded": kill.get("killedPairedExcludingEngineSupplied")})
    for column in COLUMNS:
        recorded = unit.killed_paired.get(column)
        if recorded is None:
            continue
        derived = sum(len(corpus.members(i, unit.language, column))
                      for i in unit.covered(corpus, column))
        if derived != recorded:
            raise EmptySurvivorAmbiguity(
                "FAMILY-EMPTY-SURVIVOR-AMBIGUOUS %s (%s column): the survivor "
                "vector implies %d killed paired mutants and the record says "
                "%d. An empty survivor vector beside a zero kill count encodes "
                "'nothing evaluated' and 'everything killed' with the same "
                "token (section 5.2, section 7 delta 1) and is refused."
                % (run_id, column, derived, recorded))
    return unit


# ---------------------------------------------------------------------------
# The eighteen members
# ---------------------------------------------------------------------------

class Member(object):
    """One registered family member. Section 5.2's crossing, one cell."""

    __slots__ = ("id", "level", "column", "population", "adjusted")

    def __init__(self, member_id, level, column, population, adjusted):
        self.id = member_id
        self.level = level
        self.column = column
        self.population = population
        self.adjusted = adjusted

    @property
    def permutations(self):
        return (PERMUTATIONS_ADJUSTED if self.adjusted
                else PERMUTATIONS_UNADJUSTED)

    def __repr__(self):
        return "Member(%s, %s, %s, %s, %s)" % (
            self.id, self.level, self.column, self.population,
            "ANCOVA" if self.adjusted else "unadjusted")


def _build_members():
    """The crossing, in section 5.5 Reprint 1's own M1..M18 order.

    Level varies slowest, then the engine column, then the population/adjustment
    cell — which is what puts L1/incl/ITT at M1 and L2c/excl/PP/ANCOVA at M18.
    The ITT x ANCOVA cell is not skipped here so much as never generated: the
    cell list is the three cells section 5.2 registers, and the fourth crossing
    is refused by `member_outcomes()` if anyone constructs it by hand."""
    cells = (("ITT", False), ("PP", False), ("PP", True))
    members = []
    number = 0
    for level in LEVELS:
        for column in COLUMNS:
            for population, adjusted in cells:
                number += 1
                members.append(Member("M%d" % number, level, column,
                                      population, adjusted))
    return tuple(members)


MEMBERS = _build_members()
MEMBER_IDS = tuple(member.id for member in MEMBERS)
MEMBERS_BY_ID = dict((member.id, member) for member in MEMBERS)

#: The two cells section 5.2 registers OUT of the family. The second has no
#: population pole here at all — "artifact-bearing complete-case" is not a value
#: `Member.population` can take — so only the first needs a refusal.
REFUSED_CELLS = (("ITT", True),)


# ---------------------------------------------------------------------------
# Outcomes, the offset, and the two contrasts
# ---------------------------------------------------------------------------

def level_is_l2c(member) -> bool:
    return member.level == "L2c"


def population_units(units, population):
    """Section 5.2's two population poles.

    ITT = every section-1a admitted run, a run with no scorable suite scoring 0,
    so the population is every unit handed in. Per-protocol = the
    `referenceIdentity`-passing runs."""
    if population == "ITT":
        return tuple(units)
    if population == "PP":
        return tuple(unit for unit in units if unit.identity_pass)
    raise FamilyError("FAMILY-UNKNOWN-POPULATION %r" % (population,))


def raw_outcome(unit, corpus, level, column, weighting="native"):
    """The member's weighted count over the run's coverage set S, before L2c's
    offset. A run that evaluated nothing scores 0 in every level and every
    column (R1-3)."""
    if not unit.evaluated:
        return 0.0
    table = corpus.weights(level, column, weighting)
    index = 0 if unit.language == "jps" else 1
    covered = unit.covered(corpus, column)
    return math.fsum(table[i][index] for i in covered if i in table)


def offset(units, corpus, column, population, weighting="native",
           predicate="kill-record"):
    """L2c's registered de-biasing estimator.

    off^ = sum_g pi^_g (w^A_g - w^C_g), pi^ the pooled, ARM-LABEL-FREE coverage
    marginal over the selected runs of that member's own analysis population
    (section 5.2, "L2c, registered definition"). No arm label is read: the
    marginal pools every selected unit of the population regardless of arm, and
    the weights come from the manifests.

    `weighting` was finding F-1's open question. Round 1 (R1-4) ruled the
    HYBRID — `"shared"` offsets under native outcomes, the reading that
    reproduces section 5.2's published -0.04956 / -0.04846 / -0.04922 /
    -0.04813 and Reprint 1's M13..M18. ROUND 2 (R2-2) REFUSED that ruling and
    the maintainer re-ruled NATIVE-FOR-BOTH: the offset is taken in the SAME
    universe as the outcome it de-biases, so the default is `"native"` and the
    registered value is `harness/PINS.json`'s `family.offsetWeighting`. The
    shared reading stays computable and is published as Tier D beside it
    (the superseded hybrid, and shared-for-both).

    `predicate` is ROUND-1 FINDING R1-3's split: `"kill-record"` selects the
    units that carry a kill record — F-3's predicate, the only one that
    reproduces 019's published ITT offsets (marginal size 90) — and
    `"evaluated"` selects the units that actually evaluated a mutant (88 on
    019: the two identity-failing arm-A runs leave). The two per-protocol
    marginals are identical (both runs fail identity); the two ITT readings
    are both published, the kill-record one as 019's own and the evaluated
    one as the R1-3 correction."""
    if predicate == "kill-record":
        selected = [unit for unit in population_units(units, population)
                    if unit.carries_kill_record]
    elif predicate == "evaluated":
        selected = [unit for unit in population_units(units, population)
                    if unit.evaluated]
    else:
        raise FamilyError("FAMILY-UNKNOWN-PREDICATE %r" % (predicate,))
    if not selected:
        raise EmptyArmDenominator(
            "FAMILY-EMPTY-ARM the %s population has no %s run, so the "
            "coverage marginal L2c's offset needs is undefined"
            % (population, predicate))
    table = corpus.weights("L2c", column, weighting)
    indices = sorted(table)
    counts = dict((i, 0) for i in indices)
    for unit in selected:
        for i in unit.covered(corpus, column):
            if i in counts:
                counts[i] += 1
    size = float(len(selected))
    return math.fsum((counts[i] / size) * (table[i][0] - table[i][1])
                     for i in indices)


def member_outcomes(member, units, corpus, weighting="native",
                    offset_weighting="native", predicate="kill-record",
                    _allow_mixed=False):
    """`[(arm, outcome, caseCount), ...]` for one member, in unit order.

    The ITT x ANCOVA cell is refused HERE, before any number exists, because a
    refusal that arrives after the covariate-less runs have been dropped is the
    fallback section 5.2 forbids. ROUND-2 FINDING R2-2: so is a MIXED
    UNIVERSE — an L2c outcome weighted in one universe with an offset from the
    other — for the same reason and at the same seat; `alternative_outcomes()`
    is the one caller allowed past it, and it labels what it returns Tier D.

    `predicate` is round-1 R1-3's split threaded through to the SUBTRACTION
    set as well as the marginal (round 2): under `"kill-record"` the offset is
    subtracted from every arm-A run carrying a kill record (36 on 019 — the
    reading that reproduces Reprint 1); under `"evaluated"` from the 34 that
    evaluated a mutant. §5.2's R1-3 correction table is computed through this
    path now rather than transcribed."""
    if level_is_l2c(member) and weighting != offset_weighting \
            and not _allow_mixed:
        raise MixedUniverseRefused(
            "FAMILY-MIXED-UNIVERSE %s: the outcome is weighted %r and the "
            "offset %r; section 5.2 criterion (iii) requires the de-biased "
            "form, and de-biasing an estimand with another universe's null "
            "offset leaves a computable residual (+0.043552 PP / +0.042584 ITT "
            "on 019). The two single-universe readings and the superseded "
            "hybrid are Tier D, computed by alternative_outcomes(), not by a "
            "member seat." % (member.id, weighting, offset_weighting))
    if predicate not in ("kill-record", "evaluated"):
        raise FamilyError("FAMILY-UNKNOWN-PREDICATE %r" % (predicate,))
    if (member.population, member.adjusted) in REFUSED_CELLS:
        raise IttAncovaRefused(
            "FAMILY-ITT-ANCOVA-REFUSED %s: caseCount is undefined for a run "
            "with no parseable suite, so adjusting the ITT pole for it is a "
            "covert change of population, not an adjustment (section 5.2). "
            "The six quantities are published in Tier D with that sentence "
            "attached; the family does not contain this cell and this scorer "
            "does not fall back to complete cases." % member.id)
    level = member.level
    selected = population_units(units, member.population)
    shift = 0.0
    if level == "L2c":
        shift = offset(units, corpus, member.column, member.population,
                       offset_weighting, predicate)
    rows = []
    for unit in selected:
        value = raw_outcome(unit, corpus, level, member.column, weighting)
        takes = (unit.carries_kill_record if predicate == "kill-record"
                 else unit.evaluated)
        if level == "L2c" and takes and unit.arm == "A":
            # F-3's registered subtraction population — the arm-A runs that
            # carry a kill record (36 on 019), which with the kill-record
            # marginal above is the reading that reproduces Reprint 1; under
            # the `evaluated` predicate the 34 that evaluated a mutant.
            value -= shift
        if member.adjusted and unit.case_count is None:
            raise FamilyError(
                "FAMILY-MISSING-COVARIATE %s has no caseCount and is in an "
                "adjusted member's population; section 5.2 pin 4 requires a "
                "caseCount for every admitted run with a suite" % unit.run_id)
        rows.append((unit.arm, value, unit.case_count))
    return rows


def _by_arm(rows):
    table = {}
    for arm, value, covariate in rows:
        table.setdefault(arm, []).append((value, covariate))
    return table


def _mean(values):
    values = list(values)
    if not values:
        raise EmptyArmDenominator(
            "FAMILY-EMPTY-ARM a mean over an empty arm is not INDETERMINATE, "
            "it is not computed at all (section 5.1)")
    return math.fsum(values) / len(values)


def unadjusted_difference(rows, left, right):
    table = _by_arm(rows)
    for arm in (left, right):
        if not table.get(arm):
            raise EmptyArmDenominator(
                "FAMILY-EMPTY-ARM arm %s has no unit in this member's "
                "population; section 5.1 registers that the contrast is not "
                "computed at all" % arm)
    return (_mean(value for value, _ in table[left])
            - _mean(value for value, _ in table[right]))


def ancova(rows):
    """Section 5.2's ANCOVA, pinned to the byte.

    "Pooled *within-arm* slope estimated over **all three arms** jointly;
    adjusted difference evaluated at the grand covariate mean." Both halves of
    that sentence are load-bearing: the slope pools every arm present in `rows`,
    including the arm neither side of the contrast names, and the grand mean is
    over the same set. Section 5.2 pin 2 registers the three-arm form and sends
    the pairwise variant to Tier D, which is `ancova(two_arm_rows)`."""
    table = _by_arm(rows)
    numerator = []
    denominator = []
    for arm in sorted(table):
        entries = table[arm]
        covariate_mean = _mean(c for _, c in entries)
        value_mean = _mean(v for v, _ in entries)
        for value, covariate in entries:
            numerator.append((covariate - covariate_mean)
                             * (value - value_mean))
            denominator.append((covariate - covariate_mean) ** 2)
    spread = math.fsum(denominator)
    if spread == 0.0:
        raise FamilyError(
            "FAMILY-NO-COVARIATE-SPREAD every run carries the same caseCount; "
            "the pooled within-arm slope is undefined and is not imputed")
    slope = math.fsum(numerator) / spread
    grand = _mean(c for _, _, c in rows)
    adjusted = {}
    covariate_means = {}
    for arm in sorted(table):
        entries = table[arm]
        covariate_means[arm] = _mean(c for _, c in entries)
        adjusted[arm] = (_mean(v for v, _ in entries)
                         + slope * (grand - covariate_means[arm]))
    return {"slope": slope, "grandCovariateMean": grand,
            "armCovariateMeans": covariate_means, "adjustedMeans": adjusted}


def adjusted_difference(rows, left, right):
    table = _by_arm(rows)
    for arm in (left, right):
        if not table.get(arm):
            raise EmptyArmDenominator(
                "FAMILY-EMPTY-ARM arm %s has no unit in this member's "
                "population; section 5.1 registers that the contrast is not "
                "computed at all" % arm)
    fit = ancova(rows)
    return fit["adjustedMeans"][left] - fit["adjustedMeans"][right]


def difference(rows, left, right, adjusted):
    return (adjusted_difference(rows, left, right) if adjusted
            else unadjusted_difference(rows, left, right))


# ---------------------------------------------------------------------------
# Section 5.3's two permutation schemes
# ---------------------------------------------------------------------------

def permutation_test(rows, left, right, adjusted, permutations, seed):
    """Section 5.3's per-member test. One scheme per pole, both stated here.

    UNADJUSTED — "Exact two-sided permutation test on the difference in means,
    permuting arm labels within the two-arm subset." Only the two contrasted
    arms take part; the third arm is not in the subset and is not permuted.

    ADJUSTED — "The unit's **whole record** (outcome and `caseCount`) travels
    with the permuted label." The third arm stays where it is and keeps
    contributing to the three-arm pooled slope, which is what section 5.2 pin 2
    pins. This is exact under the STRONG sharp null only, and section 5.3 says
    so; nothing here claims otherwise.

    The count is two-sided on the absolute difference and the p is section 5.3's
    `(count + 1) / (B + 1)`. The tolerance on the comparison is one part in
    1e12 of nothing: a permutation that reproduces the observed statistic
    exactly must COUNT, and float noise must not remove it."""
    observed = difference(rows, left, right, adjusted)
    subset = [row for row in rows if row[0] in (left, right)]
    rest = [row for row in rows if row[0] not in (left, right)]
    if not subset:
        raise EmptyArmDenominator(
            "FAMILY-EMPTY-ARM the %s-%s subset is empty" % (left, right))
    labels = [row[0] for row in subset]
    payload = [(row[1], row[2]) for row in subset]
    engine = random.Random(seed)
    count = 0
    for _ in range(permutations):
        engine.shuffle(payload)
        permuted = [(labels[i], payload[i][0], payload[i][1])
                    for i in range(len(subset))]
        candidate = (adjusted_difference(permuted + rest, left, right)
                     if adjusted else
                     unadjusted_difference(permuted, left, right))
        if abs(candidate) >= abs(observed) - 1e-12:
            count += 1
    return {"observed": observed, "count": count,
            "permutations": permutations, "seed": seed,
            "p": (count + 1) / float(permutations + 1),
            "method": ("whole-record permutation" if adjusted
                       else "label permutation")}


# ---------------------------------------------------------------------------
# Dispersion — section 5.6's sigma column
# ---------------------------------------------------------------------------

def pooled_within_arm_sd(rows):
    """Section 5.6: "pooled within-arm SD, unbiased (N - k ...), all arm-blind".

    k is the number of arms present, so the divisor is N - k. Arm-blind in the
    sense section 5.6 means it: the arm labels partition the sum of squares and
    no arm's mean is compared with another's."""
    table = _by_arm(rows)
    squares = []
    total = 0
    for arm in sorted(table):
        entries = table[arm]
        centre = _mean(v for v, _ in entries)
        squares.extend((value - centre) ** 2 for value, _ in entries)
        total += len(entries)
    if total <= len(table):
        raise EmptyArmDenominator(
            "FAMILY-EMPTY-ARM N - k is not positive; there is no dispersion "
            "estimate and none is imputed")
    return math.sqrt(math.fsum(squares) / (total - len(table)))


def residual_sd(rows):
    """Section 5.6's adjusted-member sigma: "residual N - 4"."""
    table = _by_arm(rows)
    fit = ancova(rows)
    slope = fit["slope"]
    squares = []
    total = 0
    for arm in sorted(table):
        entries = table[arm]
        covariate_mean = _mean(c for _, c in entries)
        value_mean = _mean(v for v, _ in entries)
        squares.extend(((value - value_mean) - slope * (covariate
                                                        - covariate_mean)) ** 2
                       for value, covariate in entries)
        total += len(entries)
    if total <= 4:
        raise EmptyArmDenominator(
            "FAMILY-EMPTY-ARM N - 4 is not positive; there is no residual "
            "dispersion estimate and none is imputed")
    return math.sqrt(math.fsum(squares) / (total - 4))


#: Section 5.6's MDE constant: "MDE = 2.8016 * sigma * sqrt(1/n_A + 1/n_C) at
#: two-sided alpha = 0.05, 80 % power". Transcribed, not derived: 2.8016 is
#: z(0.975) + z(0.80) and section 5.6 publishes it to four places.
MDE_CONSTANT = 2.8016


def minimum_detectable_effect(sigma, n_left, n_right):
    if n_left <= 0 or n_right <= 0:
        raise EmptyArmDenominator(
            "FAMILY-EMPTY-ARM an MDE over an empty arm is not computed")
    return MDE_CONSTANT * sigma * math.sqrt(1.0 / n_left + 1.0 / n_right)


# ---------------------------------------------------------------------------
# Section 5.3's Tier D interval
# ---------------------------------------------------------------------------

def bca_interval(rows, left, right, adjusted, resamples=None, seed=None,
                 alpha=ALPHA):
    """BCa bootstrap interval on the member's difference. TIER D. NO DECISION
    READS IT (section 5.3, section 5.8).

    REFUSES UNLESS PINNED. Section 5.3 registers "BCa bootstrap, per member,
    coverage stated as approximate" and pins neither a resample count nor a
    seed, while it pins both for the permutation tests two bullets earlier. A
    Tier D quantity produced from a number this file chose would be a figure no
    registration authorises, so there is no default here — finding F-2's second
    half. The caller passes the pinned pair once `PINS.json` carries one.

    The resampling is STRATIFIED BY ARM, which is the only scheme under which
    the resampled statistic is the same functional as the observed one, and
    ROUND-1 FINDING R1-5's second half fixed WHICH arms that stratification
    covers. The adjusted statistic fits the pooled within-arm slope over ALL
    THREE arms (section 5.2's registered ANCOVA), so for an adjusted member
    every arm is data and every stratum is resampled, and the jackknife
    deletes over every row; holding arm B fixed — the first implementation —
    bootstrapped a different functional than the observed one. For an
    unadjusted member the statistic reads only the two contrast arms, and the
    scheme resamples exactly those. Coverage is approximate and is labelled so
    in the returned block; the word "exact" is used only of a permutation null
    distribution (section 5.3) and does not appear here."""
    if resamples is None or seed is None:
        raise IntervalUnpinned(
            "FAMILY-BCA-UNPINNED section 5.3 registers a BCa interval and pins "
            "neither its resample count nor its seed, and PINS.json carries no "
            "family member. Pass the pinned pair; this scorer does not choose "
            "one and does not publish an interval it invented the B for.")
    subset = [row for row in rows if row[0] in (left, right)]
    if not subset:
        raise EmptyArmDenominator(
            "FAMILY-EMPTY-ARM the %s-%s subset is empty" % (left, right))
    # R1-5: the resampled arms are the arms the STATISTIC reads — all of them
    # for an adjusted member (the three-arm slope), the contrast pair for an
    # unadjusted one.
    if adjusted:
        resampled_arms = sorted(set(row[0] for row in rows))
    else:
        resampled_arms = [left, right]
    rest = [row for row in rows if row[0] not in resampled_arms]
    observed = difference(rows, left, right, adjusted)
    strata = dict((arm, [row for row in rows if row[0] == arm])
                  for arm in resampled_arms)
    for arm in (left, right):
        if not strata.get(arm):
            raise EmptyArmDenominator(
                "FAMILY-EMPTY-ARM arm %s has no unit" % arm)
    engine = random.Random(seed)
    replicates = []
    for _ in range(resamples):
        drawn = []
        for arm in resampled_arms:
            pool = strata[arm]
            drawn.extend(pool[engine.randrange(len(pool))]
                         for _ in range(len(pool)))
        try:
            replicates.append(difference(drawn + rest, left, right, adjusted))
        except FamilyError:
            continue
    if not replicates:
        raise FamilyError(
            "FAMILY-BCA-DEGENERATE no bootstrap replicate was computable")
    replicates.sort()
    below = sum(1 for value in replicates if value < observed)
    fraction = below / float(len(replicates))
    if fraction <= 0.0 or fraction >= 1.0:
        bias = 0.0
    else:
        bias = _normal_quantile(fraction)
    jackknife = []
    pooled = [row for arm in resampled_arms for row in strata[arm]]
    for index in range(len(pooled)):
        held = pooled[:index] + pooled[index + 1:]
        try:
            jackknife.append(difference(held + rest, left, right, adjusted))
        except FamilyError:
            continue
    centre = _mean(jackknife)
    top = math.fsum((centre - value) ** 3 for value in jackknife)
    bottom = math.fsum((centre - value) ** 2 for value in jackknife)
    acceleration = 0.0 if bottom == 0.0 else top / (6.0 * bottom ** 1.5)
    lower = _bca_endpoint(replicates, bias, acceleration, alpha / 2.0)
    upper = _bca_endpoint(replicates, bias, acceleration, 1.0 - alpha / 2.0)
    return {"point": observed, "lower": lower, "upper": upper,
            "resamples": resamples, "seed": seed, "alpha": alpha,
            "biasCorrection": bias, "acceleration": acceleration,
            "coverage": "approximate",
            "resampledArms": list(resampled_arms),
            "method": "BCa bootstrap, stratified by arm over the arms the "
                      "statistic reads"}


def _bca_endpoint(replicates, bias, acceleration, level):
    quantile = _normal_quantile(level)
    adjusted_level = _normal_cdf(
        bias + (bias + quantile) / (1.0 - acceleration * (bias + quantile)))
    position = adjusted_level * (len(replicates) - 1)
    low = int(math.floor(position))
    high = min(low + 1, len(replicates) - 1)
    weight = position - low
    return replicates[low] * (1.0 - weight) + replicates[high] * weight


def _normal_cdf(value):
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def _normal_quantile(probability):
    """Inverse normal CDF by bisection. Fixed iteration count, no tolerance and
    no early exit, so the same bits come out on any platform — the discipline
    `e4lib/stats.py` carries from Study 012's Clopper-Pearson bisection."""
    if not 0.0 < probability < 1.0:
        raise FamilyError("FAMILY-QUANTILE-DOMAIN %r" % (probability,))
    low, high = -40.0, 40.0
    for _ in range(200):
        middle = (low + high) / 2.0
        if _normal_cdf(middle) < probability:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


# ---------------------------------------------------------------------------
# The family, the drop-a-pole table and the IU verdict
# ---------------------------------------------------------------------------

def score_member(member, units, corpus, left, right, seed=PERMUTATION_SEED,
                 weighting="native", offset_weighting="native",
                 bca_resamples=None, bca_seed=None, predicate="kill-record",
                 _allow_mixed=False):
    """One member's whole published row. Identical shape for every member."""
    rows = member_outcomes(member, units, corpus, weighting, offset_weighting,
                           predicate, _allow_mixed=_allow_mixed)
    table = _by_arm(rows)
    counts = dict((arm, len(table.get(arm, ()))) for arm in sorted(ARM_LANGUAGE))
    for arm in (left, right):
        if counts.get(arm, 0) == 0:
            raise EmptyArmDenominator(
                "FAMILY-EMPTY-ARM %s: arm %s has a zero denominator. Section "
                "5.1: each member's per-arm denominator must be positive, a "
                "contrast over an empty arm is not INDETERMINATE, it is not "
                "computed at all, and the outcome falls to the rows above."
                % (member.id, arm))
    test = permutation_test(rows, left, right, member.adjusted,
                            member.permutations, seed)
    sigma = residual_sd(rows) if member.adjusted else pooled_within_arm_sd(rows)
    row = {
        "id": member.id,
        "level": member.level,
        "engine": member.column,
        "population": member.population,
        "adjustment": "ANCOVA" if member.adjusted else None,
        "n": counts,
        "difference": test["observed"],
        "sign": (0 if test["observed"] == 0.0
                 else (1 if test["observed"] > 0.0 else -1)),
        "p": test["p"],
        "permutationCount": test["count"],
        "permutations": test["permutations"],
        "seed": test["seed"],
        "method": test["method"],
        "rejects": test["p"] < ALPHA,
        "sigma": sigma,
        "mde": minimum_detectable_effect(sigma, counts[left], counts[right]),
        "interval": None,
        "intervalRefusal": None,
    }
    try:
        row["interval"] = bca_interval(rows, left, right, member.adjusted,
                                       bca_resamples, bca_seed)
    except IntervalUnpinned as refusal:
        row["intervalRefusal"] = str(refusal)
    return row


#: The nine poles section 5.5's Reprint 2 drops, one at a time, in its own order.
POLES = (("L1", lambda m: m.level == "L1"),
         ("L3", lambda m: m.level == "L3"),
         ("L2c", lambda m: m.level == "L2c"),
         ("engine-included", lambda m: m.column == "included"),
         ("engine-excluded", lambda m: m.column == "excluded"),
         ("ITT", lambda m: m.population == "ITT"),
         ("per-protocol", lambda m: m.population == "PP"),
         ("adjusted", lambda m: m.adjusted),
         ("unadjusted", lambda m: not m.adjusted))


def verdict(rows, arms=("A", "C")):
    """Section 5.9 row 4's antecedent, evaluated. Not a decision row.

    THE RETURNED SHAPE IS `e4lib/decision.py`'s CONTRACT, not a shape this file
    chose. `decision._family_claims()` reads `members` (a list, whose length it
    checks against its own `REGISTERED_FAMILY_SIZE`), `claim`, `sign` and
    `arms`; `decision.direction()` reads `sign` and `arms` and spells the
    direction in arm names. Those keys are here, under those names, so the two
    deltas meet at a written interface rather than at a convention. The
    descriptive keys beside them (`positive`, `rejecting`, ...) are section
    5.5's reprint, which no decision reads.

    "All eighteen family members agree in the sign of the A-C difference and all
    eighteen reject at two-sided alpha = 0.05" -> CLAIM, direction the common
    sign. Otherwise INDETERMINATE-BY-DISAGREEMENT.

    Refuses a result set that is not the registered membership. Section 5.2:
    membership is append-only, a maintainer "may **never** remove one", and
    removing members is the ANTI-CONSERVATIVE direction under section 5.4's
    intersection-union logic — so a verdict computed over a short family would
    be more likely to claim, not less, and is refused rather than warned about."""
    seen = [row["id"] for row in rows]
    missing = [member_id for member_id in MEMBER_IDS if member_id not in seen]
    if missing:
        raise MembershipError(
            "FAMILY-MEMBERSHIP-INCOMPLETE the verdict was asked for over %d of "
            "the %d registered members; %s are absent. Section 5.2 registers "
            "membership as append-only and removal moves the intersection-union "
            "test toward CLAIM, so a short family is refused, not warned about."
            % (len(seen), len(MEMBER_IDS), ", ".join(missing)))
    if len(seen) != len(set(seen)):
        raise MembershipError(
            "FAMILY-MEMBERSHIP-DUPLICATE a member appears twice; an IU verdict "
            "over a multiset is not the registered test")
    # ROUND-1 FINDING R1-8, three refusals the old checks lacked:
    extras = [member_id for member_id in seen if member_id not in MEMBERS_BY_ID]
    if extras:
        raise MembershipError(
            "FAMILY-MEMBERSHIP-EXTRA the verdict was handed rows for %s, which "
            "the registration does not contain; a favourable row wearing a "
            "registered id's seat is exactly what a closed membership exists "
            "to refuse" % ", ".join(sorted(extras)))
    for row in rows:
        member = MEMBERS_BY_ID[row["id"]]
        if (row.get("level"), row.get("engine"), row.get("population"),
                row.get("adjustment")) != (member.level, member.column,
                                           member.population,
                                           "ANCOVA" if member.adjusted
                                           else None):
            raise MembershipError(
                "FAMILY-MEMBERSHIP-RELABELLED %s's row states axes %r and the "
                "registration says %r; a row cannot sit in a member's seat by "
                "carrying its id alone" % (
                    row["id"],
                    (row.get("level"), row.get("engine"),
                     row.get("population"), row.get("adjustment")),
                    (member.level, member.column, member.population,
                     "ANCOVA" if member.adjusted else None)))
        derived_sign = (0 if row["difference"] == 0.0
                        else (1 if row["difference"] > 0.0 else -1))
        derived_rejects = row["p"] < ALPHA
        if row["sign"] != derived_sign or bool(row["rejects"]) != derived_rejects:
            raise MembershipError(
                "FAMILY-MEMBERSHIP-INCONSISTENT %s carries sign %r / rejects "
                "%r where its own difference %r and p %r derive %r / %r; the "
                "verdict recomputes both and refuses a row whose stated "
                "booleans disagree with its stated numbers"
                % (row["id"], row["sign"], row["rejects"], row["difference"],
                   row["p"], derived_sign, derived_rejects))
    signs = set(row["sign"] for row in rows)
    unanimous_sign = len(signs) == 1 and 0 not in signs
    all_reject = all(row["rejects"] for row in rows)
    claims = unanimous_sign and all_reject
    return {
        "verdict": CLAIM if claims else INDETERMINATE,
        "claim": claims,
        # STRINGS IN EVERY BRANCH, never `None` in one and a word in another:
        # the brief's section 4.2.4 says the published quantity set is identical
        # whatever the outcome, and a key whose TYPE changes with the verdict is
        # a branch in the published record.
        "sign": ("+" if signs == {1} else ("-" if signs == {-1} else "none")),
        "direction": ("positive" if signs == {1} else
                      ("negative" if signs == {-1} else "none")),
        "arms": list(arms),
        "positive": sum(1 for row in rows if row["sign"] > 0),
        "negative": sum(1 for row in rows if row["sign"] < 0),
        "zero": sum(1 for row in rows if row["sign"] == 0),
        "rejecting": sum(1 for row in rows if row["rejects"]),
        "members": [row["id"] for row in rows],
        "memberCount": len(rows),
        "signUnanimous": unanimous_sign,
        "allReject": all_reject,
        "alpha": ALPHA,
        "rule": ("intersection-union: CLAIM iff every registered member agrees "
                 "in sign and every registered member rejects at two-sided "
                 "alpha = 0.05 (section 5.4, section 5.9 row 4)"),
    }


def drop_a_pole(rows):
    """Section 5.5's Reprint 2, computed rather than asserted.

    Each row drops every member carrying one pole and re-evaluates the same IU
    rule over what is left. It is a DIAGNOSTIC and no decision reads it: section
    5.2's membership is append-only precisely so that "the family without pole
    X" is never the family."""
    by_id = dict((row["id"], row) for row in rows)
    table = []
    for name, carries in POLES:
        kept = [by_id[member.id] for member in MEMBERS
                if member.id in by_id and not carries(member)]
        positive = sum(1 for row in kept if row["sign"] > 0)
        rejecting = sum(1 for row in kept if row["rejects"])
        signs = set(row["sign"] for row in kept)
        claims = (bool(kept) and len(signs) == 1 and 0 not in signs
                  and rejecting == len(kept))
        table.append({"poleDropped": name, "membersLeft": len(kept),
                      "positive": positive, "rejecting": rejecting,
                      "verdict": CLAIM if claims else INDETERMINATE,
                      "members": [row["id"] for row in kept]})
    return table


def refused_cell_tier_d(units, corpus, left="A", right="C",
                        offset_weighting="native"):
    """ROUND-1 FINDING R1-7: section 5.2's six argued-out ITT x ANCOVA
    quantities, published as TIER D — non-member, non-decision — beside the
    family's hard refusal of the cell.

    The cell is refused as a MEMBER because adjusting the ITT pole drops the
    covariate-less runs, a covert change of population; what section 5.2
    registers instead is DISCLOSURE: the six adjusted differences over the
    artifact-bearing complete-case population (the ITT units that carry a
    caseCount), with that population's per-arm composition printed beside
    them so a reader sees exactly what the refused cell would have been
    computed over. `member_outcomes()` still refuses the cell; this function
    is the disclosure, reads no member seat, and nothing in
    `e4lib/decision.py` reads it."""
    itt = population_units(units, "ITT")
    complete = [unit for unit in itt if unit.case_count is not None]
    composition = {
        "population": "artifact-bearing complete-case (ITT with a caseCount)",
        "perArm": dict((arm, sum(1 for unit in complete if unit.arm == arm))
                       for arm in sorted(ARM_LANGUAGE)),
        "droppedPerArm": dict(
            (arm, sum(1 for unit in itt
                      if unit.arm == arm and unit.case_count is None))
            for arm in sorted(ARM_LANGUAGE)),
    }
    quantities = []
    for level in LEVELS:
        for column in COLUMNS:
            shift = offset(units, corpus, column, "ITT", offset_weighting)
            rows = []
            for unit in complete:
                value = raw_outcome(unit, corpus, level, column)
                if level == "L2c" and unit.carries_kill_record                         and unit.arm == "A":
                    value -= shift
                rows.append((unit.arm, value, unit.case_count))
            quantities.append({
                "level": level, "engine": column,
                "population": "ITT", "adjustment": "ANCOVA",
                "adjustedDifference": adjusted_difference(rows, left, right),
                "tier": "D",
                "reason": "section 5.2's refused cell, disclosed over the "
                          "complete-case population named beside it; not a "
                          "member, read by no decision",
            })
    return {"composition": composition, "quantities": quantities}


#: The members whose rows do not read a weighting at all: `Corpus.weights()`
#: ignores the argument for L1 and L3, so the twelve non-L2c members are
#: identical under every reading (asserted by test, not assumed).
WEIGHTING_INVARIANT_MEMBERS = tuple(m.id for m in MEMBERS if m.level != "L2c")


def alternative_outcomes(units, corpus, left, right, weighting,
                         offset_weighting, label, status,
                         seed=PERMUTATION_SEED, bca_resamples=None,
                         bca_seed=None, base_rows=None):
    """ROUND-2 FINDING R2-3: one Tier D alternative reading of the family,
    COMPLETE — every registered quantity a member row carries, the verdict
    and the drop-a-pole table over all eighteen — under a weighting pair the
    registered estimand did not choose. `member` is False in every row and the
    block says so: nothing here is a member seat and no decision reads it.

    Only the six L2c members read a weighting, so `base_rows` (the registered
    reading's rows) supplies the twelve invariant ones and the six are
    recomputed under (weighting, offset_weighting) with the mixed-universe
    guard lifted — the block is where the superseded hybrid lives, labelled."""
    base = dict((row["id"], row) for row in (base_rows or ()))
    rows = []
    for member in MEMBERS:
        if member.id in base and member.level != "L2c":
            row = dict(base[member.id])
        else:
            row = score_member(member, units, corpus, left, right, seed,
                               weighting, offset_weighting, bca_resamples,
                               bca_seed, _allow_mixed=True)
        row["tier"] = "D"
        row["member"] = False
        rows.append(row)
    offsets = {}
    for column in COLUMNS:
        for population in ("ITT", "PP"):
            offsets["%s/%s" % (column, population)] = offset(
                units, corpus, column, population, offset_weighting)
    return {
        "label": label,
        "status": status,
        "tier": "D",
        "member": False,
        "reason": ("a single-universe alternative to the registered estimand, "
                   "published under section 10's 'full estimand grid' so a "
                   "reader can see what the ruling chose against; read by no "
                   "decision" if status == "ALTERNATIVE" else
                   "the reading published through round 1 (native outcome, "
                   "shared offset), SUPERSEDED by the round-2 R2-2 ruling; "
                   "retained for continuity with Study 019's reprint, read by "
                   "no decision"),
        "outcomeWeighting": weighting,
        "offsetWeighting": offset_weighting,
        "offsets": offsets,
        "members": rows,
        "verdict": verdict(rows, (left, right)),
        "dropAPole": drop_a_pole(rows),
        "weightingInvariantMembers": list(WEIGHTING_INVARIANT_MEMBERS),
    }


def family_report(units, corpus, left="A", right="C",
                  seed=PERMUTATION_SEED, weighting="native",
                  offset_weighting="native", bca_resamples=None,
                  bca_seed=None):
    """Every registered quantity, in one block, with one shape.

    SECTION 4.2.4 OF THE BRIEF, ENFORCED BY CONSTRUCTION: "the published
    quantity set is **identical in every branch**, registered so the outcome
    cannot change what is reported". Every key below is always present and every
    member is always in `members`, whether the verdict is CLAIM or
    INDETERMINATE; the verdict is one value inside the block and never a switch
    over what the block contains.

    `offsets` publishes BOTH readings of finding F-1 in both columns, so the
    registered figure and the one the Fact-2 table's words describe are side by
    side rather than one of them being silently the answer."""
    rows = [score_member(member, units, corpus, left, right, seed, weighting,
                         offset_weighting, bca_resamples, bca_seed)
            for member in MEMBERS]
    offsets = {}
    for column in COLUMNS:
        for population in ("ITT", "PP"):
            for reading in ("shared", "native"):
                for predicate in (("kill-record", "evaluated")
                                  if population == "ITT" else ("kill-record",)):
                    # R1-3: the evaluation-corrected marginal, published
                    # beside 019's own kill-record reading. The two differ
                    # only on ITT (the two runs the predicates split on fail
                    # identity, so the PP marginals are one set), and
                    # publishing the PP pair too would print one number
                    # under two names. R2-3: every entry is a DICT naming
                    # its column, population, weighting and predicate, and
                    # whether it is the reading the estimand used — so the
                    # reading in use is machine-identifiable rather than
                    # inferred from a sibling member.
                    key = "%s/%s/%s%s" % (column, population, reading,
                                          "/evaluated" if predicate == "evaluated"
                                          else "")
                    offsets[key] = {
                        "value": offset(units, corpus, column, population,
                                        reading, predicate),
                        "column": column, "population": population,
                        "weighting": reading, "predicate": predicate,
                        "registered": (reading == offset_weighting
                                       and predicate == "kill-record"),
                        "tier": ("registered"
                                 if reading == offset_weighting
                                 and predicate == "kill-record" else "D"),
                    }
    alternatives = []
    for alt_weighting, alt_offset, label, status in (
            ("native", "shared",
             "hybrid (outcome native / offset shared)", "SUPERSEDED"),
            ("shared", "shared", "shared-for-both", "ALTERNATIVE")):
        if (alt_weighting, alt_offset) == (weighting, offset_weighting):
            continue
        alternatives.append(alternative_outcomes(
            units, corpus, left, right, alt_weighting, alt_offset, label,
            status, seed, bca_resamples, bca_seed, base_rows=rows))
    return {
        "contrast": "%s-%s" % (left, right),
        "alpha": ALPHA,
        "registeredMembers": list(MEMBER_IDS),
        "members": rows,
        "verdict": verdict(rows, (left, right)),
        "dropAPole": drop_a_pole(rows),
        "offsets": offsets,
        "offsetReadingUsed": offset_weighting,
        "outcomeWeightingUsed": weighting,
        # R2-2 / R2-3: the estimand, stated; the alternatives, complete.
        "estimand": {"outcomeWeighting": weighting,
                     "offsetWeighting": offset_weighting,
                     "universe": ("single" if weighting == offset_weighting
                                  else "mixed"),
                     "ruledBy": "round-2 R2-2 (maintainer ruling 2026-08-26: "
                                "native-for-both)",
                     "pinnedIn": "harness/PINS.json family.outcomeWeighting / "
                                 "family.offsetWeighting"},
        "alternatives": alternatives,
        "weightingInvariantMembers": list(WEIGHTING_INVARIANT_MEMBERS),
        "refusedCells": [{"population": population,
                          "adjustment": "ANCOVA" if adjusted else None,
                          "reason": "section 5.2: covert change of population; "
                                    "the scorer refuses rather than falls back"}
                         for population, adjusted in REFUSED_CELLS],
        # R1-7: the refusal above stays a refusal; the six argued-out
        # quantities and the complete-case composition are DISCLOSED beside
        # it, Tier D, exactly as section 5.2 promises.
        "refusedCellTierD": refused_cell_tier_d(units, corpus, left, right,
                                                offset_weighting),
        "corpus": {
            "sharedClasses": dict(
                (column, len(corpus.column_indices(column)))
                for column in COLUMNS),
            "nativeDenominators": dict(
                (column, dict((language,
                               corpus.native_denominator(language, column))
                              for language in LANGUAGES))
                for column in COLUMNS),
            "sharedDenominators": dict(
                (column, dict((language,
                               corpus.shared_denominator(language, column))
                              for language in LANGUAGES))
                for column in COLUMNS),
        },
    }


def extend_family(additions):
    """Section 5.2's append-only rule, as the only way membership can change.

    "After the freeze a maintainer may **add** a member — monotone toward
    INDETERMINATE under section 5.4's intersection-union logic — and may
    **never remove one**. An addition requires a `DEVIATIONS.md` entry and the
    **pre-addition verdict is published beside the post-addition one**."

    Returns the extended tuple; refuses anything that is not strictly an
    addition. It does not write `DEVIATIONS.md` and it does not check that one
    was written — that is `make_manifest.py`'s and the maintainer's business —
    but it refuses to let the eighteen shrink, which is the half that can be
    enforced in code."""
    additions = tuple(additions)
    existing = set(MEMBER_IDS)
    for member in additions:
        if member.id in existing:
            raise MembershipError(
                "FAMILY-MEMBER-DUPLICATE %s is already registered" % member.id)
        if (member.population, member.adjusted) in REFUSED_CELLS:
            raise IttAncovaRefused(
                "FAMILY-ITT-ANCOVA-REFUSED %s: the ITT x ANCOVA cell is "
                "registered OUT of the family and adding it back is not an "
                "append-only addition, it is a reversal of a registration"
                % member.id)
        existing.add(member.id)
    return MEMBERS + additions
