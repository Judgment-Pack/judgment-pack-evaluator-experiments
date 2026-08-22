---
status: proposed
date: 2026-08-21
deciders: maintainer
---

# Verify the record from its own commit, and keep state as data the documents render

## Context and problem statement

Study 019's pre-freeze review ran twelve cross-vendor rounds, and its middle rounds were
dominated by one class of finding, recurring under different names: **the record drifted
from the tree it described, and the tests meant to prevent that either could not see the
drift or could be defeated by wording.** Concretely, across rounds 3–9:

- A suite-of-record number ("N passed") was claimed from a working tree and was false of
  the committed HEAD three separate times — once because the manifest went stale between
  the test run and the commit, once because a fix was left unstaged, once because the
  commit itself shipped a bytecode cache that only validated on the machine that wrote it.
- Status headers restated round counts, verdicts and open/closed state in prose, and a
  test suite tried to hold that English to the truth. The reviewer defeated the parsers
  for four consecutive rounds (negated sentences accepted as attributions, placeholder
  disposition cells counted as dispositions, duplicate round identities silently
  collapsed, quoted YAML keys skipping a guard). Each response grew the parser; each
  round the reviewer found the next bypass. The arms race was unwinnable by construction.
- The regime's own ceremony reddened the tree: opening a review round (a prompt-only
  commit) failed the lifecycle tests, because "round state" was derived from directory
  equality rather than from what a round's artifacts actually show.

Three mechanisms ended the class, and the round-11/12 record shows it ended (one finding,
then zero). This ADR registers them for every subsequent study, in ADR 0004's lineage:
0004 keeps appendable files out of the covered set; this ADR keeps every covered claim
bound to committed bytes and every stateful claim out of parsed prose.

## Decision

1. **The archive-verified suite of record.** A suite-of-record claim ("N passed") is made
   only of a commit, and only after running the suite from a reconstruction of that very
   commit: `git archive <commit> | tar -x` into a fresh directory, `git init && git add
   -A` inside it (index-binding tests need a real index), then the full suite under the
   registered interpreter and flags. Every commit that states or moves a covered claim is
   verified this way **before push — ceremony and prompt-only commits included**, since
   Study 019's two self-inflicted blockers were both ceremony commits. A number produced
   any other way is a working-tree observation, not a suite of record.

2. **State is data; documents render it.** Round counts, verdicts, severities and
   open/closed state live in one machine-readable block in the review record
   (`ROUND-STATE-BLOCK`, strict-parsed: duplicate keys refused at every depth, closed
   member sets, typed members, a closed verdict vocabulary bound to the review prompt's
   output contract). A committed renderer produces the one status sentence each front
   door carries between markers, verbatim-required and never parsed for meaning. Round
   state is **derived from the round's own artifacts** (prompt, verbatim review, record
   section, per-finding disposition cells) and compared to the block member-by-member;
   exactly one round — the highest — may be open. Opening or closing a round is then a
   mechanical edit: block, render, manifest, archive-verify.

3. **A two-tier threat model for the guard layer itself.** The registered surface —
   preregistration, stimulus, gold, corpora, references, prompts, sealed sets, and the
   scoring/driver/integrity chain — gets adversarial review and freeze gating, in full.
   The review-support apparatus (currency tests, ceremony tooling, renderers) is
   registered as **drift detection under an honest operator**: its purpose is to catch
   the maintainer's own staleness, not to survive the maintainer as an adversary — "a
   gate against drift, not a root of trust." Hardening findings against that apparatus
   are recorded as advisories in an appendable register (excluded from the covered set
   per ADR 0004), not gated. Study 019's reviewer, asked directly, upheld this scope on
   its merits; the regime requires recorded review and written dispositions, "not a test
   that adjudicates arbitrary English."

Supporting conventions registered with the same force:

- **History is load-bearing; never rewrite it for metadata.** Review records name clean
  HEADs by hash. Retroactive DCO sign-off therefore uses the DCO app's individual
  remediation commits (`.github/dco.yml` enables it, landed with this lineage), never a
  rebase.
- **Anchor order is linear and one-directional**: covered files → manifest → the registry
  pins the manifest → the commit anchors the registry. The manifest is regenerated last
  in every reconciliation; the registry is never covered; and lineage members inside the
  registry (digests of *another* study's reviewed files at port time) are historical
  facts, not live bindings — a sweep that "refreshes" one corrupts the port record.

## Consequences

- Suite-of-record claims survive checkout: what CI, a reviewer, or a future maintainer
  reconstructs from the commit is what was claimed of it. The cost is ~2 minutes per
  verified commit, paid at every ceremony step.
- Status prose cannot drift from state, because the only stateful sentence is rendered;
  everything else the headers say is ordinary prose whose truth rests on review, where
  the regime always placed it.
- The guard layer stops growing adversarially. Study 019's currency suite shrank when
  the English-parsing tier was deleted, and the reviewer's findings after the descope
  were registered-surface findings — three, then one, then zero.
- The clean round is representable (a late 019 lesson folded in here): a round that
  returns a verdict with zero findings is a registered shape — severities all zero,
  finding range null, a disposition table as empty as the review — because the first
  clean round in the regime's history was initially unencodable by machinery that had
  never seen one.
- These conventions bind new studies. Studies 016–018 are left as they stand, for ADR
  0004's reason: re-scoping a frozen study's machinery to adopt a convention it never
  used would rewrite anchors to repair a defect none of them exhibited.
