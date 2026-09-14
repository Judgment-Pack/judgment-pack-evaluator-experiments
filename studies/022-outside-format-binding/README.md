# Study 022 — a gateway receipt bound into an in-toto attestation: what each verifier sees, and what neither does

**Status: preregistration DRAFT — in pre-freeze cross-vendor review (`PREREG-REVIEW.md`).
Nothing has run under a freeze; `results/` is absent until the registered primary attempt, and
everything under `pilots/` is harness validation that supports no claim.**

Every receipt of a gateway store is bound into one in-toto Statement in a DSSE envelope: the
subjects are what the receipt's own verifier resolves by digest (the retained artifact, and for
an action the decision record it claims and each receipt it cites), the predicate is the
receipt verbatim, the envelope is signed with a study-minted key that is not the gateway's.
Nineteen constructions tamper with the store or with the attestations, and three verifiers look
— the gateway's own, the in-toto reference implementation (`securesystemslib`,
`in-toto-attestation`, unmodified), and the binding's rules. The registered result is the
ownership map: what an in-toto consumer sees of a receipt by re-digest, what only the gateway's
key covers (the seal, the chain, the count, the gateway's identity — a store re-minted under
another key attests just as well), and what only the binding's own rules see (an attestation
that verifies while vouching for the wrong artifact).

Interoperability, in the sense of Studies 013–016: an independently developed verifier,
consumed at a pinned version, never modified. Not a study of any deployment.
