"""The three-layer verification ceremony — adapter/SPEC.md section 5.

Ordered, fail-closed, offline. Each layer runs and records independently so the
detection matrix can attribute; the combined verdict is pass iff every layer
passes. Inputs: one cell directory (the acceptance bundle plus the retained
artifact set) and the pinned `jpack` executable. Nothing else — no network, no
ledger, no state.

  Layer OWP     `openworkproof.acceptance.verify_acceptance_bundle`, unchanged,
                called as a library function with its inputs reconstructed from
                the bundle JSON and its public keys taken from the work order's
                own key bindings. Any exception is a layer failure with the
                message recorded (the upstream demo script's discarded booleans
                are why the library function is called directly).
  Layer BINDING adapter checks over the raw bundle JSON, first failure wins.
                Parses dicts rather than models so a bundle OWP would refuse is
                still adjudicated.
  Layer REPLAY  deterministic recomputation with the pinned binary under the
                commitment's own replay tuple, including its supported-extension
                set and its evaluator spec version.

Every layer returns the same structured record — `{"verdict", "code", "detail"}`
— and `outcome()` is the only string anything adjudicates on. `detail` is for
humans and never enters a comparison: that is what keeps a decorated runtime
string (`replay-refused: pack-not-conformant`) from becoming an unregistered
verdict. The registered vocabulary is the `{verdict, code}` **pair** table
(`LAYER_VERDICT_CODES`), checked before any normalization: an unknown verdict
carrying a known code, or a bare `unavailable` with no code, is reported as an
out-of-vocabulary outcome and lands on the scorer's validity channel rather
than being rounded into a registered failure.

The commitment REPLAY and BINDING work from is the one at the signed
authorization-time binding point (`WorkOrder.objective`); a chain that carries no
commitment there has nothing to replay, which is why M28 and E19 report
`unavailable` rather than a disposition comparison.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from commitment import (  # noqa: E402
    ACTION_TOOL,
    CommitmentSchemaError,
    authorized_action,
    canonical_encoding_problem,
    commitment_bytes,
    commitment_digest,
    disposition_digest,
    envelope_disposition,
    parse_commitment_bytes,
    sha256_prefixed,
    validate_commitment,
)

CELL_FILES = (
    "bundle.json",
    "commitment.json",
    "pack.json",
    "facts.json",
    "evidence.json",
    "evaluation.json",
)
MANIFEST_NAME = "MANIFEST.sha256"

BINDING_CODES = (
    "commitment-objective-missing",
    "commitment-schema-invalid",
    "binding-point-divergence",
    "executing-receipt-missing",
    "pack-artifact-missing",
    "pack-digest-mismatch",
    "facts-artifact-missing",
    "facts-digest-mismatch",
    "evidence-artifact-missing",
    "evidence-digest-mismatch",
    "disposition-digest-mismatch-retained",
    "action-tool-mismatch",
    "action-arguments-mismatch",
    "action-map-violation",
)
REPLAY_CODES = (
    "replay-unavailable",
    "replay-executable-mismatch",
    "replay-refused",
    "replay-spec-version-mismatch",
    "replay-disposition-mismatch",
)

# The tools whose receipts are *executions* under the study's SPEC section 4 map.
# `owp.create_pr_proposal` is deliberately outside it: the map never authorizes
# it, so a chain carrying one is not carrying an execution of a judged action.
ACTION_CLASS_TOOLS = (ACTION_TOOL,)

# The registered `{verdict, code}` PAIRS, per layer. Round 2 found that an
# unknown verdict paired with a known code was being normalized into a
# registered `fail:<code>` outcome, and that `pass`/`unavailable` swallowed
# arbitrary codes — so a bare `unavailable` was indistinguishable from the
# registered (`unavailable`, `replay-unavailable`) pair. The pair, not the
# verdict and not the code alone, is what the vocabulary registers.
#
# On the OWP layer upstream reports bundle-level failure as one composite
# verdict, so its only registered code is `None`. On the replay layer
# `replay-unavailable` is the code of the `unavailable` verdict and of nothing
# else: it is deliberately absent from the `fail` pairs.
LAYER_VERDICT_CODES = {
    "owp": (("pass", None), ("fail", None), ("unavailable", None)),
    "binding": (("pass", None),) + tuple(("fail", code) for code in BINDING_CODES),
    "replay": (("pass", None), ("unavailable", "replay-unavailable"))
    + tuple(
        ("fail", code) for code in REPLAY_CODES if code != "replay-unavailable"
    ),
}
REGISTERED_PAIRS = frozenset(
    pair for pairs in LAYER_VERDICT_CODES.values() for pair in pairs
)

# The prefix an unregistered pair is reported under. It is deliberately outside
# every layer's outcome vocabulary, so the scorer's validity channel refuses it
# instead of the detection channel counting it.
UNREGISTERED_PREFIX = "unregistered"


def result(verdict, code=None, detail=None):
    """The one shape every layer returns."""
    return {"verdict": verdict, "code": code, "detail": detail}


def pair_problem(layer, layer_result):
    """None when `(verdict, code)` is registered for `layer`, else why not."""
    pairs = LAYER_VERDICT_CODES.get(layer)
    if pairs is None:
        return "layer %r is not a registered layer" % (layer,)
    pair = (layer_result.get("verdict"), layer_result.get("code"))
    if pair in pairs:
        return None
    return (
        "layer %s returned the unregistered verdict/code pair (%r, %r)"
        % (layer, pair[0], pair[1])
    )


def outcome(layer_result, layer=None):
    """The adjudicated string for a layer record — code only, never detail.

    An unregistered pair is *not* normalized: it becomes an out-of-vocabulary
    string that the scorer refuses on the validity channel. Nothing outside the
    registered pair table can be laundered into a registered outcome. With
    `layer` the check is that layer's own table (which is what the ceremony
    uses, and what makes a bare replay `unavailable` unregistered); without it,
    the union — the weakest form, for callers that only hold a record.
    """
    verdict = layer_result.get("verdict")
    code = layer_result.get("code")
    registered = LAYER_VERDICT_CODES.get(layer, REGISTERED_PAIRS) if layer else (
        REGISTERED_PAIRS
    )
    if (verdict, code) not in registered:
        return "%s:%s/%s" % (UNREGISTERED_PREFIX, verdict, code)
    if verdict in ("pass", "unavailable"):
        return verdict
    return "fail" if code is None else "fail:" + code


# --------------------------------------------------------------------------
# cell plumbing
# --------------------------------------------------------------------------

def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def installed_package_root(name="openworkproof"):
    """The installed distribution's package directory, resolved from metadata.

    Deliberately **not** `importlib.util.find_spec`: that resolves through
    `sys.path`, so a directory prepended to it could answer for the very package
    the caller is trying to authenticate. The installed distribution's own
    metadata is independent of `sys.path` order, which is what makes this usable
    as the reference point for "did we import the installed package?".
    """
    import importlib.metadata

    distribution = importlib.metadata.distribution(name)
    root = Path(distribution.locate_file(name)).resolve()
    if not root.is_dir():
        raise RuntimeError("the installed %s package directory is not readable" % name)
    return root


def installed_package_digest(name="openworkproof", root=None):
    """A deterministic digest over the *installed* package's own source files.

    Round 2's blocker: every OWP pin was either a mutable local-file URL (the
    `pip freeze` line) or an unverified declaration (the commit string), so the
    package the verification path actually imports was never checked. This walks
    the installed package directory — resolved through `importlib` unless the
    caller supplies one — sorts by package-relative path, and hashes
    `path \\0 bytes \\0` for every file that is not a `__pycache__` artefact, so a
    byte edit anywhere inside the installed package, including a schema JSON,
    changes the value.

    One implementation, two callers: the scorer enforces it as a freeze pin
    before it adjudicates, and the builder re-verifies it after it imports the
    pinned clone's helpers (round 4). Two implementations could drift, and the
    pin is only worth what the weaker of them checks.
    """
    import importlib.util

    if root is None:
        spec = importlib.util.find_spec(name)
        if spec is None or not spec.origin:
            raise RuntimeError("the %s package is not importable" % name)
        root = Path(spec.origin).resolve().parent
    root = Path(root)
    if not root.is_dir():
        raise RuntimeError("the %s package directory is not readable" % name)
    relatives = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    digest = hashlib.sha256()
    for relative in relatives:
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update((root / relative).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def manifest_text(directory):
    """`sha256  name` for every cell file present, sorted by name."""
    directory = Path(directory)
    lines = []
    for name in sorted(CELL_FILES):
        path = directory / name
        if path.is_file():
            lines.append("%s  %s" % (sha256_file(path), name))
    return "\n".join(lines) + "\n"


def manifest_problems(directory):
    """Manifest integrity: listed files present and matching, no unlisted files."""
    directory = Path(directory)
    manifest = directory / MANIFEST_NAME
    if not manifest.is_file():
        return ["manifest is absent"]
    problems = []
    listed = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, name = line.partition("  ")
        listed[name] = digest
    for name, digest in sorted(listed.items()):
        path = directory / name
        if not path.is_file():
            problems.append("listed file is absent: " + name)
        elif sha256_file(path) != digest:
            problems.append("listed file does not match its digest: " + name)
    for name in sorted(CELL_FILES):
        if (directory / name).is_file() and name not in listed:
            problems.append("present file is not listed: " + name)
    return problems


class Cell:
    """One frozen cell directory. Absent artifacts read as None, never as an error."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self.name = self.directory.name

    def read(self, name):
        path = self.directory / name
        return path.read_bytes() if path.is_file() else None

    def json(self, name):
        payload = self.read(name)
        if payload is None:
            return None
        try:
            return json.loads(payload.decode("utf-8"))
        except Exception:
            return None


def jpack_digest(jpack_bin):
    return "sha256:" + sha256_file(jpack_bin)


def jpack_release(jpack_bin):
    """The evaluator's reported release, or None when it cannot be asked."""
    try:
        completed = subprocess.run(
            [str(jpack_bin), "--version"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception:
        return None
    parts = completed.stdout.strip().split()
    return parts[-1] if parts else None


def evaluate(jpack_bin, work_dir, pack_bytes, facts_bytes, evidence_bytes,
             supported_extensions=()):
    """Run the pinned evaluator over retained bytes; return (envelope bytes, exit).

    The committed supported-extension set is part of the Core section 8.2 input
    tuple, so it is passed through as `--supported-extension` (repeatable) rather
    than committed and ignored.
    """
    work_dir = Path(work_dir)
    pack_path = work_dir / "pack.json"
    facts_path = work_dir / "facts.json"
    pack_path.write_bytes(pack_bytes)
    facts_path.write_bytes(facts_bytes)
    command = [
        str(jpack_bin),
        "experimental",
        "evaluate",
        str(pack_path),
        "--facts",
        str(facts_path),
        "--format",
        "json",
    ]
    if evidence_bytes is not None:
        evidence_path = work_dir / "evidence.json"
        evidence_path.write_bytes(evidence_bytes)
        command.extend(["--evidence", str(evidence_path)])
    for extension in supported_extensions or ():
        command.extend(["--supported-extension", str(extension)])
    completed = subprocess.run(command, capture_output=True, timeout=300)
    return completed.stdout, completed.returncode


# --------------------------------------------------------------------------
# Layer OWP
# --------------------------------------------------------------------------

def layer_owp(cell):
    bundle = cell.json("bundle.json")
    if bundle is None:
        return result("unavailable", None, "bundle is unreadable")
    try:
        import base64

        import openworkproof.acceptance as acceptance
        from openworkproof.models import (
            ACTION_RECEIPT_ADAPTER,
            AcceptanceReceipt,
            CapabilityGrant,
            CompositionReport,
            EvidenceRef,
            WorkOrder,
        )
        from openworkproof.policy import CommittedEvidence
        from openworkproof.signing import decode_and_verify_key_binding

        work_order = WorkOrder.model_validate(bundle["work_order"])
        public_keys = {
            binding.key_id: decode_and_verify_key_binding(binding)
            for binding in work_order.key_bindings
        }
        grants = tuple(
            CapabilityGrant.model_validate(item)
            for item in sorted(bundle["effective_grants"], key=lambda i: i["grant_id"])
        )
        attempts = tuple(
            CapabilityGrant.model_validate(item)
            for item in sorted(bundle["grant_attempts"], key=lambda i: i["digest"])
        )
        receipts = tuple(
            ACTION_RECEIPT_ADAPTER.validate_python(item) for item in bundle["receipts"]
        )
        reports = tuple(
            CompositionReport.model_validate(item)
            for item in bundle["composition_reports"]
        )
        acceptance_receipt = AcceptanceReceipt.model_validate(
            bundle["acceptance_receipt"]
        )
        committed = tuple(
            CommittedEvidence(
                reference=EvidenceRef.model_validate(item["reference"]),
                payload=base64.b64decode(item["payload_b64"]),
            )
            for item in bundle["committed_evidence"]
        )
        acceptance.verify_acceptance_bundle(
            work_order=work_order,
            report=reports[-1],
            effective_grants=grants,
            grant_attempts=attempts,
            receipts=receipts,
            committed_evidence=committed,
            acceptance_receipt=acceptance_receipt,
            public_keys=public_keys,
            reports=reports,
        )
    except Exception as error:
        # Upstream reports bundle-level failure as one composite verdict, so the
        # OWP layer carries no code of its own: its outcome is `fail` and the
        # upstream message is recorded as detail.
        return result("fail", None, "%s: %s" % (type(error).__name__, error))
    return result("pass")


# --------------------------------------------------------------------------
# Layer BINDING
# --------------------------------------------------------------------------

def _fail(code, detail=None):
    return result("fail", code, detail)


def _objective_text(cell):
    bundle = cell.json("bundle.json")
    if not isinstance(bundle, dict):
        return None, None
    objective = (bundle.get("work_order") or {}).get("objective")
    return bundle, objective if isinstance(objective, str) else None


def _looks_like_a_commitment(raw):
    """True when the bytes decode to a version-1 commitment under lax parsing.

    The distinction the codes turn on: a chain that carries no commitment at the
    signed point at all (`commitment-objective-missing`) versus one that carries
    a version-1 commitment the strict rules refuse — duplicate members, invalid
    UTF-8, a non-canonical encoding (`commitment-schema-invalid`).
    """
    try:
        candidate = json.loads(bytes(raw).decode("utf-8", errors="strict"))
    except Exception:
        return False
    return isinstance(candidate, dict) and candidate.get("commitmentVersion") == "1"


def commitment_at_binding_point(cell):
    """The commitment carried by `WorkOrder.objective`, or None."""
    _, objective = _objective_text(cell)
    if objective is None:
        return None
    raw = objective.encode("utf-8")
    try:
        candidate = parse_commitment_bytes(raw)
        validate_commitment(candidate)
        if canonical_encoding_problem(raw, candidate) is not None:
            return None
    except CommitmentSchemaError:
        return None
    return candidate


def _commitment_from_objective(cell):
    """(candidate, canonical bytes) or a failing layer record."""
    bundle, objective = _objective_text(cell)
    if bundle is None:
        return _fail("commitment-objective-missing", "bundle is unreadable")
    if objective is None:
        return _fail("commitment-objective-missing", "objective is not a string")
    raw = objective.encode("utf-8")
    try:
        candidate = parse_commitment_bytes(raw)
    except CommitmentSchemaError as error:
        if _looks_like_a_commitment(raw):
            return _fail("commitment-schema-invalid", str(error))
        return _fail("commitment-objective-missing", str(error))
    try:
        validate_commitment(candidate)
        problem = canonical_encoding_problem(raw, candidate)
        if problem is not None:
            return _fail("commitment-schema-invalid", problem)
        canonical = commitment_bytes(candidate)
    except CommitmentSchemaError as error:
        return _fail("commitment-schema-invalid", str(error))
    return candidate, canonical


def _retained_commitment_problem(cell, candidate, canonical):
    """The byte-level retained-vs-signed rule (SPEC section 5)."""
    retained = cell.read("commitment.json")
    if retained is None:
        return _fail(
            "binding-point-divergence",
            "retained commitment document is absent",
        )
    if retained == canonical:
        return None
    try:
        parsed = parse_commitment_bytes(retained)
    except CommitmentSchemaError as error:
        return _fail("commitment-schema-invalid", "retained commitment: " + str(error))
    if parsed == candidate:
        return _fail(
            "commitment-schema-invalid",
            "retained commitment bytes are not the canonical JCS encoding",
        )
    return _fail(
        "binding-point-divergence",
        "retained commitment document is not the objective commitment",
    )


def _tool_call_receipts(bundle):
    return [
        receipt
        for receipt in bundle.get("receipts", [])
        if isinstance(receipt, dict) and receipt.get("event_type") == "tool_call"
    ]


def action_class_receipts(bundle):
    """Structural discovery: every receipt that *is* an execution under the map.

    Discovery is by tool, never by the attacker-controlled marker — a negative
    disposition cannot execute by simply omitting the commitment digest from its
    request context.
    """
    return [
        receipt
        for receipt in _tool_call_receipts(bundle)
        if receipt.get("tool_name") in ACTION_CLASS_TOOLS
    ]


def marked_receipts(bundle, digest):
    """Receipts whose nested request carries the commitment digest."""
    return [
        receipt
        for receipt in _tool_call_receipts(bundle)
        if isinstance(receipt.get("nested_claim"), dict)
        and receipt["nested_claim"].get("context_source_digest") == digest
    ]


def layer_binding(cell):
    parsed = _commitment_from_objective(cell)
    if isinstance(parsed, dict) and "verdict" in parsed:
        return parsed
    candidate, canonical = parsed
    bundle = cell.json("bundle.json")

    problem = _retained_commitment_problem(cell, candidate, canonical)
    if problem is not None:
        return problem

    try:
        digest = commitment_digest(candidate)
    except CommitmentSchemaError as error:
        return _fail("commitment-schema-invalid", str(error))
    judgment = candidate["judgment"]
    action = candidate["action"]

    executions = action_class_receipts(bundle)
    marked = marked_receipts(bundle, digest)

    # Exact-set totality over the action class (SPEC section 5).
    if action is None:
        if executions:
            return _fail(
                "action-map-violation",
                "commitment authorizes no action yet the chain carries %d "
                "action-class receipt(s)" % len(executions),
            )
        if marked:
            return _fail(
                "action-map-violation",
                "commitment authorizes no action yet a receipt carries its digest",
            )
        executing = None
    else:
        # A marked receipt is what the chain *claims* is the executing call. If
        # the claim names a tool the map cannot authorize, that is the binding
        # failure, whether or not an action-class receipt also exists.
        mismarked = [
            receipt
            for receipt in marked
            if receipt.get("tool_name") != action["toolName"]
        ]
        if mismarked:
            return _fail(
                "action-tool-mismatch",
                "the commitment digest is bound to a %r receipt, not the "
                "committed %r" % (mismarked[0].get("tool_name"), action["toolName"]),
            )
        if not executions:
            return _fail(
                "executing-receipt-missing",
                "commitment authorizes an action yet the chain carries no "
                "action-class receipt",
            )
        if len(executions) > 1:
            return _fail(
                "action-map-violation",
                "commitment authorizes one action yet the chain carries %d "
                "action-class receipts" % len(executions),
            )
        executing = executions[0]
        if not marked:
            return _fail(
                "binding-point-divergence",
                "the executing request does not carry the commitment digest",
            )
        if executing.get("correlation_factors", {}).get("context_source_digest") != digest:
            return _fail(
                "binding-point-divergence",
                "receipt correlation factors do not mirror the request binding",
            )

    pack_bytes = cell.read("pack.json")
    if pack_bytes is None:
        return _fail("pack-artifact-missing", "retained pack bytes are absent")
    if sha256_prefixed(pack_bytes) != judgment["packDigest"]:
        return _fail("pack-digest-mismatch", "retained pack bytes are not the committed pack")
    pack = cell.json("pack.json")
    if not isinstance(pack, dict) or (
        pack.get("id") != judgment["packId"]
        or pack.get("version") != judgment["packVersion"]
        or pack.get("specVersion") != judgment["specVersion"]
    ):
        return _fail("pack-digest-mismatch", "retained pack identity is not the committed one")

    facts_bytes = cell.read("facts.json")
    if facts_bytes is None:
        return _fail("facts-artifact-missing", "retained facts bytes are absent")
    if sha256_prefixed(facts_bytes) != judgment["factsDigest"]:
        return _fail("facts-digest-mismatch", "retained facts bytes are not the committed facts")

    evidence_bytes = cell.read("evidence.json")
    committed_evidence_digest = judgment["evidenceDigest"]
    if committed_evidence_digest is None:
        if evidence_bytes is not None:
            return _fail(
                "evidence-digest-mismatch",
                "commitment declares no evidence document yet one is retained",
            )
    elif evidence_bytes is None:
        return _fail("evidence-artifact-missing", "retained evidence bytes are absent")
    elif sha256_prefixed(evidence_bytes) != committed_evidence_digest:
        return _fail(
            "evidence-digest-mismatch",
            "retained evidence bytes are not the committed evidence",
        )

    envelope = cell.json("evaluation.json")
    if not isinstance(envelope, dict):
        return _fail(
            "disposition-digest-mismatch-retained",
            "retained evaluator envelope is unreadable",
        )
    try:
        retained_disposition_digest = disposition_digest(envelope)
    except CommitmentSchemaError as error:
        return _fail("disposition-digest-mismatch-retained", str(error))
    if retained_disposition_digest != judgment["dispositionDigest"]:
        return _fail(
            "disposition-digest-mismatch-retained",
            "retained disposition is not the committed disposition",
        )

    if action is not None:
        if executing.get("arguments_digest") != action["argumentsDigest"]:
            return _fail(
                "action-arguments-mismatch",
                "executed arguments are not the committed arguments",
            )
        facts = json.loads(facts_bytes.decode("utf-8"))
        derived = authorized_action(envelope_disposition(envelope), facts)
        if derived != action:
            return _fail(
                "action-map-violation",
                "the section 4 map does not authorize the executed action",
            )
    return result("pass")


# --------------------------------------------------------------------------
# Layer REPLAY
# --------------------------------------------------------------------------

def _unavailable(detail):
    return result("unavailable", "replay-unavailable", detail)


def layer_replay(cell, jpack_bin, work_dir):
    candidate = commitment_at_binding_point(cell)
    if candidate is None:
        return _unavailable("no conforming commitment at the signed binding point")
    judgment = candidate["judgment"]

    if jpack_bin is None or not Path(jpack_bin).is_file():
        return _unavailable("the pinned evaluator is not available")
    if jpack_digest(jpack_bin) != judgment["executableDigest"]:
        return _fail(
            "replay-executable-mismatch",
            "executable digest is not the recorded one",
        )
    release = jpack_release(jpack_bin)
    if release != judgment["evaluatorRelease"]:
        return _fail(
            "replay-executable-mismatch",
            "evaluator release %r is not the recorded %r"
            % (release, judgment["evaluatorRelease"]),
        )

    pack_bytes = cell.read("pack.json")
    facts_bytes = cell.read("facts.json")
    evidence_bytes = cell.read("evidence.json")
    if pack_bytes is None or facts_bytes is None:
        return _unavailable("retained pack or facts bytes are absent")
    if judgment["evidenceDigest"] is not None and evidence_bytes is None:
        return _unavailable("retained evidence bytes are absent")
    if judgment["evidenceDigest"] is None:
        evidence_bytes = None

    stdout, returncode = evaluate(
        jpack_bin,
        work_dir,
        pack_bytes,
        facts_bytes,
        evidence_bytes,
        supported_extensions=judgment["supportedExtensions"],
    )
    try:
        envelope = json.loads(stdout.decode("utf-8"))
    except Exception:
        return _fail(
            "replay-refused",
            "unreadable: the evaluator produced no readable envelope (exit %d)"
            % returncode,
        )
    error = envelope.get("evaluationError")
    if error is not None or "disposition" not in envelope:
        error_class = (error or {}).get("class", "unclassified")
        return _fail(
            "replay-refused",
            "%s: the evaluator refused the retained inputs" % error_class,
        )
    replayed_spec_version = envelope.get("evaluatorSpecVersion")
    if replayed_spec_version != judgment["evaluatorSpecVersion"]:
        return _fail(
            "replay-spec-version-mismatch",
            "replayed evaluatorSpecVersion %r is not the committed %r"
            % (replayed_spec_version, judgment["evaluatorSpecVersion"]),
        )
    if disposition_digest(envelope) != judgment["dispositionDigest"]:
        return _fail(
            "replay-disposition-mismatch",
            "recomputed disposition is not the committed disposition",
        )
    return result("pass")


# --------------------------------------------------------------------------
# the ceremony
# --------------------------------------------------------------------------

def verify_cell(cell_dir, jpack_bin, work_dir):
    """Run the three layers independently and derive the combined verdict."""
    cell = Cell(cell_dir)
    layers = {
        "owp": layer_owp(cell),
        "binding": layer_binding(cell),
        "replay": layer_replay(cell, jpack_bin, work_dir),
    }
    outcomes = {name: outcome(record, name) for name, record in layers.items()}
    combined = "pass" if all(value == "pass" for value in outcomes.values()) else "fail"
    return {
        "cell": cell.name,
        "owp": dict(layers["owp"], outcome=outcomes["owp"]),
        "binding": dict(layers["binding"], outcome=outcomes["binding"]),
        "replay": dict(layers["replay"], outcome=outcomes["replay"]),
        "combined": combined,
    }
