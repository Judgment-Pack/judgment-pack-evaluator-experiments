import os
import sys
from pathlib import Path

import pytest

STUDY = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(STUDY / "harness"))
sys.path.insert(0, str(STUDY / "registry"))


@pytest.fixture(scope="session")
def study():
    return STUDY


@pytest.fixture(scope="session")
def jpack_bin():
    """The pinned evaluator. Missing toolchain FAILS the suite, never skips."""
    value = os.environ.get("JPACK_BIN")
    if not value or not Path(value).is_file():
        pytest.fail("JPACK_BIN is required for this suite and is not available")
    return value


@pytest.fixture(scope="session")
def owp_source():
    value = os.environ.get("OWP_SOURCE")
    if not value or not Path(value).is_dir():
        pytest.fail("OWP_SOURCE is required for this suite and is not available")
    return value
