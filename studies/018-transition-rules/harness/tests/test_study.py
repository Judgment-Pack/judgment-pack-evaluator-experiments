"""Study-level integrity: pins, vocabulary sync, pair machinery, determinism."""

import dataclasses
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import build_fixtures
import run_verify
import score
import upstream016
import transition

STUDY = Path(__file__).resolve().parent.parent.parent


def test_study016_sources_match_their_pins():
    assert upstream016.problems() == []


def test_matrix_schema_and_frozen_id_set():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    assert score.matrix_schema_problems(matrix) == []


def test_pins_registry_is_consistent():
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    values = {m: (pins.get(m) or {}).get("sha256") for m in score.FREEZE_PINS}
    if any(v is None for v in values.values()):
        assert all(v is None for v in values.values()), values
    else:
        for member, relative in score.PINNED_DIGEST_MEMBERS:
            assert values[member] == score.sha256_file(STUDY / relative), member
    assert pins["harnessPython"]["version"] == "3.12.11"


def test_fixture_manifests_verify():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    for cell in matrix["cells"]:
        directory = build_fixtures.cell_directory(STUDY / "fixtures", cell["id"])
        assert directory.is_dir(), cell["id"]
        assert run_verify.manifest_problems(directory) == [], cell["id"]
        assert run_verify.required_file_problems(directory, cell) == [], cell["id"]


def test_no_bytecode_caches_shadow_pinned_source():
    """Round-1 R1-1: a .py digest does not describe what ran if a divergent
    cache is loaded instead; an equivalent cache is accepted."""
    assert score.bytecode_cache_problems() == []


def test_registered_authority_binds_the_retained_fixtures():
    """Round-1 R1-13, round-3 blocker 4: the pin must bind the fixtures.

    Deriving *a* key from the registered label proves nothing — the derived
    public key has to be the one every retained trust configuration pins, and
    the locked builder has to read the label rather than hard-code it. Both are
    checked under mutation of the label.
    """
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    assert score.dependency_problems(pins) == []
    assert build_fixtures.registered_authority_label() == \
        pins["registryAuthority"]["authoritySeedLabel"]

    registry = upstream016.load(build=True).checkpoint
    expected = registry.public_key_b64(
        registry.private_key(pins["registryAuthority"]["authoritySeedLabel"]))
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    for cell in matrix["cells"]:
        retained = json.loads((build_fixtures.cell_directory(
            STUDY / "fixtures", cell["id"]) / "trustconfig.json").read_text(encoding="utf-8"))
        assert retained["authorityPublicKey"] == expected, cell["id"]

    # a label that derives a different key must be caught for EVERY cell, not
    # merely somewhere (round-4 blocker 5: "some mismatch appears" would pass a
    # scorer that checked one fixture and ignored the rest)
    mutated = json.loads(json.dumps(pins))
    mutated["registryAuthority"]["authoritySeedLabel"] = "study-018/not-the-registered-label"
    problems = score.pin_problems(mutated)
    flagged = {cell["id"] for cell in matrix["cells"]
               if any(cell["id"] in problem and "does not derive" in problem
                      for problem in problems)}
    assert flagged == {cell["id"] for cell in matrix["cells"]}, (
        "the authority pin does not bind every retained trust configuration; "
        "unflagged: %s" % sorted({c["id"] for c in matrix["cells"]} - flagged))


def test_authority_check_reads_each_fixture_not_just_the_first(tmp_path, monkeypatch):
    """Round-5 finding 5: deriving "every cell was checked" from ids in error
    strings passes a scorer that re-reads the FIRST trust configuration while
    reporting the current loop id. Here exactly one fixture is corrupted, in a
    copied tree, and exactly that cell must be flagged."""
    shutil.copytree(STUDY / "fixtures", tmp_path / "fixtures")
    monkeypatch.setattr(score, "STUDY", tmp_path)
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))

    # Round-6 finding 4: two victims left a scorer free to read those two and
    # reuse the first fixture for the other twenty. Every cell is corrupted in
    # turn, so any cell the scorer does not actually read shows up here.
    for victim in [cell["id"] for cell in matrix["cells"]]:
        path = build_fixtures.cell_directory(tmp_path / "fixtures", victim) / "trustconfig.json"
        original = path.read_text(encoding="utf-8")
        trust = json.loads(original)
        trust["authorityPublicKey"] = "A" + trust["authorityPublicKey"][1:]
        path.write_text(json.dumps(trust, indent=2), encoding="utf-8")
        try:
            problems = [p for p in score.pin_problems(pins) if "does not derive" in p]
        finally:
            path.write_text(original, encoding="utf-8")
        assert len(problems) == 1 and victim in problems[0], (victim, problems)


def test_locked_builder_follows_a_mutated_authority_label(tmp_path, monkeypatch):
    """Round-4 blocker 5: banning one literal spelling is not the property.

    The builder must actually *read* the registered label, so changing the label
    must change the authority every fixture pins. Exercised by pointing
    `PINS_PATH` at a mutated registry and rebuilding.
    """
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    pins["registryAuthority"]["authoritySeedLabel"] = "study-018/some-other-authority"
    mutated_pins = tmp_path / "PINS.json"
    mutated_pins.write_text(json.dumps(pins, indent=2), encoding="utf-8")
    monkeypatch.setattr(build_fixtures, "PINS_PATH", mutated_pins)

    assert build_fixtures.registered_authority_label() == "study-018/some-other-authority"
    payloads = build_fixtures.build_payloads()
    registry = upstream016.load(build=True).checkpoint
    expected = registry.public_key_b64(
        registry.private_key("study-018/some-other-authority"))
    committed = registry.public_key_b64(
        registry.private_key(json.loads(
            (STUDY / "harness" / "PINS.json").read_text(encoding="utf-8")
        )["registryAuthority"]["authoritySeedLabel"]))
    assert expected != committed
    ns = upstream016.load(build=True)
    for cid, payload in payloads.items():
        trust = json.loads(payload["trustconfig.json"].decode("utf-8"))
        assert trust["authorityPublicKey"] == expected, cid
        # Round-5 finding 5: checking only the emitted trust key would pass a
        # builder that kept signing histories with a hard-coded authority while
        # advertising the label-derived one — producing fixtures that cannot
        # verify. The snapshot must actually be signed by the label's key.
        outcome = ns.verify_currency.layer_currency(
            json.loads(payload["commitment.json"].decode("utf-8")),
            payload["snapshot.json"], payload["trustconfig.json"])
        if cid == "neg-currency-unauthenticated":
            # Round-6 finding 4: skipping this cell contradicted the "every
            # rebuilt cell" claim. It cannot demonstrate signer-follows-label,
            # because its signature is deliberately corrupted — so it is asserted
            # to be exactly that corruption and nothing else.
            assert outcome["code"] == "snapshot-signature-invalid", (cid, outcome["code"])
            continue
        assert outcome["verdict"] in ("pass", "fail"), (cid, outcome)
        assert outcome["code"] in (None, "not-current-at-snapshot"), (cid, outcome["code"])

    # an absent or empty label is refused rather than silently defaulted
    for bad in (None, "", 7):
        pins["registryAuthority"]["authoritySeedLabel"] = bad
        mutated_pins.write_text(json.dumps(pins, indent=2), encoding="utf-8")
        with pytest.raises(build_fixtures.BuildError):
            build_fixtures.registered_authority_label()


def test_registered_dependencies_are_enforced():
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    assert score.dependency_problems(pins) == []
    broken = json.loads(json.dumps(pins))
    broken["dependencies"]["versions"]["rfc8785"] = "0.0.0-not-installed"
    assert score.dependency_problems(broken) != []


def test_upstream_pins_are_bound_from_stamped_bytes():
    """Round-1 R1-3: the loader uses the mapping the attempt stamps."""
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    bound = upstream016.bind_pins(pins["study016"]["files"])
    assert bound == pins["study016"]["files"]
    with pytest.raises(upstream016.Upstream016Error):
        upstream016.bind_pins({"registry/verify_currency.py": "0" * 64})


def test_study_manifest_is_fresh():
    import make_manifest
    assert make_manifest.verify_problems() == []


def test_rebuild_is_deterministic_and_matches_committed_bytes(tmp_path):
    completed = subprocess.run(
        [sys.executable, str(STUDY / "harness" / "build_fixtures.py"),
         "--out", str(tmp_path / "fixtures")],
        capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stderr
    committed = STUDY / "fixtures" / "cells"
    rebuilt = tmp_path / "fixtures" / "cells"
    committed_files = sorted(p.relative_to(committed).as_posix()
                             for p in committed.rglob("*") if p.is_file())
    rebuilt_files = sorted(p.relative_to(rebuilt).as_posix()
                           for p in rebuilt.rglob("*") if p.is_file())
    assert committed_files == rebuilt_files
    for relative in committed_files:
        assert (committed / relative).read_bytes() == (rebuilt / relative).read_bytes(), relative


def test_scorer_is_deterministic_and_control_gates_hold(tmp_path):
    outputs = []
    for name in ("attempt-a", "attempt-b"):
        completed = subprocess.run(
            [sys.executable, str(STUDY / "harness" / "score.py"),
             "--attempt-root", str(tmp_path / name)],
            capture_output=True, text=True,
        )
        assert completed.returncode == 0, completed.stderr
        raw = (tmp_path / name / "RESULTS.json").read_text(encoding="utf-8")
        outputs.append(raw.replace(name, "attempt-x"))
        results = json.loads(raw)
        assert results["pipelineInvalid"] is False
        pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
        frozen = all((pins.get(m) or {}).get("sha256") is not None
                     for m in score.FREEZE_PINS)
        assert results["label"] == ("REGISTERED" if frozen else "PILOT")
        for cid, record in results["cells"].items():
            if record["role"] == "control-gate":
                assert record["adjudicated"] and not record["divergent"], cid
    assert outputs[0] == outputs[1]


def test_rendered_matrix_publishes_this_studys_evidence(tmp_path):
    """Round-3 blocker 3: the renderer published Study 017's witness triple, so
    every transition row read `compared=None, attributed=None, unattributed=None`
    while the study's own two fields went unrendered."""
    completed = subprocess.run(
        [sys.executable, str(STUDY / "harness" / "score.py"),
         "--attempt-root", str(tmp_path / "render")],
        capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stderr
    rendered = (tmp_path / "render" / "DETECTION-MATRIX.md").read_text(encoding="utf-8")
    for stale in ("compared=", "attributed=", "unattributed=", "witness"):
        assert stale not in rendered, stale
    results = json.loads((tmp_path / "render" / "RESULTS.json").read_text(encoding="utf-8"))
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))

    # Round-4 blocker 4: substring checks passed while values were wrong. Every
    # rendered row is now parsed and reconciled against RESULTS.json.
    rows = {}
    for line in rendered.splitlines():
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) == 6 and parts[2] in score.LAYERS:
            rows[(parts[0], parts[2])] = parts
    assert len(rows) == len(results["cells"]) * len(score.LAYERS), (
        "rendered rows do not cover every cell and layer")
    for (cid, layer), parts in rows.items():
        record = results["cells"][cid]
        assert parts[1] == record["role"]
        assert parts[3] == "`%s`" % record["expected"][layer]
        assert parts[4].startswith("`%s`" % record["observed"][layer])
        diverged = record["observed"][layer] != record["expected"][layer]
        assert ("≠" in parts[4]) == diverged, (cid, layer)
        if layer == "transition":
            # each field is checked in its own rendered clause, so registered
            # values cannot be swapped between fields and still pass
            expected_evidence = record.get("expectedRuleEvidence") or {}
            # Round-6 finding 3: `dict(zip(...))` silently dropped any extra
            # clause, and `startswith` let "citedPosition: 20" satisfy a
            # registered 2. The clause list is length-checked and each clause is
            # compared for exact equality against the value RESULTS.json carries.
            rendered_clauses = parts[5].split(", ")
            assert len(rendered_clauses) == len(score.EVIDENCE_FIELDS), parts[5]
            clauses = dict(zip(score.EVIDENCE_FIELDS, rendered_clauses))
            for field, value in (record.get("ruleEvidence") or {}).items():
                if field in expected_evidence:
                    marker = " ≠" if expected_evidence[field] != value else ""
                    wanted = "%s: %s (registered %s%s)" % (
                        field, value, expected_evidence[field], marker)
                else:
                    wanted = "%s: %s" % (field, value)
                assert clauses[field] == wanted, (cid, field, clauses[field], wanted)
            # a concordant row carries no structured mismatch marker either
            if not record["divergent"]:
                assert "≠" not in parts[5], (cid, parts[5])

    # every registered identity group is rendered as its own row
    assert "## Registered identity groups" in rendered
    for group in matrix.get("identityGroups", ()):
        assert ", ".join(group) in rendered

    # The mismatch markers must appear when values disagree. Round-5 finding 4:
    # a single fabrication that breaks BOTH at once, checked with "does any row
    # contain ≠", passes even when one of the two markers is deleted. The two
    # are therefore fabricated and asserted separately.
    victim = "div-position-window-elapsed"

    def render(mutate):
        fabricated = json.loads(json.dumps(results["cells"]))
        mutate(fabricated[victim])
        forged = score.detection_matrix_markdown(
            "PILOT", matrix, fabricated, {}, "R1 falsified (PILOT)", [victim])
        return [l for l in forged.splitlines() if l.startswith("| " + victim + " |")]

    # Round-6 finding 3: both fabrications left `divergent`/`divergentLayers` at
    # their concordant values, so a renderer leaking a marker across columns
    # *conditional on the real divergence state* passed. Each fabrication now
    # carries the divergence state a genuine record of that kind would carry.
    def outcome_only(record):
        record["observed"]["transition"] = "usable"
        record["divergent"] = True
        record["divergentLayers"] = ["transition"]

    def evidence_only(record):
        record["ruleEvidence"]["retiredAtPosition"] = 99
        record["expectedRuleEvidence"] = dict(record.get("expectedRuleEvidence") or {},
                                              retiredAtPosition=4)
        record["divergent"] = True
        record["divergentLayers"] = ["transition:retiredAtPosition"]

    outcome_rows = render(outcome_only)
    transition_row = [r for r in outcome_rows if "| transition |" in r][0]
    assert "`usable` ≠" in transition_row, "outcome mismatch marker missing"
    assert "≠" not in transition_row.rsplit("|", 2)[1], (
        "an outcome-only mismatch must not mark the evidence column")

    evidence_rows = render(evidence_only)
    transition_row = [r for r in evidence_rows if "| transition |" in r][0]
    assert "retiredAtPosition: 99 (registered 4 ≠)" in transition_row, (
        "structured-evidence mismatch marker missing")
    assert "` ≠" not in transition_row, (
        "an evidence-only mismatch must not mark the outcome column")


def test_scorer_refuses_existing_attempt_root(tmp_path):
    root = tmp_path / "occupied"
    root.mkdir()
    completed = subprocess.run(
        [sys.executable, str(STUDY / "harness" / "score.py"),
         "--attempt-root", str(root)],
        capture_output=True, text=True,
    )
    assert completed.returncode == 2
    assert "already exists" in completed.stderr


def test_holdout_refused_while_freeze_pins_null(tmp_path, monkeypatch):
    pins = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    for member in score.FREEZE_PINS:
        pins.setdefault(member, {})["sha256"] = None
    nulled = tmp_path / "PINS.json"
    nulled.write_text(json.dumps(pins, indent=2), encoding="utf-8")
    monkeypatch.setattr(score, "PINS_PATH", nulled)
    root = tmp_path / "holdout-early"
    assert score.main(["--attempt-root", str(root), "--include-holdout"]) == 2
    results = json.loads((root / "RESULTS.json").read_text(encoding="utf-8"))
    assert results["pipelineInvalid"] is True
    assert "refused" in results["problem"]
    marker = json.loads((root / "ATTEMPT.json").read_text(encoding="utf-8"))
    assert marker["pinsRawSha256"] == results["pinsRawSha256"]
    assert marker["pinsRawSha256"] is not None


def test_scorer_records_attempt_before_pins_parse(tmp_path, monkeypatch):
    root = tmp_path / "marker"
    broken = tmp_path / "PINS.json"
    broken.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(score, "PINS_PATH", broken)
    with pytest.raises(BaseException):
        score.main(["--attempt-root", str(root)])
    assert (root / "ATTEMPT.json").is_file()
    assert (root / "RESULTS.json").is_file()


def test_spec_vocabulary_matches_the_evaluator():
    """rule/SPEC.md section 4 is the governing table."""
    spec = (STUDY / "rule" / "SPEC.md").read_text(encoding="utf-8")
    table = re.findall(r"^\| `([a-z0-9-]+)` \|", spec, flags=re.MULTILINE)
    assert sorted(table) == sorted(transition.CODES)


def test_matrix_expectations_use_only_registered_outcomes():
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    ns = upstream016.load()
    for cell in matrix["cells"]:
        for layer, expected in cell["expected"].items():
            if expected in ("pass", "usable", "unavailable"):
                continue
            head, _, code = expected.partition(":")
            assert code, cell["id"]
            if layer == "transition":
                assert head == "not-usable" and code in transition.CODES, cell["id"]
            else:
                assert head == "fail" and code in ns.verify_currency.CODES, cell["id"]


def test_the_registered_divergence_is_real():
    """The study's positive result, asserted structurally: the four div-* cells
    share commitment, snapshot and trust configuration, and differ only in the
    rule configuration — so their differing outcomes are the rule's doing."""
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    ids = [c["id"] for c in matrix["cells"] if c["id"].startswith("div-")]
    assert len(ids) == 4
    # Round-1 R1-12: assert the EXACT difference set, citation included.
    shared = {}
    for cid in ids:
        directory = build_fixtures.cell_directory(STUDY / "fixtures", cid)
        for name in build_fixtures.CELL_FILES:
            path = directory / name
            shared.setdefault(name, set()).add(
                score.sha256_file(path) if path.is_file() else None)
    differing = {name for name, digests in shared.items() if len(digests) > 1}
    assert differing == {"ruleconfig.json"}, differing
    assert len(shared["ruleconfig.json"]) == 4


def test_backdated_citation_is_byte_identical_to_the_honest_cell():
    """The boundary exhibit: identical bytes, so no rule over this evidence can
    separate honest reliance from a chosen-early citation."""
    matrix = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))
    assert score.identity_group_problems(matrix) == {}
    a = build_fixtures.cell_directory(STUDY / "fixtures", "div-grandfather-on-cited-support")
    b = build_fixtures.cell_directory(STUDY / "fixtures", "bnd-backdated-citation")
    for name in build_fixtures.CELL_FILES:
        assert (a / name).is_file() == (b / name).is_file(), name
        if (a / name).is_file():
            assert (a / name).read_bytes() == (b / name).read_bytes(), name


def test_preregistration_counts_are_derived_from_the_matrix():
    """Every count the preregistration states is recomputed from MATRIX.json.

    Round-2 R2-2 disposed of stale counts by claiming this test existed. It did
    not, and by round 3 the document had drifted again in two places at once:
    §1a said 18 cells against a 21-cell matrix, and §4 said five registered
    absences against six. The preregistration is pinned at the freeze and is the
    governing document, so a count in it is a registered claim like any other.
    """
    text = (STUDY / "PREREGISTRATION.md").read_text(encoding="utf-8")
    cells = json.loads((STUDY / "harness" / "MATRIX.json").read_text(encoding="utf-8"))["cells"]

    def count(predicate):
        return sum(1 for cell in cells if predicate(cell))

    def stated(pattern):
        found = re.findall(pattern, text)
        assert found, "the preregistration no longer states: " + pattern
        return [int(value) for value in found]

    control_gates = [c for c in cells if c["role"] == "control-gate"]
    expected = {
        r"`harness/MATRIX\.json`, (\d+) cells": len(cells),
        r"\n(\d+) cells \(matrixVersion": len(cells),
        r"(\d+) positive controls": sum(1 for c in control_gates
                                        if not c["id"].startswith("neg-")),
        r"(\d+) negative controls": sum(1 for c in control_gates
                                        if c["id"].startswith("neg-")),
        r"(\d+)\s*\n?endpoints across divergence": count(lambda c: c["role"] == "endpoint"),
        r"(\d+) descriptive row": count(lambda c: c["role"] == "descriptive"),
        r"(\d+) demonstration": count(lambda c: c["role"] == "demonstration"),
    }
    for pattern, actual in expected.items():
        for value in stated(pattern):
            assert value == actual, "%s: preregistration says %d, matrix has %d" % (
                pattern, value, actual)

    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
             7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    # Round-5 finding 6 and round-6 finding 6: the docstring claims EVERY count,
    # so every count stated anywhere in the document is derived here, not only
    # the cell table's — both statements of the rule count, and the number of
    # companion artifacts pinned alongside this document.
    assert len(transition.RULES) == 3
    assert "one of %s registered rules" % words[len(transition.RULES)] in text
    assert "The %s rules are a **construct**" % words[len(transition.RULES)] in text
    for rule in transition.RULES:
        assert "`%s`" % rule in text, rule

    companions = [relative for member, relative in score.PINNED_DIGEST_MEMBERS
                  if member not in ("preregistration", "studyManifest")]
    assert "%s companion artifacts are registered" % words[len(companions)].capitalize() in text
    for relative in companions:
        assert "(%s)" % relative in text, relative

    absences = count(lambda c: c.get("registeredAbsences"))
    assert "names the %s cells that deliberately retain no citation" % words[absences] in text

    # Round-4 blocker 6: the totals were derived but the prose's breakdown of
    # the negative controls was not, so editing "two never-bound-digest
    # controls" passed. Each named sub-count is derived too.
    digest_controls = count(lambda c: c["id"].startswith("neg-never-supported-")
                            and not c["id"].endswith("-version"))
    version_controls = count(lambda c: c["id"] == "neg-never-supported-version")
    assert "%s never-bound-digest controls" % words[digest_controls] in text
    assert "%s\nnever-bound-version control" % words[version_controls] in text or \
        "%s never-bound-version control" % words[version_controls] in text
    for phrase, present in (("an unregistered rule", "neg-ruleconfig-malformed"),
                            ("an unauthenticated snapshot", "neg-currency-unauthenticated")):
        assert phrase in text and any(c["id"] == present for c in cells), phrase
    assert all(c["registeredAbsences"] == ["citation"]
               for c in cells if c.get("registeredAbsences")), (
        "the prose says every registered absence is a citation")

    holdout = json.loads((STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(encoding="utf-8"))
    assert len(holdout["cells"]) == len(json.loads(
        (STUDY / "harness" / "MATRIX-HOLDOUT-EVIDENCE.json").read_text(encoding="utf-8"))["cells"])


def test_holdout_machinery_lands_with_the_reviewer_cells():
    """The round-2 reviewer's cells and their construction machinery land
    together and are NEVER executed before the freeze (the 014/016/017 regime).

    This test asserts everything about the stratum that can be checked without
    constructing a single byte: every registered cell has a hook, every hook
    refuses outside a valid post-freeze context, and every cell carries exactly
    this study's structured-evidence fields. Whether a hook builds what its
    construction text says is adjudicated by the first execution — which is the
    whole of what the stratum is for — and a hook that fails there is recorded
    as `harness-error`, not silently dropped.
    """
    import score
    holdout = json.loads((STUDY / "harness" / "MATRIX-HOLDOUT.json").read_text(encoding="utf-8"))
    assert holdout["reviewer"], "the stratum must carry its reviewer attribution"
    ids = [cell["id"] for cell in holdout["cells"]]
    assert ids == ["h%02d" % n for n in range(1, 11)]
    assert not score.holdout_schema_problems(holdout)

    # every cell is constructible in principle, and nothing is constructible now
    assert set(build_fixtures.HOLDOUT_HOOKS) == set(ids)
    for cell_id in ids:
        with pytest.raises(build_fixtures.HoldoutRefused):
            build_fixtures.HOLDOUT_HOOKS[cell_id](None)
    with pytest.raises(build_fixtures.HoldoutRefused):
        build_fixtures.construct_holdout(None, STUDY / "fixtures", holdout["cells"])

    # the structured expectations are complete, separate, and this study's
    evidence = score.holdout_evidence_expectations()
    assert not score.holdout_evidence_problems(holdout, evidence)
    assert set(evidence) == set(ids)
    for cell in holdout["cells"]:
        assert set(cell["expected"]) == {"currency", "transition"}
        assert "expectedRuleEvidence" not in cell, (
            "structured expectations belong in MATRIX-HOLDOUT-EVIDENCE.json so the "
            "reviewer's block stays byte-for-byte as authored")


def test_holdout_refusal_precedes_any_upstream_load_or_write(tmp_path, monkeypatch):
    """Round-4 blocker 6: refusing eventually is not the property.

    The bypass test asserts only that `HoldoutRefused` is raised in the end; a
    route that derived the authority key, folded a registry and *then* refused
    would satisfy it while having already done the work the gate exists to
    prevent. Here the upstream loader is replaced by a tripwire, so any route
    that touches it before validating fails loudly.

    Scope, stated exactly (round-6 finding 5, which caught this test claiming
    "any key or payload"): what is proved is that no route loads the pinned
    upstream and no route writes a file before refusing. Pure in-memory work
    with no upstream and no write — assembling a commitment blob, say — is NOT
    detected here, and no registry byte can be produced that way, since every
    key and history comes from the upstream this tripwire guards.
    """
    touched = []

    def tripwire(*arguments, **keywords):
        touched.append(True)
        raise AssertionError("the upstream was loaded before the context was validated")

    monkeypatch.setattr(build_fixtures.upstream016, "load", tripwire)
    monkeypatch.chdir(tmp_path)
    for name in ["_holdout_h%02d" % n for n in range(1, 11)] + ["_authority"]:
        with pytest.raises(build_fixtures.HoldoutRefused):
            getattr(build_fixtures, name)(None)
    with pytest.raises(build_fixtures.HoldoutRefused):
        build_fixtures.construct_holdout(None, tmp_path, [{"id": "h01"}])
    # round-5 finding 6: `_holdout_cell` is a holdout-producing primitive in its
    # own right and was omitted from this tripwire
    with pytest.raises(build_fixtures.HoldoutRefused):
        build_fixtures._holdout_cell(None, None, None, [], commitment=b"{}",
                                     rule="stop-at-retirement")
    # round-6 finding 5: the gated WRAPPERS in HOLDOUT_HOOKS are the routes the
    # scorer actually calls, and none of them was exercised here
    for cell_id, hook in sorted(build_fixtures.HOLDOUT_HOOKS.items()):
        with pytest.raises(build_fixtures.HoldoutRefused):
            hook(None)
    assert not touched
    # and nothing was written anywhere under the working directory
    assert not [p for p in tmp_path.rglob("*") if p.is_file()]


def test_no_holdout_route_constructs_bytes_without_a_context():
    """Round-3 blocker 5: the gate must sit below every route, not only on the
    HOLDOUT_HOOKS mapping. `_gated` wrapped the mapping, so an importer could
    call `_holdout_h01(None)` directly and build real registry bytes before the
    freeze. Every raw constructor and both innermost primitives are checked."""
    routes = ["_holdout_h%02d" % n for n in range(1, 11)]
    for name in routes:
        with pytest.raises(build_fixtures.HoldoutRefused):
            getattr(build_fixtures, name)(None)
    with pytest.raises(build_fixtures.HoldoutRefused):
        build_fixtures._authority(None)
    with pytest.raises(build_fixtures.HoldoutRefused):
        build_fixtures._holdout_cell(None, None, None, [], commitment=b"{}",
                                     rule="stop-at-retirement")

    # and no module-level route escapes the audit: every callable whose name
    # marks it as holdout machinery must take a context as its first argument
    import inspect
    for name, value in vars(build_fixtures).items():
        if name.startswith(("_holdout", "construct_holdout")) and callable(value):
            first = list(inspect.signature(value).parameters)[:1]
            assert first and first[0] == "context", (
                "%s does not take a context as its first parameter" % name)


def test_holdout_call_sites_bind_statically():
    """Every holdout call site must bind against its callee's signature.

    The stratum is never executed before the freeze, so an arity error inside a
    hook is invisible to every other test — the context gate raises first and
    hides it. `_holdout_h03` really did pass `registry` where `context` belongs;
    at the attempt that cell would have come back `harness-error` and the whole
    holdout would have reported inconclusive. This binds each call statically,
    without constructing anything.
    """
    import ast
    import inspect

    source = (STUDY / "harness" / "build_fixtures.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    # Round-4 blocker 6: the first version of this audit listed callees by hand
    # and so skipped hook-to-hook calls (`_holdout_h02` → `_holdout_h01`,
    # `_holdout_h05`/`_holdout_h06`/`_holdout_h07` → `_holdout_h04`) — exactly
    # the calls most likely to drift. Every holdout callable is now in scope.
    callees = {"_holdout_cell", "_authority", "_require_context", "write_cell",
               "commitment_bytes", "event", "construct_holdout",
               "registered_authority_label", "holdout_context_problems"}
    callees |= {name for name in vars(build_fixtures)
                if name.startswith("_holdout") and callable(getattr(build_fixtures, name))}
    for hook in ("_holdout_h%02d" % n for n in range(1, 11)):
        assert hook in callees, hook
    checked = 0
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef)
                and (node.name.startswith(("_holdout", "_gated"))
                     or node.name in ("construct_holdout", "gated_hook", "_authority"))):
            continue
        for call in ast.walk(node):
            if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)):
                continue
            name = call.func.id
            if name not in callees:
                continue
            signature = inspect.signature(getattr(build_fixtures, name))
            positional = [object()] * len(call.args)
            keywords = {kw.arg: object() for kw in call.keywords if kw.arg}
            try:
                signature.bind(*positional, **keywords)
            except TypeError as error:
                raise AssertionError("%s calls %s incompatibly: %s"
                                     % (node.name, name, error))
            # The context must be threaded, never a stray local and never a
            # literal. Round-5 finding 6: restricting this to three inner
            # functions let `_holdout_h05` call `_holdout_h04(None, ...)` and
            # still bind, with the gate hiding it until the attempt. The rule
            # is now derived from the callee: anything whose first parameter is
            # `context` must receive the caller's `context` by name.
            takes_context = list(signature.parameters)[:1] == ["context"]
            if takes_context:
                # round-6 finding 5: the identity check only fired when a
                # POSITIONAL argument existed, so `_holdout_h04(context=None,
                # cited=5)` passed. The context may arrive either way.
                keyword = [kw.value for kw in call.keywords if kw.arg == "context"]
                supplied = (call.args[:1] or keyword)
                assert supplied, "%s calls %s with no context at all" % (node.name, name)
                first = supplied[0]
                assert isinstance(first, ast.Name) and first.id == "context", (
                    "%s passes %r as the context of %s - every holdout route "
                    "must thread the caller's context"
                    % (node.name, ast.unparse(first), name))
            checked += 1
    assert checked >= 20, "the call-site audit found almost nothing to check"

    # Dynamic dispatch is invisible to a callee-name audit — `hook(context)`
    # inside `construct_holdout` names no function. Round-6 finding 5: a literal
    # `None` there would pass everything above and stay hidden behind the gate
    # until the attempt. Inside holdout scope, no call may pass a literal at all
    # where a context belongs, so the constant is banned outright.
    banned = 0
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef)
                and (node.name.startswith(("_holdout", "_gated"))
                     or node.name in ("construct_holdout", "gated_hook", "_authority"))):
            continue
        for call in ast.walk(node):
            if not isinstance(call, ast.Call):
                continue
            for argument in list(call.args) + [kw.value for kw in call.keywords]:
                assert not (isinstance(argument, ast.Constant) and argument.value is None), (
                    "%s passes a literal None to %s; inside holdout scope a "
                    "context must always be threaded by name"
                    % (node.name, ast.unparse(call.func)))
                banned += 1
    assert banned, "the literal-None audit inspected nothing"


def test_holdout_construction_is_gated_on_every_freeze_pin(tmp_path, monkeypatch):
    """The stratum executes only after the freeze. Each pin is nulled in turn —
    in a temporary registry, so this holds identically before and after the
    freeze — and the gate must refuse naming that pin. A gate that omits one of
    the pins it added is the 017 round-2 class of defect.
    """
    import hashlib

    def sha256_file(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    real = json.loads((STUDY / "harness" / "PINS.json").read_text(encoding="utf-8"))
    filled = {"sha256": "f" * 64}
    # Round-4 blocker 6: naming the pins via score.FREEZE_PINS makes this test
    # shrink silently if a pin is ever dropped from that tuple. The six are
    # asserted literally, so removing one fails here rather than going unnoticed.
    assert score.FREEZE_PINS == ("preregistration", "matrix", "matrixHoldout",
                                 "matrixHoldoutEvidence", "ruleSpec", "studyManifest")
    for member in score.FREEZE_PINS:
        assert member in real, "a freeze pin the gate names is missing from PINS.json"

    def context_for(pins):
        raw = (json.dumps(pins, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        pins_path = tmp_path / "PINS.json"
        pins_path.write_bytes(raw)
        monkeypatch.setattr(build_fixtures, "PINS_PATH", pins_path)
        return build_fixtures.HoldoutAttemptContext(
            attempt_root=str(tmp_path),
            pins_raw_sha256=hashlib.sha256(raw).hexdigest(),
            preregistration_sha256=sha256_file(STUDY / "PREREGISTRATION.md"),
            matrix_holdout_sha256=sha256_file(STUDY / "harness" / "MATRIX-HOLDOUT.json"),
            matrix_holdout_evidence_sha256=sha256_file(
                STUDY / "harness" / "MATRIX-HOLDOUT-EVIDENCE.json"))

    # all six filled: the gate has nothing to say about the pins
    everything = dict(real, **{member: filled for member in score.FREEZE_PINS})
    assert not build_fixtures.holdout_context_problems(context_for(everything))

    for member in score.FREEZE_PINS:
        one_null = dict(everything, **{member: {"sha256": None}})
        problems = build_fixtures.holdout_context_problems(context_for(one_null))
        assert any(member in problem for problem in problems), (
            "the gate does not refuse while %s is null" % member)

    # a context whose digests disagree with the live files is refused
    for field in ("pins_raw_sha256", "preregistration_sha256",
                  "matrix_holdout_sha256", "matrix_holdout_evidence_sha256"):
        context = context_for(everything)
        tampered = dataclasses.replace(context, **{field: "0" * 64})
        assert build_fixtures.holdout_context_problems(tampered)


def test_transition_refuses_over_an_unauthenticated_snapshot():
    """Round-1 R1-1: a rule is evaluated only over an authenticated membership
    answer, and the composed verdict can never be usable without one."""
    import transition
    directory = build_fixtures.cell_directory(STUDY / "fixtures",
                                              "neg-currency-unauthenticated")
    outcome = run_verify.verify_cell(directory)
    assert outcome["currency"]["outcome"].startswith("fail:snapshot-")
    assert outcome["transition"]["outcome"] == "unavailable"
    assert outcome["combined"] != "usable"
    for bad in ("unavailable", "fail:snapshot-signature-invalid", "fail:binding-rebound"):
        assert bad not in transition.ADJUDICABLE_CURRENCY


def test_membership_comes_from_the_pinned_upstream_fold():
    """Round-1 R1-2: lifecycle semantics are the upstream's by construction.

    2.0.0 is retired at position 4 and reinstated at 5, and a never-bound
    digest must never be supported at any position — the two cases the
    hand-rolled tracker got wrong.
    """
    import transition
    ns = upstream016.load(build=True)
    registry = ns.checkpoint
    authority = registry.private_key("study-018/currency-authority/1")
    history = registry.build_registry(authority, [
        build_fixtures.event("add", "1.0.0", build_fixtures.DIGEST_A),
        build_fixtures.event("add", "2.0.0", build_fixtures.DIGEST_B),
        build_fixtures.event("retire", "1.0.0"),
        build_fixtures.event("retire", "2.0.0"),
        build_fixtures.event("reinstate", "2.0.0")])
    payloads = [record["checkpoint"] for record in history]
    fold = ns.verify_currency.fold_supported
    series = build_fixtures.SERIES_ID
    real = ("2.0.0", build_fixtures.DIGEST_B)
    never_bound = ("2.0.0", "sha256:" + "b" * 64)
    assert transition._supported_at(payloads, series, real, 2, fold) is True
    assert transition._supported_at(payloads, series, real, 4, fold) is False
    assert transition._supported_at(payloads, series, real, 5, fold) is True
    for position in range(1, 6):
        assert transition._supported_at(payloads, series, never_bound, position, fold) is False
    assert transition._left_position(payloads, series, real, fold) == 4
