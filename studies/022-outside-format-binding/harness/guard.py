"""Trusted import resolution, established before any other study or package import (PREREGISTRATION.md section 2).

This module uses only `os` and `sys`, which the interpreter loads at startup from its own library, so
nothing it refuses has run when it refuses it. Every entry script sets the bytecode policy with `os` and
`sys` alone, then imports this module (compiled from its source, as every module after that point is)
and calls `establish(study)` before importing anything else:

- the import path (`sys.path`) holds only the study's own roots (the script's directory, the study root
  as the working directory), the interpreter's own library and the virtual environment; any other entry
  (a `PYTHONPATH` injection, a foreign directory) is refused;
- the study roots (`adapter/`, `harness/`, `harness/tests/`) hold no importable file that is not a `.py`
  module (a `.pyc` beside the sources, an extension, an archive), no directory an import could resolve to
  other than `harness/tests` and `__pycache__` (never consulted under the cache prefix), no symbolic link,
  and no `.py` whose name is a module of the interpreter's library or a pinned package's top level;
- the virtual environment's import roots hold nothing an installed distribution does not record: no
  unrecorded module or package directory (the import system prefers a package directory to a
  same-named module), no path hook, no symbolic link; and no two metadata directories claim one
  distribution name, so the distribution whose files are hashed is the one whose record grants
  ownership;
- no site customization module was imported at start-up;
- the bytecode-cache prefix is set and holds no file, and bytecode writing is disabled.
"""
import os
import sys

IMPORTABLE_SUFFIXES = (".pyc", ".pyo", ".so", ".pyd", ".dll", ".dylib", ".pth", ".egg", ".zip", ".whl")
PINNED_TOP_LEVEL = ("securesystemslib", "in_toto_attestation", "cryptography", "google")
ROOTS = ("adapter", "harness", os.path.join("harness", "tests"))


def _real(p):
    return os.path.realpath(p)


def _under(path, parent):
    path, parent = _real(path), _real(parent)
    return path == parent or path.startswith(parent + os.sep)


def path_problems(study):
    """Every sys.path entry is a study root, the interpreter's library, or the virtual environment."""
    out = []
    allowed_roots = [_real(os.path.join(study, r)) for r in ROOTS] + [_real(study)]
    for entry in sys.path:
        e = _real(entry) if entry else _real(os.getcwd())
        if e in allowed_roots or _under(e, sys.base_prefix) or _under(e, sys.prefix):
            continue
        out.append("sys.path entry %r is not a study root, the interpreter's library or the virtual environment" % entry)
    if os.environ.get("PYTHONPATH"):
        out.append("PYTHONPATH is set (%r); the study's processes run without it" % os.environ["PYTHONPATH"])
    return out


def shadow_problems(study):
    """Nothing importable under the study roots but registered .py modules."""
    out = []
    stdlib = os.path.dirname(os.__file__)
    for rel in ROOTS:
        root = os.path.join(study, rel)
        for name in sorted(os.listdir(root)):
            p = os.path.join(root, name)
            if os.path.islink(p):
                out.append("%s/%s is a symbolic link" % (rel, name))
                continue
            if os.path.isdir(p):
                if name == "__pycache__" or (rel == "harness" and name == "tests"):
                    continue
                out.append("%s/%s is a directory an import could resolve to" % (rel, name))
                continue
            lower = name.lower()
            if lower.endswith(IMPORTABLE_SUFFIXES) or ".so." in lower:
                out.append("%s/%s is importable and is not a .py module" % (rel, name))
                continue
            if lower.endswith(".py"):
                stem = name[:-3]
                if stem in sys.builtin_module_names or stem in PINNED_TOP_LEVEL or os.path.exists(os.path.join(stdlib, stem + ".py")) \
                        or os.path.isdir(os.path.join(stdlib, stem)):
                    out.append("%s/%s shadows a module of the interpreter's library or a pinned package" % (rel, name))
    return out


def _record_paths(record_file):
    """The relative paths a distribution's RECORD lists (a quoted first field may hold a comma)."""
    out = []
    with open(record_file, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            if line.startswith('"'):
                end = line.find('"', 1)
                while end != -1 and end + 1 < len(line) and line[end + 1] == '"':
                    end = line.find('"', end + 2)
                rel = line[1:end].replace('""', '"') if end != -1 else line.split(",")[0]
            else:
                rel = line.split(",")[0]
            out.append(rel)
    return out


def _declared_name(metadata_file):
    """The normalized distribution name a METADATA file declares (PEP 503 normalization), or None."""
    try:
        with open(metadata_file, encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    break  # the headers end at the first blank line
                if line.lower().startswith("name:"):
                    raw = line.split(":", 1)[1].strip().lower()
                    out = ""
                    for ch in raw:
                        out += "-" if ch in "-_." and not out.endswith("-") else ch
                    return out
    except OSError:
        return None
    return None


def environment_problems():
    """Every entry under the virtual environment's import roots is a file an installed distribution records (its RECORD)
    or a directory such files populate -- nothing else: no unrecorded module, no unrecorded package directory (which
    the import system would prefer to a same-named module), no path hook, no symbolic link. `__pycache__` directories
    are skipped: under the empty cache prefix they are never consulted."""
    out = []
    roots = [e for e in sys.path if e and _under(e, sys.prefix) and os.path.isdir(e)]
    if not roots:
        out.append("no import root of the virtual environment is on sys.path")
    for root in roots:
        root = _real(root)
        owned_files, owned_dirs = set(), set()
        claimed = {}
        for name in sorted(os.listdir(root)):
            record = os.path.join(root, name, "RECORD")
            if name.endswith(".dist-info") and os.path.isfile(record):
                # one metadata directory per distribution name: a second directory claiming a name already claimed is refused,
                # so the distribution whose files are hashed and the distribution whose RECORD grants ownership are the same
                declared = _declared_name(os.path.join(root, name, "METADATA"))
                if declared is None:
                    out.append("%s declares no distribution name" % os.path.join(root, name))
                    continue  # its record grants nothing
                if declared in claimed:
                    out.append("%s claims the distribution name %r that %s already claims" % (os.path.join(root, name), declared, claimed[declared]))
                    continue  # its record grants nothing
                claimed[declared] = os.path.join(root, name)
                for rel in _record_paths(record):
                    full = os.path.normpath(os.path.join(root, rel))
                    if not _under(full, root):
                        continue  # a script outside the import root (bin/): not importable from here
                    owned_files.add(full)
                    parent = os.path.dirname(full)
                    while _under(parent, root) and parent != root:
                        owned_dirs.add(parent)
                        parent = os.path.dirname(parent)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
            for d in dirnames:
                full = os.path.join(dirpath, d)
                if os.path.islink(full):
                    out.append("%s is a symbolic link" % full)
                elif full not in owned_dirs:
                    out.append("%s is a directory no installed distribution records a file under" % full)
            for f in sorted(filenames):
                full = os.path.join(dirpath, f)
                if os.path.islink(full):
                    out.append("%s is a symbolic link" % full)
                elif full not in owned_files:
                    out.append("%s is not a file any installed distribution records" % full)
    return out


def site_problems():
    """Site initialization ran before this guard could: a customization module, if one was imported, has already run."""
    return ["%s was imported at interpreter start-up" % name for name in ("sitecustomize", "usercustomize") if name in sys.modules]


def cache_problems():
    out = []
    if not sys.dont_write_bytecode:
        out.append("bytecode writing is not disabled")
    prefix = sys.pycache_prefix
    if not prefix:
        out.append("no bytecode-cache prefix is set")
    elif not os.path.isdir(prefix):
        out.append("the bytecode-cache prefix %s is not a directory" % prefix)
    else:
        for dirpath, _, files in os.walk(prefix):
            if files:
                out.append("the bytecode-cache prefix %s holds files (%s); it must be empty" % (prefix, os.path.join(dirpath, files[0])))
                break
    return out


def establish(study):
    """Refuse to run unless trusted import resolution holds; returns None."""
    problems = cache_problems() + site_problems() + path_problems(study) + shadow_problems(study) + environment_problems()
    if problems:
        raise SystemExit("refusing to start: trusted import resolution is not established:\n  " + "\n  ".join(problems))


def fresh_cache_prefix():
    """For an entry script, before importing this module: an empty directory of this process's own, made with os alone."""
    base = os.environ.get("TMPDIR") or "/tmp"
    for attempt in range(10000):
        d = os.path.join(base, "study022-pycache-%d-%d" % (os.getpid(), attempt))
        try:
            os.mkdir(d, 0o700)
            return d
        except FileExistsError:
            continue
    raise SystemExit("could not make an empty bytecode-cache prefix under %s" % base)
