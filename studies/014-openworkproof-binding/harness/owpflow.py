"""Build-time OpenWorkProof flow driver — the nine-step chain, made deterministic.

Runs the same nine-step five-role workflow the upstream delivery suite drives
(work order -> root grant activation -> two delegated grants -> repo_read ->
apply_patch -> local verification -> compose -> independent verifier -> recompose
-> acceptance request -> external acceptance), with three study-owned changes and
nothing else:

  1. `WorkOrder.objective` carries the judgment commitment (SPEC section 3).
  2. The executing request's `context_source_digest` carries the commitment digest.
  3. The Acceptor signs in process rather than over a TCP subprocess (identical
     bytes: `sign_payload("acceptance-receipt", draft, acceptor_key)`), because
     the study runs offline.

The executing tool call goes through OpenWorkProof's own patch executor. A real
source archive is written with `repo_tools.write_source_archive`, the work order
is bound to it, `repo_tools.initialize_candidate_workspace` recreates a real Git
candidate workspace under a private runtime root, and
`repo_tools.apply_patch_in_candidate_workspace` parses the canonical patch bytes
(`parse_patch_phase_a`), applies them (`apply_patch_phase_b`), commits the Git
checkpoint and derives the `PatchResultEvidence`. That executor-produced evidence
is the receipt's committed result payload and the post-patch replay checkpoint is
derived from the executor's own candidate commit and workspace manifest — the
fixture oracle is upstream's, not the harness's. The receipt envelope around it
is still assembled here (upstream ships no `execute_apply_patch` entry point;
its own delivery suite hand-builds the same envelope) and published through the
unmodified `evidence.complete_receipt_publication`.

This module is BUILD-TIME ONLY. It reaches into the pinned OpenWorkProof clone's
test helpers (read only, never modified, `OWP_SOURCE`) so that no upstream bytes
are copied into this repository; the verification path (`adapter/verify.py`,
`harness/run_verify.py`, `harness/score.py`) imports the installed package only.
The frozen fixture bytes, not this builder, are what the study scores.

`OWP_SOURCE` is pinned, not merely present (round 3). Before a single helper is
imported, `load_upstream` checks that the clone's HEAD equals
`PINS.json`'s pinned commit, that its tracked files are clean, that no
import-capable untracked path sits under the roots this module prepends to
`sys.path` (round 4, widened in round 5 to every suffix the interpreter will
import — `.pyc`, `.so`, `.pyd` — not `.py` alone), that every helper file it
imports matches its pinned digest in `openworkproof.upstreamHelpers.files`, and
that the installed distribution's own location is resolved and cached *before*
anything is prepended (round 5: `importlib.metadata` searches the live
`sys.path`). After the import it checks that the `openworkproof` the process
actually loaded resolves inside the installed package directory and still matches
`openworkproof.installedPackageDigest`, and that **every** module that appeared
during the import came from the interpreter's pre-existing search path, the
installed package, or a pinned helper file (round 5). Any failure refuses the
build.

Determinism: fixed Ed25519 seeds, fixed clocks, caller-supplied nonces, and — the
one thing upstream provides no seam for — `secrets.token_hex` patched with a
counter-derived generator for the duration of a build (recorded in PINS.json).
"""

import base64
import copy
import hashlib
import importlib.machinery
import json
import os
import shutil
import sqlite3
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROLES = ("Maintainer", "Manager", "Developer", "Verifier", "Sidecar", "Acceptor")

# The study's action file lives outside `src`, so the work order, the grants and
# both path predicates admit one extra write root. Recorded as an upstream-fixture
# divergence; nothing else in the fixture shape changes.
ACTION_ROOT = "decision-actions"
READ_ROOTS = [ACTION_ROOT, "src", "tests"]
WRITE_ROOTS = [ACTION_ROOT, "src"]

PATCH_OCCURRED_AT = "2026-01-01T00:00:05Z"
PATCH_REQUESTED_AT = "2026-01-01T00:00:02Z"
ACCEPTANCE_EXPIRES_AT = "2026-01-01T00:30:00Z"

# The candidate source the whole study patches. `src/wrap.py` is the upstream m2
# candidate file (so the repo-read step reads exactly what upstream reads);
# `decision-actions/.keep` exists because `apply_patch_phase_b` refuses to create
# a file whose immediate parent directory does not already exist.
ACTION_ROOT_KEEP_BYTES = b"Decision actions produced under this work order.\n"
SOURCE_COMMIT_AUTHOR = "Study014 <study014@example.invalid>"
SOURCE_COMMIT_MESSAGE = "study-014 candidate source\n"

_UPSTREAM = {}


class FlowError(RuntimeError):
    """The flow refused to build a configured chain."""


# --------------------------------------------------------------------------
# upstream access (build time only)
# --------------------------------------------------------------------------

PINS_PATH = Path(__file__).resolve().parent / "PINS.json"

# The upstream files this module imports or reads. Exactly these five: the
# conftest (loaded by explicit path) and the four test modules imported below.
UPSTREAM_HELPER_FILES = (
    "tests/conftest.py",
    "tests/test_delivery_m2.py",
    "tests/test_independent_recomposition.py",
    "tests/test_mcp_server.py",
    "tests/test_receipt_chain.py",
)

# The clone-relative roots `load_upstream` prepends to `sys.path`. Exactly one
# today; the untracked-shadow check below is written over the tuple so a second
# root cannot be added without its guard coming with it.
IMPORT_ROOTS = ("tests",)


def _pins():
    return json.loads(PINS_PATH.read_text(encoding="utf-8"))


def _git(root, *arguments):
    """Run git inside the clone; return stdout, or None when git cannot answer."""
    import subprocess

    try:
        completed = subprocess.run(
            ["git", "-C", str(root)] + list(arguments),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except Exception:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout


def _untracked_paths(root):
    """Every untracked clone-relative path, or None when git cannot answer.

    `--others` **without** `--exclude-standard`, deliberately: an ignored path is
    still an importable path, and the ignore rules can be extended from
    `.git/info/exclude`, which is not a tracked file and so cannot be caught by
    the cleanliness check. `-z` because git quotes unusual names otherwise.
    """
    output = _git(root, "ls-files", "--others", "-z")
    if output is None:
        return None
    return [item for item in output.split("\0") if item]


BYTECODE_CACHE_DIRECTORY = "__pycache__"


def importable_suffixes():
    """Every suffix the running interpreter's own import machinery will load.

    `importlib.machinery.all_suffixes()` — source, bytecode and extension-module
    suffixes together — rather than a hand-written `".py"`. Round 5's finding:
    the round-4 classifier tested `.py` alone, so a sourceless `openworkproof.pyc`
    or a compiled `openworkproof.cpython-312-x86_64-linux-gnu.so` dropped under a
    prepended root imported exactly as well as a `.py` would and was classified
    as inert. Asking the interpreter that will do the importing keeps the list
    from drifting away from the machinery it describes.
    """
    return tuple(importlib.machinery.all_suffixes())


def _under_import_root(relative):
    parts = relative.strip("/").split("/")
    return any(
        parts[: len(import_root.split("/"))] == import_root.split("/")
        for import_root in IMPORT_ROOTS
    )


def import_shadow_paths(root, untracked):
    """Untracked paths under a prepended import root that Python could import.

    Round 4's blocker. Untracked paths are ignored by the cleanliness check on
    purpose — a `build/` directory beside the checkout changes nothing this
    module reads — but `load_upstream` *prepends* `<clone>/tests` to `sys.path`.
    Under that root an untracked path is not inert: `tests/openworkproof/` with
    an `__init__.py` is imported in preference to the digest-checked installed
    package and then stays in `sys.modules` for every later verification, and
    any untracked importable file can shadow a module name through the same root
    (namespace packages make the deeper ones reachable too).

    So under an import root the rule inverts: any untracked path carrying an
    importable suffix (round 5: `importable_suffixes()`, so `.pyc` and the
    `.so`/`.pyd` extension variants count exactly as `.py` does), and any
    untracked directory carrying an `__init__` of any importable suffix, is a
    refusal. Outside those roots untracked stays ignored — this clone's own
    untracked `build/lib/openworkproof/` is exactly that shape and is exactly why
    the check is scoped to the roots rather than to the whole tree.

    **One named exemption: PEP 3147 bytecode cache entries.** A file inside a
    `__pycache__/` directory cannot introduce a module name — the interpreter
    consults `__pycache__/<name>.<tag>.pyc` only when `<name>.py` already exists
    beside it, and a *sourceless* import must place the `.pyc` at the module's
    own position, which this classifier refuses. Exempting them is also the only
    way the rule can hold at all: importing the pinned helpers necessarily writes
    those caches into the read-only clone, so refusing them would refuse the
    pinned clone after its own first use. The residual this leaves is narrow and
    stated rather than hidden: a cache entry whose recorded source metadata
    matches could be executed in place of the digest-checked source beside it.
    """
    root = Path(root)
    suffixes = importable_suffixes()
    shadows = []
    for relative in untracked:
        if not _under_import_root(relative):
            continue
        trimmed = relative.rstrip("/")
        parts = trimmed.split("/")
        path = root / trimmed
        if any(trimmed.endswith(suffix) for suffix in suffixes):
            if BYTECODE_CACHE_DIRECTORY in parts[:-1]:
                continue
            shadows.append(trimmed)
        elif path.is_dir() and any(
            (path / ("__init__" + suffix)).exists() for suffix in suffixes
        ):
            # A symlinked or otherwise directory-shaped untracked entry: git
            # names it once, so the file rule above never sees its contents.
            shadows.append(trimmed + "/")
    return sorted(set(shadows))


def path_roots(entries):
    """`sys.path`-style entries as resolved directories; unresolvable ones drop."""
    roots = set()
    for entry in entries:
        try:
            roots.add(Path(entry or ".").resolve())
        except Exception:  # pragma: no cover - unresolvable path entry
            continue
    return roots


def _within(path, roots):
    return any(path == root or root in path.parents for root in roots)


def _module_origins(module):
    """Every filesystem location a loaded module claims to have come from."""
    try:
        origin = getattr(module, "__file__", None)
    except Exception:  # pragma: no cover - hostile module object
        origin = None
    if origin:
        return [origin]
    try:
        search = list(getattr(module, "__path__", []) or [])
    except Exception:  # pragma: no cover - hostile module object
        search = []
    return [str(entry) for entry in search]


def imported_module_problems(before, root, admitted_roots, modules=None):
    """Authenticate every module the helper import added to `sys.modules`.

    Round 5's finding: the round-4 post-import check spoke about `openworkproof`
    and nothing else, so whatever *else* the prepended roots delivered — a second
    package, a helper the pins do not cover, a module out of a directory that
    something appended to `sys.path` on its way past — was never looked at at all.

    The check is a diff of `sys.modules` taken across the import, and it makes
    two statements about every module that appeared:

      1. its origin sits under a root that was already reachable **before** the
         prepend (the stdlib, site-packages, this study's own directories), under
         the installed package directory, or under one of the pinned import
         roots — and nowhere else. Anything else means the import reached a
         location this build never authorized;
      2. if it came out of a pinned import root, it is one of the pinned helper
         files (`UPSTREAM_HELPER_FILES`). The roots this builder puts on
         `sys.path` may deliver the five files whose digests are pinned, and not
         a sixth.

    Empty means every module loaded is accounted for.
    """
    modules = sys.modules if modules is None else modules
    root = Path(root).resolve()
    import_roots = {(root / import_root).resolve() for import_root in IMPORT_ROOTS}
    admitted = set(admitted_roots) | import_roots
    pinned = {(root / name).resolve() for name in UPSTREAM_HELPER_FILES}
    problems = []
    for name in sorted(set(modules) - set(before)):
        module = modules.get(name)
        if module is None:
            continue
        for origin in _module_origins(module):
            try:
                path = Path(origin).resolve()
            except Exception:  # pragma: no cover - unresolvable module origin
                problems.append(
                    "the module %s appeared during the helper import with an "
                    "unresolvable origin %r" % (name, origin)
                )
                continue
            if not _within(path, admitted):
                problems.append(
                    "the module %s was imported from %s, which is outside the "
                    "installed package, the search path this build started with, "
                    "and the pinned import roots" % (name, path)
                )
            elif _within(path, import_roots) and path not in pinned:
                problems.append(
                    "the module %s was imported from %s, under a pinned import "
                    "root but not one of the pinned upstream helper files"
                    % (name, path)
                )
    return problems


def loaded_package_problems(pins=None, name="openworkproof"):
    """After the helper import: the `openworkproof` in memory is the installed one.

    The path checks above run *before* anything is imported, which leaves the
    other half of round 4's finding: whatever `sys.path` did during the import,
    the module the process ended up with has to be the package the freeze pins.
    Two independent statements, both required:

      1. the loaded module's `__file__` resolves inside the installed
         distribution's own package directory (located through the distribution
         metadata, not through `sys.path`, which is the thing under suspicion);
      2. that directory still hashes to `openworkproof.installedPackageDigest`.

    Empty means the loaded package is the pinned installed one.
    """
    import importlib

    import verify  # adapter-side; the single implementation of this pin

    pins = _pins() if pins is None else pins
    try:
        module = importlib.import_module(name)
    except Exception as error:
        return [
            "the %s package could not be imported after the helper import: %s"
            % (name, error)
        ]
    origin = getattr(module, "__file__", None)
    if not origin:
        return [
            "the imported %s module carries no file origin, so it cannot be shown "
            "to be the installed package" % name
        ]
    try:
        installed_root = verify.installed_package_root(name)
    except Exception as error:
        return [
            "the installed %s package directory could not be resolved: %s"
            % (name, error)
        ]
    problems = []
    origin = Path(origin).resolve()
    if installed_root != origin.parent and installed_root not in origin.parents:
        problems.append(
            "the imported %s module resolves to %s, outside the installed package "
            "directory %s" % (name, origin, installed_root)
        )
    expected = (pins.get("openworkproof") or {}).get("installedPackageDigest")
    if not expected:
        problems.append(
            "PINS.json carries no installed openworkproof package digest, so the "
            "package this build imported is unverified"
        )
        return problems
    try:
        actual = verify.installed_package_digest(name, root=installed_root)
    except Exception as error:
        return problems + [
            "the installed %s package could not be re-verified after the helper "
            "import: %s" % (name, error)
        ]
    if actual != expected:
        problems.append(
            "the installed %s package no longer matches its pinned digest after "
            "the helper import" % name
        )
    return problems


def upstream_problems(root, pins=None):
    """Every reason this clone is not the pinned one. Empty means it is.

    Round 3's finding: the builder imported external test helpers after checking
    only that `tests/conftest.py` existed, so `OWP_SOURCE` could point at any
    working tree — including a modified one — and the fixtures would still be
    called upstream's. Four independent checks now stand between the flag and
    the import:

      1. the clone's HEAD is exactly the pinned commit;
      2. its tracked files are clean (untracked paths outside the import roots
         are ignored — a build directory beside the checkout changes nothing
         this module reads);
      3. no untracked path under an import root is import-capable (round 4:
         `import_shadow_paths`, because those roots go on `sys.path`; round 5
         widened "import-capable" to every suffix the interpreter loads);
      4. every helper file this module imports matches its pinned digest.

    Any one of them failing is a refusal, not a warning: the fixture oracle's
    whole claim is that it is upstream's.
    """
    pins = _pins() if pins is None else pins
    upstream = (pins.get("openworkproof") or {})
    helpers = upstream.get("upstreamHelpers") or {}
    problems = []
    root = Path(root)
    if not (root / "tests" / "conftest.py").is_file():
        return [
            "OWP_SOURCE must point at the pinned OpenWorkProof clone "
            "(tests/conftest.py not found)"
        ]

    pinned_commit = helpers.get("commit") or upstream.get("commit")
    if not pinned_commit:
        problems.append("PINS.json carries no pinned OpenWorkProof commit")
    else:
        head = _git(root, "rev-parse", "HEAD")
        if head is None:
            problems.append(
                "the OWP_SOURCE clone's HEAD could not be read with git, so it "
                "cannot be shown to be the pinned commit"
            )
        elif head.strip() != pinned_commit:
            problems.append(
                "the OWP_SOURCE clone is at %s, pinned %s"
                % (head.strip(), pinned_commit)
            )

    status = _git(root, "status", "--porcelain")
    if status is None:
        problems.append("the OWP_SOURCE clone's working tree state could not be read")
    else:
        dirty = [
            line
            for line in status.splitlines()
            if line.strip() and not line.startswith("??")
        ]
        if dirty:
            problems.append(
                "the OWP_SOURCE clone has modified tracked files: %s" % "; ".join(dirty)
            )

    untracked = _untracked_paths(root)
    if untracked is None:
        problems.append(
            "the OWP_SOURCE clone's untracked paths could not be read, so the "
            "import roots this builder prepends to sys.path cannot be shown to be "
            "free of shadowing modules"
        )
    else:
        shadows = import_shadow_paths(root, untracked)
        if shadows:
            problems.append(
                "the OWP_SOURCE clone carries import-capable untracked paths under "
                "the import roots %s, which this builder prepends to sys.path: %s"
                % (", ".join(IMPORT_ROOTS), "; ".join(shadows))
            )

    pinned_files = helpers.get("files")
    if not isinstance(pinned_files, dict) or not pinned_files:
        problems.append(
            "PINS.json pins no upstream helper file digests, so the bytes this "
            "builder imports are unverified"
        )
        pinned_files = {}
    missing_pins = [name for name in UPSTREAM_HELPER_FILES if name not in pinned_files]
    if pinned_files and missing_pins:
        problems.append(
            "these imported upstream helpers are unpinned: %s" % ", ".join(missing_pins)
        )
    unused_pins = [name for name in pinned_files if name not in UPSTREAM_HELPER_FILES]
    if unused_pins:
        problems.append(
            "PINS.json pins upstream files this builder does not import: %s"
            % ", ".join(sorted(unused_pins))
        )
    for name in UPSTREAM_HELPER_FILES:
        expected = pinned_files.get(name)
        if expected is None:
            continue
        path = root / name
        if not path.is_file():
            problems.append("pinned upstream helper is absent: " + name)
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            problems.append("pinned upstream helper does not match its digest: " + name)
    return problems


def load_upstream(source=None):
    """Import the pinned clone's fixture helpers once, read only and verified."""
    if _UPSTREAM:
        return _UPSTREAM
    root = Path(source or os.environ.get("OWP_SOURCE", "")).expanduser()
    problems = upstream_problems(root)
    if problems:
        raise FlowError(
            "the OWP_SOURCE clone is not the pinned one, so no fixture may be "
            "built from it: " + "; ".join(problems)
        )

    import verify  # adapter-side; the installed-distribution locator

    # Round 5: the installed distribution is located and cached BEFORE a single
    # root reaches `sys.path`. `importlib.metadata.distribution()` searches the
    # live path, so resolving it afterwards would ask the very path this check
    # distrusts where the package it authenticates lives.
    try:
        installed_root = verify.installed_package_root()
    except Exception as error:
        raise FlowError(
            "the installed openworkproof package could not be located before the "
            "import roots were prepended, so no fixture may be built: %s" % error
        )

    inserted = [str(root / import_root) for import_root in IMPORT_ROOTS]
    # Snapshotted before the prepend, both of them: the roots that were already
    # reachable, and the modules that were already loaded.
    admitted_roots = path_roots(sys.path) | {installed_root}
    before_modules = set(sys.modules)
    for entry in inserted:
        sys.path.insert(0, entry)

    def refuse(headline, problems):
        for entry in inserted:
            if entry in sys.path:
                sys.path.remove(entry)
        raise FlowError(headline + ": " + "; ".join(problems))

    # The upstream conftest is loaded by explicit path under a private module
    # name: under pytest the bare name `conftest` already belongs to the harness
    # suite's own conftest, and importing it here would silently pick that up.
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "study014_upstream_conftest", root / "tests" / "conftest.py"
    )
    conftest = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(conftest)

    import test_delivery_m2
    import test_independent_recomposition
    import test_mcp_server
    import test_receipt_chain

    # Round 4's other half: the roots above were on `sys.path` while everything
    # under them imported, so the last word belongs to the module that actually
    # loaded. A build whose `openworkproof` is not the pinned installed package
    # is refused here, after the import and before a single fixture byte.
    loaded = loaded_package_problems()
    if loaded:
        refuse(
            "the openworkproof package this build imported is not the pinned "
            "installed one, so no fixture may be built from it",
            loaded,
        )

    # Round 5: and `openworkproof` is not the only module that loaded. Every
    # module that appeared while those roots were on `sys.path` has to be
    # accounted for by where it came from.
    imported = imported_module_problems(before_modules, root, admitted_roots)
    if imported:
        refuse(
            "the helper import loaded modules this build did not authorize, so "
            "no fixture may be built from them",
            imported,
        )

    _UPSTREAM.update(
        {
            "root": root,
            "conftest": conftest,
            "m2": test_delivery_m2,
            "chain": test_receipt_chain,
            "mcp": test_mcp_server,
            "recomposition": test_independent_recomposition,
        }
    )
    return _UPSTREAM


def _fixture(function):
    """pytest wraps fixture functions to refuse direct calls; unwrap them."""
    return getattr(function, "__wrapped__", function)


# --------------------------------------------------------------------------
# deterministic identities, clocks, entropy
# --------------------------------------------------------------------------

def role_seed(role):
    return hashlib.sha256(("study-014/role/" + role).encode("utf-8")).digest()


def role_keys():
    """The six fixture keys: Ed25519 private keys from fixed seeds."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from openworkproof.signing import key_id

    keys = {}
    for role in ROLES:
        private_key = Ed25519PrivateKey.from_private_bytes(role_seed(role))
        public_key = private_key.public_key()
        raw = public_key.public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        keys[role] = (
            private_key,
            {
                "role": role,
                "subject_id": role.lower(),
                "key_id": key_id(public_key),
                "public_key_b64url": base64.urlsafe_b64encode(raw)
                .decode("ascii")
                .rstrip("="),
            },
        )
    return keys


class DeterministicEntropy:
    """Counter-derived stand-in for `secrets.token_hex` (build path only)."""

    def __init__(self, salt=""):
        self.salt = salt
        self.draws = 0

    def token_hex(self, nbytes=None):
        self.draws += 1
        size = 32 if nbytes is None else nbytes
        out = b""
        block = 0
        while len(out) < size:
            seed = "study-014/entropy/%s/%d/%d" % (self.salt, self.draws, block)
            out += hashlib.sha256(seed.encode("utf-8")).digest()
            block += 1
        return out[:size].hex()


def nonce(salt, label):
    return hashlib.sha256(("study-014/nonce/%s/%s" % (salt, label)).encode()).hexdigest()


def fixed_now():
    return datetime(2026, 1, 1, 0, 0, 5, tzinfo=timezone.utc)


# --------------------------------------------------------------------------
# the candidate source archive
# --------------------------------------------------------------------------

def source_files(upstream):
    """The two files of the study's candidate source, in canonical path order."""
    from openworkproof.repo_tools import SourceFile

    return (
        SourceFile(ACTION_ROOT + "/.keep", "100644", ACTION_ROOT_KEEP_BYTES),
        SourceFile("src/wrap.py", "100644", upstream["m2"].WRAP_CANDIDATE.encode("utf-8")),
    )


def source_archive(upstream):
    """The exact `source/base.owpsrc` bytes and their derived Git identity.

    Written by upstream's own `write_source_archive`, so the archive digest, tree
    object id and commit object id are OWP's derivations of these bytes and not
    the harness's.
    """
    from openworkproof.repo_tools import git_commit_oid, git_tree_oid, write_source_archive

    files = source_files(upstream)
    tree_oid = git_tree_oid(files)
    commit_raw = (
        "tree %s\n"
        "author %s 0 +0000\n"
        "committer %s 0 +0000\n"
        "\n"
        "%s" % (tree_oid, SOURCE_COMMIT_AUTHOR, SOURCE_COMMIT_AUTHOR, SOURCE_COMMIT_MESSAGE)
    ).encode("ascii")
    raw = write_source_archive(files, commit_raw)
    return {
        "files": files,
        "commit_raw": commit_raw,
        "tree_oid": tree_oid,
        "source_commit": git_commit_oid(commit_raw),
        "bytes": raw,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def parsed_source(upstream, work_order, archive):
    """Upstream's own parse of the archive, bound to the signed work order."""
    from openworkproof.repo_tools import parse_source_archive

    return parse_source_archive(
        archive["bytes"],
        work_order,
        trusted_helper_image_digest=work_order.replay_profile.trusted_helper_image_digest,
    )


# --------------------------------------------------------------------------
# the study work order
# --------------------------------------------------------------------------

def work_order_document(upstream, *, objective, updates=None, archive=None):
    """The upstream fixture work order with the study's objective, roots and source."""
    import rfc8785

    conftest = upstream["conftest"]
    bindings = _fixture(conftest.key_bindings)()
    artifacts = _fixture(conftest.demo_evidence_artifacts)()
    document = _fixture(conftest.work_order_dict)(bindings, artifacts)

    document["objective"] = objective
    if archive is not None:
        # Bind the work order to the archive that actually exists, exactly as
        # upstream's own `_bound_source` helper does: without this the candidate
        # workspace cannot be initialised from the declared source at all.
        document["source_commit"] = archive["source_commit"]
        document["source_artifact"]["sha256"] = archive["sha256"]
        document["source_artifact"]["size_bytes"] = len(archive["bytes"])
        document["replay_profile"]["source_artifact_sha256"] = archive["sha256"]
        document["replay_profile_digest"] = hashlib.sha256(
            rfc8785.dumps(
                {
                    "domain": "openworkproof/replay-profile/v0.1",
                    "profile": document["replay_profile"],
                }
            )
        ).hexdigest()
    document["allowed_read_roots"] = list(READ_ROOTS)
    document["allowed_write_roots"] = list(WRITE_ROOTS)
    document["root_grant_template"]["allowed_read_roots"] = list(READ_ROOTS)
    document["root_grant_template"]["allowed_write_roots"] = list(WRITE_ROOTS)

    preconditions = []
    for spec in document["preconditions"]:
        if spec["name"] == "path_allowed":
            spec = conftest.predicate(
                spec["name"],
                spec["applies_to_tools"],
                {**spec["arguments"], "allowed_roots": list(READ_ROOTS)},
                version=spec["version"],
            )
        preconditions.append(spec)
    document["preconditions"] = sorted(
        preconditions, key=lambda item: item["predicate_id"]
    )
    invariants = []
    for spec in document["invariants"]:
        if spec["name"] == "path_allowed":
            spec = conftest.predicate(
                spec["name"],
                spec["applies_to_tools"],
                {**spec["arguments"], "allowed_roots": list(WRITE_ROOTS)},
                version=spec["version"],
            )
        invariants.append(spec)
    document["invariants"] = sorted(invariants, key=lambda item: item["predicate_id"])

    if updates:
        document.update(copy.deepcopy(updates))
    return document


def signed_work_order(upstream, document, keys):
    return _fixture(upstream["conftest"].signed_work_order)(document, keys)


# --------------------------------------------------------------------------
# the chain
# --------------------------------------------------------------------------

def candidate_workspace(tmp_path, parsed, *, salt):
    """A real Git candidate workspace, recreated by upstream from the archive."""
    from openworkproof.repo_tools import WorkspaceInitRequest, initialize_candidate_workspace

    runtime_root = Path(tmp_path).resolve() / "candidate-runtime"
    runtime_root.mkdir(mode=0o700)
    runtime_root.chmod(0o700)
    workspace_id = hashlib.sha256(
        ("study-014/workspace/" + salt).encode("utf-8")
    ).hexdigest()
    return initialize_candidate_workspace(
        WorkspaceInitRequest(
            runtime_root=runtime_root,
            workspace_id=workspace_id,
            source=parsed,
        )
    )


def _checkpoint_for(files, head_commit):
    """The replay checkpoint upstream itself derives from a file set and commit."""
    from openworkproof.repo_tools import ReplayCheckpoint, _replay_workspace_manifest

    manifest, digest = _replay_workspace_manifest(files, head_commit)
    return ReplayCheckpoint(
        files=tuple(files),
        head_commit=head_commit,
        workspace_manifest=manifest,
        workspace_manifest_digest=digest,
        verified_test_results=(),
    )


DEVELOPER_QUOTA = {"tool_calls": 3, "repair_rounds": 0}


def _case(upstream, tmp_path, work_order, keys, now, *, salt, parsed,
          developer_quota=None):
    """Ledger, activated root grant, verifier and developer grants, checkpoint.

    Modelled on the upstream `_m2_case`; the developer grant additionally carries
    the study's action write root, and the checkpoint is the real candidate
    workspace's rather than a hand-built manifest.

    `developer_quota` exists for the upstream retry-episode probe alone: every
    registered cell builds on `DEVELOPER_QUOTA` (three tool calls, no repair
    rounds), which is exactly what the nine-step chain spends, so a probe asking
    whether upstream admits a *second* patch has to widen it or it only ever
    rediscovers the fixture's own quota. No fixture passes this argument.
    """
    from openworkproof.policy import AuthorizationLedgerPrefix, derive_authorization_context

    chain = upstream["chain"]
    mcp = upstream["mcp"]

    work_order = chain._work_order_with_pr_chain_predicates(
        work_order, keys["Maintainer"][0]
    )
    root = mcp._resigned_root(work_order, keys["Maintainer"][0])
    ledger_path = tmp_path / "chain.sqlite3"
    evidence_root = tmp_path / "chain-evidence"
    evidence_root.mkdir()
    chain._activate_ledger_root(ledger_path, work_order, root, keys, now)

    verifier = chain._child_grant(
        work_order,
        root,
        keys,
        label="study014:verifier",
        subject_role="Verifier",
        updates={"quota": {"tool_calls": 2, "repair_rounds": 0}},
    )
    verifier_issuance = chain._issue_child(
        ledger_path,
        verifier,
        chain._delegation_request(
            work_order,
            root,
            verifier,
            keys,
            actor_role="Manager",
            nonce=nonce(salt, "verifier-request"),
        ),
        keys,
        now,
    )
    developer = chain._child_grant(
        work_order,
        root,
        keys,
        label="study014:developer",
        updates={
            "allowed_tools": ["owp.apply_patch", "owp.repo_read", "owp.rollback_patch"],
            "allowed_read_roots": list(READ_ROOTS),
            "allowed_write_roots": list(WRITE_ROOTS),
            "quota": dict(developer_quota or DEVELOPER_QUOTA),
        },
    )
    developer_issuance = chain._issue_child(
        ledger_path,
        developer,
        chain._delegation_request(
            work_order,
            root,
            developer,
            keys,
            actor_role="Manager",
            nonce=nonce(salt, "developer-request"),
        ),
        keys,
        now,
    )

    # The source checkpoint is the real candidate workspace's: the file set
    # upstream parsed out of the archive at the commit upstream's own Git
    # recreation produced.
    workspace = candidate_workspace(tmp_path, parsed, salt=salt)
    if workspace.head_commit != work_order.source_commit:
        raise FlowError("candidate workspace head is not the work order source commit")
    checkpoint = _checkpoint_for(parsed.files, workspace.head_commit)
    if checkpoint.workspace_manifest_digest != workspace.workspace_manifest_digest:
        raise FlowError("candidate workspace manifest is not the replayed manifest")
    receipts, grants, attempts = chain._grant_replay_inputs(ledger_path, work_order)
    context = derive_authorization_context(
        work_order,
        AuthorizationLedgerPrefix(
            effective_grants=tuple(sorted(grants.values(), key=lambda i: i.grant_id)),
            grant_attempts=tuple(sorted(attempts.values(), key=lambda i: i.digest)),
            receipts=receipts,
        ),
        (),
        checkpoint,
        now,
    )
    return {
        "ledger_path": ledger_path,
        "evidence_root": evidence_root,
        "work_order": work_order,
        "context": context,
        "root": root,
        "verifier": verifier,
        "developer": developer,
        "verifier_issuance": verifier_issuance,
        "developer_issuance": developer_issuance,
        "checkpoint": checkpoint,
        "manifest_digest": checkpoint.workspace_manifest_digest,
        "workspace": workspace,
        "parsed_source": parsed,
        "patch_rounds": 0,
    }


def _agent_request(case, keys, *, role, tool_name, arguments, nonce_value,
                   context_source_digest, requested_at):
    from openworkproof.models import AgentRequest, request_arguments_digest
    from openworkproof.signing import sign_payload

    binding = keys[role][1]
    return AgentRequest.model_validate(
        sign_payload(
            "agent-request",
            {
                "claim_type": "agent-request",
                "work_order_digest": case["work_order"].digest,
                "grant_id": case["developer"].grant_id,
                "actor_id": binding["subject_id"],
                "actor_key_id": binding["key_id"],
                "tool_name": tool_name,
                "arguments_digest": request_arguments_digest(tool_name, arguments),
                "nonce": nonce_value,
                "requested_at": requested_at,
                "authentication_method": "agent_signature",
                "model_id": "model",
                "model_version": "1",
                "prompt_template_digest": "a" * 64,
                "context_source_digest": context_source_digest,
            },
            keys[role][0],
        )
    )


def _repo_read(upstream, case, keys, now, *, salt, context_source_digest):
    """Step 2, with the request's context source digest under study control."""
    import openworkproof.mcp_server as mcp_server
    from openworkproof.models import RepoReadArguments
    from openworkproof.policy import ProspectiveExecutionFacts

    # The read runs against the real candidate worktree, not a stand-in copy.
    candidate_root = case["workspace"].worktree
    arguments = RepoReadArguments(path="src/wrap.py")
    request = _agent_request(
        case,
        keys,
        role="Developer",
        tool_name="owp.repo_read",
        arguments=arguments,
        nonce_value=nonce(salt, "repo-read"),
        context_source_digest=context_source_digest,
        requested_at=PATCH_REQUESTED_AT,
    )
    receipt = mcp_server.execute_repo_read(
        case["ledger_path"],
        evidence_root=case["evidence_root"],
        context=case["context"],
        request=request,
        request_arguments=arguments,
        execution_facts=ProspectiveExecutionFacts(
            execution_context_id="1" * 64,
            container_instance_id_digest="2" * 64,
            controller_id=keys["Sidecar"][1]["key_id"],
        ),
        sidecar_private_key=keys["Sidecar"][0],
        candidate_runtime_root=candidate_root,
        handler=mcp_server.make_repo_pipeline_read_handler(),
        clock=lambda: now,
    )
    case["repo_read_receipt"] = receipt
    case["previous_receipt"] = receipt
    case["candidate_root"] = candidate_root
    return receipt


def _publish_action_patch(upstream, case, keys, now, *, salt, patch_bytes,
                          target_paths, context_source_digest, occurred_at,
                          parents, ordinal=1, nonce_label="apply-patch"):
    """Step 3 — the executing tool call, driven through OWP's patch executor.

    `apply_patch_in_candidate_workspace` parses the canonical patch bytes,
    applies them to the real candidate workspace and derives the result; the
    derived `PatchResultEvidence` is what the receipt commits and the derived
    candidate commit and workspace manifest are what the next checkpoint carries.
    The receipt envelope is assembled here because upstream ships no
    `execute_apply_patch` entry point; every value inside it that describes the
    execution comes from the executor.
    """
    import rfc8785
    import openworkproof.evidence as evidence
    import openworkproof.mcp_server as mcp_server
    from openworkproof.models import ACTION_RECEIPT_ADAPTER
    from openworkproof.predicates import (
        EvaluationContext,
        evaluate_required_predicates,
        select_required_predicates,
    )
    from openworkproof.repo_tools import (
        PatchRequest,
        ResolutionManifest,
        ResolutionManifestEntry,
        _candidate_files_from_git,
        apply_patch_in_candidate_workspace,
        resolution_manifest_digest,
    )
    from openworkproof.signing import key_id, sign_payload

    work_order = case["work_order"]
    previous = case["previous_receipt"]
    developer = case["developer"]
    # Quota authority is replayed from the ledger at publication: the context
    # must be the one that already carries the repo-read receipt.
    context = upstream["m2"]._refresh_context(case, case["checkpoint"], now)
    case["context"] = context

    arguments = {
        "target_paths": list(target_paths),
        "patch_digest": hashlib.sha256(patch_bytes).hexdigest(),
        "patch_size_bytes": len(patch_bytes),
    }
    request = _agent_request(
        case,
        keys,
        role="Developer",
        tool_name="owp.apply_patch",
        arguments=arguments,
        nonce_value=nonce(salt, nonce_label),
        context_source_digest=context_source_digest,
        requested_at=PATCH_REQUESTED_AT,
    )

    parent_checkpoint = case["checkpoint"]
    executed = apply_patch_in_candidate_workspace(
        PatchRequest(
            workspace=case["workspace"],
            patch_bytes=patch_bytes,
            expected_patch_digest=arguments["patch_digest"],
            expected_patch_size_bytes=arguments["patch_size_bytes"],
            declared_target_paths=tuple(target_paths),
            parent_commit=parent_checkpoint.head_commit,
            parent_manifest_digest=parent_checkpoint.workspace_manifest_digest,
            occurred_at=occurred_at,
            replay_profile=work_order.replay_profile,
            replay_profile_digest=work_order.replay_profile_digest,
        )
    )
    result = executed.evidence.model_dump(mode="json")
    result_bytes = rfc8785.dumps(result)
    result_digest = hashlib.sha256(result_bytes).hexdigest()
    candidate_commit = executed.candidate_commit

    manifest = ResolutionManifest(
        schema_version="openworkproof-resolution-manifest/0.1",
        workspace_manifest_digest=executed.parent_manifest_digest,
        requested_paths=tuple(target_paths),
        resolved_entries=tuple(
            ResolutionManifestEntry(requested_path=path, resolved_relative_path=path)
            for path in target_paths
        ),
    )
    remaining_before = mcp_server._remaining_tool_calls(context, developer.grant_id)
    path_input = {
        "requested_paths": list(target_paths),
        "resolved_entries": [
            {"requested_path": path, "resolved_relative_path": path}
            for path in target_paths
        ],
        "resolution_manifest_digest": resolution_manifest_digest(manifest),
    }
    quota_input = {
        "grant_id": developer.grant_id,
        "metric": "tool_calls",
        "amount": 1,
        "grant_remaining_before": remaining_before,
        "ledger_prefix_digest": previous.digest,
    }
    selected = select_required_predicates(
        work_order=work_order,
        tool_name="owp.apply_patch",
        policy_decision="allow",
        execution_status="succeeded",
        test_mode="developer",
    )
    inputs = {}
    for spec in selected:
        if spec.name == "path_allowed":
            inputs[spec.predicate_id] = path_input
        elif spec.name == "quota_remaining":
            inputs[spec.predicate_id] = quota_input
        else:
            raise FlowError("unexpected apply-patch predicate: " + spec.name)
    predicate_results = evaluate_required_predicates(
        selected,
        EvaluationContext(
            inputs=inputs,
            authoritative_inputs=inputs,
            authoritative_ledger_prefix_digests={developer.grant_id: previous.digest},
        ),
    )

    raw = {
        "protocol_version": "0.1",
        "receipt_id": hashlib.sha256(
            rfc8785.dumps(
                {
                    "domain": "openworkproof/receipt-id/v0.1",
                    "request_digest": request.digest,
                    "entropy": __import__("secrets").token_hex(32),
                }
            )
        ).hexdigest(),
        "work_order_digest": work_order.digest,
        "actor_type": "agent",
        "actor_id": request.actor_id,
        "actor_key_id": request.actor_key_id,
        "nested_claim_type": "agent-request",
        "nested_claim_digest": request.digest,
        "nested_claim": request.model_dump(mode="json"),
        "gateway_signer_key_id": key_id(keys["Sidecar"][0].public_key()),
        "event_type": "tool_call",
        "policy_decision": "allow",
        "policy_error_code": None,
        "execution_status": "succeeded",
        "execution_error_code": None,
        "quota_charge": {
            "grant_id": developer.grant_id,
            "metric": "tool_calls",
            "amount": 1,
            "remaining_after": remaining_before - 1,
        },
        "state_before": context.current_state,
        "state_after": context.current_state,
        "parent_receipt_ids": list(parents),
        "correlation_factors": {
            "model_id": request.model_id,
            "model_version": request.model_version,
            "prompt_template_digest": request.prompt_template_digest,
            "context_source_digest": request.context_source_digest,
            "toolchain_id": hashlib.sha256(
                rfc8785.dumps(
                    {
                        "domain": "openworkproof/toolchain/v0.1",
                        "tool_name": "owp.apply_patch",
                        "tool_version": "0.1",
                    }
                )
            ).hexdigest(),
            "execution_context_id": "1" * 64,
            "container_instance_id_digest": "2" * 64,
            "controller_id": keys["Sidecar"][1]["key_id"],
            "fixed_test_source_digest": None,
        },
        "evidence_refs": [
            {
                "path": "evidence/patch-input/%02d.diff" % ordinal,
                "sha256": arguments["patch_digest"],
                "media_type": "text/x-diff",
                "size_bytes": len(patch_bytes),
            },
            {
                "path": "evidence/patch-result/%02d.json" % ordinal,
                "sha256": result_digest,
                "media_type": "application/json",
                "size_bytes": len(result_bytes),
            },
        ],
        "occurred_at": occurred_at,
        "sequence": previous.sequence + 1,
        "nonce": request.nonce,
        "previous_receipt_digest": previous.digest,
        "grant_id": developer.grant_id,
        "tool_name": "owp.apply_patch",
        "tool_version": "0.1",
        "request_arguments": arguments,
        "arguments_digest": request.arguments_digest,
        "output_digest": result_digest,
        "predicate_results": [item.model_dump(mode="json") for item in predicate_results],
    }
    receipt = ACTION_RECEIPT_ADAPTER.validate_python(
        sign_payload("action-receipt", raw, keys["Sidecar"][0])
    )
    evidence.complete_receipt_publication(
        case["ledger_path"],
        evidence_root=case["evidence_root"],
        receipt=receipt,
        payloads={
            receipt.evidence_refs[0].path: patch_bytes,
            receipt.evidence_refs[1].path: result_bytes,
        },
        clock=lambda: now,
        trusted_resolution_manifest=manifest,
    )
    checkpoint = _checkpoint_for(
        _candidate_files_from_git(case["workspace"], candidate_commit),
        candidate_commit,
    )
    if checkpoint.workspace_manifest_digest != executed.workspace_manifest_digest:
        raise FlowError("post-patch checkpoint is not the executor's own manifest")
    case["patch_receipt"] = receipt
    case["previous_receipt"] = receipt
    case["checkpoint"] = checkpoint
    case["patch_rounds"] += 1
    return receipt


def patch_parent_ids(case):
    """The protocol parent set for the executing receipt: the grant issuance that
    authorized it plus the latest repo-read on the same grant. Publication replays
    causality and demands exactly this set, which is why the F23/F25 cells are
    built as post-hoc transforms rather than as flows."""
    chosen = [case["developer_issuance"], case["repo_read_receipt"]]
    return tuple(item.receipt_id for item in sorted(chosen, key=lambda i: i.sequence))


# A second apply-patch round on one chain (cell `d18`) is not constructible
# through the live path at this commit, and the refusal is threefold:
#
#   1. publication demands the ledger tip be among the new receipt's parents
#      ("receipt publication candidate does not extend the authority tip",
#      evidence.py:1310);
#   2. causal replay demands the apply-patch parent set be exactly
#      {authorizing grant issuance, latest prior repo_read on that grant}, so
#      naming the tip instead fails ("receipt causal parents failed exact
#      historical replay", composition.py:667);
#   3. even with a satisfying parent set, causal replay refuses a second
#      allow/succeeded apply-patch outright ("a second active patch is not
#      allowed", composition.py:676) unless the first was rolled back through a
#      full needs_rework -> rollback -> retry episode.
#
# `d18` is therefore built as a post-hoc insertion (see `harness/build_fixtures.py`),
# the same shape `e21`/`f23`/`f25` already use, and its OWP-layer refusal is the
# registered expectation rather than something the harness engineers away.


def _through_proof_ready(upstream, case, keys, now, *, salt):
    """Steps 4-7, driven exactly as the upstream delivery suite drives them."""
    import openworkproof.acceptance as acceptance

    m2 = upstream["m2"]
    mcp = upstream["mcp"]
    recomposition = upstream["recomposition"]

    case["context"] = m2._refresh_context(case, case["checkpoint"], now)
    context = case["context"]
    request, arguments, facts = m2._verifier_run_tests_request(
        case, case["checkpoint"], keys, now
    )
    case["request"] = request
    case["arguments"] = arguments
    case["facts"] = facts
    mcp._execute_run_tests_case(
        case,
        case["ledger_path"].parent,
        keys,
        mcp._FakeRunTestsExecutionDriver(),
        context=context,
        request=request,
        request_arguments=arguments,
        execution_facts=facts,
        candidate_snapshot_request=mcp._run_tests_snapshot_request(
            case, case["ledger_path"].parent
        ),
        now=now,
    )
    locally_verified = mcp._current_run_tests_context(case, now)
    if locally_verified.current_state != "locally_verified":
        raise FlowError("local verification did not complete")

    first = acceptance.compose_proof_transaction(
        case["ledger_path"],
        evidence_root=case["evidence_root"],
        context=locally_verified,
        request=recomposition._signed_compose_request(
            case,
            locally_verified,
            keys,
            now,
            previous_report_digest=None,
            nonce_label="study014:first-compose:" + salt,
        ),
        sidecar_private_key=keys["Sidecar"][0],
        clock=lambda: now,
    )
    first_digest = acceptance.composition_report_digest(first.report)

    recomposition._execute_independent_run(
        case,
        keys,
        None,
        now,
        execution_context_id="a1" * 32,
        container_instance_id_digest="b1" * 32,
        nonce_label="study014:independent:" + salt,
    )
    refreshed = mcp._current_run_tests_context(case, now)
    second = acceptance.compose_proof_transaction(
        case["ledger_path"],
        evidence_root=case["evidence_root"],
        context=refreshed,
        request=recomposition._recompose_request(
            case,
            refreshed,
            keys,
            now,
            previous_report_digest=first_digest,
            nonce_label="study014:recompose:" + salt,
        ),
        sidecar_private_key=keys["Sidecar"][0],
        clock=lambda: now,
    )
    if second.report.verifier_conclusion != "proof_ready":
        raise FlowError("recomposition did not reach proof_ready")
    case["second_report"] = second
    return second


def _accept(upstream, case, keys, now, *, salt):
    """Steps 8-9: acceptance request, in-process Acceptor signature, commit."""
    import rfc8785
    import openworkproof.acceptance as acceptance
    from openworkproof.models import AcceptanceReceipt, AgentRequest, request_arguments_digest
    from openworkproof.signing import sign_payload

    mcp = upstream["mcp"]
    proof_ready = mcp._current_run_tests_context(case, now)
    scope = {
        "work_order_digest": case["work_order"].digest,
        "operation": "submit_final_acceptance",
        "composition_report_digest": acceptance.composition_report_digest(
            case["second_report"].report
        ),
    }
    target_action_digest = hashlib.sha256(
        rfc8785.dumps(
            {
                "domain": "openworkproof/final-acceptance-action/v0.1",
                "requested_scope": scope,
            }
        )
    ).hexdigest()
    arguments = {
        "request_kind": "final_acceptance",
        "target_action_digest": target_action_digest,
        "required_role": "Acceptor",
        "requested_scope": scope,
        "expires_at": ACCEPTANCE_EXPIRES_AT,
    }
    manager = keys["Manager"][1]
    acceptance.request_acceptance_transaction(
        case["ledger_path"],
        evidence_root=case["evidence_root"],
        context=proof_ready,
        request=AgentRequest.model_validate(
            sign_payload(
                "agent-request",
                {
                    "claim_type": "agent-request",
                    "work_order_digest": case["work_order"].digest,
                    "grant_id": case["root"].grant_id,
                    "actor_id": manager["subject_id"],
                    "actor_key_id": manager["key_id"],
                    "tool_name": "owp.request_acceptance",
                    "arguments_digest": request_arguments_digest(
                        "owp.request_acceptance", arguments
                    ),
                    "nonce": nonce(salt, "acceptance-request"),
                    "requested_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "authentication_method": "agent_signature",
                    "model_id": "model",
                    "model_version": "1",
                    "prompt_template_digest": "a" * 64,
                    "context_source_digest": "b" * 64,
                },
                keys["Manager"][0],
            )
        ),
        sidecar_private_key=keys["Sidecar"][0],
        expires_at=datetime(2026, 1, 1, 0, 30, 0, tzinfo=timezone.utc),
        clock=lambda: now,
    )
    awaiting = mcp._current_run_tests_context(case, now)
    draft = acceptance.prepare_acceptance(
        case["ledger_path"],
        evidence_root=case["evidence_root"],
        context=awaiting,
        clock=lambda: now,
    )
    signed = AcceptanceReceipt.model_validate(
        sign_payload(
            "acceptance-receipt",
            json.loads(draft.canonical_payload),
            keys["Acceptor"][0],
        )
    )
    acceptance.commit_acceptance(
        case["ledger_path"],
        evidence_root=case["evidence_root"],
        context=awaiting,
        acceptance=signed,
        public_keys=None,
        clock=lambda: now,
    )
    terminal = mcp._current_run_tests_context(case, now)
    if terminal.current_state != "accepted":
        raise FlowError("chain did not reach accepted")
    return signed


def export_bundle(upstream, case, acceptance_receipt):
    """The upstream evidence-bundle envelope, minus its narrative metadata."""
    import openworkproof.acceptance as acceptance
    from openworkproof.policy import CommittedEvidence
    from openworkproof.signing import decode_and_verify_key_binding

    work_order = case["work_order"]
    receipts, grants, attempts = upstream["chain"]._grant_replay_inputs(
        case["ledger_path"], work_order
    )
    connection = sqlite3.connect(case["ledger_path"])
    try:
        rows = connection.execute(
            "SELECT report_json FROM composition_reports ORDER BY source_state_version"
        ).fetchall()
    finally:
        connection.close()
    reports = tuple(
        acceptance.CompositionReport.model_validate_json(row[0]) for row in rows
    )
    committed = []
    for receipt in receipts:
        for reference in receipt.evidence_refs:
            payload = (
                case["evidence_root"] / reference.path.removeprefix("evidence/")
            ).read_bytes()
            committed.append(CommittedEvidence(reference=reference, payload=payload))
    committed.sort(key=lambda item: item.reference.path.encode())
    public_keys = {
        binding.key_id: decode_and_verify_key_binding(binding)
        for binding in work_order.key_bindings
    }
    acceptance.verify_acceptance_bundle(
        work_order=work_order,
        report=reports[-1],
        effective_grants=tuple(sorted(grants.values(), key=lambda i: i.grant_id)),
        grant_attempts=tuple(sorted(attempts.values(), key=lambda i: i.digest)),
        receipts=receipts,
        committed_evidence=tuple(committed),
        acceptance_receipt=acceptance_receipt,
        public_keys=public_keys,
        reports=reports,
    )
    return {
        "schema_version": "openworkproof/evidence-bundle/v0.1",
        "metadata": {
            "study": "judgment-pack Study 014",
            "protocol_version": "v0.1",
            "signature_algorithm": "Ed25519",
            "canonicalization": "RFC 8785 JCS",
            "digest_algorithm": "SHA-256",
        },
        "work_order": work_order.model_dump(mode="json"),
        "public_keys": {
            binding.key_id: {
                "role": binding.role,
                "subject_id": binding.subject_id,
                "key_id": binding.key_id,
                "public_key_b64url": binding.public_key_b64url,
            }
            for binding in work_order.key_bindings
        },
        "effective_grants": [
            grant.model_dump(mode="json")
            for grant in sorted(grants.values(), key=lambda i: i.grant_id)
        ],
        "grant_attempts": [
            attempt.model_dump(mode="json")
            for attempt in sorted(attempts.values(), key=lambda i: i.digest)
        ],
        "receipts": [receipt.model_dump(mode="json") for receipt in receipts],
        "composition_reports": [report.model_dump(mode="json") for report in reports],
        "acceptance_receipt": acceptance_receipt.model_dump(mode="json"),
        "committed_evidence": [
            {
                "reference": item.reference.model_dump(mode="json"),
                "payload_b64": base64.b64encode(item.payload).decode("ascii"),
                "payload_sha256": hashlib.sha256(item.payload).hexdigest(),
            }
            for item in committed
        ],
    }


def run_flow(tmp_path, *, objective, patch_bytes, target_paths,
             binding_digest=None, binding_point="apply_patch",
             patch_occurred_at=PATCH_OCCURRED_AT, work_order_updates=None,
             salt="baseline", owp_source=None):
    """Drive one complete chain and return its verified evidence bundle."""
    upstream = load_upstream(owp_source)
    placeholder = "b" * 64
    keys = role_keys()
    now = fixed_now()
    # Publication demands `occurred_at == clock()`, so a receipt that falls
    # outside its grant's window (E21) moves the clock for every step from the
    # executing call onward; steps 1-2 keep the fixture instant.
    late = datetime.strptime(patch_occurred_at, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )

    from openworkproof import repo_tools
    from openworkproof.repo_tools import CandidateExecutionSnapshot, ExecutionSnapshotPlan

    def _snapshot(request):
        return CandidateExecutionSnapshot(
            head_commit=request.expected_head_commit,
            workspace_manifest_digest=request.expected_workspace_manifest_digest,
            plan=ExecutionSnapshotPlan(
                files=(),
                read_only=True,
                owner_uid=65532,
                owner_gid=65532,
                atime_unix_seconds=0,
                mtime_unix_seconds=0,
                clear_extended_attributes=True,
                clear_posix_acls=True,
                clear_file_capabilities=True,
            ),
        )

    entropy = DeterministicEntropy(salt)
    with mock.patch("secrets.token_hex", entropy.token_hex), mock.patch.object(
        repo_tools, "prepare_candidate_execution_snapshot", _snapshot
    ):
        archive = source_archive(upstream)
        document = work_order_document(
            upstream, objective=objective, updates=work_order_updates, archive=archive
        )
        work_order = signed_work_order(upstream, document, keys)
        parsed = parsed_source(upstream, work_order, archive)
        case = _case(
            upstream,
            tmp_path,
            work_order,
            keys,
            now,
            salt=salt,
            parsed=parsed,
        )
        _repo_read(
            upstream,
            case,
            keys,
            now,
            salt=salt,
            context_source_digest=(
                binding_digest
                if binding_point == "repo_read" and binding_digest
                else placeholder
            ),
        )
        _publish_action_patch(
            upstream,
            case,
            keys,
            late,
            salt=salt,
            patch_bytes=patch_bytes,
            target_paths=target_paths,
            context_source_digest=(
                binding_digest
                if binding_point == "apply_patch" and binding_digest
                else placeholder
            ),
            occurred_at=patch_occurred_at,
            parents=patch_parent_ids(case),
        )
        _through_proof_ready(upstream, case, keys, late, salt=salt)
        acceptance_receipt = _accept(upstream, case, keys, late, salt=salt)
        bundle = export_bundle(upstream, case, acceptance_receipt)
    return bundle
