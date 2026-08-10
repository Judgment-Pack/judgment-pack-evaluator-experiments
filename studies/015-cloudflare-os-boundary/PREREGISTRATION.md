# Preregistration — Study 015: the judgment/staged-action boundary under a governed-agent platform

**Status: DRAFT until frozen by merge after pre-freeze cross-vendor review; governing thereafter.**

**Nothing has run.** At the time of this draft no registered attempt exists; everything executed
during harness development lands under `pilots/`, is labeled harness validation, and supports no
claim. After the freeze this file is never edited; corrections go to [`DEVIATIONS.md`](DEVIATIONS.md).

Three companion artifacts are registered *with* this document and pinned at the freeze:
[`adapter/SPEC.md`](adapter/SPEC.md) (the retained-record model, commitment schema, verification
ceremony with exact verdict codes, and disposition→action map), [`harness/MATRIX.json`](harness/MATRIX.json)
(the machine-readable locked-replication cell registry the scorer adjudicates against) and
[`harness/MATRIX-HOLDOUT.json`](harness/MATRIX-HOLDOUT.json) (the reviewer-authored holdout
stratum). Where prose here and those artifacts could diverge, the pinned artifacts govern and the
divergence is a deviation.

## 1. Question

Cloudflare OS ships an open, inspectable governed-agent platform whose Gatekeeper contract stages
external side effects into an approval queue: capability introduction, observation-aware sharing,
human and automatic approval, deferred simulated effects, and an unsigned per-workspace action
log. Its action policy today is a connector-author Boolean plus a per-Gatekeeper user opt-in, and
its own source anticipates richer action descriptions and a future policy engine. A JPS
disposition is none of those things: it is a portable, deterministic judgment with explicit
unknown, conflict, and escalation. When a bridge carries the one into the other, the published
boundary analysis for this class of platform names five collapses a bridge must not perform and
several bindings it must add. This study makes those requirements executable and attempts to
falsify them.

**R1 (primary, retractable):** for every adjudicated **endpoint** cell in the registered
locked-replication matrix, the observed per-layer detection outcome (platform contract / adapter
binding / pinned-evaluator replay, plus the derived combined verdict) equals the per-cell
registered expectation in `harness/MATRIX.json`. Control-gate, demonstration and descriptive rows
are published in full and count toward nothing (§5).

**R2 (secondary, descriptive):** the detection-ownership map — which failures the platform's own
executable policy surface catches, which only the adapter's binding catches, which only
pinned-evaluator replay catches, and which nothing catches. R2 is a restatement of the matrix by
category, not an independent endpoint. Its most important content is registered in advance: the
per-cell `platformChecksEngaged` field makes visible that for most semantic cells the platform's
executable policy surface engages nothing — the platform cannot see judgment semantics, and the
study measures that instead of assuming it.

The study attempts to falsify the bridge, not to demonstrate compatibility. A cell caught by no
layer that was registered as detectable falsifies R1 and is reported with the same prominence as
a pass.

## 1a. Two strata (Study 014's postdictivity remedy, adopted from the start)

- **Locked replication** (`harness/MATRIX.json`, 24 cells). Expectations are corrected freely
  against pilot observations *before* the freeze; the registered run is therefore a conformance
  replication over behaviour the maintainer has already observed, falsifiable by regression and
  never readable as a prospective prediction. Every pilot that changed an expectation is retained
  under `pilots/` and named in [`DEVIATIONS.md`](DEVIATIONS.md).
- **Reviewer holdout** (`harness/MATRIX-HOLDOUT.json`). Cells authored by the pre-freeze
  cross-vendor reviewer, committed verbatim with attribution, and **never executed before the
  freeze**. `harness/score.py --include-holdout` refuses mechanically while
  `harness/PINS.json`'s `preregistration.sha256` is null, and a harness test asserts that
  refusal. Holdout results are reported separately and never merged into the locked stratum's
  counts. **An empty holdout is not a passing holdout**: if the reviewer authors no cells, the
  prospective-prediction gap stands open and this study says so.

The fixture builder and the binding verifier share one commitment/digest implementation
(`adapter/commitment.py`), so the locked stratum has no independent mutation oracle — the same
standing limitation Study 014 recorded, inherited knowingly.

## 2. Apparatus and pins

- **Cloudflare OS** at commit `b2a51b5426398c8353d9d4dd984bd525121ab5f2` (Apache-2.0; no tagged
  release exists — the pin is the only available behavioral baseline), cloned read-only and
  located via `CFOS_SOURCE`, **source unmodified**. Dependencies come from upstream's own
  `pnpm-lock.yaml` (digest pinned) via `pnpm install --frozen-lockfile --ignore-scripts`; the
  workspace declares no postinstall scripts. The pinned code the study executes: `classifyTool`
  and its helpers (`packages/mcp-shared/src/tools.ts`), `AutoApprovalDrainer`
  (`packages/workshop-backend/src/auto-approval.ts`), upstream's own mock Durable Object storage
  (`packages/workshop-backend/__tests__/mock-storage.ts`) and `createTypedStorage`
  (`packages/typed-storage/src/index.ts`); the pinned types the fixtures are held to:
  `ActionRecord`, `ActionDescription`, `ObservationDescription`, `AutoApproveTagRecord`,
  `AiChatAuthorInfo`. Per-file digests in `harness/PINS.json`; the probe runner self-reports the
  clone commit, tracked-tree cleanliness, node version, and every probed file's digest per
  attempt, and the scorer enforces the report against the pins.
- **The one injected seam:** `cloudflare:workers` is aliased to a study stub whose only used
  runtime export is an inert `tracing` object, because `auto-approval.ts` constructs a logger on
  the observability path. Nothing on any adjudicated code path reads the stub's behavior.
- **The probe toolchain:** every probe entrypoint is bundled by the pinned clone's own esbuild
  (lockfile-resolved version) with the upstream imports resolved into the clone, then run under
  the pinned node. Upstream's vitest path is unusable on this apparatus (its native rollup
  binary needs a newer glibc than the host provides) — recorded, and immaterial: the bundled
  modules are the same pinned sources either way.
- **jpack** v0.16.0 release binary, archive `sha256 1a12503c…ed59`, binary `sha256 7c11ebef…9325`
  — the same pins Studies 013 and 014 froze, including 013's reproducible-build corroboration.
  Located via `JPACK_BIN`, digest-checked before every use.
- **Baseline pack**: `data-request-intake-triage` — the specification's own conformance-corpus
  pack, vendored byte-for-byte (`sha256 5bdf53e5…3aca`). Every fixture's facts and
  evidence-availability documents are verbatim cases from the same corpus's seed manifest, so
  every disposition the study binds is one the specification registers, not one the study
  authored.
- Interpreter, node, venv, and every other pin: `harness/PINS.json`. **Pins are enforced, not
  declared** (§2 of the pins file's own note; enforcement is in `harness/score.py` and any
  mismatch is terminal pipeline-invalidity).
- `harness/STUDY-MANIFEST.sha256` is the exact-set whole-study manifest — protocol documents,
  pin registry, both matrix strata, every adapter, harness and probe source file, and every
  per-cell fixture manifest. Verified before any cell is adjudicated.

## 3. Scenario (deterministic, no models, no network)

A workspace connects one MCP Gatekeeper to a vetted tracker endpoint
(`https://tracker.example/mcp`) carrying tool `create_work_item` (annotations: not read-only,
not destructive, idempotent). The bridge under test evaluates the triage pack over a
conformance-case fact set; disposition `proceed` authorizes exactly one staged `create_work_item`
call whose arguments derive deterministically from the retained facts; every other disposition
authorizes inaction (`adapter/SPEC.md` §4). The staged call binds the commitment at staging time
and the published report binds it at report time (SPEC §3). Auto-approval follows the platform's
own two-signal rule: the author verdict on the action plus a user-enabled rule for the action
kind. All clocks in fixtures are fixed constants; fixture construction is a one-time act and the
frozen bytes, not the builder, are what the study scores.

**What is modeled, stated plainly** (SPEC §0 is the registered statement): the workspace queue
lifecycle and gatekeeper-side store are harness-modeled records — the platform's Durable Object
never runs. `ledger.json` uses the platform's own `ActionRecord` shape and is held to the pinned
**published** contract (`ActionLogEntry` and its member types, with the two server-only
fields stripped and stated) by the platform's own TypeScript compiler at the
lockfile-resolved version (`harness/typecheck.py`); holding it to the server-side type
itself proved impossible from the committed tree — the backend graph typechecks only
against a wrangler-regenerated `worker-configuration.d.ts` — and that is recorded as an
apparatus finding, not worked around. `platform.json` models what an instrumented
Gatekeeper deployment could retain. The
platform behaviors the study executes are the two its contract makes executable outside the
Durable Object: MCP tool classification and the auto-approval drain, both run as pinned upstream
code. The submit-time eligibility predicate and the apply chokepoint are welded to the Durable
Object (`overseer.ts:2868-2911`, `2481-2509`) and are **not** exercised; the drain carries an
independent copy of the same two-signal eligibility rule and upstream's own unit suite exercises
the drainer exactly this way. Runtime behavior of the platform is out of scope entirely —
detection here is post-hoc provability from retained artifacts (Study 013 owns the
runtime-behavior question for its own harness; nothing transfers).

## 4. Cells

24 cells in `harness/MATRIX.json`: 1 positive control, 3 negative controls (trust-tier refusal,
annotation refusal, drain-order refusal — proving the two pinned platform checks are alive on
exactly the branches the semantic cells lean on), 18 endpoint mutation cells across six
registered categories (A judgment-artifact, S semantic-collapse, O observation-evidence,
B binding-integrity, D deferred-simulation, and the endpoint rows of M annotation-trust), 1
demonstration (`m01-readonly-bypass`) and 1 descriptive boundary (`m02-ambiguous-commit`).

The S family is the published boundary analysis's five forbidden mappings, one cell each
(`s01` unresolved→rejected, `s02` unknown staged and auto-applied, `s03` operational failure
retconned as epistemic unknown, `s04` approval-as-evidence, plus `o01` observation-as-evidence),
with `s05` (handoff dropped) and `s06` (not-applicable executed) completing the disposition
space. The B family is the decision-to-staged-action binding profile exercised violation by
violation: reuse, argument drift, revision drift after delayed approval, gatekeeper substitution,
action-kind substitution, unbound execution. The D family is the deferred-approval protocol's two
hazards: a dependent action whose simulated premise was rejected, and simulated success reported
as a committed effect.

### 4a. Registered per-cell fields

Beyond its expectation, every cell registers `role` (`endpoint` / `control-gate` /
`demonstration` / `descriptive`, §5), `variant` (`none` / `stale-store` / `coherent-rebuild` /
`bridge-behavior` / `environment` / `out-of-band`), `attackerCapability` (§4b),
`registeredAbsences` (artifact names whose absence the registry authorizes — all empty in this
matrix; the vocabulary exists so absence-validity can never be inferred from an expected
verdict), and `platformChecksEngaged` (which pinned upstream checks the cf layer engages — the
registered visibility of every vacuous pass).

### 4b. Threat model — what each capability means and what it cannot reach

- **`none`** — the untouched baseline.
- **`bridge`** — the bridge itself misbehaves: it stages, applies, claims, or maps something the
  committed disposition does not authorize. Most semantic cells live here, because the boundary
  analysis's collapses are bridge behaviors, not attacks.
- **`store`** — the retained store is edited after the fact, either sloppily (`stale-store`:
  one artifact drifts, digests go stale) or coherently (`coherent-rebuild`: the envelope and
  commitment are rebuilt to agree with the forgery). No signature stops either, because the
  platform signs nothing; what stops the coherent rebuild is recomputation under the pinned
  evaluator — and only for forgeries that change what the retained inputs evaluate to.
- **`environment`** — the world moves: the external resource advances revision between staging
  and delayed approval, or an at-most-once dispatch lands in genuine ambiguity.
- **`out-of-band`** — an effect reaches the resource without an action record: the annotated
  read-path (`m01`, the platform's own documented annotation-trust tradeoff) or a non-Gatekeeper
  path (`b06`).

**The registered ceiling, inherited from Study 014 §4b and stated once:** every retained record
in this study is unsigned, because the platform provides no signing surface for action records
and no `WorkOrder.objective` equivalent to carry a signed commitment. A party that can rewrite
the *entire* retained store coherently — envelope, commitment, ledger, platform store, and
report together, around a disposition the retained inputs genuinely produce — presents a
consistent history this ceremony accepts. What the layers catch is internal inconsistency
(binding), input/output forgery that replay can recompute away (replay), and claims the
platform's own policy code refuses (cf). Catching a fully coherent rewrite requires an anchor
outside the store — a transparency log, a signed carrier, a reviewed-set lock analogue — which
the platform does not offer at the pin and which is out of scope here. **Decision currency** —
"a newer pack version has since been activated" — is likewise not store-internal, admits no
fixture distinct from the baseline, and is recorded as an analytic limitation, not a row
(Study 014 §4c's finding, unchanged by anything this platform ships).

### 4c. What the cf layer is and is not

The cf layer runs real pinned upstream code and nothing else. It is deliberately **not** a
platform verifier, because the platform ships none: no runtime schema validation, no signature,
no bundle checker — the action-record contract is TypeScript types and prose. The two checks the
cf layer runs are the two policy surfaces the pinned source makes executable outside a Durable
Object, and the negative controls prove both alive. A cf `pass` on a semantic cell therefore
means exactly what R2 needs it to mean: *the platform's own executable policy surface, given
everything the retained store knows, notices nothing* — with `platformChecksEngaged` making the
vacuous cases visible rather than silently green. The fixture typecheck (`harness/typecheck.py`: every ledger record held to the pinned
published contract types by the clone's own compiler) is a validity gate on the apparatus, not a
detection layer: a fixture that fails it is pipeline-invalid, never a cf fail.

## 5. Endpoints and decision rule

Per cell, the scorer records three independent layer outcomes and the derived combined verdict
(pass iff all pass), then compares the 4-tuple against the registered expectation. Adjudication
is on the registered **code** alone: each layer returns `{verdict, code, detail}` and the detail
string never enters a comparison. Divergence in either direction — a registered-detectable cell
that passes, a registered-pass layer that fails, or a different failure code than registered —
is a divergence.

Ordered, exhaustive, per registered attempt:

1. Any cell **pipeline-invalid** (§6), or any freeze-integrity mismatch (§2) →
   `R1 inconclusive — pipeline-invalid`; terminal for that attempt; no rerun replaces it.
2. Else, any **control-gate** row diverging → `R1 inconclusive — control gate failed`. The four
   control rows are validity gates on the apparatus, evaluated before any endpoint row; a gate
   failure voids the attempt rather than falsifying R1.
3. Else, zero divergences across the **endpoint** cells → `R1 holds`.
4. Else → `R1 falsified`, with every divergence listed.

`demonstration` (`m01`) and `descriptive` (`m02`) rows are adjudicated and published but count
toward nothing: `m01` is a disclosed designed demonstration of the platform's own documented
annotation-trust tradeoff and cannot be cited as a detection; `m02` is a registered boundary
whose all-pass row means "no offline layer can prove commit", not "nothing is wrong".

The scorer (`harness/score.py`) is the only thing that publishes; its argument surface is the
attempt root plus `--include-holdout` and nothing else. Adjudication is deterministic
recomputation from frozen fixture bytes; no output embeds a timestamp or an absolute path, so
running it twice must be byte-identical.

## 6. Validity channel (separate from detection)

**Pipeline-invalid** (excluded from adjudication, counted separately, never a detection): a cell
whose fixture fails its own manifest check; an artifact absent when the cell's
`registeredAbsences` did not authorize it, or present when it did; a layer outcome outside the
registered vocabulary; a crash of the harness itself as opposed to an outcome from a layer; a
fixture ledger that fails the pinned-types typecheck; any freeze-integrity or pin mismatch under
§2 — including the cf runner's clone-integrity self-report. A cell in any of these states is
**NOT-ADJUDICATED** — never a true or false detection.

Both of Study 014's round-1 properties are mechanical here from the start:

- **Validity and detection are independent.** Permitted absences are read from the cell's own
  `registeredAbsences` field and from nothing else.
- **Nothing fails silently.** `ATTEMPT.json` is written before any cell runs, and every failure
  path — including a crash inside a cell and a crash during finalization — persists a terminal
  pipeline-invalid `RESULTS.json`.

The exhaustive verdict-code vocabulary lives in `adapter/SPEC.md` §5. Harness tests diff the
SPEC table against the codes `verify.py` declares and the codes `score.py` classifies, **and**
construct a minimal condition for every registered code, asserting the exact code and the
first-failure ordering — so the vocabulary cannot drift from the counting and no registered code
can be unreachable prose.

## 7. Controls and counting integrity

- Positive control: the untouched baseline must pass all three layers (validity gate).
- Negative controls: `neg-mcp-byo-autoapply` and `neg-mcp-nonidempotent-autoapply` must fail the
  cf layer through the pinned classifier's own trust-tier and annotation branches;
  `neg-drain-skip` must fail it through the pinned drainer's stop-at-first-gate rule. Together
  they prove the cf layer's two checks are alive on exactly the branches `s02` needs to pass
  through, so `s02`'s registered cf-pass cannot be an artifact of a dead layer.
- `m01` is a disclosed designed demonstration, not a discovery; registered `demonstration`.
- `m02` is a registered boundary; its all-pass row is published as a boundary, counted as
  neither detection nor miss.
- Layer attribution is a design property of the families: A is caught by binding's digests or by
  replay alone (`a02`, `a03`, `s03` are the replay-only rows), S/O/B/D by the adapter's binding
  and by nothing else, and the negative controls by cf and by nothing else. No endpoint cell
  registers a multi-layer detection, so every detection is attributable to exactly one layer.
- No silent exclusions: every registered cell appears in the output with an outcome or
  NOT-ADJUDICATED. The scorer refuses an attempt directory that already exists.

## 8. What is enforced, what is recorded, what is not prevented

Enforced by machinery: fixture manifests; the whole-study exact-set manifest; every non-null pin
(prereg/matrix/SPEC digests when filled, `jpack` binary digest always, interpreter version,
`pip freeze` digest, node version, clone commit and cleanliness, probed-file digests); the
frozen cell-id set and per-cell schema; the SPEC/code verdict-vocabulary sync and per-code
reachability with first-failure ordering; the holdout refusal before the freeze; the fixture
typecheck against the pinned contract types; upstream bytes never vendored into the repo
(clone-only via `CFOS_SOURCE`); missing `CFOS_SOURCE` or `JPACK_BIN` failing the determinism
tests rather than skipping them.

Recorded, not enforced: the `cloudflare:workers` stub seam (observability path only); the
harness node version differing from upstream CI's own pin (22.23.1 vs 22.14.0); the platform's
absence of runtime validation for its own contract (the reason the typecheck gate exists); the
modeled status of `platform.json` and of effect attestations; that the builder and verifier
share one commitment implementation (no independent mutation oracle).

Not prevented: a fully coherent rewrite of the unsigned retained store (§4b's ceiling); any
attack on the platform's actual runtime, which never runs here.

## 9. What this study cannot show

No policy truth and no fact truth — binding and lineage, not truth; `evidenceBacking` digests
assert what was captured, never that it is authentic or sufficient, and nothing here inspects an
evidence artifact. No authorization from judgment: an `approve`-family outcome is not a
capability, a Gatekeeper grant, or a release of a staged effect, and the map's "authorizes" is
the adapter's own contract, not the platform's. No claim about Cloudflare OS runtime behavior —
the Durable Object, the submit gate, the apply chokepoint, sharing, observers, and the agent
loop never execute; findings about them are findings about the pinned *contract and source*,
exercised where it is executable and typechecked where it is not. No security audit of
Cloudflare OS and no endorsement; the platform's own TODOs (richer action descriptions, a
policy engine, policy hints) are load-bearing context, not findings. No claim that the platform
*should* adopt this binding profile, and no claim about Cloudflare's managed products, which are
outside the pinned open-source baseline. No JPS conformance claim (§3.4 machinery not engaged).
No prospective-prediction claim for the locked stratum (§1a). No coverage claim beyond the 24
registered cells; no general interoperability claim beyond: this platform contract at this
commit, this pack, this action encoding, this machine, one adapter written by the JPS side. No
"zero trust": the verifier trusts the pinned clone, the pinned jpack binary, the adapter code,
and the retained store as-retained — enumerated, finite, and honest. And no claim that a
detection here would have *prevented* anything at runtime: detection is post-hoc provability,
the platform applies effects on its own authority, and nothing in this study sits on that path.

## 10. Publication commitment

The detection matrix is published in full whichever way it lands: every divergence, every
registered-boundary confirmation, and any cell caught by neither system — the last with the
same prominence as a pass, because a precise map of what the composition cannot bind is the
study's most useful possible output.

## Decision register (for the pre-freeze reviewer)

- [D-1] The cf layer runs exactly two upstream checks and registers every other cf outcome as a
  vacuous pass made visible by `platformChecksEngaged`. Alternative rejected: reimplementing the
  platform's prose contract as study-written validation and calling it the platform — that would
  manufacture a cf layer the pinned source does not contain. Is the two-check surface honest and
  sufficient for the R2 claim as worded?
- [D-2] The map executes only `proceed`; `clarify-return` and `decline-redirect` are registered
  non-executable communications. Is any S/B attribution sensitive to that choice, and should a
  clarify-with-unbound-execution cell exist in the holdout?
- [D-3] `evidenceBacking` lives inside the commitment's `judgment` member and is adapter-carried
  lineage. Alternative rejected: a separate evidence-manifest artifact — more fields to bind,
  same trust root, no additional oracle. Does the placement weaken the s04/o01 attribution?
- [D-4] The negative controls prove classifier and drainer aliveness but no negative control
  proves the *binding* layer alive; binding aliveness rests on the per-code reachability tests.
  Is that sufficient, or should a binding-layer control-gate row exist?
- [D-5] `m02`'s honest bridge registers all-pass as a descriptive boundary. Should an
  `applied-unproven`-reported-as-`applied` variant exist as an endpoint (a milder overclaim than
  `d02`), or does `d02` own the family adequately?
