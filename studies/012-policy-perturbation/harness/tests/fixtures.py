#!/usr/bin/env python3
"""Throwaway fixtures with a KNOWN coverage, drop and census profile, and the
machinery to put them into five-arm slot trees (§6 C4).

Nothing here is study data: the records are invented for the tests, their ids
are not the authored ones, and no real completion, session, or codex binary is
involved. What the fixtures buy is what C4 asks for — a completion whose
H ∩ class membership is known BY CONSTRUCTION for every one of the six classes,
at whatever `(T_low, T_high)` an arm registers, so the counting code cannot
silently miscount and call it a finding.

Every record set below is a FUNCTION of the arm's pair, and every expected
output is registered beside it as a constant, because this study has five arms
at two pairs and a set of literals for (40, 70) would say nothing about arm D:

  `full_records`      — reaches all six classes with correctly-labelled records
                        (`FULL_PROFILE`, `FULL_CENSUS`), at the arm's own edges
  `partial_records`   — reaches classes 1, 3 and 4 in H, class 2 ONLY with a
                        mislabelled record, and classes 0 and 5 not at all
                        (`PARTIAL_PROFILE`)
  `drop_records`      — one element per drop code, in the compiler's own check
                        order (`DROP_HISTOGRAM`)
  `COMPLETION_EMPTY`  — §3.3's authoring-empty run: admissible evidence, no
                        parseable array, valid, covering nothing
  `LABELLED_NO_CLASS` — one accepted, correctly labelled record satisfying no
                        class predicate (round 4, finding 9): the covered-class
                        set is empty and the run held H records anyway
  `quarantined_only_records`
                      — one accepted record, quarantined, whose predicates put
                        it in classes 2 and 3 (round 4, finding 9): reached in
                        the raw and Q senses, covered in neither
                        (`QUARANTINED_ONLY_PROFILE`)

The slot machinery uses the REAL driver's seal and ledger (`batch.seal_slot`,
`batch.ledger_record`, `batch.record_digest`) rather than hand-written
manifests, so a fixture cannot agree with a scorer that both misread §2.9;
`batch.STUDY` is patched to the throwaway study root while the ledger records
are built, because a record names its slot's STUDY-RELATIVE path (C5 rule 2).

The record builders are pure functions of a threshold pair; everything that
touches a slot goes through the harness modules imported below, so a fixture
and the thing it is a fixture for cannot hold two definitions of one artifact.
"""
from __future__ import annotations
import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from decimal import Decimal

import batch
import score_rates
import transcript_check

ARMS = ("A", "B", "C", "D", "E")
BASELINE_ARM = "A"
AUTHORING = "authoring"
LEDGER_FILE = "BATCH.json"
SHORTFALL_FILE = "SHORTFALL.json"
# The six system directories the wrapper puts on the child PATH, which
# score_rates.check_environment() requires; kept here as a literal so the
# fixtures cannot pass the check by importing the thing under test.
SYSTEM_PATH = ("/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin",
               "/sbin", "/bin")


# --- the records, parameterized by the arm's registered pair ----------------

def _decimal(value: Decimal) -> str:
    """A canonical `riskScore` string: no trailing zeros, no leading zero, so
    the compiler's `decimal-form` check accepts it at every arm's edges."""
    text = format(value.normalize(), "f")
    return text


def _record(case_id: str, score, *, country: str = "NL", personal: bool = False,
            sanctions: bool = False, outcome: str, by: str, at: str) -> dict:
    return {
        "caseId": case_id,
        "vendor": {"legalName": case_id.replace("-", " ").title(),
                   "sanctionsHit": sanctions, "registeredCountry": country,
                   "handlesPersonalData": personal,
                   "riskScore": score if isinstance(score, str) else _decimal(score)},
        "decision": {"outcome": outcome, "decidedBy": by, "decidedAt": at},
    }


def full_records(t_low, t_high) -> list:
    """Seven correctly-labelled records reaching ALL SIX classes at this arm's
    own edges — the fixture C4 requires "at the shifted edges" for arm D and at
    (40, 70) for every other arm, built once so the two cannot drift apart.

    The seventh record reaches no class at all (every predicate requires no
    sanctions hit), because a fixture in which every record lands somewhere
    would not exercise the empty intersection.
    """
    low, high = Decimal(str(t_low)), Decimal(str(t_high))
    return [
        # class 0 (== T_high) and class 1 ([T_high, T_high+1)); P3 -> review
        _record("threshold-exact", high, outcome="manual-review",
                by="reviewer-1", at="2026-06-02T09:00:00Z"),
        # class 1 only; P3 -> review
        _record("fraction-above-threshold", high + Decimal("0.5"),
                outcome="manual-review", by="reviewer-2",
                at="2026-06-03T11:30:00Z"),
        # classes 2 (personal ∧ [T_low, T_low+1)) and 3 ([T_low, T_high));
        # P4 -> review
        _record("personal-data-at-low", low, country="DE", personal=True,
                outcome="manual-review", by="reviewer-3",
                at="2026-06-04T14:15:00Z"),
        # class 3 only; no personal data, below T_high: P5 -> clear
        _record("mid-band-no-personal", low + 15, country="FR",
                outcome="clear", by="reviewer-4", at="2026-06-05T08:45:00Z"),
        # class 4 (embargoed SY, no numeric content); P2 -> reject
        _record("embargoed-syria", high + Decimal("18.75"), country="SY",
                personal=True, outcome="reject", by="reviewer-5",
                at="2026-06-06T16:20:00Z"),
        # class 5 (personal ∧ [T_low-1, T_low)); below T_low: P5 -> clear
        _record("personal-just-below-low", low - 1, country="PT", personal=True,
                outcome="clear", by="reviewer-6", at="2026-06-07T10:00:00Z"),
        # no class: every predicate requires sanctionsHit false. P1 -> reject
        _record("sanctioned-north-korea", high + 21, country="KP",
                sanctions=True, outcome="reject", by="reviewer-7",
                at="2026-06-08T12:00:00Z"),
    ]


# The profile the tests hold the counting code to, by construction, at ANY
# registered pair. Registered in the same committed module as the fixture, as
# §6 C4 requires.
FULL_PROFILE = {
    "accepted": ["embargoed-syria", "fraction-above-threshold",
                 "mid-band-no-personal", "personal-data-at-low",
                 "personal-just-below-low", "sanctioned-north-korea",
                 "threshold-exact"],
    "dropCodes": {},
    "h": ["embargoed-syria", "fraction-above-threshold", "mid-band-no-personal",
          "personal-data-at-low", "personal-just-below-low",
          "sanctioned-north-korea", "threshold-exact"],
    "q": [],
    "covered": [0, 1, 2, 3, 4, 5],
    "raw": [0, 1, 2, 3, 4, 5],
    "qIntersection": [],
    "qOnly": [],
    "members": {
        "0": {"h": ["threshold-exact"], "q": []},
        "1": {"h": ["fraction-above-threshold", "threshold-exact"], "q": []},
        "2": {"h": ["personal-data-at-low"], "q": []},
        "3": {"h": ["mid-band-no-personal", "personal-data-at-low"], "q": []},
        "4": {"h": ["embargoed-syria"], "q": []},
        "5": {"h": ["personal-just-below-low"], "q": []},
    },
}
# §4.5's census over ONE run of the full completion: every record is its own
# probe, so the per-class probe counts are the per-class record counts.
FULL_CENSUS = {
    "records": 7, "h": 7, "q": 0,
    "recordsPerClass": [1, 2, 1, 2, 1, 1],
    "probesPerClass": [1, 2, 1, 2, 1, 1],
}
# S10 (§4.6): where arm D's records land in ARM A's coordinate system. D's
# narrow numeric classes are at 45 and 72, so none of A's narrow numeric
# classes (0, 1, 2, 5) is reached; A's class 3 is the 30-wide band [40, 70),
# which D's 45 and 60 sit inside, and A's class 4 names no number at all.
# §5.3 (ii) predicts exactly this shape, and it is the "known answer" C4 asks
# the cross-scoring to be exercised at.
FULL_OLD_EDGE_FROM_D = [3, 4]


def partial_records(t_low, t_high) -> list:
    """C4's mislabel and empty-class fixture: classes 1, 3 and 4 reached in H,
    class 2 reached ONLY by a mislabelled record, classes 0 and 5 reached by no
    record at all, and one element per two of the drop codes so a run's drop
    histogram is non-empty."""
    low, high = Decimal(str(t_low)), Decimal(str(t_high))
    records = [
        _record("fraction-above-threshold", high + Decimal("0.5"),
                outcome="manual-review", by="reviewer-2",
                at="2026-06-03T11:30:00Z"),
        _record("mid-band-no-personal", low + 15, country="FR", outcome="clear",
                by="reviewer-4", at="2026-06-05T08:45:00Z"),
        _record("embargoed-syria", high + Decimal("18.75"), country="SY",
                personal=True, outcome="reject", by="reviewer-5",
                at="2026-06-06T16:20:00Z"),
        _record("sanctioned-north-korea", high + 21, country="KP",
                sanctions=True, outcome="reject", by="reviewer-7",
                at="2026-06-08T12:00:00Z"),
        # Q: the mirror says manual-review at this arm's pair and the record
        # says clear. Classes 2 and 3, mislabelled — class 2's ONLY reader.
        _record("mislabelled-at-low", low, country="FR", personal=True,
                outcome="clear", by="reviewer-8", at="2026-06-09T09:10:00Z"),
        # dropped: decimal-form (a leading zero is not canonical)
        _record("tallow-bay-imports", "07", outcome="clear", by="reviewer-9",
                at="2026-06-10T09:00:00Z"),
    ]
    # dropped: duplicate-id (mid-band-no-personal already claimed the caseId)
    duplicate = _record("mid-band-no-personal", low + 16, country="FR",
                        outcome="clear", by="reviewer-10",
                        at="2026-06-11T09:00:00Z")
    return records + [duplicate]


PARTIAL_PROFILE = {
    "accepted": ["embargoed-syria", "fraction-above-threshold",
                 "mid-band-no-personal", "mislabelled-at-low",
                 "sanctioned-north-korea"],
    "dropCodes": {"decimal-form": 1, "duplicate-id": 1},
    "h": ["embargoed-syria", "fraction-above-threshold", "mid-band-no-personal",
          "sanctioned-north-korea"],
    "q": ["mislabelled-at-low"],
    "covered": [1, 3, 4],          # H reaches these
    "raw": [1, 2, 3, 4],           # any accepted record reaches these
    "qIntersection": [2, 3],       # Q reaches these
    "qOnly": [2],                  # ONLY Q reaches these — the mislabel class
    "unreached": [0, 5],           # reached by no record at all
}

def old_labelled_records(t_low, t_high) -> list:
    """Round 10, finding 7's corpus: three records placed at the BASELINE's
    edges and labelled by the BASELINE's rule, for a slot of an arm whose own
    pair is somewhere else.

    The pair is passed in — arm A's, taken from arm A's own `ARM.json` — so the
    fixture cannot drift from the edges S10 cross-scores against. In arm D, at
    (45, 72), every one of the first two is QUARANTINED: D's mirror clears a 70
    with no personal data and clears a 40 that handles it, and the records say
    `manual-review` because the old rule did. That is the shape §5.3 (ii)'s
    second outcome names — the model reproduced 40 and 70 in the face of a text
    that says 45 and 72 — and while S10 intersected with H it was the shape S10
    could not see.
    """
    low, high = Decimal(str(t_low)), Decimal(str(t_high))
    return [
        # baseline classes 0 (== T_high) and 1 ([T_high, T_high+1)), labelled by
        # the OLD P3. No personal data, so the only route into these classes
        # under a shifted mirror would be the personal-data branch.
        _record("old-edge-exact-high", high, outcome="manual-review",
                by="reviewer-1", at="2026-06-02T09:00:00Z"),
        # baseline classes 2 (P ∧ [T_low, T_low+1)) and 3 ([T_low, T_high)),
        # labelled by the OLD P4.
        _record("old-edge-personal-at-low", low, country="DE", personal=True,
                outcome="manual-review", by="reviewer-3",
                at="2026-06-04T14:15:00Z"),
        # baseline class 5 (P ∧ [T_low-1, T_low)): `clear` under both pairs, so
        # this one is H wherever it is scored and was S10's only visible record.
        _record("old-edge-personal-below-low", low - Decimal("0.5"),
                country="PT", personal=True, outcome="clear", by="reviewer-6",
                at="2026-06-07T10:00:00Z"),
    ]


# What the corpus above reaches in ARM A's coordinate system (S10) and what it
# reached before round 10 finding 7, scored in ARM D: the whole point is the
# difference. Class 4 is the embargo class, which no record here is in.
OLD_LABELLED_FROM_D = [0, 1, 2, 3, 5]
OLD_LABELLED_FROM_D_UNDER_THE_H_FILTER = [5]

RIDGELINE = {
    "caseId": "ridgeline-supplies",
    "vendor": {"legalName": "Ridgeline Supplies", "sanctionsHit": False,
               "registeredCountry": "SE", "handlesPersonalData": False,
               "riskScore": "12"},
    "decision": {"outcome": "clear", "decidedBy": "reviewer-9",
                 "decidedAt": "2026-06-10T09:00:00Z"},
}


def _variant(case_id: str, **changes) -> dict:
    """RIDGELINE with one thing wrong."""
    record = json.loads(json.dumps(RIDGELINE))
    record["caseId"] = case_id
    for path, value in changes.items():
        section, member = path.split(".")
        if section == "record":
            record[member] = value
        else:
            record[section][member] = value
    return record


def drop_records(t_low=None, t_high=None) -> list:
    """One element per drop code, in the compiler's own check order, so a
    reordered or skipped check shows up as a changed histogram rather than as
    nothing. The codes do not depend on an arm's pair; the signature matches
    the other record builders so a test can iterate over all three."""
    return [
        RIDGELINE,
        "not a record at all",                                               # schema
        _variant("tallow-bay-imports", **{"vendor.riskScore": "07"}),        # decimal-form
        _variant("kestrel-freight", **{"vendor.registeredCountry": "nl"}),   # country-form
        _variant("Bad_Id"),                                                  # id-form
        _variant("juniper-cleaning", **{"decision.outcome": "approve"}),     # outcome-value
        _variant("solano-textiles",
                 **{"decision.decidedAt": "2026-06-31T00:00:00Z"}),          # timestamp-form
        _variant("ridgeline-supplies"),                                      # duplicate-id
    ]


DROP_HISTOGRAM = {"schema": 1, "decimal-form": 1, "country-form": 1,
                  "id-form": 1, "outcome-value": 1, "timestamp-form": 1,
                  "duplicate-id": 1}
DROP_PROFILE = {"accepted": ["ridgeline-supplies"], "h": ["ridgeline-supplies"],
                "q": [], "covered": [], "raw": [], "dropCodes": DROP_HISTOGRAM}

# Round 4, finding 9's first case: ONE record, accepted and correctly labelled —
# a score of 12 with no personal data and no sanctions hit is `clear` under the
# mirror at every registered pair — that satisfies none of the six class
# predicates. The run reached no class, so `coveredNothing` is true; the scorer
# used to compute "did this run hold a correctly labelled record at all", which
# published `coveredClasses: []` beside `coveredNothing: false`.
LABELLED_NO_CLASS = [RIDGELINE]
LABELLED_NO_CLASS_PROFILE = {"accepted": ["ridgeline-supplies"],
                             "h": ["ridgeline-supplies"], "q": [],
                             "covered": [], "raw": [], "qIntersection": [],
                             "dropCodes": {}}


def quarantined_only_records(t_low, t_high) -> list:
    """Round 4, finding 9's second case: the one record of `partial_records()`
    this arm's mirror quarantines, alone.

    The array parses, the compiler accepts it, and the record's predicates put
    it in classes 2 and 3 — so the run REACHES classes in the raw (S1) and Q
    (S2) senses and covers none of them, because coverage is over H. Its
    covered-class set is empty and `coveredNothing` is true.
    """
    return [record for record in partial_records(t_low, t_high)
            if record["caseId"] == "mislabelled-at-low"]


QUARANTINED_ONLY_PROFILE = {"accepted": ["mislabelled-at-low"], "h": [],
                            "q": ["mislabelled-at-low"],
                            "covered": [], "raw": [2, 3],
                            "qIntersection": [2, 3], "dropCodes": {}}

# The bracketed aside never parses as a JSON array, so the record array wins
# extraction — the compiler's widest-span rule, exercised rather than assumed.
PREAMBLE = "Here are the office's files [7 filed, some rejected at intake]:\n\n"
TRAILER = "\n\nNo commentary follows."


def completion(records: list) -> str:
    return PREAMBLE + json.dumps(records, indent=2) + TRAILER


# §3.3's authoring-empty run: admissible evidence, nothing usable in it. Not a
# pipeline failure — the author simply produced no array, and a perturbation
# that makes the author fail outright must not be scored as if it had never
# been tried.
COMPLETION_EMPTY = ("The office keeps its files under seal and declines to "
                    "reproduce them here.")


# --- session shapes ---------------------------------------------------------

ITEM_KIND = {"user": "input_text", "developer": "input_text",
             "assistant": "output_text"}


def message(role: str, text: str) -> dict:
    return {"type": "response_item",
            "payload": {"type": "message", "role": role,
                        "content": [{"type": ITEM_KIND[role], "text": text}]}}


def default_prior(cwd: str, home: str) -> list:
    """The shape of codex's own pre-prompt boilerplate: it quotes the sandbox
    root and the session home (both normalized away before the golden digests
    are taken) and a date (normalized too), and it carries no study
    vocabulary — the leak screen must pass on an honest session.

    It is arm-INDEPENDENT, which is why [D-8] registers one golden capture for
    all five arms: the pre-prompt context is what the CLI says before the arm's
    prompt is delivered."""
    return [
        ("developer",
         "<permissions_instructions>\nYou are running with a workspace sandbox "
         "rooted at %s. Files outside it are read-only.\n"
         "</permissions_instructions>" % cwd),
        ("developer",
         "<agent_identity>\nYou are a general coding agent. Current date: "
         "2026-08-06.\nSession files live under %s.\n</agent_identity>" % home),
        ("user", "<recommended_plugins>\nAirtable, Apollo, Asana\n"
                 "</recommended_plugins>"),
    ]


SESSION_ID = "00000000-0000-4000-8000-%012d"


def session_entries(prompt: str, answer: str, cwd: str, home: str, model: str,
                    prior=None, reasoning: bool = True, extra=(),
                    session_id: str = None) -> list:
    """A transcript in the shape a real pinned-CLI session carries: codex's own
    boilerplate, an inert reasoning item, a turn context, the ARM'S registered
    prompt as the last user message, and one assistant answer.

    `session_id` names the session, as the pinned CLI's `session_meta` does. It
    is a per-slot value here because §3.3's `session-reused` reads it over all
    150 slots: two slots naming one session are one call however their
    directories are named."""
    entries = [{"type": "session_meta",
                "payload": {"id": session_id or SESSION_ID % 0,
                            "cwd": cwd, "cli_version": "0.145.0-fake"}}]
    for role, text in (default_prior(cwd, home) if prior is None else prior):
        entries.append(message(role, text))
    if reasoning:
        entries.append({"type": "response_item",
                        "payload": {"type": "reasoning", "id": "rs_1",
                                    "summary": [], "encrypted_content": "opaque"}})
    entries.append({"type": "turn_context",
                    "payload": {"model": model, "cwd": cwd,
                                "current_date": "2026-08-06"}})
    entries.append(message("user", prompt))
    entries.append({"type": "event_msg",
                    "payload": {"type": "agent_message", "message": answer}})
    entries.append(message("assistant", answer))
    return entries + list(extra)


def write_session(path: str, entries: list) -> None:
    with open(path, "wb") as handle:
        for entry in entries:
            handle.write((json.dumps(entry) + "\n").encode("utf-8"))


# --- the arms, copied into a throwaway root ---------------------------------

ARM_FILES = ("ARM.json", "FAMILY.json", "POLICY.md", "PROMPT.txt")


def file_digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def read_text(path: str) -> str:
    with open(path, "rb") as handle:
        return handle.read().decode("utf-8")


def arm_prompt_path(arms_root: str, arm: str) -> str:
    return os.path.join(arms_root, arm, "PROMPT.txt")


def arm_pair(arms_root: str, arm: str) -> tuple:
    """(T_low, T_high) as the strings `ARM.json` registers them — the pair the
    mirror is instantiated at, read from the arm's own artifact and from
    nowhere else (§2.2 [D-14])."""
    with open(os.path.join(arms_root, arm, "ARM.json"), "rb") as handle:
        definition = json.loads(handle.read().decode("utf-8"))
    return definition["thresholds"]["tLow"], definition["thresholds"]["tHigh"]


def build_arms_root(root: str, study: str) -> str:
    """A throwaway `arms/` root holding the study's REAL five arm artifacts, so
    every pinned digest in `harness/PINS.json` still answers for them — and
    NOTHING else: the tree this returns is the tree the DRIVER leaves.

    The authoring roots are deliberately not pre-created (round 9, finding 4).
    This helper used to make all five, and that one line is why no test could
    ever see the scorer refuse an arm the prefix had not reached: `batch.py`
    creates `arms/<X>/authoring/` with that arm's FIRST slot, so a batch that
    died in round 1 leaves 5−k of them absent, and a fixture that made them all
    in advance was scoring a population no batch can produce. `build_slot()`
    makes its own slot and its parents, so every population that reaches an arm
    still has that arm's root."""
    arms_root = os.path.join(root, "arms")
    for arm in ARMS:
        os.makedirs(os.path.join(arms_root, arm), exist_ok=True)
        for name in ARM_FILES:
            shutil.copyfile(os.path.join(study, "arms", arm, name),
                            os.path.join(arms_root, arm, name))
    return arms_root


def throwaway_root(prefix: str = "s012-tests-") -> str:
    """A temporary root whose PATH carries no §6 C6 leak token, because every
    slot's recorded working directory lives under it and admission re-screens
    that path. A machine whose temp directory spells a study term would fail
    every fixture with `isolation-unproven`, which is a true refusal about the
    machine and a useless one about the code — so it is refused here, loudly."""
    root = tempfile.mkdtemp(prefix=prefix)
    leaked = sorted(token for token in transcript_check.LEAK_TOKENS
                    if token in root.lower())
    if leaked:
        shutil.rmtree(root, True)
        raise RuntimeError(
            "the temporary directory %r carries the leak token(s) %r: set TMPDIR "
            "to a path with no study vocabulary in it and re-run" % (root, leaked))
    return root


def standin_study(root: str, wrapper: str, harness: str, *,
                  git: bool = True) -> str:
    """A stand-in study whose OWN path is what the wrapper resolves as
    `$STUDY`: the committed wrapper reached through a symlink (the bytes that
    run are the committed bytes; `$STUDY` follows the invocation path, not the
    file's real location), the committed harness symlinked in for the wrapper's
    python steps, and a git repo so the wrapper's worktree line sees
    production's shape rather than its degraded one.

    Round 9, finding 6 is why this exists: the wrapper anchors its slot guard
    at the `$STUDY` it resolves for itself, so a tree it will write into has to
    BE a study — the alternative was an override argument, which §2.7 caps out.
    The layout the wrapper constrains, and this helper therefore fixes:

      * the returned path is RESOLVED, because the anchor compares against
        `pwd -P` and a caller that built its slots from a symlinked spelling of
        the same directory would have every one of them refused;
      * the scratch parent must be a SIBLING of this directory, never inside
        it — the wrapper refuses a scratch that resolves inside its own
        worktree, and `git init` here is what makes that check answer;
      * `arms/` is deliberately NOT pre-created. The wrapper's registered
        branch makes its own anchor, and a fixture that made the population
        root first would falsify the driver tests that read the root's absence
        as "no slot was created".

    `git=False` skips the `git init` and is the ONE case that wants the
    degraded shape: the wrapper refuses a study it cannot find a worktree for
    (round 10, finding 6 registers that refusal in `harness/PORTS.md`), and a
    fixture whose stand-in is always a repository is exactly why no test
    reached that line for two rounds. Every other caller wants production's
    shape and takes the default.

    `PYTHONDONTWRITEBYTECODE` must be set for every interpreter that reaches
    the symlinked harness: it is the committed directory, and the §2.10 gate
    refuses on a cache beside the reviewed sources.
    """
    study = os.path.realpath(os.path.join(root, "study"))
    os.makedirs(os.path.join(study, "transcription"))
    os.symlink(wrapper, os.path.join(study, "transcription",
                                     os.path.basename(wrapper)))
    os.symlink(harness, os.path.join(study, "harness"))
    if git:
        subprocess.run(["git", "init", "-q", study], check=True)
    return study


# --- slot shapes ------------------------------------------------------------

def build_slot(slot: str, entry: dict, arms_root: str, pins: dict, *,
               answer: str = None, arm: str = None, prompt_arm: str = None,
               exit_status: int = 0, session: bool = True,
               completion_file: bool = True, entries=None, cwd: str = None,
               home: str = None, golden: str = None, session_id: str = None,
               call: dict = None) -> str:
    """One slot in the shape `transcription/authoring_call.sh` retains plus the
    three schedule stamps `batch.stamp_slot()` adds (§2.9), built in process so
    a scorer test needs neither bash nor a CLI.

    `entry` is the registered schedule's record for this slot — the source of
    the arm, the global index, the round, the position and the arm's own slot
    index — so a fixture cannot invent a place in the order.

    `arm` overrides the arm the CALL.json claims and `prompt_arm` overrides the
    arm whose PROMPT.txt goes into the transcript; both default to the arm
    whose tree the slot sits in, and the two exist because C4's first two
    fixtures are exactly the cases where they differ. `call` is a final
    overlay on the record, for the cases that need one member wrong.
    """
    os.makedirs(slot, exist_ok=True)
    name = os.path.basename(slot)
    tree_arm = entry["arm"]
    arm = tree_arm if arm is None else arm
    prompt_arm = tree_arm if prompt_arm is None else prompt_arm
    parent = os.path.dirname(slot)
    cwd = cwd or os.path.join(parent, "scratch-" + name)
    home = home or os.path.join(parent, "home-" + name)
    prompt = read_text(arm_prompt_path(arms_root, prompt_arm))
    if answer is None:
        answer = completion(full_records(*arm_pair(arms_root, tree_arm)))
    record = {
        "argv": ["codex", "exec", "--ignore-user-config", "-m",
                 pins["codex"]["model"]],
        "cwd": cwd, "home": home, "codexHome": os.path.join(home, ".codex"),
        "environment": ["PATH", "HOME", "TMPDIR", "CODEX_HOME"],
        # C6's constructed environment, in the shape the wrapper writes it:
        # six fixed system directories plus one per-run binary directory, and
        # a TMPDIR inside this run's own scratch.
        "environmentValues": {
            "PATH": ":".join(SYSTEM_PATH + (os.path.join(parent, "bin-" + name),)),
            "HOME": home,
            "TMPDIR": os.path.join(cwd, "tmp"),
            "CODEX_HOME": os.path.join(home, ".codex")},
        "pinsSha256": None, "goldenSha256": None if golden is None
                            else file_digest(golden),
        "environmentScrubbed": True, "codexHomeIsolated": True,
        "homeIsolated": True,
        # The recursive inventory C6 registers: the .codex directory the
        # wrapper made and the credential it copied into it, and nothing else.
        "isolatedHomeInventory": [".codex", ".codex/auth.json"],
        "operatorHomeSkillsPresent": True, "credentialCopied": True,
        "credentialRemoved": True, "isolation": "isolated",
        "ignoreUserConfig": True, "model": pins["codex"]["model"],
        "cli": pins["codex"]["version"],
        "binarySha256": pins["codex"]["binarySha256"],
        "exitStatus": exit_status, "newSessionCount": 1 if session else 0,
        "stdin": "closed (/dev/null)",
        # §3.1 gate 9 / §2.9: which arm this run was made with, which bytes
        # that arm's prompt was, and where the slot sits in §2.8's order. The
        # wrapper writes the first two and the driver the last three.
        "arm": arm,
        # The stamp follows the arm the CALL claims, not the bytes the
        # transcript happens to carry: C4 fixture 1 is the case where the
        # stamps are honest and the BYTES are another arm's, and it is only a
        # test of §3.1 gate 2 if the stamp checks pass first.
        "armPromptSha256": file_digest(arm_prompt_path(arms_root, arm)),
        "globalIndex": entry["globalIndex"], "round": entry["round"],
        "position": entry["position"], "slotIndex": entry["slotIndex"],
        # S8's duration is derived from these and no clock is ever read.
        "startedAt": "2026-08-07T%02d:%02d:00Z" % (entry["globalIndex"] % 24,
                                                   entry["globalIndex"] % 60),
        "endedAt": "2026-08-07T%02d:%02d:42Z" % (entry["globalIndex"] % 24,
                                                 entry["globalIndex"] % 60),
        "note": "test fixture slot",
    }
    record["pinsSha256"] = _registry_of_record()
    if call:
        record.update(call)
    _write_json(os.path.join(slot, "CALL.json"), record)
    for stream in ("stdout.raw", "stderr.raw"):
        with open(os.path.join(slot, stream), "wb") as handle:
            handle.write(answer.encode("utf-8") if stream == "stdout.raw" else b"")
    if session:
        if entries is None:
            entries = session_entries(prompt, answer, cwd, home,
                                      model=pins["codex"]["model"],
                                      session_id=session_id
                                      or SESSION_ID % entry["globalIndex"])
        write_session(os.path.join(slot, "session.jsonl"), entries)
        try:
            context = transcript_check.context_digests(
                os.path.join(slot, "session.jsonl"), record)
        except transcript_check.TranscriptError:
            # A session the checker refuses has no context to retain. The slot
            # keeps a placeholder so that admission reaches the transcript gate
            # and names the transcript, rather than stopping at a missing file.
            context = {"contextVersion": "1", "entries": []}
        _write_json(os.path.join(slot, "context.json"), context)
    if completion_file and exit_status == 0:
        with open(os.path.join(slot, "completion.txt"), "wb") as handle:
            handle.write(answer.encode("utf-8"))
    return slot


def _registry_of_record() -> str:
    """The digest of the COMMITTED `harness/PINS.json` — the registry every
    honest slot names (§2.10). The fixtures stamp it rather than a stand-in, so
    `admit()` runs its registry check against the value `main()` would compute
    and no scoring here needs the library override."""
    return score_rates.file_digest(score_rates.REGISTRY_OF_RECORD)


def _write_json(path: str, body) -> None:
    with open(path, "w") as handle:
        json.dump(body, handle, indent=2)
        handle.write("\n")


def write_golden(path: str, slot: str) -> str:
    """This study's golden capture, taken from a built slot exactly as
    `batch.py capture-golden` takes it from its probe runs (§3.2). One capture
    serves all five arms ([D-8]): the pre-prompt context precedes the arm's
    prompt and carries none of it."""
    with open(os.path.join(slot, "CALL.json")) as handle:
        call = json.load(handle)
    context = transcript_check.context_digests(os.path.join(slot, "session.jsonl"),
                                               call)
    _write_json(path, {"contextVersion": context["contextVersion"],
                       "entries": context["entries"],
                       "capturedFrom": [os.path.basename(slot)],
                       "note": "test fixture capture"})
    return path


def stamp_golden(golden: str, *slots: str) -> str:
    """Record, in each slot's CALL.json, the golden capture it was made
    against — what the real wrapper does from GOLDEN_SHA256 (§3.2).

    The fixtures derive their golden FROM a built slot, so the stamp cannot be
    written when that slot is built; every test that scores a fixture slot
    stamps it once the capture exists, exactly as the batch stamps the digest
    its preflight verified. It happens BEFORE the seal, so the stamp is inside
    the manifest §2.9 takes."""
    digest = file_digest(golden)
    for slot in slots:
        path = os.path.join(slot, "CALL.json")
        with open(path) as handle:
            call = json.load(handle)
        call["goldenSha256"] = digest
        _write_json(path, call)
    return digest


# --- the seal and the ledger, from the REAL driver --------------------------

@contextlib.contextmanager
def patched_study(study: str):
    """`batch.STUDY` pointed at a throwaway study root while ledger records are
    built, because §6 C5 rule 2 puts the ledger and the slot set in bijection
    "at the path the record names" and `batch.ledger_record()` writes that path
    STUDY-relative. Patching the root is what lets the fixtures use the real
    record builder instead of writing a record by hand."""
    original = batch.STUDY
    batch.STUDY = study
    try:
        yield
    finally:
        batch.STUDY = original


def seal_and_ledger(study: str, arms_root: str, pairs: list) -> list:
    """Seal every slot and build the chained ledger with the DRIVER's own
    machinery (§2.9): `batch.seal_slot()` writes each `SLOT-MANIFEST.json`,
    `batch.ledger_record()` builds the record, and `batch.record_digest()`
    links it to the one before. `pairs` is [(schedule entry, slot path)] in
    registered call order.

    Nothing here re-specifies the manifest or the chain: if the driver and the
    scorer disagreed about either, these fixtures would fail rather than agree
    with both.

    Every record carries wrapper exit 0 and no refusal code: the scorer
    recomputes admission from the retained bytes and never trusts the record
    (§3.3), so the fixtures give it nothing to lean on.
    """
    records, previous = [], None
    with patched_study(study):
        for entry, slot in pairs:
            manifest = batch.seal_slot(slot, entry)
            record = batch.ledger_record(entry, slot, 0, None, manifest,
                                         previous)
            previous = batch.record_digest(record)
            records.append(record)
    _write_json(os.path.join(arms_root, LEDGER_FILE), {
        "batchVersion": "3", "records": records,
        "note": "test fixture ledger, built by batch.py's own record machinery",
    })
    return records


def declare_shortfall(arms_root: str, records: list, present: int) -> dict:
    """§2.8's shortfall declaration over a fixture prefix, in the shape §6 C5
    rule 5 requires the scorer to read: the completed prefix's last global
    index, the slot it names as last, and the count of slots present.

    The member names are `score_rates.check_population()`'s, and
    `test_admission.py`'s
    `test_the_declared_shortfall_the_driver_writes_is_the_one_the_scorer_reads`
    is where `batch.py`'s own writer is held to them — a fixture that quietly
    agreed with only one of the two modules would hide exactly the
    disagreement C5 rule 5 exists to prevent.

    `completedRounds` counts WHOLE rounds, by the driver's own rule: the last
    slot's round number is what round 3's finding 15 found wrong in `batch.py`,
    and a fixture that kept it would declare one completed round over a prefix
    that ends three slots into round 1. `lastSlotEndedAtFrom` is null beside a
    null clock for the same reason the driver writes it that way — the scorer's
    empty-prefix reader looks at both (round 9, finding 4).
    """
    last = records[-1] if records else None
    counted: dict = {}
    for record in records:
        counted[record["round"]] = counted.get(record["round"], 0) + 1
    whole_rounds = 0
    while counted.get(whole_rounds + 1) == len(ARMS):
        whole_rounds += 1
    body = {
        "registeredRounds": 30, "registeredRunsPerArm": 30,
        "registeredSlots": 150,
        "completedRounds": whole_rounds,
        "completedThroughGlobalIndex": last["globalIndex"] if last else 0,
        "completedSlots": present,
        "lastSlot": last["path"] if last else None,
        "lastSlotEndedAt": None,
        "lastSlotEndedAtFrom": None,
        "reason": "test fixture: a prefix of the registered order",
    }
    _write_json(os.path.join(arms_root, SHORTFALL_FILE), body)
    return body


# --- a whole throwaway population -------------------------------------------

class Population:
    """A throwaway study root holding a PREFIX of §2.8's registered call order:
    the five arms' registered artifacts, one slot per scheduled entry, the
    golden capture, the sealed ledger and the shortfall declaration a short
    batch must carry (§2.8, C5 rule 5).

    The prefix is the registered order's own — slot 1 is global index 1 — so
    the arms are interleaved exactly as the batch would interleave them, and a
    five-slot prefix is one slot of every arm.
    """

    def __init__(self, root: str, study: str, pins: dict):
        self.root = root
        self.study = os.path.join(root, "study")
        self.pins = pins
        self.arms_root = build_arms_root(self.study, study)
        self.schedule = score_rates.registered_schedule()
        self.golden = os.path.join(self.study, "GOLDEN-CONTEXT.json")
        self.entries, self.slots, self.records = [], [], []

    def slot_path(self, entry: dict) -> str:
        return os.path.join(self.arms_root, entry["arm"], AUTHORING,
                            "run-%03d" % entry["slotIndex"])

    def build(self, specs: list, ledger: bool = True) -> "Population":
        """`specs` is one dict of `build_slot()` keyword arguments per slot, in
        registered call order, plus two hooks: `mutate(slot)` runs after the
        golden stamp and BEFORE the seal (an alteration the seal covers), and
        `break_seal(slot)` runs after it (the §2.9 alteration the seal is for).

        An EMPTY `specs` builds the ZERO prefix — the tree a batch that died
        before its first slot finished leaves (round 9, finding 4): the five
        arms' artifacts, no authoring root anywhere, and the declaration §2.8
        requires. `ledger=False` removes `BATCH.json` as well, which completes
        that tree: the driver writes the ledger inside the run loop, after a
        slot, so a batch with no slot never wrote one.
        """
        self.entries = self.schedule[:len(specs)]
        for entry, spec in zip(self.entries, specs):
            spec = dict(spec)
            spec.pop("mutate", None)
            spec.pop("break_seal", None)
            self.slots.append(build_slot(self.slot_path(entry), entry,
                                         self.arms_root, self.pins, **spec))
        # §3.2: the capture precedes the batch, and every plan below builds
        # its first slot honest, so the capture is taken from that one and
        # stamped into all of them.
        if self.slots:
            write_golden(self.golden, self.slots[0])
            stamp_golden(self.golden, *self.slots)
        else:
            # The capture precedes the batch, so the zero prefix has one too —
            # taken, as `batch.py capture` takes it, from a PROBE call that is
            # no slot of the registered order. It is built OUTSIDE `arms/` and
            # removed again, so the population root stays exactly what a batch
            # with no completed slot leaves: five arm artifact sets and not one
            # authoring root.
            probe = os.path.join(self.root, "golden-probe", "run-001")
            build_slot(probe, self.schedule[0], self.arms_root, self.pins)
            write_golden(self.golden, probe)
            shutil.rmtree(os.path.dirname(probe), True)
        for slot, spec in zip(self.slots, specs):
            if spec.get("mutate"):
                spec["mutate"](slot)
        self.records = seal_and_ledger(self.study, self.arms_root,
                                       list(zip(self.entries, self.slots)))
        if not ledger:
            os.remove(os.path.join(self.arms_root, LEDGER_FILE))
        for slot, spec in zip(self.slots, specs):
            if spec.get("break_seal"):
                spec["break_seal"](slot)
        if len(self.entries) < len(self.schedule):
            declare_shortfall(self.arms_root, self.records, len(self.slots))
        return self

    # -- the scoring, entered where the fixtures can enter it ----------------

    def score_runs(self) -> dict:
        """`score_rates.score()`'s own population sequence, from the line after
        `verify_preconditions()` down to the last `score_run()`.

        The preconditions are NOT skipped as a convenience: they bind the
        study's own committed artifacts — the ported bytes, the registered
        interpreter, the golden pin, the freeze digest and §6 C7's recorded
        control — and three of those are `null` in `harness/PINS.json` until
        their registered moments arrive (§2.10, §3.2, §6 C7), so no fixture
        population can satisfy them and none should be able to.
        `test_admission.py::test_the_scoring_refuses_before_it_reads_a_slot`
        asserts the ORDER those preconditions refuse in — the golden capture
        first, many checks above §6 C7's recorded control — over registries
        that test writes rather than over whatever stage the committed tree has
        reached, which is what that case proves and all it proves (round 10,
        finding 5: it used to be cited here as §6 C7's coverage, and it never
        reached §6 C7).
        `test_the_scorer_refuses_a_control_record_that_is_not_this_studys` is
        the C7 gate's own negative case, over a population that gets past this
        line; everything below it is the real thing, function for function and
        in `score()`'s own order.

        The endpoints are computed separately by `score()` because every rate
        block costs an exact 200-halving Clopper-Pearson interval in rationals
        (§4.3) — about a quarter-second each and 220 of them per scoring — and
        most of C4's fixtures are statements about a run's CODE, not about a
        rate.
        """
        arms_root = self.arms_root
        slots, unexpected = {}, {}
        for arm in ARMS:
            slots[arm], unexpected[arm] = score_rates.collect_slots(
                score_rates.slots_root(arms_root, arm))
        # `score()`'s own order: the declaration before the ledger, and the
        # ledger told what the declaration and the disk say, so the zero prefix
        # reads here exactly as it reads there (round 9, finding 4).
        shortfall = score_rates.terminality(arms_root, slots, len(self.schedule))
        ledger = score_rates.load_ledger(
            arms_root, shortfall, sum(len(paths) for paths in slots.values()))
        population = score_rates.check_population(arms_root, slots, ledger,
                                                  self.schedule, shortfall)
        by_key, prefix, counts = (population["byKey"], population["prefix"],
                                  population["counts"])
        ordered = [(key, entry[2]) for key, entry in
                   sorted(by_key.items(), key=lambda item: item[1][0]["globalIndex"])]
        seal_failures = []
        for key, path in ordered:
            _entry, record, _ = by_key[key]
            detail = score_rates.verify_seal(path, record)
            if detail is not None:
                seal_failures.append({"arm": key[0], "slot": key[1],
                                      "detail": detail})
        chain_failure = score_rates.verify_chain(ledger)
        sealed = not seal_failures and chain_failure is None
        reused = score_rates.session_reuse(ordered)
        arms = self.definitions()
        rows, records_by_arm = [], {arm: {} for arm in ARMS}
        for key, path in ordered:
            entry, record, _ = by_key[key]
            arm = key[0]
            row, accepted = score_rates.score_run(path, arm, arms_root,
                                                  self.golden, self.pins,
                                                  arms[arm], entry, record,
                                                  reused.get(key))
            rows.append(row)
            if row["valid"]:
                records_by_arm[arm][key[1]] = accepted
        n = self.pins["batch"]["n"]
        complete = len(ledger) == len(self.schedule) and all(
            counts[arm] == n for arm in ARMS)
        return {"runs": rows, "recordsByArm": records_by_arm,
                "unexpected": unexpected, "definitions": arms,
                "trials": n, "complete": complete,
                "seal": {"verified": sealed, "manifestFailures": seal_failures,
                         "chainFailure": chain_failure},
                # The population bookkeeping `score()`'s own document is
                # assembled from (round 7, finding 8): `publish()` below builds
                # the WHOLE published surface, and every one of these is a
                # member of it that a fixture would otherwise have to invent.
                "ledger": ledger, "prefix": prefix, "counts": counts,
                "shortfall": shortfall,
                "byKey": {(row["arm"], row["slot"]): row for row in rows}}

    def score(self) -> dict:
        """`score_runs()` plus §4's endpoints and §5's verdicts, by the same
        three calls `score_rates.score()` makes: one `score_arm()` per arm, the
        census lifted out of each arm block, and `compute_verdicts()` over the
        integers those blocks just wrote.

        The census is keyed by arm here and is a LIST in `RESULTS.json`; the
        two shapes are one computation either way, and `publish()` below is
        where the published one is built. Fixtures that want the published
        document ask for it there rather than reading this object as if it
        were one (round 7, finding 8)."""
        results = self.score_runs()
        n = results["trials"]
        arm_blocks = {arm: score_rates.score_arm(
            arm, results["definitions"][arm], n,
            [row for row in results["runs"] if row["arm"] == arm],
            results["recordsByArm"][arm], results["unexpected"][arm])
            for arm in ARMS}
        census_blocks = [arm_blocks[arm].pop("census") for arm in ARMS]
        results.update({
            "arms": arm_blocks,
            "census": {block["arm"]: block for block in census_blocks},
            "censusBlocks": census_blocks,
            "verdicts": score_rates.compute_verdicts(arm_blocks, n,
                                                     results["complete"],
                                                     results["seal"]["verified"])})
        return results

    def preconditions(self) -> dict:
        """The members `verify_preconditions()` returns, as far as a fixture
        population can honestly have them (round 7, finding 8).

        A fixture cannot run the real preconditions and must not pretend to:
        they bind the study's own committed artifacts, and three of §2.10's
        pins are the study's own, filled at their registered moments and never
        a fixture's to hold. So the two digests this population really does
        have — the registered mirror module and its own golden capture — are
        computed, and the three that belong to the study's freeze rather than
        to this population are `None`. They reach the
        `cell` block and nothing else; no rate, no interval and no verdict
        reads one, and `publish()` marks the document unpublishable in the way
        the scorer's own writer checks.
        """
        return {"portedFiles": {}, "study010LockSha256": None,
                "mirrorSha256": score_rates.file_digest(
                    score_rates.REGISTERED_MIRROR),
                "goldenSha256": score_rates.file_digest(self.golden),
                "preregistrationSha256": None,
                "registeredN": self.pins["batch"]["n"],
                "schedule": self.schedule,
                "arms": self.definitions()}

    def publish(self) -> dict:
        """The WHOLE `RESULTS.json` document this population would publish,
        built by `score_rates.results_document()` — the scorer's own writer
        (round 7, finding 8).

        §4.3 registers its interval-scope walk over `RESULTS.json`, and until
        this existed the walk had to make do with `score()`'s object: no
        `cell`, no `schedule`, no `crossArm`, and a census of another shape. A
        member the writer emits and a fixture did not build was outside a test
        whose whole purpose is to say which blocks may carry an interval.
        Calling the writer is what makes the walked object the published shape
        rather than a copy of it that has to be kept up to date by hand.

        The document is a FIXTURE's: `registryOverride` carries the digest this
        population supplied, which is exactly what that member is for, and
        `_write_outputs()` refuses to publish a table whose cell carries a
        non-null one (§2.10, §7). Nothing here can become a published rate.
        """
        results = self.score()
        registry = _registry_of_record()
        return score_rates.results_document(
            pins=self.pins, preconditions=self.preconditions(),
            registry_sha256=registry, override=registry,
            arms=results["definitions"], schedule=self.schedule,
            prefix=results["prefix"], ledger=results["ledger"],
            counts=results["counts"], shortfall=results["shortfall"],
            complete=results["complete"], n=results["trials"],
            sealed=results["seal"]["verified"],
            seal_failures=results["seal"]["manifestFailures"],
            chain_failure=results["seal"]["chainFailure"],
            arm_blocks=results["arms"], census_blocks=results["censusBlocks"],
            rows=results["runs"], verdicts=results["verdicts"])

    def definitions(self) -> dict:
        """The five arm definitions, loaded and cross-keyed exactly as
        `verify_preconditions()` does it: every arm keeps its own family for
        its own classes and takes ARM A's for S10's cross-scoring, read once so
        no arm can be cross-scored against a different A."""
        arms = {arm: score_rates.load_arm(self.arms_root, arm,
                                          self.pins["arms"][arm])
                for arm in ARMS}
        for arm in ARMS:
            arms[arm]["oldEdgeClasses"] = arms[BASELINE_ARM]["classes"]
        return arms


# --- §4.3's registered interval vectors, as fixtures ------------------------
#
# C4's last item: "the §4.3 registered test vectors at n = 25 and n = 50",
# transcribed here from PREREGISTRATION.md §4.3 INDEPENDENTLY of the copy
# `score_rates.REGISTERED_VECTORS` carries, so that
# `test_verdict_parity.py` can hold three things together — the frozen file,
# the scorer's data, and this transcription — rather than comparing the scorer
# to itself. n = 30 is this study's own denominator, n = 25 is [D-1]'s live
# alternative, and n = 50 is Study 011's, retained as a port control against
# numbers a predecessor already published.
REGISTERED_VECTORS = {
    30: {0: (0.0000, 0.1157), 1: (0.0008, 0.1722), 2: (0.0082, 0.2207),
         3: (0.0211, 0.2653), 4: (0.0376, 0.3072), 15: (0.3130, 0.6870),
         26: (0.6928, 0.9624), 27: (0.7347, 0.9789), 28: (0.7793, 0.9918),
         29: (0.8278, 0.9992), 30: (0.8843, 1.0000)},
    25: {0: (0.0000, 0.1372), 1: (0.0010, 0.2035), 2: (0.0098, 0.2603),
         3: (0.0255, 0.3122), 12: (0.2780, 0.6869), 22: (0.6878, 0.9745),
         23: (0.7397, 0.9902), 24: (0.7965, 0.9990), 25: (0.8628, 1.0000)},
    50: {0: (0.0000, 0.0711), 1: (0.0005, 0.1065), 25: (0.3553, 0.6447),
         40: (0.6628, 0.8997), 45: (0.7819, 0.9667), 50: (0.9289, 1.0000)},
}
# §5.1's two cuts at this study's own denominator: HIGH iff k >= 27 (the arm
# missed at most 3 of 30), LOW iff k <= 3.
REGISTERED_CUTS = {"trials": 30, "high": 27, "low": 3}


# --- the preregistration's own tables, read out of the frozen file ----------

def markdown_tables(body: str) -> list:
    """[(header cells, [row cells])] for every pipe table in a markdown file,
    found BY ITS SHAPE — a header row, a `---` rule, then rows — so a table
    that moves in the file is still the same table and a test cannot be
    anchored to a line number.

    Used by `test_partition_parity.py` and `test_verdict_parity.py` to diff
    §3.3's partition, §5.1's levels, §5.2's three contrasts and §5.3's decision
    table against the scorer's own encodings, which is what §6 C5's last
    paragraph and §3.3's own text register.
    """
    tables, rows = [], None
    for line in body.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            rows = None
            continue
        cells = [cell.strip() for cell in stripped[1:-1].split("|")]
        if rows is None:
            rows = [cells]
            tables.append(rows)
        else:
            rows.append(cells)
    parsed = []
    for rows in tables:
        if len(rows) < 2 or not all(set(cell) <= set("- :") and cell
                                    for cell in rows[1]):
            continue
        parsed.append((rows[0], rows[2:]))
    return parsed


def plain(cell: str) -> str:
    """One table cell with its markdown taken off: emphasis and code quoting
    removed, the preregistration's typographic operators written the way Python
    writes them, and whitespace collapsed.

    Applied to BOTH sides of every diff, because the scorer's tables quote some
    conditions in backticks (`gate` is false) and not others, and a difference
    in quoting is not a difference in a rule. Nothing else is touched: every
    word, number and operator survives, so a cut that moved still shows up.
    """
    text = cell.replace("**", "").replace("*", "").replace("`", "")
    for typographic, ascii_form in (("≥", ">="), ("≤", "<="),
                                    ("≠", "!="), ("→", "->")):
        text = text.replace(typographic, ascii_form)
    return " ".join(text.split())


def synthetic_row(arm: str, entry: dict, *, covered=(), raw=None, q=(),
                  q_only=(), old_edge=(), accepted: int = 1) -> dict:
    """One `score_run()` row, written directly at known integers.

    C4's eighth fixture asks for a synthetic POPULATION exercising every row of
    §5.3's decision table, and a decision-table row is a function of per-class
    counts over 30 slots per arm — 150 slots per case, six cases. What the rows
    below feed is the real arithmetic: `score_arm()` computes every k, every
    denominator, every interval and every level from them, `compute_verdicts()`
    computes the contrasts and the gate, and `decision_row()` picks the row. No
    verdict machinery is re-implemented here; only the per-slot counting the
    other fixtures exercise end to end on real bytes is short-circuited.
    """
    covered = sorted(covered)
    raw = covered if raw is None else sorted(raw)
    assert set(covered) <= set(raw), "H(r) is a subset of A(r) in every run"
    return {
        "arm": arm, "slot": "run-%03d" % entry["slotIndex"],
        "globalIndex": entry["globalIndex"], "round": entry["round"],
        "position": entry["position"], "valid": True,
        "code": None, "detail": None, "batchCode": None,
        # Both stamp-derived members, so the two row builders stay in step: a
        # synthetic row reaches `score_arm()` and never `results_document()`,
        # but a row shape that agrees with `score_run()`'s only by accident is
        # one a later reader has to check (round 10, finding 9).
        "wallClockSeconds": 42, "utcDates": ["2026-08-07"],
        "accepted": accepted, "dropped": 0, "dropCodes": {},
        "h": accepted, "q": len(q),
        # A synthetic row always carries a parseable array — the array is what
        # `accepted` counts — so §3.3's `authoring-empty` row is False by
        # construction and the wider "reached no class" quantity is what varies
        # (round 3, finding 13).
        "authoringEmpty": False,
        "noParseableArray": False,
        "coveredNothing": not covered,
        "coveredClasses": covered, "rawClasses": raw, "qClasses": sorted(q),
        "qOnlyClasses": sorted(q_only), "oldEdgeClasses": sorted(old_edge),
        "classesCovered": len(covered),
        "classMembers": {str(index): {"h": [], "q": []} for index in range(6)},
        "completionSha256": "sha256:" + "%064d" % entry["globalIndex"],
        "compiledSha256": None,
    }


# --- the stand-in CLI and the stand-in operator HOME -------------------------
#
# Added for `test_batch.py`, which drives the REAL wrapper and the REAL driver:
# the only stand-ins are the binary and the operator's home, and neither
# reaches a network or a model. Everything above this line is used by the
# in-process fixtures, which invoke neither.

FAKE_CLI = '''#!__PYTHON__
"""A stand-in for the pinned codex CLI: it answers --version, writes a session
into $CODEX_HOME, prints a planned completion, and exits with a planned status.
It never calls a model and never reaches the network. The plan and the call
counter live BESIDE this file, because the wrapper scrubs the environment with
env -i and only PATH, HOME, TMPDIR and CODEX_HOME survive — and because a plan
inside the binary would change its digest, which the wrapper checks for real.

It reproduces ONE empirical behaviour of the pinned CLI that Study 010's fifth
pre-freeze review found: skills under $HOME/.agents reach the model, as a
pre-prompt message. That is what a fresh HOME excludes per run, and it is what
makes the §6 C7 negative control able to FAIL the golden match instead of being
a control whose outcome the harness decides."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# The tests directory AND the harness beside it: `fixtures` imports the harness
# modules, and this process is `env -i`-scrubbed, so nothing it needs is on the
# path unless it is put there. The import itself is deferred past the --version
# branch, which the wrapper takes before every call and which needs none of it.
sys.path[:0] = ["__TESTS__", os.path.dirname("__TESTS__")]


def main(argv):
    if "--version" in argv:
        # The version the wrapper gates on, read from a file BESIDE the binary
        # so a test can drift it between invocations without moving the digest
        # the registry pins. `test_batch.py` uses that to produce the one slot
        # shape a batch cannot otherwise reach: a wrapper that refused at its
        # own preflight, so the slot carries a REFUSAL.json and no CALL.json.
        marker = os.path.join(HERE, "version.txt")
        if os.path.exists(marker):
            with open(marker) as handle:
                print(handle.read().strip())
            return 0
        print("codex-cli 0.145.0-fake")
        return 0
    with open(os.path.join(HERE, "plan.json")) as handle:
        plan = json.load(handle)
    counter = os.path.join(HERE, "counter")
    index = 0
    if os.path.exists(counter):
        with open(counter) as handle:
            index = int(handle.read().strip())
    with open(counter, "w") as handle:
        handle.write(str(index + 1))
    step = plan[index] if index < len(plan) else plan[-1]
    import fixtures
    if step.get("sleep"):
        # A call still in flight: the credential copy exists, the slot is not
        # sealed, and a signal arriving now is the case the traps cover.
        time.sleep(step["sleep"])
    prompt = argv[-1]
    model = argv[argv.index("-m") + 1]
    home = os.environ["HOME"]
    prior = fixtures.default_prior(os.getcwd(), home)
    skills = os.path.join(home, ".agents", "skills")
    if os.path.isdir(skills):
        prior = prior + [("developer", "<available_skills>\\n%s\\n</available_skills>"
                          % ", ".join(sorted(os.listdir(skills))))]
    sessions = os.path.join(os.environ["CODEX_HOME"], "sessions")
    os.makedirs(sessions, exist_ok=True)
    entries = fixtures.session_entries(prompt, step["completion"], os.getcwd(),
                                       home, model, prior=prior,
                                       session_id=fixtures.SESSION_ID % (index + 1))
    if step.get("no_assistant"):
        # Exit 0 with a transcript carrying no assistant message: the shape that
        # kills the wrapper mid-run (completion extraction raises under set -e),
        # used to prove the credential cleanup survives an abnormal death.
        entries = entries[:-2]
    if step.get("no_session"):
        # No transcript at all: the wrapper finds no new session, retains no
        # context, and exits 11. §6 C7's third registered outcome runs on it.
        sys.stdout.write(step["completion"])
        return int(step.get("exit", 0))
    fixtures.write_session(os.path.join(sessions, "rollout-%d.jsonl" % index), entries)
    sys.stdout.write(step["completion"])
    return int(step.get("exit", 0))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
'''

# The sentinel credential the wrapper-driven tests plant in a fake operator
# HOME. No retained artifact may contain these bytes: the wrapper copies the
# credential into the isolated home for the call and deletes it when the slot is
# sealed, and `test_batch.py` scans every retained byte and every leftover under
# the scratch parent for the token.
SENTINEL_CREDENTIAL = '{"OPENAI_API_KEY": "sk-s012-sentinel-never-retained"}\n'
SENTINEL_TOKEN = "sk-s012-sentinel-never-retained"
SENTINEL_SKILL = "sentinel-skill-that-must-not-reach-the-model"


def write_operator_home(root: str, credential: bool = True,
                        skills: bool = False) -> str:
    """A stand-in for the operator's real HOME: a `.codex/auth.json` carrying the
    sentinel credential, and optionally a `.agents/skills` tree of the kind Study
    010 found reaching the model. Nothing here touches the real one."""
    os.makedirs(os.path.join(root, ".codex"), exist_ok=True)
    if credential:
        with open(os.path.join(root, ".codex", "auth.json"), "w") as handle:
            handle.write(SENTINEL_CREDENTIAL)
    if skills:
        os.makedirs(os.path.join(root, ".agents", "skills", SENTINEL_SKILL),
                    exist_ok=True)
    return root


def write_fake_cli(directory: str, plan: list, python: str, tests_dir: str) -> str:
    """The stand-in CLI plus its plan; returns the binary path whose digest the
    test registry pins, so the wrapper's digest check runs for real."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "codex")
    with open(path, "w") as handle:
        handle.write(FAKE_CLI.replace("__PYTHON__", python).replace("__TESTS__",
                                                                   tests_dir))
    os.chmod(path, 0o755)
    write_plan(directory, plan)
    return path


def write_plan(directory: str, plan: list) -> None:
    """The stand-in CLI's plan, rewritten without touching the binary — so the
    digest the registry pins does not move and the wrapper's binary check is
    still a check."""
    with open(os.path.join(directory, "plan.json"), "w") as handle:
        json.dump(plan, handle)


def write_cli_version(directory: str, version: str) -> None:
    """Drift the stand-in CLI's reported version without touching its bytes: the
    wrapper's binary-digest check still passes and its VERSION check refuses, so
    the refusal is the wrapper's own preflight and not a driver-side stand-in."""
    with open(os.path.join(directory, "version.txt"), "w") as handle:
        handle.write(version + "\n")
