#!/usr/bin/env python3
"""C1 in code: the ported-byte digest table, verified before anything runs.

PREREGISTRATION.md §6 C1 registers that the ported bytes are Study 010's, and
§7 lists that table under what is mechanically enforced. This module is what
makes that true at run time rather than only in pytest: `batch.preflight()`
calls it before it creates a slot, and `score_rates.score()` calls it before it
reads one. A one-character drift in the byte-identical `policy_mirror.py` would
otherwise change a published rate and a §5 tier with nothing refusing.

**Where each column's authority comes from.** `harness/PORTS.md` is an editable
file in this study, so it cannot be the authority for what Study 010's bytes
were: an attacker who edits a port here need only edit that row's two digest
cells to keep the table self-consistent. Study 010's `PROTOCOL-LOCK.json` is
the authority for the SOURCE side, and it is itself pinned by digest in
`harness/PINS.json`. PORTS.md stays the authority for the DESTINATION side —
it is this study's change list, and there is nothing older to check a changed
port against.

What it checks, in this order, and nothing else (§7 claims exactly this list):

  1. `harness/PORTS.md`'s table parses, and names exactly the six ported files;
  2. `studies/010-blinded-oracle/PROTOCOL-LOCK.json` hashes to the digest
     `harness/PINS.json` pins in `pinnedFrom.fileSha256` (010's lock does not
     digest itself, so without this pin the table's authority is a mutable
     file). This is checked FIRST: everything below reads that file;
  3. the lock's `lockedInputs` map names every source the table names, and for
     every row BOTH the source file in `studies/010-blinded-oracle/` AND the
     source digest PORTS.md records hash to / equal the digest **the lock**
     records for it. So a row's source column is checked against 010's lock,
     never against the row itself;
  4. every destination file in this study hashes to the digest PORTS.md
     records for it — and, for the three ports §2.1 declares BYTE-IDENTICAL,
     to the digest the lock records for its source as well, so that claim
     rests on 010's lock rather than on a prose column;
  5. `PROMPT.txt`, `PROBE-PROMPT.txt` and `FAMILY.json` hash to the digests
     `harness/PINS.json` pins for them;
  6. the interpreter running this process is the one `harness/PINS.json` pins
     (implementation exactly, version series exactly; the patch level is
     recorded, not required — §2.6).

What it does NOT check, stated here so §7 cannot claim it: nothing is compared
to a git HEAD blob, and `harness/PORTS.md` itself is not digest-pinned — it is
this study's own change list, and the destination digests it records rest on
review. The source side does not rest on it at all.
"""
from __future__ import annotations
import hashlib
import json
import os
import platform
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
TEN = os.path.normpath(os.path.join(STUDY, "..", "010-blinded-oracle"))
DEFAULT_PORTS = os.path.join(HERE, "PORTS.md")
DEFAULT_PINS = os.path.join(HERE, "PINS.json")

# The six files PORTS.md must account for. A row deleted from the table is a
# check silently dropped, so the destination set is required to be exactly this.
REQUIRED_PORTS = frozenset((
    "harness/policy_mirror.py",
    "harness/records_compile.py",
    "harness/transcript_check.py",
    "transcription/authoring_call.sh",
    "transcription/PROMPT.txt",
    "FAMILY.json",
))

# §2.1's first table: the three files ported BYTE-IDENTICALLY. For these the
# destination does not rest on PORTS.md at all — its digest must equal the one
# Study 010's lock records for the source, so "byte-identical" is a checked
# relation between this study's file and 010's lock rather than a claim in a
# prose column. Without this, editing a byte-identical port here and editing
# its destination cell to match would pass every other check in this module.
BYTE_IDENTICAL = frozenset((
    "harness/policy_mirror.py",
    "transcription/PROMPT.txt",
    "FAMILY.json",
))

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
    """[(source, source sha256, destination, destination sha256)] from
    PORTS.md's table — this study's change list, parsed rather than duplicated
    so the reviewed file and the checked one are the same file. What each
    column is checked AGAINST is verify()'s business, and it is not this
    table: the source column answers to Study 010's lock."""
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


def verify(study: str = STUDY, ten: str = TEN, ports_path: str = None,
           pins_path: str = None) -> dict:
    """The whole table, or IntegrityError. Returns what it checked, so a
    caller can record it."""
    ports_path = ports_path or os.path.join(study, "harness", "PORTS.md")
    pins_path = pins_path or os.path.join(study, "harness", "PINS.json")
    rows = parse_ports(ports_path)
    destinations = set(row[2] for row in rows)
    if destinations != set(REQUIRED_PORTS):
        missing = sorted(set(REQUIRED_PORTS) - destinations)
        extra = sorted(destinations - set(REQUIRED_PORTS))
        raise IntegrityError(
            "%s's table does not name exactly the six ported files (missing %s, "
            "unexpected %s)" % (ports_path, missing or "none", extra or "none"))
    if not os.path.isfile(pins_path):
        raise IntegrityError("no registry at %s" % pins_path)
    pins = load_json(pins_path)

    # 010's lock FIRST: it is the authority every source digest below is
    # checked against, so its own bytes are established before it is read.
    lock_path = os.path.join(ten, "PROTOCOL-LOCK.json")
    if not os.path.isfile(lock_path):
        raise IntegrityError("Study 010's PROTOCOL-LOCK.json is missing")
    lock_digest = digest(lock_path)
    if lock_digest != bare(pins.get("pinnedFrom", {}).get("fileSha256")):
        raise IntegrityError(
            "Study 010's PROTOCOL-LOCK.json is sha256:%s, not the pinned %s"
            % (lock_digest, pins.get("pinnedFrom", {}).get("fileSha256")))
    locked = load_json(lock_path).get("lockedInputs")
    if not isinstance(locked, dict) or not locked:
        raise IntegrityError("Study 010's PROTOCOL-LOCK.json carries no lockedInputs "
                             "map: the ports have no authority to be checked against")

    checked = []
    for source, source_sha, destination, destination_sha in rows:
        # The SOURCE side answers to 010's lock, not to this study's table.
        # Editing a port here and editing its PORTS.md row to match is the
        # attack this ordering exists to refuse.
        if source not in locked:
            raise IntegrityError(
                "harness/PORTS.md names %s as a port, and Study 010's "
                "PROTOCOL-LOCK.json locks no such input: a port with no locked "
                "source has no provenance" % source)
        lock_sha = bare(locked[source])
        if source_sha != lock_sha:
            raise IntegrityError(
                "harness/PORTS.md records sha256:%s for Study 010's %s and that "
                "study's PROTOCOL-LOCK.json locks sha256:%s: the ports table "
                "disagrees with the lock it claims to copy from"
                % (source_sha, source, lock_sha))
        origin = os.path.join(ten, source)
        if not os.path.isfile(origin):
            raise IntegrityError("Study 010's %s is missing: the ported table's "
                                 "authority cannot be checked" % source)
        actual_source = digest(origin)
        if actual_source != lock_sha:
            raise IntegrityError(
                "Study 010's %s is sha256:%s, not the sha256:%s its own "
                "PROTOCOL-LOCK.json locks" % (source, actual_source, lock_sha))
        # The DESTINATION side answers to PORTS.md: it is this study's change
        # list, and an adapted port has nothing older to be checked against.
        here = os.path.join(study, destination)
        if not os.path.isfile(here):
            raise IntegrityError("the ported file %s is missing from %s"
                                 % (destination, study))
        actual = digest(here)
        if actual != destination_sha:
            raise IntegrityError(
                "%s is sha256:%s, not the sha256:%s harness/PORTS.md records: the "
                "ported bytes are not the bytes this study registered"
                % (destination, actual, destination_sha))
        # …except for the three byte-identical ports, whose destination answers
        # to the lock as well. Otherwise "byte-identical" would rest on a prose
        # column: edit the file here, edit its destination cell to match, and
        # every other check in this module still passes.
        if destination in BYTE_IDENTICAL and actual != lock_sha:
            raise IntegrityError(
                "%s is ported BYTE-IDENTICALLY and is sha256:%s, not the sha256:%s "
                "Study 010's PROTOCOL-LOCK.json locks for %s: a byte-identical port "
                "that differs from 010's locked bytes is a reinterpretation of the "
                "reference semantics" % (destination, actual, lock_sha, source))
        checked.append(destination)

    for member in ("prompt", "probePrompt", "family"):
        entry = pins.get(member)
        if not isinstance(entry, dict):
            raise IntegrityError("harness/PINS.json pins no %s" % member)
        path = os.path.join(study, entry["path"])
        if not os.path.isfile(path):
            raise IntegrityError("%s is missing" % entry["path"])
        actual = digest(path)
        if actual != bare(entry.get("sha256")):
            raise IntegrityError("%s is sha256:%s, not the pinned %s"
                                 % (entry["path"], actual, entry.get("sha256")))
        checked.append(entry["path"])

    interpreter = verify_interpreter(pins)

    return {"portedFiles": sorted(set(checked)),
            "study010LockSha256": "sha256:" + lock_digest,
            "lockedSources": sorted(row[0] for row in rows),
            "interpreter": interpreter,
            "portsRecord": os.path.relpath(ports_path, study)}


def verify_interpreter(pins: dict) -> str:
    """The registry's `python` member, read by code rather than only recorded.

    §2.6 registers what is enforced: the implementation exactly, and the
    version SERIES (major.minor) exactly. The patch level is recorded and not
    required — CI pins `3.12` and resolves whatever patch release is current,
    and this study's arithmetic is exact rationals and integer combinatorics
    that no patch release moves. What the series does buy is real: Study 010
    ran on CPython 3.8 and the ported compiler's behaviour is stated against
    3.12's, so a run under another series is not the registered harness.
    """
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
            "this harness is running on %s %s and harness/PINS.json registers the "
            "%r series: the registered interpreter is not the one in use"
            % (implementation, platform.python_version(), entry.get("series")))
    return "%s %s" % (implementation, platform.python_version())


def main(argv: list) -> int:
    try:
        summary = verify()
    except IntegrityError as error:
        print("refused: %s" % error)
        return 1
    print("ported bytes verified: %d files against %s, %d sources against Study "
          "010's lock %s, on %s"
          % (len(summary["portedFiles"]), summary["portsRecord"],
             len(summary["lockedSources"]), summary["study010LockSha256"],
             summary["interpreter"]))
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv))
