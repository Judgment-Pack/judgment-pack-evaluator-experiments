"""Fixture construction — a one-time act; the frozen bytes, not this builder, are scored.

Every cell derives from one shared deterministic timeline. The JPS side is real: every
`evaluation.json` is the exact stdout of the pinned evaluator (JPACK_BIN) over the cell's
retained facts and evidence bytes, which are themselves the JCS serialization of verbatim
cases from the specification's conformance seed manifest (vendored digests in PINS.json).
The platform-identity values are derived by the adapter's reproduction of the platform's
own rule, which a harness test compares against the pinned `actionKindFor` itself.

Both strata are constructed here. Construction is not adjudication: the holdout fixtures
are BUILT before the freeze — they must exist for the scorer's holdout gate to pass — but
no layer verdict is ever computed over them until `--include-holdout` is allowed, which
the scorer refuses while the preregistration digest is null.

All clocks are fixed constants. Run:
    JPACK_BIN=... CFOS_SOURCE=... python harness/build_fixtures.py
"""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDY / "adapter"))
sys.path.insert(0, str(STUDY / "harness"))

import cf_runner  # noqa: E402
import commitment as cmt  # noqa: E402

FIXTURES = STUDY / "fixtures"
PACK_PATH = FIXTURES / "data-request-intake-triage.pack.json"

# A second portal-scoped resource: the portal rejects unscoped grants, so the
# substitution target must carry a `#server=` scope like the first (round 3).
# A SECOND portal deployment. The portal hosts one endpoint per deployment and a wire
# tool belongs to its own server scope, so a second target needs its own endpoint, its
# own scope and correspondingly-named tools (round 4).
OTHER_ENDPOINT = "https://other-tracker.example/mcp"
OTHER_SERVER_ID = "other"
OTHER_RESOURCE_URL = "%s#server=%s" % (OTHER_ENDPOINT, OTHER_SERVER_ID)
OTHER_TOOL_NAME = "other_create_work_item"
BOUND_REVISION = "rev-7"
DRIFTED_REVISION = "rev-9"

# A DEPLOYMENT is everything a retained record inherits from the portal binding its call
# was staged through, registered as one object rather than assumed:
#
# * `serverName` — the portal's scope label, `${serverName} / ${scopeServerName ?? serverId}`
#   (`gatekeeper-mcp-portal/src/portal.ts:495-498`). It is what `describeCall` prints and
#   what an approval prompt names.
# * `endpoint` — `host.endpoint`, the BARE endpoint `describeCall` renders
#   (`mcp-shared/src/session.ts:113`, `facet.ts:82-83`); the `#server=` form is the
#   resourceUrl, never the printed endpoint.
# * `resourceUrl` / `serverId` — the scoped grant, and the upstream server id the
#   action-kind scope tag encodes (`portal.ts:523-525`).
# * `resourceTitle` — the workspace's denormalized title for the connection
#   (`overseer.ts:2686` from `:2557`). Its default is the same scope label; the value here
#   is a workspace-local title override, the one mutation upstream allows on that field
#   (`overseer.ts:9388-9393`), and each deployment carries its own.
#
# Round 5 (R4-3) found `describe()` hard-coded the first deployment's server name and
# endpoint, cache key included, so `b04` and `h04` retained the second deployment's
# structural fields beside prose naming the first — a tuple no host can emit, since
# `session.ts:110-117` supplies the CURRENT host's own `serverName` and `endpoint`.
PORTAL = {
    "serverName": "tracker portal / tracker",
    "endpoint": cmt.PORTAL_ENDPOINT,
    "serverId": cmt.UPSTREAM_SERVER_ID,
    "resourceUrl": cmt.RESOURCE_URL,
    "resourceTitle": "Tracker",
}
OTHER_PORTAL = {
    "serverName": "other tracker portal / other",
    "endpoint": OTHER_ENDPOINT,
    "serverId": OTHER_SERVER_ID,
    "resourceUrl": OTHER_RESOURCE_URL,
    "resourceTitle": "Other Tracker",
}
DEPLOYMENTS = (PORTAL, OTHER_PORTAL)

ENABLER = {"type": "user", "id": "governor@example.invalid", "name": "Governor"}
APPROVER = {"type": "user", "id": "approver@example.invalid", "name": "Approver"}
AGENT_CALLER = {"from": "agent", "chatId": 1}

# The catalog the pinned MCP Portal connector would expose for this deployment. Tool
# names carry the portal's `<upstream server id>_<tool>` wire form; annotations are what
# the upstream server declares and what `classifyTool` reads.
TRACKER_TOOL = {
    "name": cmt.ACTION_TOOL,
    "description": "Create a work item in the tracker.",
    "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
}
# A genuinely non-auto-approvable write: unannotated, so `classifyTool` gives it
# `mode: action, autoApprovable: false` on any tier (tools.ts:66-69). Round 2 found the
# earlier manual gate was fabricated by omitting `autoApprovable` on a tool the connector
# would have marked auto-approvable; this is a gate the pinned classifier actually makes.
GATE_TOOL = {
    "name": cmt.SECOND_TOOL,
    "description": "Close a work item in the tracker.",
    "annotations": {},
}
DELETE_TOOL = {
    "name": "tracker_delete_work_item",
    "description": "Delete a work item in the tracker.",
    "annotations": {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True},
}

# The specification conformance seed cases each cell evaluates (facts + evidence verbatim).
CASES = {
    "proceed": "proceed-complete-and-appropriate",
    "clarify": "clarify-incomplete",
    "conflict": "conflict-decline-and-clarify",
    "unknown": "required-evidence-unknown",
    "absent": "required-evidence-absent",
    "not-applicable": "not-applicable-request-type",
}

# The evidence artifacts an acquiring system would retain. Their bytes are frozen in each
# cell (`evidence-artifacts.json`) so a backing digest has a checkable preimage; the study
# never inspects their content and asserts nothing about their authenticity — and nothing
# here is a capture: these bytes are constructed, and the ceremony establishes only that a
# retained preimage hashes to the committed digest.
EVIDENCE_ARTIFACTS = {
    "intake-form": cmt.jcs({"artifact": "intake-form", "capture": "fixture-capture-01"}),
    "sponsor-endorsement": cmt.jcs(
        {"artifact": "sponsor-endorsement", "capture": "fixture-capture-02"}
    ),
}


def timestamp(index):
    return "2026-08-01T00:%02d:00.000Z" % index


def staged_call_source(gatekeeper_id=1, action_key=11):
    """The provenance an attestation claims when the store names a staged call as origin."""
    return {"kind": "staged-call", "gatekeeperId": gatekeeper_id, "action": action_key}


# The other two arms of that union: an attestation sourcing the effect to the read path (no
# queue entry exists to name) and one sourcing it outside the ceremony altogether.
READ_PATH_SOURCE = {"kind": "read-path"}


def load_cases():
    manifest = json.loads(
        (FIXTURES / "conformance-cases.json").read_text(encoding="utf-8")
    )
    return {case["id"]: case for case in manifest["cases"]}


def evaluate_envelope(jpack_bin, facts_bytes, evidence_bytes):
    with tempfile.TemporaryDirectory(prefix="study015-build-eval-") as scratch:
        scratch = Path(scratch)
        facts = scratch / "facts.json"
        evidence = scratch / "evidence.json"
        facts.write_bytes(facts_bytes)
        evidence.write_bytes(evidence_bytes)
        completed = subprocess.run(
            [
                str(jpack_bin),
                "experimental",
                "evaluate",
                str(PACK_PATH),
                "--facts",
                str(facts),
                "--evidence",
                str(evidence),
                "--format",
                "json",
            ],
            capture_output=True,
            timeout=300,
        )
    if completed.returncode != 0:
        raise SystemExit(
            "the pinned evaluator refused a fixture case: " + completed.stderr.decode()
        )
    return completed.stdout


class Timeline:
    """One cell's records, assembled then serialized deterministically."""

    def __init__(self, action_kind, described=None):
        self.action_kind = action_kind
        self.described = described or {
            "title": "action",
            "description": "action",
        }
        self.gatekeepers = [
            {
                "id": 1,
                "resourceUrl": PORTAL["resourceUrl"],
                "serverTrust": "vetted",
                "tools": [copy.deepcopy(TRACKER_TOOL)],
            }
        ]
        self.auto_rules = []
        self.ledger = []
        self.staged = []
        self.effects = []
        self.observed = []
        self.witnesses = []
        self.apply_revisions = {}

    # -- platform-side state -------------------------------------------

    def rule(self, kind=None, gatekeeper_id=1):
        return {
            "gatekeeperId": gatekeeper_id,
            "actionKind": dict(kind or self.action_kind),
            "enabledBy": dict(ENABLER),
        }

    def enable_rule(self, kind=None, gatekeeper_id=1):
        self.auto_rules.append(self.rule(kind, gatekeeper_id))

    def witness(self, *, gatekeeper_id=1, pass_index=1, at, applied_ids, rules=None):
        """The stage-time drain witness for one pass (SPEC section 0)."""
        self.witnesses.append(
            {
                "gatekeeperId": gatekeeper_id,
                "pass": pass_index,
                "at": at,
                "appliedActionIds": sorted(applied_ids),
                "rules": [dict(rule) for rule in (rules if rules is not None
                                                  else self.auto_rules)],
                "gatekeeperPresent": True,
            }
        )

    # -- ledger --------------------------------------------------------

    def add_action(self, ledger_id, *, gatekeeper_id=1, action_key, state,
                   auto=False, autoApprovable=True, kind=None, resolved_at=None,
                   described=None, deployment=None):
        # The exact field set `mcp-shared/src/session.ts:126-135` submits: describeCall's
        # title and description, implementsRevert false, awaitDecision ALWAYS true, an
        # explicit autoApprovable boolean, and the connector-derived action kind.
        description = {
            "title": (described or self.described)["title"],
            "description": (described or self.described)["description"],
            "implementsRevert": False,
            "awaitDecision": True,
            "autoApprovable": bool(autoApprovable),
        }
        if kind is not False:
            description["actionKind"] = dict(kind or self.action_kind)
        deployment = deployment or PORTAL
        record = {
            "id": ledger_id,
            "gatekeeperId": gatekeeper_id,
            "resourceTitle": deployment["resourceTitle"],
            "resourceUrl": deployment["resourceUrl"],
            "caller": dict(AGENT_CALLER),
            "createdAt": timestamp(ledger_id),
            "state": state,
            "type": "action",
            "action": action_key,
            "description": description,
        }
        if state in ("approved", "rejected"):
            record["resolvedBy"] = dict(ENABLER if auto else APPROVER)
            # `appliedAt` is a RESOLUTION stamp upstream: overseer.ts sets it on approve
            # (:2495) and on reject (:7729). The study never reads it as evidence of
            # application — only `state == "approved"` means applied.
            record["appliedAt"] = resolved_at or timestamp(30 + ledger_id)
        if state == "approved":
            # `applyPendingAction` always stores the flag, both ways (overseer.ts:2497).
            record["autoApproved"] = bool(auto)
        self.ledger.append(record)
        return record

    def add_observation(self, ledger_id, title, description, deployment=None):
        deployment = deployment or PORTAL
        self.ledger.append(
            {
                "id": ledger_id,
                "gatekeeperId": 1,
                "resourceTitle": deployment["resourceTitle"],
                "resourceUrl": deployment["resourceUrl"],
                "caller": dict(AGENT_CALLER),
                "createdAt": timestamp(ledger_id),
                "state": "approved",
                "type": "observation",
                "description": {"title": title, "description": description},
            }
        )

    # -- gatekeeper-side store -----------------------------------------

    def stage(self, *, gatekeeper_id=1, action_key, tool_name, arguments,
              commitment_digest=None, revision=BOUND_REVISION,
              connector_outcome="committed"):
        call = {
            "gatekeeperId": gatekeeper_id,
            "action": action_key,
            "toolName": tool_name,
            "arguments": arguments,
            "resourceRevisionAtStage": revision,
            "connectorOutcome": connector_outcome,
        }
        if commitment_digest is not None:
            call["commitmentDigest"] = commitment_digest
        self.staged.append(call)
        return call

    def applied_at_revision(self, *, gatekeeper_id=1, action_key, revision):
        self.apply_revisions["%s:%s" % (gatekeeper_id, action_key)] = revision

    def attest_effect(self, arguments, *, resource_url=cmt.RESOURCE_URL,
                      tool_name=cmt.ACTION_TOOL, source=None):
        # An attestation states where the store SAYS the effect came from. Round 4:
        # without a call identity the ceremony could only count effects, so a correct
        # count could coexist with an effect the store sources to a different, unretained
        # call. Round 5: that identity was then written onto cells that stage nothing, so
        # the provenance is a registered UNION — a named staged call, the read path, or
        # outside the queue entirely — and it remains a claim the store makes about
        # itself, never a corroborated one. Round 7 (R6-1 residue): "the staged call it
        # came from" was the causal reading the rescope withdrew, still living here.
        self.effects.append(
            {
                "resourceUrl": resource_url,
                "toolName": tool_name,
                "arguments": arguments,
                "source": dict(source or staged_call_source()),
            }
        )

    def platform_document(self):
        return {
            "gatekeepers": self.gatekeepers,
            "autoApproveTags": self.auto_rules,
            "stagedCalls": self.staged,
            "observedCalls": self.observed,
            "drainWitnesses": self.witnesses,
            "world": {"resourceRevisionAtApply": self.apply_revisions},
            "effects": self.effects,
        }


def dumps(document):
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_cell(directory, artifacts):
    directory.mkdir(parents=True, exist_ok=True)
    for name, payload in artifacts.items():
        (directory / name).write_bytes(payload)
    manifest_lines = [
        "%s  %s" % (cmt.sha256_hex(payload), name)
        for name, payload in sorted(artifacts.items())
    ]
    (directory / "MANIFEST.sha256").write_text(
        "\n".join(manifest_lines) + "\n", encoding="utf-8"
    )


def backing_for(evidence):
    return {
        requirement: {
            "kind": "artifact",
            "digest": cmt.sha256_prefixed(EVIDENCE_ARTIFACTS[requirement]),
        }
        for requirement, availability in evidence.items()
        if availability == "present"
    }


def artifacts_for(evidence):
    return {
        requirement: EVIDENCE_ARTIFACTS[requirement]
        for requirement, availability in evidence.items()
        if availability == "present"
    }


def honest_report(envelope, digest, execution, note=""):
    disposition = envelope["disposition"]
    return {
        "commitmentDigest": digest,
        "decision": {
            "kind": disposition.get("kind"),
            "outcomeId": disposition.get("outcomeId"),
            "reasons": list(disposition.get("reasons") or []),
            "handoffState": (disposition.get("handoff") or {}).get("state"),
        },
        "execution": execution,
        "note": note,
    }


class Builder:
    def __init__(self):
        jpack_bin = os.environ.get("JPACK_BIN")
        if not jpack_bin or not Path(jpack_bin).is_file():
            raise SystemExit("JPACK_BIN must point at the pinned evaluator")
        self.jpack_bin = jpack_bin
        self.executable_digest = "sha256:" + cmt.sha256_hex(Path(jpack_bin).read_bytes())
        self.pack_bytes = PACK_PATH.read_bytes()
        self.cases = load_cases()
        self.action_kind = {
            "tag": cmt.action_kind_tag(),
            "label": cmt.ACTION_TOOL,
        }
        self.delete_kind = {
            "tag": cmt.action_kind_tag(tool_name=DELETE_TOOL["name"]),
            "label": DELETE_TOOL["name"],
        }
        self.gate_kind = {
            "tag": cmt.action_kind_tag(tool_name=GATE_TOOL["name"]),
            "label": GATE_TOOL["name"],
        }
        self._descriptions = {}
        self._envelopes = {}

    def describe(self, tool, tool_args, mode="action", classified_by="default",
                 deployment=None):
        """The prose the pinned connector would submit, from upstream's own describeCall.

        Round 2: the fixtures previously carried invented short prose, which no connector
        emits. These are the real strings, generated by the pinned function.

        Round 5: the DEPLOYMENT is an input, not a constant. `describeCall` prints the
        calling host's own server name and endpoint, so prose generated for one deployment
        cannot appear on a record staged through another — and the cache key carries the
        deployment for the same reason.
        """
        deployment = deployment or PORTAL
        key = json.dumps(
            [deployment["serverName"], deployment["endpoint"],
             tool["name"], tool_args, mode, classified_by],
            sort_keys=True,
        )
        if key not in self._descriptions:
            helpers = cf_runner.build_helpers(
                {
                    "describeCalls": [
                        {
                            "label": "d",
                            "serverName": deployment["serverName"],
                            "endpoint": deployment["endpoint"],
                            "tool": tool,
                            "toolArgs": tool_args,
                            "mode": mode,
                            "classifiedBy": classified_by,
                        }
                    ]
                }
            )
            self._descriptions[key] = helpers["describedCalls"]["d"]
        return self._descriptions[key]

    def case_bytes(self, case_key):
        case = self.cases[CASES[case_key]]
        return cmt.jcs(case["facts"]), cmt.jcs(case["evidenceAvailability"])

    def envelope_bytes(self, case_key):
        if case_key not in self._envelopes:
            facts_bytes, evidence_bytes = self.case_bytes(case_key)
            self._envelopes[case_key] = evaluate_envelope(
                self.jpack_bin, facts_bytes, evidence_bytes
            )
        return self._envelopes[case_key]

    # ------------------------------------------------------------------
    # assembly primitives
    # ------------------------------------------------------------------

    def build(self, *, case_key, envelope_bytes=None, action_override=None,
              backing_override=None, artifacts_override=None,
              executable_digest=None, judgment_override=None):
        """Retained JPS artifacts + the commitment for one cell."""
        facts_bytes, evidence_bytes = self.case_bytes(case_key)
        raw_envelope = (
            self.envelope_bytes(case_key) if envelope_bytes is None else envelope_bytes
        )
        envelope = json.loads(raw_envelope.decode("utf-8"))
        evidence = json.loads(evidence_bytes.decode("utf-8"))
        disposition = envelope["disposition"]
        facts = json.loads(facts_bytes.decode("utf-8"))
        if action_override is None:
            action = cmt.authorized_action(
                disposition, facts, bound_resource_revision=BOUND_REVISION
            )
        else:
            action = action_override
        backing = backing_for(evidence) if backing_override is None else backing_override
        artifacts = (
            artifacts_for(evidence) if artifacts_override is None else artifacts_override
        )
        document = cmt.build_commitment(
            pack_bytes=self.pack_bytes,
            facts_bytes=facts_bytes,
            evidence_bytes=evidence_bytes,
            envelope=envelope,
            executable_digest=executable_digest or self.executable_digest,
            backing=backing,
            action=action,
        )
        if judgment_override:
            document["judgment"].update(judgment_override)
        return {
            "facts_bytes": facts_bytes,
            "evidence_bytes": evidence_bytes,
            "envelope_bytes": raw_envelope,
            "envelope": envelope,
            "commitment": document,
            "digest": cmt.commitment_digest(document),
            "action": document["action"],
            "facts": facts,
            "artifacts": artifacts,
        }

    def forced_action(self, case_key, **overrides):
        """An action object the map forbids — the bridge misbehaving on purpose."""
        facts_bytes, _ = self.case_bytes(case_key)
        facts = json.loads(facts_bytes.decode("utf-8"))
        action = {
            "gatekeeperId": cmt.GATEKEEPER_ID,
            "resourceUrl": cmt.RESOURCE_URL,
            "serverTrust": cmt.SERVER_TRUST,
            "toolName": cmt.ACTION_TOOL,
            "actionKindTag": cmt.action_kind_tag(),
            "argumentsDigest": cmt.arguments_digest(cmt.action_arguments(facts)),
            "boundResourceRevision": BOUND_REVISION,
        }
        action.update(overrides)
        return action

    def artifacts(self, built, timeline, report):
        return {
            "pack.json": self.pack_bytes,
            "facts.json": built["facts_bytes"],
            "evidence.json": built["evidence_bytes"],
            "evidence-artifacts.json": dumps(cmt.artifacts_document(built["artifacts"])),
            "evaluation.json": built["envelope_bytes"],
            "commitment.json": cmt.commitment_bytes(built["commitment"]),
            "ledger.json": dumps(timeline.ledger),
            "platform.json": dumps(timeline.platform_document()),
            "report.json": dumps(report),
        }

    # ------------------------------------------------------------------
    # the standard executed baseline (proceed, applied, effected)
    # ------------------------------------------------------------------

    def timeline(self, built=None, tool=None, tool_args=None):
        """A Timeline whose default action prose is the connector's own for this call."""
        if built is None:
            described = self.describe(TRACKER_TOOL, {})
        else:
            described = self.describe(
                tool or TRACKER_TOOL,
                cmt.action_arguments(built["facts"]) if tool_args is None else tool_args,
            )
        return Timeline(self.action_kind, described)

    def executed_timeline(self, built, *, auto=True, revision=BOUND_REVISION,
                          attest=True, connector_outcome="committed"):
        timeline = self.timeline(built)
        if auto:
            timeline.enable_rule()
        record = timeline.add_action(1, action_key=11, state="approved", auto=auto)
        timeline.stage(
            action_key=11,
            tool_name=cmt.ACTION_TOOL,
            arguments=cmt.action_arguments(built["facts"]),
            commitment_digest=built["digest"],
            connector_outcome=connector_outcome,
        )
        timeline.applied_at_revision(action_key=11, revision=revision)
        if auto:
            timeline.witness(at=record["appliedAt"], applied_ids=[1])
        if attest:
            timeline.attest_effect(cmt.action_arguments(built["facts"]),
                                   source=staged_call_source(action_key=11))
        return timeline

    def inaction_cell(self, case_key, *, report_mutator=None, envelope_bytes=None):
        built = self.build(case_key=case_key, envelope_bytes=envelope_bytes)
        timeline = self.timeline(built)
        report = honest_report(built["envelope"], built["digest"], "none")
        if report_mutator:
            report_mutator(report)
        return built, timeline, report


def build_all():
    builder = Builder()
    for parent in ("baseline", "mutations", "holdout"):
        directory = FIXTURES / parent
        if directory.is_dir():
            shutil.rmtree(directory)

    def emit(cell_id, built, timeline, report, stratum="locked"):
        if stratum == "holdout":
            directory = FIXTURES / "holdout" / cell_id
        elif cell_id == "pos-baseline":
            directory = FIXTURES / "baseline"
        else:
            directory = FIXTURES / "mutations" / cell_id
        write_cell(directory, builder.artifacts(built, timeline, report))

    # ---- control gates ----------------------------------------------------
    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built)
    emit("pos-baseline", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # byo trust tier; the ledger still claims auto-approval. The commitment binds the
    # tier the map fixes (vetted), because the map — not the store — determines it; the
    # deployment's endpoint is byo, so the binding layer sees the divergence too.
    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built)
    timeline.gatekeepers[0]["serverTrust"] = "byo"
    emit("neg-mcp-byo-autoapply", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # idempotentHint withdrawn; the ledger still claims auto-approval.
    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built)
    del timeline.gatekeepers[0]["tools"][0]["annotations"]["idempotentHint"]
    emit("neg-mcp-nonidempotent-autoapply", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # A manual gate that was pending when the claimed auto-approval happened: it is
    # resolved (rejected) only afterwards, so a final-state reading would miss it and the
    # stage-time reconstruction does not.
    built = builder.build(case_key="proceed")
    timeline = builder.timeline(built)
    timeline.enable_rule()
    timeline.gatekeepers[0]["tools"].append(copy.deepcopy(GATE_TOOL))
    gate_arguments = {"itemId": "WI-1"}
    timeline.add_action(1, action_key=10, state="rejected", autoApprovable=False,
                        kind=builder.gate_kind, resolved_at=timestamp(45),
                        described=builder.describe(GATE_TOOL, gate_arguments))
    timeline.stage(action_key=10, tool_name=GATE_TOOL["name"],
                   arguments=gate_arguments, connector_outcome="rejected")
    record = timeline.add_action(2, action_key=11, state="approved", auto=True,
                                 resolved_at=timestamp(32))
    timeline.stage(action_key=11, tool_name=cmt.ACTION_TOOL,
                   arguments=cmt.action_arguments(built["facts"]),
                   commitment_digest=built["digest"])
    timeline.applied_at_revision(action_key=11, revision=BOUND_REVISION)
    timeline.witness(at=record["appliedAt"], applied_ids=[2])
    timeline.attest_effect(cmt.action_arguments(built["facts"]))
    emit("neg-drain-skip", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # Binding-layer liveness through the official scorer: non-canonical commitment bytes.
    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False)
    artifacts = builder.artifacts(
        built, timeline,
        honest_report(built["envelope"], built["digest"], "effect-attested"))
    artifacts["commitment.json"] = artifacts["commitment.json"] + b"\n"
    write_cell(FIXTURES / "mutations" / "neg-binding-control", artifacts)

    # Replay-layer liveness: a retained pack the pinned evaluator refuses to load. Two
    # layers fail here by construction — an unparseable pack corroborates no committed
    # identity either — and that is the point of a gate: it proves both are alive.
    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False)
    refused = builder.pack_bytes[: len(builder.pack_bytes) // 2]
    document = copy.deepcopy(built["commitment"])
    document["judgment"]["packDigest"] = cmt.sha256_prefixed(refused)
    digest = cmt.commitment_digest(document)
    timeline.staged[0]["commitmentDigest"] = digest
    artifacts = builder.artifacts(
        built, timeline, honest_report(built["envelope"], digest, "effect-attested"))
    artifacts["pack.json"] = refused
    artifacts["commitment.json"] = cmt.commitment_bytes(document)
    write_cell(FIXTURES / "mutations" / "neg-replay-control", artifacts)

    # ---- A: judgment-artifact ---------------------------------------------
    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False)
    artifacts = builder.artifacts(
        built, timeline,
        honest_report(built["envelope"], built["digest"], "effect-attested"))
    pack = json.loads(builder.pack_bytes.decode("utf-8"))
    pack["description"] = pack.get("description", "") + " "
    artifacts["pack.json"] = dumps(pack)
    write_cell(FIXTURES / "mutations" / "a01-pack-bytes-drift", artifacts)

    # clarify-return forged to proceed, everything rebuilt coherently.
    forged = json.loads(builder.envelope_bytes("clarify").decode("utf-8"))
    forged["disposition"] = {"handoff": {"state": "none"}, "kind": "outcome",
                             "outcomeId": "proceed", "reasons": []}
    forged_bytes = dumps(forged)
    built = builder.build(case_key="clarify", envelope_bytes=forged_bytes)
    timeline = builder.executed_timeline(built, auto=False)
    emit("a02-disposition-forged", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # executable digest forged (coherently re-bound).
    built = builder.build(case_key="proceed", executable_digest="sha256:" + "0" * 64)
    timeline = builder.executed_timeline(built, auto=False)
    emit("a03-evaluator-digest-forged", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # a committed identity that is not the retained artifacts' identity.
    built = builder.build(case_key="proceed",
                          judgment_override={"evaluatorRelease": "0.15.0"})
    timeline = builder.executed_timeline(built, auto=False)
    emit("a04-judgment-identity-forged", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # ---- S: semantic collapse ----------------------------------------------
    def misattribute(report):
        report["decision"] = {"kind": "outcome", "outcomeId": "rejected",
                              "reasons": [], "handoffState": "requested"}
        report["note"] = "request rejected by the judgment"
    built, timeline, report = builder.inaction_cell("conflict", report_mutator=misattribute)
    emit("s01-conflict-as-rejected", built, timeline, report)

    built = builder.build(case_key="unknown",
                          action_override=builder.forced_action("unknown"))
    timeline = builder.executed_timeline(built)
    emit("s02-unknown-auto-applied", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # operational failure retconned: retained inputs are the proceed case, retained
    # envelope is a real unresolved(unknown) envelope from different inputs.
    retcon_envelope = builder.envelope_bytes("unknown")
    facts_bytes, evidence_bytes = builder.case_bytes("proceed")
    envelope = json.loads(retcon_envelope.decode("utf-8"))
    evidence = json.loads(evidence_bytes.decode("utf-8"))
    document = cmt.build_commitment(
        pack_bytes=builder.pack_bytes,
        facts_bytes=facts_bytes,
        evidence_bytes=evidence_bytes,
        envelope=envelope,
        executable_digest=builder.executable_digest,
        backing=backing_for(evidence),
        action=None,
    )
    built = {
        "facts_bytes": facts_bytes,
        "evidence_bytes": evidence_bytes,
        "envelope_bytes": retcon_envelope,
        "envelope": envelope,
        "commitment": document,
        "digest": cmt.commitment_digest(document),
        "action": None,
        "facts": json.loads(facts_bytes.decode("utf-8")),
        "artifacts": artifacts_for(evidence),
    }
    timeline = builder.timeline(built)
    emit("s03-opfail-as-unknown", built, timeline,
         honest_report(envelope, built["digest"], "none",
                       note="evaluation returned unknown; no action taken"))

    # a present claim backed by an approval record rather than an evidence artifact.
    _, evidence_bytes = builder.case_bytes("proceed")
    evidence = json.loads(evidence_bytes.decode("utf-8"))
    backing = backing_for(evidence)
    backing["sponsor-endorsement"] = {"kind": "approval-record", "ref": "ledger:1"}
    built = builder.build(case_key="proceed", backing_override=backing)
    timeline = builder.executed_timeline(built, auto=False)
    emit("s04-approval-as-evidence", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    def close_quietly(report):
        report["decision"]["handoffState"] = "none"
        report["note"] = "case closed"
    built, timeline, report = builder.inaction_cell("absent", report_mutator=close_quietly)
    emit("s05-handoff-dropped", built, timeline, report)

    built = builder.build(case_key="not-applicable",
                          action_override=builder.forced_action("not-applicable"))
    timeline = builder.executed_timeline(built, auto=False)
    emit("s06-not-applicable-executed", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # a present claim backed by an observation record.
    backing = backing_for(evidence)
    backing["intake-form"] = {"kind": "observation-record", "ref": "ledger:1"}
    built = builder.build(case_key="proceed", backing_override=backing)
    timeline = builder.timeline(built)
    read_tool = dict(copy.deepcopy(TRACKER_TOOL), name="tracker_get_intake_form",
                     annotations={"readOnlyHint": True})
    timeline.gatekeepers[0]["tools"].append(read_tool)
    read_args = {"requestId": "R-1"}
    read_described = builder.describe(read_tool, read_args, mode="read",
                                      classified_by="server-annotation")
    timeline.add_observation(1, read_described["title"], read_described["description"])
    timeline.observed.append(
        {"gatekeeperId": 1, "ledgerId": 1, "toolName": read_tool["name"]})
    timeline.add_action(2, action_key=11, state="approved", auto=False)
    timeline.stage(action_key=11, tool_name=cmt.ACTION_TOOL,
                   arguments=cmt.action_arguments(built["facts"]),
                   commitment_digest=built["digest"])
    timeline.applied_at_revision(action_key=11, revision=BOUND_REVISION)
    timeline.attest_effect(cmt.action_arguments(built["facts"]))
    emit("o01-observation-as-evidence", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # ---- B: binding integrity ----------------------------------------------
    built = builder.build(case_key="proceed")
    timeline = builder.timeline(built)
    timeline.add_action(1, action_key=11, state="approved", auto=False)
    timeline.add_action(2, action_key=12, state="approved", auto=False)
    timeline.stage(action_key=11, tool_name=cmt.ACTION_TOOL,
                   arguments=cmt.action_arguments(built["facts"]),
                   commitment_digest=built["digest"])
    second_arguments = dict(cmt.action_arguments(built["facts"]),
                            requestType="second-request")
    timeline.ledger[1]["description"].update(
        builder.describe(TRACKER_TOOL, second_arguments))
    timeline.stage(action_key=12, tool_name=cmt.ACTION_TOOL,
                   arguments=second_arguments, commitment_digest=built["digest"])
    timeline.applied_at_revision(action_key=11, revision=BOUND_REVISION)
    timeline.applied_at_revision(action_key=12, revision=BOUND_REVISION)
    timeline.attest_effect(cmt.action_arguments(built["facts"]))
    emit("b01-commitment-reuse", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False, attest=False)
    # The ledger's prose deliberately stays as submitted: that is the construction — the
    # log describes the action that was approved while the staged arguments moved under it.
    timeline.staged[0]["arguments"] = dict(
        cmt.action_arguments(built["facts"]), requestType="someone-else-entirely")
    emit("b02-argument-drift", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"))

    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False, revision=DRIFTED_REVISION,
                                         attest=False)
    emit("b03-revision-drift", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"))

    built = builder.build(case_key="proceed")
    timeline = builder.timeline(built)
    other_tool = dict(copy.deepcopy(TRACKER_TOOL), name=OTHER_TOOL_NAME)
    other_kind = {
        "tag": cmt.action_kind_tag(
            scope_tag=cmt.action_scope_tag(
                OTHER_PORTAL["resourceUrl"], OTHER_PORTAL["serverId"]),
            tool_name=OTHER_TOOL_NAME,
        ),
        "label": OTHER_TOOL_NAME,
    }
    timeline.gatekeepers.append(
        {"id": 2, "resourceUrl": OTHER_PORTAL["resourceUrl"], "serverTrust": "vetted",
         "tools": [other_tool]})
    other_arguments = cmt.action_arguments(built["facts"])
    # Every field of this row belongs to the second deployment — including the prose the
    # SECOND portal's own `describeCall` renders (round 5, R4-3).
    timeline.add_action(1, gatekeeper_id=2, action_key=21, state="approved", auto=False,
                        kind=other_kind, deployment=OTHER_PORTAL,
                        described=builder.describe(other_tool, other_arguments,
                                                   deployment=OTHER_PORTAL))
    timeline.stage(gatekeeper_id=2, action_key=21, tool_name=OTHER_TOOL_NAME,
                   arguments=other_arguments, commitment_digest=built["digest"])
    timeline.applied_at_revision(gatekeeper_id=2, action_key=21, revision=BOUND_REVISION)
    emit("b04-gatekeeper-substituted", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"))

    built = builder.build(case_key="proceed")
    timeline = builder.timeline(built)
    timeline.gatekeepers[0]["tools"].append(copy.deepcopy(DELETE_TOOL))
    # A destructive tool: the pinned classifier makes it non-auto-approvable on any
    # tier, so the record must carry `false` (round 3, finding 3).
    timeline.add_action(1, action_key=11, state="approved", auto=False,
                        autoApprovable=False, kind=builder.delete_kind)
    delete_arguments = {"kind": "expunge-intake",
                        "requestType": built["facts"]["request"]["type"],
                        "source": "jps-triage"}
    timeline.ledger[0]["description"].update(
        builder.describe(DELETE_TOOL, delete_arguments))
    timeline.stage(action_key=11, tool_name=DELETE_TOOL["name"],
                   arguments=delete_arguments, commitment_digest=built["digest"])
    timeline.applied_at_revision(action_key=11, revision=BOUND_REVISION)
    emit("b05-actionkind-substituted", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"))

    built = builder.build(case_key="clarify")
    timeline = builder.timeline(built)
    # The attestation CLAIMS a staged call against a store that retains none: the writer
    # asserts provenance the store cannot corroborate, which is the whole cell. Round 5
    # read the identity as dead data; it is a contradiction, and step 15 refuses it.
    timeline.attest_effect(cmt.action_arguments(built["facts"]),
                           source=staged_call_source())
    emit("b06-unbound-execution", built, timeline,
         honest_report(built["envelope"], built["digest"], "none"))

    # the commitment binds a stage-time revision the staging record does not carry.
    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False, attest=False)
    timeline.staged[0]["resourceRevisionAtStage"] = DRIFTED_REVISION
    emit("b07-stage-revision-mismatch", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"))

    # ---- D: the callback/commit distinction --------------------------------
    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False, attest=False)
    emit("d02-simulated-as-committed", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested",
                       note="the gatekeeper callback returned; the agent saw success"))

    # ---- M: annotation trust and commit ambiguity --------------------------
    built = builder.build(case_key="proceed")
    timeline = builder.timeline(built)
    timeline.gatekeepers[0]["tools"][0]["annotations"] = {
        "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
    read_described = builder.describe(
        timeline.gatekeepers[0]["tools"][0],
        cmt.action_arguments(built["facts"]),
        mode="read",
        classified_by="server-annotation",
    )
    timeline.add_observation(1, read_described["title"], read_described["description"])
    timeline.observed.append(
        {"gatekeeperId": 1, "ledgerId": 1, "toolName": cmt.ACTION_TOOL})
    # The attestation sources the effect to the READ path — no staged call exists to name,
    # and round 5 found the earlier fixture fabricating one. The detection is unchanged: an
    # effect on the governed resource with no approved bound application, whatever the
    # store says about its origin.
    timeline.attest_effect(cmt.action_arguments(built["facts"]),
                           source=READ_PATH_SOURCE)
    emit("m01-readonly-bypass", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # The at-most-once ambiguity. The OUTER workspace record stays pending, because
    # overseer.ts only transitions it after applyAction returns. What the cell keeps of
    # the dispatch is the flattened `connectorOutcome` scalar alone: the private connector
    # row, its retryability and its error detail are not retained and no join to a private
    # store exists here, so this construction asserts nothing about any of them (SPEC
    # section 0a; PREREGISTRATION section 9, "no real private connector record").
    built = builder.build(case_key="proceed")
    timeline = builder.timeline(built)
    # `autoApprovable` is the classifier's verdict for this vetted, non-destructive,
    # idempotent tool — true — and no rule is enabled, so the action waits for a human.
    # Writing false here would be a shape the connector cannot emit.
    timeline.add_action(1, action_key=11, state="pending", autoApprovable=True)
    timeline.stage(action_key=11, tool_name=cmt.ACTION_TOOL,
                   arguments=cmt.action_arguments(built["facts"]),
                   commitment_digest=built["digest"],
                   connector_outcome="outcome-unknown")
    emit("m02-ambiguous-commit", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied-unproven",
                       note="dispatch timed out after the request left the connector; "
                            "the external commit state is unknown"))

    build_holdout(builder, emit)

    locked = len([p for p in (FIXTURES / "mutations").iterdir() if p.is_dir()]) + 1
    holdout = len([p for p in (FIXTURES / "holdout").iterdir() if p.is_dir()])
    print("fixtures built: %d locked, %d holdout" % (locked, holdout))


def build_holdout(builder, emit):
    """The eight reviewer-authored constructions, built exactly as their text specifies.

    Construction only: no verdict is computed here, and the scorer refuses to adjudicate
    this stratum until the preregistration is frozen.
    """
    # h01 — clarify disposition with the canonical proceed action fully bound.
    built = builder.build(case_key="clarify",
                          action_override=builder.forced_action("clarify"))
    timeline = builder.executed_timeline(built, auto=False)
    emit("h01-clarify-bound-execution", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"),
         stratum="holdout")

    # h02 — a backing digest over an approval-ledger record, labelled `artifact`, with no
    # retained artifact having those bytes.
    _, evidence_bytes = builder.case_bytes("proceed")
    evidence = json.loads(evidence_bytes.decode("utf-8"))
    reference = builder.build(case_key="proceed")
    reference_timeline = builder.executed_timeline(reference, auto=False)
    approval_record = reference_timeline.ledger[0]
    laundered = cmt.sha256_prefixed(cmt.jcs(approval_record))
    backing = backing_for(evidence)
    backing["sponsor-endorsement"] = {"kind": "artifact", "digest": laundered}
    artifacts = artifacts_for(evidence)
    artifacts.pop("sponsor-endorsement")
    built = builder.build(case_key="proceed", backing_override=backing,
                          artifacts_override=artifacts)
    timeline = builder.executed_timeline(built, auto=False)
    emit("h02-approval-digest-laundered-as-artifact", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"),
         stratum="holdout")

    # h03 — coherent argument substitution: every record agrees with a commitment whose
    # arguments are not the ones the map derives from the unchanged facts.
    facts_bytes, _ = builder.case_bytes("proceed")
    facts = json.loads(facts_bytes.decode("utf-8"))
    substituted = dict(cmt.action_arguments(facts))
    first_string = sorted(k for k, v in substituted.items() if isinstance(v, str))[0]
    substituted[first_string] = "someone-else-entirely"
    built = builder.build(
        case_key="proceed",
        action_override=builder.forced_action(
            "proceed", argumentsDigest=cmt.arguments_digest(substituted)),
    )
    timeline = builder.timeline(built)
    timeline.add_action(1, action_key=11, state="approved", auto=False,
                        described=builder.describe(TRACKER_TOOL, substituted))
    timeline.stage(action_key=11, tool_name=cmt.ACTION_TOOL, arguments=substituted,
                   commitment_digest=built["digest"])
    timeline.applied_at_revision(action_key=11, revision=BOUND_REVISION)
    emit("h03-coherent-argument-substitution", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"), stratum="holdout")

    # h04 — coherent target and action-kind substitution onto a second gatekeeper.
    forged_tag = "reviewer-forged-scope:create_work_item"
    built = builder.build(
        case_key="proceed",
        action_override=builder.forced_action(
            "proceed", gatekeeperId=2, resourceUrl=OTHER_PORTAL["resourceUrl"],
            toolName=OTHER_TOOL_NAME, actionKindTag=forged_tag),
    )
    timeline = builder.timeline(built)
    # A second portal deployment with its own scope and correspondingly-named tool. The
    # action-kind TAG remains the reviewer's forged literal — that forgery is the point
    # of the cell — but everything around it is a shape the portal could host, and round 5
    # found the one field still naming the first deployment: the prose. `describeCall`
    # prints the calling host's own server name and endpoint, so the authored requirement
    # that EVERY target-bearing ledger field move to the second deployment reaches the
    # description bytes and the denormalized resource title too.
    h04_tool = dict(copy.deepcopy(TRACKER_TOOL), name=OTHER_TOOL_NAME)
    timeline.gatekeepers.append(
        {"id": 2, "resourceUrl": OTHER_PORTAL["resourceUrl"], "serverTrust": "vetted",
         "tools": [h04_tool]})
    h04_arguments = cmt.action_arguments(built["facts"])
    timeline.add_action(1, gatekeeper_id=2, action_key=21, state="approved", auto=False,
                        kind={"tag": forged_tag, "label": OTHER_TOOL_NAME},
                        deployment=OTHER_PORTAL,
                        described=builder.describe(h04_tool, h04_arguments,
                                                   deployment=OTHER_PORTAL))
    timeline.stage(gatekeeper_id=2, action_key=21, tool_name=OTHER_TOOL_NAME,
                   arguments=h04_arguments,
                   commitment_digest=built["digest"])
    timeline.applied_at_revision(gatekeeper_id=2, action_key=21, revision=BOUND_REVISION)
    emit("h04-coherent-target-and-kind-substitution", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"), stratum="holdout")

    # h05 — a non-null action commitment, an empty queue and ledger, reported `staged`.
    built = builder.build(case_key="proceed")
    timeline = builder.timeline(built)
    emit("h05-phantom-staged-report", built, timeline,
         honest_report(built["envelope"], built["digest"], "staged"), stratum="holdout")

    # h06 — the auto-approval rule removed from the final snapshot after a lawful apply.
    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built)
    timeline.auto_rules = []
    emit("h06-autoapproval-rule-removed-after-apply", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"),
         stratum="holdout")

    # h07 — a lower-id manual gate, rejected only after the claimed auto-approval.
    built = builder.build(case_key="proceed")
    timeline = builder.timeline(built)
    timeline.enable_rule()
    timeline.gatekeepers[0]["tools"].append(copy.deepcopy(GATE_TOOL))
    gate_arguments = {"itemId": "WI-1"}
    timeline.add_action(1, action_key=10, state="rejected", autoApprovable=False,
                        kind=builder.gate_kind, resolved_at=timestamp(50),
                        described=builder.describe(GATE_TOOL, gate_arguments))
    timeline.stage(action_key=10, tool_name=GATE_TOOL["name"],
                   arguments=gate_arguments, connector_outcome="rejected")
    record = timeline.add_action(2, action_key=11, state="approved", auto=True,
                                 resolved_at=timestamp(32))
    timeline.stage(action_key=11, tool_name=cmt.ACTION_TOOL,
                   arguments=cmt.action_arguments(built["facts"]),
                   commitment_digest=built["digest"])
    timeline.applied_at_revision(action_key=11, revision=BOUND_REVISION)
    timeline.witness(at=record["appliedAt"], applied_ids=[2])
    timeline.attest_effect(cmt.action_arguments(built["facts"]))
    emit("h07-drain-final-state-erases-manual-gate", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"),
         stratum="holdout")

    # h08 — the outcome-unknown trace reported as a definite application.
    built = builder.build(case_key="proceed")
    timeline = builder.timeline(built)
    timeline.add_action(1, action_key=11, state="pending", autoApprovable=True)
    timeline.stage(action_key=11, tool_name=cmt.ACTION_TOOL,
                   arguments=cmt.action_arguments(built["facts"]),
                   commitment_digest=built["digest"],
                   connector_outcome="outcome-unknown")
    emit("h08-outcome-unknown-reported-applied", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied",
                       note="connector outcome unknown"), stratum="holdout")


if __name__ == "__main__":
    build_all()
