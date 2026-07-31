# Adversarial review — Study 008

## Review status

An in-house adversarial pass, run against the completed study and the code it depends on, with every
attack checked against source rather than argued. It is **not** the independent, cross-vendor review
the evidence bar requires. Its findings were accepted rather than rebutted: they changed the study's
headline, added calibration controls, and corrected the framing in
[`RESULTS.md`](RESULTS.md) and [`ANALYSIS.md`](ANALYSIS.md). Findings that survive as unrepaired
limits are listed below with what was done about each.

## Strongest contrary interpretation

> Study 007's verifier is not independent of Arm B — it *is* Arm B. `verify_candidate` re-derives the
> claim by calling `derive_payload` (007 `harness/study.py:465-467`), the same function Arm C is
> compared against, then requires the candidate's facts, availability, status, fact claims and claim
> availability to equal that output (`:473-497`) and its basis to be a **superset** of that
> function's basis (`:499`). So D1 is not "an independent authority admitted the rule"; it is
> "Arm C's claim equals Arm B's claim and its basis contains Arm B's." D2 is entailed, D4 is a
> determinism check, D5 is a subset of D1. And the rule itself was authored *from* `derive_payload`
> (`derivation-rule/README.md:26-27` describes its corpus as cross-checked to reproduce
> `derive_payload`'s claim). The honest headline is not "a portable rule cleared an independent bar"
> but "a faithful transcription transcribes faithfully, and its short-circuit read set coincides with
> the original's hand-curated basis on these eight payload shapes — and not on the ninth."

This is accepted in full. `ANALYSIS.md` now leads with it.

## Confirmed findings and disposition

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | The verifier's admission criterion **is** Arm B's derivation (007 `study.py:465-500`), so D1/D2 test transcription fidelity, not independent admission | Critical | **Accepted.** Endpoint table in `RESULTS.md` now states what each endpoint actually tests; `ANALYSIS.md` leads with the contrary interpretation. The preregistration's independence premise is recorded as false in `DEVIATIONS.md` §4. |
| 2 | D1's basis test is a **superset** test (`:499`); a kitchen-sink basis passes | Major | **Accepted and measured.** Added calibration controls to the harness: an un-derived wide basis is admitted **24/24**, a one-short basis **0/24**. Reported in `RESULTS.md` above the endpoint discussion. |
| 3 | D2 cannot fail while D1 passes, so the preregistration's named "worst outcome" is unreachable | Major | **Accepted.** Stated in the endpoint table and in `ANALYSIS.md`; the registered guard against silently admitting a wrong mapping did not exist. |
| 4 | D4 is vacuous — the verifier forces both arms' runtime inputs byte-identical | Major | **Accepted.** Labelled as a determinism check. Scoring also tightened so a `None == None` runtime failure no longer counts as agreement. |
| 5 | D5 is entailed by D1 and reflects **host assembly**, shared with Arm B, not the portable rule | Major | **Accepted.** The recovery table in `ANALYSIS.md` is now attributed to `envelope()`/`cell_inputs()`, which both arms share. |
| 6 | "Built separately … without either being written against the other" is contradicted by `derivation-rule/README.md:26-27` | Critical (framing) | **Accepted.** The preregistration is frozen and not edited; `DEVIATIONS.md` §4 records the premise as false and confines the study's contribution to D3 and the probe. |
| 7 | The probe's divergence was already recorded in `derivation-rule/corpus/type-notdated.json`, committed before the preregistration | Major (framing) | **Accepted.** `RESULTS.md` and `ANALYSIS.md` now say the probe *confirms the verifier rejects* that basis rather than discovering the divergence. |
| 8 | The freeze omitted `gateway.key`, `common.py`, `acquisition_gateway.py` and all per-cell data, and nothing checked the freeze was committed (Study 007 had `verify_committed_freeze`; Study 008 dropped it) | Major | **Fixed.** `FROZEN_INPUTS` extended; `cell_data_digest()` freezes every per-cell artifact, receipt, `cell.json` and `final.json`; `verify_committed_freeze()` restored and enforced in `run`. |
| 9 | The arms differed in the `explanation` string too, so "differ in exactly one respect" was literally false | Minor | **Fixed.** Both arms now use one shared `EXPLANATION` constant. |
| 10 | Arm B re-implements `candidate_from_gateway` rather than calling the frozen function | Minor | **Accepted, recorded** in `DEVIATIONS.md` §5. The rebuild is structurally identical apart from the explanation, so no number changes. |
| 11 | `armA.admitted` was `null` in every record; Arm A's 21/24 and the lost-cell list were transcribed constants | Minor | **Fixed.** `arm_a_admitted()` derives per-cell admission from Study 007's own `RESULTS.json` (`M2`), yielding 21/24. |
| 12 | `derive.py:279-285` resolves fact-source pointers **outside** the read set, so a fact's own pointer enters the basis only if some condition tested it | Minor→Major contract gap | **Accepted.** Recorded in `ANALYSIS.md` as a second, independent way the read set can under-cover the basis. Not repaired here: changing `derive.py` mid-study would tune the artifact under test. |
| 13 | A test that cannot fail (`value <= of`) | Minor | **Accepted**, left as a shape check; the substantive assertions are the arm and input tests. |

## Attacks that did not hold up

Recorded because a review that only confirms is not a review:

- **Preregistration ordering.** Sound. `dac8d56` contains only `PREREGISTRATION.md` and `README.md`;
  the harness first appears in the results commit.
- **Rule tuned mid-run.** No evidence. The rule and `derive.py` each have exactly one commit,
  predating the preregistration, and their on-disk digests match the freeze.
- **Verifier edited.** Unchanged; the runtime monkeypatch touches only `runtime_binary` and
  `screening_pack`, which `verify_candidate` never calls.
- **Probe illegitimacy.** The probe is sound. Arm B is admitted with zero errors on the *same*
  constructed store, which exercises every receipt, attestation, binding, subject and artifact check,
  so Arm C's single error is attributable to the basis alone.
- **D3 is a restatement of D1.** Not quite: D1 requires ⊇, D3 requires =. D3 adds the "no extra
  pointers" direction and is the only endpoint with independent content.

## Remaining independent-review requirement

Everything above is this project reviewing its own work. The rule, the verifier, the study and this
review share one author. Independent validation would mean a third party running the clean-room Go
implementation against these 24 cells and against a corpus that exercises the basis divergence. That
has not been done and is not claimed.
