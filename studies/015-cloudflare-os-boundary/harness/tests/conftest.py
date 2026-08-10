"""Shared fixtures. CFOS_SOURCE and JPACK_BIN are required, not skippable:
a determinism suite that silently skips its subject is not a determinism suite
(PREREGISTRATION section 8)."""

import json
import os
import shutil
import sys
from pathlib import Path

import pytest

STUDY = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(STUDY / "adapter"))
sys.path.insert(0, str(STUDY / "harness"))


@pytest.fixture(scope="session")
def study():
    return STUDY


@pytest.fixture(scope="session")
def jpack_bin():
    value = os.environ.get("JPACK_BIN")
    assert value and Path(value).is_file(), "JPACK_BIN must point at the pinned evaluator"
    return value


@pytest.fixture(scope="session")
def cfos_source():
    value = os.environ.get("CFOS_SOURCE")
    assert value and Path(value).is_dir(), "CFOS_SOURCE must point at the pinned clone"
    return value


@pytest.fixture()
def cell_copy(tmp_path):
    """Copy a frozen fixture cell for mutation; returns (mutate, path) helpers."""

    def _copy(cell_id):
        source = (
            STUDY / "fixtures" / "baseline"
            if cell_id == "pos-baseline"
            else STUDY / "fixtures" / "mutations" / cell_id
        )
        target = tmp_path / cell_id
        shutil.copytree(source, target)
        return target

    return _copy


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump_json(path, document):
    Path(path).write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
