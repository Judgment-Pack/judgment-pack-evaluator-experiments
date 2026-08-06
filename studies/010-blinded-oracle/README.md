# Study 010 — the blinded oracle

Study 009's registered next question: does a record set authored
independently of the packs surface an encoding defect neither author chose
knowing the other's work? Six preregistration revisions and five
adversarial pre-freeze reviews stand behind the design that ran — the
reviews rejected an operator-controlled coin, a steerable publication
clock, an unauthenticated one, and a transcript gate that would have
rejected the very session it was meant to admit. Every review and its
per-finding disposition is in [`PREREG-REVIEW.md`](PREREG-REVIEW.md);
[`PREREGISTRATION.md`](PREREGISTRATION.md) governs, and its §9 states
plainly what the protocol enforces, what it merely records, and what it
cannot prevent.

## Result

**E1 = caught**, and the headline the study was run for: sixteen records
authored independently of the pack covered **all six** pre-committed
boundary classes — including a mutation that introduces a
threshold the policy does not name. The beacon selected the
embargo-literal class, and a Syrian vendor record caught a pack whose
embargo list had silently lost SY. Because every class was already
covered, the beacon selected which defect demonstrated the catch rather
than caught versus miss — `ANALYSIS.md` says so.
[`ANALYSIS.md`](ANALYSIS.md) leads with the coverage profile and says what
the result does not establish; [`DEVIATIONS.md`](DEVIATIONS.md) §1 records
that two pilot runs preceded the registered one.

The ordering the commit graph must show (PREREGISTRATION.md §8): protocol
lock → lock Rekor timestamp → authoring call (immutable
`transcription/authoring/call-N` slots) → records commit → records Rekor
inclusion (the publication) → push → beacon round → `DRAW.json` + pack D +
`DEFECT.json` (derived from the published tree) → artifact freeze → sealed
attempts under `trials/` → `RESULTS.json` → post-run adversarial review.
`RESULTS.json` and `ANALYSIS.md` were committed together, so git does not
establish their internal write order; every reported value recomputes from
the retained artifacts.

Driver: `harness/study.py
lock|timestamp-lock|publish|witness|draw|validate|freeze|run|score` with
`JPACK_BIN` naming the pinned v0.15.0 binary. The study stays out of CI by
repo rule; every command refuses drifted, uncommitted, or unlocked state,
and the first attempt started under the freeze is primary even if it
crashed.
