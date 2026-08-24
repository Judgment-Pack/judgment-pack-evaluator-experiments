"""Suite fixtures: the harness on `sys.path`, and the registration as text.

Study 012's conftest does the same two things for the same reason — the harness
modules are invoked by path in production, so the suite imports them the way the
ceremony runs them, and every test that claims something about the registration
reads the registration's own bytes rather than a copy of them."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
if HARNESS not in sys.path:
    sys.path.insert(0, HARNESS)


@pytest.fixture(scope="session")
def study():
    return STUDY


@pytest.fixture(scope="session")
def preregistration():
    with open(os.path.join(STUDY, "PREREGISTRATION.md"), "rb") as handle:
        return handle.read().decode("utf-8")


@pytest.fixture(scope="session")
def pins():
    with open(os.path.join(HARNESS, "PINS.json"), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))
