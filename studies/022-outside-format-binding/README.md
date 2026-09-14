# Study 022 — a gateway receipt bound into an in-toto attestation: what each verifier sees, and what neither does

**Status: preregistration DRAFT — in pre-freeze cross-vendor review (`PREREG-REVIEW.md`).
Nothing has run under a freeze; `results/` is absent until the registered primary attempt, and
everything under `pilots/` is harness validation that supports no claim.**

Every receipt of a gateway store is bound into one in-toto Statement in a DSSE envelope: the
subjects are what the receipt's own verifier resolves by digest (the retained artifact, and for
an action the decision record it claims and each receipt it cites), the predicate is the
receipt verbatim, the envelope is signed with a study-minted key that is not the gateway's.
Nineteen constructions tamper with the store or with the attestations, and three verifiers look
— the gateway's own; a study-written consumer ceremony using the unmodified in-toto reference
implementation for its signature verification (`securesystemslib`) and its Statement validation
(`in-toto-attestation`); and the binding's rules. The registered result is the
ownership map: what an in-toto consumer sees of a receipt by re-digest, what only the gateway's
key covers (the seal, the chain, the count, the gateway's identity — a store re-minted under
another key attests just as well), and what only the binding's own rules see (an attestation
that verifies while vouching for the wrong artifact).

The harness tests run from the study root, in the virtual environment holding the pinned
packages, with the study's bytecode policy in force from the interpreter's start:

    PYTHONPYCACHEPREFIX=$(mktemp -d) PYTHONDONTWRITEBYTECODE=1 GATEWAY_BIN=<the pinned binary> python -m unittest discover -s harness/tests

Interoperability, in the sense of Studies 013–016, with one precision: the signature
verification and the Statement validation are an independently developed implementation,
consumed at a pinned version and never modified; the ceremony around them — which receipts to
expect attestations for, which types to pin, how to resolve a subject — is this study's own
consumer policy, and the specification marks which step is whose. Not a study of any deployment.
