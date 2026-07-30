"""Attestation core, inline (stdio proxy) deployment shape.

Built to SPEC.md. Standard library only, so a second implementation can be
written clean-room from SPEC.md alone and agreement-tested against this one
(ADR-0002: an external contract two implementations agree on, not code checked
against itself).

The component is an MCP server to a client and an MCP client to one downstream
MCP server, over stdio (newline-delimited JSON-RPC 2.0). It forwards every
message unaltered and, for each successful tools/call result flowing
downstream->client, stamps a hash-chained receipt and retains the result before
forwarding. The forwarded result is byte-identical to the downstream's; the
model neither authors nor carries the proof.

Trust boundary (inline shape): the operator, not the downstream or the client,
is assumed to control the key and the store. What is proven is wire-level:
nothing the model computes enters the proof, and every successful tools/call
result forwarded is attested or the run fails closed. OS-level isolation of the
key and store from a same-UID downstream, and detection of whole-session replay
or final-tail rollback, are the hosted gateway's responsibility (ADR-0002)."""

import binascii
import datetime
import hashlib
import hmac
import json
import os
import re
import subprocess
import sys
import threading

RECEIPT_VERSION = "1"
MIN_KEY_BYTES = 32
_SAFE_INT_MAX = (1 << 53) - 1
_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_ABSENT = object()  # distinguishes an absent `id` member from an explicit null


class AttestationError(Exception):
    """A result cannot be attested. The caller must fail closed: a result that
    cannot be attested is not forwarded as if it were."""


class _DuplicateKeyError(ValueError):
    """A JSON object with a repeated member name is outside canon's domain."""


def _reject_duplicate_keys(pairs):
    """A json object_pairs_hook that rejects a repeated member name, so a
    result whose meaning depends on first-vs-last-wins is never attested (the
    bytes forwarded to the client would be ambiguous to a differently-parsing
    reader). Deterministic across implementations, unlike silent last-wins."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError("duplicate object member name: %r" % (key,))
        result[key] = value
    return result


def _loads(text):
    """Parse one JSON message, rejecting duplicate object member names."""
    return json.loads(text, object_pairs_hook=_reject_duplicate_keys)


def _id_key(value):
    """A hashable, JSON-type-tagged correlation key for a request/response id.

    Python's `True == 1 == 1.0` and their equal hashes would otherwise let a
    response with id `true` retire a pending request with id `1`, slipping the
    real result through unattested. Tagging by JSON type keeps `true`, `1`, and
    `1.0` distinct. Arrays/objects are not valid JSON-RPC ids but are tagged
    distinctly so they can never collide with a scalar id either. bool is tested
    before int, since bool is an int subclass."""
    if value is None:
        return ("null",)
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, int):
        return ("int", value)
    if isinstance(value, float):
        return ("float", value)
    if isinstance(value, str):
        return ("str", value)
    return ("composite", json.dumps(value, sort_keys=True))


def _check_domain(value):
    """Enforce canon's restricted JSON domain (SPEC.md): objects, arrays,
    strings of Unicode scalar values, booleans, null, and integers in the safe
    range. Anything else is not reproducibly canonicalizable across languages,
    so it is outside the domain and canon raises."""
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if not (-_SAFE_INT_MAX <= value <= _SAFE_INT_MAX):
            raise ValueError("integer outside the canon safe range: %r" % value)
        return
    if isinstance(value, float):
        raise ValueError("non-integer number is outside the canon domain: %r" % value)
    if isinstance(value, str):
        _reject_lone_surrogate(value)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("non-string object member name: %r" % (key,))
            _reject_lone_surrogate(key)  # a surrogate in a KEY, too, not only a value
            _check_domain(item)
        return
    if isinstance(value, list):
        for item in value:
            _check_domain(item)
        return
    raise ValueError("value outside the canon domain: %r" % (value,))


def _reject_lone_surrogate(text):
    # A lone surrogate is not a Unicode scalar value; reject it deterministically
    # rather than let UTF-8 encoding raise later.
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        raise ValueError("string contains a lone surrogate, outside the canon domain")


def canon(value):
    """Canonical serialization (SPEC.md 'canon'): object members sorted by
    Unicode code point, compact separators, raw UTF-8, over a restricted JSON
    domain. Returns bytes. Raises ValueError on a value outside the domain."""
    _check_domain(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def digest(data):
    """digest(bytes) = 'sha256:' + lowercase-hex(SHA-256(bytes))."""
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _hexdigest(digest_string):
    return digest_string.split(":", 1)[1]


def _require_key(key):
    if len(key) < MIN_KEY_BYTES:
        raise AttestationError(
            "attestation key must be at least %d bytes; got %d" % (MIN_KEY_BYTES, len(key))
        )
    return key


def _fsync_dir(path):
    """Make a new directory entry durable. A no-op where directory fsync is
    unsupported."""
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


class Store:
    """The append-only receipt and content-addressed artifact store.

    Append-only here means this component never overwrites a receipt and refuses
    to proceed if it cannot durably write one. It does NOT defend against an
    external actor with write access deleting or replaying store files; that is
    the gateway's job (SPEC.md 'Trust boundary')."""

    def __init__(self, root, key, authority):
        self.root = root
        self.key = _require_key(key)
        self.authority = authority
        os.makedirs(os.path.join(root, "artifacts"), exist_ok=True)
        os.makedirs(os.path.join(root, "receipts"), exist_ok=True)

    def keyed_digest(self, domain, data):
        return "hmac-sha256:" + hmac.new(
            self.key, domain.encode("ascii") + b":" + data, hashlib.sha256
        ).hexdigest()

    def _write_temp(self, near, data):
        tmp = "%s.%d.%s.tmp" % (near, os.getpid(), binascii.hexlify(os.urandom(6)).decode())
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return tmp

    def retain(self, canonical_result):
        """Write the exact canonical result bytes content-addressed. Idempotent."""
        result_digest = digest(canonical_result)
        path = os.path.join(self.root, "artifacts", _hexdigest(result_digest))
        tmp = self._write_temp(path, canonical_result)
        try:
            os.replace(tmp, path)
            _fsync_dir(os.path.dirname(path))
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        return result_digest

    def stamp(self, receipt_core):
        """Append one receipt at receipts/<sessionId>/<callIndex>.json. Atomic,
        exclusive (append-only), and durable; fails closed if it cannot write."""
        session_dir = os.path.join(self.root, "receipts", receipt_core["sessionId"])
        os.makedirs(session_dir, exist_ok=True)
        path = os.path.join(session_dir, "%d.json" % receipt_core["callIndex"])
        mac = hmac.new(self.key, canon(receipt_core), hashlib.sha256).hexdigest()
        stored = dict(receipt_core)
        stored["hmac"] = mac
        tmp = self._write_temp(path, canon(stored) + b"\n")
        try:
            try:
                os.link(tmp, path)  # atomic exclusive create; raises if path exists
            except FileExistsError:
                raise AttestationError("receipt already exists (append-only): %s" % path)
            _fsync_dir(session_dir)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        return stored


def _now():
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )


class Proxy:
    """Pumps JSON-RPC messages between a client (this process's stdio) and one
    downstream MCP server, stamping successful tools/call results in passing."""

    def __init__(self, downstream_cmd, store, session_id=None):
        self.downstream_cmd = list(downstream_cmd)
        self.store = store
        self.session_id = session_id or binascii.hexlify(os.urandom(8)).decode()
        self.call_index = 0
        self._prev_hmac = None
        self._pending = {}   # outstanding client->server request id -> (kind, tool, arguments)
        self._server_info = None
        self._lock = threading.Lock()
        self._fatal = None
        self._downstream = None

    def _note_request(self, message):
        """Client->downstream direction. Track EVERY outstanding client request
        id -- not only tools/call -- so a second request reusing an outstanding
        id (a protocol violation that could misroute attestation) fails closed,
        and so no server->client response can retire a tool call it does not
        belong to. A client RESPONSE (id, no method) to a server->client request
        carries no method and is not a client request, so it is not tracked."""
        mid = message.get("id", _ABSENT)
        # A client request is any message with an id member AND a method member
        # (member PRESENCE, not value: an explicit `method: null` is still a
        # request-shaped message that occupies its id, and must be duplicate-
        # checked, not silently skipped). A notification (method, no id) and a
        # client response to a server request (id, no method) are not tracked.
        # An explicit `id: null` IS an id -- conflating it with an absent member
        # would let a null-id tool call slip through unattested.
        if mid is _ABSENT or "method" not in message:
            return
        key = _id_key(mid)
        method = message.get("method")
        with self._lock:
            if key in self._pending:
                raise AttestationError("duplicate outstanding request id %r" % (mid,))
            if method == "tools/call":
                params = message.get("params") or {}
                self._pending[key] = ("tools/call", params.get("name"), params.get("arguments") or {})
            elif method == "initialize":
                self._pending[key] = ("initialize", None, None)
            else:
                self._pending[key] = ("other", None, None)

    def _note_response(self, message):
        """Downstream->client direction. Only a genuine JSON-RPC response --
        carrying `result` or `error`, and no `method` -- retires a pending
        request. A server->client request/notification (has `method`) and a
        malformed method-less object with neither result nor error must NOT
        consume a pending entry, or a later genuine tool result would go
        unattested."""
        if "method" in message:
            return
        if "result" not in message and "error" not in message:
            return
        mid = message.get("id", _ABSENT)
        if mid is _ABSENT:
            return
        with self._lock:
            tracked = self._pending.pop(_id_key(mid), _ABSENT)
        if tracked is _ABSENT:
            return
        kind = tracked[0]
        if kind == "initialize":
            result = message.get("result") or {}
            with self._lock:
                self._server_info = result.get("serverInfo")
            return
        if kind != "tools/call" or "result" not in message:
            # A non-tool request answered, or a tools/call error response (no
            # result): nothing to attest.
            return
        served_at = _now()
        _, tool, arguments = tracked
        result = message["result"]
        result_digest = self.store.retain(canon(result))
        with self._lock:
            index = self.call_index
            self.call_index += 1
            server_info = self._server_info
            prev_hmac = self._prev_hmac
        receipt_core = {
            "receiptVersion": RECEIPT_VERSION,
            "sessionId": self.session_id,
            "callIndex": index,
            "prevHmac": prev_hmac,
            "tool": tool,
            "argumentsDigest": self.store.keyed_digest("args", canon(arguments)),
            "resultDigest": result_digest,
            "isError": bool(result.get("isError", False)) if isinstance(result, dict) else False,
            "servedAt": served_at,
            "authority": self.store.authority,
            "downstream": {"command": self.downstream_cmd, "serverInfo": server_info},
        }
        stored = self.store.stamp(receipt_core)
        with self._lock:
            self._prev_hmac = stored["hmac"]

    def run(self):
        self._downstream = subprocess.Popen(
            self.downstream_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stderr,
        )
        up = threading.Thread(
            target=self._pump, args=(sys.stdin.buffer, self._downstream.stdin, self._note_request), daemon=True,
        )
        down = threading.Thread(
            target=self._pump, args=(self._downstream.stdout, sys.stdout.buffer, self._note_response), daemon=True,
        )
        up.start()
        down.start()
        # End on the first terminal condition: a fatal in either direction, or
        # either pump reaching EOF (client stdin closed, or downstream stdout
        # closed / process died). Polling both liveness flags avoids waiting
        # forever on one pump when the other ends. The loop advances time only
        # while up is alive; if down ends first, its liveness flag drops and the
        # loop exits within one poll interval.
        while up.is_alive() and down.is_alive() and self._fatal is None:
            up.join(0.1)
        if self._fatal is not None:
            return self._fail()
        # One pump ended cleanly. Close the downstream's stdin so a well-behaved
        # server exits, then drain the downstream pump under a bounded wait.
        # Every result already forwarded to the client is attested -- the down
        # pump forwards only after stamping -- so bounding the drain cannot let
        # an unattested result through; it only bounds shutdown of a downstream
        # that ignores its closed stdin.
        try:
            if self._downstream.stdin is not None and not self._downstream.stdin.closed:
                self._downstream.stdin.close()
        except OSError:
            pass
        down.join(timeout=10)
        if self._fatal is not None:
            return self._fail()
        if down.is_alive():
            # The downstream did not finish draining within the bound (it is
            # ignoring its closed stdin, or a stamp is wedged). We cannot confirm
            # every result was attested and cleanly forwarded, so fail closed
            # rather than claim success.
            self._terminate()
            sys.stderr.write("attest: downstream did not drain; failing closed\n")
            return 1
        # down reached EOF, so the downstream closed stdout and has exited or is
        # about to. Reap it and propagate a non-zero downstream exit.
        try:
            rc = self._downstream.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._terminate()
            return 1
        if rc != 0:
            sys.stderr.write("attest: downstream exited %d\n" % rc)
            return 1
        return 0

    def _fail(self):
        self._terminate()
        sys.stderr.write("attest: fatal, failing closed: %s\n" % self._fatal)
        return 1

    def _terminate(self):
        try:
            self._downstream.terminate()
        except (OSError, AttributeError):
            pass

    def _go_fatal(self, reason):
        if self._fatal is None:
            self._fatal = reason

    def _pump(self, source, sink, observe):
        """Read newline-delimited JSON-RPC from source; act on each object
        message; then forward the ORIGINAL bytes unaltered. Any failure to
        attest, a batch, or an unexpected error fails the run closed WITHOUT
        forwarding the offending line."""
        try:
            for line in source:
                stripped = line.strip()
                if stripped:
                    try:
                        message = _loads(stripped)
                    except _DuplicateKeyError as error:
                        # Ambiguous bytes we must not attest or forward as if
                        # unambiguous.
                        self._go_fatal("duplicate object member: %s" % error)
                        return
                    except ValueError:
                        message = None  # not a JSON message; forward as opaque bytes
                    except Exception as error:
                        self._go_fatal("parse: %s: %s" % (type(error).__name__, error))
                        return
                    if isinstance(message, list):
                        self._go_fatal("JSON-RPC batch is not supported")
                        return
                    if isinstance(message, dict):
                        try:
                            observe(message)
                        except Exception as error:
                            self._go_fatal("%s: %s" % (type(error).__name__, error))
                            return
                try:
                    sink.write(line)
                    sink.flush()
                except (BrokenPipeError, OSError):
                    return
        except (BrokenPipeError, OSError):
            pass
        finally:
            try:
                sink.close()
            except OSError:
                pass


def verify(store_root, key, expected_authority=None):
    """Verify every receipt under store_root. See SPEC.md 'Verification' for the
    checks and the two residuals (whole-session replay and final-tail rollback)
    that need an external anchor. Returns (ok, findings)."""
    _require_key(key)
    findings = []
    receipts_root = os.path.join(store_root, "receipts")
    all_ok = True
    if not os.path.isdir(receipts_root):
        return True, findings
    for session_id in sorted(os.listdir(receipts_root)):
        session_dir = os.path.join(receipts_root, session_id)
        if not os.path.isdir(session_dir):
            continue
        by_index = {}
        for name in sorted(os.listdir(session_dir)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(session_dir, name)
            try:
                with open(path, "rb") as handle:
                    # _loads rejects duplicate member names, so a receipt whose
                    # bytes are ambiguous under first-vs-last-wins is malformed,
                    # not silently recovered to its signed form.
                    stored = _loads(handle.read().decode("utf-8"))
                if not isinstance(stored, dict):
                    raise ValueError("receipt is not a JSON object")
                status = _verify_one(stored, key, store_root, session_id, name, expected_authority)
            except Exception:
                all_ok = False
                findings.append({"sessionId": session_id, "file": name, "status": "malformed"})
                continue
            if status != "ok":
                all_ok = False
            else:
                by_index[stored["callIndex"]] = stored
            findings.append({"sessionId": session_id, "callIndex": stored.get("callIndex"), "status": status})
        chain_status = _verify_chain(by_index)
        if chain_status != "ok":
            all_ok = False
            findings.append({"sessionId": session_id, "callIndex": None, "status": chain_status})
    return all_ok, findings


def _verify_one(stored, key, store_root, session_id, name, expected_authority):
    # type(x) is int, not isinstance: a JSON true is an int subclass and must
    # not pass as a callIndex.
    if "hmac" not in stored or type(stored.get("callIndex")) is not int:
        return "malformed"
    result_digest = stored.get("resultDigest")
    # Validate the digest shape before it reaches a filesystem path, so a value
    # like "sha256:/dev/zero" can never escape the artifacts directory.
    if not isinstance(result_digest, str) or not _DIGEST_RE.match(result_digest):
        return "malformed"
    receipt_core = {k: v for k, v in stored.items() if k != "hmac"}
    expected_mac = hmac.new(key, canon(receipt_core), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_mac, stored.get("hmac", "")):
        return "hmac-mismatch"
    if stored.get("sessionId") != session_id or ("%d.json" % stored["callIndex"]) != name:
        return "misfiled"
    if expected_authority is not None and stored.get("authority") != expected_authority:
        return "authority-mismatch"
    artifact_path = os.path.join(store_root, "artifacts", _hexdigest(result_digest))
    if not os.path.exists(artifact_path):
        return "artifact-missing"
    with open(artifact_path, "rb") as handle:
        data = handle.read()
    if digest(data) != result_digest:
        return "artifact-mismatch"
    return "ok"


def _verify_chain(by_index):
    if not by_index:
        return "ok"
    # Compare against the count of receipts, never range(max_index): a signed
    # but huge callIndex must not allocate proportional to its value.
    if sorted(by_index) != list(range(len(by_index))):
        return "sequence-broken"
    prev = None
    for index in range(len(by_index)):
        receipt = by_index[index]
        if receipt.get("prevHmac") != prev:
            return "chain-broken"
        prev = receipt["hmac"]
    return "ok"


def _load_key(path):
    with open(path, "rb") as handle:
        return handle.read()


def main(argv):
    if len(argv) >= 2 and argv[1] == "verify":
        if len(argv) < 4:
            sys.stderr.write("usage: attest.py verify <store> <keyfile> [--authority NAME]\n")
            return 2
        authority = argv[5] if len(argv) >= 6 and argv[4] == "--authority" else None
        try:
            ok, findings = verify(argv[2], _load_key(argv[3]), authority)
        except AttestationError as error:
            sys.stderr.write("attest: %s\n" % error)
            return 2
        json.dump({"ok": ok, "findings": findings}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if ok else 1
    if len(argv) < 4 or argv[1] != "wrap":
        sys.stderr.write(
            "usage:\n"
            "  attest.py wrap <store> <keyfile> [--authority NAME] -- <downstream cmd...>\n"
            "  attest.py verify <store> <keyfile> [--authority NAME]\n"
        )
        return 2
    store_root, key_path = argv[2], argv[3]
    rest = argv[4:]
    authority = "acquisition-proxy:local"
    if rest and rest[0] == "--authority":
        authority = rest[1]
        rest = rest[2:]
    if rest and rest[0] == "--":
        rest = rest[1:]
    if not rest:
        sys.stderr.write("attest: no downstream command given after --\n")
        return 2
    try:
        store = Store(store_root, _load_key(key_path), authority)
    except AttestationError as error:
        sys.stderr.write("attest: %s\n" % error)
        return 2
    return Proxy(rest, store).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
