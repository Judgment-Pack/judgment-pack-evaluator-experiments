# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5928 of 5928; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-sanctions-embargoed` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `baekdu-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "3", outcome reject |
| 3 | `parsa-embargo-threshold` | accepted: unsanctioned, IR, personal=true, score "40", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "97.25", outcome reject |
| 5 | `summit-exactly-seventy` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `harbor-above-seventy` | accepted: unsanctioned, AU, personal=true, score "70.01", outcome manual-review |
| 7 | `cedar-high-risk-no-data` | accepted: unsanctioned, FR, personal=false, score "84.6", outcome manual-review |
| 8 | `maple-data-exactly-forty` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `tulip-data-mid-band` | accepted: unsanctioned, NL, personal=true, score "55.75", outcome manual-review |
| 10 | `sakura-data-below-seventy` | accepted: unsanctioned, JP, personal=true, score "69.999", outcome manual-review |
| 11 | `fjord-data-below-forty` | accepted: unsanctioned, NO, personal=true, score "39.999", outcome clear |
| 12 | `alpine-data-zero-risk` | accepted: unsanctioned, CH, personal=true, score "0", outcome clear |
| 13 | `savanna-no-data-exactly-forty` | accepted: unsanctioned, KE, personal=false, score "40", outcome clear |
| 14 | `andes-no-data-mid-band` | accepted: unsanctioned, CL, personal=false, score "58.4", outcome clear |
| 15 | `baltic-no-data-below-seventy` | accepted: unsanctioned, EE, personal=false, score "69.999", outcome clear |
