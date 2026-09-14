# Study 021 — does replayed history catch a planted defect, and can the profile tell a moved line from the rest?

**Status: RUN. Frozen at the squash-merge of PR #105 after eight pre-freeze cross-vendor
review rounds (`PREREG-REVIEW.md`); the runtime pinned by one post-freeze commit
(`DEVIATIONS.md`); the registered primary attempt `results/primary-attempt-001` ran once under
the published v0.21.0 binary: `R1 holds` — 131 registered cells, 0 divergent, the reviewer's
holdout 8/8, every control gate green (`ANALYSIS.md`). Everything under `pilots/` is harness
validation that supports no claim.**

A pack drafted from policy documents is tested against the decisions actually made under the
policy — each past decision a matrix row whose facts are what was on file and whose expectation
is what was recorded. The runtime replays the rows and reports a **profile** beside the
mismatches (runtime ADR-0034): agreement by origin, coverage by origin, and at each threshold the
pack draws, how many past cases sit below, at and above it and how many disagree. This study
plants nine classes of mechanical defect in four packs, builds two kinds of history under the
unplanted packs — cases that sit where the policy draws its lines, and cases drawn at random
over its domains, in four sizes — and measures two things, with exact intervals: whether the
replay **catches** the defect, and whether the profile's threshold report then carries the
**line-moved signature** a moved threshold carries, so that a defect would be read as a policy
change or a policy change as a defect.

Registered in advance, with the structure in each pack's text that each expectation follows from
(`PREREGISTRATION.md` §6): a rule's guard masked by an exception at the same literal; a rule
whose outcome is the fallback; boundary flips that random history cannot see; evidence guards
under a required-evidence escalation; the one-sided sites whose defects *must* masquerade as a
moved line, because on one side of a threshold a swapped outcome and a line moved to the far end
are the same observation.

No model, no external component: one runtime mechanism, measured study-internal end to end.
