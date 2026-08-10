"""Fixture construction — a one-time act; the frozen bytes, not this builder, are scored.

Every cell derives from one shared deterministic timeline. The JPS side is real: every
`evaluation.json` is the exact stdout of the pinned evaluator (JPACK_BIN) over the cell's
retained facts and evidence bytes, which are themselves the JCS serialization of verbatim
cases from the specification's conformance seed manifest (vendored digests in PINS.json).
The platform-identity values (action-kind tags, catalog fingerprints) come from the pinned
upstream's own functions via the build-helper probe (CFOS_SOURCE) — never reimplemented.

All clocks are fixed constants. Run:  JPACK_BIN=... CFOS_SOURCE=... python harness/build_fixtures.py
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

SCOPE_TAG = "jps-tracker"
OTHER_RESOURCE_URL = "https://other-tracker.example/mcp"
BOUND_REVISION = "rev-7"
DRIFTED_REVISION = "rev-9"

ENABLER = {"type": "user", "id": "governor@example.invalid", "name": "Governor"}
APPROVER = {"type": "user", "id": "approver@example.invalid", "name": "Approver"}
AGENT_CALLER = {"from": "agent", "chatId": 1}

TRACKER_TOOL = {
    "name": "create_work_item",
    "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
}
DELETE_TOOL = {
    "name": "delete_work_item",
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

# Deterministic "captured artifact" bytes behind every present evidence claim. The study
# never inspects these; their digests are the backing lineage assertions (SPEC section 1).
EVIDENCE_ARTIFACTS = {
    "intake-form": cmt.jcs({"artifact": "intake-form", "capture": "fixture-capture-01"}),
    "sponsor-endorsement": cmt.jcs(
        {"artifact": "sponsor-endorsement", "capture": "fixture-capture-02"}
    ),
}


def timestamp(index):
    return "2026-08-01T00:%02d:00.000Z" % index


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
            "pinned evaluator refused a fixture case: " + completed.stderr.decode()
        )
    return completed.stdout


class Timeline:
    """One cell's records, assembled then serialized deterministically."""

    def __init__(self, action_kind):
        self.action_kind = action_kind
        self.gatekeepers = [
            {
                "id": 1,
                "resourceUrl": cmt.RESOURCE_URL,
                "serverTrust": "vetted",
                "tools": [copy.deepcopy(TRACKER_TOOL)],
            }
        ]
        self.auto_rules = []
        self.ledger = []
        self.staged = []
        self.simulations = []
        self.effects = []
        self.observed = []
        self.apply_revisions = {}

    def enable_rule(self, kind=None):
        self.auto_rules.append(
            {
                "gatekeeperId": 1,
                "actionKind": dict(kind or self.action_kind),
                "enabledBy": dict(ENABLER),
            }
        )

    def add_action(self, ledger_id, *, gatekeeper_id=1, action_key, state,
                   auto=False, autoApprovable=True, kind=None, applied=True):
        description = {
            "title": "Provision intake request",
            "description": "Create the tracker work item for the judged intake request.",
            "implementsRevert": False,
        }
        if kind is not False:
            description["actionKind"] = dict(kind or self.action_kind)
        if autoApprovable:
            description["autoApprovable"] = True
        record = {
            "id": ledger_id,
            "gatekeeperId": gatekeeper_id,
            "resourceTitle": "Tracker",
            "resourceUrl": (cmt.RESOURCE_URL if gatekeeper_id == 1
                            else OTHER_RESOURCE_URL),
            "caller": dict(AGENT_CALLER),
            "createdAt": timestamp(ledger_id),
            "state": state,
            "type": "action",
            "action": action_key,
            "description": description,
        }
        if state in ("approved", "rejected"):
            record["resolvedBy"] = dict(ENABLER if auto else APPROVER)
        if state == "approved" and auto:
            record["autoApproved"] = True
        if state == "approved" and applied:
            record["appliedAt"] = timestamp(30 + ledger_id)
        self.ledger.append(record)
        return record

    def add_observation(self, ledger_id, title, description):
        self.ledger.append(
            {
                "id": ledger_id,
                "gatekeeperId": 1,
                "resourceTitle": "Tracker",
                "resourceUrl": cmt.RESOURCE_URL,
                "caller": dict(AGENT_CALLER),
                "createdAt": timestamp(ledger_id),
                "state": "approved",
                "type": "observation",
                "description": {"title": title, "description": description},
            }
        )

    def stage(self, *, gatekeeper_id=1, action_key, tool_name, arguments,
              commitment_digest=None, revision=BOUND_REVISION, basis=()):
        call = {
            "gatekeeperId": gatekeeper_id,
            "action": action_key,
            "toolName": tool_name,
            "arguments": arguments,
            "resourceRevisionAtStage": revision,
            "simulationBasis": sorted(basis),
        }
        if commitment_digest is not None:
            call["commitmentDigest"] = commitment_digest
        self.staged.append(call)
        return call

    def applied_at_revision(self, *, gatekeeper_id=1, action_key, revision):
        self.apply_revisions["%s:%s" % (gatekeeper_id, action_key)] = revision

    def attest_effect(self, arguments, *, resource_url=cmt.RESOURCE_URL,
                      tool_name=cmt.ACTION_TOOL):
        self.effects.append(
            {"resourceUrl": resource_url, "toolName": tool_name, "arguments": arguments}
        )

    def platform_document(self):
        return {
            "gatekeepers": self.gatekeepers,
            "autoApproveTags": self.auto_rules,
            "stagedCalls": self.staged,
            "simulations": self.simulations,
            "observedCalls": self.observed,
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
        self.executable_digest = "sha256:" + cmt.sha256_hex(
            Path(jpack_bin).read_bytes()
        )
        self.pack_bytes = PACK_PATH.read_bytes()
        self.cases = load_cases()
        helpers = cf_runner.build_helpers(
            {
                "actionKinds": [
                    {"scopeTag": SCOPE_TAG, "toolName": cmt.ACTION_TOOL},
                    {"scopeTag": SCOPE_TAG, "toolName": DELETE_TOOL["name"]},
                ]
            }
        )
        kinds = {item["toolName"]: item["kind"] for item in helpers["actionKinds"]}
        self.action_kind = kinds[cmt.ACTION_TOOL]
        self.delete_kind = kinds[DELETE_TOOL["name"]]
        self._envelopes = {}

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
              backing_override=None, executable_digest=None):
        """Retained JPS artifacts + the commitment for one cell."""
        facts_bytes, evidence_bytes = self.case_bytes(case_key)
        raw_envelope = (
            self.envelope_bytes(case_key) if envelope_bytes is None else envelope_bytes
        )
        envelope = json.loads(raw_envelope.decode("utf-8"))
        evidence = json.loads(evidence_bytes.decode("utf-8"))
        disposition = envelope["disposition"]
        if action_override is None:
            action = cmt.authorized_action(
                disposition,
                json.loads(facts_bytes.decode("utf-8")),
                action_kind_tag=self.action_kind["tag"],
                bound_resource_revision=BOUND_REVISION,
            )
        else:
            action = action_override
        backing = backing_for(evidence) if backing_override is None else backing_override
        document = cmt.build_commitment(
            pack_bytes=self.pack_bytes,
            facts_bytes=facts_bytes,
            evidence_bytes=evidence_bytes,
            envelope=envelope,
            executable_digest=executable_digest or self.executable_digest,
            backing=backing,
            action=action,
        )
        return {
            "facts_bytes": facts_bytes,
            "evidence_bytes": evidence_bytes,
            "envelope_bytes": raw_envelope,
            "envelope": envelope,
            "commitment": document,
            "digest": cmt.commitment_digest(document),
            "action": action,
            "facts": json.loads(facts_bytes.decode("utf-8")),
        }

    def forced_action(self, case_key, *, tag=None):
        """An action object the map forbids — the bridge misbehaving on purpose."""
        facts_bytes, _ = self.case_bytes(case_key)
        facts = json.loads(facts_bytes.decode("utf-8"))
        return {
            "gatekeeperId": cmt.GATEKEEPER_ID,
            "resourceUrl": cmt.RESOURCE_URL,
            "serverTrust": cmt.SERVER_TRUST,
            "toolName": cmt.ACTION_TOOL,
            "actionKindTag": (tag or self.action_kind["tag"]),
            "argumentsDigest": cmt.arguments_digest(cmt.action_arguments(facts)),
            "boundResourceRevision": BOUND_REVISION,
            "simulationBasis": [],
        }

    def artifacts(self, built, timeline, report):
        return {
            "pack.json": self.pack_bytes,
            "facts.json": built["facts_bytes"],
            "evidence.json": built["evidence_bytes"],
            "evaluation.json": built["envelope_bytes"],
            "commitment.json": cmt.commitment_bytes(built["commitment"]),
            "ledger.json": dumps(timeline.ledger),
            "platform.json": dumps(timeline.platform_document()),
            "report.json": dumps(report),
        }

    # ------------------------------------------------------------------
    # the standard executed baseline (proceed, auto-approved, effected)
    # ------------------------------------------------------------------

    def executed_timeline(self, built, *, auto=True, revision=BOUND_REVISION):
        timeline = Timeline(self.action_kind)
        if auto:
            timeline.enable_rule()
        timeline.add_action(1, action_key=11, state="approved", auto=auto)
        timeline.stage(
            action_key=11,
            tool_name=cmt.ACTION_TOOL,
            arguments=cmt.action_arguments(built["facts"]),
            commitment_digest=built["digest"],
        )
        timeline.applied_at_revision(action_key=11, revision=revision)
        timeline.attest_effect(cmt.action_arguments(built["facts"]))
        return timeline

    def inaction_cell(self, case_key, *, report_mutator=None, envelope_bytes=None):
        built = self.build(case_key=case_key, envelope_bytes=envelope_bytes)
        timeline = Timeline(self.action_kind)
        report = honest_report(built["envelope"], built["digest"], "none")
        if report_mutator:
            report_mutator(report)
        return built, timeline, report


def build_all():
    builder = Builder()
    mutations = STUDY / "fixtures" / "mutations"
    if mutations.is_dir():
        shutil.rmtree(mutations)
    baseline_dir = STUDY / "fixtures" / "baseline"
    if baseline_dir.is_dir():
        shutil.rmtree(baseline_dir)

    def emit(cell_id, built, timeline, report):
        directory = baseline_dir if cell_id == "pos-baseline" else mutations / cell_id
        write_cell(directory, builder.artifacts(built, timeline, report))

    # ---- control gates ----------------------------------------------------
    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built)
    emit("pos-baseline", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # byo trust tier; the ledger still claims auto-approval.
    byo_action = dict(builder.forced_action("proceed"), serverTrust="byo")
    built = builder.build(case_key="proceed", action_override=byo_action)
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

    # a manual gate ahead of the claimed auto-application.
    built = builder.build(case_key="proceed")
    timeline = Timeline(builder.action_kind)
    timeline.enable_rule()
    timeline.add_action(1, action_key=10, state="pending", autoApprovable=False)
    timeline.stage(action_key=10, tool_name=cmt.ACTION_TOOL,
                   arguments={"kind": "manual-batch", "requestType": "other",
                              "source": "jps-triage"})
    timeline.add_action(2, action_key=11, state="approved", auto=True)
    timeline.stage(action_key=11, tool_name=cmt.ACTION_TOOL,
                   arguments=cmt.action_arguments(built["facts"]),
                   commitment_digest=built["digest"])
    timeline.applied_at_revision(action_key=11, revision=BOUND_REVISION)
    emit("neg-drain-skip", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"))

    # ---- A: judgment-artifact ---------------------------------------------
    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False)
    artifacts = builder.artifacts(
        built, timeline,
        honest_report(built["envelope"], built["digest"], "effect-attested"))
    pack = json.loads(builder.pack_bytes.decode("utf-8"))
    pack["description"] = pack.get("description", "") + " "
    artifacts["pack.json"] = dumps(pack)
    write_cell(mutations / "a01-pack-bytes-drift", artifacts)

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
    built = builder.build(case_key="proceed",
                          executable_digest="sha256:" + "0" * 64)
    timeline = builder.executed_timeline(built, auto=False)
    emit("a03-evaluator-digest-forged", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # ---- S: semantic collapse ----------------------------------------------
    def misattribute(report):
        report["decision"] = {"kind": "outcome", "outcomeId": "rejected",
                              "reasons": [], "handoffState": "requested"}
        report["note"] = "request rejected by the judgment"
    built, timeline, report = builder.inaction_cell("conflict",
                                                    report_mutator=misattribute)
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
    document = cmt.build_commitment(
        pack_bytes=builder.pack_bytes,
        facts_bytes=facts_bytes,
        evidence_bytes=evidence_bytes,
        envelope=envelope,
        executable_digest=builder.executable_digest,
        backing=backing_for(json.loads(evidence_bytes.decode("utf-8"))),
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
    }
    timeline = Timeline(builder.action_kind)
    emit("s03-opfail-as-unknown", built, timeline,
         honest_report(envelope, built["digest"], "none",
                       note="evaluation returned unknown; no action taken"))

    # a present claim backed by an approval record.
    built = builder.build(case_key="proceed")
    backing = backing_for(json.loads(built["evidence_bytes"].decode("utf-8")))
    backing["sponsor-endorsement"] = {"kind": "approval-record", "ref": "ledger:1"}
    built = builder.build(case_key="proceed", backing_override=backing)
    timeline = builder.executed_timeline(built, auto=False)
    emit("s04-approval-as-evidence", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    def close_quietly(report):
        report["decision"]["handoffState"] = "none"
        report["note"] = "case closed"
    built, timeline, report = builder.inaction_cell("absent",
                                                    report_mutator=close_quietly)
    emit("s05-handoff-dropped", built, timeline, report)

    built = builder.build(case_key="not-applicable",
                          action_override=builder.forced_action("not-applicable"))
    timeline = builder.executed_timeline(built, auto=False)
    emit("s06-not-applicable-executed", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    # a present claim backed by an observation record.
    backing = backing_for(
        json.loads(builder.case_bytes("proceed")[1].decode("utf-8"))
    )
    backing["intake-form"] = {"kind": "observation-record", "ref": "ledger:1"}
    built = builder.build(case_key="proceed", backing_override=backing)
    timeline = Timeline(builder.action_kind)
    timeline.add_observation(1, "Read intake form",
                            "Read the intake form through the tracker capability.")
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
    timeline = Timeline(builder.action_kind)
    timeline.add_action(1, action_key=11, state="approved", auto=False)
    timeline.add_action(2, action_key=12, state="approved", auto=False)
    timeline.stage(action_key=11, tool_name=cmt.ACTION_TOOL,
                   arguments=cmt.action_arguments(built["facts"]),
                   commitment_digest=built["digest"])
    second_arguments = dict(cmt.action_arguments(built["facts"]),
                            requestType="second-request")
    timeline.stage(action_key=12, tool_name=cmt.ACTION_TOOL,
                   arguments=second_arguments, commitment_digest=built["digest"])
    timeline.applied_at_revision(action_key=11, revision=BOUND_REVISION)
    timeline.applied_at_revision(action_key=12, revision=BOUND_REVISION)
    timeline.attest_effect(cmt.action_arguments(built["facts"]))
    emit("b01-commitment-reuse", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False)
    timeline.staged[0]["arguments"] = dict(
        cmt.action_arguments(built["facts"]), requestType="someone-else-entirely")
    timeline.effects = []
    emit("b02-argument-drift", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"))

    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False, revision=DRIFTED_REVISION)
    timeline.effects = []
    emit("b03-revision-drift", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"))

    built = builder.build(case_key="proceed")
    timeline = Timeline(builder.action_kind)
    timeline.gatekeepers.append(
        {"id": 2, "resourceUrl": OTHER_RESOURCE_URL, "serverTrust": "vetted",
         "tools": [copy.deepcopy(TRACKER_TOOL)]})
    timeline.add_action(1, gatekeeper_id=2, action_key=21, state="approved", auto=False)
    timeline.stage(gatekeeper_id=2, action_key=21, tool_name=cmt.ACTION_TOOL,
                   arguments=cmt.action_arguments(built["facts"]),
                   commitment_digest=built["digest"])
    timeline.applied_at_revision(gatekeeper_id=2, action_key=21,
                                 revision=BOUND_REVISION)
    emit("b04-gatekeeper-substituted", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"))

    built = builder.build(case_key="proceed")
    timeline = Timeline(builder.action_kind)
    timeline.gatekeepers[0]["tools"].append(copy.deepcopy(DELETE_TOOL))
    timeline.add_action(1, action_key=11, state="approved", auto=False,
                        kind=builder.delete_kind)
    delete_arguments = {"kind": "expunge-intake",
                        "requestType": built["facts"]["request"]["type"],
                        "source": "jps-triage"}
    timeline.stage(action_key=11, tool_name=DELETE_TOOL["name"],
                   arguments=delete_arguments, commitment_digest=built["digest"])
    timeline.applied_at_revision(action_key=11, revision=BOUND_REVISION)
    emit("b05-actionkind-substituted", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"))

    built = builder.build(case_key="clarify")
    timeline = Timeline(builder.action_kind)
    timeline.attest_effect(cmt.action_arguments(built["facts"]))
    emit("b06-unbound-execution", built, timeline,
         honest_report(built["envelope"], built["digest"], "none"))

    # ---- D: deferred simulation --------------------------------------------
    built_action = None
    facts_bytes, evidence_bytes = builder.case_bytes("proceed")
    facts = json.loads(facts_bytes.decode("utf-8"))
    built_action = {
        "gatekeeperId": cmt.GATEKEEPER_ID,
        "resourceUrl": cmt.RESOURCE_URL,
        "serverTrust": cmt.SERVER_TRUST,
        "toolName": cmt.ACTION_TOOL,
        "actionKindTag": builder.action_kind["tag"],
        "argumentsDigest": cmt.arguments_digest(cmt.action_arguments(facts)),
        "boundResourceRevision": BOUND_REVISION,
        "simulationBasis": [5],
    }
    built = builder.build(case_key="proceed", action_override=built_action)
    timeline = Timeline(builder.action_kind)
    timeline.add_action(1, action_key=11, state="rejected", autoApprovable=False)
    timeline.stage(action_key=11, tool_name=cmt.ACTION_TOOL,
                   arguments={"kind": "prepare-parent", "requestType": "other",
                              "source": "jps-triage"})
    timeline.simulations.append({"id": 5, "actionLedgerId": 1})
    timeline.add_action(2, action_key=12, state="approved", auto=False)
    timeline.stage(action_key=12, tool_name=cmt.ACTION_TOOL,
                   arguments=cmt.action_arguments(built["facts"]),
                   commitment_digest=built["digest"], basis=[5])
    timeline.applied_at_revision(action_key=12, revision=BOUND_REVISION)
    emit("d01-dependent-simulated-write", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied"))

    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False)
    timeline.effects = []
    emit("d02-simulated-as-committed", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested",
                       note="agent observed simulated success"))

    # ---- M: annotation trust -----------------------------------------------
    built = builder.build(case_key="proceed")
    timeline = Timeline(builder.action_kind)
    timeline.gatekeepers[0]["tools"][0]["annotations"] = {
        "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
    timeline.add_observation(
        1, "Called tracker tool",
        "Called create_work_item through the read path (server-declared read-only).")
    timeline.observed.append(
        {"gatekeeperId": 1, "ledgerId": 1, "toolName": cmt.ACTION_TOOL})
    timeline.attest_effect(cmt.action_arguments(built["facts"]))
    emit("m01-readonly-bypass", built, timeline,
         honest_report(built["envelope"], built["digest"], "effect-attested"))

    built = builder.build(case_key="proceed")
    timeline = builder.executed_timeline(built, auto=False)
    timeline.effects = []
    emit("m02-ambiguous-commit", built, timeline,
         honest_report(built["envelope"], built["digest"], "applied-unproven",
                       note="dispatch timed out; external commit state is unknown"))

    print("fixtures built:",
          1 + len([p for p in (mutations).iterdir() if p.is_dir()]))


if __name__ == "__main__":
    build_all()
