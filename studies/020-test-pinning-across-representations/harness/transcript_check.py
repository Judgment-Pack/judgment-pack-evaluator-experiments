#!/usr/bin/env python3
"""The transcript binding.

**STUDY 020 PORT NOTE.** These are Study 019's bytes, taken by digest under
`harness/PORTS.md`'s two-sided table. The lineage sentence below is 019's own and is
kept as history; the binding that RUNS is 020's — `harness/integrity.py` verifies
Study 019's lock first (`harness/STUDY-MANIFEST.sha256`, at the digest 019's own
registry pins for it) and binds this file's source cell to 019's line for it.
This file carries ONE registered design change over 019's bytes — §2.1's
`gate-5-extension` branch, taken 2026-08-24 by the sweep's witness-resolution
step: gate 5 binds the pinned REASONING EFFORT beside the model and the cwd,
by path, over both witnessed spellings; null-and-absent are non-witnesses, and
under a FILLED pin at least one non-null witness is REQUIRED (R1-12).
`harness/PORTS.md`'s row for this file records the change, and §7's
ported-unchanged sentence had already carved the seat out by name — "the
transcript binding and its gates other than gate 5".

PORTED from Study 012's own adapted bytes
(sha256 64542bc5d6d8f6682a29dee870aa07feb5757db3941c48af581a974c2423a5b2 — the
destination digest Study 012's own harness/PORTS.md records for it; this study's
harness/PORTS.md records the source digest and every change, and
harness/integrity.py binds this file to it): the retained codex session
transcript is the authoring evidence, and the compiler's input must be exactly
the completion that transcript records.

**The check logic carries one registered extension and is otherwise not
touched.** The `response_item` whitelist, the terminal-prompt rule, the leak
denylist, the golden allowlist comparison, the completion byte binding, the
`turn_context` model/cwd binding, the integer-exit-0 rule and duplicate-key
rejection on every transcript line are Study 010's, through 011 and 012,
unchanged; the `turn_context` binding additionally names the pinned reasoning
effort (the `gate-5-extension` above). Two further things change, and they are
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

Round-1 finding R1-5 adds a third change, and it is a rule rather than a
subject: **every refusal names its CAUSE.** `check()` still says admissible or
raises, and its checks are untouched; what is new is that each raise site carries
a reason tag, `REASON_CAUSE` maps every tag to one side of §1a's partition, and
`classify()` turns the exception into a structured verdict every scored slot goes
through. The distinction is the one the review names: a transcript carrying a
tool call or a turn after the registered prompt is the AUTHOR breaking §3's
single-shot, no-tools instruction — an authoring outcome, retained in the
denominator and scoring zero — while a mismatched prompt, a drifted golden
context, a mangled log or a completion the wrapper mis-extracted is the
APPARATUS, which §1a excludes. Wiring the gate in without that map would have
filed every tool call as pipeline-invalid and quietly deleted the runs the
no-tools instruction exists to catch.

What this file deliberately does NOT do: judge a record, count a class, extract
the registered marker block, or decide whether a run enters a rate denominator;
it says admissible, or names a side and a code and lets the scorer place the run.

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
5. `turn_context` (when the transcript carries it) names the locked model,
   the call's own working directory, and — when the effort pin is filled —
   the pinned reasoning effort, in either of its two witnessed spellings
   (`effort`, `collaboration_mode.settings.reasoning_effort`). A member
   holding null is not a witness; under a FILLED pin at least one non-null
   matching witness must exist (R1-12 — the gate-5-extension branch means
   the transcript witnesses the effort, so an unwitnessed call refuses),
   and a non-string witness value refuses as malformed.
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
    """A refusal by this gate, carrying the REASON TAG that attributes it.

    Round-1 finding R1-5: wiring `check()` into per-slot scoring wholesale would
    have made one attribution error out of two different facts. This gate refuses
    a transcript that carries a tool call and a transcript whose pre-prompt
    context was corrupted with the same exception, and those are not the same
    event: the model using a tool is the AUTHOR violating §3's single-shot,
    no-tools instruction — an authoring outcome, retained in the denominator and
    scoring zero — while a mismatched prompt, a drifted golden context or a
    mangled log is the APPARATUS failing, which §1a excludes.

    So every raise site names its reason, `REASON_CAUSE` maps the reason to a
    side and a §1a code, and `classify()` refuses outright on a reason the map
    does not name. There is no default: a refusal nobody classified is
    pipeline-invalid, never a silently counted run."""

    def __init__(self, message, reason=None):
        super().__init__(message)
        self.reason = reason


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

    reason = "completion-undecodable"


# --------------------------------------------------------------------------
# the cause map (R1-5)
# --------------------------------------------------------------------------
#
# Left: the reason tag a raise site names. Right: the SIDE of §1a's partition
# the refusal belongs to, and the code the scorer files it under. The two
# authoring reasons are the two the round-1 review names — the author using a
# tool, and the author taking a turn after the registered prompt — and both are
# facts about what the MODEL emitted into a transcript the wrapper retained
# whole. Everything else is a fact about the apparatus: the bytes the prompt was
# assembled from, the pre-prompt context the golden capture pins, the log the CLI
# wrote, the exit status the wrapper recorded, or the completion file the wrapper
# extracted. Nothing in this map is a judgement about the artifact; that is
# `admit()`'s, on the other side of the population rule.
AUTHOR_PROTOCOL_CODE = "author-protocol-violation"
APPARATUS_TRANSCRIPT_CODE = "transcript-refused"

REASON_CAUSE = {
    # the author's own protocol violations — retained, counted, scoring zero
    "tool-use": ("authoring", AUTHOR_PROTOCOL_CODE),
    "extra-turn": ("authoring", AUTHOR_PROTOCOL_CODE),
    # apparatus integrity — pipeline-invalid, excluded from every denominator
    "log-corrupt": ("apparatus", APPARATUS_TRANSCRIPT_CODE),
    "unreadable": ("apparatus", APPARATUS_TRANSCRIPT_CODE),
    "prompt-mismatch": ("apparatus", APPARATUS_TRANSCRIPT_CODE),
    "context-mismatch": ("apparatus", APPARATUS_TRANSCRIPT_CODE),
    "leak": ("apparatus", APPARATUS_TRANSCRIPT_CODE),
    "no-answer": ("apparatus", APPARATUS_TRANSCRIPT_CODE),
    "completion-mismatch": ("apparatus", APPARATUS_TRANSCRIPT_CODE),
    "completion-undecodable": ("apparatus", APPARATUS_TRANSCRIPT_CODE),
    "turn-context-mismatch": ("apparatus", APPARATUS_TRANSCRIPT_CODE),
    "exit-status": ("apparatus", APPARATUS_TRANSCRIPT_CODE),
}

AUTHOR_REASONS = tuple(sorted(reason for reason, (side, _code)
                              in REASON_CAUSE.items() if side == "authoring"))
APPARATUS_REASONS = tuple(sorted(reason for reason, (side, _code)
                                 in REASON_CAUSE.items() if side == "apparatus"))


class UnclassifiedRefusal(Exception):
    """A refusal reached `classify()` carrying a reason `REASON_CAUSE` does not
    name. It is deliberately NOT a `TranscriptError`: a transcript that this
    module refused for a cause nobody registered is a defect in this module, and
    the fail-closed answer is to invalidate the attempt rather than to guess a
    side and move a run between denominators. Callers let it propagate."""


def classify(session_path: str, prompt_path: str, completion_path: str,
             call_path: str, golden_path: str, model: str = None,
             arm: str = None, effort: str = None) -> dict:
    """The full binding of `check()`, as a STRUCTURED verdict rather than as an
    exception — the entry point every scored slot goes through (R1-5).

    Returns `{"admissible", "reason", "side", "code", "message"}`. An admissible
    transcript answers `{"admissible": True, "reason": None, "side": None,
    "code": None}`; a refused one carries the reason tag, the §1a side that
    reason is attributed to, and the code the scorer files the run under.

    Fail-closed in three places, each of them a way this could have leaked:
    a `TranscriptError` with no reason, a reason the map does not name, and a
    read error on any of the five paths all raise instead of answering. The
    caller may not treat "I could not tell" as "admissible", and may not treat it
    as an authoring outcome either."""
    try:
        check(session_path, prompt_path, completion_path, call_path,
              golden_path, model=model, arm=arm, effort=effort)
    except (TranscriptError, CompletionUndecodable) as error:
        reason = getattr(error, "reason", None)
        if reason not in REASON_CAUSE:
            raise UnclassifiedRefusal(
                "the transcript gate refused with the unregistered reason %r "
                "(%s): every refusal is attributed to the author or to the "
                "apparatus before any run moves between denominators"
                % (reason, error))
        side, code = REASON_CAUSE[reason]
        return {"admissible": False, "reason": reason, "side": side,
                "code": code, "message": str(error)}
    except ValueError as error:
        # A JSON document this gate reads but does not parse line by line —
        # CALL.json, the golden capture — that will not decode. The bytes are the
        # apparatus's, so the refusal is too, and it is named rather than
        # collapsed into `log-corrupt`'s message.
        side, code = REASON_CAUSE["log-corrupt"]
        return {"admissible": False, "reason": "log-corrupt", "side": side,
                "code": code,
                "message": "a document this gate reads is not readable JSON: %s"
                           % error}
    except OSError as error:
        side, code = REASON_CAUSE["unreadable"]
        return {"admissible": False, "reason": "unreadable", "side": side,
                "code": code,
                "message": "a byte this gate binds is not readable: %s" % error}
    return {"admissible": True, "reason": None, "side": None, "code": None,
            "message": "the transcript binds to the registered prompt, the "
                       "golden context and the retained completion"}


def _refuse_duplicate_keys(pairs):
    keys = [key for key, _ in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate object keys")
    return dict(pairs)


def _load(line: bytes, number: int) -> dict:
    try:
        return json.loads(line.decode("utf-8"), object_pairs_hook=_refuse_duplicate_keys)
    except ValueError as error:
        raise TranscriptError("line %d is not duplicate-free JSON: %s" % (number, error),
                              reason="log-corrupt")


def _reasoning_is_inert(payload: dict, number: int) -> None:
    """A reasoning item may carry an id, an encrypted blob, a summary, and
    passthrough metadata — never content items, tool names, arguments, or
    outputs. Anything resembling a call refuses."""
    forbidden = {"name", "arguments", "input", "output", "call_id", "content",
                 "tool", "tool_name", "result"}
    present = forbidden & set(payload)
    if present:
        raise TranscriptError(
            "line %d: reasoning item carries call-like members %s"
            % (number, sorted(present)), reason="tool-use")
    summary = payload.get("summary", [])
    if not isinstance(summary, list):
        raise TranscriptError("line %d: reasoning summary is not a list" % number,
                              reason="log-corrupt")


def _load_document(path: str) -> dict:
    """A whole JSON document this gate READS but does not parse line by line —
    `CALL.json` and the golden capture — under the same duplicate-key rule every
    transcript line already gets.

    The salvage audit's defect f. Both sites used to be a bare
    `json.load(open(path))`: no `object_pairs_hook`, and no context manager. The
    hook is the material half. A golden capture with a duplicated `"entries"`,
    or a `CALL.json` with a duplicated `"cwd"` or `"goldenSha256"`, means one
    thing to this gate and another to `score.load_json()` reading the same bytes
    — and `score.load_json()`, `batch._load_json()` and `integrity.load_json()`
    all refuse duplicates already, so the shadowed member survives exactly where
    the admission decision is made. `_refuse_duplicate_keys` raises `ValueError`,
    which is the class `classify()` already maps to `log-corrupt`/apparatus, so
    this adds a refusal without adding a reason tag.

    The context manager is the other half: an undecodable document used to leak
    the open file handle out of the raising frame."""
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"),
                          object_pairs_hook=_refuse_duplicate_keys)


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
                raise TranscriptError("line %d is not a JSON object" % number,
                                      reason="log-corrupt")
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
                raise TranscriptError(
                    "line %d: response_item without an object payload" % number,
                    reason="log-corrupt")
            item = payload.get("type")
            if item == "reasoning":
                _reasoning_is_inert(payload, number)
                continue
            if item != "message":
                raise TranscriptError(
                    "line %d: off-whitelist response_item payload type %r"
                    % (number, item), reason="tool-use")
            role = payload.get("role")
            if role not in MESSAGE_ROLES:
                raise TranscriptError(
                    "line %d: off-whitelist message role %r" % (number, role),
                    reason="tool-use")
            expected_item = ITEM_KIND[role]
            content = payload.get("content")
            if not isinstance(content, list) or not content:
                raise TranscriptError(
                    "line %d: message without a content list" % number,
                    reason="log-corrupt")
            texts = []
            for entry_item in content:
                if not isinstance(entry_item, dict) or entry_item.get("type") != expected_item \
                        or not isinstance(entry_item.get("text"), str):
                    raise TranscriptError(
                        "line %d: %s message carries a non-%s content item"
                        % (number, role, expected_item), reason="log-corrupt")
                texts.append(entry_item["text"])
            events.append((role, "".join(texts)))
    return events, contexts


def extract_completion(session_path: str) -> str:
    """The registered completion: the last assistant message's text."""
    events, _ = _events(session_path)
    assistants = [text for role, text in events if role == "assistant"]
    if not assistants:
        raise TranscriptError("the transcript holds no assistant message",
                              reason="no-answer")
    return assistants[-1]


#: The two words of the pinned CLI's own fixed boilerplate that are also derived
#: study tokens, exempted from THIS screen and from no other seat. The first
#: golden capture (2026-08-19) enumerated every token the real boilerplate fires
#: (recorded in PREREG-REVIEW.md): on word boundaries, exactly `rejected`
#: ("commands will be rejected", the sandbox notice) and `absent`
#: ("intentionally absent from the `functions.exec` namespace", the tool
#: catalogue). All other hits were substring artifacts — the clause ids d1–d8
#: matching inside hex identifiers — which the word-boundary rule below removes
#: without any exemption, keeping their full power for real mentions. What
#: guards the pre-prompt context against even these two words remains
#: `check_golden()`'s exact-reproduction allowlist, which refuses ANY change to
#: it. The exemption does not reach the wrapper's path screen or the negative
#: corpus.
PRIOR_CONTEXT_EXEMPT = frozenset({"rejected", "absent"})


def _token_pattern(token):
    """A word-boundary pattern for one token: `d5` in "clause d5" refuses, `d5`
    inside `87d5ab` does not. leak_tokens residual 2 predicted ordinary-word
    collisions with the CLI's own boilerplate; the first capture showed the
    substring rule ALSO manufactured clause-id hits inside every hex identifier,
    which is noise no reviewer asked for. Boundaries are non-alphanumeric so
    multi-word and punctuated tokens keep matching as written."""
    return re.compile(r"(?<![0-9a-z])" + re.escape(token) + r"(?![0-9a-z])")


def screen_prior_context(events: list, position: int, paths: list = ()) -> None:
    """No message before the registered prompt may carry study vocabulary.

    Environment paths are excised before matching: codex's own boilerplate
    quotes the sandbox workspace root and home directory, and a machine
    whose directories happen to spell a study term leaks nothing by it.
    The wrapper independently refuses a scratch path containing a leak
    token, so the excision cannot hide a planted one. Tokens match on word
    boundaries, and the two words of the pinned CLI's own boilerplate are
    exempt (`PRIOR_CONTEXT_EXEMPT` above) — `check_golden()`'s
    exact-reproduction allowlist is what actually guards this context."""
    for index, (role, text) in enumerate(events):
        if index >= position:
            continue
        lowered = text.lower()
        for path in paths:
            if path:
                lowered = lowered.replace(path.lower(), "<path>")
        for token in LEAK_TOKENS:
            if token in PRIOR_CONTEXT_EXEMPT:
                continue
            if _token_pattern(token).search(lowered):
                raise TranscriptError(
                    "prior %s message (item %d) contains the leak token %r"
                    % (role, index, token), reason="leak")


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
    golden = _load_document(golden_path)
    actual = context_digests(session_path, call)
    if golden.get("contextVersion") != actual["contextVersion"]:
        raise TranscriptError("the golden capture is a different context version",
                              reason="context-mismatch")
    expected, seen = golden.get("entries", []), actual["entries"]
    if len(expected) != len(seen):
        raise TranscriptError(
            "the session carries %d pre-prompt context items, the golden capture %d"
            % (len(seen), len(expected)), reason="context-mismatch")
    for index, (want, got) in enumerate(zip(expected, seen)):
        if want.get("role") != got["role"] or want.get("sha256") != got["sha256"] \
                or want.get("length") != got["length"]:
            raise TranscriptError(
                "pre-prompt context item %d (%s) is not the locked golden context"
                % (index, got["role"]), reason="context-mismatch")


def check(session_path: str, prompt_path: str, completion_path: str,
          call_path: str, golden_path: str, model: str | None = None,
          arm: str | None = None, effort: str | None = None) -> None:
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
            % (named, len(positions)), reason="prompt-mismatch")
    position = positions[0]
    for index, (role, _) in enumerate(events):
        if role in ("user", "developer") and index > position:
            raise TranscriptError("a user/developer message follows %s" % named,
                                  reason="extra-turn")
    call = _load_document(call_path)
    scratch = call.get("cwd", "")
    for token in LEAK_TOKENS:
        if token in scratch.lower():
            raise TranscriptError(
                "the call's working directory contains the leak token %r" % token,
                reason="leak")
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
        raise TranscriptError("no assistant message answers the registered prompt",
                              reason="no-answer")
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
        raise TranscriptError(
            "completion.txt is not the transcript's last assistant message",
            reason="completion-mismatch")
    status = call.get("exitStatus")
    if not isinstance(status, int) or isinstance(status, bool) or status != 0:
        raise TranscriptError(
            "the call did not exit with integer status 0: %r" % status,
            reason="exit-status")
    if model is not None:
        named = {context.get("model") for context in contexts if "model" in context}
        if named and named != {model}:
            raise TranscriptError(
                "the transcript's turn context names %r, not the locked model %r"
                % (sorted(named), model), reason="turn-context-mismatch")
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
                   call.get("cwd")), reason="turn-context-mismatch")
    if effort is not None:
        # §2.1's M-24 witness resolution took the `gate-5-extension` branch
        # (sweeps/2026-08-24-effort-sweep, step zero): the pinned CLI's
        # transcript names the reasoning effort in `turn_context`, in two
        # spellings — the top-level `effort` member and the nested
        # `collaboration_mode.settings.reasoning_effort` — so the effort pin is
        # bound here exactly as the model is, same reason tag, same apparatus
        # side. Three rules, each load-bearing:
        #   - BY PATH, not by name scan: `effort` is a generic key that other
        #     payload structures are free to carry for other quantities, and a
        #     recursive name scan would read whatever a future transcript
        #     format happens to call `effort` or `reasoning_effort` anywhere in
        #     the payload; the gate reads exactly the two registered paths the
        #     witness resolution certified and nothing else.
        #   - a member PRESENT AND NULL is not a witness (the sweep's witness
        #     step's own rule) — but R1-12 closed the fail-open this once
        #     implied: under a FILLED pin at least one non-null witness is
        #     REQUIRED, so a 019-shaped all-null transcript refuses as
        #     unwitnessed rather than passing silently. (An UNFILLED pin still
        #     skips the clause entirely, which is what keeps 019-era callers
        #     and pre-fill states meaningful.)
        #   - EVERY turn_context, not merely one — the cwd clause's rule.
        #   - a nested level that is not an object is an absent path, never an
        #     exception: every other refusal in this module leaves through
        #     `TranscriptError` with a reason and a side, and a malformed
        #     `collaboration_mode` must not hand `classify()` an AttributeError
        #     it has no classification for.
        def _nested(payload):
            mode = payload.get("collaboration_mode")
            if not isinstance(mode, dict):
                return None
            settings = mode.get("settings")
            if not isinstance(settings, dict):
                return None
            return settings.get("reasoning_effort")

        named_efforts = set()
        for context in contexts:
            for value in (context.get("effort"), _nested(context)):
                if value is None:
                    continue
                # R1-12: a witness that is not a string is a malformed record,
                # refused with the gate's own reason — never a TypeError out
                # of `classify()`.
                if not isinstance(value, str):
                    raise TranscriptError(
                        "the transcript's turn context carries a non-string "
                        "reasoning-effort value of type %s"
                        % type(value).__name__,
                        reason="turn-context-mismatch")
                named_efforts.add(value)
        # R1-12: the branch this study RUNS UNDER is `gate-5-extension` — the
        # transcript witnesses the effort — so under a FILLED pin a transcript
        # with no witness at all is not a pass, it is the anomaly the branch
        # exists to catch (fail-open was the finding: no turn_context, an
        # absent path, or all-null values sailed through while the wrapper
        # stamped `reasoningEffortWitnessed: true`).
        if not named_efforts:
            raise TranscriptError(
                "the effort pin is %r and the transcript carries no non-null "
                "effort witness in any turn_context: under the registered "
                "gate-5-extension branch an unwitnessed call is refused, not "
                "presumed" % (effort,),
                reason="turn-context-mismatch")
        if named_efforts != {effort}:
            raise TranscriptError(
                "the transcript's turn context names the reasoning effort %r, "
                "not the pinned %r"
                % (sorted(named_efforts), effort),
                reason="turn-context-mismatch")
