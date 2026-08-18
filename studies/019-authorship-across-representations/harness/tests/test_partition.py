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
# R1-5's authoring outcome, registered in its own sentence because it is NOT an
# admission code: `admit()` cannot return it, `e4lib/admit.py`'s DROP_ORDER is
# the admission list above, and the transcript binding is what assigns this one.
PROTOCOL = re.compile(
    r"is not an admission code — (.+?) — the transcript binding's author-side "
    r"verdict")


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
    for name, pattern in (("apparatus", APPARATUS), ("authoring", AUTHORING),
                          ("protocol", PROTOCOL)):
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


def test_the_protocol_outcome_is_registered_and_is_not_an_admission_code(
        preregistration):
    """R1-5. The transcript binding's author-side verdict is an AUTHORING
    outcome — retained, counted, scoring zero — and it is registered in its own
    sentence because `admit()` can never return it: it is read off the retained
    transcript, not off the artifact."""
    registered = registered_lists(preregistration)["protocol"]
    assert registered == [phrase for _code, phrase
                          in batch.AUTHORING_PROTOCOL_CODES]
    for code, _phrase in batch.AUTHORING_PROTOCOL_CODES:
        assert batch.CODE_PARTITION[code][0] == "authoring"
        assert code not in [name for name, _ in batch.AUTHORING_CODES]


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
    phrases = (registered["apparatus"] + registered["authoring"]
               + registered["protocol"])
    assert sorted(phrase for _side, phrase in batch.CODE_PARTITION.values()) == \
        sorted(phrases)
    assert len(set(phrases)) == len(phrases)
    assert set(code for code, _ in batch.APPARATUS_CODES) & \
        set(code for code, _ in batch.AUTHORING_CODES) == set()


def test_every_wrapper_exit_status_maps_into_the_partition_or_is_a_success():
    """R1-4. The wrapper's statuses are the driver's only evidence about a call,
    so each one is either 'the slot is complete' or a code on §1a's APPARATUS
    side — with no exemption for the pre-call refusal, which is where the hole
    was: `preflight-refused` was in no partition, `population()` excludes only
    codes it recognises as apparatus, and the slot the driver sealed and
    ledgered went into every per-arm denominator as an ordinary authoring run.
    A status that mapped to an authoring code would file an apparatus failure as
    the author's work."""
    for status, (code, _gloss) in batch.WRAPPER_EXIT_MEANINGS.items():
        if code == "complete":
            continue
        assert code in batch.CODE_PARTITION, status
        assert batch.CODE_PARTITION[code][0] == "apparatus", status


def test_an_unregistered_wrapper_status_refuses_rather_than_taking_a_code():
    """R1-4's fail-closed half. `WRAPPER_CODES.get(status, "wrapper-error")` gave
    every unknown status a sentinel code that no partition named and no rule
    excluded; the driver sealed and ledgered such slots and the scorer counted
    them. There is no sentinel now: an unregistered status is a BatchError, and
    the batch stops."""
    import pytest as _pytest
    for status in (2, 7, 129, 130, 143, -9):
        with _pytest.raises(batch.BatchError) as caught:
            batch.wrapper_code(status)
        assert "unregistered status is not a refusal code" in str(caught.value)
    for status, (code, _gloss) in batch.WRAPPER_EXIT_MEANINGS.items():
        expected = None if code == "complete" else code
        assert batch.wrapper_code(status) == expected


def test_the_two_wrapper_failure_phases_are_two_codes():
    """R1-4's attribution half: a failure BEFORE the call and a failure AFTER it
    are two events. Under `set -e` a failing post-call helper exited 1, which the
    driver read as 'a pre-call refusal; nothing was called' — while the call had
    been made and the slot retained."""
    assert batch.WRAPPER_CODES[1] == "preflight-refused"
    assert batch.WRAPPER_CODES[13] == "post-call-failure"
    assert batch.CODE_PARTITION["preflight-refused"][0] == "apparatus"
    assert batch.CODE_PARTITION["post-call-failure"][0] == "apparatus"


def test_the_scorers_codes_are_the_partition():
    """SKELETON (SCAFFOLD item S1). Becomes a real assertion when
    `harness/score.py` lands: every code `admit()` can return must be a key of
    CODE_PARTITION, and every key must be reachable."""
    score = pytest.importorskip(
        "score", reason="harness/score.py is not assembled yet (SCAFFOLD S1); "
                        "the third diff §1a registers cannot run until it is")
    # The scorer's partition-derived constants are bound lazily, after its
    # integrity gate, so a reader binds them the way `main()` does rather than
    # reading the pre-binding placeholders.
    score.bind_study_modules()
    assert set(score.ADMISSION_CODES) == set(batch.CODE_PARTITION)
    assert set(score.APPARATUS_SIDE) | set(score.AUTHORING_SIDE) == \
        set(batch.CODE_PARTITION)
    # R1-4/R1-5's two additions reach the scorer's own sides, which is what
    # decides the denominator: the wrapper's two new apparatus codes leave it,
    # and the transcript binding's author-side code stays in it.
    for code in ("preflight-refused", "post-call-failure"):
        assert code in score.APPARATUS_SIDE, code
    assert "author-protocol-violation" in score.AUTHORING_SIDE
