"""Digest-enforced access to the frozen Study 014 sources this study extends.

Decision D-1: Study 014's adapter and build machinery are consumed exactly the
way 014 consumes OpenWorkProof — as a pinned upstream, unmodified, with every
imported file's digest enforced against this study's `harness/PINS.json` before
anything is imported. 014 is frozen (its own STUDY-MANIFEST pins these bytes);
this study re-pins them here so a drift in either place refuses the run.

`load()` returns a namespace with 014's `verify`, `commitment` and (on the
build path) `build_fixtures`/`owpflow` modules. Name-based imports resolve
`verify`, `commitment` and `owpflow` — names this study deliberately does not
reuse — while 014's `build_fixtures` and `score` (names this study *does* use)
are only ever loaded here, by explicit file location, under aliased module
names. After loading, sys.path is re-ordered so this study's own modules stay
first; a harness test asserts the post-load resolution of every shared name.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
STUDY_014 = (STUDY.parent / "014-openworkproof-binding").resolve()
PINS_PATH = STUDY / "harness" / "PINS.json"


class Upstream014Error(RuntimeError):
    """The frozen Study 014 sources do not match their pins."""


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pinned_files():
    pins = json.loads(PINS_PATH.read_text(encoding="utf-8"))
    return pins["study014"]["files"]


def problems():
    """Every pinned-file mismatch, or [] when the frozen sources match."""
    out = []
    for relative, digest in sorted(pinned_files().items()):
        path = STUDY_014 / relative
        if not path.is_file():
            out.append("pinned Study 014 file is absent: " + relative)
        elif sha256_file(path) != digest:
            out.append("pinned Study 014 file does not match its digest: " + relative)
    return out


def _load_by_path(alias, path):
    spec = importlib.util.spec_from_file_location(alias, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


class _Namespace:
    pass


_LOADED = None


def load(build=False):
    """The verified 014 namespace; `build=True` adds the flow machinery."""
    global _LOADED
    mismatches = problems()
    if mismatches:
        raise Upstream014Error("; ".join(mismatches))
    if _LOADED is None:
        for entry in (str(STUDY_014 / "adapter"), str(STUDY_014 / "harness")):
            if entry not in sys.path:
                sys.path.append(entry)
        namespace = _Namespace()
        import verify as verify014  # noqa: E402  (unique name, 014's adapter)
        import commitment as commitment014  # noqa: E402
        namespace.verify = verify014
        namespace.commitment = commitment014
        namespace.build_fixtures = None
        namespace.owpflow = None
        _LOADED = namespace
    if build and _LOADED.build_fixtures is None:
        # 014's build_fixtures prepends its own directories to sys.path at
        # import time; loading it under an alias keeps this study's
        # `build_fixtures`/`score` names resolvable, and the re-ordering below
        # keeps them first afterwards.
        _LOADED.build_fixtures = _load_by_path(
            "study014_build_fixtures", STUDY_014 / "harness" / "build_fixtures.py"
        )
        import owpflow  # noqa: E402
        _LOADED.owpflow = owpflow
        own = str(STUDY / "harness")
        while own in sys.path:
            sys.path.remove(own)
        sys.path.insert(0, own)
    return _LOADED
