"""Per-code reachability — every registered code, a minimal condition, exact match.

Round 1's finding: the SPEC/code vocabulary test was syntactic. It compared prose
against declared constants and proved neither that a declared code was reachable
nor that a runtime string belonged to the vocabulary. These tests construct the
minimal condition for each registered `adapter/SPEC.md` section 5 code and assert
the **exact** code.

Round 2's finding: the every-code ordering claim was overstated (four hand-picked
orderings) and the meta-test that backed the coverage claim merely grepped this
file for code literals. Both are replaced here. Every ordered check now carries a
**competing-defect** case — the checked defect present together with a defect the
ceremony would reach later — and asserts the earlier code wins; and the coverage
meta-test is built from `verify.LAYER_VERDICT_CODES`, the exported registered
`{verdict, code}` pair table, against the codes these tables actually assert.

Every case is built by transforming a frozen cell in a temporary directory.
Nothing here writes to `fixtures/`.
"""

import ast
import json
import shutil
import sys
from pathlib import Path

import pytest

from conftest import STUDY, jpack_bin  # noqa: E402

sys.path.insert(0, str(STUDY / "adapter"))
sys.path.insert(0, str(STUDY / "harness"))

import commitment  # noqa: E402
import verify  # noqa: E402

BASELINE = STUDY / "fixtures" / "baseline"
# `c10` is the registered reject-executed cell: its commitment authorizes an
# action its own disposition does not, so it carries the ceremony's *last*
# binding check (the section 4 map on the derived action) already planted. It is
# the only way to put a competing defect downstream of `action-arguments-mismatch`
# without re-signing a chain inside a test.
REJECT_EXECUTED = STUDY / "fixtures" / "mutations" / "c10-reject-executed"


def staged(tmp_path, name="cell", origin=BASELINE):
    directory = tmp_path / name
    shutil.copytree(origin, directory)
    return directory


def bundle_of(directory):
    return json.loads((directory / "bundle.json").read_text(encoding="utf-8"))


def write_bundle(directory, bundle):
    (directory / "bundle.json").write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def binding_code(directory):
    record = verify.layer_binding(verify.Cell(directory))
    return record["code"] if record["verdict"] != "pass" else None


_PINNED = object()


def replay_code(directory, work_root, binary=_PINNED):
    """`binary=None` means "no evaluator available", not "use the pinned one"."""
    record = verify.layer_replay(
        verify.Cell(directory), jpack_bin() if binary is _PINNED else binary, work_root
    )
    return record["code"] if record["verdict"] != "pass" else None


def objective_commitment(directory):
    return json.loads(bundle_of(directory)["work_order"]["objective"])


def set_objective(directory, raw_text):
    bundle = bundle_of(directory)
    bundle["work_order"]["objective"] = raw_text
    write_bundle(directory, bundle)


def rewrite_objective(directory, mutate):
    """Apply `mutate` to the objective's commitment and re-encode it canonically."""
    candidate = objective_commitment(directory)
    mutate(candidate)
    set_objective(directory, commitment.commitment_bytes(candidate).decode("utf-8"))


def rebind_chain(directory, mutate):
    """Rewrite the commitment *and* everything downstream that names its digest.

    `rewrite_objective` alone cannot reach the binding ceremony's later checks:
    changing the commitment changes its digest, so the executing receipt stops
    carrying it and `binding-point-divergence` fires long before the artifact
    comparisons. This rewrites the objective, the retained document and both
    copies of the digest inside the executing receipt, so the ceremony walks past
    the marker checks and lands on the check actually under test.
    """
    candidate = objective_commitment(directory)
    mutate(candidate)
    raw = commitment.commitment_bytes(candidate)
    set_objective(directory, raw.decode("utf-8"))
    (directory / "commitment.json").write_bytes(raw)
    digest = commitment.commitment_digest(candidate)
    bundle = bundle_of(directory)
    receipt = executing_receipt(bundle)
    receipt["nested_claim"]["context_source_digest"] = digest
    receipt["correlation_factors"]["context_source_digest"] = digest
    write_bundle(directory, bundle)


def executing_receipt(bundle):
    return next(
        receipt
        for receipt in bundle["receipts"]
        if receipt.get("tool_name") == "owp.apply_patch"
    )


def repo_read_receipt(bundle):
    return next(
        receipt
        for receipt in bundle["receipts"]
        if receipt.get("tool_name") == "owp.repo_read"
    )


# --------------------------------------------------------------------------
# the defect vocabulary — one deterministic transform each
# --------------------------------------------------------------------------

def defect_none(directory):
    """No planted defect: the condition under test is an argument, not a byte."""


def defect_bundle_unreadable(directory):
    (directory / "bundle.json").write_bytes(b"{not json at all")


def defect_objective_not_a_string(directory):
    bundle = bundle_of(directory)
    bundle["work_order"]["objective"] = 42
    write_bundle(directory, bundle)


def defect_objective_not_a_commitment(directory):
    set_objective(directory, "Apply a deterministic patch and verify it.")


def defect_objective_unknown_field(directory):
    rewrite_objective(
        directory,
        lambda candidate: candidate["judgment"].__setitem__(
            "handoffTarget", {"kind": "human-role"}
        ),
    )


def defect_objective_duplicate_member(directory):
    raw = json.dumps(objective_commitment(directory), separators=(",", ":"))
    set_objective(directory, raw.replace('{"action":', '{"action":null,"action":', 1))


def defect_objective_noncanonical(directory):
    set_objective(directory, json.dumps(objective_commitment(directory), indent=2))


def defect_objective_lone_surrogate(directory):
    """A signed objective that is JSON but not I-JSON (R2-4)."""
    raw = json.dumps(objective_commitment(directory), separators=(",", ":"))
    mutated = raw.replace("expense-approval", "expense-\\ud800approval", 1)
    assert mutated != raw
    set_objective(directory, mutated)


def defect_objective_duplicate_extension(directory):
    """`supportedExtensions` carries the same member twice (R2-8)."""
    rewrite_objective(
        directory,
        lambda candidate: candidate["judgment"].__setitem__(
            "supportedExtensions",
            ["https://example.com/ext/unused", "https://example.com/ext/unused"],
        ),
    )


def defect_retained_noncanonical(directory):
    (directory / "commitment.json").write_text(
        json.dumps(objective_commitment(directory), indent=2), encoding="utf-8"
    )


def defect_retained_absent(directory):
    (directory / "commitment.json").unlink()


def defect_retained_unparseable(directory):
    (directory / "commitment.json").write_bytes(b'{"commitmentVersion": "1", ')


def defect_retained_different(directory):
    candidate = objective_commitment(directory)
    candidate["judgment"]["packDigest"] = "sha256:" + "ab" * 32
    (directory / "commitment.json").write_bytes(commitment.commitment_bytes(candidate))


def defect_marker_points_elsewhere(directory):
    bundle = bundle_of(directory)
    digest = commitment.commitment_digest(objective_commitment(directory))
    repo_read_receipt(bundle)["nested_claim"]["context_source_digest"] = digest
    executing_receipt(bundle)["nested_claim"]["context_source_digest"] = "11" * 32
    write_bundle(directory, bundle)


def defect_no_execution(directory):
    bundle = bundle_of(directory)
    bundle["receipts"] = [
        receipt
        for receipt in bundle["receipts"]
        if receipt.get("tool_name") != "owp.apply_patch"
    ]
    write_bundle(directory, bundle)


def defect_surplus_execution(directory):
    bundle = bundle_of(directory)
    extra = json.loads(json.dumps(executing_receipt(bundle)))
    extra["receipt_id"] = "aa" * 32
    extra["nested_claim"]["context_source_digest"] = "b" * 64
    bundle["receipts"].append(extra)
    write_bundle(directory, bundle)


def defect_null_action_with_execution(directory):
    candidate = objective_commitment(directory)
    candidate["action"] = None
    raw = commitment.commitment_bytes(candidate)
    set_objective(directory, raw.decode("utf-8"))
    (directory / "commitment.json").write_bytes(raw)


def defect_null_action_with_marked_receipt(directory):
    """Commitment to inaction, no action-class receipt — but a marked one.

    The other arm of the null-action totality rule: nothing was executed under
    the map, yet some receipt claims this commitment as its context.
    """
    candidate = objective_commitment(directory)
    candidate["action"] = None
    raw = commitment.commitment_bytes(candidate)
    set_objective(directory, raw.decode("utf-8"))
    (directory / "commitment.json").write_bytes(raw)
    bundle = bundle_of(directory)
    bundle["receipts"] = [
        receipt
        for receipt in bundle["receipts"]
        if receipt.get("tool_name") != "owp.apply_patch"
    ]
    repo_read_receipt(bundle)["nested_claim"]["context_source_digest"] = (
        commitment.commitment_digest(candidate)
    )
    write_bundle(directory, bundle)


def defect_unmarked_execution(directory):
    bundle = bundle_of(directory)
    executing_receipt(bundle)["nested_claim"]["context_source_digest"] = "cd" * 32
    write_bundle(directory, bundle)


def defect_unmirrored_correlation(directory):
    bundle = bundle_of(directory)
    executing_receipt(bundle)["correlation_factors"]["context_source_digest"] = "ef" * 32
    write_bundle(directory, bundle)


def defect_pack_absent(directory):
    (directory / "pack.json").unlink()


def defect_pack_edited(directory):
    payload = (directory / "pack.json").read_bytes()
    mutated = payload.replace(b'"5000"', b'"6000"')
    assert mutated != payload
    (directory / "pack.json").write_bytes(mutated)


def defect_pack_identity_drift(directory):
    """Pack bytes whose digest still matches, whose identity no longer does.

    The digest check passes because the commitment is rebound to the edited
    bytes; the identity check is what has to see that the retained pack is a
    different pack version from the one the judgment names.
    """
    payload = (directory / "pack.json").read_bytes()
    mutated = payload.replace(b'"version": "0.1.0"', b'"version": "0.9.9"')
    assert mutated != payload
    (directory / "pack.json").write_bytes(mutated)
    rebind_chain(
        directory,
        lambda candidate: candidate["judgment"].__setitem__(
            "packDigest", commitment.sha256_prefixed(mutated)
        ),
    )


def defect_facts_absent(directory):
    (directory / "facts.json").unlink()


def defect_facts_edited(directory):
    payload = (directory / "facts.json").read_bytes()
    mutated = payload.replace(b"250.00", b"240.00")
    assert mutated != payload
    (directory / "facts.json").write_bytes(mutated)


def defect_evidence_absent(directory):
    (directory / "evidence.json").unlink()


def defect_evidence_edited(directory):
    (directory / "evidence.json").write_bytes(
        b'{"receipt":"present","cost-center":"unknown"}'
    )


def defect_evidence_declared_absent(directory):
    """The commitment declares no evidence document while one is retained."""
    rebind_chain(
        directory,
        lambda candidate: candidate["judgment"].__setitem__("evidenceDigest", None),
    )


def defect_envelope_unreadable(directory):
    (directory / "evaluation.json").write_bytes(b"[]")


def defect_envelope_without_a_disposition(directory):
    (directory / "evaluation.json").write_bytes(b'{"evaluatorRelease":"0.16.0"}')


def defect_disposition_forged(directory):
    envelope = json.loads((directory / "evaluation.json").read_text(encoding="utf-8"))
    envelope["disposition"]["reasons"] = ["forged"]
    (directory / "evaluation.json").write_text(
        json.dumps(envelope, separators=(",", ":"), ensure_ascii=False), encoding="utf-8"
    )


def defect_arguments_digest_wrong(directory):
    bundle = bundle_of(directory)
    executing_receipt(bundle)["arguments_digest"] = "cc" * 32
    write_bundle(directory, bundle)


# replay-side defects


def defect_executable_digest_forged(directory):
    rewrite_objective(
        directory,
        lambda candidate: candidate["judgment"].__setitem__(
            "executableDigest", "sha256:" + "99" * 32
        ),
    )


def defect_evaluator_release_forged(directory):
    rewrite_objective(
        directory,
        lambda candidate: candidate["judgment"].__setitem__(
            "evaluatorRelease", "0.15.0"
        ),
    )


def defect_spec_version_forged(directory):
    rewrite_objective(
        directory,
        lambda candidate: candidate["judgment"].__setitem__(
            "evaluatorSpecVersion", "0.9.9-draft"
        ),
    )


def defect_disposition_digest_forged(directory):
    rewrite_objective(
        directory,
        lambda candidate: candidate["judgment"].__setitem__(
            "dispositionDigest", "sha256:" + "77" * 32
        ),
    )


def defect_pack_unreadable_to_the_evaluator(directory):
    """Retained pack bytes the evaluator cannot even parse into a document.

    Distinct from `defect_pack_not_conformant`: that one produces a classified
    `evaluationError`, this one produces no readable envelope at all, which is
    the replay layer's other `replay-refused` arm.
    """
    broken = b"this is not a judgment pack\n"
    (directory / "pack.json").write_bytes(broken)
    rewrite_objective(
        directory,
        lambda candidate: candidate["judgment"].__setitem__(
            "packDigest", commitment.sha256_prefixed(broken)
        ),
    )


def defect_pack_not_conformant(directory):
    """Retained pack the evaluator refuses, kept consistent with the commitment."""
    payload = (directory / "pack.json").read_bytes()
    broken = payload.replace(
        b'"specVersion": "0.2.0-draft"', b'"specVersion": "0.1.0-draft"'
    )
    assert broken != payload
    (directory / "pack.json").write_bytes(broken)

    def rebind(candidate):
        candidate["judgment"]["packDigest"] = commitment.sha256_prefixed(broken)
        candidate["judgment"]["specVersion"] = "0.1.0-draft"

    rewrite_objective(directory, rebind)


# --------------------------------------------------------------------------
# the baseline itself
# --------------------------------------------------------------------------

def test_baseline_binding_passes(tmp_path):
    assert binding_code(staged(tmp_path)) is None


# --------------------------------------------------------------------------
# BINDING codes — one minimal condition each
# --------------------------------------------------------------------------

BINDING_CASES = (
    ("commitment-objective-missing", defect_objective_not_a_commitment),
    ("commitment-schema-invalid", defect_objective_unknown_field),
    ("commitment-schema-invalid", defect_objective_duplicate_member),
    ("commitment-schema-invalid", defect_objective_noncanonical),
    ("commitment-schema-invalid", defect_objective_lone_surrogate),
    ("commitment-schema-invalid", defect_objective_duplicate_extension),
    ("commitment-schema-invalid", defect_retained_noncanonical),
    ("binding-point-divergence", defect_retained_different),
    ("binding-point-divergence", defect_unmarked_execution),
    ("binding-point-divergence", defect_unmirrored_correlation),
    ("action-tool-mismatch", defect_marker_points_elsewhere),
    ("executing-receipt-missing", defect_no_execution),
    ("action-map-violation", defect_surplus_execution),
    ("action-map-violation", defect_null_action_with_execution),
    ("pack-artifact-missing", defect_pack_absent),
    ("pack-digest-mismatch", defect_pack_edited),
    ("facts-artifact-missing", defect_facts_absent),
    ("facts-digest-mismatch", defect_facts_edited),
    ("evidence-artifact-missing", defect_evidence_absent),
    ("evidence-digest-mismatch", defect_evidence_edited),
    ("disposition-digest-mismatch-retained", defect_disposition_forged),
    ("action-arguments-mismatch", defect_arguments_digest_wrong),
)


@pytest.mark.parametrize(
    "code,defect", BINDING_CASES, ids=[
        "%s-%s" % (code, defect.__name__) for code, defect in BINDING_CASES
    ]
)
def test_binding_code_is_reachable(tmp_path, code, defect):
    directory = staged(tmp_path)
    defect(directory)
    assert binding_code(directory) == code


# --------------------------------------------------------------------------
# BINDING first-failure ordering — every ordered check, competing defects
#
# One row per ordered check in `verify.layer_binding`, in ceremony order. Each
# row plants the checked defect together with a defect the ceremony reaches
# strictly later and asserts the earlier code. The last row starts from `c10`,
# whose chain already carries the ceremony's final check (the section 4 map on
# the derived action) — the only downstream defect that cannot be planted by a
# byte edit, because every input the map reads is pinned by an earlier check.
# --------------------------------------------------------------------------

BINDING_ORDER_CASES = (
    ("commitment-objective-missing", defect_bundle_unreadable,
     defect_pack_edited, BASELINE),
    ("commitment-objective-missing", defect_objective_not_a_string,
     defect_pack_edited, BASELINE),
    ("commitment-objective-missing", defect_objective_not_a_commitment,
     defect_pack_edited, BASELINE),
    ("commitment-schema-invalid", defect_objective_duplicate_member,
     defect_pack_edited, BASELINE),
    ("commitment-schema-invalid", defect_objective_noncanonical,
     defect_pack_edited, BASELINE),
    ("commitment-schema-invalid", defect_objective_unknown_field,
     defect_facts_edited, BASELINE),
    ("binding-point-divergence", defect_retained_absent,
     defect_pack_edited, BASELINE),
    ("commitment-schema-invalid", defect_retained_unparseable,
     defect_pack_edited, BASELINE),
    ("commitment-schema-invalid", defect_retained_noncanonical,
     defect_pack_edited, BASELINE),
    ("binding-point-divergence", defect_retained_different,
     defect_pack_absent, BASELINE),
    ("action-map-violation", defect_null_action_with_execution,
     defect_pack_edited, BASELINE),
    ("action-map-violation", defect_null_action_with_marked_receipt,
     defect_pack_edited, BASELINE),
    ("action-tool-mismatch", defect_marker_points_elsewhere,
     defect_surplus_execution, BASELINE),
    ("executing-receipt-missing", defect_no_execution,
     defect_pack_edited, BASELINE),
    ("action-map-violation", defect_surplus_execution,
     defect_pack_edited, BASELINE),
    ("binding-point-divergence", defect_unmarked_execution,
     defect_pack_edited, BASELINE),
    ("binding-point-divergence", defect_unmirrored_correlation,
     defect_facts_edited, BASELINE),
    ("pack-artifact-missing", defect_pack_absent, defect_facts_edited, BASELINE),
    ("pack-digest-mismatch", defect_pack_edited, defect_facts_edited, BASELINE),
    ("pack-digest-mismatch", defect_pack_identity_drift,
     defect_facts_edited, BASELINE),
    ("facts-artifact-missing", defect_facts_absent, defect_evidence_edited, BASELINE),
    ("facts-digest-mismatch", defect_facts_edited, defect_evidence_edited, BASELINE),
    ("evidence-digest-mismatch", defect_evidence_declared_absent,
     defect_disposition_forged, BASELINE),
    ("evidence-artifact-missing", defect_evidence_absent,
     defect_disposition_forged, BASELINE),
    ("evidence-digest-mismatch", defect_evidence_edited,
     defect_disposition_forged, BASELINE),
    ("disposition-digest-mismatch-retained", defect_envelope_unreadable,
     defect_arguments_digest_wrong, BASELINE),
    ("disposition-digest-mismatch-retained", defect_envelope_without_a_disposition,
     defect_arguments_digest_wrong, BASELINE),
    ("disposition-digest-mismatch-retained", defect_disposition_forged,
     defect_arguments_digest_wrong, BASELINE),
    ("action-arguments-mismatch", defect_arguments_digest_wrong, None, REJECT_EXECUTED),
)


@pytest.mark.parametrize(
    "code,earlier,later,origin", BINDING_ORDER_CASES, ids=[
        "%s-over-%s" % (code, later.__name__ if later else "the-registered-map-violation")
        for code, _, later, _ in BINDING_ORDER_CASES
    ]
)
def test_the_earlier_binding_check_wins(tmp_path, code, earlier, later, origin):
    # The later-ordered defect is planted FIRST, because several transforms read
    # the objective they rewrite and the earlier defect may destroy it. Planting
    # order is not check order; the assertion is about check order.
    directory = staged(tmp_path, origin=origin)
    if later is not None:
        later(directory)
        earlier(directory)
    else:
        earlier(directory)
        # The competing later defect is the cell's own registered one: `c10`
        # commits to an action its disposition does not authorize, which is the
        # ceremony's last check. Assert it really is there before relying on it.
        untouched = staged(tmp_path, name="control", origin=origin)
        assert binding_code(untouched) == "action-map-violation"
    assert binding_code(directory) == code


# --------------------------------------------------------------------------
# REPLAY codes — one minimal condition each
# --------------------------------------------------------------------------

def test_replay_unavailable_without_a_commitment(tmp_path, work_root):
    directory = staged(tmp_path)
    defect_objective_not_a_commitment(directory)
    assert replay_code(directory, work_root) == "replay-unavailable"


def test_replay_unavailable_without_the_evaluator(tmp_path, work_root):
    directory = staged(tmp_path)
    assert replay_code(directory, work_root, binary=None) == "replay-unavailable"


def test_replay_unavailable_without_retained_inputs(tmp_path, work_root):
    directory = staged(tmp_path)
    defect_facts_absent(directory)
    assert replay_code(directory, work_root) == "replay-unavailable"


REPLAY_CASES = (
    ("replay-executable-mismatch", defect_executable_digest_forged),
    ("replay-executable-mismatch", defect_evaluator_release_forged),
    ("replay-refused", defect_pack_not_conformant),
    ("replay-spec-version-mismatch", defect_spec_version_forged),
    ("replay-disposition-mismatch", defect_disposition_digest_forged),
)


@pytest.mark.parametrize(
    "code,defect", REPLAY_CASES, ids=[
        "%s-%s" % (code, defect.__name__) for code, defect in REPLAY_CASES
    ]
)
def test_replay_code_is_reachable(tmp_path, work_root, code, defect):
    directory = staged(tmp_path)
    defect(directory)
    assert replay_code(directory, work_root) == code


def test_replay_refused_records_the_class_as_detail_only(tmp_path, work_root):
    """A refusal is never a disposition: the class is detail, the code is exact."""
    directory = staged(tmp_path)
    defect_pack_not_conformant(directory)
    record = verify.layer_replay(verify.Cell(directory), jpack_bin(), work_root)
    assert record["code"] == "replay-refused"
    assert record["detail"] and ":" in record["detail"]
    assert verify.outcome(record, "replay") == "fail:replay-refused"


# --------------------------------------------------------------------------
# REPLAY first-failure ordering — every ordered check, competing defects
# --------------------------------------------------------------------------

# The fourth column is the evaluator: `_PINNED` is the pinned binary, `None` is
# "no evaluator available", which is a check site of its own and the one round 3
# named — an evaluator-unavailable attempt carrying a downstream defect must
# report `replay-unavailable`, not the defect.
REPLAY_ORDER_CASES = (
    ("replay-unavailable", defect_objective_not_a_commitment,
     defect_pack_not_conformant, _PINNED),
    ("replay-unavailable", defect_none, defect_disposition_digest_forged, None),
    ("replay-executable-mismatch", defect_executable_digest_forged,
     defect_spec_version_forged, _PINNED),
    ("replay-executable-mismatch", defect_evaluator_release_forged,
     defect_disposition_digest_forged, _PINNED),
    ("replay-unavailable", defect_facts_absent,
     defect_disposition_digest_forged, _PINNED),
    ("replay-unavailable", defect_evidence_absent,
     defect_disposition_digest_forged, _PINNED),
    ("replay-refused", defect_pack_not_conformant,
     defect_disposition_digest_forged, _PINNED),
    ("replay-spec-version-mismatch", defect_spec_version_forged,
     defect_disposition_digest_forged, _PINNED),
)


@pytest.mark.parametrize(
    "code,earlier,later,binary", REPLAY_ORDER_CASES, ids=[
        "%s-%s-over-%s" % (code, earlier.__name__, later.__name__)
        for code, earlier, later, _ in REPLAY_ORDER_CASES
    ]
)
def test_the_earlier_replay_check_wins(tmp_path, work_root, code, earlier, later, binary):
    # Planted later-first, for the same reason as the binding ladder above.
    directory = staged(tmp_path)
    later(directory)
    earlier(directory)
    assert replay_code(directory, work_root, binary=binary) == code


def test_even_unparseable_pack_bytes_are_a_classified_refusal(tmp_path, work_root):
    """Why the replay layer's `unreadable` arm carries no ordering case.

    That arm needs an evaluator that produces no readable envelope at all. The
    pinned binary classifies even bytes that are not a pack document, so the arm
    is unreachable through any retained-artifact edit — reaching it would take a
    different executable, which the `executableDigest` check refuses first. This
    is the evidence for that exemption in the site-coverage test below.
    """
    directory = staged(tmp_path)
    defect_pack_unreadable_to_the_evaluator(directory)
    record = verify.layer_replay(verify.Cell(directory), jpack_bin(), work_root)
    assert record["code"] == "replay-refused"
    assert not record["detail"].startswith("unreadable")


# --------------------------------------------------------------------------
# the committed supported-extension set is an input, not decoration
# --------------------------------------------------------------------------

def test_supported_extensions_reach_the_evaluator(tmp_path, work_root):
    """The baseline pack requires no extension, so a declared one changes no
    disposition — the observable is that the evaluator is invoked with the flag
    and still produces the committed disposition, which is the honest bound on
    this field's materiality."""
    directory = staged(tmp_path)
    pack_bytes = (directory / "pack.json").read_bytes()
    facts_bytes = (directory / "facts.json").read_bytes()
    evidence_bytes = (directory / "evidence.json").read_bytes()
    plain, _ = verify.evaluate(
        jpack_bin(), work_root, pack_bytes, facts_bytes, evidence_bytes
    )
    with_extension, _ = verify.evaluate(
        jpack_bin(),
        work_root,
        pack_bytes,
        facts_bytes,
        evidence_bytes,
        supported_extensions=("https://example.com/ext/unused",),
    )
    assert json.loads(plain)["disposition"] == json.loads(with_extension)["disposition"]


# --------------------------------------------------------------------------
# coverage, derived from the exported vocabulary rather than from this source
# --------------------------------------------------------------------------

COVERED_CODES = (
    {code for code, _ in BINDING_CASES}
    | {code for code, _, _, _ in BINDING_ORDER_CASES}
    | {code for code, _ in REPLAY_CASES}
    | {code for code, _, _, _ in REPLAY_ORDER_CASES}
    | {"replay-unavailable"}
)
ORDERED_CODES = (
    {code for code, _, _, _ in BINDING_ORDER_CASES}
    | {code for code, _, _, _ in REPLAY_ORDER_CASES}
)


def registered_codes():
    """Every code the exported `{verdict, code}` pair table registers."""
    return {
        code
        for pairs in verify.LAYER_VERDICT_CODES.values()
        for _, code in pairs
        if code is not None
    }


def test_every_registered_code_has_a_reachability_case():
    """Coverage asserted against the exported table, not against this file's text.

    The round-1 version searched this source for `"<code>"` literals, which would
    have been satisfied by a comment. This compares the codes the case tables
    above actually assert against the codes `verify.LAYER_VERDICT_CODES` declares.
    """
    registered = registered_codes()
    assert registered - COVERED_CODES == set(), "unreachable registered codes"
    assert COVERED_CODES - registered == set(), "cases assert unregistered codes"


def test_every_ordered_check_carries_a_competing_defect_case():
    """Every code with a check ahead of another one is ordering-tested.

    The one exception is stated rather than assumed: `replay-disposition-mismatch`
    is the replay ceremony's final check, so it has no later-ordered defect to
    compete with. `action-map-violation` names three checks — the two null-action
    arms and the surplus-execution arm, all ordering-tested above, plus the
    derived-action arm, which is the binding ceremony's final check and is the
    competing defect the `action-arguments-mismatch` row runs against.

    Coverage per *code* is the weak claim; coverage per *check site* is the one
    round 3 asked for, and it is proved separately below.
    """
    terminal = {"replay-disposition-mismatch"}
    assert registered_codes() - ORDERED_CODES == terminal


# --------------------------------------------------------------------------
# ordering coverage per CHECK SITE — the inventory parsed, the coverage traced
#
# Round 3's finding: "the claimed every-check ordering proof still omits check
# sites such as evaluator-unavailable-with-a-downstream-defect". Coverage by code
# could not have caught that — `replay-unavailable` was already covered by a
# different site. So neither half of the claim is prose here:
#
#   the inventory   every failing return inside the ordered ceremony, found by
#                   parsing `adapter/verify.py` with `ast` (not by grepping it
#                   for code literals, which is what round 1 rejected);
#   the coverage    which site actually fired, recorded by line-tracing each
#                   competing-defect case — so a case that lands on a different
#                   check with the same code stops counting as covering the
#                   check it claims.
# --------------------------------------------------------------------------

CEREMONY_FUNCTIONS = (
    "_commitment_from_objective",
    "_retained_commitment_problem",
    "layer_binding",
    "layer_replay",
)
VERIFY_PATH = Path(verify.__file__).resolve()

# The sites with no competing-defect case, each with the reason it has none.
# Keyed by (function, code, first characters of the literal detail) so the list
# does not silently follow a line number around.
EXEMPT_SITES = {
    (
        "layer_binding",
        "action-map-violation",
        "the section 4 map does not authorize the exec",
    ): "the binding ceremony's final check: no later-ordered defect exists to "
       "compete with it, and it is itself the competing defect for the "
       "action-arguments-mismatch row",
    (
        "layer_replay",
        "replay-disposition-mismatch",
        "recomputed disposition is not the committed d",
    ): "the replay ceremony's final check, same reason",
    (
        "layer_replay",
        "replay-refused",
        "unreadable: the evaluator produced no readabl",
    ): "unreachable through any retained-artifact edit: the pinned evaluator "
       "classifies even unparseable pack bytes, and an evaluator that emitted an "
       "unreadable envelope would be refused by the executableDigest check first "
       "(demonstrated by test_even_unparseable_pack_bytes_are_a_classified_refusal)",
    (
        "layer_binding",
        "commitment-schema-invalid",
        "<computed>",
    ): "defensive: commitment_digest() re-canonicalizes a commitment that "
       "validate_commitment() has already accepted, so no input reaches it that "
       "it can refuse",
}


def _detail_head(call):
    """The literal detail argument's first characters, or `<computed>`."""
    name = getattr(call.func, "id", None)
    arguments = call.args
    detail = arguments[0] if name == "_unavailable" else (
        arguments[1] if len(arguments) > 1 else None
    )
    # A `%`-formatted detail still identifies its site by its literal template.
    if isinstance(detail, ast.BinOp) and isinstance(detail.op, ast.Mod):
        detail = detail.left
    if isinstance(detail, ast.Constant) and isinstance(detail.value, str):
        return detail.value[:45]
    return "<computed>"


def ordered_check_sites():
    """`{line: (function, code, detail head)}` for every failing return."""
    tree = ast.parse(VERIFY_PATH.read_text(encoding="utf-8"))
    sites = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in CEREMONY_FUNCTIONS:
            continue
        for statement in ast.walk(node):
            if not isinstance(statement, ast.Return):
                continue
            call = statement.value
            if not isinstance(call, ast.Call):
                continue
            name = getattr(call.func, "id", None)
            if name not in ("_fail", "_unavailable"):
                continue
            code = (
                "replay-unavailable"
                if name == "_unavailable"
                else call.args[0].value
            )
            sites[statement.lineno] = (node.name, code, _detail_head(call))
    return sites


def fired_site(run, sites):
    """The line of the failing return that produced this outcome."""
    executed = set()
    filename = str(VERIFY_PATH)

    def tracer(frame, event, argument):
        if frame.f_code.co_filename != filename:
            return None
        if event == "line":
            executed.add(frame.f_lineno)
        return tracer

    previous = sys.gettrace()
    sys.settrace(tracer)
    try:
        run()
    finally:
        sys.settrace(previous)
    fired = sorted(executed & set(sites))
    assert len(fired) == 1, "expected exactly one failing return, traced %s" % [
        sites[line] for line in fired
    ]
    return fired[0]


def test_every_ordered_check_site_has_a_competing_defect_case(tmp_path, work_root):
    sites = ordered_check_sites()
    covered = {}

    for index, (code, earlier, later, origin) in enumerate(BINDING_ORDER_CASES):
        directory = staged(tmp_path, name="site-binding-%d" % index, origin=origin)
        if later is not None:
            later(directory)
        earlier(directory)
        line = fired_site(lambda: binding_code(directory), sites)
        assert sites[line][1] == code, (earlier.__name__, sites[line])
        covered[line] = earlier.__name__

    for index, (code, earlier, later, binary) in enumerate(REPLAY_ORDER_CASES):
        directory = staged(tmp_path, name="site-replay-%d" % index)
        later(directory)
        earlier(directory)
        line = fired_site(
            lambda: replay_code(directory, work_root, binary=binary), sites
        )
        assert sites[line][1] == code, (earlier.__name__, sites[line])
        covered[line] = earlier.__name__

    uncovered = {sites[line] for line in sites if line not in covered}
    assert uncovered == set(EXEMPT_SITES), (
        "check sites with no competing-defect case: %s"
        % sorted(uncovered - set(EXEMPT_SITES))
    )


def test_the_registered_pair_table_matches_the_declared_code_tuples():
    assert {code for _, code in verify.LAYER_VERDICT_CODES["binding"] if code} == set(
        verify.BINDING_CODES
    )
    assert {code for _, code in verify.LAYER_VERDICT_CODES["replay"] if code} == set(
        verify.REPLAY_CODES
    )
    assert ("unavailable", "replay-unavailable") in verify.LAYER_VERDICT_CODES["replay"]
    assert ("fail", "replay-unavailable") not in verify.LAYER_VERDICT_CODES["replay"]


def test_an_unregistered_pair_is_not_normalized_into_an_outcome():
    """R2-5: an unknown verdict with a known code must not become `fail:<code>`."""
    laundered = verify.result("bogus", "pack-digest-mismatch", "x")
    assert verify.outcome(laundered, "binding").startswith(verify.UNREGISTERED_PREFIX)
    assert verify.pair_problem("binding", laundered) is not None
    # A bare `unavailable` on the replay layer is not the registered pair either.
    bare = verify.result("unavailable", None, "x")
    assert verify.pair_problem("replay", bare) is not None
    assert verify.outcome(bare, "replay").startswith(verify.UNREGISTERED_PREFIX)
    assert verify.pair_problem("owp", bare) is None
