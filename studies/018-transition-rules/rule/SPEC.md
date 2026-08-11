# The transition rule — citation schema, rule vocabulary, and the Layer TRANSITION contract

Status: REGISTERED with the Study 018 preregistration (the digest in `harness/PINS.json`
governs after the freeze). It is a **study registration, not a format proposal**: nothing
here lands in JPS, the runtime, or the gateway, and no producer or consumer outside this
study is bound by it.

## 1. What this layer is for, and what it must never become

[RFC 0011 §2a](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0011-judgment-currency-anchor.md)
states that membership at a snapshot does not determine continued reliance: that second
question is a **transition rule** and belongs to the relying party. This layer is a
prototype of such a rule evaluator, deliberately separate from Study 016's frozen currency
verifier — which is consumed unmodified and whose output stays exactly *membership at
snapshot*. The transition layer consumes that verdict **as a fact**; it never recomputes
membership, and the study fails if the two ever merge.

## 2. The citation and the rule configuration

A **citation** records the registry head an artifact validated against — the construction
raised publicly on the Study 016 announcement thread (RFC 0011 Unresolved #11):

```json
{"citationVersion": "1", "seriesId": "…", "citedHead": "sha256:<64 hex>"}
```

It is **unsigned here on purpose**: signing changes nothing this study measures, because
the party that would sign is the party that chooses what to cite (see `bnd-backdated-citation`).

A **rule configuration** states one relying party's rule for one series:

```json
{"ruleConfigVersion": "1", "seriesId": "…",
 "rule": "stop-at-retirement" | "position-window" | "grandfather-on-cited-support",
 "windowPositions": <non-negative integer> | null,
 "windowDuration": <string> | null}
```

Rules are **configuration, not code paths**, so that no rule is privileged by construction
and a fourth rule would be a configuration rather than a patch. The vocabulary is closed;
an unregistered rule is fail-closed.

## 3. The evaluation ceremony

Ordered, fail-closed, offline. Inputs: the commitment tuple, the auditor's snapshot (its
checkpoint digests and payloads, recomputed from its own bytes), the retained citation, the
rule configuration, and Layer CURRENCY's verdict.

1. **Configuration.** Well-formed version-1 rule configuration whose `seriesId` equals the
   commitment's `packId`, else `transition-unavailable`. A rule is stated per series and
   confers nothing outside it.
2. **Ordering.** A `position-window` naming a **duration** rather than a position count is
   `transition-unavailable`: the only ordering available offline is positional,
   `effectiveFrom` is carried and never compared in the pinned upstream, and nothing here
   holds a clock (RFC 0011 Unresolved #3).
3. **`stop-at-retirement`** consumes Layer CURRENCY's verdict alone — `usable` if the
   version is in the supported set at the auditor's snapshot, else
   `not-usable-version-retired`. **It needs no citation**, and is therefore unaffected by
   every citation finding in the matrix.
4. **The citation**, for the remaining rules: present, well-formed, naming this series, and
   locating a head that is a position of the auditor's snapshot — else
   `transition-unavailable`. A head the auditor cannot locate is not evidence about the
   history it holds, and the layer says it cannot place the artifact rather than treating
   the citation as absent.
5. **The fold.** The positions at which the committed `(version, digest)` entered and left
   the supported set, computed with the pinned upstream's own add/retire/reinstate
   semantics over the same payload shape — positions, where the upstream computes a set.
6. **The rule.** `grandfather-on-cited-support`: `usable` if the cited position is one at which the version
   was in the supported set, else `not-usable-cited-state-not-supported`. `position-window`:
   `usable` if the version has not left the set; `not-usable-cited-state-not-supported` if
   the cited position is at or after the leaving position; otherwise `usable` or
   `not-usable-window-elapsed` according to how many positions have elapsed since.

## 4. Vocabulary (exhaustive)

Outcome strings are `usable`, `unavailable`, or `not-usable:<code>`.

| Code | Meaning |
|---|---|
| `transition-unavailable` | a required input or configuration is absent or malformed, the rule is stated for another series, the rule needs a citation and none is retained or it cannot be located in this history, or the rule names an ordering this apparatus does not have — fail-closed, never a permission |
| `not-usable-version-retired` | the version is not in the supported set at the auditor's snapshot and the stated rule permits no reliance beyond that point |
| `not-usable-window-elapsed` | more registry positions have elapsed since the version left the set than the stated window permits |
| `not-usable-cited-state-not-supported` | the cited head is at or after the position at which the version left the supported set |

## 5. What a verdict means, exactly

`usable` means **usable under the stated rule, on the evidence retained** — not that the
decision is correct, that the version is current, or that the artifact was created when it
claims. The citation attests the state an artifact's author *claims* to have relied on: an
author who chooses what to cite can cite an early head, and `bnd-backdated-citation` is
byte-identical to `div-grandfather-on-cited-support` for exactly that reason — honest reliance and
backdated reliance are the same evidence, so no rule over this evidence separates them.
Closing that gap needs a trusted ordering between the artifact and the registry, which
RFC 0011 Unresolved #3 leaves open and this study does not supply.

Ceiling, both layers, stated once and meant: binding/lineage, not truth. The registry says
which versions an authority asserted in force; a transition rule says what one relying
party does with that; neither says that anything is right.
