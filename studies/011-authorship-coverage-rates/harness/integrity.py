#!/usr/bin/env python3
"""C1 in code: the ported-byte digest table, verified before anything runs.

PREREGISTRATION.md §6 C1 registers that the ported bytes are Study 010's, and
§7 lists that table under what is mechanically enforced. This module is what
makes that true at run time rather than only in pytest: `batch.preflight()`
calls it before it creates a slot, and `score_rates.score()` calls it before it
reads one. A one-character drift in the byte-identical `policy_mirror.py` would
otherwise change a published rate and a §5 tier with nothing refusing.

What it checks, and nothing else (§7 claims exactly this list):

  1. `harness/PORTS.md`'s table parses, and names exactly the six ported files;
  2. every destination file in this study hashes to the digest PORTS.md
     records for it;
  3. every source file in `studies/010-blinded-oracle/` hashes to the Study 010
     digest PORTS.md records for it — so the table's two columns are checked
     against the files on both sides, not against each other;
  4. `studies/010-blinded-oracle/PROTOCOL-LOCK.json` hashes to the digest
     `harness/PINS.json` pins in `pinnedFrom.fileSha256` (010's lock does not
     digest itself, so without this pin the table's authority is a mutable
     file);
  5. `PROMPT.txt`, `PROBE-PROMPT.txt` and `FAMILY.json` hash to the digests
     `harness/PINS.json` pins for them.

What it does NOT check, stated here so §7 cannot claim it: nothing is compared
to a git HEAD blob, and `harness/PORTS.md` itself is not digest-pinned — it is
the authority the table is read from, and its own integrity rests on review and
on the fact that both of its digest columns are checked against real files.
"""
from __future__ import annotations
import hashlib
import json
import os
import re

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

# | `source` | `sha` | `destination` | `sha` | changed |
ROW = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|")


class IntegrityError(Exception):
    """A refusal that precedes every call and every count."""


def digest(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def bare(value) -> str:
    """A digest with or without the `sha256:` prefix, as a bare hex string."""
    if not isinstance(value, str):
        raise IntegrityError("a digest is missing where one is required: %r" % (value,))
    return value.split(":")[-1].strip()


def parse_ports(ports_path: str) -> list:
    """[(source, source sha256, destination, destination sha256)] from
    PORTS.md's table. The table is the registered provenance record; parsing
    it rather than duplicating it keeps one authority instead of two."""
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
    checked = []
    for source, source_sha, destination, destination_sha in rows:
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
        origin = os.path.join(ten, source)
        if not os.path.isfile(origin):
            raise IntegrityError("Study 010's %s is missing: the ported table's "
                                 "authority cannot be checked" % source)
        actual_source = digest(origin)
        if actual_source != source_sha:
            raise IntegrityError(
                "Study 010's %s is sha256:%s, not the sha256:%s harness/PORTS.md "
                "records" % (source, actual_source, source_sha))
        checked.append(destination)

    pins = json.loads(open(pins_path, "rb").read().decode("utf-8"))
    lock = os.path.join(ten, "PROTOCOL-LOCK.json")
    if not os.path.isfile(lock):
        raise IntegrityError("Study 010's PROTOCOL-LOCK.json is missing")
    lock_digest = digest(lock)
    if lock_digest != bare(pins.get("pinnedFrom", {}).get("fileSha256")):
        raise IntegrityError(
            "Study 010's PROTOCOL-LOCK.json is sha256:%s, not the pinned %s"
            % (lock_digest, pins.get("pinnedFrom", {}).get("fileSha256")))

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

    return {"portedFiles": sorted(set(checked)),
            "study010LockSha256": "sha256:" + lock_digest,
            "portsRecord": os.path.relpath(ports_path, study)}


def main(argv: list) -> int:
    try:
        summary = verify()
    except IntegrityError as error:
        print("refused: %s" % error)
        return 1
    print("ported bytes verified: %d files against %s, Study 010 lock %s"
          % (len(summary["portedFiles"]), summary["portsRecord"],
             summary["study010LockSha256"]))
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv))
