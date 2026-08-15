"""ADR 0004's two exclusions, asserted so a future widening fails the suite.

ADR 0004 decides that a study's manifest covers what must not change, that a
file whose purpose is to be appended to after the freeze is not that, and that
`DEVIATIONS.md` and `README.md` are therefore excluded **by construction, in a
named constant, with a harness test asserting the exclusion**. This is that
test. It has real power here rather than being a guard over an absent file:
both files EXIST in this study today, so an edit that widened the covered set
would cover them and these assertions would fail.

The third exclusion — `harness/PINS.json` — is Study 014's linear-anchor rule,
and it is asserted with the same idiom: the manifest must not cover the registry
that pins the manifest, or the anchor cannot be initialized without a SHA-256
fixed point.
"""
import os

import make_manifest


def test_the_two_adr_0004_exclusions_are_named_constants():
    assert "DEVIATIONS.md" in make_manifest.EXCLUDED_DOCUMENTS
    assert "README.md" in make_manifest.EXCLUDED_DOCUMENTS


def test_neither_appendable_file_is_covered_and_both_exist(study):
    """The exclusion is asserted against files that are really there: a guard
    over an absent file passes for the wrong reason."""
    for name in ("DEVIATIONS.md", "README.md"):
        assert os.path.isfile(os.path.join(study, name)), name
        assert name not in make_manifest.manifest_entries()


def test_the_registry_is_not_covered_by_the_manifest_it_pins():
    assert "harness/PINS.json" in make_manifest.EXCLUDED_DOCUMENTS
    assert "harness/PINS.json" not in make_manifest.manifest_entries()


def test_the_manifest_does_not_cover_itself():
    assert "harness/STUDY-MANIFEST.sha256" not in make_manifest.manifest_entries()


def test_no_registered_document_is_also_excluded():
    """A path in both constants would make the covered set depend on which
    constant a future reader believed."""
    overlap = set(make_manifest.REGISTERED_DOCUMENTS) & \
        set(make_manifest.EXCLUDED_DOCUMENTS + make_manifest.EXCLUDED_ARTIFACTS)
    assert overlap == set()


def test_every_harness_source_and_the_ports_table_are_covered():
    entries = make_manifest.manifest_entries()
    for name in ("harness/batch.py", "harness/integrity.py",
                 "harness/make_manifest.py", "harness/transcript_check.py",
                 "harness/authoring_call.sh", "harness/PORTS.md",
                 "harness/tests/test_manifest.py"):
        assert name in entries, name


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
