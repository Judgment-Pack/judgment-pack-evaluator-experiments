"""Digest-enforced access to the frozen Study 014 sources this study extends.

Decision D-1: Study 014's adapter and build machinery are consumed exactly the
way 014 consumes OpenWorkProof — as a pinned upstream, unmodified, with every
imported file's digest enforced against this study's `harness/PINS.json`.

Enforcement is on the LOADED MODULE, and loading is by authenticated absolute
path only (round-1 R1-1; round-2 confirmation residual):

- nothing here ever appends a 014 directory to `sys.path`, and no bare `import`
  of a 014 module name occurs — each module is loaded with
  `importlib.util.spec_from_file_location` from the exact pinned path, whose
  bytes are digest-checked immediately before execution, so there is no window
  in which an earlier `sys.path` shadow can execute;
- a pre-existing `sys.modules` entry for any shared name (`verify`,
  `commitment`, `owpflow`) that this loader did not itself create is refused —
  something else already imported code under a name this study is about to
  trust. The names are pre-seeded (after that refusal) so the frozen modules'
  own bare imports of each other resolve to the verified instances;
- on every `load()` call — cached loads included — each owned module's
  `sys.modules` identity, resolved `__file__`, and file bytes are re-verified
  against the pins, so a post-load substitution is caught at the next gate.

014's `build_fixtures` (a name this study also uses) is loaded under the alias
`study014_build_fixtures`. A harness test asserts the post-load resolution of
every shared name.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
STUDY_014 = (STUDY.parent / "014-openworkproof-binding").resolve()
PINS_PATH = STUDY / "harness" / "PINS.json"

# load order matters: each module's bare imports must already be seeded.
MODULE_PATHS = (
    ("commitment", "adapter/commitment.py"),
    ("verify", "adapter/verify.py"),
    ("owpflow", "harness/owpflow.py"),
    ("study014_build_fixtures", "harness/build_fixtures.py"),
)
VERIFY_ONLY = ("commitment", "verify")


class Upstream014Error(RuntimeError):
    """The frozen Study 014 sources do not match their pins."""


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pinned_files():
    pins = json.loads(PINS_PATH.read_text(encoding="utf-8"))
    return pins["study014"]["files"]


def problems():
    """Every pinned-file mismatch on disk, or [] when the sources match."""
    out = []
    for relative, digest in sorted(pinned_files().items()):
        path = STUDY_014 / relative
        if not path.is_file():
            out.append("pinned Study 014 file is absent: " + relative)
        elif sha256_file(path) != digest:
            out.append("pinned Study 014 file does not match its digest: " + relative)
    return out


def _verified_path(relative):
    pins = pinned_files()
    path = (STUDY_014 / relative).resolve()
    if relative not in pins:
        raise Upstream014Error("no digest pin for %s" % relative)
    if not path.is_file() or sha256_file(path) != pins[relative]:
        raise Upstream014Error(
            "pinned Study 014 file does not match its digest: %s" % relative
        )
    return path


def _load_by_path(name, relative):
    """Digest-check, then execute from the authenticated absolute path."""
    path = _verified_path(relative)
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


class _Namespace:
    pass


_LOADED = None
_OWNED_MODULES = {}


def _module_problems():
    """Per-load verification of every owned module: identity, origin, bytes."""
    pins = pinned_files()
    paths = dict(MODULE_PATHS)
    out = []
    for name, module in _OWNED_MODULES.items():
        if sys.modules.get(name) is not module:
            out.append(
                "module %r in sys.modules is no longer the verified instance" % name
            )
            continue
        relative = paths[name]
        expected = (STUDY_014 / relative).resolve()
        origin = getattr(module, "__file__", None)
        if origin is None or Path(origin).resolve() != expected:
            out.append(
                "module %r resolved to %r, not the pinned %s" % (name, origin, expected)
            )
        elif sha256_file(expected) != pins[relative]:
            out.append("module %r bytes do not match the pinned digest" % (name,))
    return out


def load(build=False):
    """The verified 014 namespace; `build=True` adds the flow machinery."""
    global _LOADED
    mismatches = problems()
    if mismatches:
        raise Upstream014Error("; ".join(mismatches))
    if _LOADED is None:
        for name, _ in MODULE_PATHS:
            if name in sys.modules and name not in _OWNED_MODULES:
                raise Upstream014Error(
                    "module name %r is already imported by something else; "
                    "refusing to trust it as the pinned Study 014 source" % name
                )
        namespace = _Namespace()
        for name, relative in MODULE_PATHS:
            if name in VERIFY_ONLY:
                _OWNED_MODULES[name] = _load_by_path(name, relative)
        namespace.commitment = _OWNED_MODULES["commitment"]
        namespace.verify = _OWNED_MODULES["verify"]
        namespace.owpflow = None
        namespace.build_fixtures = None
        _LOADED = namespace
    if build and _LOADED.build_fixtures is None:
        for name, relative in MODULE_PATHS:
            if name not in VERIFY_ONLY and name not in _OWNED_MODULES:
                _OWNED_MODULES[name] = _load_by_path(name, relative)
        _LOADED.owpflow = _OWNED_MODULES["owpflow"]
        _LOADED.build_fixtures = _OWNED_MODULES["study014_build_fixtures"]
        # 014's build_fixtures prepends its own directories at exec time; keep
        # this study's harness first so shared names keep resolving here.
        own = str(STUDY / "harness")
        while own in sys.path:
            sys.path.remove(own)
        sys.path.insert(0, own)
    module_mismatches = _module_problems()
    if module_mismatches:
        raise Upstream014Error("; ".join(module_mismatches))
    return _LOADED
