"""One typed representation of a file tree, for reconstruction comparison and observation digests alike.

An entry is a directory ("d") or a regular file (its SHA-256); anything else -- a symbolic link
(the root included), a device, a pipe, a socket -- is refused before any byte is read, so a tree
that verifies is a tree of plain directories and plain files and nothing besides.
"""
import hashlib
import json
import os
import stat
from pathlib import Path


def typed_tree(root):
    """Every entry under a tree by relative POSIX path: "d" for a directory, else the file's SHA-256 hex."""
    root = Path(root)
    st = os.lstat(root)  # a missing root raises
    if not stat.S_ISDIR(st.st_mode):
        raise RuntimeError("the tree root %s is not a plain directory" % root)
    out = {}
    stack = [root]
    while stack:
        d = stack.pop()
        for entry in sorted(os.listdir(d)):
            p = d / entry
            rel = p.relative_to(root).as_posix()
            mode = os.lstat(p).st_mode
            if stat.S_ISDIR(mode):
                out[rel] = "d"
                stack.append(p)
            elif stat.S_ISREG(mode):
                out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
            else:
                raise RuntimeError("entry %s under %s is neither a plain directory nor a plain file" % (rel, root))
    return out


def same_tree(a, b):
    """Byte-for-byte equality of two trees: the same paths, the same kinds, the same file bytes."""
    return typed_tree(a) == typed_tree(b)


def tree_digest(root):
    """A digest over the typed tree: directories and files alike, so an added empty directory changes it."""
    return hashlib.sha256(json.dumps(typed_tree(root), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
