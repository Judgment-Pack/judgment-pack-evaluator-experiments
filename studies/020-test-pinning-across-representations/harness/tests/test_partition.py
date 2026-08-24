"""§1a's population rule, diffed against the code partition.

§1a registers two lists and one consequence: apparatus failures are
pipeline-invalid and leave the denominator, authoring outcomes are valid,
counted, and score zero on every endpoint they reach. A run that moves between
those lists moves between denominators, which is why the registration says a
harness test diffs the prose partition against the scorer's code partition and
against every code `admit()` can return.

**REBUILT FOR 020, and the rebuild is what §7's delta 3 asks for.** Study 019's
§1a stated the authoring outcomes as a comma-separated SENTENCE and this module
parsed that sentence. 020 states them as a TABLE with a third column — *arms it
can reach* — because 020 adds a code that is B/C-only (`presence-idiom-unsound`,
§3.2), and a two-column partition cannot be diffed against a three-column
registration. The table is therefore parsed as a table, and the third column is
diffed against `batch.AUTHORING_CODE_ARMS` and, through it, against
`e4lib/admit.py`'s enforcing `ARM_REACHABLE_CODES`, so an arm-structural leak
has three places that disagree rather than one that quietly widens.

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
# The §1a table's rows: | `code` | arms | meaning |
ROW = re.compile(r"^\|\s*\**`([a-z0-9-]+)`\**\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$")


def flatten(text):
    """One line, emphasis and code ticks removed: the registration's wrapping
    and bolding are not differences."""
    return " ".join(text.replace("*", "").replace("`", "").split())


def section_text(preregistration):
    found = SECTION.findall("\n" + preregistration)
    assert len(found) == 1, (
        "PREREGISTRATION.md holds %d sections numbered 1a; the population rule "
        "is identified by that heading" % len(found))
    return found[0]


def section(preregistration):
    return flatten(section_text(preregistration))


def registered_apparatus(preregistration):
    matches = APPARATUS.findall(section(preregistration))
    assert len(matches) == 1, (
        "§1a holds %d apparatus lists; the partition is identified by that "
        "sentence" % len(matches))
    return [item.strip() for item in matches[0].split(",")]


def registered_authoring(preregistration):
    """{code: (arms tuple, meaning)} from §1a's own table.

    The table is the registration; a row this parser cannot read is a row the
    diff would silently drop, so the row count is asserted against the number of
    table lines rather than against a number written here."""
    lines = [line.strip() for line in section_text(preregistration).splitlines()
             if line.strip().startswith("|")]
    body = [line for line in lines
            if not set(line) <= set("|- ") and "arms it can reach" not in line]
    table = {}
    for line in body:
        match = ROW.match(line)
        assert match, "§1a's authoring table has an unreadable row: %r" % line
        code, arms, meaning = match.groups()
        assert code not in table, code
        table[code] = (tuple(part.strip().strip("*")
                             for part in arms.replace("`", "").split(",")),
                       flatten(meaning))
    assert len(table) == len(body), "a row was lost between parse and diff"
    return table


def test_the_apparatus_list_is_the_codes(preregistration):
    registered = registered_apparatus(preregistration)
    assert registered == [phrase for _code, phrase in batch.APPARATUS_CODES]


def test_the_authoring_table_is_the_codes(preregistration):
    """CODE by code, in the registration's own order — including the one 020
    adds. The MEANING column is prose the registration owns and the code column
    is the contract, so the diff is over codes and over the arms column."""
    registered = registered_authoring(preregistration)
    coded = [code for code, _phrase
             in batch.AUTHORING_CODES + batch.AUTHORING_PROTOCOL_CODES]
    assert sorted(registered) == sorted(coded)
    assert "presence-idiom-unsound" in registered, (
        "§3.2's guard emits a registered authoring code and §1a's table must "
        "carry it whether or not it ever fires")


def test_the_arms_column_is_the_reachability_map(preregistration):
    """The third column, and the reason 020 has one. `presence-idiom-unsound`
    is structurally unreachable in arm A (§11.11), `schema-invalid-pack` in
    arms B/C, and `opa-check-failed`/`v0-syntax` in arm A. Three copies of that
    fact exist — the registration's table, `batch.AUTHORING_CODE_ARMS` and
    `e4lib/admit.py`'s enforcing `ARM_REACHABLE_CODES` — and all three are
    diffed here, so no one of them can widen alone."""
    from e4lib import admit as admit_lib
    registered = registered_authoring(preregistration)
    for code, (arms, _meaning) in sorted(registered.items()):
        assert tuple(arms) == batch.AUTHORING_CODE_ARMS[code], code
    for code, arms in sorted(batch.AUTHORING_CODE_ARMS.items()):
        if code in [name for name, _ in batch.AUTHORING_PROTOCOL_CODES]:
            # Not an admission code: `admit()` can never return it, so it is
            # deliberately absent from the enforcing map.
            for arm, reachable in admit_lib.ARM_REACHABLE_CODES.items():
                assert code not in reachable, (code, arm)
            continue
        for arm, reachable in sorted(admit_lib.ARM_REACHABLE_CODES.items()):
            assert (code in reachable) == (arm in arms), (code, arm)


def test_the_presence_idiom_code_is_b_and_c_only(preregistration):
    """§11.11, as a test rather than a ceiling nobody checks. An arm-A run that
    somehow produced this code would make the two E2 tables compare different
    partitions, so `admit()` refuses it."""
    from e4lib import admit as admit_lib
    registered = registered_authoring(preregistration)
    assert registered["presence-idiom-unsound"][0] == ("B", "C")
    assert batch.AUTHORING_CODE_ARMS["presence-idiom-unsound"] == ("B", "C")
    assert "presence-idiom-unsound" not in admit_lib.ARM_REACHABLE_CODES["A"]
    for arm in ("B", "C"):
        assert "presence-idiom-unsound" in admit_lib.ARM_REACHABLE_CODES[arm]


def test_the_e2_table_carries_the_new_code(preregistration):
    """§5.1's E2 row: "The table carries `presence-idiom-unsound` (§3.2), with
    its per-arm count published whether or not it ever fires." A code that is
    registered in §1a and absent from the published table is a code no reader
    of the results can see."""
    body = flatten(preregistration)
    assert "E2: authoring-validity profile" in body
    assert ("The table carries presence-idiom-unsound (§3.2), with its per-arm "
            "count published whether or not it ever fires") in body


def test_the_protocol_outcome_is_registered_and_is_not_an_admission_code(
        preregistration):
    """R1-5. The transcript binding's author-side verdict is an AUTHORING
    outcome — retained, counted, scoring zero — and it is NOT an admission code:
    it is read off the retained transcript, not off the artifact, so `admit()`
    can never return it."""
    registered = registered_authoring(preregistration)
    for code, _phrase in batch.AUTHORING_PROTOCOL_CODES:
        assert code in registered
        assert batch.CODE_PARTITION[code][0] == "authoring"
        assert code not in [name for name, _ in batch.AUTHORING_CODES]


def test_the_timeout_is_on_the_apparatus_side(preregistration):
    """The design-phase lesson, asserted rather than remembered: the pilot
    driver mis-filed timeouts as an authoring code, which silently moves a run
    out of the excluded set and into every rate's denominator."""
    registered = registered_apparatus(preregistration)
    assert "call timeout at the registered ceiling" in registered
    assert "call-timeout" not in registered_authoring(preregistration)
    assert batch.CODE_PARTITION["call-timeout"][0] == "apparatus"
    assert batch.WRAPPER_EXIT_MEANINGS[12][0] == "call-timeout"


def test_the_partition_is_exhaustive_and_disjoint(preregistration):
    apparatus = registered_apparatus(preregistration)
    authoring = registered_authoring(preregistration)
    assert sorted(phrase for side, phrase in batch.CODE_PARTITION.values()
                  if side == "apparatus") == sorted(apparatus)
    assert sorted(code for code, (side, _p) in batch.CODE_PARTITION.items()
                  if side == "authoring") == sorted(authoring)
    assert len(set(apparatus)) == len(apparatus)
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
    """The third diff §1a registers: every code `admit()` can return is a key of
    CODE_PARTITION, and every key is reachable."""
    score = pytest.importorskip("score")
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
    # 020's addition reaches the same side, which is what keeps a flagged run in
    # every ITT denominator scoring zero rather than leaving the population.
    assert "presence-idiom-unsound" in score.AUTHORING_SIDE
    from e4lib import admit as admit_lib
    assert set(admit_lib.DROP_ORDER) <= set(batch.CODE_PARTITION)
    assert admit_lib.DROP_ORDER[-1] == "presence-idiom-unsound"
