"""Thin, uniform backends for study 001 (policy representation).

WHAT THIS FILE DOES
-------------------
Defines one interface --- ``Backend.complete(system, user, *, seed) -> dict`` ---
and three implementations:

* ``MockBackend``       deterministic canned responses derived from a hash of the
                        prompt. Used for plumbing tests, CI and dry runs. It
                        records ``backend="mock"`` and
                        ``model="mock/deterministic-v1"`` and never impersonates a
                        real model in result metadata.
* ``AnthropicBackend``  plain ``urllib`` POST to the Anthropic Messages API using
                        ``ANTHROPIC_API_KEY``. Model id, temperature, max_tokens,
                        effort and thinking mode are passed in and recorded.
* ``CodexBackend``      shells out to the locally installed ``codex exec`` CLI in
                        a deliberately NON-agentic way: one prompt in, text out.

Every backend returns ``{"text", "raw", "latency_ms", "error"}`` and exposes
``describe()`` returning the exact model identifier and parameter set that the
harness writes into each result row.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
* No prompt construction (see ``arms.py``), no scoring (see ``score.py``), no
  retry-until-parseable loop: a malformed model response is data, not an error to
  paper over.
* No silent fallback. ``AnthropicBackend`` raises at construction time if
  ``ANTHROPIC_API_KEY`` is unset; it never degrades to ``MockBackend``.
* No structured-output / tool-calling coercion. All three arms of the study must
  face the identical output contract expressed in the prompt alone, so we do NOT
  use ``output_config.format`` even though it would reduce parse failures --- doing
  so would change what the study measures.
* No concurrency. Runs are sequential so that a mock run is byte-reproducible.

EXACT ``codex exec`` INVOCATION
-------------------------------
Investigated with ``codex exec --help`` on Codex CLI v0.145.0 and smoke-tested.
The harness runs, with the prompt supplied on **stdin** (the trailing ``-``)::

    codex exec \\
        --skip-git-repo-check \\
        --ephemeral \\
        --ignore-user-config \\
        --ignore-rules \\
        --sandbox read-only \\
        --color never \\
        --model <MODEL> \\
        -c 'mcp_servers={}' \\
        -c 'tools={web_search=false,view_image=false}' \\
        --output-last-message <TMPFILE> \\
        -

Rationale for each flag:

* ``--ephemeral``            do not persist session files to disk.
* ``--ignore-user-config``   do not load ``$CODEX_HOME/config.toml``; this is what
                             actually keeps the operator's MCP servers out of the
                             run. Auth still resolves from ``CODEX_HOME``.
* ``--ignore-rules``         do not load user/project execpolicy ``.rules`` files.
* ``--sandbox read-only``    no file writes; read-only sandbox also means no
                             network egress for model-generated shell commands.
* ``-c 'mcp_servers={}'``    belt-and-braces: empty MCP server table.
* ``-c 'tools={...}''``      disables the built-in ``web_search`` and
                             ``view_image`` tools. Measured effect on a trivial
                             prompt: 6027 -> 907 tokens, i.e. the tool preamble is
                             genuinely gone.
* ``--output-last-message``  the agent's final message is written verbatim to a
                             temp file; that file is the backend's ``text``.
                             stdout is captured only as ``raw`` for diagnostics.
* ``--color never``          keep the captured transcript free of ANSI escapes.

CAVEATS --- READ BEFORE USING ``CodexBackend`` FOR THE PREREGISTERED RUN
------------------------------------------------------------------------
1. **It is not fully deterministic.** ``codex exec`` exposes no temperature and
   no seed. The ``seed`` argument is recorded in the result row but is NOT sent
   to the CLI; run-to-run variation is therefore expected and is precisely what
   the study's consistency metric measures for this family.
2. **It is not perfectly non-agentic.** Even with the flags above, the CLI still
   loads its own bundled skill descriptions into context (it emits
   ``warning: Skill descriptions were shortened ...``) and the model still has a
   shell tool available inside the read-only sandbox. We could not find a
   supported flag to remove either (``--disable skills`` is rejected:
   ``Unknown feature flag: skills``). In practice the model answers directly for
   a single self-contained prompt, but this is a behavioural expectation, not an
   enforced guarantee. This limitation is disclosed rather than worked around.
3. Codex may emit a preamble around the JSON object; ``arms.parse_prediction``
   handles fenced and prose-wrapped JSON, and records a parse failure otherwise.

Python 3.10+ (``from __future__ import annotations`` keeps it importable on 3.8
so the tests can run under whichever interpreter has pytest). Standard library
only.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Sequence

__all__ = [
    "BackendError",
    "Backend",
    "MockBackend",
    "AnthropicBackend",
    "CodexBackend",
    "make_backend",
]

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

DEFAULT_ANTHROPIC_MODEL = "claude-opus-5"
DEFAULT_CODEX_MODEL = "gpt-5.6-sol"


class BackendError(RuntimeError):
    """Raised for configuration faults that must stop the run immediately."""


def _digest(*parts: str) -> bytes:
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(b"\x00")
    return h.digest()


class Backend:
    """Uniform completion interface.

    Subclasses set ``name`` (recorded verbatim as ``backend``) and ``model`` (the
    exact model identifier), and populate ``params`` with every knob that could
    change the output.
    """

    name: str = "base"

    def __init__(self) -> None:
        self.model: str = ""
        self.params: Dict[str, Any] = {}

    def complete(self, system: str, user: str, *, seed: Optional[int]) -> Dict[str, Any]:
        raise NotImplementedError

    def describe(self) -> Dict[str, Any]:
        """Return the metadata every result row must carry."""
        return {
            "backend": self.name,
            "model": self.model,
            "params": json.loads(json.dumps(self.params, sort_keys=True)),
        }


# --------------------------------------------------------------------------- #
# Mock
# --------------------------------------------------------------------------- #


class MockBackend(Backend):
    """Deterministic canned responses derived from sha256(system, user, seed).

    The mock is intentionally *imperfect*: a fixed fraction of prompts yield an
    unparseable response and a fixed fraction wrap the JSON in a code fence, so
    that the parser, the parse-failure accounting and the scorer are all exercised
    end to end without API access. ``latency_ms`` is synthesised from the same
    digest so that a whole mock run is byte-reproducible.

    It never claims to be a real model: ``backend`` is ``"mock"`` and ``model`` is
    ``"mock/deterministic-v1"``.
    """

    name = "mock"
    MODEL_ID = "mock/deterministic-v1"

    def __init__(
        self,
        *,
        rule_ids: Optional[Sequence[str]] = None,
        unparseable_every: int = 16,
        fenced_every: int = 3,
    ) -> None:
        super().__init__()
        self.model = self.MODEL_ID
        self.rule_ids: List[str] = sorted(rule_ids) if rule_ids else []
        self.unparseable_every = int(unparseable_every)
        self.fenced_every = int(fenced_every)
        self.params = {
            "unparseable_every": self.unparseable_every,
            "fenced_every": self.fenced_every,
            "rule_vocabulary_size": len(self.rule_ids),
        }

    def complete(self, system: str, user: str, *, seed: Optional[int]) -> Dict[str, Any]:
        d = _digest(system, user, "" if seed is None else str(seed))
        latency_ms = 5 + (d[3] % 45)

        if self.unparseable_every and d[0] % self.unparseable_every == 0:
            text = (
                "After weighing the operations against the policy I believe this "
                "transaction cannot stand as written."
            )
            return {"text": text, "raw": {"mock_digest": d.hex()}, "latency_ms": latency_ms,
                    "error": None}

        bucket = d[1] % 10
        if bucket <= 5:
            decision = "illegal"
        elif bucket <= 8:
            decision = "legal"
        else:
            decision = "cannot_decide"

        n_cited = d[4] % 4
        if self.rule_ids:
            cited = [self.rule_ids[(d[5 + i] * 7 + i) % len(self.rule_ids)] for i in range(n_cited)]
        else:
            cited = ["mock-rule-%d" % ((d[5 + i] % 61) + 1) for i in range(n_cited)]
        # de-duplicate while preserving order
        seen: Dict[str, None] = {}
        for c in cited:
            seen.setdefault(c, None)
        cited = list(seen)

        payload = {
            "decision": decision,
            "cited_rules": cited,
            "reason": "Deterministic mock response derived from prompt digest %s." % d[:6].hex(),
        }
        body = json.dumps(payload, indent=2, sort_keys=True)
        if self.fenced_every and d[2] % self.fenced_every == 0:
            text = "```json\n" + body + "\n```"
        else:
            text = body
        return {"text": text, "raw": {"mock_digest": d.hex()}, "latency_ms": latency_ms,
                "error": None}


# --------------------------------------------------------------------------- #
# Anthropic
# --------------------------------------------------------------------------- #


class AnthropicBackend(Backend):
    """Anthropic Messages API over plain ``urllib``.

    Fails loudly at construction when ``ANTHROPIC_API_KEY`` is absent --- there is
    no fallback to the mock, because a silently-mocked "real" arm would corrupt
    the study.

    Note on ``temperature``: the current Opus/Sonnet 5 generation rejects
    ``temperature``/``top_p``/``top_k`` with a 400. The parameter is therefore
    ``None`` by default and only included in the request body when explicitly set;
    it is recorded either way so the run is self-describing.
    """

    name = "anthropic"

    def __init__(
        self,
        *,
        model: str = DEFAULT_ANTHROPIC_MODEL,
        max_tokens: int = 4096,
        temperature: Optional[float] = None,
        effort: Optional[str] = None,
        thinking: Optional[str] = None,
        timeout_s: float = 600.0,
        max_retries: int = 3,
        api_key: Optional[str] = None,
    ) -> None:
        super().__init__()
        key = api_key if api_key is not None else os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise BackendError(
                "ANTHROPIC_API_KEY is not set. The anthropic backend refuses to run "
                "without credentials; it will not fall back to the mock backend."
            )
        self._api_key = key
        self.model = model
        self.params = {
            "max_tokens": int(max_tokens),
            "temperature": temperature,
            "effort": effort,
            "thinking": thinking,
            "timeout_s": float(timeout_s),
            "max_retries": int(max_retries),
            "anthropic_version": ANTHROPIC_VERSION,
        }

    def _body(self, system: str, user: str) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.params["max_tokens"],
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        if self.params["temperature"] is not None:
            body["temperature"] = self.params["temperature"]
        if self.params["thinking"]:
            body["thinking"] = {"type": self.params["thinking"]}
        if self.params["effort"]:
            body["output_config"] = {"effort": self.params["effort"]}
        return body

    @staticmethod
    def _extract_text(payload: Dict[str, Any]) -> str:
        chunks: List[str] = []
        for block in payload.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "text":
                chunks.append(block.get("text") or "")
        return "".join(chunks)

    def complete(self, system: str, user: str, *, seed: Optional[int]) -> Dict[str, Any]:
        # The Messages API has no seed parameter; `seed` is recorded by the caller
        # in the result row but cannot be transmitted. Repeated trials therefore
        # measure genuine run-to-run variation.
        data = json.dumps(self._body(system, user)).encode("utf-8")
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        attempts = int(self.params["max_retries"]) + 1
        started = time.monotonic()
        last_error = "unknown error"
        for attempt in range(attempts):
            req = urllib.request.Request(
                ANTHROPIC_MESSAGES_URL, data=data, headers=headers, method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=self.params["timeout_s"]) as resp:
                    raw = json.loads(resp.read().decode("utf-8"))
                latency_ms = int((time.monotonic() - started) * 1000)
                if raw.get("stop_reason") == "refusal":
                    return {
                        "text": self._extract_text(raw),
                        "raw": raw,
                        "latency_ms": latency_ms,
                        "error": "refusal:%s" % ((raw.get("stop_details") or {}).get("category")),
                    }
                return {
                    "text": self._extract_text(raw),
                    "raw": raw,
                    "latency_ms": latency_ms,
                    "error": None,
                }
            except urllib.error.HTTPError as exc:  # noqa: PERF203 - explicit branches
                detail = exc.read().decode("utf-8", "replace")[:2000]
                last_error = "http %d: %s" % (exc.code, detail)
                retryable = exc.code in (408, 409, 429) or exc.code >= 500
                if not retryable or attempt == attempts - 1:
                    break
                delay = float(exc.headers.get("retry-after") or (2 ** attempt))
                time.sleep(min(delay, 60.0))
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = "connection: %r" % (exc,)
                if attempt == attempts - 1:
                    break
                time.sleep(min(2 ** attempt, 60.0))
        latency_ms = int((time.monotonic() - started) * 1000)
        return {"text": "", "raw": None, "latency_ms": latency_ms, "error": last_error}


# --------------------------------------------------------------------------- #
# Codex
# --------------------------------------------------------------------------- #


class CodexBackend(Backend):
    """One-shot, non-agentic ``codex exec`` invocation. See module docstring."""

    name = "codex"

    def __init__(
        self,
        *,
        model: str = DEFAULT_CODEX_MODEL,
        executable: str = "codex",
        timeout_s: float = 600.0,
        workdir: Optional[str] = None,
        extra_config: Sequence[str] = (),
    ) -> None:
        super().__init__()
        resolved = shutil.which(executable)
        if resolved is None:
            raise BackendError(
                "codex executable %r not found on PATH. The codex backend refuses to "
                "run without it; it will not fall back to the mock backend." % executable
            )
        self._executable = resolved
        self.model = model
        self._workdir = workdir or tempfile.gettempdir()
        self._extra_config = list(extra_config)
        self.params = {
            "executable": resolved,
            "sandbox": "read-only",
            "ephemeral": True,
            "ignore_user_config": True,
            "ignore_rules": True,
            "mcp_servers": "{}",
            "tools": "{web_search=false,view_image=false}",
            "extra_config": self._extra_config,
            "timeout_s": float(timeout_s),
            "workdir": self._workdir,
            "deterministic": False,
            "seed_supported": False,
        }

    def _argv(self, last_message_path: str) -> List[str]:
        argv = [
            self._executable,
            "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--sandbox",
            "read-only",
            "--color",
            "never",
            "--model",
            self.model,
            "-c",
            "mcp_servers={}",
            "-c",
            "tools={web_search=false,view_image=false}",
        ]
        for cfg in self._extra_config:
            argv.extend(["-c", cfg])
        argv.extend(["--output-last-message", last_message_path, "-"])
        return argv

    def complete(self, system: str, user: str, *, seed: Optional[int]) -> Dict[str, Any]:
        # `codex exec` takes a single prompt, so the system block is folded into the
        # prompt under an explicit marker. `seed` cannot be transmitted (see caveat
        # 1 in the module docstring).
        prompt = "SYSTEM INSTRUCTIONS\n%s\n\nTASK\n%s\n" % (system.strip(), user.strip())
        started = time.monotonic()
        tmpdir = tempfile.mkdtemp(prefix="jps-codex-")
        last_message_path = os.path.join(tmpdir, "last_message.txt")
        try:
            proc = subprocess.run(  # noqa: S603 - argv list, no shell
                self._argv(last_message_path),
                input=prompt.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self._workdir,
                timeout=self.params["timeout_s"],
            )
        except subprocess.TimeoutExpired:
            latency_ms = int((time.monotonic() - started) * 1000)
            return {"text": "", "raw": None, "latency_ms": latency_ms,
                    "error": "timeout after %ss" % self.params["timeout_s"]}
        finally:
            pass
        latency_ms = int((time.monotonic() - started) * 1000)
        stdout = proc.stdout.decode("utf-8", "replace")
        stderr = proc.stderr.decode("utf-8", "replace")
        text = ""
        if os.path.exists(last_message_path):
            with open(last_message_path, "r", encoding="utf-8") as fh:
                text = fh.read()
            os.unlink(last_message_path)
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass
        error = None
        if proc.returncode != 0:
            error = "codex exit %d: %s" % (proc.returncode, stderr.strip()[:2000])
        elif not text.strip():
            error = "codex produced no final message"
        return {
            "text": text,
            "raw": {"returncode": proc.returncode, "stdout": stdout, "stderr": stderr},
            "latency_ms": latency_ms,
            "error": error,
        }


# --------------------------------------------------------------------------- #
# Factory
# --------------------------------------------------------------------------- #


def make_backend(name: str, **kwargs: Any) -> Backend:
    """Construct a backend by name. Unknown names raise ``BackendError``."""
    if name == "mock":
        return MockBackend(
            rule_ids=kwargs.get("rule_ids"),
            unparseable_every=kwargs.get("unparseable_every", 16),
            fenced_every=kwargs.get("fenced_every", 3),
        )
    if name == "anthropic":
        return AnthropicBackend(
            model=kwargs.get("model") or DEFAULT_ANTHROPIC_MODEL,
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature"),
            effort=kwargs.get("effort"),
            thinking=kwargs.get("thinking"),
            timeout_s=kwargs.get("timeout_s", 600.0),
            max_retries=kwargs.get("max_retries", 3),
        )
    if name == "codex":
        return CodexBackend(
            model=kwargs.get("model") or DEFAULT_CODEX_MODEL,
            executable=kwargs.get("executable", "codex"),
            timeout_s=kwargs.get("timeout_s", 600.0),
            workdir=kwargs.get("workdir"),
        )
    raise BackendError("unknown backend %r (expected mock|anthropic|codex)" % name)
