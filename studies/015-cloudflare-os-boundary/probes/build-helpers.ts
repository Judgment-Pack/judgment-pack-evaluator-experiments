// Build-time helper: lets the fixture builder use the pinned platform's own identity
// functions instead of reimplementing them (PREREGISTRATION section 2). Bundled by the
// clone's esbuild like every probe entrypoint. Driven by env:
// BUILD_REQUEST names a JSON file {actionKinds: [{scopeTag, toolName}], catalogs: {name:
// [tools]}}; BUILD_OUT receives the computed values. Build path only; the verification
// ceremony never reads this file's output directly — the values it computes are frozen
// into fixtures and adjudicated as bytes.

import { readFileSync, writeFileSync } from "node:fs";

import { actionKindFor, catalogRevision } from "@gadgets/mcp-shared/tools";

async function main(): Promise<void> {
  const requestPath = process.env.BUILD_REQUEST;
  const outPath = process.env.BUILD_OUT;
  if (!requestPath || !outPath) {
    throw new Error("BUILD_REQUEST and BUILD_OUT must be set");
  }
  const request = JSON.parse(readFileSync(requestPath, "utf-8")) as {
    actionKinds?: Array<{ scopeTag: string; toolName: string }>;
    catalogs?: Record<string, unknown[]>;
  };
  const actionKinds = (request.actionKinds ?? []).map((item) => ({
    ...item,
    kind: actionKindFor(item.scopeTag, item.toolName),
  }));
  const catalogs: Record<string, string> = {};
  for (const [name, tools] of Object.entries(request.catalogs ?? {})) {
    catalogs[name] = await catalogRevision(tools as never);
  }
  writeFileSync(outPath, JSON.stringify({ actionKinds, catalogs }, null, 2) + "\n");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
