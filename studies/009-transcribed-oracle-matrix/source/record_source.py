#!/usr/bin/env python3
"""The record-source MCP stdio server: one frozen record per tools/call.

Deterministic and dumb on purpose. It reads records from RECORDS_DIR, serves
the record named by arguments.caseId as the tools/call result verbatim, and
knows nothing about packs, policies, or outcomes. Everything it emits is in
the canon domain because the frozen records are.
"""
from __future__ import annotations
import json
import os
import sys


def main() -> None:
    records_dir = os.environ["RECORDS_DIR"]
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        message = json.loads(line)
        if "id" not in message:
            continue  # a notification needs no reply
        if message.get("method") == "initialize":
            reply = {"jsonrpc": "2.0", "id": message["id"], "result": {
                "protocolVersion": "2025-06-18",
                "serverInfo": {"name": "study-009-record-source", "version": "1"},
                "capabilities": {"tools": {}},
            }}
        elif message.get("method") == "tools/call":
            case_id = (message.get("params") or {}).get("arguments", {}).get("caseId", "")
            path = os.path.join(records_dir, case_id + ".json")
            if not case_id or "/" in case_id or not os.path.exists(path):
                reply = {"jsonrpc": "2.0", "id": message["id"],
                         "error": {"code": -32602, "message": "unknown caseId"}}
            else:
                with open(path) as handle:
                    reply = {"jsonrpc": "2.0", "id": message["id"], "result": json.load(handle)}
        else:
            reply = {"jsonrpc": "2.0", "id": message["id"], "result": {}}
        sys.stdout.write(json.dumps(reply, separators=(",", ":")) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
