"""E5 — the interpretive-spread census. Study 012's machinery, ported.

**STUDY 020 PORT NOTE.** These are Study 019's bytes, taken by digest under
`harness/PORTS.md`'s two-sided table. The lineage sentence below is 019's own and is
kept as history; the binding that RUNS is 020's — `harness/integrity.py` verifies
Study 019's lock first (`harness/STUDY-MANIFEST.sha256`, at the digest 019's own
registry pins for it) and binds this file's source cell to 019's line for it.
`PREREGISTRATION.md` §7 lists this file under "ported with no design change".

PORTED FROM Study 012's `harness/census.py`
(sha256 `911eb25773923789e5ddeae20f0bfa68032f932ae9c62fd7e9a21ad8aa8b73ea`), the
digest `harness/SCAFFOLD.md` item S6 names. `harness/PORTS.md` carries the
two-sided row. PREREGISTRATION.md section 5 registers E5 as "012's census
machinery, ported" and section 7 lists it under the ported harness, so this is a
port and not a new census — Study 012's own port row says the same thing about
Study 011's `analysis/diversity.py`, and the reason is the same: a registered
secondary written fresh is a registered secondary nobody has run.

THE ENUMERATED CHANGE LIST
--------------------------
1. **Carried verbatim**: `show_signature()` (012 lines 226-235), `_token()`
   (237-241), `show_multiset()` (243-249) and `cover_greedily()` (251-269) —
   the deterministic renderers and the greedy cover, which name nothing about
   any study's policy family. `_x4()`'s `signature()` (012 lines 515-541), the
   distinct-whole-run-multiset distribution that 012's round-5 finding 9 forced
   into existence, is carried as `signature_groups()` with the same ordering key
   (descending by run count, then by the rendering) so a group table produced
   here sorts the way 012's does.
2. **NOT carried, because they name Study 012's stimulus and nothing here**:
   `_policy_mirror()`, `edges()`, `embargoed()`, `score()`, `band()`,
   `profile()`, `probe()`, `probe_exact()`, `deciding_clause()`,
   `clause_text()`, `show_probe()`, and X1-X6 (`_x1()`…`_x6()`) with their
   `render_markdown()`. Study 012's census is over vendor records a model wrote
   INSIDE a completion, under one arm's thresholds; this study's authors emit a
   policy and a test suite, and there is no `vendor` record to bucket. Carrying
   those functions would give this study six registered endpoints it did not
   register.
3. **The stimulus is a PARAMETER, not a module constant.** 012's census read
   the arm's `FAMILY.json` and `ARM.json`. Here `census()` takes the per-run
   outcome vectors and the label of the stimulus they were produced on, so the
   census machinery cannot silently be run on the wrong grid.
4. **The two registered rows are section 5's, and only those**: "per-arm
   distinct structural encodings and pairwise-disagreement profiles". 012's
   X1-X6 are not registered here and are therefore not computed (this is 012's
   own change 3, applied to this study's registration).
5. **No publisher and no `__main__`**, carried from 012's change 5: the only
   publisher in this study is `harness/score.py`. This module computes and
   renders; the scorer writes.
6. **No interval**, carried from 012: every count here is case-level or
   run-pair-level, and cases inside one completion are not independent trials.
   Section 5 makes E5 descriptive and section 1's R2 "is never adjudicated and
   never falsifies".

THE STIMULUS IS REGISTERED (SCAFFOLD item S6, closed)
-----------------------------------------------------
`registered_stimulus()` was a refusing stub for as long as section 5 named no
census grid. Section 5 names one now — "Registered census stimulus: the gold-row
input set (the frozen gold suite's inputs, and the freeze pins the count in
`harness/PINS.json`'s `goldSuite.rows`; disagreement profiles are computed over
exactly these cells, closing the section 9 joint-reading concern about unstated
stimuli)" — so the stimulus is READ from the frozen gold suite, as ids and order
only. The quotation deliberately elides section 5's row COUNT (round-4 finding
R4-6: this docstring still said 109 after the suite grew to 117). The count is
never restated here; `registered_stimulus()` computes it from the rows it is
handed, and the currency suite recomputes section 5's from the committed suite. Section 9 is unchanged and still governs: E4's stimulus is the mutant set
against each run's own authored suite, the census's is these cells, and no
tradeoff statement combining the two is licensed. The label travels inside every
record this module emits so that a reader of one table cannot lose it.
"""
from __future__ import annotations

import collections


class CensusError(Exception):
    """A refusal in the census, with a named code as its first word."""


def _token(part) -> str:
    """One member of a key, written as the census writes booleans everywhere
    else in this file. Carried verbatim from Study 012."""
    return str(part).lower() if isinstance(part, bool) else str(part)


def show_signature(multiset: tuple) -> str:
    """One whole-run multiset as text — `(approve, []) x3, …` — in the order the
    multiset was built in, so two runs that answered the same way the same
    number of times render identically and two that did not cannot render the
    same. Carried verbatim from Study 012 (its section 4.5 X4, round 5 finding
    9)."""
    if not multiset:
        return "none"
    return ", ".join("(%s) x%d" % (", ".join(_token(part) for part in key), count)
                     for key, count in multiset)


def show_multiset(counter) -> str:
    """A counter of scalar values, ascending by rendering, as `approve x58`.

    Changed from Study 012 in ONE respect, recorded because it is a behaviour
    change and not a rename: 012 sorted by `Decimal(value)` because its values
    were risk scores. This study's values are outcome tokens, so the sort is by
    the rendered string. A numeric sort over `approve` would raise."""
    if not counter:
        return "none"
    return ", ".join("%s x%d" % (value, count) for value, count
                     in sorted(counter.items(), key=lambda item: str(item[0])))


def cover_greedily(probe_runs: dict, n_runs: int = None) -> int:
    """How few probes suffice to cover every covered run. Greedy, with a
    deterministic tie-break on the probe key, so the count is reproducible; it
    is an upper bound on the true minimum, and it is exact wherever it equals
    the number of probes. Carried verbatim from Study 012, except that `n_runs`
    is now optional — 012 accepted it and never read it."""
    remaining = set()
    for runs in probe_runs.values():
        remaining |= runs
    chosen = 0
    while remaining:
        best = max(sorted(probe_runs),
                   key=lambda key: len(probe_runs[key] & remaining))
        gain = probe_runs[best] & remaining
        if not gain:
            break
        remaining -= gain
        chosen += 1
    return chosen


def encoding_key(vector) -> tuple:
    """One run's STRUCTURAL ENCODING key: the multiset of its answers.

    A multiset and not a sequence, so two runs that answered the same stimulus
    the same way in a different internal order are one encoding — the census
    asks how many DISTINCT readings the arm produced, and an ordering is not a
    reading."""
    return tuple(sorted(collections.Counter(tuple(answer) if isinstance(answer, (list, tuple))
                                            else (answer,)
                                            for answer in vector).items(),
                        key=repr))


def signature_groups(per_run: dict) -> list:
    """Every distinct whole-run encoding with the runs carrying it.

    Carried from Study 012's `_x4().signature()` (lines 515-541) with its
    ordering key unchanged: descending by the number of runs, then by the
    rendering, "so the order is a fact about the data and not about a hash"."""
    counted = collections.Counter(encoding_key(vector)
                                  for vector in per_run.values())
    members = collections.defaultdict(list)
    for run, vector in sorted(per_run.items()):
        members[encoding_key(vector)].append(run)
    return [{"signature": show_signature(multiset),
             "runs": count,
             "runIds": sorted(members[multiset])}
            for multiset, count in
            sorted(counted.items(),
                   key=lambda item: (-item[1], show_signature(item[0])))]


def pairwise_disagreement(per_run: dict) -> dict:
    """Section 5's second E5 row: the pairwise-disagreement profile.

    For every unordered pair of runs in an arm, the number of stimulus points on
    which the two runs' artifacts answered differently. Published as the
    distribution over pairs rather than as a mean, for Study 012's round-5
    reason: a mean says how far apart the arm is on average and cannot
    distinguish one outlier from a uniform spread, and the spread is what the
    census is about.

    Refuses on ragged vectors: two runs answered "the same stimulus" or they did
    not, and comparing a 40-point vector with a 39-point one position by
    position is a comparison of two different questions."""
    runs = sorted(per_run)
    lengths = {len(per_run[run]) for run in runs}
    if len(lengths) > 1:
        raise CensusError(
            "E5-RAGGED-VECTORS the runs answered %s stimulus points; a pairwise "
            "disagreement count over vectors of different lengths compares two "
            "different questions" % sorted(lengths))
    distribution = collections.Counter()
    pairs = []
    for left_index, left in enumerate(runs):
        for right in runs[left_index + 1:]:
            differing = sum(1 for a, b in zip(per_run[left], per_run[right])
                            if a != b)
            distribution[differing] += 1
            pairs.append({"runs": [left, right], "disagreements": differing})
    total = sum(distribution.values())
    return {
        "pairs": total,
        "stimulusPoints": (sorted(lengths)[0] if lengths else 0),
        "distribution": {str(key): distribution[key]
                         for key in sorted(distribution)},
        "identicalPairs": distribution.get(0, 0),
        "maxDisagreements": max(distribution) if distribution else None,
        "perPair": pairs,
    }


def census(arm: str, per_run: dict, stimulus_label: str) -> dict:
    """The two registered E5 rows for one arm.

    `per_run` is `{run id: [answer, …]}` — one answer per stimulus point, in the
    stimulus's own order. `stimulus_label` names the grid the vectors came from
    and is carried into the record, because section 9 makes "which stimulus" the
    load-bearing fact about every census number."""
    if not per_run:
        return {"arm": arm, "stimulus": stimulus_label, "runs": 0,
                "distinctEncodings": 0, "encodings": [],
                "pairwiseDisagreement": None,
                "minimalCoveringSet": 0}
    groups = signature_groups(per_run)
    covering = {group["signature"]: set(group["runIds"]) for group in groups}
    return {
        "arm": arm,
        "stimulus": stimulus_label,
        "runs": len(per_run),
        "distinctEncodings": len(groups),
        "encodings": groups,
        "pairwiseDisagreement": pairwise_disagreement(per_run),
        "minimalCoveringSet": cover_greedily(covering),
        "note": "descriptive; section 1's R2 is never adjudicated and never "
                "falsifies, and section 9 forbids any tradeoff statement "
                "combining these rows with the E4 rates",
    }


# ROUND-1 FINDING R1-19. The label used to be the constant string
# "the gold-row input set (105 gold inputs)", written when the suite had 105
# rows; the adequacy work and the arm-A reference repair have moved it twice
# since, and a published census table would have carried a count the suite it
# was computed over does not have. The count is DERIVED from the stimulus that
# was actually read, so the label cannot disagree with its own data.
STIMULUS_LABEL_TEMPLATE = "the gold-row input set (%d gold inputs)"


def stimulus_label(count: int) -> str:
    """The registered stimulus's label at the count actually read."""
    return STIMULUS_LABEL_TEMPLATE % count


def registered_stimulus(gold_rows: list, gold_sha256: str = None) -> dict:
    """Section 5's REGISTERED census stimulus: the gold-row input set.

    This was a refusing stub (`E5-STIMULUS-UNREGISTERED`, SCAFFOLD item S6) for
    as long as section 5 named no grid. It names one now — "Registered census
    stimulus: the gold-row input set (the frozen gold suite's inputs, and the
    freeze pins the count in `harness/PINS.json`'s `goldSuite.rows`;
    disagreement profiles are computed over exactly these cells, closing the
    section 9 joint-reading concern about unstated
    stimuli)" — the row COUNT elided from the quotation, because a count
    restated here goes stale and did (R4-6) — so the stimulus is READ from the frozen
    gold suite rather than refused, and it is read as a stimulus and not as an
    oracle: only the row IDS and their ORDER are taken, and no expectation of
    theirs reaches any census number. What each arm's artifacts ANSWER on these
    cells is the census's data.

    Section 9 is unchanged and still governs the reading: the census's
    expressiveness rows and the E4 kill rates live on different stimuli — E4's
    is the mutant set against each run's own authored suite — and no tradeoff
    statement combining them is licensed. That is why the label travels with
    every census record this module emits.

    Refuses rather than guessing when the suite it is handed is not a stimulus:
    an empty suite has no cells, and duplicate ids would make two different
    cells one census point."""
    if not gold_rows:
        raise CensusError(
            "E5-STIMULUS-EMPTY the registered census stimulus is the gold-row "
            "input set and the gold suite handed to it has no rows")
    points = [row["id"] for row in gold_rows]
    if len(set(points)) != len(points):
        raise CensusError(
            "E5-STIMULUS-DUPLICATE-CELLS the gold suite carries duplicate row "
            "ids, so two different cells would be one census point")
    return {"label": stimulus_label(len(points)), "count": len(points),
            "points": points,
            "goldSha256": gold_sha256,
            "registeredIn": "PREREGISTRATION.md section 5, E5",
            "note": "section 9: the census's rows and the E4 kill rates live on "
                    "different stimuli (E4's is the mutant set against each "
                    "run's own authored suite) and no tradeoff statement "
                    "combining them is licensed"}


def render_markdown(per_arm: list) -> str:
    """The census table, rendered. No publisher here (change 5): the scorer
    writes what this returns."""
    lines = ["# E5 — interpretive-spread census", "",
             "Descriptive. No decision reads any of it (PREREGISTRATION.md "
             "section 5), and section 9 forbids combining these rows with the "
             "E4 rates.", ""]
    for entry in per_arm:
        lines += ["## Arm %s" % entry["arm"], "",
                  "Stimulus: %s. Runs: %d. Distinct structural encodings: %d. "
                  "Minimal covering set: %d."
                  % (entry["stimulus"], entry["runs"],
                     entry["distinctEncodings"], entry["minimalCoveringSet"]),
                  "", "| Encoding | Runs |", "|---|---|"]
        for group in entry["encodings"]:
            lines.append("| `%s` | %d |" % (group["signature"], group["runs"]))
        spread = entry["pairwiseDisagreement"]
        if spread is not None:
            lines += ["", "| Disagreements | Pairs |", "|---|---|"]
            for key in sorted(spread["distribution"], key=int):
                lines.append("| %s | %d |" % (key, spread["distribution"][key]))
        lines.append("")
    return "\n".join(lines) + "\n"
