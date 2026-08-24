"""§3.2's presence-idiom guard: the predicate, the gate, and the wiring.

WHAT THIS FILE DOES
-------------------
Three groups, and the middle one is the reason the file exists at all.

1. **The predicate**, over syntax trees the PINNED BINARY produced. §3.2's test
   is "on the syntax tree", so a fixture tree written out by hand here would be
   this suite's idea of OPA's parser rather than OPA's — Study 012's round-12
   lesson, a copy checking a copy. Every tree in the first group therefore comes
   from `opa parse --format json` on Rego source written in this file, and the
   group SKIPS when the pinned binary is not available (§7 forbids invoking
   `opa` in CI at all).

2. **The gate.** §3.2 registers the guard as a `GATE(pre-freeze)` whose
   `TODO(prereg)` block is still open, so the code is registered in §1a's table
   and E2's ordered table while `admit()` cannot return it. Both halves are
   asserted, including the one that is easy to leave untested: that the wiring
   REFUSES to activate rather than quietly accepting an operator's numbers.
   These tests need no engine and run everywhere.

3. **The wiring.** `DROP_ORDER`, `ARM_REACHABLE_CODES`, `batch.CODE_PARTITION`
   and §1a's own table, diffed; and `admit()` driven through the guarded branch
   with the detector stubbed, because what is under test there is the ADMISSION
   DECISION and not the parser.

DELIBERATELY DOES NOT DO
------------------------
* **It does not compute §3.2's power analysis and it does not assert its
  numbers.** (i)-(v) are a pre-freeze artifact computed over 019's retained
  policies and published in `CORRECTION-TARGETS.md` (§10). What this file
  asserts is that the GATE reads 40/40 and 0/22 and refuses anything else —
  the plumbing, not the finding.
* **It does not assert a rate over 019's corpus.** A test that hard-coded "the
  detector fires on 41 of 77" would be a result frozen into the harness before
  the analysis that is supposed to produce it.
* **It does not exercise scoring.** A flagged run's zero comes from §1a's
  population rule, which `tests/test_partition.py` and the scorer's own suite
  own.
"""
import json
import os

import pytest

import batch
import score
from e4lib import admit as admit_lib
from e4lib import engines
from e4lib import presence_idiom

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)


def _pins():
    with open(os.path.join(HARNESS, "PINS.json"), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def _skip_reason():
    tools = engines.Toolchain(_pins())
    if tools.problems:
        return "the pinned engines are not available: " + tools.problems[0]
    return None


needs_opa = pytest.mark.skipif(_skip_reason() is not None,
                               reason=_skip_reason() or "")


@pytest.fixture(scope="module")
def tools():
    return engines.Toolchain(_pins()).require()


@pytest.fixture(scope="session")
def paths():
    """The registered input domain's path kinds, derived from the gold rows.

    Session-scoped and read from `gold/GOLD.json`, so a domain change moves
    every assertion below with it rather than leaving them agreeing with a
    constant."""
    with open(os.path.join(STUDY, "gold", "GOLD.json"), "rb") as handle:
        gold = json.loads(handle.read().decode("utf-8"))
    return presence_idiom.input_paths([row["inputs"] for row in gold["rows"]])


def tree(tools, source, tmp_path):
    path = os.path.join(str(tmp_path), "policy.rego")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(source)
    code, raw = engines.opa_parse(tools, path, str(tmp_path))
    assert code == 0, "the fixture policy did not parse: %r" % raw[:200]
    return presence_idiom.parse_tree(raw)


HEADER = "package study\n\nimport rego.v1\n\n"


def scan(tools, paths, tmp_path, body):
    return presence_idiom.scan_tree(tree(tools, HEADER + body, tmp_path), paths)


def verdicts(report):
    return sorted({row["verdict"] for row in report["terms"]})


# --------------------------------------------------------------------------
# 1. the predicate, against the pinned parser
# --------------------------------------------------------------------------

@needs_opa
def test_the_registered_input_domain_is_derived_and_not_declared(paths):
    """§3.2's parenthetical is "a reference resolving to an object member of
    `input`", and which members those are is a fact about the registered domain.
    The three object paths are ASSERTED HERE as the domain's current content,
    but they are read out of `gold/GOLD.json` through the same renderer the
    scored invocations use — so a domain that grew an object member fails this
    assertion instead of leaving the detector quietly blind to it."""
    assert {path for path, kind in paths.items() if kind == "object"} == \
        {"input", "input.vendor", "input.evidence"}
    assert paths["input.vendor.riskScore"] == "scalar"


@needs_opa
def test_a_bare_object_literal_operand_flags(tools, paths, tmp_path):
    report = scan(tools, paths, tmp_path,
                  'required := {"riskScore": true}\n'
                  'r if { "riskScore" in required }\n')
    assert report["flagged"] and report["objectTerms"] == 1


@needs_opa
def test_a_set_or_array_operand_does_not_flag(tools, paths, tmp_path):
    report = scan(tools, paths, tmp_path,
                  'r1 if { "a" in {"a", "b"} }\n'
                  'r2 if { "a" in ["a", "b"] }\n')
    assert not report["flagged"] and verdicts(report) == ["collection"]


@needs_opa
def test_the_registered_mechanism_flags_and_the_scalar_member_does_not(
        tools, paths, tmp_path):
    """§3.2's own example. `"riskScore" in input.vendor` is the arm-B/C E1
    collapse; `"x" in input.vendor.riskScore` is a type error, not this one, and
    a detector that flagged it would be reporting a different mechanism under
    this code."""
    report = scan(tools, paths, tmp_path,
                  'r1 if { "riskScore" in input.vendor }\n')
    assert report["flagged"]
    other = scan(tools, paths, tmp_path,
                 'r2 if { "x" in input.vendor.riskScore }\n')
    assert not other["flagged"] and verdicts(other) == ["scalar"]


@needs_opa
def test_the_recommended_idiom_does_not_flag(tools, paths, tmp_path):
    """`object.keys` is what §3.2's forensic note names as the correct spelling,
    and it is the one thing this detector must never punish: a guard that fired
    on the fix would make the flagged population uninterpretable."""
    report = scan(tools, paths, tmp_path,
                  'r if { "riskScore" in object.keys(input.vendor) }\n')
    assert not report["flagged"] and verdicts(report) == ["collection"]


@needs_opa
def test_object_get_into_the_input_domain_flags(tools, paths, tmp_path):
    """The commonest spelling in 019's retained policies is not the bare
    reference; it is `object.get(input, "vendor", {})`, whose result is the
    member or the default and is an object either way."""
    report = scan(tools, paths, tmp_path,
                  'r if { "riskScore" in object.get(input, "vendor", {}) }\n')
    assert report["flagged"]
    assert any("object.get" in row["reason"] for row in report["terms"])


@needs_opa
def test_object_get_of_a_member_the_domain_does_not_have_takes_the_default(
        tools, paths, tmp_path):
    report = scan(tools, paths, tmp_path,
                  'r if { "a" in object.get(input, "absent", {"a": 1}) }\n')
    assert report["flagged"]
    clean = scan(tools, paths, tmp_path,
                 'r if { "a" in object.get(input, "absent", {"a", "b"}) }\n')
    assert not clean["flagged"]


@needs_opa
def test_a_body_binding_is_followed(tools, paths, tmp_path):
    report = scan(tools, paths, tmp_path,
                  'r if {\n\tvendor := input.vendor\n'
                  '\t"riskScore" in vendor\n}\n')
    assert report["flagged"]


@needs_opa
def test_a_function_parameter_is_resolved_at_its_call_sites(tools, paths,
                                                            tmp_path):
    """The shape without which the detector is half-blind: the trap is written
    inside a helper whose parameter has no value where it stands."""
    report = scan(tools, paths, tmp_path,
                  'risk_values(vendor) := [vendor.riskScore] if {\n'
                  '\t"riskScore" in vendor\n}\n'
                  'r if { some v in risk_values(input.vendor); v > 0 }\n')
    assert report["flagged"]


@needs_opa
def test_a_parameter_passed_through_two_helpers_is_resolved(tools, paths,
                                                            tmp_path):
    """The bounded fixpoint's reason for existing: the inner helper's call site
    passes the OUTER helper's parameter, so one pass cannot see it."""
    report = scan(tools, paths, tmp_path,
                  'inner(v) := [v.riskScore] if { "riskScore" in v }\n'
                  'outer(vendor) := inner(vendor)\n'
                  'r if { some v in outer(input.vendor); v > 0 }\n')
    assert report["flagged"]


@needs_opa
def test_a_parameter_with_two_kinds_of_call_site_is_not_resolved(tools, paths,
                                                                 tmp_path):
    """Unanimity, not the majority: one site passing an object and another a set
    is a parameter with no single kind, and the operand stays undetermined
    rather than taking the first site's word."""
    report = scan(tools, paths, tmp_path,
                  'holds(coll) if { "riskScore" in coll }\n'
                  'r1 if { holds(input.vendor) }\n'
                  'r2 if { holds({"riskScore", "x"}) }\n')
    assert not report["flagged"]
    assert "undetermined" in verdicts(report)


@needs_opa
def test_a_recursive_parameter_reports_a_cycle_rather_than_hanging(tools, paths,
                                                                   tmp_path):
    report = scan(tools, paths, tmp_path,
                  'loop(v) := loop(v)\n'
                  'r if { "riskScore" in loop(input.vendor) }\n')
    assert not report["flagged"]


@needs_opa
def test_an_object_comprehension_flags_and_the_other_two_do_not(tools, paths,
                                                                tmp_path):
    flagged = scan(tools, paths, tmp_path,
                   'r if { "a" in {k: v | some k, v in ["a", "b"]} }\n')
    assert flagged["flagged"]
    # The comprehensions here range over an ARRAY, not over `input.vendor`:
    # an inner `some k, v in input.vendor` is itself an `in` term over an
    # object and would flag the module on its own, which would leave this
    # assertion agreeing for the wrong reason.
    clean = scan(tools, paths, tmp_path,
                 'r1 if { "a" in {k | some k in ["a", "b"]} }\n'
                 'r2 if { "a" in [x | some x in ["a", "b"]] }\n')
    assert not clean["flagged"] and verdicts(clean) == ["collection"]


@needs_opa
def test_both_desugarings_are_found_and_nothing_filters_on_the_form(
        tools, paths, tmp_path):
    """§3.2 registers the predicate over "any `in` term", so `some k, v in
    <object>` is flagged on the same rule as `"k" in <object>`. The `form`
    member is carried for the power analysis's (iii) member and is NOT a
    filter — asserted here, because narrowing the predicate to membership tests
    would be a registered-text change wearing a refactor."""
    report = scan(tools, paths, tmp_path,
                  'r if { some k, v in input.vendor; k == "a"; v != null }\n')
    forms = {row["form"] for row in report["terms"]}
    assert forms == {"iteration"}
    assert report["flagged"], (
        "an iteration over an object is still an `in` term whose right operand "
        "is an object, which is what §3.2 registers")
    operators = {row["operator"] for row in report["terms"]}
    assert operators == {"internal.member_3"}


@needs_opa
def test_a_name_bound_to_two_kinds_is_dropped_rather_than_guessed(tools, paths,
                                                                  tmp_path):
    report = scan(tools, paths, tmp_path,
                  'thing := {"a": 1} if { input.vendor.newVendor == "yes" }\n'
                  'thing := {"a", "b"} if { input.vendor.newVendor == "no" }\n'
                  'r if { "a" in thing }\n')
    assert not report["flagged"] and "undetermined" in verdicts(report)


@needs_opa
def test_the_scan_refuses_a_policy_the_parser_would_not_read(tools, paths,
                                                             tmp_path):
    """An unreadable tree is a policy the detector did not examine. Recording it
    as "not flagged" would put a silent false negative into the power analysis's
    specificity member, which is the one §3.2 requires to be exactly 0/22."""
    path = os.path.join(str(tmp_path), "broken.rego")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("package study\n\nthis is not rego\n")
    with pytest.raises(presence_idiom.PresenceIdiomError) as raised:
        presence_idiom.scan(tools, path, str(tmp_path), paths)
    assert str(raised.value).startswith("PRESENCE-PARSE-REFUSED")


# --------------------------------------------------------------------------
# 1b. the pieces that need no engine
# --------------------------------------------------------------------------

def test_the_input_domain_refuses_a_path_with_two_kinds(monkeypatch):
    """A path that is an object in one registered point and a scalar in another
    would make §3.2's `object member of input` name no single fact."""
    monkeypatch.setattr(engines, "render_rego_input",
                        lambda point: json.dumps(point))
    with pytest.raises(presence_idiom.PresenceIdiomError) as raised:
        presence_idiom.input_paths([{"vendor": {"a": 1}}, {"vendor": "x"}])
    assert str(raised.value).startswith("PRESENCE-AMBIGUOUS-INPUT-PATH")


def test_the_input_domain_refuses_to_be_empty():
    with pytest.raises(presence_idiom.PresenceIdiomError) as raised:
        presence_idiom.input_paths([])
    assert str(raised.value).startswith("PRESENCE-EMPTY-INPUT-DOMAIN")


def test_an_unreadable_parse_output_refuses():
    with pytest.raises(presence_idiom.PresenceIdiomError) as raised:
        presence_idiom.parse_tree(b"{not json")
    assert str(raised.value).startswith("PRESENCE-UNPARSEABLE-TREE")
    with pytest.raises(presence_idiom.PresenceIdiomError):
        presence_idiom.parse_tree(b"[]")


def test_an_in_term_outside_every_rule_refuses_rather_than_being_dropped():
    """The rule-wise walk is what gives an operand its body scope, and a term it
    never reached would be absent from the detector's denominator without
    anything saying so."""
    member = {"type": "call",
              "value": [{"type": "ref",
                         "value": [{"type": "var", "value": "internal"},
                                   {"type": "string", "value": "member_2"}]},
                        {"type": "string", "value": "a"},
                        {"type": "object", "value": []}]}
    with pytest.raises(presence_idiom.PresenceIdiomError) as raised:
        presence_idiom.scan_tree({"rules": [], "stray": member}, {})
    assert str(raised.value).startswith("PRESENCE-TERM-OUTSIDE-RULE")


# --------------------------------------------------------------------------
# 2. the gate
# --------------------------------------------------------------------------

EXACT = {
    "sensitivity": {"fired": 40, "of": 40},
    "specificity": {"fired": 0, "of": 22},
    "falsePositiveRate": "published",
    "counterfactualShift": "published",
    "mutationCheck": "published",
}
CLOSED = "a registration with no TODO block in it"
SOME_PATHS = {"input": "object"}


def test_the_registration_still_carries_the_gates_todo_block(preregistration):
    """The premise every assertion below rests on: while these bytes are in
    PREREGISTRATION.md the guard is not registered, and this test is what turns
    their removal into a suite failure rather than a silent activation."""
    assert presence_idiom.gate_open(preregistration)
    assert preregistration.count(presence_idiom.GATE_ANCHOR) == 1


def test_the_gate_is_open_today_so_the_wiring_hands_back_no_guard(
        preregistration):
    assert presence_idiom.attempt_guard(preregistration, None,
                                        SOME_PATHS) is None


def test_offering_an_analysis_while_the_todo_stands_refuses(preregistration):
    """§3.2's gate is a fact about the REGISTRATION, not about what the operator
    has computed. An analysis offered against an open TODO is the failure the
    gate exists to prevent."""
    with pytest.raises(presence_idiom.GateOpenError) as raised:
        presence_idiom.attempt_guard(preregistration, EXACT, SOME_PATHS)
    assert str(raised.value).startswith("PRESENCE-GATE-OPEN")


def test_deleting_the_todo_block_does_not_buy_the_guard():
    with pytest.raises(presence_idiom.GateUnmetError) as raised:
        presence_idiom.attempt_guard(CLOSED, None, SOME_PATHS)
    assert str(raised.value).startswith("PRESENCE-GATE-UNMET")


@pytest.mark.parametrize("member", presence_idiom.GATE_MEMBERS)
def test_a_power_analysis_missing_any_registered_member_refuses(member):
    """§3.2: "It must report, at minimum: (i) … (v)". All five, or no guard."""
    short = dict(EXACT)
    short.pop(member)
    with pytest.raises(presence_idiom.GateUnmetError) as raised:
        presence_idiom.attempt_guard(CLOSED, short, SOME_PATHS)
    assert member in str(raised.value)


@pytest.mark.parametrize("member,entry", [
    ("sensitivity", {"fired": 39, "of": 40}),
    ("sensitivity", {"fired": 40, "of": 41}),
    ("specificity", {"fired": 1, "of": 22}),
    ("specificity", {"fired": 0, "of": 21}),
])
def test_anything_other_than_forty_of_forty_and_zero_of_twenty_two_refuses(
        member, entry):
    """"if the detector cannot meet (i) and (ii) EXACTLY — 40/40 and 0/22 — the
    guard is not registered at all". One short is not nearly enough; it is the
    Tier D branch."""
    near = dict(EXACT)
    near[member] = entry
    with pytest.raises(presence_idiom.GateUnmetError) as raised:
        presence_idiom.attempt_guard(CLOSED, near, SOME_PATHS)
    assert "not registered at all" in str(raised.value)


def test_a_rate_that_states_no_denominator_refuses():
    malformed = dict(EXACT)
    malformed["specificity"] = 0
    with pytest.raises(presence_idiom.GateUnmetError) as raised:
        presence_idiom.attempt_guard(CLOSED, malformed, SOME_PATHS)
    assert "states no rate" in str(raised.value)


def test_the_gates_numbers_are_the_registrations_numbers(preregistration):
    """The constants are diffed against §3.2's own sentence, so a study that
    re-derived the corpus and changed the figures cannot leave the code
    enforcing the old pair."""
    assert preregistration.count("### 3.2") == 1, \
        "PREREGISTRATION.md holds more than one section numbered 3.2"
    section = preregistration.split("### 3.2")[1].split("\n## 4.")[0]
    assert "%d/%d and %d/%d" % (presence_idiom.GATE_SENSITIVITY
                                + presence_idiom.GATE_SPECIFICITY) in section
    assert "the 40 that use bare-object" in section
    assert "none** of the 22 perfect runs" in section


def test_an_exact_analysis_over_a_closed_gate_activates():
    guard = presence_idiom.attempt_guard(CLOSED, EXACT, SOME_PATHS)
    assert isinstance(guard, presence_idiom.Guard)
    assert guard.analysis is EXACT


def test_an_activated_guard_refuses_arm_a():
    """§11.11: the asymmetry is structural, and a guard asked for an arm-A
    verdict is a caller who wired it into the wrong branch."""
    guard = presence_idiom.attempt_guard(CLOSED, EXACT, SOME_PATHS)
    with pytest.raises(presence_idiom.PresenceIdiomError) as raised:
        guard.verdict(None, "A", "/nonexistent/policy.rego", "/tmp")
    assert str(raised.value).startswith("PRESENCE-ARM-UNREACHABLE")


def test_a_guard_cannot_be_activated_over_an_empty_input_domain():
    with pytest.raises(presence_idiom.PresenceIdiomError) as raised:
        presence_idiom.attempt_guard(CLOSED, EXACT, {})
    assert str(raised.value).startswith("PRESENCE-EMPTY-INPUT-DOMAIN")


# --------------------------------------------------------------------------
# 3. the wiring
# --------------------------------------------------------------------------

class StubTools:
    jpack = "/nonexistent/jpack"
    opa = "/nonexistent/opa"
    caps = "/nonexistent/caps.json"


def test_the_code_is_registered_in_the_partition_whether_or_not_it_fires():
    """§5's E2 entry: the table "carries `presence-idiom-unsound` (§3.2), with
    its per-arm count published whether or not it ever fires". So the code is in
    the partition today, with the guard off — a table whose rows depended on the
    outcome would report a different partition in each branch."""
    assert presence_idiom.CODE in admit_lib.DROP_ORDER
    assert batch.CODE_PARTITION[presence_idiom.CODE][0] == "authoring"
    assert presence_idiom.CODE in [code for code, _ in batch.AUTHORING_CODES]


def test_the_code_is_arm_structural_to_b_and_c():
    assert presence_idiom.ARMS == ("B", "C")
    for arm in presence_idiom.ARMS:
        assert presence_idiom.CODE in admit_lib.ARM_REACHABLE_CODES[arm]
    assert presence_idiom.CODE not in admit_lib.ARM_REACHABLE_CODES["A"]


def test_section_1as_table_registers_the_code_for_b_and_c(preregistration):
    """The prose side of the same fact, read out of the registration's own
    bytes: §1a's authoring-outcome table is where the code is registered, and
    its "arms it can reach" cell is what `ARM_REACHABLE_CODES` mirrors."""
    rows = [line for line in preregistration.splitlines()
            if line.startswith("|") and presence_idiom.CODE in line]
    assert len(rows) == 1, (
        "§1a registers %r in %d table rows" % (presence_idiom.CODE, len(rows)))
    cells = [cell.strip().replace("*", "").replace("`", "")
             for cell in rows[0].strip("|").split("|")]
    assert cells[0] == presence_idiom.CODE
    assert [arm.strip() for arm in cells[1].split(",")] == \
        list(presence_idiom.ARMS)


def test_the_e2_table_carries_the_row_at_count_zero_with_the_guard_off():
    """The published shape of "whether or not it ever fires"."""
    score.bind_study_modules()
    profile = score.e2_profile("B", [{"run": "run-001", "code": None,
                                      "admitted": True}])
    row = [entry for entry in profile["orderedCodes"]
           if entry["code"] == presence_idiom.CODE]
    assert len(row) == 1 and row[0]["count"] == 0
    assert row[0]["side"] == "authoring"


def test_admit_cannot_return_the_code_while_the_gate_is_open(tmp_path,
                                                             monkeypatch):
    """The registered-off state, end to end: no guard reaches `admit()`, so the
    detector is never consulted and the code is unreachable."""
    monkeypatch.setattr(engines, "opa_check", lambda *a, **k: (0, []))
    called = []
    monkeypatch.setattr(presence_idiom, "scan",
                        lambda *a, **k: called.append(a) or {"flagged": True})
    artifact, code, _detail = admit_lib.admit(
        StubTools(), "B", "package study\n", str(tmp_path))
    assert code is None and artifact is not None
    assert called == [], "the detector ran with no guard activated"


def test_admit_refuses_a_guard_that_did_not_come_through_the_gate(tmp_path):
    """A stand-in that answers like a guard is not the registration's condition
    for the code entering the population."""
    class LooksLikeAGuard:
        def verdict(self, tools, arm, policy_path, workdir):
            return presence_idiom.CODE, {}

    with pytest.raises(admit_lib.AdmissionError) as raised:
        admit_lib.admit(StubTools(), "B", "package study\n", str(tmp_path),
                        LooksLikeAGuard())
    assert str(raised.value).startswith("ADMIT-UNACTIVATED-GUARD")


def test_an_activated_guard_turns_a_flagged_policy_into_the_code(tmp_path,
                                                                 monkeypatch):
    """The other side of the switch, with the detector stubbed: what is under
    test is the admission decision, not the parser."""
    monkeypatch.setattr(engines, "opa_check", lambda *a, **k: (0, []))
    monkeypatch.setattr(presence_idiom, "scan",
                        lambda *a, **k: {"flagged": True, "objectTerms": 1,
                                         "terms": [], "undeterminedTerms": 0})
    guard = presence_idiom.attempt_guard(CLOSED, EXACT, SOME_PATHS)
    artifact, code, detail = admit_lib.admit(
        StubTools(), "B", "package study\n", str(tmp_path), guard)
    assert code == presence_idiom.CODE
    assert artifact is None, (
        "a flagged run scores zero on every endpoint it reaches (§1a); handing "
        "the artifact back would let it be evaluated as well as coded")
    assert detail["presenceIdiom"]["objectTerms"] == 1


def test_an_activated_guard_leaves_an_unflagged_policy_admitted(tmp_path,
                                                                monkeypatch):
    monkeypatch.setattr(engines, "opa_check", lambda *a, **k: (0, []))
    monkeypatch.setattr(presence_idiom, "scan",
                        lambda *a, **k: {"flagged": False, "objectTerms": 0,
                                         "terms": [], "undeterminedTerms": 0})
    guard = presence_idiom.attempt_guard(CLOSED, EXACT, SOME_PATHS)
    artifact, code, detail = admit_lib.admit(
        StubTools(), "B", "package study\n", str(tmp_path), guard)
    assert code is None and artifact is not None
    assert detail["presenceIdiom"]["flagged"] is False


def test_the_guard_is_never_consulted_for_arm_a(tmp_path, monkeypatch):
    """§11.11 from the caller's side: arm A never reaches the detector, so the
    arm-structural refusal is a backstop rather than the only thing standing
    between arm A and a code it cannot mean."""
    monkeypatch.setattr(engines, "jpack_json",
                        lambda *a, **k: ({"status": "valid"}, 0, "", ""))
    called = []
    monkeypatch.setattr(presence_idiom, "scan",
                        lambda *a, **k: called.append(a) or {"flagged": True})
    guard = presence_idiom.attempt_guard(CLOSED, EXACT, SOME_PATHS)
    _artifact, code, detail = admit_lib.admit(StubTools(), "A", "{}",
                                              str(tmp_path), guard)
    assert code is None and called == []
    assert "presenceIdiom" not in detail


def test_a_leaked_presence_code_in_arm_a_refuses(tmp_path, monkeypatch):
    """The backstop itself. §5's "arm-structural categories within-arm-only" is
    enforced for this code by the same check every other code gets."""
    monkeypatch.setattr(admit_lib, "admit_arm_a",
                        lambda *a, **k: (None, presence_idiom.CODE, {}))
    with pytest.raises(admit_lib.AdmissionError) as raised:
        admit_lib.admit(StubTools(), "A", "{}", str(tmp_path))
    assert str(raised.value).startswith("ADMIT-ARM-STRUCTURAL-LEAK")
