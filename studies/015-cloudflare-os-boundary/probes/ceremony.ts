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
//   1. classification-refused   — classifyTool over every routing decision the ledger claims
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

// ---------------------------------------------------------------------------
// check 1 — classification (pinned classifyTool over every claimed routing)
// ---------------------------------------------------------------------------

function classificationCheck(
  ledger: LedgerEntry[],
  platform: PlatformStore,
): { verdict: Verdict | null; engaged: boolean } {
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
function pendingAt(entry: LedgerEntry, at: number): boolean | null {
  if (entry.type !== "action") return false;
  const created = Date.parse(entry.createdAt);
  if (Number.isNaN(created)) return null; // unusable timestamp: refuse, never exclude
  if (entry.appliedAt !== undefined) {
    const resolved = Date.parse(entry.appliedAt);
    if (Number.isNaN(resolved)) return null;
    if (resolved < created) return null; // resolved before it existed
    if (resolved < at) return false; // already resolved when the pass ran
  } else if (entry.state !== "pending") {
    return null; // resolved with no resolution stamp: not reconstructible
  }
  return created <= at;
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
  if (claimed.size === 0) {
    return { verdict: null, engaged: false };
  }

  const witnesses = platform.drainWitnesses ?? [];
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
    const at = Date.parse(witness.at);
    if (Number.isNaN(at)) {
      return {
        verdict: fail(
          "drain-order-violation",
          `pass ${witness.pass}: the witness carries no usable instant`,
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
    const attribution = new Map<number, string | undefined>();
    const applyFn: ApplyPendingActionFn = async (record, resolvedBy) => {
      applied.push(record.id);
      // Upstream persists the rule enabler as the audit attribution
      // (auto-approval.ts:85 -> overseer.ts:2496); the replay records what the pinned
      // drainer passed so a forged `resolvedBy` in the ledger is checkable.
      attribution.set(record.id, (resolvedBy as { id?: string } | undefined)?.id);
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
      const recorded = ledger.find((entry) => entry.id === id);
      const claimed = (recorded?.resolvedBy as { id?: string } | undefined)?.id;
      if (expected !== undefined && claimed !== undefined && expected !== claimed) {
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

  // Every claimed auto-approval must be accounted for by some witnessed pass, and no
  // pass may claim an application the ledger does not record.
  for (const [gatekeeperId, ids] of claimed) {
    const seen = (replayed.get(gatekeeperId) ?? []).slice().sort((a, b) => a - b);
    const expected = ids.slice().sort((a, b) => a - b);
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
  for (const gatekeeperId of replayed.keys()) {
    if (!claimed.has(gatekeeperId)) {
      return {
        verdict: fail(
          "drain-order-violation",
          `gatekeeper ${gatekeeperId}: a drain witness claims applications the ledger ` +
            `does not record as auto-approved`,
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
      ledger = readJson(join(cell.dir, "ledger.json")) as LedgerEntry[];
      platform = readJson(join(cell.dir, "platform.json")) as PlatformStore;
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
