"""The Appendix A equality, enforced (round 3, finding 7).

§2.6 registers that every arm artifact is reproducible from Appendix A by the
registered assembly rule. `integrity.verify_arms()` checks the relations the
artifacts must satisfy; this test checks the stronger statement the appendix
makes — the committed twenty files ARE the assembler's output, byte for byte.
A drift in either direction (an edited arm file, or an assembler that no
longer produces the committed bytes) fails here before any digest table can
be updated to paper over it.
"""
import filecmp
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
sys.path.insert(0, HARNESS)

import arm_assembly  # noqa: E402


def test_the_committed_arms_are_the_assemblers_output(tmp_path):
    built = arm_assembly.build(str(tmp_path))
    assert len(built) == 20
    mismatches = []
    for arm in ("A", "B", "C", "D", "E"):
        for name in ("ARM.json", "FAMILY.json", "POLICY.md", "PROMPT.txt"):
            fresh = os.path.join(str(tmp_path), arm, name)
            committed = os.path.join(STUDY, "arms", arm, name)
            if not filecmp.cmp(fresh, committed, shallow=False):
                mismatches.append("arms/%s/%s" % (arm, name))
    assert not mismatches, (
        "the committed arm files are not the assembler's output: %s"
        % mismatches)


def test_the_assemblers_digests_match_the_registry():
    import hashlib
    import json
    with open(os.path.join(HARNESS, "PINS.json"), "rb") as handle:
        pins = json.loads(handle.read().decode("utf-8"))
    for arm, member, name in (
            (arm, member, name)
            for arm in ("A", "B", "C", "D", "E")
            for member, name in (("policySha256", "POLICY.md"),
                                 ("promptSha256", "PROMPT.txt"),
                                 ("familySha256", "FAMILY.json"),
                                 ("armSha256", "ARM.json"))):
        with open(os.path.join(STUDY, "arms", arm, name), "rb") as handle:
            actual = hashlib.sha256(handle.read()).hexdigest()
        pinned = pins["arms"][arm][member].split(":")[-1]
        assert actual == pinned, ("arms/%s/%s" % (arm, name))
