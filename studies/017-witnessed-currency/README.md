# Study 017 — witnessed currency: what a witness contract buys, and which clause each remaining silence isolates

**Status: DRAFT. Nothing is frozen and nothing has run under a freeze.**

Study 016 measured that a single-operator signed currency registry is silent to a fresh,
stateless verifier shown one view of a split history — and that the silence is exactly
statelessness. This study measures the next mechanism up: a **sighting** — one witness
key's signature over a history head it has observed — compared against the presented
view. The question is not whether witnessing "works"; it is **which clause of the witness
contract** named by
[RFC 0011 Unresolved #9](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0011-judgment-currency-anchor.md#unresolved-questions)
— retention, cross-view comparison, verifier enforcement, witness independence and
non-collusion — **each remaining silence isolates**.

Registered in advance, silence and payoff alike:

- **The payoff**: the exact split view 016 proved silent becomes observable with **one
  honest sighting crossing views** (`wit-split-view-caught`) — and the fork pair is built
  so both branches keep the committed version current, isolating the attribution to the
  witness layer alone.
- **Collusion, the load-bearing exhibit** (`wit-collusion-a/b`, registered
  expected-undetected): the same pinned witness key attests contradictory heads at the
  same position across the pair, each run internally valid and satisfying its
  enforcement clause. The scorer validates the equivocation structurally from retained
  bytes. This is the empirical case for witness **independence** — the clause nothing in
  the mechanism enforces. Its sibling `wit-one-honest` shows one honest, comparing
  witness converting the silence into a refusal: independence measured as a diff.
- **Partition and enforcement** (`wit-partition-vacuous` vs `-enforced`): an empty
  comparison is vacuously consistent at `minimumSightings: 0` and a fail-closed refusal
  at `1` — the enforcement clause, measured as an arm pair.
- **The retention horizon** (`wit-retention-horizon`): a sighting anchors only the
  prefix it names; a fork above the sighted position is invisible — the
  fork-after-anchor limit recurring one level up.

**This is not an interoperability study.** No external component exists anywhere in the
apparatus: Layer CURRENCY is Study 016's frozen verifier consumed as a digest-pinned
unmodified upstream (`harness/upstream016.py` — the 016→014 posture applied to 016
itself), and everything else is study-internal. It measures a governance mechanism's
floor; witnessing here is **observability, not prevention**, and no witness-independence
claim exists — all keys are study-minted, and the collusion pair is the argument for
independence, not a simulation of it.

## Layout

- [`PREREGISTRATION.md`](PREREGISTRATION.md) — governing document (DRAFT until frozen).
- [`witness/`](witness/) — the registered sighting schema/ceremony (`SPEC.md`), the
  writer, and Layer WITNESS.
- [`harness/`](harness/) — pins (incl. the frozen-016 upstream digests), matrices,
  builder, two-layer runner, scorer, deterministic tests.
- [`fixtures/`](fixtures/) — the 14 frozen cells (fully synthetic; no evaluator binary,
  no clone — the suite runs offline on stdlib + `cryptography` + `rfc8785`).
- `pilots/` — pre-freeze execution, labeled harness validation, non-citable.
- `results/` — absent until a registered post-freeze attempt.

Nothing in this repository claims any JPS conformance.
