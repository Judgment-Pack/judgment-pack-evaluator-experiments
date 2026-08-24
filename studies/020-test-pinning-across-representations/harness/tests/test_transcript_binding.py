#!/usr/bin/env python3
"""The full transcript binding, and the CAUSE it attributes each refusal to —
round 1's R1-5.

The finding: `transcript_check.check()` was never invoked for a scored slot. The
wrapper called `extract_completion()` and `context_digests()`; the scorer trusted
the golden digest `CALL.json` was stamped with and the completion the wrapper had
already written; and the only non-test caller of `check_golden()` was the golden
capture itself. So a transcript carrying the wrong prompt, an extra pre-prompt
turn, or a completion that is not its last assistant message stayed in the
population, and §3.1's six gates guarded the recapture and nothing else.

The finding's second half is why this module is not one assertion that `check()`
is called: wiring the gate in WHOLESALE would have made a second attribution
error. `check()` refuses every call and tool form, and a model that used a tool
was violating §3's single-shot, no-tools INSTRUCTION — that is the author's
failure, an authoring outcome retained in the denominator and scoring zero, and
filing it as pipeline-invalid would quietly delete exactly the runs the
instruction exists to catch. A mismatched prompt, a drifted golden context, a
mangled log or a mis-extracted completion is the apparatus, and §1a excludes it.

So every case below is adversarial and every case names a SIDE. The module holds
three kinds of test:

* one per reason tag, over a synthetic transcript built to trigger exactly that
  refusal, asserting the reason, the side and the §1a code;
* the closure tests — every reason in the map is reachable, every reachable
  reason is in the map, every raise site in `transcript_check.py` carries one,
  and every code the gate can assign is a key of `batch.CODE_PARTITION` on the
  side the map claims;
* the fail-closed tests — a refusal with no reason, and a refusal with a reason
  nobody registered, both raise rather than answering.

The transcripts are BUILT rather than captured, and deliberately: a captured one
would exercise the admissible path and nothing else, and every case here is about
a path a real session is not supposed to take.
"""
from __future__ import annotations
import ast
import json
import os

import pytest

import batch
import transcript_check

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)

# A working directory the call records. It is a STRING and not this machine's
# tmp path on purpose: `check()` screens the recorded cwd for leak tokens and
# normalizes it out of the pre-prompt context, and a pytest tmp path carries the
# TEST'S OWN NAME, which would make some cases pass or fail by what they are
# called.
CWD = "/srv/w/0001"
HOME = "/srv/h/0001"
MODEL = "the-locked-model"
PROMPT = "Author the artifact. Reply with the marker block and nothing else.\n"
ANSWER = "MARKER:\n```\n{}\n```\n"
# Codex's own pre-prompt boilerplate, in the two-item shape `_events()` reads it.
# Screened by `test_the_fixtures_own_boilerplate_carries_no_leak_token` below, so
# a fixture cannot make a case pass or fail for a reason the case is not about.
PRIOR = (
    ("developer", "You are running with a workspace sandbox rooted at "
                  "%s. Files outside it are read-only." % CWD),
    ("developer", "You are a general coding agent. Session files live under "
                  "%s." % HOME),
)


def message(role, text):
    kind = transcript_check.ITEM_KIND[role]
    return {"type": "response_item",
            "payload": {"type": "message", "role": role,
                        "content": [{"type": kind, "text": text}]}}


def rows_for(prompt=PROMPT, answer=ANSWER, prior=PRIOR, model=MODEL, cwd=CWD):
    rows = [{"type": "session_meta",
             "payload": {"id": "00000000-0000-4000-8000-000000000001",
                         "cwd": cwd, "cli_version": "0.145.0"}}]
    for role, text in prior:
        rows.append(message(role, text))
    rows.append({"type": "response_item",
                 "payload": {"type": "reasoning", "id": "rs_1", "summary": [],
                             "encrypted_content": "opaque"}})
    rows.append({"type": "turn_context",
                 "payload": {"model": model, "cwd": cwd}})
    rows.append(message("user", prompt))
    rows.append(message("assistant", answer))
    return rows


class Slot:
    """One built slot: the five paths `classify()` binds, and the knobs each
    adversarial case turns."""

    def __init__(self, root, rows=None, prompt=PROMPT, completion=None,
                 exit_status=0, golden_rows=None, golden=None,
                 completion_bytes=None):
        self.root = str(root)
        os.makedirs(self.root, exist_ok=True)
        self.session = os.path.join(self.root, "session.jsonl")
        self.prompt = os.path.join(self.root, "PROMPT.txt")
        self.completion = os.path.join(self.root, "completion.txt")
        self.call = os.path.join(self.root, "CALL.json")
        self.golden = os.path.join(self.root, "GOLDEN-CONTEXT.json")
        rows = rows_for() if rows is None else rows
        self._write_session(self.session, rows)
        with open(self.prompt, "wb") as handle:
            handle.write(prompt.encode("utf-8"))
        if completion_bytes is not None:
            body = completion_bytes
        else:
            body = (ANSWER if completion is None else completion).encode("utf-8")
        with open(self.completion, "wb") as handle:
            handle.write(body)
        with open(self.call, "w") as handle:
            json.dump({"cwd": CWD, "home": HOME, "exitStatus": exit_status},
                      handle)
        if golden is None:
            source = self.session
            if golden_rows is not None:
                source = os.path.join(self.root, "golden-session.jsonl")
                self._write_session(source, golden_rows)
            golden = transcript_check.context_digests(
                source, {"cwd": CWD, "home": HOME})
        with open(self.golden, "w") as handle:
            json.dump(golden, handle)

    @staticmethod
    def _write_session(path, rows):
        with open(path, "wb") as handle:
            for row in rows:
                handle.write((json.dumps(row) + "\n").encode("utf-8"))

    def verdict(self, arm="A", effort=None):
        # `effort` defaults to None — the pin-unfilled posture — so every case
        # written before the gate-5 extension stays about what it is about.
        return transcript_check.classify(self.session, self.prompt,
                                         self.completion, self.call,
                                         self.golden, model=MODEL, arm=arm,
                                         effort=effort)


def assert_refused(verdict, reason, side):
    assert verdict["admissible"] is False, verdict
    assert verdict["reason"] == reason, verdict
    assert verdict["side"] == side, verdict
    assert verdict["code"] in batch.CODE_PARTITION, verdict
    assert batch.CODE_PARTITION[verdict["code"]][0] == side, verdict


# --------------------------------------------------------------------------
# the fixture's own hygiene
# --------------------------------------------------------------------------

def test_the_fixtures_own_boilerplate_carries_no_leak_token():
    """A fixture that leaked would make half the cases below refuse for a reason
    they are not about, and the refusal would read as a finding."""
    transcript_check.screen_prior_context(list(PRIOR), len(PRIOR), [CWD, HOME])


def test_the_built_transcript_is_admissible(tmp_path):
    """The floor every adversarial case is measured against: with nothing wrong,
    the gate admits. Without this, a case could 'pass' because the builder is
    broken rather than because the mutation was caught."""
    verdict = Slot(tmp_path / "clean").verdict()
    assert verdict == {"admissible": True, "reason": None, "side": None,
                       "code": None, "message": verdict["message"]}


# --------------------------------------------------------------------------
# the AUTHOR's side — retained, counted, scoring zero
# --------------------------------------------------------------------------

def test_a_tool_call_is_the_authors_protocol_violation(tmp_path):
    """§3: authoring is single-shot, NO TOOLS. A transcript carrying a call form
    is the author disobeying the instruction — an authoring outcome. Filing it as
    apparatus would delete the very runs the instruction exists to detect, and
    would do it silently, by excluding them from the denominator."""
    rows = rows_for()
    rows.insert(-1, {"type": "response_item",
                     "payload": {"type": "function_call", "name": "shell",
                                 "arguments": "{\"cmd\":[\"ls\"]}",
                                 "call_id": "c1"}})
    verdict = Slot(tmp_path / "tool", rows=rows,
                   golden_rows=rows_for()).verdict()
    assert_refused(verdict, "tool-use", "authoring")
    assert verdict["code"] == "author-protocol-violation"


def test_a_tool_role_message_is_the_authors_protocol_violation(tmp_path):
    rows = rows_for()
    rows.insert(-1, {"type": "response_item",
                     "payload": {"type": "message", "role": "tool",
                                 "content": [{"type": "output_text",
                                              "text": "exit 0"}]}})
    assert_refused(Slot(tmp_path / "tool-role", rows=rows,
                        golden_rows=rows_for()).verdict(),
                   "tool-use", "authoring")


def test_a_reasoning_item_smuggling_a_call_is_the_authors_side(tmp_path):
    """The inert-reasoning rule exists because a reasoning payload is the one
    shape a call can hide in. It is still the author calling."""
    rows = rows_for()
    rows.insert(-1, {"type": "response_item",
                     "payload": {"type": "reasoning", "id": "rs_2",
                                 "summary": [], "name": "shell",
                                 "arguments": "{}"}})
    assert_refused(Slot(tmp_path / "smuggled", rows=rows,
                        golden_rows=rows_for()).verdict(),
                   "tool-use", "authoring")


def test_a_turn_after_the_registered_prompt_is_the_authors_side(tmp_path):
    """The prompt is TERMINAL. A user or developer turn after it means the run
    was not single-shot — the author's loop, not the apparatus's."""
    rows = rows_for()
    rows.append(message("user", "and now revise it"))
    rows.append(message("assistant", "revised"))
    assert_refused(Slot(tmp_path / "extra-turn", rows=rows,
                        golden_rows=rows_for(),
                        completion="revised").verdict(),
                   "extra-turn", "authoring")


def test_the_author_side_verdict_is_counted_and_not_excluded():
    """The consequence, asserted where it is decided rather than in prose: the
    code the author-side verdict carries is on §1a's AUTHORING side, which is
    what keeps the run in the denominator scoring zero."""
    for reason in transcript_check.AUTHOR_REASONS:
        side, code = transcript_check.REASON_CAUSE[reason]
        assert side == "authoring"
        assert batch.CODE_PARTITION[code] == ("authoring",
                                              "author protocol violation")


# --------------------------------------------------------------------------
# the APPARATUS's side — pipeline-invalid, excluded
# --------------------------------------------------------------------------

def test_a_transcript_carrying_another_prompt_is_apparatus(tmp_path):
    """The gate R1-5 says was never reached for a scored slot: the transcript's
    user message must be THE ARM'S prompt bytes. A slot built from another arm's
    prompt — or from a prompt edited after the freeze — is the apparatus."""
    rows = rows_for(prompt="a different instruction entirely\n")
    assert_refused(Slot(tmp_path / "other-prompt", rows=rows).verdict(),
                   "prompt-mismatch", "apparatus")


def test_a_second_copy_of_the_prompt_is_apparatus(tmp_path):
    rows = rows_for()
    rows.insert(1, message("user", PROMPT))
    assert_refused(Slot(tmp_path / "twice", rows=rows).verdict(),
                   "prompt-mismatch", "apparatus")


def test_an_added_pre_prompt_turn_is_apparatus(tmp_path):
    """The golden allowlist's whole point: a turn added BEFORE the prompt changes
    the pre-prompt context, whatever it says. The golden here is built from the
    clean rows, so the built session no longer reproduces it."""
    rows = rows_for()
    rows.insert(2, message("developer", "Remember the earlier draft."))
    assert_refused(Slot(tmp_path / "planted", rows=rows,
                        golden_rows=rows_for()).verdict(),
                   "context-mismatch", "apparatus")


def test_an_edited_pre_prompt_turn_is_apparatus(tmp_path):
    """Same count, same roles, different bytes — the case a count check would
    pass and the digest comparison catches."""
    prior = (PRIOR[0], ("developer", PRIOR[1][1] + " Prefer terse answers."))
    rows = rows_for(prior=prior)
    assert_refused(Slot(tmp_path / "edited", rows=rows,
                        golden_rows=rows_for()).verdict(),
                   "context-mismatch", "apparatus")


def test_a_leak_token_before_the_prompt_is_apparatus(tmp_path):
    """The denylist behind the allowlist. A prior turn carrying the study's own
    vocabulary is a contaminated context, not an author who misbehaved."""
    token = sorted(transcript_check.LEAK_TOKENS)[0]
    prior = (PRIOR[0], ("developer", "Earlier we discussed %s." % token))
    rows = rows_for(prior=prior)
    assert_refused(Slot(tmp_path / "leaked", rows=rows,
                        golden_rows=rows).verdict(),
                   "leak", "apparatus")


def test_a_mangled_transcript_line_is_apparatus(tmp_path):
    slot = Slot(tmp_path / "mangled")
    with open(slot.session, "ab") as handle:
        handle.write(b"{not json\n")
    assert_refused(slot.verdict(), "log-corrupt", "apparatus")


def test_a_duplicate_key_in_a_transcript_line_is_apparatus(tmp_path):
    slot = Slot(tmp_path / "shadowed")
    with open(slot.session, "ab") as handle:
        handle.write(b'{"type": "response_item", "type": "turn_context"}\n')
    assert_refused(slot.verdict(), "log-corrupt", "apparatus")


def test_a_transcript_with_no_answer_is_apparatus(tmp_path):
    """No assistant message after the prompt. It is the apparatus side for a
    reason the wrapper makes true: the same transcript fails the wrapper's
    completion extraction, which is now status 13 — `post-call-failure`, also
    apparatus. The two readings of one transcript agree."""
    rows = [row for row in rows_for()
            if not (row.get("type") == "response_item"
                    and row["payload"].get("role") == "assistant")]
    assert_refused(Slot(tmp_path / "silent", rows=rows,
                        golden_rows=rows_for()).verdict(),
                   "no-answer", "apparatus")


def test_a_completion_that_is_not_the_last_assistant_message_is_apparatus(tmp_path):
    """The binding the scorer used to take on trust: `completion.txt` is the
    wrapper's extraction, and a file that is not the transcript's own last
    assistant message is a compiler input nobody authored."""
    assert_refused(Slot(tmp_path / "swapped",
                        completion="something else entirely").verdict(),
                   "completion-mismatch", "apparatus")


def test_an_undecodable_completion_is_apparatus(tmp_path):
    assert_refused(Slot(tmp_path / "undecodable",
                        completion_bytes=b"\xff\xfe not utf-8").verdict(),
                   "completion-undecodable", "apparatus")


def test_a_turn_context_naming_another_model_is_apparatus(tmp_path):
    rows = rows_for(model="some-other-model")
    assert_refused(Slot(tmp_path / "model", rows=rows).verdict(),
                   "turn-context-mismatch", "apparatus")


def test_a_turn_context_naming_another_workdir_is_apparatus(tmp_path):
    rows = rows_for()
    rows.append({"type": "turn_context",
                 "payload": {"model": MODEL, "cwd": "/srv/w/9999"}})
    assert_refused(Slot(tmp_path / "cwd", rows=rows,
                        golden_rows=rows_for()).verdict(),
                   "turn-context-mismatch", "apparatus")


def test_a_turn_context_naming_another_effort_is_apparatus(tmp_path):
    """Gate 5's `gate-5-extension` clause (§2.1's M-24 branch), the model
    case's mirror: the top-level `effort` spelling names a tier that is not
    the pinned one."""
    rows = rows_for()
    for row in rows:
        if row["type"] == "turn_context":
            row["payload"]["effort"] = "high"
    assert_refused(Slot(tmp_path / "effort", rows=rows).verdict(effort="low"),
                   "turn-context-mismatch", "apparatus")


def test_a_second_turn_context_naming_another_effort_is_apparatus(tmp_path):
    """The cwd clause's EVERY-member rule, mirrored for the effort's nested
    spelling: a second turn_context carrying a foreign tier refuses even
    though the first names the pinned one."""
    rows = rows_for()
    for row in rows:
        if row["type"] == "turn_context":
            row["payload"]["effort"] = "low"
    rows.append({"type": "turn_context",
                 "payload": {"model": MODEL, "cwd": CWD,
                             "collaboration_mode": {
                                 "settings": {"reasoning_effort": "xhigh"}}}})
    assert_refused(Slot(tmp_path / "effort2", rows=rows,
                        golden_rows=rows_for()).verdict(effort="low"),
                   "turn-context-mismatch", "apparatus")


def test_a_null_effort_member_is_not_a_witness_and_admits(tmp_path):
    """019's ACTUAL transcript shape under a FILLED pin: the nested member is
    present and holds null, the top-level spelling is absent. Both are
    non-witnesses, not mismatches — a membership idiom here would build
    `{None}` and refuse every 019-shaped transcript, the failure M-24
    predicted. The sweep's witness step rules the same fact the same way
    (`test_sweep.py`'s null-member case), and two readings of one fact is the
    defect this program keeps finding."""
    rows = rows_for()
    for row in rows:
        if row["type"] == "turn_context":
            row["payload"]["collaboration_mode"] = {
                "settings": {"reasoning_effort": None}}
    verdict = Slot(tmp_path / "effortnull", rows=rows).verdict(effort="low")
    assert verdict["admissible"] is True, verdict


def test_a_matching_effort_witness_admits(tmp_path):
    """The positive fixture of the witnessed shape (none existed anywhere in
    the suite before the extension): both spellings present, both naming the
    pinned tier — the sweep's own transcripts' shape, verified over all 27."""
    rows = rows_for()
    for row in rows:
        if row["type"] == "turn_context":
            row["payload"]["effort"] = "low"
            row["payload"]["collaboration_mode"] = {
                "settings": {"reasoning_effort": "low"}}
    verdict = Slot(tmp_path / "effortok", rows=rows).verdict(effort="low")
    assert verdict["admissible"] is True, verdict


def test_a_malformed_collaboration_mode_is_an_absent_path_not_a_crash(
        tmp_path):
    """A nested level that is not an object is an ABSENT PATH: every refusal in
    this module leaves through `TranscriptError` with a reason and a side, and
    a malformed `collaboration_mode` (a string, a list, a number) must not hand
    `classify()` an AttributeError it has no classification for. Found by the
    fill's adversarial verification pass, which crashed the first
    implementation with `collaboration_mode: "off"`."""
    for label, malformed in (("string", "off"), ("list", ["x"]),
                             ("settings-string", {"settings": "none"})):
        rows = rows_for()
        for row in rows:
            if row["type"] == "turn_context":
                row["payload"]["effort"] = "low"
                row["payload"]["collaboration_mode"] = malformed
        verdict = Slot(tmp_path / ("malformed-" + label),
                       rows=rows).verdict(effort="low")
        assert verdict["admissible"] is True, (label, verdict)


def test_the_effort_is_read_by_path_and_never_by_name_scan(tmp_path):
    """The registered by-path property, made to discriminate: look-alike
    members OUTSIDE the two registered paths — a same-named key inside another
    structure, and the nested spelling at the wrong level — must not reach the
    gate. A recursive name-scan implementation refuses this transcript and
    fails here."""
    rows = rows_for()
    for row in rows:
        if row["type"] == "turn_context":
            row["payload"]["effort"] = "low"
            row["payload"]["last_token_usage"] = {"effort": "xhigh"}
            row["payload"]["settings"] = {"reasoning_effort": "xhigh"}
    verdict = Slot(tmp_path / "lookalike", rows=rows).verdict(effort="low")
    assert verdict["admissible"] is True, verdict


def test_the_driver_seat_threads_the_pin_into_the_gate(tmp_path, monkeypatch):
    """The production seat, made mutation-visible: `batch.transcript_verdict()`
    must hand the REGISTRY's `codex.reasoningEffort` to `classify()`. Found by
    the fill's verification pass: with every existing case, deleting the
    `effort=` threading left the suite green, so nothing bound the driver to
    the gate it claims to run. Here a transcript naming a foreign tier under a
    filled pin must refuse THROUGH THE DRIVER's own call — an implementation
    that drops the threading admits it and fails the first assertion — and the
    same slot under a matching pin must admit, so the case cannot pass by
    refusing everything."""
    rows = rows_for()
    for row in rows:
        if row["type"] == "turn_context":
            row["payload"]["effort"] = "xhigh"
    slot = Slot(tmp_path / "seat", rows=rows)
    monkeypatch.setattr(batch, "arm_prompt",
                        lambda pins, arm: (slot.prompt, "sha256:stand-in"))
    pins = {"codex": {"model": MODEL, "reasoningEffort": "low"}}
    verdict = batch.transcript_verdict(slot.root, "A", pins, slot.golden)
    assert verdict["admissible"] is False, verdict
    assert verdict["reason"] == "turn-context-mismatch", verdict
    assert verdict["side"] == "apparatus", verdict
    matching = {"codex": {"model": MODEL, "reasoningEffort": "xhigh"}}
    verdict = batch.transcript_verdict(slot.root, "A", matching, slot.golden)
    assert verdict["admissible"] is True, verdict


def test_a_recorded_nonzero_exit_is_apparatus(tmp_path):
    assert_refused(Slot(tmp_path / "exit", exit_status=3).verdict(),
                   "exit-status", "apparatus")


def test_a_missing_transcript_is_apparatus_and_not_an_absence(tmp_path):
    slot = Slot(tmp_path / "missing")
    os.unlink(slot.session)
    assert_refused(slot.verdict(), "unreadable", "apparatus")


def test_an_unreadable_golden_capture_is_apparatus(tmp_path):
    slot = Slot(tmp_path / "bad-golden")
    with open(slot.golden, "w") as handle:
        handle.write("{not json")
    assert_refused(slot.verdict(), "log-corrupt", "apparatus")


# --------------------------------------------------------------------------
# closure and fail-closed
# --------------------------------------------------------------------------

def test_every_registered_reason_is_reached_by_a_case_above():
    """The map is not allowed to grow a reason no case exercises: an unexercised
    reason is a side nobody checked, and the side is the denominator.

    The exercised set is READ OUT OF THIS FILE — every `assert_refused(...)`
    call's reason argument — rather than written out a second time beside the
    cases, so a case deleted or a reason added moves this assertion rather than
    leaving a hand-kept list agreeing with itself (Study 012's round-12 lesson: a
    test module that was a copy checking a copy)."""
    with open(os.path.abspath(__file__), "rb") as handle:
        tree = ast.parse(handle.read().decode("utf-8"))
    reached = {node.args[1].value for node in ast.walk(tree)
               if isinstance(node, ast.Call)
               and getattr(node.func, "id", None) == "assert_refused"
               and len(node.args) >= 2
               and isinstance(node.args[1], ast.Constant)}
    assert reached == set(transcript_check.REASON_CAUSE)


def test_every_raise_site_in_the_module_names_a_reason():
    """The rule, enforced over the SOURCE rather than remembered: a raise site
    added later without a reason would reach `classify()` unclassified. It would
    fail closed there — but it would fail closed at the primary attempt, and this
    fails at the commit."""
    with open(os.path.join(HARNESS, "transcript_check.py"), "rb") as handle:
        tree = ast.parse(handle.read().decode("utf-8"))
    untagged = [node.lineno for node in ast.walk(tree)
                if isinstance(node, ast.Raise)
                and isinstance(node.exc, ast.Call)
                and getattr(node.exc.func, "id", None) == "TranscriptError"
                and not any(keyword.arg == "reason"
                            for keyword in node.exc.keywords)]
    assert untagged == []


def test_a_refusal_with_no_reason_fails_closed(tmp_path, monkeypatch):
    """The hole this closes is the one R1-5 names in the other direction: a
    refusal nobody attributed must not become 'admissible', and must not become
    an authoring outcome either. It invalidates."""
    def raise_untagged(*_args, **_kwargs):
        raise transcript_check.TranscriptError("something refused")
    monkeypatch.setattr(transcript_check, "check", raise_untagged)
    with pytest.raises(transcript_check.UnclassifiedRefusal) as caught:
        Slot(tmp_path / "untagged").verdict()
    assert "before any run moves between denominators" in str(caught.value)


def test_a_refusal_with_an_unregistered_reason_fails_closed(tmp_path, monkeypatch):
    def raise_unknown(*_args, **_kwargs):
        raise transcript_check.TranscriptError("refused", reason="something-new")
    monkeypatch.setattr(transcript_check, "check", raise_unknown)
    with pytest.raises(transcript_check.UnclassifiedRefusal):
        Slot(tmp_path / "unknown").verdict()


def test_every_code_the_gate_assigns_is_in_the_partition():
    """§1a's third diff, over the transcript gate's codes rather than over
    `admit()`'s: a code the partition does not name is a run no rule counts and
    no rule excludes."""
    for reason, (side, code) in transcript_check.REASON_CAUSE.items():
        assert code in batch.CODE_PARTITION, reason
        assert batch.CODE_PARTITION[code][0] == side, reason
    assert transcript_check.APPARATUS_TRANSCRIPT_CODE in \
        [code for code, _phrase in batch.APPARATUS_CODES]
    assert transcript_check.AUTHOR_PROTOCOL_CODE in \
        [code for code, _phrase in batch.AUTHORING_PROTOCOL_CODES]


def test_the_author_side_is_exactly_the_two_the_review_names():
    """Not a taxonomy this study is free to grow quietly: the author side is the
    two protocol violations the round-1 review identifies, and everything else is
    the apparatus. A third member here moves runs into a denominator and belongs
    in a registered amendment, not in a refactor."""
    assert transcript_check.AUTHOR_REASONS == ("extra-turn", "tool-use")


# --------------------------------------------------------------------------
# the two whole documents this gate reads — salvage audit, defect f
# --------------------------------------------------------------------------
#
# The gate refuses a duplicate key on every transcript LINE (`_load`), and
# `score.load_json()`, `batch._load_json()` and `integrity.load_json()` all
# refuse duplicates on whole documents. The two whole documents THIS gate reads
# — `CALL.json` and the golden capture — were a bare `json.load(open(path))`,
# so a shadowed member meant one thing here and another at every other reader of
# the same bytes. These cases are the difference, and each one is written so
# that the shadowed value CHANGES the gate's answer: a duplicate that could not
# change an answer would not discriminate between the fix and its absence.

def _overwrite(path, text):
    with open(path, "wb") as handle:
        handle.write(text.encode("utf-8"))


def test_a_call_record_with_a_shadowed_cwd_is_refused(tmp_path):
    """`cwd` is read twice by this gate — screened for leak tokens, and passed
    to `context_digests()` as the path to normalize out of the context. A
    `CALL.json` carrying two of them makes the gate's answer depend on which one
    the parser happened to keep, and the last-wins value here is a directory the
    golden context was not captured under."""
    slot = Slot(tmp_path / "dup-cwd")
    _overwrite(slot.call,
               '{"cwd": "%s", "home": "%s", "exitStatus": 0, '
               '"cwd": "/srv/w/9999"}' % (CWD, HOME))
    verdict = slot.verdict()
    assert_refused(verdict, "log-corrupt", "apparatus")
    assert "duplicate object keys" in verdict["message"]


def test_a_call_record_with_a_shadowed_exit_status_is_refused(tmp_path):
    """The same hole at the member that decides the exit-status gate: a record
    that says 0 and then says 1 is not a record of a successful call."""
    slot = Slot(tmp_path / "dup-exit")
    _overwrite(slot.call,
               '{"cwd": "%s", "home": "%s", "exitStatus": 0, '
               '"exitStatus": 1}' % (CWD, HOME))
    assert_refused(slot.verdict(), "log-corrupt", "apparatus")


def test_a_golden_capture_with_shadowed_entries_is_refused(tmp_path):
    """The allowlist itself. The first `entries` is the context this session
    really has; the second is empty, and an empty allowlist compares equal to a
    session with no pre-prompt context at all. Whichever the parser keeps, the
    document does not say one thing — so it is refused rather than read."""
    slot = Slot(tmp_path / "dup-entries")
    with open(slot.golden, "rb") as handle:
        golden = json.loads(handle.read().decode("utf-8"))
    _overwrite(slot.golden,
               '{"contextVersion": %s, "entries": %s, "entries": []}'
               % (json.dumps(golden["contextVersion"]),
                  json.dumps(golden["entries"])))
    verdict = slot.verdict()
    assert_refused(verdict, "log-corrupt", "apparatus")
    assert "duplicate object keys" in verdict["message"]


def test_a_golden_capture_with_a_shadowed_context_version_is_refused(tmp_path):
    slot = Slot(tmp_path / "dup-version")
    with open(slot.golden, "rb") as handle:
        golden = json.loads(handle.read().decode("utf-8"))
    _overwrite(slot.golden,
               '{"contextVersion": "99", "entries": %s, "contextVersion": %s}'
               % (json.dumps(golden["entries"]),
                  json.dumps(golden["contextVersion"])))
    assert_refused(slot.verdict(), "log-corrupt", "apparatus")


def test_a_duplicate_free_call_and_golden_still_admit(tmp_path):
    """The control the four cases above are measured against: the new rule
    refuses SHADOWED members and nothing else. Without this, all four could be
    passing because the loader broke every document it reads."""
    assert Slot(tmp_path / "clean-documents").verdict()["admissible"] is True


def test_neither_whole_document_is_read_by_a_bare_json_load():
    """Over the SOURCE, because the behavioural cases above only prove the two
    CURRENT call sites are covered. A third whole-document read added later with
    `json.load(open(...))` would reintroduce exactly this defect, and the
    duplicate-key hook is not something a reviewer can see from a diff of the
    call site alone."""
    with open(os.path.join(HARNESS, "transcript_check.py"), "rb") as handle:
        tree = ast.parse(handle.read().decode("utf-8"))
    bare = [node.lineno for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and getattr(node.func, "attr", None) in ("load", "loads")
            and getattr(getattr(node.func, "value", None), "id", None) == "json"
            and not any(keyword.arg == "object_pairs_hook"
                        for keyword in node.keywords)]
    assert bare == []


class TestPriorContextExemption(object):
    """The 2026-08-19 adjudication: word-boundary matching, and the two literal
    words of the pinned CLI's own boilerplate exempt from this screen only.

    The first golden capture enumerated every token the real boilerplate fires:
    on boundaries, exactly `rejected` and `absent`; the clause ids d1-d8 fired
    only as substrings inside hex identifiers, which the boundary rule removes
    with no exemption at all. check_golden's exact-reproduction allowlist stays
    the instrument that guards the pre-prompt context against every word,
    exempt or not."""

    def test_the_pinned_clis_own_boilerplate_passes(self):
        events = [("developer", "Do not provide sandbox_permissions; commands "
                                "will be rejected. Some tools are intentionally "
                                "absent from the functions.exec namespace."),
                  ("user", "the registered prompt")]
        transcript_check.screen_prior_context(events, 1)   # must not raise

    def test_a_bare_outcome_id_still_refuses(self):
        """`rejected` is exempt; `reject` is not, and boundary matching means
        the exemption of the inflection no longer shadows the stem."""
        events = [("user", "the pack should reject this vendor"),
                  ("user", "the registered prompt")]
        with pytest.raises(transcript_check.TranscriptError):
            transcript_check.screen_prior_context(events, 1)

    def test_a_clause_id_on_a_word_boundary_still_refuses(self):
        events = [("developer", "see clause d5 for the exception"),
                  ("user", "the registered prompt")]
        with pytest.raises(transcript_check.TranscriptError):
            transcript_check.screen_prior_context(events, 1)

    def test_a_clause_id_inside_a_hex_identifier_does_not_refuse(self):
        """The substring artifact the first capture surfaced: every d1-d8 hit
        was inside an identifier like `87d5ab`. Noise, not vocabulary."""
        events = [("developer", "session 87d5ab3fd1c2 opened; call id ebd4d600"),
                  ("user", "the registered prompt")]
        transcript_check.screen_prior_context(events, 1)   # must not raise

    def test_a_prior_turn_with_a_threshold_still_refuses(self):
        events = [("user", "remember the spend floor is 100000"),
                  ("user", "the registered prompt")]
        with pytest.raises(transcript_check.TranscriptError):
            transcript_check.screen_prior_context(events, 1)

    def test_the_exemption_is_exactly_the_two_boilerplate_words(self):
        assert transcript_check.PRIOR_CONTEXT_EXEMPT == frozenset(
            {"rejected", "absent"})

    def test_the_wrapper_path_screen_is_not_exempted(self):
        """The other seat, unchanged: the wrapper's own path screen (inside
        harness/authoring_call.sh's embedded preflight) still refuses a
        scratch path spelling an outcome id. Asserted on the wrapper's source
        because the screen runs in the child: the refusal string and the
        absence of any exemption import are what a reviewer can check."""
        source = open(os.path.join(HARNESS, "authoring_call.sh")).read()
        assert "carries leak tokens" in source
        assert "PRIOR_CONTEXT_EXEMPT" not in source
