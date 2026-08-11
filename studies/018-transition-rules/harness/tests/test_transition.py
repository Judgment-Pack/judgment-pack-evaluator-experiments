"""Layer TRANSITION unit suite: every registered code reachable, rules exact."""

import hashlib
import json

import pytest

import citation as ct
import transition as tr
import upstream016

SERIES = "https://example.com/judgment-packs/transition-policy"
OTHER = "https://example.com/judgment-packs/other-policy"
DA = "sha256:" + hashlib.sha256(b"unit/a").hexdigest()
DB = "sha256:" + hashlib.sha256(b"unit/b").hexdigest()


@pytest.fixture(scope="session")
def world():
    ns = upstream016.load(build=True)
    registry = ns.checkpoint
    authority = registry.private_key("study-018/currency-authority/1")
    ev = lambda k, v, d=None: {"event": k, "seriesId": SERIES, "packVersion": v,
                               "effectiveFrom": "2026-01-01T00:00:00Z",
                               **({"packDigest": d} if d else {})}
    history = registry.build_registry(authority, [
        ev("add", "1.0.0", DA), ev("add", "2.0.0", DB), ev("retire", "1.0.0"),
        ev("retire", "2.0.0"), ev("reinstate", "2.0.0")])
    digests = ["sha256:" + hashlib.sha256(
        registry.canonical_bytes(registry.DOMAIN_CHECKPOINT, r["checkpoint"])).hexdigest()
        for r in history]
    return {"digests": digests, "payloads": [r["checkpoint"] for r in history]}


def commitment(version="1.0.0", digest=DA, series=SERIES):
    return {"commitmentVersion": "1",
            "judgment": {"packId": series, "packVersion": version, "packDigest": digest}}


def out(record):
    if record["verdict"] in ("usable", "unavailable"):
        return record["verdict"]
    return "%s:%s" % (record["verdict"], record["code"])


def run(world, rule, cited=None, currency="fail:not-current-at-snapshot", **kw):
    config = ct.ruleconfig_bytes(series_id=kw.pop("series", SERIES), rule=rule, **kw)
    citation = None if cited is None else ct.citation_bytes(
        series_id=SERIES, cited_head=world["digests"][cited - 1])
    return tr.layer_transition(commitment(), world["digests"], world["payloads"],
                               citation, config, currency)


def test_the_divergence_is_deterministic(world):
    """One registry verdict, four usability answers, same evidence."""
    assert out(run(world, "stop-at-retirement")) == "not-usable:not-usable-version-retired"
    assert out(run(world, "position-window", cited=2, window_positions=5)) == "usable"
    assert out(run(world, "position-window", cited=2, window_positions=1)) == \
        "not-usable:not-usable-window-elapsed"
    assert out(run(world, "run-to-expiry", cited=2)) == "usable"


def test_stop_at_retirement_needs_no_citation(world):
    assert out(run(world, "stop-at-retirement", cited=None)) == \
        "not-usable:not-usable-version-retired"
    assert out(run(world, "stop-at-retirement", currency="pass")) == "usable"


def test_citation_absent_is_fail_closed_for_rules_that_need_it(world):
    for rule, kw in (("run-to-expiry", {}), ("position-window", {"window_positions": 5})):
        assert out(run(world, rule, cited=None, **kw)) == "unavailable"


def test_duration_window_is_unavailable(world):
    result = run(world, "position-window", cited=2, window_duration="24h")
    assert (result["verdict"], result["code"]) == ("unavailable", "transition-unavailable")
    assert "no trusted ordering" in result["detail"]


def test_citation_after_retirement(world):
    assert out(run(world, "run-to-expiry", cited=4)) == \
        "not-usable:not-usable-created-after-retirement"
    assert out(run(world, "position-window", cited=4, window_positions=5)) == \
        "not-usable:not-usable-created-after-retirement"


def test_citation_outside_the_history_is_unavailable(world):
    config = ct.ruleconfig_bytes(series_id=SERIES, rule="run-to-expiry")
    foreign = ct.citation_bytes(series_id=SERIES,
                                cited_head="sha256:" + "0" * 64)
    result = tr.layer_transition(commitment(), world["digests"], world["payloads"],
                                 foreign, config, "fail:not-current-at-snapshot")
    assert (result["verdict"], result["code"]) == ("unavailable", "transition-unavailable")


def test_foreign_series_rule_confers_nothing(world):
    assert out(run(world, "run-to-expiry", cited=2, series=OTHER)) == "unavailable"


def test_unregistered_rule_is_fail_closed(world):
    config = ct.ruleconfig_bytes(series_id=SERIES, rule="run-to-expiry").replace(
        b'"run-to-expiry"', b'"invent-a-rule"')
    result = tr.layer_transition(commitment(), world["digests"], world["payloads"],
                                 None, config, "fail:not-current-at-snapshot")
    assert result["code"] == "transition-unavailable"


def test_malformed_inputs_stay_in_the_vocabulary(world):
    for citation, config in (
        (7, ct.ruleconfig_bytes(series_id=SERIES, rule="run-to-expiry")),
        (None, "not-bytes"),
        (b"{not json", ct.ruleconfig_bytes(series_id=SERIES, rule="run-to-expiry")),
    ):
        result = tr.layer_transition(commitment(), world["digests"], world["payloads"],
                                     citation, config, "fail:not-current-at-snapshot")
        assert result["code"] in tr.CODES


def test_duplicate_members_refuse(world):
    raw = ct.ruleconfig_bytes(series_id=SERIES, rule="run-to-expiry").decode("utf-8")
    doctored = raw.replace('"windowDuration": null', '"windowDuration": null, "windowDuration": null', 1)
    result = tr.layer_transition(commitment(), world["digests"], world["payloads"],
                                 None, doctored.encode("utf-8"), "fail:not-current-at-snapshot")
    assert result["code"] == "transition-unavailable"


def test_every_registered_code_is_reachable():
    assert {"transition-unavailable", "not-usable-version-retired",
            "not-usable-window-elapsed", "not-usable-created-after-retirement"} == set(tr.CODES)


def test_evaluator_never_imports_the_writer():
    assert "import citation" not in open(tr.__file__, encoding="utf-8").read()
