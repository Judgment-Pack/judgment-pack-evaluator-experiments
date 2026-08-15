# Preregistration — Study 019: authorship across representations

**Status: DRAFT. Not frozen. Nothing has run. No pin is filled; every execution before the
freeze is a PILOT and supports no claim. This draft carries the registered section structure
and the design decisions already taken; every open item is marked `TODO(prereg)` and must be
closed before any review round can return `freezable as written`.**

## The freeze and the primary attempt

`TODO(prereg)`: this section is written in full before the freeze, in the 016/017 form —
naming (a) the freeze commit by reference ("the squash-merge commit of PR #NN on `main`"),
(b) the literal attempt root `results/primary-attempt-001`, which must not exist at the freeze
and which the scorer refuses if it does, and (c) the exact governing invocation under the
pinned interpreter, e.g.
`<the CPython PINS.json pins> harness/score.py --attempt-root results/primary-attempt-001`.
The first invocation of that command is the primary attempt, crash and all.

## 1. Question

Within the registered JPS-expressible policy fragment, does a constrained judgment
representation (JPS) change how reliably a model authors an executable policy — compared with
raw Rego and with Rego plus a prescribed judgment convention?

**R1 (primary, retractable), difference form, scope inside the claim:** within the registered
JPS-expressible fragment, under single-shot authorship, arm A's per-run perfect-gold-agreement
rate exceeds arm B's: the exact A−B difference interval lies strictly above 0 at the
registered minimum meaningful difference δ (`TODO(prereg)`: fix δ and publish the
operating-characteristic table for N=50/arm, the 012 §5.4 pattern). An INDETERMINATE or
unsupported outcome licenses neither "constraint doesn't help" nor any A-vs-C conclusion.

**The A-vs-C contrast** is reported with the same machinery (difference interval, δ,
INDETERMINATE row), interpreted confirmatorily only if R1 is decided (hierarchical
multiplicity rule). No action table is registered: what each outcome would mean for the
program lives in §11, which is explicitly not a registered commitment.

**R2 (secondary, descriptive):** the failure map — where each representation's authoring
attempts fail (E3 taxonomy), what each run-authored test suite pins (E4), and how far
independent authors diverge from one another (E5). R2 is never adjudicated and never
falsifies.

## 1a. Population and prospective content

This study has **no locked-replication stratum and no reviewer-holdout stratum**; it uses the
arm vocabulary of Studies 011/012, the program's authorship-rate precedents, not the
two-strata shape of 013–018. The two-strata shape does not apply because nothing about the 150
authoring runs has been observed at freeze time: the prospective content of an authorship-rate
study is the post-freeze runs themselves. Reviewer-authored prospective content lives in the
sealed reviewer mutant set (§4) — first executed at the primary attempt, scored "as authored",
reported separately, moving nothing — and in reviewer-vs-maintainer gold disagreement,
reported as an ambiguity diagnostic that can never move E1.

**Population rule (enforced in code, the Study 001/011 lesson).** The denominator of every
per-arm rate is attempted runs whose apparatus succeeded. Apparatus/transport failures (slot
shape, call exit, golden-context mismatch, binary digest mismatch, transcript refusal) are
pipeline-invalid and excluded. Every failure attributable to what the author emitted —
unparseable artifact, schema-invalid pack, `opa check` failure, v0 syntax, no extractable
fenced block, unreadable output shape — is an authoring outcome: valid, counted, scoring zero
gold agreement. E1 and E2 are computed on the same denominator. A harness test diffs the prose
partition table against the scorer's code partition and against every code `admit()` can
return.

## 2. Apparatus and pins

All pins null until the freeze; the scorer labels any run PILOT while any pin is null.

- **jpack**: current release (v0.17.0 line at design time) pinned in the Study 013 shape —
  releaseTag, releaseAsset, archiveSha256 verified against `checksums.txt`, binarySha256,
  reproducible-build attestation. Verdicts and §8.4 error classes are read from the JSON
  payload only; exit codes distinguish "invocation failed" (3/4/5 — harness-error terminal)
  from "the evaluator answered" (0/1/2). The harness runs outside any `jpack.json` that
  declares an `audit` member. `TODO(prereg)`: fill the pin block.
- **OPA**: current stable 1.x pinned as `opa_linux_amd64_static` plus the published per-asset
  sha256, version resolved from the release page at pin time — never from memory. No
  reproducible-build claim is available (official builds embed timestamp and hostname); the
  pin is against the published artifact only, stated here rather than left for review. Rego
  dialect v1, pinned in prompt and command line; a v0 emission is an authoring outcome with
  its own code. A capabilities file is generated from the pinned binary with a registered
  denylist (clock, network, rand, uuid, `opa.runtime`, print/trace, timezone-taking time
  forms, `net.cidr_expand`), and a canary negative control (a `time.now_ns` policy that must
  be refused) demonstrates the gate has power. Scored invocations use `--strict`,
  `--strict-builtin-errors`, `--fail`, `--timeout`, `env -i` with `TZ=UTC`, and per-run
  exclusive directories; `opa test` JSON is normalized (strip `duration`, sort by
  package/name) before hashing. `TODO(prereg)`: resolve version + digests; verify empirically
  the exit-code behavior, whether `opa exec` accepts `--capabilities`, and the checksum
  artifact shape; record the license from the repository `LICENSE` at pin time.
- **Authoring toolchain**: the program's standing pinned stack (Study 012's codex pins),
  re-pinned at design time; one model, single-model ceiling in §9. `TODO(prereg)`: re-pin.
- **Interpreter and schedule**: CPython pinned by implementation/series/exact version; runs
  sequential, never parallel; all slots within one UTC calendar day (crossing midnight is a
  DEVIATIONS entry, not a stopping rule); arm-interleaved first-order carryover-balanced
  schedule re-derived for three arms and asserted by a harness test. N = 50 runs/arm, 150
  slots, fixed in the registry before the batch (decided 2026-08-14).

## 3. The contest policy and its calibration

Vendor-approval domain, confined to the JPS-expressible fragment: three outcomes plus
unresolved semantics; ~8–12 rules over risk score, requested spend, country risk, sanctions
status (ordinary fact strings) and financial evidence (the §8.2 evidence document); 4–6
numeric thresholds with mixed inclusive/exclusive boundaries; 2–3 exceptions exercising all
three effects; precedence encoded as mutual exclusion (the hand-written negation count is a
registered covariate); `fallbackOutcome` absent over part of the space so `no-match` is
reachable; escalation present, its target scored descriptively only. Both tri-state
mechanisms are present deliberately, their semantics stated exactly in prose. The
expressiveness census (descriptive companion, never adjudicated) records per row whether a
gap is a deliberate Core refusal or a maintainer roadmap item — numeric outputs are the
latter (stated 2026-08-14, planned for a later JPS version). Registered design rule: a spec
change landing before the freeze does not expand the contest fragment; widening the fragment
re-opens the design and its review, and the enriched output side belongs to a follow-up
against the version that ships it. The canonical
facts grid is authored as decimal strings with a registered fixed scale per numeric field; the
Rego projection is `to_number` over those exact bytes with a freeze-time round-trip assertion.

Ordering and contamination control: draft prose → ambiguity audit → gold v0 authored with
per-row clause citations → ambiguity stratum frozen → only then calibration pilots (labelled,
non-citable, all arms). Prose edits after pilots are allowed only where a mechanical check
shows no unchanged gold row cites an edited clause. Every piloted-and-discarded candidate
policy is published with its pilot rates; the frozen policy's own pilot rate is not an
estimate of anything. The calibration target is the region where the difference endpoints are
decidable (no arm saturated at 0 or 1); the stopping rule is registered.
`TODO(prereg)`: the policy prose itself, the grid, and the calibration stopping rule.

## 4. Oracle, references, and mutants

- Gold suite authored by the maintainer from the prose alone, per §3's ordering; every row
  cites its governing clause(s).
- Clean-room second oracle bound to `CLEAN-ROOM-PROTOCOL.md` by name, implemented from the
  POLICY.md bytes and nothing else by a **different vendor from the arms' authoring stack**
  (hard requirement). Deliverables: room brief, numbered DECISIONS.md, transcript audit
  recorded in the import commit, void-on-violation. Disagreement disposition, not a
  zero-disagreement gate: every divergence retained verbatim, adjudicated in writing against
  cited clauses, adjudication published; a divergence the prose cannot settle routes its rows
  to the ambiguity stratum automatically.
- Ambiguity stratum membership is mechanical: a row enters iff the two oracles disagree on it
  or the clean-room DECISIONS.md flags its governing clause as undetermined. Frozen before any
  pilot artifact is opened; E1 published both with and without the stratum.
- One reference implementation per language (maintainer-authored, verified against gold and
  both oracles, conforming to the shared naming appendix), frozen. Two disjoint mutant sets:
  the **adequacy set** (maintainer-authored, executed pre-freeze; the gold suite must kill
  100% of it or the freeze is blocked) and the **reviewer set** (cross-vendor
  reviewer-authored, sealed, first executed at the primary attempt, scored "as authored").
  Mutant pairing across languages is an observable criterion: paired iff the gold-grid
  disagreement sets against their own references are identical under the alignment map;
  witness sets computed and published at freeze; cross-arm E4 runs over the paired subset
  only, and the per-language unpairable count is published as a finding.
`TODO(prereg)`: gold suite, references, mutant sets, alignment map (two axes: run-level
admission; row-level APPROVE/REVIEW/REJECT/UNRESOLVED(reason-set)/ROW-ERROR(class), with the
worked conflict-row example in all three arms).

## 5. Arms, prompts, and endpoints

Arms: **A** JPS pack + test matrix (matrixVersion 2); **B** Rego v1 + opa tests with an
informal output contract; **C** Rego v1 + opa tests + the prescribed judgment convention —
result contract (JSON Schema) **plus** conventions for mutual exclusion/precedence and an
explicit unresolved/conflict result (decided 2026-08-14: full convention). Prompts are
assembled mechanically from registered fenced blocks: a byte-identical shared header (contest
prose + the naming appendix — outcome ids, fact pointer paths, evidence-requirement ids, Rego
package path + entrypoint rule name) plus an arm suffix. Arm B's prose contract is a
registered mechanical de-formalization of C's JSON Schema with its own digest, so B and C
differ in formality only. Excerpt parity is a sufficiency criterion asserted by a freeze test
(every construct the arm's reference uses appears in the arm's excerpt; the reference uses no
construct absent from it); the Rego excerpt derives by a registered rule from the official OPA
docs at a pinned commit; the cross-vendor reviewer holds a veto over both excerpts. Authoring
is single-shot, no tools, no repair; artifact extraction is a registered deterministic
fenced-block rule; prompt iteration during design is governed by a symmetric, disclosed
budget. System boundary rule: in-system = anything the pinned binary does at evaluation time;
out-of-system = anything requiring an authoring loop.

Endpoints (exact Clopper–Pearson intervals; scope = the §8.3 portable disposition under the
alignment map, applied consistently — `trace[]` and escalation-target content are outside it):
- **E1 (primary quantity)**: per-run perfect gold agreement, ITT denominator (§1a). Primary
  contrasts: exact A−B and A−C difference intervals with δ and an explicit INDETERMINATE
  verdict row that licenses nothing and triggers nothing.
- **E2**: authoring-validity profile — the ordered code table over the run-level axis (four
  Core §8.4 classes; `opa check` codes; v0-syntax; output-shape-unreadable), same denominator.
- **E3**: row-level failure taxonomy (boundary off-by-one, unknown-handling,
  evidence-mechanism confusion, precedence/exclusion, missing-rule, outcome-mapping,
  contract-shape); arm-structural categories are within-arm-only, enforced in the scorer.
- **E4**: run-authored test kill rate — a suite is admitted only if it passes its language's
  unmutated reference (identity control, registered as a mutant-set member); a kill = passes
  reference AND fails mutant; per-arm identity-failure rate is its own published quantity;
  cross-arm comparison over the paired mutant subset only.
- **E5**: interpretive-spread census (012's registered census machinery).
- Non-endpoints, with registered reasons: coverage probes (carry no expectations and never
  gate — verified against the runtime); `trace[]` and escalation-target content (outside the
  portable disposition); repair count (no-repair discipline); LOC (census only).

## 6. Validity channel (separate from detection)

Control gates, above every substantive row of the decision rule, adjudicating the claim in
neither direction when they fail: both references pass gold 100% at attempt time; the OPA
capabilities canary is refused; the golden-context gate holds (two agreeing probe captures;
isolation negative control under recorded operator assent); every binary digest matches its
pin. Ordered, exhaustive decision rule with a last row that always matches, in the 012 form.
`TODO(prereg)`: the full ordered table.

## 7–8. Controls, counting integrity, enforcement

Ported machinery (by digest, two-sided PORTS.md table): 012's call wrapper, batch driver
(schedule re-derived for three arms), integrity/transcript/golden-context controls, census,
scorer skeleton. New builds: per-language admission layer, two-engine execution layer,
alignment map, mutant tooling with identity control, C's convention document, B's
de-formalization, OPA capabilities tooling. The manifest is scoped per ADR 0004:
`DEVIATIONS.md` and `README.md` excluded by named constant with an asserting harness test
(the 014 `REGISTERED_DOCUMENTS`/`EXCLUDED_DOCUMENTS` shape). `TODO(prereg)`: the full §7/§8
text in the 016/017 fully-spelled-out form.

## 9. What this study cannot show

Fidelity is measured within the JPS-expressible fragment, selected by arm A's expressive
envelope and no other criterion; the program's own census (Study 003: 12/12 real decisions
escape the pack) says this fragment does not cover real business decisions, and no result
here generalizes beyond it. Single-shot authorship only — no outcome is evidence about tooled
authoring workflows, which are the registered follow-up (as is the high-prevalence
constrained fourth arm, JSON Logic/DMN, deferred 2026-08-14). One model, one day, one policy
family, one prompt per arm. Unless the registered gradient measurement runs, no direction of
the result separates representation from training familiarity, and both directions are
reported as confounded. Joint-reading prohibition: the expressiveness census and the fidelity
rates live on different stimuli; no tradeoff statement combining them is licensed. The census
describes spec 0.2.0-draft as pinned; gaps recorded as roadmap items (numeric outputs) are
statements about the pinned version, not about JPS's future, and are not scored. An
INDETERMINATE or unsupported contrast licenses no negation. The gold suite is two authors
deep, not independent of the program. Nothing here measures whether any policy or fact is
true, and nothing claims any JPS conformance.

## 10. Publication commitment

All rates, all arms, all intervals, the full decision table, every identity-failure and
unpairable-mutant count, published whichever way they land, with a pass's prominence.
CORRECTION.md targets (verbatim wording, venue, URL, retrieval date) are pinned before the
freeze. `TODO(prereg)`: the pinned targets.

## 11. What we would do with each outcome (NOT a registered commitment)

This section is discussion, deliberately outside the registered protocol; no observed result
obligates any of it. If A−B and A−C both decide in A's favor, the evaluator/language line
continues with the census as its honest boundary statement. If A and C cannot be separated at
δ, or C decides above A, the natural next artifact is a runtime/spec ADR exploring a JPS
semantic profile over OPA (spec + schemas + conformance + gateway retained), taking this
study's census and asymmetry ledger as inputs. The gateway line is unaffected by every
outcome — that independence is by design, and is part of why this study is safe to run.
