// The study's single injected seam (PREREGISTRATION section 2, recorded in PINS.json):
// `auto-approval.ts` constructs a logger whose transitive import chain reaches
// `cloudflare:workers` for the `tracing` object. The drainer never calls the tracer on any
// adjudicated path; this stub exists so the module graph loads under plain Node. The class
// exports mirror the shape upstream's own node-env stub exports
// (packages/mcp-shared/__tests__/stubs/cloudflare-workers.ts) for type-position imports.

export class DurableObject<Env = unknown> {}
export class RpcTarget {}
export class WorkerEntrypoint<Env = unknown> {}
export class RpcStub<T = unknown> {}

// Inert tracing surface: enough for `createTracer`-style closures to be constructed and
// never meaningfully invoked. Every method is a no-op that returns something shaped like
// "a span" so an accidental call cannot throw and change control flow.
const span = {
  end() {},
  setAttribute() {},
  setAttributes() {},
  recordException() {},
  addEvent() {},
  setStatus() {},
};
export const tracing = {
  enterNewSpan(_name: string, callback?: (span: unknown) => unknown) {
    return typeof callback === "function" ? callback(span) : span;
  },
  startSpan(_name?: string) {
    return span;
  },
  getActiveSpan() {
    return span;
  },
};
