"""Section 2a.5's transfer gate C4 — round-2 finding R2-11, driven.

The finding: `decision.CONTROL_GATES` required `c4-transfer-calibration`,
`score.py` never created it, and no production code read the pilot at attempt
time, so EVERY attempt failed as "not evaluated" and neither registered branch
could occur. The tests that hid it built their gates dict FROM
`CONTROL_GATES` itself (`test_score_decision.py:31`), so the key the producer
never made was always present in test. T1 reads the PRODUCER."""

import ast
import hashlib
import json
import os

import pytest

import score
from e4lib import decision
from e4lib import transfer

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)


# ---------------------------------------------------------------------------
# T1 — the gate key, read from the PRODUCER
# ---------------------------------------------------------------------------

def _gate_keys_in_producer():
    """The string keys of the `gates = {...}` literal inside `score.main()` —
    the dict the attempt actually publishes — parsed from the source, so a
    fixture built off `CONTROL_GATES` cannot stand in for it."""
    with open(os.path.join(HARNESS, "score.py"), "rb") as handle:
        tree = ast.parse(handle.read().decode("utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for inner in ast.walk(node):
                if isinstance(inner, ast.Assign) \
                        and any(isinstance(target, ast.Name)
                                and target.id == "gates"
                                for target in inner.targets) \
                        and isinstance(inner.value, ast.Dict):
                    return sorted(key.value for key in inner.value.keys
                                  if isinstance(key, ast.Constant))
    raise AssertionError("score.main() builds no `gates = {...}` literal")


def test_the_producer_builds_exactly_the_registered_gates():
    """THE test that would have caught R2-11. MUTATION: delete the
    `"c4-transfer-calibration"` line from `score.main()`'s gates dict — fails.
    (`test_score_decision.py`'s fixture passes under exactly that mutation.)"""
    assert _gate_keys_in_producer() == sorted(decision.CONTROL_GATES)


# ---------------------------------------------------------------------------
# the observables and the comparison
# ---------------------------------------------------------------------------

def _call(**edits):
    call = {"model": "m", "cli": "codex-cli 0.145.0", "binarySha256": "sha256:b",
            "reasoningEffort": "low",
            "argv": ["codex", "exec", "--sandbox", "workspace-write"],
            "codexHomeIsolated": True, "environmentScrubbed": True,
            "isolatedHomeInventory": [".codex/config.toml", ".codex/auth.json"],
            "durationSeconds": 100.0}
    call.update(edits)
    return call


def _side(duration, completion, tokens=500, per_arm=3, **call_edits):
    return {arm: [{"call": transfer.call_members(_call(durationSeconds=duration,
                                                       **call_edits)),
                   "completionBytes": completion,
                   "reasoningOutputTokens": tokens}
                  for _ in range(per_arm)]
            for arm in transfer.ARMS}


def _reference(duration=100.0, completion=1000, **call_edits):
    return transfer.validate_reference(transfer.reference_document(
        "2026-08-24-pilot", transfer.observables(
            _side(duration, completion, **call_edits))))


@pytest.mark.parametrize("row,edit", [
    ("model", {"model": "other"}),
    ("cliVersion", {"cli": "codex-cli 0.146.0"}),
    ("binarySha256", {"binarySha256": "sha256:c"}),
    ("reasoningEffort", {"reasoningEffort": "high"}),
    ("sandboxPolicy", {"argv": ["codex", "exec", "--sandbox", "read-only"]}),
    ("codexHomeIsolated", {"codexHomeIsolated": False}),
    ("environmentScrubbed", {"environmentScrubbed": False}),
    ("isolatedHomeInventory", {"isolatedHomeInventory": [".codex/extra"]}),
])
def test_each_exact_row_differing_is_pipeline_invalid_at_row_one(row, edit):
    """T2. MUTATION per case: remove that row from `REGISTERED_EXACT_ROWS` —
    its case fails."""
    reference = _reference()
    batch = transfer.observables(_side(100.0, 1000, **edit))
    c4 = transfer.compare(reference, batch)
    assert c4["outcome"] == transfer.OUTCOME_PIPELINE_INVALID
    assert any(row in problem for problem in c4["pipelineProblems"])
    unequal = [entry["row"] for entry in c4["exactRows"] if not entry["equal"]]
    assert unequal == [row]
    verdict = decision.decide({"pipelineProblems": c4["pipelineProblems"],
                               "shortfallDeclared": [], "controlGates": {},
                               "family": {}})
    assert verdict["row"] == "pipeline-invalid" and verdict["rowIndex"] == 1


@pytest.mark.parametrize("factor,expected", [
    (0.80, transfer.OUTCOME_HOLD), (1.25, transfer.OUTCOME_HOLD),
    (0.79, transfer.OUTCOME_CALIBRATION_INVALID),
    (1.26, transfer.OUTCOME_CALIBRATION_INVALID),
])
def test_the_band_is_closed_at_both_ends(factor, expected):
    """T3. `ratio = pilot / batch`; the pilot's median is `factor` times the
    batch's. MUTATION: widen a band to (0.75, 1.30) — the 0.79 case fails."""
    reference = _reference(duration=100.0 * factor, completion=1000)
    batch = transfer.observables(_side(100.0, 1000))
    c4 = transfer.compare(reference, batch)
    assert c4["outcome"] == expected
    cell = next(row for row in c4["bandRows"]
                if row["row"] == "callDurationSeconds" and row["arm"] == "A")
    assert round(cell["ratio"], 4) == round(factor, 4)
    if expected == transfer.OUTCOME_CALIBRATION_INVALID:
        assert c4["gateCauses"] and c4["pipelineProblems"] == []


def test_two_sidedness_precedence_and_both_published():
    """T4. An exact row AND a band cell both differ: row 1, not row 3, and
    BOTH are in the published block. MUTATION: test the band rows before the
    exact rows in `compare()` — fails."""
    reference = _reference(duration=900.0)
    batch = transfer.observables(_side(100.0, 1000, model="other"))
    c4 = transfer.compare(reference, batch)
    assert c4["outcome"] == transfer.OUTCOME_PIPELINE_INVALID
    assert any(not row["inBand"] for row in c4["bandRows"])
    assert any(not row["equal"] for row in c4["exactRows"])
    assert c4["gateCauses"]           # computed and published, never suppressed


def test_the_ratio_direction_is_pilot_over_batch_pinned_to_bytes():
    """T5. §2a.5's own arithmetic: 1660.184 / 199 = 8.3426 to four places, out
    of band. MUTATION: invert to batch / pilot — fails."""
    reference = _reference(duration=1660.184)
    batch = transfer.observables(_side(199.0, 1000))
    cell = next(row for row in transfer.compare(reference, batch)["bandRows"]
                if row["row"] == "callDurationSeconds" and row["arm"] == "A")
    assert round(cell["ratio"], 4) == 8.3426
    assert cell["inBand"] is False


def test_the_cohort_is_executed_calls_only():
    """T7. A slot with no resolvable duration (exit 126's shape in 019) enters
    no median and no exact tuple. MUTATION: drop the `executed()` filter — the
    median moves."""
    side = _side(100.0, 1000)
    side["A"].append({"call": transfer.call_members(
        _call(durationSeconds=None, startedAt=None, endedAt=None,
              model="other")),
        "completionBytes": 99999, "reasoningOutputTokens": None})
    obs = transfer.observables(side)
    assert obs["perArm"]["A"]["executed"] == 3
    assert obs["perArm"]["A"]["medians"]["callDurationSeconds"] == 100.0
    assert obs["perArm"]["A"]["medians"]["completionBytes"] == 1000
    assert obs["exact"]["model"] == "m" and obs["exactProblems"] == []


def test_a_duration_resolves_from_the_wrappers_timestamps():
    call = _call(durationSeconds=None, startedAt="2026-08-24T10:00:00Z",
                 endedAt="2026-08-24T10:03:20Z")
    assert transfer.duration_seconds(call) == 200.0
    assert transfer.executed(call)


def test_a_side_that_disagrees_with_itself_is_its_own_problem():
    side = _side(100.0, 1000)
    side["B"][0]["call"]["model"] = "other"
    obs = transfer.observables(side)
    assert obs["exactProblems"]
    c4 = transfer.compare(_reference(), obs)
    assert c4["outcome"] == transfer.OUTCOME_PIPELINE_INVALID


def test_the_token_row_is_descriptive_and_gates_nothing():
    """R2-11(A)'s ruling: two band rows; the reasoning-token median is
    published on both sides and decides nothing. MUTATION: add the token row
    to `REGISTERED_BANDS` — the outcome flips to calibration-invalid here."""
    reference = _reference()
    batch = transfer.observables(_side(100.0, 1000, tokens=5))
    c4 = transfer.compare(reference, batch)
    assert c4["outcome"] == transfer.OUTCOME_HOLD
    assert [row for row, _ in transfer.REGISTERED_BANDS] == \
        ["callDurationSeconds", "completionBytes"]
    tokens = [row for row in c4["descriptiveMedians"]
              if row["row"] == "reasoningOutputTokens"]
    assert len(tokens) == 3 and all(row["gates"] is False for row in tokens)
    assert tokens[0]["pilot"] == 500 and tokens[0]["batch"] == 5


# ---------------------------------------------------------------------------
# the reference pin, through the scorer's own seat
# ---------------------------------------------------------------------------

def test_an_absent_or_mismatched_reference_is_pipeline_invalid(tmp_path,
                                                                monkeypatch):
    """T6. MUTATION: make the absent branch set `held: False` (row 3) instead
    of a pipeline problem — (a) fails."""
    monkeypatch.setattr(score, "STUDY", str(tmp_path))
    batch = transfer.observables(_side(100.0, 1000))
    pins = {"calibration": {"label": "2026-08-24-pilot",
                            "c4ReferenceSha256": "sha256:" + "0" * 64}}
    c4, problems = score.transfer_gate(pins, batch)
    assert problems and c4["outcome"] == transfer.OUTCOME_PIPELINE_INVALID
    assert any("absent" in problem for problem in problems)
    here = tmp_path / "calibration" / "2026-08-24-pilot"
    here.mkdir(parents=True)
    body = json.dumps(_reference(), indent=2, sort_keys=True)
    (here / transfer.REFERENCE_NAME).write_text(body, encoding="utf-8")
    c4, problems = score.transfer_gate(pins, batch)
    assert any("hashes to" in problem for problem in problems)
    pins["calibration"]["c4ReferenceSha256"] = "sha256:" + hashlib.sha256(
        body.encode("utf-8")).hexdigest()
    c4, problems = score.transfer_gate(pins, batch)
    assert problems == [] and c4["outcome"] == transfer.OUTCOME_HOLD
    pins["calibration"]["label"] = None
    c4, problems = score.transfer_gate(pins, batch)
    assert any("calibration.label is null" in problem for problem in problems)


def test_the_gate_reads_the_registered_table_verbatim(preregistration):
    """T12. Prose currency: the band numbers and the exact-row names in §2a.5
    are the module's constants. MUTATION: change one band constant in the
    code — fails; change one in PREREGISTRATION.md — fails."""
    flat = " ".join(preregistration.split())
    for row, (low, high) in transfer.REGISTERED_BANDS:
        assert "[%.2f×, %.2f×]" % (low, high) in flat, row
    assert "per-arm median call duration" in flat
    assert "per-arm median completion bytes" in flat
    assert "two band rows, not three" in flat
    assert "The ratio** is pilot ÷ batch" in flat
    assert "C4 is two-sided" in flat


def test_the_markdown_prints_every_row_whatever_the_outcome():
    """T9. MUTATION: publish `transferGate` only when the gate fails — the
    hold case prints no section and this fails."""
    for factor in (1.0, 9.0):
        reference = _reference(duration=100.0 * factor)
        c4 = transfer.compare(reference, transfer.observables(_side(100.0, 1000)))
        results = {"label": "PILOT", "unfilledPins": [], "decision": {
            "row": "x", "rowIndex": 1, "verdict": "v", "registeredText": "",
            "causes": []}, "pairedDenominators": {},
            "sharedClasses": {"count": 33, "unequalCount": 20},
            "e1": {}, "e2": {}, "e4": {}, "e5": None, "family": {},
            "familyGatedBy": ["x"], "refusals": {}, "transferGate": c4}
        body = score.results_markdown(results)
        assert "## C4 — the transfer gate" in body
        for row in transfer.REGISTERED_EXACT_ROWS:
            assert "| %s |" % row in body
        assert body.count("| callDurationSeconds |") == 3
        assert body.count("| completionBytes |") == 3
        assert ("Outcome: **hold**" in body) == (factor == 1.0)


def test_the_two_other_publication_paths_carry_the_member_explicitly():
    """The declared-short and terminal documents carry `transferGate: null`
    rather than omitting it — a reader can distinguish "not evaluated on this
    path" from "the publisher forgot"."""
    with open(os.path.join(HARNESS, "score.py"), "rb") as handle:
        source = handle.read().decode("utf-8")
    assert source.count('"transferGate": None') == 2
    assert '"transferGate": c4' in source


def test_pipeline_invalid_is_derived_not_hard_coded():
    """T10, at the source: the results literal derives `pipelineInvalid` from
    the outcome's problems. MUTATION: restore the hard-coded False — fails."""
    with open(os.path.join(HARNESS, "score.py"), "rb") as handle:
        source = handle.read().decode("utf-8")
    assert '"pipelineInvalid": bool(outcome["pipelineProblems"])' in source
    assert '"pipelineInvalid": False,\n            "pinsRawSha256"' not in source


def test_the_family_clobber_is_an_extend(tmp_path):
    """T11, a regression fence: `registered_family()` EXTENDS the seeded
    pipeline problems rather than assigning over them. MUTATION: restore
    `outcome["pipelineProblems"] = [...]` at the absent-module site — fails."""
    outcome = {"pipelineProblems": ["C4 exact row model differs"],
               "shortfallDeclared": [], "controlGates": {}, "family": {}}
    saved = score.family_module
    score.family_module = lambda: None
    try:
        score.registered_family({}, {}, {}, outcome, {}, [])
    finally:
        score.family_module = saved
    assert outcome["pipelineProblems"][0] == "C4 exact row model differs"
    assert len(outcome["pipelineProblems"]) == 2
