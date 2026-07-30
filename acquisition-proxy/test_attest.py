"""Tests for the attestation core, built to prove the invariants SPEC.md
claims -- not merely to exercise the happy path. Standard library only.

An integration test wraps the real judgment-pack MCP server (`jpack mcp`) to
show the component attests an arbitrary downstream it was not built for; it
skips cleanly when no `jpack` is on PATH.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import attest

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = b"k" * 32  # exactly the 32-byte minimum


class CanonKnownAnswers(unittest.TestCase):
    def test_vectors_from_spec(self):
        self.assertEqual(attest.canon({"b": 1, "a": 2}), b'{"a":2,"b":1}')
        self.assertEqual(attest.canon({"k": "é"}), b'{"k":"\xc3\xa9"}')
        self.assertEqual(attest.canon({"z": [3, 2, 1], "a": {}}), b'{"a":{},"z":[3,2,1]}')
        self.assertEqual(attest.canon({"t": True, "n": None, "x": -5}), b'{"n":null,"t":true,"x":-5}')
        self.assertEqual(attest.canon("line\nbreak"), b'"line\\nbreak"')

    def test_domain_rejects_float_and_nan_and_bignum(self):
        for bad in (1.5, float("nan"), float("inf"), (1 << 53), -(1 << 53)):
            with self.assertRaises(ValueError):
                attest.canon({"v": bad})

    def test_domain_rejects_nested_and_lone_surrogate(self):
        with self.assertRaises(ValueError):
            attest.canon({"a": {"b": [1, 2, 1.5]}})       # a float nested deep
        with self.assertRaises(ValueError):
            attest.canon({"a": [{"b": (1 << 60)}]})        # a bignum nested deep
        with self.assertRaises(ValueError):
            attest.canon({"s": "\ud800"})                  # lone surrogate

    def test_digest_shape(self):
        d = attest.digest(b"hello")
        self.assertTrue(d.startswith("sha256:"))
        self.assertEqual(len(d), len("sha256:") + 64)


class Correlation(unittest.TestCase):
    """Direct probes of the request/response correlation logic, keyed by
    JSON-type-tagged id. These guard the family of bugs five review rounds
    found: an id of one JSON type must never retire a pending call of another,
    and only a genuine response retires a pending entry."""

    def _proxy(self):
        store = type("S", (), {
            "authority": "a",
            "retain": lambda self, b: "sha256:" + ("0" * 64),
            "stamp": lambda self, c: dict(c, hmac="h"),
            "keyed_digest": lambda self, d, b: "hmac-sha256:z",
        })()
        return attest.Proxy(["x"], store)

    def test_id_key_distinguishes_json_types(self):
        for a, b in [(True, 1), (1.0, 1), ("1", 1), (True, "true")]:
            self.assertNotEqual(attest._id_key(a), attest._id_key(b))
        for weird in ([1, 2], {"a": 1}, None, False):
            hash(attest._id_key(weird))  # total and hashable, no crash

    def test_array_id_not_retired_by_scalar(self):
        p = self._proxy()
        p._note_request({"id": [1], "method": "tools/call", "params": {"name": "t", "arguments": {}}})
        p._note_response({"id": 1, "result": {}})            # scalar must not retire [1]
        self.assertEqual(len(p._pending), 1)
        p._note_response({"id": [1], "result": {}})          # the real array-id result attests
        self.assertEqual(p.call_index, 1)

    def test_out_of_order_responses_each_attest(self):
        p = self._proxy()
        p._note_request({"id": 1, "method": "tools/call", "params": {"name": "a", "arguments": {}}})
        p._note_request({"id": 2, "method": "tools/call", "params": {"name": "b", "arguments": {}}})
        p._note_response({"id": 2, "result": {}})
        p._note_response({"id": 1, "result": {}})
        self.assertEqual(p.call_index, 2)
        self.assertEqual(len(p._pending), 0)

    def test_server_request_and_nonresponse_do_not_retire(self):
        p = self._proxy()
        p._note_request({"id": 9, "method": "tools/call", "params": {"name": "t", "arguments": {}}})
        p._note_response({"id": 9, "method": "sampling/createMessage", "params": {}})  # has method
        p._note_response({"id": 9})  # neither result nor error
        self.assertEqual(len(p._pending), 1)
        p._note_response({"id": 9, "result": {}})
        self.assertEqual(p.call_index, 1)


class KeyGuards(unittest.TestCase):
    def test_short_key_refused(self):
        with self.assertRaises(attest.AttestationError):
            attest.Store(tempfile.mkdtemp(), b"tooshort", "a")
        with self.assertRaises(attest.AttestationError):
            attest.verify(tempfile.mkdtemp(), b"tooshort")


class KnownAnswerHmac(unittest.TestCase):
    def test_keyed_digest_is_deterministic_and_keyed(self):
        s1 = attest.Store(tempfile.mkdtemp(), KEY, "a")
        s2 = attest.Store(tempfile.mkdtemp(), b"j" * 32, "a")
        d1 = s1.keyed_digest("args", attest.canon({"q": "x"}))
        self.assertTrue(d1.startswith("hmac-sha256:"))
        self.assertEqual(d1, s1.keyed_digest("args", attest.canon({"q": "x"})))
        self.assertNotEqual(d1, s2.keyed_digest("args", attest.canon({"q": "x"})))  # keyed
        self.assertNotEqual(d1, s1.keyed_digest("other", attest.canon({"q": "x"})))  # domain-separated


class StoreAndVerifier(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.store = attest.Store(self.dir, KEY, "test:authority")
        self._prev = None

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _stamp(self, index, session="sess"):
        core = {
            "receiptVersion": "1", "sessionId": session, "callIndex": index,
            "prevHmac": self._prev if session == "sess" else None,
            "tool": "t", "argumentsDigest": self.store.keyed_digest("args", attest.canon({})),
            "resultDigest": self.store.retain(attest.canon({"v": index})),
            "isError": False, "servedAt": "2026-07-30T00:00:00Z",
            "authority": "test:authority", "downstream": {"command": ["x"], "serverInfo": None},
        }
        stored = self.store.stamp(core)
        if session == "sess":
            self._prev = stored["hmac"]
        return stored

    def _verify(self, **kw):
        return attest.verify(self.dir, KEY, **kw)

    def test_chain_of_receipts_verifies(self):
        for i in range(3):
            self._stamp(i)
        ok, findings = self._verify()
        self.assertTrue(ok, findings)
        self.assertEqual([f["status"] for f in findings], ["ok", "ok", "ok"])

    def test_append_only_refuses_overwrite(self):
        self._stamp(0)
        with self.assertRaises(attest.AttestationError):
            self._stamp(0)

    def test_wrong_key_is_hmac_mismatch(self):
        self._stamp(0)
        ok, findings = attest.verify(self.dir, b"z" * 32)
        self.assertFalse(ok)
        self.assertEqual(findings[0]["status"], "hmac-mismatch")

    def test_tampered_artifact_is_mismatch(self):
        stored = self._stamp(0)
        path = os.path.join(self.dir, "artifacts", stored["resultDigest"].split(":", 1)[1])
        with open(path, "wb") as handle:
            handle.write(b'{"v":999}')
        ok, findings = self._verify()
        self.assertFalse(ok)
        self.assertEqual(findings[0]["status"], "artifact-mismatch")

    def test_tampered_receipt_field_is_hmac_mismatch(self):
        self._stamp(0)
        path = os.path.join(self.dir, "receipts", "sess", "0.json")
        with open(path, "rb") as handle:
            stored = json.loads(handle.read())
        stored["tool"] = "tampered"
        os.remove(path)
        with open(path, "wb") as handle:
            handle.write(attest.canon(stored) + b"\n")
        ok, findings = self._verify()
        self.assertFalse(ok)
        self.assertEqual(findings[0]["status"], "hmac-mismatch")

    def test_missing_artifact_detected(self):
        stored = self._stamp(0)
        os.remove(os.path.join(self.dir, "artifacts", stored["resultDigest"].split(":", 1)[1]))
        ok, findings = self._verify()
        self.assertFalse(ok)
        self.assertEqual(findings[0]["status"], "artifact-missing")

    def test_sequence_gap_detected(self):
        self._stamp(0)
        self._prev = None  # break the chain deliberately so 2 is standalone
        self._stamp(2)
        ok, findings = self._verify()
        self.assertFalse(ok)
        self.assertTrue(any(f["status"] == "sequence-broken" for f in findings))

    def test_replay_into_other_session_is_misfiled(self):
        self._stamp(0)
        # Copy the valid receipt into a different session directory.
        src = os.path.join(self.dir, "receipts", "sess", "0.json")
        dst_dir = os.path.join(self.dir, "receipts", "elsewhere")
        os.makedirs(dst_dir)
        shutil.copy(src, os.path.join(dst_dir, "0.json"))
        ok, findings = self._verify()
        self.assertFalse(ok)
        self.assertTrue(any(f["status"] == "misfiled" for f in findings))

    def test_rename_into_other_index_is_misfiled(self):
        self._stamp(0)
        self._stamp(1)
        # Rename receipt 1 to slot 5: its signed callIndex (1) no longer matches.
        src = os.path.join(self.dir, "receipts", "sess", "1.json")
        os.rename(src, os.path.join(self.dir, "receipts", "sess", "5.json"))
        ok, findings = self._verify()
        self.assertFalse(ok)
        self.assertTrue(any(f["status"] == "misfiled" for f in findings))

    def test_interior_deletion_breaks_chain(self):
        for i in range(3):
            self._stamp(i)
        os.remove(os.path.join(self.dir, "receipts", "sess", "1.json"))
        ok, findings = self._verify()
        self.assertFalse(ok)
        # A gap at index 1: sequence-broken (0,2 present, n=3).
        self.assertTrue(any(f["status"] in ("sequence-broken", "chain-broken") for f in findings))

    def test_chain_broken_with_valid_hmacs(self):
        # A receipt individually valid (correct HMAC, correctly filed) but whose
        # prevHmac points at the wrong predecessor must be caught as chain-broken
        # -- not merely hmac-mismatch. Build receipt 1 by hand with a bad
        # prevHmac and re-sign it with the real key, so it passes every
        # per-receipt check and only the chain link is wrong.
        self._stamp(0)
        core = {
            "receiptVersion": "1", "sessionId": "sess", "callIndex": 1,
            "prevHmac": "deadbeef" * 8,  # a wrong predecessor, not receipt 0's hmac
            "tool": "t", "argumentsDigest": self.store.keyed_digest("args", attest.canon({})),
            "resultDigest": self.store.retain(attest.canon({"v": 1})),
            "isError": False, "servedAt": "2026-07-30T00:00:00Z",
            "authority": "test:authority", "downstream": {"command": ["x"], "serverInfo": None},
        }
        self.store.stamp(core)  # correctly signs and files it at sess/1.json
        ok, findings = self._verify()
        self.assertFalse(ok)
        statuses = [f["status"] for f in findings]
        self.assertNotIn("hmac-mismatch", statuses)  # every receipt is individually valid
        self.assertIn("chain-broken", statuses)

    def test_malformed_receipt_files_do_not_crash_verify(self):
        self._stamp(0)
        for bad in (b"0", b"[]", b'{"no":"hmac"}', b"not json at all", b'{"hmac":123}',
                    b'{"hmac":"x","callIndex":true,"sessionId":"sess"}'):
            path = os.path.join(self.dir, "receipts", "sess", "9.json")
            with open(path, "wb") as handle:
                handle.write(bad)
            ok, findings = self._verify()  # must not raise
            self.assertFalse(ok)
            self.assertTrue(any(f["status"] == "malformed" for f in findings))
            os.remove(path)

    def test_verify_rejects_duplicate_key_receipt(self):
        # A receipt file with a duplicate member name is ambiguous under
        # first-vs-last-wins; verify must call it malformed, not silently
        # recover the signed form via last-wins.
        self._stamp(0)
        path = os.path.join(self.dir, "receipts", "sess", "0.json")
        with open(path, "rb") as handle:
            body = handle.read().decode()
        # Inject a duplicate "tool" member ahead of the original.
        doubled = body.replace('"tool":', '"tool":"x","tool":', 1)
        with open(path, "wb") as handle:
            handle.write(doubled.encode())
        ok, findings = self._verify()  # must not silently accept
        self.assertFalse(ok)
        self.assertTrue(any(f["status"] == "malformed" for f in findings))

    def test_path_traversal_digest_is_malformed_not_read(self):
        # A receipt whose resultDigest is a path, correctly signed, must be
        # rejected as malformed BEFORE any filesystem read -- never allowed to
        # escape the artifacts directory (e.g. sha256:/dev/zero).
        core = {
            "receiptVersion": "1", "sessionId": "sess", "callIndex": 0, "prevHmac": None,
            "tool": "t", "argumentsDigest": self.store.keyed_digest("args", attest.canon({})),
            "resultDigest": "sha256:/dev/zero", "isError": False,
            "servedAt": "2026-07-30T00:00:00Z", "authority": "test:authority",
            "downstream": {"command": ["x"], "serverInfo": None},
        }
        # Sign it with the real key so it is not merely an hmac-mismatch.
        session_dir = os.path.join(self.dir, "receipts", "sess")
        os.makedirs(session_dir, exist_ok=True)
        import hashlib as _h, hmac as _hm
        mac = _hm.new(KEY, attest.canon(core), _h.sha256).hexdigest()
        stored = dict(core, hmac=mac)
        with open(os.path.join(session_dir, "0.json"), "wb") as handle:
            handle.write(attest.canon(stored) + b"\n")
        ok, findings = self._verify()
        self.assertFalse(ok)
        self.assertEqual(findings[0]["status"], "malformed")

    def test_huge_callindex_does_not_allocate(self):
        # A signed receipt with an enormous safe-range callIndex must not make
        # the chain check allocate range(callIndex); it is simply sequence-broken.
        core = {
            "receiptVersion": "1", "sessionId": "sess", "callIndex": (1 << 52), "prevHmac": None,
            "tool": "t", "argumentsDigest": self.store.keyed_digest("args", attest.canon({})),
            "resultDigest": self.store.retain(attest.canon({"v": 0})),
            "isError": False, "servedAt": "2026-07-30T00:00:00Z", "authority": "test:authority",
            "downstream": {"command": ["x"], "serverInfo": None},
        }
        session_dir = os.path.join(self.dir, "receipts", "sess")
        os.makedirs(session_dir, exist_ok=True)
        import hashlib as _h, hmac as _hm
        mac = _hm.new(KEY, attest.canon(core), _h.sha256).hexdigest()
        stored = dict(core, hmac=mac)
        with open(os.path.join(session_dir, "%d.json" % (1 << 52)), "wb") as handle:
            handle.write(attest.canon(stored) + b"\n")
        ok, findings = self._verify()  # must return quickly, not OOM
        self.assertFalse(ok)
        self.assertTrue(any(f["status"] == "sequence-broken" for f in findings))

    def test_authority_enforced_when_requested(self):
        self._stamp(0)
        ok, _ = self._verify(expected_authority="test:authority")
        self.assertTrue(ok)
        ok, findings = self._verify(expected_authority="someone-else")
        self.assertFalse(ok)
        self.assertTrue(any(f["status"] == "authority-mismatch" for f in findings))


# A stub MCP server. Modes: normal (fixed result), error (JSON-RPC error to a
# tools/call), apperror (result.isError true), batch (emits a JSON-RPC batch).
STUB = r"""
import json, sys
mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    msg = json.loads(line)
    mid = msg.get("id")
    method = msg.get("method")
    if method == "initialize":
        out = {"jsonrpc":"2.0","id":mid,"result":{"protocolVersion":"2025-06-18","serverInfo":{"name":"stub","version":"9"},"capabilities":{}}}
    elif method == "tools/call":
        if mode == "error":
            out = {"jsonrpc":"2.0","id":mid,"error":{"code":-32000,"message":"boom"}}
        elif mode == "apperror":
            out = {"jsonrpc":"2.0","id":mid,"result":{"content":[{"type":"text","text":"nope"}],"isError":True}}
        else:
            name = (msg.get("params") or {}).get("name")
            out = {"jsonrpc":"2.0","id":mid,"result":{"content":[{"type":"text","text":"result-of-"+str(name)}],"isError":False}}
    elif mid is not None:
        out = {"jsonrpc":"2.0","id":mid,"result":{}}
    else:
        continue
    if mode == "idcollide" and method == "tools/call":
        # A server->client REQUEST reusing the tools/call id (ids are
        # direction-scoped). It must NOT consume the pending tool call.
        sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":mid,"method":"sampling/createMessage","params":{}})+"\n")
        sys.stdout.flush()
    if mode == "batch" and method == "tools/call":
        sys.stdout.write(json.dumps([out])+"\n")  # a one-element JSON-RPC batch
    else:
        sys.stdout.write(json.dumps(out)+"\n")
    sys.stdout.flush()
"""


class Driver:
    def __init__(self, tmp):
        self.tmp = tmp
        self.key_path = os.path.join(tmp, "key")
        with open(self.key_path, "wb") as handle:
            handle.write(b"integration-key-of-thirty-two-by")
        self.store_dir = os.path.join(tmp, "store")
        self.stub_path = os.path.join(tmp, "stub.py")
        with open(self.stub_path, "w") as handle:
            handle.write(STUB)

    def run(self, client_lines, mode="normal"):
        proc = subprocess.Popen(
            [sys.executable, os.path.join(HERE, "attest.py"), "wrap", self.store_dir,
             self.key_path, "--"] + [sys.executable, self.stub_path, mode],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        payload = b"".join(line.encode() + b"\n" for line in client_lines)
        out, err = proc.communicate(payload, timeout=30)
        return proc.returncode, out, err

    def verify(self):
        return attest.verify(self.store_dir, b"integration-key-of-thirty-two-by")


def _call(idx, name, args):
    return json.dumps({"jsonrpc": "2.0", "id": idx, "method": "tools/call",
                       "params": {"name": name, "arguments": args}})


INIT = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
INITED = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})


class ProxyBehavior(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.d = Driver(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_result_forwarded_raw_bytes_and_attested(self):
        code, out, err = self.d.run([INIT, INITED, _call(2, "screen", {"q": "acme"})])
        self.assertEqual(code, 0, err)
        # The exact result line the stub emitted must appear byte-for-byte in
        # what the client received -- not merely a re-parse of it.
        expected_line = json.dumps(
            {"jsonrpc": "2.0", "id": 2,
             "result": {"content": [{"type": "text", "text": "result-of-screen"}], "isError": False}}
        ).encode() + b"\n"
        self.assertIn(expected_line, out)
        ok, findings = self.d.verify()
        self.assertTrue(ok, findings)
        self.assertEqual(len([f for f in findings if f["status"] == "ok"]), 1)
        sess = os.listdir(os.path.join(self.d.store_dir, "receipts"))[0]
        with open(os.path.join(self.d.store_dir, "receipts", sess, "0.json"), "rb") as handle:
            receipt = json.loads(handle.read())
        self.assertEqual(receipt["tool"], "screen")
        self.assertEqual(receipt["downstream"]["serverInfo"], {"name": "stub", "version": "9"})
        self.assertEqual(receipt["prevHmac"], None)
        # arguments are keyed-digested, not stored: no plaintext leak.
        self.assertTrue(receipt["argumentsDigest"].startswith("hmac-sha256:"))
        self.assertNotIn("acme", json.dumps(receipt))

    def test_two_calls_chain(self):
        code, out, err = self.d.run(
            [INIT, INITED, _call(2, "a", {}), _call(3, "b", {})])
        self.assertEqual(code, 0, err)
        ok, findings = self.d.verify()
        self.assertTrue(ok, findings)
        self.assertEqual(len([f for f in findings if f["status"] == "ok"]), 2)

    def test_jsonrpc_error_response_is_not_attested(self):
        code, out, err = self.d.run([INIT, INITED, _call(2, "x", {})], mode="error")
        self.assertEqual(code, 0, err)
        # The error response was forwarded, but nothing was attested.
        self.assertIn(b'"error"', out)
        receipts_root = os.path.join(self.d.store_dir, "receipts")
        stamped = sum(len(os.listdir(os.path.join(receipts_root, s)))
                      for s in os.listdir(receipts_root)) if os.path.isdir(receipts_root) else 0
        self.assertEqual(stamped, 0)

    def test_app_error_result_is_attested(self):
        code, out, err = self.d.run([INIT, INITED, _call(2, "x", {})], mode="apperror")
        self.assertEqual(code, 0, err)
        ok, findings = self.d.verify()
        self.assertTrue(ok, findings)
        sess = os.listdir(os.path.join(self.d.store_dir, "receipts"))[0]
        with open(os.path.join(self.d.store_dir, "receipts", sess, "0.json"), "rb") as handle:
            receipt = json.loads(handle.read())
        self.assertTrue(receipt["isError"])

    def _receipt_count(self):
        receipts_root = os.path.join(self.d.store_dir, "receipts")
        if not os.path.isdir(receipts_root):
            return 0
        return sum(len(os.listdir(os.path.join(receipts_root, s)))
                   for s in os.listdir(receipts_root))

    def test_batch_fails_closed_and_is_not_forwarded(self):
        code, out, err = self.d.run([INIT, INITED, _call(2, "x", {})], mode="batch")
        # The batch (a downstream->client array) must fail the run closed...
        self.assertEqual(code, 1, err)
        # ...and must NOT be forwarded to the client, nor leave a receipt.
        self.assertNotIn(b"result-of-x", out)
        self.assertEqual(self._receipt_count(), 0)

    def test_server_request_reusing_id_does_not_steal_the_tool_call(self):
        # A downstream server->client request reusing the tools/call id must not
        # consume the pending call; the real result must still be attested.
        code, out, err = self.d.run([INIT, INITED, _call(2, "screen", {})], mode="idcollide")
        self.assertEqual(code, 0, err)
        self.assertIn(b"result-of-screen", out)  # the real result was forwarded
        ok, findings = self.d.verify()
        self.assertTrue(ok, findings)
        self.assertEqual(self._receipt_count(), 1)  # and attested

    def test_duplicate_outstanding_id_fails_closed(self):
        # Two tools/call with the same id, before any response, is a protocol
        # violation the proxy cannot attest safely: fail closed.
        code, out, err = self.d.run([INIT, INITED, _call(2, "a", {}), _call(2, "b", {})])
        self.assertEqual(code, 1, err)

    def test_non_tool_request_reusing_outstanding_id_fails_closed(self):
        # A non-tools/call client request reusing an outstanding tools/call id
        # (which could otherwise let a foreign response retire the tool call and
        # slip the real result through unattested) must fail closed.
        other = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "resources/read",
                            "params": {"uri": "x"}})
        code, out, err = self.d.run([INIT, INITED, _call(2, "screen", {}), other])
        self.assertEqual(code, 1, err)

    def test_id_type_confusion_does_not_retire_foreign_call(self):
        # A response with id true must NOT retire a pending tools/call with id 1
        # (Python's True==1). The real id-1 result must still be attested.
        init = json.dumps({"jsonrpc": "2.0", "id": 99, "method": "initialize", "params": {}})
        call = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                           "params": {"name": "screen", "arguments": {}}})
        # A foreign server->client... actually simulate a stray downstream error
        # response with id true arriving before the real result, via a stub mode.
        confuse_stub = os.path.join(self.tmp, "confuse.py")
        with open(confuse_stub, "w") as handle:
            handle.write(
                "import sys, json\n"
                "for line in sys.stdin:\n"
                "    line=line.strip()\n"
                "    if not line: continue\n"
                "    m=json.loads(line); mid=m.get('id'); meth=m.get('method')\n"
                "    if meth=='initialize':\n"
                "        sys.stdout.write(json.dumps({'jsonrpc':'2.0','id':mid,'result':{'serverInfo':{'name':'c','version':'1'}}})+'\\n')\n"
                "    elif meth=='tools/call':\n"
                "        # a stray error with id true, THEN the real result with id 1\n"
                "        sys.stdout.write(json.dumps({'jsonrpc':'2.0','id':True,'error':{'code':-1,'message':'x'}})+'\\n')\n"
                "        sys.stdout.write(json.dumps({'jsonrpc':'2.0','id':mid,'result':{'content':[{'type':'text','text':'real-'+str(m.get('params',{}).get('name'))}],'isError':False}})+'\\n')\n"
                "    sys.stdout.flush()\n"
            )
        proc = subprocess.Popen(
            [sys.executable, os.path.join(HERE, "attest.py"), "wrap", self.d.store_dir,
             self.d.key_path, "--", sys.executable, confuse_stub],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        out, err = proc.communicate("\n".join([init, INITED, call]).encode() + b"\n", timeout=30)
        self.assertIn(b"real-screen", out)
        self.assertEqual(self._receipt_count(), 1, err)  # the real id-1 result attested

    def test_null_method_reusing_id_fails_closed(self):
        # A second client message with method:null reusing an outstanding
        # tools/call id must be duplicate-checked (member presence), not skipped.
        call = _call(2, "screen", {})
        nullmethod = json.dumps({"jsonrpc": "2.0", "id": 2, "method": None, "params": {}})
        code, out, err = self.d.run([INIT, INITED, call, nullmethod])
        self.assertEqual(code, 1, err)

    def test_null_id_tool_call_is_attested_not_bypassed(self):
        # An explicit id:null tools/call and its id:null result must not be
        # conflated with "no id" -- the result must be attested.
        init = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        call = json.dumps({"jsonrpc": "2.0", "id": None, "method": "tools/call",
                           "params": {"name": "screen", "arguments": {}}})
        code, out, err = self.d.run([init, INITED, call])
        self.assertEqual(code, 0, err)
        self.assertIn(b"result-of-screen", out)
        self.assertEqual(self._receipt_count(), 1)  # attested, not bypassed

    def test_downstream_nonzero_exit_fails_the_run(self):
        # A downstream that crashes (nonzero exit) must not let the proxy report
        # success, even though no unattested result was forwarded.
        crash_stub = os.path.join(self.tmp, "crash.py")
        with open(crash_stub, "w") as handle:
            handle.write("import sys, json\n"
                         "for line in sys.stdin:\n"
                         "    line=line.strip()\n"
                         "    if not line: continue\n"
                         "    m=json.loads(line)\n"
                         "    if m.get('method')=='initialize':\n"
                         "        sys.stdout.write('{\"jsonrpc\":\"2.0\",\"id\":%s,\"result\":{}}\\n' % json.dumps(m.get('id'))); sys.stdout.flush()\n"
                         "    sys.exit(7)\n")
        proc = subprocess.Popen(
            [sys.executable, os.path.join(HERE, "attest.py"), "wrap", self.d.store_dir,
             self.d.key_path, "--", sys.executable, crash_stub],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        # Keep the client side open briefly by sending init then closing; the
        # downstream exits 7 after the first message.
        out, err = proc.communicate((INIT + "\n").encode(), timeout=30)
        self.assertEqual(proc.returncode, 1, err)

    def test_duplicate_keys_in_downstream_result_fail_closed(self):
        # A downstream line with a duplicate object member name is ambiguous;
        # attesting one interpretation while forwarding the raw bytes to a
        # differently-parsing client is exactly the divergence to prevent.
        dup_stub = os.path.join(self.tmp, "dupstub.py")
        with open(dup_stub, "w") as handle:
            handle.write(
                "import sys\n"
                "for line in sys.stdin:\n"
                "    line=line.strip()\n"
                "    if not line: continue\n"
                "    import json\n"
                "    m=json.loads(line); mid=m.get('id'); meth=m.get('method')\n"
                "    if meth=='initialize':\n"
                "        sys.stdout.write('{\"jsonrpc\":\"2.0\",\"id\":%s,\"result\":{\"serverInfo\":{\"name\":\"d\",\"version\":\"1\"}}}\\n' % json.dumps(mid))\n"
                "    elif meth=='tools/call':\n"
                "        sys.stdout.write('{\"jsonrpc\":\"2.0\",\"id\":%s,\"result\":{\"x\":1,\"x\":2}}\\n' % json.dumps(mid))\n"
                "    elif mid is not None:\n"
                "        sys.stdout.write('{\"jsonrpc\":\"2.0\",\"id\":%s,\"result\":{}}\\n' % json.dumps(mid))\n"
                "    sys.stdout.flush()\n"
            )
        proc = subprocess.Popen(
            [sys.executable, os.path.join(HERE, "attest.py"), "wrap", self.d.store_dir,
             self.d.key_path, "--", sys.executable, dup_stub],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        payload = "\n".join([INIT, INITED, _call(2, "x", {})]).encode() + b"\n"
        out, err = proc.communicate(payload, timeout=30)
        self.assertEqual(proc.returncode, 1, err)  # failed closed
        self.assertEqual(self._receipt_count(), 0)


class ProxyWithJpackMcp(unittest.TestCase):
    def setUp(self):
        self.jpack = shutil.which("jpack")
        if not self.jpack:
            self.skipTest("no jpack on PATH")
        self.tmp = tempfile.mkdtemp()
        self.key_path = os.path.join(self.tmp, "key")
        with open(self.key_path, "wb") as handle:
            handle.write(b"jpack-integration-key-of-length!")
        self.store_dir = os.path.join(self.tmp, "store")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_attests_describe_runtime(self):
        init = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                           "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                      "clientInfo": {"name": "t", "version": "0"}}})
        proc = subprocess.Popen(
            [sys.executable, os.path.join(HERE, "attest.py"), "wrap", self.store_dir,
             self.key_path, "--", self.jpack, "mcp"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        payload = "\n".join([init, INITED, _call(2, "describe_runtime", {})]).encode() + b"\n"
        out, err = proc.communicate(payload, timeout=30)
        ok, findings = attest.verify(self.store_dir, b"jpack-integration-key-of-length!")
        self.assertTrue(ok, (findings, err))
        self.assertTrue(any(f["status"] == "ok" for f in findings))
        sess = os.listdir(os.path.join(self.store_dir, "receipts"))[0]
        with open(os.path.join(self.store_dir, "receipts", sess, "0.json"), "rb") as handle:
            receipt = json.loads(handle.read())
        self.assertEqual(receipt["tool"], "describe_runtime")
        self.assertIsNotNone(receipt["downstream"]["serverInfo"])


if __name__ == "__main__":
    unittest.main()
