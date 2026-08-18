#!/usr/bin/env python3
"""The port chain and the pin registry in code: verified before any call and
any count — PARTIAL PORT.

PORTED from Study 012's `harness/integrity.py`
(sha256 `98e11a14f931e47ece6b5c975afe46a18ef784d8824785fab8632083c5014af1`, the
destination digest Study 012's own `harness/PORTS.md` records for it, at commit
`019c95be9e86c575878015954dfec17e4f84e683`). What was taken, what changed and
what was deliberately left behind is enumerated in this study's
`harness/PORTS.md`, whose table this module machine-reads.

**The chain, one level and every link a pinned digest.** Study 012 inherited
through three levels (011's registry and ports, 010's lock); this study
inherits from ONE source study, and the chain is correspondingly shorter and is
stated here rather than implied:

```
this file                     (pinned in harness/PINS.json at port time)
    -> Study 012's harness/PINS.json   cff265e7…   (pinned below, and in PORTS.md)
       Study 012's harness/PORTS.md    e754a583…   (pinned by 012's OWN registry,
                                                    read from it and not chosen here)
```

`verify_chain()` therefore, in order: verifies Study 012's `harness/PINS.json`
against the digest this file pins for it; verifies Study 012's `harness/PORTS.md`
against the digest **012's own registry** records for it under `ownPorts`
(not a digest this study chooses); verifies THIS study's `harness/PORTS.md`
against the digest this study's `harness/PINS.json` records for it, so the file
that says what each enumerated change *was* cannot be rewritten after the
review; and then binds each row of the port table to the authority that row
actually has — the six files taken from Study 012 to the DESTINATION cells of
012's own `PORTS.md` on the source side, and `harness/make_manifest.py`, taken
from Study 014, to 014's working file at the recorded commit, because Study 014
pins none of its own harness sources and the recorded commit is the whole of
that row's source-side binding.

**What is NOT carried, said plainly so §7 cannot claim it.** Study 012's arm
artifacts (C8), family schema (C9), clean-room mirror gate (C10), landmark
grid, policy parser and census are all absent: this study has no policy mutants
in the 012 sense and its controls are registered separately. Its `[D-20]`
whole-tree git manifest is absent too, and deliberately: this study's manifest
is ADR 0004's **exact-set** manifest (`harness/make_manifest.py`,
`harness/STUDY-MANIFEST.sha256`, pinned as `studyManifest`), which excludes
`DEVIATIONS.md` and `README.md` by construction. Carrying both would give one
study two manifests that could disagree.

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
# The one source study, and the one further study a single file is taken from.
TWELVE = os.path.normpath(os.path.join(STUDY, "..", "012-policy-perturbation"))
FOURTEEN = os.path.normpath(os.path.join(STUDY, "..", "014-openworkproof-binding"))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# The chain's two ends, pinned here in reviewed code. Study 012's registry
# digest is this file's; the digest of 012's PORTS.md is NOT here — it is read
# from 012's own registry, which is what "the digest 012 pins for it, not one
# this study chooses" means in code.
TWELVE_PINS_SHA256 = "cff265e75fc3f3be82fcbbb12527d14faa30935e6f804c3f02dd2fb22fcc64f4"
# The commit the port was taken at. The six files taken from Study 012 are
# bound to 012's own PORTS.md digests, which are stronger than a commit; the one
# file taken from Study 014 is bound to this commit and to nothing older,
# because Study 014 pins none of its own harness sources.
PORT_COMMIT = "019c95be9e86c575878015954dfec17e4f84e683"

ARMS = ("A", "B", "C")

# The port table's registered destination set. A row deleted from PORTS.md is a
# check silently dropped, so the set must be exact — and a row ADDED must be as
# loud, which is why the scorer's two ported modules are registered here rather
# than discovered from the table (`harness/SCAFFOLD.md` item M1, points 2 and 3).
REQUIRED_PORTS = frozenset((
    "harness/authoring_call.sh",
    "harness/batch.py",
    "harness/integrity.py",
    "harness/transcript_check.py",
    "harness/e4lib/stats.py",
    "harness/e4lib/census.py",
    "harness/make_manifest.py",
))

# Tier 1 (the source study): destination -> the path Study 012's own PORTS.md
# records the file under. The source cell of each row must equal 012's
# DESTINATION cell for that path, and 012's working file must hash to it.
# `e4lib/stats.py` and `e4lib/census.py` are tier-1 rows for exactly that
# reason: 012 publishes a destination cell for `harness/score_rates.py` and for
# `harness/census.py`, and those cells are what this study's source side answers
# to — 012's own SOURCE cell for its census (`analysis/diversity.py`, from Study
# 011) is one level further back than this chain reaches and is deliberately not
# read here.
TIER1_TWELVE_PATHS = {
    "harness/authoring_call.sh": "transcription/authoring_call.sh",
    "harness/batch.py": "harness/batch.py",
    "harness/integrity.py": "harness/integrity.py",
    "harness/transcript_check.py": "harness/transcript_check.py",
    "harness/e4lib/stats.py": "harness/score_rates.py",
    "harness/e4lib/census.py": "harness/census.py",
}
# No tier: Study 014 pins none of its harness sources, so this row is bound to
# the recorded commit's working file and to nothing older.
UNPINNED_SOURCES = {
    "harness/make_manifest.py": (FOURTEEN, "harness/make_manifest.py"),
}

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


def verify_chain(study: str = STUDY, twelve: str = TWELVE,
                 ports_path: str = None, pins_path: str = None) -> dict:
    """The one-level chain, then the rows, bound by the authority each row has.

    Study 012's `verify_chain()` did this over three levels and three tiers;
    this is that function with the levels it no longer has removed and the
    authorities it does have named. Everything the shape of the check rests on
    is 012's: the placeholder scan, the registry's own `pinnedFrom` members
    checked against the review-bound constants above, the exact destination set,
    and per-row source and destination digests."""
    ports_path = ports_path or os.path.join(study, "harness", "PORTS.md")
    pins_path = pins_path or os.path.join(study, "harness", "PINS.json")

    twelve_pins_path = os.path.join(twelve, "harness", "PINS.json")
    twelve_ports_path = os.path.join(twelve, "harness", "PORTS.md")
    if not os.path.isfile(twelve_pins_path):
        raise IntegrityError("Study 012's harness/PINS.json is missing")
    actual = digest(twelve_pins_path)
    if actual != TWELVE_PINS_SHA256:
        raise IntegrityError(
            "Study 012's harness/PINS.json is sha256:%s, not the pinned sha256:%s"
            % (actual, TWELVE_PINS_SHA256))
    twelve_pins = load_json(twelve_pins_path)

    # 012's PORTS.md at the digest 012's OWN registry pins for it — not one this
    # study chooses. This is the whole of what makes the source cells below an
    # inheritance rather than a transcription.
    own = twelve_pins.get("ownPorts") or {}
    twelve_ports_pin = bare(own.get("sha256"))
    if own.get("path") != "harness/PORTS.md":
        raise IntegrityError(
            "Study 012's registry records its ports file at %r, not "
            "harness/PORTS.md" % (own.get("path"),))
    if not os.path.isfile(twelve_ports_path):
        raise IntegrityError("Study 012's harness/PORTS.md is missing")
    actual = digest(twelve_ports_path)
    if actual != twelve_ports_pin:
        raise IntegrityError(
            "Study 012's harness/PORTS.md is sha256:%s, not the sha256:%s its "
            "own registry records for it" % (actual, twelve_ports_pin))

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
    if bare(entry.get("sha256")) != TWELVE_PINS_SHA256 \
            or entry.get("path") != "harness/PINS.json":
        raise IntegrityError(
            "the registry's pinnedFrom.pins member (%r) is not the "
            "review-bound harness/PINS.json at %s"
            % (entry, TWELVE_PINS_SHA256))
    if recorded.get("study") != "studies/012-policy-perturbation" \
            or recorded.get("commit") != PORT_COMMIT:
        raise IntegrityError(
            "the registry's pinnedFrom study or commit is not the recorded port "
            "provenance (%s at %s)"
            % ("studies/012-policy-perturbation", PORT_COMMIT))

    rows = parse_ports(ports_path)
    destinations = set(row[2] for row in rows)
    if destinations != set(REQUIRED_PORTS):
        missing = sorted(set(REQUIRED_PORTS) - destinations)
        extra = sorted(destinations - set(REQUIRED_PORTS))
        raise IntegrityError(
            "harness/PORTS.md does not name exactly the registered port set "
            "(missing %s, unexpected %s)" % (missing or "none", extra or "none"))

    twelve_rows = {row[2]: row for row in parse_ports(twelve_ports_path)}

    for source, source_sha, destination, destination_sha in rows:
        here = os.path.join(study, destination)
        if not os.path.isfile(here):
            raise IntegrityError("the ported file %s is missing" % destination)
        actual = digest(here)
        if actual != destination_sha:
            raise IntegrityError(
                "%s is sha256:%s, not the sha256:%s harness/PORTS.md records"
                % (destination, actual, destination_sha))

        if destination in TIER1_TWELVE_PATHS:
            twelve_path = TIER1_TWELVE_PATHS[destination]
            if source != twelve_path:
                raise IntegrityError(
                    "harness/PORTS.md names %r as the source of %s; Study 012's "
                    "path is %r" % (source, destination, twelve_path))
            row = twelve_rows.get(twelve_path)
            if row is None:
                raise IntegrityError(
                    "Study 012's PORTS.md carries no provenance row for %s"
                    % twelve_path)
            if source_sha != row[3]:
                raise IntegrityError(
                    "harness/PORTS.md records sha256:%s as the 012-side digest "
                    "of %s and 012's own PORTS.md records sha256:%s"
                    % (source_sha, twelve_path, row[3]))
            origin = os.path.join(twelve, twelve_path)
            if not os.path.isfile(origin) or digest(origin) != source_sha:
                raise IntegrityError(
                    "Study 012's %s does not hash to the recorded 012-side "
                    "digest" % twelve_path)
        else:
            root, relative = UNPINNED_SOURCES[destination]
            if source != relative:
                raise IntegrityError(
                    "harness/PORTS.md names %r as the source of %s; the "
                    "recorded source path is %r"
                    % (source, destination, relative))
            origin = os.path.join(root, relative)
            if not os.path.isfile(origin) or digest(origin) != source_sha:
                raise IntegrityError(
                    "%s does not hash to the sha256:%s this study's PORTS.md "
                    "records as its source; the recorded commit is the only "
                    "authority this row has" % (origin, source_sha))

    return {"pins": pins, "rows": rows,
            "study012PortsSha256": twelve_ports_pin}


# --- the registered label rule ----------------------------------------------

def freeze_pin_state(pins: dict) -> dict:
    """{registered pin name: True when filled} over `FREEZE_PINS`.

    A member whose parent object is absent counts as null rather than raising:
    a registry that has not grown the member yet is exactly the pre-freeze state
    this rule exists to label."""
    state = {}
    for name, path in FREEZE_PINS:
        node = pins
        for key in path:
            node = node.get(key) if isinstance(node, dict) else None
            if node is None:
                break
        state[name] = node is not None
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

    Study 012's `[D-20]` whole-tree git manifest is deliberately not carried
    (module docstring). This study's manifest covers what must not change, and
    `harness/make_manifest.py` excludes `DEVIATIONS.md` and `README.md` by named
    constant. Two things are checked here: the committed manifest still equals
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


def verify(study: str = STUDY, twelve: str = TWELVE) -> dict:
    """Everything this partial port can establish, in the registered order: no
    unreviewed bytecode or untracked source, the port chain, the interpreter,
    the exact-set manifest, and the label the registry earns.

    IntegrityError on the first refusal; a summary dict when every check passed.
    What it deliberately does NOT establish is in the module docstring, and the
    unported controls are in `harness/SCAFFOLD.md` — a green summary here is not
    a statement that the study is ready to run."""
    verify_bytecode(study)
    chain = verify_chain(study, twelve)
    interpreter = verify_interpreter(chain["pins"])
    manifest = verify_manifest(study, chain["pins"])
    label = study_label(chain["pins"])
    return {"portedFiles": sorted(row[2] for row in chain["rows"]),
            "study012PortsSha256": "sha256:" + chain["study012PortsSha256"],
            "studyManifest": manifest,
            "label": label,
            "unfilledPins": unfilled_pins(chain["pins"]),
            "interpreter": interpreter}


def main(argv: list) -> int:
    try:
        summary = verify()
    except IntegrityError as error:
        print("refused: %s" % error)
        return 1
    print("integrity verified: %d ported files; manifest %s; on %s"
          % (len(summary["portedFiles"]), summary["studyManifest"],
             summary["interpreter"]))
    print("label: %s%s"
          % (summary["label"],
             "" if not summary["unfilledPins"]
             else " (null freeze pins: %s)" % ", ".join(summary["unfilledPins"])))
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
