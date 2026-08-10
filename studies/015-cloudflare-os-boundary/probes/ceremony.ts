// The cf layer — the platform's own executable policy surface, run as pinned upstream
// code over the retained records of each cell (adapter/SPEC.md section 5, layer `cf`).
//
// This entrypoint is bundled by the pinned clone's own esbuild (harness/cf_runner.py)
// with the upstream imports resolved into the clone, then executed under plain Node. It
// reads CF_CELLS (a JSON file listing {id, dir} pairs) and writes CF_OUT: one verdict
// object per cell plus an apparatus self-report the Python scorer enforces against
// harness/PINS.json. Nothing here reads MATRIX.json — expectations never enter the layer.
//
// Ordering within the layer (SPEC section 5, first failure wins):
//   1. classification-refused   — classifyTool over every routing decision the ledger claims
//   2. drain-order-violation    — AutoApprovalDrainer replay over the retained records
//
// Engagement is reported per cell: a check that evaluated nothing does not appear, so a
// vacuous pass is visible as vacuous (PREREGISTRATION section 4c).

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

type Verdict = { verdict: "pass" | "fail"; code: string | null; detail: string | null };

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

type PlatformStore = {
  gatekeepers: Array<{
    id: number;
    resourceUrl: string;
    serverTrust: ServerTrust;
    tools: Array<{ name: string; annotations?: Record<string, unknown> }>;
  }>;
  autoApproveTags: Array<{
    gatekeeperId: number;
    actionKind: { tag: string; label: string };
    enabledBy: { type: string; id: string; name: string };
  }>;
  stagedCalls: Array<{
    gatekeeperId: number;
    action: number;
    toolName: string;
    arguments: unknown;
    resourceRevisionAtStage: string;
    simulationBasis: number[];
    commitmentDigest?: string;
  }>;
  observedCalls?: Array<{ gatekeeperId: number; ledgerId: number; toolName: string }>;
};

function fail(code: string, detail: string): Verdict {
  return { verdict: "fail", code, detail };
}

const PASS: Verdict = { verdict: "pass", code: null, detail: null };

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

  const routings: Array<{ label: string; gatekeeperId: number; toolName: string;
                          claimed: "auto-action" | "read" }> = [];
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
// check 2 — drain replay (pinned AutoApprovalDrainer over the retained records)
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

async function drainCheck(
  ledger: LedgerEntry[],
  platform: PlatformStore,
): Promise<{ verdict: Verdict | null; engaged: boolean }> {
  const claimedByGatekeeper = new Map<number, number[]>();
  for (const entry of ledger) {
    if (entry.type === "action" && entry.autoApproved === true) {
      const claimed = claimedByGatekeeper.get(entry.gatekeeperId) ?? [];
      claimed.push(entry.id);
      claimedByGatekeeper.set(entry.gatekeeperId, claimed);
    }
  }
  if (claimedByGatekeeper.size === 0) {
    return { verdict: null, engaged: false };
  }

  for (const [gatekeeperId, claimed] of claimedByGatekeeper) {
    const storage = makeStorage();
    for (const rule of platform.autoApproveTags) {
      storage.autoApproveTags.put(rule as never);
    }
    for (const entry of ledger) {
      const record: Record<string, unknown> = {
        ...entry,
        createdAt: new Date(entry.createdAt),
      };
      if (entry.appliedAt !== undefined) {
        record.appliedAt = new Date(entry.appliedAt);
      }
      if (entry.type === "action" && entry.autoApproved === true) {
        record.state = "pending";
        delete record.resolvedBy;
        delete record.autoApproved;
        delete record.appliedAt;
      }
      storage.actions.put(record as never);
    }

    const applied: number[] = [];
    const applyFn: ApplyPendingActionFn = async (record, resolvedBy, autoApproved) => {
      applied.push(record.id);
      const fresh = storage.actions.get(record.id) as Record<string, unknown> | undefined;
      if (fresh && fresh.type === "action") {
        fresh.state = "approved";
        fresh.resolvedBy = resolvedBy;
        fresh.autoApproved = autoApproved;
        storage.actions.put(fresh as never);
      }
    };
    await new AutoApprovalDrainer(storage, applyFn).drain(gatekeeperId);

    const claimedSorted = [...claimed].sort((a, b) => a - b);
    if (JSON.stringify(applied) !== JSON.stringify(claimedSorted)) {
      return {
        verdict: fail(
          "drain-order-violation",
          `gatekeeper ${gatekeeperId}: ledger claims auto-applied ` +
            `[${claimedSorted.join(", ")}] but the pinned drainer replay applies ` +
            `[${applied.join(", ")}]`,
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
  ];
  const digests: Record<string, string> = {};
  for (const relative of probed) {
    digests[relative] = createHash("sha256")
      .update(readFileSync(join(source, relative)))
      .digest("hex");
  }
  const git = (...args: string[]) =>
    execFileSync("git", ["-C", source, ...args], { encoding: "utf-8" }).trim();
  return {
    nodeVersion: process.version,
    cloneCommit: git("rev-parse", "HEAD"),
    cloneTrackedClean: git("status", "--porcelain", "--untracked-files=no") === "",
    lockfileSha256: createHash("sha256")
      .update(readFileSync(join(source, "pnpm-lock.yaml")))
      .digest("hex"),
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
    results[cell.id] = { ...(drain.verdict ?? PASS), engaged };
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
