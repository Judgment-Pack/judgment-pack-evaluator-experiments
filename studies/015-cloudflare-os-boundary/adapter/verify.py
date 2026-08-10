"""The verification ceremony — three layers over one cell's retained bytes.

Implements adapter/SPEC.md section 5. Inputs per cell: the retained artifact set and, for
the `upstream` layer, the verdict the node probe runner computed from the same retained
bytes (`harness/cf_runner.py`); for the `replay` layer, the pinned `jpack` executable.
Nothing else — no network, no matrix, no expectations: a layer never knows what it is
registered to say.

Two properties the binding layer holds to, both round-1 findings:

* **Independent derivation.** The registered disposition→action map is applied by the
  verifier to the *retained* judgment, and the commitment's action is compared against
  that derivation. A bridge that commits a different target, tool, action kind, or
  arguments is caught even when every downstream record agrees with its own commitment.
  Only the contextual members (trust tier, stage-time revision, simulation basis) come
  from the store, and each has its own check.
* **No silent suppression.** Every binding check runs; the first failure in registered
  order is the adjudicated code, and every other failing code is published alongside it
  as `suppressed`. "Exactly one layer" is then a statement about what was observed, not
  an artifact of returning early.
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
    "evidence-artifacts.json",
    "evaluation.json",
    "commitment.json",
    "ledger.json",
    "platform.json",
    "report.json",
)
MANIFEST_NAME = "MANIFEST.sha256"

UPSTREAM_CODES = (
    "classification-refused",
    "drain-order-violation",
)
BINDING_CODES = (
    "commitment-missing",
    "commitment-schema-invalid",
    "retained-store-unreadable",
    "pack-artifact-missing",
    "pack-digest-mismatch",
    "judgment-identity-mismatch",
    "facts-digest-mismatch",
    "evidence-digest-mismatch",
    "disposition-digest-mismatch-retained",
    "evidence-backing-invalid",
    "action-derivation-mismatch",
    "action-map-violation",
    "binding-reuse",
    "target-mismatch",
    "argument-drift",
    "stage-revision-mismatch",
    "revision-drift",
    "simulation-basis-invalid",
    "unbound-execution",
    "handoff-dropped",
    "commit-overclaim",
    "report-state-unsupported",
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
# The connector outcome an instrumented Gatekeeper retains per staged call. `committed`
# and `failed` are determinate; `outcome-unknown` is the platform's own at-most-once
# ambiguity, the only state that supports an `applied-unproven` report.
CONNECTOR_OUTCOMES = ("pending", "committed", "failed", "outcome-unknown")


def result(verdict, code=None, detail=None, suppressed=()):
    """The one shape every layer returns."""
    return {
        "verdict": verdict,
        "code": code,
        "detail": detail,
        "suppressed": list(suppressed),
    }


def outcome(layer_result):
    """The adjudicated string for a layer record — code only, never detail."""
    verdict = layer_result["verdict"]
    if verdict in ("pass", "unavailable", "not-engaged"):
        return verdict
    code = layer_result.get("code")
    return "fail" if code is None else "fail:" + code


def _fail(code, detail=None, suppressed=()):
    return result("fail", code, detail, suppressed)


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
# layer upstream — the pinned platform functions, replayed by the node runner
# --------------------------------------------------------------------------

def layer_upstream(cell_id, upstream_verdicts):
    """The node runner's verdict for this cell, vocabulary-checked.

    `not-engaged` is a distinct outcome from `pass`: it says the platform's replayed
    policy functions had nothing in this construction to decide, which is the opposite
    of an endorsement (PREREGISTRATION section 4c).
    """
    if upstream_verdicts is None:
        return result("unavailable", None, "no upstream runner output is available")
    record = (upstream_verdicts.get("cells") or {}).get(cell_id)
    if record is None:
        return result("unavailable", None, "upstream runner reported nothing for this cell")
    verdict = record.get("verdict")
    if verdict in ("pass", "not-engaged"):
        return result(verdict, None, record.get("detail"))
    if verdict == "unavailable":
        return result("unavailable", None, record.get("detail"))
    if verdict == "fail" and record.get("code") in UPSTREAM_CODES:
        return _fail(record["code"], record.get("detail"))
    return _fail(None, "upstream runner returned an out-of-vocabulary record: %r" % (record,))


def upstream_engagement(cell_id, upstream_verdicts):
    """The runner-reported engaged-check list (registry metadata, validity-checked)."""
    if upstream_verdicts is None:
        return None
    record = (upstream_verdicts.get("cells") or {}).get(cell_id)
    if record is None:
        return None
    return record.get("engaged")


# --------------------------------------------------------------------------
# layer binding — context
# --------------------------------------------------------------------------

class Context:
    """Everything the binding checks read, resolved once."""

    def __init__(self, cell):
        self.cell = cell
        self.commitment = None
        self.digest = None
        self.judgment = None
        self.action = None
        self.pack_bytes = None
        self.facts_bytes = None
        self.evidence_bytes = None
        self.facts = None
        self.evidence = {}
        self.envelope = None
        self.disposition = {}
        self.artifacts = None
        self.artifacts_problem = None
        self.ledger = []
        self.platform = {}
        self.report = None
        self.derived = None

    # -- derived views -------------------------------------------------

    @property
    def bound_calls(self):
        return [
            call
            for call in self.platform.get("stagedCalls") or []
            if call.get("commitmentDigest") == self.digest
        ]

    @property
    def ledger_actions(self):
        return [entry for entry in self.ledger if entry.get("type") == "action"]

    def records_for(self, call):
        """Every ledger action record matching a staged call — cardinality is checkable."""
        return [
            entry
            for entry in self.ledger_actions
            if entry.get("gatekeeperId") == call.get("gatekeeperId")
            and entry.get("action") == call.get("action")
        ]

    def record_for(self, call):
        matches = self.records_for(call)
        return matches[0] if len(matches) == 1 else None

    @property
    def applied_bound(self):
        applied = []
        for call in self.bound_calls:
            for record in self.records_for(call):
                if record.get("state") == "approved":
                    applied.append((call, record))
        return applied

    @property
    def matching_effects(self):
        """Effects attested against the judged subject (SPEC section 5)."""
        if self.facts is None:
            return []
        expected = cmt.arguments_digest(cmt.action_arguments(self.facts))
        matches = []
        for effect in self.platform.get("effects") or []:
            if effect.get("toolName") != cmt.ACTION_TOOL:
                continue
            if effect.get("resourceUrl") != cmt.RESOURCE_URL:
                continue
            if cmt.arguments_digest(effect.get("arguments")) == expected:
                matches.append(effect)
        return matches

    def gatekeeper(self, gatekeeper_id):
        for candidate in self.platform.get("gatekeepers") or []:
            if candidate.get("id") == gatekeeper_id:
                return candidate
        return None

    @property
    def handoff_state(self):
        return (self.disposition.get("handoff") or {}).get("state")


def _load_context(cell):
    """Resolve the context, or return a gate failure that forbids further checks."""
    context = Context(cell)

    raw = cell.bytes("commitment.json")
    if raw is None:
        return None, ("commitment-missing", "no commitment.json is retained")
    try:
        candidate = cmt.parse_commitment_bytes(raw)
        problem = cmt.canonical_encoding_problem(raw, candidate)
        if problem:
            return None, ("commitment-schema-invalid", problem)
        cmt.validate_commitment(candidate)
    except cmt.CommitmentSchemaError as error:
        return None, ("commitment-schema-invalid", str(error))

    context.commitment = candidate
    context.judgment = candidate["judgment"]
    context.action = candidate["action"]
    context.digest = cmt.commitment_digest(candidate)

    context.pack_bytes = cell.bytes("pack.json")
    context.facts_bytes = cell.bytes("facts.json")
    context.evidence_bytes = cell.bytes("evidence.json")
    context.envelope = cell.json("evaluation.json")
    context.report = cell.json("report.json")

    ledger = cell.json("ledger.json")
    platform = cell.json("platform.json")
    if not isinstance(ledger, list) or not isinstance(platform, dict):
        # Without the store nothing downstream is evaluable; this is a distinct code
        # rather than a map violation, which round 1 found was conflating two states.
        return None, (
            "retained-store-unreadable",
            "the retained ledger or platform store is absent or unreadable",
        )
    context.ledger = ledger
    context.platform = platform

    if context.facts_bytes is not None:
        try:
            context.facts = json.loads(context.facts_bytes.decode("utf-8"))
        except Exception:
            context.facts = None
    if context.evidence_bytes is not None:
        try:
            loaded = json.loads(context.evidence_bytes.decode("utf-8"))
            context.evidence = loaded if isinstance(loaded, dict) else {}
        except Exception:
            context.evidence = {}
    if isinstance(context.envelope, dict) and isinstance(
        context.envelope.get("disposition"), dict
    ):
        context.disposition = context.envelope["disposition"]

    artifacts_document = cell.json("evidence-artifacts.json")
    if artifacts_document is None:
        context.artifacts_problem = "no retained captured-artifact store"
    else:
        try:
            context.artifacts = cmt.decode_artifacts(artifacts_document)
        except cmt.CommitmentSchemaError as error:
            context.artifacts_problem = str(error)

    if context.facts is not None and context.disposition:
        context.derived = cmt.derived_action(context.disposition, context.facts)

    return context, None


# --------------------------------------------------------------------------
# layer binding — the checks, in registered order (SPEC section 5)
# --------------------------------------------------------------------------

def _check_pack(context):
    if context.pack_bytes is None:
        return "pack-artifact-missing", "no pack.json is retained"
    if cmt.sha256_prefixed(context.pack_bytes) != context.judgment["packDigest"]:
        return (
            "pack-digest-mismatch",
            "retained pack bytes do not match the committed digest",
        )
    return None


def _check_judgment_identity(context):
    """Every committed identity/release field against its retained source.

    Round 1 found these were carried and never cross-checked: a commitment could name a
    different pack id, version, spec version or evaluator release than the artifacts it
    binds and no layer would notice.
    """
    problems = []
    if context.pack_bytes is not None:
        try:
            pack = json.loads(context.pack_bytes.decode("utf-8"))
        except Exception:
            pack = None
        if not isinstance(pack, dict):
            # A pack that does not parse cannot corroborate any committed identity.
            # Silently skipping would let an unparseable artifact clear this check.
            problems.append(
                "the retained pack does not parse, so no committed identity field can "
                "be corroborated against it"
            )
        else:
            for field, member in (
                ("packId", "id"),
                ("packVersion", "version"),
                ("specVersion", "specVersion"),
            ):
                if context.judgment[field] != pack.get(member):
                    problems.append(
                        "judgment.%s (%r) is not the retained pack's %s (%r)"
                        % (field, context.judgment[field], member, pack.get(member))
                    )
    envelope = context.envelope
    if isinstance(envelope, dict):
        if context.judgment["evaluatorSpecVersion"] != envelope.get(
            "evaluatorSpecVersion"
        ):
            problems.append(
                "judgment.evaluatorSpecVersion is not the retained envelope's"
            )
        release = (envelope.get("tool") or {}).get("version")
        if context.judgment["evaluatorRelease"] != release:
            problems.append("judgment.evaluatorRelease is not the retained envelope's")
    extensions = context.judgment["supportedExtensions"]
    if len(set(extensions)) != len(extensions):
        problems.append("judgment.supportedExtensions carries duplicates")
    if problems:
        return "judgment-identity-mismatch", "; ".join(problems)
    return None


def _check_facts(context):
    if (
        context.facts_bytes is None
        or cmt.sha256_prefixed(context.facts_bytes) != context.judgment["factsDigest"]
    ):
        return (
            "facts-digest-mismatch",
            "retained facts bytes are absent or do not match the committed digest",
        )
    return None


def _check_evidence(context):
    committed = context.judgment["evidenceDigest"]
    if committed is None:
        if context.evidence_bytes is not None:
            return (
                "evidence-digest-mismatch",
                "commitment declares no evidence document but one is retained",
            )
        return None
    if (
        context.evidence_bytes is None
        or cmt.sha256_prefixed(context.evidence_bytes) != committed
    ):
        return (
            "evidence-digest-mismatch",
            "retained evidence bytes are absent or do not match the committed digest",
        )
    return None


def _check_disposition_digest(context):
    if context.envelope is None:
        return (
            "disposition-digest-mismatch-retained",
            "no readable evaluator envelope is retained",
        )
    try:
        retained = cmt.disposition_digest(context.envelope)
    except cmt.CommitmentSchemaError as error:
        return "disposition-digest-mismatch-retained", str(error)
    if retained != context.judgment["dispositionDigest"]:
        return (
            "disposition-digest-mismatch-retained",
            "the retained envelope's canonical disposition does not match the commitment",
        )
    return None


def _check_evidence_backing(context):
    """Backing entries against the *retained artifact bytes*, not against their own shape.

    Round 1's blocker: a digest-shaped reference proves nothing. Every `present` claim
    must carry an `artifact` backing whose digest is the digest of an artifact actually
    retained in this cell — so hashing an approval record, an observation record, or any
    other convenient bytes and labelling the result `artifact` fails here.
    """
    backing = context.judgment["evidenceBacking"]
    for requirement, availability in sorted(context.evidence.items()):
        if availability == "present" and requirement not in backing:
            return (
                "evidence-backing-invalid",
                "present claim has no backing entry: " + requirement,
            )
    if backing and context.artifacts is None:
        return (
            "evidence-backing-invalid",
            "backing entries are committed but the captured-artifact store is "
            "unusable: %s" % context.artifacts_problem,
        )
    for requirement in sorted(backing):
        if context.evidence.get(requirement) != "present":
            return (
                "evidence-backing-invalid",
                "backing entry for a claim that is not present: " + requirement,
            )
        entry = backing[requirement]
        if entry.get("kind") != "artifact":
            return (
                "evidence-backing-invalid",
                "backing for %s is a %r reference, not a captured-artifact digest — "
                "resource access and human approval are not evidence"
                % (requirement, entry.get("kind")),
            )
        if set(entry) != {"kind", "digest"}:
            return (
                "evidence-backing-invalid",
                "backing for %s does not carry exactly a kind and a digest" % requirement,
            )
        digest = entry.get("digest")
        if not isinstance(digest, str) or not digest.startswith("sha256:") or len(
            digest
        ) != 71:
            return (
                "evidence-backing-invalid",
                "backing for %s carries no sha256 artifact digest" % requirement,
            )
        payload = (context.artifacts or {}).get(requirement)
        if payload is None:
            return (
                "evidence-backing-invalid",
                "backing for %s names no retained artifact — a backing digest with no "
                "preimage is an assertion, not lineage" % requirement,
            )
        if cmt.sha256_prefixed(payload) != digest:
            return (
                "evidence-backing-invalid",
                "the retained artifact for %s does not hash to its backing digest"
                % requirement,
            )
    for requirement in sorted(context.artifacts or {}):
        if requirement not in backing:
            return (
                "evidence-backing-invalid",
                "an artifact is retained for %s with no backing entry" % requirement,
            )
    return None


def _check_action_derivation(context):
    """The commitment's action against the map applied to the *retained* judgment.

    This is the verifier's independent oracle. Without it every downstream check only
    establishes that the store agrees with whatever the bridge chose to commit.
    """
    if context.facts is None:
        return (
            "action-derivation-mismatch",
            "retained facts are unreadable, so the authorized action cannot be derived",
        )
    if not context.disposition:
        return (
            "action-derivation-mismatch",
            "no retained disposition, so the authorized action cannot be derived",
        )
    derived = context.derived
    action = context.action
    if derived is None:
        # Inaction is derived; the null/non-null consistency is the map check's job.
        return None
    if action is None:
        return None
    divergent = [
        field
        for field in cmt.DERIVED_ACTION_FIELDS
        if action.get(field) != derived[field]
    ]
    if divergent:
        return (
            "action-derivation-mismatch",
            "the committed action diverges from the action the map derives from the "
            "retained judgment: %s" % ", ".join(divergent),
        )
    return None


def _check_action_map(context):
    executable = cmt.executable(context.disposition) if context.disposition else False
    action = context.action
    bound = context.bound_calls
    if action is not None and not executable:
        return (
            "action-map-violation",
            "the commitment carries an action object under a non-executable disposition",
        )
    if action is None and executable:
        return (
            "action-map-violation",
            "the commitment carries no action under an executable disposition",
        )
    if action is None and bound:
        return "action-map-violation", "a staged call binds a commitment to inaction"
    if action is not None and bound and context.matching_effects:
        for call in bound:
            records = context.records_for(call)
            if not any(record.get("state") == "approved" for record in records):
                return (
                    "action-map-violation",
                    "the bound staged call took effect with no approved ledger record",
                )
    return None


def _check_binding_reuse(context):
    bound = context.bound_calls
    applied = context.applied_bound
    if len(bound) > 1 or len(applied) > 1:
        return (
            "binding-reuse",
            "%d staged calls / %d applied records bind one commitment digest"
            % (len(bound), len(applied)),
        )
    for call in bound:
        if len(context.records_for(call)) > 1:
            return (
                "binding-reuse",
                "more than one ledger record claims the bound staged call",
            )
    return None


def _bound_pair(context):
    """The single bound staged call and its single ledger record, or (None, None)."""
    bound = context.bound_calls
    if context.action is None or len(bound) != 1:
        return None, None
    return bound[0], context.record_for(bound[0])


def _check_target(context):
    call, record = _bound_pair(context)
    if call is None:
        return None
    action = context.action
    gatekeeper = context.gatekeeper(call.get("gatekeeperId"))
    record_tag = None
    if record is not None:
        record_tag = ((record.get("description") or {}).get("actionKind") or {}).get("tag")
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
        return (
            "target-mismatch",
            "the bound staged call diverges from the committed target: "
            + ", ".join(mismatches),
        )
    return None


def _check_arguments(context):
    call, _ = _bound_pair(context)
    if call is None:
        return None
    digest = cmt.arguments_digest(call.get("arguments"), tool_name=call.get("toolName"))
    if digest != context.action["argumentsDigest"]:
        return (
            "argument-drift",
            "the staged call's retained arguments do not digest to the committed value",
        )
    return None


def _check_stage_revision(context):
    """The committed `boundResourceRevision` against the revision recorded at staging.

    Round 1: the commitment bound a stage-time revision that nothing ever compared to
    the staging record, so only the apply-time drift was actually checked.
    """
    call, _ = _bound_pair(context)
    if call is None:
        return None
    staged = call.get("resourceRevisionAtStage")
    if staged != context.action["boundResourceRevision"]:
        return (
            "stage-revision-mismatch",
            "the staged call records revision %r; the commitment binds %r"
            % (staged, context.action["boundResourceRevision"]),
        )
    return None


def _check_apply_revision(context):
    call, record = _bound_pair(context)
    if call is None or record is None or record.get("state") != "approved":
        return None
    world = context.platform.get("world") or {}
    revisions = world.get("resourceRevisionAtApply") or {}
    key = "%s:%s" % (call.get("gatekeeperId"), call.get("action"))
    applied = revisions.get(key)
    if applied != context.action["boundResourceRevision"]:
        return (
            "revision-drift",
            "resource revision at apply (%r) differs from the bound revision (%r)"
            % (applied, context.action["boundResourceRevision"]),
        )
    return None


def _check_simulation_basis(context):
    call, _ = _bound_pair(context)
    if context.action is None:
        return None
    basis = context.action["simulationBasis"]
    if call is not None and sorted(call.get("simulationBasis") or []) != list(basis):
        return (
            "simulation-basis-invalid",
            "the staged call's simulation basis %r is not the committed basis %r"
            % (call.get("simulationBasis"), basis),
        )
    simulations = {
        simulation.get("id"): simulation
        for simulation in context.platform.get("simulations") or []
    }
    for basis_id in basis:
        simulation = simulations.get(basis_id)
        premise = None
        if simulation is not None:
            premise = next(
                (
                    entry
                    for entry in context.ledger_actions
                    if entry.get("id") == simulation.get("actionLedgerId")
                ),
                None,
            )
        if simulation is None or premise is None or premise.get("state") != "approved":
            return (
                "simulation-basis-invalid",
                "simulation basis %r rests on a premise that is %s"
                % (
                    basis_id,
                    "absent"
                    if simulation is None or premise is None
                    else premise.get("state"),
                ),
            )
    return None


def _check_unbound_execution(context):
    if not context.matching_effects:
        return None
    if context.action is not None and context.applied_bound:
        return None
    return (
        "unbound-execution",
        "an effect matching the judged subject is attested with no approved action "
        "record bound to this commitment",
    )


def _check_handoff(context):
    if context.handoff_state != "requested":
        return None
    report = context.report
    if report is None or (report.get("decision") or {}).get("handoffState") != "requested":
        return (
            "handoff-dropped",
            "the disposition requests handoff and the published report drops it",
        )
    return None


def _check_commit_overclaim(context):
    report = context.report
    if report is None or report.get("execution") != "effect-attested":
        return None
    if not context.matching_effects:
        return (
            "commit-overclaim",
            "the report claims an attested effect and none is retained — a returned "
            "callback or a simulated success is not a committed external effect",
        )
    return None


def _connector_outcome(context, call):
    if call is None:
        return None
    return call.get("connectorOutcome")


def _check_report_state(context):
    """Closed predicates for every execution state (SPEC section 5, report vocabulary).

    Round 1: only `effect-attested` was correlated with anything retained, so `none`,
    `staged`, `applied` and `applied-unproven` were accepted as free-text claims.
    """
    report = context.report
    if report is None:
        return None  # absence is the report-misattribution check's business
    state = report.get("execution")
    if state not in EXECUTION_STATES:
        return (
            "report-state-unsupported",
            "the report's execution state is out of vocabulary: %r" % (state,),
        )
    bound = context.bound_calls
    call, record = _bound_pair(context)
    effects = context.matching_effects
    connector = _connector_outcome(context, call)
    if connector is not None and connector not in CONNECTOR_OUTCOMES:
        return (
            "report-state-unsupported",
            "the staged call's connector outcome is out of vocabulary: %r" % (connector,),
        )

    if state == "none":
        if bound or effects:
            return (
                "report-state-unsupported",
                "the report claims no execution while a bound staged call or a matching "
                "effect is retained",
            )
        return None

    if not bound:
        return (
            "report-state-unsupported",
            "the report claims execution state %r with no staged call bound to this "
            "commitment" % state,
        )

    if state == "staged":
        if record is not None and record.get("state") != "pending":
            return (
                "report-state-unsupported",
                "the report claims the action is merely staged while its ledger record "
                "is %r" % record.get("state"),
            )
        if effects:
            return (
                "report-state-unsupported",
                "the report claims the action is merely staged while a matching effect "
                "is attested",
            )
        return None

    if state == "applied":
        if record is None or record.get("state") != "approved":
            return (
                "report-state-unsupported",
                "the report claims the action was applied while no single approved "
                "ledger record is bound to it",
            )
        if connector == "outcome-unknown":
            return (
                "report-state-unsupported",
                "the connector outcome is unknown; an at-most-once dispatch whose "
                "result was never observed is applied-unproven, not applied",
            )
        return None

    if state == "applied-unproven":
        if connector != "outcome-unknown":
            return (
                "report-state-unsupported",
                "the report claims an unproven application while the retained connector "
                "outcome is %r — unproven is the ambiguity state, not a default" % connector,
            )
        if effects:
            return (
                "report-state-unsupported",
                "the report claims an unproven application while a matching effect is "
                "attested",
            )
        return None

    # effect-attested: the attestation itself is `commit-overclaim`'s business; here the
    # only additional requirement is that something was actually applied.
    if record is None or record.get("state") != "approved":
        return (
            "report-state-unsupported",
            "the report claims an attested effect with no approved bound ledger record",
        )
    return None


def _check_report_misattribution(context):
    report = context.report
    if report is None:
        return "report-misattribution", "no published report is retained"
    if report.get("commitmentDigest") != context.digest:
        return (
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
        context.disposition.get("kind"),
        context.disposition.get("outcomeId"),
        list(context.disposition.get("reasons") or []),
        context.handoff_state,
    )
    if reported != actual:
        return (
            "report-misattribution",
            "the published decision %r is not the committed disposition %r"
            % (reported, actual),
        )
    return None


# Registered order. The list *is* the SPEC section 5 ordering; a harness test asserts
# that this sequence and the SPEC's numbered steps are the same sequence.
BINDING_CHECKS = (
    ("pack-artifact-missing/pack-digest-mismatch", _check_pack),
    ("judgment-identity-mismatch", _check_judgment_identity),
    ("facts-digest-mismatch", _check_facts),
    ("evidence-digest-mismatch", _check_evidence),
    ("disposition-digest-mismatch-retained", _check_disposition_digest),
    ("evidence-backing-invalid", _check_evidence_backing),
    ("action-derivation-mismatch", _check_action_derivation),
    ("action-map-violation", _check_action_map),
    ("binding-reuse", _check_binding_reuse),
    ("target-mismatch", _check_target),
    ("argument-drift", _check_arguments),
    ("stage-revision-mismatch", _check_stage_revision),
    ("revision-drift", _check_apply_revision),
    ("simulation-basis-invalid", _check_simulation_basis),
    ("unbound-execution", _check_unbound_execution),
    ("handoff-dropped", _check_handoff),
    ("commit-overclaim", _check_commit_overclaim),
    ("report-state-unsupported", _check_report_state),
    ("report-misattribution", _check_report_misattribution),
)


def layer_binding(cell):
    """Every check runs; the first failure is adjudicated, the rest are published."""
    context, gate = _load_context(cell)
    if gate is not None:
        return _fail(gate[0], gate[1])
    failures = []
    for _, check in BINDING_CHECKS:
        try:
            found = check(context)
        except Exception as error:  # a check must never take the layer down silently
            found = (
                "retained-store-unreadable",
                "binding check raised: %s: %s" % (type(error).__name__, error),
            )
        if found is not None:
            failures.append(found)
    if not failures:
        return result("pass", None, None)
    primary = failures[0]
    return _fail(primary[0], primary[1], [code for code, _ in failures[1:]])


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

def verify_cell(cell_dir, jpack_bin, work_root, upstream_verdicts, cell_id=None):
    cell = Cell(cell_dir)
    if cell_id is None:
        cell_id = Path(cell_dir).name
    work_dir = Path(work_root) / cell_id
    work_dir.mkdir(parents=True, exist_ok=True)
    layers = {
        "upstream": layer_upstream(cell_id, upstream_verdicts),
        "binding": layer_binding(cell),
        "replay": layer_replay(cell, jpack_bin, work_dir),
    }
    # `not-engaged` is not an objection; a cell is combined-pass when no layer objects.
    combined = (
        "pass"
        if all(
            layers[name]["verdict"] in ("pass", "not-engaged") for name in layers
        )
        else "fail"
    )
    return {
        "upstream": layers["upstream"],
        "binding": layers["binding"],
        "replay": layers["replay"],
        "combined": combined,
        "upstreamEngaged": upstream_engagement(cell_id, upstream_verdicts),
    }
