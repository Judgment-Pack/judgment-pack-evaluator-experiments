"""ADR 0004's exclusions, asserted so a future widening fails the suite.

ADR 0004 decides that a study's manifest covers what must not change, that a
file whose purpose is to be appended to after the freeze is not that, and that
such files are excluded **by construction, in a named constant, with a harness
test asserting the exclusion**. This is that test. It has real power here rather
than being a guard over an absent file: every named file EXISTS in this study
today, so an edit that widened the covered set would cover them and these
assertions would fail.

THREE APPENDABLE FILES, not two. `DEVIATIONS.md` and `README.md` are ADR 0004's
own examples; **`PREREG-REVIEW.md` is round-3 finding R3-1** and is the same
shape of file — it grows by one disposition table per review round, so covering
it made every round's own dispositions stale the committed manifest. It did that
three rounds running, including in a response that reported a green suite while
three enforcement tests were red. Round 2 answered with a procedure and a second
failing test; the third recurrence is the evidence that a procedure which must be
remembered every round is not a safeguard. So it leaves the covered set by named
constant, like the other two, and `test_the_review_record_cannot_be_re_covered`
below is what makes re-covering it fail the suite rather than pass quietly.

The fourth exclusion — `harness/PINS.json` — is Study 014's linear-anchor rule,
and it is asserted with the same idiom: the manifest must not cover the registry
that pins the manifest, or the anchor cannot be initialized without a SHA-256
fixed point.
"""
import os
import pathlib

import make_manifest

# The files ADR 0004 calls appendable in this study, each of which exists today.
APPENDABLE = ("DEVIATIONS.md", "README.md", "PREREG-REVIEW.md")


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
    `--freeze` must refuse while any is pending."""
    pending = make_manifest.pending_documents()
    assert set(pending) <= set(make_manifest.REGISTERED_DOCUMENTS)
    entries = make_manifest.manifest_entries()
    for name in pending:
        assert name not in entries
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
        # and is not fabricated — asserted rather than assumed.
        assert not [name for name in make_manifest.manifest_entries()
                    if name.startswith("mutants/jps/")]
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
