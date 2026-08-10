// Focused probes that call the pinned platform's own functions to demonstrate the named
// mechanisms the matrix leans on (PREREGISTRATION section 7). These are demonstrations of
// upstream behavior under the study's replay harness pattern, not detections: upstream's
// own suites (packages/mcp-shared/__tests__/tools.test.ts,
// packages/workshop-backend/__tests__/auto-approval.test.ts) already exercise these
// functions; what these probes pin down is that the exact branches the cells depend on
// behave as registered under the study's aliased, stubbed, node-only loading.

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { actionKindFor, catalogRevision, classifyTool } from "@gadgets/mcp-shared/tools";
import {
  AutoApprovalDrainer,
  type ApplyPendingActionFn,
  type AutoApprovalStorage,
} from "@gadgets/workshop-backend/auto-approval";
import { makeMockStorage } from "@gadgets/workshop-backend/mock-storage";
import { collection, createTypedStorage } from "@gadgets/typed-storage";

// Minimal runner: sequential suites, fail-fast exit code, no framework.
type Case = { name: string; body: () => void | Promise<void> };
const cases: Case[] = [];
let currentSuite = "";
function suite(name: string, body: () => void): void {
  currentSuite = name;
  body();
}
function test(name: string, body: () => void | Promise<void>): void {
  cases.push({ name: `${currentSuite} › ${name}`, body });
}

const TRACKER_TOOL = {
  name: "tracker_create_work_item",
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true },
};

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

function putAction(
  storage: AutoApprovalStorage,
  id: number,
  opts: { autoApprovable?: boolean; tag?: string; state?: string } = {},
) {
  storage.actions.put({
    id,
    gatekeeperId: 1,
    caller: { from: "agent", chatId: 1 },
    createdAt: new Date("2026-08-01T00:00:00Z"),
    state: opts.state ?? "pending",
    type: "action",
    action: id,
    description: {
      title: `Action ${id}`,
      description: `Action ${id}`,
      implementsRevert: false,
      ...(opts.tag === undefined
        ? { actionKind: { tag: "t:create_work_item", label: "create_work_item" } }
        : opts.tag === ""
          ? {}
          : { actionKind: { tag: opts.tag, label: opts.tag } }),
      ...(opts.autoApprovable === undefined ? {} : { autoApprovable: opts.autoApprovable }),
    },
  } as never);
}

function enableRule(storage: AutoApprovalStorage, tag = "t:create_work_item") {
  storage.autoApproveTags.put({
    gatekeeperId: 1,
    actionKind: { tag, label: tag },
    enabledBy: { type: "user", id: "enabler@example.invalid", name: "Enabler" },
  } as never);
}

async function drainApplied(storage: AutoApprovalStorage): Promise<number[]> {
  const applied: number[] = [];
  const applyFn: ApplyPendingActionFn = async (record) => {
    applied.push(record.id);
    const fresh = storage.actions.get(record.id) as Record<string, unknown> | undefined;
    if (fresh && fresh.type === "action") {
      fresh.state = "approved";
      storage.actions.put(fresh as never);
    }
  };
  await new AutoApprovalDrainer(storage, applyFn).drain(1);
  return applied;
}

suite("classifyTool — the m01/neg-mcp branches (tools.ts:62-77)", () => {
  test("honours readOnlyHint true on a byo endpoint: read path on the server's word", () => {
    const mislabeled = {
      name: "tracker_create_work_item",
      annotations: { readOnlyHint: true, destructiveHint: true },
    };
    const classified = classifyTool(mislabeled as never, "byo");
    assert.equal(classified.mode, "read");
    assert.equal(classified.classifiedBy, "server-annotation");
    assert.equal(classified.autoApprovable, false);
  });

  test("never auto-approves a write on a byo endpoint, whatever it claims", () => {
    const classified = classifyTool(TRACKER_TOOL as never, "byo");
    assert.equal(classified.mode, "action");
    assert.equal(classified.autoApprovable, false);
  });

  test("refuses auto-approval without an exact idempotentHint === true", () => {
    const unannotated = {
      name: "tracker_create_work_item",
      annotations: { readOnlyHint: false, destructiveHint: false },
    };
    assert.equal(classifyTool(unannotated as never, "vetted").autoApprovable, false);
  });

  test("auto-approves only vetted + non-destructive + idempotent", () => {
    const classified = classifyTool(TRACKER_TOOL as never, "vetted");
    assert.equal(classified.mode, "action");
    assert.equal(classified.autoApprovable, true);
  });
});

suite("AutoApprovalDrainer — the neg-drain-skip/s02 branches (auto-approval.ts:58-92)", () => {
  test("applies eligible pending actions in ascending id order", async () => {
    const storage = makeStorage();
    enableRule(storage);
    putAction(storage, 3, { autoApprovable: true });
    putAction(storage, 1, { autoApprovable: true });
    putAction(storage, 2, { autoApprovable: true });
    assert.deepEqual(await drainApplied(storage), [1, 2, 3]);
  });

  test("stops at a manual gate and never skips ahead of it", async () => {
    const storage = makeStorage();
    enableRule(storage);
    putAction(storage, 5, {}); // no author verdict: a human gate
    putAction(storage, 7, { autoApprovable: true });
    assert.deepEqual(await drainApplied(storage), []);
  });

  test("eligibility reads exactly the author verdict and the rule — no other field", async () => {
    // The s02 mechanism: nothing in the record carries a disposition, so a record staged
    // under an unresolved judgment is indistinguishable from any other eligible record.
    const storage = makeStorage();
    enableRule(storage);
    putAction(storage, 1, { autoApprovable: true });
    assert.deepEqual(await drainApplied(storage), [1]);
  });
});

suite("the registered scenario's foreclosures, read from pinned source", () => {
  // PREREGISTRATION section 4c and SPEC section 4a rest on these two source facts. They
  // are assertions about the pinned TEXT, not about behaviour: the study never runs the
  // connector, and this suite says so rather than implying a behavioural demonstration.
  const clone = (): string => {
    const source = process.env.CFOS_SOURCE;
    if (!source) throw new Error("CFOS_SOURCE must be set");
    return source;
  };

  test("the pinned MCP connector opts out of simulation and awaits the decision", () => {
    const session = readFileSync(
      join(clone(), "packages/mcp-shared/src/session.ts"),
      "utf-8",
    );
    assert.ok(
      session.includes("Nothing about a queued call is simulated"),
      "the connector's own statement that it does not simulate is missing",
    );
    assert.ok(
      session.includes("awaitDecision: true"),
      "the connector's awaitDecision opt-out is missing",
    );
  });

  test("the generic contract makes simulation advisory, not required", () => {
    const contract = readFileSync(
      join(clone(), "packages/workshop-shared/src/gatekeeper.ts"),
      "utf-8",
    );
    assert.ok(
      contract.includes("there is no strict requirement that a gatekeeper does such"),
      "the contract's own opt-out language is missing",
    );
  });
});

suite("catalog identity helpers", () => {
  test("actionKindFor derives the policy tag from the portal's scope and tool", () => {
    // The adapter's Python reproduction is compared against this same pinned function
    // by `harness/tests/test_study.py::test_adapter_tag_reproduction_agrees_with_upstream`,
    // which is where that guarantee actually lives — a TypeScript restatement of
    // upstream's own body could only ever assert f(x) == f(x).
    const scope = "mcp-portal:https%3A%2F%2Ftracker.example%2Fmcp:portal-tracker";
    const kind = actionKindFor(scope, "tracker_create_work_item");
    assert.equal(
      kind.tag,
      "mcp-portal%3Ahttps%253A%252F%252Ftracker.example%252Fmcp%3Aportal-tracker" +
        ":tracker_create_work_item",
    );
    assert.equal(kind.label, "tracker_create_work_item");
  });

  test("catalogRevision moves when a policy-feeding annotation moves", async () => {
    const before = await catalogRevision([TRACKER_TOOL as never]);
    const flipped = {
      ...TRACKER_TOOL,
      annotations: { ...TRACKER_TOOL.annotations, readOnlyHint: true },
    };
    const after = await catalogRevision([flipped as never]);
    assert.notEqual(before, after);
  });
});

async function main(): Promise<void> {
  let failures = 0;
  for (const item of cases) {
    try {
      await item.body();
      console.log("ok   " + item.name);
    } catch (error) {
      failures += 1;
      console.error("FAIL " + item.name);
      console.error(error);
    }
  }
  console.log(`${cases.length - failures}/${cases.length} upstream probes passed`);
  if (failures > 0) process.exit(1);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
