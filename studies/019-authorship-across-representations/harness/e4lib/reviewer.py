"""The sealed reviewer mutant set — loaded and schema-checked before the
attempt, executed exactly once AT the attempt, published on its own.

ROUND-1 FINDING R1-10, which was that none of that existed. §1a registers the
reviewer set as this study's only prospective reviewer-authored content —
"authored during review rounds, committed verbatim, first executed at the
primary attempt, scored 'as authored', reported separately, moving nothing" —
and the flag `--include-reviewer-set` reached `ATTEMPT.json` and a null-pin guard
and nothing else. No code loaded the set, executed it, or reported it, and
`reviewerMutantSet` was not in the freeze set, so a REGISTERED attempt was
reachable with the pin still null.

Five properties, each of them a line in that registration:

* **Mandatory for REGISTERED.** `harness/score.py` refuses to publish a
  REGISTERED attempt without the flag, and `integrity.FREEZE_PINS` now carries
  `reviewerMutantSet`, so the label rule cannot be satisfied while the set's
  digest is null.
* **Validated without being executed.** `load()` reads the manifest, checks its
  schema, and verifies every payload against its recorded digest and against the
  registry pin. It runs no engine. That is what makes "first executed at the
  primary attempt" checkable rather than promised: the pre-attempt path has no
  execution in it to accidentally take.
* **Validated against the schema that was AUTHORED, and BEFORE any endpoint.**
  Round-2 finding R2-7, in two halves. The loader checked four member NAMES and
  nothing else, so a set with two mutants, one language, an extra member, a
  `.txt` payload or a filename naming another directory loaded clean — and its
  containment check was `dirname(normpath(file)).startswith("..")`, which an
  ABSOLUTE path passes, because `dirname("/x")` is `"/"` and
  `os.path.join(root, "/x")` is `"/x"`. The round's own prompt registers 6–10
  mutants with both languages represented, records of exactly
  `{id, language, file, sha256}`, and filenames `rm-<language>-NN.<ext>`; all of
  it is enforced here now, on real paths. **Round-9 finding R9-4** is the half of
  that sentence which was still a sentence: the filename check compared `file`
  with `id + extension` and validated the ID against nothing, so all six records
  renamed to `not-authored-*` — with the payload hashes and the manifest pin
  recomputed — passed closure, both freeze gates and `--check`. The id is
  matched against `ID_PATTERN` now, with its language segment bound to the
  record's `language`, and the manifest is decoded with the house
  duplicate-member hook, so a second `reviewerSetVersion` is a refusal rather
  than last-one-wins. And `harness/score.py` calls this
  BEFORE it computes an endpoint, with any failure terminating the attempt as
  pipeline-invalid: the load used to sit after the decision, with its refusal
  caught into `refusals` and the attempt still exiting 0, so a missing or
  digest-invalid mandatory holdout could coexist with a published substantive
  verdict.
* **Executed exactly once.** `execute()` refuses a second call on the same
  record. The attempt is a single process and the scorer calls it once, and the
  guard is there because "first executed at the primary attempt" is a claim
  about a count.
* **Published separately.** Its results land under `reviewerSet` in
  `RESULTS.json` and in their own section of `RESULTS.md`, never inside E4.
* **No R1 dependency.** The decision is computed from an outcome dict built by
  `harness/score.py` out of exactly `pipelineProblems`, `shortfallDeclared`,
  `controlGates` and `contrasts`; nothing here reaches any of them.
  `tests/test_score_attempt.py` asserts the independence structurally rather
  than by inspection.

**Scored "as authored".** A reviewer mutant is run against each admitted,
identity-passing run's own suite through the SAME kill machinery the registered
mutants use, and the outcome is reported. No reviewer mutant is paired, none
enters a witness group, none moves a cut, and a reviewer mutant the engine
refuses on is a refusal here exactly as it is there.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

from . import e4

MANIFEST_NAME = "MANIFEST.json"
SET_VERSION = 1
LANGUAGES = ("jps", "rego")
RECORD_MEMBERS = ("id", "language", "file", "sha256")

# ROUND-9 FINDING R9-4. The registered filename, as a pattern rather than as a
# sentence in a prompt. `reviews/round-2/PROMPT.md` registers the sealed set's
# filenames as `rm-<language>-NN.<ext>` and names the instances
# (`rm-jps-01.json`, `rm-rego-01.rego`, …); the loader checked only that `file`
# equalled `id + extension`, which is a check on the AGREEMENT of two authored
# strings and not on either of them. The id was never validated at all, so the
# reviewer renamed all six records to `not-authored-*`, recomputed the payload
# hashes and the manifest pin, and passed closure, `--freeze-gates`, `--freeze`
# and `--check`. `<language>` is BOUND here — the id's own language segment must
# be the record's `language` — because `rm-rego-01.json` declared `jps` is a
# filename that satisfies the shape and misnames the thing it seals.
#
# `\A` and `\Z` rather than `^` and `$`: Python's `$` matches BEFORE a trailing
# newline, so `^rm-(jps|rego)-[0-9]{2}$` — the pattern as the finding wrote it —
# admits `"rm-jps-01\n"`, which is a different string from the registered id and
# names a different file. Verified rather than assumed: the newline id is one of
# the constructions in `tests/test_score_reviewer.py`.
ID_PATTERN = re.compile(r"\Arm-(jps|rego)-[0-9]{2}\Z")
ID_SHAPE = "rm-<language>-NN"

# THE AUTHORED SCHEMA, as the round's own prompt registers it and as the
# reviewer emitted it (round-2 finding R2-7). The loader used to check the four
# member NAMES and nothing else, so a set with two mutants, one language, an
# extra member, a `.txt` payload or a filename naming another directory loaded
# clean — and the round-1 disposition's "loader validates" was true of a schema
# nobody authored.
MANIFEST_MEMBERS = ("reviewerSetVersion", "mutants")
SET_MINIMUM, SET_MAXIMUM = 6, 10
EXTENSION_OF_LANGUAGE = {"jps": ".json", "rego": ".rego"}


class ReviewerSetError(Exception):
    """A refusal about the sealed set, with a named code as its first word."""


def _digest(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _bare(value) -> str:
    return value.split(":")[-1] if isinstance(value, str) else value


def _refuse_duplicate_keys(pairs):
    """ROUND-9 FINDING R9-4, second half, in the house idiom
    (`harness/transcript_check.py`, `harness/score.py`, `harness/integrity.py`,
    `harness/grid_gate.py`, `harness/render_round_status.py`).

    The sealed manifest was read with the ordinary decoder, which resolves a
    repeated member by last-one-wins and says nothing: a manifest carrying two
    `reviewerSetVersion` members — or two `sha256` members in one record —
    loaded clean, and a human reading the file saw the FIRST one while the
    loader checked the second. A sealed set is what was authored, and a file
    readable two ways is not one document. The hook runs on every object the
    decoder builds, so it is not a top-level courtesy."""
    keys = [key for key, _ in pairs]
    if len(set(keys)) != len(keys):
        duplicated = sorted({key for key in keys if keys.count(key) > 1})
        raise ValueError("the member(s) %s appear twice in one object"
                         % ", ".join(repr(key) for key in duplicated))
    return dict(pairs)


def load(root: str, pinned_sha256=None) -> dict:
    """The sealed set, validated and NOT executed.

    `root` is the study-relative directory the registry names
    (`reviewerMutantSet.path`). `pinned_sha256` is the registry's digest OVER THE
    MANIFEST; when it is non-null the manifest must hash to it, which is what
    binds the executed bytes to the freeze."""
    manifest_path = os.path.join(root, MANIFEST_NAME)
    if not os.path.isdir(root):
        raise ReviewerSetError(
            "REVIEWER-SET-ABSENT the registered reviewer mutant directory does "
            "not exist; §1a registers the set as this study's only prospective "
            "reviewer-authored content and a registered attempt executes it")
    if not os.path.isfile(manifest_path):
        raise ReviewerSetError(
            "REVIEWER-SET-ABSENT the reviewer mutant set carries no %s"
            % MANIFEST_NAME)
    if pinned_sha256 is not None and _digest(manifest_path) != _bare(pinned_sha256):
        raise ReviewerSetError(
            "REVIEWER-SET-DIGEST the sealed manifest does not hash to the digest "
            "harness/PINS.json records for it: the set executed at the attempt "
            "is bound to the freeze by that digest and by nothing else")
    with open(manifest_path, "rb") as handle:
        try:
            manifest = json.loads(handle.read().decode("utf-8"),
                                  object_pairs_hook=_refuse_duplicate_keys)
        except (ValueError, UnicodeDecodeError) as error:
            raise ReviewerSetError(
                "REVIEWER-SET-SCHEMA the sealed manifest is not readable "
                "duplicate-free JSON (%s: %s)"
                % (type(error).__name__, error))
    if not isinstance(manifest, dict):
        raise ReviewerSetError(
            "REVIEWER-SET-SCHEMA the sealed manifest is a JSON %s and the "
            "registered shape is an object" % type(manifest).__name__)
    if manifest.get("reviewerSetVersion") != SET_VERSION:
        raise ReviewerSetError(
            "REVIEWER-SET-SCHEMA reviewerSetVersion is %r and this study "
            "registers %d" % (manifest.get("reviewerSetVersion"), SET_VERSION))
    records = manifest.get("mutants")
    if not isinstance(records, list) or not records:
        raise ReviewerSetError(
            "REVIEWER-SET-SCHEMA the sealed manifest carries no non-empty "
            "`mutants` list; an empty sealed set is not a set the attempt can "
            "report as authored")
    extra = sorted(set(manifest) - set(MANIFEST_MEMBERS))
    if extra:
        raise ReviewerSetError(
            "REVIEWER-SET-SCHEMA the sealed manifest carries the member(s) %s "
            "and the registered manifest is exactly %s: a sealed set is what "
            "was authored, and an unregistered member is a member nothing "
            "checked" % (", ".join(extra), ", ".join(MANIFEST_MEMBERS)))
    if not SET_MINIMUM <= len(records) <= SET_MAXIMUM:
        raise ReviewerSetError(
            "REVIEWER-SET-SCHEMA the sealed manifest lists %d mutants and the "
            "registered set is %d-%d: the cardinality is part of what was "
            "authored, not a courtesy"
            % (len(records), SET_MINIMUM, SET_MAXIMUM))
    root_real = os.path.realpath(root)
    seen, loaded = set(), []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ReviewerSetError(
                "REVIEWER-SET-SCHEMA record %d is a JSON %s and a record is an "
                "object" % (index, type(record).__name__))
        missing = [member for member in RECORD_MEMBERS
                   if not isinstance(record.get(member), str)]
        if missing:
            raise ReviewerSetError(
                "REVIEWER-SET-SCHEMA record %d is missing the string member(s) "
                "%s" % (index, ", ".join(missing)))
        surplus = sorted(set(record) - set(RECORD_MEMBERS))
        if surplus:
            raise ReviewerSetError(
                "REVIEWER-SET-SCHEMA record %d carries the member(s) %s and a "
                "registered record is exactly %s"
                % (index, ", ".join(surplus), ", ".join(RECORD_MEMBERS)))
        if record["language"] not in LANGUAGES:
            raise ReviewerSetError(
                "REVIEWER-SET-SCHEMA %s names the language %r and the registered "
                "languages are %s"
                % (record["id"], record["language"], ", ".join(LANGUAGES)))
        # ROUND-9 FINDING R9-4: the registered id, checked against the pattern
        # the round-2 prompt registers rather than only against its own
        # extension. `match` is anchored at both ends by the pattern itself, so
        # a trailing newline or a path segment is a refusal and not a suffix.
        matched = ID_PATTERN.match(record["id"])
        if matched is None:
            raise ReviewerSetError(
                "REVIEWER-SET-SCHEMA record %d names the id %r and the "
                "registered sealed-set id is %s with NN two digits and "
                "<language> one of %s (reviews/round-2/PROMPT.md): a set whose "
                "members are not the ones that were authored is not the sealed "
                "set" % (index, record["id"], ID_SHAPE, ", ".join(LANGUAGES)))
        if matched.group(1) != record["language"]:
            raise ReviewerSetError(
                "REVIEWER-SET-SCHEMA %s names the language %r and its own id "
                "spells %r: the registered filename is %s.<ext>, so the id's "
                "language segment and the record's language are one fact and "
                "not two" % (record["id"], record["language"], matched.group(1),
                             ID_SHAPE))
        if record["id"] in seen:
            raise ReviewerSetError(
                "REVIEWER-SET-SCHEMA the id %r appears twice; a set with two "
                "members of one name has no per-mutant result" % record["id"])
        seen.add(record["id"])
        # CONTAINMENT, on real paths (round-2 R2-7). The check was
        # `dirname(normpath(file)).startswith("..")`, and `dirname("/x")` is
        # `"/"` — so an ABSOLUTE path passed it, and `os.path.join(root, "/x")`
        # is `"/x"`, which leaves the sealed directory entirely. A member is a
        # bare filename inside the sealed directory or it is not a member.
        registered_name = record["id"] + EXTENSION_OF_LANGUAGE[record["language"]]
        if record["file"] != registered_name:
            raise ReviewerSetError(
                "REVIEWER-SET-SCHEMA %s names the file %r and the registered "
                "filename for a %s mutant of that id is %r"
                % (record["id"], record["file"], record["language"],
                   registered_name))
        path = os.path.join(root, record["file"])
        if os.path.commonpath([root_real, os.path.realpath(path)]) != root_real:
            raise ReviewerSetError(
                "REVIEWER-SET-SCHEMA %s resolves outside the sealed directory"
                % record["id"])
        if not os.path.isfile(path):
            raise ReviewerSetError(
                "REVIEWER-SET-ABSENT %s names %s, which is not a file"
                % (record["id"], record["file"]))
        actual = _digest(path)
        if actual != _bare(record["sha256"]):
            raise ReviewerSetError(
                "REVIEWER-SET-DIGEST %s hashes to sha256:%s and the sealed "
                "manifest records sha256:%s: the set is executed as sealed or "
                "not at all" % (record["id"], actual, _bare(record["sha256"])))
        loaded.append({"id": record["id"], "language": record["language"],
                       "path": path, "sha256": actual})
    languages = sorted({record["language"] for record in loaded})
    if languages != sorted(LANGUAGES):
        raise ReviewerSetError(
            "REVIEWER-SET-SCHEMA the sealed set represents %s and the "
            "registered set represents both languages: a set that reaches one "
            "arm's language is not the holdout that was authored"
            % (", ".join(languages) or "no language"))
    return {"version": SET_VERSION, "manifestSha256": _digest(manifest_path),
            "mutants": loaded, "count": len(loaded),
            "executed": False,
            "note": "loaded and schema-checked; no engine has been invoked"}


def execute(tools, sealed: dict, per_arm_runs: dict, context: dict,
            arms, language_of_arm: dict, workdir: str) -> dict:
    """Run the sealed set against every admitted identity-passing suite, once.

    "Scored as authored": the same kill machinery, the same refusal routing, no
    pairing, no cut, no contribution to any registered rate."""
    if sealed.get("executed"):
        raise ReviewerSetError(
            "REVIEWER-SET-RE-EXECUTED the sealed set is executed exactly once, "
            "at the primary attempt; a second execution is not what §1a "
            "registers and its result would not be the first")
    sealed["executed"] = True
    per_arm = {}
    for arm in arms:
        language = language_of_arm[arm]
        members = [record for record in sealed["mutants"]
                   if record["language"] == language]
        rows = []
        for run in per_arm_runs.get(arm) or []:
            if not run.get("identityPass") or not run.get("suitePath"):
                continue
            outcomes = {}
            for record in members:
                if language == "jps":
                    outcome, _detail = e4.kill_arm_a(
                        tools, record["path"], run["scoredCases"], workdir)
                else:
                    outcome, _detail = e4.kill_arm_rego(
                        tools, record["path"], run["suitePath"], workdir)
                outcomes[record["id"]] = outcome
            rows.append({
                "run": run["run"],
                "killed": sorted(mutant for mutant, outcome in outcomes.items()
                                 if outcome == e4.KILLED),
                "survived": sorted(mutant for mutant, outcome in outcomes.items()
                                   if outcome == e4.SURVIVED),
                "refused": sorted(mutant for mutant, outcome in outcomes.items()
                                  if outcome == e4.REFUSED),
            })
        per_arm[arm] = {
            "arm": arm, "language": language,
            "reviewerMutants": len(members),
            "scoredRuns": len(rows),
            "perRun": rows,
        }
    return {
        "version": sealed["version"],
        "manifestSha256": "sha256:" + sealed["manifestSha256"],
        "reviewerMutants": sealed["count"],
        "perArm": per_arm,
        "movesNothing": "§1a: scored as authored, reported separately, moving "
                        "nothing. No number in this block enters E1-E5, any "
                        "control gate, any contrast, or the decision rule.",
    }
