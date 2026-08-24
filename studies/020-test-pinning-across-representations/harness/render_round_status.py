"""The round-status sentence, rendered from data rather than remembered.

**ROUND-7 FINDINGS R7-2, R7-3, R7-4 and R7-7, and the registered maintainer
decision recorded with them.** Four consecutive rounds defeated a currency guard
that tried to adjudicate English: a negated verdict attribution read as an
assertion, a denial of an open-state sentence satisfied the open-state regex, a
polarity sweep rejected a true sentence, and a Setext heading slipped past a
heading guard. The answer registered in `PREREG-REVIEW.md`'s round-7 section is
NOT a fifth parser. It is the program's own baseline (ADR 0004: navigation is
not where claims live): the round lifecycle becomes MACHINE-READABLE data, the
documents RENDER one sentence from it, and the suite compares the rendered
string to the documents verbatim — exact equality, no parsing of prose, no
polarity analysis. A document that quotes its own attestation and then denies it
is review's problem, exactly as it is in every predecessor study.

The data is the ROUND-STATE BLOCK: an HTML-comment-fenced JSON object in
`PREREG-REVIEW.md`, which is the record and therefore the authority on what each
round returned. The record's prose tables stay, for humans; the BLOCK is what
the tests read, and `harness/tests/test_prereg_currency.py` cross-checks the
block STRUCTURALLY against `reviews/round-N/`, the verbatim reviews' finding
ids, and the record's own disposition tables.

**PORTED from Study 019's `harness/render_round_status.py` with ONE registered
change (`PREREGISTRATION.md` §7, delta 10), and a narrowed surface list.**

019's `parse_block()` refused a block registering ZERO rounds, because 019 first
wrote its block after round 1 already existed. Study 020 opens its review record
BEFORE any round runs, so the empty-of-rounds block is the state this study
starts in and the port PERMITS it and renders it (`0 review rounds are on the
record …`). Every other refusal is ported unchanged: duplicate members at every
depth, closed object shapes, the closed verdict vocabulary bound to the review
prompt's output line, the single-open-round rule, contiguity, and the
marker-span reading. `harness/tests/test_prereg_currency.py` mutation-checks the
change: restore the refusal and the test that certifies the empty block fails.

Two surfaces carry the rendered sentence, each between the markers below:

    README.md, PREREGISTRATION.md

019's third front door was `design/POLICY-DRAFT.md`. It is NOT one here: 020's
policy prose is ported frozen from 019 rather than drafted in this tree, so
`design/POLICY-DRAFT.md` is a carried working document and not a front door
this study attests through.

Run at round-open and at round-close, so the ceremony commit is mechanical:

    <the pinned interpreter> harness/render_round_status.py --check
    <the pinned interpreter> harness/render_round_status.py --write

`--check` is what the suite asserts in a second way; `--write` regenerates the
sentence on all three surfaces from the block and reports which ones moved.

**ROUND-8 FINDINGS R8-3, R8-4 and R8-6 — the machine-readable surface made
actually machine-readable.** Round 7 replaced an English parser with data, and
the reviewer then attacked the data as data rather than as prose, which is the
right attack and found three holes:

* **R8-3** — the verdict was any non-empty string and was compared to nothing.
  Changing round 7's block verdict to `FREEZABLE AS WRITTEN` passed every
  structural predicate in the suite while the verbatim review still ended
  `DO NOT FREEZE`. `VERDICT_LINES` closes the vocabulary to the review prompt's
  own output contract and binds each token to the line the reviewer writes.
* **R8-4** — the block promised to refuse anything readable two ways and used
  the ordinary decoder. Duplicate members resolved last-one-wins at every
  depth, and surplus TOP-LEVEL members were accepted. `_no_duplicate_members()`
  and `_closed_object()` are the two halves of that promise, kept.
* **R8-6** — the sentence and the markers were counted independently and never
  ordered, so a correct sentence out of band satisfied the check while the
  markers enclosed something else, and `--write` over a REVERSED pair deleted
  everything between them. `marker_span()` is now the one reading both the
  check and the rewrite use.
"""

import argparse
import json
import re
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
RECORD = "PREREG-REVIEW.md"

# The two front doors (§7 delta 10). `PREREG-REVIEW.md` is deliberately NOT one
# of them: it carries the block, and a document that renders its own source can
# be made self-consistent while saying nothing true about the tree.
# `design/POLICY-DRAFT.md` was 019's third and is not one here: this study's
# policy prose is ported frozen, so that document attests nothing about 020.
SURFACES = ("README.md", "PREREGISTRATION.md")

BEGIN = "<!-- round-status:begin -->"
END = "<!-- round-status:end -->"

# The block, fenced so that a Markdown reader never sees it and a parser can
# find exactly one of it.
BLOCK_OPEN = "<!-- ROUND-STATE-BLOCK"
BLOCK_CLOSE = "ROUND-STATE-BLOCK -->"

COMPLETE = "complete"
AWAITING_REVIEW = "awaiting-review"
AWAITING_RESPONSE = "awaiting-response"
STATES = (COMPLETE, AWAITING_REVIEW, AWAITING_RESPONSE)
OPEN_STATES = (AWAITING_REVIEW, AWAITING_RESPONSE)

# ROUND-8 FINDING R8-3: the block's verdict is a PROTOCOL TOKEN, not free text.
#
# `parse_block()` accepted any non-empty string, and nothing compared the token
# to the review it claims to summarise: changing round 7's block verdict to
# `FREEZABLE AS WRITTEN` passed every structural predicate in the suite while
# the verbatim review still ended `DO NOT FREEZE`. The freeze rule reads that
# token, so an unbound verdict is the one datum in the block that could say the
# study is freezable while the record says it is not.
#
# The vocabulary is the review prompt's own output contract — "then one line
# exactly: `freezable as written`, `freezable after listed fixes`, or
# `DO NOT FREEZE`" — carried here as the three tokens the block may record,
# mapped to the exact line the reviewer is asked to write. Comparing the two is
# structural protocol parsing (a closed token set against one line), not English
# semantics: `harness/tests/test_prereg_currency.py` requires each round's block
# verdict to be the token its verbatim review's final non-blank line spells.
FREEZABLE = "FREEZABLE AS WRITTEN"
FREEZABLE_AFTER_FIXES = "FREEZABLE AFTER LISTED FIXES"
DO_NOT_FREEZE = "DO NOT FREEZE"

# `{block token: the review's own final line}`. The contract writes two of the
# three in lower case and one in upper; case is therefore not load-bearing and
# the comparison folds it, while the WORDS are exact.
VERDICT_LINES = {
    FREEZABLE: "freezable as written",
    FREEZABLE_AFTER_FIXES: "freezable after listed fixes",
    DO_NOT_FREEZE: "DO NOT FREEZE",
}
VERDICTS = tuple(VERDICT_LINES)

# The one verdict the regime accepts as a freeze authorisation (RFC 0009's
# repository-local rule, quoted in `PREREG-REVIEW.md`'s header). Named here so
# the freeze gate reads a constant rather than a spelling.
FREEZE_VERDICT = FREEZABLE

PREFIX = ("ROUND STATUS (rendered from PREREG-REVIEW.md's round-state block by "
          "harness/render_round_status.py; edit the block, never this sentence)")

_OPEN_CLAUSE = {
    AWAITING_REVIEW: "round %d is open, awaiting the reviewer's answer",
    AWAITING_RESPONSE: ("round %d is open, awaiting the maintainer's written "
                        "disposition per finding"),
}


class BlockError(Exception):
    """The block is absent, unparseable, or not the registered shape."""


def block_text(record_text):
    """The one fenced block's JSON text. Two fences, or none, is an error —
    a second block is exactly how a stale one survives beside a fresh one."""
    opens = [match.start() for match in re.finditer(re.escape(BLOCK_OPEN),
                                                    record_text)]
    closes = [match.start() for match in re.finditer(re.escape(BLOCK_CLOSE),
                                                     record_text)]
    if len(opens) != 1 or len(closes) != 1:
        raise BlockError(
            "the record must carry exactly one round-state block; found %d "
            "opening and %d closing fence(s)" % (len(opens), len(closes)))
    if closes[0] < opens[0]:
        raise BlockError("the round-state block's fences are out of order")
    return record_text[opens[0] + len(BLOCK_OPEN):closes[0]]


BLOCK_MEMBERS = ("blockVersion", "rounds")
ROUND_MEMBERS = ("number", "state", "verdict", "severities", "findings")
SEVERITIES = ("BLOCKER", "MAJOR", "MINOR")


def _no_duplicate_members(pairs):
    """ROUND-8 FINDING R8-4, first half: the object hook that makes "readable
    two ways" impossible AT EVERY DEPTH.

    `json.loads` resolves a repeated member by last-one-wins, silently. The
    block promised to refuse anything readable two ways and then read itself
    with the ordinary decoder, so a second `blockVersion` or a second `verdict`
    parsed clean and a reader of the file saw the first one. This hook runs on
    every object the decoder builds, so the refusal is not a top-level courtesy."""
    seen, out = set(), {}
    for key, value in pairs:
        if key in seen:
            raise ValueError("the member %r appears twice in one object; a "
                             "block that can be read two ways is not a "
                             "machine-readable surface" % key)
        seen.add(key)
        out[key] = value
    return out


def _closed_object(where, value, members):
    """ROUND-8 FINDING R8-4, second half: an object is EXACTLY its registered
    members. Surplus members were refused inside round entries and nowhere else,
    so a top-level member the renderer never reads sat in the block unremarked —
    which is where a second, stale, human-read copy of the lifecycle lives."""
    if not isinstance(value, dict):
        raise BlockError("%s is a JSON %s and the registered shape is an object"
                         % (where, type(value).__name__))
    surplus = sorted(set(value) - set(members))
    if surplus:
        raise BlockError("%s carries unregistered member(s) %s; the registered "
                         "shape is exactly %s"
                         % (where, ", ".join(surplus), ", ".join(members)))
    missing = [member for member in members if member not in value]
    if missing:
        raise BlockError("%s is missing the member(s) %s"
                         % (where, ", ".join(missing)))


def parse_block(record_text):
    """The block as a validated structure.

    Every shape requirement is refused rather than defaulted: a block that can
    be read two ways is not a machine-readable surface. ROUND-8 FINDING R8-4 is
    that the sentence was true of the round entries and false of everything
    else — duplicate members were resolved last-one-wins at every depth and the
    top level accepted surplus members — so the reading is now closed on both
    axes and member-by-member on type."""
    try:
        block = json.loads(block_text(record_text),
                           object_pairs_hook=_no_duplicate_members)
    except ValueError as error:
        raise BlockError("the round-state block is not readable JSON: %s" % error)
    _closed_object("the round-state block", block, BLOCK_MEMBERS)
    if not isinstance(block["rounds"], list):
        raise BlockError("the round-state block's `rounds` is a JSON %s and the "
                         "registered shape is a list"
                         % type(block["rounds"]).__name__)
    if block["blockVersion"] != 1 or isinstance(block["blockVersion"], bool):
        raise BlockError("blockVersion is %r and this study registers 1"
                         % (block["blockVersion"],))
    numbers = []
    for index, entry in enumerate(block["rounds"]):
        _closed_object("round entry %d" % index, entry, ROUND_MEMBERS)
        number = entry.get("number")
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            raise BlockError("round entry %d has no positive integer `number`"
                             % index)
        numbers.append(number)
        if entry.get("state") not in STATES:
            raise BlockError("round %d has state %r; the registered states are %s"
                             % (number, entry.get("state"), ", ".join(STATES)))
        verdict = entry.get("verdict")
        severities = entry.get("severities")
        findings = entry.get("findings")
        if entry["state"] == AWAITING_REVIEW:
            if verdict is not None or severities is not None or findings is not None:
                raise BlockError(
                    "round %d is awaiting review and cannot carry a verdict, "
                    "severity counts or a finding range" % number)
            continue
        # R8-3: a CLOSED vocabulary, so the block cannot record a verdict the
        # output contract has no line for and nothing can compare it against.
        if verdict not in VERDICTS:
            raise BlockError(
                "round %d records the verdict %r and the review prompt's output "
                "contract registers exactly %s"
                % (number, verdict, ", ".join(VERDICTS)))
        if not isinstance(severities, dict) or not severities:
            raise BlockError("round %d must record its severity counts" % number)
        for name, count in sorted(severities.items()):
            if name not in SEVERITIES:
                raise BlockError("round %d records the severity %r" % (number, name))
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                raise BlockError("round %d's %s count is %r"
                                 % (number, name, count))
        if sum(severities.values()) == 0:
            # THE CLEAN ROUND — first representable 2026-08-19, when round 12
            # returned `freezable as written` with zero findings and this
            # machinery, which had never seen a clean round, refused to encode
            # one. Zero findings have no ids, so the range is null by
            # construction rather than a degenerate {1..0}.
            if findings is not None:
                raise BlockError(
                    "round %d records zero findings by severity and must "
                    "record its finding range as null: %r" % (number, findings))
        else:
            if not isinstance(findings, dict) or set(findings) != {"first", "last"}:
                raise BlockError("round %d must record its finding range as "
                                 "{first, last}" % number)
            if findings["first"] != 1 or not isinstance(findings["last"], int) \
                    or isinstance(findings["last"], bool) \
                    or findings["last"] < 1:
                raise BlockError("round %d's finding range must start at 1 and end "
                                 "at a positive integer: %r" % (number, findings))
            if sum(severities.values()) != findings["last"]:
                raise BlockError(
                    "round %d states %d findings by severity and %d by id range"
                    % (number, sum(severities.values()), findings["last"]))
    if numbers != sorted(numbers):
        raise BlockError("the block's rounds are out of order: %s" % numbers)
    if len(set(numbers)) != len(numbers):
        raise BlockError("the block repeats a round number: %s" % numbers)
    if numbers != list(range(1, len(numbers) + 1)):
        raise BlockError("the block's rounds must be 1..N contiguous: %s" % numbers)
    # §7 DELTA 10 — THE ONE REGISTERED CHANGE TO THIS FILE. Study 019 refused a
    # block registering ZERO rounds here:
    #
    #     if not numbers:
    #         raise BlockError("the block registers no rounds")
    #
    # 019 could afford that because it first wrote the block after round 1
    # existed. Study 020 opens its review record BEFORE any round runs, so the
    # empty block is the state this study STARTS in, and a refusal on it makes
    # the port's own first act — `--write` over a record with no rounds —
    # impossible. The empty block is permitted and rendered; nothing else about
    # the reading moves, and the contiguity rule above is what keeps "empty"
    # from being a hole a partial block can hide in.
    open_rounds = [entry["number"] for entry in block["rounds"]
                   if entry["state"] in OPEN_STATES]
    if len(open_rounds) > 1:
        raise BlockError("more than one round is open: %s" % open_rounds)
    if open_rounds and open_rounds[0] != max(numbers):
        raise BlockError("round %d is open and is not the highest round (%d)"
                         % (open_rounds[0], max(numbers)))
    return block


def read_block(study=None):
    root = Path(study) if study is not None else STUDY
    return parse_block((root / RECORD).read_text(encoding="utf-8"))


def _ranges(numbers):
    """`[1, 2, 3, 5, 6, 7]` -> `"1-3 and 5-7"`. A list of runs, so the sentence
    stays one sentence however many rounds run."""
    runs, start, previous = [], None, None
    for number in sorted(numbers):
        if start is None:
            start = previous = number
            continue
        if number == previous + 1:
            previous = number
            continue
        runs.append((start, previous))
        start = previous = number
    if start is not None:
        runs.append((start, previous))
    parts = ["%d" % low if low == high else "%d-%d" % (low, high)
             for low, high in runs]
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def render(block):
    """The ONE sentence all three front doors carry verbatim.

    It states four things and nothing else: how many rounds are on the record,
    how many have returned a verdict, which rounds returned which verdict, and
    which round (if any) is open and who owes the next move."""
    rounds = block["rounds"]
    returned = [entry for entry in rounds if entry.get("verdict")]
    by_verdict = []
    for entry in returned:
        for verdict, numbers in by_verdict:
            if verdict == entry["verdict"]:
                numbers.append(entry["number"])
                break
        else:
            by_verdict.append((entry["verdict"], [entry["number"]]))
    clauses = []
    for verdict, numbers in by_verdict:
        clauses.append("%s %s returned %s"
                       % ("rounds" if len(numbers) > 1 else "round",
                          _ranges(numbers), verdict))
    open_entry = next((entry for entry in rounds
                       if entry["state"] in OPEN_STATES), None)
    tail = ("no round is open" if open_entry is None
            else _OPEN_CLAUSE[open_entry["state"]] % open_entry["number"])
    return ("%s: %d review round%s on the record, %d %s returned a verdict — %s "
            "— and %s."
            % (PREFIX,
               len(rounds), " is" if len(rounds) == 1 else "s are",
               len(returned), "has" if len(returned) == 1 else "have",
               "; ".join(clauses) if clauses else "none has returned a verdict",
               tail))


def sentence(study=None):
    return render(read_block(study))


def flat(text):
    """Whitespace collapsed and nothing else. The rendered sentence is required
    of the documents in this form so a Markdown line wrap is not a difference,
    and NOTHING else is normalised — the comparison is exact equality on the
    collapsed string, not a search over prose."""
    return " ".join(text.split())


def marker_span(relative, text):
    """ROUND-8 FINDING R8-6, first half: `(begin offset, end offset)`, or a
    named refusal.

    The markers were COUNTED and never ORDERED. `write()` then partitioned on
    the first `BEGIN` and, in the partition after it, on the first `END` — so a
    document whose markers appear END-first has an empty middle and a `tail`
    that starts after the `END`, and rewriting it DISCARDED everything between
    the two markers, which on a reversed pair is the whole body of the document.
    Order is checked here, once, and both `surface_problems()` and `write()` ask
    this function rather than counting for themselves."""
    begins = [match.start() for match in re.finditer(re.escape(BEGIN), text)]
    ends = [match.start() for match in re.finditer(re.escape(END), text)]
    if len(begins) != 1 or len(ends) != 1:
        return None, ("%s must carry exactly one %s / %s marker pair; it "
                      "carries %d and %d"
                      % (relative, BEGIN, END, len(begins), len(ends)))
    if ends[0] < begins[0]:
        return None, ("%s carries its round-status markers in the order %s … "
                      "%s; the sentence lives BETWEEN them, and rewriting a "
                      "reversed pair would delete the text they enclose"
                      % (relative, END, BEGIN))
    return (begins[0], ends[0]), None


def surface_problems(study=None):
    """Every front door that does not carry the rendered sentence exactly once,
    between its markers, and nowhere else.

    ROUND-8 FINDING R8-6, second half: the sentence and the markers were counted
    INDEPENDENTLY, so a document carrying the correct sentence anywhere at all
    and a marker pair anywhere at all passed — including a pair in the wrong
    order, and including a copy of the sentence out of band while the markers
    enclosed something else. The markers are what `--write` regenerates, so what
    they enclose is what this study attests; a copy outside them is a second,
    unregenerated attestation that the next round leaves stale."""
    root = Path(study) if study is not None else STUDY
    wanted = flat(sentence(study))
    problems = []
    for relative in SURFACES:
        path = root / relative
        if not path.is_file():
            problems.append("%s does not exist" % relative)
            continue
        text = path.read_text(encoding="utf-8")
        span, refusal = marker_span(relative, text)
        if refusal is not None:
            problems.append(refusal)
            continue
        begin, end = span
        enclosed = flat(text[begin + len(BEGIN):end])
        if enclosed != wanted:
            problems.append(
                "%s's round-status markers enclose %r and the block renders "
                "%r; run `python harness/render_round_status.py --write`"
                % (relative, enclosed, wanted))
        for where, outside in (("before", text[:begin]),
                               ("after", text[end + len(END):])):
            if wanted in flat(outside):
                problems.append(
                    "%s carries a second copy of the rendered round-status "
                    "sentence %s its markers; only the enclosed one is "
                    "regenerated, so the other goes stale silently"
                    % (relative, where))
    return problems


def write(study=None):
    """Replace the text between the markers on every surface. Returns the
    surfaces that moved. Refuses a surface whose markers are absent OR out of
    order rather than guessing where the sentence goes (R8-6): a rewrite that
    can delete the document's body is not a mechanical ceremony."""
    root = Path(study) if study is not None else STUDY
    wanted = sentence(study)
    moved = []
    for relative in SURFACES:
        path = root / relative
        text = path.read_text(encoding="utf-8")
        span, refusal = marker_span(relative, text)
        if refusal is not None:
            raise BlockError(
                "%s; add the pair by hand once, in order, and this command "
                "keeps it current afterwards" % refusal)
        begin, end = span
        updated = "%s%s\n%s\n%s" % (text[:begin], BEGIN, wanted, text[end:])
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            moved.append(relative)
    return moved


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--print", dest="show", action="store_true",
                        help="print the rendered sentence")
    parser.add_argument("--check", action="store_true",
                        help="verify all three front doors carry it verbatim")
    parser.add_argument("--write", action="store_true",
                        help="regenerate it on all three front doors")
    arguments = parser.parse_args(argv)
    try:
        if arguments.write:
            moved = write()
            print("rewritten: %s" % (", ".join(moved) if moved else "nothing moved"))
        if arguments.show or not (arguments.write or arguments.check):
            print(sentence())
        if arguments.check:
            problems = surface_problems()
            for problem in problems:
                print(problem)
            return 1 if problems else 0
    except BlockError as error:
        print("refused: %s" % error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
