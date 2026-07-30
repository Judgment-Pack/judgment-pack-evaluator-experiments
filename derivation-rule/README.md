# Portable derivation rule

Layer 4 of the trustworthy-input-acquisition line ([ADR-0002](../docs/adr/0002-trustworthy-input-acquisition-research-line.md),
item 2): the **bytes → claim** step, made portable and independently implementable.

Studies 006 and 007 turned an acquired artifact into a claim (facts, evidence availability,
acquisition status) with one hand-written function, `derive_payload`, that was at once the
ground-truth oracle, the control builder, the grader, and the source of the stage labels — so the
derivation was only ever checked against itself. That circularity is the deepest methodological flaw
in those studies. The fix is to make the derivation **data**: a rule ([`rules/screening.rule.json`](rules/screening.rule.json))
that two independent implementations apply to the same artifact and must agree on, byte for byte.
Their agreement is the evidence that derivation fidelity is real and not a private convention of one
program — the agreement track's method (`python/` vs the reference runtime) applied to the derivation
step.

## What is here

- [`SPEC.md`](SPEC.md) — the external contract: the rule format, the condition ops, the canonical
  claim, the deterministic time and pointer model, and the agreement interface. A second
  implementation is built from this alone.
- [`derive.py`](derive.py) — the reference implementation (stdlib only).
- [`derive.go`](derive.go) — a **clean-room** second implementation, written in Go from `SPEC.md`
  alone by an author with no access to `derive.py`. Same contract, different language, so their
  agreement is genuine evidence rather than shared code.
- [`rules/screening.rule.json`](rules/screening.rule.json) — the OFAC screening derivation of studies
  006/007, expressed as a portable rule. Its 13-case corpus was cross-checked to reproduce the
  original `derive_payload`'s claim (facts, evidence, status, reason) on every case.
- [`corpus/`](corpus/) — frozen cases spanning every outcome (resolved, subject-mismatch,
  stale/future/malformed freshness, type failures, absent, unknown), plus `adv-*` adversarial cases
  that pinned every ambiguity the agreement test surfaced (float literal in a rule, an artifact
  `1.0` equal to an integer literal, an invalid calendar date, no-final-`always`, out-of-domain
  values reaching the claim). Each case is either an accept case (`expected` claim) or a reject case
  (`"reject": true`). The lone-surrogate rejection is covered by `test_derive.py` rather than the
  corpus, since a lone surrogate cannot round-trip a normally serialized JSON case file.
- [`agreement.py`](agreement.py) — drives two implementations over the corpus and diffs their
  canonical output. With no second command it checks the reference against the frozen corpus.

## Guarantee, and non-guarantee

A derivation rule says only how bytes become a claim, deterministically. It guarantees nothing about
whether the artifact is true, current, or complete — the claim is a function of the rule and the
bytes, and two conforming implementations produce the byte-identical canonical claim. What is
attested by [the acquisition proxy](../acquisition-proxy/) are the bytes; what is made portable and
checkable here is the step from those bytes to the claim a pack evaluates.

## A note on `basis`

The rule's derived claim carries a `basis`: the artifact pointers the derivation actually consulted
on the path it took, short-circuit-sensitive and sorted. This is a cleaner, fully-deterministic
definition than the studies' `derive_payload`, which hand-declared a `basis` set per branch (its
`unknown` branch, for instance, declared only `/status` though its failed `not_found` check had
already read `/checkedSuccessfully`). Portablizing the derivation surfaced and fixed that
inconsistency; the corpus records the principled `basis`, and both implementations reproduce it.

## Run

```bash
python3 -m unittest test_derive -v     # reference: corpus replay + op/error units
python3 agreement.py                   # reference vs the frozen corpus (no second impl needed)
go build -o /tmp/derive-go derive.go   # build the clean-room implementation
python3 agreement.py /tmp/derive-go    # cross-language agreement, byte for byte
```
