# Run log — Study 006

- preregistration commit: `7790cb4`
- preregistration SHA-256: `sha256:a6d39674b4ad65e2a21eee666565731ef9d08a63082d0821c616f03aacacf134`
- runner version: `1`
- model: `gpt-5.6-terra`
- reasoning effort: `low`
- client: `codex-cli 0.145.0`
- Python: `3.8.20 (default, Jun 12 2025, 17:51:52)  [GCC 9.4.0]`

## Repository baselines

- experiment: `7790cb4114c04d6e6a3ccd303b18a3c6939f1aca`
- spec: `b3db68eae470ccb401362b3dc549192c10b86158`
- runtime: `bdf4b16159265fedd582bdcb2aeda18ec9ac7a3d`
- demo: `3069ab8f5b11127d267b0f23df989f8533d0ca5d`

## Artifact SHA-256

- `PREREGISTRATION.md`: `sha256:a6d39674b4ad65e2a21eee666565731ef9d08a63082d0821c616f03aacacf134`
- `fixtures/cases.json`: `sha256:80edea6f51f957c451863ea92d5296670ab5f3d449521468e9d6f253c8f3ed0c`
- `fixtures/binding-lock.json`: `sha256:55a3d791ee48f8c2a4d5f57de40a80e6f694600017f0dacd29afd2e53fb2598c`
- `fixtures/gateway.key`: `sha256:9019844959035cee4d662881ba6fb90d9f273bbc912a39d6eb66e30a0ab71143`
- `fixtures/PROMPT.txt`: `sha256:3457bc4eebdc016ad28e09488a99c4f2b41b9064d24614e5ae63ac5dcaf9faaf`
- `schema/candidate.schema.json`: `sha256:d0dd95c0da10d933a2f4584ce3c1cd3398521ed9c2bcebf4e62e9bf28c5bfc26`
- `schema/binding-lock.schema.json`: `sha256:4846afc9994e51da0a54ac16503d3cfaf69ffcd16917ab5977ec47293d6b7b20`
- `harness/common.py`: `sha256:5b540d15feb46bc46363362fbf4750db93117a7fb837fa4e2912a626bc71b6fd`
- `harness/acquisition_gateway.py`: `sha256:638ddf1eee88b2b53d25fa7988d79c281f82b44cde01aa3b9a5d67913d4a50a4`
- `harness/study.py`: `sha256:18be4575b09ce3d06886047dca02645fc7161e63bd657873824a072ff8cbb159`
- `/home/onword/repo/judgment-pack/judgment-pack-runtime/bin/judgment-pack`: `sha256:b8cfe3a99ad683c0df9de0bc8d79fafdeea3f6cee639b143f46dc3a92827776d`
- `/home/onword/repo/judgment-pack/judgment-pack-demo/projects/enterprise-demo/packs/sanctions-screening.pack.json`: `sha256:d587abe5c247fbcf0b890222792eadb18b22837d9555dbd1ef1fd15d015a4ea0`

## Fixed model trial order

| # | cell | repetition | scenario |
|---:|---|---:|---|
| 1 | `r01-s01` | 1 | S01 |
| 2 | `r01-s02` | 1 | S02 |
| 3 | `r01-s03` | 1 | S03 |
| 4 | `r01-s04` | 1 | S04 |
| 5 | `r01-s05` | 1 | S05 |
| 6 | `r01-s06` | 1 | S06 |
| 7 | `r01-s07` | 1 | S07 |
| 8 | `r01-s08` | 1 | S08 |
| 9 | `r02-s01` | 2 | S01 |
| 10 | `r02-s02` | 2 | S02 |
| 11 | `r02-s03` | 2 | S03 |
| 12 | `r02-s04` | 2 | S04 |
| 13 | `r02-s05` | 2 | S05 |
| 14 | `r02-s06` | 2 | S06 |
| 15 | `r02-s07` | 2 | S07 |
| 16 | `r02-s08` | 2 | S08 |
| 17 | `r03-s01` | 3 | S01 |
| 18 | `r03-s02` | 3 | S02 |
| 19 | `r03-s03` | 3 | S03 |
| 20 | `r03-s04` | 3 | S04 |
| 21 | `r03-s05` | 3 | S05 |
| 22 | `r03-s06` | 3 | S06 |
| 23 | `r03-s07` | 3 | S07 |
| 24 | `r03-s08` | 3 | S08 |

## Post-Phase-A reporting repair

D1–D3 were not rerun. The separate D4 audit reads retained Phase A artifacts as recorded in
`DEVIATIONS.md`.

- pre-Phase-A runner SHA-256:
  `sha256:18be4575b09ce3d06886047dca02645fc7161e63bd657873824a072ff8cbb159`
- model-run/scorer runner SHA-256 after D4 reporting repair:
  `sha256:bc555b3dc2f1a5e868a8d8c6d72a964de972bc53510bdc81c883a13446cdaaeb`
- original D1–D3 JSON SHA-256:
  `sha256:780809c997518e37a75e1cac10da8b68147b8f37b128405c61a009885b8fe496`
- separate D4 audit JSON SHA-256:
  `sha256:4ec9e0208d2a07912726e1aa5f877bf05e870d03aa5a5764b005687f53494fcc`

## Phase-B pre-treatment schema repair

The retained first `r01-s01` attempt was rejected before inference or MCP discovery as recorded in
`DEVIATIONS.md`.

- original candidate-schema SHA-256:
  `sha256:d0dd95c0da10d933a2f4584ce3c1cd3398521ed9c2bcebf4e62e9bf28c5bfc26`
- explicit-string-type candidate-schema SHA-256 used for the allowed rerun:
  `sha256:ac94113119b79fb8ffbe0d1786bea9e453bc536cd3bbb7e5f43b8580cd1fb3a3`

## Phase-B termination

The one allowed rerun was rejected before inference or MCP discovery because the hosted strict
schema subset does not permit `uniqueItems`. No third launch was made. No model cell completed and
M1–M5 are not estimable.

- attempt 1 marker:
  `sha256:67840576c64995f0cb38b94446e76d6860983224cf340a141b27104d8fdae75f`
- attempt 1 events:
  `sha256:606096993a0d2bb4e9affbc82d96397fb90b4cbf307c89e78ee2bcd34b38f794`
- attempt 1 stderr:
  `sha256:6c535592cccb63e2b481fee7ca1ed970797dcd5ce27c0dbeac998e186c074d08`
- attempt 2 marker:
  `sha256:476d1629b6bf5519b7282c6540da9e36f7ed71ba198292357412aa853da14af3`
- attempt 2 events:
  `sha256:23f9ae673d76b0be9d7278b3baaaabfa75339204a2fb704375ffb5fbdc1a9bbb`
- attempt 2 stderr:
  `sha256:5f964eb2335413f329205b209246c120e39292202d9bf5864920d0e9491537a6`
