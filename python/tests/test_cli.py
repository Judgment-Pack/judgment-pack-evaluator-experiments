from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from tests.pack_fixtures import appendix_pack


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
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result == {
        "kind": "outcome",
        "outcomeId": "proceed",
        "reasons": [],
        "handoff": "none",
        "experimental": True,
        "conformanceClaim": "none",
    }


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
    )
    assert completed.returncode == 2
    assert completed.stdout == ""
    error = json.loads(completed.stderr)
    assert error["error"]["kind"] == "invalid-input"
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
    )
    assert completed.returncode == 2
    assert json.loads(completed.stderr)["error"]["kind"] == "invalid-input"
