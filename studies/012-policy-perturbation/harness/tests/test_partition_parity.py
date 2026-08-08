#!/usr/bin/env python3
"""§3.3's partition and the scorer's are one list, or they are two claims and
the second one is prose.

§3.3 registers the partition exhaustively, code by code, and says in its own
text that "a harness test parses this table out of this file and diffs it
against the scorer's own partition table and against the codes its admission
can actually return". This is that test, and it is three-way on purpose:

  the PREREGISTRATION's table   ==   `score_rates.CODE_PARTITION`   ==   the
  codes `admit()` and `score_run()` can actually return

Two of the three would not be enough. A table that matches the file but names
a code no function returns is a registered outcome that cannot happen; a
function that returns a code the table does not carry is an outcome with no
registered partition, and §4.2's arithmetic would have nowhere to put it.

The table is located by its SHAPE — the pipe table whose header is
`| outcome | partition |` — so it is still found when the file is edited
above it, and a line number never becomes part of the registration.

Round 4, finding 7: the third leg is a REACHABILITY check and not a string
harvest. It walks the scorer's admission call graph — `admit()` and
`score_run()`, then every function in this module they call, transitively — and
collects the codes only from functions that walk reaches. A code returned from a
function nothing calls is dead code, and a partition whose third leg counted it
would certify a registered outcome that cannot happen, which is the first of the
two failures the three-way diff exists to catch.
"""
from __future__ import annotations
import ast

import fixtures
import score_rates

# §3.3: "Three codes are new to this study", each closing a route round 1 or
# round 2 found open. They are the reason C4 registers three extra fixtures,
# and the reason this file checks the table rather than trusting it.
NEW_CODES = ("arm-mismatch", "schedule-mismatch", "session-reused")
# §3.3's two valid outcomes, which carry no code: the row for a completion with
# no parseable array, and the row for an ordinary valid run.
VALID_ROWS = ("(no code, no parseable array)", "(no code)")


def partition_table(body: str) -> tuple:
    """({outcome: partition}, [the no-code rows]) as §3.3's table registers
    them, parsed out of the frozen preregistration by the table's shape."""
    for header, rows in fixtures.markdown_tables(body):
        if [fixtures.plain(cell) for cell in header] != ["outcome", "partition"]:
            continue
        codes, valid = {}, []
        for outcome, partition in rows:
            outcome = fixtures.plain(outcome)
            partition = fixtures.plain(partition)
            if outcome.startswith("("):
                valid.append((outcome, partition))
            else:
                codes[outcome.strip("`")] = partition
        return codes, valid
    raise AssertionError("§3.3's | outcome | partition | table is not in the "
                         "preregistration: the partition is not registered")


ADMISSION_ROOTS = ("admit", "score_run")


def _defined_functions(tree) -> dict:
    """{name: node} for every function the module defines, nested ones included
    — a call graph blind to a nested helper would be a call graph with a hole in
    it. Two definitions of one name would make the map ambiguous, so that is a
    failure here rather than a silent overwrite."""
    table: dict = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            assert node.name not in table, (
                "%s is defined twice: this walk resolves a call by name" % node.name)
            table[node.name] = node
    return table


def _own_body(node) -> list:
    """Every node in this function's body EXCEPT the bodies of the functions
    defined inside it. A nested definition is reached by CALLING it, which is
    the call graph's job; folding its body in here is exactly the conflation
    that let dead code count as reachable."""
    stack, own = list(node.body), []
    while stack:
        current = stack.pop()
        own.append(current)
        for child in ast.iter_child_nodes(current):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            stack.append(child)
    return own


def returnable_codes(source: str = None) -> set:
    """Every code the admission path can actually name, read off the source
    rather than off a comment: the first member of every tuple returned or
    assigned to the `(code, detail, empty)` triple, collected from `admit()`,
    `score_run()`, and every function in the module those two REACH by calling
    it — transitively, by a bare-name call.

    `source` defaults to the scorer's own bytes; the parameter exists so a test
    can hold this walk to a probe whose reachable and dead codes are known,
    because a reachability check nobody has run on a known answer is a claim
    about a walk rather than a walk.

    Calls through a module attribute (`records_compile.compile_records`) leave
    this module and are not followed: a code is this scorer's outcome only where
    this scorer names it, which is what `CODE_PARTITION` is a list of.
    """
    if source is None:
        with open(score_rates.__file__.replace(".pyc", ".py"), "rb") as handle:
            source = handle.read().decode("utf-8")
    tree = ast.parse(source)
    defined = _defined_functions(tree)
    codes, reached, queue = set(), set(), list(ADMISSION_ROOTS)
    while queue:
        name = queue.pop()
        if name in reached or name not in defined:
            continue
        reached.add(name)
        for inner in _own_body(defined[name]):
            if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name):
                queue.append(inner.func.id)
            value = getattr(inner, "value", None) if isinstance(
                inner, (ast.Return, ast.Assign)) else None
            if isinstance(value, ast.Tuple) and value.elts:
                first = value.elts[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    codes.add(first.value)
    return codes


# A probe with a known answer, held to the walk above: `admit()` calls one
# helper and not the other, so `session-count` is reachable and `dead-code` is a
# code no run can be given. The old harvest returned both.
REACHABILITY_PROBE = '''
def admit(slot):
    if not _regular(slot):
        return "slot-shape", "missing", False
    failure = _sessions(slot)
    if failure is not None:
        return failure
    return None, None, False


def _regular(path):
    return True


def _sessions(slot):
    return "session-count", "not the integer 1", False


def never_called(slot):
    return "dead-code", "no caller reaches this", False
'''


def test_the_registered_partition_is_the_scorers_partition(preregistration):
    registered, _valid = partition_table(preregistration)
    assert registered == score_rates.CODE_PARTITION, (
        "PREREGISTRATION.md §3.3 and score_rates.CODE_PARTITION disagree: %r"
        % sorted(set(registered.items()) ^ set(score_rates.CODE_PARTITION.items())))


def test_the_partition_is_exhaustive_over_one_class(preregistration):
    """Every code in §3.3's table is pipeline-invalid — the partition has one
    invalid class, and §4.2 counts it into the primary denominator rather than
    out of it, so a second class would silently change what a rate is over."""
    registered, _valid = partition_table(preregistration)
    assert set(registered.values()) == {"pipeline-invalid"}
    assert set(score_rates.CODE_PARTITION.values()) == {"pipeline-invalid"}


def test_the_reachability_walk_ignores_a_code_no_call_can_reach():
    """Round 4, finding 7: the promised reachability check was a string harvest,
    so a code placed in a function nothing calls read as an outcome a run can be
    given. The walk is held to a probe with a known answer — one helper called
    and one not — because a check that has never been shown to fire is prose.
    """
    assert returnable_codes(REACHABILITY_PROBE) == {"slot-shape", "session-count"}
    # Named the other way round as well, so the assertion above cannot pass by
    # collecting nothing at all: the dead code is in the source and not the set.
    assert "dead-code" in REACHABILITY_PROBE
    assert "dead-code" not in returnable_codes(REACHABILITY_PROBE)


def test_the_codes_the_scorer_can_return_are_the_codes_it_registers(preregistration):
    """The third leg of the three-way diff: what the admission path can name.

    `returnable_codes()` reaches the codes through the call graph (round 4,
    finding 7), so this is a statement about the codes a run can be given and
    not about the string literals the file contains.
    """
    registered, _valid = partition_table(preregistration)
    returnable = returnable_codes()
    assert returnable == set(score_rates.CODE_PARTITION), (
        "admit()/score_run() and CODE_PARTITION disagree: %r"
        % sorted(returnable ^ set(score_rates.CODE_PARTITION)))
    assert returnable == set(registered), (
        "admit()/score_run() and PREREGISTRATION.md §3.3 disagree: %r"
        % sorted(returnable ^ set(registered)))


def test_the_two_valid_outcomes_carry_no_code(preregistration):
    """§3.3's last two rows: a completion with no parseable JSON array is
    `authoring-empty` — valid, in every denominator, covering nothing — and an
    ordinary valid run carries no code either. Neither is a refusal, and the
    scorer names both."""
    _registered, valid = partition_table(preregistration)
    assert [row[0] for row in valid] == list(VALID_ROWS)
    assert "authoring-empty" in valid[0][1]
    assert "valid" in valid[1][1]
    assert score_rates.VALID_OUTCOMES == ("valid", "authoring-empty")
    for outcome in score_rates.VALID_OUTCOMES:
        assert outcome not in score_rates.CODE_PARTITION


def test_the_three_new_codes_are_registered_and_encoded(preregistration):
    """The three codes §3.3 marks as new to this study — the ones C4's extra
    fixtures exist for. They are in the table, they are in the scorer's
    partition, and `admit()` can actually return each of them."""
    registered, _valid = partition_table(preregistration)
    returnable = returnable_codes()
    for code in NEW_CODES:
        assert code in registered, code
        assert code in score_rates.CODE_PARTITION, code
        assert code in returnable, code
    # …and the preregistration marks exactly these three as new, in the
    # sentence that introduces them.
    introduction = preregistration.split("**Three codes are new to this study**")[1]
    introduction = introduction.split("Every other code")[0]
    named = [code for code in score_rates.CODE_PARTITION
             if "**`%s`**" % code in introduction]
    assert sorted(named) == sorted(NEW_CODES)


def test_the_partition_carries_no_code_the_prose_forgot(preregistration):
    """A code that appears in the table but nowhere in the file's prose is a
    code no reader was told about; a code in the prose that the table omits is
    an outcome with no partition. The first is what this checks, because the
    second is what the diff above already catches."""
    registered, _valid = partition_table(preregistration)
    for code in registered:
        assert "`%s`" % code in preregistration, code


def test_the_seal_failure_is_deliberately_not_a_code(preregistration):
    """§3.3's closing paragraph: a slot whose recomputed `SLOT-MANIFEST.json`
    disagrees with the ledger is NOT given a refusal code, because a code would
    understate it — it invalidates confirmatory scoring for the whole batch.
    The scorer's partition must therefore hold no manifest or chain code."""
    registered, _valid = partition_table(preregistration)
    assert not [code for code in registered
                if "manifest" in code or "seal" in code or "chain" in code]
    assert "One class of failure is deliberately *not* a refusal code" in preregistration
    # `verify_seal()` returns a SENTENCE and not a code, and `score()`'s caller
    # decides what the batch's verdicts are worth (C5 rule 6).
    assert score_rates.verify_seal.__doc__.strip().startswith(
        "None when this slot's seal holds, else the discrepancy in one sentence")
