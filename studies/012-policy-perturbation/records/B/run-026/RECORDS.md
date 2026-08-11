# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5975 of 5975; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `taedong-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `persis-embargo-borderline` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "70", outcome reject |
| 5 | `atlas-seventy-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `meridian-high-risk-data` | accepted: unsanctioned, SG, personal=true, score "84.25", outcome manual-review |
| 7 | `summit-maximum-risk` | accepted: unsanctioned, US, personal=false, score "100", outcome manual-review |
| 8 | `harbor-data-forty-threshold` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `cedar-data-midrange` | accepted: unsanctioned, FR, personal=true, score "55.5", outcome manual-review |
| 10 | `pacific-data-below-seventy` | accepted: unsanctioned, AU, personal=true, score "69.99", outcome manual-review |
| 11 | `maple-data-below-forty` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 12 | `sakura-data-zero-risk` | accepted: unsanctioned, JP, personal=true, score "0", outcome clear |
| 13 | `alpine-no-data-forty` | accepted: unsanctioned, CH, personal=false, score "40", outcome clear |
| 14 | `baltic-no-data-below-seventy` | accepted: unsanctioned, EE, personal=false, score "69.99", outcome clear |
| 15 | `andean-no-data-low-risk` | accepted: unsanctioned, CL, personal=false, score "18.75", outcome clear |
