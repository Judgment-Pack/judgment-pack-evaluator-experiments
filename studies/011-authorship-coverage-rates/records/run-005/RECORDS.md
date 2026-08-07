# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6034 of 6034; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargoed` | accepted: sanctioned, IR, personal=true, score "88.4", outcome reject |
| 2 | `baekdu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "8.2", outcome reject |
| 3 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "91.7", outcome reject |
| 4 | `tehran-embargo-boundary-risk` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `alpine-exact-seventy` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `harbor-high-risk-personal-data` | accepted: unsanctioned, SG, personal=true, score "84.25", outcome manual-review |
| 7 | `ironwood-high-risk-no-data` | accepted: unsanctioned, DE, personal=false, score "70.01", outcome manual-review |
| 8 | `bluebell-personal-data-at-forty` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `maple-personal-data-midrange` | accepted: unsanctioned, CA, personal=true, score "55.6", outcome manual-review |
| 10 | `sunrise-personal-data-below-seventy` | accepted: unsanctioned, JP, personal=true, score "69.99", outcome manual-review |
| 11 | `cedar-personal-data-below-forty` | accepted: unsanctioned, US, personal=true, score "39.99", outcome clear |
| 12 | `fjord-personal-data-low-risk` | accepted: unsanctioned, NO, personal=true, score "0", outcome clear |
| 13 | `outback-no-data-at-forty` | accepted: unsanctioned, AU, personal=false, score "40", outcome clear |
| 14 | `tulip-no-data-below-seventy` | accepted: unsanctioned, NL, personal=false, score "69.99", outcome clear |
| 15 | `andes-no-data-moderate-risk` | accepted: unsanctioned, CL, personal=false, score "52.75", outcome clear |
