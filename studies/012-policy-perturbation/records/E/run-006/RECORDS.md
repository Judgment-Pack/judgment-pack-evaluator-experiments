# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6031 of 6031; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `helios-sanctions-high-risk` | accepted: sanctioned, DE, personal=true, score "88.5", outcome reject |
| 2 | `chollima-embargoed-registration` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `pars-embargoed-review-boundary` | accepted: unsanctioned, IR, personal=true, score "70", outcome reject |
| 4 | `levant-embargoed-high-risk` | accepted: unsanctioned, SY, personal=true, score "100", outcome reject |
| 5 | `maple-review-threshold` | accepted: unsanctioned, CA, personal=false, score "70", outcome manual-review |
| 6 | `fjord-above-review-threshold` | accepted: unsanctioned, NO, personal=false, score "70.01", outcome manual-review |
| 7 | `sakura-high-risk-data-handler` | accepted: unsanctioned, JP, personal=true, score "92.75", outcome manual-review |
| 8 | `andes-data-threshold` | accepted: unsanctioned, CL, personal=true, score "40", outcome manual-review |
| 9 | `cedar-data-midband` | accepted: unsanctioned, GB, personal=true, score "55.4", outcome manual-review |
| 10 | `coral-data-below-review` | accepted: unsanctioned, AU, personal=true, score "69.999", outcome manual-review |
| 11 | `tulip-data-below-personal-threshold` | accepted: unsanctioned, NL, personal=true, score "39.999", outcome clear |
| 12 | `alpine-zero-risk-data-handler` | accepted: unsanctioned, CH, personal=true, score "0", outcome clear |
| 13 | `baltic-nondata-personal-threshold` | accepted: unsanctioned, EE, personal=false, score "40", outcome clear |
| 14 | `savanna-nondata-below-review` | accepted: unsanctioned, KE, personal=false, score "69.999", outcome clear |
| 15 | `pacific-routine-low-risk` | accepted: unsanctioned, SG, personal=false, score "27.5", outcome clear |
