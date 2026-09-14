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


def normalized(name):
    """PEP 503 normalization: lower case, every run of `-`, `_` and `.` collapsed to one hyphen."""
    out = ""
    for ch in name.lower():
        if ch in "-_.":
            if not out.endswith("-"):
                out += "-"
        else:
            out += ch
    return out


def inventory():
    """Every distribution the environment holds, one per normalized name -- the same inventory grants ownership of files
    and supplies the bytes that are hashed. Returns (distributions by normalized name, problems); a second metadata
    directory claiming a name already claimed is a problem, and neither of the two is used."""
    from importlib import metadata
    found, problems, duplicated = {}, [], set()
    for dist in metadata.distributions():
        name = normalized(dist.metadata["Name"] or "")
        if not name:
            problems.append("a metadata directory declares no distribution name (%s)" % dist._path)
            continue
        if name in found:
            problems.append("two metadata directories claim the distribution name %r (%s and %s)" % (name, found[name]._path, dist._path))
            duplicated.add(name)
        else:
            found[name] = dist
    for name in duplicated:
        del found[name]
    return found, problems


def package_digest(dist):
    """A digest over an installed distribution's files, in RECORD order, with each file's bytes."""
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


STUDY_MODULES = ("bind", "verify_attestation", "verify_binding", "storewalk", "cells", "pins", "run_layers", "score", "run_attempt",
                 "make_manifest", "trees", "guard", "marker", "test_study")


def _under(path, parent):
    return path == parent or str(path).startswith(str(parent) + "/")


def execution_problems(pins, dists=None):
    """The code that is running is the pinned code. Every module in sys.modules is classified by the file it was loaded
    from: a built-in or frozen module of the interpreter; a file of the interpreter's own library (trusted, a stated
    limit); a file of a pinned distribution, loaded by the source or extension loader with its cache path under the
    empty prefix; a registered study module from the study tree, loaded from its .py; anything else is refused --
    a module of any name loaded from any other place, a cache read beside a source, a loader of another class, an
    in-memory stand-in. The environment holds exactly the pinned distributions and no path hook; the import path,
    the study roots and the cache prefix are as harness/guard.py requires; the interpreter is the pinned implementation."""
    import platform
    import sysconfig
    from importlib import machinery, metadata
    out = []
    guard = sys.modules.get("guard")
    if guard is None or Path(getattr(guard, "__file__", "") or "/").resolve() != (STUDY / "harness" / "guard.py").resolve():
        return ["the trusted guard was not established by this process's bootstrap"]
    out += guard.cache_problems() + guard.site_problems() + guard.path_problems(str(STUDY)) + guard.shadow_problems(str(STUDY)) + guard.environment_problems()
    if platform.python_implementation() != pins["harnessPython"]["implementation"]:
        out.append("the interpreter is %s, not the pinned %s" % (platform.python_implementation(), pins["harnessPython"]["implementation"]))
    site = Path(sysconfig.get_paths()["purelib"]).resolve()
    library = Path(sysconfig.get_paths()["stdlib"]).resolve().parent  # the interpreter's lib/: its library, lib-dynload, its zip
    pinned = {normalized(n) for n in pins["intoto"]["packages"]}
    if dists is None:
        dists, inventory_problems = inventory()
        out += inventory_problems
    installed = dists
    for extra in sorted(set(installed) - pinned):
        out.append("distribution %s is installed in the virtual environment and is not pinned" % extra)
    for hook in sorted(site.glob("*.pth")):
        out.append("path hook %s is in the virtual environment; a .pth file runs code at startup" % hook.name)
    owned, tops = {}, {}
    for name in sorted(pinned & set(installed)):
        dist = installed[name]
        for f in dist.files or []:
            path = Path(dist.locate_file(f)).resolve()
            owned[path] = name
            if _under(path, site):
                top = path.relative_to(site).parts[0]
                if not top.endswith(".dist-info"):
                    tops[top.split(".")[0]] = name
    ModuleType = type(sys)  # the exact module type: type() is read, never isinstance(), which honours a spoofed __class__

    def verified_module(name, loader_kind):
        """A module in sys.modules that is a real module object loaded from a pinned file by the named loader class."""
        m = sys.modules.get(name)
        if m is None or type(m) is not ModuleType:
            return None
        o = Path(getattr(m, "__file__", "") or "/").resolve()
        return m if o in owned and type(getattr(m, "__loader__", None)) is loader_kind else None

    proxy_type = None
    utils = verified_module("cryptography.utils", machinery.SourceFileLoader)
    if utils is not None:
        proxy_type = getattr(utils, "_ModuleWithDeprecations", None)
    # the two objects cryptography's pinned extension creates in memory, admitted by identity to what verified modules hold
    rust = verified_module("cryptography.hazmat.bindings._rust", machinery.ExtensionFileLoader)
    cffi_backend = verified_module("_cffi_backend", machinery.ExtensionFileLoader)
    openssl_module = getattr(rust, "_openssl", None) if rust is not None else None
    openssl_lib = getattr(openssl_module, "lib", None) if type(openssl_module) is ModuleType else None
    lib_type = getattr(cffi_backend, "Lib", None) if cffi_backend is not None else None
    typing_module = sys.modules.get("typing")
    typing_ok = type(typing_module) is ModuleType and _under(Path(getattr(typing_module, "__file__", "") or "/").resolve(), library)
    prefix = sys.pycache_prefix
    study_roots = ((STUDY / "adapter").resolve(), (STUDY / "harness").resolve())
    for modname, mod in list(sys.modules.items()):
        if mod is None:
            continue
        if proxy_type is not None and type(mod) is proxy_type:
            inner = mod.__dict__.get("_module")  # cryptography's own deprecation proxy: the real module is what ran
            if type(inner) is ModuleType:
                mod = inner
        # the object's real type first, before any acceptance by namespace, origin or name
        if type(mod) is not ModuleType:
            # exactly: the two classes the library's typing module registers under typing.io and typing.re, and the OpenSSL
            # binding table cryptography's extension exposes -- each by identity to what a verified owner holds
            if modname in ("typing.io", "typing.re") and typing_ok and mod is getattr(typing_module, modname.split(".")[1], None):
                continue
            if modname == "_openssl.lib" and openssl_lib is not None and mod is openssl_lib and lib_type is not None and type(mod) is lib_type:
                continue
            out.append("%s is not a module (%s) and is not an object a verified owner holds" % (modname, type(mod).__name__))
            continue
        spec = getattr(mod, "__spec__", None)
        loader = spec.loader if spec is not None and spec.loader is not None else getattr(mod, "__loader__", None)
        origin = spec.origin if spec is not None and spec.origin else getattr(mod, "__file__", None)
        cached = getattr(mod, "__cached__", None)
        top = modname.split(".")[0]
        if modname == "_openssl" and openssl_module is not None and mod is openssl_module and not getattr(mod, "__file__", None) and not (spec is not None and spec.origin):
            continue  # the module cryptography's verified extension created in memory, by identity
        if spec is not None and spec.origin is None and spec.submodule_search_locations is not None and not getattr(mod, "__file__", None):
            locations = [Path(loc).resolve() for loc in spec.submodule_search_locations]
            inside = (lambda loc: _under(loc, site)) if top in tops else (lambda loc: _under(loc, site) or _under(loc, library))
            if not locations or not all(inside(loc) for loc in locations):
                out.append("%s is a namespace package with a search location outside the pinned distributions and the library" % modname)
            continue
        if origin in (None, "built-in", "frozen"):
            frozen = (machinery.BuiltinImporter, machinery.FrozenImporter)
            if loader in frozen or type(loader) in frozen or modname in sys.builtin_module_names:
                continue
            parent = sys.modules.get(modname.rpartition(".")[0]) if "." in modname else None
            parent_origin = Path(getattr(parent, "__file__", "") or "/").resolve()
            if parent is not None and parent_origin in owned and type(getattr(parent, "__loader__", None)) is machinery.ExtensionFileLoader:
                continue  # a submodule a pinned extension module creates in memory
            out.append("%s has no file origin and is not a built-in, frozen, pinned-extension or pinned originless module" % modname)
            continue
        o = Path(origin).resolve()
        if o in owned:
            if type(loader) not in (machinery.SourceFileLoader, machinery.ExtensionFileLoader):
                out.append("%s (a file of %s) was loaded by %s, not by the source or the extension loader" % (modname, owned[o], type(loader).__name__))
            if cached and (not prefix or not _under(Path(cached), Path(prefix))):
                out.append("%s's bytecode cache %s is not under the empty cache prefix" % (modname, cached))
        elif _under(o, library):
            if top in tops:
                out.append("%s carries a pinned distribution's name but was loaded from the interpreter's library (%s)" % (modname, o))
        elif modname == "guard" and o == (STUDY / "harness" / "guard.py").resolve() and spec is None and loader is None:
            continue  # the trusted guard: compiled from its bytes by exact path by the entry script's bootstrap, with no loader
        elif any(_under(o, root) for root in study_roots):
            if not (modname in STUDY_MODULES or (modname == "__main__")):
                out.append("%s was loaded from the study tree (%s) and is not a registered study module" % (modname, o))
            if type(loader) is not machinery.SourceFileLoader or o.suffix != ".py":
                out.append("%s (%s) was not loaded from its .py by the source loader" % (modname, o))
            if cached and (not prefix or not _under(Path(cached), Path(prefix))):
                out.append("%s's bytecode cache %s is not under the empty cache prefix" % (modname, cached))
        else:
            out.append("%s was loaded from %s: outside the interpreter's library, the pinned distributions and the study tree" % (modname, o))
    return out


def problems(pins, gateway_binary, require_all=False):
    out = []
    if gateway_binary is None or not Path(gateway_binary).resolve().is_file():
        out.append("the gateway verifier binary is not given or not a file")
    else:
        digest = sha256_file(Path(gateway_binary).resolve())  # the one file that is hashed is the one file that is launched (run_layers.resolved_gateway)
        if pins["gateway"]["binarySha256"] and pins["gateway"]["binarySha256"] != digest:
            out.append("the gateway binary's digest %s is not the pinned %s" % (digest, pins["gateway"]["binarySha256"]))
        if require_all and not pins["gateway"]["binarySha256"]:
            out.append("the gateway binary is not pinned")
    if sha256_file(STUDY / "fixtures" / "baseline" / "gateway.pubkey") != pins["gateway"]["publicKeySha256"]:
        out.append("the corpus public key is not the pinned one")
    dists, inventory_problems = inventory()  # the one inventory: hashing below and ownership in execution_problems() consume it
    out += inventory_problems
    for name, pin in pins["intoto"]["packages"].items():
        dist = dists.get(normalized(name))
        if dist is None:
            out.append("%s is not installed (or not uniquely)" % name)
            continue
        version, digest = package_digest(dist)
        if version != pin["version"]:
            out.append("%s is %s, not the pinned %s" % (name, version, pin["version"]))
        if pin["installedDigest"] and pin["installedDigest"] != digest:
            out.append("%s's installed files do not match the pinned digest" % name)
        if require_all and not pin["installedDigest"]:
            out.append("%s's installed digest is not pinned" % name)
    if adapter_keyid() != pins["adapter"]["keyid"]:
        out.append("the adapter key is not the pinned one")
    out += trusted_pubkey_problems(pins)
    if pins["harnessPython"].get("version") and pins["harnessPython"]["version"] != sys.version.split()[0]:
        out.append("the interpreter is %s, not the pinned %s" % (sys.version.split()[0], pins["harnessPython"]["version"]))
    if require_all and not pins["harnessPython"].get("version"):
        out.append("the interpreter version is not pinned")
    out += execution_problems(pins, dists)
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
