# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6014 of 6014; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "85", outcome reject |
| 2 | `baekdu-embargo-zero-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `levant-embargo-mid-risk` | accepted: unsanctioned, SY, personal=true, score "55.5", outcome reject |
| 4 | `tehran-embargo-high-risk` | accepted: unsanctioned, IR, personal=false, score "100", outcome reject |
| 5 | `maple-data-below-threshold` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 6 | `rhine-data-at-forty` | accepted: unsanctioned, DE, personal=true, score "40", outcome manual-review |
| 7 | `sakura-data-mid-band` | accepted: unsanctioned, JP, personal=true, score "58.25", outcome manual-review |
| 8 | `andes-data-below-seventy` | accepted: unsanctioned, CL, personal=true, score "69.99", outcome manual-review |
| 9 | `harbor-nondata-at-forty` | accepted: unsanctioned, AU, personal=false, score "40", outcome clear |
| 10 | `alpine-nondata-mid-band` | accepted: unsanctioned, CH, personal=false, score "56.75", outcome clear |
| 11 | `baltic-nondata-below-seventy` | accepted: unsanctioned, EE, personal=false, score "69.999", outcome clear |
| 12 | `nile-nondata-at-seventy` | accepted: unsanctioned, EG, personal=false, score "70", outcome manual-review |
| 13 | `cedar-data-at-seventy` | accepted: unsanctioned, LB, personal=true, score "70", outcome manual-review |
| 14 | `fjord-high-risk-nondata` | accepted: unsanctioned, NO, personal=false, score "88.4", outcome manual-review |
| 15 | `savanna-high-risk-data` | accepted: unsanctioned, KE, personal=true, score "100", outcome manual-review |
