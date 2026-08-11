# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5980 of 5980; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `oryx-sanctions-precedence` | accepted: sanctioned, IR, personal=true, score "88.5", outcome reject |
| 2 | `paektu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `caspian-embargo-high-risk` | accepted: unsanctioned, IR, personal=true, score "70", outcome reject |
| 4 | `levant-embargo-mid-risk` | accepted: unsanctioned, SY, personal=true, score "40", outcome reject |
| 5 | `summit-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `redwood-high-risk-data` | accepted: unsanctioned, US, personal=true, score "92.75", outcome manual-review |
| 7 | `atlas-maximum-risk` | accepted: unsanctioned, AU, personal=false, score "100", outcome manual-review |
| 8 | `bluebell-data-threshold` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `cedar-data-upper-bound` | accepted: unsanctioned, FR, personal=true, score "69.999", outcome manual-review |
| 10 | `fjord-data-midrange` | accepted: unsanctioned, NO, personal=true, score "55.4", outcome manual-review |
| 11 | `maple-zero-risk` | accepted: unsanctioned, CA, personal=false, score "0", outcome clear |
| 12 | `lotus-data-below-threshold` | accepted: unsanctioned, SG, personal=true, score "39.999", outcome clear |
| 13 | `pampas-nondata-mid-risk` | accepted: unsanctioned, AR, personal=false, score "40", outcome clear |
| 14 | `alpine-nondata-upper-bound` | accepted: unsanctioned, CH, personal=false, score "69.999", outcome clear |
| 15 | `sakura-low-risk-data` | accepted: unsanctioned, JP, personal=true, score "18.25", outcome clear |
