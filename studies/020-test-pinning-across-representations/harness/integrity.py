#!/usr/bin/env python3
"""The port chain and the pin registry in code: verified before any call and
any count — WHOLE-HARNESS PORT.

PORTED from Study 019's `harness/integrity.py`
(sha256 `ba2175ad213abcd019e10dc7768aa16f5bcb7f52f77c5af1520c942fc81657e3`, the
line Study 019's own frozen `harness/STUDY-MANIFEST.sha256` carries for it).
Study 019 inherited this file from Study 012 as a PARTIAL port of seven files;
Study 020 inherits Study 019's whole harness, so the shape of the check is the
same and the SET it ranges over is the whole machinery `PREREGISTRATION.md` §7
enumerates. What was taken, what changed and what was deliberately left behind
is in this study's `harness/PORTS.md`, whose table this module machine-reads.

**The chain, one level and every link a pinned digest — and the source study's
LOCK is the authority, not a hand-copied table.** Study 019 bound its seven
rows to Study 012's `PORTS.md` DESTINATION cells, because those seven were all
012 published a digest for. Study 019 is FROZEN and publishes a digest for
every byte of its harness and every registered artifact, in one file, pinned by
its own registry: `harness/STUDY-MANIFEST.sha256`. That file is this port's
source-side authority.

```
this file                          (pinned in harness/PINS.json at port time)
    -> Study 019's harness/PINS.json              9ba6394d…  (pinned below, and
                                                              in PINS.json)
       Study 019's harness/STUDY-MANIFEST.sha256  79076e31…  (the digest 019's
                                                              OWN registry pins
                                                              for it, read from
                                                              it and not chosen
                                                              here)
```

`verify_chain()` therefore, in order: verifies Study 019's `harness/PINS.json`
against the digest this file pins for it; verifies Study 019's
`harness/STUDY-MANIFEST.sha256` against the digest **019's own registry**
records for it under `studyManifest` (not a digest this study chooses); verifies
THIS study's `harness/PORTS.md` against the digest this study's
`harness/PINS.json` records for it, so the file that says what each enumerated
change *was* cannot be rewritten after the review; and then binds each row of
the port table to the authority that row actually has — every ported harness
file to 019's own manifest line for it, on both sides.

`verify_ported_artifacts()` is the same binding for the registered artifacts
§4.1 ports by digest — the policy prose, the gold suite, both mutant manifests
and every mutant payload, both references, the off-gold certificate and the two
verification documents. They are NOT rows in `PORTS.md`: 019's lock already
publishes a digest for each of them under the same study-relative path, so a
second transcription of those digests into a table here would be a copy that
can drift from the lock it claims to quote. The three arm prompts are bound to
019's REGISTRY (`arms.<ARM>.promptSha256`) instead, because 019's manifest does
not cover them and its registry does.

**What is NOT carried, said plainly so §7 cannot claim it.** Study 019's
reviewer mutant set is spent and does not carry (§4.3): 020 registers a fresh
sealed set, and `controls/reviewer-mutants/` is absent here until it is
authored. Study 019's pilot (`design/pilots/`) does not carry either — §2a.1
registers five differences that make it unreusable — and neither does
`design/pilot/pilot_run.py` (§7 delta 12) or 019's own end-to-end smoke
transcript, which is 019's evidence and not 020's. The `design/` working tree
IS carried, and it is carried UNPINNED: 019's manifest covers no path under
`design/`, so the recorded port commit is the whole of that carry's source-side
binding and `harness/PORTS.md` says so in prose rather than pretending to a
digest. This study's manifest is ADR 0004's **exact-set** manifest
(`harness/make_manifest.py`, `harness/STUDY-MANIFEST.sha256`, pinned as
`studyManifest`), scoped per §7 delta 11.

**Stage-aware by design.** Every freeze pin in `harness/PINS.json` is null
until the freeze, and `study_label()` — not a comment — is what makes that
visible: any null freeze pin labels the run **PILOT**, and only a registry
whose every freeze pin is non-null labels it REGISTERED. The toolchain blocks
(`jpack`, `opa`, `codex`, `python`) are resolved at design time and carry
digests already; they are marked `resolvedAtDesignTime` and are enforced under
both labels.
"""


from __future__ import annotations
import hashlib
import json
import os
import platform
import re
import subprocess
import sys

# The ceremony's commands run with bytecode writing disabled: set structurally,
# not left to the operator's environment. This file is invoked by path, so it is
# one of those commands — the flag belongs in every entry the ceremony names,
# not in one.
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
# The one source study. Study 020 takes its whole harness and its registered
# artifacts from Study 019 and from nowhere else, so there is one sibling here
# and not two.
NINETEEN = os.path.normpath(
    os.path.join(STUDY, "..", "019-authorship-across-representations"))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# The chain's two ends, pinned here in reviewed code. Study 019's registry
# digest is this file's; the digest of 019's LOCK is NOT here — it is read from
# 019's own registry, which is what "the digest 019 pins for it, not one this
# study chooses" means in code.
NINETEEN_PINS_SHA256 = \
    "9ba6394db66f0e3723359c17f68e4a612870a015f3f973e1efad10fd522a759c"
# The source study's lock, by the member its registry records it under.
NINETEEN_LOCK_PIN = "studyManifest"
NINETEEN_LOCK_PATH = "harness/STUDY-MANIFEST.sha256"
# The commit the port was taken at. Every harness row and every registered
# artifact is bound to 019's own lock, which is stronger than a commit; the
# `design/` working tree is bound to this commit and to nothing older, because
# 019's manifest covers no path under `design/`. `harness/PORTS.md` records that
# in its own authority column.
PORT_COMMIT = "e87e1311da11c28e929edf1e7e39f048e4ec0e6a"

ARMS = ("A", "B", "C")

# The port table's registered destination set. A row deleted from PORTS.md is a
# check silently dropped, so the set must be exact — and a row ADDED must be as
# loud, which is why the set is registered here rather than discovered from the
# table. This is §7's "ported with no design change" list at file granularity:
# every byte of the harness that runs.
REQUIRED_PORTS = frozenset(
    ["harness/" + name for name in (
        "authoring_call.sh", "batch.py", "grid_gate.py", "integrity.py",
        "leak_tokens.py", "make_manifest.py", "render_round_status.py",
        "score.py", "transcript_check.py")]
    + ["harness/e4lib/" + name for name in (
        "__init__.py", "admit.py", "capabilities.py", "census.py",
        "decision.py", "domain.py", "e4.py", "engines.py", "extract.py",
        "reviewer.py", "stats.py")]
    + ["harness/tests/" + name for name in (
        "conftest.py", "test_batch.py", "test_census_replication.py",
        "test_design_regeneration.py", "test_grid_gate.py",
        "test_leak_tokens.py", "test_manifest.py", "test_partition.py",
        "test_pins.py", "test_ports_chain.py", "test_prereg_currency.py",
        "test_schedule.py", "test_score_admit.py", "test_score_attempt.py",
        "test_score_capabilities.py", "test_score_census.py",
        "test_score_decision.py", "test_score_domain.py", "test_score_e4.py",
        "test_score_engines.py", "test_score_extract.py",
        "test_score_pipeline.py", "test_score_publication.py",
        "test_score_reviewer.py", "test_score_stats.py",
        "test_transcript_binding.py")])

# NEW IN 020 — files with NO source-side row, because there is no source-side
# file. §7's deltas 3 and 5 register new machinery (`presence-idiom-unsound` and
# the eighteen-member family scorer), and new machinery cannot be ported by
# digest from a study that never had it.
#
# This set is not a relaxation of the exact-set property, it is the second half
# of it. `REQUIRED_PORTS` alone would have made "add a harness file and register
# it nowhere" invisible the moment any file legitimately had no row; keeping the
# two sets disjoint and checking the union against the directory keeps the
# original failure — a harness file nobody registered — loud. `verify_chain()`
# adds the property that makes membership here CHECKABLE rather than declared:
# Study 019's lock must not name the path. A file 019 does have is a file this
# study owes a row for, and calling it new does not make it new.
NEW_IN_020 = frozenset((
    "harness/e4lib/family.py",
    "harness/e4lib/presence_idiom.py",
    "harness/tests/test_family.py",
    "harness/tests/test_presence_idiom.py",
))

# Every harness file that runs, ported or new. `verify_chain()` checks THIS
# against the directory, so the two sets are exhaustive together and the
# original failure — a harness file registered nowhere — still refuses.
REGISTERED_HARNESS_FILES = REQUIRED_PORTS | NEW_IN_020

# The registered artifacts §4.1 ports BY DIGEST, bound to the same lock and
# deliberately NOT transcribed into `PORTS.md`: 019's manifest already publishes
# a digest for each of them under the same study-relative path, and a second
# copy of those digests in a table here is a copy that can drift from the lock
# it claims to quote. The mutant payloads are covered by the same rule through
# `ARTIFACT_TREES` below, one file at a time.
PORTED_ARTIFACTS = (
    "policy/POLICY.md",
    "gold/GOLD.json",
    "mutants/MANIFEST-jps.json",
    "mutants/MANIFEST-rego.json",
    "reference/REFERENCE-A.md",
    "reference/REFERENCE-B.md",
    "reference/refA/pack.json",
    "reference/refB/policy.rego",
    "controls/off-gold-equivalence.json",
    "verification/V7-COMPLETENESS.md",
    "verification/V8-ASYMMETRY-LEDGER.md",
)
# The payload trees, exact one-level globs, checked file for file against the
# lock in BOTH directions: a payload 019 covers and 020 does not have, and one
# 020 has that 019's lock does not name, are the same defect.
ARTIFACT_TREES = (("mutants/jps", ".json"), ("mutants/rego", ".rego"))

# The three arm prompts are bound to 019's REGISTRY rather than to its manifest,
# because 019's manifest does not cover `arms/` and its registry pins each
# prompt's digest under `arms.<ARM>.promptSha256` — the same member the call
# wrapper's own prompt-digest gate reads.
PROMPT_PATHS = {arm: "arms/%s/PROMPT.txt" % arm for arm in ARMS}

# The freeze pins §2 and §7 register, in the order PINS.json carries them. A
# null anywhere here makes the run a PILOT (`study_label()`); REGISTERED
# requires every one of them.
#
# ROUND-1 FINDING R1-9, and it was the reachability that made it a blocker: the
# set stopped at eleven members, so `REGISTERED` was reachable while the
# capabilities file, the model, the golden capture, the probe prompt, the
# isolation assent, the jpack build attestation and the sealed reviewer set were
# all still null — every one of them a value the attempt depends on, and the
# capabilities pin in particular merely RECORDED as "unenforced" by the
# toolchain rather than blocking anything. Seven members are added below, each
# named by the registration that owes it:
#
#   opa.capabilitiesSha256              §2, and the canary control gate
#   codex.model                         §2 "Model named by explicit flag"
#   golden.sha256 / probePrompt.sha256  §2, §6's golden-context gate
#   isolationNegative.assent            §6, and the driver's own precondition
#   jpack.reproducibleBuildAttestation  §2 "reproducible-build attestation at
#                                       freeze (jpack supports it)"
#   reviewerMutantSet.sha256            §1a/§4, and round-1 R1-10
#
# `tests/test_pins.py` drives the label rule pin by pin: each one, nulled alone
# on an otherwise-full registry, must produce PILOT.
FREEZE_PINS = (
    ("preregistration", ("preregistration", "sha256")),
    ("policyProse", ("policyProse", "sha256")),
    ("goldSuite", ("goldSuite", "sha256")),
    ("matrixA", ("arms", "A", "promptSha256")),
    ("matrixB", ("arms", "B", "promptSha256")),
    ("matrixC", ("arms", "C", "promptSha256")),
    ("mutantManifests", ("mutantManifests", "sha256")),
    ("referenceA", ("references", "A", "sha256")),
    ("referenceB", ("references", "B", "sha256")),
    ("offGoldCertificate", ("offGoldCertificate", "sha256")),
    ("studyManifest", ("studyManifest", "sha256")),
    ("opaCapabilities", ("opa", "capabilitiesSha256")),
    ("jpackBuildAttestation", ("jpack", "reproducibleBuildAttestation")),
    ("model", ("codex", "model")),
    ("probePrompt", ("probePrompt", "sha256")),
    ("goldenContext", ("golden", "sha256")),
    ("isolationAssent", ("isolationNegative", "assent")),
    ("reviewerMutantSet", ("reviewerMutantSet", "sha256")),
)

# ROUND-7 FINDING R7-8: a pin whose SOURCE nobody names is a pin nobody fills.
#
# `reviewerMutantSet.sha256` has been one of the eighteen pins `study_label()`
# requires for `REGISTERED` since round 1, and the exhaustive freeze-fill
# procedure in `harness/SCAFFOLD.md` filled the other seventeen and then claimed
# the label — because nothing anywhere said what value this one takes or where
# it comes from. A null pin is reported by `unfilled_pins()` either way; what
# was missing is the second half of the sentence, so every freeze pin now names
# the artifact its value is computed from. `tests/test_pins.py` asserts the two
# tables have exactly the same members, so a pin added without a source, or a
# source left behind by a deleted pin, fails the suite.
PIN_SOURCES = {
    "preregistration": "sha256 of the reviewed PREREGISTRATION.md (filled LAST)",
    "policyProse": "sha256 of policy/POLICY.md, ported frozen from Study 019 "
                   "by digest (PREREGISTRATION.md §7) rather than drafted here",
    "goldSuite": "sha256 of gold/GOLD.json",
    "matrixA": "sha256 of arms/A/PROMPT.txt, assembled deterministically",
    "matrixB": "sha256 of arms/B/PROMPT.txt, assembled deterministically",
    "matrixC": "sha256 of arms/C/PROMPT.txt, assembled deterministically",
    "mutantManifests": "sha256 over mutants/MANIFEST-jps.json and "
                       "mutants/MANIFEST-rego.json",
    "referenceA": "sha256 of reference/refA/pack.json",
    "referenceB": "sha256 of reference/refB/policy.rego",
    "offGoldCertificate": "sha256 of controls/off-gold-equivalence.json",
    "studyManifest": "sha256 of harness/STUDY-MANIFEST.sha256, written by "
                     "harness/make_manifest.py --freeze",
    "opaCapabilities": "sha256 of the pinned OPA capabilities file",
    "jpackBuildAttestation": "the pinned jpack build's reproducible-build "
                             "attestation",
    "model": "the model id the authoring wrapper is invoked with, by explicit flag",
    "probePrompt": "sha256 of the golden-context probe prompt (SCAFFOLD G1)",
    "goldenContext": "sha256 of the golden-context capture, WRITTEN by the "
                     "capture command (SCAFFOLD G1)",
    "isolationAssent": "the recorded assent from the isolation negative control, "
                       "WRITTEN by that control (SCAFFOLD G2)",
    "reviewerMutantSet": "sha256 of controls/reviewer-mutants/MANIFEST.json, "
                         "after harness/e4lib/reviewer.py validates the set "
                         "without executing it; harness/make_manifest.py "
                         "reports the value and refuses the freeze without it",
}


# | `source` | `sha` | `destination` | `sha` | changed |
ROW = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|")


class IntegrityError(Exception):
    """A refusal that precedes every call and every count."""


def digest(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _refuse_duplicate_keys(pairs):
    keys = [key for key, _ in pairs]
    if len(set(keys)) != len(keys):
        raise IntegrityError("duplicate object keys")
    return dict(pairs)


def load_json(path: str):
    """Duplicate-key-rejecting JSON. A registry or a lock with a shadowed
    member cannot mean one thing here and another to a reader."""
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"),
                          object_pairs_hook=_refuse_duplicate_keys)


def bare(value) -> str:
    """A digest with or without the `sha256:` prefix, as a bare hex string."""
    if not isinstance(value, str):
        raise IntegrityError("a digest is missing where one is required: %r" % (value,))
    return value.split(":")[-1].strip()


def parse_ports(ports_path: str) -> list:
    """[(source, source sha256, destination, destination sha256)] from a
    PORTS.md table. What each column is checked AGAINST is verify_chain()'s
    business, and it is not this table."""
    if not os.path.isfile(ports_path):
        raise IntegrityError("no ports record at %s" % ports_path)
    rows = []
    with open(ports_path, "rb") as handle:
        for line in handle.read().decode("utf-8").splitlines():
            match = ROW.match(line.strip())
            if match:
                rows.append(tuple(match.groups()))
    if not rows:
        raise IntegrityError("%s carries no parseable port rows" % ports_path)
    return rows


# --- the chain -------------------------------------------------------------


def parse_lock(lock_path: str) -> dict:
    """`{study-relative path: sha256}` from a `sha256  path` lock file.

    The source study's lock is a `sha256sum`-format file, and this reads it as
    exactly that: two spaces, digest first. A line that does not parse is an
    error rather than a skip — a lock with an unreadable line is a lock that
    covers less than it appears to."""
    if not os.path.isfile(lock_path):
        raise IntegrityError("no lock at %s" % lock_path)
    entries = {}
    with open(lock_path, "rb") as handle:
        for number, line in enumerate(
                handle.read().decode("utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            head, separator, relative = line.partition("  ")
            if not separator or not re.match(r"^[0-9a-f]{64}$", head) \
                    or not relative.strip():
                raise IntegrityError(
                    "%s line %d is not a `sha256  path` entry: %r"
                    % (lock_path, number, line))
            if relative in entries:
                raise IntegrityError(
                    "%s names %s twice; a lock readable two ways is not a lock"
                    % (lock_path, relative))
            entries[relative] = head
    if not entries:
        raise IntegrityError("%s carries no entries" % lock_path)
    return entries


def source_lock(nineteen: str = NINETEEN) -> dict:
    """Study 019's lock, verified FIRST and at the digest 019's own registry
    pins for it — §7's "integrity verifies the source study's lock first", as
    the one function every source-side binding in this module goes through."""
    pins_path = os.path.join(nineteen, "harness", "PINS.json")
    if not os.path.isfile(pins_path):
        raise IntegrityError("Study 019's harness/PINS.json is missing")
    actual = digest(pins_path)
    if actual != NINETEEN_PINS_SHA256:
        raise IntegrityError(
            "Study 019's harness/PINS.json is sha256:%s, not the pinned sha256:%s"
            % (actual, NINETEEN_PINS_SHA256))
    pins = load_json(pins_path)
    recorded = pins.get(NINETEEN_LOCK_PIN) or {}
    lock_pin = bare(recorded.get("sha256"))
    if recorded.get("path") != NINETEEN_LOCK_PATH:
        raise IntegrityError(
            "Study 019's registry records its lock at %r, not %s"
            % (recorded.get("path"), NINETEEN_LOCK_PATH))
    lock_path = os.path.join(nineteen, NINETEEN_LOCK_PATH)
    if not os.path.isfile(lock_path):
        raise IntegrityError("Study 019's %s is missing" % NINETEEN_LOCK_PATH)
    actual = digest(lock_path)
    if actual != lock_pin:
        raise IntegrityError(
            "Study 019's %s is sha256:%s, not the sha256:%s its own registry "
            "records for it" % (NINETEEN_LOCK_PATH, actual, lock_pin))
    return {"pins": pins, "lockSha256": lock_pin,
            "entries": parse_lock(lock_path)}


def verify_chain(study: str = STUDY, nineteen: str = NINETEEN,
                 ports_path: str = None, pins_path: str = None) -> dict:
    """The one-level chain, then the rows, bound by the authority each row has.

    Study 019's `verify_chain()` did this over one level and two tiers against
    Study 012's PORTS.md destination cells; this is that function with the
    source-side authority moved to the thing Study 019 actually publishes — its
    frozen lock. Everything the shape of the check rests on is 012's by way of
    019's: the placeholder scan, the registry's own `pinnedFrom` members checked
    against the review-bound constants above, the exact destination set, and
    per-row source and destination digests."""
    ports_path = ports_path or os.path.join(study, "harness", "PORTS.md")
    pins_path = pins_path or os.path.join(study, "harness", "PINS.json")

    source = source_lock(nineteen)
    lock_entries = source["entries"]

    if not os.path.isfile(pins_path):
        raise IntegrityError("no registry at %s" % pins_path)
    # A `(port time)` placeholder surviving into either run-time file is an
    # unfinished port, refused by name (Study 012 §7's sentence, carried).
    for path, name in ((ports_path, "harness/PORTS.md"),
                       (pins_path, "harness/PINS.json")):
        with open(path, "rb") as handle:
            if b"(port time)" in handle.read():
                raise IntegrityError(
                    "%s still carries a `(port time)` placeholder: the port is "
                    "not finished" % name)
    pins = load_json(pins_path)
    own_ports_pin = bare((pins.get("ownPorts") or {}).get("sha256"))
    actual_ports = digest(ports_path)
    if actual_ports != own_ports_pin:
        raise IntegrityError(
            "harness/PORTS.md is sha256:%s, not the sha256:%s harness/PINS.json "
            "records for it" % (actual_ports, own_ports_pin))

    recorded = pins.get("pinnedFrom") or {}
    entry = recorded.get("pins") or {}
    if bare(entry.get("sha256")) != NINETEEN_PINS_SHA256 \
            or entry.get("path") != "harness/PINS.json":
        raise IntegrityError(
            "the registry's pinnedFrom.pins member (%r) is not the "
            "review-bound harness/PINS.json at %s"
            % (entry, NINETEEN_PINS_SHA256))
    if recorded.get("study") != "studies/019-authorship-across-representations" \
            or recorded.get("commit") != PORT_COMMIT:
        raise IntegrityError(
            "the registry's pinnedFrom study or commit is not the recorded port "
            "provenance (%s at %s)"
            % ("studies/019-authorship-across-representations", PORT_COMMIT))

    # No path is both ported by digest and new in 020. The two sets are the
    # exact-set property in two halves, and a member of both would be a file
    # governed by two rules with two consequences.
    overlap = sorted(REQUIRED_PORTS & NEW_IN_020)
    if overlap:
        raise IntegrityError(
            "%s is registered both as a port by digest and as new in 020, and "
            "019's lock names it — a path the source study HAS cannot be new "
            "here; a path is one or the other" % ", ".join(overlap))
    # What makes NEW_IN_020 membership checkable rather than declared: 019's
    # lock must not name the path. A file the source study HAS is a file this
    # study owes a PORTS.md row for, and calling it new does not make it new.
    for relative in sorted(NEW_IN_020):
        here = os.path.join(study, relative)
        if not os.path.isfile(here):
            raise IntegrityError(
                "%s is registered as new in 020 and is not on disk" % relative)
        if relative in lock_entries:
            raise IntegrityError(
                "%s is registered as new in 020 and Study 019's lock names it; "
                "a file the source study has is a file this port owes a "
                "harness/PORTS.md row for" % relative)

    rows = parse_ports(ports_path)
    destinations = set(row[2] for row in rows)
    if destinations != set(REQUIRED_PORTS):
        missing = sorted(set(REQUIRED_PORTS) - destinations)
        extra = sorted(destinations - set(REQUIRED_PORTS))
        raise IntegrityError(
            "harness/PORTS.md does not name exactly the registered port set "
            "(missing %s, unexpected %s)" % (missing or "none", extra or "none"))

    for origin_path, source_sha, destination, destination_sha in rows:
        here = os.path.join(study, destination)
        if not os.path.isfile(here):
            raise IntegrityError("the ported file %s is missing" % destination)
        actual = digest(here)
        if actual != destination_sha:
            raise IntegrityError(
                "%s is sha256:%s, not the sha256:%s harness/PORTS.md records"
                % (destination, actual, destination_sha))

        # Every harness row is a WHOLE-FILE port, so the source path is the
        # destination path: a row that renames a file is a row this study is not
        # taking by digest, and it says so here rather than in prose.
        if origin_path != destination:
            raise IntegrityError(
                "harness/PORTS.md names %r as the source of %s; this port is "
                "whole-file and by digest, so the two paths are the same path"
                % (origin_path, destination))
        pinned = lock_entries.get(origin_path)
        if pinned is None:
            raise IntegrityError(
                "Study 019's lock carries no entry for %s; a row whose source "
                "the source study's lock does not cover is not a port by digest"
                % origin_path)
        if source_sha != pinned:
            raise IntegrityError(
                "harness/PORTS.md records sha256:%s as the 019-side digest of "
                "%s and 019's own lock records sha256:%s"
                % (source_sha, origin_path, pinned))
        upstream = os.path.join(nineteen, origin_path)
        if not os.path.isfile(upstream) or digest(upstream) != source_sha:
            raise IntegrityError(
                "Study 019's %s does not hash to the recorded 019-side digest"
                % origin_path)

    return {"pins": pins, "rows": rows,
            "study019LockSha256": source["lockSha256"],
            "study019Lock": lock_entries,
            # Study 019's OWN registry, carried out so `verify()` binds the arm
            # prompts to the source study's pins and not to this study's, whose
            # prompt digests are freeze pins and are null until the freeze.
            "study019Pins": source["pins"]}


def verify_ported_artifacts(study: str = STUDY, nineteen: str = NINETEEN,
                            lock: dict = None, source_pins: dict = None) -> dict:
    """§4.1's registered artifacts, bound to the same lock, on both sides.

    Not a `PORTS.md` table: 019's lock already publishes a digest for each of
    these under the same study-relative path, so the binding is a comparison
    against that lock rather than a transcription of it. Both directions are
    checked over the payload trees — a mutant 019's lock names and this tree
    does not carry, and one this tree carries that 019's lock does not name,
    are the same defect.

    The three arm prompts are bound to 019's REGISTRY instead, because 019's
    manifest does not cover `arms/`."""
    if lock is None or source_pins is None:
        source = source_lock(nineteen)
        lock = source["entries"]
        source_pins = source["pins"]
    checked = []
    for relative in PORTED_ARTIFACTS:
        pinned = lock.get(relative)
        if pinned is None:
            raise IntegrityError(
                "Study 019's lock carries no entry for the ported artifact %s"
                % relative)
        here = os.path.join(study, relative)
        if not os.path.isfile(here):
            raise IntegrityError("the ported artifact %s is missing" % relative)
        actual = digest(here)
        if actual != pinned:
            raise IntegrityError(
                "%s is sha256:%s and Study 019's lock records sha256:%s"
                % (relative, actual, pinned))
        checked.append(relative)
    for directory, suffix in ARTIFACT_TREES:
        expected = sorted(name for name in lock
                          if name.startswith(directory + "/")
                          and name.endswith(suffix))
        here = os.path.join(study, directory)
        if not os.path.isdir(here):
            raise IntegrityError("the ported payload tree %s is missing"
                                 % directory)
        present = sorted("%s/%s" % (directory, name)
                         for name in os.listdir(here)
                         if name.endswith(suffix))
        if present != expected:
            missing = sorted(set(expected) - set(present))
            extra = sorted(set(present) - set(expected))
            raise IntegrityError(
                "%s does not carry exactly the payloads Study 019's lock names "
                "(missing %s, unexpected %s)"
                % (directory, missing[:3] or "none", extra[:3] or "none"))
        for relative in expected:
            actual = digest(os.path.join(study, relative))
            if actual != lock[relative]:
                raise IntegrityError(
                    "%s is sha256:%s and Study 019's lock records sha256:%s"
                    % (relative, actual, lock[relative]))
            checked.append(relative)
    registry_arms = source_pins.get("arms") or {}
    for arm in ARMS:
        relative = PROMPT_PATHS[arm]
        pinned = bare(((registry_arms.get(arm) or {}).get("promptSha256")))
        here = os.path.join(study, relative)
        if not os.path.isfile(here):
            raise IntegrityError("the ported arm prompt %s is missing" % relative)
        actual = digest(here)
        if actual != pinned:
            raise IntegrityError(
                "%s is sha256:%s and Study 019's registry pins sha256:%s for "
                "arm %s" % (relative, actual, pinned, arm))
        checked.append(relative)
    return {"portedArtifacts": sorted(checked)}


# --- the registered label rule ----------------------------------------------

# The literal stand-ins a half-finished registry carries, and the reason they
# need naming here. Study 012 registered one such refusal — `harness/PORTS.md`
# and `harness/PINS.json` may carry no `(port time)` cell, because an unfinished
# port is not a soft state — but it lived in the ports parser and reached the
# label rule not at all. The salvage audit probed this rule directly: with all
# eighteen freeze pins set to `""`, `"TODO(prereg)"`, `0`, `[]`, `{}` or
# `False`, `study_label()` answered REGISTERED and `unfilled_pins()` answered
# `[]`. A registry of eighteen empty strings is not a registration.
#
# Matched on the STRIPPED, case-folded value, so `"  todo  "` is the same
# refusal as `"TODO"`. `TODO(`-prefixed sentinels (`"TODO(prereg)"`) are matched
# by prefix rather than by membership, since their parenthetical varies.
PIN_PLACEHOLDERS = ("(port time)", "todo", "tbd", "fixme", "xxx", "pending",
                    "n/a", "na", "none", "null", "nil", "-", "?")
PIN_PLACEHOLDER_PREFIXES = ("todo(", "tbd(", "fixme(")


def pin_is_filled(value) -> bool:
    """Whether a freeze-pin value counts as FILLED.

    Filled means: not null, not empty, and not a stand-in. Concretely — `None`,
    any falsy value (`""`, `0`, `0.0`, `False`, `[]`, `{}`), a string that is
    only whitespace, and a string whose stripped case-folded form is one of
    `PIN_PLACEHOLDERS` or begins with one of `PIN_PLACEHOLDER_PREFIXES` are all
    UNFILLED. Everything else is filled.

    **This decides FILLED, not CORRECT.** Whether the digest a pin carries is
    the digest of the bytes on disk is `verify()`'s business and is checked
    under both labels; whether a filled pin has the right SHAPE is the
    registry's own gates'. The one thing this function may not do is what it
    used to do — count a stand-in as a registration, which made REGISTERED
    reachable without a single real value being determined."""
    if value is None or not value:
        return False
    if isinstance(value, str):
        candidate = value.strip().lower()
        if not candidate:
            return False
        if candidate in PIN_PLACEHOLDERS:
            return False
        if candidate.startswith(PIN_PLACEHOLDER_PREFIXES):
            return False
    return True


def freeze_pin_state(pins: dict) -> dict:
    """{registered pin name: True when filled} over `FREEZE_PINS`.

    A member whose parent object is absent counts as null rather than raising:
    a registry that has not grown the member yet is exactly the pre-freeze state
    this rule exists to label. `pin_is_filled()` decides what "filled" means, and
    it is stricter than `is not None` for the reason recorded above it."""
    state = {}
    for name, path in FREEZE_PINS:
        node = pins
        for key in path:
            node = node.get(key) if isinstance(node, dict) else None
            if node is None:
                break
        state[name] = pin_is_filled(node)
    return state


# The two freeze pins the PRE-FREEZE CEREMONY fills, and the reason they need a
# name of their own (round-1 R1-9's consequence, stated rather than worked
# around). `golden.sha256` is written by the golden-context capture and
# `isolationNegative.assent` by the isolation negative control — both of which
# are commands that run BEFORE the freeze and are what PRODUCE those values. A
# gate on the whole freeze set is therefore circular for exactly those two
# commands and for nothing else: they cannot require a value they exist to
# create.
#
# They ARE freeze pins: `study_label()` reads the whole set, so a REGISTERED
# attempt is unreachable while either is null, and the scorer's golden-context
# gate reads them again at attempt time. This tuple exempts them at ONE place —
# the driver's pre-ceremony gate — and nowhere else.
CEREMONY_LIFECYCLE_PINS = ("goldenContext", "isolationAssent")


def ceremony_unfilled_pins(pins: dict) -> list:
    """`unfilled_pins()` minus the two the ceremony has not reached yet."""
    return [name for name in unfilled_pins(pins)
            if name not in CEREMONY_LIFECYCLE_PINS]


def study_label(pins: dict) -> str:
    """REGISTERED iff every freeze pin is non-null; any null pin -> PILOT.

    The label is computed from the registry and never passed in. Study 014's
    round 3 found a registered run reachable with only the preregistration
    digest filled, which left the registry the attempt adjudicated unpinned;
    the rule is therefore over the WHOLE freeze set, and this function is the
    only place it is decided."""
    return "REGISTERED" if all(freeze_pin_state(pins).values()) else "PILOT"


def unfilled_pins(pins: dict) -> list:
    """The freeze pins still null, in registered order — what a PILOT label
    owes the reader."""
    state = freeze_pin_state(pins)
    return [name for name, _path in FREEZE_PINS if not state[name]]


def unfilled_pin_sources(pins: dict) -> list:
    """ROUND-7 FINDING R7-8: every null pin WITH the artifact it is filled from,
    so the ceremony's remaining work is readable rather than remembered."""
    return [(name, PIN_SOURCES[name]) for name in unfilled_pins(pins)]


# --- the interpreter, carried verbatim --------------------------------------


def verify_interpreter(pins: dict) -> str:
    """The registry's `python` member, read by code rather than only recorded
    (implementation exactly, version series exactly; the patch level is
    recorded, not required)."""
    entry = pins.get("python")
    if not isinstance(entry, dict):
        raise IntegrityError("harness/PINS.json pins no interpreter")
    implementation = platform.python_implementation()
    if implementation != entry.get("implementation"):
        raise IntegrityError(
            "this harness is running on %s and harness/PINS.json registers %r"
            % (implementation, entry.get("implementation")))
    series = "%d.%d" % sys.version_info[:2]
    if series != entry.get("series"):
        raise IntegrityError(
            "this harness is running on %s %s and harness/PINS.json registers "
            "the %r series" % (implementation, platform.python_version(),
                               entry.get("series")))
    return "%s %s" % (implementation, platform.python_version())


# --- unreviewed bytes: carried verbatim from Study 012 ----------------------


def _code_equal(left, right) -> bool:
    """Structural equality of two code objects: every code attribute, with
    co_consts compared element-wise — nested code objects recursed, sets and
    frozensets compared as sets (their marshal order is hash-seed-dependent),
    everything else by type and value."""
    code_type = type(left)
    if not isinstance(right, code_type):
        return False
    members = ("co_argcount", "co_posonlyargcount", "co_kwonlyargcount",
               "co_nlocals", "co_stacksize", "co_flags", "co_code",
               "co_names", "co_varnames", "co_freevars", "co_cellvars",
               "co_filename", "co_name", "co_qualname",
               "co_exceptiontable", "co_firstlineno", "co_linetable",
               "co_lnotab")
    for member in members:
        if getattr(left, member, None) != getattr(right, member, None):
            return False
    left_consts = left.co_consts
    right_consts = right.co_consts
    if len(left_consts) != len(right_consts):
        return False
    for a, b in zip(left_consts, right_consts):
        if not _const_equal(a, b, code_type):
            return False
    return True


def _const_equal(a, b, code_type) -> bool:
    """Type-strict, recursive constant equality: Python's == says
    (0, 1) == (False, True) and 0.0 == 0, which is exactly the laundering a
    poisoned cache would use (round 7, finding 1). Types must be identical at
    every depth; tuples recurse; sets compare as sets but with type-identical
    members; nested code recurses through _code_equal."""
    if type(a) is not type(b):
        return False
    if isinstance(a, code_type):
        return _code_equal(a, b)
    if isinstance(a, tuple):
        return len(a) == len(b) and all(
            _const_equal(x, y, code_type) for x, y in zip(a, b))
    if isinstance(a, float):
        # Python equality says 0.0 == -0.0 and would launder a sign flip a
        # cache carries into "the same constant" (round 8, finding 3): a
        # float is its bits.
        import struct
        return struct.pack("<d", a) == struct.pack("<d", b)
    if isinstance(a, complex):
        import struct
        return struct.pack("<dd", a.real, a.imag) == struct.pack(
            "<dd", b.real, b.imag)
    if isinstance(a, frozenset):
        if len(a) != len(b):
            return False
        remaining = list(b)
        for x in a:
            for index, y in enumerate(remaining):
                if _const_equal(x, y, code_type):
                    del remaining[index]
                    break
            else:
                return False
        return True
    return a == b


def verify_bytecode(study: str = STUDY) -> None:
    """Compiled bytecode beside a reviewed source loads even under -B, so a
    cache the sources did not produce is a byte that runs unreviewed (round 5,
    finding 3). The gate VALIDATES rather than banning: a cache entry is
    admitted only when it provably compiles from the source beside it — the
    running interpreter's magic number and, per the header's own mode, the
    source's exact mtime-and-size stamp or its source hash. An orphaned entry
    (no source), a foreign interpreter's, or a stale one refuses. A fresh
    cache of a reviewed source is that source compiled, and passes."""
    import importlib.util
    import marshal
    magic = importlib.util.MAGIC_NUMBER
    bad = []
    # An UNTRACKED Python source shadows a reviewed one at import time — an
    # untracked harness/integrity/__init__.py takes precedence over the
    # reviewed integrity.py and bypasses every gate without touching the
    # manifest (round 7, finding 2). The reviewed bytes are the bytes that
    # run only if no unreviewed source can be imported at all.
    tracked = set(subprocess.run(
        ["git", "ls-files", "-z", "--", "."],
        cwd=study, capture_output=True, check=True
    ).stdout.decode("utf-8").split("\0"))
    # A TRACKED cache is refused unconditionally, before any freshness question
    # is asked (round 5, finding 1). The validating gate below admits a cache
    # that provably compiles from the source beside it, which is the right rule
    # for a working tree and the wrong one for the index: a `.pyc` is fresh on
    # the machine that wrote it and stale on every checkout after, so a
    # committed one passes here and refuses everywhere else — which is exactly
    # what happened, and what made a green suite describe a tree HEAD was not.
    # Read from the index, so a cache deleted from disk but still committed is
    # still refused.
    for name in sorted(tracked):
        if not name:
            continue
        parts = name.split("/")
        if "__pycache__" in parts or name.endswith((".pyc", ".pyo")):
            bad.append((name, "tracked bytecode (committed, not merely present)"))
    for base, directories, files in os.walk(study):
        for name in files:
            if not name.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(base, name), study)
            if rel.replace(os.sep, "/") not in tracked:
                bad.append((rel, "untracked Python source"))
    for base, directories, files in os.walk(study):
        in_cache = os.path.basename(base) == "__pycache__"
        for name in files:
            path = os.path.join(base, name)
            if not in_cache:
                # A sourceless .pyc imports on its own; one outside a cache
                # directory is a byte that runs with no reviewed source
                # beside it (round 6, finding 1).
                if name.endswith(".pyc"):
                    bad.append((os.path.relpath(path, study),
                                "bytecode outside __pycache__"))
                continue
            if not name.endswith(".pyc"):
                bad.append((os.path.relpath(path, study), "not bytecode"))
                continue
            try:
                source = importlib.util.source_from_cache(path)
            except ValueError:
                bad.append((os.path.relpath(path, study), "unmappable name"))
                continue
            if not os.path.isfile(source):
                bad.append((os.path.relpath(path, study), "orphaned"))
                continue
            with open(path, "rb") as handle:
                header = handle.read(16)
            if len(header) < 16 or header[:4] != magic:
                bad.append((os.path.relpath(path, study),
                            "foreign interpreter"))
                continue
            flags = int.from_bytes(header[4:8], "little")
            with open(source, "rb") as handle:
                source_bytes = handle.read()
            if flags & 0b1:
                stored = header[8:16]
                expected = importlib.util.source_hash(source_bytes)
                if stored != expected:
                    bad.append((os.path.relpath(path, study), "stale hash"))
                    continue
            else:
                stat = os.stat(source)
                mtime = int.from_bytes(header[8:12], "little")
                size = int.from_bytes(header[12:16], "little")
                if mtime != int(stat.st_mtime) & 0xFFFFFFFF or                         size != stat.st_size & 0xFFFFFFFF:
                    bad.append((os.path.relpath(path, study), "stale stamp"))
                    continue
            # The header is provenance; the PAYLOAD is what executes. A header
            # spliced onto foreign bytecode passes every stamp, so "provably
            # compiles from the source beside it" is checked on the marshalled
            # body itself: it must equal the running interpreter's own
            # compilation of that source (round 6, finding 1).
            with open(path, "rb") as handle:
                payload = handle.read()[16:]
            # Two subtleties make this a STRUCTURAL comparison, not a byte
            # one. The compile name must be the CACHED object's own
            # co_filename (caches record the path as imported, relative
            # under a cwd-dependent sys.path entry) — reading it from the
            # cache is inert, since whatever name is planted, the code must
            # still equal the reviewed source compiled under that name. And
            # marshal bytes of set constants depend on the writing process's
            # hash seed, so equality is decided on the code objects
            # themselves: bytecode, names, and consts, with sets compared as
            # sets and nested code recursed. marshal is not hardened against
            # hostile bytes; a crafted payload that kills the interpreter
            # here kills a refusing gate, which refuses.
            try:
                cached_code = marshal.loads(payload)
                cached_name = cached_code.co_filename
            except Exception:
                bad.append((os.path.relpath(path, study),
                            "unreadable payload"))
                continue
            if not isinstance(cached_name, str):
                bad.append((os.path.relpath(path, study),
                            "unreadable payload"))
                continue
            try:
                expected_code = compile(source_bytes, cached_name, "exec",
                                        dont_inherit=True)
            except (SyntaxError, ValueError):
                bad.append((os.path.relpath(path, study),
                            "source does not compile"))
                continue
            if not _code_equal(cached_code, expected_code):
                bad.append((os.path.relpath(path, study),
                            "payload is not this source compiled"))
    if bad:
        raise IntegrityError(
            "compiled bytecode that the reviewed sources did not produce sits "
            "in the study tree (%s): delete it (§2.10)"
            % ", ".join("%s: %s" % item for item in sorted(bad)))


# --- the manifest, the whole verification, the entry ------------------------


def verify_manifest(study: str = STUDY, pins: dict = None) -> str:
    """ADR 0004's exact-set manifest, and the pin over it.

    This study's manifest covers what must not change, and
    `harness/make_manifest.py` excludes the five appendable documents §7 delta
    11 names by named constant. Two things are checked here: the committed
    manifest still equals
    the tree it covers, and — once the freeze has filled it — the registry's
    `studyManifest.sha256` is that file's digest.

    Pre-freeze the pin is null and only the exact-set comparison runs, because a
    manifest that does not describe its own tree is a defect at any stage."""
    pins = pins if pins is not None else load_json(
        os.path.join(study, "harness", "PINS.json"))
    sys.path.insert(0, os.path.join(study, "harness"))
    import make_manifest
    problems = make_manifest.manifest_problems()
    if problems:
        raise IntegrityError(
            "the study manifest does not describe the tree it covers: %s"
            % "; ".join(problems))
    pinned = ((pins.get("studyManifest") or {}).get("sha256"))
    manifest_path = os.path.join(study, "harness", "STUDY-MANIFEST.sha256")
    if pinned is None:
        return "unbound (pre-freeze; the manifest is pinned at the freeze)"
    actual = digest(manifest_path)
    if actual != bare(pinned):
        raise IntegrityError(
            "harness/STUDY-MANIFEST.sha256 is sha256:%s, not the sha256:%s the "
            "registry pins" % (actual, bare(pinned)))
    return "sha256:" + actual


def verify(study: str = STUDY, nineteen: str = NINETEEN) -> dict:
    """Everything this port can establish, in the registered order: no
    unreviewed bytecode or untracked source, the port chain, the registered
    artifacts, the interpreter, the exact-set manifest, and the label the
    registry earns.

    IntegrityError on the first refusal; a summary dict when every check passed.
    What it deliberately does NOT establish is in the module docstring — a green
    summary here is not a statement that the study is ready to run."""
    verify_bytecode(study)
    chain = verify_chain(study, nineteen)
    artifacts = verify_ported_artifacts(study, nineteen, chain["study019Lock"],
                                        chain["study019Pins"])
    interpreter = verify_interpreter(chain["pins"])
    manifest = verify_manifest(study, chain["pins"])
    label = study_label(chain["pins"])
    return {"portedFiles": sorted(row[2] for row in chain["rows"]),
            "portedArtifacts": artifacts["portedArtifacts"],
            "study019LockSha256": "sha256:" + chain["study019LockSha256"],
            "studyManifest": manifest,
            "label": label,
            "unfilledPins": unfilled_pins(chain["pins"]),
            "unfilledPinSources": unfilled_pin_sources(chain["pins"]),
            "interpreter": interpreter}


def main(argv: list) -> int:
    try:
        summary = verify()
    except IntegrityError as error:
        print("refused: %s" % error)
        return 1
    print("integrity verified: %d ported files, %d ported artifacts; manifest "
          "%s; on %s"
          % (len(summary["portedFiles"]), len(summary["portedArtifacts"]),
             summary["studyManifest"], summary["interpreter"]))
    print("label: %s%s"
          % (summary["label"],
             "" if not summary["unfilledPins"]
             else " (%d null freeze pin(s))" % len(summary["unfilledPins"])))
    # ROUND-7 FINDING R7-8: each with the artifact it is filled from, because a
    # list of names is a list of things somebody has to already know.
    for name, source in summary["unfilledPinSources"]:
        print("  null freeze pin: %s — %s" % (name, source))
    return 0


def _refuse_unsafe_import_path():
    """Round 10, finding 1, for the THIRD path-invoked entry (README step 1).

    This file carries no untracked-source tripwire of its own — the tree-wide
    scan it needs is the first thing `verify()` does, inside `verify_bytecode()`
    — and round 9 called its head "clean" on the narrower ground that it imports
    nothing study-local at module scope. That property is real and unchanged,
    but it is not the whole of it: running a script BY PATH puts that script's
    own directory first on `sys.path`, so the head imports above — `subprocess`,
    which `verify_bytecode()` asks git what is tracked with, among them —
    resolve from the study's own harness directory before any byte of this file
    runs, and `sys.path.insert(0, HERE)` at module scope has no scan before it.
    Nothing inside the file can close that: `sys.path[0]` is populated before
    the file is read.

    `-P` / `PYTHONSAFEPATH=1` is the closure, and README step 0 exports it. This
    refusal only establishes that the operator applied it — a discipline check
    against operator error, not a gate against a hostile tree, because it
    executes after the head imports it is about."""
    if not sys.flags.safe_path:
        print("refused: run this file with -P, or with PYTHONSAFEPATH=1 in the "
              "environment as README step 0 exports it; invoking a script by "
              "path puts its own directory first on sys.path, so this file's "
              "head imports — `subprocess`, which the tree-wide untracked "
              "source scan in verify_bytecode() runs on, among them — resolve "
              "from the harness directory that scan exists to police (§2.10, "
              "round 10 finding 1)", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    _refuse_unsafe_import_path()
    raise SystemExit(main(sys.argv))
