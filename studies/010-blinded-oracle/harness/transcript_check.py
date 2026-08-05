#!/usr/bin/env python3
"""The transcript binding (PREREGISTRATION.md §4): the retained codex
session transcript is the authoring evidence, and the compiler's input must
be exactly the completion that transcript records.

Admissibility, checked mechanically from session.jsonl:
  1. zero tool invocations — no response_item whose payload type is any
     call form (endswith "_call") or call output (endswith "_call_output");
  2. the last user message's text equals PROMPT.txt's bytes exactly;
  3. at least one assistant message exists, and completion.txt equals the
     last assistant message's concatenated output_text items;
  4. CALL.json records exit status 0.
"""
from __future__ import annotations
import json
import os


class TranscriptError(Exception):
    pass


def _messages(session_path: str) -> tuple[list, list, list]:
    """(user texts, assistant texts, tool payload types), in stream order."""
    users, assistants, tools = [], [], []
    with open(session_path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("type") != "response_item":
                continue
            payload = entry.get("payload") or {}
            kind = payload.get("type", "")
            if kind.endswith("_call") or kind.endswith("_call_output"):
                tools.append(kind)
            elif kind == "message":
                role = payload.get("role")
                text = "".join(
                    item.get("text", "") for item in payload.get("content", [])
                    if isinstance(item, dict) and item.get("type") in ("input_text", "output_text"))
                if role == "user":
                    users.append(text)
                elif role == "assistant":
                    assistants.append(text)
    return users, assistants, tools


def extract_completion(session_path: str) -> str:
    """The registered completion: the last assistant message's text."""
    _, assistants, _ = _messages(session_path)
    if not assistants:
        raise TranscriptError("the transcript holds no assistant message")
    return assistants[-1]


def check(session_path: str, prompt_path: str, completion_path: str,
          call_path: str) -> None:
    users, assistants, tools = _messages(session_path)
    if tools:
        raise TranscriptError("the transcript shows tool use: %s" % sorted(set(tools)))
    prompt = open(prompt_path, "rb").read().decode("utf-8")
    if not users:
        raise TranscriptError("the transcript holds no user message")
    if users[-1] != prompt:
        raise TranscriptError("the last user message is not the registered prompt bytes")
    if not assistants:
        raise TranscriptError("the transcript holds no assistant message")
    completion = open(completion_path, "rb").read().decode("utf-8")
    if completion != assistants[-1]:
        raise TranscriptError("completion.txt is not the transcript's last assistant message")
    call = json.load(open(call_path))
    if call.get("exitStatus") != 0:
        raise TranscriptError("the call did not exit 0: %r" % call.get("exitStatus"))
