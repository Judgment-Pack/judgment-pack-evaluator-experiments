# Deviations — Study 019

Deviations from the frozen preregistration land here with a reason and a date — never by
editing the preregistration or any frozen artifact. Nothing is frozen yet.


## 1 — 2026-08-20: the registered scaffold deletion broke the test that verifies it survives

**What happened.** The first post-freeze commit performed `harness/SCAFFOLD.md`'s
registered deletion (its own §9) and filled `freeze.commit` with the squash-merge commit
`51cae0225ea2e9e5679c8e496b39a62e93385278`. The suite then failed:
`test_the_lifecycle_check_survives_the_scaffolds_registered_deletion` builds its scratch
scenario by copying the live scaffold and deleting the copy — after the real deletion there
is nothing to copy, so the test that proves the deletion is survivable could not itself
survive the deletion. A frozen-apparatus defect, found by executing the registered act.

**What was done.** The minimal fix: the test's scenario construction is conditional (a
live scaffold is copied and the copy deleted; an already-deleted scaffold means the scratch
tree is natively the post-deletion shape). Every assertion the test carries is unchanged.
Because `harness/tests/*.py` is manifest-covered, the fix moves covered bytes:
`STUDY-MANIFEST.sha256` is regenerated and `studyManifest.sha256` re-pinned in the
registered anchor order, in this same commit, with this entry as the record.

**What it costs.** The frozen `studyManifest` digest of the freeze commit no longer names
the current manifest; this entry is the auditable bridge. No registered document, gold row,
mutant, reference, prompt, pin of any engine or model, or scored-surface semantics moved —
the diff is one test's setup lines, the manifest, and the one pin over it.

**What was deliberately NOT done.** No other frozen byte was touched; the defect's
sibling risk (other tests copying files whose deletion is registered) was searched for and
none exists.
