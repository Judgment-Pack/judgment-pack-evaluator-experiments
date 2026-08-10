"""Digest-enforced access to the frozen Study 014 sources this study extends.

Decision D-1: Study 014's adapter and build machinery are consumed exactly the
way 014 consumes OpenWorkProof — as a pinned upstream, unmodified, with every
imported file's digest enforced against this study's `harness/PINS.json`.

Enforcement is on the LOADED MODULE, not merely on the file (round-1 R1-1):

- a pre-existing `sys.modules` entry for any of the shared names (`verify`,
  `commitment`, `owpflow`) that this loader did not itself create is refused —
  something else already imported code under a name this study is about to
  trust;
- after import, each module's resolved `__file__` must be exactly the pinned
  path under the frozen 014 tree, and that file's bytes must match the pinned
  digest — a shadowing `sys.path` entry therefore refuses rather than
  substituting code;
- both checks re-run on every `load()` call, cached modules included, so a
  post-load substitution in `sys.modules` is caught at the next gate.

014's `build_fixtures` (a name this study also uses) is only ever loaded here,
by explicit file location, under an aliased module name; its own import-time
`sys.path` inserts are de-prioritized afterwards so this study's modules stay
first. A harness test asserts the post-load resolution of every shared name.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
STUDY_014 = (STUDY.parent / "014-openworkproof-binding").resolve()
PINS_PATH = STUDY / "harness" / "PINS.json"

# module name -> pinned repo-relative path inside the frozen 014 tree
MODULE_PATHS = {
    "verify": "adapter/verify.py",
    "commitment": "adapter/commitment.py",
    "owpflow": "harness/owpflow.py",
    "study014_build_fixtures": "harness/build_fixtures.py",
}


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


def _module_problems(loaded):
    """Loaded-module verification: origin path and bytes, per load (R1-1)."""
    pins = pinned_files()
    out = []
    for name, module in loaded.items():
        relative = MODULE_PATHS[name]
        expected = (STUDY_014 / relative).resolve()
        origin = getattr(module, "__file__", None)
        if origin is None or Path(origin).resolve() != expected:
            out.append(
                "module %r resolved to %r, not the pinned %s" % (name, origin, expected)
            )
            continue
        if relative not in pins:
            out.append("module %r has no digest pin for %s" % (name, relative))
        elif sha256_file(expected) != pins[relative]:
            out.append("module %r bytes do not match the pinned digest" % (name,))
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
_OWNED_MODULES = {}


def load(build=False):
    """The verified 014 namespace; `build=True` adds the flow machinery."""
    global _LOADED
    mismatches = problems()
    if mismatches:
        raise Upstream014Error("; ".join(mismatches))
    if _LOADED is None:
        for name in ("verify", "commitment", "owpflow"):
            if name in sys.modules and name not in _OWNED_MODULES:
                raise Upstream014Error(
                    "module name %r is already imported by something else; "
                    "refusing to trust it as the pinned Study 014 source" % name
                )
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
        _OWNED_MODULES.update({"verify": verify014, "commitment": commitment014})
        _LOADED = namespace
    if build and _LOADED.build_fixtures is None:
        _LOADED.build_fixtures = _load_by_path(
            "study014_build_fixtures", STUDY_014 / "harness" / "build_fixtures.py"
        )
        import owpflow  # noqa: E402
        _LOADED.owpflow = owpflow
        _OWNED_MODULES.update({
            "owpflow": owpflow,
            "study014_build_fixtures": _LOADED.build_fixtures,
        })
        own = str(STUDY / "harness")
        while own in sys.path:
            sys.path.remove(own)
        sys.path.insert(0, own)

    # Per-load verification, cached loads included: the module in sys.modules
    # must still be the one this loader created, resolved to the pinned path,
    # with pinned bytes.
    for name, module in _OWNED_MODULES.items():
        if sys.modules.get(name) is not module:
            raise Upstream014Error(
                "module %r in sys.modules is no longer the verified instance" % name
            )
    module_mismatches = _module_problems(_OWNED_MODULES)
    if module_mismatches:
        raise Upstream014Error("; ".join(module_mismatches))
    return _LOADED
