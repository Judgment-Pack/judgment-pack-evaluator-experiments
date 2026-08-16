#!/usr/bin/env python3
"""The transcript binding, PORTED from Study 012's own adapted bytes
(sha256 64542bc5d6d8f6682a29dee870aa07feb5757db3941c48af581a974c2423a5b2 — the
destination digest Study 012's own harness/PORTS.md records for it; this study's
harness/PORTS.md records the source digest and every change, and
harness/integrity.py binds this file to it): the retained codex session
transcript is the authoring evidence, and the compiler's input must be exactly
the completion that transcript records.

**The check logic is not touched.** The `response_item` whitelist, the
terminal-prompt rule, the leak denylist, the golden allowlist comparison, the
completion byte binding, the `turn_context` model/cwd binding, the
integer-exit-0 rule and duplicate-key rejection on every transcript line are
Study 010's, through 011 and 012, unchanged. Two things change, and they are
both SUBJECTS rather than rules:

1. **`LEAK_TOKENS` is this study's vocabulary, not Study 012's, and it is
   DERIVED.** Study 012's policy-family vocabulary (`family.json`,
   `sanctionsHit`, the mirror's threshold names) is gone because it names
   nothing here. What replaces it is not a second curated tuple: this module
   READS `harness/leak_tokens.py`'s composed screen, whose policy half is
   derived from the stimulus prose by three registered rules and whose
   instrument half is named and separately power-checked (SCAFFOLD item G3,
   closed — the residual was that this file still carried its own copy). The
   wrapper's scratch-path screen reads the same constant, so the study has one
   list and the freeze's re-derivation moves both screens together.
2. **Three arms.** `check()`'s `arm` label is one of A, B, C; gate 2 is checked
   against THAT arm's assembled prompt bytes. A slot whose transcript carries
   another arm's prompt is refused here and scored `arm-mismatch` by the scorer,
   not by this module.

Study 011's port change is retained and still in force: the golden context's
SOURCE is an argument, and `golden_path` is REQUIRED — no caller can omit the
allowlist by leaving a default in place. One recapture serves all three arms:
the pre-prompt context precedes the prompt and does not depend on it, and that
does not become three properties because there are three prompts.

What this file deliberately does NOT do: judge a record, count a class, extract
the registered marker block, or decide whether a run enters a rate denominator;
it says admissible or raises, and the scorer owns the population.

Built against a captured no-tool session from the pinned CLI, not against
an assumed schema. Real sessions carry, besides conversation messages:
`reasoning` items (admitted only in an inert shape — no tool semantics),
and codex's own fixed context (permissions instructions, agent identity,
multi-agent note, recommended plugins). The operator-controllable context
— user config, AGENTS.md, rules — is excluded by the wrapper's
`--ignore-user-config` and isolated `CODEX_HOME`; what remains is codex's
own boilerplate, retained in full and screened below.

Admissibility:

1. Every `response_item` payload is either a `message` with role user,
   developer, or assistant (role-appropriate content items only), or an
   inert `reasoning` item. ANY call form, call output, tool role,
   attachment, or unknown payload type refuses.
2. Exactly one user message equals THE ARM'S assembled prompt bytes, and no
   user/developer message follows it — the arm's prompt is terminal.
3. No message BEFORE the prompt contains any locked leak token: the
   study's representation, scored-surface, mutant and policy-domain
   vocabulary. This is what makes "the completion answers the prompt alone"
   mechanical rather than asserted — a defect-informed prior turn refuses.
4. At least one assistant message follows the prompt; the completion is
   the last of them, and completion.txt equals its UTF-8 bytes.
5. `turn_context` (when the transcript carries it) names the locked model
   and the call's own working directory.
6. `CALL.json` records integer exit status 0 (a JSON boolean is not an
   integer here).

Every check is byte-level: transcript lines are parsed with duplicate-key
rejection, so a shadowed member cannot mean one thing to this checker and
another to a reader.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import sys

# Imported the way the ceremony runs it: the harness modules are invoked by
# path, so this file's own directory is what makes `leak_tokens` importable when
# the wrapper reaches it through a symlinked `harness/`.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import leak_tokens  # noqa: E402

# Vocabulary that cannot appear before the registered prompt. Lowercase;
# matching is case-insensitive substring. These are the study's own terms:
# an authoring turn that saw any of them was not answering the policy
# alone. The prompt itself (and the policy it inlines) is exempt — it IS
# the registered instruction, and it is the last user message.
#
# ONE SOURCE OF TRUTH (SCAFFOLD item G3's residual, closed). This was a
# design-time tuple written out here; it is `harness/leak_tokens.py`'s composed
# screen now — the policy vocabulary DERIVED from the stimulus prose by three
# registered rules, unioned with that module's named instrument vocabulary. The
# wrapper's scratch-path screen reads the same constant under its other name
# (`leak_tokens.SCRATCH_TOKENS`), so the study has exactly one leak list, and
# re-deriving it at the freeze — when `policy/POLICY.md` supersedes the frozen
# candidate — moves both screens at once rather than leaving one behind.
#
# The power the list is required to have is demonstrated, not asserted:
# `leak_tokens.check_power()` requires the derived half to catch every witness
# sentence the SOURCE'S OWN MARKUP identifies while a scrambled list of the same
# size catches strictly fewer, and `leak_tokens.check_instrument_power()`
# requires the instrument half alone to catch strictly fewer than the derived
# half and the union to lose none. `harness/tests/test_leak_tokens.py` runs both
# against this constant.
LEAK_TOKENS = leak_tokens.SCREEN_TOKENS

ITEM_KIND = {"user": "input_text", "developer": "input_text", "assistant": "output_text"}
MESSAGE_ROLES = tuple(ITEM_KIND)


class TranscriptError(Exception):
    pass


class CompletionUndecodable(ValueError):
    """`completion.txt` is not decodable UTF-8 — a fact about the FILE, not a
    refusal by this gate (round 5, finding 7).

    §3.3 registers `completion-unreadable` as a reachable outcome and the scorer
    reaches it from `records_compile.read_completion()`. That read happens after
    this module's, so every undecodable completion was refused here first: the
    decode raised a bare `UnicodeDecodeError`, which is a `ValueError`, which
    `admit()` catches alongside `TranscriptError` and scores
    `transcript-refused`. The registered code named no run.

    Deliberately NOT a `TranscriptError`: this gate refuses a transcript, and a
    completion that will not decode is not a transcript refusal. Deliberately
    still a `ValueError`: every existing caller that catches one — including
    `score_rates._transcript_is_another_arm()`, which re-runs this gate against
    four other arms' prompts — keeps the behaviour it was ported with, and only
    the caller that asks for the distinction (`admit()`, which catches this
    class first) sees it.
    """


def _refuse_duplicate_keys(pairs):
    keys = [key for key, _ in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate object keys")
    return dict(pairs)


def _load(line: bytes, number: int) -> dict:
    try:
        return json.loads(line.decode("utf-8"), object_pairs_hook=_refuse_duplicate_keys)
    except ValueError as error:
        raise TranscriptError("line %d is not duplicate-free JSON: %s" % (number, error))


def _reasoning_is_inert(payload: dict, number: int) -> None:
    """A reasoning item may carry an id, an encrypted blob, a summary, and
    passthrough metadata — never content items, tool names, arguments, or
    outputs. Anything resembling a call refuses."""
    forbidden = {"name", "arguments", "input", "output", "call_id", "content",
                 "tool", "tool_name", "result"}
    present = forbidden & set(payload)
    if present:
        raise TranscriptError(
            "line %d: reasoning item carries call-like members %s" % (number, sorted(present)))
    summary = payload.get("summary", [])
    if not isinstance(summary, list):
        raise TranscriptError("line %d: reasoning summary is not a list" % number)


NORMALIZERS = (
    # Dynamic values codex quotes that carry no policy information. The
    # golden capture (transcription/GOLDEN-CONTEXT.json) pins what remains,
    # so anything NOT normalized here must match the golden bytes exactly.
    (re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?"), "<TIMESTAMP>"),
    (re.compile(r"\d{4}-\d{2}-\d{2}"), "<DATE>"),
    (re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"), "<UUID>"),
)


def normalize(text: str, paths: list) -> str:
    """One text, with environment paths and dynamic stamps replaced. Also
    NFKC-normalized and stripped of zero-width characters, so a homoglyph
    or zero-width-joined variant cannot differ from the golden bytes while
    reading identically to the model."""
    import unicodedata
    normalized = unicodedata.normalize("NFKC", text)
    normalized = "".join(ch for ch in normalized
                         if ch not in "\u200b\u200c\u200d\ufeff\u2060")
    for path in paths:
        if path and len(path) > 3:
            normalized = normalized.replace(path, "<PATH>")
    for pattern, replacement in NORMALIZERS:
        normalized = pattern.sub(replacement, normalized)
    return normalized


def context_digests(session_path: str, call: dict) -> dict:
    """The normalized pre-prompt context, as ordered (role, digest, length)
    triples — what the golden capture pins and every run must reproduce."""
    events, contexts = _events(session_path)
    prompt_positions = [i for i, (role, _) in enumerate(events) if role == "user"]
    position = prompt_positions[-1] if prompt_positions else len(events)
    paths = environment_paths(contexts, call)
    entries = []
    for role, text in events[:position]:
        canonical = normalize(text, paths)
        entries.append({"role": role,
                        "sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
                        "length": len(canonical)})
    return {"contextVersion": "1", "entries": entries}


def environment_paths(contexts: list, call: dict) -> list:
    """Paths the environment legitimately quotes: the call's working
    directory, the sandbox workspace roots, and the home directory."""
    paths = {call.get("cwd", ""), call.get("home", "")}
    for context in contexts:
        if isinstance(context.get("cwd"), str):
            paths.add(context["cwd"])
        roots = context.get("workspace_roots")
        if isinstance(roots, list):
            for root in roots:
                if isinstance(root, str):
                    paths.add(root)
                elif isinstance(root, dict) and isinstance(root.get("path"), str):
                    paths.add(root["path"])
    return sorted((path for path in paths if path and len(path) > 3), key=len, reverse=True)


def _events(session_path: str) -> tuple[list, list]:
    """([(role, text)] in stream order, [turn_context payloads])."""
    events, contexts = [], []
    with open(session_path, "rb") as handle:
        for number, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            entry = _load(raw, number)
            if not isinstance(entry, dict):
                raise TranscriptError("line %d is not a JSON object" % number)
            kind = entry.get("type")
            if kind == "turn_context":
                context = entry.get("payload")
                if isinstance(context, dict):
                    contexts.append(context)
                continue
            if kind != "response_item":
                # session_meta, event_msg mirrors, world_state: no
                # conversation content reaches the model through them.
                continue
            payload = entry.get("payload")
            if not isinstance(payload, dict):
                raise TranscriptError("line %d: response_item without an object payload" % number)
            item = payload.get("type")
            if item == "reasoning":
                _reasoning_is_inert(payload, number)
                continue
            if item != "message":
                raise TranscriptError(
                    "line %d: off-whitelist response_item payload type %r" % (number, item))
            role = payload.get("role")
            if role not in MESSAGE_ROLES:
                raise TranscriptError("line %d: off-whitelist message role %r" % (number, role))
            expected_item = ITEM_KIND[role]
            content = payload.get("content")
            if not isinstance(content, list) or not content:
                raise TranscriptError("line %d: message without a content list" % number)
            texts = []
            for entry_item in content:
                if not isinstance(entry_item, dict) or entry_item.get("type") != expected_item \
                        or not isinstance(entry_item.get("text"), str):
                    raise TranscriptError(
                        "line %d: %s message carries a non-%s content item"
                        % (number, role, expected_item))
                texts.append(entry_item["text"])
            events.append((role, "".join(texts)))
    return events, contexts


def extract_completion(session_path: str) -> str:
    """The registered completion: the last assistant message's text."""
    events, _ = _events(session_path)
    assistants = [text for role, text in events if role == "assistant"]
    if not assistants:
        raise TranscriptError("the transcript holds no assistant message")
    return assistants[-1]


def screen_prior_context(events: list, position: int, paths: list = ()) -> None:
    """No message before the registered prompt may carry study vocabulary.

    Environment paths are excised before matching: codex's own boilerplate
    quotes the sandbox workspace root and home directory, and a machine
    whose directories happen to spell a study term leaks nothing by it.
    The wrapper independently refuses a scratch path containing a leak
    token, so the excision cannot hide a planted one."""
    for index, (role, text) in enumerate(events):
        if index >= position:
            continue
        lowered = text.lower()
        for path in paths:
            if path:
                lowered = lowered.replace(path.lower(), "<path>")
        for token in LEAK_TOKENS:
            if token in lowered:
                raise TranscriptError(
                    "prior %s message (item %d) contains the leak token %r"
                    % (role, index, token))


def check_golden(session_path: str, call: dict, golden_path: str) -> None:
    """The pre-prompt context must reproduce the registered golden capture
    exactly: same count, same roles, same order, same normalized digests.

    This is an allowlist, and it is what a denylist could never be. A
    paraphrase ("the third clause should say > instead of >= at 70"), a
    zero-width-joined spelling, a base64 blob — none of them need to
    contain a banned token to leak, but all of them change the context,
    and any change refuses. The golden capture was taken from real runs of
    the registered invocation, which reproduce byte-identically after
    normalization."""
    golden = json.load(open(golden_path))
    actual = context_digests(session_path, call)
    if golden.get("contextVersion") != actual["contextVersion"]:
        raise TranscriptError("the golden capture is a different context version")
    expected, seen = golden.get("entries", []), actual["entries"]
    if len(expected) != len(seen):
        raise TranscriptError(
            "the session carries %d pre-prompt context items, the golden capture %d"
            % (len(seen), len(expected)))
    for index, (want, got) in enumerate(zip(expected, seen)):
        if want.get("role") != got["role"] or want.get("sha256") != got["sha256"] \
                or want.get("length") != got["length"]:
            raise TranscriptError(
                "pre-prompt context item %d (%s) is not the locked golden context"
                % (index, got["role"]))


def check(session_path: str, prompt_path: str, completion_path: str,
          call_path: str, golden_path: str, model: str | None = None,
          arm: str | None = None) -> None:
    """Admissible, or TranscriptError. `golden_path` is required (Study 010's
    optional default is gone): this study recaptures its own golden context,
    and an omitted allowlist would silently weaken every run's admission.

    `prompt_path` is THE ARM'S prompt (§3.1 gate 2), and `arm` is the label a
    refusal names. The label decorates messages and decides nothing: the gate
    is the bytes at `prompt_path`, and the scorer — not this module — is what
    turns "the transcript carries some other arm's prompt" into
    `arm-mismatch`."""
    events, contexts = _events(session_path)
    prompt = open(prompt_path, "rb").read().decode("utf-8")
    named = "arm %s's registered prompt" % arm if arm else "the registered prompt"
    positions = [i for i, (role, text) in enumerate(events)
                 if role == "user" and text == prompt]
    if len(positions) != 1:
        raise TranscriptError(
            "expected exactly one user message with the bytes of %s, found %d"
            % (named, len(positions)))
    position = positions[0]
    for index, (role, _) in enumerate(events):
        if role in ("user", "developer") and index > position:
            raise TranscriptError("a user/developer message follows %s" % named)
    call = json.load(open(call_path))
    scratch = call.get("cwd", "")
    for token in LEAK_TOKENS:
        if token in scratch.lower():
            raise TranscriptError("the call's working directory contains the leak token %r" % token)
    # Defence in depth: the golden allowlist is the real gate, the
    # denylist catches an obviously planted turn with a clearer message.
    screen_prior_context(events, position, environment_paths(contexts, call))
    # Unconditional: Study 010 guarded this on `golden_path is not None`
    # because the argument was optional. Here it is required, and a None
    # would be a caller bug, not a licence to skip the allowlist.
    check_golden(session_path, call, golden_path)
    assistants_after = [text for index, (role, text) in enumerate(events)
                        if role == "assistant" and index > position]
    if not assistants_after:
        raise TranscriptError("no assistant message answers the registered prompt")
    # The read and the decode are two steps, and the binding is a third (round
    # 5, finding 7): whether the file decodes is a question about the file, and
    # only a file that decoded can be compared to the transcript's own text.
    raw_completion = open(completion_path, "rb").read()
    try:
        completion = raw_completion.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CompletionUndecodable(
            "completion.txt is not decodable UTF-8: %s" % error)
    if completion != assistants_after[-1]:
        raise TranscriptError("completion.txt is not the transcript's last assistant message")
    status = call.get("exitStatus")
    if not isinstance(status, int) or isinstance(status, bool) or status != 0:
        raise TranscriptError("the call did not exit with integer status 0: %r" % status)
    if model is not None:
        named = {context.get("model") for context in contexts if "model" in context}
        if named and named != {model}:
            raise TranscriptError("the transcript's turn context names %r, not the locked model %r"
                                  % (sorted(named), model))
        # EVERY named cwd, not merely one of them — symmetrical with the model
        # clause above, and what §3.1 gate 5 registers: `turn_context`, where
        # present, names the call's own working directory. Membership admitted a
        # second turn_context naming a foreign workspace as long as one context
        # named the right one, so "where present" was true of the set and not of
        # its members.
        cwds = {context.get("cwd") for context in contexts if "cwd" in context}
        if cwds and cwds != {call.get("cwd")}:
            raise TranscriptError(
                "the transcript's turn context names the working directories %r, not "
                "the call's own %r alone"
                % (sorted(value for value in cwds if isinstance(value, str)),
                   call.get("cwd")))
