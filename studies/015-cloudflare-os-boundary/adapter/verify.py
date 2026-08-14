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
  The one contextual member — the revision the resource stood at when the action was
  staged — comes from the store and has its own checks.
* **No silent suppression.** Every binding check runs; the first failure in registered
  order is the adjudicated code, and every other failing code is published alongside it
  as `suppressed`. "Exactly one layer" is then a statement about what was observed, not
  an artifact of returning early.
"""

import hashlib
import json
import re
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
    "ledger-lifecycle-invalid",
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

EXECUTION_STATES = (
    "none",
    "staged",
    "rejected",
    "applied",
    "applied-unproven",
    "effect-attested",
)
# The connector outcome an instrumented Gatekeeper retains per staged call. `committed`
# and `failed` are determinate; `outcome-unknown` is the platform's own at-most-once
# ambiguity, the only state that supports an `applied-unproven` report.
# `rejected` is the private record's state when the approver refuses. The two writes are
# ordered, not atomic: `action-store.ts:209` writes `rejected` before
# `overseer.ts:7729-7732` updates the outer row, which is the reject-side crash window the
# matrix below admits (R7-1). Round 7 wrote "in the same transaction" here, contradicting
# the window it derived from the same two locations further down this block (R8-2).
CONNECTOR_OUTCOMES = (
    "pending",
    "committed",
    "failed",
    "rejected",
    "outcome-unknown",
)

# The registered compatibility matrix (SPEC section 5, "Retained outcome compatibility"),
# derived from the pinned source. Round 6 (R6-2) found `applied` refusing only
# `outcome-unknown` and nothing correlating the flattened scalar with the outer row at
# all, so a store carrying `connectorOutcome: "rejected"` on an `approved` record with an
# `applied` report came out completely green — against a README that says green means the
# retained store is internally consistent.
#
# Which outer lifecycle state each scalar can stand beside:
#
# * `approved` is written at one chokepoint, *after* `await gatekeeper.applyAction(...)`
#   returns (`overseer.ts:2490-2497`). The connector's apply reaches its success tail —
#   `state = "applied"` (`action-store.ts:172-173`) — only when the dispatch returned;
#   every other path throws (`:136-144` pre-state guards, `:155-169` the catch that writes
#   `failed` and rethrows), and a throw propagates out of `applyAction` so the assignment
#   is never reached. Therefore `approved` admits `committed` and nothing else.
# * `rejected` is written at one path, after `await gatekeeper.rejectAction(...)`
#   (`overseer.ts:7707-7732`); the connector's `reject` proceeds only from `pending` and
#   throws for `applying`, `applied` and `failed` (`action-store.ts:201-211`). Therefore
#   `rejected` admits `rejected`.
# * `pending` is every history in which the outer transition never happened: an
#   undispatched call (`pending`), a determinate failure (`failed` — `action-store.ts:157-158`
#   under the pinned source's own `callMayHaveTakenEffect` false), and the at-most-once
#   ambiguity (the same lines with it true, which is `outcome-unknown` here). It also
#   admits BOTH determinate resolutions, through the two symmetric crash windows, because
#   each connector path persists its own record before the outer row is written:
#   `action-store.ts:196` saves `applied` before `applyAction` returns, and
#   `action-store.ts:209` writes `rejected` before `overseer.ts:7729-7732` updates the
#   outer row. A Durable Object that dies in either window leaves exactly that pair
#   retained. Round 7 (R7-1) found only the first window admitted, which refused a
#   producible history on the reject side; what the report table below refuses is not the
#   history but any *claim* about it.
LIFECYCLE_CONNECTOR_OUTCOMES = {
    "pending": ("committed", "failed", "outcome-unknown", "pending", "rejected"),
    "approved": ("committed",),
    "rejected": ("rejected",),
}

# And which scalar each report state may claim of the BOUND call. `none` names no call, so
# it names no outcome.
#
# Round 6 registered a *gap* here: a bound call the approver refused had no supportable
# report state, because the five-state vocabulary had none for "staged, then refused".
# Round 7 (R7-1) withdrew that framing — an ordinary completed rejection is the most
# ordinary history the queue produces, and a store that cannot say so is a store that
# reports it wrongly or not at all. `rejected` is a value of the report's `execution`
# field, not a binding verdict code, and it is the one vocabulary member this round adds.
REPORT_CONNECTOR_OUTCOMES = {
    "staged": ("failed", "pending"),
    "rejected": ("rejected",),
    "applied": ("committed",),
    "applied-unproven": ("outcome-unknown",),
    "effect-attested": ("committed",),
}

# The ONE serialized form the platform can write: `Date.prototype.toISOString()` output,
# `YYYY-MM-DDTHH:mm:ss.sssZ` — four-digit year, three fraction digits, UTC, no offsets, no
# lowercase separators, no leap second. Round 5 narrowed the grammar to "strict RFC 3339",
# and round 6 (R6-5) found that still neither strict nor identical across the two layers:
# RFC 3339 admits offsets and any fraction width, this side parsed the fraction through
# `float` (so an extreme valid-shaped fraction raised `OverflowError` out of a check
# instead of returning a result), and the node side finished with `Date.parse`, which
# normalizes an impossible calendar date and collapses sub-millisecond neighbours.
#
# One form, validated identically on both sides, and the *string itself* is the instant:
# the form is fixed-width and UTC, so lexicographic order is chronological order and no
# side does arithmetic at all. Nothing here can raise.
#
# Round 7 (the R6-5 residue, filed R7-3) found "identically" still false in two
# ways that only this side had: Python's `\d` is Unicode-aware, so `٢٠٢٦` and its
# neighbours matched a grammar registered as the ASCII output of `toISOString()`, and
# `.match(...$)` accepts a trailing `\n`, because Python's `$` also matches before a final
# newline. JavaScript's `\d` is ASCII and its `$` is end-of-input, so the node side
# refused both — one store, two verdicts, and a manual-approval construction that came out
# binding-`pass` here. The class is spelled `[0-9]` and the match is `fullmatch`.
_PLATFORM_INSTANT = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})\.([0-9]{3})Z"
)
_MONTH_LENGTHS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _days_in_month(year, month):
    if month == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
        return 29
    return _MONTH_LENGTHS[month - 1]


def platform_instant(value):
    """The canonical stamp a serialized platform `Date` is, or None if it is not one.

    Returns the validated string, which is the comparable instant: `probes/ceremony.ts`
    applies the same grammar and the same calendar check to the same fields and compares
    the same bytes.
    """
    match = _PLATFORM_INSTANT.fullmatch(value) if isinstance(value, str) else None
    if match is None:
        return None
    year, month, day, hour, minute, second = (int(match.group(i)) for i in range(1, 7))
    if not 1 <= month <= 12:
        return None
    if not 1 <= day <= _days_in_month(year, month):
        return None
    if hour > 23 or minute > 59 or second > 59:
        return None
    return value


# The platform's identities are JSON numbers assigned from monotonic counters starting at
# 1 (`overseer.ts:418-422`) and read back through V8, so an identity is a non-Boolean
# integer in [1, 2^53-1] — and nothing else. Round 6 (R6-3) found the two layers
# disagreeing about that: this side deduplicated `repr(id)`, so a second gatekeeper with
# `id: 1.0` survived uniqueness and then aliased `id: 1` at lookup, while the node side
# stringified both as `"1"` and refused.
#
# Round 7 (R7-2) found that repair still leaving one definition per side, because it was
# written against the value each language *reads back* rather than against the token the
# store was written with. `json.loads("1.0")` is a `float` here and refused;
# `JSON.parse("1.0")` is `1` there and `Number.isSafeInteger` accepts it. Round 6's own
# duplicate-id regressions masked that, since a duplicate refuses on both sides for a
# different reason.
#
# So the definition is **lexical**, and it is the same sentence twice: an identity is
# written as a plain digit-only integer token — no sign, no `.`, no exponent, and not a
# Boolean — and reads back inside `[1, 2^53-1]`. This side keeps each number's own token
# through `json.loads`'s two number hooks (`Cell.store`); `probes/ceremony.ts` reads the
# same token out of `JSON.parse`'s reviver `context.source`.
MAX_SAFE_INTEGER = 2 ** 53 - 1
_INTEGER_LEXEME = re.compile(r"[0-9]+")


class _LexicalInt(int):
    """A retained JSON integer, carrying the exact token it was written as."""

    def __new__(cls, token):
        number = super().__new__(cls, token)
        number.lexeme = token
        return number


class _LexicalFloat(float):
    """A retained JSON number with a fraction or an exponent, and its own token.

    Constructed rather than refused so that a store carrying one is *read* and then
    refused by the checks that care, exactly as before — the token is what disqualifies
    it, and `float()` never raises on a valid JSON number (an overflowing exponent gives
    `inf`, which no range check admits).
    """

    def __new__(cls, token):
        number = super().__new__(cls, token)
        number.lexeme = token
        return number


def _platform_id(value):
    """True iff `value` is an identity the platform can have assigned.

    Fail-closed on provenance as well as on shape: a number with no retained token never
    came out of `Cell.store`, so it is not something the store said and is not an
    identity here. Booleans and strings carry no token either.
    """
    lexeme = getattr(value, "lexeme", None)
    if lexeme is None or _INTEGER_LEXEME.fullmatch(lexeme) is None:
        return False
    return 1 <= value <= MAX_SAFE_INTEGER


def _resolver_problems(resolver, label):
    """An `AiChatAuthorInfo` is a complete triple upstream (`api.ts:1777`).

    Round 5 found only `.id` was ever compared, so a resolver carrying the right id under
    a different name or actor type read as the same author. The whole tuple is the
    identity on both sides now; here it is the tuple's *shape* that is held, because the
    binding layer has no independent attribution to compare against.
    """
    if not isinstance(resolver, dict):
        return ["%s records a resolver that is not an author record" % label]
    problems = []
    if resolver.get("type") not in ("user", "agent", "gadget"):
        problems.append(
            "%s records resolver type %r, which is out of the platform's own vocabulary"
            % (label, resolver.get("type"))
        )
    for member in ("id", "name"):
        value = resolver.get(member)
        if not isinstance(value, str) or not value:
            problems.append("%s records a resolver with no %s" % (label, member))
    return problems


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

    def store(self, name):
        """The retained store, parsed with every number's own token kept beside it.

        Identities live in `ledger.json` and `platform.json` and nowhere else, and what
        makes a number an identity is the token it was written as, not the value it reads
        back as (R7-2). `parse_int` and `parse_float` are the only way to see that token.
        They are applied here rather than in `json()` deliberately: no other retained
        artifact is read for identities, so nothing else — a canonical disposition, a
        facts document, a published report — is parsed through a number type it never
        needed.
        """
        raw = self.bytes(name)
        if raw is None:
            return None
        try:
            return json.loads(
                raw.decode("utf-8"),
                parse_int=_LexicalInt,
                parse_float=_LexicalFloat,
            )
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

    # -- derived views -------------------------------------------------

    @property
    def bound_calls(self):
        return [
            call
            for call in self.platform.get("stagedCalls") or []
            if call.get("commitmentDigest") == self.digest
        ]

    @property
    def subject_calls(self):
        """Every staged call against the judged subject, *however it is labelled*.

        Round 2's blocker: selecting calls by the commitment digest meant a second
        same-subject call carrying a different digest, or none at all, was invisible to
        every check — so a store could hold two executions under a map that authorizes
        one.

        This is the **authorization scope**: every call to the tool and resource the map
        governs, whatever digest it carries or omits, and whatever arguments it renders.
        Scope must not be narrowed by the arguments, because an attacker chooses those —
        round 3 found that an exact-arguments filter let a changed-argument twin sit
        outside the count. Nor may it be conditioned on the judgment being executable: a
        commitment to inaction authorizes zero calls, so any call in scope is the
        violation, and an earlier version that keyed on the derived action silently
        disabled the whole check on that half of the map.

        Exact arguments still identify *the judged action* — that is `matching_effects`'
        job — but they do not bound what the decision is answerable for.
        """
        subject = []
        for call in self.platform.get("stagedCalls") or []:
            gatekeeper = self.gatekeeper(call.get("gatekeeperId"))
            if call.get("toolName") != cmt.ACTION_TOOL:
                continue
            if gatekeeper is None or gatekeeper.get("resourceUrl") != cmt.RESOURCE_URL:
                continue
            subject.append(call)
        return subject

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

    def calls_for(self, entry):
        """The reverse join: every staged call sharing an action row's identity.

        Cardinality is the caller's business, exactly as it is for `records_for` — a
        store holding two of either has more than one reading and is refused at step 10.
        """
        return [
            call
            for call in self.platform.get("stagedCalls") or []
            if call.get("gatekeeperId") == entry.get("gatekeeperId")
            and call.get("action") == entry.get("action")
        ]

    @property
    def applied_bound(self):
        applied = []
        for call in self.bound_calls:
            for record in self.records_for(call):
                if record.get("state") == "approved":
                    applied.append((call, record))
        return applied

    @property
    def governed_effects(self):
        """Every attested effect on the governed tool and resource.

        Scoped like `subject_calls`, and for the same reason: round 4 found that
        filtering effects by the exact derived arguments let a changed-argument effect
        sit outside the inventory entirely. What the decision is answerable for is the
        tool and resource the map governs; the arguments then say whether an effect is
        *the judged action* or a different one on the same governed surface.
        """
        matches = []
        for effect in self.platform.get("effects") or []:
            if effect.get("toolName") != cmt.ACTION_TOOL:
                continue
            if effect.get("resourceUrl") != cmt.RESOURCE_URL:
                continue
            matches.append(effect)
        return matches

    @property
    def matching_effects(self):
        """Governed effects whose arguments are the judged action's."""
        if self.facts is None:
            return []
        expected = cmt.arguments_digest(cmt.action_arguments(self.facts))
        return [
            effect
            for effect in self.governed_effects
            if cmt.arguments_digest(effect.get("arguments")) == expected
        ]

    def governed_inventory(self):
        """Approved ledger action rows, classified against the governed tool and resource.

        Returns `(governed, problems)`. A row is governed when its own denormalized
        resource — or, absent one, the resource of the gatekeeper it names — is the
        resource the map governs, **and** its own retained action-kind label is the tool
        the map governs. Counted from the LEDGER, not by joining through retained staged
        calls: round 4 found that an approved governed row with no staged call was simply
        invisible.

        **Classified by the row's own record, never by a joined call.** Round 5 removed a
        discard keyed on the staged call's tool name, and round 6 (R6-6) found the
        replacement resource-only: a coherent `tracker_close_work_item` approval on the
        governed resource was counted against the create-work-item authorization and
        refused as `binding-reuse`, although the SPEC's normative scope is "the governed
        tool and resource … and nothing else". The label the row itself retains is what
        classifies it, in both directions: a target-tool row stays governed even when a
        staged call sharing its identity says otherwise, and a coherently different-tool
        row is out of scope the same way a different-resource row is.

        **Nothing is discarded silently.** A row that cannot be classified — an unretained
        gatekeeper, no resource anywhere, a denormalized resource its own gatekeeper
        contradicts, no retained action-kind label, or an action-kind tag that is absent,
        empty, or not the whole tag this deployment derives for that row's own label — is
        reported as a problem, which step 10 refuses.
        """
        governed, problems = [], []
        for entry in self.ledger_actions:
            if entry.get("state") != "approved":
                continue
            label = "ledger id %s" % entry.get("id")
            gatekeeper = self.gatekeeper(entry.get("gatekeeperId"))
            row_resource = entry.get("resourceUrl")
            gate_resource = gatekeeper.get("resourceUrl") if gatekeeper else None
            if gatekeeper is None:
                problems.append(
                    "%s names gatekeeper %r, which the retained store does not hold, so "
                    "the row cannot be inventoried"
                    % (label, entry.get("gatekeeperId"))
                )
                continue
            if (
                row_resource is not None
                and gate_resource is not None
                and row_resource != gate_resource
            ):
                problems.append(
                    "%s carries resource %r while the gatekeeper it names carries %r"
                    % (label, row_resource, gate_resource)
                )
                continue
            resource = row_resource if row_resource is not None else gate_resource
            if resource is None:
                problems.append(
                    "%s carries no resource and its gatekeeper supplies none" % label
                )
                continue
            if resource != cmt.RESOURCE_URL:
                continue
            kind = (entry.get("description") or {}).get("actionKind") or {}
            tool, tag = kind.get("label"), kind.get("tag")
            if not isinstance(tool, str) or not tool:
                problems.append(
                    "%s is on the governed resource and retains no action-kind label, so "
                    "it cannot be classified against the governed tool" % label
                )
                continue
            # The tag is REQUIRED and is compared whole. `actionKindFor` (`tools.ts:94`)
            # derives it from the calling deployment's scope tag and the tool name, so for
            # a row on the governed resource there is exactly one tag its own label can
            # stand beside, and `adapter/commitment.py` already owns that derivation
            # (double encoding included). Round 6 compared only the suffix after the last
            # literal colon and skipped the comparison entirely when the tag was absent or
            # empty, so round 7 (R7-5) reached a green with a foreign scope and with no tag
            # at all — while the pinned connector emits a nonempty, deployment-derived
            # complete tag on every record it submits, and a green ceremony claims the
            # store agrees with itself. A row whose tag is not the derived one describes
            # two different actions to two different readers and is classified as neither.
            if tag != cmt.action_kind_tag(tool_name=tool):
                problems.append(
                    "%s is on the governed resource and carries action-kind tag %r beside "
                    "label %r; this deployment derives %r for that label, so what the row "
                    "records cannot be classified"
                    % (label, tag, tool, cmt.action_kind_tag(tool_name=tool))
                )
                continue
            if tool == cmt.ACTION_TOOL:
                governed.append(entry)
        return governed, problems

    @property
    def governed_applications(self):
        return self.governed_inventory()[0]

    def gatekeeper(self, gatekeeper_id):
        for candidate in self.platform.get("gatekeepers") or []:
            if candidate.get("id") == gatekeeper_id:
                return candidate
        return None

    @property
    def handoff_state(self):
        return (self.disposition.get("handoff") or {}).get("state")


# The registered drain-witness shape (SPEC section 0's retained-record model). The witness
# is study instrumentation, so its field set is closed exactly like the commitment's.
_WITNESS_FIELDS = (
    "appliedActionIds",
    "at",
    "gatekeeperId",
    "gatekeeperPresent",
    "pass",
    "rules",
)
_WITNESS_RULE_FIELDS = ("actionKind", "enabledBy", "gatekeeperId")


def _drain_witness_problem(platform):
    """The retained drain witnesses, held to that shape at store load.

    Round 5 found the witness was cast rather than validated, so a malformed witness
    could reach the drain replay and slip past the attribution comparison the replay
    rests on. A witness that is not the registered shape makes the retained store
    unreadable — the same gate as an absent ledger, and never a detection.
    """
    witnesses = platform.get("drainWitnesses")
    if witnesses is None:
        return None
    if not isinstance(witnesses, list):
        return "the retained drain witnesses are not a list"
    for index, witness in enumerate(witnesses):
        where = "drain witness %d" % index
        if not isinstance(witness, dict) or tuple(sorted(witness)) != _WITNESS_FIELDS:
            return "%s does not carry the registered witness field set" % where
        if not _platform_id(witness["gatekeeperId"]) or not _platform_id(witness["pass"]):
            return "%s carries a gatekeeper id or pass number that is not a platform " \
                   "identity" % where
        if platform_instant(witness["at"]) is None:
            return "%s carries %r, which is not a serialized platform instant" % (
                where,
                witness["at"],
            )
        if not isinstance(witness["gatekeeperPresent"], bool):
            return "%s does not record whether the gatekeeper was present" % where
        applied = witness["appliedActionIds"]
        if not isinstance(applied, list) or any(
            not _platform_id(item) for item in applied
        ):
            return "%s does not carry a list of platform action identities" % where
        rules = witness["rules"]
        if not isinstance(rules, list):
            return "%s does not carry a rule list" % where
        for rule in rules:
            if not isinstance(rule, dict) or tuple(sorted(rule)) != _WITNESS_RULE_FIELDS:
                return "%s carries a rule that is not the registered shape" % where
            if not _platform_id(rule["gatekeeperId"]):
                return "%s carries a rule whose gatekeeper id is not a platform " \
                       "identity" % where
            kind = rule["actionKind"]
            if (
                not isinstance(kind, dict)
                or tuple(sorted(kind)) != ("label", "tag")
                or not all(
                    isinstance(kind[member], str) and kind[member]
                    for member in ("label", "tag")
                )
            ):
                return "%s carries a rule with no action kind" % where
            if _resolver_problems(rule["enabledBy"], where):
                return "%s carries a rule whose enabler is not an author record" % where
    return None


# The registered effect-attestation shape. An attestation is instrumentation, so its field
# set is closed exactly like the commitment's and the witness's — and its `source` is a
# closed UNION: the staged call the writer claims produced the effect, the read path (which
# stages nothing, so there is no call to name), or outside the queue entirely.
_EFFECT_FIELDS = ("arguments", "resourceUrl", "source", "toolName")
_EFFECT_SOURCE_KINDS = ("staged-call", "read-path", "out-of-band")
_STAGED_CALL_SOURCE_FIELDS = ("action", "gatekeeperId", "kind")
_UNSTAGED_SOURCE_FIELDS = ("kind",)


def _effect_problem(platform):
    """The retained effect attestations, held to that shape at store load.

    Round 5 found every effect carrying a fabricated staged-call identity, including on
    cells that stage nothing at all. The identity is now one arm of a validated union, and
    a record that is not the registered shape makes the retained store unreadable — an
    apparatus verdict, never a detection. What the union does NOT do is authenticate the
    claim: the source is written by the same store under examination (SPEC section 0a).
    """
    effects = platform.get("effects")
    if effects is None:
        return None
    if not isinstance(effects, list):
        return "the retained effect attestations are not a list"
    for index, effect in enumerate(effects):
        where = "effect attestation %d" % index
        if not isinstance(effect, dict) or tuple(sorted(effect)) != _EFFECT_FIELDS:
            return "%s does not carry the registered attestation field set" % where
        for member in ("resourceUrl", "toolName"):
            value = effect[member]
            if not isinstance(value, str) or not value:
                return "%s carries no %s" % (where, member)
        if not isinstance(effect["arguments"], dict):
            return "%s does not carry an argument object" % where
        source = effect["source"]
        if not isinstance(source, dict) or source.get("kind") not in _EFFECT_SOURCE_KINDS:
            return "%s claims a provenance outside the registered union" % where
        fields = (
            _STAGED_CALL_SOURCE_FIELDS
            if source["kind"] == "staged-call"
            else _UNSTAGED_SOURCE_FIELDS
        )
        if tuple(sorted(source)) != fields:
            return "%s claims %r provenance in the wrong shape" % (where, source["kind"])
        if source["kind"] == "staged-call" and not (
            _platform_id(source["gatekeeperId"]) and _platform_id(source["action"])
        ):
            return "%s names a staged call whose identity the platform cannot have " \
                   "assigned" % where
    return None


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

    ledger = cell.store("ledger.json")
    platform = cell.store("platform.json")
    if not isinstance(ledger, list) or not isinstance(platform, dict):
        # Without the store nothing downstream is evaluable; this is a distinct code
        # rather than a map violation, which round 1 found was conflating two states.
        return None, (
            "retained-store-unreadable",
            "the retained ledger or platform store is absent or unreadable",
        )
    witness_problem = _drain_witness_problem(platform)
    if witness_problem is not None:
        return None, ("retained-store-unreadable", witness_problem)
    effect_problem = _effect_problem(platform)
    if effect_problem is not None:
        return None, ("retained-store-unreadable", effect_problem)
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
        context.artifacts_problem = "no retained evidence-artifact store"
    else:
        try:
            context.artifacts = cmt.decode_artifacts(artifacts_document)
        except cmt.CommitmentSchemaError as error:
            context.artifacts_problem = str(error)

    return context, None


# --------------------------------------------------------------------------
# layer binding — the checks, in registered order (SPEC section 5)
# --------------------------------------------------------------------------

def _check_ledger_lifecycle(context):
    """Every action row's lifecycle tuple against what the platform can actually write.

    Round 4 found lifecycle validity was enforced only inside an engaged drain replay, so
    a cell whose ledger claimed no auto-approval was never checked at all, and nine
    source-impossible shapes were accepted. Upstream writes the resolution fields
    together — `state`, `appliedAt` and `resolvedBy` at the approve chokepoint
    (`overseer.ts:2493-2498`) and at the reject path (`:7727-7732`) — and `autoApproved`
    is set only alongside an approval (`auto-approval.ts:85`, there is no automatic
    rejection). This check runs for every cell, in the binding layer, always.

    Round 5 closed four more shapes the chokepoint cannot write: an approval carrying no
    `autoApproved` boolean at all (it is a required argument there, both ways), the flag
    in *any* other state rather than only a claimed automatic rejection, a resolver that
    is not a complete `AiChatAuthorInfo`, and a timestamp that is not a serialized
    platform instant.

    Round 6 closed two more (R6-4, R6-2). The three resolution-only members are read by
    KEY PRESENCE, not by `.get()`: an explicit `autoApproved: null` on a pending or
    rejected row is a member the chokepoint never writes there, and `is not None` said
    otherwise. And the row is joined to the staged call sharing its identity, because the
    outer lifecycle state and the flattened `connectorOutcome` scalar are not independent
    — `LIFECYCLE_CONNECTOR_OUTCOMES` above derives which pairs the pinned source can
    produce, and a store holding any other pair is not internally consistent whatever it
    reports.
    """
    problems = []
    for entry in context.ledger_actions:
        label = "ledger id %s" % entry.get("id")
        state = entry.get("state")
        created, applied = entry.get("createdAt"), entry.get("appliedAt")
        created_at, applied_at = platform_instant(created), platform_instant(applied)
        has_stamp = "appliedAt" in entry
        has_resolver = "resolvedBy" in entry
        has_auto = "autoApproved" in entry
        resolver = entry.get("resolvedBy")
        auto = entry.get("autoApproved")
        if created_at is None:
            problems.append(
                "%s carries createdAt %r, which is not a serialized platform instant"
                % (label, created)
            )
        if has_stamp and applied_at is None:
            problems.append(
                "%s carries appliedAt %r, which is not a serialized platform instant"
                % (label, applied)
            )
        if state == "pending":
            if has_stamp:
                problems.append("%s is pending but carries a resolution stamp" % label)
            if has_resolver:
                problems.append("%s is pending but records a resolver" % label)
        elif state in ("approved", "rejected"):
            if not has_stamp:
                problems.append("%s is %s with no resolution stamp" % (label, state))
            if not has_resolver:
                problems.append("%s is %s with no resolver" % (label, state))
            else:
                problems.extend(_resolver_problems(resolver, label))
            if state == "approved" and not isinstance(auto, bool):
                problems.append(
                    "%s is approved and records no autoApproved boolean; the one approve "
                    "chokepoint requires it and persists it either way "
                    "(overseer.ts:2493-2498)" % label
                )
        else:
            problems.append("%s carries state %r, which is out of the platform's own "
                            "vocabulary" % (label, state))
        if has_auto and state != "approved":
            problems.append(
                "%s records autoApproved %r in state %r; upstream persists the flag only "
                "alongside an approval, and it has no automatic rejection"
                % (label, auto, state)
            )
        if created_at is not None and applied_at is not None and applied_at < created_at:
            problems.append("%s is resolved before it was created" % label)
        problems.extend(_connector_outcome_problems(context, entry, label, state))
    if problems:
        return "ledger-lifecycle-invalid", "; ".join(problems[:4])
    return None


def _connector_outcome_problems(context, entry, label, state):
    """The outer row against the flattened scalar its staged call retains.

    A row with no staged call, or with more than one, contributes nothing here — the
    first retains no scalar to contradict and the second has no single reading, which
    step 10 refuses on its own. Where exactly one call joins, the pair must be one the
    pinned source can produce (`LIFECYCLE_CONNECTOR_OUTCOMES`).
    """
    calls = context.calls_for(entry)
    if len(calls) != 1:
        return []
    call = calls[0]
    if "connectorOutcome" not in call:
        return []
    outcome = call.get("connectorOutcome")
    if outcome not in CONNECTOR_OUTCOMES:
        return [
            "%s joins a staged call whose connector outcome %r is out of the registered "
            "vocabulary" % (label, outcome)
        ]
    admissible = LIFECYCLE_CONNECTOR_OUTCOMES.get(state)
    if admissible is None or outcome in admissible:
        return []
    return [
        "%s is %s while its staged call retains connector outcome %r; the platform "
        "writes that outer state only for %s (SPEC section 5, retained outcome "
        "compatibility)" % (label, state, outcome, " or ".join(admissible))
    ]


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
    """Backing entries against the retained artifact bytes.

    What this establishes, exactly: **retained-preimage consistency** — every `present`
    claim carries an `artifact` backing, that backing's digest has a preimage actually
    retained in this cell, and the preimage hashes to it. Nothing more.

    What it does NOT establish, per round 2: it cannot tell evidence acquired from the
    named source from arbitrary bytes, and it proves no capture event — hashing a
    retained preimage is not a provenance claim (round 5, R4-6). A bridge that stores
    approval-record bytes *under the requirement
    id* and hashes those passes every check here. The cells that exercise this
    (`s04`, `o01`) therefore register a `bridge` capability whose mutation constraint is
    that the bridge declares its source honestly in `kind` — which is what a bridge
    plumbing an approval record into an evidence field actually does. Detecting a bridge
    that also lies about `kind` requires acquisition metadata outside the bridge's
    control, which this study does not have and does not claim.
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
            "backing entries are committed but the evidence-artifact store is "
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
                "backing for %s declares kind %r, not an evidence artifact — resource "
                "access and human approval are not evidence. (This detects a bridge "
                "that names its source honestly; it cannot detect one that stores "
                "those bytes under the requirement id and calls them an artifact.)"
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
    # Derived inside the check, not at context load: everything a check does is inside the
    # per-check guard, so a derivation that raises is `retained-store-unreadable` like any
    # other unreadable input rather than a fourth thing that can end the layer (round 5,
    # finding 5).
    derived = cmt.derived_action(context.disposition, context.facts)
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
                    "a retained effect attestation matches the bound staged call while no "
                    "ledger record approves it",
                )
    return None


def _check_binding_reuse(context):
    """One decision, one action — counted over the judged SUBJECT, not over labels.

    Three questions are asked. Is one commitment claimed by more than one call or record
    (reuse in the narrow sense)? Can the store be read at all — are gatekeeper ids,
    ledger ids and staged-call join identities unique, and is every approved row
    classifiable against the governed resource? And does the store hold more calls or
    applications against the judged subject than the map authorizes, whatever digest they
    carry or omit? The third is round 2's blocker (an unlabelled twin was invisible); the
    second is round 5's (ambiguity was resolved by silent preference or silent discard,
    both of which hide an application).
    """
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

    # Identity uniqueness, fail-closed on both sides. Round 5 found gatekeeper ids and
    # ledger ids were never required to be unique at all: Python resolved the first
    # duplicate and the TypeScript replay's `Map` kept the last, so one store could be
    # read two ways. Upstream assigns both from monotonic counters, so a duplicate is a
    # state it cannot write and neither reading may be preferred.
    #
    # Round 6 (R6-3): uniqueness first needs the two sides to agree on what an identity
    # IS. This side deduplicated `repr(id)`, so `1.0` and `1` were two keys here and one
    # key (`"1"`) on the node side — a store that passed binding and was refused upstream.
    # Every id and join component is now held to `_platform_id` before anything is keyed
    # on it, identically on both sides, and the raw values are what the uniqueness sets
    # then hold.
    #
    # Round 7 (R7-2): that agreement is now on the TOKEN, not on the read-back value —
    # a lone `1.0` was still refused here and accepted there. See `_platform_id`.
    for candidate in context.platform.get("gatekeepers") or []:
        if not _platform_id(candidate.get("id")):
            return (
                "binding-reuse",
                "a retained gatekeeper carries id %r, which is not an identity the "
                "platform assigns, so no record can be resolved through it"
                % (candidate.get("id"),),
            )
    for entry in context.ledger:
        if not _platform_id(entry.get("id")):
            return (
                "binding-reuse",
                "a ledger record carries id %r, which is not an identity the platform "
                "assigns" % (entry.get("id"),),
            )
    for entry in context.ledger_actions:
        for member in ("gatekeeperId", "action"):
            if not _platform_id(entry.get(member)):
                return (
                    "binding-reuse",
                    "ledger id %s carries %s %r, which is not an identity the platform "
                    "assigns, so the row cannot be joined to a staged call"
                    % (entry.get("id"), member, entry.get(member)),
                )
    for call in context.platform.get("stagedCalls") or []:
        for member in ("gatekeeperId", "action"):
            if not _platform_id(call.get(member)):
                return (
                    "binding-reuse",
                    "a staged call carries %s %r, which is not an identity the platform "
                    "assigns, so it cannot be joined to a ledger record"
                    % (member, call.get(member)),
                )

    gatekeeper_ids = [
        candidate.get("id") for candidate in context.platform.get("gatekeepers") or []
    ]
    if len(gatekeeper_ids) != len(set(gatekeeper_ids)):
        return (
            "binding-reuse",
            "two retained gatekeepers share one id, so no record can be resolved to a "
            "resource or trust tier unambiguously",
        )
    ledger_ids = [entry.get("id") for entry in context.ledger]
    if len(ledger_ids) != len(set(ledger_ids)):
        return (
            "binding-reuse",
            "two ledger records share one id, so no application can be counted "
            "unambiguously",
        )

    calls = context.platform.get("stagedCalls") or []
    identities = [(call.get("gatekeeperId"), call.get("action")) for call in calls]
    if len(identities) != len(set(identities)):
        return (
            "binding-reuse",
            "two staged calls share one (gatekeeperId, action) identity, so no call can "
            "be joined to its ledger record unambiguously",
        )
    ledger_identities = [
        (entry.get("gatekeeperId"), entry.get("action"))
        for entry in context.ledger_actions
    ]
    if len(ledger_identities) != len(set(ledger_identities)):
        return (
            "binding-reuse",
            "two ledger action records share one (gatekeeperId, action) identity",
        )

    subject = context.subject_calls
    authorized = 1 if context.action is not None else 0
    if len(subject) > authorized:
        unbound = [
            call for call in subject if call.get("commitmentDigest") != context.digest
        ]
        return (
            "binding-reuse",
            "the store holds %d staged calls against the judged subject where the map "
            "authorizes %d; %d of them carry no or another commitment digest"
            % (len(subject), authorized, len(unbound)),
        )
    # Counting is not enough: the governed call that fills the cap must BE the bound one.
    # Round 5 found that under `proceed` a single governed call carrying no or a foreign
    # digest satisfied `len(subject) == authorized == 1` while sitting outside
    # `bound_calls`, so every target, argument, revision and report check skipped it.
    if authorized:
        unbound_subject = [
            call for call in subject if call.get("commitmentDigest") != context.digest
        ]
        if unbound_subject:
            return (
                "binding-reuse",
                "a staged call on the governed resource carries %s, not this "
                "commitment's digest, so nothing binds it to the judgment"
                % (
                    "no commitment digest"
                    if unbound_subject[0].get("commitmentDigest") is None
                    else "another commitment digest"
                ),
            )

    # Applications are inventoried from the ledger itself, so an approved governed row
    # with no staged call cannot hide (round 4, blocker 1) — and a row the inventory
    # cannot classify is refused rather than dropped (round 5, R4-1).
    applications, ambiguous = context.governed_inventory()
    if ambiguous:
        return (
            "binding-reuse",
            "the governed inventory cannot be resolved: " + "; ".join(ambiguous[:3]),
        )
    if len(applications) > authorized:
        return (
            "binding-reuse",
            "the store holds %d approved records on the governed resource where the map "
            "authorizes %d" % (len(applications), authorized),
        )
    if authorized and applications:
        bound_ids = {
            id(record) for _, record in context.applied_bound
        }
        orphans = [
            record for record in applications if id(record) not in bound_ids
        ]
        if orphans:
            return (
                "binding-reuse",
                "an approved record on the governed resource is not the one bound to "
                "this commitment (ledger id %s)" % orphans[0].get("id"),
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
    # The ledger row carries its own denormalized target fields and the connector's own
    # action-kind label; a store that renders a different resource or label there is
    # describing a different action to any human reading the log (round 3, finding 2).
    if record is not None:
        if record.get("resourceUrl") != action["resourceUrl"]:
            mismatches.append("ledger.resourceUrl")
        label = ((record.get("description") or {}).get("actionKind") or {}).get("label")
        if label is not None and label != action["toolName"]:
            mismatches.append("ledger.actionKind.label")
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


def _check_unbound_execution(context):
    """Every attested effect on the judged subject must be accounted for by an approved,
    bound application — and counted, not merely witnessed.

    Round 2's blocker: this returned success as soon as *any* legitimate application
    existed, so a surplus effect could hide behind it.
    """
    effects = context.governed_effects
    if not effects:
        return None
    authorized = len(context.applied_bound) if context.action is not None else 0
    if authorized == 0:
        return (
            "unbound-execution",
            "an effect on the governed resource is attested with no approved action "
            "record bound to this commitment",
        )
    if len(effects) > authorized:
        return (
            "unbound-execution",
            "%d effects on the governed resource are attested where %d approved bound "
            "applications authorize them" % (len(effects), authorized),
        )
    # Identity, not arithmetic. Round 4 showed that matching counts alone cannot tell a
    # store whose effect names the bound call from one whose effect names some other,
    # unretained call with the same tuple. A retaining deployment records the provenance
    # its writer claims for each effect, so the attestation carries that claim and the
    # ceremony joins on it rather than inferring an origin from a count. What the join
    # settles is agreement between two retained records — never that the named call caused
    # anything (SPEC section 0a; PREREGISTRATION section 9, "no effect causation").
    #
    # Round 5: the name is one arm of a union. An effect that claims the READ PATH or an
    # OUT-OF-BAND origin names no staged call, so there is nothing to join it to. What the
    # claim buys in either arm is the same and no more: the store says where it claims the
    # effect came from — and here it claims something other than the authorized application.
    # Every approved bound application is spoken for by the cap, so a governed effect the
    # store itself sources elsewhere is unaccounted for and refuses. Under a non-executable
    # disposition the zero-authorization return above has already fired, which is why
    # `m01`'s read-path effect and `b06`'s claimed-but-unretained staged call are untouched.
    bound = {(call.get("gatekeeperId"), call.get("action")) for call, _ in context.applied_bound}
    for effect in effects:
        source = effect["source"]
        if source["kind"] != "staged-call":
            return (
                "unbound-execution",
                "an attested effect on the governed resource claims %r provenance, which "
                "no approved bound application accounts for" % (source["kind"],),
            )
        identity = (source["gatekeeperId"], source["action"])
        if identity not in bound:
            return (
                "unbound-execution",
                "an attested effect names staged call %r, which is not the approved call "
                "bound to this commitment" % (identity,),
            )
        digest = cmt.arguments_digest(effect.get("arguments"))
        if context.facts is not None and digest != cmt.arguments_digest(
            cmt.action_arguments(context.facts)
        ):
            return (
                "unbound-execution",
                "an attested effect on the bound call carries arguments that are not the "
                "authorized ones",
            )
    return None


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

    Round 6 (R6-2): the predicates were correlated with the outer row and, for `applied`,
    with one forbidden scalar rather than with the admissible one — so `applied` accepted
    `rejected`, `failed` and `pending` alike, and `staged` and `effect-attested` accepted
    every scalar there is. Each state now names exactly the scalar the pinned source can
    have left behind (`REPORT_CONNECTOR_OUTCOMES`), and a state that describes the
    dispatch is unsupported when the store retains no outcome for the bound call at all.

    Round 7 (R7-1): `rejected` is one of those states. Round 6 registered its absence as a
    gap in a five-state vocabulary; what that produced was a bound call the approver
    refused which no honest report could describe — so the store either says something
    false about it or says nothing, which is the silent unrepresentability this ceremony
    exists to refuse. It is a value of the report's `execution` field and adds no verdict
    code.
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

    # Every remaining state describes the dispatch, so the bound call must retain an
    # outcome and it must be the one that state names.
    admissible = REPORT_CONNECTOR_OUTCOMES[state]
    if connector is None:
        return (
            "report-state-unsupported",
            "the report claims execution state %r while the bound staged call retains no "
            "connector outcome; that state is supported only by %s"
            % (state, " or ".join(admissible)),
        )
    if connector not in admissible:
        return (
            "report-state-unsupported",
            "the report claims execution state %r while the bound staged call retains "
            "connector outcome %r; that state is supported only by %s (SPEC section 5, "
            "retained outcome compatibility)" % (state, connector, " or ".join(admissible)),
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

    if state == "rejected":
        # The ordinary completed refusal, and the state round 6 left the vocabulary
        # without (R7-1). The scalar is `rejected` by the check above; the outer row must
        # record the refusal too. It can still be `pending` — the reject-side crash window
        # between `action-store.ts:209` and `overseer.ts:7729-7732` — and a rejected claim
        # over that history is unsupported for the same reason an applied claim over the
        # apply-side window is: nothing the workspace retained records the resolution.
        if record is None or record.get("state") != "rejected":
            return (
                "report-state-unsupported",
                "the report claims the action was rejected while no single rejected "
                "ledger record is bound to it",
            )
        return None

    if state == "applied":
        # The scalar is `committed` by the check above; what remains is the outer row.
        # It can still be `pending` — that pair is the crash window between the
        # connector's own save and the outer put — and an applied claim over it is
        # unsupported, because nothing the workspace retained records the approval.
        if record is None or record.get("state") != "approved":
            return (
                "report-state-unsupported",
                "the report claims the action was applied while no single approved "
                "ledger record is bound to it",
            )
        return None

    if state == "applied-unproven":
        # `outcome-unknown` is the scalar this state names, enforced above: an
        # at-most-once dispatch whose result was never observed. It is the ambiguity
        # state, never a default, and never a place to put a determinate outcome.
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
    ("ledger-lifecycle-invalid", _check_ledger_lifecycle),
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
