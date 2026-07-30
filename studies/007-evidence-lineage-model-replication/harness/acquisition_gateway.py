#!/usr/bin/env python3
"""Synthetic MCP acquisition gateway with content-addressed artifacts and receipts."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

try:
    from harness.common import (
        append_fsynced,
        attest,
        canonical,
        digest,
        load_json,
        pretty,
        write_fsynced,
    )
except ModuleNotFoundError:
    from common import (
        append_fsynced,
        attest,
        canonical,
        digest,
        load_json,
        pretty,
        write_fsynced,
    )


PROTOCOL_VERSION = "2025-06-18"
RETRIEVED_AT = "2026-07-30T15:00:00Z"


def load_scenario(path: Path, scenario_id: str) -> Dict[str, Any]:
    document = load_json(path)
    matches = [item for item in document["scenarios"] if item["id"] == scenario_id]
    if len(matches) != 1:
        raise ValueError("scenario %r resolved %d times" % (scenario_id, len(matches)))
    return matches[0]


class Gateway:
    def __init__(
        self,
        cases_path: Path,
        binding_path: Path,
        key_path: Path,
        scenario_id: str,
        repetition: int,
        cell_id: str,
        store_path: Path,
    ) -> None:
        self.scenario = load_scenario(cases_path, scenario_id)
        self.binding = load_json(binding_path)
        self.key = key_path.read_bytes().strip()
        self.repetition = repetition
        self.cell_id = cell_id
        self.store_path = store_path
        self.call_index = 0

    def list_tools(self):
        return [
            {
                "name": "acquire_screening",
                "description": (
                    "Approved read-only acquisition for semantic source "
                    "%s. Returns a structured synthetic screening payload plus "
                    "gateway-issued content and receipt digests."
                    % self.binding["sourceRef"]
                ),
                "inputSchema": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["legal_name"],
                    "properties": {
                        "legal_name": {
                            "type": "string",
                            "description": "Exact legal-entity name.",
                        }
                    },
                },
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "openWorldHint": False,
                },
            }
        ]

    def issue(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        self.call_index += 1
        payload = self.scenario["payload"]
        artifact_digest = digest(payload)
        artifact_path = (
            self.store_path
            / "artifacts"
            / (artifact_digest.split(":", 1)[1] + ".json")
        )
        write_fsynced(artifact_path, pretty(payload))
        body = {
            "receiptVersion": "1",
            "cellId": self.cell_id,
            "callIndex": self.call_index,
            "repetition": self.repetition,
            "sourceRef": self.binding["sourceRef"],
            "bindingDigest": digest(self.binding),
            "server": self.binding["binding"]["server"],
            "tool": self.binding["binding"]["tool"],
            "sideEffect": "read",
            "arguments": arguments,
            "subject": arguments["legal_name"],
            "retrievedAt": RETRIEVED_AT,
            "artifactDigest": artifact_digest,
        }
        receipt = dict(body)
        receipt["attestation"] = attest(body, self.key)
        receipt_digest = digest(receipt)
        receipt_path = (
            self.store_path
            / "receipts"
            / (receipt_digest.split(":", 1)[1] + ".json")
        )
        write_fsynced(receipt_path, pretty(receipt))
        append_fsynced(
            self.store_path / "receipt.jsonl",
            canonical({**receipt, "receiptDigest": receipt_digest}) + "\n",
        )
        return {
            "payload": payload,
            "provenance": {
                "sourceRef": self.binding["sourceRef"],
                "bindingDigest": digest(self.binding),
                "artifactDigest": artifact_digest,
                "receiptDigest": receipt_digest,
                "retrievedAt": RETRIEVED_AT,
            },
        }

    def call_tool(self, name: str, arguments: Any) -> Dict[str, Any]:
        if name != "acquire_screening":
            return {
                "content": [{"type": "text", "text": "Unknown acquisition tool."}],
                "isError": True,
            }
        if (
            not isinstance(arguments, dict)
            or set(arguments) != {"legal_name"}
            or not isinstance(arguments["legal_name"], str)
        ):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": 'Arguments must be exactly {"legal_name": <string>}.',
                    }
                ],
                "isError": True,
            }
        result = self.issue(arguments)
        return {
            "content": [{"type": "text", "text": canonical(result)}],
            "structuredContent": result,
            "isError": False,
        }

    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        request_id = request.get("id")
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "study-006-acquisition-gateway",
                        "version": "1",
                    },
                },
            }
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": self.list_tools()},
            }
        if method == "tools/call":
            params = request.get("params")
            if not isinstance(params, dict):
                params = {}
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": self.call_tool(
                    str(params.get("name", "")), params.get("arguments")
                ),
            }
        if method == "ping":
            return {"jsonrpc": "2.0", "id": request_id, "result": {}}
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--binding", required=True, type=Path)
    parser.add_argument("--key", required=True, type=Path)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--repetition", required=True, type=int)
    parser.add_argument("--cell", required=True)
    parser.add_argument("--store", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    gateway = Gateway(
        args.cases,
        args.binding,
        args.key,
        args.scenario,
        args.repetition,
        args.cell,
        args.store,
    )
    for raw_line in sys.stdin:
        try:
            request = json.loads(raw_line)
            if not isinstance(request, dict) or "id" not in request:
                continue
            response = gateway.handle(request)
        except Exception as exc:  # pragma: no cover - defensive wire boundary
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(exc)},
            }
        sys.stdout.write(canonical(response) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
