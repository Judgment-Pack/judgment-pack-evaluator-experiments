#!/usr/bin/env python3
"""Case-bound synthetic stdio MCP server for Study 005.

The server owns no network capability. It exposes only the tools declared by one
frozen fixture and appends a receipt before returning each fixture result.
"""

import argparse
import hashlib
import json
import os
import sys
from typing import Any, Dict, List


PROTOCOL_VERSION = "2025-06-18"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def load_scenario(path: str, scenario_id: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        document = json.load(handle)
    matches = [item for item in document["scenarios"] if item["id"] == scenario_id]
    if len(matches) != 1:
        raise ValueError("scenario %r resolved %d times" % (scenario_id, len(matches)))
    return matches[0]


def rotate(tools: List[Dict[str, Any]], repetition: int) -> List[Dict[str, Any]]:
    if repetition == 0:
        return list(tools)
    if repetition == 1:
        return list(tools[1:] + tools[:1])
    if repetition == 2:
        return list(tools[-1:] + tools[:-1])
    raise ValueError("repetition must be 0, 1, or 2")


def tool_description(tool: Dict[str, Any]) -> str:
    lines = [tool["description"]]
    for source_id in tool["provides"]:
        lines.append("Provides semantic input source identifier: %s" % source_id)
    if not tool["provides"]:
        lines.append("Provides no semantic input source identifier for this study.")
    if tool["sideEffect"] == "read":
        lines.append("Side-effect class: read-only.")
    else:
        lines.append("Side-effect class: mutating write.")
    return "\n".join(lines)


class Server:
    def __init__(
        self,
        cases_path: str,
        scenario_id: str,
        repetition: int,
        cell_id: str,
        receipt_path: str,
    ) -> None:
        self.scenario = load_scenario(cases_path, scenario_id)
        ordered = rotate(self.scenario["tools"], repetition)
        self.by_name: Dict[str, Dict[str, Any]] = {}
        for index, tool in enumerate(ordered):
            self.by_name["source_%s" % chr(ord("a") + index)] = tool
        self.cell_id = cell_id
        self.receipt_path = receipt_path
        self.call_index = 0

    def list_tools(self) -> List[Dict[str, Any]]:
        output = []
        for name, tool in self.by_name.items():
            read_only = tool["sideEffect"] == "read"
            output.append(
                {
                    "name": name,
                    "description": tool_description(tool),
                    "inputSchema": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["legal_name"],
                        "properties": {
                            "legal_name": {
                                "type": "string",
                                "description": "The exact legal-entity name to look up.",
                            }
                        },
                    },
                    "annotations": {
                        "readOnlyHint": read_only,
                        "destructiveHint": not read_only,
                        "idempotentHint": read_only,
                        "openWorldHint": False,
                    },
                }
            )
        return output

    def append_receipt(
        self, name: str, tool: Dict[str, Any], arguments: Dict[str, Any]
    ) -> None:
        self.call_index += 1
        row = {
            "cellId": self.cell_id,
            "callIndex": self.call_index,
            "toolName": name,
            "toolKey": tool["key"],
            "provides": tool["provides"],
            "arguments": arguments,
            "sideEffect": tool["sideEffect"],
            "resultSha256": digest(tool["result"]),
        }
        os.makedirs(os.path.dirname(os.path.abspath(self.receipt_path)), exist_ok=True)
        with open(self.receipt_path, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical(row) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def call_tool(self, name: str, arguments: Any) -> Dict[str, Any]:
        tool = self.by_name.get(name)
        if tool is None:
            return {
                "content": [{"type": "text", "text": "Unknown synthetic tool."}],
                "isError": True,
            }
        if not isinstance(arguments, dict) or set(arguments) != {"legal_name"}:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": 'Arguments must be exactly {"legal_name": <string>}.',
                    }
                ],
                "isError": True,
            }
        if not isinstance(arguments["legal_name"], str):
            return {
                "content": [{"type": "text", "text": "legal_name must be a string."}],
                "isError": True,
            }
        self.append_receipt(name, tool, arguments)
        result_text = canonical(tool["result"])
        return {
            "content": [{"type": "text", "text": result_text}],
            "structuredContent": tool["result"],
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
                        "name": "study-005-source-harness",
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
    parser.add_argument("--cases", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--repetition", required=True, type=int)
    parser.add_argument("--cell", required=True)
    parser.add_argument("--receipt", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    server = Server(
        args.cases, args.scenario, args.repetition, args.cell, args.receipt
    )
    for raw_line in sys.stdin:
        try:
            request = json.loads(raw_line)
            if not isinstance(request, dict):
                continue
            if "id" not in request:
                continue
            response = server.handle(request)
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
