"""Section 2.1's rates publisher, certified.

`harness/sweep_rates.py` computes the fill obligation's fourth quantity pair —
per-arm perfect and identity rates over the sweep's slots — by mirroring
`score.score_run()`'s extract→admit→gold→identity order. This suite pins what
makes that mirror trustworthy without invoking the pinned binaries: the
registered-scope refusal (no kill quantity anywhere), the shared semantics a
divergence would break, the publish-once discipline, and — when the published
ledger is present — the published figures' internal consistency."""

import json
import os

import pytest

import sweep_rates
from e4lib import extract

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
STUDY = os.path.dirname(HARNESS)
LABEL = "2026-08-24-effort-sweep"


@pytest.fixture(scope="session")
def published():
    path = os.path.join(sweep_rates.SWEEP_ROOT, LABEL,
                        sweep_rates.RATES_LEDGER_NAME)
    if not os.path.exists(path):
        pytest.skip("the sweep's rates ledger has not been published")
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# the registered scope: no kill quantity, by construction
# ---------------------------------------------------------------------------

def test_the_module_reaches_no_kill_machinery():
    """The docstring's claim, asserted: section 2.1 names perfect and identity
    rates and nothing else, and an endpoint-adjacent kill figure computed
    before the pilot would be the informal peek the sweep section keeps out of
    the condition choice. The module's source must not name the kill
    surface."""
    with open(os.path.join(HARNESS, "sweep_rates.py"), "r",
              encoding="utf-8") as handle:
        source = handle.read()
    for token in ("kill_rates", "kill_of", "survivorsPaired", "mutant_kill",
                  "load_mutants", "build_pairing"):
        assert token not in source, token


def test_the_published_block_carries_no_kill_member(published):
    """The same scope at the published surface: no member of any published
    record names a kill."""
    def walk(value):
        if isinstance(value, dict):
            for key, inner in value.items():
                assert "kill" not in key.lower(), key
                walk(inner)
        elif isinstance(value, list):
            for inner in value:
                walk(inner)
    walk(published)


# ---------------------------------------------------------------------------
# the mirror's shared semantics
# ---------------------------------------------------------------------------

def test_a_coded_slot_scores_no_gold_and_is_never_asked_about_identity(
        tmp_path, monkeypatch):
    """`score_run()`'s rule, held by the mirror: an authoring code ends the
    slot's scoring — `goldPerfect` false, identity `not-asked`. Driven with a
    stubbed admission so no binary runs."""
    slot = tmp_path / "slot"
    slot.mkdir()
    (slot / "completion.txt").write_text("POLICY:\n```rego\nx\n```\n",
                                         encoding="utf-8")
    monkeypatch.setattr(sweep_rates.admit_lib, "admit",
                        lambda *a, **k: (None, "opa-check-failed", {}))
    record = sweep_rates.score_slot(None, "B", str(slot), [], True,
                                    str(tmp_path / "w"))
    assert record["code"] == "opa-check-failed"
    assert record["goldPerfect"] is False
    assert record["identityWhy"] == "not-asked"


def test_an_extraction_miss_reaches_admission_as_none(tmp_path, monkeypatch):
    """`admit()` spells `no-marker-block` itself; the mirror must hand it the
    extraction layer's None unchanged rather than pre-empting the code."""
    slot = tmp_path / "slot"
    slot.mkdir()
    (slot / "completion.txt").write_text("no markers here", encoding="utf-8")
    seen = {}
    def admit(tools, arm, block, workdir, guard):
        seen["block"] = block
        return None, "no-marker-block", {}
    monkeypatch.setattr(sweep_rates.admit_lib, "admit", admit)
    record = sweep_rates.score_slot(None, "B", str(slot), [], True,
                                    str(tmp_path / "w"))
    assert seen["block"] is None
    assert record["code"] == "no-marker-block"


def test_the_suite_takes_the_scorers_own_filename(tmp_path, monkeypatch):
    """`score_run()` writes `suite.<language>`; a different name here would be
    a second reading of the same rule (and would cost `opa test` its `.rego`
    suffix)."""
    slot = tmp_path / "slot"
    slot.mkdir()
    (slot / "completion.txt").write_text(
        "POLICY:\n```rego\npackage x\n```\nTESTS:\n```rego\npackage t\n```\n",
        encoding="utf-8")
    workdir = tmp_path / "w"
    monkeypatch.setattr(sweep_rates.admit_lib, "admit",
                        lambda *a, **k: (str(workdir / "policy.rego"), None,
                                         {}))
    monkeypatch.setattr(sweep_rates, "gold_perfect",
                        lambda *a, **k: (True, 0))
    seen = {}
    def identity(tools, arm, suite_path, wd):
        seen["suite"] = os.path.basename(suite_path)
        return {"pass": True, "why": None}
    monkeypatch.setattr(sweep_rates, "reference_identity", identity)
    record = sweep_rates.score_slot(None, "B", str(slot), [], True,
                                    str(workdir))
    assert seen["suite"] == "suite.rego"
    assert record["identityPass"] is True


def test_an_unparseable_suite_is_the_registered_code_and_gold_stands(
        tmp_path, monkeypatch):
    """§5.2's state: policy admitted and gold-scored, suite present but not
    parseable to cases — the run carries `unparseable-artifact` AND keeps its
    computed gold verdict, exactly as 019's six pin-4 runs teach."""
    slot = tmp_path / "slot"
    slot.mkdir()
    (slot / "completion.txt").write_text(
        "POLICY:\n```rego\npackage x\n```\nTESTS:\n```rego\npackage t\n```\n",
        encoding="utf-8")
    workdir = tmp_path / "w"
    monkeypatch.setattr(sweep_rates.admit_lib, "admit",
                        lambda *a, **k: (str(workdir / "policy.rego"), None,
                                         {}))
    monkeypatch.setattr(sweep_rates, "gold_perfect",
                        lambda *a, **k: (True, 0))
    monkeypatch.setattr(
        sweep_rates, "reference_identity",
        lambda *a, **k: {"pass": False, "why": "suite-unparseable",
                         "code": "unparseable-artifact"})
    record = sweep_rates.score_slot(None, "B", str(slot), [], True,
                                    str(workdir))
    assert record["code"] == "unparseable-artifact"
    assert record["goldPerfect"] is True
    assert record["identityPass"] is False


# ---------------------------------------------------------------------------
# the published figures
# ---------------------------------------------------------------------------

def test_the_published_rates_are_the_slot_records_reaggregated(published):
    """Every per-arm cell equals its own slot records recounted, and the
    denominators are the sweep's registered 3/arm — a hand-edited cell breaks
    the recount."""
    for setting in published["settings"]:
        for arm in ("A", "B", "C"):
            mine = [row for row in setting["slots"] if row["arm"] == arm]
            cell = setting["perArm"][arm]
            assert cell["calls"] == len(mine) == 3
            assert cell["perfect"] == sum(
                1 for row in mine if row["goldPerfect"])
            assert cell["identityPass"] == sum(
                1 for row in mine if row["identityPass"])
            assert cell["codes"] == sorted(
                row["code"] for row in mine if row["code"])


def test_the_published_block_says_uncitable_and_names_its_scope(published):
    assert published["citable"] is False
    assert "no kill quantity" in published["obligation"]
    assert published["goldRows"] == 117
    assert published["guardRegistered"] is True


def test_the_guard_fired_in_fresh_authoring(published):
    """The presence-idiom guard's first live firings outside 019's
    retrospective: the published records carry the code. Descriptive — no rate
    or direction is read off it — but its presence is what makes the E2 table's
    new code a measured category rather than a reserved word."""
    codes = [row["code"]
             for setting in published["settings"]
             for row in setting["slots"] if row["code"]]
    assert "presence-idiom-unsound" in codes


def test_publishing_over_the_existing_ledger_is_refused():
    if not os.path.exists(os.path.join(sweep_rates.SWEEP_ROOT, LABEL,
                                       sweep_rates.RATES_LEDGER_NAME)):
        pytest.skip("no published ledger to collide with")
    with pytest.raises(sweep_rates.RatesError, match="RATES-EXISTS"):
        sweep_rates.main(["--label", LABEL, "--write"])


def test_the_rates_section_is_in_the_published_sweep_table():
    """§2.1's obligation sentence names ONE published table; the rates section
    lives inside SWEEP.md itself, beside the driver's columns, not only in a
    sibling a reader may never open."""
    path = os.path.join(sweep_rates.SWEEP_ROOT, LABEL, "SWEEP.md")
    if not os.path.exists(path):
        pytest.skip("no published sweep table")
    with open(path, "r", encoding="utf-8") as handle:
        body = handle.read()
    assert sweep_rates.RATES_HEADING in body
    assert "No kill quantity is computed" in body
