"""§1a's population rule, diffed against the code partition — SKELETON.

§1a registers two lists and one consequence: apparatus failures are
pipeline-invalid and leave the denominator, authoring outcomes are valid,
counted, and score zero on every endpoint they reach. A run that moves between
those lists moves between denominators, which is why the registration says a
harness test diffs the prose partition against the scorer's code partition and
against every code `admit()` can return.

Two of those three diffs are live here. The third — every code `admit()` can
return — cannot be: `harness/score.py` does not exist yet
(`harness/SCAFFOLD.md`, item S1), and a test that pretended to check it would be
the exact failure §1a exists to prevent. It is written below as a skeleton that
SKIPS with a named reason while the scorer is absent and becomes a real
assertion the moment it lands, rather than as a comment someone must remember.

The prose side is parsed out of the registration's own bytes by anchors unique
in the file, each parser asserting that uniqueness — Study 012's round-12
lesson, where a test module was a copy checking a copy and a registration-only
edit stayed green.
"""
import re

import pytest

import batch

SECTION = re.compile(r"\n## 1a\. (.*?)(?=\n## )", re.DOTALL)
APPARATUS = re.compile(r"Apparatus failures — (.+?) — are pipeline-invalid")
AUTHORING = re.compile(
    r"attributable to what the author emitted — (.+?) — is an authoring outcome")


def flatten(text):
    """One line, emphasis and code ticks removed: the registration's wrapping
    and bolding are not differences."""
    return " ".join(text.replace("*", "").replace("`", "").split())


def section(preregistration):
    found = SECTION.findall("\n" + preregistration)
    assert len(found) == 1, (
        "PREREGISTRATION.md holds %d sections numbered 1a; the population rule "
        "is identified by that heading" % len(found))
    return flatten(found[0])


def registered_lists(preregistration):
    body = section(preregistration)
    lists = {}
    for name, pattern in (("apparatus", APPARATUS), ("authoring", AUTHORING)):
        matches = pattern.findall(body)
        assert len(matches) == 1, (
            "§1a holds %d %s lists; the partition is identified by that "
            "sentence" % (len(matches), name))
        lists[name] = [item.strip() for item in matches[0].split(",")]
    return lists


def test_the_apparatus_list_is_the_codes(preregistration):
    registered = registered_lists(preregistration)["apparatus"]
    assert registered == [phrase for _code, phrase in batch.APPARATUS_CODES]


def test_the_authoring_list_is_the_codes(preregistration):
    registered = registered_lists(preregistration)["authoring"]
    assert registered == [phrase for _code, phrase in batch.AUTHORING_CODES]


def test_the_timeout_is_on_the_apparatus_side(preregistration):
    """The design-phase lesson, asserted rather than remembered: the pilot
    driver mis-filed timeouts as an authoring code, which silently moves a run
    out of the excluded set and into every rate's denominator."""
    registered = registered_lists(preregistration)
    assert "call timeout at the registered ceiling" in registered["apparatus"]
    assert "call timeout at the registered ceiling" not in registered["authoring"]
    assert batch.CODE_PARTITION["call-timeout"][0] == "apparatus"
    assert batch.WRAPPER_EXIT_MEANINGS[12][0] == "call-timeout"


def test_the_partition_is_exhaustive_and_disjoint(preregistration):
    registered = registered_lists(preregistration)
    phrases = registered["apparatus"] + registered["authoring"]
    assert sorted(phrase for _side, phrase in batch.CODE_PARTITION.values()) == \
        sorted(phrases)
    assert len(set(phrases)) == len(phrases)
    assert set(code for code, _ in batch.APPARATUS_CODES) & \
        set(code for code, _ in batch.AUTHORING_CODES) == set()


def test_every_wrapper_exit_status_maps_into_the_partition_or_is_a_success():
    """The wrapper's statuses are the driver's only evidence about a call, so
    each one is either 'the slot is complete', 'nothing was spent', or a code on
    §1a's apparatus side. A status that mapped to an authoring code would file
    an apparatus failure as the author's work."""
    for status, (code, _gloss) in batch.WRAPPER_EXIT_MEANINGS.items():
        if code in ("complete", "preflight-refused"):
            continue
        assert batch.CODE_PARTITION[code][0] == "apparatus", status


def test_the_scorers_codes_are_the_partition():
    """SKELETON (SCAFFOLD item S1). Becomes a real assertion when
    `harness/score.py` lands: every code `admit()` can return must be a key of
    CODE_PARTITION, and every key must be reachable."""
    score = pytest.importorskip(
        "score", reason="harness/score.py is not assembled yet (SCAFFOLD S1); "
                        "the third diff §1a registers cannot run until it is")
    assert set(score.ADMISSION_CODES) == set(batch.CODE_PARTITION)
