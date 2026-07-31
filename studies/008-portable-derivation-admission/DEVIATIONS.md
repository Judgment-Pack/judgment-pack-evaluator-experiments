# Deviations — Study 008

Deviations from [`PREREGISTRATION.md`](PREREGISTRATION.md), recorded as they occurred. The
preregistration itself is never edited.

## 1. Sibling-repository path resolution under a git worktree

**What.** Study 007's harness locates the runtime binary and the screening pack as siblings of the
experiment repository's git *toplevel*. Study 008 was developed in a git worktree, where the toplevel
is the worktree directory, so those siblings did not resolve. `harness/study.py::_bind_sibling_repos`
resolves them from the *common* git dir instead.

**Scope.** Path resolution only. No verifier, derivation, evaluation, or scoring semantics change.
The same binary and pack are used as a non-worktree checkout would use.

**Bearing on endpoints.** None. D4 would otherwise have been uncomputable in this environment.

## 2. Attestation key loading

**What.** The first run loaded `fixtures/gateway.key` with `read_bytes()`; Study 007 loads it with
`read_bytes().strip()`. The trailing newline made every receipt fail attestation, so both arms were
rejected 24/24 on the first run.

**Scope.** A harness defect, corrected before any endpoint was scored. It was detectable precisely
because it hit Arm B — Study 007's own assembler, which must pass — so it could not be mistaken for a
finding.

**Bearing on endpoints.** None. No result was recorded from the defective run; `run` rewrites
`trials/` from scratch on each invocation.

## 3. Exploratory probe added after scoring

**What.** `harness/probe.py` and [`PROBE.json`](PROBE.json) were added after D1–D5 were scored, to
test the risk the preregistration registered under D3 (short-circuit evaluation reading fewer
pointers than the verifier requires) on a payload shape Study 007's corpus does not contain.

**Scope.** Explicitly **not** a registered endpoint and never pooled with D1–D5. It adds no cell, and
changes no scored number.

**Bearing on endpoints.** None numerically, but it is load-bearing for interpretation: it shows D3's
24/24 is corpus-contingent. It is reported in [`RESULTS.md`](RESULTS.md) under its own heading and
analysed in [`ANALYSIS.md`](ANALYSIS.md). Adding a probe that *weakens* the study's headline reading
after the fact is the direction of bias this record exists to make visible.
