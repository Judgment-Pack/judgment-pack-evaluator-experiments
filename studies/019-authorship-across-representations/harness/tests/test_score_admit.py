"""Admission — section 1a's SIX authoring codes, and the toolchain gate.

The design pilot had THREE drop codes and section 1a registers six. The split is
the reconciliation `harness/SCAFFOLD.md` item S2 owed, and every branch of it is
driven here: which check refused decides the code, and no branch may return a
code its own arm cannot structurally reach.

The engine calls are stubbed, deliberately. What is under test is the DECISION
about a check's outcome, not the pinned binaries' behaviour — that is what
`design/TOOLCHAIN-NOTES.md` recorded empirically and what the attempt-time
control gates re-verify. A stub also means the suite runs in CI, where section 7
forbids invoking `codex`, `jpack` or `opa` at all.
"""
import hashlib
import os

import pytest

import batch
from e4lib import admit as admit_lib
from e4lib import engines


class StubTools:
    """A toolchain object the admission layer can carry without a binary."""
    jpack = "/nonexistent/jpack"
    opa = "/nonexistent/opa"
    caps = "/nonexistent/caps.json"


@pytest.fixture
def tools():
    return StubTools()


# --- the six codes, one branch each -----------------------------------------

def test_no_block_is_the_no_marker_code(tools, tmp_path):
    artifact, code, _detail = admit_lib.admit(tools, "A", None, str(tmp_path))
    assert artifact is None and code == "no-marker-block"


def test_arm_a_non_json_is_unparseable(tools, tmp_path):
    artifact, code, detail = admit_lib.admit(tools, "A", "{not json",
                                             str(tmp_path))
    assert artifact is None and code == "unparseable-artifact"
    assert "parseError" in detail


def test_arm_a_invalid_pack_is_schema_invalid(tools, tmp_path, monkeypatch):
    monkeypatch.setattr(engines, "jpack_json", lambda *a, **k: (
        {"status": "invalid",
         "diagnostics": [{"code": "JPS-E-001", "layer": "schema",
                          "instancePath": "/rules/0", "severity": "error",
                          "message": "upstream prose that must not be recorded"}],
         "layers": [{"name": "schema", "status": "failed"}]}, 1, "", ""))
    artifact, code, detail = admit_lib.admit(tools, "A", "{}", str(tmp_path))
    assert artifact is None and code == "schema-invalid-pack"
    assert detail["diagnostics"] == [{"code": "JPS-E-001", "layer": "schema",
                                      "instancePath": "/rules/0"}]
    assert "message" not in detail["diagnostics"][0], \
        "diagnostics are codes, layers and pointers only — never message prose"
    assert detail["failedLayers"] == ["schema"]


def test_arm_a_non_json_payload_is_unreadable_output_shape(tools, tmp_path,
                                                           monkeypatch):
    """Section 2: verdicts are read from the JSON payload only. A validator that
    emitted no payload told us nothing about the artifact — that is a shape
    problem, not a schema verdict."""
    monkeypatch.setattr(engines, "jpack_json", lambda *a, **k: (None, 3, "", ""))
    artifact, code, detail = admit_lib.admit(tools, "A", "{}", str(tmp_path))
    assert artifact is None and code == "unreadable-output-shape"
    assert detail["validateExit"] == 3


def test_arm_a_valid_pack_is_admitted(tools, tmp_path, monkeypatch):
    monkeypatch.setattr(engines, "jpack_json",
                        lambda *a, **k: ({"status": "valid"}, 0, "", ""))
    artifact, code, _detail = admit_lib.admit(tools, "A", "{}", str(tmp_path))
    assert code is None and artifact.endswith("pack.json")
    assert os.path.isfile(artifact)


def test_rego_type_error_is_opa_check_failed(tools, tmp_path, monkeypatch):
    monkeypatch.setattr(engines, "opa_check",
                        lambda *a, **k: (1, ["rego_type_error"]))
    artifact, code, detail = admit_lib.admit(tools, "B", "package study\n",
                                             str(tmp_path))
    assert artifact is None and code == "opa-check-failed"
    assert detail["checkErrorCodes"] == ["rego_type_error"]


def test_v1_parse_failure_that_compiles_under_v0_is_v0_syntax(tools, tmp_path,
                                                              monkeypatch):
    """The mechanical discriminator: bytes that fail under the pinned v1 dialect
    and compile under `--v0-compatible` ARE v0 syntax, by the compiler's own
    reading. No string matching on upstream's message prose."""
    def check(_tools, _path, _workdir, v0_compatible=False):
        return (0, []) if v0_compatible else (1, ["rego_parse_error"])
    monkeypatch.setattr(engines, "opa_check", check)
    artifact, code, detail = admit_lib.admit(tools, "C", "package t\np[x] { x := 1 }\n",
                                             str(tmp_path))
    assert artifact is None and code == "v0-syntax"
    assert detail["v0CompatibleExit"] == 0


def test_v1_parse_failure_that_also_fails_under_v0_is_unparseable(tools, tmp_path,
                                                                  monkeypatch):
    def check(_tools, _path, _workdir, v0_compatible=False):
        return 1, ["rego_parse_error"]
    monkeypatch.setattr(engines, "opa_check", check)
    artifact, code, _detail = admit_lib.admit(tools, "B", "!!! not rego\n",
                                              str(tmp_path))
    assert artifact is None and code == "unparseable-artifact"


def test_an_unreadable_check_document_is_unreadable_output_shape(tools, tmp_path,
                                                                 monkeypatch):
    monkeypatch.setattr(engines, "opa_check",
                        lambda *a, **k: (1, [admit_lib.UNREADABLE_CHECK_OUTPUT]))
    artifact, code, _detail = admit_lib.admit(tools, "B", "package study\n",
                                              str(tmp_path))
    assert artifact is None and code == "unreadable-output-shape"


def test_an_empty_rego_block_is_unparseable(tools, tmp_path):
    artifact, code, _detail = admit_lib.admit(tools, "C", "   \n", str(tmp_path))
    assert artifact is None and code == "unparseable-artifact"


def test_a_clean_rego_policy_is_admitted(tools, tmp_path, monkeypatch):
    monkeypatch.setattr(engines, "opa_check", lambda *a, **k: (0, []))
    artifact, code, _detail = admit_lib.admit(tools, "B", "package study\n",
                                              str(tmp_path))
    assert code is None and artifact.endswith("policy.rego")


# --- the partition, and the arm-structural rule -----------------------------

def test_every_admission_code_is_on_section_1as_authoring_side():
    """Nothing this layer returns may be an apparatus code: an admission
    decision is about what the AUTHOR emitted, by construction."""
    for code in admit_lib.DROP_ORDER:
        assert batch.CODE_PARTITION[code][0] == "authoring", code


def test_the_drop_order_is_exactly_the_authoring_codes():
    assert sorted(admit_lib.DROP_ORDER) == \
        sorted(code for code, _phrase in batch.AUTHORING_CODES)


def test_every_arms_reachable_set_is_a_subset_of_the_drop_order():
    for arm, codes in admit_lib.ARM_REACHABLE_CODES.items():
        assert set(codes) <= set(admit_lib.DROP_ORDER), arm


def test_the_arm_structural_categories_are_within_arm_only():
    """Section 5: "arm-structural categories within-arm-only, enforced in the
    scorer". A Rego file has no pack schema; arm A has no Rego dialect."""
    assert "schema-invalid-pack" in admit_lib.ARM_REACHABLE_CODES["A"]
    assert "schema-invalid-pack" not in admit_lib.ARM_REACHABLE_CODES["B"]
    assert "v0-syntax" not in admit_lib.ARM_REACHABLE_CODES["A"]
    assert "opa-check-failed" not in admit_lib.ARM_REACHABLE_CODES["A"]


def test_a_cross_arm_code_refuses_rather_than_publishing_a_mixed_partition(
        tools, tmp_path, monkeypatch):
    monkeypatch.setattr(admit_lib, "admit_arm_a",
                        lambda *a, **k: (None, "v0-syntax", {}))
    with pytest.raises(admit_lib.AdmissionError) as raised:
        admit_lib.admit(tools, "A", "{}", str(tmp_path))
    assert str(raised.value).startswith("ADMIT-ARM-STRUCTURAL-LEAK")


def test_an_unknown_arm_refuses(tools, tmp_path):
    with pytest.raises(admit_lib.AdmissionError) as raised:
        admit_lib.admit(tools, "D", "{}", str(tmp_path))
    assert str(raised.value).startswith("ADMIT-UNKNOWN-ARM")


# --- the toolchain gate -----------------------------------------------------

def _write(path, body):
    path.write_bytes(body)
    return "sha256:" + hashlib.sha256(body).hexdigest()


def test_the_toolchain_is_fail_closed_on_a_digest_mismatch(tmp_path):
    """Section 2's stated hazard: "The operator PATH binary is v0.10.0 and must
    never be invoked." A mismatch refuses before the first subprocess."""
    jpack = tmp_path / "jpack"
    opa = tmp_path / "opa"
    caps = tmp_path / "caps.json"
    _write(jpack, b"the wrong jpack")
    opa_digest = _write(opa, b"opa")
    caps_digest = _write(caps, b"{}")
    pins = {"jpack": {"binarySha256": "sha256:" + "0" * 64},
            "opa": {"assetSha256": opa_digest,
                    "capabilitiesSha256": caps_digest}}
    tools = engines.Toolchain(pins, {"JPACK_BIN": str(jpack),
                                     "OPA_BIN": str(opa),
                                     "OPA_CAPS": str(caps)})
    assert tools.problems
    assert tools.problems[0].startswith("binary-digest-mismatch")
    with pytest.raises(engines.EngineError):
        tools.require()


def test_a_matching_toolchain_passes_and_publishes_no_absolute_path(tmp_path):
    jpack = tmp_path / "jpack"
    opa = tmp_path / "opa"
    caps = tmp_path / "caps.json"
    pins = {"jpack": {"binarySha256": _write(jpack, b"jpack")},
            "opa": {"assetSha256": _write(opa, b"opa"),
                    "capabilitiesSha256": _write(caps, b"{}")}}
    tools = engines.Toolchain(pins, {"JPACK_BIN": str(jpack),
                                     "OPA_BIN": str(opa),
                                     "OPA_CAPS": str(caps)}).require()
    record = tools.record()
    assert record["problems"] == [] and record["unenforcedPins"] == []
    assert str(tmp_path) not in repr(record)


def test_a_null_pin_is_recorded_as_unenforced_rather_than_silently_satisfied(
        tmp_path):
    """The registry's own rule: "The non-null members are enforced under both
    labels." A null one is a declaration, and the record says which."""
    jpack = tmp_path / "jpack"
    opa = tmp_path / "opa"
    caps = tmp_path / "caps.json"
    pins = {"jpack": {"binarySha256": _write(jpack, b"jpack")},
            "opa": {"assetSha256": _write(opa, b"opa"),
                    "capabilitiesSha256": None}}
    _write(caps, b"{}")
    tools = engines.Toolchain(pins, {"JPACK_BIN": str(jpack),
                                     "OPA_BIN": str(opa),
                                     "OPA_CAPS": str(caps)}).require()
    assert [entry["pin"] for entry in tools.unenforced] == \
        ["opa.capabilitiesSha256"]


def test_an_unset_binary_variable_refuses_rather_than_falling_back_to_path():
    tools = engines.Toolchain({}, {})
    assert len(tools.problems) == 3
    assert all(problem.startswith("binary-digest-mismatch")
               for problem in tools.problems)


def test_the_scrubbed_environment_pins_utc_and_carries_no_jpack_config():
    environment = engines.clean_env("/scratch")
    assert environment["TZ"] == "UTC"
    assert "JPACK_CONFIG" not in environment
    assert environment["HOME"] == environment["TMPDIR"] == "/scratch"
