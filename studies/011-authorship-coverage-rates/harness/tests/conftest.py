#!/usr/bin/env python3
"""Test wiring: the harness directory and this directory on sys.path, and the
study's own PINS.json read once.

The tests run offline and call no CLI: the only "codex" any of them touches is
the stand-in in fixtures.py, invoked through the real wrapper with its own
digest pinned in a test registry.

About the operator's HOME, precisely: the wrapper copies `$HOME/.codex/auth.json`
into each run's isolated home, so a wrapper-driven test would copy the real
credential if it ran with the real HOME. It does not — `test_batch.py`
redirects `HOME` to a throwaway directory carrying a sentinel credential for
every case that invokes the wrapper, and one of its cases scans every retained
byte and every leftover under the scratch parent for that sentinel. The tests
do read two retained Study 010 artifacts (its lock and its completion), by
design: C1 and C3 are checks against them.
"""
from __future__ import annotations
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
for path in (HARNESS, HERE):
    if path not in sys.path:
        sys.path.insert(0, path)

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def study() -> str:
    return STUDY


@pytest.fixture(scope="session")
def pins() -> dict:
    """The study's real registry: the in-process slot fixtures record its
    pinned model and binary digest in their CALL.json, so admission is tested
    against the values the batch will actually run under."""
    with open(os.path.join(HARNESS, "PINS.json")) as handle:
        return json.load(handle)


@pytest.fixture(scope="session")
def pins_path() -> str:
    return os.path.join(HARNESS, "PINS.json")
