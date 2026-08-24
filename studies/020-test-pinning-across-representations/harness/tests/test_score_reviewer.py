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


# The AUTHORED shape (round-2 R2-7): six mutants, both languages, filenames
# `rm-<language>-NN.<registered extension>`, and records carrying exactly the
# four registered members. The old fixture was two mutants named `r-a-001`
# with an extra `authoredBy` member and a `sealedAt` beside the list — none of
# which the round's own prompt registers, and all of which the loader accepted.
DEFAULT_MUTANTS = [
    ("rm-jps-01", "jps", "rm-jps-01.json", '{"specVersion": "0.2.0-draft"}\n'),
    ("rm-jps-02", "jps", "rm-jps-02.json", '{"specVersion": "0.2.1-draft"}\n'),
    ("rm-jps-03", "jps", "rm-jps-03.json", '{"specVersion": "0.2.2-draft"}\n'),
    ("rm-rego-01", "rego", "rm-rego-01.rego", "package study\n"),
    ("rm-rego-02", "rego", "rm-rego-02.rego", "package study\n# two\n"),
    ("rm-rego-03", "rego", "rm-rego-03.rego", "package study\n# three\n"),
]


def sealed_tree(root, *, mutants=None, edits=None, manifest=None):
    root.mkdir(parents=True, exist_ok=True)
    mutants = mutants if mutants is not None else DEFAULT_MUTANTS
    records = []
    for identifier, language, filename, body in mutants:
        (root / filename).write_text(body)
        records.append({
            "id": identifier, "language": language, "file": filename,
            "sha256": hashlib.sha256(body.encode()).hexdigest(),
        })
    document = manifest if manifest is not None else {
        "reviewerSetVersion": reviewer.SET_VERSION,
        "mutants": records,
    }
    if edits:
        document.update(edits)
    (root / reviewer.MANIFEST_NAME).write_text(json.dumps(document))
    return root


def records_of(root):
    return json.loads((root / reviewer.MANIFEST_NAME).read_text())["mutants"]


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
    assert loaded["count"] == 6
    assert loaded["executed"] is False
    assert "no engine has been invoked" in loaded["note"]
    assert sorted(set(record["language"] for record in loaded["mutants"])) == \
        ["jps", "rego"]


def test_the_manifest_digest_binds_the_executed_bytes_to_the_freeze(tmp_path):
    sealed = sealed_tree(tmp_path / "reviewer-mutants")
    loaded = reviewer.load(str(sealed))
    assert reviewer.load(str(sealed), loaded["manifestSha256"])["count"] == 6
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed), "sha256:" + "0" * 64)
    assert str(raised.value).startswith("REVIEWER-SET-DIGEST")


def test_a_payload_edited_after_sealing_refuses(tmp_path):
    """"Committed verbatim": the set is executed as sealed or not at all."""
    sealed = sealed_tree(tmp_path / "reviewer-mutants")
    (sealed / "rm-rego-01.rego").write_text("package study\n# edited\n")
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
    # ROUND-2 R2-7: the authored schema, which the loader did not enforce.
    ({"sealedAt": "round-1"}, "REVIEWER-SET-SCHEMA"),
])
def test_every_schema_failure_refuses_by_name(tmp_path, edits, code):
    sealed = sealed_tree(tmp_path / "reviewer-mutants", edits=edits)
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert str(raised.value).startswith(code)


# --- ROUND-2 R2-7: the schema is the one that was AUTHORED ------------------

def test_a_set_below_the_registered_cardinality_refuses(tmp_path):
    """The round's own prompt: "6-10 mutants total, both languages
    represented". The loader accepted two."""
    sealed = sealed_tree(tmp_path / "reviewer-mutants",
                         mutants=DEFAULT_MUTANTS[:2])
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert "6-10" in str(raised.value)


def test_a_set_above_the_registered_cardinality_refuses(tmp_path):
    extra = [("rm-rego-%02d" % index, "rego", "rm-rego-%02d.rego" % index,
              "package study\n# %d\n" % index) for index in range(4, 10)]
    sealed = sealed_tree(tmp_path / "reviewer-mutants",
                         mutants=DEFAULT_MUTANTS + extra)
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert "6-10" in str(raised.value)


def test_a_single_language_set_refuses(tmp_path):
    """"Both languages represented": a set that reaches one arm's language is
    not the holdout that was authored."""
    single = [("rm-rego-%02d" % index, "rego", "rm-rego-%02d.rego" % index,
               "package study\n# %d\n" % index) for index in range(1, 7)]
    sealed = sealed_tree(tmp_path / "reviewer-mutants", mutants=single)
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert "both languages" in str(raised.value)


def test_an_unregistered_record_member_refuses(tmp_path):
    sealed = sealed_tree(tmp_path / "reviewer-mutants")
    records = records_of(sealed)
    records[0]["authoredBy"] = "round-2 reviewer"
    sealed_tree(sealed, edits={"mutants": records},
                manifest={"reviewerSetVersion": reviewer.SET_VERSION,
                          "mutants": records})
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert "authoredBy" in str(raised.value)


@pytest.mark.parametrize("filename", ["rm-jps-01.rego", "rm-jps-01.txt",
                                      "rm-jps-99.json", "other/rm-jps-01.json"])
def test_a_filename_that_is_not_the_registered_one_refuses(tmp_path, filename):
    """Filename/extension consistency: a `jps` mutant is `<id>.json` and a
    `rego` mutant is `<id>.rego`, and the id names the file."""
    sealed = sealed_tree(tmp_path / "reviewer-mutants")
    records = records_of(sealed)
    records[0]["file"] = filename
    (sealed / reviewer.MANIFEST_NAME).write_text(json.dumps(
        {"reviewerSetVersion": reviewer.SET_VERSION, "mutants": records}))
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert str(raised.value).startswith("REVIEWER-SET-SCHEMA")


def test_an_absolute_path_does_not_escape_the_sealed_directory(tmp_path):
    """THE REVIEWER'S R2-7 CONSTRUCTION. The containment check was
    `dirname(normpath(file)).startswith("..")` — and `dirname("/x")` is `"/"`,
    which does not start with `..`, while `os.path.join(root, "/x")` is `"/x"`.
    An absolute path therefore passed containment and was read from outside the
    sealed set entirely."""
    outside = tmp_path / "outside.json"
    outside.write_text('{"specVersion": "0.2.0-draft"}\n')
    sealed = sealed_tree(tmp_path / "reviewer-mutants")
    records = records_of(sealed)
    records[0]["file"] = str(outside)
    records[0]["sha256"] = hashlib.sha256(outside.read_bytes()).hexdigest()
    (sealed / reviewer.MANIFEST_NAME).write_text(json.dumps(
        {"reviewerSetVersion": reviewer.SET_VERSION, "mutants": records}))
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert str(raised.value).startswith("REVIEWER-SET-SCHEMA")


def test_two_members_of_one_name_refuse(tmp_path):
    body = "package study\n"
    digest = hashlib.sha256(body.encode()).hexdigest()
    duplicate = {"id": "rm-rego-01", "language": "rego",
                 "file": "rm-rego-01.rego", "sha256": digest}
    sealed = sealed_tree(tmp_path / "reviewer-mutants",
                         edits={"mutants": [duplicate] * 6})
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert "appears twice" in str(raised.value)


# --- ROUND-9 FINDING R9-4: the registered id, not only the agreeing pair -----

# Every one of these is a `file` that equals `id + <the registered extension for
# the declared language>`, which is the whole of what the loader used to check.
# The first is the reviewer's own construction, run at the size it was run at
# (all six records renamed) in the test below; the rest are the shape's edges.
NON_CONFORMING_IDS = [
    "not-authored-01",          # the construction: nothing about it is `rm-…`
    "rm-jps-1",                 # NN is TWO digits
    "rm-jps-001",               # …and exactly two
    "RM-JPS-01",                # the registered id is lower case
    "rm-jps-0a",                # NN is digits
    "rm-jps-01 ",               # a trailing space is a different filename
    "rm-jps-01\n",              # `$` matches before a trailing newline; `\Z` does not
    " rm-jps-01",
    "rm-json-01",               # a language segment that is not a language
    "rm-jps-01-extra",
]


@pytest.mark.parametrize("identity", NON_CONFORMING_IDS)
def test_an_id_outside_the_registered_pattern_refuses(tmp_path, identity):
    """R9-4. `reviews/round-2/PROMPT.md` registers the sealed set's filenames as
    `rm-<language>-NN.<ext>`; the loader required only `file == id + extension`
    and validated the id against nothing, so any pair of agreeing strings was a
    member. Each id here agrees with its own filename and is not the registered
    shape, and each must refuse — including the two that a `^…$` pattern admits
    and a `\\A…\\Z` one does not."""
    extension = reviewer.EXTENSION_OF_LANGUAGE["jps"]
    body = '{"specVersion": "0.2.0-draft"}\n'
    mutants = [(identity, "jps", identity + extension, body)] \
        + DEFAULT_MUTANTS[1:]
    sealed = sealed_tree(tmp_path / "reviewer-mutants", mutants=mutants)
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert str(raised.value).startswith("REVIEWER-SET-SCHEMA")
    assert "rm-<language>-NN" in str(raised.value)


def test_the_authored_ids_load_so_the_pattern_is_strictness_not_obstruction(
        tmp_path):
    """The other direction, without which the parametrization above proves only
    that something refuses: the conforming set — both languages, `NN` from `01`
    to `10`, which is the registered cardinality's ceiling — loads."""
    conforming = [("rm-jps-%02d" % index, "jps", "rm-jps-%02d.json" % index,
                   '{"specVersion": "0.2.%d-draft"}\n' % index)
                  for index in (1, 7, 10)] \
        + [("rm-rego-%02d" % index, "rego", "rm-rego-%02d.rego" % index,
            "package study\n# %d\n" % index) for index in (2, 9, 10)]
    sealed = sealed_tree(tmp_path / "reviewer-mutants", mutants=conforming)
    assert reviewer.load(str(sealed))["count"] == 6


def test_the_whole_set_renamed_still_refuses(tmp_path):
    """The construction as the reviewer ran it: ALL SIX records renamed to
    `not-authored-*`, with every payload hash recomputed over its real bytes and
    the manifest internally consistent. It passed closure, `--freeze-gates`,
    `--freeze` and `--check`, because nothing anywhere held the authored names."""
    renamed = [("not-authored-%s" % identity.split("-", 1)[1], language,
                "not-authored-%s%s" % (identity.split("-", 1)[1],
                                       filename[filename.rindex("."):]), body)
               for identity, language, filename, body in DEFAULT_MUTANTS]
    sealed = sealed_tree(tmp_path / "reviewer-mutants", mutants=renamed)
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert str(raised.value).startswith("REVIEWER-SET-SCHEMA")


def test_the_ids_language_segment_is_bound_to_the_records_language(tmp_path):
    """A conforming SHAPE that misnames the thing it seals: `rm-rego-04`
    declared `jps`, with the `.json` extension its declared language registers,
    so `file == id + extension` holds exactly. The id's language segment and the
    record's `language` are one fact."""
    body = '{"specVersion": "0.2.0-draft"}\n'
    mutants = [("rm-rego-04", "jps", "rm-rego-04.json", body)] \
        + DEFAULT_MUTANTS[1:]
    sealed = sealed_tree(tmp_path / "reviewer-mutants", mutants=mutants)
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert "one fact and not two" in str(raised.value)


@pytest.mark.parametrize("injection,where", [
    ('"reviewerSetVersion": 1, "reviewerSetVersion": 2', "the top level"),
    ('"id": "rm-jps-01", "id": "rm-jps-02"', "one record"),
])
def test_a_duplicate_member_in_the_sealed_manifest_refuses(tmp_path, injection,
                                                           where):
    """R9-4's second half. The sealed manifest was read with the ordinary
    decoder, which resolves a repeated member last-one-wins and says nothing, so
    a manifest a human reads one way and the loader reads another loaded clean.
    The house hook (`transcript_check`, `score`, `integrity`, `grid_gate`,
    `render_round_status`) runs at every depth, which is why the nested case
    refuses too."""
    sealed = sealed_tree(tmp_path / "reviewer-mutants")
    manifest = sealed / reviewer.MANIFEST_NAME
    text = manifest.read_text()
    original, _, replacement = injection.partition(", ")
    assert original in text, (text[:120], where)
    manifest.write_text(text.replace(original, injection, 1))
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed))
    assert "duplicate-free" in str(raised.value), where


# --- ROUND-10 FINDING R10-3: the version is TYPE-exact, not value-equal -----

@pytest.mark.parametrize("literal", ["true", "1.0", "1e0", "1E0", '"1"'])
def test_a_mistyped_reviewer_set_version_refuses(tmp_path, literal):
    """R10-3. The authored schema (`reviews/round-2/PROMPT.md`) specifies
    `"reviewerSetVersion": 1` — a JSON integer — and the loader asked only
    `!= SET_VERSION`, which Python satisfies with `True`, `1.0` and `1e0`
    alike. The reviewer substituted each of them into the REAL sealed manifest,
    re-pinned it, and `load()` returned a set whose published `version` is the
    constant integer 1, so the object hid the type its own source carried.

    The literals are written as TEXT, not through `json.dumps`: `1e0` and `1E0`
    are JSON numbers that no Python value round-trips to, and the finding is
    about what a sealed FILE may say. `true` is the one a bare
    `isinstance(x, int)` would still admit, because `bool` subclasses `int`."""
    sealed = sealed_tree(tmp_path / "reviewer-mutants")
    manifest = sealed / reviewer.MANIFEST_NAME
    text = manifest.read_text()
    original = '"reviewerSetVersion": 1'
    assert original in text, text[:120]
    manifest.write_text(text.replace(original,
                                     '"reviewerSetVersion": %s' % literal, 1))

    # the digest pin moves with the edit, exactly as the reviewer moved it, so
    # nothing but the type check can be what refuses
    pinned = "sha256:" + hashlib.sha256(manifest.read_bytes()).hexdigest()
    with pytest.raises(reviewer.ReviewerSetError) as raised:
        reviewer.load(str(sealed), pinned)
    assert str(raised.value).startswith("REVIEWER-SET-SCHEMA")
    assert "reviewerSetVersion" in str(raised.value)


def test_the_registered_integer_version_still_loads(tmp_path):
    """The other direction: `1` as an integer is the authored member and loads,
    so R10-3's check is exactness and not obstruction."""
    sealed = sealed_tree(tmp_path / "reviewer-mutants")
    assert '"reviewerSetVersion": 1,' in \
        (sealed / reviewer.MANIFEST_NAME).read_text()
    assert reviewer.load(str(sealed))["version"] == reviewer.SET_VERSION


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
    runs = {"A": [{"run": "run-001", "referenceIdentityPass": True,
                   "suitePath": "/tmp/suite.json", "scoredCases": []}],
            "B": [{"run": "run-002", "referenceIdentityPass": True,
                   "suitePath": "/tmp/suite.rego", "scoredCases": []}],
            "C": []}
    published = reviewer.execute(None, sealed, runs, {}, ("A", "B", "C"),
                                {"A": "jps", "B": "rego", "C": "rego"},
                                str(tmp_path))
    assert published["reviewerMutants"] == 6
    assert published["perArm"]["A"]["perRun"][0]["killed"] == \
        ["rm-jps-01", "rm-jps-02", "rm-jps-03"]
    assert published["perArm"]["B"]["perRun"][0]["survived"] == \
        ["rm-rego-01", "rm-rego-02", "rm-rego-03"]
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
    runs = {"A": [], "B": [{"run": "run-002", "referenceIdentityPass": False,
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
    runs = {"A": [], "B": [{"run": "run-002", "referenceIdentityPass": True,
                            "suitePath": "/tmp/s.rego", "scoredCases": []}],
            "C": []}
    published = reviewer.execute(None, sealed, runs, {}, ("A", "B", "C"),
                                 {"A": "jps", "B": "rego", "C": "rego"},
                                 str(tmp_path))
    assert published["perArm"]["B"]["perRun"][0]["refused"] == \
        ["rm-rego-01", "rm-rego-02", "rm-rego-03"]


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
