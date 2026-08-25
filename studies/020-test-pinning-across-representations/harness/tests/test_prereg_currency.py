"""The registration, checked against the artifacts and against itself.

**REBUILT FOR STUDY 020 from Study 019's module of the same name.** Study 019's
version closed nineteen prose findings by making them stay closed — every count
the registration stated about a committed artifact was RECOMPUTED from that
artifact, and every sentence a review had corrected was read out of the
document's own bytes rather than out of a copy. The IDEA ports whole. Most of
019's individual assertions do not, and each of the three reasons is worth
naming rather than leaving a reader to infer from what is missing:

* **019's registration is not 020's.** The δ/α decision clause, the FM interval's
  honest name, the X1 retirement prose, the pilot supersession chain, the OC
  table's operating point, the adequacy lemma's three measured metrics and the
  archived D3 question are Study 019's registered sentences. 020 registers
  different ones — no δ, no τ, no cut (§1.3), a two-tier footing (§0), an
  eighteen-member family (§5.2), a closed verdict vocabulary (§1.3) — and the
  assertions below are about THOSE.
* **The artifacts are not here yet.** §4.1 ports the gold suite, both mutant
  corpora, both references and the off-gold certificate BY DIGEST, and
  `harness/SCAFFOLD.md` item A1 carries that as a `GATE(pre-freeze)`. Every
  recomputed-count test therefore SKIPS by a named reason — the `artifacts`
  fixture is the one place that decision is made — and becomes live, unchanged,
  the moment the bytes land.
* **The review record is EMPTY of rounds, and that is a registered shape**
  (§7 delta 10). 019's round-lifecycle layer is the largest thing this module
  carries and it ports nearly verbatim; what changed is that the zero-round
  block PARSES and RENDERS, that an absent `reviews/` is zero rounds rather
  than breakage, and that there are TWO front doors rather than three. Where a
  019 assertion needed a non-empty block to mean anything, it is driven from a
  SYNTHETIC block instead of being skipped — a validator nobody has seen refuse
  is a validator nobody has tested, and waiting for round 1 to test it is
  exactly how it would go untested.

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


def unquoted(text):
    """`flatten()` with blockquote markers removed too. R1's own sentences live
    inside a `>` block, so a flatten that only collapsed whitespace would assert
    the QUOTING rather than the words."""
    return flatten(" ".join(line.lstrip("> ") for line in text.splitlines()))


@pytest.fixture(scope="module")
def flat(request):
    with open(os.path.join(_study(), "PREREGISTRATION.md"), "rb") as handle:
        return flatten(handle.read().decode("utf-8"))


@pytest.fixture(scope="module")
def plain(request):
    with open(os.path.join(_study(), "PREREGISTRATION.md"), "rb") as handle:
        return unquoted(handle.read().decode("utf-8"))


def _study():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(here))


def _load(relative):
    with open(os.path.join(_study(), relative), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def _read(relative):
    with open(os.path.join(_study(), relative), "rb") as handle:
        return handle.read().decode("utf-8")


def _sibling_test_module(name):
    """Another test module in this directory, imported by path.

    There is no `tests` package (deliberately — the suite is run from the
    harness root with `harness/` on the path), so a sibling is reached by path.
    Used where a property belongs to ONE module and two modules must assert it:
    re-implementing the walk here would make the two assertions independent,
    which is the opposite of what is wanted."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    written = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("_s020_" + name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = written


@pytest.fixture(scope="module")
def artifacts():
    """The committed artifacts the registration makes claims about, loaded once
    and RECOMPUTED rather than read out of any summary file.

    **This fixture is the one place the pre-artifact phase is decided.** §4.1
    ports the corpora by digest and `harness/SCAFFOLD.md` item A1 carries the
    port as a `GATE(pre-freeze)`; until the bytes land, every test that depends
    on this fixture skips with the reason named, and every one of them becomes
    live unchanged the moment they do. Deleting them instead would lose the
    checks; softening them would be worse than losing them."""
    from e4lib import e4
    design = os.path.join(_study(), "design", "mutants")
    needed = [os.path.join(design, "refA", "MANIFEST.json"),
              os.path.join(design, "refB", "MANIFEST.json"),
              os.path.join(_study(), "design", "gold", "gold.json"),
              os.path.join(_study(), "design", "reference", "OFFGOLD-CERT.json")]
    missing = [path for path in needed if not os.path.isfile(path)]
    if missing:
        pytest.skip(
            "PREREGISTRATION.md §4.1 ports the gold suite, both mutant corpora "
            "and the off-gold certificate BY DIGEST and harness/SCAFFOLD.md "
            "item A1 carries the port as a GATE(pre-freeze); these are not in "
            "this tree yet: %s"
            % ", ".join(os.path.relpath(path, _study()) for path in missing))
    mutants = e4.load_mutants(needed[0], needed[1],
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
        "unpairable": e4.unpairable(mutants, paired_ids),
        "engineSupplied": {language: len(e4.engine_supplied_ids(mutants, language))
                           for language in ("jps", "rego")},
        "offGold": _load("design/reference/OFFGOLD-CERT.json"),
    }


# ==========================================================================
# THE COUNTS 020 STATES ABOUT ARTIFACTS IT DOES NOT CARRY YET
# ==========================================================================


def test_the_gold_row_count_and_digest_are_the_committed_suites(artifacts, flat):
    """R1-19's rule, unchanged: a number the registration states about a
    committed artifact is recomputed from that artifact."""
    assert "**117 rows**" in _read("PREREGISTRATION.md")
    assert artifacts["goldRows"] == 117


def test_the_pairing_counts_are_recomputed_from_the_manifests(artifacts, flat):
    """§4.1 states the pairing as re-derived — "33 shared non-degenerate witness
    classes, 69 paired adequate JPS, 62 paired adequate Rego" — and this is that
    re-derivation."""
    assert ("33 shared non-degenerate witness classes, 69 paired adequate JPS, "
            "62 paired adequate Rego" in flat)
    # `build_pairing()` returns the GROUP LIST, and the shared count is derived
    # from it exactly as `harness/score.py` derives the `sharedGroups` member it
    # publishes — `countedInPairedSubset`, the flag the paired subset is defined
    # by. This test asserted a member the fixture never had; it could not have
    # failed before the corpora landed, because the fixture SKIPPED.
    shared = sum(1 for group in artifacts["pairing"]
                 if group["countedInPairedSubset"])
    assert shared == 33
    assert len(artifacts["pairedIds"]["jps"]) == 69
    assert len(artifacts["pairedIds"]["rego"]) == 62


def test_the_pins_note_gold_count_is_the_committed_suites(artifacts, pins):
    assert str(artifacts["goldRows"]) in pins["goldSuite"]["note"]
    assert pins["goldSuite"]["rows"] == artifacts["goldRows"]


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
        # NEW IN 020: an ABSENT `reviews/` is ZERO ROUNDS, not a defect. Study
        # 019 wrote its record after round 1 already existed, so the directory
        # was always there and its absence could only be breakage; 020 opens the
        # record before any round runs (ADR 0005, decision 2) and git cannot
        # track an empty directory. The refusal this drops is not lost: the
        # cross-check below compares this SET with the block's, so a block that
        # declares rounds over an absent `reviews/` still fails — by naming the
        # rounds it cannot find, which is a better message than the old one.
        return {}, []
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


# --- a SYNTHETIC record, and why 020 needs one -------------------------------
#
# Study 019 ran these mutation tests against its OWN record: twelve rounds, a
# verbatim review each, a disposition table each. Every one of them mutated a
# real row and asserted that the reading refused.
#
# 020's record is EMPTY of rounds by registration (§7 delta 10), so every one of
# those mutations would mutate nothing and every assertion would pass over an
# unexercised reader. Skipping them until round 1 lands is the worst of the
# three options: a validator nobody has seen refuse is a validator nobody has
# tested, and the round that finally exercises it is the round that most needs
# it to already work.
#
# So the mutations run against a SYNTHETIC record and a synthetic `reviews/`
# tree, built here to the registered shapes. It is a fixture and not a fake
# authority: the REAL record is still read by the structural cross-checks above
# and by the rendered-sentence tests, and the synthetic one exists only so the
# refusals are driven from day one.


def _synthetic(tmp_path, rounds=2):
    """`(record text, reviews directory)` — a record with `rounds` complete
    rounds, each with a verbatim review, a section, a disposition table and a
    severity column, all to the shapes the readers above require."""
    reviews = tmp_path / "reviews"
    entries, sections = [], []
    for number in range(1, rounds + 1):
        findings = ["R%d-%d" % (number, index) for index in (1, 2)]
        directory = reviews / ("round-%d" % number)
        directory.mkdir(parents=True)
        (directory / "PROMPT.md").write_text(
            "# Round %d prompt\n" % number, encoding="utf-8")
        (directory / "REVIEW.md").write_text(
            "# Round %d review\n\n%s\n\n%s\n\n%s\n"
            % (number, findings[0], findings[1],
               render_round_status.VERDICT_LINES[
                   render_round_status.DO_NOT_FREEZE]),
            encoding="utf-8")
        entries.append({"number": number, "state": COMPLETE,
                        "verdict": render_round_status.DO_NOT_FREEZE,
                        "severities": {"BLOCKER": 1, "MAJOR": 1, "MINOR": 0},
                        "findings": {"first": 1, "last": 2}})
        sections.append(
            "## Round %d — the reviewer's pass\n\n"
            "| Finding | Severity | Disposition |\n|---|---|---|\n"
            "| %s | BLOCKER | **Fixed.** The gate now refuses it. |\n"
            "| %s | MAJOR | **Fixed.** The count is derived. |\n"
            % (number, findings[0], findings[1]))
    body = json.dumps({"blockVersion": 1, "rounds": entries}, indent=1)
    text = ("# Pre-freeze review record — synthetic\n\n"
            "%s\n%s\n%s\n\n## Rounds\n\n%s"
            % (render_round_status.BLOCK_OPEN, body,
               render_round_status.BLOCK_CLOSE, "\n".join(sections)))
    return text, str(reviews)


@pytest.fixture
def synthetic(tmp_path):
    return _synthetic(tmp_path)


def test_the_synthetic_record_is_the_registered_shape(synthetic):
    """The fixture's own control. Every mutation test below asserts that a
    BROKEN record is refused; if the UNBROKEN one were also refused, each of
    them would pass for the wrong reason and prove nothing."""
    text, reviews = synthetic
    block = render_round_status.parse_block(text)
    assert [entry["number"] for entry in block["rounds"]] == [1, 2]
    states, problems = _tree_states(text, reviews)
    assert problems == [], problems
    assert sorted(states) == [1, 2]
    for number in (1, 2):
        assert states[number]["state"] == COMPLETE
        assert states[number]["findings"] == ["R%d-1" % number,
                                              "R%d-2" % number]
        assert states[number]["verdict"] == render_round_status.DO_NOT_FREEZE
        assert states[number]["severities"] == {"BLOCKER": 1, "MAJOR": 1}


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
            # A CLEAN ROUND: zero findings, range null.
            assert entry["findings"] is None, entry
            continue
        assert sum(entry["severities"].values()) == entry["findings"]["last"]


def test_the_zero_round_block_is_a_REGISTERED_shape_and_renders():
    """§7's delta 10, and the reason this study needed it.

    Study 019's `parse_block()` refused a block registering ZERO rounds,
    because 019 first wrote its block after round 1 already existed — so "no
    rounds" could only mean a malformed block there. 020 opens its review
    record BEFORE any round runs, which makes the empty-of-rounds block a
    registered shape rather than breakage, and the renderer produces a sentence
    for it.

    Asserted in BOTH directions, because a relaxation is only defensible if it
    is exactly as wide as it was registered to be: the empty block parses and
    renders, and the refusals it does NOT relax still bite — an absent block, a
    `rounds` member that is not a list, and rounds that are not 1..N."""
    # Rebuilt against the first real round, exactly as its pre-round-1 form
    # obliged: the EMPTY block is exercised SYNTHETICALLY now — §7 delta 10's
    # relaxation is a parser property, not a property of the live record —
    # while the live block carries round 1 open and both front doors render
    # that state verbatim.
    text = _review_record()
    head, _, rest = text.partition(render_round_status.BLOCK_OPEN)
    _, _, tail = rest.partition(render_round_status.BLOCK_CLOSE)
    body = json.dumps({"blockVersion": 1, "rounds": []}, indent=2)
    synthetic = "%s%s\n%s\n%s%s" % (head, render_round_status.BLOCK_OPEN,
                                    body, render_round_status.BLOCK_CLOSE,
                                    tail)
    rendered = render_round_status.render(
        render_round_status.parse_block(synthetic))
    assert rendered.endswith(
        "0 review rounds are on the record, 0 have returned a verdict — none "
        "has returned a verdict — and no round is open.")
    block = _block()
    assert [entry["number"] for entry in block["rounds"]] == [1]
    assert block["rounds"][0]["state"] in render_round_status.STATES
    assert render_round_status.surface_problems(_study()) == []

    def _with(body):
        text = _review_record()
        head, _, rest = text.partition(render_round_status.BLOCK_OPEN)
        _, _, tail = rest.partition(render_round_status.BLOCK_CLOSE)
        return "%s%s\n%s\n%s%s" % (head, render_round_status.BLOCK_OPEN, body,
                                    render_round_status.BLOCK_CLOSE, tail)

    for label, body in (
            ("a rounds member that is not a list",
             '{"blockVersion": 1, "rounds": {}}'),
            ("rounds that do not start at 1",
             '{"blockVersion": 1, "rounds": [{"number": 2, '
             '"state": "awaiting-review", "verdict": null, '
             '"severities": null, "findings": null}]}'),
            ("an unreadable block", '{"blockVersion": 1, "rounds": [')):
        with pytest.raises(render_round_status.BlockError):
            render_round_status.parse_block(_with(body))
    text = _review_record()
    head, _, _rest = text.partition(render_round_status.BLOCK_OPEN)
    with pytest.raises(render_round_status.BlockError):
        render_round_status.parse_block(head)


def test_the_blocks_own_refusals_bite():
    """The shape rules have power in the other direction, run as mutations of
    the real block: a repeated round number, a section out of order, two open
    rounds, and a severity total that disagrees with the finding range must each
    be REFUSED rather than resolved. A validator nobody has seen refuse is a
    validator nobody has tested."""
    text = _review_record()
    # The mutations need a NON-EMPTY block to mutate, and 020's is empty by
    # registration (§7 delta 10). A synthetic three-round block is used instead
    # of the real one, so these refusals are driven from day one rather than
    # from whichever round first makes the real block long enough — which is
    # exactly the state in which a validator goes untested.
    revise = render_round_status.DO_NOT_FREEZE
    rounds = [
        {"number": 1, "state": COMPLETE, "verdict": revise,
         "severities": {"BLOCKER": 1, "MAJOR": 1, "MINOR": 0},
         "findings": {"first": 1, "last": 2}},
        {"number": 2, "state": COMPLETE, "verdict": revise,
         "severities": {"BLOCKER": 0, "MAJOR": 1, "MINOR": 0},
         "findings": {"first": 1, "last": 1}},
        {"number": 3, "state": AWAITING_REVIEW, "verdict": None,
         "severities": None, "findings": None},
    ]
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


def test_the_empty_of_rounds_block_parses_and_renders():
    """§7 DELTA 10 — the ONE registered change to `render_round_status.py`.

    Study 019 refused a block registering zero rounds, because 019 first wrote
    its block after round 1 existed. Study 020 opens its review record BEFORE any
    round runs, so the empty block is this study's opening state and the port
    permits it. The registered rendering is the sentence §7 quotes.

    THE MUTATION CHECK, run: restore 019's

        if not numbers:
            raise BlockError("the block registers no rounds")

    after the contiguity rule in `parse_block()` and this case fails with that
    exact message, while every other case in this section still passes — so the
    assertion discriminates the delta and nothing else. Restored, the file's
    sha256 is unchanged.

    The refusals the port KEEPS are asserted above and are not weakened by this:
    a block with rounds still has to be contiguous from 1, may carry at most one
    open round, and that round must be the highest."""
    text = _review_record()
    head, _, rest = text.partition(render_round_status.BLOCK_OPEN)
    _, _, tail = rest.partition(render_round_status.BLOCK_CLOSE)
    body = json.dumps({"blockVersion": 1, "rounds": []}, indent=2)
    empty = "%s%s\n%s\n%s%s" % (head, render_round_status.BLOCK_OPEN, body,
                                render_round_status.BLOCK_CLOSE, tail)
    block = render_round_status.parse_block(empty)
    assert block["rounds"] == []
    rendered = render_round_status.render(block)
    assert "0 review rounds are on the record" in rendered
    assert "none has returned a verdict" in rendered
    assert "no round is open" in rendered


def test_the_two_front_doors_are_the_registered_surfaces(study):
    """§7 DELTA 10's other half: `SURFACES` narrows to two. 019's third,
    `design/POLICY-DRAFT.md`, is not a 020 front door — this study's policy prose
    is ported frozen rather than drafted here, so that document attests nothing
    about 020 and regenerating a status sentence into it would be a third,
    unread attestation."""
    assert render_round_status.SURFACES == ("README.md", "PREREGISTRATION.md")
    for relative in render_round_status.SURFACES:
        assert os.path.isfile(os.path.join(study, relative)), relative
    assert "design/POLICY-DRAFT.md" not in render_round_status.SURFACES


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
    # 020's record carries no round sections yet, so the duplicate is
    # constructed rather than found — the refusal is driven from day one rather
    # than from whichever round first gives the reader something to duplicate.
    heading = "## Round 5 — the reviewer's fifth pass"
    mutated = text + "\n\n%s\n\nbody\n\n%s\n\nbody\n" % (heading, heading)
    sections, problems = _record_sections(mutated)
    assert any("more than one `## Round 5` section" in problem
               for problem in problems), problems
    assert 5 in sections


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


def test_a_block_verdict_the_review_did_not_return_is_refused(synthetic):
    """R8-3, run as the reviewer ran it: round 7's block verdict changed to
    `FREEZABLE AS WRITTEN` — the one token that would authorise a freeze —
    while its verbatim review still ends `DO NOT FREEZE`. Every structural
    predicate passed. Two things must refuse it now: the closed vocabulary (a
    verdict outside the contract is not a verdict) and the binding to the
    reviewer's own final line."""
    text, reviews = synthetic
    block = _block(text)
    rounds = block["rounds"]

    def _record_with(new_rounds):
        body = json.dumps({"blockVersion": 1, "rounds": new_rounds}, indent=2)
        head, _, rest = text.partition(render_round_status.BLOCK_OPEN)
        _, _, tail = rest.partition(render_round_status.BLOCK_CLOSE)
        return "%s%s\n%s\n%s%s" % (head, render_round_status.BLOCK_OPEN, body,
                                   render_round_status.BLOCK_CLOSE, tail)

    refusing = [number for number, entry in _block_states(text).items()
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
    verdict, final_line = _review_verdict(number, reviews)
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


def test_no_round_has_returned_the_freeze_verdict_yet():
    """THE TRIPWIRE, restored for 020 — Study 019's R8-1 tripwire in its
    original form, because 020's record is back in the state 019's was written
    for.

    No round has returned `freezable as written`, so the FIRST round that does
    forces a deliberate revisit of this test instead of a sentence somebody
    forgot to update. When it fires, the assertion it becomes is 019's
    successor: the freeze verdict on the record was returned by a COMPLETE
    round with ZERO findings whose verbatim review's final line is the token
    byte-exact, and by no round that carries findings.

    Both halves are here already, so the successor is a deletion rather than a
    rewrite: the positive attestation below runs over whatever rounds exist,
    which today is none."""
    assert render_round_status.FREEZE_VERDICT in render_round_status.VERDICTS
    states, problems = _tree_states()
    assert problems == [], "\n  ".join([""] + problems)
    freeze_rounds = [n for n, entry in _block_states().items()
                     if entry["verdict"] == render_round_status.FREEZE_VERDICT]
    assert freeze_rounds == [], (
        "a round has returned the freeze verdict; replace this tripwire with "
        "the positive attestation below rather than deleting it")
    for number in freeze_rounds:
        facts = states[number]
        assert facts["state"] == COMPLETE, (number, facts["state"])
        assert facts["findings"] == [], (number, facts["findings"])
        assert facts["finalLine"] == \
            render_round_status.VERDICT_LINES[render_round_status.FREEZE_VERDICT]


# --- ROUND-8 FINDING R8-4: the block is schema-closed at every depth ---------

def test_a_block_readable_two_ways_is_refused(synthetic):
    """R8-4, in the three constructions the reviewer ran. The block's own
    docstring promised to refuse anything readable two ways and then used the
    ordinary decoder: a duplicate `blockVersion`, a duplicate `verdict` inside a
    round entry, and a surplus TOP-LEVEL member were all accepted, the first two
    resolving last-one-wins while a human reader saw the first."""
    text, _reviews = synthetic
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

def test_a_duplicate_disposition_row_is_refused_and_not_overwritten(synthetic):
    """R8-5's first half, run as the reviewer ran it: a SECOND row for a finding,
    carrying a different severity and a contradictory disposition. The rows went
    into dictionaries with no duplicate check and completion was key-set
    equality, so the later row silently won and the round still read `complete`."""
    text, reviews = synthetic
    states, _problems = _tree_states(text, reviews)
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

    after, problems = _tree_states(mutated, reviews)
    assert after[number]["state"] == MALFORMED, (
        "a round whose table names a finding twice is not a complete round")
    assert any("more than one row for %s" % name in problem
               for problem in problems), problems


def test_a_commented_out_disposition_table_does_not_complete_a_round(synthetic):
    """R8-5's second half, the reviewer's construction exactly: wrapping ALL of
    a round's rows in one multiline HTML comment left the round reading
    `complete` with its whole table inactive. A fenced code block is the same
    defect in the other inactive context."""
    text, reviews = synthetic
    states, _problems = _tree_states(text, reviews)
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
        after, _problems = _tree_states(mutated, reviews)
        assert after[number]["dispositions"] == {}, (
            "%s is not a disposition table: %s" % (label, after[number]))
        assert after[number]["state"] != COMPLETE, (
            "round %d stayed complete with its whole table inside %s"
            % (number, label))


# --- ROUND-8 FINDING R8-7: an inactive heading is not a heading --------------

def test_a_heading_inside_a_fence_or_a_comment_is_not_a_heading(synthetic):
    """R8-7, at the surface 020 has. Study 019 drove this over
    `design/POLICY-DRAFT.md`'s verification heading; 020 drafts no policy prose
    (§7 delta 10), so the same liveness property is driven over the surface that
    does exist — the record's own `## Round N` headings, which
    `_record_sections()` reads through `_live_lines()`.

    The finding is the same one: the exact required line placed inside a fenced
    code block or a multiline HTML comment satisfied a raw substring
    requirement while presenting nothing to a reader. A structural reader that
    counts inactive content is not reading structure."""
    text, _reviews = synthetic
    sections, problems = _record_sections(text)
    assert sorted(sections) == [1, 2] and problems == []
    heading = "## Round 2 — the reviewer's pass"
    assert text.count(heading) == 1

    for label, wrapper in (("a fenced code block", "```\n%s\n```"),
                           ("a tilde-fenced code block", "~~~\n%s\n~~~"),
                           ("a multiline HTML comment", "<!--\n%s\n-->")):
        mutated = text.replace(heading, wrapper % heading, 1)
        assert heading in mutated, (
            "the construction keeps the exact text in the file, which is why a "
            "raw substring requirement passed it (%s)" % label)
        inactive, _problems = _record_sections(mutated)
        assert sorted(inactive) == [1], (
            "round 2's heading is inside %s and is not a heading: %s"
            % (label, sorted(inactive)))

    # …and the liveness must not hide a heading that IS live: a second, live
    # copy beside the inactive one is still read, and is still a duplicate.
    decoy = text.replace(heading, "%s\n\n```\n%s\n```" % (heading, heading), 1)
    _sections, problems = _record_sections(decoy)
    assert problems == [], problems


def test_the_live_line_reader_keeps_the_documents_own_line_count():
    """`_live_lines()` is shared by the table reader and the heading reader, and
    the Setext half of the second one looks at the FOLLOWING line — so blanking
    inactive content must never change how many lines there are."""
    for relative in ("PREREG-REVIEW.md", "PREREGISTRATION.md", "README.md",
                     os.path.join("harness", "SCAFFOLD.md")):
        with open(os.path.join(_study(), relative), "rb") as handle:
            text = handle.read().decode("utf-8")
        assert len(_live_lines(text)) == len(text.split("\n")), relative
    sample = "a\n<!-- b\nc -->\nd\n```\n# e\n```\n# f\n"
    assert _live_lines(sample) == ["a", "", "", "d", "", "", "", "# f", ""]


def test_a_placeholder_disposition_cell_reopens_its_round(synthetic):
    """R6-3's construction, kept, with ROUND-7 FINDING R7-3's length heuristic
    removed from underneath it. Each mutation of a real disposition cell must
    move the round the artifacts show from `complete` to `awaiting-response`."""
    text, reviews = synthetic
    states, _problems = _tree_states(text, reviews)
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
        after, problems = _tree_states(mutated, reviews)
        assert problems == [], problems
        assert name in after[number]["pendingRows"], (
            "%r read as a written disposition for %s" % (replacement, name))
        assert after[number]["state"] == AWAITING_RESPONSE, (
            "round %d stayed closed with %s's cell %r"
            % (number, name, replacement))


def test_a_prompt_only_round_reads_as_open_and_not_as_a_broken_tree(synthetic,
                                                                     tmp_path):
    """R6-1's construction, kept: the round-opening commit, where
    `reviews/round-N/PROMPT.md` is committed and nothing else exists yet. That
    tree is the regime working correctly and the model must say so.

    ROUND-7 FINDING R7-1 is what happens when the model says so and the
    maintainer's ceremony does not: the round-7 prompt-only commit did not carry
    the rendered sentence, so the lifecycle tests were red on the commit whose
    greenness the prompt asserted. `harness/render_round_status.py --write` is
    the answer to that half, and this is the answer to this one."""
    text, existing = synthetic
    states, _problems = _tree_states(text, existing)
    highest = max(states)
    reviews = tmp_path / "opened"
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

def test_the_two_front_doors_carry_the_rendered_sentence_verbatim():
    """The whole positive attestation, and it is an EXACT COMPARISON rather than
    a search: the sentence is rendered from the block here, at test time, and
    each front door must carry that string exactly once.

    TWO front doors, not 019's three (§7 delta 10): 019's third was
    `design/POLICY-DRAFT.md`, and 020's policy prose is ported FROZEN rather
    than drafted here, so a third front door would render a status sentence
    into a document this study does not author. The count is read from
    `SURFACES` rather than written here, and the narrowing is asserted below.

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
    assert render_round_status.SURFACES == ("README.md", "PREREGISTRATION.md")
    assert "design/POLICY-DRAFT.md" not in render_round_status.SURFACES
    # 019's `design/POLICY-DRAFT.md` IS in this tree — the whole `design/` tree
    # is carried, unpinned, and `harness/PORTS.md` says so under "Carried
    # UNPINNED". What §7 delta 10 registers is that it is not a SURFACE: 020
    # drafts no policy prose of its own, so the draft attests nothing about this
    # study and the renderer must not write a status sentence into it. That is
    # the property asserted, and it is stronger than the file's absence was —
    # an absent file cannot carry a stale sentence, and this one is checked for
    # one.
    draft = os.path.join(_study(), "design", "POLICY-DRAFT.md")
    if os.path.exists(draft):
        with open(draft, "rb") as handle:
            carried = render_round_status.flat(handle.read().decode("utf-8"))
        assert wanted not in carried, (
            "019's carried policy draft must not carry 020's rendered "
            "round-status sentence: it is not one of this study's front doors")
        assert "review round" not in carried.lower().split("019")[0][:400]


def test_the_rendered_sentence_moves_when_the_block_moves():
    """The property a remembered sentence can never have. Four mutations of the
    real block — a verdict changed, a round's state opened, a round added, the
    open round closed — must each change the rendered string, and the documents
    carry only the unmutated one."""
    # A synthetic two-round block, for the reason `test_the_blocks_own_refusals_
    # bite` uses one: 020's real block is empty by registration, and a mutation
    # test over an empty block mutates nothing. The REAL block's rendering is
    # asserted against the documents by the test above; this one asserts the
    # sentence is a FUNCTION of the block, which is the property a remembered
    # sentence can never have.
    block = {"blockVersion": 1, "rounds": [
        {"number": 1, "state": COMPLETE,
         "verdict": render_round_status.DO_NOT_FREEZE,
         "severities": {"BLOCKER": 0, "MAJOR": 1, "MINOR": 0},
         "findings": {"first": 1, "last": 1}},
        {"number": 2, "state": AWAITING_RESPONSE,
         "verdict": render_round_status.FREEZABLE_AFTER_FIXES,
         "severities": {"BLOCKER": 0, "MAJOR": 1, "MINOR": 0},
         "findings": {"first": 1, "last": 1}}]}
    rendered = render_round_status.render(block)
    mutations = {}

    # …and the EMPTY block, which is what the documents actually carry: every
    # mutation below must render something the front doors do not contain, and
    # the empty block must render something they do.
    assert render_round_status.flat(
        render_round_status.render(_block())) == render_round_status.flat(
            render_round_status.sentence(_study()))

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


def test_the_registration_header_names_no_round_while_none_is_complete():
    """The revision a reader is holding is only meaningful against the round it
    answers: the highest COMPLETE round in the block. 020 has none, so the
    header must claim none — and the assertion is two-sided, because a header
    that named a round nobody has run would be the drift this whole layer
    exists to catch.

    When the first round completes, this becomes 019's form: the header must
    carry `post-round-N` for exactly the highest complete round."""
    complete = [number for number, entry in _block_states().items()
                if entry["state"] == COMPLETE]
    with open(os.path.join(_study(), "PREREGISTRATION.md"), "rb") as handle:
        header = flatten(handle.read().decode("utf-8").split("\n## ")[0])
    found = re.findall(r"post-round-(\d+)", header)
    if not complete:
        assert found == [], (
            "no round is complete and the registration header says "
            "post-round-%s" % "/".join(found))
        # State-agnostic across the two open states (awaiting-review /
        # awaiting-response): the header must say the round is OPEN; the exact
        # rendered sentence is held verbatim by surface_problems() already.
        assert "round 1 is open" in header
        return
    answered = max(complete)
    assert found, (
        "the registration's status header must name the round this revision "
        "responds to, as `post-round-N`")
    assert [int(number) for number in found] == [answered] * len(found), (
        "the highest round this revision has dispositioned is %d and the "
        "registration header says post-round-%s"
        % (answered, "/".join(found)))


def test_the_two_headers_agree_on_the_revision_ordinal():
    """A cheap cross-check with no external authority: whatever revision the
    study is on, its two front doors must say the same one.

    020's headers say "first revision" rather than 019's "Nth major revision",
    so the pattern reads either spelling and the agreement is what is asserted —
    not the wording, which is the documents' own."""
    pattern = re.compile(r"(%s)(?: major)? revision" % "|".join(_REVISIONS))
    seen = {}
    for relative in render_round_status.SURFACES:
        with open(os.path.join(_study(), relative), "rb") as handle:
            header = flatten(handle.read().decode("utf-8").split("\n## ")[0])
        found = pattern.findall(header.lower())
        assert found, "%s's status header states no revision ordinal" % relative
        seen[relative] = found[0]
    assert len(set(seen.values())) == 1, seen


# ==========================================================================
# 020's OWN currency properties — the registration against itself and the code
# ==========================================================================
#
# R1-20's rule, carried: a sentence ABOUT the code is checked against the code's
# own constants, so a one-sided edit names its own drift site.


def test_the_ports_sentence_counts_what_the_code_registers():
    """`harness/PORTS.md`'s prose states the size of the registered destination
    set; `integrity.REQUIRED_PORTS` is that set. Study 019's round-1 finding
    R1-20 was this exact sentence, stale at "five" while the constant held
    seven, so the count is READ OUT OF THE CONSTANT here and the document must
    spell the same number."""
    words = {5: "five", 6: "six", 7: "seven", 13: "thirteen", 20: "twenty",
             46: "forty-six"}
    ports = flatten(_read("harness/PORTS.md"))
    size = len(integrity.REQUIRED_PORTS)
    assert "the destination set at exactly the %s files this table names" \
        % words[size] in ports
    assert "the destination set to be exactly the %s files above" \
        % words[size] in ports
    assert "The seven files 019 itself ported answer to BOTH" in ports
    assert len(integrity.TIER_PORTS_PATHS) == 7
    # The set's SECOND half, which is the other way a row can be missing and
    # nobody notice: a harness file with no source-side row because 019 had no
    # such file. `verify_chain()` checks the union against the directory, so the
    # two halves are exhaustive together.
    assert integrity.REGISTERED_HARNESS_FILES == \
        integrity.REQUIRED_PORTS | integrity.NEW_IN_020
    assert not (integrity.REQUIRED_PORTS & integrity.NEW_IN_020)
    for name in integrity.NEW_IN_020:
        assert os.path.isfile(os.path.join(_study(), name)), name


def test_the_wrapper_rows_difference_count_is_the_number_it_enumerates():
    """R1-20's other half: a row that says "THREE registered differences" must
    enumerate three, and the enumeration is what a reader checks the wrapper
    against. Counted from the row's own bold ordinals rather than from a number
    written here."""
    for row in integrity.parse_ports(
            os.path.join(_study(), "harness", "PORTS.md")):
        source, _source_sha, destination, _destination_sha = row
        if destination != "harness/authoring_call.sh":
            continue
        break
    else:
        raise AssertionError("no row for harness/authoring_call.sh")
    text = _read("harness/PORTS.md")
    cell = [line for line in text.splitlines()
            if line.startswith("| `%s` |" % source)][0]
    stated = re.search(r"complete port, (\w+) registered differences", cell)
    assert stated, cell
    words = {"TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5, "SIX": 6,
             "SEVEN": 7, "EIGHT": 8}
    enumerated = len(re.findall(r"\*\*\(\d\)", cell))
    assert enumerated == words[stated.group(1).upper()], (
        "the row says %s registered differences and enumerates %d"
        % (stated.group(1), enumerated))


def test_every_row_that_claims_a_difference_count_enumerates_that_many():
    """The same property over EVERY row, so a row added later cannot state a
    count nobody checks."""
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10}
    text = _read("harness/PORTS.md")
    checked = 0
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        stated = re.search(r"port, (\w+) registered differences", line)
        if not stated:
            continue
        enumerated = len(re.findall(r"\*\*\(\d\)", line))
        assert enumerated == words[stated.group(1).lower()], line[:120]
        checked += 1
    assert checked >= 4, "no row states a difference count; the check is idle"


def test_the_harness_is_described_as_existing_and_as_partial():
    """§7 says what the port IS, and the tree must match both halves: the
    machinery is here, and the deltas that have not landed are named."""
    ports = flatten(_read("harness/PORTS.md"))
    scaffold = flatten(_read("harness/SCAFFOLD.md"))
    for name in sorted(integrity.REQUIRED_PORTS):
        assert os.path.isfile(os.path.join(_study(), name)), name
    assert "COMPLETE port of 019's executable harness surface" in ports
    assert "AND of its registered artifacts" in ports
    assert "PARTIAL port of the study" in ports
    for item in ("A1", "S1", "S3", "S4", "S5", "S6", "S8", "R1"):
        assert "| %s |" % item in scaffold, item


def test_no_lifecycle_note_still_calls_a_landed_item_outstanding():
    """019's R4-6, carried: a note that describes a state the tree no longer has
    is a note on the tripwire whose whole job is to describe the tree. The four
    deltas that LANDED with this port must not appear in the owed register, and
    the ones that have not must."""
    scaffold = flatten(_read("harness/SCAFFOLD.md"))
    ports = flatten(_read("harness/PORTS.md"))
    for landed in ("the scorer's survivor-vector schema; the token collision is "
                   "fixed",
                   "no threshold",
                   "the new admission code",
                   "the ownPolicyIdentity invocation",
                   "the eighteen-member family scorer",
                   "registeredLabelRule restated",
                   "the schedule re-derived at the registered round count",
                   "the freeze gate's calibration/ rule",
                   "the fresh sealed reviewer set",
                   "the empty-of-rounds review record",
                   # R1-18 amended delta 11: the register briefly LEFT the
                   # covered set and round 1 put it back — the landed phrase
                   # moved with the ruling.
                   "the register is COVERED again",
                   "design/pilot/pilot_run.py deleted, not ported",
                   "the D-1 smoke restatement"):
        assert landed in ports, landed
    assert "presence_idiom.py" in ports
    assert "All THIRTEEN of §7's deltas have landed" in scaffold
    # …and no landed delta is still described as OWED in the S table. What the
    # S rows may still owe is a VALUE the delta produces or a document it waits
    # on — never the delta itself, so the mechanism names are absent here.
    owed = scaffold.split("## S — the registered deltas")[1].split("## R —")[0]
    assert "survivor-vector schema" not in owed
    assert "ownPolicyIdentity invocation" not in owed
    assert "eighteen-member family scorer." not in owed


def test_the_registration_states_the_integrity_bootstrap_and_not_the_stronger_claim():
    """019's R3-7, carried verbatim into 020's §7: integrity is a gate against
    drift, not a root of trust, and the bootstrap is stated rather than
    glossed."""
    text = _read("PREREGISTRATION.md")
    flat_text = flatten(text)
    assert "Integrity is a gate against drift, not a root of trust" in flat_text
    assert ("What that cannot be is a proof that the checker is the checker the "
            "manifest describes" in flat_text)
    assert ("integrity is a gate against drift, not a root of trust" in
            flat_text or "gate against drift" in flat_text)


def test_the_publication_commitment_does_not_promise_a_forbidden_interval():
    """019's R3-8, carried: §10 may not promise to publish a quantity §5.9
    forbids computing. 020 states the rule and its one exception in terms."""
    flat_text = flatten(_read("PREREGISTRATION.md"))
    assert ("It is not a promise that a family evaluation exists in every "
            "outcome, because §5.9 forbids computing one above row 3" in flat_text)
    assert ("Publishing a number the registered rule says must not be computed "
            "is not a stronger publication commitment; it is a violation of "
            "§5.9 wearing one." in flat_text)


def test_the_bundle_is_registered_and_no_formality_only_claim_survives():
    """019's R1-17, carried into 020's §1.1, §3.1 and §9: A−C is a BUNDLE, no
    component attribution is licensed, and no formality-only claim about the
    B/C difference appears anywhere."""
    flat_text = flatten(_read("PREREGISTRATION.md"))
    assert ("A−C therefore compares the pack format against "
            "Rego-plus-the-full-convention, as bundles." in flat_text)
    assert ("no attribution of any part of an A−C result to any component of "
            "the bundle — representation, result schema, or any individual "
            "convention — is licensed" in flat_text)
    assert ("No formality-only claim about the B/C difference appears anywhere "
            "in this registration." in flat_text)
    assert ("A−C is a bundled treatment and nothing inside the bundle is "
            "separable" in flat_text)


def test_the_registration_registers_no_cut_and_no_threshold():
    """020's OWN version of 019's δ-clause currency test, and it is the opposite
    assertion: §1.3 registers NO δ, NO τ, NO cut and NO dichotomy, and says why
    — "there is no τ that can be unattainable, which is the property that killed
    019's E4". A registration that grew one back would fail here."""
    plain_text = unquoted(_read("PREREGISTRATION.md"))
    assert "No δ, no τ, no cut, no dichotomy, and no registered direction." \
        in plain_text
    assert ("there is no τ that can be unattainable, which is the property that "
            "killed 019's E4" in plain_text)
    assert "No replacement attainability machinery is registered" in plain_text
    assert "no cross-scale comparison is made anywhere in this document" \
        in plain_text


def test_the_verdict_vocabulary_is_closed_and_unsupported_is_absent():
    """§1.3 closes the vocabulary and bans one word by name. The ban is checked
    over the WHOLE document, because a word banned in one section and used in
    another is not banned."""
    text = _read("PREREGISTRATION.md")
    flat_text = flatten(text)
    assert ("There is exactly one verdict vocabulary: CLAIM or "
            "INDETERMINATE-BY-DISAGREEMENT." in flat_text)
    assert "The word UNSUPPORTED is not used anywhere in 020" in flat_text
    occurrences = re.findall(r"\bUNSUPPORTED\b", text)
    assert len(occurrences) == 1, (
        "§1.3 bans the word and the document uses it %d times; the one "
        "occurrence is the ban itself" % len(occurrences))


def test_the_family_size_is_one_number_everywhere_it_is_stated():
    """The eighteen-member family is stated in §1.3, §5.2, §5.4, §5.9 and §10,
    and in `e4lib/decision.py`'s constant. One number, five prose sites, one
    constant — and the count of §5.5's reprint rows is what settles it."""
    from e4lib import decision
    text = _read("PREREGISTRATION.md")
    flat_text = flatten(text)
    rows = re.findall(r"^\| M(\d+) \| L", text, re.MULTILINE)
    assert [int(number) for number in rows] == list(range(1, 19)), rows
    from e4lib import family
    assert decision.REGISTERED_FAMILY_SIZE == len(rows)
    # …and the members EXIST, which is the half that could not be
    # asserted while §7 delta 5 was open: the prose, the decision
    # rule's constant and the scorer's own table are one number.
    assert len(family.MEMBERS) == len(rows)
    for phrase in ("all eighteen registered family members (§5.2) agree",
                   "The registered sensitivity family — eighteen members",
                   "an intersection–union test",
                   "All eighteen family members agree in the sign of the A−C "
                   "difference and all eighteen reject",
                   "All eighteen point estimates, all eighteen p-values"):
        assert phrase in unquoted(text), phrase


def test_the_two_tier_footing_labels_every_descriptive_table():
    """§0's standing clause is a MANDATORY reprint, not a convention: "Every
    Tier D table carries the standing clause … *descriptive; published as an
    interpretation quantity that no decision reads.*"

    Counted on the FLATTENED text, because the registration wraps its own
    sentences and a raw substring count would measure the line breaks. Both
    casings count: §0 states the rule in lower case inside a sentence and the
    tables carry it capitalised."""
    text = _read("PREREGISTRATION.md")
    flat_text = " ".join(text.split())
    clause = "escriptive; published as an interpretation quantity that no " \
             "decision reads."
    assert flat_text.count(clause) >= 4, (
        "the standing Tier D clause appears %d times; §0 makes it a mandatory "
        "reprint beside every Tier D table" % flat_text.count(clause))
    # …and beside each of the tables §0 and §5 name by position: the
    # leaked-direction table (§0.2) and E1's exclusive disposition table (§5.1).
    for anchor in ("| §1a admitted, ITT-114 (38/37/39) | group, 33 shared |",
                   "| C | 39 | 9 (`opa-check-failed` 9) |"):
        assert anchor in flat_text, anchor
        after = flat_text.split(anchor, 1)[1][:600]
        assert clause in after, anchor
    # §0 states the rule itself, and §5.5 restates it over its three reprints.
    assert ("**Every Tier D table carries the standing clause, carried verbatim "
            "from 019 §5's R1-15 discipline: *descriptive; published as an "
            "interpretation quantity that no decision reads.*" in flat_text)
    assert ("All three are **arm-labelled by design, under Tier D** — "
            "*descriptive; published as an interpretation quantity that no "
            "decision reads.*" in flat_text)


def test_the_presence_idiom_numbers_agree_across_all_three_surfaces(pins):
    """The power analysis exists in three places — the published document, the
    registry block and the preregistration's filled TODO — and a number that
    moved in one of them would be a registration nobody could check. The
    registry is the machine-readable one and the other two must carry its
    strings."""
    document = flatten(_read("harness/POWER-PRESENCE-IDIOM.md"))
    registration = flatten(_read("PREREGISTRATION.md"))
    block = pins["presenceIdiomGuard"]
    for member in ("sensitivity", "specificity", "falsePositivesOnLawfulIn"):
        value = flatten(block[member])
        assert value in document, (member, value)
        assert value in registration, (member, value)
    assert block["registered"] is True
    assert "40/40" in registration and "0/22" in registration


def test_the_readme_states_the_registered_question_and_the_current_state():
    """The reader-facing front door must state THIS study's question and this
    study's state, and must not claim a review that has not happened. The
    state read is the BLOCK'S, not a phrase this test froze at one moment —
    the first version hard-coded "round 1 is open" and went stale the day the
    round completed."""
    readme = flatten(_read("README.md"))
    assert "what its accompanying test suite pins down" in readme
    states = _block_states()
    open_rounds = [number for number, entry in states.items()
                   if entry["state"] != COMPLETE]
    complete = [number for number, entry in states.items()
                if entry["state"] == COMPLETE]
    if open_rounds:
        assert "round %d is open" % max(open_rounds) in readme
    else:
        assert complete, "no round exists and the question test read a state"
        assert "post-round-%d" % max(complete) in readme
    for claim in ("has been reviewed", "review is complete",
                  "freezable as written"):
        assert claim not in readme.lower(), claim


def test_the_manifest_is_current_with_the_tree():
    """R2-1, carried, and it fails HERE as well as in `tests/test_manifest.py`:
    a single failing test in a suite this size reads as one test's problem, and
    a currency failure is not that."""
    assert make_manifest.manifest_problems() == [], (
        "the committed manifest does not describe the tree it covers; "
        "regenerate it LAST, after PORTS.md and PINS.json (ADR 0005)")


def test_the_appendable_records_are_excluded_by_named_constant():
    """R3-1, carried. The exclusion is what stops the manifest going stale every
    time a round lands a disposition, and it is by NAMED CONSTANT with its
    reason — a name without its reason is what a later widening argues past."""
    for name in ("PREREG-REVIEW.md", "DEVIATIONS.md", "README.md",
                 "harness/ADVISORIES.md", "harness/PINS.json"):
        assert name in make_manifest.EXCLUDED_DOCUMENTS, name
        assert make_manifest.EXCLUDED_DOCUMENTS[name].strip(), name
    assert "PREREGISTRATION.md" in make_manifest.REGISTERED_DOCUMENTS, (
        "excluding an appendable record must not become an argument for "
        "excluding the document that carries the claims")


def test_the_registered_ci_enforcement_exists():
    """019's R4-6, carried: the deterministic controls this study registers must
    be RUN by something. The job is named here and its steps are read out of the
    workflow rather than remembered."""
    root = os.path.dirname(os.path.dirname(_study()))
    workflow = os.path.join(root, ".github", "workflows", "ci.yml")
    assert os.path.isfile(workflow), workflow
    with open(workflow, "rb") as handle:
        text = handle.read().decode("utf-8")
    assert "study-020-harness:" in text
    # The job's own block, cut at the NEXT top-level job key rather than at a
    # blank line: a job body contains blank lines, and a cut that took the
    # whole rest of the file would let a later job satisfy these assertions.
    after = text.split("study-020-harness:", 1)[1]
    lines = []
    for line in after.split("\n"):
        if re.fullmatch(r"  [a-z0-9-]+:", line):
            break
        lines.append(line)
    body = "\n".join(lines)
    assert "studies/020-test-pinning-across-representations" in body
    assert "PYTHONDONTWRITEBYTECODE" in body
    assert "harness/integrity.py" in body
    assert "python -m pytest harness/tests" in body
    # …and the engines are not invoked. Read over the job's EXECUTABLE lines
    # only: the comments name the three binaries in order to say they are not
    # run, and a check that could not tell a comment from a command would make
    # the explanation illegal.
    executable = "\n".join(
        line for line in body.split("\n")
        if line.strip() and not line.strip().startswith("#"))
    for forbidden in ("JPACK_BIN", "OPA_BIN", "OPA_CAPS", "codex"):
        assert forbidden not in executable, (
            "§7 forbids invoking the engines in CI and the job names %s"
            % forbidden)
    assert "python -m pytest harness/tests" in executable
    assert "render_round_status.py --check" in executable
