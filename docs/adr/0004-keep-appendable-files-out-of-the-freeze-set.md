---
status: proposed
date: 2026-08-12
deciders: maintainer
---

# Keep appendable files out of a study's freeze set

## Context and problem statement

A frozen study pins `harness/STUDY-MANIFEST.sha256` in `harness/PINS.json` as `studyManifest`, and
the manifest covers an exact set of files. Every covered file is therefore frozen transitively: an
edit changes the manifest, which breaks the pin, which fails pin enforcement on every subsequent
run. That is the intended behaviour, and it is what makes a frozen study's claims checkable.

Studies **016, 017 and 018** put `DEVIATIONS.md` inside that covered set. Each of their
preregistrations also says, in terms, that post-freeze corrections go to `DEVIATIONS.md` rather than
by editing frozen artifacts. Both cannot be true. **Appending the first genuine deviation would
break the anchor the deviation exists to protect** — leaving a study that discovers a real problem
after its freeze to choose between not recording it and invalidating its own pins.

`README.md` is covered by the same three manifests, so each study's status banner is frozen at
whatever it said before its attempt ran. Studies 017 and 018 both still read *"Nothing has run under
the freeze; `results/` is absent until the registered primary attempt"* while their results sit
beside them.

### It is a regression, and the earlier shape was deliberate

| Study | `DEVIATIONS.md` covered | `DEVIATIONS.md` used post-freeze |
| --- | --- | --- |
| 014 | **no** — excluded by construction | **yes**, one entry |
| 015 | **no** | **yes**, substantial |
| 016 | yes | no |
| 017 | yes | no |
| 018 | yes | no |

Study 014 scopes its manifest to `REGISTERED_DOCUMENTS` — preregistration, review record, SPEC,
matrices — and carries an explicit comment that the exclusions are "by construction, not by
omission … asserted by a harness test, so a future edit that quietly re-covers either one fails the
suite". Study 016 widened the set to include `README.md` and `DEVIATIONS.md` and dropped that
guard.

**The two studies that actually needed the mechanism are the two where it still works.** 016–018
never exercised it, which is the only reason this survived twelve pre-freeze review rounds on 018
alone — including three rounds specifically hunting safeguards that cannot fail. It was found by
attempting to use it, not by reading it.

## Decision

A study's manifest covers **what must not change**. A file whose purpose is to be appended to after
the freeze is not that, and is excluded **by construction** with a harness test asserting the
exclusion.

Concretely, for any new study:

1. Scope the manifest to registered documents: the preregistration, the pre-freeze review record,
   the study's SPEC, and every registered matrix and evidence map.
2. Exclude `DEVIATIONS.md` and `README.md` explicitly, in a named constant, not by omission.
3. Assert both exclusions in a harness test, so a future widening fails the suite rather than
   passing quietly and taking the deviation mechanism with it.
4. Prefer status banners that cannot go stale; where one can, keep it outside the covered set.

## Consequences

**Studies 016, 017 and 018 are left alone.** They are frozen, their pins are correct, and their
recorded results are unaffected — re-scoping their manifests now would rewrite an anchor to repair a
mechanism none of them used, which trades a real guarantee for a hypothetical convenience. Their
`ANALYSIS.md` files are outside the covered set and are where any correction belongs; Study 018's
already records this.

The cost is asymmetric and worth naming: a study that never deviates loses nothing, and a study that
does would otherwise lose either the record or the anchor. That is why this is decided ahead of the
next study rather than when one needs it.

**What is given up.** Excluding `README.md` means a study's front matter is not covered by the
whole-study digest, so a reader cannot verify it from the manifest alone. That is the correct trade:
the README is navigation, the registered artifacts carry the claims, and the pins already cover
every artifact a claim rests on.

Tracked as [issue #65](https://github.com/Judgment-Pack/judgment-pack-evaluator-experiments/issues/65).
