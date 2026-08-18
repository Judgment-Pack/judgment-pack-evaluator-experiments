"""The sealed reviewer mutant set — round-1 R1-10.

The finding was that the holdout was "wholly unwired": the governing primary
command omitted `--include-reviewer-set`, the flag only reached `ATTEMPT.json`
and a null-pin guard, no code loaded, executed or reported the set, and
`reviewerMutantSet` was not in `FREEZE_PINS` — so the promised first execution
"at the primary attempt" could not occur, and REGISTERED was reachable with the
pin still null.

Each clause of §1a's sentence gets its own case here, because the sentence is
five separate promises: authored during review rounds, committed VERBATIM, first
executed AT the primary attempt, scored AS AUTHORED, reported SEPARATELY, moving
NOTHING.
"""
import hashlib
import json

import pytest

import integrity
from e4lib import reviewer


def sealed_tree(root, *, mutants=None, edits=None, manifest=None):
    root.mkdir(parents=True, exist_ok=True)
    mutants = mutants if mutants is not None else [
        ("r-a-001", "jps", "r-a-001.json", '{"specVersion": "0.2.0-draft"}\n'),
        ("r-b-001", "rego", "r-b-001.rego", "package study\n"),
    ]
    records = []
    for identifier, language, filename, body in mutants:
        (root / filename).write_text(body)
        records.append({
            "id": identifier, "language": language, "file": filename,
            "sha256": hashlib.sha256(body.encode()).hexdigest(),
            "authoredBy": "round-1 reviewer",
        })
    document = manifest if manifest is not None else {
        "reviewerSetVersion": reviewer.SET_VERSION,
        "sealedAt": "round-1",
        "mutants": records,
    }
    if edits:
        document.update(edits)
    (root / reviewer.MANIFEST_NAME).write_text(json.dumps(document))
    return root


# --- mandatory for REGISTERED ----------------------------------------------

def test_the_set_is_a_freeze_pin_so_registered_cannot_skip_it():
    """The label rule is the mechanism: while `reviewerMutantSet.sha256` is
    null the study is a PILOT, and `--include-reviewer-set` refuses on a null
    pin — so the flag and the pin close each other's loophole."""
    assert "reviewerMutantSet" in [name for name, _p in integrity.FREEZE_PINS]
    assert dict(integrity.FREEZE_PINS)["reviewerMutantSet"] == \
        ("reviewerMutantSet", "sha256")


# --- validated WITHOUT being executed ---------------------------------------

def test_loading_validates_and_invokes_no_engine(tmp_path):
    """"First executed at the primary attempt" is a claim about a COUNT, and it
    is checkable only if the pre-attempt path has no execution in it to take.
    `load()` takes no toolchain argument at all."""
    sealed = sealed_tree(tmp_path / "reviewer-mutants")
    loaded = reviewer.load(str(sealed))
    assert loaded["count"] == 2
    assert loaded["executed"] is False
    assert "no engine has been invoked" in loaded["note"]
    assert sorted(record["language"] for record in loaded["mutants"]) == \
        ["jps", "rego"]


def test_the_manifest_digest_binds_the_executed_bytes_to_the_freeze(tmp_path):
    sealed = sealed_tree(tmp_path / "reviewer-mutants")
    loaded = reviewer.load(str(sealed))
    assert reviewer.load(str(sealed), loaded["manifestSha256"])["count"] == 2
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed), "sha256:" + "0" * 64)
    assert str(raised.value).startswith("REVIEWER-SET-DIGEST")


def test_a_payload_edited_after_sealing_refuses(tmp_path):
    """"Committed verbatim": the set is executed as sealed or not at all."""
    sealed = sealed_tree(tmp_path / "reviewer-mutants")
    (sealed / "r-b-001.rego").write_text("package study\n# edited\n")
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert str(raised.value).startswith("REVIEWER-SET-DIGEST")


@pytest.mark.parametrize("edits,code", [
    ({"reviewerSetVersion": 2}, "REVIEWER-SET-SCHEMA"),
    ({"mutants": []}, "REVIEWER-SET-SCHEMA"),
    ({"mutants": "two"}, "REVIEWER-SET-SCHEMA"),
    ({"mutants": [{"id": "r-1"}]}, "REVIEWER-SET-SCHEMA"),
    ({"mutants": [{"id": "r-1", "language": "python", "file": "x",
                   "sha256": "0" * 64}]}, "REVIEWER-SET-SCHEMA"),
])
def test_every_schema_failure_refuses_by_name(tmp_path, edits, code):
    sealed = sealed_tree(tmp_path / "reviewer-mutants", edits=edits)
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert str(raised.value).startswith(code)


def test_two_members_of_one_name_refuse(tmp_path):
    body = "package study\n"
    digest = hashlib.sha256(body.encode()).hexdigest()
    sealed = sealed_tree(tmp_path / "reviewer-mutants", edits={"mutants": [
        {"id": "r-b-001", "language": "rego", "file": "r-b-001.rego",
         "sha256": digest},
        {"id": "r-b-001", "language": "rego", "file": "r-b-001.rego",
         "sha256": digest}]})
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert "appears twice" in str(raised.value)


def test_an_absent_set_refuses_rather_than_scoring_zero_reviewer_mutants(
        tmp_path):
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(tmp_path / "nothing-here"))
    assert str(raised.value).startswith("REVIEWER-SET-ABSENT")


# --- executed EXACTLY ONCE, and reported separately -------------------------

def test_the_set_is_executed_exactly_once(tmp_path, monkeypatch):
    from e4lib import e4
    monkeypatch.setattr(e4, "kill_arm_a",
                        lambda *a, **k: (e4.KILLED, {"case": "c1"}))
    monkeypatch.setattr(e4, "kill_arm_rego",
                        lambda *a, **k: (e4.SURVIVED, {}))
    sealed = reviewer.load(str(sealed_tree(tmp_path / "reviewer-mutants")))
    runs = {"A": [{"run": "run-001", "identityPass": True,
                   "suitePath": "/tmp/suite.json", "scoredCases": []}],
            "B": [{"run": "run-002", "identityPass": True,
                   "suitePath": "/tmp/suite.rego", "scoredCases": []}],
            "C": []}
    published = reviewer.execute(None, sealed, runs, {}, ("A", "B", "C"),
                                {"A": "jps", "B": "rego", "C": "rego"},
                                str(tmp_path))
    assert published["reviewerMutants"] == 2
    assert published["perArm"]["A"]["perRun"][0]["killed"] == ["r-a-001"]
    assert published["perArm"]["B"]["perRun"][0]["survived"] == ["r-b-001"]
    assert published["perArm"]["C"]["scoredRuns"] == 0
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.execute(None, sealed, runs, {}, ("A", "B", "C"),
                         {"A": "jps", "B": "rego", "C": "rego"}, str(tmp_path))
    assert str(raised.value).startswith("REVIEWER-SET-RE-EXECUTED")


def test_a_run_that_failed_identity_is_not_scored_against_the_set(tmp_path,
                                                                  monkeypatch):
    """"Scored as authored" is about the mutants, not about the runs: a suite
    that did not pin its reference down cannot be said to have killed anything,
    exactly as in E4."""
    from e4lib import e4
    monkeypatch.setattr(e4, "kill_arm_rego",
                        lambda *a, **k: (e4.KILLED, {}))
    sealed = reviewer.load(str(sealed_tree(tmp_path / "reviewer-mutants")))
    runs = {"A": [], "B": [{"run": "run-002", "identityPass": False,
                            "suitePath": "/tmp/s.rego", "scoredCases": []}],
            "C": []}
    published = reviewer.execute(None, sealed, runs, {}, ("A", "B", "C"),
                                 {"A": "jps", "B": "rego", "C": "rego"},
                                 str(tmp_path))
    assert published["perArm"]["B"]["scoredRuns"] == 0


def test_a_refused_reviewer_mutant_is_published_as_refused(tmp_path,
                                                           monkeypatch):
    from e4lib import e4
    monkeypatch.setattr(e4, "kill_arm_rego", lambda *a, **k: (e4.REFUSED, {}))
    sealed = reviewer.load(str(sealed_tree(tmp_path / "reviewer-mutants")))
    runs = {"A": [], "B": [{"run": "run-002", "identityPass": True,
                            "suitePath": "/tmp/s.rego", "scoredCases": []}],
            "C": []}
    published = reviewer.execute(None, sealed, runs, {}, ("A", "B", "C"),
                                 {"A": "jps", "B": "rego", "C": "rego"},
                                 str(tmp_path))
    assert published["perArm"]["B"]["perRun"][0]["refused"] == ["r-b-001"]


def test_the_published_block_says_it_moves_nothing(tmp_path, monkeypatch):
    from e4lib import e4
    monkeypatch.setattr(e4, "kill_arm_rego", lambda *a, **k: (e4.SURVIVED, {}))
    sealed = reviewer.load(str(sealed_tree(tmp_path / "reviewer-mutants")))
    published = reviewer.execute(None, sealed, {"A": [], "B": [], "C": []}, {},
                                 ("A", "B", "C"),
                                 {"A": "jps", "B": "rego", "C": "rego"},
                                 str(tmp_path))
    assert "moving nothing" in published["movesNothing"]
    assert published["manifestSha256"].startswith("sha256:")
