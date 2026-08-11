# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5960 of 5960; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-sanctions-high-risk` | accepted: sanctioned, DE, personal=true, score "88", outcome reject |
| 2 | `taedong-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "8", outcome reject |
| 3 | `persia-cloud-embargo` | accepted: unsanctioned, IR, personal=true, score "35", outcome reject |
| 4 | `levant-systems-embargo` | accepted: unsanctioned, SY, personal=false, score "92.75", outcome reject |
| 5 | `summit-risk-threshold` | accepted: unsanctioned, US, personal=false, score "70", outcome manual-review |
| 6 | `alpine-high-risk-data` | accepted: unsanctioned, CH, personal=true, score "70.01", outcome manual-review |
| 7 | `harbor-maximum-risk` | accepted: unsanctioned, GB, personal=false, score "100", outcome manual-review |
| 8 | `cedar-data-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `blue-orchid-mid-risk` | accepted: unsanctioned, SG, personal=true, score "55.5", outcome manual-review |
| 10 | `maple-data-upper-bound` | accepted: unsanctioned, CA, personal=true, score "69.99", outcome manual-review |
| 11 | `fjord-no-data-upper-bound` | accepted: unsanctioned, NO, personal=false, score "69.99", outcome clear |
| 12 | `coral-no-data-mid-risk` | accepted: unsanctioned, AU, personal=false, score "40", outcome clear |
| 13 | `sakura-data-below-threshold` | accepted: unsanctioned, JP, personal=true, score "39.99", outcome clear |
| 14 | `tulip-data-zero-risk` | accepted: unsanctioned, NL, personal=true, score "0", outcome clear |
| 15 | `andes-low-risk-clearance` | accepted: unsanctioned, CL, personal=false, score "18.375", outcome clear |
