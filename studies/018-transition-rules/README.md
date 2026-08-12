# Study 018 — transition rules over cited registry state: what a citation buys a stated rule, and where the evidence stops

**Status: DRAFT. Nothing is frozen and nothing has run under a freeze.**

This study does not come from an internal roadmap. A reader (`@circuit`) proposed, on the
[Study 016 announcement thread](https://dev.to/kikashy/the-receipt-was-valid-the-policy-was-retired-164a),
that a decision record the registry **head** it validated against. The reply drew the
distinction that makes it a study: there are two separate questions after that, and
conflating them is the error.

1. **Evidence** — what registry state did this artifact claim to rely on?
2. **Organisational policy** — given that history, may this decision still be relied upon?

The second is a **transition rule**, and it is not answered by membership alone. That became
[RFC 0011 §2a](https://github.com/Judgment-Pack/judgment-pack-spec/blob/main/rfcs/0011-judgment-currency-anchor.md)
(merged); its Unresolved #10 asks where such a rule is sourced and audited, and #11 asks what
a cited head is worth. This study measures **#11 only**: what a cited head lets a stated rule
compute, and where that evidence stops. It takes no position on where a transition rule
should be sourced or audited, and #10 stays open.

## The result the matrix is built around

One registry verdict — `not current at snapshot` — supports **four configured evaluations yielding three exact outcomes** over identical evidence, according to which rule is configured:
`stop-at-retirement` refuses; `position-window` permits or refuses depending on its parameter;
`grandfather-on-cited-support` permits. The same evidence therefore does not determine a
usability answer on its own — which is §2a's separation, measured rather than argued. What
follows for a registry's design is not measured here and is not claimed.

## The boundaries, registered in advance

- **The backdated citation** (`bnd-backdated-citation`, registered expected-undetected) is
  **byte-identical** to `div-grandfather-on-cited-support`. Honest reliance and backdated reliance are the
  same evidence, so no rule over this evidence separates them — the citation attests the
  state an author *claims*, never when the artifact was created. Signing it changes nothing:
  the party that would sign is the party that chooses what to cite.
- **Duration windows are not evaluable** (`bnd-duration-window`): the only ordering available
  offline is positional. A reader may reasonably object that a position window is not what an
  organisation means by "24 hours" — that objection *is* the cell.
- **The citation's value is rule-dependent**: `stop-at-retirement` needs none and is
  unaffected by every citation finding here; the other two are fail-closed without one.
- **Mint-time refusal is a counterfactual**, conditional on a policy this study does not
  supply: there is no producer stage and no accepted-head policy anywhere in the apparatus.
  Whatever it shows belongs to that hypothetical policy, never to the citation.

## Shape

Registry-and-rule only: no receipt protocol, no evaluator binary, no external clone — the
whole suite runs offline in about a second. Layer CURRENCY is Study 016's frozen verifier
consumed as a digest-pinned unmodified upstream (its output stays exactly membership); Layer
TRANSITION is the one added evaluator, and the study fails if they ever merge.

**This is not an interoperability study.** Nothing here is independently developed, and the
three rules are a construct — not a survey of what organisations actually hold.

Nothing in this repository claims any JPS conformance.
