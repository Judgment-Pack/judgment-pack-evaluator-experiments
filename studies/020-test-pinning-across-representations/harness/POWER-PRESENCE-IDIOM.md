# The presence-idiom guard's power analysis — §3.2's `GATE(pre-freeze)`

**Status: computed and published BEFORE the freeze, which is what §3.2 registers
it as.** The guard is `harness/e4lib/presence_idiom.py` and the code it emits is
`presence-idiom-unsound` (§1a's table). §3.2 registers the guard **conditionally**:

> if the detector cannot meet (i) and (ii) exactly — 40/40 and 0/22 — **the
> guard is not registered at all** and the mechanism is carried as a Tier D
> descriptive finding only.

**Verdict: the condition is met and the guard IS registered.**
`harness/PINS.json`'s `presenceIdiomGuard.registered` carries that as data, and
`harness/e4lib/admit.py`'s `guard_is_registered()` is the only place it is read —
fail-shut toward NOT registered, so a registry that lost the member would
withhold the code rather than emit it.

Everything below is measured over Study 019's **retained bytes**, at
`studies/019-authorship-across-representations/arms/{B,C}/authoring/*/`. Nothing
was copied into this study and no model was called. The engine is the pinned
`opa_linux_amd64_static` (`opa.assetSha256` `1dd5c559…`), invoked as
`opa parse --format json` under `TZ=UTC` with a scrubbed environment.

---

## The population, and why it is three populations

Study 019 ran 100 arm-B/arm-C slots and retained **76** as §1a-admitted runs
(arm B 37, arm C 39). Those 76 are the denominator §3.2 names. They are not one
population for this purpose, and the analysis reports all three, because the
detector only ever runs at one of them:

| population | n | what it is |
|---|---|---|
| **retained** | 76 | every arm-B/C run in 019's §1a denominator — §3.2's stated denominator |
| **parseable** | 73 | those the pinned `opa parse` accepts; three do not parse at all |
| **admitted** | 60 | those whose policy passed `opa check` — **the detector's registered operating set**, because §3.2 runs it over "each admitted arm-B/arm-C policy" |

The three that do not parse (`B run-016`, `B run-040`, `B run-050`) all carry
Study 019's authoring code **`unparseable-artifact`**. They are refused by an
earlier registered code and never reach the detector, by construction and not by
accident: `harness/e4lib/admit.py` runs the detector only after `opa check`
returns 0.

---

## The in-class set is RE-DERIVED, not read off M-14

§3.2's (i) is a sensitivity claim, and sensitivity measured against the
detector's own definition of the class is not a measurement — it is the
circularity Study 008 taught this programme to check for. The in-class set is
therefore re-derived by a **second implementation that shares no code and no
input representation with the detector**:

* the **detector** reads `opa parse --format json` — the pinned binary's syntax
  tree;
* the **oracle** reads the **policy source bytes the model emitted**, with
  comments stripped, and decides by text: a presence test (`"<literal>" in …`)
  whose collection is a reference to `input` or to a registered object member of
  it, an object literal (a brace group with a top-level `:`, which is what
  separates `{"a": 1}` from the set `{"a", "b"}`), a name bound in the source to
  either, or `object.get(input, "<member>", …)`.

Neither implementation was written against the other's output, and the
disagreements between them were resolved by inspecting the policy — three times,
each recorded below.

**The oracle's answer: 40 of the 76 retained arm-B/C policies use bare-object
membership.** That is M-14's discriminator, reproduced from the bytes by a
method M-14 did not use. Per arm: **21 of 37 in arm B, 19 of 39 in arm C**.

---

## (i) Sensitivity

| population | in-class | flagged | sensitivity |
|---|---|---|---|
| retained (76) | 40 | 39 | **39/40** |
| parseable (73) | 39 | 39 | **39/39** |
| admitted (60) | 32 | 32 | **32/32** |

**40/40 of the in-class runs receive an authoring code.** The one in-class run
the detector does not flag is `B run-040`, which the pinned parser refuses; it
receives the registered authoring code `unparseable-artifact` instead, from a
check that runs strictly earlier. So the in-class set is fully covered by §1a's
partition, and the detector is exact on every policy it is registered to see:
**39/39 parseable, 32/32 admitted, zero false negatives in either.**

This is reported as three numbers rather than one because the honest statement
depends on the denominator, and §3.2's "40 of 76" is a denominator that includes
16 runs whose policy never reaches the detector.

**Agreement is exact at the USE level too, not only at the run level.** Over the
73 parseable policies the oracle finds **178** bare-object presence tests and
the detector flags **178**, with **zero per-run count mismatches across all 73
policies**. Two independent implementations agreeing run for run and use for use
is the evidence that the class is a property of the corpus rather than of either
implementation.

### The three disagreements, and what each one was

Each was a defect in one implementation, found by the other, and each is
recorded rather than smoothed away:

1. **Identity vs content in the alias map (detector defect, 7 runs).** Two rule
   bodies that each write `vendor := input.vendor` are two distinct dicts in the
   parsed document and one binding in the language. `bindings()` compared them
   by identity, called them a conflict and dropped the name — which dropped
   exactly the commonest alias in this corpus. Fixed by comparing canonical
   JSON. Sensitivity before the fix: 29/36.
2. **`object.get` as a collection (oracle defect, 3 runs).** The oracle treated
   every call as lawful, so it missed
   `"riskScore" in object.get(input, "vendor", {})` — which is `input.vendor`
   reached through a builtin. Fixed by reading the two literal arguments out of
   the source. The detector had these right from the start.
3. **The probe operand (both, before either was measured).** An early detector
   flagged `some x in input.vendor`, which is a **lawful iteration** over an
   object's values and appears 351 times in this corpus. `classify()` now
   requires the left operand to be a scalar literal — a PRESENCE test — before
   the collection is resolved at all. Without that condition the false-positive
   count on lawful uses would have been 351 rather than 0, which is the single
   largest thing this analysis found.

---

## (ii) Specificity — the 22 perfect runs

**0/22 perfect runs flagged.** All 22 (arm B 8, arm C 14) parse, all 22 are
admitted, and the detector fires on none of them. The result is the same in
every population, because every perfect run is in all three.

This is the half of the analysis that decides whether the guard may be
registered at all: a detector that flagged a perfect run would zero-score a
suite that pins the reference down exactly, and no sensitivity figure would
excuse it.

---

## (iii) The false-positive census over lawful `in` uses

Over the 73 parseable policies the detector reads **599** membership terms —
**256** written as expressions and **343** inside `some` declarations.

| | uses | flagged |
|---|---|---|
| **presence tests** (scalar-literal left operand) | 248 | 178 |
| — collection is a ref onto a registered object path of `input` | 95 | 95 |
| — collection is a name resolving to one, or `object.get(input, …)` | 83 | 83 |
| — collection is a call returning a set (`object.keys(…)` and friends) | 38 | **0** |
| — collection is a name resolving to a non-object | 3 | **0** |
| — collection is an unresolvable name | 29 | **0** (unclassified) |
| **iterations and bindings** (variable left operand) | 351 | **0** |
| — over an array literal | 11 | **0** |
| — over a set literal | 4 | **0** |
| — over a call | 87 | **0** |
| — over a name | 249 | **0** |

**False positives on lawful `in` uses: 0/392 lawful uses, 0/15 over sets and
arrays** — the two forms §3.2(iii) names by name. The 15 are the 11 array
literals and the 4 set literals; both reference implementations' own idiom
(`object.keys(…)`, 38 uses as a presence-test collection and 87 as an iteration)
is likewise never flagged.

**29 uses are UNCLASSIFIED and none of them is flagged.** An unresolvable name
is reported as unresolved rather than guessed at in either direction, which is
the conservative choice for a detector whose output is an authoring code.

---

## Two measured ceilings, stated here and not discovered later

1. **Presence tests over a FUNCTION PARAMETER are not detected — 2 runs.**
   `B run-023` and `C run-040` both write
   `risk_values(vendor) := [vendor.riskScore] if { "riskScore" in vendor }` and
   call it with `input.vendor`. Semantically that is the same defect through a
   function boundary; syntactically the collection is a parameter, and neither
   the detector nor the independent oracle resolves it. Both runs are non-perfect,
   which is consistent with the mechanism. If they are counted in-class the class
   is 42 rather than 40 and sensitivity on the parseable population is 39/41;
   the analysis does NOT count them, because M-14's discriminator and this
   oracle both stop at the syntax tree, and moving the boundary after seeing
   which side the runs fell on is exactly the choice §5.2's admission test
   forbids. The residual is published here instead.
2. **Alias scope is over-approximated.** `bindings()` ignores rule scope: a
   name bound in one rule body is visible to the whole document, and a name
   bound twice to different terms is dropped rather than resolved to either. On
   this corpus that costs nothing — the per-run use counts agree with the
   oracle exactly, 73 of 73 — and it is measured here rather than assumed.

`presence-idiom-unsound` is also **structurally unreachable in arm A** (§11.11),
which is a registered ceiling of the guard rather than a finding of this
analysis: arm A's format has no analogous single-operator trap on this surface,
and arm A's own near-miss profile in 019 stands unexplained by this mechanism.

---

## (iv) The counterfactual per-member shift — COMPUTED

§3.2(iv) asks for **every one of §5.2's eighteen members recomputed with the
flagged runs coded `presence-idiom-unsound`, published beside the unflagged
figures.** This section first shipped as "NOT COMPUTED, and why": the
eighteen-member family scorer was §7's delta 5, `harness/SCAFFOLD.md` item S4,
and computing the shift with an ad-hoc implementation would have published
eighteen numbers no registered code path can reproduce. The scorer has landed
(`e4lib/family.py`), and the shift is now computed by the registered script
**`harness/counterfactual_shift.py`**, reproduced by
`harness/tests/test_counterfactual_shift.py`, and published in full —
four `family_report()` blocks and the per-member distillation — at
**`harness/COUNTERFACTUAL-SHIFT.json`**.

**The recode, derived from the registration:** a flagged run becomes what every
other authoring-coded run already is on 019's batch — identity false, no kill
record — because `e4lib/admit.py` returns no policy path for a flagged run, so
nothing downstream can run the identity control or a suite. The run stays in
every ITT denominator scoring zero, takes no offset, and leaves the
per-protocol population.

**The flagged set is derived, then gated:** the script re-runs the certified
detector over the 60 admitted policies and refuses to publish unless it lands
on the certified counts exactly — **32 of the 60 admitted runs, arm B 19 of
30, arm C 13 of 30** (the corrected split; the note below records how the gate
caught this document's own first printing).

**The measured effect on the family, A–C (the primary contrast):**

| members | unflagged | counterfactual | shift |
|---|---|---|---|
| all six ITT members (M1/M4/M7/M10/M13/M16) | +0.138 … +0.232 | +0.306 … +0.426 | **+0.168 … +0.209, all positive** |
| all six PP members (M2/M5/M8/M11/M14/M17) | +0.031 … +0.128 | +0.006 … +0.104 | **−0.022 … −0.031, all negative** |
| all six PP/ANCOVA members (M3/M6/M9/M12/M15/M18) | −0.004 … +0.091 | −0.008 … +0.088 | −0.008 … −0.002, all negative |

The code **amplifies every ITT member** (32 B/C runs move from "scored" to
"scoring zero", widening arm A's intention-to-treat lead) and **attenuates
every A–C per-protocol member** (the flagged runs leave the PP denominator, and
the runs that remain are the better ones). Two α = 0.05 decisions flip, both
from reject to not-reject: **M2 and M5**, the L1 per-protocol members
(p 0.0213 → 0.3483 in both columns). No other member's decision moves in
either contrast. In A–B the ITT amplification is larger (+0.246 … +0.303) and
the PP members barely move (|shift| ≤ 0.011, mixed sign). The full 36-row
table with p-values under both codings is in `COUNTERFACTUAL-SHIFT.json`; the
unflagged column reproduces Reprint 1's certified figures to the printed digit
(M17 A–C +0.1275; F-2's anchor p-values exactly), which is the evidence the
script's adapter is the fixture adapter and not a second reading of 019's
batch.

What (iv) was registered to settle is therefore settled by measurement: the
code's effect on the family is **direction-heterogeneous by population** —
it moves ITT members away from the null and PP members toward it — so no
single-direction story about "the guard's effect" is licensed, and any §5
verdict sensitive to those two L1/PP rejections now has the counterfactual
figure to cite instead of an assumption.

> **CORRECTION (pre-freeze, found by the (iv) computation).** This document
> first published the per-arm split as "arm B 15 of 30, arm C 17 of 30". That
> split was never measured: it was arithmetic that assumed how the in-class
> runs overlap the not-admitted runs, exactly the enumerate-instead-of-derive
> defect this programme's standing rule names. When
> `harness/counterfactual_shift.py` re-derived the flagged set by running the
> detector (its certified-counts gate refused to publish over the mismatch),
> the measured split is **arm B 19 of 30, arm C 13 of 30** — same total, 32.
> Every other figure in this document reconciles exactly with the measured
> split and none depended on it: 39/39 parseable is B 20 flagged (19 admitted
> + `B run-025`, `opa-check-failed`) + C 19 flagged (13 admitted + 6
> `opa-check-failed`: C `run-017/032/033/036/046/047`), and the oracle's
> retained in-class split B 21 / C 19 is the measured 19 + 1 + 1 and 13 + 6.
> No figure outside the split moved, and the preregistration's §3.2(iv) row
> carries the corrected split with this note cited. The gate that fired is
> kept firing in CI:
> `test_counterfactual_shift.py::test_the_certified_gate_refused_the_first_printed_split`.

---

## (v) The mutation check

The programme's standing *mutation-check every safeguard test* rule, and §3.2(v)
requires it by name: **break the detector, confirm the test that certifies it
fails, and label any assertion that cannot discriminate.**

The mutation is the one the rule points at: **drop the object-type branch** from
`_object_valued()`, so neither an object term nor a reference onto a registered
object path of `input` is object-valued any more.

| | flagged runs (of 73 parseable) | flagged uses |
|---|---|---|
| the detector | **39** | **178** |
| the mutant | **23** | **83** |
| the detector, restored | **39** | **178** |

Sensitivity collapses from **39/39 to 23/39** and §3.2's condition (i) fails, so
the certifying measurement discriminates. The mutant still flags 23 runs through
the `object.get` branch alone, which is itself worth recording: it means the two
branches are not redundant and neither one alone carries the result.

The same mutation is driven as a test —
`harness/tests/test_score_presence_idiom.py::test_breaking_the_object_branch_makes_the_sensitivity_case_fail` —
over the AST fixtures, so the check runs in CI where §7 forbids invoking `opa`
at all. **One assertion was found not to discriminate and was rebuilt:** the
first version of that test patched `classify_operand()`, which
`memberships()` does not call, so the mutation reached nothing and the test
passed over an unmutated detector. It patches `_object_valued()` now.

---

## Reproducing this

The detector, the oracle and every count above are reproduced by re-running the
analysis over 019's retained tree with the pinned binary. The two
implementations, the population table, the census and the mutation check are the
whole of it; nothing here reads a model, a clock or a path outside the two study
trees.

| quantity | value |
|---|---|
| retained arm-B/C policies | 76 (B 37 / C 39) |
| in-class by the independent source oracle | 40 (B 21 / C 19) |
| (i) sensitivity | **40/40 in-class runs receive an authoring code** — 39/39 of those the detector reaches, 32/32 admitted; the fortieth is refused earlier by `opa check` and coded `unparseable-artifact` |
| (ii) specificity | **0/22 perfect runs flagged** |
| (iii) false positives on lawful `in` | **0/392 lawful uses, 0/15 over sets and arrays** |
| (iv) counterfactual per-member shift | **computed** by `harness/counterfactual_shift.py` over the derived-and-gated flagged set (32/60: B 19, C 13) — every ITT member amplified (A–C +0.168…+0.209), every A–C PP member attenuated (−0.031…−0.022), two decisions flip (M2, M5: reject → not-reject); full table in `harness/COUNTERFACTUAL-SHIFT.json` |
| (v) mutation check | drop the object-type branch: 39/39 → **23/39**, and the certifying test fails |
| unclassified uses | 29, none flagged |
| measured false negatives beyond the class | 2 (presence tests over a function parameter) |
