"""Protocol-integrity suite: vocabulary sync, registry schema, manifests, refusals.

Per-code reachability and first-failure ordering live in `test_reachability.py`; this
file owns everything that must hold before any cell runs.

Nothing here adjudicates a reviewer-holdout fixture. The holdout may be *constructed*
before the freeze — the scorer's gate requires the fixtures to exist — but no layer
verdict is computed over one until the preregistration is frozen, so every condition
below is built from locked fixtures or from the registry alone.
"""

import ast
import io
import json
import re
import tokenize

import pytest

import commitment as cmt
import make_manifest
import score
import typecheck
import verify
from conftest import STUDY, load_json


# ---------------------------------------------------------------------------
# vocabulary sync — SPEC section 5 vs the code vs the scorer
# ---------------------------------------------------------------------------

def spec_text():
    return (STUDY / "adapter" / "SPEC.md").read_text(encoding="utf-8")


ALL_CODES = verify.UPSTREAM_CODES + verify.BINDING_CODES + verify.REPLAY_CODES


@pytest.mark.parametrize("code", ALL_CODES)
def test_every_registered_code_is_in_the_spec(code):
    assert "`%s`" % code in spec_text(), code


def test_spec_code_tables_are_exactly_the_registered_vocabulary():
    section = spec_text().split("## 5. The verification ceremony", 1)[1]
    upstream_section = section.split("### Layer `binding`", 1)[0]
    binding_section = section.split("### Layer `binding`", 1)[1].split(
        "### Layer `replay`", 1
    )[0]
    replay_section = section.split("### Layer `replay`", 1)[1].split(
        "### Report vocabulary", 1
    )[0]
    numbered = re.compile(r"^\d+\.\s+`([a-z0-9-]+)`", re.MULTILINE)
    assert set(numbered.findall(upstream_section)) == set(verify.UPSTREAM_CODES)
    binding_codes = {
        token
        for token in re.findall(r"`([a-z0-9-]+)`", binding_section)
        if token in verify.BINDING_CODES
    }
    assert binding_codes == set(verify.BINDING_CODES)
    replay_codes = set(re.findall(r"`(replay-[a-z0-9-]+)`", replay_section))
    assert replay_codes == set(verify.REPLAY_CODES)


def reachability_asserted_codes():
    """Every verdict code the reachability suite constructs a minimal condition for.

    The join key is the assertion itself — `...["code"] == "<code>"`, read out of that
    suite's own source — so a check whose fixture disappears cannot keep the claim that
    one exists.
    """
    source = (STUDY / "harness" / "tests" / "test_reachability.py").read_text(
        encoding="utf-8"
    )
    return set(
        re.findall(
            r'\[ ?"code" ?\] ?== ?"([a-z0-9-]+)"', re.sub(r"\s+", " ", source)
        )
    )


def test_every_binding_check_is_ordered_named_and_reachable():
    """Three registry facts about the nineteen binding checks — and only those three.

    That this document's numbered steps are the order the checks run in; that the SPEC's
    binding section names every code each check can return; and that the reachability
    suite constructs a minimal condition for each of those codes.

    It does **not** establish that the SPEC's prose and the implementation mean the same
    thing. Round 5 (finding 5) found the earlier name — `..._is_the_implemented_order` —
    claiming an equivalence its body never checked: it compared labels. Semantic
    agreement between the two is what review is for, and nothing here substitutes for it.
    """
    section = spec_text().split("### Layer `binding`", 1)[1].split(
        "### Layer `replay`", 1
    )[0]
    spec_order = []
    for line in section.splitlines():
        match = re.match(r"^\d+\.\s+`([a-z0-9-]+)`", line.strip())
        if match:
            spec_order.append(match.group(1))
    implemented = [label.split("/")[0] for label, _ in verify.BINDING_CHECKS]
    assert spec_order == implemented

    reachable = reachability_asserted_codes()
    for label, _ in verify.BINDING_CHECKS:
        for code in label.split("/"):
            assert "`%s`" % code in section, code
            assert code in reachable, code


def test_scorer_vocabulary_is_derived_from_verify():
    assert set(score.LAYER_OUTCOMES["upstream"]) == {
        "pass",
        "not-engaged",
        "unavailable",
    } | {"fail:" + code for code in verify.UPSTREAM_CODES}
    assert set(score.LAYER_OUTCOMES["binding"]) == {"pass"} | {
        "fail:" + code for code in verify.BINDING_CODES
    }
    assert set(score.LAYER_OUTCOMES["replay"]) == {"pass", "unavailable"} | {
        "fail:" + code for code in verify.REPLAY_CODES
    }


def test_execution_states_and_connector_outcomes_are_in_the_spec():
    text = spec_text()
    for state in verify.EXECUTION_STATES + verify.CONNECTOR_OUTCOMES:
        assert "`%s`" % state in text, state


def report_vocabulary_rows():
    """The registered report-state table, read back out of the document."""
    section = spec_text().split("### Report vocabulary", 1)[1].split(
        "### Retained outcome compatibility", 1
    )[0]
    return [line for line in section.splitlines() if line.startswith("| `")]


def test_the_registered_report_states_are_the_enforced_ones():
    """Vocabulary sync for the report table itself (R7-1).

    The compatibility matrix below it has been read back since round 6; the table that
    registers the execution states had only a presence check, so a state could be enforced
    without a registered predicate, or registered without being enforced. Round 7 adds one
    state to that table (`rejected`) — which is exactly the moment a table nobody parses
    starts to drift.
    """
    rows = report_vocabulary_rows()
    assert [row.split("|")[1].strip().strip("`") for row in rows] == list(
        verify.EXECUTION_STATES
    )
    # `none` names no call, so it names no connector outcome; every other state describes
    # the dispatch and must name the scalars that support it.
    assert set(verify.REPORT_CONNECTOR_OUTCOMES) == set(verify.EXECUTION_STATES) - {"none"}


def test_the_registered_outcome_matrix_is_the_enforced_one():
    """Vocabulary sync for round 6's compatibility matrix (R6-2).

    SPEC section 5 registers which flattened `connectorOutcome` scalar may stand beside
    which outer lifecycle state, and which report state may claim it of the bound call.
    `verify.py` enforces two dicts. This reads the registered table back out of the
    document and asserts they are the same matrix — the SPEC's table is the registration,
    and a table that drifts from what runs is the unreachable prose this study forbids.
    """
    section = spec_text().split("### Retained outcome compatibility", 1)[1]
    rows = [
        line for line in section.splitlines() if line.startswith("| `")
    ]
    assert {row.split("|")[1].strip().strip("`") for row in rows} == set(
        verify.CONNECTOR_OUTCOMES
    )
    for row in rows:
        columns = row.split("|")
        scalar = columns[1].strip().strip("`")
        registered_states = set(re.findall(r"`([a-z-]+)`", columns[2]))
        registered_reports = set(re.findall(r"`([a-z-]+)`", columns[3]))
        enforced_states = {
            state
            for state, scalars in verify.LIFECYCLE_CONNECTOR_OUTCOMES.items()
            if scalar in scalars
        }
        enforced_reports = {
            state
            for state, scalars in verify.REPORT_CONNECTOR_OUTCOMES.items()
            if scalar in scalars
        }
        assert registered_states == enforced_states, scalar
        assert registered_reports == enforced_reports, scalar


def test_not_engaged_is_not_a_pass_anywhere_in_the_scorer():
    """`not-engaged` must be its own outcome, never folded into pass in the vocabulary."""
    assert "not-engaged" in score.LAYER_OUTCOMES["upstream"]
    assert "not-engaged" not in score.LAYER_OUTCOMES["binding"]
    assert "not-engaged" not in score.LAYER_OUTCOMES["replay"]


# ---------------------------------------------------------------------------
# registry and manifests
# ---------------------------------------------------------------------------

def test_matrix_is_schema_clean():
    assert score.matrix_problems(load_json(STUDY / "harness" / "MATRIX.json")) == []


def test_matrix_layer_attribution_is_single_layer_for_endpoints():
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    for cell in registry["cells"]:
        if cell["role"] != "endpoint":
            continue
        failing = [
            layer
            for layer, outcome in cell["expected"].items()
            if outcome not in ("pass", "not-engaged")
        ]
        assert len(failing) == 1, (cell["id"], failing)


def test_every_endpoint_registers_a_mutation_constraint():
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    for cell in registry["cells"]:
        assert cell["mutationConstraint"].strip(), cell["id"]


def test_holdout_is_authored_disjoint_and_constructed():
    holdout = load_json(STUDY / "harness" / "MATRIX-HOLDOUT.json")
    assert score.holdout_problems(holdout) == []
    assert holdout["reviewer"]
    assert len(holdout["cells"]) >= 4


def test_holdout_expectations_match_the_authored_file_modulo_the_recorded_migration():
    """The reviewer's expectations are never revised — only mechanically re-keyed."""
    authored = load_json(STUDY / "reviews" / "round-1" / "MATRIX-HOLDOUT.authored.json")
    migrated = load_json(STUDY / "harness" / "MATRIX-HOLDOUT.json")
    assert migrated.get("schemaMigration")
    by_id = {cell["id"]: cell for cell in migrated["cells"]}
    assert set(by_id) == {cell["id"] for cell in authored["cells"]}
    for cell in authored["cells"]:
        after = by_id[cell["id"]]
        assert after["construction"] == cell["construction"]
        assert after["note"] == cell["note"]
        assert after["upstreamChecksReplayed"] == cell["platformChecksEngaged"]
        assert after["expected"]["binding"] == cell["expected"]["binding"]
        assert after["expected"]["replay"] == cell["expected"]["replay"]
        expected_upstream = cell["expected"]["cf"]
        if not cell["platformChecksEngaged"] and expected_upstream == "pass":
            expected_upstream = "not-engaged"
        assert after["expected"]["upstream"] == expected_upstream


def test_study_manifest_is_exact():
    assert make_manifest.manifest_problems() == []


def test_the_study_manifest_excludes_the_appendable_files_by_construction(monkeypatch):
    """ADR 0004: the manifest covers what must not change, and these two must.

    `DEVIATIONS.md` is the only place a post-freeze correction may land, so covering it
    would mean the first genuine deviation broke the anchor the deviation exists to
    protect; `README.md` carries a status banner that has to be able to change.

    Round 6 (R6-7) found the earlier version of this test tautological: no candidate glob
    reached a top-level `.md`, so the filter never met either name and removing the
    constant changed nothing. The population now includes every top-level `*.md`, and the
    load-bearing assertion below is the counterfactual — disable the constant and both
    files enter the manifest, which is what makes their absence a decision.
    """
    assert make_manifest.EXCLUDED_DOCUMENTS == ("DEVIATIONS.md", "README.md")
    covered = make_manifest.manifest_entries()
    for name in make_manifest.EXCLUDED_DOCUMENTS:
        assert (STUDY / name).is_file(), name  # excluded, not merely absent
        assert name not in covered, name
    assert "PREREGISTRATION.md" in covered
    assert "PREREG-REVIEW.md" in covered
    assert "harness/STUDY-MANIFEST.sha256" not in covered, (
        "the manifest must not cover itself either"
    )

    monkeypatch.setattr(make_manifest, "EXCLUDED_DOCUMENTS", ())
    widened = make_manifest.manifest_entries()
    assert "DEVIATIONS.md" in widened
    assert "README.md" in widened
    assert set(widened) - set(covered) == {"DEVIATIONS.md", "README.md"}, (
        "the exclusion is the only difference the constant makes"
    )


def test_every_fixture_manifest_is_exact():
    roots = [STUDY / "fixtures" / "baseline"]
    for parent in ("mutations", "holdout"):
        roots.extend(sorted((STUDY / "fixtures" / parent).iterdir()))
    for root in roots:
        assert verify.manifest_problems(root) == [], root.name


def test_fixture_typecheck_is_clean(cfos_source):
    del cfos_source
    assert typecheck.typecheck_problems() == []


def test_typecheck_is_a_scorer_precondition():
    """A published score may not call itself valid without the registered typecheck.

    The locked stratum is checked before adjudication; the holdout's own fixtures are
    checked only when the holdout is being adjudicated, so a holdout defect cannot make
    the locked stratum inconclusive (round 2, blocker 5).
    """
    source = (STUDY / "harness" / "score.py").read_text(encoding="utf-8")
    assert "typecheck.typecheck_problems(include_holdout=False)" in source
    assert "typecheck.typecheck_problems(include_holdout=True)" in source


# ---------------------------------------------------------------------------
# withdrawn claims — the guard that replaces the named-list sweep (R8-1)
# ---------------------------------------------------------------------------

# The phrase classes PREREGISTRATION section 9 withdrew. Each one names a thing this
# apparatus does not establish: that a retained history is one the pinned platform's own
# paths reach, that an attested effect stands in a causal relation to a call, or that a
# private connector field this study never retains is asserted anywhere.
WITHDRAWN_CLAIM_PHRASES = (
    "can actually retain",
    "actually emits",
    "took effect",
    "produced by",
    "caused by",
    "retryab",
    "the effect happens",
)

# Where a phrase above is legitimate, and why. An entry is (surface, phrase, anchor,
# justification): a match is permitted only when `anchor` — whitespace-normalized and
# lowercased like the scanned text — appears in the surrounding window, so the licence is
# granted to one passage rather than to a whole file. Every entry must be used.
WITHDRAWN_CLAIM_ALLOWLIST = (
    (
        "PREREGISTRATION.md",
        "produced by",
        "nothing here shows that a given retained history could have been produced by",
        "section 9 registering the no-source-reachability limit; the phrase is the thing "
        "being withdrawn, stated as a negation",
    ),
    (
        "PREREGISTRATION.md",
        "caused by",
        "is *matched*, never shown to have been caused by that call",
        "section 9 registering the no-effect-causation limit, stated as a negation",
    ),
    (
        "PREREGISTRATION.md",
        "retryab",
        "retryability, error detail, and every private field beyond the scalar are absent "
        "by construction and asserted nowhere",
        "section 9 registering the no-real-private-connector-record limit; this is the "
        "canonical statement every other surface defers to",
    ),
    (
        "README.md",
        "caused by",
        "matched to a bound call's identity, never shown to be caused by it",
        "the README restating section 9's no-effect-causation limit for a reader who "
        "starts here",
    ),
    (
        "adapter/SPEC.md",
        "retryab",
        "yes (`error`, `retryable`), within a 100-record window",
        "section 0a's retained-record table naming the pinned connector's own `error` and "
        "`retryable` fields and recording that neither is retained",
    ),
    (
        "harness/MATRIX.json",
        "retryab",
        "its retryability and its error detail are not retained and are not joined here",
        "`m02`'s registered construction saying which private fields the cell does not "
        "keep; the registry's prose is frozen and this is a negation",
    ),
    (
        "harness/build_fixtures.py",
        "retryab",
        "its retryability and its error detail are not retained and no join to a private",
        "the builder comment for the same `m02` construction, in the same negation",
    ),
)

# Skipped wherever they appear, because a guard must hold its own vocabulary verbatim.
_GUARD_TABLES = ("WITHDRAWN_CLAIM_PHRASES", "WITHDRAWN_CLAIM_ALLOWLIST")


def _guard_table_lines(source):
    """The line numbers occupied by the two tables above, in any module that defines them."""
    skipped = set()
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Assign):
            continue
        names = {t.id for t in node.targets if isinstance(t, ast.Name)}
        if names & set(_GUARD_TABLES):
            skipped.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    return skipped


def _normalize(text):
    return " ".join(text.split()).lower()


def _flatten(pieces):
    """Join (locator, text) pieces into one normalized string plus a per-character index.

    Joining normalized pieces with a single space is what lets a phrase broken across a
    Markdown line wrap, or across two comment lines, still be found: the scanned text has
    no line breaks in it at all.
    """
    parts = []
    locators = []
    for locator, raw in pieces:
        chunk = _normalize(raw) + " "
        parts.append(chunk)
        locators.extend([locator] * len(chunk))
    return "".join(parts), locators


def _text_pieces(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    return [("%d" % (number + 1), line) for number, line in enumerate(lines)]


def _python_pieces(path):
    """Comments and string literals — never bare code, so an identifier is not prose."""
    source = path.read_text(encoding="utf-8")
    skipped = _guard_table_lines(source)
    pieces = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type not in (tokenize.COMMENT, tokenize.STRING):
            continue
        if token.start[0] in skipped:
            continue
        pieces.append(("%d" % token.start[0], token.string))
    return pieces


def _json_pieces(path, prefix=""):
    def walk(node, where):
        if isinstance(node, str):
            return [(where, node)]
        if isinstance(node, dict):
            found = []
            for key, value in node.items():
                found.extend(walk(value, "%s.%s" % (where, key)))
            return found
        if isinstance(node, list):
            found = []
            for index, value in enumerate(node):
                found.extend(walk(value, "%s[%d]" % (where, index)))
            return found
        return []

    return walk(load_json(path), prefix)


# Never scanned, and each for a reason the round-8 ruling on `h08` makes explicit:
# `DEVIATIONS.md` and `PREREG-REVIEW.md` narrate the study's own history and must quote the
# claims they record as withdrawn; `reviews/` and `pilots/` are verbatim third-party and
# attempt records this study may not edit at all; `harness/MATRIX-HOLDOUT.json` is the
# reviewer's authored registry, held byte-equal to `reviews/round-1/` by its own test, so a
# phrase inside it is dispositioned in `DEVIATIONS.md` and never repaired in place.
NARRATING_LEDGERS = ("DEVIATIONS.md", "PREREG-REVIEW.md")


def living_surfaces():
    """Every surface a reader reads as this study's current claims, by glob not by list.

    Round 6 (R6-7) found an enumerated population making its own filter tautological, and
    round 7 found a named-list sweep repairing three sites while the same sentence lived on
    three lines away. So the population is derived: top-level documents, the SPEC, both
    adapter modules, every harness module and test, every probe, and the locked registry's
    prose. A document added tomorrow is covered the day it is written.
    """
    found = []
    for path in sorted(STUDY.glob("*.md")):
        if path.name not in NARRATING_LEDGERS:
            found.append((path.name, _text_pieces(path)))
    for path in sorted(STUDY.glob("adapter/*.md")):
        found.append(("adapter/%s" % path.name, _text_pieces(path)))
    # TypeScript is scanned whole: a comment extractor for it would be apparatus needing
    # its own tests, and an identifier that legitimately carries a phrase can take an
    # allowlist entry like any other use.
    for path in sorted(STUDY.glob("probes/**/*.ts")):
        found.append((str(path.relative_to(STUDY)), _text_pieces(path)))
    for pattern in ("adapter/*.py", "harness/*.py", "harness/tests/*.py"):
        for path in sorted(STUDY.glob(pattern)):
            found.append((str(path.relative_to(STUDY)), _python_pieces(path)))
    found.append(("harness/MATRIX.json", _json_pieces(STUDY / "harness" / "MATRIX.json")))
    return found


# How far either side of a match an allowlist anchor may sit, and how much of the passage a
# refusal prints. The licence radius is the wider of the two so that one entry covers one
# passage: section 0a's table row names the private connector's fields three times over in
# a single sentence, and that is one licence, not three.
LICENCE_RADIUS = 400
REPORT_RADIUS = 140


def withdrawn_claim_matches():
    matches = []
    for surface, pieces in living_surfaces():
        text, locators = _flatten(pieces)
        for phrase in WITHDRAWN_CLAIM_PHRASES:
            start = text.find(phrase)
            while start != -1:
                end = start + len(phrase)
                matches.append((
                    surface,
                    locators[start],
                    phrase,
                    text[max(0, start - LICENCE_RADIUS):end + LICENCE_RADIUS],
                    text[max(0, start - REPORT_RADIUS):end + REPORT_RADIUS],
                ))
                start = text.find(phrase, start + 1)
    return matches


def test_living_surfaces_carry_no_withdrawn_claims():
    """The machinery that replaces three rounds of named-list sweeps.

    Rounds 6, 7 and 8 each found the same class of sentence on a living surface, each time
    a few lines from where the previous round had repaired it, and each time the repair was
    a list of sites a reviewer had reached. A list cannot close a class. This scans the
    derived population above for every phrase class section 9 withdrew, and refuses any
    occurrence that is not licensed by name in `WITHDRAWN_CLAIM_ALLOWLIST`.

    The two tables are skipped wherever they are defined, since the guard must hold the
    vocabulary it forbids; every other line of this file is scanned like any other.
    """
    unlicensed = []
    used = set()
    for surface, locator, phrase, licence_window, shown in withdrawn_claim_matches():
        licences = [
            index
            for index, entry in enumerate(WITHDRAWN_CLAIM_ALLOWLIST)
            if entry[0] == surface
            and entry[1] == phrase
            and _normalize(entry[2]) in licence_window
        ]
        if licences:
            used.update(licences)
        else:
            unlicensed.append("%s:%s %r ... %s" % (surface, locator, phrase, shown))
    assert unlicensed == [], "\n".join(unlicensed)
    dead = [
        entry[0:3] for index, entry in enumerate(WITHDRAWN_CLAIM_ALLOWLIST)
        if index not in used
    ]
    assert dead == [], "allowlist entries no longer matching anything: %r" % (dead,)


# ---------------------------------------------------------------------------
# refusals and validity separation
# ---------------------------------------------------------------------------

def test_holdout_refused_while_preregistration_digest_is_null(tmp_path):
    pins = load_json(STUDY / "harness" / "PINS.json")
    if pins["preregistration"]["sha256"] is None:
        with pytest.raises(SystemExit):
            score.run(tmp_path / "attempt", include_holdout=True)
        # The refusal is recorded, not silent: the attempt marker is written before
        # anything is read, and nothing was adjudicated or published.
        assert (tmp_path / "attempt" / "ATTEMPT.json").is_file()
        assert not (tmp_path / "attempt" / "RESULTS.json").exists()


def test_scorer_refuses_an_existing_attempt_root(tmp_path):
    (tmp_path / "attempt").mkdir()
    with pytest.raises(SystemExit):
        score.run(tmp_path / "attempt")


def test_holdout_outcomes_do_not_enter_r1_arithmetic():
    """Structural: the two strata are adjudicated into disjoint collections.

    This is the whole guarantee, and the name says so. It is **not** that nothing in the
    holdout can affect R1: registry parsing, pin enforcement, the whole-study manifest and
    publication are attempt-scope preconditions shared by both strata, so a malformed
    holdout artifact can still make the whole attempt inconclusive (round 4, R4-5; round 5
    found the earlier name `..._cannot_change_r1` claiming more than these four
    substring assertions can carry, and more than the scorer does).
    """
    source = (STUDY / "harness" / "score.py").read_text(encoding="utf-8")
    assert "holdout_validity = []" in source
    assert 'sink = holdout_validity if is_holdout else validity' in source
    # R1's inputs are drawn from `rows`, which only ever receives locked cells.
    assert 'invalid = [row for row in rows if row["status"] == NOT_ADJUDICATED]' in source
    assert '(holdout_rows if is_holdout else rows).append(row)' in source


def test_replay_set_drift_is_not_adjudicated(jpack_bin, tmp_path):
    """An upstream report whose replayed set differs from the registry is validity."""
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    cell = dict(next(c for c in registry["cells"] if c["id"] == "pos-baseline"))
    verdicts = {
        "cells": {
            "pos-baseline": {
                "verdict": "pass",
                "code": None,
                "detail": None,
                "engaged": ["classifyTool"],  # the registry says both are replayed
            }
        }
    }
    validity = []
    row = score.adjudicate_cell(cell, jpack_bin, tmp_path, verdicts, validity)
    assert row["status"] == score.NOT_ADJUDICATED
    assert any("upstreamChecksReplayed" in item["problem"] for item in validity)
    assert row["divergences"] == []


def test_registered_absences_authority_is_the_cell_field():
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    cell = dict(next(c for c in registry["cells"] if c["id"] == "pos-baseline"))
    cell["registeredAbsences"] = ["report"]
    problems = score.pipeline_problems(STUDY / "fixtures" / "baseline", cell)
    assert "registered absence is present: report.json" in problems


def test_layer_functions_never_read_the_matrix():
    assert "MATRIX" not in (STUDY / "adapter" / "verify.py").read_text(encoding="utf-8")


def test_probe_sources_never_read_the_matrix():
    for path in sorted((STUDY / "probes").rglob("*.ts")):
        code_lines = [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if not line.strip().startswith(("//", "*", "/*"))
        ]
        assert "MATRIX" not in "\n".join(code_lines), path.name


# ---------------------------------------------------------------------------
# the adapter's reproduction of the platform's own rule
# ---------------------------------------------------------------------------

def test_action_kind_tag_matches_the_platform_rule():
    # The literal the pinned MCP Portal connector produces for the registered endpoint,
    # upstream server id and tool — double-encoded, because the portal's scope tag is
    # itself encoded and `actionKindFor` encodes the scope tag again.
    assert cmt.action_scope_tag() == (
        "mcp-portal:https%3A%2F%2Ftracker.example%2Fmcp:portal-tracker"
    )
    assert cmt.action_kind_tag() == (
        "mcp-portal%3Ahttps%253A%252F%252Ftracker.example%252Fmcp%3Aportal-tracker"
        ":tracker_create_work_item"
    )


def test_adapter_tag_reproduction_agrees_with_upstream(cfos_source):
    """The adapter reproduces `actionKindFor`; upstream itself must agree.

    This calls the PINNED function through the build-helper runner and compares its
    output to `commitment.py`'s own reproduction over adversarial inputs. An earlier
    probe claimed to do this and did not: it compared upstream against an inline
    restatement of upstream's one-line body, asserting f(x) == f(x) while six documents
    cited it as the guarantee.
    """
    del cfos_source
    import cf_runner

    cases = [
        (cmt.action_scope_tag(), cmt.ACTION_TOOL),
        (cmt.action_scope_tag(), cmt.SECOND_TOOL),
        ("scope with spaces", "tool/with/slashes"),
        ("a:b", "c d"),
        ("caf\u00e9", "na\u00efve_tool"),
        ("100%", "a+b=c"),
        ("~!*'()-_.", "already%20encoded"),
    ]
    helpers = cf_runner.build_helpers(
        {
            "actionKinds": [
                {"scopeTag": scope, "toolName": tool} for scope, tool in cases
            ]
        }
    )
    assert len(helpers["actionKinds"]) == len(cases)
    for item, (scope, tool) in zip(helpers["actionKinds"], cases):
        assert item["kind"]["tag"] == cmt.action_kind_tag(scope, tool), (scope, tool)
        assert item["kind"]["label"] == tool


# Cells whose construction deliberately makes the retained prose disagree with the call
# the store now holds. Each is the registry's own words, and each is asserted to DIFFER
# below, so the set cannot decay into a blanket skip.
REGISTERED_PROSE_MUTATIONS = {
    # "after approval the gatekeeper-side staged arguments are edited to provision a
    # different requester; the ledger record and its prose description are untouched"
    "b02-argument-drift",
}
# ...and cells whose action-kind TAG is a literal the reviewer forged on purpose.
REGISTERED_TAG_FORGERIES = {
    # "change actionKindTag to the literal reviewer-forged-scope:create_work_item"
    "h04-coherent-target-and-kind-substitution",
}


def registered_action_rows():
    """Every action row of both strata, with its cell, staged call and deployment.

    The holdout is *read*, not adjudicated: no layer verdict is computed here. Round 5
    (finding 5) found this condition excluding the holdout, which is where the second
    deployment lives — precisely the stratum whose construction it needed to hold.
    """
    import build_fixtures

    deployments = {
        deployment["resourceUrl"]: deployment
        for deployment in build_fixtures.DEPLOYMENTS
    }
    registries = [
        (load_json(STUDY / "harness" / "MATRIX.json"), "locked-replication"),
        (load_json(STUDY / "harness" / "MATRIX-HOLDOUT.json"), "reviewer-holdout"),
    ]
    for registry, stratum in registries:
        for cell in registry["cells"]:
            directory = score.cell_directory(cell, stratum)
            ledger = json.loads((directory / "ledger.json").read_text(encoding="utf-8"))
            platform = json.loads(
                (directory / "platform.json").read_text(encoding="utf-8")
            )
            gatekeepers = {
                gatekeeper.get("id"): gatekeeper
                for gatekeeper in platform.get("gatekeepers") or []
            }
            for entry in ledger:
                if entry.get("type") != "action":
                    continue
                deployment = deployments.get(entry.get("resourceUrl"))
                assert deployment is not None, (cell["id"], entry.get("resourceUrl"))
                calls = [
                    item
                    for item in platform.get("stagedCalls") or []
                    if item.get("gatekeeperId") == entry.get("gatekeeperId")
                    and item.get("action") == entry.get("action")
                ]
                assert len(calls) == 1, (cell["id"], entry["id"])
                gatekeeper = gatekeepers.get(entry.get("gatekeeperId"))
                tool = next(
                    (
                        candidate
                        for candidate in (gatekeeper or {}).get("tools") or []
                        if candidate.get("name") == calls[0]["toolName"]
                    ),
                    None,
                )
                assert tool is not None, (cell["id"], entry["id"])
                yield cell["id"], entry, calls[0], tool, deployment


def test_registered_scenario_is_connector_shaped(cfos_source):
    """Round 2, blocker 2: every registered identifier must be one whose shape a pinned
    connector's source defines. The generic MCP connector hardwires byo, so a vetted,
    auto-approvable write is producible only through the portal.

    Round 5 (findings 4 and 5) made the comparison a whole-description one. For every
    action row of both strata, the retained title and description bytes are regenerated
    by the PINNED `describeCall` from the registered deployment the row names, the tool
    the retained catalog holds, and the arguments the retained staged call carries — and
    the action-kind tag and label are compared unconditionally, against the deployment's
    own scope tag rather than the first portal's. The earlier version compared no prose,
    skipped the holdout, and checked the label only where the tag already matched its
    primary-deployment expectation, which is exactly what masked `b04`.

    What this establishes is coherence between a row's prose and the deployment it names
    — not that the deployment is real. The deployment tuple is registered by the builder;
    the bytes are generated by upstream.
    """
    del cfos_source
    import cf_runner

    assert cmt.RESOURCE_URL.endswith("#server=tracker")
    assert cmt.ACTION_TOOL.startswith("tracker_")
    assert cmt.SERVER_TRUST == "vetted"

    rows, requests = [], []
    for cell_id, entry, call, tool, deployment in registered_action_rows():
        description = entry["description"]
        # session.ts:126-135 always sets these three.
        assert description.get("awaitDecision") is True, cell_id
        assert isinstance(description.get("autoApprovable"), bool), cell_id
        assert description["implementsRevert"] is False, cell_id
        # The row's denormalized title is the deployment's (overseer.ts:2686).
        assert entry.get("resourceTitle") == deployment["resourceTitle"], cell_id
        label = "%s:%s" % (cell_id, entry["id"])
        requests.append(
            {
                "label": label,
                "serverName": deployment["serverName"],
                "endpoint": deployment["endpoint"],
                "tool": tool,
                "toolArgs": call["arguments"],
                "mode": "action",
                "classifiedBy": "default",
            }
        )
        rows.append((cell_id, label, description, call, deployment))

    described = cf_runner.build_helpers({"describeCalls": requests})["describedCalls"]
    for cell_id, label, description, call, deployment in rows:
        generated = described[label]
        assert description["title"] == generated["title"], cell_id
        if cell_id in REGISTERED_PROSE_MUTATIONS:
            assert description["description"] != generated["description"], cell_id
        else:
            assert description["description"] == generated["description"], cell_id
        # ...and the action kind is the connector's own, for the tool the staged call
        # names and the deployment the row names — not a literal the fixture chose.
        kind = description["actionKind"]
        assert kind["label"] == call["toolName"], cell_id
        expected_tag = cmt.action_kind_tag(
            cmt.action_scope_tag(deployment["resourceUrl"], deployment["serverId"]),
            call["toolName"],
        )
        if cell_id in REGISTERED_TAG_FORGERIES:
            assert kind["tag"] != expected_tag, cell_id
        else:
            assert kind["tag"] == expected_tag, cell_id


def test_derived_action_fields_are_disjoint_from_contextual_ones():
    assert not set(cmt.DERIVED_ACTION_FIELDS) & set(cmt.CONTEXTUAL_ACTION_FIELDS)
    assert set(cmt.DERIVED_ACTION_FIELDS) | set(cmt.CONTEXTUAL_ACTION_FIELDS) == set(
        cmt.ACTION_FIELDS
    )


def test_suppressed_codes_are_published_for_multi_defect_cells(jpack_bin, tmp_path):
    """s05 carries a second defect by construction; it must be published, not hidden."""
    del jpack_bin, tmp_path
    result = verify.layer_binding(
        verify.Cell(STUDY / "fixtures" / "mutations" / "s05-handoff-dropped")
    )
    assert result["code"] == "handoff-dropped"
    assert "report-misattribution" in result["suppressed"]


def test_matrix_modeled_dependencies_are_registered_where_used():
    """Any cell whose construction leans on a modeled datum must declare it."""
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    for cell in registry["cells"]:
        directory = score.cell_directory(cell)
        platform = json.loads((directory / "platform.json").read_text(encoding="utf-8"))
        declared = set(cell["modeledDependencies"])
        if platform.get("effects"):
            assert "effectAttestation" in declared, cell["id"]
        if platform.get("drainWitnesses"):
            assert "drainSnapshot" in declared, cell["id"]
        if platform.get("stagedCalls"):
            assert "stagedCallArguments" in declared, cell["id"]
