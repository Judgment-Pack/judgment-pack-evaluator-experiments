"""The capability sandbox: the rules, the committed bytes, and the derivation.

WHAT THIS FILE DOES
-------------------
Three layers, in the order they can be trusted.

1. **The registry binding.** The nine family words live in
   `harness/PINS.json` at `opa.capabilitiesDenylist`, and the module's
   :data:`REGISTERED_DENYLIST` is a transcription. Bound in both directions
   here, so a family added or dropped on either side fails.
2. **The committed artifact, read as bytes.** `controls/opa-capabilities.json`
   is checked without invoking anything: it must be a FIXED POINT of the filter
   (no surviving builtin is denied by any rule), it must be missing every
   builtin the rules name, it must still contain the neighbours the rules are
   careful NOT to take, and `render()` must reproduce its bytes exactly.
3. **The derivation, against the pinned binary.** Skipped unless `$OPA_BIN` is
   set AND hashes to `opa.assetSha256` — section 7's rule is that CI runs the
   deterministic controls only, and an unpinned binary must never satisfy this
   suite. When the pin is met, every measured claim in the module's docstring is
   re-measured: the print-lowering fact, the catch-all's three-builtin
   over-denial, no idle family, and byte equality with the committed file.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
* **It does not fill or assert a value for `opa.capabilitiesSha256`.** The pin
  is null pre-freeze; `tests/test_pins.py` owns that assertion and this file
  asserts only that committing the artifact did not fill it.
* **It does not assert that any scored invocation names the committed file.**
  Nothing resolves `opa.capabilitiesPath` at run time — `Toolchain` reads
  `$OPA_CAPS` — and a test asserting a wiring that does not exist would be a
  test of this file's wishes.
* **It does not re-derive the filter's arithmetic from OPA's documentation.**
  Where a claim is empirical ("the compiler lowers `print` to
  `internal.print`"), the pinned-binary section MEASURES it rather than
  restating it.
"""
import json
import os

import pytest

from e4lib import capabilities
from e4lib import engines

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(os.path.dirname(HERE))


def _pins():
    with open(os.path.join(STUDY, "harness", "PINS.json"), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def _pinned_opa_or_none():
    try:
        return capabilities.pinned_opa(_pins())
    except capabilities.CapabilitiesError:
        return None


PINNED_OPA = _pinned_opa_or_none()
needs_opa = pytest.mark.skipif(
    PINNED_OPA is None,
    reason="OPA_BIN is unset or does not hash to the registry's "
           "opa.assetSha256; the derivation is not re-measured")


# --- layer 1: the registry binding ------------------------------------------

def test_the_denylist_is_the_registrys_and_the_registrys_is_the_modules(pins):
    """A family cannot be added or dropped in the module without the registry
    disagreeing, or in the registry without the module disagreeing."""
    registered = pins["opa"]["capabilitiesDenylist"]
    assert tuple(registered) == capabilities.REGISTERED_DENYLIST
    assert len(registered) == len(set(registered)) == 9


def test_every_registered_word_is_implemented_by_exactly_one_rule():
    """The mapping from prose to predicate is total and injective: a word with
    no rule is a denylist entry that denies nothing, and two rules claiming one
    word make the registry ambiguous about what was implemented."""
    implemented = [family.registered for family in capabilities.FAMILIES]
    assert tuple(implemented) == capabilities.REGISTERED_DENYLIST


def test_the_catch_all_claims_no_registered_word():
    """It is a SUPERSET layer and says so: `registered` is None, so no reader
    can mistake the flag rule for one of the nine the registry names."""
    assert capabilities.CATCH_ALL.registered is None
    assert capabilities.CATCH_ALL.id not in \
        [family.id for family in capabilities.FAMILIES]


def test_the_registry_names_where_the_file_lives_and_the_pin_matches_it(pins):
    """`capabilitiesPath` is where it lives; `capabilitiesSha256` is what the
    FREEZE fills. Pre-ceremony this asserted the pin null — committing the
    artifact did not fill it. The freeze-fill has run (SCAFFOLD §F5), so the pin
    now has one honest state per phase: null before the ceremony reaches it, and
    EXACTLY the committed file's digest after — a pin that disagrees with the
    bytes it names is worse than a null one."""
    import hashlib

    assert pins["opa"]["capabilitiesPath"] == capabilities.REGISTERED_RELPATH
    path = capabilities.committed_path(STUDY)
    assert os.path.isfile(path)
    pin = pins["opa"]["capabilitiesSha256"]
    if pin is not None:
        with open(path, "rb") as fh:
            actual = hashlib.sha256(fh.read()).hexdigest()
        assert pin == "sha256:" + actual


def test_the_registry_records_that_the_rules_over_deny(pins):
    """The over-denial is a reviewed fact in the registry's own bytes, not a
    surprise a reader meets in the diff of a generated file."""
    note = pins["opa"]["capabilitiesDenylistNote"]
    for name in capabilities.CATCH_ALL_ONLY_AT_PIN:
        assert name in note, name
    assert "internal.print" in note


# --- layer 2: the committed artifact, without invoking anything --------------

def test_the_committed_file_is_a_fixed_point_of_the_filter():
    """Every surviving builtin survives EVERY rule. This is the property that
    makes the committed bytes checkable without the binary: a builtin the rules
    deny cannot be in the file, whatever produced it."""
    document = capabilities.committed_document(STUDY)
    denied = {record["name"]: capabilities.classify(record)
              for record in document["builtins"]}
    assert {name: hits for name, hits in denied.items() if hits} == {}
    assert len(document["builtins"]) > 100


def test_refiltering_the_committed_file_refuses_because_every_family_is_idle():
    """The idle-family refusal, demonstrated on real bytes: run the filter over
    its own output and all nine rules match nothing, which the module calls a
    rule that has stopped reading rather than a filter with nothing to do."""
    document = capabilities.committed_document(STUDY)
    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.filter_capabilities(document)
    message = str(caught.value)
    assert "matched NOTHING" in message
    for word in capabilities.REGISTERED_DENYLIST:
        assert word in message, word


@pytest.mark.parametrize("name", [
    "time.now_ns",           # clock, and the canary's builtin
    "print", "internal.print",  # the lowering fact
    "trace",
    "rand.intn",
    "uuid.rfc4122", "uuid.parse",
    "opa.runtime",
    "http.send", "net.lookup_ip_addr",
    "net.cidr_expand",
    "time.clock", "time.date", "time.diff", "time.format", "time.weekday",
    "io.jwt.decode_verify", "io.jwt.encode_sign", "io.jwt.encode_sign_raw",
])
def test_the_committed_file_has_removed_every_builtin_the_rules_name(name):
    document = capabilities.committed_document(STUDY)
    assert name not in {record["name"] for record in document["builtins"]}


@pytest.mark.parametrize("name", [
    "time.add_date",      # `time` namespace, takes ns, NO timezone branch
    "time.parse_ns",      # `time` namespace, has arguments
    "net.cidr_contains",  # `net` namespace, deterministic
    "io.jwt.decode",      # `io.jwt`, not flagged nondeterministic
    "json.unmarshal", "sprintf",
])
def test_the_committed_file_keeps_the_neighbours_the_rules_avoid(name):
    """The rules' discrimination is the whole reason they are rules. A
    name-prefix reading of "clock" would take `time.add_date`; a namespace
    reading of "network" would take `net.cidr_contains`; the flag alone would
    leave `io.jwt.decode` in and take the signers, which is exactly what it
    does."""
    document = capabilities.committed_document(STUDY)
    assert name in {record["name"] for record in document["builtins"]}


def test_the_committed_file_carries_the_non_builtin_members_through():
    """The denylist is over builtins. `rego_v1` is what makes section 2's v1
    dialect pin meaningful, and a filter that quietly dropped it would change
    the language the arms are authoring in."""
    document = capabilities.committed_document(STUDY)
    assert set(document) == {"builtins", "features", "future_keywords",
                             "wasm_abi_versions"}
    assert "rego_v1" in document["features"]
    assert document["future_keywords"]
    assert document["wasm_abi_versions"]


def test_the_committed_bytes_are_what_render_produces():
    """Byte equality, not structural equality: the registry pins a digest over
    these bytes, so a document that parses the same and renders differently is
    a mismatch at the gate."""
    committed = capabilities.committed_bytes(STUDY)
    assert capabilities.render(json.loads(committed.decode("utf-8"))) == \
        committed
    assert committed.endswith(b"\n") and not committed.endswith(b"\n\n")
    assert capabilities.digest(committed).startswith("sha256:")


# --- layer 2b: the rules, on synthetic records -------------------------------

def _builtin(name, **extra):
    record = {"name": name, "decl": {"type": "function"}}
    record.update(extra)
    return record


def test_the_print_rule_reads_the_last_segment_not_the_registered_word():
    """The measured fact this rule exists for: denying the builtin the registry
    NAMES leaves the family working, because the compiler lowers `print` to
    `internal.print`."""
    assert capabilities.classify(_builtin("print")) == ("print",)
    assert capabilities.classify(_builtin("internal.print")) == ("print",)
    assert capabilities.classify(_builtin("sprintf")) == ()


def test_the_clock_rule_reads_the_declaration_not_the_name():
    nullary = {"name": "time.something", "decl": {"type": "function"}}
    assert "clock" in capabilities.classify(nullary)
    with_args = {"name": "time.something",
                 "decl": {"type": "function", "args": [{"type": "number"}]}}
    assert capabilities.classify(with_args) == ()


def test_the_timezone_rule_reads_the_ns_tz_union_branch():
    tz_arg = {"type": "any", "of": [
        {"type": "number"},
        {"type": "array", "static": [{"type": "number"}, {"type": "string"}]}]}
    takes = {"name": "x.y", "decl": {"type": "function", "args": [tz_arg]}}
    assert capabilities.classify(takes) == ("timezone",)
    plain = {"name": "x.y", "decl": {"type": "function",
                                     "args": [{"type": "number"},
                                              {"type": "number"}]}}
    assert capabilities.classify(plain) == ()
    # A static array of two numbers is not an `[ns, tz]` branch.
    two_numbers = {"type": "any", "of": [
        {"type": "array", "static": [{"type": "number"}, {"type": "number"}]}]}
    assert capabilities.classify(
        {"name": "x.y",
         "decl": {"type": "function", "args": [two_numbers]}}) == ()


def test_the_network_rule_needs_the_namespace_and_the_flag_together():
    assert capabilities.classify(_builtin("net.pure")) == ()
    assert capabilities.classify(
        _builtin("net.impure", nondeterministic=True)) == \
        ("network", "nondeterministic")
    # The flag alone, outside the two namespaces, is the catch-all only.
    assert capabilities.classify(
        _builtin("io.jwt.encode_sign", nondeterministic=True)) == \
        ("nondeterministic",)


def test_the_trace_rule_reads_the_binarys_own_category():
    assert capabilities.classify(
        _builtin("some.other.name", categories=["tracing"])) == ("trace",)


def test_the_nondeterministic_flag_is_read_as_true_not_as_truthy():
    """`"nondeterministic": "no"` is truthy. Reading it as truthy would deny a
    builtin the binary declared deterministic, and reading `1` as True would
    admit a shape the binary does not emit; `is True` is the only reading that
    answers to the record."""
    assert capabilities.classify(
        _builtin("x.y", nondeterministic="no")) == ()
    assert capabilities.classify(_builtin("x.y", nondeterministic=1)) == ()
    assert capabilities.classify(
        _builtin("x.y", nondeterministic=True)) == ("nondeterministic",)


# --- layer 2c: the refusals --------------------------------------------------

def test_a_record_without_a_name_is_refused():
    for record in ({}, {"decl": {}}, [], "time.now_ns", None):
        with pytest.raises(capabilities.CapabilitiesError):
            capabilities.classify(record)


def test_a_document_that_is_not_an_object_is_refused():
    with pytest.raises(capabilities.CapabilitiesError):
        capabilities.filter_capabilities(["builtins"])


def test_a_document_without_a_builtins_list_is_refused_by_name():
    """The refusal that matters most: a shape change that silently produced an
    empty `builtins` list would emit a MAXIMALLY restrictive file, which refuses
    every policy and looks like a very effective filter."""
    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.filter_capabilities({"builtins": {}})
    assert "would be a sandbox that refuses everything" in str(caught.value)


def test_a_filter_that_removes_everything_is_refused():
    """A file with no builtins refuses the canary too, which would make the
    negative control pass for the wrong reason."""
    document = {"builtins": [_builtin(name) for name in
                             ("print", "rand.intn", "uuid.parse",
                              "opa.runtime", "net.cidr_expand")]}
    # `trace` is denied by its CATEGORY, not by its name — a record named
    # `trace` with no `tracing` category survives, which is the discrimination
    # `test_the_trace_rule_reads_the_binarys_own_category` asserts.
    document["builtins"].append(_builtin("trace", categories=["tracing"]))
    document["builtins"].append(
        {"name": "time.now", "decl": {"type": "function"}})
    document["builtins"].append(
        {"name": "net.x", "decl": {"type": "function"},
         "nondeterministic": True})
    tz_arg = {"type": "any", "of": [
        {"type": "array", "static": [{"type": "number"}, {"type": "string"}]}]}
    document["builtins"].append(
        {"name": "time.fmt", "decl": {"type": "function", "args": [tz_arg]}})
    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.filter_capabilities(document)
    assert "removed every builtin" in str(caught.value)


def test_an_idle_family_is_refused_and_named():
    """One survivor keeps the empty-`kept` refusal out of the way, so what fires
    is the idle-family rule and the message names the word that went idle."""
    document = {"builtins": [_builtin("sprintf"), _builtin("print")]}
    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.filter_capabilities(document)
    assert "clock" in str(caught.value)
    assert "print" not in str(caught.value).split("matched NOTHING")[1]


def test_the_absent_artifact_is_refused_with_the_command_that_makes_it(
        tmp_path):
    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.committed_bytes(str(tmp_path))
    assert "--write" in str(caught.value)


def test_an_unpinned_or_absent_binary_is_refused_rather_than_invoked(tmp_path):
    pins = _pins()
    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.pinned_opa(pins, environ={})
    assert "OPA_BIN is unset" in str(caught.value)

    decoy = tmp_path / "opa"
    decoy.write_bytes(b"not the pinned binary")
    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.pinned_opa(pins, environ={"OPA_BIN": str(decoy)})
    assert "opa.assetSha256 pins" in str(caught.value)

    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.pinned_opa(pins,
                                environ={"OPA_BIN": str(tmp_path / "nope")})
    assert "is not a file" in str(caught.value)


def test_a_binary_that_cannot_be_invoked_is_refused_not_treated_as_empty(
        tmp_path):
    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.capability_set(str(tmp_path / "no-such-binary"),
                                    str(tmp_path))
    assert "could not be invoked" in str(caught.value)


def test_non_json_output_is_refused_rather_than_parsed_as_nothing(monkeypatch,
                                                                  tmp_path):
    monkeypatch.setattr(engines, "_run",
                        lambda *a, **k: (0, "v0.17.0\nv0.17.1\n", ""))
    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.capability_set("/pins/opa", str(tmp_path))
    assert "did not emit JSON" in str(caught.value)


def test_a_nonzero_exit_is_refused_with_the_stderr_it_came_with(monkeypatch,
                                                               tmp_path):
    monkeypatch.setattr(engines, "_run", lambda *a, **k: (1, "", "boom"))
    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.capability_set("/pins/opa", str(tmp_path))
    assert "exited 1" in str(caught.value) and "boom" in str(caught.value)


def test_the_argv_asks_for_the_current_set_and_not_the_version_list(monkeypatch,
                                                                    tmp_path):
    """Bare `opa capabilities` prints historical VERSION NAMES. A file derived
    from that output would have no builtins at all — which is the failure the
    `builtins` shape refusal above exists to catch, and this is the flag that
    keeps it from arising."""
    seen = {}

    def capture(argv, cwd, timeout=None):
        seen["argv"] = argv
        return 0, json.dumps({"builtins": []}), ""

    monkeypatch.setattr(engines, "_run", capture)
    capabilities.capability_set("/pins/opa", str(tmp_path))
    assert seen["argv"] == ["/pins/opa", "capabilities", "--current"]


def test_check_committed_names_both_digests_when_the_bytes_disagree(monkeypatch,
                                                                    tmp_path):
    document = capabilities.committed_document(STUDY)
    document["builtins"] = document["builtins"][:-1]
    monkeypatch.setattr(engines, "_run",
                        lambda *a, **k: (0, json.dumps(document), ""))
    monkeypatch.setattr(capabilities, "filter_capabilities",
                        lambda full: (full, {"x": ("clock",)}))
    with pytest.raises(capabilities.CapabilitiesError) as caught:
        capabilities.check_committed("/pins/opa", str(tmp_path), STUDY)
    message = str(caught.value)
    assert "derived" in message and "committed" in message
    assert "do NOT edit the file by hand" in message


# --- layer 3: the derivation, against the pinned binary ----------------------

@needs_opa
def test_the_committed_file_is_what_the_pinned_binary_derives(tmp_path):
    """The whole claim, re-run: `controls/opa-capabilities.json` is generated,
    not authored."""
    assert capabilities.check_committed(PINNED_OPA, str(tmp_path), STUDY) == \
        capabilities.digest(capabilities.committed_bytes(STUDY))


@needs_opa
def test_no_registered_family_is_idle_against_the_pinned_binary(tmp_path):
    derivation = capabilities.derive(PINNED_OPA, str(tmp_path))
    matched = set()
    for hits in derivation.removals.values():
        matched.update(hits)
    for family in capabilities.FAMILIES:
        assert family.id in matched, family.registered


@needs_opa
def test_the_catch_all_over_denies_exactly_the_three_jwt_builtins(tmp_path):
    """The over-denial is measured, not assumed. If a rebuilt binary flagged
    more, this constant would be wrong and this is where that shows."""
    derivation = capabilities.derive(PINNED_OPA, str(tmp_path))
    assert capabilities.catch_all_only(derivation.removals) == \
        capabilities.CATCH_ALL_ONLY_AT_PIN


@needs_opa
def test_the_full_set_is_strictly_larger_and_holds_the_canary_builtin(tmp_path):
    derivation = capabilities.derive(PINNED_OPA, str(tmp_path))
    full = {record["name"] for record in derivation.full["builtins"]}
    kept = {record["name"] for record in derivation.filtered["builtins"]}
    assert "time.now_ns" in full and "time.now_ns" not in kept
    assert kept < full
    assert full - kept == set(derivation.removals)


@needs_opa
def test_denying_the_registered_print_name_alone_leaves_the_family_working(
        tmp_path):
    """THE MEASUREMENT the `print` rule exists for, run against the pinned
    binary rather than restated: restore `internal.print` to the filtered set,
    leave `print` removed, and a policy calling `print("x")` compiles clean.

    This is the mutation the rule survives. A denylist implemented as the names
    the registry says would pass every other assertion in this file."""
    derivation = capabilities.derive(PINNED_OPA, str(tmp_path))
    full_records = {record["name"]: record
                    for record in derivation.full["builtins"]}
    weakened = dict(derivation.filtered)
    weakened["builtins"] = (list(derivation.filtered["builtins"])
                            + [full_records["internal.print"]])

    workdir = str(tmp_path)
    weak_path = os.path.join(workdir, "caps-name-list.json")
    with open(weak_path, "wb") as handle:
        handle.write(capabilities.render(weakened))
    policy = os.path.join(workdir, "printer.rego")
    with open(policy, "w", encoding="utf-8") as handle:
        handle.write('package p\nimport rego.v1\ny if { print("x") }\n')

    class _Tools(object):
        opa = PINNED_OPA
        caps = capabilities.committed_path(STUDY)

    weak_code, _weak_codes = engines.opa_check(_Tools(), policy, workdir,
                                               capabilities=weak_path)
    assert weak_code == 0, ("with `internal.print` restored the print family "
                            "still compiles: a name list is not a filter")
    strict_code, strict_codes = engines.opa_check(_Tools(), policy, workdir)
    assert strict_code != 0 and strict_codes == ["rego_type_error"]


# --- layer 3b: the canary's two arms, against the pinned binary --------------

@needs_opa
def test_the_canary_is_accepted_unfiltered_and_refused_by_the_committed_file(
        tmp_path):
    """Both directions, which is the only pair that means the filter has power:
    refused both ways would be a broken probe and accepted both ways would be a
    filter that constrains nothing."""

    class _Tools(object):
        opa = PINNED_OPA
        caps = capabilities.committed_path(STUDY)

    record = engines.capabilities_canary(_Tools(), str(tmp_path))
    assert record["refused"] is True
    assert record["errorCodes"] == ["rego_type_error"]
    assert record["acceptedUnfiltered"] is True
    assert record["unfilteredProblem"] is None
    assert record["bothDirections"] is True


@needs_opa
def test_the_unfiltered_arm_names_a_file_rather_than_omitting_the_flag(
        tmp_path):
    """Both arms must differ in exactly ONE thing. An arm that omitted
    `--capabilities` would make accepted/refused an artefact of the flag."""
    path = capabilities.write_full_capabilities(PINNED_OPA, str(tmp_path))
    assert os.path.isfile(path)
    written = json.loads(open(path, "rb").read().decode("utf-8"))
    assert "time.now_ns" in {record["name"] for record in written["builtins"]}
