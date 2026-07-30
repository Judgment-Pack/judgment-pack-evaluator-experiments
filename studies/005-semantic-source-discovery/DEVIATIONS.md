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
