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

## 4. The preregistration's independence premise is false

**What.** [`PREREGISTRATION.md`](PREREGISTRATION.md) §1 asserts that the rule and the verifier "were
built separately, for different purposes, without either being written against the other," and rests
the study's informativeness on it. The adversarial review established from the repository that both
halves are wrong:

- Study 007's `verify_candidate` re-derives the claim by calling `derive_payload` (007
  `harness/study.py:465-467`) and grades the candidate against that output, with a superset test on
  the basis (`:499`). `derive_payload` is Arm B, so the verifier's semantic core *is* the arm Arm C
  is compared against.
- The rule under test was authored from `derive_payload`: `derivation-rule/README.md:26-27` describes
  its 13-case corpus as cross-checked to reproduce that function's claim on every case.

**Scope.** Framing, not execution. No number changes; the harness always did what the protocol said.

**Bearing on endpoints.** Severe and interpretive. D1 and D2 measure transcription fidelity against
Arm B rather than independent admission; D2 cannot fail while D1 passes, so the preregistration's
named "worst outcome" (§6) is unreachable; D4 is a determinism check; D5 is entailed by D1. Only D3
(basis **equality**, which the verifier does not force) and the probe carry independent content.
Recorded here rather than by editing the frozen preregistration. `ANALYSIS.md` leads with it and
`RESULTS.md` states per endpoint what each actually tests.

## 5. Arm B re-implements `candidate_from_gateway`

**What.** The preregistration names Study 007's `candidate_from_gateway` as Arm B. The harness calls
`derive_payload` directly and rebuilds the envelope in its own `envelope()`, so that Arm B and Arm C
share one assembler and can differ only in claim and basis.

**Scope.** The rebuild is structurally identical to 007 `study.py:287-326`. Originally the two arms
also differed in the `explanation` string, making the preregistration's "differ in exactly one
respect" literally false; both arms now use one shared constant.

**Bearing on endpoints.** None. `explanation` is only type-checked by the verifier.

## 6. Controls and freeze hardening added after scoring

**What.** After the adversarial review, and after D1-D5 were first scored, the harness gained: two
calibration controls (an un-derived wide basis, and a one-pointer-short basis); a `cellData` digest
freezing every per-cell artifact, receipt, `cell.json` and `final.json`; `gateway.key`, `common.py`
and `acquisition_gateway.py` added to `FROZEN_INPUTS`; a restored `verify_committed_freeze()` (Study
007 had this control and Study 008 had dropped it); stricter D4 scoring so a runtime failure on both
arms no longer counts as agreement; and Arm A's admission derived from Study 007's `RESULTS.json`
(`M2`) instead of transcribed constants.

**Scope.** The controls are **not** registered endpoints and are never pooled with D1-D5. The freeze
and scoring changes were applied before the final re-run, and every registered endpoint was recomputed
from scratch afterwards with unchanged values.

**Bearing on endpoints.** No registered value changed. The wide control (admitted 24/24) is what
establishes that D1 cannot distinguish a derived basis from a generous authored one — i.e. it was
added specifically because it weakens the study's headline.
