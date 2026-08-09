#!/usr/bin/env python3
"""C1, C8, C9 and the C10 gate in code: verified before any call and any count.

PREREGISTRATION.md §6 registers these controls; this module is what makes them
true at run time rather than only in pytest: `batch.preflight()` calls
`verify()` before it creates a slot, and `score_rates.score()` calls it before
it reads one. A one-character drift in any arm's `POLICY.md` would otherwise
change what 30 slots measure with nothing refusing.

**C1 — the three-level chain, bound by authority rather than by port kind.**
In this order: Study 011's `harness/PINS.json` and `harness/PORTS.md` are
verified against the digests §2.2 registers for them; Study 010's
`PROTOCOL-LOCK.json` is verified against the digest *011* pins for it (not one
this study chooses); this study's own `harness/PORTS.md` is verified against
the digest `harness/PINS.json` records for it, so the file that says what each
enumerated change *was* cannot be rewritten after the review; and then every
row of the port table is bound to the authority that row actually has — tier 1
to 010's lock, tier 2 to 011's `PINS.json`, tier 3 to 011's own bytes through
011's `PORTS.md`. The four files taken from 011's own harness are in no tier:
011 pinned none of them, and they are bound to the recorded commit and to
nothing older (§6 C1 states what that costs and what covers it).

**C8 — the arm artifacts are what §2 says they are.** Digests for all twenty
arm files, the single registered mirror, the assembled preamble,
`CONVENTIONS_DELTA` and `CLAIM.md`; the §2.6 prompt equation with `HEADER`
derived from 011's pinned prompt bytes minus 010's locked policy bytes; the
§2.6 document structure parsed; the preamble and conventions equalities
checked both ways (cross-arm equality AND derivation from 010's bytes); the
clause-body digit-run census under §2.6's definition, the inclusivity-adjacency
tuple sequences with the registered closed vocabulary, arm C's permutation
re-derived by enumerating all 120, arm D's census under sigma, arm E's
digit-run rules over the whole file; and the 280-cell landmark-grid equalities
of §2.4 — every arm's mirror verdict vector and family class vector elementwise
equal to arm A's.

**C9 — the class schema, structurally and extensionally.** Every arm's
`FAMILY.json` must equal §2.3's schema instantiated at that arm's
(`T_low`, `T_high`): six contiguous indices and structural equality of all six
predicate encodings after substituting the pair. Arm A's must additionally
equal Study 010's locked family byte for byte (checked in tier 1).

**C10's gate.** `verify()` refuses while any arm's clean-room second mirror
(`analysis/mirror2_<arm>.py`) is missing or disagrees with the registered
mirror on that arm's 280-cell grid. This is a precondition of the batch, not a
post-hoc analysis (§6 C10); the attempt ledger itself lives in
`MIRROR-AGREEMENT.md` and is reviewed, not parsed.

**Stage-aware members, named rather than implied.** Two registry members are
null until their registered moment and are skipped while null, because §2.10
says so in both cases: `claim.sha256` (pinned before the freeze; a `CLAIM.md`
missing AT the freeze is a defect, so the check becomes required as soon as
`freeze.preregistrationSha256` is non-null) and `freeze.treeManifestSha256`
(recorded by the final review round; when non-null the whole-tree manifest is
recomputed and must match). `golden.sha256` is likewise null until §3.2's
capture and is the scorer's to enforce per slot, not this module's.

What this module does NOT do, so §7 cannot claim it: it compares no file to a
git HEAD blob; it does not verify that arm B's prose is a paraphrase or that
arm E's references are comprehensible (C8 says which controls bound that and
that none closes it); and it does not authenticate `MIRROR-AGREEMENT.md`'s
narrative — it runs the agreement, which is the checkable part.
"""
from __future__ import annotations
import hashlib
import importlib.util
import itertools
import json
import os
import platform
import re
import subprocess
import sys
from collections import Counter
from decimal import Decimal

# The ceremony's commands run with bytecode writing disabled (§2.10, round 5
# finding 3): set structurally, not left to the operator's environment. Round
# 9, finding 1: README step 1 invokes this file by path, so it is one of those
# commands — the flag belongs in every entry the ceremony names, not in one.
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
ELEVEN = os.path.normpath(os.path.join(STUDY, "..", "011-authorship-coverage-rates"))
TEN = os.path.normpath(os.path.join(STUDY, "..", "010-blinded-oracle"))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
# The single registered mirror module (§2.2 [D-14]) is imported LAZILY:
# the bytecode gate must run before any grid module loads, or a poisoned
# cache would already be executing when the gate inspected it (round 6,
# finding 1).
def _mirror():
    import policy_mirror  # noqa: E402
    return policy_mirror

# §2.2's chain table: the two ends this study pins itself. 010's lock digest is
# NOT here — it is read from 011's PINS.json, which is what "the digest 011
# pins for it, not one this study chooses" means in code.
ELEVEN_PINS_SHA256 = "e00076972377a640236c95496feb083e49730f22c80d82b896d1d1d77fc6dc79"
ELEVEN_PORTS_SHA256 = "783cc9c32f8b2c77ba3ab91cbe4caaa91e9d9b035dd539659b77ed423f689ea3"

ARMS = ("A", "B", "C", "D", "E")

# §2 and §2.4: the registered threshold pairs. ARM.json carries each pair and
# is pinned, but the pairs themselves are registered here in reviewed code —
# a pinned file stating (50, 80) for arm D would otherwise pass every digest.
REGISTERED_PAIRS = {"A": ("40", "70"), "B": ("40", "70"), "C": ("40", "70"),
                    "D": ("45", "72"), "E": ("40", "70")}

# §2.6 [D-5]: arm C's registered presentation order, re-derived below by
# enumeration rather than trusted from this constant (the constant is what the
# enumeration's unique answer is required to equal).
PERMUTATION_C = ("P1", "P2", "P4", "P5", "P3")

# §2.6's closed inclusivity vocabulary. Longest-first, so "at or above" is not
# consumed as "or above" with a stray "at" left behind.
INCLUSIVE_CUES = ("at or above", "or above", "or more", "or higher")
EXCLUSIVE_CUES = ("less than", "below", "under")

THREE_PART = "absent a sanctions hit or an embargoed registration"
TWO_PART = "absent a sanctions hit"

# §2.6 [D-16]: PREAMBLE_DELTA, the single registered substitution.
PREAMBLE_DELTA = ("Study 010", "this study")

# The port table's registered destination set (§2.2's three tables). A row
# deleted from PORTS.md is a check silently dropped, so the set must be exact.
REQUIRED_PORTS = frozenset((
    "harness/policy_mirror.py",
    "arms/A/POLICY.md",
    "arms/A/FAMILY.json",
    "transcription/PROBE-PROMPT.txt",
    "harness/records_compile.py",
    "harness/transcript_check.py",
    "transcription/authoring_call.sh",
    "harness/integrity.py",
    "harness/batch.py",
    "harness/score_rates.py",
    "harness/census.py",
))

# Tier 1 (§6 C1): destination -> the key 010's PROTOCOL-LOCK.json locks the
# source under. arms/A/POLICY.md is source-bound to the lock and
# destination-bound to PORTS.md (it carries the two registered deltas).
TIER1_LOCK_KEYS = {
    "harness/policy_mirror.py": "harness/policy_mirror.py",
    "arms/A/POLICY.md": "policy/POLICY.md",
    "arms/A/FAMILY.json": "FAMILY.json",
}
# Tier-1 destinations that must ALSO equal the lock digest (byte-identical).
TIER1_LOCK_BOTH_SIDES = frozenset(("arms/A/FAMILY.json",))
# Tier 2: destination -> the 011 PINS.json member that pins it.
TIER2_PINS_MEMBERS = {"transcription/PROBE-PROMPT.txt": "probePrompt"}
# Tier 3: destination -> the path 011's own PORTS.md records it under.
TIER3_ELEVEN_PATHS = {
    "harness/records_compile.py": "harness/records_compile.py",
    "harness/transcript_check.py": "harness/transcript_check.py",
    "transcription/authoring_call.sh": "transcription/authoring_call.sh",
}
# No tier (§6 C1): 011 pinned none of these; source cells are checked against
# 011's working files — the recorded commit, and nothing older.
ELEVEN_OWN_SOURCES = {
    "harness/integrity.py": "harness/integrity.py",
    "harness/batch.py": "harness/batch.py",
    "harness/score_rates.py": "harness/score_rates.py",
    "harness/census.py": "analysis/diversity.py",
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


# --- §2.4's landmark grid, the instrument C8 clause 6 and C10 both read ------

COUNTRIES = ("KP", "IR", "SY", "CA", "DE")


def landmarks(t_low, t_high) -> list:
    """§2.4's FOURTEEN landmarks, as exact decimal strings: five ON an edge
    some predicate names (T_low-1, T_low, T_low+1, T_high, T_high+1), seven
    0.01 probes beside one of those edges, and the floor and the ceiling. The
    set was closed twice by a review that found a mutant family it could not
    see (T_low+1 and T_high+1 with their probes in round 1; T_low-1-0.01 in
    round 2)."""
    low, high = Decimal(t_low), Decimal(t_high)
    cent = Decimal("0.01")
    values = [Decimal(0),
              low - 1 - cent,
              low - 1, low - cent, low,
              low + cent, low + 1 - cent, low + 1,
              high - cent, high, high + cent,
              high + 1 - cent, high + 1,
              Decimal(100)]
    return [format(value, "f") for value in values]


def grid(t_low, t_high) -> list:
    """{false,true} x {KP,IR,SY,CA,DE} x {false,true} x landmarks — 280 cells,
    in the registered cell order (the order matters: C8 compares vectors
    elementwise)."""
    cells = []
    for sanctions in (False, True):
        for country in COUNTRIES:
            for personal in (False, True):
                for score in landmarks(t_low, t_high):
                    cells.append({"sanctionsHit": sanctions,
                                  "registeredCountry": country,
                                  "handlesPersonalData": personal,
                                  "riskScore": score})
    return cells


def verdict_vector(t_low, t_high) -> list:
    return [_mirror().verdict(cell, t_low, t_high)
            for cell in grid(t_low, t_high)]


def class_vector(classes: list, t_low, t_high) -> list:
    """One tuple of matching class indices per cell of that arm's own grid."""
    return [tuple(entry["index"] for entry in classes
                  if _mirror().predicate_matches(entry["predicate"], cell))
            for cell in grid(t_low, t_high)]


# --- §2.6's document structure and its checks --------------------------------

BULLET = re.compile(r"^- \*\*(P[1-5])\.\*\* (.*)$")


def parse_policy(data: bytes):
    """(preamble, [(label, raw body)] in presentation order, conventions).

    §2.6 registers the structure this parses: a preamble (title line and
    introductory paragraph), five clause bullets `- **P<n>.** `, and a trailing
    conventions paragraph. Raw bodies keep their line breaks so byte-identity
    across arms is checkable; census and cue scanning flatten them first.
    """
    lines = data.decode("utf-8").split("\n")
    bullets = []          # (label, [lines])
    preamble_lines = []
    conventions_lines = []
    state = "preamble"
    for line in lines:
        match = BULLET.match(line)
        if match:
            bullets.append((match.group(1), [match.group(2)]))
            state = "bullets"
            continue
        if state == "preamble":
            preamble_lines.append(line)
        elif state == "bullets":
            if line.startswith("  ") and line.strip():
                bullets[-1][1].append(line[2:])
            elif not line.strip():
                state = "after"
            else:
                raise IntegrityError(
                    "a policy line is neither a bullet, a continuation, nor a "
                    "blank separator: %r" % line)
        else:
            conventions_lines.append(line)
    if len(bullets) != 5:
        raise IntegrityError("a policy text carries %d clause bullets, not 5"
                             % len(bullets))
    labels = [label for label, _ in bullets]
    if sorted(labels) != ["P1", "P2", "P3", "P4", "P5"]:
        raise IntegrityError("the clause labels are %r: each of P1-P5 must "
                             "appear exactly once" % (labels,))
    preamble = "\n".join(preamble_lines).strip("\n")
    conventions = "\n".join(conventions_lines).strip("\n")
    if not preamble or not conventions:
        raise IntegrityError("a policy text is missing its preamble or its "
                             "conventions paragraph")
    bodies = [(label, "\n".join(parts)) for label, parts in bullets]
    return preamble, bodies, conventions


def flat(body: str) -> str:
    """A clause body as one line of single-spaced text, emphasis stripped —
    the form the census and the cue scan read (§2.6 masks and strips before
    counting)."""
    return " ".join(body.replace("*", "").split())


def mask_labels(text: str) -> str:
    """§2.6: clause-label tokens P1-P5 masked out first — they are structural
    cross-references, present identically in every arm."""
    return re.sub(r"\bP[1-5]\b", " ", text)


def census(body: str) -> Counter:
    """The clause-body digit-run census: the multiset of maximal digit runs
    with clause labels masked out first (§2.6, definition used by every check
    below and by C8 clause 5)."""
    return Counter(re.findall(r"[0-9]+", mask_labels(flat(body))))


def bounds(label: str, body: str) -> list:
    """[(label, literal, side, sense)] for every digit run in one clause body,
    in reading order, under §2.6's closed vocabulary. Every literal must carry
    exactly one adjacent cue — a bound with no cue, two cues, or a cue not in
    the vocabulary refuses."""
    text = mask_labels(flat(body))
    tuples = []
    for match in re.finditer(r"[0-9]+", text):
        literal = match.group(0)
        before = text[:match.start()].rstrip()
        after = text[match.end():].lstrip()
        found = []
        for sense, cues in (("inclusive", INCLUSIVE_CUES),
                            ("exclusive", EXCLUSIVE_CUES)):
            for cue in cues:
                if after.lower().startswith(cue):
                    found.append(("after", sense, cue))
                    break
            else:
                continue
            break
        for sense, cues in (("inclusive", INCLUSIVE_CUES),
                            ("exclusive", EXCLUSIVE_CUES)):
            for cue in cues:
                if before.lower().endswith(cue):
                    found.append(("before", sense, cue))
                    break
            else:
                continue
            break
        if len(found) != 1:
            raise IntegrityError(
                "clause %s states the literal %s with %s adjacent inclusivity "
                "cues from the registered vocabulary; the invariant needs "
                "exactly one" % (label, literal, len(found) or "no"))
        side, sense, _ = found[0]
        tuples.append((label, literal, side, sense))
    return tuples


NAME_KEYS = (("personal-data threshold", "T_low"), ("review threshold", "T_high"))


def name_bounds(label: str, body: str) -> list:
    """[(label, T_low|T_high, sense)] for arm E: cues attach to the two
    registered threshold NAMES, and a named bound carries no side (§2.6 — the
    side flips from after the literal to before the name at the inclusive
    bounds, a flip inherent to denaming)."""
    text = mask_labels(flat(body)).lower()
    hits = []
    for name, key in NAME_KEYS:
        for match in re.finditer(re.escape(name), text):
            before = text[:match.start()].rstrip()
            if before.endswith("the"):
                before = before[:-3].rstrip()
            after = text[match.end():].lstrip()
            sense = None
            for candidate, cues in (("inclusive", INCLUSIVE_CUES),
                                    ("exclusive", EXCLUSIVE_CUES)):
                for cue in cues:
                    if before.endswith(cue) or after.startswith(cue):
                        sense = candidate
                        break
                if sense:
                    break
            if sense:
                hits.append((match.start(), (label, key, sense)))
    return [entry for _, entry in sorted(hits)]


def sigma(pair_a, pair_x):
    """The literal substitution §2.4 registers, as a mapping over decimal
    strings: T_low and its two derived edges, T_high and its one."""
    low_a, high_a = Decimal(pair_a[0]), Decimal(pair_a[1])
    low_x, high_x = Decimal(pair_x[0]), Decimal(pair_x[1])
    mapping = {}
    for base_a, base_x, offsets in ((low_a, low_x, (-1, 0, 1)),
                                    (high_a, high_x, (0, 1))):
        for offset in offsets:
            mapping[format(base_a + offset, "f")] = format(base_x + offset, "f")
    return mapping


def apply_sigma(counter: Counter, mapping: dict) -> Counter:
    return Counter({mapping.get(run, run): count
                    for run, count in counter.items()})


def establishers(bodies: list) -> tuple:
    """(sanctions establisher, embargo establisher), re-derived from the parsed
    bodies (§2.6's conditions 2 and 3 name what each establishes)."""
    sanctions = [label for label, body in bodies
                 if "sanction" in flat(body).lower()
                 and not flat(body).lower().startswith("absent")]
    embargo = [label for label, body in bodies
               if "embargo" in flat(body).lower()
               and not flat(body).lower().startswith(THREE_PART)]
    if len(sanctions) != 1 or len(embargo) != 1:
        raise IntegrityError(
            "the establishing clauses do not re-derive: %r establish sanctions "
            "hits and %r embargoed registrations; conditions 2 and 3 need one "
            "of each" % (sanctions, embargo))
    return sanctions[0], embargo[0]


def backward(order: tuple, bodies_by_label: dict, sanc: str, emb: str) -> bool:
    """§2.6's conditions 1-3 for one presentation order."""
    position = {label: index for index, label in enumerate(order)}
    for label in order:
        body = flat(bodies_by_label[label]).lower()
        for reference in re.findall(r"\bp([1-5])\b", body):
            referenced = "P" + reference
            if referenced != label and position[referenced] >= position[label]:
                return False
        if body.startswith(THREE_PART):
            if position[sanc] >= position[label] or position[emb] >= position[label]:
                return False
        elif body.startswith(TWO_PART):
            if position[sanc] >= position[label]:
                return False
    return True


def movement(order: tuple) -> int:
    return sum(1 for index, label in enumerate(order)
               if label != "P%d" % (index + 1))


# --- the chain (C1) ----------------------------------------------------------

def verify_chain(study: str = STUDY, eleven: str = ELEVEN, ten: str = TEN,
                 ports_path: str = None, pins_path: str = None) -> dict:
    """C1: the three-level chain, then the three tiers, then the untierable
    four. Returns {'pins': ..., 'rows': ...} for the callers that verify
    further."""
    ports_path = ports_path or os.path.join(study, "harness", "PORTS.md")
    pins_path = pins_path or os.path.join(study, "harness", "PINS.json")

    # The two ends first (§2.2's chain table): everything below reads them.
    eleven_pins_path = os.path.join(eleven, "harness", "PINS.json")
    eleven_ports_path = os.path.join(eleven, "harness", "PORTS.md")
    for path, pinned, name in ((eleven_pins_path, ELEVEN_PINS_SHA256,
                                "Study 011's harness/PINS.json"),
                               (eleven_ports_path, ELEVEN_PORTS_SHA256,
                                "Study 011's harness/PORTS.md")):
        if not os.path.isfile(path):
            raise IntegrityError("%s is missing" % name)
        actual = digest(path)
        if actual != pinned:
            raise IntegrityError("%s is sha256:%s, not the pinned sha256:%s"
                                 % (name, actual, pinned))
    eleven_pins = load_json(eleven_pins_path)

    # The registry's own provenance members answer to the review-bound
    # constants above — a registry stating a different chain would
    # otherwise stand uncontradicted while the code checked its own
    # numbers (round 6, finding 11).
    # (checked after this study's registry is loaded, below)

    # 010's lock, at the digest 011 pins for it — not one this study chooses.
    lock_path = os.path.join(ten, "PROTOCOL-LOCK.json")
    if not os.path.isfile(lock_path):
        raise IntegrityError("Study 010's PROTOCOL-LOCK.json is missing")
    lock_pin = bare(eleven_pins.get("pinnedFrom", {}).get("fileSha256"))
    lock_digest = digest(lock_path)
    if lock_digest != lock_pin:
        raise IntegrityError(
            "Study 010's PROTOCOL-LOCK.json is sha256:%s, not the sha256:%s "
            "Study 011 pins for it" % (lock_digest, lock_pin))
    locked = load_json(lock_path).get("lockedInputs")
    if not isinstance(locked, dict) or not locked:
        raise IntegrityError("Study 010's PROTOCOL-LOCK.json carries no "
                             "lockedInputs map")

    # This study's own registry, then its own PORTS.md at the registry's pin —
    # the file that records what each enumerated change WAS cannot be
    # rewritten after the review.
    if not os.path.isfile(pins_path):
        raise IntegrityError("no registry at %s" % pins_path)
    # §7's sentence, made true verbatim: a `(port time)` placeholder surviving
    # into either run-time file is an unfinished port, refused by name (the
    # all-zero digest markers refuse too, through the mismatches below).
    for path, name in ((ports_path, "harness/PORTS.md"),
                       (pins_path, "harness/PINS.json")):
        with open(path, "rb") as handle:
            if b"(port time)" in handle.read():
                raise IntegrityError(
                    "%s still carries a `(port time)` placeholder: the port is "
                    "not finished (§7)" % name)
    pins = load_json(pins_path)
    own_ports_pin = bare(pins.get("ownPorts", {}).get("sha256"))
    actual_ports = digest(ports_path)
    if actual_ports != own_ports_pin:
        raise IntegrityError(
            "harness/PORTS.md is sha256:%s, not the sha256:%s harness/PINS.json "
            "records for it" % (actual_ports, own_ports_pin))

    recorded = pins.get("pinnedFrom", {})
    for member, expected, path_expected in (
            ("pins", ELEVEN_PINS_SHA256, "harness/PINS.json"),
            ("ports", ELEVEN_PORTS_SHA256, "harness/PORTS.md")):
        entry = recorded.get(member) or {}
        stated = bare(entry.get("sha256"))
        if stated != expected:
            raise IntegrityError(
                "the registry's pinnedFrom.%s digest (%s) is not the "
                "review-bound %s" % (member, stated, expected))
        if entry.get("path") != path_expected:
            raise IntegrityError(
                "the registry's pinnedFrom.%s path (%r) is not %r"
                % (member, entry.get("path"), path_expected))
    if recorded.get("study") != "studies/011-authorship-coverage-rates" or \
            recorded.get("commit") != "3b93d3e7917e917516bd55cf4c7f5285c91fbc13":
        raise IntegrityError(
            "the registry's pinnedFrom study or commit is not the recorded "
            "port provenance (round 7, finding 11)")

    rows = parse_ports(ports_path)
    destinations = set(row[2] for row in rows)
    if destinations != set(REQUIRED_PORTS):
        missing = sorted(set(REQUIRED_PORTS) - destinations)
        extra = sorted(destinations - set(REQUIRED_PORTS))
        raise IntegrityError(
            "harness/PORTS.md does not name exactly the registered port set "
            "(missing %s, unexpected %s)" % (missing or "none", extra or "none"))

    eleven_rows = {row[2]: row for row in parse_ports(eleven_ports_path)}

    for source, source_sha, destination, destination_sha in rows:
        here = os.path.join(study, destination)
        if not os.path.isfile(here):
            raise IntegrityError("the ported file %s is missing" % destination)
        actual = digest(here)
        if actual != destination_sha:
            raise IntegrityError(
                "%s is sha256:%s, not the sha256:%s harness/PORTS.md records"
                % (destination, actual, destination_sha))

        if destination in TIER1_LOCK_KEYS:
            lock_key = TIER1_LOCK_KEYS[destination]
            if lock_key not in locked:
                raise IntegrityError("Study 010's lock does not lock %s"
                                     % lock_key)
            lock_sha = bare(locked[lock_key])
            if source_sha != lock_sha:
                raise IntegrityError(
                    "harness/PORTS.md records sha256:%s for %s and 010's lock "
                    "records sha256:%s" % (source_sha, lock_key, lock_sha))
            origin = os.path.join(ten, lock_key)
            if not os.path.isfile(origin) or digest(origin) != lock_sha:
                raise IntegrityError(
                    "Study 010's %s does not hash to its own lock" % lock_key)
            if destination in TIER1_LOCK_BOTH_SIDES and actual != lock_sha:
                raise IntegrityError(
                    "%s is ported byte-identically from 010's lock and is "
                    "sha256:%s, not sha256:%s" % (destination, actual, lock_sha))
        elif destination in TIER2_PINS_MEMBERS:
            member = eleven_pins.get(TIER2_PINS_MEMBERS[destination])
            pinned = bare((member or {}).get("sha256"))
            if source_sha != pinned or actual != pinned:
                raise IntegrityError(
                    "%s must equal the digest Study 011's PINS.json records "
                    "(sha256:%s); the table records sha256:%s and the file is "
                    "sha256:%s" % (destination, pinned, source_sha, actual))
        elif destination in TIER3_ELEVEN_PATHS:
            eleven_path = TIER3_ELEVEN_PATHS[destination]
            row = eleven_rows.get(eleven_path)
            if row is None:
                raise IntegrityError(
                    "Study 011's PORTS.md carries no provenance row for %s"
                    % eleven_path)
            if source_sha != row[3]:
                raise IntegrityError(
                    "harness/PORTS.md records sha256:%s as the 011-side digest "
                    "of %s and 011's own PORTS.md records sha256:%s"
                    % (source_sha, eleven_path, row[3]))
            origin = os.path.join(eleven, eleven_path)
            if not os.path.isfile(origin) or digest(origin) != source_sha:
                raise IntegrityError(
                    "Study 011's %s does not hash to the recorded 011-side "
                    "digest" % eleven_path)
        else:
            # 011's own harness: no lock, no pin — the recorded commit only.
            eleven_path = ELEVEN_OWN_SOURCES[destination]
            origin = os.path.join(eleven, eleven_path)
            if not os.path.isfile(origin) or digest(origin) != source_sha:
                raise IntegrityError(
                    "Study 011's %s does not hash to the sha256:%s this "
                    "study's PORTS.md records as its source; the recorded "
                    "commit is the only authority these four files have"
                    % (eleven_path, source_sha))

    # 011's prompt (the HEADER source) at 010's lock, both copies.
    prompt_pin = bare(locked["transcription/PROMPT.txt"])
    eleven_prompt = os.path.join(eleven, "transcription", "PROMPT.txt")
    if digest(eleven_prompt) != prompt_pin:
        raise IntegrityError("Study 011's transcription/PROMPT.txt does not "
                             "hash to 010's lock")

    # Tier 1's "equal to 011's own copy where 011 holds one", and tier 2's
    # source-byte binding, checked against 011's working files rather than
    # only against digests this study carries (round 3, finding 17).
    for eleven_path, expected, label in (
            ("FAMILY.json", bare(locked["FAMILY.json"]),
             "Study 011's FAMILY.json vs 010's lock"),
            (os.path.join("harness", "policy_mirror.py"),
             bare(locked["harness/policy_mirror.py"]),
             "Study 011's policy_mirror.py vs 010's lock"),
            (os.path.join("transcription", "PROBE-PROMPT.txt"),
             bare(eleven_pins["probePrompt"]["sha256"]),
             "Study 011's PROBE-PROMPT.txt vs 011's own registry")):
        path = os.path.join(eleven, eleven_path)
        if not os.path.isfile(path) or digest(path) != expected:
            raise IntegrityError("%s: the copy does not hash to its pin"
                                 % label)

    return {"pins": pins, "rows": rows, "lockedInputs": locked,
            "lockSha256": lock_digest}


# --- the arm artifacts (C8, C9) ---------------------------------------------

def verify_arms(study: str = STUDY, eleven: str = ELEVEN, ten: str = TEN,
                pins: dict = None) -> dict:
    pins = pins if pins is not None else load_json(
        os.path.join(study, "harness", "PINS.json"))

    # Clause 1 — digests. Twenty arm files, the mirror, the assembled
    # preamble, CONVENTIONS_DELTA, and CLAIM.md (stage-gated: see module
    # docstring).
    arms_pins = pins.get("arms")
    if not isinstance(arms_pins, dict) or set(arms_pins) != set(ARMS):
        raise IntegrityError("harness/PINS.json pins %r, not the five arms"
                             % sorted(arms_pins or ()))
    for arm in ARMS:
        entry = arms_pins[arm]
        for member, name in (("policySha256", "POLICY.md"),
                             ("promptSha256", "PROMPT.txt"),
                             ("familySha256", "FAMILY.json"),
                             ("armSha256", "ARM.json")):
            path = os.path.join(study, "arms", arm, name)
            if not os.path.isfile(path):
                raise IntegrityError("arms/%s/%s is missing" % (arm, name))
            actual = digest(path)
            if actual != bare(entry.get(member)):
                raise IntegrityError(
                    "arms/%s/%s is sha256:%s, not the pinned %s"
                    % (arm, name, actual, entry.get(member)))
    mirror_pin = pins.get("mirror", {})
    mirror_path = os.path.join(study, "harness", "policy_mirror.py")
    if digest(mirror_path) != bare(mirror_pin.get("sha256")):
        raise IntegrityError("harness/policy_mirror.py does not hash to its "
                             "registered destination digest")
    delta_entry = pins.get("conventionsDelta", {})
    preamble_entry = pins.get("assembledPreamble", {})
    claim_entry = pins.get("claim", {})
    freeze_entry = pins.get("freeze", {})
    if claim_entry.get("sha256") is None:
        if freeze_entry.get("preregistrationSha256") is not None:
            raise IntegrityError("CLAIM.md is unpinned at the freeze (§1)")
    else:
        claim_path = os.path.join(study, claim_entry.get("path", "CLAIM.md"))
        if not os.path.isfile(claim_path):
            raise IntegrityError("CLAIM.md is pinned but missing")
        if digest(claim_path) != bare(claim_entry.get("sha256")):
            raise IntegrityError("CLAIM.md does not hash to its pin")

    # ARM.json content: the registered pairs, in reviewed code (§2, §2.4).
    pairs = {}
    for arm in ARMS:
        arm_doc = load_json(os.path.join(study, "arms", arm, "ARM.json"))
        pair = (str(arm_doc.get("thresholds", {}).get("tLow")),
                str(arm_doc.get("thresholds", {}).get("tHigh")))
        if arm_doc.get("arm") != arm or pair != REGISTERED_PAIRS[arm]:
            raise IntegrityError(
                "arms/%s/ARM.json declares arm %r at %r; the registration is "
                "%s at %r" % (arm, arm_doc.get("arm"), pair, arm,
                              REGISTERED_PAIRS[arm]))
        pairs[arm] = pair

    # Clause 2 — the prompt equation. HEADER is derived, not authored: 011's
    # pinned prompt bytes with 010's locked policy bytes (minus their final
    # LF) removed from the end — 948 bytes (§2.6).
    with open(os.path.join(eleven, "transcription", "PROMPT.txt"), "rb") as handle:
        eleven_prompt = handle.read()
    with open(os.path.join(ten, "policy", "POLICY.md"), "rb") as handle:
        ten_policy = handle.read()
    ten_policy_trimmed = ten_policy[:-1] if ten_policy.endswith(b"\n") else ten_policy
    if not eleven_prompt.endswith(ten_policy_trimmed):
        raise IntegrityError("011's prompt does not end with 010's policy "
                             "bytes: HEADER cannot be derived")
    header = eleven_prompt[:-len(ten_policy_trimmed)]
    if len(header) != 948:
        raise IntegrityError("the derived HEADER is %d bytes, not the "
                             "registered 948" % len(header))
    policies, prompts = {}, {}
    for arm in ARMS:
        with open(os.path.join(study, "arms", arm, "POLICY.md"), "rb") as handle:
            policies[arm] = handle.read()
        with open(os.path.join(study, "arms", arm, "PROMPT.txt"), "rb") as handle:
            prompts[arm] = handle.read()
        trimmed = policies[arm][:-1] if policies[arm].endswith(b"\n") else policies[arm]
        if prompts[arm] != header + trimmed:
            raise IntegrityError(
                "arms/%s/PROMPT.txt does not equal HEADER + POLICY.md minus "
                "its final LF (§2.6's prompt equation)" % arm)

    # Clause 3 — structure; clause 4 — preamble and conventions, both ways.
    parsed = {arm: parse_policy(policies[arm]) for arm in ARMS}
    preambles = {arm: parsed[arm][0] for arm in ARMS}
    conventions = {arm: parsed[arm][2] for arm in ARMS}
    if len(set(preambles.values())) != 1:
        raise IntegrityError("the preamble is not byte-identical across the "
                             "five arms")
    ten_preamble, ten_bodies, ten_conventions = parse_policy(ten_policy)
    if ten_preamble.count(PREAMBLE_DELTA[0]) != 1:
        raise IntegrityError("010's preamble does not carry %r exactly once; "
                             "PREAMBLE_DELTA has no single occurrence to apply "
                             "to" % (PREAMBLE_DELTA[0],))
    derived_preamble = ten_preamble.replace(PREAMBLE_DELTA[0], PREAMBLE_DELTA[1])
    if preambles["A"] != derived_preamble:
        raise IntegrityError("the arms' preamble is not 010's preamble with "
                             "PREAMBLE_DELTA applied (§2.6 [D-16])")
    preamble_digest = hashlib.sha256(preambles["A"].encode("utf-8")).hexdigest()
    if preamble_digest != bare(preamble_entry.get("sha256")):
        raise IntegrityError("the assembled preamble does not hash to its pin")

    if len(set(conventions[arm] for arm in ("A", "B", "C", "D"))) != 1:
        raise IntegrityError("the conventions paragraph is not byte-identical "
                             "across arms A-D")
    base_conventions = conventions["A"]
    if not base_conventions.startswith(ten_conventions):
        raise IntegrityError("the conventions paragraph does not begin with "
                             "010's conventions bytes")
    delta = base_conventions[len(ten_conventions):]
    delta_digest = hashlib.sha256(delta.encode("utf-8")).hexdigest()
    if delta_digest != bare(delta_entry.get("sha256")):
        raise IntegrityError("CONVENTIONS_DELTA (the %d bytes appended to "
                             "010's conventions) does not hash to its pin"
                             % len(delta))
    if not conventions["E"].startswith(base_conventions):
        raise IntegrityError("arm E's conventions paragraph does not begin "
                             "with the shared A-D paragraph")
    e_suffix = conventions["E"][len(base_conventions):]
    if not e_suffix or re.search(r"[0-9]", e_suffix):
        raise IntegrityError("arm E's appended threshold-definition sentence "
                             "is missing or carries a digit")
    suffix_pin = pins.get("thresholdDefinitionSentence", {})
    suffix_digest = hashlib.sha256(e_suffix.encode("utf-8")).hexdigest()
    if suffix_digest != bare(suffix_pin.get("sha256")):
        raise IntegrityError("arm E's appended threshold-definition sentence "
                             "does not hash to its registry pin (round 3, "
                             "finding 7): shape is not the registered check, "
                             "bytes are")

    # Clause 5 — censuses, cues, permutation, sigma, arm E's digit rules.
    bodies = {arm: parsed[arm][1] for arm in ARMS}
    body_census = {arm: sum((census(body) for _, body in bodies[arm]), Counter())
                   for arm in ARMS}
    census_a = Counter({"40": 2, "70": 4})
    if body_census["A"] != census_a:
        raise IntegrityError("arm A's clause-body census is %r, not "
                             "{40 x2, 70 x4}" % (dict(body_census["A"]),))
    if body_census["B"] != census_a:
        raise IntegrityError("arm B's clause-body census does not equal arm "
                             "A's")
    mapping_d = sigma(pairs["A"], pairs["D"])
    if body_census["D"] != apply_sigma(census_a, mapping_d):
        raise IntegrityError("arm D's clause-body census is not arm A's under "
                             "sigma")
    if body_census["E"]:
        raise IntegrityError("arm E's clause-body census is %r, not empty"
                             % (dict(body_census["E"]),))

    tuples = {arm: [entry
                    for label, body in sorted(bodies[arm])
                    for entry in bounds(label, body)]
              for arm in ("A", "B", "D")}
    if tuples["B"] != tuples["A"]:
        raise IntegrityError("arm B's inclusivity-adjacency tuple sequence "
                             "does not equal arm A's clause for clause")
    expected_d = [(label, mapping_d.get(literal, literal), side, sense)
                  for label, literal, side, sense in tuples["A"]]
    if tuples["D"] != expected_d:
        raise IntegrityError("arm D's inclusivity-adjacency tuple sequence "
                             "does not equal arm A's under sigma")
    key_of = {pairs["A"][0]: "T_low", pairs["A"][1]: "T_high"}
    expected_e = [(label, key_of[literal], sense)
                  for label, literal, side, sense in tuples["A"]
                  if literal in key_of]
    actual_e = [entry
                for label, body in sorted(bodies["E"])
                for entry in name_bounds(label, body)]
    if actual_e != expected_e:
        raise IntegrityError(
            "arm E's six bound senses are %r; arm A's, mapped to the "
            "threshold names, are %r" % (actual_e, expected_e))

    bodies_a = dict(bodies["A"])
    # Clause 5's byte relations, as registered rather than as statistics
    # (round 3, finding 7): A's bodies are 010's byte for byte and in order,
    # D's are A's under the registered literal substitution, and E's P1 and
    # P2 are A's. The censuses above remain as the shape checks; these are
    # the equalities C8 promises.
    if bodies["A"] != ten_bodies:
        raise IntegrityError("arm A's clause bodies are not byte-identical "
                             "to 010's, in order")
    for (label_a, body_a), (label_d, body_d) in zip(bodies["A"], bodies["D"]):
        expected_d = re.sub(r"[0-9]+",
                            lambda match: mapping_d.get(match.group(0),
                                                        match.group(0)),
                            body_a)
        if label_a != label_d or body_d != expected_d:
            raise IntegrityError("arm D's %s body is not arm A's under the "
                                 "registered literal substitution, byte for "
                                 "byte" % label_d)
    for label in ("P1", "P2"):
        if dict(bodies["E"])[label] != bodies_a[label]:
            raise IntegrityError("arm E's %s body is not byte-identical to "
                                 "arm A's" % label)
    for arm in ("B",):
        if [label for label, _ in bodies[arm]] != ["P1", "P2", "P3", "P4", "P5"]:
            raise IntegrityError("arm B's clause order is not P1-P5")
    if dict(bodies["C"]) != bodies_a:
        raise IntegrityError("arm C's clause bodies are not byte-identical to "
                             "arm A's")
    order_c = tuple(label for label, _ in bodies["C"])
    if order_c != PERMUTATION_C:
        raise IntegrityError("arm C's presentation order is %r, not the "
                             "registered %r" % (order_c, PERMUTATION_C))
    sanc, emb = establishers(bodies["A"])
    if not backward(order_c, bodies_a, sanc, emb):
        raise IntegrityError("arm C's registered permutation does not resolve "
                             "every reference backward")
    best = movement(order_c)
    for candidate in itertools.permutations(("P1", "P2", "P3", "P4", "P5")):
        if candidate == order_c:
            continue
        if backward(candidate, bodies_a, sanc, emb) and movement(candidate) >= best:
            raise IntegrityError(
                "the registered permutation is not the unique maximum-movement "
                "backward-resolving permutation: %r moves %d"
                % (candidate, movement(candidate)))

    whole_e = Counter(re.findall(r"[0-9]+", policies["E"].decode("utf-8")))
    in_body_refs = Counter(
        ref for _, body in bodies["E"]
        for ref in re.findall(r"\bP([1-5])\b", flat(body)))
    # The count is REGISTERED at exactly one (§2.6: "five plus one"); deriving
    # the expectation from the body let an added reference self-authorize
    # (round 8, finding 7).
    if sum(in_body_refs.values()) != 1:
        raise IntegrityError(
            "arm E's clause bodies carry %d in-body clause-label references; "
            "the registration counts exactly one"
            % sum(in_body_refs.values()))
    expected_whole = Counter({"1": 1, "2": 1, "3": 1, "4": 1, "5": 1})
    expected_whole.update(in_body_refs)
    expected_whole.update({"3166": 1, "1": 1, "2": 1})
    if whole_e != expected_whole:
        raise IntegrityError(
            "arm E's whole-file digit runs are %r; the registration allows "
            "exactly the clause labels, %d in-body reference(s), and the ISO "
            "3166-1 alpha-2 token: %r"
            % (dict(whole_e), sum(in_body_refs.values()), dict(expected_whole)))
    for forbidden in (pairs["A"][0], pairs["A"][1]):
        if whole_e.get(forbidden):
            raise IntegrityError("arm E's file carries the digit run %s"
                                 % forbidden)

    # Clause 6 — the landmark grid; C9 — the schema, structurally.
    families = {arm: load_json(os.path.join(study, "arms", arm, "FAMILY.json"))
                for arm in ARMS}
    vector_a = verdict_vector(*pairs["A"])
    classes_a = families["A"]["mutations"]
    class_a = class_vector(classes_a, *pairs["A"])
    for arm in ARMS:
        if verdict_vector(*pairs[arm]) != vector_a:
            raise IntegrityError(
                "arm %s's mirror verdict vector over its own 280-cell grid is "
                "not elementwise equal to arm A's" % arm)
        mutations = families[arm]["mutations"]
        indices = [entry["index"] for entry in mutations]
        if indices != list(range(6)) or any(
                type(index) is not int for index in indices):
            raise IntegrityError("arm %s's family indices are not the "
                                 "contiguous INTEGERS 0-5 (a JSON false is "
                                 "not an index; round 8, finding 8)" % arm)
        if class_vector(mutations, *pairs[arm]) != class_a:
            raise IntegrityError(
                "arm %s's family class vector over its own grid is not "
                "elementwise equal to arm A's" % arm)
        mapping = sigma(pairs["A"], pairs[arm])
        expected_predicates = [_substitute(entry["predicate"], mapping)
                               for entry in classes_a]
        actual_predicates = [entry["predicate"] for entry in mutations]
        if actual_predicates != expected_predicates:
            raise IntegrityError(
                "arm %s's six predicate encodings are not structurally equal "
                "to arm A's under its pair substitution (C9)" % arm)

    return {"pairs": pairs, "headerBytes": len(header),
            "preambleSha256": preamble_digest,
            "conventionsDeltaBytes": len(delta)}


def _substitute(node, mapping: dict):
    """A predicate encoding with the arm's pair substituted into every decimal
    string §2.4's sigma covers — structure untouched (C9's structural
    equality)."""
    if isinstance(node, dict):
        return {key: _substitute(value, mapping) for key, value in node.items()}
    if isinstance(node, list):
        return [_substitute(value, mapping) for value in node]
    if isinstance(node, str):
        return mapping.get(node, node)
    return node


# --- the clean-room second mirrors (C10's gate) ------------------------------

def verify_mirror2(study: str = STUDY, pairs: dict = None) -> list:
    """Refuses while any arm's `analysis/mirror2_<arm>.py` is missing or
    disagrees with the registered mirror on that arm's 280-cell grid. The
    attempts, the reader pre-assignment and every failure are
    MIRROR-AGREEMENT.md's to record; this function runs the agreement."""
    pairs = pairs or REGISTERED_PAIRS
    checked = []
    for arm in ARMS:
        path = os.path.join(study, "analysis", "mirror2_%s.py" % arm.lower())
        if not os.path.isfile(path):
            raise IntegrityError(
                "analysis/mirror2_%s.py is missing: §6 C10 makes every arm's "
                "clean-room second mirror a precondition of the batch, and "
                "the pre-assigned reader for arm %s has not produced one"
                % (arm.lower(), arm))
        spec = importlib.util.spec_from_file_location("mirror2_%s" % arm.lower(),
                                                      path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        pair = pairs[arm]
        for cell in grid(*pair):
            theirs = module.verdict(dict(cell))
            ours = _mirror().verdict(cell, *pair)
            if theirs != ours:
                raise IntegrityError(
                    "arm %s's clean-room mirror disagrees with the registered "
                    "mirror at %r: %r vs %r — a defect in the arm text or the "
                    "registered mirror, fixed before the freeze, not explained "
                    "after the data (§6 C10)" % (arm, cell, theirs, ours))
        checked.append(arm)
    return checked


# --- the whole-tree manifest ([D-20], from round 3 on) -----------------------

# The manifest's carrier handling (§2.10, round 3 finding 1 and round 4
# finding 2): PREREG-REVIEW.md is excluded — it carries the attestation —
# and PINS.json is bound through its NORMALIZED PROJECTION: the registry
# with its four post-freeze members nulled, serialized canonically, hashed
# into the manifest as its own entry. A covered-file edit paired with a
# registry co-edit therefore fails the recomputation.
MANIFEST_CARRIERS = ("harness/PINS.json", "PREREG-REVIEW.md")
POST_FREEZE_MEMBERS = (("freeze", "treeManifestSha256"),
                       ("freeze", "preregistrationSha256"),
                       ("golden", "sha256"),
                       ("isolationNegative", "assent"))


def manifest_excluded(name: str, members: tuple) -> bool:
    """§2.10's exclusion is a path LIST, not a pattern (round 9, finding 5).
    An entry ending in "/" names a tree: it excludes that tree and everything
    beneath it. Every other entry names exactly one file and excludes that
    path alone — a file-shaped entry does not swallow descendants, so a
    tracked `RESULTS.json/x` is reviewed bytes and belongs in the manifest."""
    for member in members:
        if member.endswith("/"):
            if name.startswith(member):
                return True
        elif name == member:
            return True
    return False


def normalized_pins(pins: dict) -> bytes:
    """The registry as the manifest binds it: the four members that are
    edited at registered moments after the freeze set to null, everything
    else byte-significant (§2.10)."""
    clone = json.loads(json.dumps(pins))
    for parent, member in POST_FREEZE_MEMBERS:
        clone.setdefault(parent, {})[member] = None
    return (json.dumps(clone, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def tree_manifest(study: str = STUDY, excluded: tuple = ()) -> str:
    """The sorted (relative path, byte length, sha256) list over every tracked
    regular file in the study directory, minus the registered exclusions and
    the two carrier files, and its sha256 — §2.10's binding of the reviewed
    bytes to the frozen ones."""
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--", "."],
        cwd=study, capture_output=True, check=True)
    entries = []
    excluded = tuple(excluded) + MANIFEST_CARRIERS
    for name in listing.stdout.decode("utf-8").split("\0"):
        if not name:
            continue
        if manifest_excluded(name, excluded):
            continue
        path = os.path.join(study, name)
        if not os.path.isfile(path) or os.path.islink(path):
            continue
        with open(path, "rb") as handle:
            data = handle.read()
        entries.append("%s %d %s" % (name, len(data),
                                     hashlib.sha256(data).hexdigest()))
    # The registry's normalized projection is a manifest entry of its own
    # (round 4, finding 2): the tree binds PINS.json minus exactly the
    # members the ceremony edits after the freeze.
    pins_path = os.path.join(study, "harness", "PINS.json")
    if os.path.isfile(pins_path):
        data = normalized_pins(load_json(pins_path))
        entries.append("harness/PINS.json#normalized %d %s"
                       % (len(data), hashlib.sha256(data).hexdigest()))
    manifest = "\n".join(sorted(entries)) + "\n"
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()


def verify_tree(study: str = STUDY, pins: dict = None) -> str:
    pins = pins if pins is not None else load_json(
        os.path.join(study, "harness", "PINS.json"))
    freeze = pins.get("freeze", {})
    pinned = freeze.get("treeManifestSha256")
    prereg_pin = freeze.get("preregistrationSha256")
    # The two freeze pins land together or not at all, in both directions
    # (round 4 finding 1; round 5 finding 2 made the coupling two-way).
    if (pinned is None) != (prereg_pin is None):
        raise IntegrityError(
            "the freeze pins disagree: preregistrationSha256 is %s and "
            "treeManifestSha256 is %s — they land together or not at all "
            "(§2.10)" % ("filled" if prereg_pin is not None else "null",
                         "filled" if pinned is not None else "null"))
    if pinned is None:
        return "unbound (pre-freeze; §2.10 binds the tree at the freeze)"
    # The pin must equal the attestation the final review round wrote into
    # PREREG-REVIEW.md (round 5, finding 1): a self-computed digest cannot
    # authenticate itself, so the pin answers to the review record —
    # defeating the binding means rewriting the record the reviewer holds.
    review_path = os.path.join(study, "PREREG-REVIEW.md")
    with open(review_path, "rb") as handle:
        review = handle.read().decode("utf-8")
    attested = re.findall(r"Tree manifest \(my computation\):\s*`?([0-9a-f]{64})`?",
                          review)
    if not attested:
        raise IntegrityError("PREREG-REVIEW.md carries no tree-manifest "
                             "attestation to check the freeze pin against")
    if bare(pinned) != attested[-1]:
        raise IntegrityError(
            "the frozen treeManifestSha256 (%s) is not the final round's "
            "attested digest (%s): the pin answers to the review record "
            "(§2.10)" % (bare(pinned), attested[-1]))
    actual = tree_manifest(study, tuple(freeze.get("excluded", ())))
    if actual != bare(pinned):
        raise IntegrityError(
            "the study tree's manifest is sha256:%s, not the sha256:%s the "
            "final review round attested: a byte changed after the review, "
            "and the only way forward is another round (§2.10)"
            % (actual, pinned))
    return "sha256:" + actual


# --- the interpreter, and the whole verification -----------------------------

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


def verify(study: str = STUDY, eleven: str = ELEVEN, ten: str = TEN) -> dict:
    """Everything, in the registered order: the chain, the arm artifacts, the
    interpreter, the clean-room mirrors, the tree manifest. IntegrityError on
    the first refusal; a summary dict when every check passed."""
    verify_bytecode(study)
    chain = verify_chain(study, eleven, ten)
    arms = verify_arms(study, eleven, ten, pins=chain["pins"])
    interpreter = verify_interpreter(chain["pins"])
    mirrors = verify_mirror2(study, arms["pairs"])
    tree = verify_tree(study, chain["pins"])
    return {"portedFiles": sorted(row[2] for row in chain["rows"]),
            "study010LockSha256": "sha256:" + chain["lockSha256"],
            "pairs": arms["pairs"],
            "headerBytes": arms["headerBytes"],
            "cleanRoomMirrors": mirrors,
            "treeManifest": tree,
            "interpreter": interpreter}


def main(argv: list) -> int:
    try:
        summary = verify()
    except IntegrityError as error:
        print("refused: %s" % error)
        return 1
    print("integrity verified: %d ported files; five arms at %s; HEADER %d "
          "bytes; clean-room mirrors %s; tree manifest %s; on %s"
          % (len(summary["portedFiles"]),
             ", ".join("%s=(%s,%s)" % (arm, low, high)
                       for arm, (low, high) in sorted(summary["pairs"].items())),
             summary["headerBytes"],
             ",".join(summary["cleanRoomMirrors"]),
             summary["treeManifest"],
             summary["interpreter"]))
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
