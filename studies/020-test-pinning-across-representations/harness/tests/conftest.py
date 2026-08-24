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


# --------------------------------------------------------------------------
# NEW IN 020: the artifact port is a GATE(pre-freeze), and a test that reads an
# artifact this tree does not carry yet must SKIP BY NAME
# --------------------------------------------------------------------------
#
# PREREGISTRATION.md §4.1 ports the gold suite, both mutant corpora and their
# manifests, both reference implementations, the off-gold certificate, the
# capabilities file and the two verification documents BY DIGEST, and
# `harness/SCAFFOLD.md` item A1 carries that as a `GATE(pre-freeze)`. The
# harness landed first, so the harness suite runs against a tree in which those
# bytes are absent.
#
# The registered discipline for that state is the program's own, from Study
# 019's `test_score_pipeline.py`: a test whose subject is absent SKIPS with the
# reason named, rather than being deleted (which loses the check), softened
# (which is worse than losing it) or left to fail (which makes a red suite the
# normal state and hides the next real failure). `harness/PINS.json` records
# each absent artifact's 019-side digest under a `…AtSource` member, so every
# one of these skips turns back into an assertion the moment the bytes land —
# and the CI job counts them, so the number cannot drift upward unnoticed.


ARTIFACT_GATE = ("PREREGISTRATION.md §4.1 ports this artifact BY DIGEST and "
                 "harness/SCAFFOLD.md item A1 carries the port as a "
                 "GATE(pre-freeze); it is not in this tree yet")


def artifact(*relative):
    """Skip unless every named study-relative path exists."""
    missing = [name for name in relative
               if not os.path.exists(os.path.join(STUDY, name))]
    if missing:
        pytest.skip("%s: %s" % (ARTIFACT_GATE, ", ".join(missing)))
    return [os.path.join(STUDY, name) for name in relative]


@pytest.fixture
def requires_artifact():
    return artifact
