"""The presence-idiom detector — §3.2's guard, and the lawful uses it must not
touch.

**Why the false-positive side is the larger half of this module.** The detector
emits a registered authoring code, and an authoring code scores a run ZERO on
every endpoint it reaches. A detector that fires on `"x" in ["a", "b"]` would
therefore delete correct suites from every rate while looking, from the counts
alone, exactly like a detector that had found the M-14 mechanism. §3.2 registers
a false-positive census over lawful `in` uses for that reason and this module is
where each lawful form is named.

**Two layers, and both are here on purpose.** The AST-level cases run
everywhere, including CI, where §7 forbids invoking `opa` at all; the
end-to-end cases parse real Rego with the PINNED binary and skip when it is
absent, which is what keeps the AST fixtures above from drifting into a shape
OPA does not produce. Neither layer alone is enough: the first cannot see a
grammar change, and the second cannot run in CI.

The mutation check §3.2(v) requires lives here too, and it is a test rather than
a note: break the object-type branch, and the sensitivity case must FAIL.
"""
import hashlib
import json
import os
import subprocess
import sys

import pytest

from e4lib import domain
from e4lib import presence_idiom

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)


# --------------------------------------------------------------------------
# the rule, stated against the syntax tree
# --------------------------------------------------------------------------


def _membership(collection, builtin="member_2", probe=None):
    """One membership, in the EXPRESSION shape. `probe` defaults to a string
    literal, which is what makes it a PRESENCE TEST rather than an iteration."""
    return {"rules": [{"body": [{"index": 0, "terms": [
        {"type": "ref", "value": [{"type": "var", "value": "internal"},
                                  {"type": "string", "value": builtin}]},
        probe or {"type": "string", "value": "riskScore"},
        collection]}]}]}


def _some_declaration(collection):
    """The same membership as `some x in <collection>` — a call term nested
    under `terms.symbols`, which is the OTHER shape the parser produces."""
    return {"rules": [{"body": [{"index": 0, "terms": {"symbols": [
        {"type": "call", "value": [
            {"type": "ref", "value": [{"type": "var", "value": "internal"},
                                      {"type": "string", "value": "member_2"}]},
            {"type": "var", "value": "x"},
            collection]}]}}]}]}


def _bound(name, term, collection):
    """A package-level `name := term`, then a presence test over `collection`."""
    document = _membership(collection)
    document["rules"].insert(0, {
        "body": [{"index": 0, "terms": {"type": "boolean", "value": True}}],
        "head": {"name": name, "value": term, "assign": True,
                 "ref": [{"type": "var", "value": name}]}})
    return document


def _ref(*path):
    parts = [{"type": "var", "value": path[0]}]
    parts += [{"type": "string", "value": name} for name in path[1:]]
    return {"type": "ref", "value": parts}


LAWFUL = {
    "array membership": {"type": "array", "value": []},
    "set membership": {"type": "set", "value": []},
    "object.keys": {"type": "call", "value": [_ref("object", "keys"),
                                              _ref("input", "vendor")]},
    "a set comprehension": {"type": "setcomprehension", "value": {}},
    "an array comprehension": {"type": "arraycomprehension", "value": {}},
    "a scalar input member": _ref("input", "vendor", "riskScore"),
    "a data reference": _ref("data", "study", "allowed"),
}

# NOT lawful and NOT flagged: the detector could not decide. An unresolvable
# operand is REPORTED, because a detector whose output is an authoring code must
# not guess in either direction, and §3.2(iii)'s census counts these.
UNRESOLVED = {
    "an unbound variable": {"type": "var", "value": "keys"},
    "a ref with a dynamic tail": {"type": "ref", "value": [
        {"type": "var", "value": "input"}, {"type": "var", "value": "k"}]},
    "object.get with a computed path": {"type": "call", "value": [
        _ref("object", "get"), _ref("input"),
        {"type": "var", "value": "path"}, {"type": "null", "value": None}]},
}

TRAPS = {
    "a literal object": {"type": "object", "value": [
        [{"type": "string", "value": "riskScore"},
         {"type": "number", "value": 1}]]},
    "an object comprehension": {"type": "objectcomprehension", "value": {}},
    "the input root": _ref("input"),
    "an object member of input": _ref("input", "vendor"),
    "the other object member of input": _ref("input", "evidence"),
}


def test_a_probe_bound_to_a_string_literal_is_the_trap():
    """ROUND-1 FINDING R1-10(a): `k := "riskScore"; k in input.vendor` is
    M-14 with one extra line, and the first implementation called it lawful
    because it read the probe's raw AST type before resolving the binding.
    Measured before adoption: zero occurrences on the certification corpus,
    so every certified figure stands — but the adversarial construction now
    flags. Mutation check: restore the raw `probe_type not in SCALAR_TYPES`
    condition and this fails."""
    document = _membership(_ref("input", "vendor"),
                           probe={"type": "var", "value": "k"})
    document["rules"].insert(0, {
        "body": [{"index": 0, "terms": {"type": "boolean", "value": True}}],
        "head": {"name": "k", "value": {"type": "string",
                                        "value": "riskScore"},
                 "assign": True, "ref": [{"type": "var", "value": "k"}]}})
    report = presence_idiom.scan_ast(document)
    assert report["flagged"] is True
    assert report["findings"][0]["kind"] in presence_idiom.FLAG_REASONS


def test_a_dynamic_tail_bound_to_a_string_resolves_and_flags():
    """R1-10(b): `member := "vendor"; "riskScore" in input[member]` is a
    static path wearing a variable's name; the bindings map this module
    already keeps resolves it. The genuinely UNBOUND tail keeps its
    unclassified verdict — that case is the parametrized `a ref with a
    dynamic tail` row above, unchanged."""
    dynamic = {"type": "ref", "value": [
        {"type": "var", "value": "input"},
        {"type": "var", "value": "member"}]}
    document = _membership(dynamic)
    document["rules"].insert(0, {
        "body": [{"index": 0, "terms": {"type": "boolean", "value": True}}],
        "head": {"name": "member", "value": {"type": "string",
                                             "value": "vendor"},
                 "assign": True, "ref": [{"type": "var", "value": "member"}]}})
    report = presence_idiom.scan_ast(document)
    assert report["flagged"] is True


def test_a_non_string_probe_is_lawful_value_membership():
    """R1-10(c): `5 in {"x": 5}` is TRUE under the pinned binary — lawful
    value membership over the object's values — and the first implementation
    flagged it, zero-scoring a correct policy. A number or boolean probe is
    outside the guard's certified class now; the numeric-key trap
    (`5 in {5: "x"}`) is §3.2's THIRD measured ceiling, zero occurrences on
    the corpus. Mutation check: treat "number" as a probe again and this
    fails."""
    trap_shaped = {"type": "object", "value": [
        [{"type": "string", "value": "x"}, {"type": "number", "value": 5}]]}
    document = _membership(trap_shaped,
                           probe={"type": "number", "value": 5})
    report = presence_idiom.scan_ast(document)
    assert report["flagged"] is False
    assert any(use.get("kind") == "value-membership"
               for use in report["lawful"])


@pytest.mark.parametrize("name", sorted(LAWFUL))
def test_a_lawful_membership_is_not_flagged(name):
    report = presence_idiom.scan_ast(_membership(LAWFUL[name]))
    assert report["flagged"] is False, name
    assert report["code"] is None
    assert report["memberships"] == 1
    assert len(report["lawful"]) == 1
    assert report["unclassified"] == []


@pytest.mark.parametrize("name", sorted(UNRESOLVED))
def test_an_unresolvable_collection_is_reported_and_not_flagged(name):
    report = presence_idiom.scan_ast(_membership(UNRESOLVED[name]))
    assert report["flagged"] is False, name
    assert len(report["unclassified"]) == 1
    assert report["lawful"] == []


@pytest.mark.parametrize("name", sorted(TRAPS))
def test_a_bare_object_membership_is_flagged(name):
    report = presence_idiom.scan_ast(_membership(TRAPS[name]))
    assert report["flagged"] is True, name
    assert report["code"] == "presence-idiom-unsound"
    assert report["findings"][0]["kind"] in presence_idiom.FLAG_REASONS


def test_both_membership_builtins_are_read():
    """`x in xs` lowers to `internal.member_2` and `k, v in xs` to
    `internal.member_3`. A detector that read only the first would miss a
    presence test written in the three-operand form."""
    for builtin in ("member_2", "member_3"):
        report = presence_idiom.scan_ast(
            _membership(TRAPS["an object member of input"], builtin))
        assert report["flagged"] is True, builtin
        assert report["findings"][0]["builtin"] == "internal." + builtin


# --- the probe operand: a PRESENCE TEST, not an iteration -------------------


@pytest.mark.parametrize("name", sorted(TRAPS))
def test_an_iteration_over_an_object_is_lawful(name):
    """`some x in input.vendor` BINDS `x` to each value and is correct Rego —
    343 of the 599 memberships in Study 019's arm-B/C corpus are this form, and
    an early version of this detector flagged every one of them. The left
    operand is what separates a presence test from an iteration, and this is the
    single largest false-positive source the power analysis found."""
    for document in (_some_declaration(TRAPS[name]),
                     _membership(TRAPS[name],
                                 probe={"type": "var", "value": "x"})):
        report = presence_idiom.scan_ast(document)
        assert report["flagged"] is False, name
        assert report["memberships"] == 1
        assert report["lawful"][0]["kind"] == "iteration-or-binding"


def test_both_parser_shapes_are_read():
    """An `in` written as an expression and one written inside a `some`
    declaration parse differently. Reading only the first shape would make every
    `some x in …` invisible — which is the right VERDICT for an iteration and
    the wrong REASON for it, and the wrong reason stops being harmless the
    moment a presence test appears inside a `some` block."""
    for build in (_membership, _some_declaration):
        assert presence_idiom.scan_ast(
            build(LAWFUL["array membership"]))["memberships"] == 1
    forms = {use["form"] for use in presence_idiom.memberships(
        _membership(LAWFUL["array membership"]))}
    assert forms == {"expression"}
    forms = {use["form"] for use in presence_idiom.memberships(
        _some_declaration(LAWFUL["array membership"]))}
    assert forms == {"some-declaration"}


# --- the alias step: "a reference RESOLVING to an object member of input" ----


def test_a_name_bound_to_an_object_member_of_input_is_flagged():
    """The commonest form in the corpus after the direct one: `vendor :=
    input.vendor` and then `"riskScore" in vendor`. 83 of the 178 flagged uses
    reach the object this way, and the detector missed all of them until the
    alias step landed."""
    document = _bound("vendor", _ref("input", "vendor"),
                      {"type": "var", "value": "vendor"})
    report = presence_idiom.scan_ast(document)
    assert report["flagged"] is True
    assert report["findings"][0]["kind"] == presence_idiom.FLAG_OBJECT_ALIAS
    assert "vendor" in report["aliases"]


def test_object_get_with_a_literal_path_is_resolved():
    """`object.get(input, "vendor", {})` IS `input.vendor`. Nothing else is
    resolved: a user-defined function's return type is not on the syntax tree."""
    document = _membership({"type": "call", "value": [
        _ref("object", "get"), _ref("input"),
        {"type": "string", "value": "vendor"},
        {"type": "object", "value": []}]})
    assert presence_idiom.scan_ast(document)["flagged"] is True
    scalar = _membership({"type": "call", "value": [
        _ref("object", "get"), _ref("input"),
        {"type": "array", "value": [{"type": "string", "value": "vendor"},
                                    {"type": "string", "value": "riskScore"}]},
        {"type": "null", "value": None}]})
    assert presence_idiom.scan_ast(scalar)["flagged"] is False
    other = _membership({"type": "call", "value": [
        _ref("other", "helper"), _ref("input", "vendor")]})
    assert presence_idiom.scan_ast(other)["flagged"] is False


def test_a_name_bound_to_a_non_object_is_lawful():
    document = _bound("keys", {"type": "call", "value": [
        _ref("object", "keys"), _ref("input", "vendor")]},
        {"type": "var", "value": "keys"})
    assert presence_idiom.scan_ast(document)["flagged"] is False


def test_a_name_bound_twice_to_different_terms_is_dropped():
    """Two bindings are two possible values, and a detector that picked one
    would be guessing. Dropping is the conservative direction: the membership is
    then unresolved and is NOT flagged."""
    document = _bound("vendor", _ref("input", "vendor"),
                      {"type": "var", "value": "vendor"})
    document["rules"].insert(0, {
        "body": [{"index": 0, "terms": {"type": "boolean", "value": True}}],
        "head": {"name": "vendor", "value": {"type": "array", "value": []},
                 "assign": True, "ref": [{"type": "var", "value": "vendor"}]}})
    report = presence_idiom.scan_ast(document)
    assert report["flagged"] is False
    assert len(report["unclassified"]) == 1


def test_the_same_binding_written_twice_is_one_binding():
    """THE DEFECT THE POWER ANALYSIS FOUND, as a regression. Two rule bodies
    that each write `vendor := input.vendor` are two distinct dicts in the
    parsed document and ONE binding in the language; comparing them by identity
    called them a conflict and dropped the name, which cost seven runs of
    sensitivity on Study 019's corpus (29/36 before the fix, 36/36 after)."""
    document = _bound("vendor", _ref("input", "vendor"),
                      {"type": "var", "value": "vendor"})
    document["rules"].insert(0, {
        "body": [{"index": 0, "terms": {"type": "boolean", "value": True}}],
        "head": {"name": "vendor",
                 # An EQUAL term, built separately: a distinct object with the
                 # same content, which is exactly what the parser produces.
                 "value": {"type": "ref", "value": [
                     {"type": "var", "value": "input"},
                     {"type": "string", "value": "vendor"}]},
                 "assign": True, "ref": [{"type": "var", "value": "vendor"}]}})
    assert presence_idiom.scan_ast(document)["flagged"] is True


def test_an_alias_chain_terminates():
    """A cycle or a long chain gives up rather than recursing: unresolved, not
    flagged."""
    document = _membership({"type": "var", "value": "a"})
    for name, target in (("a", "b"), ("b", "a")):
        document["rules"].insert(0, {
            "body": [{"index": 0, "terms": {"type": "boolean", "value": True}}],
            "head": {"name": name, "value": {"type": "var", "value": target},
                     "assign": True, "ref": [{"type": "var", "value": name}]}})
    assert presence_idiom.scan_ast(document)["flagged"] is False


def test_a_call_that_is_not_a_membership_is_not_read():
    """`equal`, `plus`, anything else: the detector is about `in` and nothing
    else, so a document full of other calls reports zero memberships rather
    than zero flags over the wrong denominator."""
    document = {"rules": [{"body": [{"index": 0, "terms": [
        {"type": "ref", "value": [{"type": "var", "value": "equal"}]},
        {"type": "var", "value": "x"},
        TRAPS["a literal object"]]}]}]}
    report = presence_idiom.scan_ast(document)
    assert report["memberships"] == 0 and report["flagged"] is False


def test_an_unknown_operand_type_is_unclassified_and_not_flagged():
    """A term form this detector has never seen is REPORTED, not flagged. A
    detector that flagged what it did not recognise would have a
    false-positive rate that is a function of the OPA release, and §3.2
    registers that rate as a number."""
    report = presence_idiom.scan_ast(
        _membership({"type": "somethingnewinopa", "value": None}))
    assert report["flagged"] is False
    assert report["unclassified"] and \
        report["unclassified"][0]["kind"] == "somethingnewinopa"


def test_memberships_are_found_wherever_they_sit():
    """The scan is STRUCTURAL rather than a list of the places a membership may
    appear: `else` chains, comprehension bodies, `with` modifiers and `some`
    declarations all nest differently, and a form this module has never seen
    still has its membership found."""
    buried = {"rules": [{"head": {"value": {"type": "objectcomprehension",
                                            "value": _membership(
                                                TRAPS["a literal object"])}}}]}
    assert presence_idiom.scan_ast(buried)["flagged"] is True


# --------------------------------------------------------------------------
# the object paths are DERIVED from the registered input document
# --------------------------------------------------------------------------


def test_the_object_paths_come_from_the_registered_domain():
    """"Derive scope, don't enumerate." A detector carrying its own copy of the
    input shape goes stale the first time the registered document moves, and the
    flag rule would then be about a document nobody registered."""
    paths = presence_idiom.object_input_paths()
    assert paths[0] == ("input",)
    assert set(paths[1:]) == {("input", member)
                              for member in domain.REGO_INPUT_MEMBERS}
    assert len(paths) == 1 + len(domain.REGO_INPUT_MEMBERS)


def test_a_member_the_domain_does_not_register_is_not_an_object_path(
        monkeypatch):
    monkeypatch.setattr(domain, "REGO_INPUT_MEMBERS", ("vendor",))
    assert presence_idiom.object_input_paths() == (("input",),
                                                   ("input", "vendor"))
    assert presence_idiom.scan_ast(
        _membership(_ref("input", "evidence")))["flagged"] is False


# --------------------------------------------------------------------------
# the pinned binary's own AST, so the fixtures above cannot drift
# --------------------------------------------------------------------------


def _pinned_opa():
    path = os.environ.get("OPA_BIN")
    if not path or not os.path.isfile(path):
        pytest.skip("the pinned OPA binary is not present; §7 forbids invoking "
                    "it in CI and the AST-level cases above carry the rule")
    with open(os.path.join(HARNESS, "PINS.json"), "rb") as handle:
        pins = json.loads(handle.read().decode("utf-8"))
    with open(path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    if "sha256:" + digest != (pins.get("opa") or {}).get("assetSha256"):
        pytest.skip("OPA_BIN does not hash to the pinned asset digest")
    return path


REAL_POLICY = """package study

import rego.v1

trap_member if {
\t"riskScore" in input.vendor
}

lawful_keys if {
\t"riskScore" in object.keys(input.vendor)
}

lawful_array if {
\t"riskScore" in ["riskScore", "requestedSpend"]
}

lawful_set if {
\t"riskScore" in {"riskScore", "requestedSpend"}
}

trap_literal if {
\t"riskScore" in {"riskScore": 1}
}
"""


def test_the_ast_shape_is_the_pinned_binarys_own(tmp_path):
    """The fixtures above assert a SHAPE; this asserts the shape is OPA's. A
    grammar change that lowered `in` differently would leave every AST-level
    case green over a tree the detector could no longer read."""
    opa = _pinned_opa()
    path = tmp_path / "policy.rego"
    path.write_text(REAL_POLICY, encoding="utf-8")
    finished = subprocess.run([opa, "parse", "--format", "json", str(path)],
                              capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin", "TZ": "UTC"})
    assert finished.returncode == 0, finished.stderr
    document = json.loads(finished.stdout)
    uses = presence_idiom.memberships(document)
    assert len(uses) == 5, uses
    flagged = [use for use in uses if use["verdict"] == "flag"]
    lawful = [use for use in uses if use["verdict"] == "lawful"]
    assert len(flagged) == 2 and len(lawful) == 3
    assert sorted(use["kind"] for use in flagged) == [
        presence_idiom.FLAG_OBJECT_INPUT_REF, presence_idiom.FLAG_OBJECT_TERM]
    assert sorted(use["collectionType"] for use in lawful) == [
        "array", "call", "set"]


def test_scan_refuses_a_policy_the_parser_rejects(tmp_path, monkeypatch):
    """The caller has already admitted the artifact through `opa check`, so a
    parse refusal AFTER a passing check is an apparatus fact — never a silent
    "not flagged".

    ROUND-2 FINDING R2-1 split this into the two states it had merged. Exit 1
    is the parser ANSWERING — a readable syntax refusal about the author's
    bytes — and stays `PresenceIdiomError`, which `admit_arm_rego()` converts
    into the typed apparatus refusal because two pinned invocations disagreeing
    about one artifact yield no verdict about the author either. An unreadable
    stream at an ANSWERING exit is the same class. Every NO-ANSWER exit is
    caught one layer down and is the case below."""
    from e4lib import engines
    monkeypatch.setattr(engines, "opa_parse_tree",
                        lambda *a, **k: (1, "", "rego_parse_error"))
    with pytest.raises(presence_idiom.PresenceIdiomError) as caught:
        presence_idiom.scan(None, "policy.rego", str(tmp_path))
    assert "PRESENCE-IDIOM-PARSE-REFUSED" in str(caught.value)
    monkeypatch.setattr(engines, "opa_parse_tree",
                        lambda *a, **k: (0, "not json", ""))
    with pytest.raises(presence_idiom.PresenceIdiomError) as caught:
        presence_idiom.scan(None, "policy.rego", str(tmp_path))
    assert "PRESENCE-IDIOM-PARSE-UNREADABLE" in str(caught.value)


def test_a_parser_that_never_answered_is_typed_apparatus_not_a_detector_error(
        tmp_path, monkeypatch):
    """ROUND-2 FINDING R2-1, at the seat where the escape happened.

    `opa_parse_tree()` returned `_run()`'s raw tuple, `parse_policy()` raised
    `PresenceIdiomError` on any non-zero exit, and `PresenceIdiomError` is not
    an `engines.EngineError` — so `score_run()`'s apparatus handler could not
    see it and one transient OPA timeout on one arm-B run left the scorer
    entirely and ended a 180-slot attempt through `main()`'s last-resort
    handler.

    MUTATION 1: delete the `_refuse_no_answer()` call in `opa_parse_tree()` —
    the timeout case raises `PresenceIdiomError` again and this test fails.
    MUTATION 2: add 124 to that call's `answer_exits` — same failure, which is
    what proves the test reads the ANSWER/NO-ANSWER split and not merely the
    exception type."""
    from e4lib import engines

    class Tools:
        opa = "/nonexistent/opa"
    monkeypatch.setattr(engines, "_run", lambda *a, **k: (124, "", ""))
    with pytest.raises(engines.EngineError) as caught:
        engines.opa_parse_tree(Tools(), "policy.rego", str(tmp_path))
    assert "ENGINE-INVOCATION-REFUSED" in str(caught.value)
    assert not isinstance(caught.value, presence_idiom.PresenceIdiomError)
    # An invocation FAILURE exit (not a parse verdict) is the same class.
    monkeypatch.setattr(engines, "_run", lambda *a, **k: (3, "", "boom"))
    with pytest.raises(engines.EngineError):
        engines.opa_parse_tree(Tools(), "policy.rego", str(tmp_path))
    # …and exit 1 still ANSWERS, so it reaches the detector's own refusal.
    monkeypatch.setattr(engines, "_run", lambda *a, **k: (1, "", "syntax"))
    code, out, err = engines.opa_parse_tree(Tools(), "policy.rego",
                                            str(tmp_path))
    assert code == 1


def test_the_two_engines_disagreeing_leaves_admission_as_apparatus(
        tmp_path, monkeypatch):
    """R2-1's residual state, and the one judgement call in the repair: `opa
    check` accepted these bytes and `opa parse` refused them. No verdict about
    the AUTHOR survives a disagreement between the study's own pinned
    invocations, so admission raises the typed apparatus refusal rather than
    letting an untyped detector error escape.

    MUTATION: remove `admit_arm_rego()`'s `except PresenceIdiomError` wrap —
    the raised exception is `PresenceIdiomError` and this test fails."""
    from e4lib import admit as admit_lib
    from e4lib import engines
    monkeypatch.setattr(engines, "opa_check", lambda *a, **k: (0, []))
    monkeypatch.setattr(engines, "opa_parse_tree",
                        lambda *a, **k: (1, "", "rego_parse_error"))
    with pytest.raises(engines.EngineError) as caught:
        admit_lib.admit(None, "B", "package x\n", str(tmp_path), True)
    assert "ENGINE-INVOCATION-REFUSED" in str(caught.value)
    assert "disagree" in str(caught.value)


# --------------------------------------------------------------------------
# §3.2(v): the mutation check, as a test rather than as a note
# --------------------------------------------------------------------------


def test_breaking_the_object_branch_makes_the_sensitivity_case_fail():
    """The programme's standing *mutation-check every safeguard test* discipline,
    which §3.2(v) requires by name: break the detector, confirm the test that
    certifies it fails, and label any assertion that cannot discriminate.

    The mutation is the one the rule points at: DROP THE OBJECT-TYPE BRANCH, so
    neither an object term nor a reference onto a registered object path of
    `input` is object-valued any more. Under it every case in `TRAPS` must stop
    being flagged.

    **This test was itself found not to discriminate and was rebuilt** — the
    finding is recorded in `harness/POWER-PRESENCE-IDIOM.md` §(v). Its first
    version patched `classify_operand()`, which `memberships()` does not call,
    so the mutation reached nothing and the assertion passed over an unmutated
    detector. It patches `_object_valued()`, which is on the path."""
    original = presence_idiom._object_valued

    def mutated(term, bound, depth=0):
        """`_object_valued()` with the object branch removed."""
        if isinstance(term, dict):
            if term.get("type") in presence_idiom.OBJECT_TYPES:
                return False, term.get("type")
            if term.get("type") == "ref":
                path = presence_idiom._ref_path(term)
                if path is not None and path in \
                        presence_idiom.object_input_paths():
                    return False, "ref"
        return original(term, bound, depth)

    presence_idiom._object_valued = mutated
    try:
        survived = [name for name in TRAPS
                    if presence_idiom.scan_ast(
                        _membership(TRAPS[name]))["flagged"]]
        # …and the alias case, which reaches the same branch one step in.
        alias = presence_idiom.scan_ast(
            _bound("vendor", _ref("input", "vendor"),
                   {"type": "var", "value": "vendor"}))["flagged"]
    finally:
        presence_idiom._object_valued = original
    assert survived == [], (
        "these cases still flag with the object branch removed, so they do not "
        "discriminate: %s" % ", ".join(survived))
    assert alias is False, "the alias case does not discriminate either"
    # The control: with the branch restored, every one of them flags again. An
    # assertion that failed here would mean the mutation was never undone and
    # the case above proved nothing.
    assert all(presence_idiom.scan_ast(_membership(TRAPS[name]))["flagged"]
               for name in TRAPS)
    assert presence_idiom.scan_ast(
        _bound("vendor", _ref("input", "vendor"),
               {"type": "var", "value": "vendor"}))["flagged"] is True


def test_the_power_analysis_is_published_and_registered_beside_the_switch(pins):
    """§3.2 makes the analysis a `GATE(pre-freeze)` with a KILL SWITCH: if the
    detector cannot meet (i) and (ii) exactly — 40/40 and 0/22 — the guard is
    not registered at all. The document is a registered document, the switch is
    a registry member, and the two must agree, so neither can be edited alone."""
    import make_manifest
    assert "harness/POWER-PRESENCE-IDIOM.md" in \
        make_manifest.REGISTERED_DOCUMENTS
    block = pins["presenceIdiomGuard"]
    assert block["powerAnalysis"].endswith("harness/POWER-PRESENCE-IDIOM.md")
    published = os.path.join(HARNESS, "POWER-PRESENCE-IDIOM.md")
    if not os.path.isfile(published):
        assert block["registered"] is False, (
            "the guard may not be registered while its power analysis is "
            "unpublished: §3.2 registers the analysis as the condition")
        return
    with open(published, "rb") as handle:
        text = handle.read().decode("utf-8")
    flat = " ".join(text.split())
    assert block["sensitivity"] in flat
    assert block["specificity"] in flat
    assert block["falsePositivesOnLawfulIn"] in flat
    # The kill switch's own condition, read off the published numbers rather
    # than off the prose that describes them.
    meets = block["sensitivity"].startswith("40/40") and \
        block["specificity"].startswith("0/22")
    assert block["registered"] is meets, (
        "§3.2's kill switch: registered iff (i) 40/40 and (ii) 0/22 exactly")


# --- the merge's own regression case ----------------------------------------


def test_the_detectors_parse_is_not_the_suites_parse():
    """A NAME COLLISION that made the certified detector unreachable, kept as a
    test because the suite could not see it.

    `e4lib/engines.py` inherited an `opa_parse()` from Study 019 returning
    `(exit, stdout)` — `e4lib/e4.py` reads it that way for the suite's case
    inputs — and §3.2's detector arrived with a second definition of the SAME
    name returning `(exit, stdout, stderr)`. Python does not add a function
    there, it replaces one: the later `def` won, `parse_policy()` unpacked two
    values into three names, and `scan()` raised `ValueError` on its first real
    call. Every case in this file monkeypatches the parse with a three-tuple
    stub, and the one case that uses the pinned binary calls `subprocess.run`
    directly — so nothing on either line ever executed the real path.

    Two distinct names, two arities, both alive."""
    from e4lib import engines
    assert engines.opa_parse is not engines.opa_parse_tree
    assert "e4lib/domain.py" in engines.opa_parse.__doc__
    assert "NEW IN 020" in engines.opa_parse_tree.__doc__


def test_the_detector_runs_end_to_end_against_the_pinned_binary(tmp_path):
    """`scan()` itself, not `memberships()` over a tree somebody else parsed.
    This is the case whose absence let the collision above live: it is the only
    one that reaches `engines.opa_parse_tree()` through the detector's own
    entry point."""
    opa = _pinned_opa()
    policy = tmp_path / "policy.rego"
    policy.write_text(REAL_POLICY, encoding="utf-8")

    class Pinned:
        pass

    tools = Pinned()
    tools.opa = opa
    report = presence_idiom.scan(tools, str(policy), str(tmp_path))
    assert report["flagged"] is True
    assert report["memberships"] == 5
    assert len(report["findings"]) == 2
