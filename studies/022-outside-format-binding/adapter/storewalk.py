"""How both adapter layers walk a store and look for an attestation.

Receipts are enumerated as the gateway enumerates them (its SPEC.md section 3a): per session
directory, every non-directory entry named `*.json`, by name. Presence is strict: an
attestation is absent when there is no directory entry at its path; a path that is present but
not a plain file -- a directory, a symbolic link, a device -- is not absence and not an outcome,
it is an I/O failure that propagates (the validity channel).
"""
import os
import stat
from pathlib import Path


def presence(path):
    """'absent' when there is no directory entry; 'file' when a plain file; anything else present raises."""
    try:
        mode = os.lstat(path).st_mode
    except FileNotFoundError:
        return "absent"
    if not stat.S_ISREG(mode):
        raise OSError("%s is present but is not a plain file" % path)
    return "file"


def stored_receipts(store):
    """(session, stem, path) for every receipt file the store holds, in the gateway's enumeration order."""
    receipts = Path(store) / "receipts"
    out = []
    for session in sorted(os.listdir(receipts)):
        sp = receipts / session
        mode = os.lstat(sp).st_mode
        if stat.S_ISLNK(mode):
            raise OSError("%s is a symbolic link" % sp)
        if not stat.S_ISDIR(mode):
            continue
        for entry in sorted(os.listdir(sp)):
            if not entry.endswith(".json"):
                continue
            fp = sp / entry
            mode = os.lstat(fp).st_mode
            if stat.S_ISDIR(mode):
                continue
            if not stat.S_ISREG(mode):
                raise OSError("%s is present but is not a plain file" % fp)
            out.append((session, entry[:-len(".json")], fp))
    return out
