"""The scorer's parts, one module per registered concern.

`harness/score.py` is the single publisher (PREREGISTRATION.md "The freeze and
the primary attempt": "The scorer is the only publisher"). This package holds
the machinery it publishes FROM, split so that each part answers to one
authority and can be tested against that authority alone:

    stats.py     the interval arithmetic — PORTED BY DIGEST from Study 012's
                 `harness/score_rates.py` (Clopper-Pearson, exact rationals,
                 the registered test vectors) and from this study's
                 `design/mutants/oc_table.py` (the FM-score exact unconditional
                 contrast, Reading 1: the Delta0 = 0 inversion the registered
                 decision actually reads)
    extract.py   the registered marker rule (design/pilot/pilot_run.py)
    admit.py     the per-language admission layer and section 1a's SIX
                 authoring codes, which the pilot's three do not cover
    engines.py   the two-engine execution layer, with the pinned binaries
                 verified fail-closed before any of them is invoked
    e4.py        pairing, the X1 filter, the identity control, kill, the tau cut
    census.py    E5 — Study 012's census machinery, ported
    capabilities.py  the OPA capability filter — derived from the pinned
                 binary's own set under the registered denylist, with the
                 both-directions canary (salvaged from the E1-line apparatus)
    decision.py  section 5's ordered exhaustive decision rule

Nothing in this package makes a model call, reads a clock, or looks at an
absolute path it was not given. `harness/PORTS.md` carries a two-sided row for
every ported module and every assembled module names its design prototype and
that prototype's sha256 in its own docstring.

The package deliberately imports nothing at package scope: Study 012's round-8
finding 1 is that a chain of imports is only as deferred as its eagerest link,
and `integrity.verify_bytecode()` has to run before any of these modules load.
"""
