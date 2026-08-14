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
# withdrawn claims — the lexical backstop (R8-1, rescoped at R9-1)
# ---------------------------------------------------------------------------

# The phrase classes PREREGISTRATION section 9 withdrew, written as regular expressions
# over the whitespace-normalized, lowercased text below. Each one names a thing this
# apparatus does not establish: that a retained history is one the pinned platform's own
# paths reach, that an attested effect stands in a causal relation to a call, or that a
# private connector field this study never retains is asserted anywhere.
#
# The list is deliberately short of the class it serves. Round 9 (R9-1) showed the two
# stems that would close the remaining variants — a bare `admits` and a bare `produces` —
# are registered vocabulary here: the matrix ADMITS tuples and evaluators PRODUCE
# dispositions, both legitimately and both on many surfaces. Adding either would make the
# backstop refuse the apparatus's own language, so neither is added, and what the backstop
# therefore does not reach is written down in `HISTORICAL_FORMULATIONS` rather than
# implied to be covered.
WITHDRAWN_CLAIM_PHRASES = (
    "can actually",
    "actually emits",
    "took effect",
    "produced by",
    "caused by",
    "retryab",
    "the effect happens",
    r"\bproducible\b",
    r"\bleaves\b[^.\x00]{0,60}\bretained\b",
)

# Where a phrase above is legitimate, and why. An entry is
# (surface, phrase, anchor, occurrences, justification): a match is permitted only when
# `anchor` — whitespace-normalized and lowercased like the scanned text — appears in the
# surrounding window, AND the entry's licensed matches number exactly `occurrences`.
# Round 9 (R9-1) found the anchor alone insufficient: the licence window is wide enough to
# shadow a second, unrelated occurrence of the same phrase, so a new claim written beside a
# licensed passage inherited its licence. The count is what closes that — a licence covers
# a stated number of known occurrences, and an extra one fails whether or not it sits
# beside the anchor. A count that no longer matches also fails, so a repaired site cannot
# leave a stale licence behind.
WITHDRAWN_CLAIM_ALLOWLIST = (
    (
        "PREREGISTRATION.md",
        "produced by",
        "nothing here shows that a given retained history could have been produced by",
        1,
        "section 9 registering the no-source-reachability limit; the phrase is the thing "
        "being withdrawn, stated as a negation",
    ),
    (
        "PREREGISTRATION.md",
        "caused by",
        "is *matched*, never shown to have been caused by that call",
        1,
        "section 9 registering the no-effect-causation limit, stated as a negation",
    ),
    (
        "PREREGISTRATION.md",
        "retryab",
        "retryability, error detail, and every private field beyond the scalar are absent "
        "by construction and asserted nowhere",
        1,
        "section 9 registering the no-real-private-connector-record limit; this is the "
        "canonical statement every other surface defers to",
    ),
    (
        "PREREGISTRATION.md",
        r"\bproducible\b",
        "an earlier draft used a bare endpoint, an invented scope tag and short "
        "hand-written prose; none of it was producible",
        1,
        "section 4a recording why the earlier scenario was withdrawn: a negation about "
        "this study's own discarded draft, in the paragraph that registers section 9's "
        "limit two sentences earlier",
    ),
    (
        "README.md",
        "caused by",
        "matched to a bound call's identity, never shown to be caused by it",
        1,
        "the README restating section 9's no-effect-causation limit for a reader who "
        "starts here",
    ),
    (
        "adapter/SPEC.md",
        "retryab",
        "yes (`error`, `retryable`), within a 100-record window",
        3,
        "section 0a's retained-record table naming the pinned connector's own `error` and "
        "`retryable` fields and recording that neither is retained — one table row, one "
        "sentence, and the word three times over: `retryability` in the column head, "
        "`retryable` in the private-store cell, `retryability` again in the "
        "not-retained cell",
    ),
    (
        "adapter/SPEC.md",
        r"\bproducible\b",
        "a vetted, auto-approvable write is producible **only** through the portal",
        1,
        "round 2's deployment finding: a statement about which pinned connector can be "
        "configured at all, which is what forces the registered deployment; it is not a "
        "claim about any retained history",
    ),
    (
        "adapter/SPEC.md",
        r"\bproducible\b",
        "an invented `jps-tracker` scope and an omitted `awaitdecision`; none of that was "
        "producible",
        1,
        "the same section recording why the earlier draft's identifiers were withdrawn, "
        "as a negation about this study's own discarded draft",
    ),
    (
        "harness/MATRIX.json",
        "retryab",
        "its retryability and its error detail are not retained and are not joined here",
        1,
        "`m02`'s registered construction saying which private fields the cell does not "
        "keep; the registry's prose is frozen and this is a negation",
    ),
    (
        "harness/build_fixtures.py",
        "retryab",
        "its retryability and its error detail are not retained and no join to a private",
        1,
        "the builder comment for the same `m02` construction, in the same negation",
    ),
    (
        "adapter/commitment.py",
        r"\bproducible\b",
        "round 2 established that the earlier scenario was not producible by any pinned "
        "connector",
        1,
        "the same round-2 deployment finding as the SPEC entry above, stated as a "
        "negation about the withdrawn draft scenario",
    ),
    (
        "harness/tests/test_study.py",
        r"\bproducible\b",
        "the generic mcp connector hardwires byo, so a vetted, auto-approvable write is "
        "producible only through the portal",
        1,
        "the docstring of the regression that enforces the round-2 deployment finding, "
        "restating the SPEC sentence it checks",
    ),
)

# What rounds 6 through 9 actually quoted as the offending text, and whether this backstop
# reaches it. An entry is (round, formulation, phrase or None, where it was found). The
# `None` rows are the honest half: each is a formulation a review round found on a living
# surface and no stem here matches, because the stem that would match it is registered
# vocabulary (`admits`, `produces`) or because the finding was a different class of defect
# altogether. They are not a backlog to be closed by widening the list; they are the
# measure of how much of the class the review loop, not this test, is carrying.
HISTORICAL_FORMULATIONS = (
    ("6", "an attestation names the call that produced it", None,
     "PREREG-REVIEW.md:154"),
    ("6", "an effect produced by a different unretained call", "produced by",
     "PREREG-REVIEW.md:154"),
    ("6", "the verifier reasons about an effect caused by a call", "caused by",
     "verify.py:1250-1253"),
    ("6", "a deployment recording which call produced it", None,
     "verify.py:1250-1253"),
    ("6", "substituted causation, and the wrong cause", None,
     "test_reachability.py:406-412"),
    ("6", "the effect happens", "the effect happens", "MATRIX.json:685"),
    ("6", "the queue bypass is real", None, "MATRIX.json:691"),
    ("6", "external state is not retryable", "retryab",
     "fixtures/mutations/m02-ambiguous-commit/report.json:10"),
    ("6", "an unretained private row is failed/non-retryable", "retryab",
     "build_fixtures.py:931-950"),
    ("7", "an effect produced by an unretained call", "produced by",
     "SPEC.md:490, step 15"),
    ("7", "the staged call it came from", None, "build_fixtures.py:319-325"),
    ("7", "the trace the pinned source can actually retain", "can actually",
     "PREREGISTRATION D-5"),
    ("7", "retryable: true", "retryab", "SPEC.md:597 and verify.py:115"),
    ("8", "nothing took effect", "took effect",
     "the passages R8-1 named under R6-1r"),
    ("8", "the inner and outer rejections happen in the same transaction", None,
     "verify.py:92-93 (R8-2 — a false account of the source, not a withdrawn claim; "
     "this backstop models the claim class only)"),
    ("9", "paths admit", None,
     "R9-1's example class; `admits` is registered vocabulary and is not a stem"),
    ("9", "the queue produces / a history produces", None,
     "verify.py:147, SPEC.md:353, ceremony.ts:672; bare `produces` is registered "
     "vocabulary and is not a stem"),
    ("9", "refused a producible history", r"\bproducible\b", "verify.py:134"),
    ("9", "the pinned source can produce", None,
     "verify.py:905-906 and :969-970; the modal form of the same registered verb"),
    ("9", "what the platform can actually write", "can actually", "verify.py:883"),
    ("9", "dies in either window and leaves exactly that pair retained",
     r"\bleaves\b[^.\x00]{0,60}\bretained\b", "verify.py:132-133"),
)

# The nine passages the round-9 block repaired, as they read BEFORE the repair, with the
# phrase class that reaches each — `None` where none does. The demonstration is the point:
# three of nine would have been refused by the hardened backstop and six would not, which
# is the same arithmetic `HISTORICAL_FORMULATIONS` records and the reason the docstring
# below claims only what it claims.
ROUND_NINE_REPAIRS = (
    ("adapter/verify.py:128-131",
     "each connector path persists its own record before the outer row is written",
     None),
    ("adapter/verify.py:132-133",
     "a durable object that dies in either window leaves exactly that pair retained",
     r"\bleaves\b[^.\x00]{0,60}\bretained\b"),
    ("adapter/verify.py:133-134",
     "round 7 found only the first window admitted, which refused a producible history "
     "on the reject side",
     r"\bproducible\b"),
    ("adapter/verify.py:147",
     "an ordinary completed rejection is the most ordinary history the queue produces",
     None),
    ("adapter/verify.py:883",
     "every action row's lifecycle tuple against what the platform can actually write",
     "can actually"),
    ("adapter/verify.py:905-906",
     "derives which pairs the pinned source can produce",
     None),
    ("adapter/verify.py:969-970",
     "the pair must be one the pinned source can produce",
     None),
    ("adapter/SPEC.md:352-353",
     "over a queue the pinned drainer leaves alone — which is what a manual-approval "
     "history produces — replays coherently and passes",
     None),
    ("probes/ceremony.ts:671-672",
     "over a queue the pinned drainer leaves alone — a perfectly coherent pass, and the "
     "shape a manual-approval history produces",
     None),
)

# The representations round 9 named as evading extraction, as Python sources, with the
# phrase each must yield once the extractor is right. The last entry is the control: a run
# ends where the prose stops, so two comments five lines apart are two runs and no phrase
# is manufactured by joining them.
EVASION_REPRESENTATIONS = (
    (
        "an f-string literal (CPython 3.12 splits these into FSTRING_* tokens)",
        'DETAIL = f"the attestation was caused by the bound call"\n',
        "caused by",
    ),
    (
        "an f-string interrupted by a replacement field",
        'DETAIL = f"the attestation was caused {suffix} by the bound call"\n',
        "caused by",
    ),
    (
        "a phrase split across two contiguous comment lines",
        "# the retained attestation was caused\n# by the bound call\n",
        "caused by",
    ),
    (
        "a phrase split across adjacent string literals",
        'DETAIL = (\n    "the retained attestation was caused "\n    "by the bound call"\n)\n',
        "caused by",
    ),
    (
        "CONTROL: two comments separated by code are two runs, and do not join",
        "# the retained attestation was caused\nA = 1\nB = 2\nC = 3\n# by the bound call\n",
        None,
    ),
)

# Skipped wherever they appear, because a backstop must hold its own vocabulary verbatim.
_GUARD_TABLES = (
    "WITHDRAWN_CLAIM_PHRASES",
    "WITHDRAWN_CLAIM_ALLOWLIST",
    "HISTORICAL_FORMULATIONS",
    "ROUND_NINE_REPAIRS",
    "EVASION_REPRESENTATIONS",
)


def _guard_table_lines(source):
    """The line numbers occupied by the tables above, in any module that defines them."""
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


# Leading markup that is not prose: line comments in either language, block-comment rails,
# Markdown bullets, headings and quote marks. Round 9 (R9-1) found these breaking a phrase
# in two: `# ... pair` on one line and `# retained` on the next joined as `pair # retained`
# and matched nothing, so a claim written across a comment wrap was invisible. Stripping
# them is what makes a contiguous run read as one sentence.
_LINE_MARKER = re.compile(r"^\s*(?://+|/\*+|\*/|\*(?=\s)|#+(?=\s|$)|>+)\s*")

# Between two runs. It is a character no phrase contains and the gapped pattern excludes,
# so a run boundary can never be crossed by a match.
_RUN_BREAK = "\x00"


def _strip_markers(line):
    previous = None
    while previous != line:
        previous = line
        line = _LINE_MARKER.sub("", line, count=1)
    return line


def _flatten(runs):
    """Join runs of (locator, text) into one normalized string plus a per-character index.

    Pieces inside a run are joined with a single space, which is what lets a phrase broken
    across a Markdown line wrap, a comment wrap or two adjacent string literals still be
    found: within a run the scanned text has no line breaks and no comment markers in it at
    all. Runs are joined with `_RUN_BREAK`, so nothing is manufactured across a gap.
    """
    parts = []
    locators = []
    for run in [run for run in runs if run]:
        if parts:
            parts.append(_RUN_BREAK)
            locators.append(locators[-1])
        for locator, raw in run:
            chunk = _normalize(raw) + " "
            parts.append(chunk)
            locators.extend([locator] * len(chunk))
    return "".join(parts), locators


def _text_runs(path):
    """A text file is one run: every line is contiguous with the next, markers removed."""
    lines = path.read_text(encoding="utf-8").splitlines()
    return [[("%d" % (number + 1), _strip_markers(line)) for number, line in enumerate(lines)]]


def _string_token_text(literal):
    """The VALUE of a string literal, so its quotes and prefix cannot break a phrase."""
    try:
        value = ast.literal_eval(literal)
    except (SyntaxError, ValueError):
        return literal
    return value if isinstance(value, str) else literal


def _token_prose(token):
    """The prose a token carries, or None if it carries none.

    Comments and string literals only — never bare code, so an identifier is not prose.
    Under CPython 3.12 an f-string is no longer one STRING token (PEP 701): it arrives as
    FSTRING_START / FSTRING_MIDDLE / FSTRING_END around its replacement fields, and round 9
    (R9-1) found the extractor reading none of it. The MIDDLE tokens carry the literal
    text; the delimiters carry nothing and are dropped, which also lets the two halves
    either side of a replacement field join as one run.
    """
    if token.type == tokenize.COMMENT:
        return re.sub(r"^#+\s*", "", token.string)
    if token.type == tokenize.STRING:
        return _string_token_text(token.string)
    if token.type == getattr(tokenize, "FSTRING_MIDDLE", None):
        return token.string
    return None


def _python_runs_from_source(source):
    """Prose tokens, grouped into runs of consecutive lines."""
    skipped = _guard_table_lines(source)
    runs = []
    current = []
    last_line = None
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        text = _token_prose(token)
        if text is None or token.start[0] in skipped:
            continue
        if last_line is not None and token.start[0] > last_line + 1:
            runs.append(current)
            current = []
        current.append(("%d" % token.start[0], text))
        last_line = token.end[0]
    runs.append(current)
    return runs


def _python_runs(path):
    return _python_runs_from_source(path.read_text(encoding="utf-8"))


def _json_runs(path, prefix=""):
    """Every string value, each its own run: two values are never one sentence."""

    def walk(node, where):
        if isinstance(node, str):
            return [[(where, node)]]
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
            found.append((path.name, _text_runs(path)))
    for path in sorted(STUDY.glob("adapter/*.md")):
        found.append(("adapter/%s" % path.name, _text_runs(path)))
    # TypeScript is scanned whole: a comment extractor for it would be apparatus needing
    # its own tests, and an identifier that legitimately carries a phrase can take an
    # allowlist entry like any other use.
    for path in sorted(STUDY.glob("probes/**/*.ts")):
        found.append((str(path.relative_to(STUDY)), _text_runs(path)))
    for pattern in ("adapter/*.py", "harness/*.py", "harness/tests/*.py"):
        for path in sorted(STUDY.glob(pattern)):
            found.append((str(path.relative_to(STUDY)), _python_runs(path)))
    found.append(("harness/MATRIX.json", _json_runs(STUDY / "harness" / "MATRIX.json")))
    return found


# How far either side of a match an allowlist anchor may sit, and how much of the passage a
# refusal prints. The licence radius is the wider of the two so that one entry can cover
# one passage: section 0a's table row names the private connector's fields three times over
# in a single sentence. What bounds the licence is no longer the radius — it is the
# occurrence count each entry registers.
LICENCE_RADIUS = 400
REPORT_RADIUS = 140


def withdrawn_claim_hits(surface, runs):
    """Every match of every withdrawn phrase class on one surface's runs."""
    text, locators = _flatten(runs)
    found = []
    for phrase in WITHDRAWN_CLAIM_PHRASES:
        for match in re.finditer(phrase, text):
            start, end = match.span()
            found.append((
                surface,
                locators[start],
                phrase,
                text[max(0, start - LICENCE_RADIUS):end + LICENCE_RADIUS],
                text[max(0, start - REPORT_RADIUS):end + REPORT_RADIUS],
            ))
    return found


def withdrawn_claim_matches():
    matches = []
    for surface, runs in living_surfaces():
        matches.extend(withdrawn_claim_hits(surface, runs))
    return matches


def adjudicate_matches(matches, allowlist=None):
    """(unlicensed occurrences, entries whose licensed count is not the registered one)."""
    allowlist = WITHDRAWN_CLAIM_ALLOWLIST if allowlist is None else allowlist
    unlicensed = []
    counted = {index: 0 for index in range(len(allowlist))}
    for surface, locator, phrase, licence_window, shown in matches:
        licences = [
            index
            for index, entry in enumerate(allowlist)
            if entry[0] == surface
            and entry[1] == phrase
            and _normalize(entry[2]) in licence_window
        ]
        if licences:
            for index in licences:
                counted[index] += 1
        else:
            unlicensed.append("%s:%s %r ... %s" % (surface, locator, phrase, shown))
    miscounted = [
        (entry[0], entry[1], "registered %d, found %d" % (entry[3], counted[index]))
        for index, entry in enumerate(allowlist)
        if counted[index] != entry[3]
    ]
    return unlicensed, miscounted


def test_living_surfaces_carry_no_withdrawn_claims():
    """A LEXICAL BACKSTOP over formulations already found and repaired. Not a proof.

    What it claims: none of the exact phrase classes in `WITHDRAWN_CLAIM_PHRASES` can
    return to a living surface unlicensed. Rounds 6, 7 and 8 each found the same class of
    sentence a few lines from where the previous round had repaired it, each time because
    the repair was a list of sites a reviewer had reached; this makes reintroduction of a
    *known* formulation mechanically impossible instead of a matter of who read what.

    What it does NOT claim, stated so that no later round has to discover it: it is not a
    semantic check, it does not decide whether a new sentence asserts a withdrawn claim,
    and its stem list is knowingly narrower than the class section 9 withdrew — round 9
    (R9-1) established that the two stems which would close the remaining variants are the
    apparatus's own registered vocabulary and cannot be added. `HISTORICAL_FORMULATIONS`
    records every formulation the four review records quoted and marks, one by one, which
    this backstop reaches and which it does not; the ones it does not are carried by the
    review loop, which owns semantic completeness and always did.

    The tables are skipped wherever they are defined, since the backstop must hold the
    vocabulary it forbids; every other line of this file is scanned like any other.
    """
    unlicensed, miscounted = adjudicate_matches(withdrawn_claim_matches())
    assert unlicensed == [], "\n".join(unlicensed)
    assert miscounted == [], (
        "allowlist entries whose licensed occurrence count is not the registered one: %r"
        % (miscounted,)
    )


def _hits_on(text, surface="synthetic"):
    return withdrawn_claim_hits(surface, [[("1", text)]])


@pytest.mark.parametrize(
    "formulation", HISTORICAL_FORMULATIONS, ids=lambda item: "%s:%s" % (item[0], item[3])
)
def test_the_backstop_reaches_exactly_the_historical_formulations_it_claims(formulation):
    """Every formulation rounds 6-9 quoted, held to the coverage the table registers.

    A covered row must still be refused, or a repaired class has silently reopened. An
    uncovered row must still be uncovered: if one starts matching, someone widened the stem
    list and the table's arithmetic — and the honesty of the docstring above — has to be
    restated rather than quietly improved.
    """
    _round, quoted, phrase, _where = formulation
    hits = {hit[2] for hit in _hits_on(quoted)}
    if phrase is None:
        assert hits == set(), (quoted, hits)
    else:
        assert phrase in hits, (quoted, hits)


@pytest.mark.parametrize(
    "repair", ROUND_NINE_REPAIRS, ids=lambda item: item[0]
)
def test_the_round_nine_repairs_read_against_the_backstop_before_repair(repair):
    """The five ranges R9-1 named, passage by passage, as they read before this block.

    Three of the nine passages are refused by a phrase class and six are not — the six
    being the `produces`/`can produce`/`persists` formulations no stem may cover. This is
    the pre-repair half of the demonstration; the post-repair half is
    `test_living_surfaces_carry_no_withdrawn_claims` passing over the repaired tree.
    """
    site, before, phrase = repair
    hits = {hit[2] for hit in _hits_on(before)}
    if phrase is None:
        assert hits == set(), (site, hits)
    else:
        assert phrase in hits, (site, hits)


def test_the_backstop_coverage_arithmetic_is_the_one_the_docstrings_state():
    """The arithmetic the rescope rests on, asserted rather than described.

    If a stem is ever widened or a formulation added, this fails and the numbers in the
    docstrings and in `DEVIATIONS.md` have to be restated in the same commit.
    """
    covered = [item for item in ROUND_NINE_REPAIRS if item[2] is not None]
    assert len(covered) == 3, [item[0] for item in covered]
    assert len(ROUND_NINE_REPAIRS) == 9
    reached = [item for item in HISTORICAL_FORMULATIONS if item[2] is not None]
    assert (len(reached), len(HISTORICAL_FORMULATIONS)) == (12, 21)


@pytest.mark.parametrize(
    "representation", EVASION_REPRESENTATIONS, ids=lambda item: item[0]
)
def test_the_extractor_reads_the_representations_round_nine_named(representation):
    """Round 9 (R9-1): a phrase hidden by REPRESENTATION rather than by wording.

    An f-string, a comment wrap and an implicit string concatenation each put a phrase
    somewhere the old extractor did not look; all three are the same sentence to a reader.
    The control asserts the other direction — the run boundary is real, so the extractor
    does not invent a phrase by joining two passages that are not one.
    """
    _name, source, phrase = representation
    hits = {hit[2] for hit in withdrawn_claim_hits("synthetic", _python_runs_from_source(source))}
    if phrase is None:
        assert hits == set(), hits
    else:
        assert phrase in hits, hits


def test_a_licence_covers_a_counted_set_of_occurrences_and_no_more():
    """R9-1: the anchor window is wide enough to shadow a second occurrence.

    A new claim written beside a licensed passage used to inherit its licence, because the
    licence asked only whether the anchor was nearby. Each entry now registers how many
    occurrences it covers, so the extra one is refused by arithmetic rather than by whether
    a reviewer noticed it sitting there.
    """
    entry = WITHDRAWN_CLAIM_ALLOWLIST[0]
    only = (entry,)
    surface, phrase, anchor, occurrences = entry[0], entry[1], entry[2], entry[3]
    window = _normalize(anchor)
    exact = [(surface, "1", phrase, window, window)] * occurrences
    assert adjudicate_matches(exact, only) == ([], [])
    extra = exact + [(surface, "2", phrase, window, window)]
    unlicensed, miscounted = adjudicate_matches(extra, only)
    assert unlicensed == [], unlicensed
    assert [item[0:2] for item in miscounted] == [(surface, phrase)]
    assert adjudicate_matches(exact[:-1], only)[1] != []


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
