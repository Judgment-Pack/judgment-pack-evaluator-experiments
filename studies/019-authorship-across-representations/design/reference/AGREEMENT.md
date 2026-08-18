# Reference agreement report (design-time, 2026-08-15)

Two reference implementations of contest policy DRAFT v0.2, built independently by
separate agents from the prose (shared engine-fact context; implementation-level
independence only — the interpretation-independence instrument is the future
clean-room oracle):

- refA/pack.json — JPS pack, evaluated by the pinned jpack 0.17.0 (binary sha256 42f35f79…)
- refB/policy.rego — Rego v1, evaluated by the pinned OPA 1.19.0 static (sha256 1dd5c559…), capabilities-filtered, --strict clean

Grid: cells.json (2,540 cells; gen_grid.py) — full numeric cross with overrides quiet,
full tri-state cross at six representative bases, and targeted interaction cells.
Diff protocol: diff_refs.py compares (disposition, sorted reason set) per cell.

Result: after one adjudicated divergence (policy v0.2, adjudication A1 — U1 governs O2
under an indeterminate O3), both references agree 2,540/2,540 with zero engine errors.
V6 settled — see POLICY-DRAFT.md design notes and the two REPORT.md files. refB/inputs
(per-cell input documents, ~11MB) is regenerable from cells.json + run_grid.py and is
not committed.

**Superseded on 2026-08-18 (round-1 finding R1-2).** This report used to end "and
exclusion X1 registered". `refA/pack.json` was repaired (`refA/PACK-CHANGE-001.md`):
**X1 is retired, the registered exclusion set is empty, and the two references now agree
on all 236,196 cells of the derived space as well as all 2,540 grid cells**
(`OFFGOLD-CERT.md`, reissued the same day). The repair changes no grid cell —
`refA/results.jsonl` regenerates byte-identical on the pinned engine — so the 2,540/2,540
record above stands as written, under a new pack digest.

## Artifact digests (refA/pack.json updated 2026-08-18)
```
da4ee85c9d8b9f37ef523058144c163e80da50e485e2a148ea7d655253114618  cells.json
db9776070fbf5e193443ffb1f371b2524b4662f0877868306323b5c9e3701853  refA/pack.json
d2cbfed239f4151a767d22f09a01f1a1bd161e54ebbc99c546ebc33b9aee03e3  refA/results.jsonl
1f2e1ad1d423240dd262852f19057a8e906387d5a1b71db8b8a15bc010fc12e2  refB/policy.rego
d2cbfed239f4151a767d22f09a01f1a1bd161e54ebbc99c546ebc33b9aee03e3  refB/results.jsonl
```
Pre-repair `refA/pack.json`: `956ceebbc08886acdc3973b43112e9896f2853b3895243b3b97ff33a910453ee`.
