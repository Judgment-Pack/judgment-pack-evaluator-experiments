# Round 12 — commissioning brief (verbatim; absolute paths normalized)

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra,
workspace-write sandbox in a scratch directory, worktree read at commit 19a5bb8
(the freeze 968a9f8, the registered attempt, and the results package). Run: 2026-08-14.
Scope: only what is new since the round-11 read.

---

# Round 12 — results-package confirmation (pre-merge review of PR #68)

You have reviewed this study through eleven rounds; round 11 said freezable after listed
fixes. Since then: the listed fix landed (06e85f6), the round-11 record was filed (72346f9),
the study froze (968a9f8 — four protocol digests pinned by the registered tooling), the
registered attempt ran with --include-holdout, and the results package landed (19a5bb8).
This round reviews ONLY what is new since your round-11 read: the freeze commit, the
attempt artifacts, and the results package. The frozen preregistration is no longer
editable; corrections land in DEVIATIONS.

Worktree: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7d92f5c5-d830-493a-b7d9-768fa12d62df/scratchpad/exp-015 (HEAD = 19a5bb8).
Study dir: studies/015-cloudflare-os-boundary
New since round 11: git log 72346f9..HEAD --oneline; diffs via git show 968a9f8 / git show 19a5bb8.
The attempt: results/primary-attempt-001/{RESULTS.json, DETECTION-MATRIX.md, ATTEMPT.json, ANALYSIS.md}.

Environment if you wish to re-execute (the attempt is deterministic; a re-run must
reproduce it byte-for-byte except any timestamp field):
export CFOS_SOURCE=<CFOS_SOURCE>
export JPACK_BIN=<JPACK_BIN>
export PATH=/home/onword/.nvm/versions/node/v22.23.1/bin:$PATH
venv: <venv>

Audit:
1. The freeze: digests in PINS.json match the frozen files byte-for-byte; the manifest is
   exact; the suite passes on the frozen tree; the scorer's holdout requirement flipped
   from refuse-without to require.
2. The attempt's integrity: RESULTS.json provenance against the pins; R1's statement at
   its registered width (locked-replication standing, §1a); the holdout scored separately
   with the "nothing here can change R1" boundary intact.
3. ANALYSIS.md against RESULTS.json and the registries, row by row: every classification
   claim (which round/mechanism closed which cell) checked against the cited dispositions
   and code; h04's "the derivation oracle never ran" checked against verify.py's gate
   order; h06's registered-acceptance tracing checked against SPEC §5 upstream step 2, the
   fixture bytes, ceremony.ts's witness seeding, and the C1/C4 records — the load-bearing
   question is whether the acceptance is genuinely registered for this history or
   stretched over it. The agent's own corrections (h05 to round-1 finding 11, not the
   rounds-6/7 matrix) — verify.
4. The qualifications: the "prospective" limitation (holdout outcomes computable pre-freeze
   via the snapshot method — stated in ANALYSIS limitations); results/ outside both
   mechanical guards (stated); the stale frozen banner (recorded in DEVIATIONS). Judge
   whether each is stated at its true width.
5. README's Results section and banner: no claim exceeding ANALYSIS; the phrase-guard
   fingerprint discipline held (locator 92 byte-identical passage).

Output: numbered findings R12-<n> (severity, offending, contradiction, proposed fix) —
empty if none survive verification; then exactly one verdict line:
`do not merge` / `mergeable after listed fixes` / `mergeable as written`,
one justification paragraph, and CODEX-015-R12-DONE on its own line.
