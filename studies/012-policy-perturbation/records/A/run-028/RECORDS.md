# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6011 of 6011; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `redwood-sanctions-embargo-override` | accepted: sanctioned, IR, personal=true, score "88.5", outcome reject |
| 2 | `baekdu-embargo-zero-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `persia-embargo-moderate-risk` | accepted: unsanctioned, IR, personal=true, score "45", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "92", outcome reject |
| 5 | `alpine-risk-seventy` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `harbor-high-risk-personal-data` | accepted: unsanctioned, AU, personal=true, score "70.01", outcome manual-review |
| 7 | `summit-maximum-risk` | accepted: unsanctioned, US, personal=false, score "100", outcome manual-review |
| 8 | `cedar-personal-data-forty` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `sakura-personal-data-midrange` | accepted: unsanctioned, JP, personal=true, score "55.5", outcome manual-review |
| 10 | `fjord-personal-data-below-seventy` | accepted: unsanctioned, NO, personal=true, score "69.99", outcome manual-review |
| 11 | `maple-personal-data-zero-risk` | accepted: unsanctioned, CA, personal=true, score "0", outcome clear |
| 12 | `tulip-personal-data-below-forty` | accepted: unsanctioned, NL, personal=true, score "39.99", outcome clear |
| 13 | `rhine-nonpersonal-forty` | accepted: unsanctioned, DE, personal=false, score "40", outcome clear |
| 14 | `andes-nonpersonal-below-seventy` | accepted: unsanctioned, CL, personal=false, score "69.99", outcome clear |
| 15 | `nile-nonpersonal-moderate-risk` | accepted: unsanctioned, EG, personal=false, score "58.25", outcome clear |
