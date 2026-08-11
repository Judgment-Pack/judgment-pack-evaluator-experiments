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

- **The payoff**: a fork of the same threat class 016 proved silent becomes observable
  from **one attributed record of a sibling head** (`wit-split-view-caught`) — the fork is
  built so both branches keep the committed version current, isolating the attribution to
  the witness layer. This is not a replay of 016's cells, and the study says so.
- **Collusion** (`wit-collusion-a/b`, registered expected-undetected): the same pinned key
  records contradictory heads at the same position across the pair, each run internally
  valid and satisfying every *implemented* clause. The scorer recomputes the contradiction
  from retained bytes, and a pair that fails to validate makes the attempt
  pipeline-invalid. The cells illustrate why a non-collusion clause may be required; they
  measure no organisational property.
- **Delivery control, the round-1 lesson** (`wit-suppression-omitted` / `-corrupted`,
  registered expected-undetected): the reviewer falsified the draft's routing by giving an
  honest conflicting record an unpinned key-id label — the label alone turned a detection
  into a pass. Routing is now by signature verification (`neg-relabel-attack` keeps that
  construction as a standing control), but whoever controls delivery can still omit or
  corrupt the record. Those two cells register the residue rather than hiding it, and
  `wit-required-witness-absent` is the arm that bounds them.
- **Zero-sighting enforcement** (`wit-zero-sightings-vacuous` vs `-enforced`): an empty
  comparison is vacuously consistent at `minimumSightings: 0` and a fail-closed refusal at
  `1`. No cause is attributed to the emptiness — partition, outage, withholding and a
  witness that never spoke are one condition here.
- **Positional prefix coverage** (`wit-prefix-coverage`) and **the recency policy's cost**
  (`wit-recency-refused` vs `wit-historical-audit`, the same bytes under both policies: a
  deliberate audit of an older snapshot and a stale presentation are indistinguishable, so
  only the configured policy decides).

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
- [`fixtures/`](fixtures/) — the 18 frozen cells (fully synthetic; no evaluator binary,
  no clone — the suite runs offline on stdlib + `cryptography` + `rfc8785`).
- `pilots/` — pre-freeze execution, labeled harness validation, non-citable.
- `results/` — absent until a registered post-freeze attempt.

Nothing in this repository claims any JPS conformance.
