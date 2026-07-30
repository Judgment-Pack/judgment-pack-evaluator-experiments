# Study 004 run log

Recorded before any encoding room opened, per PREREGISTRATION.md §3.

## Treatment

- Runtime source commit: `a3058cbadee993306d2f8bc9184cd6d9191a9143` (the preregistered commit,
  verified by `git rev-parse HEAD` in the build checkout).
- Binary: `CGO_ENABLED=0 go build -trimpath -buildvcs=false ./cmd/jpack` (Go toolchain of the
  operator's machine; `-buildvcs=false` because the build checkout is a git worktree whose
  gitfile defeats VCS stamping — version metadata is not consumed by any harness step).
- Binary SHA-256: `18d83cf48d5921daffae676ea3809ea12a59fd310fbb107e85348c1f3bb1048e`.
  One binary; byte-identical copies placed in each room's `bin/`.
- Policies: τ-bench pinned commit `1d244f5dca42944b67a379b44bfeb9f5748f189d`
  (`sierra-research/tau2-bench`), `data/tau2/domains/{airline,retail}/policy.md`, 166 and 136
  lines — matching Study 003's frozen frame.
- Pack re-declaration: all 11 pack copies re-declared `0.1.0-draft` → `0.2.0-draft` by the
  harness; every before/after digest in `redeclaration-log.json`; all validate at exit 0 under
  the pinned binary.

## Cluster derivation

The frame pass recorded each item's sentence and clause but not an explicit connected-decision
set; the harness derived the sets from the adjudicated clauses and reasons, recorded here
before any room opened:

| Room | Cluster | Frame item | Basis |
| --- | --- | --- | --- |
| room-a1-a7 | {A1, A7} | A1 3 | certificate remainder constrains the refunds decision |
| room-a1-a6 | {A1, A6} | A1 7 | insurance purchased at booking entitles the cancel decision's full refund (Study 003 recorded the entitlement as belonging to Cancel) |
| room-a3-a7 | {A3, A7} | A3 4 | cabin-downgrade difference entitles the refunds decision |
| room-a2-a6-a7 | {A2, A6, A7} | A7 2 | compensation coupled to the change/cancel act |
| room-r1-r3 | {R1, R3} | R3 1 | post-modification terminality of modify/cancel |

## Encoders

One encoder session per room, launched in parallel after this log was written; model and
configuration appended per room after the audit. Isolation is by strict instruction plus full
transcript audit (the operator tooling cannot mechanically disable an agent's read access
outside the room) — recorded as a deviation from CLEAN-ROOM-PROTOCOL §2's "disable" language
in the study's DEVIATIONS.md; §3's audit is the enforced control, and a breach voids the room.

## Encoders — recorded after the audit

All five rooms: one Claude agent session each (claude-opus-5 via the operator's Workflow
orchestration, one session, no reruns, no selection among outputs; 465s wall-clock for the
parallel batch). Transcript audit: all five transcripts inspected mechanically for
out-of-room file paths, network commands, and web tools — zero flags in every room
(19/23/26/33/26 tool calls respectively). All five rooms accepted.

## Harness — recorded after the rooms closed

All five graphs validate at exit 0; every `graph evaluate` ran at exit 0 on both constructed
input sets; every repeated run byte-identical. The construction log records every
unconstructed leaf (per the registered table's `any`/`not`/`not-equals` skips); several nodes
therefore evaluate unresolved on the resolving set — recorded as constructed, never tuned.
