# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5979 of 5979; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `tigris-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "100", outcome reject |
| 2 | `paektu-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `damascus-embargo-data` | accepted: unsanctioned, SY, personal=true, score "39.99", outcome reject |
| 4 | `persis-embargo-high-risk` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `redwood-review-threshold` | accepted: unsanctioned, US, personal=false, score "70", outcome manual-review |
| 6 | `alpine-above-review-threshold` | accepted: unsanctioned, CH, personal=false, score "70.01", outcome manual-review |
| 7 | `meridian-maximum-risk` | accepted: unsanctioned, AU, personal=true, score "100", outcome manual-review |
| 8 | `harbor-personal-threshold` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `sakura-personal-midband` | accepted: unsanctioned, JP, personal=true, score "55.5", outcome manual-review |
| 10 | `baltic-personal-below-review` | accepted: unsanctioned, EE, personal=true, score "69.99", outcome manual-review |
| 11 | `maple-below-personal-threshold` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 12 | `fjord-zero-risk-data` | accepted: unsanctioned, NO, personal=true, score "0", outcome clear |
| 13 | `andes-nondata-personal-threshold` | accepted: unsanctioned, CL, personal=false, score "40", outcome clear |
| 14 | `lotus-nondata-below-review` | accepted: unsanctioned, SG, personal=false, score "69.99", outcome clear |
| 15 | `rhine-low-risk-supplier` | accepted: unsanctioned, DE, personal=false, score "18.25", outcome clear |
