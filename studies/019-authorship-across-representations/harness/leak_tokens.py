#!/usr/bin/env python3
"""`LEAK_TOKENS`, RE-DERIVED from the stimulus prose — SCAFFOLD item G3.

**Assembled from design, not ported.** There is no Study 012 source for this
file: 012's `LEAK_TOKENS` was a curated tuple in `harness/transcript_check.py`
and this study registers that the list must be *derived* from the frozen policy
prose, with a committed checker showing it has power on mutated inputs — the
same standard §3 already applies to the language-materials checkers. Its design
lineage is the stimulus itself: `design/POLICY-DRAFT.md` v0.3, whose sha256 at
derivation time is published by `report()` under `source.sha256` and asserted by
`harness/tests/test_leak_tokens.py` against the file this module reads.
`harness/transcript_check.py`'s tuple is the design-time list this supersedes;
`design_time_gap()` names, mechanically, what the freeze must copy across.

WHY DERIVED. A curated denylist is a list of the terms whoever wrote it happened
to think of. The claim the screen is asked to support — "no turn before the
prompt had seen the policy" — is a claim about the POLICY's vocabulary, so the
vocabulary has to be read out of the policy. Re-derivation also makes the list
answer to the prose: change a threshold in the source and the derived list
moves, which `check_rederivation()` demonstrates rather than asserts.

THE SLICE IS THE SOURCE'S OWN. `design/POLICY-DRAFT.md` marks the boundary
itself — everything from `## Vendor Approval Policy` to
`## Design notes (not part of the stimulus)` is the stimulus; the design notes
after it are not, and deriving tokens from them would deny the model the
vocabulary of a document it never sees. Both markers are required to occur
exactly once, so a re-heading of the file refuses rather than silently moving
the slice. `policy/POLICY.md` supersedes the draft the moment the freeze copies
it into place (`SOURCES` is ordered, `source_path()` takes the first that
exists), and the derivation is otherwise unchanged.

THE THREE REGISTERED RULES, and nothing else:

  R1 `domain_nouns()`  — every `**bold**` span and every `` `backticked` ``
     identifier in the slice. Those are the prose's OWN markup for a named
     term: the input names, the four outcome ids and the unresolved kinds, the
     clause headings' labels, and O3's queue name. A clause heading contributes
     its LABEL (`P1 — Financial evidence.` gives `financial evidence`), because
     the id is R2's business.
  R2 `clause_ids()`    — every `[PDOU]<digit>[a-c]?` token in the slice:
     p1, d1…d8, d6a, d6b, d6c, o1, o2, o3, u1.
  R3 `thresholds()`    — every numeric literal in a sentence that carries one of
     the registered comparison phrases (`COMPARISON_PHRASES`), which is what
     makes a numeral a THRESHOLD rather than a range endpoint in the Inputs list
     or an index in a worked example — plus, for each, the spellings a leaking
     turn could use: the punctuated form, a `$`-prefixed form, the bare integer
     digits, and the English words (`spellings()`).

ADMISSIBILITY, and the two residuals it buys. A candidate is a token only if it
survives `admissible()`:

  * at least `MIN_TOKEN_CHARS` characters, **unless it is a clause id** — the
    one class this study registers that is short by construction, exempted by
    name and reported by `report()` under `shortExempt` rather than smuggled in;
  * at most `MAX_TOKEN_WORDS` words — U1's rule is a bolded SENTENCE, and a
    sentence is not a token;
  * not itself a bare clause id (R2 owns those) and not empty after
    normalization;
  * if it is a BARE numeral — digits with no separator — its longest run of
    digits is at least `MIN_BARE_DIGIT_RUN`. `2,000,000.00` and `$500,000.00`
    are not bare and are admitted whole; this is the rule that keeps `40`, `70`
    and `90` OUT.
    They are the risk-score thresholds and they are genuinely policy content —
    but the wrapper screens the SCRATCH PATH with this list, that path ends in
    the wrapper's own pid, and a two-digit token would refuse something like one
    honest call in ten for a reason that is not about the call. The thresholds
    survive as `forty`, `seventy` and `ninety`; the digit forms do not, and
    `report()["dropped"]` says so by name.

RESIDUALS, stated rather than implied.

  1. A prior turn that writes "the threshold is 70" is not caught. The denylist
     is a BACKSTOP; `transcript_check.check_golden()`'s allowlist is the
     instrument — its own docstring says why ("a paraphrase … none of them need
     to contain a banned token to leak, but all of them change the context").
  2. `review`, `approve`, `reject` and `unresolved` are ordinary English words
     as well as this policy's outcome ids, and they are derived, so they are
     here. If codex's own boilerplate ever carried one, the GOLDEN CAPTURE would
     refuse first — `batch.capture_golden()` runs `screen_prior_context()` over
     every probe capture — so the failure is pre-batch, visible, and costs no
     slot. That is checked at capture time and is not assumed here.
  3. The state values (`CLEAR`, `MATCH`, `UNKNOWN`, `LOW`, `MEDIUM`, `HIGH`) are
     deliberately NOT derived: they are unmarked ALL-CAPS words in the prose,
     three of them are among the commonest words in any agent preamble, and R1
     already carries the input each of them is a state of. The omission is
     registered here rather than left to be read off the output.
  4. `check_negative_corpus()` proves no token fires on the names the wrapper
     itself constructs, for every arm and every slot index — but a pid of six or
     more digits can still contain `100000`, `500000` or `2000000`. That refusal
     is pre-call, spends nothing, and the operator re-runs; it is named here so
     it is a recorded residual and not a surprise.

POWER, which is what makes this a checker and not a list. `check_power()`
requires: the derived list catches EVERY witness — a witness being a sentence of
the normative sections that the SOURCE'S OWN MARKUP says names something, so the
witness set is built by a rule the token set does not share, and a filter that
dropped a load-bearing candidate shows up as an uncaught witness; a scrambled
list catches strictly fewer; the empty list catches none. `check_rederivation()`
adds the other direction: mutate a threshold in the source text and the derived
list must move with it.

Run: <the pinned interpreter> harness/leak_tokens.py [--report]
"""
from __future__ import annotations
import json
import os
import re
import sys

# The DERIVATION's source is the study's own prose, so this file resolves its
# study through the symlinks an invocation may reach it by (`realpath`, as
# `make_manifest.py` does) rather than following the invocation path the way
# `batch.py`'s population root deliberately does. A stand-in study symlinks the
# committed harness in; the policy it derives from is still this study's.
HERE = os.path.dirname(os.path.realpath(__file__))
STUDY = os.path.dirname(HERE)

# In order: the frozen prose once it exists, then the frozen CANDIDATE. The
# freeze copies `design/POLICY-DRAFT.md` to `policy/POLICY.md` (SCAFFOLD F step
# 2) and this list is re-derived from the frozen copy at that point, with no
# edit here.
SOURCES = ("policy/POLICY.md", "design/POLICY-DRAFT.md")

# The source's own boundary markers. Each must occur exactly once.
STIMULUS_BEGIN = "## Vendor Approval Policy"
STIMULUS_END = "## Design notes (not part of the stimulus)"

# The normative sections the witness set is drawn from — the source's own
# headings, again, and not a slice this file chooses.
NORMATIVE_HEADINGS = ("### Precondition", "### Determination clauses",
                      "### Overrides", "### Unreadable inputs")

# R3: what makes a numeral a threshold. A numeral in a sentence carrying none of
# these is a range endpoint (`an integer from 0 to 100`) or an index in a worked
# example, not a bound the policy compares against.
COMPARISON_PHRASES = ("or above", "at least", "below", "above",
                      "up to and including")

MIN_TOKEN_CHARS = 4
MAX_TOKEN_WORDS = 8
MIN_BARE_DIGIT_RUN = 4
# What makes a numeral something other than a BARE one. `2,000,000.00` carries
# both; `40` carries neither.
SEPARATORS = ",."

CLAUSE_ID = re.compile(r"\b([PDOU]\d[a-c]?)\b")
BOLD = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
BACKTICKED = re.compile(r"`([^`\n]+)`")
# A numeral may not END on its separator: `below 70, and` carries the numeral
# `70` and a clause comma, and a pattern that swallowed the comma derived the
# token `70,` — a spelling the prose does not contain and no turn would write.
NUMERAL = re.compile(r"(?<![0-9A-Za-z.,])\$?(\d(?:[\d,]*\d)?(?:\.\d+)?)")
DIGIT_RUN = re.compile(r"\d+")
SENTENCE = re.compile(r"(?<=[.:;])\s+|\n+")


class LeakTokenError(Exception):
    """A refusal from the derivation or from one of its checks."""


# --- reading the source -----------------------------------------------------

def source_path(study: str = STUDY) -> str:
    for relative in SOURCES:
        path = os.path.join(study, relative)
        if os.path.isfile(path):
            return path
    raise LeakTokenError(
        "no policy prose at any of %s: the leak-token list is derived from the "
        "stimulus and cannot be derived from nothing"
        % ", ".join(SOURCES))


def source_text(study: str = STUDY) -> str:
    with open(source_path(study), "rb") as handle:
        return handle.read().decode("utf-8")


def stimulus(text: str) -> str:
    """The stimulus slice, between the source's own two boundary markers.

    Each marker is required to occur EXACTLY once. A source that grew a second
    `## Design notes` heading, or renamed the first, refuses here rather than
    deriving the list from a slice nobody chose."""
    for marker in (STIMULUS_BEGIN, STIMULUS_END):
        found = text.count(marker)
        if found != 1:
            raise LeakTokenError(
                "the policy prose carries %d occurrences of %r and the stimulus "
                "slice is identified by that heading occurring once"
                % (found, marker))
    begin = text.index(STIMULUS_BEGIN)
    end = text.index(STIMULUS_END)
    if end <= begin:
        raise LeakTokenError(
            "the policy prose puts %r before %r: the stimulus slice runs from "
            "the first to the second" % (STIMULUS_END, STIMULUS_BEGIN))
    return text[begin:end]


# --- number words -----------------------------------------------------------

_UNITS = ("zero", "one", "two", "three", "four", "five", "six", "seven",
          "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
          "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
_TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
         "eighty", "ninety")


def _under_thousand(value: int) -> str:
    if value < 20:
        return _UNITS[value]
    if value < 100:
        return _TENS[value // 10] + ("-" + _UNITS[value % 10] if value % 10 else "")
    rest = value % 100
    return _UNITS[value // 100] + " hundred" + (" " + _under_thousand(rest) if rest else "")


def words(value: int) -> str:
    """`40` -> `forty`, `2000000` -> `two million`. Covers 0…999,999,999, which
    is every value this policy's own bounds can produce (`$10,000,000.00` is the
    largest numeral in the prose and no threshold exceeds `$2,000,000.00`)."""
    if not 0 <= value <= 999999999:
        raise LeakTokenError("no word form is derived for %d" % value)
    if value == 0:
        return _UNITS[0]
    parts = []
    for size, name in ((1000000, "million"), (1000, "thousand")):
        if value >= size:
            parts.append(_under_thousand(value // size) + " " + name)
            value %= size
    if value:
        parts.append(_under_thousand(value))
    return " ".join(parts)


def spellings(literal: str) -> list:
    """Every form of one threshold a leaking turn could write: the punctuated
    form as the prose writes it, that form with a `$`, the bare integer digits,
    and the English words. Admissibility drops whichever of them are not
    evidence — for `40` that is every form but `forty`."""
    integral = int(literal.replace(",", "").split(".")[0])
    forms = [literal, "$" + literal, str(integral), words(integral)]
    if "." in literal:
        forms.append(literal.split(".")[0])
        forms.append("$" + literal.split(".")[0])
    return forms


# --- the three rules --------------------------------------------------------

def _normalize(candidate: str) -> str:
    """One line, lowercased, the clause-id lead-in of a heading removed, and
    the surrounding punctuation stripped."""
    text = " ".join(candidate.replace("\n", " ").split())
    text = re.sub(r"^[PDOU]\d[a-c]?\s*[—–-]?\s*", "", text)
    return text.strip().strip(".,;:—–-").lower()


def domain_nouns(slice_text: str) -> list:
    """R1: the prose's own markup for a named term — bold spans and backticked
    identifiers, normalized."""
    found = []
    for candidate in BOLD.findall(slice_text) + BACKTICKED.findall(slice_text):
        normalized = _normalize(candidate)
        if normalized and normalized not in found:
            found.append(normalized)
    return found


def clause_ids(slice_text: str) -> list:
    """R2: p1, d1…d8, d6a…d6c, o1…o3, u1 — derived, not listed."""
    found = []
    for candidate in CLAUSE_ID.findall(slice_text):
        lowered = candidate.lower()
        if lowered not in found:
            found.append(lowered)
    return sorted(found)


def threshold_literals(slice_text: str) -> list:
    """R3's numerals, as the prose writes them: every numeric literal in a
    sentence carrying a registered comparison phrase."""
    found = []
    for sentence in SENTENCE.split(slice_text):
        lowered = sentence.lower()
        if not any(phrase in lowered for phrase in COMPARISON_PHRASES):
            continue
        for literal in NUMERAL.findall(sentence):
            if literal not in found:
                found.append(literal)
    return sorted(found, key=lambda text: (len(text), text))


def thresholds(slice_text: str) -> list:
    """R3: the threshold numerals AND their spellings."""
    found = []
    for literal in threshold_literals(slice_text):
        for form in spellings(literal):
            if form not in found:
                found.append(form)
    return found


# --- admissibility ----------------------------------------------------------

def is_clause_id(candidate: str) -> bool:
    return bool(re.fullmatch(r"[pdou]\d[a-c]?", candidate))


def admissible(candidate: str, clause_id: bool = False) -> str:
    """None when the candidate is a token, or the REASON it is not.

    A reason rather than a boolean, because `report()` publishes every drop
    beside the rule that proposed it: a derivation whose filter is invisible is
    a curated list wearing a derivation's clothes."""
    if not candidate:
        return "empty after normalization"
    if not clause_id and is_clause_id(candidate):
        return "a bare clause id (rule R2 owns those)"
    if len(candidate.split()) > MAX_TOKEN_WORDS:
        return "%d words; a sentence is not a token (max %d)" % (
            len(candidate.split()), MAX_TOKEN_WORDS)
    # The bare-numeral clause runs BEFORE the length floor, so a two-digit
    # threshold is dropped for the reason that is actually about it rather than
    # for the length it happens also to fail. The reasons are published.
    if not any(character.isalpha() for character in candidate) \
            and not any(character in SEPARATORS for character in candidate):
        # A BARE numeral: digits with no separator. `2,000,000.00` is not one —
        # its commas and cents make it a spelling no path and no ordinary
        # sentence produces by accident — but `40` is, and `40` would fire on
        # the wrapper's own pid.
        longest = max((len(run) for run in DIGIT_RUN.findall(candidate)), default=0)
        if longest < MIN_BARE_DIGIT_RUN:
            return ("a bare numeral whose longest digit run is %d; a run "
                    "shorter than %d is not evidence and would fire on the "
                    "wrapper's own pid" % (longest, MIN_BARE_DIGIT_RUN))
    if not clause_id and len(candidate) < MIN_TOKEN_CHARS:
        return "shorter than %d characters" % MIN_TOKEN_CHARS
    return None


# --- the derivation ---------------------------------------------------------

def derive(slice_text: str) -> dict:
    """The three rules, filtered, with every drop recorded.

    Returns `{"tokens": (...), "byRule": {...}, "dropped": [...],
    "shortExempt": [...]}`. `tokens` is sorted so the list is a function of the
    prose and not of the order the rules happened to run in."""
    proposals = (("R1 domain nouns", domain_nouns(slice_text), False),
                 ("R2 clause ids", clause_ids(slice_text), True),
                 ("R3 thresholds", thresholds(slice_text), False))
    tokens, by_rule, dropped, short = [], {}, [], []
    for rule, candidates, clause_id in proposals:
        kept = []
        for candidate in candidates:
            reason = admissible(candidate, clause_id=clause_id)
            if reason is not None:
                dropped.append((rule, candidate, reason))
                continue
            if clause_id and len(candidate) < MIN_TOKEN_CHARS:
                short.append(candidate)
            kept.append(candidate)
            if candidate not in tokens:
                tokens.append(candidate)
        by_rule[rule] = tuple(kept)
    return {"tokens": tuple(sorted(tokens)), "byRule": by_rule,
            "dropped": tuple(dropped), "shortExempt": tuple(sorted(short))}


def derived(study: str = STUDY) -> dict:
    return derive(stimulus(source_text(study)))


LEAK_TOKENS = derived()["tokens"]

# The INSTRUMENT vocabulary — this study's own apparatus, which the derivation
# cannot produce and which no rule here could.
#
# The three derivation rules read the STIMULUS, and the stimulus is a vendor
# approval policy: by construction it says nothing about jpack, the
# preregistration, the mutant machinery or the scored surface's member names. A
# prior turn that had seen any of THOSE had seen this study, and a scratch path
# naming one would blunt the transcript screen exactly as a policy term would.
# So the screen is the UNION, and this half is a design-time list ON PURPOSE and
# says so: it is not derived, it is not claimed to be derived, and
# `report()["instrument"]` publishes it separately from the derived tokens so a
# reader can always see which half of the screen answers to the prose.
#
# `check_instrument_power()` below is what keeps it from being decoration: the
# instrument half alone must catch strictly FEWER stimulus witnesses than the
# derived half, which is the mechanical statement that it is not doing the
# policy half's job by accident.
INSTRUMENT_TOKENS = (
    # The study and its instruments
    "judgment-pack", "jpack", "pack.json", "judgment pack", "matrixversion",
    "specversion", "preregistration", "study-019", "study 019",
    "authorship across representations",
    # The scored surface's registered member names (the naming appendix's
    # spellings, which are identifiers rather than policy prose)
    "outcomeid", "onunknown", "applicability", "evidencerequirements",
    "sourcerefs",
    # The mutation machinery and the endpoints
    "mutant", "kill rate", "high-kill", "gold suite", "identity control",
    "witness set", "paired adequate",
)

# What BOTH screens read: the derived policy vocabulary and the instrument
# vocabulary, in one place (SCAFFOLD item G3's residual). The wrapper screens
# the scratch path with it and `transcript_check.LEAK_TOKENS` IS it — there is
# no second list anywhere in the study, so the two screens cannot drift and the
# freeze's re-derivation moves both at once.
SCREEN_TOKENS = tuple(sorted(set(LEAK_TOKENS) | set(INSTRUMENT_TOKENS)))
# The name the wrapper reads (harness/PORTS.md's fifth registered difference).
SCRATCH_TOKENS = SCREEN_TOKENS


def design_time_gap(study: str = STUDY) -> dict:
    """The gap between the DERIVED list and the screen the study actually uses.

    It was the freeze's to-do list while `transcript_check.LEAK_TOKENS` was a
    separate design-time tuple: which derived tokens the screen did not carry,
    and which screen tokens the derivation did not produce. It is a STANDING
    check now that the screen is built from the derivation — the first list must
    be empty, always, and the second must be exactly `INSTRUMENT_TOKENS` — and
    `harness/tests/test_leak_tokens.py` asserts both, so a token added to the
    screen by hand has nowhere to hide."""
    tokens = set(derived(study)["tokens"])
    screen = set(SCREEN_TOKENS)
    return {"missingFromDesignTime": tuple(sorted(tokens - screen)),
            "designTimeOnly": tuple(sorted(screen - tokens))}


# --- power ------------------------------------------------------------------

def normative_slice(slice_text: str) -> str:
    """The stimulus from its first normative heading onward — the sections whose
    sentences are the witnesses."""
    positions = [slice_text.index(heading) for heading in NORMATIVE_HEADINGS
                 if heading in slice_text]
    if len(positions) != len(NORMATIVE_HEADINGS):
        raise LeakTokenError(
            "the stimulus does not carry all of %s: the witness set is drawn "
            "from the source's own normative headings"
            % ", ".join(NORMATIVE_HEADINGS))
    return slice_text[min(positions):]


def witnesses(slice_text: str) -> list:
    """Every sentence of the normative sections that the SOURCE'S OWN MARKUP
    says names something: it carries a clause id, a bold span or a backticked
    identifier in its RAW text.

    The witness rule and the token rule are deliberately different rules over
    the same bytes. Tokens survive normalization and `admissible()`; witnesses
    are selected before either runs. So a filter that dropped a load-bearing
    candidate does not also remove the sentence that needed it, and the
    coverage below is a real check rather than a tautology."""
    found = []
    for sentence in SENTENCE.split(normative_slice(slice_text)):
        text = sentence.strip()
        if not text or text.startswith("###"):
            continue
        if CLAUSE_ID.search(text) or BOLD.search(text) or BACKTICKED.search(text):
            found.append(text)
    return found


def catches(tokens, text: str) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in tokens)


def uncaught(tokens, sentences) -> list:
    return [sentence for sentence in sentences if not catches(tokens, sentence)]


def scramble(tokens) -> tuple:
    """A list of the same size that matches nothing: every token's last
    character replaced by a character the stimulus does not use. Deliberately
    not a TRUNCATION — a shorter token is a substring of the original and would
    match MORE, which would make the mutant look stronger than the list it
    weakens."""
    return tuple(token[:-1] + "§" for token in tokens)


def power_report(study: str = STUDY) -> dict:
    slice_text = stimulus(source_text(study))
    tokens = derive(slice_text)["tokens"]
    sentences = witnesses(slice_text)
    return {
        "witnesses": len(sentences),
        "baselineUncaught": tuple(uncaught(tokens, sentences)),
        "scrambledCaught": len(sentences) - len(uncaught(scramble(tokens), sentences)),
        "emptyCaught": len(sentences) - len(uncaught((), sentences)),
        "baselineCaught": len(sentences) - len(uncaught(tokens, sentences)),
    }


def check_power(study: str = STUDY) -> dict:
    """The registered power property, or LeakTokenError.

    Three clauses: the derived list catches every witness; a scrambled list of
    the same size catches strictly fewer; the empty list catches none. The
    second is the one that makes this a demonstration — a list with no power
    would catch the same witnesses scrambled as unscrambled, because it would be
    catching them for some reason other than its own bytes."""
    report = power_report(study)
    if report["baselineUncaught"]:
        raise LeakTokenError(
            "%d of %d witness sentences carry a term the source's own markup "
            "names and the derived list does not catch: %r. Either a rule or "
            "the admissibility filter dropped something load-bearing"
            % (len(report["baselineUncaught"]), report["witnesses"],
               list(report["baselineUncaught"][:3])))
    if report["scrambledCaught"] >= report["baselineCaught"]:
        raise LeakTokenError(
            "a scrambled list of the same size catches %d of %d witnesses and "
            "the derived list catches %d: the list is not what is doing the "
            "catching" % (report["scrambledCaught"], report["witnesses"],
                          report["baselineCaught"]))
    if report["emptyCaught"]:
        raise LeakTokenError("the empty list caught %d witnesses"
                             % report["emptyCaught"])
    return report


def instrument_power_report(study: str = STUDY) -> dict:
    """How many stimulus witnesses each half of the screen catches on its own."""
    slice_text = stimulus(source_text(study))
    sentences = witnesses(slice_text)
    tokens = derive(slice_text)["tokens"]
    return {
        "witnesses": len(sentences),
        "derivedCaught": len(sentences) - len(uncaught(tokens, sentences)),
        "instrumentCaught": len(sentences) - len(uncaught(INSTRUMENT_TOKENS,
                                                          sentences)),
        "screenCaught": len(sentences) - len(uncaught(SCREEN_TOKENS, sentences)),
    }


def check_instrument_power(study: str = STUDY) -> dict:
    """The power check the COMPOSED screen owes (SCAFFOLD item G3's residual).

    `check_power()` demonstrates that the derived list is what catches the
    stimulus's witnesses. This demonstrates the other half of the composition:
    the instrument vocabulary alone catches strictly FEWER of them, so the
    screen's policy power comes from the derivation and not from a design-time
    tuple that happens to overlap it — and the union still catches every witness,
    so adding the instrument half cannot have cost the screen anything."""
    report = instrument_power_report(study)
    if report["instrumentCaught"] >= report["derivedCaught"]:
        raise LeakTokenError(
            "the instrument vocabulary alone catches %d of %d witnesses and the "
            "derived list catches %d: the screen's policy power is not coming "
            "from the derivation"
            % (report["instrumentCaught"], report["witnesses"],
               report["derivedCaught"]))
    if report["screenCaught"] != report["witnesses"]:
        raise LeakTokenError(
            "the composed screen catches %d of %d witnesses: composing the two "
            "halves must not lose any"
            % (report["screenCaught"], report["witnesses"]))
    return report


def check_rederivation(study: str = STUDY) -> dict:
    """The other direction: the list is a FUNCTION of the prose.

    Move a threshold in the source text and the derived list must move with it.
    A curated list would not — which is exactly the property that distinguishes
    this file from the tuple it supersedes."""
    text = source_text(study)
    slice_text = stimulus(text)
    before = set(derive(slice_text)["tokens"])
    literals = threshold_literals(slice_text)
    if not literals:
        raise LeakTokenError("the stimulus carries no threshold numerals")
    # The largest threshold, moved to a value the prose does not otherwise use.
    original = literals[-1]
    mutated_literal = "3" + original[1:]
    mutated = derive(stimulus(text.replace(original, mutated_literal)))["tokens"]
    after = set(mutated)
    if before == after:
        raise LeakTokenError(
            "replacing the threshold %r with %r left the derived list "
            "unchanged: the list is not a function of the prose"
            % (original, mutated_literal))
    return {"threshold": original, "mutatedTo": mutated_literal,
            "gained": tuple(sorted(after - before)),
            "lost": tuple(sorted(before - after))}


# --- the negative corpus ----------------------------------------------------

# The names `harness/authoring_call.sh` constructs under the scratch parent, as
# format strings. A token that fires on one of these refuses honest calls, so
# the corpus is the wrapper's own output and not a guess about the operator's
# filesystem.
WRAPPER_NAME_TEMPLATES = ("s019-authoring-%(arm)s-%(slot)s-%(pid)d",
                          "s019-home-%(arm)s-%(slot)s-%(pid)d",
                          "s019-bin-%(arm)s-%(slot)s-%(pid)d",
                          "s019-c7-raw-%(pid)d")


def negative_corpus(arms=("A", "B", "C", "none"), slots=range(1, 151),
                    pids=(1, 999, 12345, 99999)) -> list:
    """Every name the wrapper builds, over every arm and every registered slot
    index. Not exhaustive over pids, and `check_negative_corpus()` says so."""
    names = []
    for template in WRAPPER_NAME_TEMPLATES:
        for arm in arms:
            for slot in slots:
                for pid in pids:
                    names.append(template % {"arm": arm,
                                             "slot": "run-%03d" % slot,
                                             "pid": pid})
    return names


def check_negative_corpus(tokens=None) -> int:
    """No token fires on a name the wrapper itself constructs.

    NOT a proof over every pid: `100000`, `500000` and `2000000` are tokens, and
    a pid of six or more digits can contain one. That refusal is pre-call and
    spends nothing — it is recorded in this module's docstring as residual 4
    rather than defended against."""
    tokens = LEAK_TOKENS if tokens is None else tokens
    names = negative_corpus()
    for name in names:
        lowered = name.lower()
        firing = sorted(token for token in tokens if token in lowered)
        if firing:
            raise LeakTokenError(
                "the derived token(s) %r fire on %r, a name the wrapper builds "
                "for every call: this list would refuse honest runs"
                % (firing, name))
    return len(names)


# --- entry point ------------------------------------------------------------

def report(study: str = STUDY) -> dict:
    path = source_path(study)
    import hashlib
    with open(path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    result = derived(study)
    return {"source": {"path": os.path.relpath(path, study),
                       "sha256": "sha256:" + digest},
            "tokens": list(result["tokens"]),
            "byRule": {rule: list(kept) for rule, kept in result["byRule"].items()},
            "shortExempt": list(result["shortExempt"]),
            "dropped": [{"rule": rule, "candidate": candidate, "reason": reason}
                        for rule, candidate, reason in result["dropped"]],
            "instrument": list(INSTRUMENT_TOKENS),
            "screen": list(SCREEN_TOKENS),
            "power": {key: (list(value) if isinstance(value, tuple) else value)
                      for key, value in power_report(study).items()},
            "instrumentPower": instrument_power_report(study),
            "designTimeGap": {key: list(value)
                              for key, value in design_time_gap(study).items()}}


def main(argv: list) -> int:
    try:
        if "--report" in argv:
            print(json.dumps(report(), indent=2, sort_keys=True))
            return 0
        check_power()
        check_instrument_power()
        check_rederivation()
        checked = check_negative_corpus()
        print("%d leak tokens derived from %s; %d in the composed screen "
              "(+%d instrument)"
              % (len(LEAK_TOKENS), os.path.relpath(source_path(), STUDY),
                 len(SCREEN_TOKENS), len(INSTRUMENT_TOKENS)))
        print("power: every witness caught, a scrambled list catches fewer, "
              "the empty list none, the instrument half alone fewer")
        print("negative corpus: %d wrapper-built names, none matched" % checked)
        return 0
    except LeakTokenError as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
