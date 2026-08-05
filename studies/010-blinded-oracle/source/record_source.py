#!/usr/bin/env python3
"""The record-source MCP stdio server: one frozen record per tools/call.

Deterministic and dumb on purpose. It reads records from the directories in
RECORDS_DIRS (os.pathsep-separated, searched in order — Study 010 lists the
authored records directory and then the locked controls directory), serves
the record named by arguments.caseId as the tools/call result verbatim, and
knows nothing about packs, policies, or outcomes. Everything it emits is in
the canon domain because the frozen records are.
"""
from __future__ import annotations
import json
import os
import sys


def find(dirs: list, case_id: str) -> str:
    for base in dirs:
        path = os.path.join(base, case_id + ".json")
        if os.path.exists(path):
            return path
    return ""


def main() -> None:
    dirs = os.environ["RECORDS_DIRS"].split(os.pathsep)
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
                "serverInfo": {"name": "study-010-record-source", "version": "1"},
                "capabilities": {"tools": {}},
            }}
        elif message.get("method") == "tools/call":
            case_id = (message.get("params") or {}).get("arguments", {}).get("caseId", "")
            path = find(dirs, case_id) if case_id and "/" not in case_id else ""
            if not path:
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
