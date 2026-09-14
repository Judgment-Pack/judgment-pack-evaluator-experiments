# Deviations — Study 021

Outside the freeze set by design; written after the freeze.

1. **The post-freeze pin commit** the preregistration names (its freeze block: "one commit made
   when v0.21.0 publishes, carrying the published binary's digest and touching nothing else") is
   the commit titled "study 021: pin the published v0.21.0 linux/amd64 runtime binary" — the
   commit immediately preceding the results commit on `main` (the pull request was rebase-merged
   so that it lands as its own commit; its hash on `main` is `PIN_COMMIT_ON_MAIN`, filled by the
   edit that followed the merge): `harness/PINS.json`'s `jpack.sha256` filled with
   `sha256:5e307176d22e350f6619b2f760fee843db115f2c9d7e4bb188168846e59d4f35`, the digest of the
   linux/amd64 `jpack` binary as published in the runtime's v0.21.0 release, nothing else touched.
   For the record: a first invocation of the governing command under a pin written without the
   `sha256:` prefix the harness compares was refused by the runner before it created the root
   ("the runtime's digest … is not the pinned …"), so no attempt was started and no reserved seed
   was drawn; the pin commit was amended to the prefixed form (the same commit, rewritten before
   any merge; it was rewritten once more, unchanged in content, when the branch was rebased onto
   `main` after Study 022's freeze merged ahead of it) and the governing command then ran once,
   as `results/primary-attempt-001`.
2. **Nothing else.** The registration, the matrices and the harness ran as frozen.
