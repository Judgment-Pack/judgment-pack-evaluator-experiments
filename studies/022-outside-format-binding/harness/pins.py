"""What the study pins, and how each pin is checked before anything is adjudicated.

- the gateway verifier: a commit of the gateway repository and a reproducible build recipe
  (`CGO_ENABLED=0 go build -trimpath -buildvcs=false` in `go/` under the pinned Go toolchain),
  pinned by the binary's SHA-256; the runner and the scorer refuse another binary;
- the corpus public key the gateway layer verifies under, by digest;
- the in-toto reference implementation: `securesystemslib` and `in-toto-attestation` by
  version and by a digest over the installed package files, read through importlib;
- the adapter key: the study-minted Ed25519 key's id, recomputed from its seed;
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


def trusted_pubkey_problems(pins):
    """The fixture's public key file is the pinned adapter key, by material and by id."""
    sys.path.insert(0, str(STUDY / "adapter"))
    import bind
    public = json.loads((STUDY / "fixtures" / "baseline" / "attestations" / "adapter.pubkey.json").read_text())
    signer = bind.adapter_signer()
    if public.get("keyid") != pins["adapter"]["keyid"] or public.get("keyval", {}).get("public") != signer.public_key.keyval.get("public"):
        return ["fixtures/baseline/attestations/adapter.pubkey.json is not the pinned adapter key"]
    return []


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
