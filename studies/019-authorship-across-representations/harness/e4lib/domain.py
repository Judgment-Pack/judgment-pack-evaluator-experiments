"""The registered input domain, and the symmetric case enumeration it needs.

ROUND-1 FINDING R1-3, in one module. The finding was that "the promised common
input-domain and X1 filters do not exist across arms": arm A parsed its matrix
and applied a filter, arms B/C handed the scorer an opaque `opa test` file,
hard-coded `x1Excluded = []`, and received no case-level domain validation at
all. The certificate measured 18,954 reference divergences on inputs outside the
registered domain, so an unvalidated case is a case on which the two arms'
references are not known to agree — and an asymmetric filter can move E4.

This module is what makes the treatment SYMMETRIC, and it does it the only way
that is symmetric: by enumerating the case inputs of EVERY arm mechanically from
the artifact the author emitted, and validating each one against the same
registered domain before identity and before mutation execution.

    arm A     `facts` + `evidenceAvailability` of each matrixVersion-2 case
    arms B/C  every `with input as <literal>` term of the `opa test` file, read
              out of `opa parse --format json`'s own syntax tree

THE REGISTERED DOMAIN (§SPACE of `design/reference/cert_offgold.py`, and
`design/prompts/NAMING-APPENDIX.md` for the wire forms)
------------------------------------------------------------------------------
The registered space is the READABLE domain of each axis plus, on the axes that
admit it, the registered encoding of "unreadable/unreported" — an OMITTED MEMBER,
"never a null, never a sentinel string":

    sanctionsStatus     CLEAR | MATCH | UNKNOWN          — always present
    countryRisk         LOW | MEDIUM | HIGH              | omitted
    riskScore           integer 0..100                   | omitted
    requestedSpend      0.00 .. 10000000.00, cents       | omitted
    newVendor           yes | no                         | omitted
    criticalSupplier    yes | no                         | omitted
    priorEnforcement    yes | no                         | omitted
    financial-evidence  present | absent                 | omitted
    insurance-certificate  present | absent              | omitted

`sanctionsStatus` is the one axis with no omitted state, and that is a REGISTERED
LIMIT rather than an oversight: the certificate says so in its own words — "an
input document with `/vendor/sanctionsStatus` physically absent is OUTSIDE this
space" — and the labelled supplementary stratum it measured on that extension is
exactly where the two references stop agreeing. A case that omits it is asking a
question this study's oracle does not answer.

The WIRE FORM differs by arm and the domain check therefore does too, because
the naming appendix registers two different bindings for one value:

    arm A     `riskScore`/`requestedSpend` are decimal STRINGS — integer scale
              for risk, two decimals for spend, no leading zeros, no exponent
    arms B/C  the same two are JSON NUMBERS

Checking the string form against arm A and the number form against B/C is not an
asymmetry in the domain; it is the same domain in the two encodings the
registration assigns. A number where the appendix registers a string (or the
reverse) is out of domain, not silently coerced: a coercion here is precisely how
`100000.01` becomes a float on one side of a threshold the policy tests with `>`.

WHAT A FAILURE MEANS, AND WHY THAT IS NOT THIS MODULE'S CHOICE
--------------------------------------------------------------
This module answers two questions and decides nothing:

    `enumerate_*`      can the artifact's cases be enumerated at all?
    `domain_problems`  is this enumerated input inside the registered domain?

`harness/score.py` maps the two answers onto §1a's registered outcomes, and the
mapping is stated there rather than here so that one file carries the population
rule. Neither answer is ever a silent pass, which is the whole of R1-3's demand.
"""
from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation

# The registered enumerations, as the naming appendix spells them.
SANCTIONS_VALUES = ("CLEAR", "MATCH", "UNKNOWN")
COUNTRY_VALUES = ("LOW", "MEDIUM", "HIGH")
YES_NO_VALUES = ("yes", "no")
AVAILABILITY_VALUES = ("present", "absent")

RISK_MIN, RISK_MAX = Decimal(0), Decimal(100)
SPEND_MIN, SPEND_MAX = Decimal("0.00"), Decimal("10000000.00")
SPEND_EXPONENT = -2                       # cents precision, exactly

# The registered arm-A decimal-string forms: "no leading zeros, no exponent",
# integer scale for risk and two decimals for spend.
RISK_STRING = re.compile(r"^(0|[1-9][0-9]*)$")
SPEND_STRING = re.compile(r"^(0|[1-9][0-9]*)\.[0-9]{2}$")

# The canonical cell keys, and the members they live under in each wire form.
VENDOR_CELLS = (("risk", "riskScore"),
                ("spend", "requestedSpend"),
                ("sanctions", "sanctionsStatus"),
                ("country", "countryRisk"),
                ("newVendor", "newVendor"),
                ("critical", "criticalSupplier"),
                ("prior", "priorEnforcement"))
EVIDENCE_CELLS = (("finEvidence", "financial-evidence"),
                  ("insurance", "insurance-certificate"))

# The registered top-level members of a Rego input document.
REGO_INPUT_MEMBERS = ("vendor", "evidence")


class DomainError(Exception):
    """A refusal about the enumeration itself, with a named code first."""


# --------------------------------------------------------------------------
# the registered domain
# --------------------------------------------------------------------------

class _ExplicitNull(object):
    """The PRESENCE SENTINEL — round-2 finding R2-4, first half.

    The registered encoding of "unreadable/unreported" is an OMITTED MEMBER,
    "never a null, never a sentinel string" (the module head, the naming
    appendix, and `design/reference/refB/policy.rego`'s own comment: "the
    projection never emits a JSON null, so the sentinels cannot collide with a
    real value"). The enumeration used to lose that distinction one step before
    the check that depends on it: `_literal()` converts an AST `null` to Python
    `None`, `dict.get()` returns `None` for an absent member too, and
    `_enum_problem()` then reads an optional `None` as an omission. A suite
    writing `"newVendor": null` therefore passed domain validation and identity
    validation and went on to kill paired mutants, on an input point the
    registered space does not contain and the off-gold certificate says nothing
    about.

    Presence is now decided where presence is KNOWN — at the document, by key
    membership — and survives into the check as this sentinel, in BOTH wire
    forms: arm A's matrix `"newVendor": null` and arms B/C's `newVendor: null`
    reach the same refusal by the same route, which is what §4's "enforced
    symmetrically" requires."""

    __slots__ = ()

    def __repr__(self):
        return "<explicit JSON null>"

    __str__ = __repr__


EXPLICIT_NULL = _ExplicitNull()


def _null_problem(cell):
    return ("%s is present carrying a JSON null, and the registered encoding of "
            "an unreadable/unreported input is an OMITTED MEMBER — never a "
            "null, never a sentinel string" % cell)


def _presence(document: dict, member: str):
    """One member's value, with ABSENT and PRESENT-BUT-NULL kept apart."""
    if member not in document:
        return None
    value = document[member]
    return EXPLICIT_NULL if value is None else value


def _enum_problem(cell, value, allowed, optional):
    """One enumerated axis. An omitted member is `None`; a null or a sentinel
    string is NOT an omission and is reported as the value it is."""
    if value is EXPLICIT_NULL:
        return _null_problem(cell)
    if value is None:
        if optional:
            return None
        return "%s is omitted and the registered domain admits no unreadable " \
               "state for it" % cell
    if not isinstance(value, str) or value not in allowed:
        return "%s is %r and the registered domain is %s%s" % (
            cell, value, "/".join(allowed), " or omitted" if optional else "")
    return None


def _risk_problem(value, wire: str):
    if value is EXPLICIT_NULL:
        return _null_problem("risk")
    if value is None:
        return None
    if wire == "string":
        if not isinstance(value, str) or not RISK_STRING.match(value):
            return ("risk is %r and arm A's registered wire form is a decimal "
                    "string at integer scale with no leading zeros" % (value,))
        number = Decimal(value)
    else:
        if isinstance(value, float):
            return ("risk is %r and reached this check as a binary float: JSON "
                    "numbers are decoded as exact decimals here, because a "
                    "float is what silently moves a value across a threshold"
                    % (value,))
        if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
            return ("risk is %r and arms B/C's registered wire form is a JSON "
                    "number at integer scale" % (value,))
        number = Decimal(value)
        if number != number.to_integral_value():
            return "risk is %r and the registered domain is integer 0..100" % (value,)
    if not RISK_MIN <= number <= RISK_MAX:
        return "risk is %s and the registered domain is 0..100" % number
    return None


def _spend_problem(value, wire: str):
    if value is EXPLICIT_NULL:
        return _null_problem("spend")
    if value is None:
        return None
    if wire == "string":
        if not isinstance(value, str) or not SPEND_STRING.match(value):
            return ("spend is %r and arm A's registered wire form is a decimal "
                    "string at two decimals with no leading zeros" % (value,))
        number = Decimal(value)
    else:
        if isinstance(value, float):
            return ("spend is %r and reached this check as a binary float: JSON "
                    "numbers are decoded as exact decimals here, because a "
                    "float is what silently moves a value across a threshold"
                    % (value,))
        if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
            return ("spend is %r and arms B/C's registered wire form is a JSON "
                    "number" % (value,))
        try:
            number = Decimal(value)
        except (InvalidOperation, ValueError, ArithmeticError):
            return "spend is %r and is not a readable decimal" % (value,)
        if number != number.quantize(Decimal("0.01")):
            return ("spend is %s and the registered domain is cents precision"
                    % number)
    if not SPEND_MIN <= number <= SPEND_MAX:
        return "spend is %s and the registered domain is 0.00..10000000.00" % number
    return None


def domain_problems(signature: dict, wire: str) -> list:
    """Every way this input point leaves the registered domain, sorted.

    `wire` is `"string"` for arm A's matrix bindings and `"number"` for arms
    B/C's Rego bindings — the two encodings the naming appendix registers for one
    domain. An empty list is the statement that the point is inside the space the
    off-gold certificate covers, which is the space on which the two references
    are known to agree; a non-empty one is never a silent pass.

    An UNKNOWN member is a problem in its own right. The registered input
    document has exactly these members, and a case that adds one is asserting
    something about a fact this policy family does not carry."""
    if wire not in ("string", "number"):
        raise DomainError("DOMAIN-UNKNOWN-WIRE %r is not a registered wire form"
                          % (wire,))
    problems = []
    problems.append(_risk_problem(signature.get("risk"), wire))
    problems.append(_spend_problem(signature.get("spend"), wire))
    problems.append(_enum_problem("sanctions", signature.get("sanctions"),
                                  SANCTIONS_VALUES, optional=False))
    problems.append(_enum_problem("country", signature.get("country"),
                                  COUNTRY_VALUES, optional=True))
    for cell in ("newVendor", "critical", "prior"):
        problems.append(_enum_problem(cell, signature.get(cell), YES_NO_VALUES,
                                      optional=True))
    for cell in ("finEvidence", "insurance"):
        problems.append(_enum_problem(cell, signature.get(cell),
                                      AVAILABILITY_VALUES, optional=True))
    for member in sorted(signature.get("unknownMembers") or ()):
        problems.append("%s is not a registered input member" % member)
    # A point whose DOCUMENT is the wrong shape (round-2 R2-4): the term the
    # suite asserts with is not an object at all, or carries no `vendor`. It is
    # out of domain for a reason the axis checks cannot state, so the reason
    # travels with the signature rather than being dropped on the way in.
    for problem in signature.get("shapeProblems") or ():
        problems.append(problem)
    return sorted(problem for problem in problems if problem)


def signature_from_documents(vendor, evidence, extra_members=(),
                             shape_problems=()) -> dict:
    """The canonical signature of one input point, with every member the
    registered document does NOT carry recorded rather than dropped.

    PRESENCE IS DECIDED HERE (round-2 R2-4), because here is where it is still
    knowable: a member the document does not carry reads `None`, and a member it
    carries with a JSON null reads `EXPLICIT_NULL`. `dict.get()` collapsed the
    two, and the registered domain distinguishes them."""
    vendor = vendor if isinstance(vendor, dict) else {}
    evidence = evidence if isinstance(evidence, dict) else {}
    signature = {}
    for cell, member in VENDOR_CELLS:
        signature[cell] = _presence(vendor, member)
    for cell, member in EVIDENCE_CELLS:
        signature[cell] = _presence(evidence, member)
    known_vendor = set(member for _cell, member in VENDOR_CELLS)
    known_evidence = set(member for _cell, member in EVIDENCE_CELLS)
    unknown = ["vendor.%s" % name for name in vendor if name not in known_vendor]
    unknown += ["evidence.%s" % name for name in evidence
                if name not in known_evidence]
    unknown += list(extra_members)
    signature["unknownMembers"] = sorted(unknown)
    signature["shapeProblems"] = sorted(shape_problems)
    return signature


def point_signature(value) -> dict:
    """The signature of one RESOLVED `with input as` value, whatever it is.

    Every resolved term is validated (round-2 R2-4): a term that is not an
    object, or an object carrying members the registered input document does not
    have, used to be filtered out by `_is_input_document()` and validated by
    nobody — which is a silent pass on exactly the inputs least likely to be in
    the registered space."""
    if not isinstance(value, dict):
        return signature_from_documents(
            None, None,
            shape_problems=["the `with input as` term resolves to a JSON %s and "
                            "the registered input document is an object"
                            % type(value).__name__])
    extra = [name for name in value if name not in REGO_INPUT_MEMBERS]
    shape = []
    if "vendor" not in value:
        shape.append("the `with input as` term carries no `vendor` member and "
                     "the registered input document puts every vendor fact "
                     "under it")
    for member in REGO_INPUT_MEMBERS:
        if member in value and not isinstance(value[member], dict):
            shape.append("the `with input as` term's `%s` member is a JSON %s "
                         "and the registered input document is an object of "
                         "objects" % (member, type(value[member]).__name__))
    return signature_from_documents(value.get("vendor"), value.get("evidence"),
                                    extra, shape)


# --------------------------------------------------------------------------
# arms B and C: the case inputs, out of the parser's own tree
# --------------------------------------------------------------------------

_SCALAR_TYPES = {"string": str, "number": None, "boolean": bool, "null": None}


def _named_value(term, names):
    """A package-level NAME resolved to the value the pinned binary computed
    for it, or `None` when the term is not such a name.

    Real suites write `"evidence": financial_present` — a package-level constant
    beside the table. The syntax tree carries a ref there, and the RESOLVED
    package document carries the value; substituting one for the other is the
    pinned binary's own answer, not this module's guess."""
    if not names or not isinstance(term, dict):
        return None
    if term.get("type") == "var" and term.get("value") in names:
        return names[term["value"]]
    if term.get("type") == "ref":
        path = term.get("value")
        if (isinstance(path, list) and len(path) == 1
                and isinstance(path[0], dict)
                and path[0].get("type") == "var"
                and path[0].get("value") in names):
            return names[path[0]["value"]]
    return None


def _literal(term, names=None):
    """A `opa parse --format json` term as a Python value, or `DomainError`.

    Only LITERALS convert — plus package-level NAMES whose values the pinned
    binary has already computed (`names`). A call, a comprehension or a set is a
    case whose input point cannot be read off the syntax tree at all, and the
    honest answer is a refusal naming the construct rather than a guess: this
    module's whole job is that an unenumerable case is never a silent pass."""
    resolved = _named_value(term, names)
    if resolved is not None:
        return resolved
    if not isinstance(term, dict):
        raise DomainError("DOMAIN-UNENUMERABLE-CASE a `with input as` term is "
                          "not a syntax node")
    kind = term.get("type")
    value = term.get("value")
    if kind == "object":
        if not isinstance(value, list):
            raise DomainError("DOMAIN-UNENUMERABLE-CASE an object term carries "
                              "no member list")
        out = {}
        for pair in value:
            if not isinstance(pair, list) or len(pair) != 2:
                raise DomainError("DOMAIN-UNENUMERABLE-CASE an object term "
                                  "carries a member that is not a key/value pair")
            key = _literal(pair[0], names)
            if not isinstance(key, str):
                raise DomainError("DOMAIN-UNENUMERABLE-CASE an object term "
                                  "carries a non-string key")
            out[key] = _literal(pair[1], names)
        return out
    if kind == "array":
        if not isinstance(value, list):
            raise DomainError("DOMAIN-UNENUMERABLE-CASE an array term carries "
                              "no element list")
        return [_literal(item, names) for item in value]
    if kind == "string":
        if not isinstance(value, str):
            raise DomainError("DOMAIN-UNENUMERABLE-CASE a string term carries "
                              "a non-string value")
        return value
    if kind == "number":
        return value
    if kind == "boolean":
        return bool(value)
    if kind == "null":
        return None
    raise DomainError("DOMAIN-UNENUMERABLE-CASE a `with input as` term of type "
                      "%r is not a literal input document" % (kind,))


def _is_input_target(target) -> bool:
    """`with input as ...` and not `with input.vendor as ...`.

    A PARTIAL override names a path into the document rather than the document,
    so the point it produces depends on what the rest of `input` was — which is
    not a readable input point and is refused as unenumerable by the caller."""
    if not isinstance(target, dict) or target.get("type") != "ref":
        return False
    value = target.get("value")
    return (isinstance(value, list) and len(value) == 1
            and isinstance(value[0], dict)
            and value[0].get("type") == "var"
            and value[0].get("value") == "input")


def _head_parameter_bindings(node, into: dict) -> None:
    """`f(doc) := … { … with input as doc }` — the parameter's value is at the
    CALL SITES, so it binds to them rather than to nothing.

    Real suites factor the evaluation into a helper (`decision_for(doc)` in the
    pilot's own arm-B run-004), and a helper's parameter is neither a literal nor
    a name in its own body. It is still mechanically resolvable: every call to
    the function is in the same file, and the argument in the matching position
    is a term this module already resolves."""
    head = node.get("head") if isinstance(node, dict) else None
    if not isinstance(head, dict):
        return
    arguments = head.get("args")
    name = head.get("name")
    if not isinstance(arguments, list) or not isinstance(name, str):
        return
    for index, argument in enumerate(arguments):
        parameter = _var_name(argument)
        if parameter is not None:
            into[parameter] = ("param", (name, index))


def _collect_callsites(node, into: dict, bindings=None) -> None:
    """`{function name: [(arguments, bindings in scope at the call)]}`."""
    if isinstance(node, dict):
        scope = bindings
        if isinstance(node.get("body"), list):
            scope = dict(bindings or {})
            _collect_bindings(node["body"], scope)
            _head_parameter_bindings(node, scope)
        if node.get("type") == "call" and isinstance(node.get("value"), list) \
                and node["value"]:
            name = _op_name(node["value"][0])
            if name is not None and "." not in name:
                into.setdefault(name, []).append(
                    (node["value"][1:], scope or {}))
        for value in node.values():
            _collect_callsites(value, into, scope)
    elif isinstance(node, list):
        for item in node:
            _collect_callsites(item, into, bindings)


def _walk_with_terms(node, found, bindings=None):
    """Every `with` term anywhere in the tree, in document order, each paired
    with the LOCAL BINDINGS in scope where it was written.

    Walked structurally rather than read off `rules[].body[]`: `with` modifiers
    attach to expressions, and expressions occur in rule bodies, `else` bodies,
    every-bodies and comprehension bodies alike. A walk cannot miss a site a
    later dialect adds, and missing one is exactly the silent pass R1-3 is
    about.

    The bindings travel with the term because round-2 R2-4 is about the term and
    not about the file: `with input as built` is an input point exactly when
    `built` can be resolved, and the only place `built` is defined is the body
    the modifier hangs in."""
    if isinstance(node, dict):
        scope = bindings
        if isinstance(node.get("body"), list):
            scope = dict(bindings or {})
            _collect_bindings(node["body"], scope)
            _head_parameter_bindings(node, scope)
        modifiers = node.get("with")
        if isinstance(modifiers, list):
            for modifier in modifiers:
                if isinstance(modifier, dict):
                    found.append((modifier, scope or {}))
        for key, value in node.items():
            if key != "with":
                _walk_with_terms(value, found, scope)
    elif isinstance(node, list):
        for item in node:
            _walk_with_terms(item, found, bindings)


# --- the local binding trace (round-2 R2-4) --------------------------------
#
# The reviewer's residual probe built its input point inside the rule body —
# `built := make_bad(7)` — while leaving an unrelated input-shaped literal at
# package level. The enumeration validated the aggregate of input-shaped
# literals in the tree, so the decoy made the point set non-empty and the actual
# tested input was never checked. An unrelated literal must never certify an
# indirect input, so the enumeration is now PER TERM: a `with input as` term is
# an enumerable case exactly when THAT term resolves, through the pinned
# parser's tree and the pinned evaluator's package document, to a concrete
# value. A term that does not resolve is a refusal by name, whatever else the
# file contains.

_ASSIGN_OPS = ("assign", "eq", "equal")
_MEMBER_OPS = {"internal.member_2": (0, 1), "internal.member_3": (1, 2)}
_RESOLVE_DEPTH = 12


class _Unresolved(Exception):
    """A term this module will not guess at. Never escapes the module."""


def _op_name(term):
    """The dotted operator name of an expression's head term, or None."""
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


def _var_name(term):
    if isinstance(term, dict) and term.get("type") == "var" \
            and isinstance(term.get("value"), str):
        return term["value"]
    return None


def _collect_bindings(body, into: dict) -> None:
    """`{local name: binding}` for one rule body.

    Two forms, and they are the two real suites use: `x := <term>` / `x = <term>`
    binds a term, and `some k, x in coll` (`internal.member_3`) or
    `some x in coll` (`internal.member_2`) binds x to a MEMBER of coll."""
    for expression in body or []:
        if not isinstance(expression, dict):
            continue
        terms = expression.get("terms")
        if isinstance(terms, dict):
            for symbol in terms.get("symbols") or []:
                _bind_symbol(symbol, into)
            continue
        if isinstance(terms, list) and len(terms) == 3:
            operator = _op_name(terms[0])
            if operator in _ASSIGN_OPS:
                for name, other in ((_var_name(terms[1]), terms[2]),
                                    (_var_name(terms[2]), terms[1])):
                    if name is not None and name not in into:
                        into[name] = ("term", other)
            elif operator in _MEMBER_OPS:
                _bind_symbol({"type": "call", "value": [terms[0]] + terms[1:]},
                             into)


def _bind_symbol(symbol, into: dict) -> None:
    if not isinstance(symbol, dict) or symbol.get("type") != "call":
        return
    call = symbol.get("value")
    if not isinstance(call, list) or not call:
        return
    positions = _MEMBER_OPS.get(_op_name(call[0]))
    if positions is None:
        return
    value_at, collection_at = positions
    arguments = call[1:]
    if len(arguments) <= max(value_at, collection_at):
        return
    name = _var_name(arguments[value_at])
    if name is not None and name not in into:
        into[name] = ("member", arguments[collection_at])


def _index(value, key):
    """One step of a static path into a resolved value."""
    if isinstance(value, dict) and key in value:
        return value[key]
    if isinstance(value, list) and isinstance(key, int) \
            and 0 <= key < len(value):
        return value[key]
    raise _Unresolved("the path step %r is not in the resolved value" % (key,))


def _members(value):
    if isinstance(value, dict):
        return list(value.values())
    if isinstance(value, (list, tuple)):
        return list(value)
    raise _Unresolved("a `some … in` collection resolved to a JSON %s"
                      % type(value).__name__)


def _resolve_term(term, bindings, names, depth=0, callsites=None) -> list:
    """Every concrete value `term` can take, or `_Unresolved`.

    A literal is itself; a package-level name is what the pinned binary computed
    for it; a local is what its binding says; a function parameter is what its
    call sites pass; a static path into any of those is that path applied. A
    call, a comprehension, an arithmetic expression or a name nothing in scope
    defines is UNRESOLVED — and unresolved is a refusal, never a zero."""
    if depth > _RESOLVE_DEPTH:
        raise _Unresolved("the binding chain is longer than %d steps"
                          % _RESOLVE_DEPTH)
    try:
        return [_literal(term, names)]
    except DomainError:
        pass
    name = _var_name(term)
    if name is not None:
        return _resolve_name(name, [], bindings, names, depth, callsites)
    if isinstance(term, dict) and term.get("type") == "ref":
        path = term.get("value")
        if isinstance(path, list) and path:
            root = _var_name(path[0])
            if root is not None:
                steps = []
                for node in path[1:]:
                    if not isinstance(node, dict) \
                            or node.get("type") not in ("string", "number"):
                        raise _Unresolved("a path step is a %r term"
                                          % (node or {}).get("type"))
                    steps.append(node.get("value"))
                return _resolve_name(root, steps, bindings, names, depth,
                                     callsites)
    raise _Unresolved("a %r term is not a readable input point"
                      % (term or {}).get("type"))


def _resolve_name(name, steps, bindings, names, depth, callsites=None) -> list:
    # The NEAREST scope first: a name the rule body binds is that binding, and a
    # name nothing in the body binds is the package-level rule of that name.
    if name in (bindings or {}):
        kind, term = bindings[name]
        if kind == "param":
            roots = _resolve_parameter(term, names, depth, callsites)
        else:
            resolved = _resolve_term(term, bindings, names, depth + 1,
                                     callsites)
            roots = resolved if kind == "term" else [
                member for value in resolved for member in _members(value)]
    elif names and name in names:
        roots = [names[name]]
    else:
        raise _Unresolved("the name %r is not a package-level rule and nothing "
                          "in its rule body binds it" % name)
    if not steps:
        return roots
    out = []
    for root in roots:
        value = root
        for step in steps:
            value = _index(value, step)
        out.append(value)
    return out


def _resolve_parameter(where, names, depth, callsites) -> list:
    """A function parameter, resolved from every call site in the file."""
    function, position = where
    sites = (callsites or {}).get(function) or []
    if not sites:
        raise _Unresolved("the parameter %d of %r is never passed a value "
                          "anywhere in the suite" % (position, function))
    values = []
    for arguments, scope in sites:
        if position >= len(arguments):
            raise _Unresolved("a call to %r passes %d argument(s) and the "
                              "parameter is at position %d"
                              % (function, len(arguments), position))
        values.extend(_resolve_term(arguments[position], scope, names,
                                    depth + 1, callsites))
    return values


def parse_tree(raw: bytes):
    """`opa parse --format json` output as a document, with every JSON number
    decoded as a `Decimal`.

    The decode is the load-bearing part. `requestedSpend` values sit on either
    side of a threshold the policy tests with `>`, and a float round-trip of
    `100000.01` is a silent boundary flip — the same hazard
    `engines.render_rego_input()` exists to avoid on the way out."""
    try:
        return json.loads(raw.decode("utf-8"), parse_float=Decimal,
                          parse_int=int)
    except (ValueError, UnicodeDecodeError) as error:
        raise DomainError("DOMAIN-UNPARSEABLE-SUITE `opa parse` emitted no "
                          "readable syntax tree (%s)" % type(error).__name__)


def canonical(value) -> str:
    """One spelling of a value, so two readings of one input point collapse."""
    return json.dumps(value, sort_keys=True, default=str)


def cases_from_tree(document, names=None) -> tuple:
    """`(unresolved, [(index, signature)])` — one reading PER `with input as`
    TERM.

    TWO ENUMERATION MODES, because real authored suites use both and a mode that
    only handles one would either refuse most suites or silently validate none
    of them:

    * **direct** — `with input as {…}`, the literal in the modifier itself;
    * **recovered** — `with input as tc.input` over a TABLE, which is what the
      pilot's own arm-B and arm-C suites do. The modifier names its point rather
      than carrying it, so the name is resolved: against the pinned evaluator's
      package document for a package-level rule, and against the rule body's own
      `:=` and `some … in` bindings for a local.

    ROUND-2 FINDING R2-4, second half, and it is why this is per term. The scan
    used to be over every input-shaped OBJECT LITERAL anywhere in the tree, and
    the suite was accepted whenever that aggregate was non-empty. So a suite
    could carry one unrelated valid literal — the reviewer's `decoy` — build its
    real input inside a rule body (`built := make_bad(7)`, `newVendor: 7`) and
    have the decoy certify it: the actual asserted point was never enumerated,
    never domain-checked, and went on to kill four paired mutants. The point set
    is now exactly the set the `with input as` terms RESOLVE to, so a literal no
    term names certifies nothing, and a term that resolves to nothing is
    `unresolved` — which the caller turns into the registered authoring code.

    `unresolved` is the list of those refusals, one message per term. It replaces
    a bare count: a caller that must refuse should be able to say which term.

    Duplicates collapse: two tests asserting about one input point are one point,
    and the domain check is about points."""
    modifiers, callsites = [], {}
    _collect_callsites(document, callsites)
    _walk_with_terms(document, modifiers)
    unresolved, values = [], []
    for modifier, bindings in modifiers:
        if not _is_input_target(modifier.get("target")):
            raise DomainError(
                "DOMAIN-UNENUMERABLE-CASE a `with` term overrides something "
                "other than the whole `input` document, so its input point "
                "cannot be read from the suite")
        try:
            values.extend(_resolve_term(modifier.get("value"), bindings,
                                        names, 0, callsites))
        except _Unresolved as error:
            unresolved.append(str(error))
    return unresolved, resolved_points(values)


def resolved_points(values) -> list:
    """`[(index, signature)]` over the values `with input as` terms resolved to,
    deduplicated. EVERY value is validated, whatever its shape."""
    points, seen = [], set()
    for value in values:
        key = canonical(value)
        if key in seen:
            continue
        seen.add(key)
        points.append(value)
    return [(index, point_signature(value))
            for index, value in enumerate(points)]


def package_path(document) -> str:
    """`data.<package>` from a parse tree, for the evaluation query."""
    path = ((document or {}).get("package") or {}).get("path")
    if not isinstance(path, list) or not path:
        raise DomainError("DOMAIN-UNPARSEABLE-SUITE the syntax tree names no "
                          "package, so its resolved document has no query")
    parts = []
    for term in path:
        value = term.get("value") if isinstance(term, dict) else None
        if not isinstance(value, str):
            raise DomainError("DOMAIN-UNPARSEABLE-SUITE the package path is not "
                              "a list of names")
        parts.append(value)
    return ".".join(parts)


def package_document(raw: bytes):
    """The value `opa eval` computed for a package query, or `None`."""
    document = json.loads(raw.decode("utf-8"), parse_float=Decimal)
    try:
        return document["result"][0]["expressions"][0]["value"]
    except (KeyError, IndexError, TypeError):
        return None
