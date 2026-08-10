#!/usr/bin/env python3
"""The gate derivation, once, for every module that has gates.

Round 16 built a derived pre-call ledger over `harness/batch.py` and recorded,
honestly, that `score_rates.verify_preconditions()` kept "the identical
silent-omission property". Round 17, finding 3 measured what that cost: TWELVE
of that function's twenty-three refusal sites can be removed together with
`harness/integrity.py` exiting 0 and the pinned suite unmoved, and the record
said three — a number that appears nowhere in the tree and could not be
checked. Four of the twenty-three are covered by name; eight more are driven
only through a needle (`"VERDICT.json"`) that all eight of them carry, so ten
cases prove that the C7 block refuses and none of them can say which gate did.

This module is the half of that derivation that is not about `batch.py`. It is
here rather than in `test_batch.py` because the alternative was a second copy
of two hundred and fifty lines of AST walking, and "two hand-kept builders and
two hand-kept guards" is the pattern `test_manifest.py` already records as this
sequence's signature defect. A THIRD site is sized and waiting —
`collect_slots`, `terminality`, `load_ledger` and `check_population` run twenty
more refusal sites before `score()` reads a slot — and it should cost a table,
not a rewrite.

WHAT IS GENERIC AND WHAT IS NOT. Generic: reading a module's own source,
deciding whether a callee can raise (transitively), labelling a refusal by the
`if` or the `except` that guards it, reading the constant head of a refusal
message, and the two structural rules round 17 added — compound-statement
HEADERS are scanned, and an `except` handler labels its own body. Not generic,
and therefore supplied by the caller: which callees count as gates, what a
`preflight()` delegation means, where a call is SPENT, and which `if` is a
dispatch rather than a gate. Those enter through `classify` and `narrow`.
"""
from __future__ import annotations
import ast


def module_functions(tree: ast.Module) -> dict:
    """{name: node} for the module's own top-level functions."""
    return {node.name: node for node in tree.body
            if isinstance(node, ast.FunctionDef)}


def parse(path: str) -> ast.Module:
    """A module's own source, read from the file the tests import and
    `integrity.verify()` pins — not a second copy."""
    with open(path.replace(".pyc", ".py"), "rb") as handle:
        return ast.parse(handle.read().decode("utf-8"))


def is_raise_of(node: ast.Raise, exception: str) -> bool:
    """Whether a `raise` names this module's own refusal type."""
    if node.exc is None:
        return False
    raised = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
    return isinstance(raised, ast.Name) and raised.id == exception


def raised_literal(node: ast.Raise):
    """The refusal STRING a `raise X(...)` carries, or None.

    `"…%s…" % (values)` is read down to its literal left side: the needle a
    test asserts can only ever be a constant fragment of the message."""
    if not isinstance(node.exc, ast.Call) or not node.exc.args:
        return None
    argument = node.exc.args[0]
    while isinstance(argument, ast.BinOp) and isinstance(argument.op, ast.Mod):
        argument = argument.left
    if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
        return argument.value
    return None


def can_raise(name: str, functions: dict, exception: str,
              seen=frozenset()) -> bool:
    """Whether calling `name` can raise `exception`, directly or through
    another module-level function of the same file.

    Refusal CAPABILITY is transitive; gate IDENTITY is not. Keeping those two
    apart is what stops a depth-one gate set from either missing a gate that
    refuses through a helper or counting that helper as a gate of its own."""
    node = functions.get(name)
    if node is None or name in seen:
        return False
    for inner in ast.walk(node):
        if isinstance(inner, ast.Raise) and is_raise_of(inner, exception):
            return True
        if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) \
                and can_raise(inner.func.id, functions, exception,
                              seen | {name}):
            return True
    return False


def callee_gates(host: ast.FunctionDef, functions: dict, exception: str,
                 skip=(), limit=None) -> tuple:
    """The gate FUNCTIONS one host runs: its own direct module-level callees
    that can refuse, above `limit` when a limit is given.

    DEPTH ONE, and deliberately. A literal transitive closure would reach every
    function a gate reaches and count each as a gate in its own right while its
    caller is already ledgered as one."""
    return tuple(sorted(
        {node.func.id for node in ast.walk(host)
         if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
         and node.func.id in functions and node.func.id not in skip
         and (limit is None or node.lineno < limit)
         and can_raise(node.func.id, functions, exception)}))


def sites_in(function: ast.FunctionDef, exception: str, classify,
             narrow=None, context=None) -> list:
    """[(kind, label, line, context, literal)] for one function body.

    `kind` is "inline" for a `raise` the function makes itself, or whatever
    `classify(call)` returns for a call it makes. An inline gate's LABEL is the
    source of the `if` that guards it, unparsed: a line number would move under
    every edit above it and a message would make the needle test circular, so
    the condition is what a reader identifies the gate by, and rewording it is
    an edit to the ledger — which is the point.

    `classify(call)` returns (kind, label) for a call that is a site, or None.
    `narrow(test, context)` returns (context for the body, context for the
    orelse) when an `if` selects a PATH rather than guarding a gate, else None;
    a selecting `if` leaves the guard label alone and changes the context.

    TWO STRUCTURAL RULES, both added by round 17 and both load-bearing.

    COMPOUND-STATEMENT HEADERS ARE SCANNED. The walk used to recurse into
    `If`/`For`/`While`/`With` BODIES and never inspect `If.test`, `For.iter`,
    `While.test` or `With.items`, so a call in a header was invisible. That is
    live, not hypothetical: `batch.capture_slots()` — the gate `batch.py`'s own
    docstring names as the one that keeps a golden capture from being derived
    from the batch's own runs — is the iterator of a `for` loop, so widening
    the gate set without this would have put it in the gate set and produced no
    cell for it: a gate function with no site.

    AN `except` HANDLER LABELS ITS OWN BODY. Handler bodies used to inherit the
    enclosing guard, so two handlers under one guard collapsed into one cell
    and a gate disappeared silently. `score_rates.verify_preconditions()` has
    exactly that shape — two top-level `except` raises, both inheriting
    `"<unguarded>"` — so mirroring the derivation without this fix would have
    reproduced, at the second site, the defect it exists to abolish: its
    twenty-three raise sites collapse to twenty-two keys.
    """
    found = []

    def record(node, guard, context):
        for inner in ast.walk(node):
            if isinstance(inner, ast.Raise) and is_raise_of(inner, exception):
                found.append(("inline", guard, inner.lineno, context,
                              raised_literal(inner)))
            if not isinstance(inner, ast.Call):
                continue
            site = classify(inner)
            if site is not None:
                found.append((site[0], site[1], inner.lineno, context, None))

    def visit(statements, guard, context):
        for statement in statements:
            if isinstance(statement, ast.Raise):
                if is_raise_of(statement, exception):
                    found.append(("inline", guard, statement.lineno, context,
                                  raised_literal(statement)))
                continue
            if isinstance(statement, ast.If):
                # the header runs before either arm, under the enclosing guard
                record(statement.test, guard, context)
                selected = narrow(statement.test, context) if narrow else None
                if selected is not None:
                    visit(statement.body, guard, selected[0])
                    visit(statement.orelse, guard, selected[1])
                    continue
                visit(statement.body, ast.unparse(statement.test), context)
                visit(statement.orelse,
                      "not (%s)" % ast.unparse(statement.test), context)
                continue
            if isinstance(statement, (ast.For, ast.While, ast.With)):
                for header in ([statement.iter] if isinstance(statement, ast.For)
                               else [statement.test]
                               if isinstance(statement, ast.While)
                               else [item.context_expr
                                     for item in statement.items]):
                    record(header, guard, context)
                visit(statement.body, guard, context)
                visit(getattr(statement, "orelse", []) or [], guard, context)
                continue
            if isinstance(statement, ast.Try):
                visit(statement.body, guard, context)
                for handler in statement.handlers:
                    visit(handler.body,
                          ("except %s" % ast.unparse(handler.type)
                           if handler.type is not None else "except"), context)
                visit(statement.orelse, guard, context)
                visit(statement.finalbody, guard, context)
                continue
            record(statement, guard, context)

    visit(function.body, "<unguarded>", context)
    return found


def gate_identity(site: tuple) -> tuple:
    """The gate a site IS, with the host dropped where the host is not part of
    its identity. A gate FUNCTION is one gate however many callers it has,
    while an inline `if … raise` belongs to the function it is written in, and
    two functions can guard on the same condition."""
    host, kind, label = site
    return ("gate", label) if kind == "gate" else ("inline", host, label)


def refusal_literals(hosts: dict, gates: tuple, functions: dict,
                     exception: str, classify) -> dict:
    """{gate identity: (refusal string, …)} — the messages each gate raises,
    read out of the module's own source. A gate FUNCTION owns every `raise` in
    its body; an inline gate owns the raises its own `if` guards.

    Over the UNION gate set and every host, never one host's. The needle test
    is a claim that no OTHER gate can supply a case's needle, and a universe
    that is a fraction of the module's refusals cannot support it."""
    literals = {}
    for host, node in sorted(hosts.items()):
        for kind, label, _line, _context, literal in sites_in(
                node, exception, classify):
            if kind != "inline" or literal is None:
                continue
            literals.setdefault(("inline", host, label), []).append(literal)
    for gate in gates:
        literals[("gate", gate)] = [
            text for text in
            (raised_literal(node) for node in ast.walk(functions[gate])
             if isinstance(node, ast.Raise) and is_raise_of(node, exception))
            if text]
    return {key: tuple(value) for key, value in literals.items()}


class Gate:
    """One row of a ledger: how a cell is held, and by what name.

    `how` is "command" when the cell is driven through the registered
    interface — the strongest form, because deleting the gate makes that
    command SUCCEED; "residual" when the cell is derived but not driven, in
    which case `why` states what does hold the gate today. A residual row is a
    DECLARED gap: the derivation still refuses to let the cell disappear.
    `batch.py`'s ledger carries a third value, "preflight", for a cell the
    command line cannot reach because a gate above it refuses first.

    `recipe` is the method that leaves this one gate unmet. `None` means the
    ceremony step is simply not taken — the strictly better form, since then
    the only difference between the refusing run and the admitting one is the
    registered act itself.

    `shared` names the other gates whose refusal messages also contain this
    row's needle. It is almost always empty; where it is not, the collision is
    recorded rather than discovered later, because a needle another gate can
    supply is how a case goes vacuous (round 16, finding 2)."""

    def __init__(self, how, named=None, recipe=None, shared=(), why=None):
        self.how = how
        self.named = named
        self.recipe = recipe
        self.shared = tuple(shared)
        self.why = why
