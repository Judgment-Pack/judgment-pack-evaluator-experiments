#!/usr/bin/env python3
"""Which command-line flags name a place this harness WRITES — derived.

Round 18, finding 1. §2.10 rule 3 says every act from the freeze to publication
moves carrier or excluded bytes only, and round 17 built one general predicate
for it — `score_rates.require_lawful_destination()` — and then applied it at
three call sites chosen BY HAND. The record called that "general rather than
fourth" and "applied to every operator-supplied destination at once". It was
not: `batch.py capture --captures DIR` is a fourth, it was ungated, and staging
the attempts §8 retains beneath an in-study `--captures` moved the tree
manifest. Four rounds running, a class was repaired by listing its members and
the next round found the member the list missed.

So the members are not listed any more. This module walks the driver's and the
scorer's own sources and answers, for every `--flag` their `main()` reads, the
two questions the hand list was standing in for:

  1. does that flag's VALUE reach a call that creates a file, or the wrapper's
     slot argument — i.e. is it a destination at all?
  2. was the lawful-destination rule called with that same value on the way?

A flag that reaches a write and is not in the registered table fails BY NAME. A
FIFTH destination flag therefore arrives as a named failure, and so does a gate
deleted from any of the four.

KEYED ON (flag, entry function, formal), which is the shape `PARAMETER_ROOTS`
already uses and not the flag alone: `--out` names THREE different destinations
through three commands, and keyed by the flag they would be one row whose gate
could be deleted at two of the three sites invisibly. Measured: deleting the
gate at `batch.py:1946` flips `(--out, capture_golden, out_path)` and
`(--out, run_capture, out_path)` to UNGATED while
`(--out, capture_isolation_negative, out_dir)` stays green.

WHAT IS GENERIC AND WHAT IS NOT, the same division `gatescan.py` makes.
Generic and here: the seeding, the forward propagation, the interprocedural
binding, and the gate observation. Supplied by the caller, because they are the
scan's vocabulary and belong with the rest of it in `test_manifest.py`: which
calls create a file, which of those create at THIS call site (`open(p, "rb")`
does not), which calls are pure path arithmetic, which callee is the gate, and
which arguments are declared sinks because a process outside the AST writes
there.
"""
from __future__ import annotations
import ast


def dotted(node):
    """The dotted spelling of an expression (`x`, `x.y`, `x.y.z`), or None."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return None if base is None else base + "." + node.attr
    return None


def flag_literals(node) -> list:
    """Every `--flag` string constant inside an expression."""
    return [inner.value for inner in ast.walk(node)
            if isinstance(inner, ast.Constant)
            and isinstance(inner.value, str) and _is_flag(inner.value)]


def flag_reads(entry: ast.FunctionDef) -> dict:
    """{flag: [the call nodes that READ it]} inside one entry point.

    A flag is read by any call that carries its literal — `_argument(argv,
    "--captures", DEFAULT_CAPTURES)` in the driver, `options.get(
    "--emit-records")` in the scorer. The rule is the LITERAL and not a list of
    reader function names, because a list of reader names is the same
    enumeration one level down: `batch.py` hand-rolls `_argument()` and
    `score_rates.py` parses into a dict, and a third module would spell it a
    third way.

    A flag compared against `argv` without being read — `"--resume" in argv` —
    is registered with no reading call. It cannot be a destination (it has no
    value), and it is in the roster so that the flag census is the command
    line's own and not the destinations' subset.

    A `--…` literal carrying WHITESPACE is a sentence about a flag and not a
    flag: `raise BatchError("--scratch-parent is required")` is the live
    example. The test is the token's own shape, so no message has to be
    listed."""
    found = {}
    for node in ast.walk(entry):
        if isinstance(node, ast.Call):
            for argument in list(node.args) + [word.value
                                               for word in node.keywords]:
                if isinstance(argument, ast.Constant) \
                        and isinstance(argument.value, str) \
                        and _is_flag(argument.value):
                    found.setdefault(argument.value, []).append(node)
        elif isinstance(node, ast.Compare):
            for flag in flag_literals(node.left):
                found.setdefault(flag, [])
    return found


def _is_flag(text: str) -> bool:
    return text.startswith("--") and len(text) > 2 and not text.split() [1:] \
        and text == text.strip()


class Taint:
    """Forward taint from a set of seeds to every write, through one module.

    The propagation is deliberately small and deliberately stated. It follows
    assignment, `for` targets, walrus, pure path arithmetic, `%` formatting,
    f-strings, comprehensions, and calls to the module's own top-level
    functions — binding actuals to formals by position and by keyword, and
    taking a tainted `return` back as the call's own taint. That is what
    carries `attempt = next_attempt(captures_dir)` and `for slot in plan(...)`,
    which is the whole path from `--captures` to a written byte.

    It is a FIXED POINT and not a single pass, because the binding of a formal
    can taint a function this walk has already been through."""

    def __init__(self, tree: ast.Module, writers: dict, creates,
                 path_pure: frozenset, gate: str, declared_sinks: dict):
        self.functions = {node.name: node for node in tree.body
                          if isinstance(node, ast.FunctionDef)}
        self.writers = writers
        self.creates = creates
        self.path_pure = path_pure
        self.gate = gate
        self.declared_sinks = declared_sinks
        self.seeds = set()
        self.tainted_params = set()
        self.tainted_returns = set()
        self.sinks = []
        self.gated = set()
        # The bindings made in the ENTRY's own body: the first interprocedural
        # hop a flag's value takes, which is the key. Every hop below it is the
        # SAME destination seen further down its own call chain — `--captures`
        # binds `run_capture(captures_dir)` and then, through `plan()` and
        # `refuse_slot()`, `_write_json(path)` — and keying on those would put
        # one destination in the roster four times, each row UNGATED because
        # the gate is above the point it was seeded at.
        self.first_hop = set()
        self.entry = None
        self.current = None

    # --- one expression, given the tainted local names ----------------------

    def tainted(self, node, local: set) -> bool:
        if node is None:
            return False
        if any(node is seed for seed in self.seeds):
            return True
        if isinstance(node, ast.Name):
            return node.id in local
        if isinstance(node, ast.Call):
            name = dotted(node.func)
            if name in self.path_pure:
                return any(self.tainted(argument, local)
                           for argument in node.args)
            if name in self.functions:
                self.bind(name, node, local)
                return name in self.tainted_returns
            return False
        if isinstance(node, ast.BinOp):
            return (self.tainted(node.left, local)
                    or self.tainted(node.right, local))
        if isinstance(node, ast.BoolOp):
            return any(self.tainted(value, local) for value in node.values)
        if isinstance(node, ast.IfExp):
            return (self.tainted(node.body, local)
                    or self.tainted(node.orelse, local))
        if isinstance(node, (ast.ListComp, ast.GeneratorExp, ast.SetComp)):
            inner = set(local)
            for generator in node.generators:
                if self.tainted(generator.iter, local) \
                        and isinstance(generator.target, ast.Name):
                    inner.add(generator.target.id)
            return self.tainted(node.elt, inner)
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return any(self.tainted(item, local) for item in node.elts)
        if isinstance(node, ast.JoinedStr):
            return any(self.tainted(value, local) for value in node.values)
        if isinstance(node, ast.FormattedValue):
            return self.tainted(node.value, local)
        if isinstance(node, ast.Starred):
            return self.tainted(node.value, local)
        return False

    def bind(self, callee: str, call: ast.Call, local: set) -> None:
        """Actual arguments to formals, by position and by keyword."""
        node = self.functions[callee]
        formals = [argument.arg for argument in node.args.args]
        made = set()
        for index, actual in enumerate(call.args):
            if index < len(formals) and self.tainted(actual, local):
                made.add((callee, formals[index]))
        for word in call.keywords:
            if word.arg and self.tainted(word.value, local):
                made.add((callee, word.arg))
        self.tainted_params |= made
        if self.current is not None and self.current == self.entry:
            self.first_hop |= made

    # --- one function body --------------------------------------------------

    def walk(self, name: str) -> None:
        node = self.functions[name]
        self.current = name
        local = {formal for (function, formal) in self.tainted_params
                 if function == name}
        moved = True
        while moved:                       # a loop can taint its own target
            moved = False
            for statement in ast.walk(node):
                bound = None
                if isinstance(statement, ast.Assign) \
                        and len(statement.targets) == 1 \
                        and isinstance(statement.targets[0], ast.Name):
                    if self.tainted(statement.value, local):
                        bound = statement.targets[0].id
                elif isinstance(statement, (ast.For, ast.AsyncFor)) \
                        and isinstance(statement.target, ast.Name):
                    if self.tainted(statement.iter, local):
                        bound = statement.target.id
                elif isinstance(statement, (ast.NamedExpr, ast.AnnAssign)) \
                        and isinstance(statement.target, ast.Name):
                    if self.tainted(getattr(statement, "value", None), local):
                        bound = statement.target.id
                if bound is not None and bound not in local:
                    local.add(bound)
                    moved = True
        for call in [inner for inner in ast.walk(node)
                     if isinstance(inner, ast.Call)]:
            callee = dotted(call.func)
            if callee is None:
                continue
            if callee.rsplit(".", 1)[-1] == self.gate and call.args \
                    and self.tainted(call.args[0], local):
                self.gated.add(name)
            index = self.writers.get(callee)
            if index is not None and self.creates(call) \
                    and len(call.args) > index \
                    and self.tainted(call.args[index], local):
                self.sinks.append(("write", name, call.lineno,
                                   ast.unparse(call.args[index])))
            index = self.declared_sinks.get(callee)
            if index is not None and len(call.args) > index \
                    and self.tainted(call.args[index], local):
                self.sinks.append(("declared", name, call.lineno,
                                   ast.unparse(call.args[index])))
            if callee in self.functions:
                self.bind(callee, call, local)
        for statement in ast.walk(node):
            if isinstance(statement, ast.Return) \
                    and self.tainted(statement.value, local):
                self.tainted_returns.add(name)

    def run(self, seeds=(), params=(), entry: str = None, rounds: int = 12):
        """(sinks, gated functions) at the fixed point."""
        self.seeds = list(seeds)
        self.tainted_params = set(params)
        self.tainted_returns = set()
        self.first_hop = set()
        self.entry = entry
        for _ in range(rounds):
            before = (set(self.tainted_params), set(self.tainted_returns))
            self.sinks, self.gated = [], set()
            for name in list(self.functions):
                if name == entry or any(function == name for (function, _formal)
                                        in self.tainted_params):
                    self.walk(name)
            if (self.tainted_params, self.tainted_returns) == before:
                break
        return self.sinks, self.gated


def roster(source: str, entry: str, writers: dict, creates,
           path_pure: frozenset, gate: str, declared_sinks: dict) -> dict:
    """{(flag, entry function, formal): (True if gated, ((kind, function, line,
    text), …))} for every flag whose value reaches a write.

    Two passes, and the second is what the keying costs. The first seeds the
    reading calls inside `main()` and records which (function, formal) each
    flag's value binds to on its FIRST hop out of the entry; the second re-runs
    the analysis for ONE of those bindings at a time, so a flag that names
    three destinations through three commands produces three rows and a gate
    deleted at one of them is one row's failure."""
    tree = ast.parse(source)

    def build():
        return Taint(tree, writers, creates, path_pure, gate, declared_sinks)

    readers = set()
    found = {}
    for flag, reads in sorted(flag_reads(build().functions[entry]).items()):
        found.setdefault(flag, [])
        if not reads:
            continue
        probe = build()
        readers |= {dotted(call.func) for call in reads
                    if dotted(call.func) in probe.functions}
        probe.run(seeds=reads, entry=entry)
        found[flag] = sorted(probe.first_hop)
    rows = {}
    for flag, bindings in sorted(found.items()):
        for function, formal in bindings:
            if function in readers:
                continue                   # the reader's own parameter
            one = build()
            sinks, gated = one.run(params={(function, formal)})
            if not sinks:
                continue
            rows[(flag, function, formal)] = (
                bool(gated), tuple(sorted(set(sinks))))
    return rows
