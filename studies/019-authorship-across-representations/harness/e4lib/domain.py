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

def _enum_problem(cell, value, allowed, optional):
    """One enumerated axis. An omitted member is `None`; a null or a sentinel
    string is NOT an omission and is reported as the value it is."""
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
    return sorted(problem for problem in problems if problem)


def signature_from_documents(vendor, evidence, extra_members=()) -> dict:
    """The canonical signature of one input point, with every member the
    registered document does NOT carry recorded rather than dropped."""
    vendor = vendor if isinstance(vendor, dict) else {}
    evidence = evidence if isinstance(evidence, dict) else {}
    signature = {}
    for cell, member in VENDOR_CELLS:
        signature[cell] = vendor.get(member)
    for cell, member in EVIDENCE_CELLS:
        signature[cell] = evidence.get(member)
    known_vendor = set(member for _cell, member in VENDOR_CELLS)
    known_evidence = set(member for _cell, member in EVIDENCE_CELLS)
    unknown = ["vendor.%s" % name for name in vendor if name not in known_vendor]
    unknown += ["evidence.%s" % name for name in evidence
                if name not in known_evidence]
    unknown += list(extra_members)
    signature["unknownMembers"] = sorted(unknown)
    return signature


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


def _walk_with_terms(node, found):
    """Every `with` term anywhere in the tree, in document order.

    Walked structurally rather than read off `rules[].body[]`: `with` modifiers
    attach to expressions, and expressions occur in rule bodies, `else` bodies,
    every-bodies and comprehension bodies alike. A walk cannot miss a site a
    later dialect adds, and missing one is exactly the silent pass R1-3 is
    about."""
    if isinstance(node, dict):
        modifiers = node.get("with")
        if isinstance(modifiers, list):
            for modifier in modifiers:
                if isinstance(modifier, dict):
                    found.append(modifier)
        for key, value in node.items():
            if key != "with":
                _walk_with_terms(value, found)
    elif isinstance(node, list):
        for item in node:
            _walk_with_terms(item, found)


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


def _walk_object_literals(node, found, names=None):
    """Every INPUT-SHAPED object in the tree, as Python values, best-effort.

    An object term that converts is descended into as DATA — a case table
    converts whole, and the input documents live one level inside it, so
    stopping at the outermost convertible object would collect the table and
    none of its cases. A term that does not convert contributes nothing and
    stops that branch; the caller decides what an unconvertible branch means."""
    if isinstance(node, dict):
        if node.get("type") == "object":
            try:
                _collect_documents(_literal(node, names), found)
                return
            except DomainError:
                pass
        for value in node.values():
            _walk_object_literals(value, found, names)
    elif isinstance(node, list):
        for item in node:
            _walk_object_literals(item, found, names)


def _is_input_document(value) -> bool:
    """The registered Rego input document's shape: `{"vendor": …}` with at most
    `evidence` beside it.

    `vendor` is the discriminating member — the naming appendix puts every
    vendor fact under it — and it is what makes an input document recognisable
    inside a table entry that also carries a name and an expectation."""
    return (isinstance(value, dict) and "vendor" in value
            and set(value) <= set(REGO_INPUT_MEMBERS))


def canonical(value) -> str:
    """One spelling of a value, so two readings of one input point collapse."""
    return json.dumps(value, sort_keys=True, default=str)


def cases_from_tree(document, names=None) -> tuple:
    """`[(index, signature)]` for every input point this suite asserts about.

    TWO ENUMERATION MODES, because real authored suites use both and a mode that
    only handles one would either refuse most suites or silently validate none
    of them:

    * **direct** — `with input as {…}`, the literal in the modifier itself;
    * **recovered** — `with input as tc.input` over a TABLE, which is what the
      pilot's own arm-B and arm-C suites do. The input points are still literals
      in the file, one level in; the modifier names them rather than carrying
      them.

    So the scan is over every OBJECT LITERAL in the tree that has the registered
    input document's shape, which is a superset of the direct terms and is
    exactly as mechanical: it is the pinned parser's own tree, and no string
    matching, no evaluation and no guess about what a test intends.

    The one thing that is never a silent pass: a suite whose `with input as`
    terms are all indirect AND in which no input-shaped literal exists at all
    has constructed its points by some computation, and this refuses rather than
    reporting zero cases and validating nothing.

    Duplicates collapse: two tests asserting about one input point are one point,
    and the domain check is about points."""
    modifiers = []
    _walk_with_terms(document, modifiers)
    indirect = 0
    for modifier in modifiers:
        if not _is_input_target(modifier.get("target")):
            raise DomainError(
                "DOMAIN-UNENUMERABLE-CASE a `with` term overrides something "
                "other than the whole `input` document, so its input point "
                "cannot be read from the suite")
        try:
            value = _literal(modifier.get("value"), names)
        except DomainError:
            indirect += 1
            continue
        if not isinstance(value, dict):
            indirect += 1
    literals = []
    _walk_object_literals(document, literals, names)
    return indirect, input_points(literals)


def input_points(values) -> list:
    """`[(index, signature)]` for the input-shaped documents among `values`,
    deduplicated. Two tests asserting about one point are one point."""
    points, seen = [], set()
    for value in values:
        if not _is_input_document(value):
            continue
        key = canonical(value)
        if key in seen:
            continue
        seen.add(key)
        points.append(value)
    cases = []
    for index, value in enumerate(points):
        extra = [name for name in value if name not in REGO_INPUT_MEMBERS]
        cases.append((index, signature_from_documents(value.get("vendor"),
                                                      value.get("evidence"),
                                                      extra)))
    return cases


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


def resolved_input_points(raw: bytes) -> list:
    """The input points inside an `opa eval` result document.

    THE SECOND ENUMERATION MODE, and the one real suites need. The pilot's own
    arm-B and arm-C suites build their case inputs out of named constants
    (`"evidence": financial_present`) and helper functions
    (`make_input(status, …)` over `object.union`), so the SYNTAX tree carries a
    ref exactly where the point is. Evaluating the suite's own package resolves
    them — with the pinned binary, under the pinned capabilities, at the
    registered flags — and the result is data this module can walk the same way
    it walks a literal. No string matching, no re-implementation of Rego, and no
    guess about what a test intends."""
    value = package_document(raw)
    if value is None:
        return []
    found = []
    _collect_documents(value, found)
    return input_points(found)


def _collect_documents(node, found):
    if isinstance(node, dict):
        if _is_input_document(node):
            found.append(node)
            return
        for item in node.values():
            _collect_documents(item, found)
    elif isinstance(node, list):
        for item in node:
            _collect_documents(item, found)
