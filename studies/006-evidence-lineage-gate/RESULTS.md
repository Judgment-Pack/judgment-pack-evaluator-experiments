# Results — Study 006

## Outcome

The deterministic lineage gate passed all four registered Phase A endpoints. Phase B terminated
before treatment after the one allowed infrastructure rerun, so the model endpoints and usability
prediction are not estimable.

## Phase A — deterministic enforcement

| Endpoint | Result | Outcome |
|---|---:|---|
| D1 unsafe acceptance under syntax trust | 8/8 attacks accepted | predicted |
| D1 unsafe acceptance under verified lineage | 0/8 attacks accepted | pass |
| D2 registered attack link localized | 8/8 | pass |
| D3 valid control accepted and evaluated `clear` | both policies | pass |
| D4 admitted evaluator input/output integrity | 2/2 | pass |

The two D4 cases are the unmodified control and A08 before its registered post-evaluation output
mutation. In each, the real runtime received JSON-equal facts and evidence from the verified
envelope, and its exact portable disposition matched the evaluation receipt.

## Phase B — model authoring

The first `r01-s01` launch was rejected with HTTP 400 `invalid_json_schema` because a string
`const` lacked an explicit `type`. The allowed rerun was rejected with HTTP 400 because
`uniqueItems` is not permitted by the hosted strict-output schema subset.

Both failures occurred before inference or MCP discovery:

- model cells completed: **0/24**;
- prompts or synthetic MCP payloads received by a model: **0**;
- M1–M5: **not estimable**;
- registered M2 prediction: **not estimable**, neither hit nor miss.

The second rejection exhausted the preregistered rerun allowance. No third attempt was made.

## Interpretation

Within its synthetic trust boundary, the implementation blocked all registered mutations between
the acquired artifact, prepared facts/evidence, evaluator input, and downstream disposition. It
does not prove that a real OFAC source is truthful or authoritative, and it does not establish that
an AI agent can reliably author the required envelope. Those are separate claims.
