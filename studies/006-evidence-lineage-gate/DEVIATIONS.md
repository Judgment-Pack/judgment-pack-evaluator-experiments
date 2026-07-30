# Deviations — Study 006

Deviations from [`PREREGISTRATION.md`](PREREGISTRATION.md) are recorded here as they occur,
never by editing the preregistration.

## Post-Phase-A reporting repair

1. The first deterministic tamper run reported D1–D3 but omitted the registered D4 summary even
   though it had retained the exact verified evaluator inputs, outputs, and receipts required to
   compute it. The original `TAMPER-RESULTS.json` and `TAMPER-RESULTS.md` are not rerun or changed.
   Before any model trial, a separate `audit-d4` command was added to read those retained artifacts
   and report D4 without changing attack semantics, expected stages, or D1–D3 scoring.

## Phase-B pre-treatment schema repair

2. The first Phase B launch (`r01-s01`) was rejected by the OpenAI API with HTTP 400
   `invalid_json_schema` before model inference or MCP discovery. The strict structured-output
   subset requires an explicit `type` beside string `const` constraints. The exact event and stderr
   logs are retained as infrastructure attempt 1. `type: string` was added beside the existing
   `const` values for fact-claim target, fact-claim JSON pointer, and evidence requirement id. This
   changes no representable candidate, fixture, prompt, verifier rule, endpoint, or expected result.
   The cell will use its single preregistered infrastructure rerun.

## Phase-B termination before treatment

3. The one allowed infrastructure rerun of `r01-s01` was also rejected by the OpenAI API with
   HTTP 400 `invalid_json_schema` before model inference or MCP discovery. The service's strict
   structured-output subset does not permit `uniqueItems`, which the candidate schema used for
   `lineage.evidenceClaim.basisPointers`. The exact event and stderr logs are retained as
   infrastructure attempt 2. No model received the prompt, tool catalog, or synthetic source
   payload in either attempt.

   The preregistration permits only one infrastructure rerun. Phase B is therefore terminated
   without a third launch, without changing the schema again, and without scoring M1–M5. The
   model-usability prediction is **not estimable**, rather than a hit or a miss. A corrected hosted
   model study requires a new frozen registration.
