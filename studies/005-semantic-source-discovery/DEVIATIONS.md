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
