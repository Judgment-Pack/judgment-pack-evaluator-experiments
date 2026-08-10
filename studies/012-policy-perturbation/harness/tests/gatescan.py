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

ROUND 18, FINDING 1 widened two things that had been narrow in the same way.

THE SPELLING. Every callee test here used to be `isinstance(node.func,
ast.Name)`, so a callee written `score_rates.require_lawful_destination(…)`
was invisible — to `can_raise()`, to `callee_gates()`, and therefore to both
ledgers. That was not a theoretical gap: round 17's own new rule, the one its
disposition called "general rather than fourth", is spelled that way at both of
its call sites in `batch.py`, so the derived ledger held ZERO cells for it and
the whole rule rested on three hand-listed behavioural pairs. A callee is
resolved by its DOTTED spelling now, through `Universe` below, which follows an
`import` into the sibling module the caller names.

THE REFUSAL VOCABULARY. A ledger over one exception name is a ledger over one
module's refusals, and `batch.py main()` answers `refused: …` for three types,
not one. `refusal_types()` reads that set out of the entry's own `except`
clause rather than taking it as an argument, so a driver that starts catching a
fourth refusal type widens its own gate set by being written, not by being
listed here.
"""
from __future__ import annotations
import ast
import os


def dotted(node):
    """The dotted spelling of a callee (`x`, `x.y`, `x.y.z`), or None for a
    callee that is computed rather than named."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return None if base is None else base + "." + node.attr
    return None


def module_functions(tree: ast.Module) -> dict:
    """{name: node} for the module's own top-level functions."""
    return {node.name: node for node in tree.body
            if isinstance(node, ast.FunctionDef)}


_PARSED = {}


def parse(path: str) -> ast.Module:
    """A module's own source, read from the file the tests import and
    `integrity.verify()` pins — not a second copy.

    Memoised on the file's own (path, mtime, size), because the derivations
    above re-read their subject on every call by design and round 18 gave them
    a second module to read: `score_rates.py` is 300 KB and the driver's ledger
    parses its universe once per host per cell. The memo is keyed on the file's
    STAMP and not on its name, so an edited source is re-read — the property
    "this reads the file the tests import" is unchanged, and only the count of
    times it is decoded moves."""
    source = path.replace(".pyc", ".py")
    stamp = os.stat(source)
    key = (os.path.realpath(source), stamp.st_mtime_ns, stamp.st_size)
    if key not in _PARSED:
        with open(source, "rb") as handle:
            _PARSED[key] = ast.parse(handle.read().decode("utf-8"))
    return _PARSED[key]


class Universe:
    """Every module-level function a module can reach BY NAME — its own, and
    the sibling harness modules it imports — keyed by the spelling the CALLER
    writes.

    The alternative was to keep resolving `ast.Name` only and to write the
    limitation into a docstring, which is what round 17 did and what round 18
    found. A dotted callee is resolved here the way the interpreter resolves
    it: `import score_rates` binds the name `score_rates` to that file, so
    `score_rates.require_lawful_destination` names a function whose body this
    can read, and a spelling that resolves to nothing on disk resolves to
    nothing here either.

    It follows `import <sibling>` only. `from x import y`, `import x as y` and
    any package import are deliberately NOT followed: `test_manifest.py`'s
    binding discipline is what keeps the harness's own sources to the one
    spelling this can read, and a resolver that guessed at the others would be
    claiming a reach it does not have. A callee it cannot resolve is not a
    gate, which is the same fail-quiet the depth-one rule already has and is
    stated in both ledgers' own limits."""

    def __init__(self, path: str):
        self.root = os.path.splitext(os.path.basename(path))[0]
        self._functions = {}
        self._aliases = {}
        self._load(self.root, path)

    def _load(self, key: str, path: str) -> None:
        if key in self._functions:
            return
        tree = parse(path)
        self._functions[key] = module_functions(tree)
        self._aliases[key] = {}
        directory = os.path.dirname(os.path.abspath(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Import):
                continue
            for alias in node.names:
                if alias.asname is not None or "." in alias.name:
                    continue
                sibling = os.path.join(directory, alias.name + ".py")
                if os.path.isfile(sibling):
                    self._aliases[key][alias.name] = alias.name
                    self._load(alias.name, sibling)

    def functions(self, module: str = None) -> dict:
        """{name: node} for one module's own top-level functions."""
        return self._functions[module or self.root]

    def resolve(self, spelling, module: str = None):
        """(module key, function node) for a dotted callee written inside
        `module`, or None when it names no module-level function this can
        read."""
        if spelling is None:
            return None
        home = module or self.root
        parts = spelling.split(".")
        if len(parts) == 1:
            node = self._functions.get(home, {}).get(parts[0])
            return (home, node) if node is not None else None
        if len(parts) == 2:
            target = self._aliases.get(home, {}).get(parts[0])
            if target is not None:
                node = self._functions.get(target, {}).get(parts[1])
                return (target, node) if node is not None else None
        return None


def refusal_types(function: ast.FunctionDef) -> tuple:
    """The refusal type NAMES an entry point answers with, read out of its own
    `except` clause.

    `batch.main()` catches `(BatchError, score_rates.ScoreError,
    transcript_check.TranscriptError)` and prints all three as `refused: …`, so
    all three are refusals an operator meets and a gate that raises any of them
    is a gate. Taking the set from the source rather than from an argument is
    what makes a fourth one arrive by being caught rather than by being written
    down here. Matched on the LAST dotted component, because the same type is
    spelled `ScoreError` inside its own module and `score_rates.ScoreError`
    outside it."""
    names = []
    for node in ast.walk(function):
        if not isinstance(node, ast.ExceptHandler) or node.type is None:
            continue
        for item in (node.type.elts if isinstance(node.type, ast.Tuple)
                     else [node.type]):
            spelling = dotted(item)
            if spelling is not None:
                names.append(spelling.rsplit(".", 1)[-1])
    return tuple(sorted(set(names)))


def entry_points(main: ast.FunctionDef, functions: dict) -> tuple:
    """Every module-level function `main()` calls itself — the entries a
    registered command line reaches directly, whether the module dispatches
    five commands or one.

    Round 18, finding 2: a behavioural probe that names a function BELOW one of
    these is a probe bound at the wrong depth on its own call chain, and the
    wiring above it can then be deleted with the suite green — measured, at
    `score_rates.py:4711-4712`, against a docstring claiming the opposite. The
    legal set of drive targets is COMPUTED from the module's own dispatch here
    rather than written down anywhere, so a probe that binds to a helper fails
    by name at collection."""
    return tuple(sorted({dotted(node.func) for node in ast.walk(main)
                         if isinstance(node, ast.Call)
                         and dotted(node.func) in functions}))


def is_raise_of(node: ast.Raise, exceptions) -> bool:
    """Whether a `raise` names one of the refusal types under derivation.

    Compared on the last dotted component: a module raises its own error by its
    bare name and a caller catches it through the module's, and both spellings
    are the same type."""
    if node.exc is None:
        return False
    if isinstance(exceptions, str):
        exceptions = (exceptions,)
    raised = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
    spelling = dotted(raised)
    return spelling is not None and spelling.rsplit(".", 1)[-1] in exceptions


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


def can_raise(spelling: str, universe: Universe, exceptions,
              module: str = None, seen=frozenset()) -> bool:
    """Whether calling `spelling` can raise one of `exceptions`, directly or
    through another module-level function it in turn calls — including one in
    a sibling module it reaches by its dotted name.

    Refusal CAPABILITY is transitive; gate IDENTITY is not. Keeping those two
    apart is what stops a depth-one gate set from either missing a gate that
    refuses through a helper or counting that helper as a gate of its own.

    The walk is INTERMODULAR because the capability is: `batch.capture_golden()`
    refuses an unlawful `--out` by calling into `score_rates`, and a walk that
    stopped at `batch.py`'s own top-level names would report that call as
    incapable of refusing anything. Each callee is resolved relative to the
    module whose body is being read, so a bare name inside `score_rates` means
    a `score_rates` function and not a `batch` one."""
    found = universe.resolve(spelling, module)
    if found is None:
        return False
    home, node = found
    if (home, node.name) in seen:
        return False
    for inner in ast.walk(node):
        if isinstance(inner, ast.Raise) and is_raise_of(inner, exceptions):
            return True
        if isinstance(inner, ast.Call) \
                and can_raise(dotted(inner.func), universe, exceptions, home,
                              seen | {(home, node.name)}):
            return True
    return False


def callee_gates(host: ast.FunctionDef, universe: Universe, exceptions,
                 skip=(), limit=None, module: str = None) -> tuple:
    """The gate FUNCTIONS one host runs: the module-level callees it names
    itself and that can refuse, above `limit` when a limit is given.

    DEPTH ONE, and deliberately. A literal transitive closure would reach every
    function a gate reaches and count each as a gate in its own right while its
    caller is already ledgered as one.

    A gate is named by the spelling the HOST writes — `require_freeze` and
    `score_rates.require_lawful_destination` are each identified by the words
    a reader of the host finds on the line. Round 18, finding 1: the second
    kind used to be dropped by an `isinstance(node.func, ast.Name)` test, which
    is how a rule called general in the record came to have no derived cell
    anywhere."""
    return tuple(sorted(
        {dotted(node.func) for node in ast.walk(host)
         if isinstance(node, ast.Call) and dotted(node.func) is not None
         and dotted(node.func) not in skip
         and (limit is None or node.lineno < limit)
         and universe.resolve(dotted(node.func), module) is not None
         and can_raise(dotted(node.func), universe, exceptions, module)}))


def sites_in(function: ast.FunctionDef, exceptions, classify,
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
            if isinstance(inner, ast.Raise) and is_raise_of(inner, exceptions):
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
                if is_raise_of(statement, exceptions):
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


def refusal_literals(hosts: dict, gates: tuple, universe: Universe,
                     exceptions, classify, module: str = None) -> dict:
    """{gate identity: (refusal string, …)} — the messages each gate raises,
    read out of the module's own source. A gate FUNCTION owns every `raise` in
    its body; an inline gate owns the raises its own `if` guards.

    Over the UNION gate set and every host, never one host's. The needle test
    is a claim that no OTHER gate can supply a case's needle, and a universe
    that is a fraction of the module's refusals cannot support it. A gate in a
    sibling module owns its own refusals the same way: the operator reads them
    on the same `refused: …` line."""
    literals = {}
    for host, node in sorted(hosts.items()):
        for kind, label, _line, _context, literal in sites_in(
                node, exceptions, classify):
            if kind != "inline" or literal is None:
                continue
            literals.setdefault(("inline", host, label), []).append(literal)
    for gate in gates:
        _home, node = universe.resolve(gate, module)
        literals[("gate", gate)] = [
            text for text in
            (raised_literal(inner) for inner in ast.walk(node)
             if isinstance(inner, ast.Raise) and is_raise_of(inner, exceptions))
            if text]
    return {key: tuple(value) for key, value in literals.items()}


def add_cell(cells: dict, key: tuple, line: int, mergeable: bool,
             message: str) -> None:
    """One derived cell: the FIRST line it is derived from, and HOW MANY call
    sites the derivation found for it.

    A GATE function is one gate however many times a host calls it — that is
    `gate_identity()`'s rule and the reason `require_freeze` is one `SATISFY`
    row and five cells — so repeated call sites of one gate collapse to one
    cell. Two distinct INLINE raises under one guard do not: that is two gates
    wearing one name, and it fails here rather than becoming a cell whose
    deletion nothing notices.

    ROUND 18, FINDING 3 is why the count exists. The merge used to discard what
    it absorbed, so the registered sentence "a deleted gate call is then a red
    suite" was false of every site but the first: at that round `batch.py`'s
    derivation walked 105 sites and emitted 82 cells, and deleting one of
    `run_batch()`'s two `verify_prefix()` calls left the whole pinned suite at
    315 passed. Counting
    the sites and asserting the count in both directions — which is exactly how
    the key set is already asserted — makes the sentence true of every site the
    derivation sees, with no new cell, no new case and no new residual.

    Sites, not distinct LINES. Two calls of one gate on one physical line are
    two sites; the same-line tolerance is kept only on the non-mergeable
    branch, where it guards against one walk emitting one raise twice rather
    than against a real repeat."""
    if key not in cells:
        cells[key] = (line, 1)
        return
    first, sites = cells[key]
    if mergeable:
        cells[key] = (min(first, line), sites + 1)
        return
    if first == line:
        return
    raise AssertionError(message % (first, line, key))


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
    supply is how a case goes vacuous (round 16, finding 2).

    `sites` is the number of CALL SITES the derivation finds for this cell.
    Repeated sites of one gate are one cell — that is `gate_identity()`'s rule
    — and the count is what makes deleting the SECOND one visible. Round 18,
    finding 3: without it, 23 of the driver's 105 gate sites could be deleted
    with the whole pinned suite green, under a registered sentence saying they
    could not."""

    def __init__(self, how, named=None, recipe=None, shared=(), why=None,
                 sites=1):
        self.how = how
        self.named = named
        self.recipe = recipe
        self.shared = tuple(shared)
        self.why = why
        self.sites = sites
