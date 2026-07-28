from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from tests.pack_fixtures import appendix_pack, base_pack


PYTHON_ROOT = Path(__file__).parents[1]


def test_cli_produces_appendix_instance_disposition(tmp_path: Path):
    pack_path = tmp_path / "pack.json"
    facts_path = tmp_path / "facts.json"
    evidence_path = tmp_path / "evidence.json"
    pack_path.write_text(json.dumps(appendix_pack()), encoding="utf-8")
    facts_path.write_text(
        json.dumps(
            {
                "request": {
                    "type": "data-access",
                    "completeness": "complete",
                    "appropriateness": "pass",
                    "embargoedInformationToUnauthorizedRecipients": False,
                }
            }
        ),
        encoding="utf-8",
    )
    evidence_path.write_text(
        json.dumps(
            {"intake-form": "present", "sponsor-endorsement": "present"}
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "jps_evaluator",
            "--pack",
            str(pack_path),
            "--facts",
            str(facts_path),
            "--evidence",
            str(evidence_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=PYTHON_ROOT,
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result == {
        "disposition": {
            "kind": "outcome",
            "outcomeId": "proceed",
            "reasons": [],
            "handoff": {"state": "none"},
        },
        "experimental": True,
        "conformanceClaim": "none",
    }
    assert (
        '"disposition":{"handoff":{"state":"none"},"kind":"outcome",'
        '"outcomeId":"proceed","reasons":[]}'
    ) in completed.stdout


def test_cli_errors_are_not_dispositions(tmp_path: Path):
    pack_path = tmp_path / "bad-pack.json"
    facts_path = tmp_path / "facts.json"
    pack_path.write_text('{"same": 1, "same": 2}', encoding="utf-8")
    facts_path.write_text("{}", encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "jps_evaluator",
            "--pack",
            str(pack_path),
            "--facts",
            str(facts_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=PYTHON_ROOT,
    )
    assert completed.returncode == 2
    assert completed.stdout == ""
    error = json.loads(completed.stderr)
    assert error["error"]["class"] == "pack-not-conformant"
    assert error["error"]["phase"] == "preflight"
    assert "disposition" not in error
    assert error["experimental"] is True
    assert error["conformanceClaim"] == "none"


def test_cli_rejects_null_evidence_document(tmp_path: Path):
    pack_path = tmp_path / "pack.json"
    facts_path = tmp_path / "facts.json"
    evidence_path = tmp_path / "evidence.json"
    pack_path.write_text(json.dumps(appendix_pack()), encoding="utf-8")
    facts_path.write_text("{}", encoding="utf-8")
    evidence_path.write_text("null", encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "jps_evaluator",
            "--pack",
            str(pack_path),
            "--facts",
            str(facts_path),
            "--evidence",
            str(evidence_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=PYTHON_ROOT,
    )
    assert completed.returncode == 2
    error = json.loads(completed.stderr)["error"]
    assert error["class"] == "malformed-input"
    assert error["phase"] == "preflight"


def test_cli_validates_pack_before_loading_malformed_facts(tmp_path: Path):
    pack = base_pack()
    pack["undeclared"] = True
    pack_path = tmp_path / "pack.json"
    facts_path = tmp_path / "facts.json"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")
    facts_path.write_text("{", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "jps_evaluator",
            "--pack",
            str(pack_path),
            "--facts",
            str(facts_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=PYTHON_ROOT,
    )
    assert completed.returncode == 2
    error = json.loads(completed.stderr)["error"]
    assert error["class"] == "pack-not-conformant"
    assert error["phase"] == "preflight"
    assert "undeclared member" in error["message"]


def test_cli_resource_error_reports_evaluation_phase(tmp_path: Path):
    pack = base_pack()
    pack["rules"][0]["when"] = {
        "op": "fact",
        "path": "/value",
        "operator": "equals",
        "value": True,
    }
    pack_path = tmp_path / "pack.json"
    facts_path = tmp_path / "facts.json"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")
    facts_path.write_text('{"value":true}', encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "jps_evaluator",
            "--pack",
            str(pack_path),
            "--facts",
            str(facts_path),
            "--evaluation-work-limit",
            "1",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=PYTHON_ROOT,
    )
    assert completed.returncode == 2
    assert completed.stdout == ""
    error = json.loads(completed.stderr)["error"]
    assert error["class"] == "resource-exhaustion"
    assert error["phase"] == "evaluation"


def test_cli_requires_and_accepts_explicit_rfc0008_opt_in(tmp_path: Path):
    pack = base_pack()
    pack["rules"][0]["when"] = {
        "op": "exists",
        "path": "/items",
        "where": {
            "op": "fact",
            "path": "/ok",
            "operator": "equals",
            "value": True,
        },
    }
    pack_path = tmp_path / "pack.json"
    facts_path = tmp_path / "facts.json"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")
    facts_path.write_text('{"items":[{"ok":true}]}', encoding="utf-8")

    command = [
        sys.executable,
        "-m",
        "jps_evaluator",
        "--pack",
        str(pack_path),
        "--facts",
        str(facts_path),
    ]
    disabled = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        cwd=PYTHON_ROOT,
    )
    assert disabled.returncode == 2
    assert (
        json.loads(disabled.stderr)["error"]["class"]
        == "pack-not-conformant"
    )

    enabled = subprocess.run(
        command + ["--enable-rfc0008", "--evaluation-work-limit", "100"],
        check=False,
        capture_output=True,
        text=True,
        cwd=PYTHON_ROOT,
    )
    assert enabled.returncode == 0, enabled.stderr
    assert json.loads(enabled.stdout)["disposition"]["outcomeId"] == "outcome-a"
