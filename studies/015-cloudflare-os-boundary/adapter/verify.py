"""The verification ceremony — three layers over one cell's retained bytes.

Implements adapter/SPEC.md section 5. Inputs per cell: the retained artifact set and, for
the `cf` layer, the verdict the node probe runner computed from the same retained bytes
(`harness/cf_runner.py`); for the `replay` layer, the pinned `jpack` executable. Nothing
else — no network, no matrix, no expectations: a layer never knows what it is registered
to say.
"""

import hashlib
import json
import subprocess
from pathlib import Path

import commitment as cmt

CELL_FILES = (
    "pack.json",
    "facts.json",
    "evidence.json",
    "evaluation.json",
    "commitment.json",
    "ledger.json",
    "platform.json",
    "report.json",
)
MANIFEST_NAME = "MANIFEST.sha256"

CF_CODES = (
    "classification-refused",
    "drain-order-violation",
)
BINDING_CODES = (
    "commitment-missing",
    "commitment-schema-invalid",
    "pack-artifact-missing",
    "pack-digest-mismatch",
    "facts-digest-mismatch",
    "evidence-digest-mismatch",
    "disposition-digest-mismatch-retained",
    "evidence-backing-invalid",
    "action-map-violation",
    "binding-reuse",
    "target-mismatch",
    "argument-drift",
    "revision-drift",
    "simulation-basis-invalid",
    "unbound-execution",
    "handoff-dropped",
    "commit-overclaim",
    "report-misattribution",
)
REPLAY_CODES = (
    "replay-unavailable",
    "replay-executable-mismatch",
    "replay-refused",
    "replay-spec-version-mismatch",
    "replay-disposition-mismatch",
)

EXECUTION_STATES = ("none", "staged", "applied", "applied-unproven", "effect-attested")


def result(verdict, code=None, detail=None):
    """The one shape every layer returns."""
    return {"verdict": verdict, "code": code, "detail": detail}


def outcome(layer_result):
    """The adjudicated string for a layer record — code only, never detail."""
    verdict = layer_result["verdict"]
    if verdict in ("pass", "unavailable"):
        return verdict
    code = layer_result.get("code")
    return "fail" if code is None else "fail:" + code


def _fail(code, detail=None):
    return result("fail", code, detail)


# --------------------------------------------------------------------------
# retained bytes
# --------------------------------------------------------------------------

def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Cell:
    """Lazy access to one cell directory's retained bytes."""

    def __init__(self, directory):
        self.directory = Path(directory)

    def path(self, name):
        return self.directory / name

    def bytes(self, name):
        path = self.path(name)
        if not path.is_file():
            return None
        return path.read_bytes()

    def json(self, name):
        raw = self.bytes(name)
        if raw is None:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return None


def manifest_problems(directory):
    """The cell's own MANIFEST.sha256, verified as an exact set."""
    directory = Path(directory)
    manifest_path = directory / MANIFEST_NAME
    if not manifest_path.is_file():
        return ["cell manifest is absent"]
    problems = []
    listed = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            digest, name = line.split(None, 1)
        except ValueError:
            problems.append("manifest line is malformed: " + line)
            continue
        listed[name.strip()] = digest
    present = {
        path.name
        for path in directory.iterdir()
        if path.is_file() and path.name != MANIFEST_NAME
    }
    for name in sorted(listed):
        if name not in present:
            problems.append("manifested artifact is absent: " + name)
        elif sha256_file(directory / name) != listed[name]:
            problems.append("artifact does not match its manifest digest: " + name)
    for name in sorted(present - set(listed)):
        problems.append("unmanifested artifact is present: " + name)
    return problems


# --------------------------------------------------------------------------
# layer cf
# --------------------------------------------------------------------------

def layer_cf(cell_id, cf_verdicts):
    """The node runner's verdict for this cell, vocabulary-checked."""
    if cf_verdicts is None:
        return result("unavailable", None, "no cf runner output is available")
    record = (cf_verdicts.get("cells") or {}).get(cell_id)
    if record is None:
        return result("unavailable", None, "cf runner reported nothing for this cell")
    verdict = record.get("verdict")
    if verdict == "pass":
        return result("pass", None, None)
    if verdict == "unavailable":
        return result("unavailable", None, record.get("detail"))
    if verdict == "fail" and record.get("code") in CF_CODES:
        return result("fail", record["code"], record.get("detail"))
    return result(
        "fail", None, "cf runner returned an out-of-vocabulary record: %r" % (record,)
    )


def cf_engagement(cell_id, cf_verdicts):
    """The runner-reported engaged-check list (registry metadata, validity-checked)."""
    if cf_verdicts is None:
        return None
    record = (cf_verdicts.get("cells") or {}).get(cell_id)
    if record is None:
        return None
    return record.get("engaged")


# --------------------------------------------------------------------------
# layer binding
# --------------------------------------------------------------------------

def _bound_staged_calls(platform, digest):
    return [
        call
        for call in platform.get("stagedCalls") or []
        if call.get("commitmentDigest") == digest
    ]


def _ledger_actions(ledger):
    return [entry for entry in ledger if entry.get("type") == "action"]


def _record_for_call(ledger, call):
    for entry in _ledger_actions(ledger):
        if (
            entry.get("gatekeeperId") == call.get("gatekeeperId")
            and entry.get("action") == call.get("action")
        ):
            return entry
    return None


def _canonical_effect_digest(facts):
    return cmt.arguments_digest(cmt.action_arguments(facts))


def _matching_effects(platform, facts):
    """Effects attested against the judged subject (SPEC section 5, step 13)."""
    matches = []
    for effect in platform.get("effects") or []:
        if effect.get("toolName") != cmt.ACTION_TOOL:
            continue
        if effect.get("resourceUrl") != cmt.RESOURCE_URL:
            continue
        digest = cmt.arguments_digest(effect.get("arguments"))
        if digest == _canonical_effect_digest(facts):
            matches.append(effect)
    return matches


def layer_binding(cell):
    raw = cell.bytes("commitment.json")
    if raw is None:
        return _fail("commitment-missing", "no commitment.json is retained")
    try:
        candidate = cmt.parse_commitment_bytes(raw)
        problem = cmt.canonical_encoding_problem(raw, candidate)
        if problem:
            return _fail("commitment-schema-invalid", problem)
        cmt.validate_commitment(candidate)
    except cmt.CommitmentSchemaError as error:
        return _fail("commitment-schema-invalid", str(error))
    judgment = candidate["judgment"]
    action = candidate["action"]
    digest = cmt.commitment_digest(candidate)

    pack_bytes = cell.bytes("pack.json")
    if pack_bytes is None:
        return _fail("pack-artifact-missing", "no pack.json is retained")
    if cmt.sha256_prefixed(pack_bytes) != judgment["packDigest"]:
        return _fail(
            "pack-digest-mismatch",
            "retained pack bytes do not match the committed digest",
        )

    facts_bytes = cell.bytes("facts.json")
    if facts_bytes is None or cmt.sha256_prefixed(facts_bytes) != judgment["factsDigest"]:
        return _fail(
            "facts-digest-mismatch",
            "retained facts bytes are absent or do not match the committed digest",
        )
    evidence_bytes = cell.bytes("evidence.json")
    if judgment["evidenceDigest"] is None:
        if evidence_bytes is not None:
            return _fail(
                "evidence-digest-mismatch",
                "commitment declares no evidence document but one is retained",
            )
    else:
        if evidence_bytes is None or cmt.sha256_prefixed(evidence_bytes) != judgment[
            "evidenceDigest"
        ]:
            return _fail(
                "evidence-digest-mismatch",
                "retained evidence bytes are absent or do not match the committed digest",
            )

    envelope = cell.json("evaluation.json")
    if envelope is None:
        return _fail(
            "disposition-digest-mismatch-retained",
            "no readable evaluator envelope is retained",
        )
    try:
        retained_digest = cmt.disposition_digest(envelope)
    except cmt.CommitmentSchemaError as error:
        return _fail("disposition-digest-mismatch-retained", str(error))
    if retained_digest != judgment["dispositionDigest"]:
        return _fail(
            "disposition-digest-mismatch-retained",
            "the retained envelope's canonical disposition does not match the commitment",
        )
    disposition = cmt.envelope_disposition(envelope)

    evidence = json.loads(evidence_bytes.decode("utf-8")) if evidence_bytes else {}
    backing = judgment["evidenceBacking"]
    for requirement, availability in sorted(evidence.items()):
        if availability == "present" and requirement not in backing:
            return _fail(
                "evidence-backing-invalid",
                "present claim has no backing entry: " + requirement,
            )
    for requirement in sorted(backing):
        if evidence.get(requirement) != "present":
            return _fail(
                "evidence-backing-invalid",
                "backing entry for a claim that is not present: " + requirement,
            )
        entry = backing[requirement]
        if entry.get("kind") != "artifact":
            return _fail(
                "evidence-backing-invalid",
                "backing for %s is a %r reference, not a captured-artifact digest — "
                "resource access and human approval are not evidence"
                % (requirement, entry.get("kind")),
            )
        digest_value = entry.get("digest")
        if set(entry) != {"kind", "digest"} or not isinstance(digest_value, str) or not (
            digest_value.startswith("sha256:") and len(digest_value) == 71
        ):
            return _fail(
                "evidence-backing-invalid",
                "backing for %s carries no artifact digest" % requirement,
            )

    ledger = cell.json("ledger.json")
    platform = cell.json("platform.json")
    if not isinstance(ledger, list) or not isinstance(platform, dict):
        return _fail(
            "action-map-violation",
            "retained ledger or platform store is unreadable",
        )
    bound_calls = _bound_staged_calls(platform, digest)
    executable = cmt.executable(disposition)

    if action is not None and not executable:
        return _fail(
            "action-map-violation",
            "the commitment carries an action object under a non-executable disposition",
        )
    if action is None and executable:
        return _fail(
            "action-map-violation",
            "the commitment carries no action under an executable disposition",
        )
    if action is None and bound_calls:
        return _fail(
            "action-map-violation",
            "a staged call binds a commitment to inaction",
        )
    if action is not None and bound_calls:
        matched_effects = _matching_effects(platform, json.loads(facts_bytes))
        for call in bound_calls:
            record = _record_for_call(ledger, call)
            if matched_effects and (record is None or record.get("state") != "approved"):
                return _fail(
                    "action-map-violation",
                    "the bound staged call took effect with no approved ledger record",
                )

    applied_bound = []
    for call in bound_calls:
        record = _record_for_call(ledger, call)
        if record is not None and record.get("state") == "approved":
            applied_bound.append((call, record))
    if len(bound_calls) > 1 or len(applied_bound) > 1:
        return _fail(
            "binding-reuse",
            "%d staged calls / %d applied records bind one commitment digest"
            % (len(bound_calls), len(applied_bound)),
        )

    if action is not None and bound_calls:
        call = bound_calls[0]
        record = _record_for_call(ledger, call)
        gatekeeper = next(
            (
                g
                for g in platform.get("gatekeepers") or []
                if g.get("id") == call.get("gatekeeperId")
            ),
            None,
        )
        record_tag = None
        if record is not None:
            record_tag = ((record.get("description") or {}).get("actionKind") or {}).get(
                "tag"
            )
        mismatches = []
        if call.get("gatekeeperId") != action["gatekeeperId"]:
            mismatches.append("gatekeeperId")
        if gatekeeper is None or gatekeeper.get("resourceUrl") != action["resourceUrl"]:
            mismatches.append("resourceUrl")
        if gatekeeper is None or gatekeeper.get("serverTrust") != action["serverTrust"]:
            mismatches.append("serverTrust")
        if call.get("toolName") != action["toolName"]:
            mismatches.append("toolName")
        if record is not None and record_tag != action["actionKindTag"]:
            mismatches.append("actionKindTag")
        if mismatches:
            return _fail(
                "target-mismatch",
                "the bound staged call diverges from the committed target: "
                + ", ".join(mismatches),
            )

        arguments = call.get("arguments")
        if (
            cmt.arguments_digest(arguments, tool_name=call.get("toolName"))
            != action["argumentsDigest"]
        ):
            return _fail(
                "argument-drift",
                "the staged call's retained arguments do not digest to the committed value",
            )

        world = platform.get("world") or {}
        apply_revisions = world.get("resourceRevisionAtApply") or {}
        key = "%s:%s" % (call.get("gatekeeperId"), call.get("action"))
        applied_revision = apply_revisions.get(key)
        if record is not None and record.get("state") == "approved":
            if applied_revision != action["boundResourceRevision"]:
                return _fail(
                    "revision-drift",
                    "resource revision at apply (%r) differs from the bound revision (%r)"
                    % (applied_revision, action["boundResourceRevision"]),
                )

        simulations = {
            simulation.get("id"): simulation
            for simulation in platform.get("simulations") or []
        }
        for basis_id in action["simulationBasis"]:
            simulation = simulations.get(basis_id)
            premise = None
            if simulation is not None:
                premise = next(
                    (
                        entry
                        for entry in _ledger_actions(ledger)
                        if entry.get("id") == simulation.get("actionLedgerId")
                    ),
                    None,
                )
            if simulation is None or premise is None or premise.get("state") != "approved":
                return _fail(
                    "simulation-basis-invalid",
                    "simulation basis %r rests on a premise that is %s"
                    % (
                        basis_id,
                        "absent"
                        if simulation is None or premise is None
                        else premise.get("state"),
                    ),
                )

    facts = json.loads(facts_bytes)
    matched_effects = _matching_effects(platform, facts)
    if matched_effects:
        authorized = bool(applied_bound) and action is not None
        if not authorized:
            return _fail(
                "unbound-execution",
                "an effect matching the judged subject is attested with no approved "
                "action record bound to this commitment",
            )

    report = cell.json("report.json")
    handoff_state = (disposition.get("handoff") or {}).get("state")
    if handoff_state == "requested":
        if report is None or (report.get("decision") or {}).get("handoffState") != "requested":
            return _fail(
                "handoff-dropped",
                "the disposition requests handoff and the published report drops it",
            )

    if report is not None and report.get("execution") == "effect-attested":
        if not matched_effects:
            return _fail(
                "commit-overclaim",
                "the report claims an attested effect and none is retained — a returned "
                "callback or a simulated success is not a committed external effect",
            )

    if report is None:
        return _fail("report-misattribution", "no published report is retained")
    if report.get("commitmentDigest") != digest:
        return _fail(
            "report-misattribution",
            "the published report does not bind this commitment",
        )
    decision = report.get("decision") or {}
    reported = (
        decision.get("kind"),
        decision.get("outcomeId"),
        list(decision.get("reasons") or []),
        decision.get("handoffState"),
    )
    actual = (
        disposition.get("kind"),
        disposition.get("outcomeId"),
        list(disposition.get("reasons") or []),
        handoff_state,
    )
    if reported != actual:
        return _fail(
            "report-misattribution",
            "the published decision %r is not the committed disposition %r"
            % (reported, actual),
        )
    if report.get("execution") not in EXECUTION_STATES:
        return _fail(
            "report-misattribution",
            "the report's execution state is out of vocabulary: %r"
            % (report.get("execution"),),
        )

    return result("pass", None, None)


# --------------------------------------------------------------------------
# layer replay
# --------------------------------------------------------------------------

def jpack_digest(jpack_bin):
    return "sha256:" + sha256_file(jpack_bin)


def evaluate(jpack_bin, work_dir, pack_bytes, facts_bytes, evidence_bytes,
             supported_extensions=()):
    """Run the pinned evaluator over retained bytes; return (envelope bytes, exit)."""
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


def layer_replay(cell, jpack_bin, work_dir):
    raw = cell.bytes("commitment.json")
    if raw is None:
        return result("unavailable", None, "no commitment to replay against")
    try:
        candidate = cmt.parse_commitment_bytes(raw)
        cmt.validate_commitment(candidate)
    except cmt.CommitmentSchemaError as error:
        return result("unavailable", None, "commitment is not replayable: %s" % error)
    judgment = candidate["judgment"]

    if jpack_bin is None or not Path(jpack_bin).is_file():
        return _fail("replay-unavailable", "JPACK_BIN is not available")
    if jpack_digest(jpack_bin) != judgment["executableDigest"]:
        return _fail(
            "replay-executable-mismatch",
            "the live evaluator binary is not the committed executable",
        )

    pack_bytes = cell.bytes("pack.json")
    facts_bytes = cell.bytes("facts.json")
    if pack_bytes is None or facts_bytes is None:
        return _fail("replay-refused", "retained inputs are incomplete")
    evidence_bytes = cell.bytes("evidence.json")

    stdout, exit_code = evaluate(
        jpack_bin,
        work_dir,
        pack_bytes,
        facts_bytes,
        evidence_bytes,
        judgment["supportedExtensions"],
    )
    try:
        envelope = json.loads(stdout.decode("utf-8"))
    except Exception:
        envelope = None
    if exit_code != 0 or envelope is None or envelope.get("status") != "evaluated":
        return _fail(
            "replay-refused",
            "the pinned evaluator did not evaluate the retained inputs (exit %d)"
            % exit_code,
        )
    if envelope.get("evaluatorSpecVersion") != judgment["evaluatorSpecVersion"]:
        return _fail(
            "replay-spec-version-mismatch",
            "the pinned evaluator applies %r, the commitment %r"
            % (envelope.get("evaluatorSpecVersion"), judgment["evaluatorSpecVersion"]),
        )
    if cmt.disposition_digest(envelope) != judgment["dispositionDigest"]:
        return _fail(
            "replay-disposition-mismatch",
            "recomputation under the pinned evaluator does not reproduce the committed "
            "disposition",
        )
    return result("pass", None, None)


# --------------------------------------------------------------------------
# the composed ceremony
# --------------------------------------------------------------------------

def verify_cell(cell_dir, jpack_bin, work_root, cf_verdicts, cell_id=None):
    cell = Cell(cell_dir)
    if cell_id is None:
        cell_id = Path(cell_dir).name
    work_dir = Path(work_root) / cell_id
    work_dir.mkdir(parents=True, exist_ok=True)
    layers = {
        "cf": layer_cf(cell_id, cf_verdicts),
        "binding": layer_binding(cell),
        "replay": layer_replay(cell, jpack_bin, work_dir),
    }
    combined = (
        "pass"
        if all(layers[name]["verdict"] == "pass" for name in layers)
        else "fail"
    )
    return {
        "cf": layers["cf"],
        "binding": layers["binding"],
        "replay": layers["replay"],
        "combined": combined,
        "cfEngaged": cf_engagement(cell_id, cf_verdicts),
    }
