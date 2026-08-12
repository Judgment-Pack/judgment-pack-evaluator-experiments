# Round 3 — two independent runs, and why both are here

Round 3 was launched twice. The first launch appeared to have failed: it printed nothing,
and its output file was empty when checked, so a second launch was started against the same
bytes and the same reviewer configuration. The first launch had not failed — it was still
running, and it wrote its output to the same path much later, **overwriting the second
launch's review after that review had already been read and dispositioned**.

The result is that `PREREG-REVIEW.md`'s round-3 blocker table answers **run B**, while the
file committed as the round-3 record was **run A**. Round 4 caught this: it found blocker
row 1 answering run A's blocker 2, and run A's actual blocker 1 — a missing never-seen-version
control — nowhere dispositioned at all.

Both are genuine cross-vendor reviews of the same pre-freeze bytes by the same model and
configuration, so both are kept rather than one being chosen:

- **`REVIEW-run-a.md`** — the first launch, which finished last. Ends with the literal
  `EXIT=$?` marker its launch command wrote, which is how it was identified. Its blocker 1
  (never-seen-version control) was **never dispositioned** until round 4 forced it, and is
  closed now.
- **`REVIEW-run-b.md`** — the second launch, whose blockers `PREREG-REVIEW.md` dispositioned.
  Recovered verbatim from the session transcript after the clobber, since the file on disk
  no longer held it.

The two overlap heavily but are not identical, which is worth stating plainly: two runs of
the same reviewer over the same bytes produced different blocker sets. Neither is the
authoritative one. Both were addressed.

Process fix: review output now goes to a run-specific path, so no two runs can write the
same file.
