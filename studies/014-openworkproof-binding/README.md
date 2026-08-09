# Study 014 — decision-to-execution binding under an external receipt protocol

**Status: DRAFT. Nothing is frozen and nothing has run under a freeze.** The
preregistration is a draft awaiting cross-vendor review; anything executed before the
freeze is harness validation under `pilots/`, labeled as such, and supports no claim
beyond "the machinery works".

## What it is

An interoperability falsification study between two independently designed layers:

- **JPS** owns the judgment: given this exact pack and these exact inputs, what
  disposition follows (deterministic, byte-portable under Core §8.3).
- **OpenWorkProof** (an independently developed execution-verification protocol —
  Ed25519-signed work orders, capability grants, action receipts, causal replay, an
  offline acceptance-bundle verifier) owns authorization, execution receipts, and chain
  verification.
- A **thin adapter** (`adapter/SPEC.md`) owns exactly one thing: a *judgment commitment* —
  the digest tuple `{pack bytes, input bytes, canonical disposition, replay tuple,
  authorized action}` — bound into the OWP chain at two signed points, and a verification
  ceremony that recomputes it from retained artifacts.

The study then tries to break the composition: 31 registered one-at-a-time mutations
(judgment-artifact, facts, disposition, action, replay/drift, causal-chain) plus controls,
each adjudicated per layer — did OWP's unchanged verifier catch it, did the adapter's
binding check catch it, did deterministic JPS replay catch it, or did nothing? An
undetected-by-all cell is a primary result, preserved, never patched
(`harness/MATRIX.json` registers two such cells up front: decision currency and policy
rollback, which no chain-internal evidence can see).

Neither protocol is modified. OWP is consumed as an installed package at a pinned commit;
jpack as a pinned release binary. The commitment rides in slots OWP signs but never
reads (`WorkOrder.objective`, `AgentRequest.context_source_digest`) — the study measures
precisely the difference between *carried under signature* and *semantically checked*.

## How it relates to what came before

- **Study 013** asked whether the surrounding application *behaves* consistently with the
  judgment, live, under an external regression harness. 014 asks whether a third party
  can later *prove*, offline, from retained artifacts and pinned keys alone, exactly which
  judgment authorized exactly which executed action. Same boundary, different question:
  behavior vs provenance. The disposition→action map here is study-defined, as 013's
  execution mapper was — JPS Core binds no caller.
- **The gateway** proves byte-lineage of *inputs* under its own signing identity and
  refuses, by policy, to let a receipt assert truth or authorization. Its mechanisms
  (record signing, chaining, the external-anchor lesson, the §5a consumer ceremony) are
  prior art here; its subject matter is disjoint. The registered-undetected cells are the
  gateway's registry lesson resurfacing one layer up.
- **ADR-0002's ceiling** governs both layers of this composition: binding/lineage, not
  truth.

## Reproduce (once frozen)

```
harness/build_fixtures.py   # one-time fixture construction (entropy pinned; output frozen by manifest)
harness/run_verify.py       # the composed ceremony over one cell
harness/score.py            # the full matrix -> detection table (the only thing that publishes)
python -m pytest harness/tests -q
```

Toolchain pins (OWP commit + venv, jpack release digests, interpreter) live in
`harness/PINS.json`; upstream identity in `upstream/`.

Nothing in this repository claims any JPS conformance.
