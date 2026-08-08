#!/usr/bin/env python3
"""Test wiring: the harness directory and this directory on sys.path, and the
study's own PINS.json read once.

The tests run offline and call no CLI: no fixture here invokes the wrapper, no
model is reached, and the only bytes read from outside the throwaway roots are
this study's own committed artifacts — the five arms' `ARM.json`, `FAMILY.json`,
`POLICY.md` and `PROMPT.txt`, `harness/PINS.json`, and `PREREGISTRATION.md`,
which the parity tests parse.

Nothing here writes into the committed tree. Every slot, ledger, seal and
golden capture a test builds lives under a throwaway temporary root
(`fixtures.throwaway_root()`), which also refuses a temp path carrying a §6 C6
leak token, because every fixture slot records its working directory and
admission re-screens it.
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
    pinned model, CLI and binary digest in their CALL.json and stamp the digest
    of the registry FILE, so admission is tested against the values the batch
    will actually run under and against the registry of record itself."""
    with open(os.path.join(HARNESS, "PINS.json")) as handle:
        return json.load(handle)


@pytest.fixture(scope="session")
def pins_path() -> str:
    return os.path.join(HARNESS, "PINS.json")


@pytest.fixture(scope="session")
def preregistration() -> str:
    with open(os.path.join(STUDY, "PREREGISTRATION.md"), "rb") as handle:
        return handle.read().decode("utf-8")
