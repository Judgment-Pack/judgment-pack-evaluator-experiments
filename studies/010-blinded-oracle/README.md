# Study 010 — the blinded oracle

Study 009's registered next question: does a record set authored
independently of the packs surface an encoding defect neither author chose
knowing the other's work? Five preregistration revisions and four
adversarial pre-freeze reviews stand behind the current design — the
reviews rejected an operator-controlled coin, a steerable publication
clock, an unauthenticated one, and a transcript gate that would have
rejected the very session it was meant to admit. Every review and its
per-finding disposition is in [`PREREG-REVIEW.md`](PREREG-REVIEW.md);
[`PREREGISTRATION.md`](PREREGISTRATION.md) governs, and its §9 states
plainly what the protocol enforces, what it merely records, and what it
cannot prevent.

The ordering the commit graph must show (PREREGISTRATION.md §8): protocol
lock → lock Rekor timestamp → authoring call (immutable
`transcription/authoring/call-N` slots) → records commit → records Rekor
inclusion (the publication) → push → beacon round → `DRAW.json` + pack D +
`DEFECT.json` (derived from the published tree) → artifact freeze → sealed
attempts under `trials/` → `RESULTS.json` → `ANALYSIS.md` → post-run
adversarial review.

Driver: `harness/study.py
lock|timestamp-lock|publish|witness|draw|validate|freeze|run|score` with
`JPACK_BIN` naming the pinned v0.15.0 binary. The study stays out of CI by
repo rule; every command refuses drifted, uncommitted, or unlocked state,
and the first attempt started under the freeze is primary even if it
crashed.
