#!/usr/bin/env python3
"""Is "deleting X turns this red" TRUE? — executed, not asserted.

Round 18, finding 2. A probe was written to prove mutation-redness, said in its
own docstring that it drove "the real entry point and not the predicate
underneath it", and drove an intermediate: deleting `score_registered()`'s one
call to `_check_records_target()` left `harness/integrity.py` at exit 0 and the
whole pinned suite at 315 passed with 177 subtests, taking BOTH halves of
§2.10 rule 3's destination rule out together. The claim was a sentence, and a
sentence about a mechanism is what rounds 15, 16, 17 and 18 have each found
drifting from the mechanism.

So the claim is run. For a rule reached from a registered entry, this module
derives the CHAIN of calls from that entry down to the gate out of the module's
own source, builds the one-edge MUTANT for each link, and lets the case re-run
against it. A case that still refuses under the mutant is a case that was not
testing that link.

THE GENERAL RULE THIS ESTABLISHES, and the one worth registering: a "deleting X
turns this red" claim is checkable exactly when X is a DERIVED edge on the path
from a derived entry to the gate, and the check is to build the one-edge mutant
and re-run the case. A redness claim that cannot be stated as an edge on a
derived chain is an assertion, and belongs in the record as a residual with its
reason rather than as a claim.

WHAT IT DOES NOT DO, and each of these is why the ledgers in `test_batch.py`
and `test_admission.py` are not replaced by it:
  * THE MUTATION OPERATOR IS CALL-DELETION ONLY. A gate weakened in place — a
    predicate inverted, a `startswith` limb dropped, `is_file=True` flipped —
    is a different operator and is not covered here. Nor is a VALUE edge:
    `results = score_registered(…)` cannot be deleted and still compile, which
    is exactly why a drive must START at the registered entry rather than
    mutate the edge into it. The top edge of any chain is covered by
    construction — you cannot delete the point you drive from — and by nothing
    else; this module reports such edges by name rather than passing over them.
  * IT PROTECTS ONLY CHAINS A PROBE DRIVES. A gate no case drives has no chain
    to walk, and what holds it is the derived ledger's key set and site count.
  * EQUIVALENT MUTANTS. If a chain ever carries two calls to one gate, deleting
    one is behaviour-preserving and the case will report a link as uncovered.
    That is a finding, not a tuning knob, and there is no exception table here
    to put it in.
  * THE MUTANT RUNS UNPINNED BYTES, IN MEMORY. It is compiled from the pinned
    source with one call removed, executed into a throwaway module object whose
    `__file__` is the real path so the module's own study derivation still
    resolves, never written to disk, never inserted into `sys.modules`, and
    discarded. "The bytes that run are the pinned bytes" is registered, and
    this is the one place in the suite where a modified compilation runs at
    all, so it says so here rather than being noticed later.
"""
from __future__ import annotations
import ast
import types

import gatescan


def call_edges(universe: gatescan.Universe, host: str, module: str = None):
    """[(callee spelling, line, is a bare statement)] for every call a host
    makes to a function this universe can resolve, in source order."""
    found = []
    node = universe.resolve(host, module)[1]
    bare = {id(statement.value) for statement in ast.walk(node)
            if isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Call)}
    for call in ast.walk(node):
        if not isinstance(call, ast.Call):
            continue
        callee = gatescan.dotted(call.func)
        if callee is None or universe.resolve(callee, module) is None:
            continue
        found.append((callee, call.lineno, id(call) in bare))
    return sorted(found, key=lambda row: row[1])


def chain_to(universe: gatescan.Universe, entry: str, gate: str,
             module: str = None) -> list:
    """The shortest call path from `entry` down to `gate`, as
    [(module, host, callee, line, deletable)] — read out of the modules' own
    source and not written down anywhere.

    `gate` is matched on its last dotted component, because a rule is spelled
    `require_lawful_destination` inside its own module and
    `score_rates.require_lawful_destination` outside it and both are the same
    function."""
    start = (module or universe.root, entry)
    queue = [(start, [])]
    seen = {start}
    while queue:
        (home, host), path = queue.pop(0)
        for callee, line, deletable in call_edges(universe, host, home):
            target = universe.resolve(callee, home)
            step = path + [(home, host, callee, line, deletable)]
            if callee.rsplit(".", 1)[-1] == gate:
                return step
            key = (target[0], target[1].name)
            if key in seen:
                continue
            seen.add(key)
            queue.append((key, step))
    return []


def mutant(module, host: str, callee: str, line: int):
    """`module`'s own source with ONE call deleted, compiled and executed into
    a throwaway module object.

    The deletion is of the STATEMENT, not of the expression: a bare `Expr` call
    is dropped and any block it empties is `pass`-filled, so the result
    compiles and every other byte of the module is what the file holds. A call
    that is not a bare statement is not deletable and is refused here rather
    than being silently skipped — see this module's own limits."""
    with open(module.__file__, "rb") as handle:
        source = handle.read().decode("utf-8")
    tree = ast.parse(source)
    removed = []

    class Cut(ast.NodeTransformer):
        def visit_Expr(self, node):
            if isinstance(node.value, ast.Call) \
                    and node.value.lineno == line \
                    and gatescan.dotted(node.value.func) == callee:
                removed.append(line)
                return None
            return node

    for definition in tree.body:
        if isinstance(definition, ast.FunctionDef) and definition.name == host:
            Cut().visit(definition)
    if len(removed) != 1:
        raise AssertionError(
            "%s.py:%d %s() -> %s is not one deletable statement (%d found): a "
            "redness claim about an edge this cannot cut is an assertion and "
            "has to be recorded as one"
            % (module.__name__, line, host, callee, len(removed)))
    _fill(tree)
    code = compile(ast.fix_missing_locations(tree), module.__file__, "exec")
    replacement = types.ModuleType(module.__name__)
    replacement.__file__ = module.__file__
    exec(code, replacement.__dict__)       # noqa: S102 — see this file's limits
    return replacement


def _fill(node) -> None:
    """`pass` into any block the cut emptied.

    `body` only. An empty `orelse` or `finalbody` is what those fields hold
    when the source never had one, and filling them turns a bare `try:` into
    `try: … else: pass`, which will not compile."""
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            if field == "body" and not value:
                value.append(ast.Pass())
            for item in value:
                if isinstance(item, ast.AST):
                    _fill(item)
        elif isinstance(value, ast.AST):
            _fill(value)
