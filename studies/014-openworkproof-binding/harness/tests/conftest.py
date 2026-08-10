"""Shared harness-test fixtures.

The environment is not optional. Round 1 found that determinism could pass
vacuously because the rebuild tests skipped when `OWP_SOURCE` was unset, so
`jpack_bin()` and `owp_source()` FAIL with a clear message rather than skipping.
Nothing in this suite skips.
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

STUDY = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(STUDY / "adapter"))
sys.path.insert(0, str(STUDY / "harness"))

import verify  # noqa: E402

PINS = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))


def jpack_bin():
    """The pinned evaluator. Absent or wrong is a test FAILURE, never a skip."""
    path = os.environ.get("JPACK_BIN")
    assert path, "JPACK_BIN is unset: the ceremony needs the pinned evaluator"
    assert Path(path).is_file(), "JPACK_BIN does not point at a file: %s" % path
    assert verify.sha256_file(path) == PINS["jpack"]["binarySha256"], (
        "JPACK_BIN does not match the pinned binary digest"
    )
    return path


def owp_source():
    """The pinned clone. Absent is a test FAILURE, never a skip."""
    path = os.environ.get("OWP_SOURCE")
    assert path, "OWP_SOURCE is unset: fixture construction needs the pinned clone"
    root = Path(path)
    assert (root / "tests" / "conftest.py").is_file(), (
        "OWP_SOURCE does not point at the pinned OpenWorkProof clone: %s" % path
    )
    commit_path = STUDY / "upstream" / "OPENWORKPROOF-COMMIT.txt"
    if commit_path.is_file():
        pinned = PINS["openworkproof"]["commit"]
        assert pinned in commit_path.read_text(encoding="utf-8"), (
            "upstream commit record does not carry the pinned commit"
        )
    return str(root)


@pytest.fixture(scope="session")
def binary():
    return jpack_bin()


@pytest.fixture(scope="session")
def source():
    return owp_source()


@pytest.fixture
def work_root():
    directory = Path(tempfile.mkdtemp(prefix="study014-test-"))
    try:
        yield directory
    finally:
        shutil.rmtree(directory, ignore_errors=True)
