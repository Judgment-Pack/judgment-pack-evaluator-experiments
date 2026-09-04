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


# ---------------------------------------------------------------------------
# R1-19: the pinned evidence trees
# ---------------------------------------------------------------------------

def test_the_sweep_evidence_trees_verify_and_tampering_refuses(tmp_path):
    """The §2.1 fill's source bytes are pinned per tree and verified byte for
    byte; a mutated, added or deleted file under a named tree refuses, and an
    unnamed future tree is permitted. Driven on a COPY so the real evidence
    never moves.

    NON-DISCRIMINATING for round-2 R2-15: the "added file" branch below adds
    an ORDINARY file, which the digest sees; it cannot see a symlink, a
    special file or an empty directory, none of which contributes a line.
    The six cases after this one are the discriminating ones."""
    import shutil
    import sys
    sys.path.insert(0, HARNESS)
    import integrity
    if not os.path.isdir(os.path.join(STUDY, "sweeps")):
        pytest.skip("no sweeps tree beside this suite")
    clone = tmp_path / "study"
    clone.mkdir()
    shutil.copytree(os.path.join(STUDY, "sweeps"), clone / "sweeps")
    (clone / "harness").mkdir()
    shutil.copy(os.path.join(HARNESS, "PINS.json"),
                clone / "harness" / "PINS.json")
    verified = integrity.verify_sweep_evidence(str(clone))
    assert "2026-08-24-effort-sweep" in verified
    # an unnamed future tree is permitted
    (clone / "sweeps" / "2027-01-01-effort-sweep").mkdir()
    integrity.verify_sweep_evidence(str(clone))
    # a mutated byte refuses
    target = clone / "sweeps" / "2026-08-24-effort-sweep" / "SWEEP.md"
    body = target.read_text(encoding="utf-8")
    target.write_text(body + "tampered\n", encoding="utf-8")
    with pytest.raises(integrity.IntegrityError, match="R1-19"):
        integrity.verify_sweep_evidence(str(clone))
    target.write_text(body, encoding="utf-8")
    # an added file refuses
    extra = clone / "sweeps" / "refused-attempt-01-leak-tokens" / "extra.txt"
    extra.write_text("x", encoding="utf-8")
    with pytest.raises(integrity.IntegrityError, match="R1-19"):
        integrity.verify_sweep_evidence(str(clone))
    extra.unlink()
    # a deleted file refuses
    victim = clone / "sweeps" / "refused-attempt-02-unregistered-label" / "SWEEP.md"
    victim.unlink()
    with pytest.raises(integrity.IntegrityError, match="R1-19"):
        integrity.verify_sweep_evidence(str(clone))


# ---------------------------------------------------------------------------
# R2-8: a prior code is a scored slot, and the fence stands without one
# ---------------------------------------------------------------------------

def test_a_prior_authoring_code_is_counted_and_scores_zero(tmp_path):
    """ROUND-2 FINDING R2-8: the wrapper writes NO completion for a tool-using
    author by design, and this function used to refuse the whole publication
    on the missing file. With the pre-step's prior code the slot is COUNTED
    under it — apparatus clean, goldPerfect False, identity never asked — and
    `completion.txt` is never opened.

    MUTATION: remove the `prior_code` early return — the slot below has no
    completion and the call raises RATES-NO-COMPLETION."""
    slot = tmp_path / "slot"
    slot.mkdir()
    record = sweep_rates.score_slot(None, "B", str(slot), [], True,
                                    str(tmp_path / "w"),
                                    prior_code="author-protocol-violation",
                                    prior_side="authoring")
    assert record["code"] == "author-protocol-violation"
    assert record["apparatusCode"] is None
    assert record["goldPerfect"] is False
    assert record["identityWhy"] == "not-asked"
    assert record["priorCode"] == "author-protocol-violation"


def test_a_prior_apparatus_code_leaves_the_denominator(tmp_path):
    slot = tmp_path / "slot"
    slot.mkdir()
    record = sweep_rates.score_slot(None, "B", str(slot), [], True,
                                    str(tmp_path / "w"),
                                    prior_code="call-timeout",
                                    prior_side="apparatus")
    assert record["apparatusCode"] == "call-timeout"
    assert record["code"] is None
    assert record["identityPass"] is None
    cell = sweep_rates.per_arm_cell([record])
    assert (cell["attempted"], cell["calls"], cell["apparatusExcluded"]) == \
        (1, 0, 1)


def test_a_prior_code_on_no_registered_side_refuses(tmp_path):
    slot = tmp_path / "slot"
    slot.mkdir()
    with pytest.raises(sweep_rates.RatesError, match="RATES-PRIOR-SIDE"):
        sweep_rates.score_slot(None, "B", str(slot), [], True,
                               str(tmp_path / "w"), prior_code="x",
                               prior_side="neither")


def test_the_fence_stands_without_a_prior_code(tmp_path):
    """An exit-0 slot with no completion and no prior code is still an
    unexplained slot; the pre-step, not this function, is what turns that
    absence into `slot-shape`."""
    slot = tmp_path / "slot"
    slot.mkdir()
    with pytest.raises(sweep_rates.RatesError, match="RATES-NO-COMPLETION"):
        sweep_rates.score_slot(None, "B", str(slot), [], True,
                               str(tmp_path / "w"))


def test_the_published_sweep_rates_still_recompute_row_for_row():
    """R2-8's regression fence for the PINNED evidence tree: the sweep's
    published `SWEEP-RATES.json` sits inside the digest pinned at
    `sweep.evidenceTrees` and its 27 calls all answered, so R2-1's and
    R2-10's vocabulary changes must reproduce every published row and every
    per-arm member that the ledger carries. The superseded `apparatusRefused`
    member is the one exclusion, marked here: it was 0 on every cell, is not
    republished, and the ledger stays as pinned.

    MUTATION: make `score_slot()`'s prior-code branch fire unconditionally —
    every row collapses to a coded record and the row comparison fails.
    LABEL: comparing only the perfect/identity totals could not discriminate a
    changed ROW shape; the assertion compares full rows."""
    if not os.environ.get("JPACK_BIN") or not os.environ.get("OPA_BIN"):
        pytest.skip("the pinned binaries are not present")
    path = os.path.join(sweep_rates.SWEEP_ROOT, LABEL,
                        sweep_rates.RATES_LEDGER_NAME)
    if not os.path.exists(path):
        pytest.skip("the sweep's rates ledger has not been published")
    import tempfile
    with open(path, "rb") as handle:
        published = json.loads(handle.read().decode("utf-8"))
    pins = sweep_rates.load_pins()
    tools = sweep_rates.toolchain(pins)
    gold = sweep_rates.load_gold()
    with tempfile.TemporaryDirectory(prefix="s020-recompute-") as scratch:
        fresh = sweep_rates.sweep_rates(tools, LABEL, gold, scratch)
    by_setting = {row["setting"]: row for row in fresh["settings"]}
    for setting in published["settings"]:
        recomputed = by_setting[setting["setting"]]
        for old, new in zip(setting["slots"], recomputed["slots"]):
            for member, value in old.items():
                if member == "apparatusRefused":
                    continue
                assert new.get(member) == value, (setting["setting"], member,
                                                  old["slot"])
        for arm in ("A", "B", "C"):
            for member, value in setting["perArm"][arm].items():
                if member == "apparatusRefused":
                    continue
                assert recomputed["perArm"][arm][member] == value, (
                    setting["setting"], arm, member)


# --- ROUND-2 R2-15: the lstat fence on the evidence walk ----------------------

def _evidence_clone(tmp_path):
    import shutil
    import sys
    sys.path.insert(0, HARNESS)
    import integrity
    if not os.path.isdir(os.path.join(STUDY, "sweeps")):
        pytest.skip("no sweeps tree beside this suite")
    clone = tmp_path / "study"
    clone.mkdir()
    shutil.copytree(os.path.join(STUDY, "sweeps"), clone / "sweeps")
    (clone / "harness").mkdir()
    shutil.copy(os.path.join(HARNESS, "PINS.json"),
                clone / "harness" / "PINS.json")
    return integrity, clone


def test_the_type_fence_does_not_move_the_pinned_digests(tmp_path):
    """R2-15 took the branch that moves NO pinned value: an unmodified clone
    verifies to exactly the registry's three digests under the fence."""
    integrity, clone = _evidence_clone(tmp_path)
    import json
    with open(os.path.join(HARNESS, "PINS.json"), "rb") as handle:
        trees = json.loads(handle.read().decode("utf-8"))["sweep"]["evidenceTrees"]
    verified = integrity.verify_sweep_evidence(str(clone))
    for name, digest in trees.items():
        if name != "rule":
            assert verified[name] == digest, name


def test_a_directory_symlink_addition_refuses(tmp_path):
    """MUTATION: revert `_evidence_lines()` to the plain os.walk — the link
    contributes no line, the digest is preserved, and this test fails."""
    integrity, clone = _evidence_clone(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "planted.txt").write_text("x", encoding="utf-8")
    (clone / "sweeps" / "2026-08-24-effort-sweep" / "planted-dir").symlink_to(
        outside, target_is_directory=True)
    with pytest.raises(integrity.IntegrityError, match="R2-15"):
        integrity.verify_sweep_evidence(str(clone))


def test_a_file_replaced_by_a_symlink_refuses(tmp_path):
    """The same bytes THROUGH a link used to hash identically."""
    integrity, clone = _evidence_clone(tmp_path)
    target = clone / "sweeps" / "2026-08-24-effort-sweep" / "SWEEP-RATES.json"
    body = target.read_bytes()
    copy = tmp_path / "copy.bin"
    copy.write_bytes(body)
    target.unlink()
    target.symlink_to(copy)
    with pytest.raises(integrity.IntegrityError, match="R2-15"):
        integrity.verify_sweep_evidence(str(clone))


def test_a_dangling_symlink_refuses_as_an_integrity_error(tmp_path):
    """Refused by NAME, not by a FileNotFoundError escaping the reader."""
    integrity, clone = _evidence_clone(tmp_path)
    (clone / "sweeps" / "refused-attempt-01-leak-tokens" / "dangling").symlink_to(
        tmp_path / "does-not-exist")
    with pytest.raises(integrity.IntegrityError, match="R2-15"):
        integrity.verify_sweep_evidence(str(clone))


def test_a_fifo_refuses_instead_of_blocking(tmp_path):
    """An `open()` on a FIFO with no writer blocks forever; the fence decides
    by lstat and never opens it. Run under a thread so a regression hangs
    as a failure rather than as a hung suite."""
    import threading
    integrity, clone = _evidence_clone(tmp_path)
    fifo = clone / "sweeps" / "refused-attempt-02-unregistered-label" / "pipe"
    os.mkfifo(str(fifo))
    outcome = {}

    def attempt():
        try:
            integrity.verify_sweep_evidence(str(clone))
            outcome["result"] = "returned"
        except integrity.IntegrityError as error:
            outcome["result"] = str(error)
        except Exception as error:                  # noqa: BLE001 (named)
            outcome["result"] = "other: %r" % (error,)

    worker = threading.Thread(target=attempt, daemon=True)
    worker.start()
    worker.join(timeout=15)
    assert not worker.is_alive(), "the verifier blocked on the fifo"
    assert "R2-15" in outcome.get("result", ""), outcome


def test_an_empty_directory_refuses(tmp_path):
    """An empty directory contributes no line and could be added or removed
    without moving the digest. MUTATION: delete only the empty-directory
    clause — this test alone fails."""
    integrity, clone = _evidence_clone(tmp_path)
    (clone / "sweeps" / "2026-08-24-effort-sweep" / "hollow").mkdir()
    with pytest.raises(integrity.IntegrityError, match="empty directory"):
        integrity.verify_sweep_evidence(str(clone))
