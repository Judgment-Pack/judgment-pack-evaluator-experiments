#!/usr/bin/env python3
"""The transcript binding (PREREGISTRATION.md §4): the retained codex
session transcript is the authoring evidence, and the compiler's input must
be exactly the completion that transcript records.

The parse is a strict whitelist over `response_item` payloads, preserving
stream order:

- `message` with role `user` or `developer`: every content item must be
  `input_text`; anything else (an image, audio, an unknown item) refuses.
- `message` with role `assistant`: every content item must be
  `output_text`.
- any other `response_item` payload type — every call form, every call
  output, `tool_search_output`, a `tool` role, an unknown type — refuses.

Entries whose top-level `type` is not `response_item` (session metadata,
event mirrors, token counts) carry no conversation content and are
ignored.

Admissibility (§4): zero refused payloads; exactly one user/developer
message equals PROMPT.txt's bytes, it is the LAST user/developer message
in the stream, and at least one assistant message follows it; the
completion is the last assistant message; `completion.txt` equals its
UTF-8 bytes; `CALL.json` records integer exit status 0 (a JSON boolean is
not an integer here).
"""
from __future__ import annotations
import json


class TranscriptError(Exception):
    pass


ITEM_KIND = {"user": "input_text", "developer": "input_text", "assistant": "output_text"}


def _events(session_path: str) -> list:
    """[(role, text)] in stream order; refuses anything off-whitelist."""
    events = []
    with open(session_path, "rb") as handle:
        for line_number, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            entry = json.loads(raw.decode("utf-8"))
            if not isinstance(entry, dict) or entry.get("type") != "response_item":
                continue
            payload = entry.get("payload")
            if not isinstance(payload, dict):
                raise TranscriptError("line %d: response_item without an object payload" % line_number)
            kind = payload.get("type")
            if kind != "message":
                raise TranscriptError(
                    "line %d: off-whitelist response_item payload type %r" % (line_number, kind))
            role = payload.get("role")
            if role not in ITEM_KIND:
                raise TranscriptError("line %d: off-whitelist message role %r" % (line_number, role))
            expected_item = ITEM_KIND[role]
            content = payload.get("content")
            if not isinstance(content, list):
                raise TranscriptError("line %d: message without a content list" % line_number)
            texts = []
            for item in content:
                if not isinstance(item, dict) or item.get("type") != expected_item \
                        or not isinstance(item.get("text"), str):
                    raise TranscriptError(
                        "line %d: %s message carries a non-%s content item"
                        % (line_number, role, expected_item))
                texts.append(item["text"])
            events.append((role, "".join(texts)))
    return events


def extract_completion(session_path: str) -> str:
    """The registered completion: the last assistant message's text."""
    assistants = [text for role, text in _events(session_path) if role == "assistant"]
    if not assistants:
        raise TranscriptError("the transcript holds no assistant message")
    return assistants[-1]


def check(session_path: str, prompt_path: str, completion_path: str,
          call_path: str) -> None:
    events = _events(session_path)
    prompt = open(prompt_path, "rb").read().decode("utf-8")
    prompt_positions = [i for i, (role, text) in enumerate(events)
                        if role in ("user", "developer") and text == prompt]
    if len(prompt_positions) != 1:
        raise TranscriptError(
            "expected exactly one user message with the registered prompt bytes, found %d"
            % len(prompt_positions))
    position = prompt_positions[0]
    for i, (role, _) in enumerate(events):
        if role in ("user", "developer") and i > position:
            raise TranscriptError("a user/developer message follows the registered prompt")
    assistants_after = [text for i, (role, text) in enumerate(events)
                        if role == "assistant" and i > position]
    if not assistants_after:
        raise TranscriptError("no assistant message answers the registered prompt")
    completion = open(completion_path, "rb").read().decode("utf-8")
    if completion != assistants_after[-1]:
        raise TranscriptError("completion.txt is not the transcript's last assistant message")
    call = json.load(open(call_path))
    status = call.get("exitStatus")
    if not isinstance(status, int) or isinstance(status, bool) or status != 0:
        raise TranscriptError("the call did not exit with integer status 0: %r" % status)
