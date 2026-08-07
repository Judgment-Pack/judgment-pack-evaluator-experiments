# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5958 of 5958; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `redwood-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `paektu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `damascus-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "92.4", outcome reject |
| 4 | `tehran-embargo-threshold` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `northstar-risk-seventy` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `cedar-high-risk-data` | accepted: unsanctioned, US, personal=true, score "84.25", outcome manual-review |
| 7 | `atlas-risk-seventy-decimal` | accepted: unsanctioned, FR, personal=false, score "70.01", outcome manual-review |
| 8 | `harbor-data-risk-forty` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `maple-data-below-seventy` | accepted: unsanctioned, CA, personal=true, score "69.99", outcome manual-review |
| 10 | `sakura-data-mid-risk` | accepted: unsanctioned, JP, personal=true, score "55.5", outcome manual-review |
| 11 | `alpine-no-data-below-seventy` | accepted: unsanctioned, CH, personal=false, score "69.99", outcome clear |
| 12 | `coral-no-data-risk-forty` | accepted: unsanctioned, AU, personal=false, score "40", outcome clear |
| 13 | `fjord-data-below-forty` | accepted: unsanctioned, NO, personal=true, score "39.99", outcome clear |
| 14 | `lotus-data-zero-risk` | accepted: unsanctioned, SG, personal=true, score "0", outcome clear |
| 15 | `andes-no-data-mid-risk` | accepted: unsanctioned, CL, personal=false, score "58.75", outcome clear |
