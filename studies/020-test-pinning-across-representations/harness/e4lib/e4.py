"""E4 — pairing, the identity control, kill, the survivor vector, and coverage.

WHAT THIS FILE DOES
-------------------
Builds §4's witness-set pairing, validates an authored suite's cases against the
registered input domain, runs §5's two named identity relations
(`referenceIdentity` and, new in 020, `ownPolicyIdentity`), executes the frozen
mutant corpus against the suite, and emits — per admitted run — an EXPLICIT
per-mutant survivor vector, the per-language paired-adequate denominators, and
the run's coverage set over the shared witness classes.

DELIBERATELY DOES NOT DO
------------------------
* **No threshold.** There is no tau, no integer cut, no `highKill` predicate and
  no reachability assertion (PREREGISTRATION.md §7 delta 2). §5.1 registers the
  primary endpoint with "**No cut, no τ, no dichotomy**", so the machinery that
  would derive one is not kept in a disabled state — it is gone, and
  `harness/tests/test_score_e4.py` asserts that no name of it survives anywhere
  a registered decision path can reach.
* **No weighting and no contrast.** The eighteen family members of §5.2, L2c's
  offset estimator, the permutation schemes and the IU verdict are
  `e4lib/family.py`'s (§7 delta 5). This module hands that module the coverage
  set and the two denominators and computes no member.
* **No arm labels in any derived quantity.** Everything here is per run.

ASSEMBLED FROM `design/mutants/e4_score.py`
(sha256 `beb42b3903284dc2c33baff33000325814a1e53171d8268ca4d56820e4f995fb`):
`load_mutants()` (152-194), `build_pairing()` (195-231), `align_expected()`
(232-245), `load_matrix()` (295-308), `identity_arm_a()` (310-322),
`kill_arm_a()` (323-336), `case_signature()` (375-384), and the per-arm
aggregation of `score_arm()` (556-654). `harness/PORTS.md` carries the two-sided
row and the enumerated change list.

WHAT THE PROTOTYPE DID NOT HAVE, and section 5 registers
--------------------------------------------------------
1. **The registered exclusion filter, and the registered input domain.** §4
   registers an exclusion-class registry and a per-run excluded-case count.
   `REGISTERED_EXCLUSION_CLASSES` is that registry as data and is EMPTY since
   round-1 R1-2 retired X1 (the arm-A reference was repaired instead), so the
   published count is a measured zero rather than a filter nobody applied;
   `in_x1()` is kept as the retired predicate, gating nothing, so the repair
   stays re-measurable. What DOES filter is the registered INPUT DOMAIN, and it
   filters all three arms alike: `e4lib/domain.py` enumerates every arm's case
   inputs mechanically — arm A's from the matrix, arms B/C's from
   `opa parse --format json`'s own syntax tree — and validates each against the
   registered space before identity and before any mutation execution (round-1
   R1-3, which found that arms B and C received no case-level validation at all).
2. **The identity control as a first-class per-arm RATE**, not a gate that
   silently removes suites. The prototype reported identity failures per suite;
   section 5 reports the rate, and section 1a requires the exclusions to be
   "reported, never silently dropped".
3. **The per-language denominators, WITHOUT a threshold on top of them**
   (§7 delta 2). 019 derived an integer cut per language from tau = 0.95; the
   machinery that keeps each language's paired-adequate denominator and lattice
   SEPARATE is what 019's R1-1 was actually about, and it is kept —
   `paired_denominators()` and `shared_classes()` publish both denominators,
   both lattices and the shared-class count, so R1-1's defect (one cut derived
   from the JPS count and applied to every arm) stays structurally impossible.
   The THRESHOLD is removed: 020 registers no tau, no integer cut and no
   `highKill` member, because §5.1 registers the endpoint as a weighted count
   over a coverage set rather than as a dichotomy.
4. **The engine-supplied-kill split** (SCAFFOLD item S9, closed). Section 4
   registers 35 (now 41) arm-A mutants "listed in the registries" whose kills
   are achievable only through the engine's structural conflict detection,
   "reported both included and excluded". Both manifests now carry a
   machine-readable `engineSuppliedKill` member — arm A's derived from
   `design/mutants/refA/REGISTRY.json`'s `conflictOnlyMutants`, arm B's an
   EMPTY registered class, because the Rego ladder has no structural conflict
   detection and an empty class is a fact where a missing member would be a
   silence. `engine_supplied_ids()` reads the member and `kill_rates()` splits
   the paired subset on it; a manifest that carries no member at all still
   REFUSES by name, because the alternative is publishing "0 engine-supplied
   kills" from an absence.

Determinism: fixed orderings everywhere (manifest order for mutants, sorted run
ids, case order within a suite), no clock, no randomness, no environment lookup.
The prototype used a thread pool for wall-clock and reassembled results in the
fixed order; that is carried, and `E4_WORKERS` changes nothing but the wall
clock.
"""
from __future__ import annotations

import json
import os
from decimal import Decimal, InvalidOperation
from fractions import Fraction

from . import domain
from . import engines
from . import stats

# The RETIRED X1 boundary, as the three numbers the prose used to state.
#
# ROUND-1 FINDING R1-2, and the arm-A reference repair that answered it
# (`design/reference/refA/PACK-CHANGE-001.md`): X1's inexpressibility claim did
# not survive review, the reference was repaired to answer the prose-correct
# `review` on all 72 cells, and the certificate's divergence count over the
# 236,196-cell registered space is now ZERO. `cert_offgold.py`'s own registry of
# exclusion classes is empty for that reason, and `REGISTERED_EXCLUSION_CLASSES`
# below is this module's copy of that fact.
#
# The predicate is KEPT and gates nothing, exactly as the certificate keeps its
# own: it is what makes "the repair moved exactly the cells the retired class
# named" a thing that can be re-measured rather than remembered.
X1_RISK_FLOOR = Decimal("40")      # inclusive
X1_RISK_CEILING = Decimal("70")    # exclusive
X1_SPEND_CAP = Decimal("100000.00")
X1_LOW_COUNTRY = "LOW"

# Section 4's registered exclusion classes, as data. EMPTY since 2026-08-18.
# A class is added by editing this dict with a written reason and nothing else,
# which is the only way one should ever be added; `partition_excluded()` reads
# it and excludes exactly what it names.
REGISTERED_EXCLUSION_CLASSES = {}

# matrix facts member -> (canonical cell key, wire kind). The canonical keys are
# the gold suite's input keys, so one signature reads for gold rows, authored
# matrix cases and Rego input points alike.
VENDOR_MEMBERS = (("riskScore", "risk", "number"),
                  ("requestedSpend", "spend", "number"),
                  ("sanctionsStatus", "sanctions", "string"),
                  ("countryRisk", "country", "string"),
                  ("newVendor", "newVendor", "string"),
                  ("criticalSupplier", "critical", "string"),
                  ("priorEnforcement", "prior", "string"))
EVIDENCE_MEMBERS = (("financial-evidence", "finEvidence"),
                    ("insurance-certificate", "insurance"))


class E4Error(Exception):
    """A refusal in the E4 machinery, with a named code as its first word."""


class MatrixError(E4Error):
    """The AUTHOR's matrix is not a matrixVersion-2 document.

    Distinguished from every other `E4Error` because it is the one refusal in
    this module that is about what the author emitted rather than about the
    apparatus: §1a keeps it in the denominator as a counted authoring outcome,
    and `harness/score.py` maps it onto the registered code. Round-1 finding
    R1-6 was that this class did not exist — `load_matrix()` assumed its way
    through the document and an `AttributeError` invalidated the whole attempt."""


class ExecutionRefusal(E4Error):
    """A pinned engine refused on a FROZEN study artifact.

    Round-1 finding R1-8: a mutant-phase timeout, compile failure or invocation
    failure used to count as a kill, and the same failure against the reference
    used to fail identity and score a correct suite zero. Neither is evidence
    about a suite, so neither is a rate; both raise here and reach the
    `engine-execution-clean` control gate."""


class SurvivorSchemaError(E4Error):
    """§7 delta 1's write-time refusal: a run record that would encode "nothing
    evaluated" and "everything killed" with the same token, or that would be
    written without the vector or without `caseCount`.

    It is an APPARATUS refusal and not an authoring outcome: nothing the author
    emitted can produce it. It means the scorer was about to write a record
    whose schema cannot distinguish two states §5.2 registers as different, and
    §5.9 row 1 is where that lands."""


def _decimal(value):
    """A canonical decimal from a wire value, or None when it is unreadable.

    Every numeric input in this study travels as a DECIMAL STRING (section 2's
    naming appendix), and `Decimal(str(v))` reads an authored JSON number
    without a float round-trip. An unreadable value is None — the same state as
    an omitted member, which is what section 4's input-domain closure requires."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, ArithmeticError):
        return None


def in_x1(signature: dict) -> bool:
    """Section 4's registered X1 exclusion class, as one predicate.

        {new vendor yes; risk in [40, 70); LOW country with spend unreadable,
         or country unreadable with spend <= 100,000.00}

    An unreadable risk is NOT in X1: the class is defined over a risk band, and
    a point with no readable risk is not in a band. That reading is the same one
    `design/gold/check_gold.py` enforces over the gold suite (`i["risk"] is not
    None and 40 <= int(i["risk"]) < 70`), and the two must agree or gold
    contains a row the filter would have excluded."""
    if signature.get("newVendor") != "yes":
        return False
    risk = _decimal(signature.get("risk"))
    if risk is None or not (X1_RISK_FLOOR <= risk < X1_RISK_CEILING):
        return False
    country = signature.get("country")
    spend = _decimal(signature.get("spend"))
    low_country_unreadable_spend = (country == X1_LOW_COUNTRY
                                    and signature.get("spend") is None)
    unreadable_country_small_spend = (country is None and spend is not None
                                      and spend <= X1_SPEND_CAP)
    return low_country_unreadable_spend or unreadable_country_small_spend


def case_signature(facts: dict, evidence: dict) -> dict:
    """The canonical input signature of one authored matrix case."""
    vendor = (facts or {}).get("vendor") or {}
    signature = {}
    for member, cell, _kind in VENDOR_MEMBERS:
        signature[cell] = vendor.get(member)
    for member, cell in EVIDENCE_MEMBERS:
        signature[cell] = (evidence or {}).get(member)
    return signature


def align_expected(expected):
    """`(kind, outcomeId, sorted reasons)` from a matrix case's
    `expectedDisposition`, or None when the case does not carry a readable one.

    This IS the alignment map on the expectation side, and it drops exactly what
    section 5 puts outside every endpoint: `handoff` (state, triggeredBy,
    target) and `trace[]` are never read, so ADR-0025's handoff assertion cannot
    enter an E4 number by accident.

    TOTAL over every JSON value (round-2 R2-6). `reasons` used to be iterated
    with only a falsy guard in front of it, so `"reasons": 1` raised an uncaught
    `TypeError` out of the scorer instead of landing on the registered authoring
    code. Every shape this cannot read now answers `None`, and `load_matrix()`
    refuses the document before this is ever reached with such a value."""
    if not isinstance(expected, dict):
        return None
    kind = expected.get("kind")
    raw_reasons = expected.get("reasons")
    if raw_reasons is None:
        raw_reasons = []
    if not isinstance(raw_reasons, list) \
            or not all(isinstance(reason, str) for reason in raw_reasons):
        return None
    reasons = tuple(sorted(raw_reasons))
    if kind == "outcome":
        outcome_id = expected.get("outcomeId")
        if not isinstance(outcome_id, str):
            return None
        return ("outcome", outcome_id, reasons)
    if kind == "unresolved":
        return ("unresolved", None, reasons)
    return None


# The REGISTERED spelling, and it is a STRING (round-2 finding R2-6).
# `design/prompts/ARM-A-INSTRUCTIONS.md`: "`matrixVersion`: the string `"2"`";
# the arm-A excerpt's own examples and every real pilot matrix
# (`design/pilots/.../arm-A/run-008/secondary.json`) emit `"matrixVersion": "2"`.
# This loader registered the INTEGER 2, so every prompt-conforming matrix was
# refused as `unparseable-artifact` and scored zero — the endpoint was
# unreachable for arm A in exactly the way R1-1's single cut made it unreachable
# for arms B and C, and the tests missed it because they were written against
# the loader rather than against the prompt.
MATRIX_VERSION = "2"
MATRIX_VERSION_MISREAD = 2

# §5's scored surface has no error-class axis, so `expectedErrorClass` is a
# registered expectation form this study cannot score: the case carries no
# readable expectation and fails the identity control, which is what §1a does
# with what the author emitted.
EXPECTATION_FORMS = ("expectedDisposition", "expectedErrorClass")


def _require(condition, message):
    if not condition:
        raise MatrixError("E4-MATRIX-SCHEMA " + message)


def load_matrix(path: str) -> tuple:
    """`(cases, note)`; a case is
    `(id, facts, evidence, expected, readable, signature)`.

    TOTAL matrixVersion-2 SCHEMA VALIDATION (round-1 R1-6). The reviewer's three
    payloads — `[]`, `{"cases": [null]}`, and a `facts.vendor` that is a string —
    are all valid JSON and all used to raise `AttributeError`/`TypeError` out of
    this function, past a caller that caught only `ValueError`, into the outer
    handler that publishes pipeline-invalid and re-raises. §1a registers the
    opposite outcome: unparseable or schema-invalid AUTHOR output is a counted
    authoring outcome that scores zero and stays in the denominator. Every
    author-controlled shape failure is therefore a `MatrixError` here, and the
    outer exception path is left for apparatus defects.

    The line between SCHEMA and READABILITY is drawn where the registration draws
    it. A member of the wrong TYPE is a schema failure and refuses the document.
    A member that is ABSENT, or an `expectedDisposition` whose `kind` is not one
    of the two registered kinds, leaves the case UNREADABLE — which fails the
    identity control, because it is what the author emitted and a suite whose
    cases cannot be read pins nothing."""
    with open(path, "rb") as handle:
        raw = handle.read()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        raise MatrixError("E4-MATRIX-SCHEMA the matrix block is not readable "
                          "JSON (%s)" % type(error).__name__)
    _require(isinstance(document, dict),
             "the matrix is a JSON %s and matrixVersion 2 is an object"
             % type(document).__name__)
    version = document.get("matrixVersion")
    _require(version == MATRIX_VERSION,
             "matrixVersion is %r and this study registers the string %r%s"
             % (version, MATRIX_VERSION,
                " (the JSON number 2 is not the registered spelling; the prompt "
                "and every example emit the string)"
                if version == MATRIX_VERSION_MISREAD else ""))
    raw_cases = document.get("cases")
    _require(isinstance(raw_cases, list),
             "the `cases` member is a JSON %s and matrixVersion 2 registers a "
             "list" % type(raw_cases).__name__)
    cases = []
    for index, case in enumerate(raw_cases):
        _require(isinstance(case, dict),
                 "case %d is a JSON %s and a case is an object"
                 % (index, type(case).__name__))
        case_id = case.get("id")
        _require(case_id is None or isinstance(case_id, str),
                 "case %d carries a non-string id" % index)
        case_id = case_id if isinstance(case_id, str) else "case[%d]" % index
        facts = case.get("facts")
        _require(facts is None or isinstance(facts, dict),
                 "%s carries a `facts` member that is a JSON %s"
                 % (case_id, type(facts).__name__))
        if isinstance(facts, dict):
            vendor = facts.get("vendor")
            _require(vendor is None or isinstance(vendor, dict),
                     "%s carries a `facts.vendor` member that is a JSON %s"
                     % (case_id, type(vendor).__name__))
        evidence = case.get("evidenceAvailability")
        _require(evidence is None or isinstance(evidence, dict),
                 "%s carries an `evidenceAvailability` member that is a JSON %s"
                 % (case_id, type(evidence).__name__))
        expectation = case.get("expectedDisposition")
        _require(expectation is None or isinstance(expectation, dict),
                 "%s carries an `expectedDisposition` member that is a JSON %s"
                 % (case_id, type(expectation).__name__))
        # ROUND-2 R2-6, second half: the enclosing-object check was the whole of
        # the validation, so a nested member of the wrong type walked past it
        # and raised out of `align_expected()`. Every nested member is typed
        # here, and the registered "exactly one of" is enforced: two expectation
        # forms in one case is a contradictory document and refuses, while
        # NEITHER form leaves the case unreadable, which is the line the
        # docstring above draws between a schema failure and an absence.
        _require(not all(form in case for form in EXPECTATION_FORMS),
                 "%s carries both `expectedDisposition` and "
                 "`expectedErrorClass` and the registered matrix row carries "
                 "exactly one of them" % case_id)
        for member in ("expectedErrorClass", "expectedErrorPhase"):
            value = case.get(member)
            _require(value is None or isinstance(value, str),
                     "%s carries a `%s` member that is a JSON %s"
                     % (case_id, member, type(value).__name__))
        if isinstance(expectation, dict):
            _require(isinstance(expectation.get("kind"), str)
                     or expectation.get("kind") is None,
                     "%s carries an `expectedDisposition.kind` that is a JSON %s"
                     % (case_id, type(expectation.get("kind")).__name__))
            reasons = expectation.get("reasons")
            _require(reasons is None
                     or (isinstance(reasons, list)
                         and all(isinstance(reason, str) for reason in reasons)),
                     "%s carries an `expectedDisposition.reasons` that is not a "
                     "list of strings (%r)" % (case_id, reasons))
            outcome_id = expectation.get("outcomeId")
            _require(outcome_id is None or isinstance(outcome_id, str),
                     "%s carries an `expectedDisposition.outcomeId` that is a "
                     "JSON %s" % (case_id, type(outcome_id).__name__))
            handoff = expectation.get("handoff")
            _require(handoff is None or isinstance(handoff, dict),
                     "%s carries an `expectedDisposition.handoff` that is a "
                     "JSON %s" % (case_id, type(handoff).__name__))
        target = case.get("expectedHandoffTarget")
        _require(target is None or isinstance(target, dict),
                 "%s carries an `expectedHandoffTarget` that is a JSON %s and "
                 "the registered member is an object or the literal null"
                 % (case_id, type(target).__name__))
        expected = align_expected(expectation)
        readable = isinstance(facts, dict) and expected is not None
        facts = facts if isinstance(facts, dict) else {}
        evidence = evidence if isinstance(evidence, dict) else {}
        cases.append((case_id, facts, evidence, expected, readable,
                      case_signature(facts, evidence)))
    return cases, {"matrixVersion": version, "caseCount": len(cases)}


def matrix_domain_signature(facts: dict, evidence: dict) -> dict:
    """One matrix case's input point in `domain.py`'s canonical shape, with
    every member the registered document does not carry recorded."""
    vendor = (facts or {}).get("vendor")
    extra = ["facts.%s" % name for name in (facts or {}) if name != "vendor"]
    return domain.signature_from_documents(vendor, evidence, extra)


def partition_excluded(cases: list) -> tuple:
    """`(scored cases, excluded case ids)` over `REGISTERED_EXCLUSION_CLASSES`.

    Applied ONCE and in one place, so identity and kill see the same case set by
    construction. The registry is EMPTY since X1's retirement (module head), so
    this excludes nothing today.

    ROUND-3 FINDING R3-9. This used to say the empty result was "published as
    the zero it is", and §4 says the opposite in terms: "There is no exclusion
    class, no per-case X1 filter and no per-run excluded-case count." The zero
    is no longer published anywhere — `harness/score.py` refuses outright if
    this ever returns a non-empty exclusion list, because a class the
    registration does not carry must not decide which cases are scored. The
    function survives as the single application point a future registered class
    would have to go through."""
    scored, excluded = [], []
    for case in cases:
        member = next((name for name, predicate
                       in sorted(REGISTERED_EXCLUSION_CLASSES.items())
                       if predicate(case[5])), None)
        if member is None:
            scored.append(case)
        else:
            excluded.append(case[0])
    return scored, excluded


# --- the mutant sets and the pairing ---------------------------------------


def load_mutants(jps_manifest_path: str, rego_manifest_path: str,
                 jps_dir: str, rego_dir: str) -> dict:
    """`{'jps': [record...], 'rego': [record...]}` in MANIFEST order, valid only.

    Changed from the prototype: the manifest paths and the mutant directories
    are ARGUMENTS rather than module constants pointing into `design/`. The
    frozen manifests are `mutants/MANIFEST-jps.json` and
    `mutants/MANIFEST-rego.json` (the registry's `mutantManifests` pin), and a
    scorer that reads its mutants from the design tree would score the study
    against unfrozen bytes."""
    records = {}
    with open(jps_manifest_path, "rb") as handle:
        jps_manifest = json.loads(handle.read().decode("utf-8"))
    jps = []
    for mutant in jps_manifest:
        if mutant.get("validates") is not True:
            continue
        witnesses = sorted(mutant.get("witnessSet") or [])
        jps.append({"id": mutant["id"],
                    "path": os.path.join(jps_dir, mutant["id"] + ".json"),
                    "witnessSet": witnesses,
                    "witnessKey": tuple(witnesses),
                    "notAdequate": bool(mutant.get("notAdequate")),
                    "class": mutant.get("class"),
                    "engineSuppliedKill": mutant.get("engineSuppliedKill")})
    with open(rego_manifest_path, "rb") as handle:
        rego_manifest = json.loads(handle.read().decode("utf-8"))
    rego = []
    for mutant in rego_manifest["mutants"]:
        if mutant.get("status") != "valid":
            continue
        witnesses = sorted(mutant.get("witnessSet") or [])
        rego.append({"id": mutant["id"],
                     "path": os.path.join(rego_dir, mutant["file"]),
                     "witnessSet": witnesses,
                     "witnessKey": tuple(witnesses),
                     "notAdequate": bool(mutant.get("notAdequate")),
                     "class": mutant.get("mutationClass"),
                     "engineSuppliedKill": mutant.get("engineSuppliedKill")})
    records["jps"], records["rego"] = jps, rego
    for language, entries in records.items():
        for entry in entries:
            if not os.path.exists(entry["path"]):
                raise E4Error("E4-MISSING-MUTANT %s %s has no file"
                              % (language, entry["id"]))
            # The empty-witness <-> notAdequate identity the pairing rule leans
            # on. Asserted rather than assumed: if it ever fails, the degenerate
            # group stops being the notAdequate set and the paired subset
            # silently changes size.
            if entry["notAdequate"] != (len(entry["witnessSet"]) == 0):
                raise E4Error(
                    "E4-WITNESS-DISAGREEMENT %s %s: notAdequate=%s but witness "
                    "set size %d" % (language, entry["id"], entry["notAdequate"],
                                     len(entry["witnessSet"])))
    return records


def build_pairing(mutants: dict) -> tuple:
    """Section 4's registered pairing rule: IDENTICAL SORTED WITNESS SETS.

    Pairing is a grouping by witness-set key and is therefore many-to-many; the
    whole grouping is the published pairing table. The empty witness set is a
    key like any other, and pairing all empty-witness JPS mutants with all
    empty-witness Rego mutants would pair on the ABSENCE of a discriminating
    gold row rather than on a shared one — so that group is emitted flagged and
    excluded from the paired subsets ("the empty witness set is degenerate and
    never pairs")."""
    groups = {}
    for language in ("jps", "rego"):
        for record in mutants[language]:
            group = groups.setdefault(record["witnessKey"],
                                      {"jps": [], "rego": []})
            group[language].append(record["id"])
    table = []
    for key in sorted(groups, key=lambda k: (len(k), k)):
        group = groups[key]
        paired = bool(group["jps"]) and bool(group["rego"])
        degenerate = paired and len(key) == 0
        table.append({
            "witnessSet": list(key),
            "witnessCount": len(key),
            "jpsMutants": group["jps"],
            "regoMutants": group["rego"],
            "jpsCount": len(group["jps"]),
            "regoCount": len(group["rego"]),
            "paired": paired,
            "notAdequate": len(key) == 0,
            "degenerate": degenerate,
            "countedInPairedSubset": paired and not degenerate,
        })
    paired_ids = {"jps": set(), "rego": set()}
    for row in table:
        if row["countedInPairedSubset"]:
            paired_ids["jps"].update(row["jpsMutants"])
            paired_ids["rego"].update(row["regoMutants"])
    return table, paired_ids


def unpairable(mutants: dict, paired_ids: dict) -> dict:
    """The counts section 4 publishes as "a finding about the defect spaces"."""
    return {language: sorted(record["id"] for record in mutants[language]
                             if not record["notAdequate"]
                             and record["id"] not in paired_ids[language])
            for language in ("jps", "rego")}


def engine_supplied_ids(mutants: dict, language: str) -> list:
    """Section 4's engine-supplied-kill list, from the manifest.

    Section 4 says those mutants are "listed in the registries", and the
    registered report is "both included and excluded". The marking used to exist
    only as a `conflict-only` glyph in `design/mutants/ADEQUACY.md`'s prose
    table; both manifests carry it as a member now (SCAFFOLD item S9), so this
    reads frozen bytes rather than parsing a registered number out of prose.

    A language whose manifest carries the member on NO mutant still refuses by
    name. The distinction is the point: a manifest where every mutant records
    `engineSuppliedKill: false` is the registered statement that the arm has an
    EMPTY engine-supplied class — which is arm B's, and which
    `design/mutants/refB/MANIFEST.json`'s `engineSuppliedKillClass` states with
    its reason — while a manifest with no member at all says nothing, and
    returning an empty list from it would publish "0 engine-supplied kills" and
    satisfy section 4 in form only.

    ROUND-2 FINDING R2-10, and the refusal was not fail-closed. It fired only
    when EVERY record was unmarked, so a manifest marking one mutant and leaving
    the next silent was accepted and published a class computed from a partial
    census — the same "0 from an absence" this refusal exists to prevent, one
    record at a time. And the marking was read for TRUTHINESS, so the string
    `"false"` counted a mutant INTO the class. Every valid record must now carry
    a real Boolean: `type(...) is bool`, which admits neither `None`, nor `0`/`1`,
    nor `"false"`, and the refusal names the records that do not."""
    entries = mutants[language]
    unmarked = [record["id"] for record in entries
                if type(record.get("engineSuppliedKill")) is not bool]
    # SILENCE and WRONG TYPE are different refusals. A manifest where no record
    # carries the member at all has said nothing (the round-1 refusal); one that
    # carries values of the wrong type has said something unreadable, and naming
    # it "carries no member" would send a reader to the wrong file.
    if all(record.get("engineSuppliedKill") is None for record in entries):
        raise E4Error(
            "E4-ENGINE-SUPPLIED-UNREGISTERED the %s mutant manifest carries no "
            "engineSuppliedKill member, so section 4's 'reported both included "
            "and excluded' cannot be computed from frozen bytes; the marking is "
            "prose in design/mutants/ADEQUACY.md and must become a manifest "
            "member before the freeze (harness/SCAFFOLD.md item S9)" % language)
    if unmarked:
        raise E4Error(
            "E4-ENGINE-SUPPLIED-INCOMPLETE %d of the %d valid %s mutants carry "
            "no BOOLEAN engineSuppliedKill member (%s%s): section 4's class is "
            "a census over the whole set, and a class computed from a partial "
            "or mistyped census is the same '0 from an absence' the refusal "
            "above exists to prevent"
            % (len(unmarked), len(entries), language,
               ", ".join(unmarked[:5]), "…" if len(unmarked) > 5 else ""))
    return sorted(record["id"] for record in entries
                  if record["engineSuppliedKill"])


# --- the identity control and kill ------------------------------------------


KILLED = "killed"
SURVIVED = "survived"
REFUSED = "refused"
# §7 delta 1. The fourth outcome, which 019's schema had no token for: the
# mutant was never executed against this suite. `survivorsPaired` alone could
# not say it — an unrun mutant is absent from the survivor list exactly as a
# killed one is — and that is the collision the delta names.
NOT_EVALUATED = "not-evaluated"
MUTANT_OUTCOMES = (KILLED, SURVIVED, REFUSED, NOT_EVALUATED)

# §5.1 and §1.2 (M-13): TWO NAMED RELATIONS, never one field with two meanings
# (§7 delta 4). `referenceIdentity` is the suite against the arm's frozen
# REFERENCE and is what the per-protocol population is defined by;
# `ownPolicyIdentity` is the same suite against the run's OWN authored policy,
# is new in 020, is published per run and per arm, and gates nothing. A single
# `identityPass` field carrying whichever was last computed is the defect this
# tuple exists to make impossible: the scorer writes both members or neither.
REFERENCE_IDENTITY = "referenceIdentity"
OWN_POLICY_IDENTITY = "ownPolicyIdentity"
IDENTITY_RELATIONS = (REFERENCE_IDENTITY, OWN_POLICY_IDENTITY)

# The identity-failure category §5's E3 taxonomy publishes for a case that left
# the registered input domain. Named once so the scorer, the taxonomy and the
# tests cannot hold three spellings of it.
OUT_OF_DOMAIN = "out-of-domain-case"


def rego_case_signatures(tools: engines.Toolchain, suite_path: str,
                         workdir: str, policy_path: str = None) -> list:
    """`[(case name, signature)]` for an `opa test` file — the B/C half of
    round-1 R1-3's symmetric enumeration.

    Arms B and C used to hand the scorer an opaque file and receive no
    case-level validation of any kind, while arm A's matrix was parsed and
    filtered. The suite's own SYNTAX TREE closes that: `opa parse --format json`
    is the pinned binary's reading of the file, and every `with input as
    <literal>` term in it is a case input this study can check against the same
    registered domain arm A's cases are checked against.

    TWO MODES, because real suites use both. Literal `with input as {…}` terms
    are read straight off the tree; a table-driven suite — which is what the
    pilot's own arm-B and arm-C runs wrote, with named evidence constants and a
    `make_input()` helper over `object.union` — carries a ref there instead, and
    that ref is resolved against the suite's own package document, EVALUATED with
    the pinned binary, plus the rule body's own `:=` and `some … in` bindings.
    Both readings are the pinned toolchain's; neither is a re-implementation of
    Rego and neither is a guess.

    ROUND-2 FINDING R2-4. The refusal used to be "no input-shaped literal exists
    ANYWHERE in the file", which is a statement about the file and not about the
    terms: the reviewer's probe carried one unrelated valid `decoy` literal,
    built its real input inside a rule body, and had the decoy satisfy the check
    while the tested point — `newVendor: 7` — was never enumerated and never
    domain-validated. The enumeration is per term now, so EVERY `with input as`
    term must resolve; one that does not is this refusal by name, whatever else
    the file contains.

    A file the pinned parser refuses, or a suite with a `with input as` term that
    cannot be resolved either way, is a `MatrixError` — the registered authoring
    outcome — and never a silent pass.

    ROUND-2 FINDING R2-1: `MatrixError` now means ONLY what its docstring says,
    "about what the author emitted". `opa_parse()` and `opa_eval_document()`
    raise `engines.EngineError` on a no-answer, and that exception passes
    THROUGH this function to `score_run()`'s apparatus handler. Before the
    repair a `parse` timeout arrived here as `code == 124` and was filed as the
    authoring code `unparseable-artifact` — a statement about the author made
    out of an invocation that never happened."""
    code, raw = engines.opa_parse(tools, suite_path, workdir)
    if code != 0:
        raise MatrixError(
            "E4-MATRIX-SCHEMA the pinned parser refuses the suite file "
            "(`opa parse` exit %d), so its cases cannot be enumerated and its "
            "input points cannot be validated against the registered domain"
            % code)
    try:
        document = domain.parse_tree(raw)
        unresolved, cases = domain.cases_from_tree(document)
        if unresolved:
            # The table-driven mode. Evaluate the suite's own package with the
            # pinned binary: that resolves the named constants and helper
            # functions real suites build their input points out of, and gives
            # the NAME MAP the per-term resolution needs.
            data_paths = [suite_path] + ([policy_path] if policy_path else [])
            eval_code, eval_raw = engines.opa_eval_document(
                tools, data_paths, domain.package_path(document), workdir)
            if eval_code == 0:
                resolved = domain.package_document(eval_raw)
                names = resolved if isinstance(resolved, dict) else None
                unresolved, cases = domain.cases_from_tree(document, names)
    except domain.DomainError as error:
        raise MatrixError("E4-MATRIX-SCHEMA %s" % error)
    except ValueError as error:
        raise MatrixError("E4-MATRIX-SCHEMA the resolved suite document is not "
                          "readable JSON (%s)" % type(error).__name__)
    if unresolved:
        raise MatrixError(
            "E4-MATRIX-SCHEMA %d `with input as` term(s) name an input point "
            "that neither the suite's syntax tree nor its resolved package "
            "document holds (%s): those case inputs cannot be validated against "
            "the registered domain, and an unrelated literal elsewhere in the "
            "file does not stand in for them"
            % (len(unresolved), "; ".join(sorted(set(unresolved))[:3])))
    return [("case[%d]" % order, signature)
            for order, (_index, signature) in enumerate(cases)]


def domain_failures(named_signatures, wire: str) -> list:
    """Every case whose input point leaves the registered domain, as identity
    failures in the shape `identity_arm_a()` returns.

    THE SAME CHECK IN ALL THREE ARMS, applied BEFORE identity and before any
    mutation execution (round-1 R1-3). A case outside the registered space is
    one on which the off-gold certificate establishes nothing — the labelled
    supplementary stratum measured 18,954 reference divergences out there — so a
    suite that asserts about it is asserting about behaviour this study's oracle
    does not fix. It is what the author emitted, so §5's identity control is
    where it lands: the run stays in the E4 denominator as not-high-kill, the
    failure is reported per arm as a first-class rate, and E3 counts it under
    `out-of-domain-case`. It is never silently dropped and never silently
    scored."""
    failures = []
    for name, signature in named_signatures:
        problems = domain.domain_problems(signature, wire)
        if problems:
            failures.append({"case": name, "expected": "<in registered domain>",
                             "got": OUT_OF_DOMAIN, "problems": problems})
    return failures


def identity_arm_a(tools: engines.Toolchain, reference_pack: str, cases: list,
                   workdir: str) -> tuple:
    """Section 5's identity control for arm A: every scored case must agree with
    the arm's own UNMUTATED reference on the scored surface.

    A case with no readable facts or expectation is a failure, not a skip: it is
    what the author emitted, and a suite whose cases cannot be read pins nothing.

    A REFERENCE that refuses is not a suite failure at all (round-1 R1-8). Every
    case reaching here has already been validated against the registered input
    domain (`domain.py`), and the off-gold certificate establishes that the
    reference answers every point of that domain — so a `ROW-ERROR` here is the
    apparatus, and zero-scoring a correct suite on it is the attribution error
    the finding names. It raises."""
    failures = []
    for case_id, facts, evidence, expected, readable, _signature in cases:
        if not readable:
            failures.append({"case": case_id, "expected": "<unreadable>",
                             "got": "<not-run>",
                             "reason": "case carries no facts object or no "
                                       "readable expectedDisposition"})
            continue
        observed = engines.eval_pack(tools, reference_pack, facts, evidence,
                                     workdir)
        if observed[0] == "ROW-ERROR":
            raise ExecutionRefusal(
                "E4-IDENTITY-ENGINE-REFUSED the arm-A reference refused on the "
                "in-domain case %s with %s: the identity control cannot be "
                "decided and a suite is not scored zero for an engine refusal"
                % (case_id, engines.scope_str(observed)))
        if observed != expected:
            failures.append({"case": case_id,
                             "expected": engines.scope_str(expected),
                             "got": engines.scope_str(observed)})
    return not failures, failures


def kill_arm_a(tools: engines.Toolchain, mutant_path: str, cases: list,
               workdir: str) -> tuple:
    """`(outcome, detail)` — `killed`/`survived`/`refused`.

    Kill is "at least one scored case disagrees on the mutant" (section 5), so
    the scan short-circuits at the first disagreement and records which case it
    was — the diagnostic E3 reads.

    A REFUSAL IS NOT A KILL (round-1 R1-8). The prototype counted any
    disagreement, `ROW-ERROR` included, so an engine timeout or a non-JSON
    payload on the mutant side made the suite look as if it had distinguished the
    mutant. Every mutant in the frozen manifests validated (`load_mutants()`
    keeps only `validates: true`), so a `ROW-ERROR` here is evidence about the
    apparatus and the mutant is scored neither way; the run's refusal list and
    the `engine-execution-clean` control gate carry it."""
    for case_id, facts, evidence, expected, readable, _signature in cases:
        if not readable:
            continue
        observed = engines.eval_pack(tools, mutant_path, facts, evidence,
                                     workdir)
        if observed[0] == "ROW-ERROR":
            return REFUSED, {"case": case_id,
                             "got": engines.scope_str(observed)}
        if observed != expected:
            return KILLED, {"case": case_id}
    return SURVIVED, {}


def identity_arm_rego(tools: engines.Toolchain, reference_policy: str,
                      suite_path: str, workdir: str) -> tuple:
    """Section 5's identity control for arms B/C, from the RESULT DOCUMENT.

    `pass` is the control held; `failed` is a real identity failure — the suite
    asserts something the reference does not do. Every other status is the
    apparatus (`engines.TEST_SUITE_STATUSES` is the two that are not) and
    raises, because `opa test` exiting nonzero because it could not compile is
    not a suite that failed to pin its reference down."""
    record = engines.opa_test(tools, reference_policy, suite_path, workdir)
    if record["status"] not in engines.TEST_SUITE_STATUSES:
        raise ExecutionRefusal(
            "E4-IDENTITY-ENGINE-REFUSED `opa test` against the arm's reference "
            "returned %s (exit %s): the identity control cannot be decided and "
            "a suite is not scored zero for an invocation failure"
            % (record["status"], record["exitCode"]))
    return record["status"] == engines.TEST_PASS, record


def own_policy_identity(tools: engines.Toolchain, arm: str, own_policy,
                        cases, suite_path: str, workdir: str) -> dict:
    """E6 (§5.1, §1.2's M-13, §7 delta 4): the run's authored SUITE against the
    run's OWN authored POLICY — one extra engine invocation per admitted run.

    THE SECOND NAMED RELATION, and it is named. `referenceIdentity` asks whether
    the suite pins the frozen reference down; this asks whether the suite passes
    against the artifact its own author wrote. They answer different questions
    about different artifacts, and 019 had only the first — so the population
    "runs whose suite is consistent with their own policy" was invisible. The
    two are separate members of the run record, computed by separate functions,
    and `IDENTITY_RELATIONS` names both so a reader of the record can never be
    reading one under the other's name.

    **It gates nothing** (§5.1: "Published per run and per arm; gates nothing;
    conditions R1's construct statement"). What it DOES reach is §6's
    `engine-execution-clean` control gate: this invocation is a scored engine
    invocation of the attempt, so an engine that refused here is an apparatus
    failure exactly as it is anywhere else, and `ExecutionRefusal` carries it to
    the same gate rather than being swallowed into a `false`.

    The returned block always carries `relation`, so a record written to disk
    names which relation produced it."""
    block = {"relation": OWN_POLICY_IDENTITY, "arm": arm,
             "gates": "nothing (§5.1: published per run and per arm; "
                      "conditions R1's construct statement)"}
    if arm == "A":
        failures = []
        for case_id, facts, evidence, expected, readable, _sig in cases:
            if not readable:
                failures.append({"case": case_id, "expected": "<unreadable>",
                                 "got": "<not-run>"})
                continue
            observed = engines.eval_pack(tools, own_policy, facts, evidence,
                                         workdir)
            if observed[0] == "ROW-ERROR":
                raise ExecutionRefusal(
                    "E6-OWN-POLICY-ENGINE-REFUSED the run's own authored pack "
                    "refused on the in-domain case %s with %s: §6's "
                    "engine-execution-clean gate covers E6's extra invocation "
                    "too, and a refusal is neither a pass nor a failure"
                    % (case_id, engines.scope_str(observed)))
            if observed != expected:
                failures.append({"case": case_id,
                                 "expected": engines.scope_str(expected),
                                 "got": engines.scope_str(observed)})
        block["pass"] = not failures
        block["failures"] = failures[:20]
        block["failureCount"] = len(failures)
        return block
    record = engines.opa_test(tools, own_policy, suite_path, workdir)
    if record["status"] not in engines.TEST_SUITE_STATUSES:
        raise ExecutionRefusal(
            "E6-OWN-POLICY-ENGINE-REFUSED `opa test` against the run's own "
            "authored policy returned %s (exit %s): §6's "
            "engine-execution-clean gate covers E6's extra invocation too"
            % (record["status"], record["exitCode"]))
    block["pass"] = record["status"] == engines.TEST_PASS
    block["failures"] = [] if block["pass"] else [record]
    block["failureCount"] = 0 if block["pass"] else 1
    return block


def kill_arm_rego(tools: engines.Toolchain, mutant_path: str, suite_path: str,
                  workdir: str) -> tuple:
    """`(outcome, record)` — `killed`/`survived`/`refused`, from the RESULT
    DOCUMENT rather than from the exit status (round-1 R1-8).

    Section 5 registers the kill as "`opa test` nonzero with class recorded",
    and nonzero was the defect: at v1.19.0 a compile failure, a load failure and
    the harness's own timeout are all nonzero, so every one of them killed every
    mutant it touched. An ASSERTION FAILURE is the kill; a test that ERRORED
    never decided; an invocation that never ran the tests is not evidence about
    the suite at all."""
    record = engines.opa_test(tools, mutant_path, suite_path, workdir)
    if record["status"] == engines.TEST_FAILED:
        return KILLED, record
    if record["status"] == engines.TEST_PASS:
        return SURVIVED, record
    return REFUSED, record


# --- the run-level endpoint -------------------------------------------------


def kill_rates(kill_of: dict, mutants: list, paired_ids: set,
               engine_supplied=()) -> dict:
    """The kill counts one suite produces, over named denominators, WITH the
    explicit per-mutant survivor vector §5.1 registers as a day-one requirement.

    `killedPaired`/`paired` is the pair the family scorer's native-denominator
    level reads; the others are R2's failure map. Each carries its denominator's
    name, so no reader can mistake the own-language rate for the cross-arm one.

    `engine_supplied` is section 4's registered list of mutants whose kills are
    achievable only through the engine's structural conflict detection. Section 4
    registers them "reported both included and excluded", so the paired subset is
    split here — once, at the only place that knows which mutant each kill came
    from — rather than reconstructed later from an aggregate.

    **THE SURVIVOR VECTOR (§5.1, §5.2 Fact 1, §7 delta 1).** `survivorVector` is
    one entry per paired-adequate mutant, in manifest order, each carrying that
    mutant's own outcome — `killed`, `survived`, `refused` or `not-evaluated`.
    019 published `survivorsPaired` alone, which is the set of SURVIVORS and
    therefore empty in two structurally different states: a suite that killed
    everything, and a suite that was never run against anything. Two arm-A runs
    of 019 (`run-025`, `run-046`) were in the second state and read as the first,
    and correcting that single collision moved 019's group-level ITT A−C from
    +0.19112 to +0.13849. The vector is total over the paired subset, so the two
    states differ in the bytes and not in an inference from them, and
    `evaluatedPaired` names how many mutants the suite was actually asked about.
    `survivorsPaired` is retained beside it as a derived convenience and is
    never the only record."""
    supplied = set(engine_supplied or ())
    adequate = [record for record in mutants if not record["notAdequate"]]
    not_adequate = [record for record in mutants if record["notAdequate"]]
    paired_adequate = [record for record in adequate
                       if record["id"] in paired_ids]
    excluded = [record for record in paired_adequate
                if record["id"] not in supplied]
    listed = [record for record in paired_adequate
              if record["id"] in supplied]
    def killed(subset):
        return sum(1 for record in subset if kill_of.get(record["id"]) == KILLED)
    def refused(subset):
        return [record["id"] for record in subset
                if kill_of.get(record["id"]) == REFUSED]
    vector = [{"id": record["id"],
               "outcome": kill_of.get(record["id"], NOT_EVALUATED),
               "engineSupplied": record["id"] in supplied}
              for record in paired_adequate]
    evaluated = sum(1 for entry in vector if entry["outcome"] != NOT_EVALUATED)
    return {
        "killedAdequate": killed(adequate),
        "adequate": len(adequate),
        "killedPaired": killed(paired_adequate),
        "paired": len(paired_adequate),
        # Section 4, "reported both included and excluded": the same paired
        # subset with the registered engine-supplied mutants taken out, and the
        # engine-supplied members on their own.
        "killedPairedExcludingEngineSupplied": killed(excluded),
        "pairedExcludingEngineSupplied": len(excluded),
        "killedEngineSupplied": killed(listed),
        "engineSupplied": len(listed),
        "killedNotAdequate": killed(not_adequate),
        "notAdequate": len(not_adequate),
        # §7 delta 1: the vector is the record; the survivor LIST is derived
        # from it and published beside it, never instead of it.
        "survivorVector": vector,
        "evaluatedPaired": evaluated,
        "survivorsPaired": [entry["id"] for entry in vector
                            if entry["outcome"] == SURVIVED],
        # Round-1 R1-8: a mutant the engine refused on is scored NEITHER way.
        # It is not a kill (an apparatus failure is not a suite distinguishing a
        # mutant) and not a survivor (nothing was asked), it stays in the
        # denominator so no refusal can inflate a rate by shrinking it, and the
        # `engine-execution-clean` control gate reads the list.
        "refusedPaired": refused(paired_adequate),
        "refusedAll": refused(mutants),
    }


def require_survivor_schema(run: dict) -> dict:
    """§7 delta 1's WRITE-TIME refusal, and the only place a run record is
    allowed to become bytes.

    Three conditions, each of which 019's schema permitted:

    1. **The token collision.** `survivorsPaired: []` with `killedPaired: 0`
       over a non-empty paired denominator is refused. Read naively that record
       says "no survivors, therefore everything was killed"; it is emitted by a
       run that killed nothing because nothing was ever executed. It is refused
       rather than repaired, because the two states are distinguishable only if
       the writer had the vector — and if it had the vector it can write it.
    2. **The vector is total.** A `kill` block whose `survivorVector` is absent,
       or does not cover exactly the paired-adequate denominator, is refused:
       the vector is the schema, not an annotation on it.
    3. **`caseCount` for every admitted run with a suite** (§5.2's pinned
       definition 4). 019 emitted six runs carrying a `kill` block with neither
       `survivorsPaired` nor `caseCount` — B run-026/027/032/036, C run-035/050,
       arm A zero, exactly the same six runs under both defects — and the ANCOVA
       members are undefined for a unit with no covariate. A suite that parses
       to no cases has `caseCount` 0, which is a number; an absent member is not.

    Returns the run so a caller can write `require_survivor_schema(run)` at the
    point of the write and have no unchecked path around it."""
    kill = run.get("kill")
    if kill is None:
        return run
    paired = kill.get("paired")
    if not isinstance(paired, int):
        raise SurvivorSchemaError(
            "E4-SURVIVOR-SCHEMA run %s carries a kill block with no integer "
            "paired denominator: the denominator names what the vector is over"
            % run.get("run"))
    vector = kill.get("survivorVector")
    if not isinstance(vector, list) or len(vector) != paired:
        raise SurvivorSchemaError(
            "E4-SURVIVOR-SCHEMA run %s carries a kill block over %d paired "
            "adequate mutants and a survivor vector of %s entries: §5.1 "
            "registers an EXPLICIT per-mutant survivor vector for every "
            "admitted run, so the vector is total over the denominator or the "
            "record is not written"
            % (run.get("run"), paired,
               "no" if not isinstance(vector, list) else len(vector)))
    outcomes = {entry.get("outcome") for entry in vector}
    unregistered = sorted(outcome for outcome in outcomes
                          if outcome not in MUTANT_OUTCOMES)
    if unregistered:
        raise SurvivorSchemaError(
            "E4-SURVIVOR-SCHEMA run %s carries the mutant outcome(s) %s and the "
            "registered vocabulary is %s"
            % (run.get("run"), ", ".join(map(repr, unregistered)),
               ", ".join(MUTANT_OUTCOMES)))
    # ROUND-1 FINDING R1-2. The old guard here refused on the two OBSOLETE
    # aggregates alone (`survivorsPaired` and `killedPaired` both empty), which
    # is exactly the state `kill_rates({})` emits for the REGISTERED
    # nothing-was-evaluated record — the most common production state (no
    # suite, no cases, out-of-domain, identity failure) — so one such admitted
    # run hard-aborted the whole attempt. By this point conditions above have
    # established the vector is present, total and registered, so the state is
    # not ambiguous: the VECTOR is authoritative. What refuses now is genuine
    # inconsistency between the vector and the aggregates, in either direction.
    derived_killed = sum(1 for entry in vector
                         if entry.get("outcome") == KILLED)
    derived_survivors = [entry.get("id") for entry in vector
                         if entry.get("outcome") == SURVIVED]
    derived_evaluated = sum(1 for entry in vector
                            if entry.get("outcome") != NOT_EVALUATED)
    if kill.get("killedPaired") != derived_killed:
        raise SurvivorSchemaError(
            "E4-SURVIVOR-EMPTY run %s records killedPaired %s and its own "
            "vector derives %d: the aggregates are summaries of the vector and "
            "may not disagree with it (§5.1; R1-2)"
            % (run.get("run"), kill.get("killedPaired"), derived_killed))
    if sorted(kill.get("survivorsPaired") or []) != sorted(
            name for name in derived_survivors if name is not None):
        raise SurvivorSchemaError(
            "E4-SURVIVOR-EMPTY run %s records a survivorsPaired list that is "
            "not the vector's SURVIVED entries: the aggregates are summaries "
            "of the vector and may not disagree with it (§5.1; R1-2)"
            % (run.get("run"),))
    if kill.get("evaluatedPaired") != derived_evaluated:
        raise SurvivorSchemaError(
            "E4-SURVIVOR-EMPTY run %s records evaluatedPaired %s and its own "
            "vector derives %d — the genuinely impossible state the old "
            "aggregate guard was reaching for: something claims to have been "
            "evaluated and the vector records no outcome for it, or the "
            "reverse (R1-2)"
            % (run.get("run"), kill.get("evaluatedPaired"),
               derived_evaluated))
    if run.get("admitted") and run.get("suitePresent") \
            and not isinstance(run.get("caseCount"), int):
        raise SurvivorSchemaError(
            "E4-CASECOUNT-ABSENT run %s is admitted and carries a suite, and "
            "its caseCount is %r: §5.2 pins caseCount = 0 for a suite that "
            "parses to no cases, so an admitted run with a suite always carries "
            "the number and never an absence"
            % (run.get("run"), run.get("caseCount")))
    return run


# --- the per-language denominators and the shared-class lattice --------------
# §7 delta 2: KEPT (each language's paired-adequate denominator and lattice stay
# separate), with no threshold on top of them.

def paired_denominators(paired_ids: dict) -> dict:
    """Each language's paired-adequate denominator and lattice, side by side.

    ROUND-1 FINDING R1-1 of Study 019, and this is the half of the answer 020
    keeps. The defect was not that a threshold existed; it was that ONE number
    derived from the JPS subset was applied to a Rego run whose subset was
    smaller. The denominators are per language here, they are never combined,
    and there is no single number derived from either of them — so the shape of
    R1-1 has nowhere to recur.

    `lattice` is the spacing of the level's own value set at that denominator
    (1/69 = 0.014493 for JPS at 019's corpus), which §5.3 needs in order to say
    "the outcome is bounded and lattice-valued" as arithmetic rather than as an
    adjective."""
    block = {}
    for language in sorted(paired_ids):
        size = len(paired_ids[language])
        block[language] = {
            "language": language,
            "pairedAdequateMutants": size,
            "lattice": float(Fraction(1, size)) if size else None,
            "statement": "arm language %s scores over its OWN %d paired "
                         "adequate mutants; no quantity derived from another "
                         "language's denominator is applied to it"
                         % (language, size),
        }
    return block


def shared_classes(pairing: list) -> dict:
    """§5.1's shared witness classes — the units the coverage set is over.

    A class is one witness-set group that is paired and non-degenerate; the
    empty witness set never pairs (`build_pairing()`). The per-class member
    counts are published PER LANGUAGE and unequal counts are counted, because
    §5.2's Fact 2 makes that imbalance the reason the native-mutant level is
    structurally biased between languages — 20 of 33 classes unequal on 019's
    corpus — and the imbalance table is a mandatory publication (§5.8)."""
    classes = []
    for row in pairing:
        if not row["countedInPairedSubset"]:
            continue
        classes.append({
            "classId": "|".join(row["witnessSet"]) or "<empty>",
            "witnessSet": list(row["witnessSet"]),
            "jpsMutants": list(row["jpsMutants"]),
            "regoMutants": list(row["regoMutants"]),
            "jpsCount": row["jpsCount"],
            "regoCount": row["regoCount"],
            "equalMembership": row["jpsCount"] == row["regoCount"],
        })
    unequal = [entry["classId"] for entry in classes
               if not entry["equalMembership"]]
    return {
        "classes": classes,
        "count": len(classes),
        "unequalMembership": unequal,
        "unequalCount": len(unequal),
        "note": "§5.1: the coverage set S is over these classes. §5.2 Fact 2: "
                "unequal per-class member counts are what make the native "
                "mutant level structurally biased between languages, so the "
                "count is published whether or not any member reads it.",
    }


def coverage_classes(kill_of: dict, classes: list, language: str) -> dict:
    """§5.2's pinned COVERAGE RULE: a run covers class g iff its suite kills
    **all** of g's members in the run's own language.

    The any/all question is not a live choice and is not registered as one:
    §5.2 records `gall == gany` in 88 of 88 checkable runs and states the
    structural condition under which that holds. BOTH are computed here anyway
    and the disagreement is published, because an equivalence registered as a
    stated fact is a fact that has to stay checkable on 020's own batch.

    A class none of whose members was evaluated is NOT covered and is reported
    separately from a class that was evaluated and survived — the same
    distinction `require_survivor_schema()` enforces one level down."""
    key = "jpsMutants" if language == "jps" else "regoMutants"
    covered_all, covered_any, unevaluated = [], [], []
    for entry in classes:
        members = entry[key]
        if not members:
            continue
        outcomes = [kill_of.get(member, NOT_EVALUATED) for member in members]
        if all(outcome == NOT_EVALUATED for outcome in outcomes):
            unevaluated.append(entry["classId"])
            continue
        if all(outcome == KILLED for outcome in outcomes):
            covered_all.append(entry["classId"])
        if any(outcome == KILLED for outcome in outcomes):
            covered_any.append(entry["classId"])
    return {
        "language": language,
        "coverageRule": "a run covers class g iff its suite kills ALL of g's "
                        "members in the run's own language (§5.2)",
        "covered": sorted(covered_all),
        "coveredCount": len(covered_all),
        "coveredAny": sorted(covered_any),
        "coveredAnyCount": len(covered_any),
        "allEqualsAny": sorted(covered_all) == sorted(covered_any),
        "unevaluatedClasses": sorted(unevaluated),
        "classCount": len(classes),
    }
