# Issue 2 — question: where is the Minimum Player Salary schedule meant to come from?

**Title:** NBA: 77 instances reference the minimum player salary, but the schedule appears in neither `reference_rules.txt` nor `auto_test.py`

**Body:**

Question rather than a bug report, about the NBA subset at commit `3b9e225`.

77 of the 216 annotated instances contain a contract at "the minimum applicable player salary" (the
prose uses several phrasings: "minimum player salary", "the minimum salary", "minimum annual
salary"). The CBA's Minimum Player Salary / Minimum Annual Salary schedule — the actual dollar
figures by years of service — appears in neither `nba/reference_rules.txt` nor the stipulation
preamble in `nba/auto_test.py`, as far as we can find.

That leaves a solver two options, and we couldn't determine which is intended:

1. **The schedule is meant to be supplied** (from the CBA or an omitted table), in which case the
   reference rules are missing an input that 77/216 instances need — a solver that refuses to
   invent the figure cannot compute those teams' salaries at all; or
2. **Minimum contracts are intended to be immaterial** to the gold computations (e.g., excluded
   from team salary under the tested rules, or negligible by construction), in which case a line in
   the README or reference rules saying so would let solvers handle them deliberately instead of
   guessing.

Which reading is intended? If it's (1) and the schedule exists somewhere we missed, a pointer would
be enough.

(Context: found while encoding the reference rules into a declarative format for a study; our
pipeline currently omits the field and escalates those instances rather than inventing figures, so
we have no score at stake in either answer — we'd just like to handle the 77 the way the benchmark
intends.)
