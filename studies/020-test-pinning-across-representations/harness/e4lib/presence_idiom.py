"""§3.2's presence-idiom detector, and the switch that keeps it out of admission.

NEW IN STUDY 020 (§7 delta 3). Nothing in Study 019's harness corresponds to
this file, so `harness/PORTS.md` carries it in the "does not carry" direction:
there is no source-side row to be two-sided about.

WHAT THIS FILE DOES
-------------------
**The predicate.** §3.2 registers one mechanical test: parse an admitted arm-B
or arm-C policy under `opa parse --format json` and flag "any `in` term whose
right operand is, on the syntax tree, an **object** (or a reference resolving to
an object member of `input`) rather than a set or array." `x in y` desugars to
`internal.member_2(x, y)` and `k, v in y` to `internal.member_3(k, v, y)`, in
both the expression position and inside a `some` term's `symbols`, so the
collection is the LAST argument of either call and the walk finds all four
spellings. The verdict is read off the tree — never off a regex over the source
text, which would see the operator inside a comment or a string.

**The `input` half of the parenthetical is DERIVED, never enumerated.** A
reference like `input.vendor` is an object member of `input` because the
REGISTERED INPUT DOMAIN says so: `input_paths()` renders every registered input
point through `engines.render_rego_input()` — the same textual renderer the
scored invocations use — and reports the kind of each dotted path. Writing
`{"input", "input.vendor", "input.evidence"}` into this file as a constant would
be a claim about the domain that no registered byte checks, and a domain that
grew a member would leave the constant quietly wrong (the program's standing
"derive scope, don't enumerate" lesson).

**The verdict vocabulary is four-valued, and only one of them flags.** `object`
flags. `collection` (set, array, and their comprehensions) does not. `scalar`
does not. `undetermined` does not, and is REPORTED with its reason: a call term
such as `object.keys(input.vendor)` — which is the idiom §3.2's forensic note
names as the correct one — resolves to nothing on the syntax tree, and a
detector that guessed at it would be firing on an unproven premise. A run scores
zero on every endpoint it reaches when this code fires (§1a), so the predicate
proves `object` or it does not flag.

**The switch.** §3.2 makes the guard a `GATE(pre-freeze)`: it "is registered
with its own power analysis, computed and published before the freeze", and the
`TODO(prereg)` block says that if the detector cannot meet (i) and (ii) exactly
— 40/40 and 0/22 — "the guard is not registered at all". So the DETECTOR is
callable now (the power analysis is executing it over 019's retained artifacts;
that is what the analysis IS), while the ADMISSION WIRING refuses to activate:

    gate open (the TODO block still stands in PREREGISTRATION.md)
        no analysis offered  -> `attempt_guard()` returns None: registered-off,
                                recorded, and `admit()` cannot return the code
        an analysis offered  -> GateOpenError. Activating a guard whose
                                obligation is still open is the failure the
                                gate exists to prevent, so it refuses loudly
                                rather than accepting the operator's word
    gate closed (the TODO block is gone from the registration)
        no analysis offered  -> GateUnmetError. The block cannot be deleted to
                                buy the guard; the numbers are the gate
        analysis offered     -> the five members (i)-(v) must all be present and
                                (i)/(ii) must read exactly 40/40 and 0/22, which
                                are the registration's own figures. Anything
                                else is GateUnmetError

`admit()` accepts only a `Guard` built through that door — a duck-typed
stand-in is an `AdmissionError`, because "it has a `verdict` method" is not the
registration's condition for the code entering the population.

DELIBERATELY DOES NOT DO
------------------------
* **It does not rewrite the operator.** That would change the authored artifact,
  which is the treatment (§3.2, "not a repair").
* **It does not exclude the run.** `presence-idiom-unsound` is an AUTHORING
  outcome: valid, counted, scoring zero, in every denominator (§1a). Nothing
  here touches the apparatus side.
* **It does not gate the batch and emits no prompt-side text.** §3.2 registers
  the prose variant OUT on a measured ground (the bundled Rego reference already
  flags the exact trap and it fired in 40 of 76 runs).
* **It does not reach arm A.** `ARM_REACHABLE_CODES` names B and C only, and
  `admit()`'s arm-structural check refuses if the code ever surfaces in arm A.
  §11.11 registers that asymmetry as a CEILING, not as a repair.
* **It does not invoke an engine to decide anything.** `opa parse` is a syntax
  operation and takes no capabilities file (`engines.opa_parse`); the pinned
  binary is not asked to evaluate, so the registered system boundary (§3.1) and
  the binary digest pin are untouched.
* **It does not compute or publish the power analysis.** (i)-(v) are a
  pre-freeze artifact of their own, named in `CORRECTION-TARGETS.md` (§10). This
  file is the thing that analysis runs and the thing that refuses until it has.
"""
from __future__ import annotations

import json

from . import engines

# §1a's table row. One spelling, so nothing has to agree with a literal.
CODE = "presence-idiom-unsound"

# §3.2: "structurally unreachable in arm A". `e4lib/admit.py` mirrors this into
# `ARM_REACHABLE_CODES`, and `tests/test_presence_idiom.py` diffs the two.
ARMS = ("B", "C")

# The desugarings of `in`. The value is how many arguments precede the
# collection, which is always the LAST one; the number is here so a reader can
# see that `k, v in coll` was not overlooked rather than having to infer it.
MEMBER_OPERATORS = {"internal.member_2": 1, "internal.member_3": 2}

# The `TODO(prereg)` block, verbatim from PREREGISTRATION.md §3.2 including both
# dashes (U+2014 then U+2013). While these bytes are in the registration the
# obligation is open, and the wiring refuses to activate.
GATE_ANCHOR = ("TODO(prereg) — the presence-idiom guard's power-analysis "
               "numbers (i)–(v).")

# §3.2's own numbers. (i) sensitivity: the detector "must fire on the 40 that
# use bare-object `in`"; (ii) specificity: "it must fire on none of the 22
# perfect runs". The TODO block restates them as "40/40 and 0/22".
GATE_SENSITIVITY = (40, 40)
GATE_SPECIFICITY = (0, 22)

# "It must report, at minimum:" — the five members, in the registration's order.
GATE_MEMBERS = ("sensitivity", "specificity", "falsePositiveRate",
                "counterfactualShift", "mutationCheck")

# Syntax-tree term types, by what they are on the tree. §3.2's dichotomy is
# "an object ... rather than a set or array"; the comprehensions are the same
# three shapes with a body, and OPA's parser names them so.
OBJECT_TYPES = ("object", "objectcomprehension")
COLLECTION_TYPES = ("set", "setcomprehension", "array", "arraycomprehension")
SCALAR_TYPES = ("string", "number", "boolean", "null")

# How deep a name is followed before the operand is reported undetermined. The
# chains that actually occur are short — parameter, call site, `object.get`,
# `input` is four — and the limit is a termination bound rather than a policy
# judgement; the cycle guard, not this number, is what stops a recursive
# function. A chain longer than this is not a presence idiom anyone wrote.
RESOLVE_DEPTH = 8


class PresenceIdiomError(Exception):
    """A refusal about the detector itself — never about an artifact."""


class GateOpenError(PresenceIdiomError):
    """Activation attempted while §3.2's `TODO(prereg)` block still stands."""


class GateUnmetError(PresenceIdiomError):
    """The gate's numbers were not met, or the analysis was not offered."""


# --------------------------------------------------------------------------
# the registered input domain, read rather than declared
# --------------------------------------------------------------------------

def input_paths(input_points) -> dict:
    """`{dotted path: "object" | "array" | "scalar"}` over the registered inputs.

    `input_points` is the registered input domain's case inputs — the `inputs`
    member of every gold row, which is the same signature
    `engines.render_rego_input()` renders for a scored invocation. Rendering
    through that function rather than building a document here is the point: the
    detector's idea of what `input.vendor` IS cannot drift from what the engine
    was handed.

    A member OMITTED from a point is absent, not null (`render_rego_input()`
    drops it), so a path is reported for the points that carry it. A path whose
    kind DIFFERS between two registered points is refused: the detector would
    then be flagging one point's shape and clearing another's, and §3.2's
    parenthetical would name no single fact."""
    kinds = {}
    seen = 0
    for point in input_points:
        seen += 1
        try:
            document = json.loads(engines.render_rego_input(point))
        except ValueError as error:
            raise PresenceIdiomError(
                "PRESENCE-UNREADABLE-INPUT-POINT registered input point %d did "
                "not render to a readable Rego input document (%s)"
                % (seen, type(error).__name__))
        _record_paths("input", document, kinds)
    if not seen:
        raise PresenceIdiomError(
            "PRESENCE-EMPTY-INPUT-DOMAIN no registered input point was offered; "
            "the `object member of input` half of §3.2's predicate is derived "
            "from the domain and cannot be derived from nothing")
    return kinds


def _record_paths(path: str, value, kinds: dict) -> None:
    if isinstance(value, dict):
        kind = "object"
    elif isinstance(value, list):
        kind = "array"
    else:
        kind = "scalar"
    if kinds.get(path, kind) != kind:
        raise PresenceIdiomError(
            "PRESENCE-AMBIGUOUS-INPUT-PATH %s is a JSON %s in one registered "
            "input point and a JSON %s in another; §3.2's `object member of "
            "input` would then name no single fact about the domain"
            % (path, kinds[path], kind))
    kinds[path] = kind
    if kind == "object":
        for member in value:
            _record_paths("%s.%s" % (path, member), value[member], kinds)


# --------------------------------------------------------------------------
# the syntax tree
# --------------------------------------------------------------------------

def parse_tree(raw: bytes) -> dict:
    """`opa parse --format json` output as a document.

    No `Decimal` hook, unlike `e4lib/domain.py`'s reader: nothing here compares
    a number against a threshold, and the operand's TYPE — which is the whole
    verdict — is `object` or it is not."""
    try:
        document = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        raise PresenceIdiomError(
            "PRESENCE-UNPARSEABLE-TREE `opa parse` emitted no readable syntax "
            "tree (%s)" % type(error).__name__)
    if not isinstance(document, dict):
        raise PresenceIdiomError(
            "PRESENCE-UNPARSEABLE-TREE `opa parse` emitted a JSON %s where the "
            "module document was expected" % type(document).__name__)
    return document


def operator_name(term):
    """The dotted name of a call's head term, or None."""
    if not isinstance(term, dict) or term.get("type") != "ref":
        return None
    path = term.get("value")
    if not isinstance(path, list) or not path:
        return None
    parts = []
    for node in path:
        value = node.get("value") if isinstance(node, dict) else None
        if not isinstance(value, str):
            return None
        parts.append(value)
    return ".".join(parts)


def rule_values(document: dict) -> dict:
    """`{package-local name: the term its value is}` for the names an operand
    can name.

    Three head shapes carry a value a membership test can be applied to, and
    they are read off the head's own structure rather than off the source text:

    * a COMPLETE rule (`req := {...}`) — head `ref` of length one, a `value` and
      no `key`: the value term itself;
    * a PARTIAL SET rule (`s contains x if ...`) — a `key` and no `value`: a
      set, which is §3.2's lawful side whatever the elements are;
    * a PARTIAL OBJECT rule (`o[k] := v if ...`) — both a `key` and a `value`:
      an object, which is §3.2's flagging side.

    A FUNCTION head (it has `args`) is not a value and is skipped; a name
    defined twice with two different shapes is dropped rather than guessed at,
    which is what makes a `default` beside a body rule safe. The dropped names
    reach the operand as `undetermined`, never as `collection`."""
    values, dropped = {}, set()
    for rule in document.get("rules") or []:
        if not isinstance(rule, dict):
            continue
        head = rule.get("head")
        if not isinstance(head, dict) or "args" in head:
            continue
        reference = head.get("ref")
        if not isinstance(reference, list) or not reference:
            continue
        name = reference[0].get("value") if isinstance(reference[0], dict) \
            else None
        if not isinstance(name, str):
            continue
        if "key" in head and "value" in head:
            term = {"type": "object", "value": []}
        elif "key" in head:
            term = {"type": "set", "value": []}
        elif "value" in head:
            term = head["value"]
        else:
            continue
        previous = values.get(name)
        if previous is not None and _term_kind(previous) != _term_kind(term):
            dropped.add(name)
        values[name] = term
    for name in dropped:
        values.pop(name, None)
    return values


def rule_bindings(rule: dict) -> dict:
    """`{local name: the term it was assigned}` for ONE rule's body.

    Empirically the load-bearing half of the resolution. The idiom 019's
    authors actually wrote is rarely `"riskScore" in input.vendor` at the point
    of use; it is

        allow if {
            vendor := input.vendor
            "riskScore" in vendor
        }

    and an operand read without body scope is a bare variable that resolves to
    nothing. `assign` (`:=`) and `eq` (`=`) are both collected, in both
    directions, because `=` is symmetric in Rego and a policy that wrote
    `input.vendor = vendor` bound the same thing.

    The scope is the WHOLE rule, comprehension bodies included, rather than one
    body per lexical scope. That is an over-approximation, and it is the safe
    direction only because a name bound twice to two different KINDS is dropped
    rather than resolved: a comprehension that rebinds `vendor` to a set beside
    an outer `vendor := input.vendor` yields `undetermined`, not a flag."""
    bindings, dropped = {}, set()
    for terms in _assignment_terms(rule):
        left, right = terms[1], terms[2]
        name = left.get("value") if isinstance(left, dict) \
            and left.get("type") == "var" else None
        value = right
        if not isinstance(name, str):
            name = right.get("value") if isinstance(right, dict) \
                and right.get("type") == "var" else None
            value = left
        if not isinstance(name, str) or name.startswith("$"):
            continue
        previous = bindings.get(name)
        if previous is not None and _term_kind(previous) != _term_kind(value):
            dropped.add(name)
        bindings[name] = value
    for name in dropped:
        bindings.pop(name, None)
    return bindings


# How many times the parameter pass is repeated before it is declared stable.
# One pass binds a parameter whose call sites pass `input.vendor`; a second
# binds the parameter of a helper called as `risk_values(vendor)` from inside a
# function whose OWN `vendor` the first pass bound, which is the shape 019's
# authors wrote. The loop exits when nothing changed, so this is a termination
# bound and not a tuning knob.
PARAMETER_ROUNDS = 6

# The synthetic term type a parameter binding carries. It is not an OPA term
# type and never appears in a parse tree; it exists because a binding must
# record the READING the caller's scope produced, not the call site's bytes.
RESOLVED_TYPE = "presence-resolved"


def parameter_bindings(document: dict, paths: dict, names: dict) -> dict:
    """`{rule index: {parameter name: term}}`, read off the CALL SITES.

    `e4lib/domain.py` had to learn the same lesson for `with input as doc`: a
    function's parameter has no value where it is written, so a rule body like

        risk_values(vendor) := [vendor.riskScore] if { "riskScore" in vendor }

    resolves to nothing until the call sites are read — and in 019's retained
    policies the call site is `risk_values(input.vendor)`. Without this the
    detector cannot see the single commonest spelling of the trap.

    UNANIMITY, not the first site: a parameter is bound only when every call
    site's term at that position classifies the same way in its OWN caller's
    scope. One site passing an object and another passing a set is a parameter
    with no single kind, and the operand stays `undetermined` rather than
    taking the majority's verdict.

    A BOUNDED FIXPOINT, because the call site is often `risk_values(vendor)`
    from inside a function whose own `vendor` is a parameter: one pass leaves
    that undetermined and the next resolves it. The iteration stops when a pass
    changes nothing, and `classify_operand`'s cycle guard is what makes
    resolving a parameter through a parameter safe."""
    sites = _callsites_by_caller(document)
    bound = {}
    for _round in range(PARAMETER_ROUNDS):
        grown = _parameter_pass(document, paths, names, sites, bound)
        if grown == bound:
            break
        bound = grown
    return bound


def _parameter_pass(document, paths, names, sites, bound):
    scopes = {}
    for index, rule in enumerate(document.get("rules") or []):
        scope = dict(names)
        scope.update(bound.get(index) or {})
        scope.update(rule_bindings(rule))
        scopes[index] = scope
    grown = {}
    for index, rule in enumerate(document.get("rules") or []):
        head = rule.get("head")
        if not isinstance(head, dict):
            continue
        args = head.get("args")
        reference = head.get("ref")
        if not isinstance(args, list) or not args \
                or not isinstance(reference, list) or not reference:
            continue
        name = reference[0].get("value") if isinstance(reference[0], dict) \
            else None
        called = [(caller, site) for caller, by_name in sites.items()
                  for site in (by_name.get(name) or [])]
        if not called:
            continue
        here = {}
        for position, argument in enumerate(args):
            parameter = argument.get("value") \
                if isinstance(argument, dict) and argument.get("type") == "var" \
                else None
            if not isinstance(parameter, str):
                continue
            passed = [(caller, site[position]) for caller, site in called
                      if len(site) > position]
            if not passed:
                continue
            readings = [classify_operand(term, paths, scopes[caller])
                        for caller, term in passed]
            verdicts = set(verdict for verdict, _reason in readings)
            if len(verdicts) == 1 and verdicts != {"undetermined"}:
                caller, term = passed[0]
                here[parameter] = {
                    "type": RESOLVED_TYPE,
                    "verdict": readings[0][0],
                    "reason": ("%s is bound at every call site to a value where "
                               "%s" % (parameter, readings[0][1])),
                    "path": _input_path(term, scopes[caller], 0, ()),
                }
        if here:
            grown[index] = here
    return grown


def _callsites_by_caller(document) -> dict:
    """`{caller rule index: {called name: [argument list, ...]}}`.

    The caller's index is kept because an argument term is read in the CALLER's
    scope: `risk_values(vendor)` names whatever `vendor` is where the call is
    written, not where the callee's parameter is."""
    sites = {}
    for index, rule in enumerate(document.get("rules") or []):
        found = {}
        _collect_callsites(rule, found)
        if found:
            sites[index] = found
    return sites


def _collect_callsites(node, into=None):
    """`{package-local name: [argument list, ...]}` for every call under `node`."""
    if into is None:
        into = {}
    if isinstance(node, dict):
        terms = node.get("terms")
        if isinstance(terms, list) and terms:
            _record_callsite(terms, into)
        if node.get("type") == "call" and isinstance(node.get("value"), list) \
                and node["value"]:
            _record_callsite(node["value"], into)
        for key in sorted(node):
            _collect_callsites(node[key], into)
    elif isinstance(node, list):
        for item in node:
            _collect_callsites(item, into)
    return into


def _record_callsite(terms, into):
    name = operator_name(terms[0])
    if not name or "." in name:
        return
    into.setdefault(name, []).append(list(terms[1:]))


ASSIGN_OPERATORS = ("assign", "eq")


def _assignment_terms(node, into=None):
    """Every `:=` / `=` expression's `[op, left, right]`, anywhere under `node`."""
    if into is None:
        into = []
    if isinstance(node, dict):
        terms = node.get("terms")
        if isinstance(terms, list) and len(terms) == 3 \
                and operator_name(terms[0]) in ASSIGN_OPERATORS:
            into.append(terms)
        for key in sorted(node):
            _assignment_terms(node[key], into)
    elif isinstance(node, list):
        for item in node:
            _assignment_terms(item, into)
    return into


def _term_kind(term):
    kind = term.get("type") if isinstance(term, dict) else None
    if kind in OBJECT_TYPES:
        return "object"
    if kind in COLLECTION_TYPES:
        return "collection"
    if kind in SCALAR_TYPES:
        return "scalar"
    return None


def classify_operand(term, paths: dict, names: dict, depth: int = 0,
                     seen=()) -> tuple:
    """`(verdict, reason)` for one `in` term's right operand.

    The verdicts are `object`, `collection`, `scalar` and `undetermined`, and
    §3.2 flags exactly the first. `undetermined` is a REPORTED outcome and never
    a silent pass: a `data` reference, a local this module cannot resolve, a
    name dropped as ambiguous, a builtin outside the small table below and a
    path outside the registered input domain all land there, and the power
    analysis's members are computed with those counts in view.

    `seen` is the cycle guard. A recursive function passes its own parameter
    back to itself (`f(vendor)` inside `f(vendor)`), and without it the name
    resolves to itself until the depth limit and reports a chain rather than the
    fact that it is a cycle."""
    if isinstance(term, dict) and term.get("type") == RESOLVED_TYPE:
        # A parameter binding, already read in its CALLER's scope. It has to
        # carry its reading rather than the call site's raw term: the term is
        # very often the bare name `vendor`, which means one thing where the
        # call is written and nothing at all inside the callee.
        return term["verdict"], term["reason"]
    direct = _term_kind(term)
    if direct is not None:
        return direct, "the operand is a %s term" % term.get("type")
    if depth >= RESOLVE_DEPTH:
        return "undetermined", ("the operand's name chain is deeper than the "
                                "registered resolution depth")
    kind = term.get("type") if isinstance(term, dict) else None
    if kind == "var":
        name = term.get("value")
        if isinstance(name, str) and name in seen:
            return "undetermined", ("%s resolves through itself; a cycle names "
                                    "no value" % name)
        if isinstance(name, str) and name in names:
            verdict, reason = classify_operand(names[name], paths, names,
                                               depth + 1,
                                               tuple(seen) + (name,))
            return verdict, "%s resolves to a value where %s" % (name, reason)
        return "undetermined", ("the operand is a variable this module cannot "
                                "resolve to a package-level value")
    if kind == "ref":
        return _classify_reference(term, paths, names, depth, seen)
    if kind == "call":
        return _classify_call(term, paths, names, depth, seen)
    return "undetermined", ("the operand is a %s term, which resolves to no "
                            "value on the syntax tree" % (kind,))


# The only builtins whose RESULT KIND this module reads, and it reads the kind
# alone — never a value. Each is a documented OPA builtin with one return type,
# so the reading is a fact about the language rather than an evaluation:
# `object.keys` yields a set, and the four object shapers yield an object. They
# are here because 019's authors reached for them constantly — `vendor :=
# object.get(input, "vendor", {})` is the single commonest way the trap's
# operand is spelled, and a detector that stops at "it is a call term" cannot
# see it. `object.get` is NOT in this table: its result is its second argument's
# member OR its default, so it gets the resolution below rather than a constant.
BUILTIN_RESULT_KINDS = {
    "object.keys": "collection",
    "object.union": "object",
    "object.union_n": "object",
    "object.filter": "object",
    "object.remove": "object",
}
OBJECT_GET = "object.get"


def _classify_call(term, paths, names, depth, seen):
    arguments = term.get("value")
    if not isinstance(arguments, list) or not arguments:
        return "undetermined", "the operand is a call with no operator"
    name = operator_name(arguments[0])
    if name in BUILTIN_RESULT_KINDS:
        return BUILTIN_RESULT_KINDS[name], ("the operand is %s(…), whose result "
                                            "is always a %s"
                                            % (name, BUILTIN_RESULT_KINDS[name]))
    if name == OBJECT_GET and len(arguments) == 4:
        return _classify_object_get(arguments, paths, names, depth, seen)
    return "undetermined", ("the operand is a %s(…) call, whose result kind "
                            "this module does not read" % (name,))


def _classify_object_get(arguments, paths, names, depth, seen):
    """`object.get(source, key, default)` — the member's kind, or the default's.

    Sound without any presence information: the builtin returns the member when
    it is there and the default when it is not, so the result's kind is
    determined exactly when BOTH are determined and AGREE, or when the member is
    not a path of the registered domain at all and the default is therefore the
    only answer. `object.get(input, "vendor", {})` is object either way, which
    is why the idiom is a flag and not an escape from one."""
    source, key, fallback = arguments[1], arguments[2], arguments[3]
    default_kind, default_reason = classify_operand(fallback, paths, names,
                                                    depth + 1, seen)
    child = _input_path(source, names, depth, seen)
    steps = _literal_steps(key)
    if child is None or steps is None:
        return "undetermined", ("the operand is object.get(…) whose source or "
                                "key is not a static path into the registered "
                                "input domain")
    path = ".".join([child] + steps)
    member_kind = paths.get(path)
    if member_kind is None:
        return default_kind, ("%s is not a path of the registered input domain, "
                              "so object.get(…) always yields its default, "
                              "where %s" % (path, default_reason))
    member_kind = "collection" if member_kind == "array" else member_kind
    if member_kind == default_kind:
        return member_kind, ("object.get(…) yields %s or its default and both "
                             "are a %s" % (path, member_kind))
    return "undetermined", ("object.get(…) yields %s (a %s) or its default (%s), "
                            "which are two kinds" % (path, member_kind,
                                                     default_kind))


def _literal_steps(term):
    """A `object.get` key as a list of path steps, or None.

    Both spellings the builtin accepts: a single string key, and an array of
    string keys for a nested member."""
    if not isinstance(term, dict):
        return None
    if term.get("type") == "string":
        return [term["value"]]
    if term.get("type") == "array" and isinstance(term.get("value"), list):
        steps = []
        for node in term["value"]:
            if not isinstance(node, dict) or node.get("type") != "string":
                return None
            steps.append(node["value"])
        return steps
    return None


def _input_path(term, names, depth, seen):
    """The dotted `input…` path a term names, or None.

    Only what the syntax tree states: a reference rooted at `input` with literal
    steps, a name bound to one, or an `object.get` into one."""
    if depth >= RESOLVE_DEPTH or not isinstance(term, dict):
        return None
    kind = term.get("type")
    if kind == RESOLVED_TYPE:
        return term.get("path")
    if kind == "ref":
        steps = term.get("value")
        if not isinstance(steps, list) or not steps \
                or not isinstance(steps[0], dict) \
                or steps[0].get("type") != "var":
            return None
        root = steps[0].get("value")
        tail = []
        for node in steps[1:]:
            if not isinstance(node, dict) or node.get("type") != "string":
                return None
            tail.append(node["value"])
        if root == "input":
            return ".".join(["input"] + tail)
        if isinstance(root, str) and not tail and root in names \
                and root not in seen:
            return _input_path(names[root], names, depth + 1,
                               tuple(seen) + (root,))
        return None
    if kind == "var":
        name = term.get("value")
        if isinstance(name, str) and name in names and name not in seen:
            return _input_path(names[name], names, depth + 1,
                               tuple(seen) + (name,))
        return None
    if kind == "call" and isinstance(term.get("value"), list) \
            and len(term["value"]) == 4 \
            and operator_name(term["value"][0]) == OBJECT_GET:
        child = _input_path(term["value"][1], names, depth + 1, seen)
        steps = _literal_steps(term["value"][2])
        if child is None or steps is None:
            return None
        return ".".join([child] + steps)
    return None


def _classify_reference(term, paths, names, depth, seen):
    steps = term.get("value")
    if not isinstance(steps, list) or not steps \
            or not isinstance(steps[0], dict) or steps[0].get("type") != "var":
        return "undetermined", "the operand is a reference with no static root"
    root = steps[0].get("value")
    tail = []
    for node in steps[1:]:
        if not isinstance(node, dict) or node.get("type") != "string":
            return "undetermined", ("the operand is a reference with a "
                                    "non-literal path step")
        tail.append(node["value"])
    if root == "input":
        path = ".".join(["input"] + tail)
        kind = paths.get(path)
        if kind == "object":
            return "object", ("%s is an object member of the registered input "
                              "domain" % path)
        if kind == "array":
            return "collection", ("%s is an array in the registered input "
                                  "domain" % path)
        if kind == "scalar":
            return "scalar", ("%s is a scalar in the registered input domain"
                              % path)
        return "undetermined", ("%s is not a path of the registered input "
                                "domain" % path)
    if isinstance(root, str) and not tail and root in seen:
        return "undetermined", ("%s resolves through itself; a cycle names no "
                                "value" % root)
    if isinstance(root, str) and not tail and root in names:
        verdict, reason = classify_operand(names[root], paths, names, depth + 1,
                                           tuple(seen) + (root,))
        return verdict, "%s resolves to a value where %s" % (root, reason)
    return "undetermined", ("the operand is a reference rooted at %r, which "
                            "this module does not resolve" % (root,))


def member_terms(document: dict) -> list:
    """Every `in` term in the module, in walk order.

    Each entry is `{"operator", "form", "left", "operand", "where"}`. `form`
    separates a MEMBERSHIP TEST — `internal.member_2` whose left operand is not
    a bare variable, which is the `"riskScore" in input.vendor` shape §3.2's
    forensic read names — from an ITERATION, which is `internal.member_3` or a
    `member_2` binding a fresh variable. **Nothing filters on `form`.** §3.2
    registers the predicate over "any `in` term", so the flag is the operand's
    verdict alone; `form` is carried so the power analysis's (iii) member can
    report the two populations separately instead of having to re-derive them.

    Both syntactic positions are walked: an expression whose `terms` is a list
    headed by the operator, and a `call` TERM, which is where a `some x in coll`
    lands (inside the expression's `symbols`)."""
    found = []
    _walk(document, found, ())
    return found


def _walk(node, found, where):
    if isinstance(node, dict):
        terms = node.get("terms")
        if isinstance(terms, list) and terms:
            _consider(terms, found, where + ("terms",))
        if node.get("type") == "call" and isinstance(node.get("value"), list) \
                and node["value"]:
            _consider(node["value"], found, where + ("call",))
        for key in sorted(node):
            _walk(node[key], found, where + (str(key),))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            _walk(item, found, where + (str(index),))


def _consider(terms, found, where):
    name = operator_name(terms[0])
    arity = MEMBER_OPERATORS.get(name)
    if arity is None or len(terms) != arity + 2:
        return
    left = terms[1]
    iterating = (name == "internal.member_3"
                 or (isinstance(left, dict) and left.get("type") == "var"))
    found.append({
        "operator": name,
        "form": "iteration" if iterating else "membership-test",
        "left": left,
        "operand": terms[-1],
        "where": ".".join(where),
    })


# --------------------------------------------------------------------------
# the detector
# --------------------------------------------------------------------------

def scan_tree(document: dict, paths: dict) -> dict:
    """The predicate over one parsed module. No engine, no filesystem.

    Rule by rule, because the resolution scope is a rule: the package-level
    names are visible everywhere and a body binding is visible in its own rule
    only. The count of `in` terms found rule-wise is checked against the count
    found over the whole document, so a term outside every rule would be a
    refusal rather than a silent omission from the denominator.

    `flagged` is true when at least one `in` term's operand classifies as
    `object`; `terms` carries every `in` term with its verdict, its reason and
    its form, so a reviewer can see what the detector did NOT flag as readily as
    what it did."""
    package_names = rule_values(document)
    parameters = parameter_bindings(document, paths, package_names)
    rows = []
    for index, rule in enumerate(document.get("rules") or []):
        names = dict(package_names)
        names.update(parameters.get(index) or {})
        names.update(rule_bindings(rule))
        for entry in member_terms(rule):
            verdict, reason = classify_operand(entry["operand"], paths, names)
            rows.append({"operator": entry["operator"], "form": entry["form"],
                         "where": "rules.%d.%s" % (index, entry["where"]),
                         "verdict": verdict, "reason": reason})
    whole = len(member_terms(document))
    if whole != len(rows):
        raise PresenceIdiomError(
            "PRESENCE-TERM-OUTSIDE-RULE the module carries %d `in` terms and "
            "only %d of them are inside a rule; a term the rule-wise walk never "
            "saw would be silently absent from the detector's denominator"
            % (whole, len(rows)))
    flagged = [row for row in rows if row["verdict"] == "object"]
    return {"flagged": bool(flagged), "terms": rows,
            "objectTerms": len(flagged),
            "undeterminedTerms": sum(1 for row in rows
                                     if row["verdict"] == "undetermined")}


def scan(tools, policy_path: str, workdir: str, paths: dict) -> dict:
    """`scan_tree()` over `opa parse --format json <policy_path>`.

    Refuses rather than reporting "not flagged" when the parse yields nothing:
    an unreadable tree is a policy the detector did not examine, and recording
    that as a clean run would put a silent false negative in the power
    analysis's specificity member."""
    code, raw = engines.opa_parse(tools, policy_path, workdir)
    if code != 0 or not raw.strip():
        raise PresenceIdiomError(
            "PRESENCE-PARSE-REFUSED `opa parse` exited %d and emitted %d bytes "
            "for the policy under test; a tree that was never read is not a "
            "policy that carries no unsound presence idiom" % (code, len(raw)))
    report = scan_tree(parse_tree(raw), paths)
    report["parseExit"] = code
    return report


# --------------------------------------------------------------------------
# the gate, and the guard it lets through
# --------------------------------------------------------------------------

def gate_open(preregistration: str) -> bool:
    """True while §3.2's `TODO(prereg)` block stands in the registration."""
    return GATE_ANCHOR in preregistration


def require_gate_closed(preregistration: str) -> None:
    if gate_open(preregistration):
        raise GateOpenError(
            "PRESENCE-GATE-OPEN §3.2 registers the presence-idiom guard as a "
            "GATE(pre-freeze) and its TODO block is still in "
            "PREREGISTRATION.md: the power-analysis numbers (i)-(v) are not "
            "computed, so the guard is not registered yet and %r cannot enter "
            "the population" % CODE)


def require_power_analysis(analysis) -> dict:
    """§3.2's (i) and (ii), checked against the registration's own figures.

    The TODO block is explicit about the consequence of missing them: "if the
    detector cannot meet (i) and (ii) exactly — 40/40 and 0/22 — the guard is
    not registered at all". So this refuses rather than warning, and it refuses
    on a MISSING member too: an analysis that did not report its
    false-positive rate, its counterfactual per-member shift or its mutation
    check is not the analysis §3.2 registered."""
    if not isinstance(analysis, dict):
        raise GateUnmetError(
            "PRESENCE-GATE-UNMET §3.2's guard is registered with its own power "
            "analysis and none was offered; deleting the TODO block does not "
            "compute it")
    missing = [member for member in GATE_MEMBERS if member not in analysis]
    if missing:
        raise GateUnmetError(
            "PRESENCE-GATE-UNMET the power analysis is missing the registered "
            "member(s) %s; §3.2 requires all of %s"
            % (", ".join(missing), ", ".join(GATE_MEMBERS)))
    for member, required in (("sensitivity", GATE_SENSITIVITY),
                             ("specificity", GATE_SPECIFICITY)):
        entry = analysis[member]
        if not isinstance(entry, dict) or "fired" not in entry \
                or "of" not in entry:
            raise GateUnmetError(
                "PRESENCE-GATE-UNMET the power analysis's %s member does not "
                "report `fired` out of `of`, so it states no rate" % member)
        if (entry["fired"], entry["of"]) != required:
            raise GateUnmetError(
                "PRESENCE-GATE-UNMET §3.2 requires %s %d/%d exactly and the "
                "analysis reports %r/%r; the guard is then not registered at "
                "all and the mechanism is Tier D descriptive material"
                % (member, required[0], required[1], entry["fired"],
                   entry["of"]))
    return analysis


class Guard:
    """An activated presence-idiom guard. Constructible only through the gate.

    Holding one is the evidence `admit()` requires: §3.2's TODO block is gone
    from the registration AND the power analysis meets (i) and (ii) exactly.
    `admit()` type-checks for this class rather than for a `verdict` method,
    because "it looks like a guard" is not the registration's condition."""

    def __init__(self, preregistration: str, analysis, paths: dict):
        require_gate_closed(preregistration)
        self.analysis = require_power_analysis(analysis)
        if not paths:
            raise PresenceIdiomError(
                "PRESENCE-EMPTY-INPUT-DOMAIN a guard cannot be activated over "
                "an empty registered input domain: §3.2's `object member of "
                "input` would resolve nothing and the detector would flag only "
                "bare object literals")
        self.paths = paths

    def verdict(self, tools, arm: str, policy_path: str, workdir: str) -> tuple:
        """`(code or None, detail)` for one admitted policy.

        Refuses on an arm it cannot reach rather than returning None: arm A
        reaching this method means a caller wired the guard into the wrong
        branch, and §11.11's asymmetry is registered as structural."""
        if arm not in ARMS:
            raise PresenceIdiomError(
                "PRESENCE-ARM-UNREACHABLE §3.2 registers %r for arms %s only, "
                "and arm %s asked for a verdict; the asymmetry is a registered "
                "ceiling (§11.11), not a branch to fill in"
                % (CODE, ", ".join(ARMS), arm))
        report = scan(tools, policy_path, workdir, self.paths)
        return (CODE if report["flagged"] else None), report


def attempt_guard(preregistration: str, analysis, paths: dict):
    """The one door. `None` while the gate is open and no analysis is claimed.

    The four cases are §3.2's, and three of them refuse:

    * gate open, no analysis — the registered-off state this study is in today.
      `None`, so `admit()` cannot return the code and E2 publishes its row at
      count zero, which is what §5's E2 entry registers ("whether or not it ever
      fires").
    * gate open, an analysis offered — `GateOpenError`. The obligation is a
      pre-freeze gate; an operator who has the numbers lands them in the
      registration first.
    * gate closed, no analysis — `GateUnmetError`. Removing the TODO block does
      not buy the guard.
    * gate closed, an analysis meeting 40/40 and 0/22 — a `Guard`."""
    if gate_open(preregistration):
        if analysis is None:
            return None
        raise GateOpenError(
            "PRESENCE-GATE-OPEN a power analysis was offered while §3.2's "
            "TODO(prereg) block still stands in PREREGISTRATION.md; the guard "
            "is registered by the registration, not by the operator's copy of "
            "the numbers")
    return Guard(preregistration, analysis, paths)
