# The transition rule — citation schema, rule vocabulary, and the Layer TRANSITION contract

Status: REGISTERED with the Study 018 preregistration (the digest in `harness/PINS.json`
governs after the freeze). It is a **study registration, not a format proposal**: nothing
here lands in JPS, the runtime, or the gateway, and no producer or consumer outside this
study is bound by it.

## 1. What this layer is for, and what it must never become

[RFC 0011 §2a](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0011-judgment-currency-anchor.md)
states that membership at a snapshot does not determine continued reliance: that second
question is a **transition rule**. This study takes no position on who owns that question
or where such a rule belongs — RFC 0011 Unresolved #10 is open, and nothing measured here
closes it. This layer is a
prototype of such a rule evaluator, deliberately separate from Study 016's frozen currency
verifier — which is consumed unmodified and whose output stays exactly *membership at
snapshot*. The transition layer consumes that verdict **as a fact** — it never recomputes
*the verdict*, and never second-guesses membership at the auditor's snapshot. It does compute
membership at **earlier prefixes**, through the upstream's own `fold_supported`, because a
rule about a cited position needs the state at that position and the verdict does not carry
it. What must never merge is the *answer*: the registry says membership, this layer says
usability, and the study fails if either starts giving the other's.

## 2. The citation and the rule configuration

A **citation** records the registry head an artifact validated against — the construction
raised publicly on the Study 016 announcement thread (RFC 0011 Unresolved #11):

```json
{"citationVersion": "1", "seriesId": "…", "citedHead": "sha256:<64 hex>"}
```

It is **unsigned here on purpose**: signing changes nothing this study measures, because
the party that would sign is the party that chooses what to cite (see `bnd-backdated-citation`).

A **rule configuration** states one configured rule for one series:

```json
{"ruleConfigVersion": "1", "seriesId": "…",
 "rule": "stop-at-retirement" | "position-window" | "grandfather-on-cited-support",
 "windowPositions": <non-negative integer> | null,
 "windowDuration": <string> | null}
```

Rule **selection** is configuration; the vocabulary and each rule's semantics are code, so a
fourth rule would be a registered patch and not merely a configuration (round-1 R1-7 — the
earlier claim to the contrary is withdrawn). The vocabulary is closed; an unregistered rule is fail-closed, `position-window` must name
exactly one window form, and the other rules must name none.

## 3. The evaluation ceremony

Ordered, fail-closed, offline. Inputs: the commitment tuple, the auditor's snapshot (its
checkpoint digests and payloads, recomputed from its own bytes), the retained citation, the
rule configuration, and Layer CURRENCY's verdict. The steps below are the order **this layer**
takes, and each gate refuses before this layer reads the next input. It is not a claim about
the composed harness: `harness/run_verify.py` parses the snapshot and reads the citation and
rule configuration from disk before calling this layer at all, so a cell whose currency
verdict is non-adjudicable has still had its bytes parsed — outside Layer CURRENCY's own
resource limits — by the time the refusal below is returned:

0. **The currency verdict, first.** Only `pass` and `fail:not-current-at-snapshot` are
   adjudicable. Any other outcome — unreadable or unauthenticated snapshot, broken chain,
   rebound binding, absent pin — is an integrity or availability failure, and this layer
   returns `transition-unavailable` **before parsing any configuration**, rather than
   reinterpreting it as a retirement (round-1 R1-1). The membership fold must also be
   supplied; without it the layer refuses here.
1. **Configuration.** Well-formed version-1 rule configuration whose `seriesId` equals the
   commitment's `packId`, else `transition-unavailable`. A rule is stated per series and
   confers nothing outside it.
2. **Ordering.** A `position-window` naming a **duration** rather than a position count is
   `transition-unavailable`: the only ordering available offline is positional,
   `effectiveFrom` is carried and never compared in the pinned upstream, and nothing here
   holds a clock (RFC 0011 Unresolved #3). This refusal precedes the citation step, so a
   duration-window cell publishes **no** structured evidence even when it retains a
   perfectly good citation.
3. **`stop-at-retirement`** needs **no citation**, and is therefore unaffected by every
   citation finding in the matrix. It is *not*, however, decided by the currency verdict
   alone: `usable` if this exact `(version, digest)` binding is in the supported set at the
   auditor's snapshot — a known version at the wrong digest is not — and
   otherwise the retained history is folded to choose *which* refusal, because non-membership
   alone does not establish a departure — `not-usable-never-supported` when this exact
   `(version, digest)` is in the supported set at no position of the history, and
   `not-usable-not-in-supported-set` when it was there and is not now. Without a foldable
   history the layer is `transition-unavailable` rather than guessing between the two.
4. **The citation**, for the remaining rules: present, well-formed, naming this series, and
   locating a head that is a position of the auditor's snapshot — else
   `transition-unavailable`. A head the auditor cannot locate is not evidence about the
   history it holds, and the layer says it cannot place the artifact rather than treating
   the citation as absent.
5. **The fold.** Membership of the committed `(version, digest)` is read from the pinned
   upstream's own `fold_supported` over each **prefix** of the retained payloads, so the
   add/retire/reinstate semantics are the upstream's by construction rather than by a
   re-implementation that could drift (round-1 R1-2). Three questions are asked of it: is the
   member supported at the **cited** prefix; is it supported after **any** prefix; and at which
   position does it first leave the set **after** the cited one. The third is asked whenever
   the member is supported at the cited position, so `grandfather-on-cited-support` computes
   and publishes `retiredAtPosition` too even though its verdict does not depend on it.
   No single "interval" is computed; a history may enter and leave repeatedly.
6. **The rule.** If the member is not supported at the cited position, the refusal is
   `not-usable-never-supported` when it is supported at no prefix at all, and otherwise
   `not-usable-cited-state-not-supported` — this branch is taken *before* either remaining
   rule is consulted, so both rules share it. If it **is** supported at the cited position,
   `grandfather-on-cited-support` is `usable`. `position-window` then looks for the first
   departure **strictly after** the cited position: if there is none the verdict is
   `usable`; otherwise `elapsed = (number of retained positions) − (departure position)`,
   and the verdict is `usable` when `elapsed ≤ windowPositions` — inclusive at the bound —
   and `not-usable-window-elapsed` above it.

### 3a. The structured evidence, defined exactly

Both fields are published only on the branches that reach them, and are `null` everywhere
else — including whenever Layer CURRENCY has already withheld an adjudicable verdict:

- **`citedPosition`** — the 1-based index of the cited head within the auditor's retained
  checkpoint digests. Non-null only when the layer **reaches** the citation step and the
  citation was retained, well-formed, named this series and was located in this history.
  It is `null` for `stop-at-retirement`, which reads no citation at all, and also `null`
  whenever an earlier gate refuses first — a non-adjudicable currency verdict, a missing
  fold, a malformed or foreign-series configuration, or a duration window — however good
  the retained citation may be. It is `null` in one **later** case too: if the citation is
  located but the history then fails to fold cleanly, the layer returns
  `transition-unavailable` without attaching either field. So a located citation is
  necessary for a non-null `citedPosition` and not sufficient, and no cell may be read as
  "the citation was absent" merely because the field is null.
- **`retiredAtPosition`** — the **first departure strictly after `citedPosition`**: the
  lowest `p > citedPosition` at which the member is supported after `p−1` events and not
  after `p`. It is **relative to the citation, not to the history as a whole**, and it is
  `null` whenever the member is not supported at the cited position — including cases where
  the member plainly departs elsewhere in the history. This is a deliberate choice and a
  contestable one: `rule/transition.py` also carries `_left_position`, which computes the
  *most recent* departure over the whole history, and the round-2 reviewer's holdout
  registers that reading for `h05` and `h08`. The decide path does **not** use it. Which
  reading a rule evaluator should publish is not settled by this study; see PREREG-REVIEW.md
  §R2-H, which registers the resulting divergence in advance rather than resolving it by
  editing either side.

## 4. Vocabulary (exhaustive)

Outcome strings are `usable`, `unavailable`, or `not-usable:<code>`.

| Code | Meaning |
|---|---|
| `transition-unavailable` | a required input or configuration is absent or malformed, the rule is stated for another series, the rule needs a citation and none is retained or it cannot be located in this history, or the rule names an ordering this apparatus does not have — fail-closed, never a permission |
| `not-usable-not-in-supported-set` | this exact `(version, digest)` is not in the supported set at the auditor's snapshot, and the stated rule permits no reliance beyond that point. It says non-membership, never "retired": Study 016 establishes only the former |
| `not-usable-never-supported` | this exact `(version, digest)` is in the supported set at **no** position of the history — it did not depart, it was never there |
| `not-usable-window-elapsed` | more registry positions have elapsed than the stated window permits, counted from the position at which this exact `(version, digest)` **first leaves the supported set after the cited position** — not from the most recent departure in the history, and not from any departure of the version at another digest. §3a states why that distinction is contestable and where it is registered |
| `not-usable-cited-state-not-supported` | this exact `(version, digest)` is not in the supported set **at the cited position**, whatever it may be elsewhere in the history |

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
which versions an authority asserted in force; a transition rule says what one stated rule
makes of that; neither says that anything is right.
