# Study 010 — the blinded oracle

Study 009's registered next question: does a record set authored
independently of the packs surface an encoding defect neither author chose
knowing the other's work? The first draft's blinding scheme (a commit-hash
coin, an in-repo authoring call) was rejected in pre-freeze review;
revision 2 rebuilt it on two locks, a drand-beacon draw over a
pre-committed six-mutation family, and a narrowed, transcript-evidenced
authoring claim. Both revisions' reviews and their dispositions are in
[`PREREG-REVIEW.md`](PREREG-REVIEW.md);
[`PREREGISTRATION.md`](PREREGISTRATION.md) governs.

The ordering the commit graph must show (PREREGISTRATION.md §8): protocol
lock → authoring call (`transcription/authoring/`) → records commit +
push → beacon round → `DRAW.json` + pack D + `DEFECT.json` → artifact
freeze → sealed attempts under `trials/` → `RESULTS.json` → `ANALYSIS.md`
→ post-run adversarial review.

Driver: `harness/study.py lock|draw|validate|freeze|run|score` with
`JPACK_BIN` naming the pinned v0.15.0 binary. The study stays out of CI by
repo rule; every command refuses drifted, uncommitted, or unlocked state.
