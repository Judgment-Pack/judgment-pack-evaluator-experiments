# Deviations — Study 005

Deviations from [`PREREGISTRATION.md`](PREREGISTRATION.md) are recorded here as they occur,
never by editing the preregistration.

## Pre-trial mechanical repairs

1. The first `validate` invocation failed before any model trial because its direct MCP smoke-test
   receipt targeted the study directory, which is read-only under the operator's current workspace
   sandbox. The smoke test was changed to use a unique temporary directory. This changes neither
   fixtures, prompts, trial settings, nor scoring; real per-cell receipts still target their
   retained trial directories.
2. The first pre-trial harness commit accidentally tracked one generated Python bytecode file.
   Before any model trial, the file was removed and a study-local ignore rule was added for Python
   caches. No executable source, fixture, prompt, or score changed.
3. Before any model trial, the runner was hardened to stop the fixed sequence on a CLI failure
   that occurs before any turn, tool call, or final response. It retains the failed infrastructure
   attempt and permits only the one rerun allowed by the preregistration. This prevents a common
   launch or configuration failure from being repeated across all 48 cells; treatment, fixtures,
   completed-cell handling, and scoring are unchanged.

## Launch-time infrastructure repair

4. All 48 first CLI attempts were rejected by the OpenAI API with HTTP 400
   `invalid_json_schema`: the service's strict structured-output subset requires every object to
   declare `additionalProperties: false`. The rejection occurred before model inference or MCP
   tool discovery; there were no agent messages, tool receipts, or final responses. The runner had
   incorrectly treated its local `turn.started` event as proof that treatment was received, so it
   continued instead of stopping after the first rejection.

   Each prompt remained byte-identical for the rerun; every original event log, stderr log, and
   completion marker is separately retained as infrastructure attempt 1. The response schema was
   mechanically closed over the same registered output domain: facts are either `{}` or the
   registered `screening.matchCount` shape, and evidence has the registered `screening-record`
   member. Expected outputs and comparison logic did not change. The runner now recognizes the
   explicit pre-inference schema rejection and reclassifies it transparently. Each cell used its
   single preregistered infrastructure rerun; no model result was replaced.
