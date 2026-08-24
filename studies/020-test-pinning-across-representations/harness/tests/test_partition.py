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

STUDY 020, §7 DELTA 3 — THE AUTHORING SIDE IS A TABLE NOW
---------------------------------------------------------
019's §1a registered its authoring outcomes as a comma list inside one
sentence, and this module diffed that sentence against `batch.AUTHORING_CODES`'
phrases. 020's §1a registers them as a TABLE with three columns — the code, the
arms it can reach, and a meaning — because `presence-idiom-unsound` (§3.2) is
arm-asymmetric and a comma list has nowhere to say so.

The diff moved with it, and it got stronger rather than weaker: the CODE column
is diffed against the code partition, and the ARMS column is diffed against
`e4lib/admit.py`'s `ARM_REACHABLE_CODES` — which is the fact §5's
"arm-structural categories within-arm-only" turns on, and which 019 could only
assert in code against itself. The old sentence's PHRASES are no longer the
diffed thing on the authoring side: the table's meaning column is prose written
for a reader ("new in 020 — §3.2's registered presence-idiom guard fires"), not
a label, and pretending it is one would be a diff that agrees by copying.

R1-5's `author-protocol-violation` is a row of that table too, and 020 has no
separate sentence for it. What made it special is unchanged and is asserted
directly instead: it is an AUTHORING outcome that `admit()` can never return,
because it is read off the retained transcript rather than off the artifact.
"""
import re

import pytest

import batch
from e4lib import admit as admit_lib

SECTION = re.compile(r"\n## 1a\. (.*?)(?=\n## )", re.DOTALL)
APPARATUS = re.compile(r"Apparatus failures — (.+?) — are pipeline-invalid")
# §1a's authoring-outcome table, identified by its header row.
TABLE_HEADER = "| code | arms it can reach | meaning |"
# The one authoring outcome the admission layer cannot produce.
PROTOCOL_CODE = "author-protocol-violation"


def authoring_table(preregistration):
    """`[(code, (arms…), meaning), …]` from §1a's registered table.

    The header row must be unique IN THE WHOLE FILE, not merely in §1a: a second
    table with the same columns elsewhere would make "the authoring outcomes"
    ambiguous, and this module would then be reading whichever one it found
    first."""
    assert preregistration.count(TABLE_HEADER) == 1, (
        "PREREGISTRATION.md holds %d tables headed %r; §1a's authoring-outcome "
        "table is identified by that row"
        % (preregistration.count(TABLE_HEADER), TABLE_HEADER))
    body = section(preregistration, flattened=False)
    assert TABLE_HEADER in body, \
        "§1a does not carry the authoring-outcome table this module diffs"
    rows = []
    started = False
    for line in body.splitlines():
        line = line.strip()
        if line == TABLE_HEADER:
            started = True
            continue
        if not started:
            continue
        if not line.startswith("|"):
            break
        cells = [cell.strip().replace("*", "").replace("`", "")
                 for cell in line.strip("|").split("|")]
        if len(cells) != 3 or set(cells[0]) <= set("-: "):
            continue
        rows.append((cells[0], tuple(arm.strip() for arm in cells[1].split(",")),
                     cells[2]))
    assert rows, "§1a's authoring-outcome table has no rows"
    return rows


def flatten(text):
    """One line, emphasis and code ticks removed: the registration's wrapping
    and bolding are not differences."""
    return " ".join(text.replace("*", "").replace("`", "").split())


def section(preregistration, flattened=True):
    found = SECTION.findall("\n" + preregistration)
    assert len(found) == 1, (
        "PREREGISTRATION.md holds %d sections numbered 1a; the population rule "
        "is identified by that heading" % len(found))
    return flatten(found[0]) if flattened else found[0]


def apparatus_list(preregistration):
    body = section(preregistration)
    matches = APPARATUS.findall(body)
    assert len(matches) == 1, (
        "§1a holds %d apparatus lists; the pipeline-invalid side is identified "
        "by that sentence" % len(matches))
    return [item.strip() for item in matches[0].split(",")]


def registered_authoring_codes(preregistration):
    return [code for code, _arms, _meaning
            in authoring_table(preregistration)]


def test_the_apparatus_list_is_the_codes(preregistration):
    assert apparatus_list(preregistration) == \
        [phrase for _code, phrase in batch.APPARATUS_CODES]


def test_the_authoring_table_is_the_codes(preregistration):
    """§1a's table, code column, against the code partition's authoring side —
    both admission codes and the transcript binding's one. §7 delta 3's
    `presence-idiom-unsound` is a row here whether or not §3.2's gate ever
    opens, so the code cannot be added to the harness without the registration
    naming it, or named without the harness carrying it.

    AS A SET, deliberately. §1a's sentence is "the registered authoring-outcome
    codes are", and its table groups the transcript binding's code beside the
    admission codes while the harness keeps them in two tuples for the reason
    the test below asserts. The PUBLICATION order is `DROP_ORDER`'s and is
    pinned where E2's table is built, not here."""
    assert sorted(registered_authoring_codes(preregistration)) == \
        sorted([code for code, _phrase in batch.AUTHORING_CODES]
               + [code for code, _phrase in batch.AUTHORING_PROTOCOL_CODES])


def test_the_tables_arms_column_is_the_arm_structural_rule(preregistration):
    """§5's "arm-structural categories within-arm-only, enforced in the scorer",
    diffed against the registration instead of against another copy of itself.
    `presence-idiom-unsound` is B and C (§3.2, §11.11); `schema-invalid-pack` is
    A; `opa-check-failed` and `v0-syntax` are B and C. 019 could assert those
    only in code."""
    for code, arms, _meaning in authoring_table(preregistration):
        if code == PROTOCOL_CODE:
            continue
        reached = tuple(arm for arm in batch.ARMS
                        if code in admit_lib.ARM_REACHABLE_CODES[arm])
        assert arms == reached, code


def test_the_protocol_outcome_is_an_authoring_code_admit_cannot_return(
        preregistration):
    """R1-5. The transcript binding's author-side verdict is an AUTHORING
    outcome — retained, counted, scoring zero — and `admit()` can never return
    it: it is read off the retained transcript, not off the artifact. 020 gives
    it a table row rather than a sentence, and its "arms it can reach" cell is
    all three, which is exactly why it cannot be diffed against
    `ARM_REACHABLE_CODES` above."""
    rows = {code: arms for code, arms, _meaning
            in authoring_table(preregistration)}
    assert rows[PROTOCOL_CODE] == tuple(batch.ARMS)
    for code, _phrase in batch.AUTHORING_PROTOCOL_CODES:
        assert batch.CODE_PARTITION[code][0] == "authoring"
        assert code not in [name for name, _ in batch.AUTHORING_CODES]
        assert code not in admit_lib.DROP_ORDER


def test_the_timeout_is_on_the_apparatus_side(preregistration):
    """The design-phase lesson, asserted rather than remembered: the pilot
    driver mis-filed timeouts as an authoring code, which silently moves a run
    out of the excluded set and into every rate's denominator."""
    assert "call timeout at the registered ceiling" in \
        apparatus_list(preregistration)
    assert "call-timeout" not in registered_authoring_codes(preregistration)
    assert batch.CODE_PARTITION["call-timeout"][0] == "apparatus"
    assert batch.WRAPPER_EXIT_MEANINGS[12][0] == "call-timeout"


def test_the_partition_is_exhaustive_and_disjoint(preregistration):
    """Both registered sides against the whole partition. The apparatus side is
    matched by PHRASE, which is how §1a spells it; the authoring side by CODE,
    which is how §1a's table spells it."""
    apparatus = apparatus_list(preregistration)
    authoring = registered_authoring_codes(preregistration)
    assert sorted(phrase for side, phrase in batch.CODE_PARTITION.values()
                  if side == "apparatus") == sorted(apparatus)
    assert sorted(code for code, (side, _phrase) in batch.CODE_PARTITION.items()
                  if side == "authoring") == sorted(authoring)
    assert len(set(apparatus)) == len(apparatus)
    assert len(set(authoring)) == len(authoring)
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
