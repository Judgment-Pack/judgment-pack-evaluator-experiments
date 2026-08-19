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

Three surfaces carry the rendered sentence, each between the markers below:

    README.md, PREREGISTRATION.md, design/POLICY-DRAFT.md

Run at round-open and at round-close, so the ceremony commit is mechanical:

    <the pinned interpreter> harness/render_round_status.py --check
    <the pinned interpreter> harness/render_round_status.py --write

`--check` is what the suite asserts in a second way; `--write` regenerates the
sentence on all three surfaces from the block and reports which ones moved.
"""

import argparse
import json
import re
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
RECORD = "PREREG-REVIEW.md"

# The three front doors. `PREREG-REVIEW.md` is deliberately NOT one of them: it
# carries the block, and a document that renders its own source can be made
# self-consistent while saying nothing true about the tree.
SURFACES = ("README.md", "PREREGISTRATION.md", "design/POLICY-DRAFT.md")

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


def parse_block(record_text):
    """The block as a validated structure.

    Every shape requirement is refused rather than defaulted: a block that can
    be read two ways is not a machine-readable surface."""
    try:
        block = json.loads(block_text(record_text))
    except ValueError as error:
        raise BlockError("the round-state block is not readable JSON: %s" % error)
    if not isinstance(block, dict) or not isinstance(block.get("rounds"), list):
        raise BlockError("the round-state block must be an object with a "
                         "`rounds` list")
    if block.get("blockVersion") != 1:
        raise BlockError("blockVersion is %r and this study registers 1"
                         % block.get("blockVersion"))
    numbers = []
    for index, entry in enumerate(block["rounds"]):
        if not isinstance(entry, dict):
            raise BlockError("round entry %d is not an object" % index)
        surplus = sorted(set(entry) - {"number", "state", "verdict",
                                       "severities", "findings"})
        if surplus:
            raise BlockError("round entry %d carries unregistered member(s) %s"
                             % (index, ", ".join(surplus)))
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
        if not isinstance(verdict, str) or not verdict.strip():
            raise BlockError("round %d must record the verdict it returned"
                             % number)
        if not isinstance(severities, dict) or not severities:
            raise BlockError("round %d must record its severity counts" % number)
        for name, count in sorted(severities.items()):
            if name not in ("BLOCKER", "MAJOR", "MINOR"):
                raise BlockError("round %d records the severity %r" % (number, name))
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                raise BlockError("round %d's %s count is %r"
                                 % (number, name, count))
        if not isinstance(findings, dict) or set(findings) != {"first", "last"}:
            raise BlockError("round %d must record its finding range as "
                             "{first, last}" % number)
        if findings["first"] != 1 or not isinstance(findings["last"], int) \
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
    if not numbers:
        raise BlockError("the block registers no rounds")
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


def surface_problems(study=None):
    """Every front door that does not carry the rendered sentence exactly once,
    and every one whose markers are missing (the markers are what `--write`
    replaces between)."""
    root = Path(study) if study is not None else STUDY
    wanted = flat(sentence(study))
    problems = []
    for relative in SURFACES:
        path = root / relative
        if not path.is_file():
            problems.append("%s does not exist" % relative)
            continue
        text = path.read_text(encoding="utf-8")
        count = flat(text).count(wanted)
        if count != 1:
            problems.append(
                "%s must carry the rendered round-status sentence exactly once, "
                "verbatim; it carries it %d time(s)" % (relative, count))
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            problems.append(
                "%s must carry exactly one %s / %s marker pair"
                % (relative, BEGIN, END))
    return problems


def write(study=None):
    """Replace the text between the markers on every surface. Returns the
    surfaces that moved. Refuses a surface whose markers are absent rather than
    guessing where the sentence goes."""
    root = Path(study) if study is not None else STUDY
    wanted = sentence(study)
    moved = []
    for relative in SURFACES:
        path = root / relative
        text = path.read_text(encoding="utf-8")
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            raise BlockError(
                "%s carries %d/%d round-status markers; add the pair by hand "
                "once, and this command keeps it current afterwards"
                % (relative, text.count(BEGIN), text.count(END)))
        head, _, rest = text.partition(BEGIN)
        _, _, tail = rest.partition(END)
        updated = "%s%s\n%s\n%s%s" % (head, BEGIN, wanted, END, tail)
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
