# Round 9 — commissioning brief (verbatim; absolute paths normalized)

Reviewer: codex-cli 0.145.0, model gpt-5.6-sol (OpenAI), reasoning effort ultra,
workspace-write sandbox in a scratch directory, worktree read at commit 6d0fdd5
(the round-8 fixes 99b5832 plus the filed round-8 record). Run: 2026-08-14.

---

# Round 9 — confirmation review of the round-8 fixes (freeze verdict)

You reviewed this study at commit e78ff3e (round 8): R7-3/4/5 RESOLVED, three items
functionally closed with named residue, new R8-1..R8-3 BLOCKER + R8-4 MINOR, and you ruled
the h08 holdout note stands with DEVIATIONS-only disposition. All were accepted; fixes
landed as commit 99b5832; the round-8 record and a ledger currency-line update landed as
6d0fdd5.

Worktree: /tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/7d92f5c5-d830-493a-b7d9-768fa12d62df/scratchpad/exp-015 (HEAD = 6d0fdd5).
Study dir: studies/015-cloudflare-os-boundary
Your round-8 findings, in-tree: reviews/round-8/REVIEW.md. Fix diff: git show 99b5832.
Cumulative since your round-5 tree: git diff dc4bc91..HEAD -- studies/015-cloudflare-os-boundary
Ledger: PREREG-REVIEW.md (rounds 6-8); DEVIATIONS.md ("Round-8 fixes", the h08 disposition).

Environment if you wish to execute:
export CFOS_SOURCE=<CFOS_SOURCE>
export JPACK_BIN=<JPACK_BIN>
venv: <venv>; pinned node v22.23.1.

Confirm or refute:
- R8-1: the three named sites, and the phrase-guard test itself
  (test_living_surfaces_carry_no_withdrawn_claims) — judge the machinery: scan surface
  derived by glob, comments+strings via tokenize on the Python side, whole-file on the TS
  side, seven phrase classes, per-passage licences with dead-entry failure, narrating
  ledgers and the holdout registry excluded with reasons. Its first run caught two live
  instances beyond your named list (SPEC.md:465, verify.py:1247) — check those fixes too.
  Try to construct a withdrawn-claim sentence that evades the guard; if you find one,
  report the evasion class rather than a single instance.
- R8-2: the store-before-outer comment; R8-4: the reference fix.
- R8-3: witnessIdentityProblem() on every identity a witness claims; your pass:1.0 and
  pass:1e0 constructions must now refuse on both sides. Note the two sides classify under
  different codes (node drain-order-violation vs python retained-store-unreadable) — judge
  whether that cross-layer code divergence is acceptable (each layer refusing under its own
  registered gate) or a finding.
- The h08 DEVIATIONS disposition as you ruled it.
Hold anything NEW in 99b5832/6d0fdd5 to the same standard. Zero-drift: both registries'
{id, expected} projections unchanged from dc4bc91; no fixture bytes changed since 3730d0b.

This is the ninth round. If blockers remain, say so plainly. If what remains is at the
severity of wording preferences, weigh whether another round buys the study anything —
the freeze exists so that the registered run, not the review loop, carries the evidence.

Output: one line per prior item (R8-1..R8-4, h08) — RESOLVED / NOT RESOLVED: <why>; any
new findings as R9-<n> (severity, offending, contradiction, proposed fix); then exactly
one verdict line:
`do not freeze` / `freezable after listed fixes` / `freezable as written`,
one justification paragraph, and CODEX-015-R9-DONE on its own line.
