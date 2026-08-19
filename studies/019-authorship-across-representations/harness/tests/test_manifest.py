"""ADR 0004's exclusions, asserted so a future widening fails the suite.

ADR 0004 decides that a study's manifest covers what must not change, that a
file whose purpose is to be appended to after the freeze is not that, and that
such files are excluded **by construction, in a named constant, with a harness
test asserting the exclusion**. This is that test. It has real power here rather
than being a guard over an absent file: every named file EXISTS in this study
today, so an edit that widened the covered set would cover them and these
assertions would fail.

FOUR APPENDABLE FILES, not two. `DEVIATIONS.md` and `README.md` are ADR 0004's
own examples; **`PREREG-REVIEW.md` is round-3 finding R3-1** and is the same
shape of file — it grows by one disposition table per review round, so covering
it made every round's own dispositions stale the committed manifest. It did that
three rounds running, including in a response that reported a green suite while
three enforcement tests were red. Round 2 answered with a procedure and a second
failing test; the third recurrence is the evidence that a procedure which must be
remembered every round is not a safeguard. So it leaves the covered set by named
constant, like the other two, and `test_the_review_record_cannot_be_re_covered`
below is what makes re-covering it fail the suite rather than pass quietly.

`harness/ADVISORIES.md` is the fourth, and it is round 9's ratified scope
ruling made structural: `PREREGISTRATION.md` §4b registers a review-support
apparatus whose findings are RECORDED rather than gated, and the register that
records them grows by an entry per such finding for as long as that apparatus is
maintained — after the freeze included. Covering it would make the first entry
break the anchor, which is the failure the other three exist to prevent.

The last exclusion — `harness/PINS.json` — is Study 014's linear-anchor rule,
and it is asserted with the same idiom: the manifest must not cover the registry
that pins the manifest, or the anchor cannot be initialized without a SHA-256
fixed point.
"""
import json
import os
import pathlib

import pytest

import make_manifest

# The files ADR 0004 calls appendable in this study, each of which exists today.
APPENDABLE = ("DEVIATIONS.md", "README.md", "PREREG-REVIEW.md",
              "harness/ADVISORIES.md")


def test_the_adr_0004_exclusions_are_named_constants_carrying_their_reason():
    """A named constant is the decision's requirement; the REASON travelling
    with the name is what a later reader needs in order not to argue past it."""
    for name in APPENDABLE:
        assert name in make_manifest.EXCLUDED_DOCUMENTS, name
        reason = make_manifest.EXCLUDED_DOCUMENTS[name]
        assert isinstance(reason, str) and reason.strip(), name
        assert "ADR 0004" in reason, (
            "%s is excluded under ADR 0004 and its reason must say so" % name)


def test_no_appendable_file_is_covered_and_all_of_them_exist(study):
    """The exclusion is asserted against files that are really there: a guard
    over an absent file passes for the wrong reason."""
    entries = make_manifest.manifest_entries()
    for name in APPENDABLE:
        assert os.path.isfile(os.path.join(study, name)), name
        assert name not in entries


def test_the_review_record_cannot_be_re_covered(study):
    """ROUND-3 R3-1, as the assertion that bites.

    Covering `PREREG-REVIEW.md` again — by adding it back to
    `REGISTERED_DOCUMENTS`, by dropping it from `EXCLUDED_DOCUMENTS`, or by a
    widened glob that sweeps it in — must FAIL HERE, because the alternative is
    what happened three rounds running: the record is appended to, the committed
    manifest silently stops describing the tree, and the suite of record is
    reported green while it is red."""
    assert "PREREG-REVIEW.md" in make_manifest.EXCLUDED_DOCUMENTS
    assert "PREREG-REVIEW.md" not in make_manifest.REGISTERED_DOCUMENTS
    assert "PREREG-REVIEW.md" not in make_manifest.manifest_entries()
    committed = os.path.join(study, "harness", "STUDY-MANIFEST.sha256")
    if os.path.isfile(committed):
        with open(committed, encoding="utf-8") as handle:
            listed = [line.split("  ", 1)[1] for line in
                      handle.read().splitlines() if line.strip()]
        assert "PREREG-REVIEW.md" not in listed, (
            "the committed manifest still covers the review record; regenerate "
            "it with harness/make_manifest.py")
    # …and the exclusion is not a silent drop: `_excluded()` is the one place
    # that decides, so a path in the constant is out however it was reached.
    assert make_manifest._excluded("PREREG-REVIEW.md")


def test_the_advisory_register_is_appendable_and_carries_what_it_records(study):
    """ROUND-9, the RATIFIED SCOPE RULING, as the assertion that bites.

    §4b registers a review-support apparatus whose findings are recorded rather
    than gated. The register that records them is worth nothing if it can be
    covered (the first advisory then breaks the anchor, exactly as the review
    record did three rounds running) or silently emptied — so both directions are
    asserted here: it is excluded by named constant, it is not in the covered
    set, and it still carries every advisory round 9 put in it, each with the
    file cite that makes it findable."""
    assert "harness/ADVISORIES.md" in make_manifest.EXCLUDED_DOCUMENTS
    assert "harness/ADVISORIES.md" not in make_manifest.REGISTERED_DOCUMENTS
    assert "harness/ADVISORIES.md" not in make_manifest.manifest_entries()
    assert make_manifest._excluded("harness/ADVISORIES.md")
    path = pathlib.Path(study) / "harness" / "ADVISORIES.md"
    text = path.read_text(encoding="utf-8")
    for advisory in ("R9-3", "R9-5", "R9-6", "R9-7"):
        assert advisory in text, (
            "the advisory register must still carry %s: an entry that is "
            "recorded and then deleted was never recorded" % advisory)
    # a recorded advisory is not a downgraded one — the severity the reviewer
    # returned travels with it, and so does §4b, which is what makes the
    # recording a registered decision rather than a preference
    assert text.count("MAJOR") >= 3 and "MINOR" in text
    assert "§4b" in text
    # and it says which surface it may concern, so an advisory against the
    # REGISTERED surface cannot be filed here instead of being answered
    assert "review-support" in text


def test_the_registry_is_not_covered_by_the_manifest_it_pins():
    assert "harness/PINS.json" in make_manifest.EXCLUDED_DOCUMENTS
    assert "harness/PINS.json" not in make_manifest.manifest_entries()


def test_the_manifest_does_not_cover_itself():
    assert "harness/STUDY-MANIFEST.sha256" not in make_manifest.manifest_entries()


def test_no_registered_document_is_also_excluded():
    """A path in both constants would make the covered set depend on which
    constant a future reader believed."""
    overlap = set(make_manifest.REGISTERED_DOCUMENTS) & \
        (set(make_manifest.EXCLUDED_DOCUMENTS)
         | set(make_manifest.EXCLUDED_ARTIFACTS))
    assert overlap == set()


def test_every_harness_source_and_the_ports_table_are_covered():
    entries = make_manifest.manifest_entries()
    for name in ("harness/batch.py", "harness/integrity.py",
                 "harness/make_manifest.py", "harness/transcript_check.py",
                 "harness/authoring_call.sh", "harness/PORTS.md",
                 "harness/score.py", "harness/tests/test_manifest.py"):
        assert name in entries, name


def test_the_scorers_own_package_is_covered_module_for_module(study):
    """SCAFFOLD item M1, point 4: `harness/e4lib/` decides every published rate,
    and reviewed sources outside the exact-set manifest are the hole ADR 0004's
    manifest exists to close.

    Asserted against the DIRECTORY rather than against a list, so a module added
    to the package and not to the manifest fails here rather than entering the
    covered set unnoticed."""
    package = pathlib.Path(study) / "harness" / "e4lib"
    on_disk = sorted("harness/e4lib/" + path.name
                     for path in package.glob("*.py"))
    assert on_disk, "the scorer package is empty; this assertion would be vacuous"
    entries = make_manifest.manifest_entries()
    assert [name for name in entries if name.startswith("harness/e4lib/")] \
        == on_disk


def test_pending_registered_documents_are_named_and_not_covered():
    """Pre-freeze, several registered documents do not exist. They must be
    reported by name rather than silently dropped from the registered set, and
    `--freeze` must refuse while any is pending.

    ROUND-5 FINDING R5-6 widens the list from documents to registered payload
    SETS, so the membership check is two-sided: every pending name is either a
    registered document or a registered set's glob, and nothing else. ROUND-7
    FINDING R7-8 widens it once more, to the freeze PINS whose source this
    module can compute — the reviewer-set digest — because a ceremony that can
    complete with that pin null is the gap the finding names."""
    pending = make_manifest.pending_documents()
    globs = {"%s/%s" % (directory, pattern)
             for directory, pattern in make_manifest.REGISTERED_PAYLOAD_SETS}
    pins = {dotted for dotted, _source, _compute
            in make_manifest.PENDING_PIN_SOURCES}
    entries = make_manifest.manifest_entries()
    for name in pending:
        if name in make_manifest.REGISTERED_DOCUMENTS:
            assert name not in entries
            continue
        if name.split(" (")[0].split(" records")[0] in pins:
            assert name in make_manifest.pending_pins(), name
            continue
        glob, _, reason = name.partition(" (")
        assert glob in globs, name
        assert reason.rstrip(")") in ("directory absent", "no file matches"), name
        assert not [entry for entry in entries
                    if entry.startswith(glob.split("*")[0])], name
    if pending:
        assert make_manifest.main(["--freeze"]) == 1


def test_the_committed_manifest_describes_the_tree_it_covers():
    assert make_manifest.manifest_problems() == []


# --- ROUND-1 FINDING R1-9: every scorer input carries a per-file hash --------

def test_every_byte_the_scorer_executes_is_a_registered_document_or_payload():
    """The finding, verbatim: the manifest "covers the two top-level mutant
    manifests and reference Markdown, but not `mutants/jps/*.json`,
    `mutants/rego/*.rego`, `reference/refA/pack.json`, `reference/refB/policy.rego`,
    or the off-gold certificate — the actual scorer inputs".

    All five are registered now. The three FILES are registered documents, so
    `--freeze` refuses while any is absent; the two payload DIRECTORIES are exact
    one-level globs, so every mutant carries its own hash rather than being
    covered by a manifest that names its directory."""
    registered = set(make_manifest.REGISTERED_DOCUMENTS)
    for name in ("reference/refA/pack.json", "reference/refB/policy.rego",
                 "controls/off-gold-equivalence.json",
                 "gold/GOLD.json", "mutants/MANIFEST-jps.json",
                 "mutants/MANIFEST-rego.json"):
        assert name in registered, name
    payload_sets = dict()
    for directory, pattern in make_manifest.REGISTERED_PAYLOAD_SETS:
        payload_sets.setdefault(directory, []).append(pattern)
    assert payload_sets["mutants/jps"] == ["*.json"]
    assert payload_sets["mutants/rego"] == ["*.rego"]
    assert sorted(payload_sets["controls/reviewer-mutants"]) == \
        ["*.json", "*.rego"]


def test_a_payload_set_that_exists_is_covered_file_by_file(study, tmp_path):
    """The glob is exact rather than a directory name: an added payload is as
    loud as a deleted one, which is the only property that makes a per-file
    hash worth having."""
    import hashlib
    root = pathlib.Path(study) / "mutants" / "jps"
    if not root.is_dir():
        # Pre-freeze the payload directory does not exist. The registered set
        # still names it, and a directory that is not there contributes nothing
        # to `manifest_entries()` and is not fabricated — asserted rather than
        # assumed. ROUND-5 FINDING R5-6: contributing nothing is the right rule
        # HERE and the wrong one at the freeze gate, so the absence is asserted
        # to be PENDING in the same breath, and the two tests below are what
        # make the freeze refuse it.
        assert not [name for name in make_manifest.manifest_entries()
                    if name.startswith("mutants/jps/")]
        assert any(name.startswith("mutants/jps/*.json")
                   for name in make_manifest.pending_documents()), (
            "an absent registered payload set must be PENDING, not silently "
            "empty: %s" % make_manifest.pending_documents())
        return
    on_disk = sorted("mutants/jps/" + path.name for path in root.glob("*.json"))
    entries = make_manifest.manifest_entries()
    assert [name for name in entries if name.startswith("mutants/jps/")] == \
        on_disk
    committed = {}
    manifest = pathlib.Path(study) / "harness" / "STUDY-MANIFEST.sha256"
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, _, name = line.partition("  ")
        committed[name] = digest
    for name in on_disk:
        payload = (pathlib.Path(study) / name).read_bytes()
        assert committed[name] == hashlib.sha256(payload).hexdigest(), name


# --- ROUND-5 FINDING R5-6: an absent payload SET blocks the freeze -----------

_SCRATCH_JPS = ("m-a-001", "m-a-002")
_SCRATCH_REGO = ("m-b-001.rego", "m-b-002.rego")


# ROUND-8 FINDING R8-2 AND R8-8: the scratch tree is a REHEARSAL of the freeze,
# so it must satisfy the freeze's validators and not only its filename checks.
#
# The old scratch tree wrote `scratch gold/GOLD.json` into the gold suite and a
# two-record sealed manifest with no `language`, no `sha256` and `{}` payloads —
# and expected `--freeze` to succeed. That expectation is exactly what R8-2
# names: it memorialised the bypass, because the loader that would have refused
# the set was never called. A scratch tree that could not survive the real gates
# proves nothing about them, so it is built to survive them.
_SCRATCH_SEALED = (("rm-jps-01", "jps", ".json"),
                   ("rm-jps-02", "jps", ".json"),
                   ("rm-jps-03", "jps", ".json"),
                   ("rm-rego-01", "rego", ".rego"),
                   ("rm-rego-02", "rego", ".rego"),
                   ("rm-rego-03", "rego", ".rego"))

# A minimal canonical grid in the registered shape: decimal strings at the
# registered fixed scale, JSON null for an omitted input, sanctions always
# present. `harness/grid_gate.py` runs over it at the scratch freeze exactly as
# it runs over `design/gold/gold.json` here and `gold/GOLD.json` at the freeze.
_SCRATCH_GRID = {
    "goldVersion": "scratch",
    "rows": [
        {"id": "g-1",
         "inputs": {"risk": "20", "spend": "50000.00", "sanctions": "CLEAR",
                    "country": "LOW", "newVendor": "no", "critical": "no",
                    "prior": "no", "finEvidence": "present",
                    "insurance": "present"}},
        {"id": "g-2",
         "inputs": {"risk": None, "spend": "2000000.00", "sanctions": "MATCH",
                    "country": None, "newVendor": None, "critical": None,
                    "prior": None, "finEvidence": "present",
                    "insurance": None}},
    ],
}


def _scratch_study(root):
    """A tree with every registered document present and nothing else, so a
    freeze over it turns on exactly the payload sets.

    ROUND-6 FINDING R6-5: the two mutant MANIFESTs are written as REAL manifests
    — arm A a list of records keyed by `id`, arm B a mapping with a `mutants`
    list keyed by `file`, which is what `e4lib/e4.py` reads — because the freeze
    gate now derives the expected payload set from them. ROUND-8 FINDING R8-8:
    and `gold/GOLD.json` is a REAL canonical grid, because the freeze now runs
    the registered grid assertion over it."""
    import json
    for name in make_manifest.REGISTERED_DOCUMENTS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("scratch %s\n" % name, encoding="utf-8")
    (root / "mutants" / "MANIFEST-jps.json").write_text(
        json.dumps([{"id": name, "validates": True} for name in _SCRATCH_JPS]),
        encoding="utf-8")
    (root / "mutants" / "MANIFEST-rego.json").write_text(
        json.dumps({"mutants": [{"id": name.split(".")[0], "file": name,
                                 "status": "valid"} for name in _SCRATCH_REGO]}),
        encoding="utf-8")
    (root / "gold" / "GOLD.json").write_text(json.dumps(_SCRATCH_GRID),
                                             encoding="utf-8")
    (root / "harness").mkdir(parents=True, exist_ok=True)
    return root


def _fill_payloads(root):
    """Exactly the payloads the scratch manifests name — including the SEALED
    REVIEWER SET, which ROUND-7 FINDING R7-8 brought inside the closure and
    ROUND-8 FINDING R8-2 brought inside the LOADER: its manifest is the shape
    `e4lib/reviewer.py` validates, with the registered cardinality, both
    languages, the registered `rm-<language>-NN.<ext>` filenames and every
    payload's real digest."""
    for name in _SCRATCH_JPS:
        _fill(root, "mutants/jps", "*.json", name + ".json")
    for name in _SCRATCH_REGO:
        _fill(root, "mutants/rego", "*.rego", name)
    _write_sealed_set(root)


def _write_sealed_set(root, records=_SCRATCH_SEALED):
    """The sealed set and its manifest, digests included, so `load()` passes."""
    import hashlib
    import json
    sealed = root / "controls" / "reviewer-mutants"
    sealed.mkdir(parents=True, exist_ok=True)
    for path in sealed.iterdir():
        if path.is_file():
            path.unlink()
    mutants = []
    for identity, language, extension in records:
        name = identity + extension
        body = ("{}\n" if extension == ".json"
                else "package study.mutant\n").encode("utf-8")
        (sealed / name).write_bytes(body)
        mutants.append({"id": identity, "language": language, "file": name,
                        "sha256": hashlib.sha256(body).hexdigest()})
    (sealed / "MANIFEST.json").write_text(
        json.dumps({"reviewerSetVersion": 1, "mutants": mutants}),
        encoding="utf-8")


def _fill(root, directory, pattern, name):
    (root / directory).mkdir(parents=True, exist_ok=True)
    (root / directory / name).write_text("{}\n", encoding="utf-8")


def test_the_freeze_refuses_a_registered_payload_set_that_is_absent_or_empty(
        tmp_path, monkeypatch):
    """R5-6, the residual the reviewer ran: with every `REGISTERED_DOCUMENTS`
    file present and both mutant payload directories absent,
    `pending_documents()` returned `[]`, `--freeze` returned success, and the
    manifest it wrote contained zero mutant payload entries. The scorer refuses
    the absence at ATTEMPT time (`score.py`), which is after the freeze the gate
    exists to hold.

    Three states, and the middle one is the one a directory-name check misses:
    root absent, root present and empty, root present and filled."""
    root = _scratch_study(tmp_path / "study")
    monkeypatch.setattr(make_manifest, "STUDY", root)
    monkeypatch.setattr(make_manifest, "MANIFEST_PATH",
                        root / "harness" / "STUDY-MANIFEST.sha256")

    assert make_manifest.pending_documents(root) != [], (
        "both payload roots are absent and the freeze gate must say so")
    assert make_manifest.main(["--freeze"]) == 1
    assert not (root / "harness" / "STUDY-MANIFEST.sha256").exists(), (
        "a refused freeze must not write a manifest")

    for directory, pattern in make_manifest.REGISTERED_PAYLOAD_SETS:
        (root / directory).mkdir(parents=True, exist_ok=True)
    reasons = dict(make_manifest.pending_payload_sets(root))
    assert reasons and set(reasons.values()) == {"no file matches"}, reasons
    assert make_manifest.main(["--freeze"]) == 1, (
        "an EMPTY registered payload set is as pending as an absent one")

    _fill_payloads(root)
    assert make_manifest.pending_payload_sets(root) == []
    assert make_manifest.pending_documents(root) == []
    assert make_manifest.main(["--freeze"]) == 0
    written = (root / "harness" / "STUDY-MANIFEST.sha256").read_text(
        encoding="utf-8")
    for directory, _pattern in make_manifest.REGISTERED_PAYLOAD_SETS:
        assert directory + "/" in written, (
            "the frozen manifest must carry the %s payloads file by file"
            % directory)


def test_one_sentinel_per_payload_glob_does_not_close_the_freeze(
        tmp_path, monkeypatch):
    """ROUND-6 FINDING R6-5, the reviewer's construction exactly: R5-6's residual
    test deliberately wrote ONE arbitrary `{}` file per registered glob and then
    expected `--freeze` to succeed. It did — the gate asked whether the glob
    matched anything, and a tree missing every mutant but one matched.

    The same tree is built here and the freeze must refuse it, naming both
    directions: the payloads the manifests name and cannot find, and the file in
    the directory the manifests do not name. Then the closure is repaired and the
    freeze succeeds, so the refusal is closure and not obstruction."""
    root = _scratch_study(tmp_path / "study")
    monkeypatch.setattr(make_manifest, "STUDY", root)
    monkeypatch.setattr(make_manifest, "MANIFEST_PATH",
                        root / "harness" / "STUDY-MANIFEST.sha256")
    for index, (directory, pattern) in enumerate(
            make_manifest.REGISTERED_PAYLOAD_SETS):
        _fill(root, directory, pattern,
              "p%d%s" % (index, pattern.replace("*", "")))

    # R5-6's gate is satisfied by exactly this tree, which is the finding
    assert make_manifest.pending_payload_sets(root) == []
    assert make_manifest.pending_documents(root) == []

    problems = make_manifest.payload_closure_problems(root)
    assert any("does not exist" in problem for problem in problems), problems
    assert any("is not named by" in problem for problem in problems), problems
    assert make_manifest.main(["--freeze"]) == 1
    assert not (root / "harness" / "STUDY-MANIFEST.sha256").exists(), (
        "a refused freeze must not write a manifest")

    for index, (directory, pattern) in enumerate(
            make_manifest.REGISTERED_PAYLOAD_SETS):
        (root / directory / ("p%d%s" % (index, pattern.replace("*", "")))).unlink()
    _fill_payloads(root)
    assert make_manifest.payload_closure_problems(root) == []
    assert make_manifest.main(["--freeze"]) == 0

    # and closure bites in the other direction too: one extra file, one missing
    _fill(root, "mutants/jps", "*.json", "m-a-999.json")
    assert any("is not named by" in problem
               for problem in make_manifest.payload_closure_problems(root))
    (root / "mutants" / "jps" / "m-a-999.json").unlink()
    (root / "mutants" / "jps" / (_SCRATCH_JPS[0] + ".json")).unlink()
    assert any("does not exist" in problem
               for problem in make_manifest.payload_closure_problems(root))
    assert make_manifest.main(["--freeze"]) == 1


def test_the_expected_payload_names_are_the_ones_the_scorer_opens(study):
    """R6-5's binding to the scorer rather than to a convention: the filename the
    freeze expects is the filename `e4lib/e4.py` builds when it loads a mutant —
    `<id>.json` for arm A, the record's own `file` for arm B. Asserted against
    the design corpus, which carries both manifests in their real shapes."""
    import json
    design = pathlib.Path(study) / "design" / "mutants"
    arm_a = json.loads((design / "refA" / "MANIFEST.json").read_text(
        encoding="utf-8"))
    expected = sorted("%s.json" % record["id"] for record in arm_a)
    on_disk = sorted(path.name for path in (design / "refA").glob("m-a-*.json"))
    assert expected == on_disk, (
        "arm A's design payloads are exactly `<id>.json` per manifest record")
    arm_b = json.loads((design / "refB" / "MANIFEST.json").read_text(
        encoding="utf-8"))
    expected = sorted(record["file"] for record in arm_b["mutants"])
    on_disk = sorted(path.name for path in (design / "refB").glob("*.rego"))
    assert expected == on_disk, (
        "arm B's design payloads are exactly the manifest's `file` members — "
        "including the dropped mutant's, which is why closure counts every "
        "record and not only the valid ones")


# --- ROUND-7 FINDING R7-6: exactly the scorer's shape, per arm ---------------

def test_the_alternative_manifest_shape_is_a_named_refusal(tmp_path, monkeypatch):
    """R7-6, run as the reviewer described it. `_manifest_records()` accepted a
    bare LIST or `{"mutants": [...]}` for EITHER arm, so two manifests with
    their shapes SWAPPED — and payload filenames that happen to match — closed
    the freeze here and raised `E4-MISSING-MUTANT` at the attempt, which is
    after the anchor the gate exists to hold.

    Each arm's alternative shape is now a refusal that names itself, and the
    real shapes still close, so the refusal is strictness and not obstruction."""
    import json
    root = _scratch_study(tmp_path / "study")
    _fill_payloads(root)
    monkeypatch.setattr(make_manifest, "STUDY", root)
    monkeypatch.setattr(make_manifest, "MANIFEST_PATH",
                        root / "harness" / "STUDY-MANIFEST.sha256")
    assert make_manifest.payload_closure_problems(root) == []

    jps = root / "mutants" / "MANIFEST-jps.json"
    rego = root / "mutants" / "MANIFEST-rego.json"
    original_jps = jps.read_text(encoding="utf-8")
    original_rego = rego.read_text(encoding="utf-8")

    # arm A given arm B's shape: the payload names are still derivable, and the
    # scorer cannot read it, so the freeze must refuse rather than close.
    jps.write_text(json.dumps({"mutants": json.loads(original_jps)}),
                   encoding="utf-8")
    problems = make_manifest.payload_closure_problems(root)
    assert any("iterates a top-level LIST" in problem for problem in problems), \
        problems
    assert make_manifest.main(["--freeze"]) == 1
    jps.write_text(original_jps, encoding="utf-8")

    # arm B given arm A's shape
    rego.write_text(json.dumps(json.loads(original_rego)["mutants"]),
                    encoding="utf-8")
    problems = make_manifest.payload_closure_problems(root)
    assert any("top-level OBJECT's `mutants`" in problem
               for problem in problems), problems
    assert make_manifest.main(["--freeze"]) == 1
    rego.write_text(original_rego, encoding="utf-8")

    assert make_manifest.payload_closure_problems(root) == []


def test_a_non_string_payload_id_is_a_refusal_and_not_a_filename(
        tmp_path, monkeypatch):
    """R7-6's second half. A numeric JPS id renders a plausible `1.json` in
    closure and fails in the scorer, which concatenates `mutant["id"] + ".json"`.
    A path separator in the member is the same defect pointing somewhere else."""
    import json
    root = _scratch_study(tmp_path / "study")
    _fill_payloads(root)
    monkeypatch.setattr(make_manifest, "STUDY", root)
    monkeypatch.setattr(make_manifest, "MANIFEST_PATH",
                        root / "harness" / "STUDY-MANIFEST.sha256")
    jps = root / "mutants" / "MANIFEST-jps.json"
    records = json.loads(jps.read_text(encoding="utf-8"))
    for bad in (1, None, "../escape", "sub/dir.json"):
        records[0]["id"] = bad
        jps.write_text(json.dumps(records), encoding="utf-8")
        problems = make_manifest.payload_closure_problems(root)
        assert any("plain filename component" in problem
                   for problem in problems), (bad, problems)
        assert make_manifest.main(["--freeze"]) == 1


# --- ROUND-7 FINDING R7-8: the sealed reviewer set is inside the gate --------

def test_the_sealed_reviewer_set_closes_like_every_other_payload_set(
        tmp_path, monkeypatch):
    """R7-8. `controls/reviewer-mutants` is a registered payload set whose bytes
    a REGISTERED attempt executes, and exact closure was implemented only for
    the two primary mutant manifests: one arbitrary file per glob satisfied the
    gate. Three directions, each of which must refuse the freeze — a payload the
    sealed manifest names and cannot find, a file beside it the manifest does
    not name, and an absent manifest — then the repair, which must close."""
    root = _scratch_study(tmp_path / "study")
    _fill_payloads(root)
    monkeypatch.setattr(make_manifest, "STUDY", root)
    monkeypatch.setattr(make_manifest, "MANIFEST_PATH",
                        root / "harness" / "STUDY-MANIFEST.sha256")
    sealed = root / "controls" / "reviewer-mutants"
    assert make_manifest.reviewer_set_closure_problems(root) == []

    (sealed / "rm-jps-01.json").unlink()
    assert any("does not exist" in problem for problem in
               make_manifest.reviewer_set_closure_problems(root))
    assert make_manifest.main(["--freeze"]) == 1
    (sealed / "rm-jps-01.json").write_text("{}\n", encoding="utf-8")

    (sealed / "rm-extra-99.json").write_text("{}\n", encoding="utf-8")
    assert any("is not named by" in problem for problem in
               make_manifest.reviewer_set_closure_problems(root))
    assert make_manifest.main(["--freeze"]) == 1
    (sealed / "rm-extra-99.json").unlink()

    manifest = sealed / "MANIFEST.json"
    body = manifest.read_text(encoding="utf-8")
    manifest.unlink()
    assert any("does not exist" in problem for problem in
               make_manifest.reviewer_set_closure_problems(root))
    assert make_manifest.main(["--freeze"]) == 1
    manifest.write_text(body, encoding="utf-8")

    assert make_manifest.reviewer_set_closure_problems(root) == []
    assert make_manifest.main(["--freeze"]) == 0


def test_the_reviewer_set_pin_is_reported_by_the_gate_with_its_source(study):
    """R7-8's other half, over the REAL tree: the freeze runbook filled the
    other seventeen pins and claimed `REGISTERED`, because nothing said where
    this one's value comes from. The gate must name the pin AND the artifact its
    digest is taken over, and it must refuse the freeze while the two disagree."""
    import hashlib
    digest = make_manifest.reviewer_set_digest(study)
    if digest is None:
        pytest.skip("the sealed reviewer set has not landed yet")
    manifest = (pathlib.Path(study) / make_manifest.REVIEWER_SET_DIR
                / make_manifest.REVIEWER_SET_MANIFEST)
    assert digest == hashlib.sha256(manifest.read_bytes()).hexdigest()
    pending = make_manifest.pending_pins(study)
    registry = json.loads((pathlib.Path(study) / "harness" / "PINS.json")
                          .read_text(encoding="utf-8"))
    recorded = registry["reviewerMutantSet"]["sha256"]
    if recorded is None:
        assert any("reviewerMutantSet.sha256" in name and digest in name
                   and make_manifest.REVIEWER_SET_MANIFEST in name
                   for name in pending), pending
        assert all(name in make_manifest.pending_documents(study)
                   for name in pending), (
            "a pending pin must reach the freeze gate, not only this function")
    else:
        assert str(recorded).split(":")[-1] == digest
        assert not [name for name in pending
                    if "reviewerMutantSet" in name]


# --- ROUND-8 FINDING R8-2: the freeze runs the sealed set's own LOADER -------

def test_the_freeze_invokes_the_sealed_sets_loader_and_not_only_its_filenames(
        tmp_path, monkeypatch):
    """R8-2, in the reviewer's construction and three more.

    The freeze checked filenames and covered-set closure and never called
    `e4lib.reviewer.load()`, which is the component that validates the schema,
    the cardinality, the languages, the registered filenames and every payload's
    DIGEST. With the manifest digest pinned, replacing one payload with `{}`
    left `pending=[]`, closure clean and `--freeze` successful, while `load()`
    refused the same tree with `REVIEWER-SET-DIGEST`.

    Each mutation below leaves the FILENAMES exactly as the manifest names them,
    so closure stays clean and the only thing that can refuse is the loader."""
    import json
    root = _scratch_study(tmp_path / "study")
    _fill_payloads(root)
    monkeypatch.setattr(make_manifest, "STUDY", root)
    monkeypatch.setattr(make_manifest, "MANIFEST_PATH",
                        root / "harness" / "STUDY-MANIFEST.sha256")
    sealed = root / "controls" / "reviewer-mutants"
    manifest = sealed / "MANIFEST.json"
    original = manifest.read_text(encoding="utf-8")

    assert make_manifest.reviewer_load_problems(root) == []
    assert make_manifest.main(["--freeze"]) == 0
    assert make_manifest.main(["--freeze-gates"]) == 0

    # 1. the reviewer's own construction: a payload replaced by `{}`, its NAME
    #    unchanged, so closure sees nothing and the digest is wrong
    payload = sealed / "rm-jps-01.json"
    kept = payload.read_bytes()
    payload.write_bytes(b"{ }\n")
    assert make_manifest.reviewer_set_closure_problems(root) == [], (
        "the filename check cannot see this, which is the finding")
    problems = make_manifest.reviewer_load_problems(root)
    assert any("REVIEWER-SET-DIGEST" in problem for problem in problems), problems
    assert make_manifest.main(["--freeze"]) == 1
    assert make_manifest.main(["--freeze-gates"]) == 1
    # …and `--check` says it too: the gate reports through `manifest_problems()`
    # as well as refusing, because an operator who runs `--check` and sees
    # nothing has been told the set is sound.
    assert any("sealed reviewer set" in problem
               for problem in make_manifest.manifest_problems()), (
        "a loader refusal must reach --check, not only --freeze")
    payload.write_bytes(kept)
    assert make_manifest.reviewer_load_problems(root) == []

    # 2. cardinality: the registered set is 6-10 and a manifest naming five
    #    records (with its five payloads beside it) closes on filenames
    _write_sealed_set(root, _SCRATCH_SEALED[:5])
    assert make_manifest.reviewer_set_closure_problems(root) == []
    problems = make_manifest.reviewer_load_problems(root)
    assert any("5 mutants" in problem for problem in problems), problems
    assert make_manifest.main(["--freeze"]) == 1

    # 3. languages: a set that reaches one arm only, closure still clean
    _write_sealed_set(root, tuple(("rm-jps-%02d" % index, "jps", ".json")
                                  for index in range(1, 7)))
    problems = make_manifest.reviewer_load_problems(root)
    assert any("both languages" in problem for problem in problems), problems
    assert make_manifest.main(["--freeze"]) == 1

    # 4. schema: a surplus manifest member, every filename unchanged
    _write_sealed_set(root)
    body = json.loads(manifest.read_text(encoding="utf-8"))
    manifest.write_text(json.dumps(dict(body, note="unregistered")),
                        encoding="utf-8")
    problems = make_manifest.reviewer_load_problems(root)
    assert any("REVIEWER-SET-SCHEMA" in problem for problem in problems), problems
    assert make_manifest.main(["--freeze"]) == 1

    manifest.write_text(original, encoding="utf-8")
    _write_sealed_set(root)
    assert make_manifest.reviewer_load_problems(root) == []
    assert make_manifest.main(["--freeze"]) == 0


def test_the_loader_runs_over_the_real_sealed_set_and_the_gate_reports_it(study):
    """The same call over the tree that is actually being frozen. The sealed set
    is committed during the review rounds, so this has power now rather than at
    the freeze — and `--check` must report a loader refusal, not only `--freeze`."""
    if not os.path.isdir(os.path.join(study, make_manifest.REVIEWER_SET_DIR)):
        pytest.skip("the sealed reviewer set has not landed yet")
    assert make_manifest.reviewer_load_problems(study) == []
    assert [problem for problem in make_manifest.manifest_problems()
            if "sealed reviewer set" in problem] == []


# --- ROUND-8 FINDING R8-8: the registered grid assertion is in the ceremony --

def test_the_freeze_runs_the_canonical_grid_assertion(tmp_path, monkeypatch):
    """R8-8. `design/BRIEF.md` §2.3 registers a freeze-time full-grid
    `project -> re-serialize -> byte-equal` assertion with a nonzero exit, and
    `design/POLICY-DRAFT.md` registers range/form validation of the canonical
    grid at freeze. Neither ran anywhere. Two seeded grids must refuse the
    freeze here — the named scale-loss construction and a range violation — and
    the correct grid must close it."""
    import json
    root = _scratch_study(tmp_path / "study")
    _fill_payloads(root)
    monkeypatch.setattr(make_manifest, "STUDY", root)
    monkeypatch.setattr(make_manifest, "MANIFEST_PATH",
                        root / "harness" / "STUDY-MANIFEST.sha256")
    grid = root / "gold" / "GOLD.json"
    original = grid.read_text(encoding="utf-8")
    assert make_manifest.grid_assertion_problems(root) == []
    assert make_manifest.main(["--freeze"]) == 0

    # the construction the BRIEF names: `70.10` authored as `70.1`
    seeded = json.loads(original)
    seeded["rows"][0]["inputs"]["spend"] = "70.1"
    grid.write_text(json.dumps(seeded), encoding="utf-8")
    problems = make_manifest.grid_assertion_problems(root)
    assert any("scale 1" in problem for problem in problems), problems
    assert make_manifest.main(["--freeze"]) == 1
    assert make_manifest.main(["--freeze-gates"]) == 1

    # and a range violation
    seeded = json.loads(original)
    seeded["rows"][0]["inputs"]["risk"] = "120"
    grid.write_text(json.dumps(seeded), encoding="utf-8")
    problems = make_manifest.grid_assertion_problems(root)
    assert any("0..100" in problem for problem in problems), problems
    assert make_manifest.main(["--freeze"]) == 1

    grid.write_text(original, encoding="utf-8")
    assert make_manifest.grid_assertion_problems(root) == []
    assert make_manifest.main(["--freeze"]) == 0


# --- ROUND-9 FINDING R9-2: the prior attempt root refuses at the FREEZE ------

def test_the_attempt_root_this_gate_names_is_the_registered_one():
    """Not a second spelling of a registered name. `harness/batch.py` owns the
    absolute constant and `harness/score.py` takes it as `--attempt-root`; a
    gate that guarded a path only IT believed in would pass while the real root
    sat beside it."""
    import batch
    relative = os.path.relpath(batch.ATTEMPT_ROOT, batch.STUDY)
    assert relative.replace(os.sep, "/") == make_manifest.PRIMARY_ATTEMPT_ROOT


def test_a_prior_attempt_root_refuses_the_freeze(tmp_path, monkeypatch):
    """R9-2. `PREREGISTRATION.md` ("The freeze and the primary attempt") states
    the condition as one of the freeze's own: at the freeze
    `results/primary-attempt-001` must not exist. Enforcement lived in the
    SCORER, which refuses at attempt time — after the anchor — so a tree
    carrying a completed prior attempt was freezable and the sentence bound
    nothing at the moment it names.

    Four ways the root is present, and the last two are the ones a plain
    `isdir()` on the working tree calls absent: a real directory, a DANGLING
    symlink (a name that exists while `exists()` says no), an attempt root under
    a second name, and a root that is gone from disk and still in the INDEX —
    which is the state the freeze anchors, since the freeze anchors a commit."""
    import shutil
    root = _scratch_study(tmp_path / "study")
    _fill_payloads(root)
    monkeypatch.setattr(make_manifest, "STUDY", root)
    monkeypatch.setattr(make_manifest, "MANIFEST_PATH",
                        root / "harness" / "STUDY-MANIFEST.sha256")
    manifest = root / "harness" / "STUDY-MANIFEST.sha256"
    attempt = root / make_manifest.PRIMARY_ATTEMPT_ROOT

    # The tree without an attempt root freezes, so every refusal below is the
    # registered condition and nothing else. The manifest is written here rather
    # than at the end because `--check` reports "study manifest is absent" and
    # stops before it reaches any gate — so the assertion that the gate reaches
    # `--check` needs a tree that has been frozen once.
    assert make_manifest.prior_attempt_problems(root) == []
    assert make_manifest.main(["--freeze"]) == 0
    anchored = manifest.read_bytes()

    # 1. the state the finding describes: a completed attempt on disk
    attempt.mkdir(parents=True)
    (attempt / "RESULTS.json").write_text('{"decision": "R1"}', encoding="utf-8")
    problems = make_manifest.prior_attempt_problems(root)
    assert any(make_manifest.PRIMARY_ATTEMPT_ROOT in problem
               for problem in problems), problems
    assert make_manifest.main(["--freeze"]) == 1
    assert manifest.read_bytes() == anchored, (
        "a refused freeze must not rewrite the manifest")
    assert make_manifest.main(["--freeze-gates"]) == 1
    assert make_manifest.main(["--check"]) == 1
    assert any(make_manifest.PRIMARY_ATTEMPT_ROOT in problem
               for problem in make_manifest.manifest_problems()), (
        "the gate must reach --check, not only --freeze")

    # 2. a DANGLING symlink: `exists()` and `isdir()` both call this absent
    shutil.rmtree(attempt)
    attempt.symlink_to("attempt-that-moved")
    assert attempt.is_symlink() and not attempt.exists()
    assert make_manifest.prior_attempt_problems(root) != [], (
        "a name that exists is a root that exists; lexists, not exists")
    assert make_manifest.main(["--freeze"]) == 1
    attempt.unlink()

    # 3. an attempt root under a second name
    second = root / make_manifest.RESULTS_DIR / "primary-attempt-002"
    second.mkdir(parents=True)
    problems = make_manifest.prior_attempt_problems(root)
    assert any("primary-attempt-002" in problem for problem in problems), problems
    assert make_manifest.main(["--freeze"]) == 1
    shutil.rmtree(root / make_manifest.RESULTS_DIR)

    # 4. gone from disk, still in the index — the freeze anchors a COMMIT
    _git(root, "init", "-q")
    attempt.mkdir(parents=True)
    (attempt / "RESULTS.json").write_text("{}", encoding="utf-8")
    _git(root, "add", "-A", "-f")
    shutil.rmtree(root / make_manifest.RESULTS_DIR)
    assert not (root / make_manifest.RESULTS_DIR).exists()
    problems = make_manifest.prior_attempt_problems(root)
    assert any("the index carries" in problem for problem in problems), problems
    assert make_manifest.main(["--freeze"]) == 1
    assert manifest.read_bytes() == anchored

    # …and with the tree clean of it in both places, the freeze closes: the
    # refusal is the registered condition and not obstruction.
    _git(root, "rm", "-q", "-r", "--cached", make_manifest.RESULTS_DIR)
    assert make_manifest.prior_attempt_problems(root) == []
    assert make_manifest.main(["--freeze"]) == 0
    assert manifest.exists()


def test_the_freeze_fill_step_names_the_prior_attempt_condition(study):
    """R9-2's procedural half, in the idiom the payload-set test uses: the
    ceremony an operator reads must name the gate, or the runbook and the code
    disagree about what the freeze checks. Skipped once the scaffold is deleted
    at the freeze, which is its registered lifecycle."""
    path = pathlib.Path(study) / "harness" / "SCAFFOLD.md"
    if not path.is_file():
        pytest.skip("SCAFFOLD.md is deleted in the first post-freeze commit")
    text = " ".join(path.read_text(encoding="utf-8").split())
    assert make_manifest.PRIMARY_ATTEMPT_ROOT in text, (
        "the freeze-fill procedure must name the attempt root whose absence it "
        "now checks")
    assert "R9-2" in text


# --- ROUND-5 FINDING R5-1: tracked bytecode is refused, from the INDEX -------

def _git(root, *arguments):
    import subprocess
    return subprocess.run(("git",) + arguments, cwd=str(root),
                          capture_output=True, check=True)


def test_tracked_bytecode_is_a_manifest_problem_and_refuses_the_freeze(
        tmp_path, monkeypatch):
    """R5-1. The round-4 response committed `harness/__pycache__/…pyc`; the
    manifest globs `*.py` and `*.sh` and never saw it, so `manifest_problems()`
    was empty over a tree `integrity.py` refuses on the next checkout.

    The check reads the INDEX, and this test proves it does: the bytecode is
    deleted from disk and left in the index, which is the state a `git rm`
    without the disk delete — or the reverse — leaves behind, and the state a
    working-tree walk calls clean."""
    root = _scratch_study(tmp_path / "study")
    _fill_payloads(root)
    _git(root, "init", "-q")
    cache = root / "harness" / "__pycache__"
    cache.mkdir(parents=True, exist_ok=True)
    (cache / "make_manifest.cpython-312.pyc").write_bytes(b"\x00fake")
    _git(root, "add", "-A", "-f")
    monkeypatch.setattr(make_manifest, "STUDY", root)
    monkeypatch.setattr(make_manifest, "MANIFEST_PATH",
                        root / "harness" / "STUDY-MANIFEST.sha256")

    found = make_manifest.tracked_bytecode(root)
    assert found == ["harness/__pycache__/make_manifest.cpython-312.pyc"], found
    assert make_manifest.main(["--freeze"]) == 1
    assert not (root / "harness" / "STUDY-MANIFEST.sha256").exists()

    # the index is the authority, not the disk
    (cache / "make_manifest.cpython-312.pyc").unlink()
    assert make_manifest.tracked_bytecode(root) == found, (
        "deleting the file from disk while it stays in the index must not "
        "clear the finding")
    assert make_manifest.main(["--freeze"]) == 1

    _git(root, "rm", "-q", "--cached",
         "harness/__pycache__/make_manifest.cpython-312.pyc")
    assert make_manifest.tracked_bytecode(root) == []
    assert make_manifest.main(["--freeze"]) == 0


def test_the_committed_study_tree_tracks_no_bytecode(study):
    """The property over the real tree, read from `git ls-files` so it binds the
    INDEX. The retained R4-6 test asserts the WORKING TREE carries no
    `__pycache__`, which is a different claim and the one that passed while a
    `.pyc` sat in HEAD — the round-4 response wrote the cache after that test
    had already run, then committed it."""
    tracked = make_manifest.tracked_paths(study)
    if tracked is None:
        pytest.skip("the study tree is not inside a git checkout")
    offenders = sorted(name for name in tracked
                       if "__pycache__" in name.split("/")
                       or name.endswith((".pyc", ".pyo")))
    assert offenders == [], (
        "compiled bytecode is tracked under the study: %s" % offenders)
    assert [problem for problem in make_manifest.manifest_problems()
            if problem.startswith("compiled bytecode")] == []


def test_the_freeze_fill_step_names_every_registered_payload_set(study):
    """R5-6's procedural half. The gate is the code above; the SCAFFOLD step an
    operator reads must name the same things, or the two disagree about what the
    freeze is. It listed the top-level mutant MANIFESTs and not the payload trees
    they point at. Skipped once the scaffold is deleted at the freeze, which is
    its registered lifecycle."""
    path = pathlib.Path(study) / "harness" / "SCAFFOLD.md"
    if not path.is_file():
        pytest.skip("SCAFFOLD.md is deleted in the first post-freeze commit")
    text = " ".join(path.read_text(encoding="utf-8").split())
    for directory, pattern in make_manifest.REGISTERED_PAYLOAD_SETS:
        if directory.startswith("controls/"):
            continue          # the sealed set is committed during the rounds
        assert "%s/%s" % (directory, pattern) in text, (
            "the freeze-fill step must name the registered payload set %s/%s"
            % (directory, pattern))


def test_the_study_root_ignores_bytecode_the_way_the_other_studies_do(study):
    """R5-1's recurrence half, in the repository's own idiom: studies 011–018
    each carry a study-root `.gitignore` naming `__pycache__/` and
    `.pytest_cache/`. Study 019 did not, which is why an ordinary local run
    could stage one."""
    path = pathlib.Path(study) / ".gitignore"
    assert path.is_file(), (
        "the study root must carry the house .gitignore (studies 011-018 all "
        "do), or an ordinary `git add -A` stages a bytecode cache")
    lines = [line.strip() for line in
             path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert "__pycache__/" in lines and ".pytest_cache/" in lines, lines
