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
