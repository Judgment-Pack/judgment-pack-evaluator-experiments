# REFERENCE-B — the frozen arm-B/C reference record

Frozen copy, landed at the freeze ceremony (2026-08-19). The executable reference is
[`reference/refB/policy.rego`](refB/policy.rego); this document carries its build record
verbatim from the design tree.

---

# refB — Rego reference implementation of contest policy draft v0.1

Built independently from the prose of `POLICY-DRAFT.md` (P1, D1–D8, O1–O3, U1) plus its
design notes, using the verified engine facts in `POLICY-PANEL-FINDINGS.md` only where
those findings bear on what the *prose* means. No other builder's code was read.

## Artifacts

| file | what |
|---|---|
| `policy.rego` | the reference policy. Package `study`, entrypoint `data.study.decision`. |
| `run_grid.py` | projection + per-cell evaluation driver. |
| `inputs/<id>.json` | the exact input document handed to OPA for each of the 2540 cells. |
| `raw.jsonl` | one record per cell: return code and the raw extracted value (or the error). |
| `results.jsonl` | the scored surface, `{"id","disposition","reasons"}`, in `cells.json` order. |
| `crosscheck.py` | independent Python model + densified-U1 self-check (see Verification). |

Reproduce: `JOBS=16 python3 run_grid.py && python3 crosscheck.py`.

## Toolchain and verification

* Pinned binary `pins/opa/opa_linux_amd64_static`, OPA **1.19.0**, Rego v1.
* `opa check --strict --capabilities pins/opa/caps-filtered.json policy.rego` — clean.
* `opa fmt --diff policy.rego` — clean.
* Every cell evaluated with `--format json --fail --strict-builtin-errors --capabilities
  caps-filtered.json --timeout 10s --data policy.rego --input <cell>.json 'data.study.decision'`
  under `TZ=UTC`, value taken from `.result[0].expressions[0].value`.
* **2540 / 2540 cells evaluated, 0 errors** — no undefined-with-`--fail`, no
  `eval_conflict_error`, no builtin error. (`decision` cannot conflict: it is one rule with
  an `else` chain plus the registered `default`.)
* The registered `default decision := {"disposition":"unresolved","reasons":["no-match"]}` is
  declared verbatim as prescribed, but it is **unreachable on this grid**: re-running all
  2540 cells against a copy of the module with the `default` line deleted produced 0
  undefined results under `--fail`. D2 is named explicitly instead (see "Unknown propagation").
* `crosscheck.py` re-implements the same reading of the prose in Python and diffs it against
  `results.jsonl`: **0 diffs**. It also re-runs U1's quantification over a *dense* domain
  (all 101 risk values; 17 spend values including 0.01, 99,999.99, 499,999.99, 1,999,999.99,
  9,999,999.99) and diffs that against the eight/eight/three candidate sets: **0 diffs** on
  the grid, and **0 diffs across a further 291,600-point sweep** of every unreadable pattern
  × every tri-state × every boundary literal. The candidate sets are therefore adequate
  stand-ins for the full domains, not merely adequate for this grid.

Result distribution over the 2540 cells:

| disposition / reasons | n |
|---|---|
| unresolved `["unknown"]` | 606 |
| reject | 560 |
| unresolved `["missing-required-evidence"]` | 487 |
| unresolved `["no-match"]` | 360 |
| review | 288 |
| approve | 127 |
| unresolved `["exception-escalation"]` | 100 |
| enhanced-review | 12 |

All three of the prose's worked U1 examples reproduce exactly: (1) risk 95 / country
unreadable / spend 1,000,000.00 → **reject**; (2) HIGH / risk 50 / spend unreadable →
**unresolved unknown**; (3) critical supplier / risk unreadable / LOW / spend 100.00 →
**review**.

---

## Encoding decisions

### 1. Two `else` ladders realize the "Order of application" section

The prose ladder is *P1 → O3 → O2 → D1–D8 (as modified by O1) → U1, earliest clause on a
tie*. That is encoded as two `else` chains, because U1 has to be able to *re-run* the lower
part of the ladder at hypothetical values.

**Entrypoint ladder** (`decision`), top to bottom *(corrected 2026-08-19 at the freeze
ceremony: this list still carried the six-rung shape with O2 at the entrypoint after this
report's own adjudication note — see "single largest reading choice" below — recorded that
rung's removal; the bytes carry five rungs, and now so does this list. Found by the V8
ledger's re-derivation, `verification/V8-ASYMMETRY-LEDGER.md`)*:

1. `fin_state == "absent"` → unresolved `missing-required-evidence`
2. `fin_state == "OMITTED"` → unresolved `unknown`
3. O3, when country **and** spend are readable → unresolved `exception-escalation`
4. U1: `count(u1_determinations) == 1` → that determination
5. U1: otherwise → unresolved `unknown`

**Clause ladder** (`determine(risk, spend, country)`), a function over *hypothetical*
readable values, top to bottom: O3, O2, D1, D2, D3, D4, D5, D6a, D6b-present, D6b-absent,
D6b-remainder, D6c (with O1), D7, D8, backstop.

Because an `else` rung is only reached when every earlier rung's body fails, rung order *is*
clause precedence, and it also discharges the earliest-clause tie-break for free: where D3
and D4 both reject (HIGH, risk ≥ 90), or D5 and D3 both reject, or the O1-suspended D6c
region and D8 both review, the earlier rung is the one that fires. That tie-break is not
observable on the scored surface (clause citation is not scored) but it is structurally
present, so a gold author citing governing clauses can read them off the rung order.

**O3 appears in both ladders, deliberately.** At the entrypoint it can only be *settled*
when country risk and requested spend are both readable. When either is unreadable, O3's own
applicability is a function of an unreadable input, so O3 must take part in U1's
quantification instead — which is exactly what the prose's worked example 2 demands (HIGH,
risk 50, spend unreadable → unknown, "spend up to $2,000,000.00 gives review (D8) but above
it gives escalation (O3)"). A `determine` restricted to D1–D8/O1–O2 would return review on
that cell and contradict the prose.

### 2. `determine` is total

The last rung of the clause ladder returns the no-match value unconditionally. This matters
mechanically: `u1_determinations` is a *set comprehension* over `determine`, and a partial
function would silently contribute nothing for the assignments where it is undefined, which
would turn a genuinely 2-valued cell into a spurious singleton. Totality is what makes
`count(...) == 1` mean "every candidate agrees" rather than "every candidate that happened to
be defined agrees".

### 3. U1 as a comprehension

```rego
u1_determinations := {d |
    some r in risk_candidates
    some s in spend_candidates
    some c in country_candidates
    d := determine(r, s, c)
}
```

A *readable* input contributes a one-element candidate list (`[v_risk]`), an *unreadable* one
contributes its full candidate set. So the fully-readable case and the U1 case are the same
code path: with nothing unreadable the comprehension is a singleton by construction and rung
5 issues it. The set (not array) comprehension collapses duplicates, so `count == 1` is
precisely U1's "every readable value the unreadable input(s) could take would yield the same
determination".

Candidate sets and why they cover every interval:

* **risk** `{0, 39, 40, 69, 70, 89, 90, 100}`. The only risk thresholds in the whole policy
  are 40 (D6a/D6b/D7 upper, D6c lower), 70 (D6c upper, D4 lower) and 90 (D3), and every
  occurrence is `< 40`, `>= 40`, `< 70`, `>= 70` or `>= 90`. That partitions the declared
  domain 0…100 into `[0,39] [40,69] [70,89] [90,100]`; every clause condition is constant on
  each block, so one representative per block suffices. Both endpoints of each block are used,
  which also drives the boundary literals through the quantifier.
* **spend** `{0, 100000, 100000.01, 500000, 500000.01, 2000000, 2000000.01, 10000000}`. The
  only spend thresholds are 100,000.00 (D6c/D7 upper, inclusive), 500,000.00 (D6a upper
  inclusive / D6b lower exclusive) and 2,000,000.00 (D6b upper **inclusive** / O3 lower
  **exclusive** — the same numeral in both senses). Blocks: `[0, 100000]`, `(100000, 500000]`,
  `(500000, 2000000]`, `(2000000, 10000000]`. Since the declared precision is cents, the open
  lower endpoints are the next representable value, `x.01`; the closed endpoints are the
  literals themselves.
* **country** `{LOW, MEDIUM, HIGH}` — that is the whole declared domain.

The dense sweep described under Verification is the empirical confirmation of this argument.

### 4. Unknown propagation — the exact choices

| situation | encoding | result |
|---|---|---|
| financial-evidence key omitted | `fin_state == "OMITTED"` sentinel, rung 2 | unresolved `unknown` (P1) |
| financial-evidence `"absent"` | rung 1 | unresolved `missing-required-evidence` (P1) |
| sanctions `UNKNOWN` | a **present string**, matched by value | unresolved `no-match` (D2), never `unknown` |
| newVendor / criticalSupplier / priorEnforcement key omitted | sentinel `null`, tested as `!= "yes"` / `== "yes"` | treated as **no** (O1, O2, D5); never produces `unknown` |
| insurance key omitted, inside D6b's region | third D6b rung | unresolved `unknown` |
| insurance `"absent"`, inside D6b's region | second D6b rung | **enhanced-review** (D6b decides it; D8 does not reach it) |
| risk / spend / country key omitted | U1 comprehension | singleton → that determination; otherwise unresolved `unknown` |

Two consequences worth stating explicitly because they are where a hand-written Rego build
most easily slips:

* **An omitted key never falls through the else-chain into D8.** Every rung that reads a
  possibly-unreadable input reads it as a *function parameter*, never from `input`, so an
  omitted key cannot make a condition quietly false. The only reads of `input` are through
  `object.get` with an explicit sentinel default, so no rung is ever undefined-by-omission.
* **`null` and `"OMITTED"` are safe sentinels** because the projection never emits a JSON
  null for any member — a null cell value means the member is *absent from the document*.

### 5. Reason sets

Every unresolved result in this build is a singleton reason set. In particular **P1 alone**
is reported when financial evidence is absent or unreported, even inside O3's escalation
region (e.g. `finEvidence: absent`, HIGH, spend 3,000,000.00 → `["missing-required-evidence"]`),
because rung 1 short-circuits the whole ladder. Note that O3's "and financial evidence is
available (P1)" conjunct — which the panel showed is load-bearing in the JPS engine, where the
resolver accumulates reasons across steps — is *behaviourally inert* in a ladder
representation: it is written into `determine` for fidelity to the prose, but removing it
would not change any result. That asymmetry belongs in the ledger (V8): the prose sentence
exists to make a JPS pack reachable, and it costs a Rego author nothing.

### 6. Numerics

`run_grid.py` builds the input document as **text**, splicing the canonical decimal strings
in unquoted (`"riskScore": 20`, `"requestedSpend": 2000000.01`). No Python float ever touches
the value. OPA parses JSON numbers as exact big rationals, so all six thresholds compare
exactly; the 2,000,000.00 / 2,000,000.01 pair (inclusive for D6b, exclusive for O3) is
verified on-grid.

---

## Ambiguities in the prose (ambiguity-stratum candidates)

Listed with on-grid cell ids where the shared grid actually contains a witness.

### A1 — O2 when O3's *applicability* is itself unreadable. 1 grid cell: `g7babce6f9a`

`CLEAR, critical=yes, risk/spend/country all unreadable, evidence present`. This build issues
**review**.

* Reading taken (review): the order-of-application section says "a determination issued by a
  clause that does not depend on the unreadable input stands", and O2 adds "its determination
  stands even where the risk score, requested spend, or country risk cannot be read". O2 reads
  neither risk nor spend nor country. Worked example 3 is the readable-country instance of the
  same move.
* Reading rejected (unresolved `unknown`): O2 "never displaces … O3", and U1's *body* is a
  counterfactual over "the clauses above", which includes O3. Substituting HIGH with spend >
  $2,000,000.00 gives escalation while LOW/MEDIUM give review, so the determinations differ
  and U1's test fails.

This is the single largest reading choice in the build. Off-grid siblings of the same shape
(critical=yes with country HIGH and spend unreadable; critical=yes with country unreadable and
spend > $2,000,000.00) are not in `cells.json`; a gold author adding one must settle A1 first.

### A2 — the same shape for D3/D4/D5, resolved the *other* way. 12 grid cells

`g9523233401 g3baa460846 gbab9a22708 gc809663a03 g69041b58cc g36e2c85833 g54c94cd4e3
g7b2b4af87f` (country unreadable, risk ≥ 70, spend > $2,000,000.00), `g6b12361e05
g31d3ba96fc` (country and risk unreadable, spend > $2,000,000.00), `g8b85d109cf g4b769488ce`
(HIGH, risk ≥ 90, spend unreadable). All 12 come out **unresolved `unknown`** here.

D3 rejects "whatever the other inputs" and D5 "whatever the risk score, requested spend, or
country risk" — the same "does not depend on the unreadable input" language that the
order-of-application gloss says makes a determination stand. This build nevertheless puts
D3/D4/D5 *inside* U1's quantification, so where O3 might or might not apply, the case is
unknown rather than reject. The textual basis for treating O2 (A1) differently from D3/D5 is
thin: O2 carries an explicit unreadability sentence and sits above U1 in the
order-of-application list, while D3/D5's "whatever" is about the values being *irrelevant*,
not about them being unreadable — and all of them are declared "subject to the overrides O2
and O3". A strict-parity implementer would either put O2 inside the quantifier (making A1
unknown) or lift D3/D4/D5 out of it (making these 12 cells reject). **Both A1 and A2 should
be treated as one ambiguity axis, not two.**

Note the prose's worked example 1 is *not* a witness: risk 95, country unreadable, spend
1,000,000.00 rejects under both readings, because at spend ≤ $2,000,000.00 O3 cannot fire for
any country value. The prose picked the one instance where the readings coincide.

### A3 — can U1 "issue" an unresolved disposal? 144 grid cells (e.g. `g940cc5fc20`, `g9380988910`, `geb6b75bbe2`)

U1 says "if every readable value … would yield the same **determination**, that determination
is issued", but the Inputs section defines a determination as one of the four outcomes and
calls the fifth state "unresolved". This build treats all five dispositions uniformly: if the
candidate set is a singleton, it is issued whatever it is. That is what keeps sanctions
`UNKNOWN` + unreadable numerics at `no-match` (D2 depends on no input but the screening
result) rather than converting it to `unknown`. A stricter reading — U1 can only issue the
four outcomes, everything else is `unknown` — flips those 144 cells. The same question would
bite D6b's unreported-insurance branch under an unreadable numeric, but the grid has no such
cell (0 witnesses).

### A4 — D6b's third branch is region-total

The prose gives D6b three insurance states. The encoding makes the third rung the *remainder*
of the region (no insurance conjunct), so a present-but-unrecognized availability string would
be read as "unreported" rather than falling to D8. The canonical grid carries only
`present` / `absent` / omitted, so this is unobservable here; it is recorded because the
freeze-time assertion ("no malformed or out-of-range values") is what makes it unobservable.

### A5 — sanctions omitted or out-of-vocabulary

No clause governs it. `determine`'s backstop rung returns `no-match`, matching the registered
default. Off-grid (`sanctions` is never null in `cells.json`), and the prose's Inputs section
declares the screening result total, so this is a defensive choice rather than a reading.

### A6 — P1's "unreported" vs D2 when both are live

`finEvidence` omitted with sanctions `UNKNOWN` yields `unknown`, not `no-match`, because P1 is
the first rung. The prose is explicit ("no other clause of this policy applies unless financial
evidence is available"), so this is not really ambiguous, but it is a place where the two
`unknown`-producing clauses share a reason token and an implementer could reasonably want the
more specific one.

---

## Irreducible mismatches with the prose

**None.** Every clause of the prose is expressible in this representation, including the two
that the panel found inexpressible in the JPS fragment (D6b's unreported branch, and P1's
reason purity beside a live escalation): an `else` ladder short-circuits rather than
accumulating, and Rego has no three-valued knowledge order to be monotone in. The three
worked examples reproduce exactly, all six numeric boundaries compare exactly, and no cell
produced an engine error.

The nearest thing to a mismatch is stated above as an encoding note rather than a defect:
O3's financial-evidence conjunct has no behavioural effect in this arm, so a clause the prose
added specifically to fix a JPS reason-set leak is free here. That is a ledger row
(B/C-favorable), not a divergence.

**V6 answer: n/a** (V6 settles arm A's `onUnknown` assignment; this build is the Rego
reference and has no `onUnknown` surface).


---

## Adjudication note (2026-08-15, appended by the maintainer side)

The "single largest reading choice" above (O2 settled at the entrypoint) was the one
cross-engine divergence: cell {CLEAR, critical=yes, country+risk+spend unreadable} read
review here and unresolved[unknown] in the JPS reference. Policy v0.2 adjudicates for
U1-governs-uniformly (O2's special sentence deleted; worked example 4 added); the
entrypoint O2 rung was removed accordingly and the full grid re-run: 2,540/2,540 agreement,
0 errors.
