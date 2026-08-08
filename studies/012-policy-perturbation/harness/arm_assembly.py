#!/usr/bin/env python3
"""Appendix A's registered assembly rule, in code, plus the text properties
§6 C8 checks over the assembled bytes.

PREREGISTRATION.md Appendix A publishes the five arm texts as fenced blocks and
registers the rule that turns them into artifacts:

    POLICY.md = PREAMBLE + "\\n\\n" + <clause-bullet block> + "\\n\\n"
                         + <conventions block> + "\\n"

with arm E's conventions block being the shared block, a newline, and arm E's
appended threshold-definition sentence. The prompt relation (§2.6) is

    HEADER            = 011's pinned PROMPT.txt bytes with 010's locked policy
                        bytes minus their final LF removed from the end
    arms/X/PROMPT.txt = HEADER + arms/X/POLICY.md minus its final LF

and `HEADER` is DERIVED here, from two digests both pinned and both verified,
rather than authored: 2706 - 1758 = 948 bytes.

Nothing in this module is authority for anything. `harness/PINS.json` holds the
digests, `harness/integrity.py` is what refuses, and this module exists so that
(a) the arm artifacts can be rebuilt from the preregistration's own bytes and
(b) a harness test can require the frozen artifacts to equal that rebuild —
Study 011's registered-illustration discipline, applied to five texts.

This module reads no clock, no environment and no randomness, and it writes
nothing unless `build` is invoked explicitly.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
EXPERIMENTS = os.path.normpath(os.path.join(STUDY, ".."))
ELEVEN = os.path.join(EXPERIMENTS, "011-authorship-coverage-rates")
TEN = os.path.join(EXPERIMENTS, "010-blinded-oracle")

PREREGISTRATION = os.path.join(STUDY, "PREREGISTRATION.md")
APPENDIX_ANCHOR = "## Appendix A — the five policy texts (DRAFT)"

ARMS = ("A", "B", "C", "D", "E")
# §2.3: an arm's whole family is determined by its (T_low, T_high) pair, and
# §2.6 registers the pair as the load-bearing member of ARM.json.
THRESHOLDS = {"A": (40, 70), "B": (40, 70), "C": (40, 70),
              "D": (45, 72), "E": (40, 70)}
PERTURBATION = {"A": "baseline", "B": "reworded", "C": "reordered",
                "D": "renamed", "E": "denamed"}
# Arm E states its thresholds by reference; every other arm states them as
# literals. Recorded per arm so the wrapper and the scorer can name it without
# re-reading the policy text.
LITERALS = {"A": True, "B": True, "C": True, "D": True, "E": False}

# §2.6: the registered inclusivity vocabulary, closed. A bound whose cue is not
# one of these seven phrases fails the check even if a reader would call it an
# inclusivity cue — the closure is the point, because an open-ended notion of
# "an inclusivity word" is a reading and a reading is what the invariant exists
# to replace.
INCLUSIVE_CUES = ("at or above", "or above", "or more", "or higher")
EXCLUSIVE_CUES = ("less than", "below", "under")

ARM_LABEL = re.compile(r"^- \*\*(P[1-5])\.\*\* ")
DIGIT_RUN = re.compile(r"[0-9]+")
LABEL_TOKEN = re.compile(r"P[1-5]")


class AssemblyError(Exception):
    """The appendix does not carry what the assembly rule needs."""


def _read(path: str) -> bytes:
    with open(path, "rb") as handle:
        return handle.read()


def sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _fences(text: str) -> list:
    """[(body, start line index)] for every ``` fenced block, in order."""
    lines = text.split("\n")
    blocks, index = [], 0
    while index < len(lines):
        if lines[index].strip() == "```":
            end = index + 1
            body = []
            while end < len(lines) and lines[end].strip() != "```":
                body.append(lines[end])
                end += 1
            if end >= len(lines):
                raise AssemblyError("an unterminated fenced block at line %d" % index)
            blocks.append(("\n".join(body), index))
            index = end + 1
        else:
            index += 1
    return blocks


def _fence_after(text: str, anchor: str, blocks: list) -> str:
    """The first fenced block that begins after `anchor`'s line."""
    position = text.find(anchor)
    if position < 0:
        raise AssemblyError("the preregistration carries no anchor %r" % anchor)
    line = text[:position].count("\n")
    for body, start in blocks:
        if start > line:
            return body
    raise AssemblyError("no fenced block follows %r" % anchor)


def appendix(preregistration: str = None) -> dict:
    """The registered pieces of Appendix A, read out of the preregistration's
    own bytes rather than copied into this file — so this module cannot drift
    from the text it implements."""
    path = preregistration or PREREGISTRATION
    text = _read(path).decode("utf-8")
    if APPENDIX_ANCHOR not in text:
        raise AssemblyError("%s carries no Appendix A" % path)
    body = text.split(APPENDIX_ANCHOR, 1)[1]
    blocks = _fences(body)
    pieces = {
        "preamble": _fence_after(body, "**The preamble, byte-identical in all five arms**", blocks),
        "conventions": _fence_after(body, "**The conventions paragraph, byte-identical in A, B, C and D.**", blocks),
        "eSentence": _fence_after(body, "Arm E's conventions paragraph is the shared conventions paragraph", blocks),
    }
    for arm, heading in zip(ARMS, ("### A.1 Arm A", "### A.2 Arm B", "### A.3 Arm C",
                                   "### A.4 Arm D", "### A.5 Arm E")):
        pieces["clauses" + arm] = _fence_after(body, heading, blocks)
    return pieces


def policy_text(arm: str, pieces: dict = None) -> bytes:
    """Appendix A's assembly rule, applied. The ONLY place this study turns the
    appendix into an artifact."""
    if arm not in ARMS:
        raise AssemblyError("%r is not a registered arm" % (arm,))
    pieces = pieces if pieces is not None else appendix()
    conventions = pieces["conventions"]
    if arm == "E":
        conventions = conventions + "\n" + pieces["eSentence"]
    document = (pieces["preamble"] + "\n\n" + pieces["clauses" + arm] + "\n\n"
                + conventions + "\n")
    return document.encode("utf-8")


def header() -> bytes:
    """§2.6's HEADER, derived from two pinned digests and never authored: 011's
    prompt bytes with 010's locked policy bytes (minus their final LF) removed
    from the end. 2706 - 1758 = 948."""
    prompt = _read(os.path.join(ELEVEN, "transcription", "PROMPT.txt"))
    policy = _read(os.path.join(TEN, "policy", "POLICY.md"))
    if not policy.endswith(b"\n"):
        raise AssemblyError("Study 010's locked policy has no final LF")
    tail = policy[:-1]
    if not prompt.endswith(tail):
        raise AssemblyError(
            "Study 011's pinned prompt does not end with Study 010's locked policy "
            "bytes: the prompt equation of §2.6 has no HEADER")
    return prompt[:len(prompt) - len(tail)]


def prompt_text(arm: str, pieces: dict = None) -> bytes:
    """§2.6's prompt equation for one arm, with no trailing newline."""
    policy = policy_text(arm, pieces)
    return header() + policy[:-1]


def derive_arm_a() -> bytes:
    """§2.1's registered relation, computed from Study 010's locked bytes:
    `PREAMBLE_DELTA` applied at its single occurrence and `CONVENTIONS_DELTA`
    appended at the registered position. Checked against the appendix assembly
    by C8 and by a harness test — the two must agree, and neither is the
    authority for the other."""
    policy = _read(os.path.join(TEN, "policy", "POLICY.md"))
    occurrences = policy.count(PREAMBLE_DELTA_FROM)
    if occurrences != 1:
        raise AssemblyError(
            "PREAMBLE_DELTA is registered at its SINGLE occurrence and Study 010's "
            "locked policy carries %d" % occurrences)
    replaced = policy.replace(PREAMBLE_DELTA_FROM, PREAMBLE_DELTA_TO)
    if not replaced.endswith(b"\n"):
        raise AssemblyError("Study 010's locked policy has no final LF")
    return replaced[:-1] + CONVENTIONS_DELTA + b"\n"


# §2.5 / [D-16]: one substitution, at its single occurrence, +1 byte.
PREAMBLE_DELTA_FROM = b"Study 010"
PREAMBLE_DELTA_TO = b"this study"
# §2.6 / [D-15]: one sentence, one leading space, 55 bytes, in ALL FIVE arms.
CONVENTIONS_DELTA = b" The office's risk scale runs from zero to one hundred."


# --- the family (§2.3's schema, instantiated) -------------------------------

def family_document(t_low: int, t_high: int) -> bytes:
    """§2.3's six classes as a `FAMILY.json`, instantiated at one arm's pair.

    At (40, 70) this reproduces Study 010's locked `FAMILY.json` BYTE FOR BYTE,
    which is C9's anchor: the arm that anchors the schema is the arm whose
    family a previous study locked, and a generator that merely produced an
    equivalent file would not establish that. Every threshold-derived number in
    the document — the predicates, the prose, the titles, the patch values and
    the `underD` sentences — is written from the pair, so arm D's family is the
    σ-image of arm A's rather than a hand-edited copy.
    """
    low, high = str(t_low), str(t_high)
    low_up, high_up, low_down = str(t_low + 1), str(t_high + 1), str(t_low - 1)
    document = {
        "familyVersion": "1",
        "pack": "packs/vendor-screening-correct.pack.json",
        "note": "Six candidate defects, ordered. The drand draw (PREREGISTRATION.md §5) "
                "selects exactly one index; the harness applies its patch to pack C to "
                "produce D. Each predicate is evaluator-independent: it reads only a "
                "record's vendor facts. Every defect class disposes as an outcome under C "
                "and as unresolved (no-match or conflict) under its D. reasonsUnderD gives "
                "the registered unresolved reason set per personal-data value (null matches "
                "either); the first matching entry applies.",
        "embargoList": ["KP", "IR", "SY"],
        "mutations": [
            {
                "index": 0,
                "title": "P3's boundary becomes exclusive",
                "patch": [{"path": "/rules/2/when/conditions/2/operator",
                           "old": "greater-than-or-equal", "new": "greater-than"}],
                "violatedClause": "P3",
                "predicate": {"sanctionsHit": False,
                              "registeredCountry": {"kind": "not-embargoed"},
                              "handlesPersonalData": None,
                              "riskScore": {"eq": high}},
                "predicateProse": "no sanctions hit, non-embargoed registration, risk score "
                                  "exactly %s" % high,
                "underD": "unresolved (no-match): P3 excludes %s, P4 and P5 require below %s"
                          % (high, high),
                "reasonsUnderD": [{"handlesPersonalData": None, "reasons": ["no-match"]}],
            },
            {
                "index": 1,
                "title": "P3's threshold moves to %s in P3 only" % high_up,
                "patch": [{"path": "/rules/2/when/conditions/2/value",
                           "old": high, "new": high_up}],
                "violatedClause": "P3",
                "predicate": {"sanctionsHit": False,
                              "registeredCountry": {"kind": "not-embargoed"},
                              "handlesPersonalData": None,
                              "riskScore": {"gte": high, "lt": high_up}},
                "predicateProse": "no sanctions hit, non-embargoed registration, risk score "
                                  "at least %s and below %s" % (high, high_up),
                "underD": "unresolved (no-match): P3 requires %s, P4 and P5 require below %s"
                          % (high_up, high),
                "reasonsUnderD": [{"handlesPersonalData": None, "reasons": ["no-match"]}],
            },
            {
                "index": 2,
                "title": "P4's lower bound moves to %s" % low_up,
                "patch": [{"path": "/rules/3/when/conditions/3/value",
                           "old": low, "new": low_up}],
                "violatedClause": "P4",
                "predicate": {"sanctionsHit": False,
                              "registeredCountry": {"kind": "not-embargoed"},
                              "handlesPersonalData": True,
                              "riskScore": {"gte": low, "lt": low_up}},
                "predicateProse": "no sanctions hit, non-embargoed registration, handles "
                                  "personal data, risk score at least %s and below %s"
                                  % (low, low_up),
                "underD": "unresolved (no-match): P4 requires %s, P5's clearance arm requires "
                          "below %s" % (low_up, low),
                "reasonsUnderD": [{"handlesPersonalData": None, "reasons": ["no-match"]}],
            },
            {
                "index": 3,
                "title": "P4's personal-data condition inverts",
                "patch": [{"path": "/rules/3/when/conditions/2/value",
                           "old": True, "new": False}],
                "violatedClause": "P4 and P5",
                "predicate": {"sanctionsHit": False,
                              "registeredCountry": {"kind": "not-embargoed"},
                              "handlesPersonalData": None,
                              "riskScore": {"gte": low, "lt": high}},
                "predicateProse": "no sanctions hit, non-embargoed registration, risk score at "
                                  "least %s and below %s (either personal-data value)"
                                  % (low, high),
                "underD": "unresolved: personal-data vendors match nothing (no-match); "
                          "non-personal-data vendors match both the mutated P4 and P5 "
                          "(conflict)",
                "reasonsUnderD": [{"handlesPersonalData": True, "reasons": ["no-match"]},
                                  {"handlesPersonalData": False, "reasons": ["conflict"]}],
            },
            {
                "index": 4,
                "title": "P2's embargo list loses SY",
                "patch": [{"path": "/rules/1/when/conditions/1/value",
                           "old": ["KP", "IR", "SY"], "new": ["KP", "IR"]}],
                "violatedClause": "P2",
                "predicate": {"sanctionsHit": False,
                              "registeredCountry": {"kind": "equals", "value": "SY"},
                              "handlesPersonalData": None, "riskScore": None},
                "predicateProse": "no sanctions hit, registered in SY (any score)",
                "underD": "unresolved (no-match): the mutated P2 no longer matches SY, and "
                          "P3/P4/P5's unmutated embargo exclusions still exclude it",
                "reasonsUnderD": [{"handlesPersonalData": None, "reasons": ["no-match"]}],
            },
            {
                "index": 5,
                "title": "P5's inner clearance bound moves to %s" % low_down,
                "patch": [{"path": "/rules/4/when/conditions/3/conditions/1/value",
                           "old": low, "new": low_down}],
                "violatedClause": "P5",
                "predicate": {"sanctionsHit": False,
                              "registeredCountry": {"kind": "not-embargoed"},
                              "handlesPersonalData": True,
                              "riskScore": {"gte": low_down, "lt": low}},
                "predicateProse": "no sanctions hit, non-embargoed registration, handles "
                                  "personal data, risk score at least %s and below %s"
                                  % (low_down, low),
                "underD": "unresolved (no-match): P5's mutated arm requires below %s, P4 "
                          "requires at least %s" % (low_down, low),
                "reasonsUnderD": [{"handlesPersonalData": None, "reasons": ["no-match"]}],
            },
        ],
    }
    return (json.dumps(document, indent=2) + "\n").encode("utf-8")


def arm_document(arm: str) -> bytes:
    """`ARM.json`: the arm id, its (T_low, T_high) and its perturbation kind.

    §2.6: "The (T_low, T_high) pair here is what parameterizes the single
    registered mirror module", so this file is load-bearing for every label in
    its arm and is pinned like every other."""
    low, high = THRESHOLDS[arm]
    document = {
        "armVersion": "1",
        "arm": arm,
        "perturbation": PERTURBATION[arm],
        "thresholds": {"tLow": low, "tHigh": high},
        "statesThresholdsAsLiterals": LITERALS[arm],
        "note": "PREREGISTRATION.md §2.6. The thresholds member parameterizes the single "
                "registered mirror module harness/policy_mirror.py (§2.2 [D-14]) and "
                "instantiates §2.3's six semantic class keys in this arm's FAMILY.json. It "
                "is pinned by sha256 in harness/PINS.json before any call, and "
                "harness/integrity.py refuses every arm whose mirror verdicts over the "
                "§2.4 landmark grid are not arm A's.",
    }
    return (json.dumps(document, indent=2) + "\n").encode("utf-8")


# --- the document structure and the registered text properties (§2.6, C8) ----

def parse_policy(body: bytes) -> dict:
    """§2.6's registered structure: a preamble, exactly five clause bullets
    labelled P1-P5, and a conventions paragraph.

    Returned as {preamble, clauses: [(label, body)], conventions}, where a
    clause body is everything after `- **P<n>.** ` with the bullet's
    continuation lines joined by their own newlines — the bytes, not a
    normalization of them.
    """
    text = body.decode("utf-8")
    if not text.endswith("\n"):
        raise AssemblyError("a policy document ends with a newline")
    lines = text[:-1].split("\n")
    first = next((i for i, line in enumerate(lines) if ARM_LABEL.match(line)), None)
    if first is None:
        raise AssemblyError("the document carries no clause bullets")
    preamble = "\n".join(lines[:first]).rstrip("\n")
    clauses, current, label = [], None, None
    index = first
    while index < len(lines):
        line = lines[index]
        match = ARM_LABEL.match(line)
        if match:
            if label is not None:
                clauses.append((label, "\n".join(current)))
            label = match.group(1)
            current = [line[match.end():]]
        elif line.startswith("  ") and label is not None:
            current.append(line)
        elif line.strip() == "" and label is not None:
            break
        else:
            raise AssemblyError("line %d is neither a clause bullet nor a continuation: %r"
                                % (index, line))
        index += 1
    if label is not None:
        clauses.append((label, "\n".join(current)))
    conventions = "\n".join(lines[index:]).strip("\n")
    if len(clauses) != 5:
        raise AssemblyError("the document carries %d clause bullets, not five" % len(clauses))
    labels = [entry[0] for entry in clauses]
    if sorted(labels) != ["P1", "P2", "P3", "P4", "P5"]:
        raise AssemblyError("the clause labels are %r, not P1-P5 each once" % (labels,))
    if not preamble or not conventions:
        raise AssemblyError("the document is missing a preamble or a conventions paragraph")
    return {"preamble": preamble, "clauses": clauses, "conventions": conventions}


def mask_labels(text: str) -> str:
    """§2.6's census definition: clause-label tokens P1-P5 masked out FIRST.

    A's own P5 body says "unless P4 applies"; that `4` is a structural
    cross-reference present identically in every arm, and counting it would
    make every arm's census carry a digit that says nothing about the
    intervention."""
    return LABEL_TOKEN.sub("", text)


def digit_census(clause_body: str) -> list:
    """The multiset of digit-runs in one clause body, sorted, under §2.6's
    definition."""
    return sorted(DIGIT_RUN.findall(mask_labels(clause_body)))


def policy_census(parsed: dict) -> list:
    """The clause-body digit-run census of a whole document, sorted."""
    runs = []
    for _, body in parsed["clauses"]:
        runs.extend(digit_census(body))
    return sorted(runs)


def whole_file_digit_runs(body: bytes) -> list:
    """Every digit-run in a `POLICY.md`, in order, unmasked — §2.5's exhaustive
    count, which is a statement about the frozen artifact and not about the
    clause bodies."""
    return DIGIT_RUN.findall(body.decode("utf-8"))


def _strip_emphasis(text: str) -> str:
    return text.replace("**", "")


def adjacency_tuples(parsed: dict) -> list:
    """§2.6's inclusivity-adjacency invariant, as the ordered tuple sequence
    (clause label, literal, side, sense) the harness compares.

    For each numeric literal in each clause body, in clause order and then in
    position order, the check looks for a cue from the registered CLOSED
    vocabulary immediately adjacent to that literal — `after` when the cue
    follows it, `before` when it precedes it. A literal with no adjacent
    registered cue raises: the invariant constrains B's word choice and not
    only its word order, and §2.6 registers that as the price of the control.
    """
    tuples = []
    for label, body in parsed["clauses"]:
        text = _strip_emphasis(mask_labels(body))
        # Continuation lines are wrapped; the adjacency is a property of the
        # sentence, not of the line, so whitespace collapses first.
        flat = " ".join(text.split())
        for match in DIGIT_RUN.finditer(flat):
            literal = match.group(0)
            before = flat[:match.start()].rstrip()
            after = flat[match.end():].lstrip()
            sense, side = None, None
            for cue in INCLUSIVE_CUES:
                if after.startswith(cue):
                    sense, side = "inclusive", "after"
                    break
                if before.endswith(cue):
                    sense, side = "inclusive", "before"
                    break
            if sense is None:
                for cue in EXCLUSIVE_CUES:
                    if before.endswith(cue):
                        sense, side = "exclusive", "before"
                        break
                    if after.startswith(cue):
                        sense, side = "exclusive", "after"
                        break
            if sense is None:
                raise AssemblyError(
                    "%s's literal %s carries no inclusivity cue from the registered "
                    "vocabulary immediately adjacent to it: the vocabulary is closed "
                    "(§2.6) and a bound outside it fails the invariant" % (label, literal))
            tuples.append((label, literal, side, sense))
    return tuples


def bound_senses(parsed: dict) -> list:
    """Arm E's form of the invariant: (clause label, threshold name, sense).

    E has no literals, so no adjacency SIDE can be preserved — you cannot write
    "the review threshold or above" the way you write "70 or above". What is
    checked is that E's six bound phrases carry the same six senses in the same
    six places as arm A's six literals do (§2.6), so the flip from *after the
    literal* to *before the name* is registered rather than discovered.
    """
    names = {"review threshold": "T_high", "personal-data threshold": "T_low"}
    senses = []
    for label, body in parsed["clauses"]:
        flat = " ".join(_strip_emphasis(mask_labels(body)).split())
        for match in re.finditer(r"(review threshold|personal-data threshold)", flat):
            before = flat[:match.start()].rstrip()
            # A named bound takes an article the literal form does not: "below
            # the review threshold" against "below 70". The article is the only
            # token allowed between the cue and the name, and it is stripped
            # here rather than added to the closed vocabulary of §2.6.
            if before.endswith(" the"):
                before = before[:-4].rstrip()
            sense = None
            for cue in INCLUSIVE_CUES:
                if before.endswith(cue):
                    sense = "inclusive"
                    break
            if sense is None:
                for cue in EXCLUSIVE_CUES:
                    if before.endswith(cue):
                        sense = "exclusive"
                        break
            if sense is None:
                continue          # a mention that is not a bound (a definition)
            senses.append((label, names[match.group(1)], sense))
    return senses


# --- arm C's permutation (§2.6 [D-5], re-derived rather than hard-coded) -----

def label_order(parsed: dict) -> tuple:
    return tuple(label for label, _ in parsed["clauses"])


def _references(bodies: dict) -> dict:
    """The three reference kinds §2.6 registers, read out of the parsed bodies:
    explicit `P<n>` cross-references, the three-part precondition, and the
    two-part one."""
    explicit, three_part, two_part = {}, set(), set()
    for label, body in bodies.items():
        flat = " ".join(_strip_emphasis(body).split()).lower()
        explicit[label] = sorted(set(
            token for token in re.findall(r"\bp[1-5]\b", flat)
            if token.upper() != label))
        if "sanctions hit or an embargoed registration" in flat:
            three_part.add(label)
        elif "absent a sanctions hit" in flat or "with no sanctions hit" in flat:
            two_part.add(label)
    return {"explicit": explicit, "threePart": three_part, "twoPart": two_part}


def resolves_backward(order: tuple, bodies: dict) -> bool:
    """§2.6's conditions 1-3 for one presentation order: every explicit
    clause-label reference, every three-part precondition and every two-part
    precondition resolves to a clause EARLIER in the order."""
    references = _references(bodies)
    position = {label: index for index, label in enumerate(order)}
    for label, targets in references["explicit"].items():
        for target in targets:
            if position[target.upper()] >= position[label]:
                return False
    for label in references["threePart"]:
        if position["P1"] >= position[label] or position["P2"] >= position[label]:
            return False
    for label in references["twoPart"]:
        if position["P1"] >= position[label]:
            return False
    return True


def _permutations(items):
    if not items:
        yield ()
        return
    for index, item in enumerate(items):
        for rest in _permutations(items[:index] + items[index + 1:]):
            yield (item,) + rest


def movement(order: tuple) -> int:
    """How many clauses the order moves out of their canonical position."""
    canonical = ("P1", "P2", "P3", "P4", "P5")
    return sum(1 for index, label in enumerate(order) if label != canonical[index])


def permutation_survey(bodies: dict) -> dict:
    """All 120 permutations enumerated against the full constraint set, so the
    registered permutation is RE-DERIVED rather than compared against a
    hard-coded tuple (§2.6, Appendix A.3)."""
    labels = ("P1", "P2", "P3", "P4", "P5")
    backward = [order for order in _permutations(list(labels))
                if resolves_backward(order, bodies)]
    best = max(movement(order) for order in backward)
    maxima = [order for order in backward if movement(order) == best]
    derangements = [order for order in backward if movement(order) == len(labels)]
    # The weaker constraint set round 1 registered against: explicit references
    # and the three-part precondition only, with the two-part opener free.
    weaker = []
    for order in _permutations(list(labels)):
        references = _references(bodies)
        position = {label: index for index, label in enumerate(order)}
        ok = all(position[target.upper()] < position[label]
                 for label, targets in references["explicit"].items()
                 for target in targets)
        ok = ok and all(position["P1"] < position[label] and position["P2"] < position[label]
                        for label in references["threePart"])
        if ok:
            weaker.append(order)
    return {"total": 120, "backward": backward, "maxMovement": best,
            "maxima": maxima, "derangementsBackward": derangements,
            "weakerDerangements": [o for o in weaker if movement(o) == len(labels)]}


# --- building the artifacts -------------------------------------------------

def artifacts(arm: str, pieces: dict = None) -> dict:
    """The four registered files of one arm, as bytes."""
    low, high = THRESHOLDS[arm]
    return {"POLICY.md": policy_text(arm, pieces),
            "PROMPT.txt": prompt_text(arm, pieces),
            "FAMILY.json": family_document(low, high),
            "ARM.json": arm_document(arm)}


def build(root: str = None) -> dict:
    """Write every arm's four files. Refuses to overwrite bytes that differ,
    so a rebuild after the freeze is a refusal rather than a silent edit."""
    root = root or os.path.join(STUDY, "arms")
    pieces = appendix()
    written = {}
    for arm in ARMS:
        directory = os.path.join(root, arm)
        os.makedirs(directory, exist_ok=True)
        for name, body in artifacts(arm, pieces).items():
            path = os.path.join(directory, name)
            if os.path.exists(path) and _read(path) != body:
                raise AssemblyError(
                    "%s exists and differs from the registered assembly: an arm artifact "
                    "is frozen before any call and is never rewritten in place" % path)
            with open(path, "wb") as handle:
                handle.write(body)
            written["arms/%s/%s" % (arm, name)] = sha256(body)
    return written


def main(argv: list) -> int:
    if len(argv) >= 2 and argv[1] == "build":
        for path, digest in sorted(build().items()):
            print("%s  %s" % (digest, path))
        return 0
    if len(argv) >= 2 and argv[1] == "digests":
        pieces = appendix()
        for arm in ARMS:
            body = policy_text(arm, pieces)
            prompt = prompt_text(arm, pieces)
            print("%s policy %5d %s" % (arm, len(body), sha256(body)))
            print("%s prompt %5d %s" % (arm, len(prompt), sha256(prompt)))
        print("preamble %d %s" % (len(pieces["preamble"].encode()),
                                  sha256(pieces["preamble"].encode())))
        print("conventionsDelta %d %s" % (len(CONVENTIONS_DELTA),
                                          sha256(CONVENTIONS_DELTA)))
        print("header %d %s" % (len(header()), sha256(header())))
        return 0
    print("usage: arm_assembly.py build | digests", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
