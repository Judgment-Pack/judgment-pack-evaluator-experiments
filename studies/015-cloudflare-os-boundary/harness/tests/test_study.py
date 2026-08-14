"""Protocol-integrity suite: vocabulary sync, registry schema, manifests, refusals.

Per-code reachability and first-failure ordering live in `test_reachability.py`; this
file owns everything that must hold before any cell runs.

Nothing here adjudicates a reviewer-holdout fixture. The holdout may be *constructed*
before the freeze — the scorer's gate requires the fixtures to exist — but no layer
verdict is computed over one until the preregistration is frozen, so every condition
below is built from locked fixtures or from the registry alone.
"""

import json
import re

import pytest

import commitment as cmt
import make_manifest
import score
import typecheck
import verify
from conftest import STUDY, load_json


# ---------------------------------------------------------------------------
# vocabulary sync — SPEC section 5 vs the code vs the scorer
# ---------------------------------------------------------------------------

def spec_text():
    return (STUDY / "adapter" / "SPEC.md").read_text(encoding="utf-8")


ALL_CODES = verify.UPSTREAM_CODES + verify.BINDING_CODES + verify.REPLAY_CODES


@pytest.mark.parametrize("code", ALL_CODES)
def test_every_registered_code_is_in_the_spec(code):
    assert "`%s`" % code in spec_text(), code


def test_spec_code_tables_are_exactly_the_registered_vocabulary():
    section = spec_text().split("## 5. The verification ceremony", 1)[1]
    upstream_section = section.split("### Layer `binding`", 1)[0]
    binding_section = section.split("### Layer `binding`", 1)[1].split(
        "### Layer `replay`", 1
    )[0]
    replay_section = section.split("### Layer `replay`", 1)[1].split(
        "### Report vocabulary", 1
    )[0]
    numbered = re.compile(r"^\d+\.\s+`([a-z0-9-]+)`", re.MULTILINE)
    assert set(numbered.findall(upstream_section)) == set(verify.UPSTREAM_CODES)
    binding_codes = {
        token
        for token in re.findall(r"`([a-z0-9-]+)`", binding_section)
        if token in verify.BINDING_CODES
    }
    assert binding_codes == set(verify.BINDING_CODES)
    replay_codes = set(re.findall(r"`(replay-[a-z0-9-]+)`", replay_section))
    assert replay_codes == set(verify.REPLAY_CODES)


def reachability_asserted_codes():
    """Every verdict code the reachability suite constructs a minimal condition for.

    The join key is the assertion itself — `...["code"] == "<code>"`, read out of that
    suite's own source — so a check whose fixture disappears cannot keep the claim that
    one exists.
    """
    source = (STUDY / "harness" / "tests" / "test_reachability.py").read_text(
        encoding="utf-8"
    )
    return set(
        re.findall(
            r'\[ ?"code" ?\] ?== ?"([a-z0-9-]+)"', re.sub(r"\s+", " ", source)
        )
    )


def test_every_binding_check_is_ordered_named_and_reachable():
    """Three registry facts about the nineteen binding checks — and only those three.

    That this document's numbered steps are the order the checks run in; that the SPEC's
    binding section names every code each check can return; and that the reachability
    suite constructs a minimal condition for each of those codes.

    It does **not** establish that the SPEC's prose and the implementation mean the same
    thing. Round 5 (finding 5) found the earlier name — `..._is_the_implemented_order` —
    claiming an equivalence its body never checked: it compared labels. Semantic
    agreement between the two is what review is for, and nothing here substitutes for it.
    """
    section = spec_text().split("### Layer `binding`", 1)[1].split(
        "### Layer `replay`", 1
    )[0]
    spec_order = []
    for line in section.splitlines():
        match = re.match(r"^\d+\.\s+`([a-z0-9-]+)`", line.strip())
        if match:
            spec_order.append(match.group(1))
    implemented = [label.split("/")[0] for label, _ in verify.BINDING_CHECKS]
    assert spec_order == implemented

    reachable = reachability_asserted_codes()
    for label, _ in verify.BINDING_CHECKS:
        for code in label.split("/"):
            assert "`%s`" % code in section, code
            assert code in reachable, code


def test_scorer_vocabulary_is_derived_from_verify():
    assert set(score.LAYER_OUTCOMES["upstream"]) == {
        "pass",
        "not-engaged",
        "unavailable",
    } | {"fail:" + code for code in verify.UPSTREAM_CODES}
    assert set(score.LAYER_OUTCOMES["binding"]) == {"pass"} | {
        "fail:" + code for code in verify.BINDING_CODES
    }
    assert set(score.LAYER_OUTCOMES["replay"]) == {"pass", "unavailable"} | {
        "fail:" + code for code in verify.REPLAY_CODES
    }


def test_execution_states_and_connector_outcomes_are_in_the_spec():
    text = spec_text()
    for state in verify.EXECUTION_STATES + verify.CONNECTOR_OUTCOMES:
        assert "`%s`" % state in text, state


def test_not_engaged_is_not_a_pass_anywhere_in_the_scorer():
    """`not-engaged` must be its own outcome, never folded into pass in the vocabulary."""
    assert "not-engaged" in score.LAYER_OUTCOMES["upstream"]
    assert "not-engaged" not in score.LAYER_OUTCOMES["binding"]
    assert "not-engaged" not in score.LAYER_OUTCOMES["replay"]


# ---------------------------------------------------------------------------
# registry and manifests
# ---------------------------------------------------------------------------

def test_matrix_is_schema_clean():
    assert score.matrix_problems(load_json(STUDY / "harness" / "MATRIX.json")) == []


def test_matrix_layer_attribution_is_single_layer_for_endpoints():
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    for cell in registry["cells"]:
        if cell["role"] != "endpoint":
            continue
        failing = [
            layer
            for layer, outcome in cell["expected"].items()
            if outcome not in ("pass", "not-engaged")
        ]
        assert len(failing) == 1, (cell["id"], failing)


def test_every_endpoint_registers_a_mutation_constraint():
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    for cell in registry["cells"]:
        assert cell["mutationConstraint"].strip(), cell["id"]


def test_holdout_is_authored_disjoint_and_constructed():
    holdout = load_json(STUDY / "harness" / "MATRIX-HOLDOUT.json")
    assert score.holdout_problems(holdout) == []
    assert holdout["reviewer"]
    assert len(holdout["cells"]) >= 4


def test_holdout_expectations_match_the_authored_file_modulo_the_recorded_migration():
    """The reviewer's expectations are never revised — only mechanically re-keyed."""
    authored = load_json(STUDY / "reviews" / "round-1" / "MATRIX-HOLDOUT.authored.json")
    migrated = load_json(STUDY / "harness" / "MATRIX-HOLDOUT.json")
    assert migrated.get("schemaMigration")
    by_id = {cell["id"]: cell for cell in migrated["cells"]}
    assert set(by_id) == {cell["id"] for cell in authored["cells"]}
    for cell in authored["cells"]:
        after = by_id[cell["id"]]
        assert after["construction"] == cell["construction"]
        assert after["note"] == cell["note"]
        assert after["upstreamChecksReplayed"] == cell["platformChecksEngaged"]
        assert after["expected"]["binding"] == cell["expected"]["binding"]
        assert after["expected"]["replay"] == cell["expected"]["replay"]
        expected_upstream = cell["expected"]["cf"]
        if not cell["platformChecksEngaged"] and expected_upstream == "pass":
            expected_upstream = "not-engaged"
        assert after["expected"]["upstream"] == expected_upstream


def test_study_manifest_is_exact():
    assert make_manifest.manifest_problems() == []


def test_the_study_manifest_excludes_the_appendable_files_by_construction():
    """ADR 0004: the manifest covers what must not change, and these two must.

    `DEVIATIONS.md` is the only place a post-freeze correction may land, so covering it
    would mean the first genuine deviation broke the anchor the deviation exists to
    protect; `README.md` carries a status banner that has to be able to change. Both are
    excluded by a named constant rather than by omission, so a later widening fails here
    instead of quietly taking the deviation mechanism with it.
    """
    assert make_manifest.EXCLUDED_DOCUMENTS == ("DEVIATIONS.md", "README.md")
    covered = make_manifest.manifest_entries()
    for name in make_manifest.EXCLUDED_DOCUMENTS:
        assert (STUDY / name).is_file(), name  # excluded, not merely absent
        assert name not in covered, name
    # ...and the exclusion is the only reason: the registered documents beside them are
    # covered, so this is a scoping decision rather than a manifest that misses .md files.
    assert "PREREGISTRATION.md" in covered
    assert "PREREG-REVIEW.md" in covered
    assert "harness/STUDY-MANIFEST.sha256" not in covered, (
        "the manifest must not cover itself either"
    )


def test_every_fixture_manifest_is_exact():
    roots = [STUDY / "fixtures" / "baseline"]
    for parent in ("mutations", "holdout"):
        roots.extend(sorted((STUDY / "fixtures" / parent).iterdir()))
    for root in roots:
        assert verify.manifest_problems(root) == [], root.name


def test_fixture_typecheck_is_clean(cfos_source):
    del cfos_source
    assert typecheck.typecheck_problems() == []


def test_typecheck_is_a_scorer_precondition():
    """A published score may not call itself valid without the registered typecheck.

    The locked stratum is checked before adjudication; the holdout's own fixtures are
    checked only when the holdout is being adjudicated, so a holdout defect cannot make
    the locked stratum inconclusive (round 2, blocker 5).
    """
    source = (STUDY / "harness" / "score.py").read_text(encoding="utf-8")
    assert "typecheck.typecheck_problems(include_holdout=False)" in source
    assert "typecheck.typecheck_problems(include_holdout=True)" in source


# ---------------------------------------------------------------------------
# refusals and validity separation
# ---------------------------------------------------------------------------

def test_holdout_refused_while_preregistration_digest_is_null(tmp_path):
    pins = load_json(STUDY / "harness" / "PINS.json")
    if pins["preregistration"]["sha256"] is None:
        with pytest.raises(SystemExit):
            score.run(tmp_path / "attempt", include_holdout=True)
        # The refusal is recorded, not silent: the attempt marker is written before
        # anything is read, and nothing was adjudicated or published.
        assert (tmp_path / "attempt" / "ATTEMPT.json").is_file()
        assert not (tmp_path / "attempt" / "RESULTS.json").exists()


def test_scorer_refuses_an_existing_attempt_root(tmp_path):
    (tmp_path / "attempt").mkdir()
    with pytest.raises(SystemExit):
        score.run(tmp_path / "attempt")


def test_holdout_outcomes_do_not_enter_r1_arithmetic():
    """Structural: the two strata are adjudicated into disjoint collections.

    This is the whole guarantee, and the name says so. It is **not** that nothing in the
    holdout can affect R1: registry parsing, pin enforcement, the whole-study manifest and
    publication are attempt-scope preconditions shared by both strata, so a malformed
    holdout artifact can still make the whole attempt inconclusive (round 4, R4-5; round 5
    found the earlier name `..._cannot_change_r1` claiming more than these four
    substring assertions can carry, and more than the scorer does).
    """
    source = (STUDY / "harness" / "score.py").read_text(encoding="utf-8")
    assert "holdout_validity = []" in source
    assert 'sink = holdout_validity if is_holdout else validity' in source
    # R1's inputs are drawn from `rows`, which only ever receives locked cells.
    assert 'invalid = [row for row in rows if row["status"] == NOT_ADJUDICATED]' in source
    assert '(holdout_rows if is_holdout else rows).append(row)' in source


def test_replay_set_drift_is_not_adjudicated(jpack_bin, tmp_path):
    """An upstream report whose replayed set differs from the registry is validity."""
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    cell = dict(next(c for c in registry["cells"] if c["id"] == "pos-baseline"))
    verdicts = {
        "cells": {
            "pos-baseline": {
                "verdict": "pass",
                "code": None,
                "detail": None,
                "engaged": ["classifyTool"],  # the registry says both are replayed
            }
        }
    }
    validity = []
    row = score.adjudicate_cell(cell, jpack_bin, tmp_path, verdicts, validity)
    assert row["status"] == score.NOT_ADJUDICATED
    assert any("upstreamChecksReplayed" in item["problem"] for item in validity)
    assert row["divergences"] == []


def test_registered_absences_authority_is_the_cell_field():
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    cell = dict(next(c for c in registry["cells"] if c["id"] == "pos-baseline"))
    cell["registeredAbsences"] = ["report"]
    problems = score.pipeline_problems(STUDY / "fixtures" / "baseline", cell)
    assert "registered absence is present: report.json" in problems


def test_layer_functions_never_read_the_matrix():
    assert "MATRIX" not in (STUDY / "adapter" / "verify.py").read_text(encoding="utf-8")


def test_probe_sources_never_read_the_matrix():
    for path in sorted((STUDY / "probes").rglob("*.ts")):
        code_lines = [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if not line.strip().startswith(("//", "*", "/*"))
        ]
        assert "MATRIX" not in "\n".join(code_lines), path.name


# ---------------------------------------------------------------------------
# the adapter's reproduction of the platform's own rule
# ---------------------------------------------------------------------------

def test_action_kind_tag_matches_the_platform_rule():
    # The literal the pinned MCP Portal connector produces for the registered endpoint,
    # upstream server id and tool — double-encoded, because the portal's scope tag is
    # itself encoded and `actionKindFor` encodes the scope tag again.
    assert cmt.action_scope_tag() == (
        "mcp-portal:https%3A%2F%2Ftracker.example%2Fmcp:portal-tracker"
    )
    assert cmt.action_kind_tag() == (
        "mcp-portal%3Ahttps%253A%252F%252Ftracker.example%252Fmcp%3Aportal-tracker"
        ":tracker_create_work_item"
    )


def test_adapter_tag_reproduction_agrees_with_upstream(cfos_source):
    """The adapter reproduces `actionKindFor`; upstream itself must agree.

    This calls the PINNED function through the build-helper runner and compares its
    output to `commitment.py`'s own reproduction over adversarial inputs. An earlier
    probe claimed to do this and did not: it compared upstream against an inline
    restatement of upstream's one-line body, asserting f(x) == f(x) while six documents
    cited it as the guarantee.
    """
    del cfos_source
    import cf_runner

    cases = [
        (cmt.action_scope_tag(), cmt.ACTION_TOOL),
        (cmt.action_scope_tag(), cmt.SECOND_TOOL),
        ("scope with spaces", "tool/with/slashes"),
        ("a:b", "c d"),
        ("caf\u00e9", "na\u00efve_tool"),
        ("100%", "a+b=c"),
        ("~!*'()-_.", "already%20encoded"),
    ]
    helpers = cf_runner.build_helpers(
        {
            "actionKinds": [
                {"scopeTag": scope, "toolName": tool} for scope, tool in cases
            ]
        }
    )
    assert len(helpers["actionKinds"]) == len(cases)
    for item, (scope, tool) in zip(helpers["actionKinds"], cases):
        assert item["kind"]["tag"] == cmt.action_kind_tag(scope, tool), (scope, tool)
        assert item["kind"]["label"] == tool


# Cells whose construction deliberately makes the retained prose disagree with the call
# the store now holds. Each is the registry's own words, and each is asserted to DIFFER
# below, so the set cannot decay into a blanket skip.
REGISTERED_PROSE_MUTATIONS = {
    # "after approval the gatekeeper-side staged arguments are edited to provision a
    # different requester; the ledger record and its prose description are untouched"
    "b02-argument-drift",
}
# ...and cells whose action-kind TAG is a literal the reviewer forged on purpose.
REGISTERED_TAG_FORGERIES = {
    # "change actionKindTag to the literal reviewer-forged-scope:create_work_item"
    "h04-coherent-target-and-kind-substitution",
}


def registered_action_rows():
    """Every action row of both strata, with its cell, staged call and deployment.

    The holdout is *read*, not adjudicated: no layer verdict is computed here. Round 5
    (finding 5) found this condition excluding the holdout, which is where the second
    deployment lives — precisely the stratum whose construction it needed to hold.
    """
    import build_fixtures

    deployments = {
        deployment["resourceUrl"]: deployment
        for deployment in build_fixtures.DEPLOYMENTS
    }
    registries = [
        (load_json(STUDY / "harness" / "MATRIX.json"), "locked-replication"),
        (load_json(STUDY / "harness" / "MATRIX-HOLDOUT.json"), "reviewer-holdout"),
    ]
    for registry, stratum in registries:
        for cell in registry["cells"]:
            directory = score.cell_directory(cell, stratum)
            ledger = json.loads((directory / "ledger.json").read_text(encoding="utf-8"))
            platform = json.loads(
                (directory / "platform.json").read_text(encoding="utf-8")
            )
            gatekeepers = {
                gatekeeper.get("id"): gatekeeper
                for gatekeeper in platform.get("gatekeepers") or []
            }
            for entry in ledger:
                if entry.get("type") != "action":
                    continue
                deployment = deployments.get(entry.get("resourceUrl"))
                assert deployment is not None, (cell["id"], entry.get("resourceUrl"))
                calls = [
                    item
                    for item in platform.get("stagedCalls") or []
                    if item.get("gatekeeperId") == entry.get("gatekeeperId")
                    and item.get("action") == entry.get("action")
                ]
                assert len(calls) == 1, (cell["id"], entry["id"])
                gatekeeper = gatekeepers.get(entry.get("gatekeeperId"))
                tool = next(
                    (
                        candidate
                        for candidate in (gatekeeper or {}).get("tools") or []
                        if candidate.get("name") == calls[0]["toolName"]
                    ),
                    None,
                )
                assert tool is not None, (cell["id"], entry["id"])
                yield cell["id"], entry, calls[0], tool, deployment


def test_registered_scenario_is_connector_shaped(cfos_source):
    """Round 2, blocker 2: every registered identifier must be one whose shape a pinned
    connector's source defines. The generic MCP connector hardwires byo, so a vetted,
    auto-approvable write is producible only through the portal.

    Round 5 (findings 4 and 5) made the comparison a whole-description one. For every
    action row of both strata, the retained title and description bytes are regenerated
    by the PINNED `describeCall` from the registered deployment the row names, the tool
    the retained catalog holds, and the arguments the retained staged call carries — and
    the action-kind tag and label are compared unconditionally, against the deployment's
    own scope tag rather than the first portal's. The earlier version compared no prose,
    skipped the holdout, and checked the label only where the tag already matched its
    primary-deployment expectation, which is exactly what masked `b04`.

    What this establishes is coherence between a row's prose and the deployment it names
    — not that the deployment is real. The deployment tuple is registered by the builder;
    the bytes are generated by upstream.
    """
    del cfos_source
    import cf_runner

    assert cmt.RESOURCE_URL.endswith("#server=tracker")
    assert cmt.ACTION_TOOL.startswith("tracker_")
    assert cmt.SERVER_TRUST == "vetted"

    rows, requests = [], []
    for cell_id, entry, call, tool, deployment in registered_action_rows():
        description = entry["description"]
        # session.ts:126-135 always sets these three.
        assert description.get("awaitDecision") is True, cell_id
        assert isinstance(description.get("autoApprovable"), bool), cell_id
        assert description["implementsRevert"] is False, cell_id
        # The row's denormalized title is the deployment's (overseer.ts:2686).
        assert entry.get("resourceTitle") == deployment["resourceTitle"], cell_id
        label = "%s:%s" % (cell_id, entry["id"])
        requests.append(
            {
                "label": label,
                "serverName": deployment["serverName"],
                "endpoint": deployment["endpoint"],
                "tool": tool,
                "toolArgs": call["arguments"],
                "mode": "action",
                "classifiedBy": "default",
            }
        )
        rows.append((cell_id, label, description, call, deployment))

    described = cf_runner.build_helpers({"describeCalls": requests})["describedCalls"]
    for cell_id, label, description, call, deployment in rows:
        generated = described[label]
        assert description["title"] == generated["title"], cell_id
        if cell_id in REGISTERED_PROSE_MUTATIONS:
            assert description["description"] != generated["description"], cell_id
        else:
            assert description["description"] == generated["description"], cell_id
        # ...and the action kind is the connector's own, for the tool the staged call
        # names and the deployment the row names — not a literal the fixture chose.
        kind = description["actionKind"]
        assert kind["label"] == call["toolName"], cell_id
        expected_tag = cmt.action_kind_tag(
            cmt.action_scope_tag(deployment["resourceUrl"], deployment["serverId"]),
            call["toolName"],
        )
        if cell_id in REGISTERED_TAG_FORGERIES:
            assert kind["tag"] != expected_tag, cell_id
        else:
            assert kind["tag"] == expected_tag, cell_id


def test_derived_action_fields_are_disjoint_from_contextual_ones():
    assert not set(cmt.DERIVED_ACTION_FIELDS) & set(cmt.CONTEXTUAL_ACTION_FIELDS)
    assert set(cmt.DERIVED_ACTION_FIELDS) | set(cmt.CONTEXTUAL_ACTION_FIELDS) == set(
        cmt.ACTION_FIELDS
    )


def test_suppressed_codes_are_published_for_multi_defect_cells(jpack_bin, tmp_path):
    """s05 carries a second defect by construction; it must be published, not hidden."""
    del jpack_bin, tmp_path
    result = verify.layer_binding(
        verify.Cell(STUDY / "fixtures" / "mutations" / "s05-handoff-dropped")
    )
    assert result["code"] == "handoff-dropped"
    assert "report-misattribution" in result["suppressed"]


def test_matrix_modeled_dependencies_are_registered_where_used():
    """Any cell whose construction leans on a modeled datum must declare it."""
    registry = load_json(STUDY / "harness" / "MATRIX.json")
    for cell in registry["cells"]:
        directory = score.cell_directory(cell)
        platform = json.loads((directory / "platform.json").read_text(encoding="utf-8"))
        declared = set(cell["modeledDependencies"])
        if platform.get("effects"):
            assert "effectAttestation" in declared, cell["id"]
        if platform.get("drainWitnesses"):
            assert "drainSnapshot" in declared, cell["id"]
        if platform.get("stagedCalls"):
            assert "stagedCallArguments" in declared, cell["id"]
