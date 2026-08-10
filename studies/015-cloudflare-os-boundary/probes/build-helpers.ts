// Build-time helper: lets the fixture builder use the pinned platform's own identity
// functions instead of reimplementing them (PREREGISTRATION section 2). Bundled by the
// clone's esbuild like every probe entrypoint. Driven by env:
// BUILD_REQUEST names a JSON file {actionKinds: [{scopeTag, toolName}], catalogs: {name:
// [tools]}}; BUILD_OUT receives the computed values. Build path only; the verification
// ceremony never reads this file's output directly — the values it computes are frozen
// into fixtures and adjudicated as bytes.

import { readFileSync, writeFileSync } from "node:fs";

import { actionKindFor, catalogRevision, describeCall } from "@gadgets/mcp-shared/tools";
import { endpointTag } from "@gadgets/mcp-shared/scope";

async function main(): Promise<void> {
  const requestPath = process.env.BUILD_REQUEST;
  const outPath = process.env.BUILD_OUT;
  if (!requestPath || !outPath) {
    throw new Error("BUILD_REQUEST and BUILD_OUT must be set");
  }
  const request = JSON.parse(readFileSync(requestPath, "utf-8")) as {
    actionKinds?: Array<{ scopeTag: string; toolName: string }>;
    catalogs?: Record<string, unknown[]>;
    endpointTags?: string[];
    describeCalls?: Array<{
      label: string;
      serverName: string;
      endpoint: string;
      tool: unknown;
      toolArgs: unknown;
      mode: "read" | "action";
      classifiedBy: "server-annotation" | "default";
    }>;
  };
  const actionKinds = (request.actionKinds ?? []).map((item) => ({
    ...item,
    kind: actionKindFor(item.scopeTag, item.toolName),
  }));
  const catalogs: Record<string, string> = {};
  for (const [name, tools] of Object.entries(request.catalogs ?? {})) {
    catalogs[name] = await catalogRevision(tools as never);
  }
  const endpointTags: Record<string, string> = {};
  for (const endpoint of request.endpointTags ?? []) {
    endpointTags[endpoint] = endpointTag(endpoint);
  }
  const describedCalls: Record<string, { title: string; description: string }> = {};
  for (const item of request.describeCalls ?? []) {
    describedCalls[item.label] = describeCall({
      serverName: item.serverName,
      endpoint: item.endpoint,
      tool: item.tool as never,
      toolArgs: item.toolArgs as never,
      mode: item.mode,
      classifiedBy: item.classifiedBy,
    });
  }
  writeFileSync(
    outPath,
    JSON.stringify({ actionKinds, catalogs, endpointTags, describedCalls }, null, 2) + "\n",
  );
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
