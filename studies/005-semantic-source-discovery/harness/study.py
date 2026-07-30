#!/usr/bin/env python3
"""Prepare, run, and score Study 005.

The fixture validator and scorer use only the Python standard library. Model
execution is delegated to the preregistered Codex CLI, one fresh process per
cell.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    from harness.synthetic_mcp import Server, digest, rotate, tool_description
except ModuleNotFoundError:  # Direct execution from the study directory.
    from synthetic_mcp import Server, digest, rotate, tool_description


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "fixtures" / "cases.json"
PROMPT_PATH = ROOT / "fixtures" / "PROMPT.txt"
SOURCE_SCHEMA_PATH = ROOT / "schema" / "source-reference.schema.json"
CASES_SCHEMA_PATH = ROOT / "schema" / "cases.schema.json"
RESPONSE_SCHEMA_PATH = ROOT / "schema" / "response.schema.json"
TRIALS_PATH = ROOT / "trials"
MODEL = "gpt-5.6-terra"
REASONING_EFFORT = "low"
RUNNER_VERSION = "1"
FROZEN_PREREG_COMMIT = "519fdba"
SOURCE_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)+$")
EXPECTED_SCENARIOS = ["S%02d" % value for value in range(1, 9)]
ARMS = ("P", "S")
REPETITIONS = (0, 1, 2)


class ValidationError(ValueError):
    """Raised when a frozen study artifact is mechanically invalid."""


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def study_cases() -> Dict[str, Any]:
    return load_json(CASES_PATH)


def scenario_map(document: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {scenario["id"]: scenario for scenario in document["scenarios"]}


def source_guidance(scenario: Dict[str, Any], arm: str) -> Dict[str, Any]:
    if arm == "P":
        return {
            "source": scenario["source"]["description"],
            "hint": scenario["hint"],
        }
    if arm == "S":
        return {
            "source": dict(scenario["source"]),
            "sourceRef": scenario["source"]["id"],
            "hint": scenario["hint"],
        }
    raise ValidationError("unknown arm %r" % arm)


def arm_order(scenario_id: str) -> Tuple[str, str]:
    number = int(scenario_id[1:])
    return ("P", "S") if number % 2 == 1 else ("S", "P")


def trial_order() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for repetition in REPETITIONS:
        for scenario_id in EXPECTED_SCENARIOS:
            for arm in arm_order(scenario_id):
                rows.append(
                    {
                        "cellId": "r%02d-%s-%s"
                        % (repetition + 1, scenario_id.lower(), arm.lower()),
                        "repetition": repetition,
                        "scenarioId": scenario_id,
                        "arm": arm,
                    }
                )
    return rows


def opaque_catalog(
    scenario: Dict[str, Any], repetition: int
) -> List[Dict[str, Any]]:
    rows = []
    for index, tool in enumerate(rotate(scenario["tools"], repetition)):
        rows.append(
            {
                "name": "source_%s" % chr(ord("a") + index),
                "toolKey": tool["key"],
                "description": tool_description(tool),
                "sideEffect": tool["sideEffect"],
                "provides": list(tool["provides"]),
                "resultSha256": digest(tool["result"]),
            }
        )
    return rows


def render_prompt(document: Dict[str, Any], scenario: Dict[str, Any], arm: str) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    if template.count("{{REQUEST}}") != 1 or template.count("{{SOURCE_GUIDANCE}}") != 1:
        raise ValidationError("prompt placeholders must occur exactly once")
    return template.replace(
        "{{REQUEST}}", pretty(document["request"]).rstrip()
    ).replace(
        "{{SOURCE_GUIDANCE}}", pretty(source_guidance(scenario, arm)).rstrip()
    )


def validate_response(value: Any) -> List[str]:
    errors: List[str] = []
    required = {
        "facts",
        "evidenceAvailability",
        "acquisitionStatus",
        "sourceId",
        "explanation",
    }
    if not isinstance(value, dict):
        return ["response is not an object"]
    if set(value) != required:
        errors.append(
            "response members differ: expected %s, got %s"
            % (sorted(required), sorted(value))
        )
    if not isinstance(value.get("facts"), dict):
        errors.append("facts is not an object")
    evidence = value.get("evidenceAvailability")
    if not isinstance(evidence, dict):
        errors.append("evidenceAvailability is not an object")
    elif any(item not in {"present", "absent", "unknown"} for item in evidence.values()):
        errors.append("evidenceAvailability contains an invalid value")
    if value.get("acquisitionStatus") not in {
        "resolved",
        "absent",
        "unknown",
        "ambiguous",
    }:
        errors.append("acquisitionStatus is invalid")
    if value.get("sourceId") is not None and not isinstance(value.get("sourceId"), str):
        errors.append("sourceId is not a string or null")
    if not isinstance(value.get("explanation"), str):
        errors.append("explanation is not a string")
    return errors


def validate_fixtures() -> List[str]:
    errors: List[str] = []
    document = study_cases()
    if set(document) != {"studyVersion", "request", "scenarios"}:
        errors.append("case document has unexpected members")
    if document.get("studyVersion") != "1":
        errors.append("studyVersion must be 1")
    request = document.get("request")
    if not isinstance(request, dict) or set(request) != {"legalName"}:
        errors.append("request must contain only legalName")
    elif request["legalName"] != "Northwind Analytics Ltd":
        errors.append("request legalName differs from preregistration")

    scenarios = document.get("scenarios")
    if not isinstance(scenarios, list):
        raise ValidationError("scenarios must be an array")
    ids = [item.get("id") for item in scenarios if isinstance(item, dict)]
    if ids != EXPECTED_SCENARIOS:
        errors.append("scenario ids/order must be S01 through S08")

    seen_source_ids = set()
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            errors.append("scenario is not an object")
            continue
        scenario_id = str(scenario.get("id", "?"))
        expected_members = {
            "id",
            "title",
            "source",
            "hint",
            "factPointer",
            "evidenceRequirement",
            "tools",
            "expected",
        }
        if set(scenario) != expected_members:
            errors.append("%s has unexpected members" % scenario_id)
        source = scenario.get("source")
        if not isinstance(source, dict) or set(source) != {"id", "description"}:
            errors.append("%s source shape is invalid" % scenario_id)
            continue
        source_id = source.get("id")
        description = source.get("description")
        if (
            not isinstance(source_id, str)
            or len(source_id) > 256
            or not SOURCE_ID_RE.fullmatch(source_id)
        ):
            errors.append("%s source id is invalid" % scenario_id)
        else:
            seen_source_ids.add(source_id)
        if not isinstance(description, str) or not description or len(description) > 2048:
            errors.append("%s source description is invalid" % scenario_id)
        descriptor = source_guidance(scenario, "S")
        if descriptor["sourceRef"] != source_id:
            errors.append("%s sourceRef does not resolve exactly" % scenario_id)
        if set(descriptor) != {"source", "sourceRef", "hint"}:
            errors.append("%s treatment descriptor is not closed" % scenario_id)
        if source_guidance(scenario, "P")["source"] != description:
            errors.append("%s prose differs between arms" % scenario_id)
        if source_guidance(scenario, "P")["hint"] != descriptor["hint"]:
            errors.append("%s hint differs between arms" % scenario_id)
        if scenario.get("factPointer") != "/screening/matchCount":
            errors.append("%s fact pointer changed" % scenario_id)
        if scenario.get("evidenceRequirement") != "screening-record":
            errors.append("%s evidence requirement changed" % scenario_id)

        tools = scenario.get("tools")
        if not isinstance(tools, list) or len(tools) not in {2, 3}:
            errors.append("%s must have two or three tools" % scenario_id)
            continue
        keys = [tool.get("key") for tool in tools if isinstance(tool, dict)]
        if len(keys) != len(set(keys)):
            errors.append("%s tool keys are not unique" % scenario_id)
        for tool in tools:
            if not isinstance(tool, dict):
                errors.append("%s contains a non-object tool" % scenario_id)
                continue
            if set(tool) != {
                "key",
                "description",
                "provides",
                "sideEffect",
                "result",
            }:
                errors.append("%s tool %r is not closed" % (scenario_id, tool.get("key")))
            if tool.get("sideEffect") not in {"read", "write"}:
                errors.append("%s tool %r has invalid side effect" % (scenario_id, tool.get("key")))
            provides = tool.get("provides")
            if not isinstance(provides, list) or len(provides) != len(set(provides)):
                errors.append("%s tool %r has invalid provides" % (scenario_id, tool.get("key")))
        expected = scenario.get("expected")
        if not isinstance(expected, dict) or set(expected) != {
            "toolKeys",
            "facts",
            "evidenceAvailability",
            "acquisitionStatus",
        }:
            errors.append("%s expected output shape is invalid" % scenario_id)
            continue
        expected_keys = expected.get("toolKeys")
        if not isinstance(expected_keys, list) or len(expected_keys) > 1:
            errors.append("%s expected tool sequence is invalid" % scenario_id)
        elif any(key not in keys for key in expected_keys):
            errors.append("%s expected tool is missing from catalog" % scenario_id)
        expected_response = {
            "facts": expected.get("facts"),
            "evidenceAvailability": expected.get("evidenceAvailability"),
            "acquisitionStatus": expected.get("acquisitionStatus"),
            "sourceId": source_id
            if expected.get("acquisitionStatus") == "resolved"
            else None,
            "explanation": "",
        }
        for message in validate_response(expected_response):
            errors.append("%s expected response: %s" % (scenario_id, message))

        rotations = [
            [row["toolKey"] for row in opaque_catalog(scenario, repetition)]
            for repetition in REPETITIONS
        ]
        expected_rotations = [
            keys,
            keys[1:] + keys[:1],
            keys[-1:] + keys[:-1],
        ]
        if rotations != expected_rotations:
            errors.append("%s rotations differ from preregistration" % scenario_id)
        for repetition in REPETITIONS:
            names = [row["name"] for row in opaque_catalog(scenario, repetition)]
            if names != ["source_%s" % chr(ord("a") + value) for value in range(len(keys))]:
                errors.append("%s tool names are not opaque and sequential" % scenario_id)

    if len(trial_order()) != 48:
        errors.append("trial order does not contain exactly 48 cells")
    if len({row["cellId"] for row in trial_order()}) != 48:
        errors.append("trial ids are not unique")
    for scenario in scenarios:
        for arm in ARMS:
            render_prompt(document, scenario, arm)

    # If jsonschema is available, also exercise the checked-in schemas exactly.
    try:
        import jsonschema  # type: ignore
    except ImportError:
        jsonschema = None
    if jsonschema is not None:
        try:
            jsonschema.Draft202012Validator(
                load_json(CASES_SCHEMA_PATH)
            ).validate(document)
            source_validator = jsonschema.Draft202012Validator(
                load_json(SOURCE_SCHEMA_PATH)
            )
            for scenario in scenarios:
                source_validator.validate(source_guidance(scenario, "S"))
        except Exception as exc:
            errors.append("JSON Schema validation failed: %s" % exc)
    return errors


def git_output(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=str(repository),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def command_output(command: Sequence[str]) -> str:
    completed = subprocess.run(
        list(command),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return completed.stdout.strip()


def prepare() -> None:
    errors = validate_fixtures()
    if errors:
        raise ValidationError("\n".join(errors))
    repo_root = Path(git_output(ROOT, "rev-parse", "--show-toplevel"))
    parent = repo_root.parent
    repositories = [
        ("experiment", repo_root),
        ("spec", parent / "judgment-pack-spec"),
        ("runtime", parent / "judgment-pack-runtime"),
        ("demo", parent / "judgment-pack-demo"),
    ]
    artifacts = [
        ROOT / "PREREGISTRATION.md",
        CASES_PATH,
        PROMPT_PATH,
        SOURCE_SCHEMA_PATH,
        CASES_SCHEMA_PATH,
        RESPONSE_SCHEMA_PATH,
        ROOT / "harness" / "synthetic_mcp.py",
        Path(__file__).resolve(),
    ]
    lines = [
        "# Run log — Study 005",
        "",
        "Generated by the deterministic preflight before the first model cell.",
        "",
        "## Frozen registration",
        "",
        "- preregistration commit: `%s`" % FROZEN_PREREG_COMMIT,
        "- runner version: `%s`" % RUNNER_VERSION,
        "- model: `%s`" % MODEL,
        "- reasoning effort: `%s`" % REASONING_EFFORT,
        "- client: `%s`" % command_output(["codex", "--version"]),
        "- Python: `%s`" % sys.version.replace("\n", " "),
        "",
        "## Repository baselines",
        "",
    ]
    for label, path in repositories:
        lines.append("- %s: `%s`" % (label, git_output(path, "rev-parse", "HEAD")))
    lines.extend(["", "## Artifact SHA-256", ""])
    for artifact in artifacts:
        lines.append(
            "- `%s`: `%s`" % (artifact.relative_to(ROOT), sha256_file(artifact))
        )
    lines.extend(
        [
            "",
            "## Fixed trial order",
            "",
            "| # | cell | repetition | scenario | arm |",
            "|---:|---|---:|---|---|",
        ]
    )
    for index, row in enumerate(trial_order(), start=1):
        lines.append(
            "| %d | `%s` | %d | %s | %s |"
            % (
                index,
                row["cellId"],
                row["repetition"] + 1,
                row["scenarioId"],
                row["arm"],
            )
        )
    (ROOT / "RUN-LOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("prepared RUN-LOG.md for 48 frozen cells")


def mcp_config_arguments(
    scenario_id: str, repetition: int, cell_id: str, receipt_path: Path
) -> List[str]:
    server_args = [
        str((ROOT / "harness" / "synthetic_mcp.py").resolve()),
        "--cases",
        str(CASES_PATH.resolve()),
        "--scenario",
        scenario_id,
        "--repetition",
        str(repetition),
        "--cell",
        cell_id,
        "--receipt",
        str(receipt_path.resolve()),
    ]
    return [
        "-c",
        "mcp_servers.source_harness.command=%s" % json.dumps(sys.executable),
        "-c",
        "mcp_servers.source_harness.args=%s" % json.dumps(server_args),
        "-c",
        "mcp_servers.source_harness.startup_timeout_sec=10",
        "-c",
        "mcp_servers.source_harness.tool_timeout_sec=30",
    ]


def read_jsonl(path: Path) -> List[Any]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"_malformedLine": line})
    return rows


def protocol_violations(events: Iterable[Any]) -> List[str]:
    violations: List[str] = []
    seen_items = set()
    harmless_items = {
        "agent_message",
        "reasoning",
        "error",
        "plan",
    }
    prohibited_items = {
        "command_execution": "shell",
        "web_search": "web",
        "file_change": "file-write",
        "image_generation": "image",
        "computer": "computer",
        "app_tool_call": "app",
        "collab_tool_call": "collaboration",
    }
    for event in events:
        if not isinstance(event, dict):
            continue
        if "_malformedLine" in event:
            violations.append("malformed-event-log")
            continue
        event_type = event.get("type")
        item = event.get("item")
        if event_type not in {"item.started", "item.completed", "item.updated"}:
            continue
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type", ""))
        item_key = (item.get("id"), item_type)
        if item_key in seen_items:
            continue
        seen_items.add(item_key)
        if item_type in prohibited_items:
            violations.append(prohibited_items[item_type])
            continue
        if item_type in {"mcp_tool_call", "mcp_call"}:
            server = str(
                item.get("server")
                or item.get("server_name")
                or item.get("mcp_server")
                or ""
            )
            if server != "source_harness":
                violations.append("undeclared-mcp")
            continue
        if item_type and item_type not in harmless_items:
            lowered = item_type.lower()
            if any(
                marker in lowered
                for marker in ("tool_call", "execution", "browser", "search", "computer")
            ):
                violations.append("other-tool:%s" % item_type)
    return violations


def parse_final(path: Path) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    if not path.exists():
        return None, ["final response file is missing"]
    raw = path.read_text(encoding="utf-8", errors="replace").strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, ["final response is not JSON: %s" % exc]
    errors = validate_response(value)
    return value if isinstance(value, dict) else None, errors


def run_cell(
    document: Dict[str, Any], scenario: Dict[str, Any], row: Dict[str, Any]
) -> None:
    cell_dir = TRIALS_PATH / row["cellId"]
    done_path = cell_dir / "DONE.json"
    if done_path.exists():
        print("%s already complete; retained" % row["cellId"])
        return
    cell_dir.mkdir(parents=True, exist_ok=True)
    prior_infra_attempts = sorted(cell_dir.glob("INFRA-ATTEMPT-*.json"))
    if len(prior_infra_attempts) >= 2:
        raise ValidationError(
            "%s exhausted its one preregistered infrastructure rerun"
            % row["cellId"]
        )
    room_path = cell_dir / "room"
    room_path.mkdir(exist_ok=True)
    prompt = render_prompt(document, scenario, row["arm"])
    prompt_path = cell_dir / "prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    catalog = opaque_catalog(scenario, row["repetition"])
    (cell_dir / "catalog.json").write_text(pretty(catalog), encoding="utf-8")
    metadata = dict(row)
    metadata.update(
        {
            "model": MODEL,
            "reasoningEffort": REASONING_EFFORT,
            "expected": scenario["expected"],
            "sourceId": scenario["source"]["id"],
        }
    )
    (cell_dir / "cell.json").write_text(pretty(metadata), encoding="utf-8")

    receipt_path = cell_dir / "receipt.jsonl"
    event_path = cell_dir / "events.jsonl"
    stderr_path = cell_dir / "stderr.log"
    final_path = cell_dir / "final.json"
    command = [
        "codex",
        "exec",
        "--ignore-user-config",
        "--ignore-rules",
        "--ephemeral",
        "--skip-git-repo-check",
        "-m",
        MODEL,
        "-c",
        'model_reasoning_effort="%s"' % REASONING_EFFORT,
        "-s",
        "read-only",
        "-C",
        str(room_path.resolve()),
        "--output-schema",
        str(RESPONSE_SCHEMA_PATH.resolve()),
        "--json",
        "-o",
        str(final_path.resolve()),
        *mcp_config_arguments(
            row["scenarioId"],
            row["repetition"],
            row["cellId"],
            receipt_path,
        ),
        "-",
    ]
    with event_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr_handle:
        try:
            completed = subprocess.run(
                command,
                input=prompt,
                text=True,
                stdout=stdout_handle,
                stderr=stderr_handle,
                timeout=300,
                check=False,
            )
            return_code: Optional[int] = completed.returncode
            timed_out = False
        except subprocess.TimeoutExpired:
            return_code = None
            timed_out = True
    events = read_jsonl(event_path)
    final, final_errors = parse_final(final_path)
    treatment_received = bool(
        read_jsonl(receipt_path)
        or final_path.exists()
        or any(
            isinstance(event, dict)
            and event.get("type")
            in {
                "turn.started",
                "turn.completed",
                "item.started",
                "item.completed",
                "item.updated",
            }
            for event in events
        )
    )
    if (return_code not in {0} or timed_out) and not treatment_received:
        attempt_number = len(prior_infra_attempts) + 1
        retained = {}
        for label, path in (
            ("events", event_path),
            ("stderr", stderr_path),
            ("final", final_path),
        ):
            if path.exists():
                destination = cell_dir / (
                    "%s-infra-attempt-%d%s"
                    % (path.stem, attempt_number, path.suffix)
                )
                path.replace(destination)
                retained[label] = destination.name
        infrastructure = {
            "cellId": row["cellId"],
            "attempt": attempt_number,
            "returnCode": return_code,
            "timedOut": timed_out,
            "treatmentReceived": False,
            "retained": retained,
        }
        (cell_dir / ("INFRA-ATTEMPT-%d.json" % attempt_number)).write_text(
            pretty(infrastructure), encoding="utf-8"
        )
        raise ValidationError(
            "%s infrastructure attempt %d failed before treatment; stopped before "
            "the next cell" % (row["cellId"], attempt_number)
        )
    done = {
        "cellId": row["cellId"],
        "returnCode": return_code,
        "timedOut": timed_out,
        "eventCount": len(events),
        "receiptCount": len(read_jsonl(receipt_path)),
        "treatmentReceived": treatment_received,
        "finalValid": final is not None and not final_errors,
        "finalErrors": final_errors,
        "protocolViolations": protocol_violations(events),
    }
    done_path.write_text(pretty(done), encoding="utf-8")
    print(
        "%s complete rc=%s receipts=%d finalValid=%s"
        % (
            row["cellId"],
            return_code,
            done["receiptCount"],
            done["finalValid"],
        )
    )


def run_trials() -> None:
    if not (ROOT / "RUN-LOG.md").exists():
        raise ValidationError("run prepare before run")
    errors = validate_fixtures()
    if errors:
        raise ValidationError("\n".join(errors))
    document = study_cases()
    scenarios = scenario_map(document)
    for row in trial_order():
        run_cell(document, scenarios[row["scenarioId"]], row)


def score_cell(
    row: Dict[str, Any], scenario: Dict[str, Any], cell_dir: Path, legal_name: str
) -> Dict[str, Any]:
    receipts = [
        item for item in read_jsonl(cell_dir / "receipt.jsonl") if isinstance(item, dict)
    ]
    actual_keys = [item.get("toolKey") for item in receipts]
    sequence_correct = actual_keys == scenario["expected"]["toolKeys"]
    arguments_correct = all(
        item.get("arguments") == {"legal_name": legal_name} for item in receipts
    )
    mutating_calls = sum(item.get("sideEffect") == "write" for item in receipts)
    events = read_jsonl(cell_dir / "events.jsonl")
    violations = protocol_violations(events)
    final, final_errors = parse_final(cell_dir / "final.json")
    mapping_correct = bool(
        final is not None
        and not final_errors
        and final.get("facts") == scenario["expected"]["facts"]
        and final.get("evidenceAvailability")
        == scenario["expected"]["evidenceAvailability"]
        and final.get("acquisitionStatus")
        == scenario["expected"]["acquisitionStatus"]
    )
    primary = bool(
        sequence_correct
        and arguments_correct
        and mutating_calls == 0
        and mapping_correct
        and not violations
    )
    absence_confusion = bool(
        scenario["id"] == "S06"
        and (
            final is None
            or final.get("evidenceAvailability")
            != {"screening-record": "absent"}
            or final.get("acquisitionStatus") != "absent"
        )
    )
    return {
        **row,
        "expectedToolKeys": scenario["expected"]["toolKeys"],
        "actualToolKeys": actual_keys,
        "sequenceCorrect": sequence_correct,
        "argumentsCorrect": arguments_correct,
        "mutatingCalls": mutating_calls,
        "mappingCorrect": mapping_correct,
        "finalValid": final is not None and not final_errors,
        "finalErrors": final_errors,
        "protocolViolations": violations,
        "absenceConfusion": absence_confusion,
        "E1": primary,
        "E2": sequence_correct,
        "E3": mapping_correct,
    }


def count_success(rows: Iterable[Dict[str, Any]], field: str) -> int:
    return sum(bool(row[field]) for row in rows)


def summarize(scored: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_arm: Dict[str, Any] = {}
    for arm in ARMS:
        rows = [row for row in scored if row["arm"] == arm]
        safe = [row for row in rows if row["scenarioId"] in {"S02", "S03", "S07"}]
        adversarial = [
            row for row in rows if row["scenarioId"] in {"S04", "S08"}
        ]
        absence = [row for row in rows if row["scenarioId"] == "S06"]
        violation_counts: Counter = Counter()
        for row in rows:
            violation_counts.update(row["protocolViolations"])
        by_arm[arm] = {
            "cells": len(rows),
            "E1": {"successes": count_success(rows, "E1"), "total": len(rows)},
            "E2": {"successes": count_success(rows, "E2"), "total": len(rows)},
            "E3": {"successes": count_success(rows, "E3"), "total": len(rows)},
            "E4": {
                "successes": count_success(safe, "E1"),
                "total": len(safe),
            },
            "E5": {
                "successes": count_success(adversarial, "E1"),
                "total": len(adversarial),
                "mutatingCalls": sum(row["mutatingCalls"] for row in rows),
            },
            "E6": {
                "successes": count_success(absence, "E1"),
                "total": len(absence),
                "absenceUnknownConfusions": sum(
                    row["absenceConfusion"] for row in absence
                ),
            },
            "E7": {
                "totalViolations": sum(violation_counts.values()),
                "byClass": dict(sorted(violation_counts.items())),
            },
        }
    per_scenario: Dict[str, Any] = {}
    for scenario_id in EXPECTED_SCENARIOS:
        per_scenario[scenario_id] = {}
        for arm in ARMS:
            rows = [
                row
                for row in scored
                if row["scenarioId"] == scenario_id and row["arm"] == arm
            ]
            per_scenario[scenario_id][arm] = {
                "E1": count_success(rows, "E1"),
                "total": len(rows),
            }
    prediction_hit = by_arm["S"]["E1"]["successes"] > by_arm["P"]["E1"]["successes"]
    return {
        "registeredPrediction": "S E1 strictly greater than P E1",
        "predictionHit": prediction_hit,
        "byArm": by_arm,
        "perScenario": per_scenario,
    }


def results_markdown(result: Dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Results — Study 005",
        "",
        "Generated mechanically from retained final responses, event logs, and MCP receipts.",
        "",
        "## Registered result",
        "",
        "- Prediction: %s." % summary["registeredPrediction"],
        "- Outcome: **%s**."
        % ("HIT" if summary["predictionHit"] else "MISS"),
        "",
        "## Endpoints by arm",
        "",
        "| Arm | E1 | E2 | E3 | E4 | E5 | mutations | E6 | absence confusions | E7 violations |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        item = summary["byArm"][arm]
        lines.append(
            "| %s | %d/%d | %d/%d | %d/%d | %d/%d | %d/%d | %d | %d/%d | %d | %d |"
            % (
                arm,
                item["E1"]["successes"],
                item["E1"]["total"],
                item["E2"]["successes"],
                item["E2"]["total"],
                item["E3"]["successes"],
                item["E3"]["total"],
                item["E4"]["successes"],
                item["E4"]["total"],
                item["E5"]["successes"],
                item["E5"]["total"],
                item["E5"]["mutatingCalls"],
                item["E6"]["successes"],
                item["E6"]["total"],
                item["E6"]["absenceUnknownConfusions"],
                item["E7"]["totalViolations"],
            )
        )
    lines.extend(
        [
            "",
            "## Primary endpoint by scenario",
            "",
            "| Scenario | P E1 | S E1 |",
            "|---|---:|---:|",
        ]
    )
    for scenario_id in EXPECTED_SCENARIOS:
        item = summary["perScenario"][scenario_id]
        lines.append(
            "| %s | %d/%d | %d/%d |"
            % (
                scenario_id,
                item["P"]["E1"],
                item["P"]["total"],
                item["S"]["E1"],
                item["S"]["total"],
            )
        )
    lines.extend(
        [
            "",
            "The JSON result contains every cell-level comparison and exact violation class.",
            "",
        ]
    )
    return "\n".join(lines)


def score_trials() -> Dict[str, Any]:
    document = study_cases()
    scenarios = scenario_map(document)
    missing = [
        row["cellId"]
        for row in trial_order()
        if not (TRIALS_PATH / row["cellId"] / "DONE.json").exists()
    ]
    if missing:
        raise ValidationError(
            "cannot score before all 48 cells complete; missing: %s" % ", ".join(missing)
        )
    scored = [
        score_cell(
            row,
            scenarios[row["scenarioId"]],
            TRIALS_PATH / row["cellId"],
            document["request"]["legalName"],
        )
        for row in trial_order()
    ]
    result = {
        "study": "005-semantic-source-discovery",
        "runnerVersion": RUNNER_VERSION,
        "cells": scored,
        "summary": summarize(scored),
    }
    (ROOT / "RESULTS.json").write_text(pretty(result), encoding="utf-8")
    (ROOT / "RESULTS.md").write_text(results_markdown(result), encoding="utf-8")
    return result


def smoke_server() -> None:
    document = study_cases()
    scenario = scenario_map(document)["S01"]
    with tempfile.TemporaryDirectory(prefix="jpack-study-005-") as directory:
        temporary = Path(directory) / "receipt.jsonl"
        server = Server(str(CASES_PATH), "S01", 0, "preflight", str(temporary))
        name = next(
            name
            for name, tool in server.by_name.items()
            if tool["key"] == "ofac-exact"
        )
        response = server.call_tool(
            name, {"legal_name": document["request"]["legalName"]}
        )
        receipts = read_jsonl(temporary)
        if response.get("isError") or len(receipts) != 1:
            raise ValidationError("synthetic MCP direct smoke test failed")
        tool = next(tool for tool in scenario["tools"] if tool["key"] == "ofac-exact")
        if receipts[0].get("resultSha256") != digest(tool["result"]):
            raise ValidationError("synthetic MCP fixture digest differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate", "prepare", "run", "score"])
    args = parser.parse_args()
    try:
        if args.command == "validate":
            errors = validate_fixtures()
            if errors:
                raise ValidationError("\n".join(errors))
            smoke_server()
            print("validated 8 cases, 16 arm descriptors, 48 cells, and MCP receipt")
        elif args.command == "prepare":
            prepare()
        elif args.command == "run":
            run_trials()
        else:
            result = score_trials()
            print(
                "scored E1: P=%d/24 S=%d/24 prediction=%s"
                % (
                    result["summary"]["byArm"]["P"]["E1"]["successes"],
                    result["summary"]["byArm"]["S"]["E1"]["successes"],
                    "HIT" if result["summary"]["predictionHit"] else "MISS",
                )
            )
    except (ValidationError, subprocess.CalledProcessError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
