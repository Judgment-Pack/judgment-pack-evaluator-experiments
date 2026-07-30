# Deviations — Study 004

Deviations from [`PREREGISTRATION.md`](PREREGISTRATION.md) are recorded here as they occur,
never by editing the preregistration.

1. **Room isolation was instruction-plus-audit, not mechanically disabled tooling.**
   CLEAN-ROOM-PROTOCOL §2 asks for disabled network/MCP; the operator's agent tooling cannot
   selectively disable an encoder's read access or network tools, so isolation was enforced by
   strict instruction and a full mechanical transcript audit (out-of-room paths, network
   commands, web tools) before any room was accepted. All five audits: zero flags
   ([`run-log.md`](run-log.md)). No room was voided.
2. **The feature-pass classifier read the frame from the study branch commit rather than
   `origin/main`** (the merge had not been fetched locally when it ran). The bytes were
   identical to the merged content (verified by digest in its report); labels unaffected.
3. **The build used `-buildvcs=false`** because the pinned-commit checkout is a git worktree
   whose gitfile defeats VCS stamping; no harness step consumes build metadata, and the binary
   digest is recorded in the run log.
