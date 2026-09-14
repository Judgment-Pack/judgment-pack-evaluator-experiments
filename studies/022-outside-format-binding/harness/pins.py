"""What the study pins, and how each pin is checked before anything is adjudicated.

- the gateway verifier: a commit of the gateway repository and a reproducible build recipe
  (`CGO_ENABLED=0 go build -trimpath -buildvcs=false` in `go/` under the pinned Go toolchain),
  pinned by the binary's SHA-256; the runner and the scorer refuse another binary;
- the corpus public key the gateway layer verifies under, by digest;
- the in-toto reference implementation: `securesystemslib` and `in-toto-attestation` by
  version and by a digest over the installed package files, read through importlib;
- the adapter key: the study-minted Ed25519 key's id, recomputed from its seed, and the fixture's
  trusted-key file held to that id and that key material;
- the executing code: every loaded module of the four pinned distributions one of their own files
  under a source or extension loader, no bytecode read from beside the sources (an empty cache
  prefix) nor written, the study modules from the study tree, the interpreter implementation;
- the freeze pins: the preregistration, the matrix, the holdout matrix, the adapter
  specification and the manifest by SHA-256.
"""
import hashlib
import json
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
PINS_PATH = STUDY / "harness" / "PINS.json"
FREEZE_FILES = {"preregistration": "PREREGISTRATION.md", "matrix": "harness/MATRIX.json", "matrixHoldout": "harness/MATRIX-HOLDOUT.json",
                "adapterSpec": "adapter/SPEC.md", "studyManifest": "harness/STUDY-MANIFEST.sha256"}


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load():
    return json.loads(PINS_PATH.read_text())


def raw_sha256():
    return hashlib.sha256(PINS_PATH.read_bytes()).hexdigest()


def package_digest(name):
    """A digest over an installed distribution's files, in RECORD order, with each file's bytes."""
    from importlib import metadata
    dist = metadata.distribution(name)
    h = hashlib.sha256()
    for f in sorted(dist.files or [], key=lambda p: str(p)):
        p = dist.locate_file(f)
        if Path(p).is_file() and not str(f).endswith((".pyc", "RECORD")):
            h.update(str(f).encode() + b"\0" + Path(p).read_bytes() + b"\0")
    return dist.version, h.hexdigest()


def adapter_keyid():
    sys.path.insert(0, str(STUDY / "adapter"))
    import bind
    return bind.adapter_signer().public_key.keyid


def import_origin_problems(name, module_name):
    """The module the harness imports must come from the pinned distribution's own files, not a shadow."""
    import importlib
    from importlib import metadata
    try:
        dist = metadata.distribution(name)
        module = importlib.import_module(module_name)
    except Exception as e:  # noqa: BLE001
        return ["%s cannot be imported (%s)" % (module_name, type(e).__name__)]
    origin = Path(getattr(module, "__file__", "") or "").resolve()
    owned = {Path(dist.locate_file(f)).resolve() for f in (dist.files or [])}
    if origin not in owned:
        return ["%s is imported from %s, which is not a file of the pinned %s distribution" % (module_name, origin, name)]
    return []


TRUSTED_KEY_FILE = STUDY / "fixtures" / "baseline" / "attestations" / "adapter.pubkey.json"


def trusted_pubkey_problems(pins, path=None):
    """The trusted key file is the pinned adapter key, by key id and by key material (recomputed from the seed)."""
    sys.path.insert(0, str(STUDY / "adapter"))
    import bind
    path = Path(path) if path else TRUSTED_KEY_FILE
    public = json.loads(path.read_text())
    signer = bind.adapter_signer()
    out = []
    if public.get("keyid") != pins["adapter"]["keyid"]:
        out.append("%s does not carry the pinned adapter key id" % path)
    if public.get("keyval", {}).get("public") != signer.public_key.keyval.get("public"):
        out.append("%s does not carry the pinned adapter key material" % path)
    return out


PACKAGE_MODULES = (("securesystemslib", "securesystemslib"), ("in-toto-attestation", "in_toto_attestation"), ("cryptography", "cryptography"), ("protobuf", "google.protobuf"))
STUDY_MODULES = ("bind", "verify_attestation", "verify_binding", "storewalk", "cells", "pins", "run_layers", "score", "run_attempt", "make_manifest", "trees")


def module_problems(modname, mod, owned, location, prefix, label):
    """One loaded module: from the pinned files, by a source or extension loader, with no bytecode read outside the empty cache prefix."""
    # cryptography wraps a deprecated module in a proxy module object that keeps the real module under _module; inspect the real one
    inner = mod.__dict__.get("_module") if hasattr(mod, "__dict__") else None
    if isinstance(inner, type(sys)) and inner is not mod:
        return module_problems(modname, inner, owned, location, prefix, label)
    spec = getattr(mod, "__spec__", None)
    loader = spec.loader if spec is not None and spec.loader is not None else getattr(mod, "__loader__", None)
    origin = spec.origin if spec is not None and spec.origin else getattr(mod, "__file__", None)
    kind = type(loader).__name__ if loader is not None else None
    cached = getattr(mod, "__cached__", None)
    search = list(getattr(spec, "submodule_search_locations", None) or []) if spec is not None else []
    if origin is None and search:  # a namespace package: a directory with no __init__, allowed only inside the pinned location
        if any(not str(Path(loc).resolve()).startswith(str(location)) for loc in search):
            return ["%s is a namespace package with a search location outside %s" % (modname, label)]
        return []
    if origin in (None, "built-in", "frozen"):
        return ["%s has no file origin" % modname]
    o = Path(origin).resolve()
    if owned is not None and o not in owned:
        return ["%s is loaded from %s, which is not a file of %s" % (modname, o, label)]
    if owned is None and not any(str(o).startswith(str((location / d).resolve()) + "/") for d in ("adapter", "harness")):
        return ["%s is loaded from %s, outside %s" % (modname, o, label)]
    if kind not in ("SourceFileLoader", "ExtensionFileLoader"):
        return ["%s was loaded by %s, not from source or from a pinned extension" % (modname, kind)]
    if cached and (not prefix or not str(cached).startswith(str(prefix))):
        return ["%s's bytecode cache %s is not under the empty cache prefix" % (modname, cached)]
    return []


def execution_problems(pins):
    """The code that is running is the pinned code: bytecode is neither read from beside the sources nor written
    (sys.pycache_prefix set to an empty directory, sys.dont_write_bytecode), every loaded module of the four pinned
    distributions is one of their own files under a source or extension loader, every study module is from the study
    tree, and the interpreter is the pinned implementation."""
    import platform
    from importlib import metadata
    out = []
    if not sys.dont_write_bytecode:
        out.append("bytecode writing is not disabled (sys.dont_write_bytecode is false)")
    prefix = sys.pycache_prefix
    if not prefix:
        out.append("no bytecode cache prefix is set (sys.pycache_prefix): cached code beside the sources could run")
    else:
        held = [p for p in Path(prefix).rglob("*") if p.is_file()]
        if held:
            out.append("the bytecode cache prefix %s holds %d file(s); it must be empty" % (prefix, len(held)))
    if platform.python_implementation() != pins["harnessPython"]["implementation"]:
        out.append("the interpreter is %s, not the pinned %s" % (platform.python_implementation(), pins["harnessPython"]["implementation"]))
    for name, top in PACKAGE_MODULES:
        try:
            dist = metadata.distribution(name)
        except Exception as e:  # noqa: BLE001
            out.append("%s is not installed (%s)" % (name, type(e).__name__))
            continue
        location = str(Path(dist.locate_file("")).resolve())
        owned = {Path(dist.locate_file(f)).resolve() for f in (dist.files or [])}
        for modname, mod in list(sys.modules.items()):
            if mod is not None and (modname == top or modname.startswith(top + ".")):
                out += module_problems(modname, mod, owned, location, prefix, "the pinned %s distribution" % name)
    for modname in STUDY_MODULES:
        mod = sys.modules.get(modname)
        if mod is not None:
            out += module_problems(modname, mod, None, STUDY, prefix, "the study tree")
    return out


def problems(pins, gateway_binary, require_all=False):
    out = []
    if gateway_binary is None or not Path(gateway_binary).is_file():
        out.append("the gateway verifier binary is not given or not a file")
    else:
        digest = sha256_file(gateway_binary)
        if pins["gateway"]["binarySha256"] and pins["gateway"]["binarySha256"] != digest:
            out.append("the gateway binary's digest %s is not the pinned %s" % (digest, pins["gateway"]["binarySha256"]))
        if require_all and not pins["gateway"]["binarySha256"]:
            out.append("the gateway binary is not pinned")
    if sha256_file(STUDY / "fixtures" / "baseline" / "gateway.pubkey") != pins["gateway"]["publicKeySha256"]:
        out.append("the corpus public key is not the pinned one")
    for name, pin in pins["intoto"]["packages"].items():
        try:
            version, digest = package_digest(name)
        except Exception as e:  # noqa: BLE001
            out.append("%s is not installed (%s)" % (name, type(e).__name__))
            continue
        if version != pin["version"]:
            out.append("%s is %s, not the pinned %s" % (name, version, pin["version"]))
        if pin["installedDigest"] and pin["installedDigest"] != digest:
            out.append("%s's installed files do not match the pinned digest" % name)
        if require_all and not pin["installedDigest"]:
            out.append("%s's installed digest is not pinned" % name)
    if adapter_keyid() != pins["adapter"]["keyid"]:
        out.append("the adapter key is not the pinned one")
    out += trusted_pubkey_problems(pins)
    for name, module_name in (("securesystemslib", "securesystemslib"), ("in-toto-attestation", "in_toto_attestation"), ("cryptography", "cryptography"), ("protobuf", "google.protobuf")):
        out += import_origin_problems(name, module_name)
    if pins["harnessPython"].get("version") and pins["harnessPython"]["version"] != sys.version.split()[0]:
        out.append("the interpreter is %s, not the pinned %s" % (sys.version.split()[0], pins["harnessPython"]["version"]))
    if require_all and not pins["harnessPython"].get("version"):
        out.append("the interpreter version is not pinned")
    out += execution_problems(pins)
    for key, relative in FREEZE_FILES.items():
        expected = pins["freeze"].get(key)
        if expected and expected != sha256_file(STUDY / relative):
            out.append("%s does not match its freeze pin" % relative)
        if require_all and not expected:
            out.append("%s is not pinned" % relative)
    sys.path.insert(0, str(STUDY / "harness"))
    import make_manifest
    if (STUDY / "harness" / "STUDY-MANIFEST.sha256").read_text() != make_manifest.render():
        out.append("harness/STUDY-MANIFEST.sha256 does not match the tree")
    return out
