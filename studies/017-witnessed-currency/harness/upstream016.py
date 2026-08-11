"""Digest-enforced access to the frozen Study 016 registry modules.

The 016→014 posture applied to 016 itself: `registry/checkpoint.py` (build
path) and `registry/verify_currency.py` (Layer CURRENCY, unchanged) are
consumed as a pinned unmodified upstream. Loading is by authenticated
absolute path only — no sys.path additions, no bare imports; a pre-existing
`sys.modules` entry for either name is refused; and every `load()` call
re-verifies each owned module's identity, origin, and bytes.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
STUDY_016 = (STUDY.parent / "016-policy-currency-anchor").resolve()
PINS_PATH = STUDY / "harness" / "PINS.json"

MODULE_PATHS = (
    ("verify_currency", "registry/verify_currency.py"),
    ("checkpoint", "registry/checkpoint.py"),
)
VERIFY_ONLY = ("verify_currency",)


class Upstream016Error(RuntimeError):
    """The frozen Study 016 sources do not match their pins."""


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


_PINNED_FILES = None


def pinned_files():
    """The upstream digest mapping. Once `bind_pins` has supplied the mapping
    extracted from the attempt's STAMPED registry bytes, it is used for every
    later check: the loader never re-reads the live registry, so the trust
    inputs cannot differ from what the attempt record commits to (round-1
    R1-3)."""
    if _PINNED_FILES is not None:
        return _PINNED_FILES
    pins = json.loads(PINS_PATH.read_text(encoding="utf-8"))
    return pins["study016"]["files"]


def bind_pins(mapping):
    """Freeze the upstream digest mapping for this process."""
    global _PINNED_FILES
    frozen = dict(mapping)
    if _PINNED_FILES is not None and _PINNED_FILES != frozen:
        raise Upstream016Error("the upstream digest mapping is already bound differently")
    _PINNED_FILES = frozen
    return frozen


def problems():
    out = []
    for relative, digest in sorted(pinned_files().items()):
        path = STUDY_016 / relative
        if not path.is_file():
            out.append("pinned Study 016 file is absent: " + relative)
        elif sha256_file(path) != digest:
            out.append("pinned Study 016 file does not match its digest: " + relative)
    return out


def _load_by_path(name, relative):
    """Hash, compile and execute the EXACT source bytes read once.

    Ordinary import machinery may execute a `__pycache__` bytecode file whose
    bytes no pin covers, so a digest over the `.py` would not describe the code
    that ran (round-1 R1-1). Reading the source once, hashing that buffer, and
    executing `compile()` of it closes the gap for the pinned upstream; the
    scorer additionally refuses to adjudicate while any bytecode cache exists
    in either tree.
    """
    if name in sys.modules and name not in _OWNED_MODULES:
        raise Upstream016Error(
            "module name %r is already imported by something else; refusing "
            "to trust it as the pinned Study 016 source" % name
        )
    pins = pinned_files()
    path = (STUDY_016 / relative).resolve()
    if not path.is_file():
        raise Upstream016Error("pinned Study 016 file is absent: %s" % relative)
    source = path.read_bytes()
    if relative not in pins or hashlib.sha256(source).hexdigest() != pins[relative]:
        raise Upstream016Error(
            "pinned Study 016 file does not match its digest: %s" % relative
        )
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(path)
    sys.modules[name] = module
    try:
        exec(compile(source, str(path), "exec"), module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


class _Namespace:
    pass


_LOADED = None
_OWNED_MODULES = {}


def _module_problems():
    pins = pinned_files()
    paths = dict(MODULE_PATHS)
    out = []
    for name, module in _OWNED_MODULES.items():
        if sys.modules.get(name) is not module:
            out.append("module %r in sys.modules is no longer the verified instance" % name)
            continue
        relative = paths[name]
        expected = (STUDY_016 / relative).resolve()
        origin = getattr(module, "__file__", None)
        if origin is None or Path(origin).resolve() != expected:
            out.append("module %r resolved to %r, not the pinned %s" % (name, origin, expected))
        elif sha256_file(expected) != pins[relative]:
            out.append("module %r bytes do not match the pinned digest" % (name,))
    return out


def load(build=False):
    """The verified 016 namespace; `build=True` adds the registry writer."""
    global _LOADED
    mismatches = problems()
    if mismatches:
        raise Upstream016Error("; ".join(mismatches))
    if _LOADED is None:
        # Preflight EVERY reserved upstream name before executing any module
        # (round-1 R1-14): the loader's contract is refusal, not deferral.
        for name, _ in MODULE_PATHS:
            if name in sys.modules and name not in _OWNED_MODULES:
                raise Upstream016Error(
                    "module name %r is already imported by something else; refusing "
                    "to trust it as the pinned Study 016 source" % name
                )
        namespace = _Namespace()
        for name, relative in MODULE_PATHS:
            if name in VERIFY_ONLY:
                _OWNED_MODULES[name] = _load_by_path(name, relative)
        namespace.verify_currency = _OWNED_MODULES["verify_currency"]
        namespace.checkpoint = None
        _LOADED = namespace
    if build and _LOADED.checkpoint is None:
        for name, relative in MODULE_PATHS:
            if name not in VERIFY_ONLY and name not in _OWNED_MODULES:
                _OWNED_MODULES[name] = _load_by_path(name, relative)
        _LOADED.checkpoint = _OWNED_MODULES["checkpoint"]
    module_mismatches = _module_problems()
    if module_mismatches:
        raise Upstream016Error("; ".join(module_mismatches))
    return _LOADED
