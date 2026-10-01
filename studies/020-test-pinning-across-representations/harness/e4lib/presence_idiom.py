"""The presence-idiom detector — §3.2's registered guard, and NOTHING else.

NEW IN STUDY 020. Not ported and not assembled from a design prototype: nothing
like it existed in Study 019, which is why `harness/PORTS.md` carries no row for
it and `integrity.REQUIRED_PORTS` deliberately does not name it. A two-sided
row would claim an inheritance that does not exist.

WHY IT EXISTS (M-14, the forensic verdict of 2026-08-23)
--------------------------------------------------------------------------
One Rego language-semantics error is Study 019's whole arm-B/C E1 collapse:
**`"key" in object` tests VALUES, not keys.** The presence test gating U1 —
`"riskScore" in input.vendor` — is false even when the member is present, so
every input is judged unreadable, the candidate sweep fires on every row, and
the grid almost never collapses to a singleton. Proven both ways: repairing
only that operator takes `run-011` from 31/86/0 to 117/117, and mutating the
correct idiom OUT of eight perfect runs collapses 8/8 to the exact observed
signature. Discriminator: 40 of 76 arm-B/C policies use bare-object `in` and
none of them is perfect; all 22 perfect runs avoid it.

WHAT THIS MODULE IS, AND THE FOUR THINGS IT IS NOT
--------------------------------------------------------------------------
It is a **detector at the ADMISSION layer**. A policy it flags receives the
registered authoring-outcome code `presence-idiom-unsound` (§1a's table, E2's
ordered table): valid, counted, and scoring zero on every endpoint it reaches,
exactly as the other authoring codes do.

It does **not rewrite the operator** — that would change the authored artifact,
i.e. the treatment. It does **not exclude the run** — that would delete an
authoring outcome. It does **not gate the batch**. It emits **no prompt-side
text**: §3.2 registers the prose variant OUT on measured grounds, because the
prompt's bundled Rego reference already flags this exact trap
(`"foo" in {"foo": 1} # false`) and it fired in 40 of 76 runs anyway.

It is at the admission layer and not at the engine layer because an
engine-level guard would have to change what the pinned OPA binary does, which
is outside the registered system boundary (§3.1) and would break the binary
digest pin.

THE RULE, AND IT IS A SYNTAX-TREE RULE IN TWO PARTS
--------------------------------------------------------------------------
§3.2: *flag any `in` term whose right operand is, on the syntax tree, an
**object** (or a reference resolving to an object member of `input`) rather
than a set or an array.*

**Part one: is it a PRESENCE TEST at all?** `opa parse --format json` lowers
`x in xs` to `internal.member_2` and `k, v in xs` to `internal.member_3`,
writing the first as an expression's `terms` list and the second — when it is
written `some x in xs` — as a call term under `terms.symbols`. Both shapes are
read. What separates the defect from correct Rego is the LEFT operand:
`"riskScore" in vendor` asks whether `vendor` CONTAINS that value, which over an
object is the M-14 bug, while `some x in vendor` BINDS `x` to each member and is
a lawful iteration over any collection. In Study 019's arm-B/C corpus 351 of the
599 memberships are iterations; flagging them would have zero-scored correct
suites at scale, and the scalar-probe condition is what prevents it.

**Part two: is the collection an OBJECT?** Only then is the right operand
resolved:

| operand | verdict | why |
|---|---|---|
| `object` / `objectcomprehension` term | FLAG | membership tests its VALUES |
| `ref` onto a registered OBJECT path of `input` | FLAG | `input.vendor` is an object by the registered input document |
| a NAME bound, in this document, to either | FLAG | the same defect through one indirection — 83 of 178 flagged uses in 019's corpus reach the object this way |
| `object.get(input, "<member>", …)` with a literal path | FLAG | that call IS `input.<member>` |
| `array`, `set`, and their comprehensions | lawful | membership over a collection, which is what `in` is for |
| any other `call` | lawful | `object.keys(x)` and friends; a user function's return type is not on the syntax tree |
| `ref` onto a scalar path of `input`, or into `data` | lawful | not an object by the registered document |
| an unbound name, a dynamic ref tail, a computed `object.get` path | **unclassified** | reported, never guessed at in either direction |

**The object paths are DERIVED, never enumerated.** `object_input_paths()`
computes them from `domain.REGO_INPUT_MEMBERS` — the registered input
document's own member list — plus the root `input` itself. The registered
document is `{"vendor": {…}, "evidence": {…}}` with scalars beneath, so the
object-valued paths are exactly `input`, `input.vendor` and `input.evidence`,
and they move if and only if the registered document moves. Writing the three
paths out here would be a list that goes stale the first time the domain does.

**The alias step is DEFINITION RESOLUTION, not dataflow.** `bindings()` reads
the two static single-assignment forms the parser produces — a package-level
`name := term` and a body-level `assign`/`eq` expression — compares repeated
bindings by CONTENT rather than by identity (two rule bodies writing
`vendor := input.vendor` are one binding in the language), and drops any name
bound to two different terms rather than resolving it to either. Nothing is
evaluated and no path is followed more than `ALIAS_DEPTH` steps.

THE MEASURED CEILINGS, from `harness/POWER-PRESENCE-IDIOM.md`
--------------------------------------------------------------------------
1. **A presence test over a FUNCTION PARAMETER is not detected.**
   `risk_values(vendor) := [vendor.riskScore] if { "riskScore" in vendor }`,
   called with `input.vendor`, is the same defect across a function boundary;
   the collection is a parameter and neither this detector nor the independent
   source oracle used to certify it resolves one. TWO runs of Study 019's 76 are
   in that state, both non-perfect, and the residual is published rather than
   closed.
2. **Alias scope is over-approximated.** A body-level binding is visible to the
   whole document. On 019's corpus that costs nothing — the per-run flag counts
   agree with the independent oracle exactly, 73 of 73 — and it is measured
   rather than assumed.
3. **The guard is arm-asymmetric by construction** (§11.11). The code is
   structurally unreachable in arm A, whose format has no analogous
   single-operator trap on this surface, and arm A's own near-miss profile in
   019 stands unexplained by this mechanism.
4. **A policy `opa parse` refuses is not a policy this detector has an opinion
   about.** It raises `PresenceIdiomError`; the caller has already admitted the
   artifact through `opa check`, so a parse refusal after a passing check is an
   APPARATUS fact and never a silent "not flagged".

THE CERTIFICATION, AND ITS KILL SWITCH
--------------------------------------------------------------------------
`harness/POWER-PRESENCE-IDIOM.md` is §3.2's `GATE(pre-freeze)` power analysis,
computed over Study 019's retained bytes: **40/40 in-class runs receive an
authoring code** (39/39 of the policies the detector reaches, 32/32 admitted),
**0/22 perfect runs flagged**, **0/392 lawful `in` uses and 0/15 over sets and
arrays**, and the registered mutation check takes sensitivity from 39/39 to
23/39 when the object branch is dropped. `harness/PINS.json`'s
`presenceIdiomGuard.registered` carries the verdict as DATA, and
`e4lib/admit.py`'s `guard_is_registered()` is the only reader — fail-shut, so a
registry that lost the member withholds the code rather than emitting it.
"""
from __future__ import annotations

import json

from . import domain, engines

# The two builtins `opa parse` lowers `in` to. `member_2` is `x in xs`;
# `member_3` is `k, v in xs`. Named as REFS (the AST's own shape) rather than as
# dotted strings, so the comparison is against the tree and not against a
# rendering of it.
MEMBERSHIP_REFS = (("internal", "member_2"), ("internal", "member_3"))

# The operand types §3.2 calls "a set or an array", widened to every term form
# that is one by construction. A type outside BOTH tables is reported as
# `unclassified` and is NOT flagged — a detector that flags what it does not
# recognise is a detector whose false-positive rate is a function of the OPA
# release, and §3.2 registers the false-positive census as a number.
LAWFUL_TYPES = ("array", "set", "arraycomprehension", "setcomprehension",
                "boolean", "number", "string", "null")
# `objectcomprehension` is deliberately absent from LAWFUL_TYPES: `"k" in {k: v |
# …}` is a presence test over an OBJECT built by a comprehension, which is the
# same defect the literal form has.
OBJECT_TYPES = ("object", "objectcomprehension")
# The term types a PROBE (the membership's left operand) may have for the
# membership to be a PRESENCE TEST rather than an iteration. `"key" in xs` asks
# whether `xs` CONTAINS the key; `some x in xs` binds `x` to each member and is
# lawful over any collection, objects included. The distinction is the whole of
# what keeps the detector off `some x in input.vendor`, which is correct Rego.
SCALAR_TYPES = ("string", "number", "boolean")

FLAG_OBJECT_TERM = "object-term"
FLAG_OBJECT_INPUT_REF = "object-input-ref"
FLAG_OBJECT_ALIAS = "object-input-alias"
FLAG_REASONS = (FLAG_OBJECT_TERM, FLAG_OBJECT_INPUT_REF, FLAG_OBJECT_ALIAS)

# The one builtin whose return value this module resolves. `object.get(input,
# "vendor", {})` IS `input.vendor` when the path is literal, and an author who
# reaches the object that way and then tests a key in it has written the same
# defect. Nothing else is resolved: a user-defined function's return type is not
# on the syntax tree, and guessing at it is how a detector acquires false
# positives (§3.2(iii), and ceiling 3 below).
OBJECT_GET = ("object", "get")

# The §1a authoring-outcome code this detector produces. `batch.CODE_PARTITION`
# is the authority for the name and `harness/tests/test_partition.py` diffs the
# two, so this constant may not drift into a second spelling.
CODE = "presence-idiom-unsound"

# How deep an alias chain is followed before the resolution gives up. A chain
# longer than this is reported as unresolved and NOT flagged, which is the
# conservative direction: the detector under-reports rather than guessing.
ALIAS_DEPTH = 8


class PresenceIdiomError(Exception):
    """A refusal about the DETECTOR — never a verdict about a policy."""


def object_input_paths() -> tuple:
    """The registered OBJECT-valued paths of the input document, derived.

    `domain.REGO_INPUT_MEMBERS` is the registered document's own member list and
    every member of it is an object keyed by fact name or requirement id; every
    path below that is a scalar. The root `input` is an object too, and
    `"riskScore" in input` is the same defect one level up, so it is here.

    Returned as tuples of path components, which is the shape `_ref_path()`
    produces, so the comparison never goes through a rendered string."""
    return (("input",),) + tuple(("input", member)
                                 for member in domain.REGO_INPUT_MEMBERS)


def parse_policy(tools: engines.Toolchain, policy_path: str,
                 workdir: str) -> dict:
    """`opa parse --format json` over one policy file, as a document.

    The pinned binary is the parser: this module carries no Rego grammar, for
    the reason §2 gives about reading verdicts from payloads rather than from
    exit codes, and for the stronger reason that a second grammar is a second
    thing that can disagree with the engine the study actually runs."""
    # ROUND-2 FINDING R2-1: `opa_parse_tree()` now raises `engines.EngineError`
    # itself on every NO-ANSWER exit (124 and the invocation failures), so this
    # function is reached only when the parser ANSWERED. Exit 1 is such an
    # answer — a readable syntax refusal — and it is the one residual state
    # `PresenceIdiomError` still names: two pinned invocations disagreeing about
    # the same bytes, `opa check` accepting the policy and `opa parse` refusing
    # it. `admit_arm_rego()` converts that to the same apparatus refusal,
    # because no verdict about the AUTHOR survives a disagreement between the
    # study's own engines (§1a's amendment block carries the marked note).
    code, out, err = engines.opa_parse_tree(tools, policy_path, workdir)
    if code != 0:
        raise PresenceIdiomError(
            "PRESENCE-IDIOM-PARSE-REFUSED `opa parse` exited %s on an ADMITTED "
            "policy: the artifact passed `opa check`, so a parse refusal here "
            "is an apparatus fact and not a policy this detector may pass "
            "silently (%s)" % (code, (err or out or "").strip()[:200]))
    try:
        return json.loads(out)
    except ValueError as error:
        raise PresenceIdiomError(
            "PRESENCE-IDIOM-PARSE-UNREADABLE `opa parse --format json` emitted "
            "no readable document (%s)" % type(error).__name__)


def _ref_path(term):
    """`("input", "vendor")` for the AST of `input.vendor`, or None.

    Only a ref whose head is a var and whose tail is all string keys has a
    static path. `input[k]` has a var in its tail and therefore no path, which
    is the correct answer: this detector does not resolve variables."""
    if not isinstance(term, dict) or term.get("type") != "ref":
        return None
    parts = term.get("value")
    if not isinstance(parts, list) or not parts:
        return None
    head = parts[0]
    if not isinstance(head, dict) or head.get("type") != "var":
        return None
    path = [head.get("value")]
    for element in parts[1:]:
        if not isinstance(element, dict) or element.get("type") != "string":
            return None
        path.append(element.get("value"))
    return tuple(path)


def _call_head(term):
    """The dotted path of a call's callee, or None for anything else."""
    if not isinstance(term, dict) or term.get("type") != "call":
        return None
    parts = term.get("value")
    if not isinstance(parts, list) or not parts:
        return None
    return _ref_path(parts[0])


def _literal_path(term):
    """A literal path argument to `object.get`: `"vendor"` or `["vendor", "x"]`."""
    if not isinstance(term, dict):
        return None
    if term.get("type") == "string":
        return (term.get("value"),)
    if term.get("type") == "array":
        parts = term.get("value")
        if isinstance(parts, list) and all(
                isinstance(element, dict) and element.get("type") == "string"
                for element in parts):
            return tuple(element.get("value") for element in parts)
    return None


def bindings(ast: dict) -> dict:
    """{name: bound term} for every STATIC single assignment in the document.

    Two forms, both read off the syntax tree and neither of them an evaluation:

    * a package-level rule `vendor := input.vendor`, which parses as a head with
      `assign: true`, a single-var `ref` and a `value`;
    * a body-level `v := <term>` or `v = <term>`, which parses as an expression
      whose callee is the bare ref `assign` (or `eq`) and whose operands are a
      var and the bound term.

    A name bound more than once ANYWHERE in the document is dropped rather than
    resolved to either binding: two bindings are two possible values, and a
    detector that picked one would be guessing. Dropping is the conservative
    direction — the membership is then unresolved and is not flagged.

    Scope is deliberately ignored. A body-level binding in one rule is visible
    to this map in every rule, which over-approximates the alias set; combined
    with the drop-on-conflict rule above, the effect is that a name means one
    thing in the whole document or it means nothing here. On Study 019's corpus
    that costs nothing and it is measured, not assumed (§3.2(iii)'s census)."""
    found, conflicted = {}, set()

    def record(name, term):
        if not isinstance(name, str):
            return
        # Compared by CONTENT, not by identity. Two rule bodies that each write
        # `vendor := input.vendor` are two distinct dicts in the parsed
        # document and one binding in the language, and an identity comparison
        # calls them a conflict — which drops exactly the commonest alias in
        # this corpus and turns a detection into a false negative.
        if name in found and _same(found[name], term):
            return
        if name in found:
            conflicted.add(name)
        found[name] = term

    for node in _walk(ast):
        head = node.get("head")
        if isinstance(head, dict) and head.get("assign") and "value" in head:
            path = _ref_path({"type": "ref", "value": head.get("ref")}) \
                if isinstance(head.get("ref"), list) else None
            if path and len(path) == 1:
                record(path[0], head["value"])
        terms = node.get("terms")
        if isinstance(terms, list) and len(terms) == 3:
            callee = _ref_path(terms[0])
            if callee in (("assign",), ("eq",)) \
                    and isinstance(terms[1], dict) \
                    and terms[1].get("type") == "var":
                record(terms[1].get("value"), terms[2])
    for name in conflicted:
        found.pop(name, None)
    return found


def _same(left, right) -> bool:
    """Two parsed terms that are the same term. Canonical JSON, because the AST
    is JSON and a canonical rendering is the cheapest total comparison there
    is."""
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def _ref_path_resolved(term, bound):
    """R1-10(b): `_ref_path()` with statically-bound var tail elements
    resolved through the bindings map. Returns the static path, or None when
    any element stays dynamic."""
    if not isinstance(term, dict) or term.get("type") != "ref":
        return None
    parts = term.get("value") or []
    path = []
    for index, part in enumerate(parts):
        if not isinstance(part, dict):
            return None
        if part.get("type") == "var":
            name = part.get("value")
            if index == 0:
                path.append(name)
                continue
            binding = bound.get(name) if bound else None
            if isinstance(binding, dict) and binding.get("type") == "string":
                path.append(binding.get("value"))
                continue
            return None
        if part.get("type") == "string":
            path.append(part.get("value"))
            continue
        return None
    return tuple(path)


def _string_probe(term, bound, depth=0):
    """R1-10(a) and (c) in one predicate: is this probe a STRING presence
    probe — a string literal, or a name statically bound to one?

    Two registered narrowings over the first implementation, each measured on
    the certification corpus before adoption (probe census there:
    351 var / 248 string, zero number or boolean):

    - (a) a var bound to a string literal IS a probe (`k := "riskScore";
      k in input.vendor` is M-14 with one extra line, and the first
      implementation called it lawful before resolving the binding);
    - (c) a NON-STRING scalar (number, boolean) is NOT in the guard's
      certified class: `5 in {"x": 5}` is lawful value membership over an
      object's values, and flagging it zero-scored a correct policy. The
      numeric-key trap (`5 in {5: "x"}`) is therefore OUTSIDE the guard —
      §3.2 registers it as the third measured ceiling rather than guessing
      at key sets statically.
    """
    if depth > ALIAS_DEPTH or not isinstance(term, dict):
        return False
    kind = term.get("type")
    if kind == "string":
        return True
    if kind == "var":
        name = term.get("value")
        binding = bound.get(name) if bound else None
        if binding is not None:
            return _string_probe(binding, bound, depth + 1)
        return False
    if kind == "ref":
        path = _ref_path(term)
        if path is not None and len(path) == 1 and bound                 and path[0] in bound:
            return _string_probe(bound[path[0]], bound, depth + 1)
        return False
    return False


def _object_valued(term, bound, depth=0):
    """`(True|False|None, kind)` — is this term an OBJECT, on the syntax tree?

    `None` means unresolved, which is not the same as False and is reported as
    such: a membership over an unresolved term is not flagged, and §3.2(iii)'s
    census counts how many there were."""
    if depth > ALIAS_DEPTH or not isinstance(term, dict):
        return None, "unresolved"
    kind = term.get("type")
    if kind in OBJECT_TYPES:
        return True, FLAG_OBJECT_TERM
    if kind in LAWFUL_TYPES:
        return False, kind
    if kind == "ref":
        path = _ref_path(term)
        if path is None:
            # ROUND-1 FINDING R1-10(b): a tail element that is a VAR bound
            # statically to a string literal is a static path wearing a
            # variable's name — `member := "vendor"; "k" in input[member]` —
            # and the bindings map this module already keeps resolves it.
            # A tail with any genuinely unresolvable element keeps the
            # unclassified verdict, exactly as before.
            path = _ref_path_resolved(term, bound)
        if path is None:
            return None, "ref-with-dynamic-tail"
        if path in object_input_paths():
            return True, FLAG_OBJECT_INPUT_REF
        if path[0] == "input":
            return False, "input-scalar-ref"
        if len(path) == 1 and path[0] in bound:
            resolved, why = _object_valued(bound[path[0]], bound, depth + 1)
            return resolved, (FLAG_OBJECT_ALIAS if resolved else why)
        return False, "ref"
    if kind == "call":
        if _call_head(term) == OBJECT_GET:
            arguments = term.get("value") or []
            if len(arguments) >= 3:
                base = _ref_path(arguments[1])
                inside = _literal_path(arguments[2])
                if base is not None and inside is not None:
                    whole = base + inside
                    if whole in object_input_paths():
                        return True, FLAG_OBJECT_ALIAS
                    if whole[0] == "input":
                        return False, "object-get-scalar"
            return None, "object-get-dynamic"
        return False, "call"
    if kind == "var":
        name = term.get("value")
        if name in bound:
            resolved, why = _object_valued(bound[name], bound, depth + 1)
            return resolved, (FLAG_OBJECT_ALIAS if resolved else why)
        return None, "unbound-var"
    return None, str(kind)


def classify(probe, collection, bound) -> tuple:
    """`(verdict, kind)` for one membership.

    TWO conditions, and the first is what keeps the detector off correct Rego.
    A membership is a PRESENCE TEST only when its left operand is a scalar
    literal: `"riskScore" in vendor` asks whether `vendor` contains that value,
    which over an object is the M-14 defect. `some x in vendor` BINDS `x` to
    each member and is a lawful iteration over any collection, objects
    included — and it is the commonest `in` in this corpus. Flagging it would
    zero-score correct suites, which is what §3.2(iii)'s census exists to
    measure and what this condition prevents.

    Only then is the collection resolved. `verdict` is `"flag"`, `"lawful"` or
    `"unclassified"`; `kind` names WHY, and for a flag it is one of
    `FLAG_REASONS` so the census can be read by mechanism rather than by
    count."""
    probe_type = probe.get("type") if isinstance(probe, dict) else None
    if probe_type in SCALAR_TYPES and probe_type != "string":
        # R1-10(c): a number or boolean probe is VALUE membership — lawful
        # over an object's values — and the numeric-key trap is the third
        # measured ceiling, not a guess this module makes.
        return "lawful", "value-membership"
    if not _string_probe(probe, bound):
        return "lawful", "iteration-or-binding"
    resolved, kind = _object_valued(collection, bound)
    if resolved is True:
        return "flag", kind
    if resolved is False:
        return "lawful", kind
    return "unclassified", kind


def classify_operand(term, bound=None) -> tuple:
    """`classify()` for a PRESENCE TEST over `term` — the single-operand form
    the tests and the census read."""
    return classify({"type": "string", "value": "probe"}, term, bound or {})


def _walk(node):
    """Every dict in the document, depth-first. The AST's shape varies by rule
    form — bodies, `else` chains, comprehension bodies, `with` modifiers, `some`
    declarations — so the scan is structural rather than a list of the places a
    membership is allowed to appear. A form this module has never seen still has
    its membership found."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _membership_operands(node):
    """The operand list of a membership, or None — in EITHER of the two shapes
    the parser produces.

    An `in` written as an expression parses as a `terms` LIST whose first
    element is the `internal.member_N` ref. An `in` written inside a `some`
    declaration parses as a `call` TERM with the same head, nested under
    `terms.symbols`. Reading only the first shape would make every `some x in
    …` invisible — which happens to be the right verdict for an iteration and
    is the WRONG REASON for it, so both shapes are read and `classify()` is
    what decides."""
    terms = node.get("terms")
    if isinstance(terms, list) and len(terms) >= 2 \
            and _ref_path(terms[0]) in MEMBERSHIP_REFS:
        return list(terms), "expression"
    if node.get("type") == "call" and _call_head(node) in MEMBERSHIP_REFS:
        value = node.get("value")
        if isinstance(value, list) and len(value) >= 2:
            return list(value), "some-declaration"
    return None, None


def memberships(ast: dict) -> list:
    """Every `in` term in the document, in both shapes, with its verdict."""
    bound = bindings(ast)
    found = []
    for node in _walk(ast):
        operands, form = _membership_operands(node)
        if operands is None:
            continue
        collection = operands[-1]
        probe = operands[1] if len(operands) > 2 else None
        verdict, kind = classify(probe, collection, bound)
        found.append({
            "builtin": ".".join(_ref_path(operands[0]) or ()),
            "form": form,
            "operands": len(operands) - 1,
            "probeType": probe.get("type") if isinstance(probe, dict) else None,
            "collectionType": collection.get("type")
            if isinstance(collection, dict) else None,
            "collectionPath": list(_ref_path(collection) or ()) or None,
            "verdict": verdict,
            "kind": kind,
        })
    return found


def scan_ast(ast: dict) -> dict:
    """The detector's whole answer over one parsed policy.

    `flagged` is the admission verdict. Everything else is the census §3.2(iii)
    requires: every membership in the policy with its verdict, so a
    false-positive rate over LAWFUL uses is a count and not an assertion."""
    uses = memberships(ast)
    flagged = [use for use in uses if use["verdict"] == "flag"]
    return {
        "flagged": bool(flagged),
        "code": CODE if flagged else None,
        "memberships": len(uses),
        "findings": flagged,
        "lawful": [use for use in uses if use["verdict"] == "lawful"],
        "unclassified": [use for use in uses
                         if use["verdict"] == "unclassified"],
        "aliases": sorted(bindings(ast)),
    }


def scan(tools: engines.Toolchain, policy_path: str, workdir: str) -> dict:
    """`parse_policy()` then `scan_ast()` — the entry point `admit()` calls."""
    return scan_ast(parse_policy(tools, policy_path, workdir))
