#!/usr/bin/env python3
"""Throwaway fixtures with a KNOWN coverage profile, and the machinery to put
them into slot-shaped directories.

Nothing here is study data: the records are invented for the tests, their ids
are not the authored ones, and no real completion, session, or codex binary is
involved. What the fixtures buy is the control the design brief asks for — a
completion whose H ∩ class membership is known by construction for every one of
the six classes, so the counting code cannot silently miscount and call it a
finding. COMPLETION_A reaches classes 1, 3 and 4 with correctly-labelled
records, reaches class 2 only with a mislabelled one, and reaches classes 0
and 5 not at all; COMPLETION_B adds one record at risk exactly 70, which
reaches class 0 as well.

This module deliberately does NOT import the harness at module scope: the fake
CLI (`write_fake_cli`) imports it from inside an env -i scrubbed subprocess
where only the tests directory is on sys.path, and it must not drag the scorer
in with it.
"""
from __future__ import annotations
import json
import os
import stat

MODEL = "gpt-5.6-sol"

# --- the records -----------------------------------------------------------

HARBOR = {  # H, class 1 only (70.5 is at least 70 and below 71, not exactly 70)
    "caseId": "harbor-freight-atlantic",
    "vendor": {"legalName": "Harbor Freight Atlantic BV", "sanctionsHit": False,
               "registeredCountry": "NL", "handlesPersonalData": False,
               "riskScore": "70.5"},
    "decision": {"outcome": "manual-review", "decidedBy": "reviewer-1",
                 "decidedAt": "2026-06-02T09:00:00Z"},
}
MERIDIAN = {  # H, class 3 (40 <= 55 < 70)
    "caseId": "meridian-data-works",
    "vendor": {"legalName": "Meridian Data Works GmbH", "sanctionsHit": False,
               "registeredCountry": "DE", "handlesPersonalData": True,
               "riskScore": "55"},
    "decision": {"outcome": "manual-review", "decidedBy": "reviewer-2",
                 "decidedAt": "2026-06-03T11:30:00Z"},
}
CYPRESS = {  # H, class 4 (unsanctioned, registered in SY)
    "caseId": "cypress-medical-supply",
    "vendor": {"legalName": "Cypress Medical Supply", "sanctionsHit": False,
               "registeredCountry": "SY", "handlesPersonalData": True,
               "riskScore": "88.75"},
    "decision": {"outcome": "reject", "decidedBy": "reviewer-3",
                 "decidedAt": "2026-06-04T14:15:00Z"},
}
NORTHWIND = {  # H, no class at all: every predicate requires no sanctions hit
    "caseId": "northwind-office-goods",
    "vendor": {"legalName": "Northwind Office Goods", "sanctionsHit": True,
               "registeredCountry": "KP", "handlesPersonalData": False,
               "riskScore": "91"},
    "decision": {"outcome": "reject", "decidedBy": "reviewer-4",
                 "decidedAt": "2026-06-05T08:45:00Z"},
}
AURORA = {  # Q: the mirror says manual-review, the record says clear.
    "caseId": "aurora-payments-eu",     # classes 2 and 3, mislabelled
    "vendor": {"legalName": "Aurora Payments EU", "sanctionsHit": False,
               "registeredCountry": "FR", "handlesPersonalData": True,
               "riskScore": "40"},
    "decision": {"outcome": "clear", "decidedBy": "reviewer-5",
                 "decidedAt": "2026-06-06T16:20:00Z"},
}
BAD_SCORE = {  # dropped: decimal-form (a leading zero is not canonical)
    "caseId": "tallow-bay-imports",
    "vendor": {"legalName": "Tallow Bay Imports", "sanctionsHit": False,
               "registeredCountry": "PT", "handlesPersonalData": False,
               "riskScore": "07"},
    "decision": {"outcome": "clear", "decidedBy": "reviewer-6",
                 "decidedAt": "2026-06-07T10:00:00Z"},
}
DUPLICATE = {  # dropped: duplicate-id (MERIDIAN already claimed the caseId)
    "caseId": "meridian-data-works",
    "vendor": {"legalName": "Meridian Data Works GmbH (re-filed)",
               "sanctionsHit": False, "registeredCountry": "DE",
               "handlesPersonalData": True, "riskScore": "56"},
    "decision": {"outcome": "manual-review", "decidedBy": "reviewer-7",
                 "decidedAt": "2026-06-08T12:00:00Z"},
}
STONEBRIDGE = {  # H, classes 0 and 1 (risk exactly 70)
    "caseId": "stonebridge-logistics",
    "vendor": {"legalName": "Stonebridge Logistics Ltd", "sanctionsHit": False,
               "registeredCountry": "IE", "handlesPersonalData": False,
               "riskScore": "70"},
    "decision": {"outcome": "manual-review", "decidedBy": "reviewer-8",
                 "decidedAt": "2026-06-09T09:10:00Z"},
}

RECORDS_A = [HARBOR, MERIDIAN, CYPRESS, NORTHWIND, AURORA, BAD_SCORE, DUPLICATE]
RECORDS_B = RECORDS_A[:4] + [STONEBRIDGE] + RECORDS_A[4:]

# One element per drop code, in the compiler's own check order, so a reordered
# or skipped check shows up as a changed histogram rather than as nothing.
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


RECORDS_DROPS = [
    RIDGELINE,
    "not a record at all",                                       # schema
    _variant("tallow-bay-imports", **{"vendor.riskScore": "07"}),        # decimal-form
    _variant("kestrel-freight", **{"vendor.registeredCountry": "nl"}),   # country-form
    _variant("Bad_Id"),                                                  # id-form
    _variant("juniper-cleaning", **{"decision.outcome": "approve"}),      # outcome-value
    _variant("solano-textiles", **{"decision.decidedAt": "2026-06-31T00:00:00Z"}),
    _variant("ridgeline-supplies"),                                      # duplicate-id
]

# The bracketed aside never parses as a JSON array, so the record array wins
# extraction — the compiler's widest-span rule, exercised rather than assumed.
PREAMBLE = "Here are the office's files [7 filed, some rejected at intake]:\n\n"
TRAILER = "\n\nNo commentary follows."


def completion(records: list) -> str:
    return PREAMBLE + json.dumps(records, indent=2) + TRAILER


COMPLETION_A = completion(RECORDS_A)
COMPLETION_B = completion(RECORDS_B)
COMPLETION_DROPS = completion(RECORDS_DROPS)
# §3.3's authoring-empty run: admissible evidence, nothing usable in it. Not a
# pipeline failure — the author simply produced no array.
COMPLETION_EMPTY = ("The office keeps its files under seal and declines to "
                    "reproduce them here.")

DROP_HISTOGRAM = {"schema": 1, "decimal-form": 1, "country-form": 1, "id-form": 1,
                  "outcome-value": 1, "timestamp-form": 1, "duplicate-id": 1}

# The profile the tests hold the counting code to, by construction.
PROFILE_A = {
    "accepted": ["aurora-payments-eu", "cypress-medical-supply",
                 "harbor-freight-atlantic", "meridian-data-works",
                 "northwind-office-goods"],
    "dropCodes": {"decimal-form": 1, "duplicate-id": 1},
    "h": ["cypress-medical-supply", "harbor-freight-atlantic",
          "meridian-data-works", "northwind-office-goods"],
    "q": ["aurora-payments-eu"],
    "covered": [1, 3, 4],          # H reaches these
    "raw": [1, 2, 3, 4],           # any accepted record reaches these
    "qIntersection": [2, 3],       # Q reaches these
    "qOnly": [2],                  # ONLY Q reaches these
    "members": {
        "0": {"h": [], "q": []},
        "1": {"h": ["harbor-freight-atlantic"], "q": []},
        "2": {"h": [], "q": ["aurora-payments-eu"]},
        "3": {"h": ["meridian-data-works"], "q": ["aurora-payments-eu"]},
        "4": {"h": ["cypress-medical-supply"], "q": []},
        "5": {"h": [], "q": []},
    },
}
PROFILE_B = {
    "accepted": sorted(PROFILE_A["accepted"] + ["stonebridge-logistics"]),
    "dropCodes": {"decimal-form": 1, "duplicate-id": 1},
    "h": sorted(PROFILE_A["h"] + ["stonebridge-logistics"]),
    "q": ["aurora-payments-eu"],
    "covered": [0, 1, 3, 4],
    "raw": [0, 1, 2, 3, 4],
    "qIntersection": [2, 3],
    "qOnly": [2],
}

# --- session shapes --------------------------------------------------------

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
    vocabulary — the leak screen must pass on an honest session."""
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


def session_entries(prompt: str, answer: str, cwd: str, home: str,
                    model: str = MODEL, prior=None, reasoning: bool = True,
                    extra=()) -> list:
    """A transcript in the shape a real pinned-CLI session carries: codex's own
    boilerplate, an inert reasoning item, a turn context, the registered prompt
    as the last user message, and one assistant answer."""
    entries = [{"type": "session_meta",
                "payload": {"id": "00000000-0000-4000-8000-000000000000",
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


# --- slot shapes -----------------------------------------------------------

def read_prompt(study: str) -> str:
    with open(os.path.join(study, "transcription", "PROMPT.txt"), "rb") as handle:
        return handle.read().decode("utf-8")


def build_slot(slot: str, answer: str, study: str, pins: dict, *,
               exit_status: int = 0, session: bool = True,
               completion_file: bool = True, entries=None,
               cwd: str = None, home: str = None) -> str:
    """One slot in the shape transcription/authoring_call.sh retains, built in
    process so a scorer test needs neither bash nor a CLI."""
    import transcript_check

    os.makedirs(slot, exist_ok=True)
    name = os.path.basename(slot)
    cwd = cwd or os.path.join(os.path.dirname(slot), "scratch-" + name)
    home = home or os.path.join(os.path.dirname(slot), "home-" + name)
    prompt = read_prompt(study)
    call = {
        "argv": ["codex", "exec", "--ignore-user-config", "-m", pins["codex"]["model"]],
        "cwd": cwd, "home": home, "codexHome": os.path.join(home, ".codex"),
        "environment": ["PATH", "HOME", "TMPDIR", "CODEX_HOME"],
        "environmentValues": {"PATH": "/usr/bin:/bin", "HOME": home,
                              "TMPDIR": os.path.join(cwd, "tmp"),
                              "CODEX_HOME": os.path.join(home, ".codex")},
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
        "stdin": "closed (/dev/null)", "note": "test fixture slot",
    }
    with open(os.path.join(slot, "CALL.json"), "w") as handle:
        json.dump(call, handle, indent=2)
        handle.write("\n")
    for stream in ("stdout.raw", "stderr.raw"):
        with open(os.path.join(slot, stream), "wb") as handle:
            handle.write(answer.encode("utf-8") if stream == "stdout.raw" else b"")
    if session:
        entries = session_entries(prompt, answer, cwd, home,
                                  model=pins["codex"]["model"]) if entries is None else entries
        write_session(os.path.join(slot, "session.jsonl"), entries)
        try:
            context = transcript_check.context_digests(
                os.path.join(slot, "session.jsonl"), call)
        except transcript_check.TranscriptError:
            # A session the checker refuses has no context to retain. The slot
            # keeps a placeholder so that admission reaches the transcript gate
            # and names the transcript, rather than stopping at a missing file.
            context = {"contextVersion": "1", "entries": []}
        with open(os.path.join(slot, "context.json"), "w") as handle:
            json.dump(context, handle, indent=2)
            handle.write("\n")
    if completion_file and exit_status == 0:
        with open(os.path.join(slot, "completion.txt"), "wb") as handle:
            handle.write(answer.encode("utf-8"))
    return slot


def write_golden(path: str, slot: str) -> str:
    """This study's golden capture, taken from a built slot exactly as
    batch.py capture takes it from its two probe runs."""
    import transcript_check

    with open(os.path.join(slot, "CALL.json")) as handle:
        call = json.load(handle)
    context = transcript_check.context_digests(os.path.join(slot, "session.jsonl"), call)
    with open(path, "w") as handle:
        json.dump({"contextVersion": context["contextVersion"],
                   "entries": context["entries"],
                   "capturedFrom": [os.path.basename(slot)],
                   "note": "test fixture capture"}, handle, indent=2)
        handle.write("\n")
    return path


def build_tree(root: str, answers: list, study: str, pins: dict) -> tuple:
    """(slots dir, golden path) for a list of completions, one slot each."""
    slots_dir = os.path.join(root, "authoring")
    os.makedirs(slots_dir, exist_ok=True)
    for index, answer in enumerate(answers, 1):
        build_slot(os.path.join(slots_dir, "run-%03d" % index), answer, study, pins)
    golden = write_golden(os.path.join(root, "GOLDEN-CONTEXT.json"),
                          os.path.join(slots_dir, "run-001"))
    return slots_dir, golden


# --- the stand-in CLI ------------------------------------------------------

FAKE_CLI = '''#!__PYTHON__
"""A stand-in for the pinned codex CLI: it answers --version, writes a session
into $CODEX_HOME, prints a planned completion, and exits with a planned status.
It never calls a model and never reaches the network. The plan and the call
counter live beside this file, because the wrapper scrubs the environment with
env -i and only PATH, HOME, TMPDIR and CODEX_HOME survive.

It reproduces ONE empirical behaviour of the pinned CLI that Study 010's fifth
pre-freeze review found: skills under $HOME/.agents reach the model, as a
pre-prompt message. That is what a fresh HOME excludes per run, and it is what
makes the §6 C7 negative control able to fail the golden match instead of
being a control whose outcome the harness decides."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "__TESTS__")
import fixtures


def main(argv):
    if "--version" in argv:
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
                                       home, model=model, prior=prior)
    if step.get("no_assistant"):
        # Exit 0 with a transcript carrying no assistant message: the shape
        # that kills the wrapper mid-run (completion extraction raises under
        # set -e), used to prove cleanup survives an abnormal death.
        entries = entries[:-2]
    fixtures.write_session(os.path.join(sessions, "rollout-%d.jsonl" % index), entries)
    sys.stdout.write(step["completion"])
    return int(step.get("exit", 0))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
'''

# The sentinel credential the wrapper-driven tests plant in a fake operator
# HOME. No retained artifact may contain these bytes: the wrapper copies the
# credential into the isolated home for the call and deletes it when the slot
# is sealed, and harness/tests/test_batch.py scans every retained byte for it.
SENTINEL_CREDENTIAL = '{"OPENAI_API_KEY": "sk-s011-sentinel-never-retained"}\n'
SENTINEL_TOKEN = "sk-s011-sentinel-never-retained"
SENTINEL_SKILL = "sentinel-skill-that-must-not-reach-the-model"


def write_operator_home(root: str, credential: bool = True,
                        skills: bool = False) -> str:
    """A stand-in for the operator's real HOME: a `.codex/auth.json` carrying
    the sentinel credential, and optionally a `.agents/skills` tree of the kind
    Study 010 found reaching the model. Nothing here touches the real one."""
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
    test pins, so the wrapper's digest check runs for real."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "codex")
    with open(path, "w") as handle:
        handle.write(FAKE_CLI.replace("__PYTHON__", python).replace("__TESTS__", tests_dir))
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    with open(os.path.join(directory, "plan.json"), "w") as handle:
        json.dump(plan, handle)
    return path
