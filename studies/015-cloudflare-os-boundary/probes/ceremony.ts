// The `upstream` layer — the platform's own policy FUNCTIONS, replayed offline by this
// harness over the retained records (adapter/SPEC.md section 5).
//
// What this is, stated exactly, because round 1 found the earlier name overclaimed it:
// `classifyTool` and `AutoApprovalDrainer` below are the pinned upstream functions,
// imported from the read-only clone and never reimplemented. Everything around them —
// which records to feed them, how to join a ledger row to a staged call, how to
// reconstruct a queue, the apply callback, and the verdict codes — is study-authored.
// The Durable Object enforcement path never runs. A `pass` here therefore means "the
// platform's replayed policy functions did not object", never "the platform endorsed
// this"; and when a construction gives them nothing to decide the verdict is
// `not-engaged`, which is a distinct outcome from `pass`.
//
// This entrypoint is bundled by the pinned clone's own esbuild (harness/cf_runner.py)
// with the upstream imports resolved into the clone, then executed under plain Node. It
// reads CF_CELLS (a JSON file listing {id, dir} pairs) and writes CF_OUT: one verdict
// object per cell plus an apparatus self-report the Python scorer enforces against
// harness/PINS.json. Nothing here reads the registry — expectations never enter a layer.
//
// Ordering within the layer (SPEC section 5, first failure wins):
//   1. classification-refused   — a store with two readings (duplicate gatekeeper ids,
//                                 ledger ids or staged-call join identities), then
//                                 classifyTool over every routing decision the ledger claims
//   2. drain-order-violation    — AutoApprovalDrainer replayed against the stage-time witness

import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { classifyTool } from "@gadgets/mcp-shared/tools";
import type { ServerTrust } from "@gadgets/mcp-shared/tools";
import {
  AutoApprovalDrainer,
  type ApplyPendingActionFn,
  type AutoApprovalStorage,
} from "@gadgets/workshop-backend/auto-approval";
import { makeMockStorage } from "@gadgets/workshop-backend/mock-storage";
import { collection, createTypedStorage } from "@gadgets/typed-storage";

type Verdict = {
  verdict: "pass" | "fail" | "not-engaged";
  code: string | null;
  detail: string | null;
};

type LedgerEntry = {
  id: number;
  gatekeeperId: number;
  type: "action" | "observation" | "bindHook";
  state: "pending" | "approved" | "rejected";
  createdAt: string;
  caller: unknown;
  action?: number;
  description: Record<string, unknown>;
  resolvedBy?: unknown;
  autoApproved?: boolean;
  appliedAt?: string;
};

// One retained record of one auto-approval drain pass.
//
// WHAT THIS IS NOT, stated first because round 2 found the earlier framing overclaimed
// it: this witness is **self-asserted instrumentation supplied by the same retained
// store the ceremony is examining**. It is not signed, not anchored outside the store,
// and not something stock Cloudflare OS keeps. A store writer who adds a matching rule
// here launders an auto-approval that no rule ever authorized, and no residue in stock
// state contradicts them. The verdict this check supports is therefore
// **consistency with the self-asserted witness**, never "the drain was historically
// lawful".
//
// What it still buys, and why it is worth keeping: the queue is reconstructed from the
// ledger's own immutable timestamps rather than from the witness, so an obstruction
// cannot be erased by resolving it later without contradicting the records the store
// kept. The witness supplies only what the platform destroys as it goes — the rule set
// in force, the pass identity, and that the gatekeeper resolved.
//
// The replay is also not a general simulation of upstream: it models one pass with one
// static rule set and an always-successful apply callback, so it does not reproduce a
// throwing apply, a mid-pass rule change, the `fresh`-recheck `continue` branch, or
// single-flight reruns. Constructions depending on those are out of its scope.
type DrainWitness = {
  gatekeeperId: number;
  pass: number;
  at: string;
  appliedActionIds: number[];
  rules: Array<{
    gatekeeperId: number;
    actionKind: { tag: string; label: string };
    enabledBy: { type: string; id: string; name: string };
  }>;
  gatekeeperPresent: boolean;
};

type PlatformStore = {
  gatekeepers: Array<{
    id: number;
    resourceUrl: string;
    serverTrust: ServerTrust;
    tools: Array<{ name: string; annotations?: Record<string, unknown> }>;
  }>;
  autoApproveTags: DrainWitness["rules"];
  stagedCalls: Array<{
    gatekeeperId: number;
    action: number;
    toolName: string;
    arguments: unknown;
    resourceRevisionAtStage: string;
    connectorOutcome?: string;
    commitmentDigest?: string;
  }>;
  drainWitnesses?: DrainWitness[];
  observedCalls?: Array<{ gatekeeperId: number; ledgerId: number; toolName: string }>;
};

function fail(code: string, detail: string): Verdict {
  return { verdict: "fail", code, detail };
}

const PASS: Verdict = { verdict: "pass", code: null, detail: null };
const NOT_ENGAGED: Verdict = { verdict: "not-engaged", code: null, detail: null };

function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf-8"));
}

// The token an identity must be written as: digits and nothing else. Same sentence as
// `_INTEGER_LEXEME` in `adapter/verify.py`. JavaScript's `$` is end-of-input (Python's is
// not, which is half of R7-3), so this is a full match.
const INTEGER_LEXEME = /^[0-9]+$/;

// What a number token that is NOT a plain integer lexeme becomes when the store is read.
//
// Round 7 (R7-2): round 6 settled identity on the value each side reads back, which is not
// one definition but two. `JSON.parse("1.0")` is `1` here and `Number.isSafeInteger`
// accepts it; `json.loads("1.0")` is a `float` there and is refused. Round 6's own
// regressions used a DUPLICATE id, which refuses on both sides for an unrelated reason, so
// the divergence went unseen. Node 22 exposes each primitive's source token to a
// `JSON.parse` reviver (`context.source`), so the store is read through one: a number
// whose token is not a plain digit-only integer is replaced by this object, which is not a
// `number` and therefore cannot be an identity, cannot be counted, and cannot alias a real
// identity in any key the checks below build. The token is kept so a diagnostic can print
// what the store actually wrote.
type NonIntegerLexeme = { nonIntegerLexeme: string };

function readStore(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf-8"), function (_key, value, context) {
    if (typeof value !== "number") return value;
    const source = (context as { source?: unknown } | undefined)?.source;
    if (typeof source !== "string") {
      // Apparatus failure, never a detection: without the token this runner cannot apply
      // the registered identity rule at all, and a weaker check in its place would be the
      // divergence R7-2 was filed about. The driver turns a throw here into an
      // `unavailable` record for the cell.
      throw new Error(
        "this Node build does not expose JSON.parse source access, which the registered " +
          "identity rule requires",
      );
    }
    if (INTEGER_LEXEME.test(source)) return value;
    return { nonIntegerLexeme: source } satisfies NonIntegerLexeme;
  });
}

// The ONE serialized form the platform can write: `Date.prototype.toISOString()` output,
// `YYYY-MM-DDTHH:mm:ss.sssZ`. Round 5 narrowed this to a strict RFC 3339 grammar; round 6
// (R6-5) found that still neither strict nor identical to the Python side — the regex was
// digit-shaped and the instant then came from `Date.parse`, which normalizes an impossible
// calendar date (`2026-02-29` silently became March 1) and collapses `.0004Z` and `.0005Z`
// onto one millisecond, so a genuinely earlier resolution could be retained in the queue
// and pass its witness.
//
// No `Date.parse` and no arithmetic: the calendar is checked by integers and the validated
// STRING is the instant. The form is fixed-width and UTC, so lexicographic order is
// chronological order, and `adapter/verify.py` validates and compares exactly the same
// bytes with exactly the same rule.
//
// The class is spelled `[0-9]` rather than `\d` to be the same sentence as
// `adapter/verify.py`'s: they are the same set in JavaScript and are not in Python, and
// round 7 (R7-3) found that side's `\d` accepting Unicode decimal digits — plus its `$`
// accepting a trailing newline, which this `$` does not.
const PLATFORM_INSTANT =
  /^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})\.([0-9]{3})Z$/;
const MONTH_LENGTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

function daysInMonth(year: number, month: number): number {
  if (month === 2 && year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) return 29;
  return MONTH_LENGTHS[month - 1];
}

function platformInstant(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const match = PLATFORM_INSTANT.exec(value);
  if (match === null) return null;
  const [year, month, day, hour, minute, second] = match.slice(1, 7).map(Number);
  if (month < 1 || month > 12) return null;
  if (day < 1 || day > daysInMonth(year, month)) return null;
  if (hour > 23 || minute > 59 || second > 59) return null;
  return value;
}

// A platform identity is a JSON number assigned from a monotonic counter starting at 1
// (`overseer.ts:418-422`). Round 6 (R6-3) found the two layers disagreeing about what
// that means: `String(id)` collapsed `1` and `1.0` here while Python's `repr` kept them
// apart, so one store was refused upstream and accepted by binding.
//
// Round 7 (R7-2) moved the definition onto the token, which `readStore` above has already
// applied: a number reaching this function was written as a plain digit-only integer, and
// anything else — `1.0`, `1e0`, `-1`, `-0` — arrived as a `NonIntegerLexeme` object and
// fails the first line. Booleans are not numbers either. The range test is still this
// side's own, because `9007199254740993` is a plain integer token that V8 cannot read
// back. Identical to `_platform_id` in `adapter/verify.py`.
function platformId(value: unknown): number | null {
  if (typeof value !== "number") return null;
  if (!Number.isSafeInteger(value)) return null;
  if (value < 1) return null;
  return value;
}

// An `AiChatAuthorInfo` is a complete triple upstream (`api.ts:1777`): actor type, id and
// display name. Round 5 found only `.id` was compared, so the same id under a different
// name or actor type read as the same author. The key below is the whole tuple, and a
// value that is not a complete author record has no key at all.
function authorKey(value: unknown): string | null {
  const author = value as { type?: unknown; id?: unknown; name?: unknown } | undefined;
  if (!author || typeof author !== "object") return null;
  if (author.type !== "user" && author.type !== "agent" && author.type !== "gadget") {
    return null;
  }
  if (typeof author.id !== "string" || author.id === "") return null;
  if (typeof author.name !== "string" || author.name === "") return null;
  return JSON.stringify([author.type, author.id, author.name]);
}

function firstDuplicate(keys: string[]): string | null {
  const seen = new Set<string>();
  for (const key of keys) {
    if (seen.has(key)) return key;
    seen.add(key);
  }
  return null;
}

// The retained store must have exactly one reading. Round 5 found that gatekeeper ids,
// ledger ids and staged-call join identities were never required to be unique: the `Map`s
// below keep the LAST duplicate while the Python ceremony resolves the FIRST, so one
// store could be read two ways and neither reading is preferable. Upstream assigns both
// ids from monotonic counters, so a duplicate is a state it cannot write.
//
// Round 6 (R6-3) added the two things missing from that: every id and join component is
// held to `platformId` BEFORE it is keyed on, so the two layers cannot disagree about
// which values are even identities, and the ledger's own `(gatekeeperId, action)` join
// identities are checked here as the binding layer already checked them.
function storeAmbiguity(ledger: LedgerEntry[], platform: PlatformStore): string | null {
  for (const g of platform.gatekeepers ?? []) {
    if (platformId(g.id) === null) {
      return `a retained gatekeeper carries id ${JSON.stringify(g.id)}, which is not an identity the platform assigns`;
    }
  }
  for (const entry of ledger) {
    if (platformId(entry.id) === null) {
      return `a ledger record carries id ${JSON.stringify(entry.id)}, which is not an identity the platform assigns`;
    }
    if (entry.type !== "action") continue;
    if (platformId(entry.gatekeeperId) === null || platformId(entry.action) === null) {
      return `ledger record ${entry.id} carries a join identity the platform cannot have assigned`;
    }
  }
  for (const c of platform.stagedCalls ?? []) {
    if (platformId(c.gatekeeperId) === null || platformId(c.action) === null) {
      return `a staged call carries a join identity the platform cannot have assigned`;
    }
  }
  const gatekeeper = firstDuplicate((platform.gatekeepers ?? []).map((g) => String(g.id)));
  if (gatekeeper !== null) return `two retained gatekeepers share id ${gatekeeper}`;
  const record = firstDuplicate(ledger.map((entry) => String(entry.id)));
  if (record !== null) return `two ledger records share id ${record}`;
  const call = firstDuplicate(
    (platform.stagedCalls ?? []).map((c) => `${c.gatekeeperId}:${c.action}`),
  );
  if (call !== null) return `two staged calls share the join identity ${call}`;
  const join = firstDuplicate(
    ledger
      .filter((entry) => entry.type === "action")
      .map((entry) => `${entry.gatekeeperId}:${entry.action}`),
  );
  if (join !== null) return `two ledger action records share the join identity ${join}`;
  return null;
}

// ---------------------------------------------------------------------------
// check 1 — classification (pinned classifyTool over every claimed routing)
// ---------------------------------------------------------------------------

function classificationCheck(
  ledger: LedgerEntry[],
  platform: PlatformStore,
): { verdict: Verdict | null; engaged: boolean } {
  const ambiguity = storeAmbiguity(ledger, platform);
  if (ambiguity !== null) {
    // Fail closed before the pinned classifier is given anything: with two readings of
    // the store there is no determinate routing to classify.
    return {
      verdict: fail(
        "classification-refused",
        `${ambiguity}, so the retained store has no single reading and no claimed ` +
          `routing can be classified against it`,
      ),
      engaged: false,
    };
  }
  const gatekeepers = new Map(platform.gatekeepers.map((g) => [g.id, g]));
  const staged = new Map(
    platform.stagedCalls.map((c) => [`${c.gatekeeperId}:${c.action}`, c]),
  );
  let engaged = false;

  const routings: Array<{
    label: string;
    gatekeeperId: number;
    toolName: string;
    claimed: "auto-action" | "read";
  }> = [];
  for (const entry of ledger) {
    if (entry.type === "action" && entry.autoApproved === true) {
      const call = staged.get(`${entry.gatekeeperId}:${entry.action}`);
      if (!call) {
        return {
          verdict: fail(
            "classification-refused",
            `ledger action ${entry.id} claims auto-approval but no staged call is retained`,
          ),
          engaged: true,
        };
      }
      routings.push({
        label: `ledger action ${entry.id}`,
        gatekeeperId: entry.gatekeeperId,
        toolName: call.toolName,
        claimed: "auto-action",
      });
    }
  }
  for (const observed of platform.observedCalls ?? []) {
    routings.push({
      label: `observed call at ledger ${observed.ledgerId}`,
      gatekeeperId: observed.gatekeeperId,
      toolName: observed.toolName,
      claimed: "read",
    });
  }

  for (const routing of routings) {
    engaged = true;
    const gatekeeper = gatekeepers.get(routing.gatekeeperId);
    const tool = gatekeeper?.tools.find((t) => t.name === routing.toolName);
    if (!gatekeeper || !tool) {
      return {
        verdict: fail(
          "classification-refused",
          `${routing.label}: tool ${routing.toolName} is not in the retained catalog`,
        ),
        engaged,
      };
    }
    const classified = classifyTool(tool as never, gatekeeper.serverTrust);
    if (routing.claimed === "auto-action") {
      if (classified.mode !== "action" || !classified.autoApprovable) {
        return {
          verdict: fail(
            "classification-refused",
            `${routing.label}: pinned classifyTool says mode=${classified.mode} ` +
              `autoApprovable=${classified.autoApprovable} (classifiedBy ` +
              `${classified.classifiedBy}) — the platform's own policy would not auto-apply it`,
          ),
          engaged,
        };
      }
    } else if (classified.mode !== "read") {
      return {
        verdict: fail(
          "classification-refused",
          `${routing.label}: claimed read-path but pinned classifyTool says mode=action`,
        ),
        engaged,
      };
    }
  }
  return { verdict: null, engaged };
}

// ---------------------------------------------------------------------------
// check 2 — drain replay against the stage-time witness
// ---------------------------------------------------------------------------

function makeStorage(): AutoApprovalStorage {
  return createTypedStorage(makeMockStorage(), {
    collections: {
      actions: collection<never>()({ primaryKey: "id" }),
      autoApproveTags: collection<never>()({
        primaryKey: (r: { gatekeeperId: number; actionKind: { tag: string } }) =>
          `${r.gatekeeperId}:${r.actionKind.tag}`,
      }),
    },
  }) as unknown as AutoApprovalStorage;
}

// A record was pending at instant t exactly when it had been created by then and had not
// yet been resolved. `appliedAt` is stamped on BOTH approve and reject (overseer.ts:2495
// and :7729), so it is a resolution timestamp — which is what makes this reconstruction
// sound, and why a resolution stamp is never read as evidence of application.
function pendingAt(entry: LedgerEntry, at: string): boolean | null {
  if (entry.type !== "action") return false;
  const created = platformInstant(entry.createdAt);
  if (created === null) return null; // unusable timestamp: refuse, never exclude
  // Strict lifecycle equivalence: upstream stamps `appliedAt` and `resolvedBy` exactly
  // when a record leaves `pending` (overseer.ts:2495-2496, :7729-7731). A row that is
  // still `pending` yet carries a resolution stamp — or is resolved without one — is a
  // state the platform cannot produce, and round 3 found the earlier version silently
  // excluded such a row from the queue, erasing an obstruction.
  const resolvedStamped = entry.appliedAt !== undefined;
  const resolvedState = entry.state !== "pending";
  if (resolvedStamped !== resolvedState) return null;
  if (resolvedStamped) {
    const resolved = platformInstant(entry.appliedAt);
    if (resolved === null) return null;
    if (resolved < created) return null; // resolved before it existed
    // Strictly before, and registered as such (SPEC section 5, upstream step 2): a record
    // resolved before the pass instant is legitimate history and is excluded from that
    // queue, while equality reads as not-yet-resolved at the witness and stays in it.
    if (resolved < at) return false;
  }
  return created <= at;
}

// The identities one retained witness claims: its own pass and gatekeeper, every action id
// it says the pass applied, and the gatekeeper each of its rules names. `adapter/verify.py`
// holds exactly this set to `_platform_id` at store load.
function witnessIdentityProblem(witness: DrainWitness): string | null {
  const named: Array<[string, unknown]> = [
    ["pass identity", witness.pass],
    ["gatekeeper id", witness.gatekeeperId],
  ];
  if (!Array.isArray(witness.appliedActionIds)) {
    return "carries no list of applied action identities";
  }
  witness.appliedActionIds.forEach((id, index) => {
    named.push([`applied action id at position ${index}`, id]);
  });
  if (!Array.isArray(witness.rules)) return "carries no rule list";
  witness.rules.forEach((rule, index) => {
    const held = rule as { gatekeeperId?: unknown } | undefined;
    named.push([`gatekeeper id of rule ${index}`, held?.gatekeeperId]);
  });
  for (const [what, value] of named) {
    if (platformId(value) === null) {
      return (
        `carries a ${what} of ${JSON.stringify(value)}, which is not an identity the ` +
        `platform assigns`
      );
    }
  }
  return null;
}

async function drainCheck(
  ledger: LedgerEntry[],
  platform: PlatformStore,
): Promise<{ verdict: Verdict | null; engaged: boolean }> {
  const claimed = new Map<number, number[]>();
  for (const entry of ledger) {
    if (entry.type === "action" && entry.autoApproved === true) {
      const list = claimed.get(entry.gatekeeperId) ?? [];
      list.push(entry.id);
      claimed.set(entry.gatekeeperId, list);
    }
  }
  // Witnesses are read BEFORE the early exit, and non-engagement means both sides are
  // empty. Round 6 (R6-4) found this returning not-engaged the moment the ledger claimed
  // no auto-approval, which made the reverse accounting at the end of this function
  // unreachable: a store whose witness claims `appliedActionIds: [1]` while every row
  // records `autoApproved: false` passed binding, went unexamined upstream, and combined
  // green — although SPEC section 5 says a witness claiming an application the ledger
  // does not record fails. A witness is a retained record about this gatekeeper's drain;
  // that it contradicts the ledger is exactly what there is to check.
  const witnesses = platform.drainWitnesses ?? [];
  if (claimed.size === 0 && witnesses.length === 0) {
    return { verdict: null, engaged: false };
  }
  if (witnesses.length === 0) {
    return {
      verdict: fail(
        "drain-order-violation",
        "the ledger claims auto-applied actions but no stage-time drain witness is " +
          "retained; a final snapshot cannot establish that the drain was lawful",
      ),
      engaged: true,
    };
  }

  // Every identity a witness claims, held to `platformId` BEFORE anything sorts, keys or
  // replays on it — the same gate `storeAmbiguity` applies to the store's other identities
  // (R6-3), and the same set `_drain_witness_problem` validates in `adapter/verify.py`.
  //
  // Round 8 (R8-3): the pass number reached the sort below unvalidated, so a witness
  // written `"pass": 1.0` arrived as a `NonIntegerLexeme`, `a.pass - b.pass` returned
  // `NaN`, the sort silently did nothing, and the cell came out `pass` with both checks
  // engaged — while the binding layer refused the same bytes as
  // `retained-store-unreadable`. One store, two readings, which is the divergence R7-2 was
  // filed about: that repair was made for the gatekeeper's own id and not for the
  // witness's.
  for (const [index, witness] of witnesses.entries()) {
    const problem = witnessIdentityProblem(witness);
    if (problem !== null) {
      return {
        verdict: fail("drain-order-violation", `drain witness ${index} ${problem}`),
        engaged: true,
      };
    }
  }

  const replayed = new Map<number, number[]>();
  for (const witness of witnesses.slice().sort((a, b) => a.pass - b.pass)) {
    if (!witness.gatekeeperPresent) {
      return {
        verdict: fail(
          "drain-order-violation",
          `pass ${witness.pass}: the witness records that gatekeeper ` +
            `${witness.gatekeeperId} was absent, so no apply could have succeeded`,
        ),
        engaged: true,
      };
    }
    const at = platformInstant(witness.at);
    if (at === null) {
      return {
        verdict: fail(
          "drain-order-violation",
          `pass ${witness.pass}: the witness carries no serialized platform instant`,
        ),
        engaged: true,
      };
    }

    const storage = makeStorage();
    for (const rule of witness.rules) {
      storage.autoApproveTags.put(rule as never);
    }
    // The queue as it stood at that instant, reconstructed from the ledger's own
    // immutable timestamps rather than from its final states — an obstruction cannot be
    // erased by later resolving it.
    const candidates = ledger.filter(
      (entry) => entry.gatekeeperId === witness.gatekeeperId,
    );
    const unreconstructable = candidates.filter(
      (entry) => pendingAt(entry, at) === null,
    );
    if (unreconstructable.length > 0) {
      return {
        verdict: fail(
          "drain-order-violation",
          `pass ${witness.pass}: ledger records ` +
            `[${unreconstructable.map((e) => e.id).join(", ")}] carry timestamps that ` +
            `cannot be reconstructed to a queue state, so the pass is not checkable`,
        ),
        engaged: true,
      };
    }
    const queue = candidates
      .filter((entry) => pendingAt(entry, at) === true)
      .slice()
      .sort((a, b) => a.id - b.id);
    for (const entry of queue) {
      const record: Record<string, unknown> = {
        ...entry,
        createdAt: new Date(entry.createdAt),
        state: "pending",
      };
      delete record.resolvedBy;
      delete record.autoApproved;
      delete record.appliedAt;
      storage.actions.put(record as never);
    }

    const applied: number[] = [];
    const attribution = new Map<number, string | null>();
    const applyFn: ApplyPendingActionFn = async (record, resolvedBy) => {
      applied.push(record.id);
      // Upstream persists the rule enabler as the audit attribution
      // (auto-approval.ts:85 -> overseer.ts:2496); the replay records the whole author
      // tuple the pinned drainer passed, so a forged or partial `resolvedBy` in the
      // ledger is checkable.
      attribution.set(record.id, authorKey(resolvedBy));
      const fresh = storage.actions.get(record.id) as Record<string, unknown> | undefined;
      if (fresh && fresh.type === "action") {
        fresh.state = "approved";
        storage.actions.put(fresh as never);
      }
    };
    await new AutoApprovalDrainer(storage, applyFn).drain(witness.gatekeeperId);

    const witnessed = witness.appliedActionIds.slice().sort((a, b) => a - b);
    if (JSON.stringify(applied) !== JSON.stringify(witnessed)) {
      return {
        verdict: fail(
          "drain-order-violation",
          `pass ${witness.pass} on gatekeeper ${witness.gatekeeperId}: the witness ` +
            `claims [${witnessed.join(", ")}] were auto-applied, but replaying the ` +
            `pinned drainer over the queue as it stood at ${witness.at} applies ` +
            `[${applied.join(", ")}]`,
        ),
        engaged: true,
      };
    }
    for (const id of witnessed) {
      const expected = attribution.get(id);
      if (expected === undefined) continue; // the pass applied nothing under this id
      const recorded = ledger.find((entry) => entry.id === id);
      const claimed = authorKey(recorded?.resolvedBy);
      // Attribution is MANDATORY for a witnessed automatic resolution: upstream always
      // persists the rule enabler (auto-approval.ts:85 -> overseer.ts:2496), so a
      // missing `resolvedBy` is itself a state the platform does not produce. Round 3
      // found that an optional comparison let deletion pass; round 5 found the
      // comparison itself read only `.id`, so the enabler's name and actor type could
      // be anything.
      if (expected === null) {
        return {
          verdict: fail(
            "drain-order-violation",
            `pass ${witness.pass}: the rule that auto-applied action ${id} names an ` +
              `enabler that is not a complete author record, so the resolution cannot ` +
              `be attributed at all`,
          ),
          engaged: true,
        };
      }
      if (claimed === null) {
        return {
          verdict: fail(
            "drain-order-violation",
            `action ${id} is claimed auto-approved but records no complete resolvedBy ` +
              `(type, id and name); upstream always attributes an auto-approval to the ` +
              `rule enabler`,
          ),
          engaged: true,
        };
      }
      if (expected !== claimed) {
        return {
          verdict: fail(
            "drain-order-violation",
            `action ${id} records resolvedBy ${claimed}, but the pinned drainer ` +
              `attributes an auto-approval under this witness to ${expected}`,
          ),
          engaged: true,
        };
      }
    }
    const seen = replayed.get(witness.gatekeeperId) ?? [];
    seen.push(...witnessed);
    replayed.set(witness.gatekeeperId, seen);
  }

  // Every claimed auto-approval must be accounted for by some witnessed pass, and no pass
  // may claim an application the ledger does not record. ONE comparison answers both, over
  // every gatekeeper either side mentions, with absence read as the empty list.
  //
  // Round 7 (R7-4): this was two loops, and the second asked whether the witness's
  // gatekeeper had a *key* in the ledger's claim map rather than whether the two lists
  // agreed. A witness accounting for nothing still inserted its key above, so an engaged
  // empty witness beside rows that claim no auto-approval — a record this ceremony
  // accepts — was refused for claiming an application it does not claim. Empty equals
  // empty.
  for (const gatekeeperId of new Set([...claimed.keys(), ...replayed.keys()])) {
    const seen = (replayed.get(gatekeeperId) ?? []).slice().sort((a, b) => a - b);
    const expected = (claimed.get(gatekeeperId) ?? []).slice().sort((a, b) => a - b);
    if (JSON.stringify(seen) !== JSON.stringify(expected)) {
      return {
        verdict: fail(
          "drain-order-violation",
          `gatekeeper ${gatekeeperId}: the ledger claims [${expected.join(", ")}] were ` +
            `auto-applied but the witnessed passes account for [${seen.join(", ")}]`,
        ),
        engaged: true,
      };
    }
  }
  return { verdict: null, engaged: true };
}

// ---------------------------------------------------------------------------
// apparatus self-report (enforced by the scorer against harness/PINS.json)
// ---------------------------------------------------------------------------

function selfReport(source: string) {
  const probed = [
    "packages/mcp-shared/src/tools.ts",
    "packages/mcp-shared/src/util.ts",
    "packages/workshop-backend/src/auto-approval.ts",
    "packages/workshop-backend/__tests__/mock-storage.ts",
    "packages/typed-storage/src/index.ts",
    "packages/workshop-shared/src/gatekeeper.ts",
    "packages/workshop-shared/src/api.ts",
    "packages/workshop-backend/src/overseer.ts",
  ];
  const digests: Record<string, string> = {};
  for (const relative of probed) {
    digests[relative] = createHash("sha256")
      .update(readFileSync(join(source, relative)))
      .digest("hex");
  }
  const git = (...args: string[]) =>
    execFileSync("git", ["-C", source, ...args], { encoding: "utf-8" }).trim();
  const packageVersion = (relative: string): string | null => {
    try {
      return JSON.parse(readFileSync(join(source, relative), "utf-8")).version ?? null;
    } catch {
      return null;
    }
  };
  return {
    nodeVersion: process.version,
    cloneCommit: git("rev-parse", "HEAD"),
    cloneTrackedClean: git("status", "--porcelain", "--untracked-files=no") === "",
    lockfileSha256: createHash("sha256")
      .update(readFileSync(join(source, "pnpm-lock.yaml")))
      .digest("hex"),
    typescriptVersion: packageVersion(
      "node_modules/.pnpm/typescript@5.9.3/node_modules/typescript/package.json",
    ),
    probedFiles: digests,
  };
}

// ---------------------------------------------------------------------------
// driver
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  const source = process.env.CFOS_SOURCE;
  const cellsPath = process.env.CF_CELLS;
  const outPath = process.env.CF_OUT;
  if (!source || !cellsPath || !outPath) {
    throw new Error("CFOS_SOURCE, CF_CELLS and CF_OUT must all be set");
  }
  const cells = readJson(cellsPath) as Array<{ id: string; dir: string }>;

  const results: Record<
    string,
    { verdict: string; code: string | null; detail: string | null; engaged: string[] }
  > = {};
  for (const cell of cells) {
    let ledger: LedgerEntry[];
    let platform: PlatformStore;
    try {
      ledger = readStore(join(cell.dir, "ledger.json")) as LedgerEntry[];
      platform = readStore(join(cell.dir, "platform.json")) as PlatformStore;
    } catch (error) {
      results[cell.id] = {
        verdict: "unavailable",
        code: null,
        detail: `retained records unreadable: ${String(error)}`,
        engaged: [],
      };
      continue;
    }

    const engaged: string[] = [];
    const classification = classificationCheck(ledger, platform);
    if (classification.engaged) engaged.push("classifyTool");
    if (classification.verdict) {
      results[cell.id] = { ...classification.verdict, engaged };
      continue;
    }
    const drain = await drainCheck(ledger, platform);
    if (drain.engaged) engaged.push("AutoApprovalDrainer");
    const settled = drain.verdict ?? (engaged.length === 0 ? NOT_ENGAGED : PASS);
    results[cell.id] = { ...settled, engaged };
  }

  writeFileSync(
    outPath,
    JSON.stringify({ apparatus: selfReport(source), cells: results }, null, 2) + "\n",
  );
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
