# Clean-room protocol

An implementation in this repository counts as RFC 0006 evidence only if it was derived from the
specification text — never from another implementation. A port inherits the first implementer's
silent resolutions and proves nothing about the prose. This protocol is how that independence is
established and audited. It is process, not repo layout: the barrier must hold while the code is
being written, wherever it is written.

## 1. Build the room — outside this repository

Create a fresh directory containing **only**:

- `reference/` — the RFC and Core specification snapshots (copy them from this repository's
  `reference/`, or re-snapshot from the spec repository at a recorded commit);
- a brief (adapt [`python/CLEAN-ROOM-BRIEF.md`](python/CLEAN-ROOM-BRIEF.md)) naming the target
  language, the deliverables, and the rules below.

The room must not contain, and the implementer must not be able to reach, any existing
implementation: not this repository (its `python/`, `harness/` — the harness encodes output
shapes), not `judgment-pack-runtime`, not any prior room.

## 2. Run the implementer under the barrier

- Use a coding agent or developer with **no prior exposure** to any existing implementation.
  Model-family diversity from previous implementers strengthens the evidence; document who/what
  implemented it and under which configuration.
- Disable anything that could tunnel information in: MCP servers, network access, tools that
  search other repositories. Sandbox writes to the room.
- The brief's standing rules: read only `reference/`; where the text underdetermines a choice,
  choose the most defensible reading and **record it as a numbered entry in `DECISIONS.md`**
  (text relied on, alternatives seen, reading chosen, why); if a reading disagrees with the RFC's
  appendix table, record the disagreement rather than bending to match; claim no conformance
  anywhere; derive the appendix instances into tests.

## 3. Audit before accepting

Review the full session transcript/log for any read outside the room and any reference to an
existing implementation. A violated barrier voids the exercise — start over; do not "fix" it.
Record the audit result in the import commit message.

## 4. Import and referee — only after the room is closed

- Import the room's output as `<language>/` in one commit that documents: who implemented it,
  under what barrier, and the audit result.
- Run `harness/` against the existing implementations on the appendix instances and probes.
  **Agreement** is portability evidence. **Divergence** is adjudicated against the specification
  text only — never by making one implementation copy another — and then recorded in RFC 0006 as
  a found ambiguity. Both outcomes are the product.

## Known limits of this evidence

Implementations gathered under this protocol on one maintainer's machines share that maintainer's
direction, and the RFC's own recorded implementation experience is part of the reference text —
later rooms are corroborated by it, not blind to it. Third-party implementations in independently
governed repositories remain the strongest evidence; this protocol is the honest maximum available
before that exists.
