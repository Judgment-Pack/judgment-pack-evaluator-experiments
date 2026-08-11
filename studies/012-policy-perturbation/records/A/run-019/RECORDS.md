# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6042 of 6042; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "91.5", outcome reject |
| 2 | `baekdu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "8.25", outcome reject |
| 3 | `persia-embargo-low-risk` | accepted: unsanctioned, IR, personal=false, score "0", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "100", outcome reject |
| 5 | `atlas-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `harbor-high-risk-data` | accepted: unsanctioned, SG, personal=true, score "70.01", outcome manual-review |
| 7 | `summit-maximum-risk` | accepted: unsanctioned, AU, personal=false, score "100", outcome manual-review |
| 8 | `cedar-personal-data-threshold` | accepted: unsanctioned, US, personal=true, score "40", outcome manual-review |
| 9 | `sakura-personal-data-midrange` | accepted: unsanctioned, JP, personal=true, score "55.5", outcome manual-review |
| 10 | `fjord-personal-data-upper-edge` | accepted: unsanctioned, NO, personal=true, score "69.99", outcome manual-review |
| 11 | `maple-personal-data-below-threshold` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 12 | `alpine-personal-data-zero-risk` | accepted: unsanctioned, CH, personal=true, score "0", outcome clear |
| 13 | `tulip-nondata-forty` | accepted: unsanctioned, NL, personal=false, score "40", outcome clear |
| 14 | `andean-nondata-upper-edge` | accepted: unsanctioned, CL, personal=false, score "69.999", outcome clear |
| 15 | `baltic-low-risk-supplier` | accepted: unsanctioned, EE, personal=false, score "18.75", outcome clear |
