# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5989 of 5989; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "8.5", outcome reject |
| 1 | `redwood-sanctions-embargoed` | accepted: sanctioned, IR, personal=true, score "92", outcome reject |
| 2 | `choson-industrial-registration` | accepted: unsanctioned, KP, personal=false, score "12", outcome reject |
| 3 | `persia-cloud-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-analytics-registration` | accepted: unsanctioned, SY, personal=true, score "75", outcome reject |
| 5 | `atlas-exact-high-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `cedar-high-risk-data-processor` | accepted: unsanctioned, US, personal=true, score "88.4", outcome manual-review |
| 7 | `harbor-high-risk-no-data` | accepted: unsanctioned, SG, personal=false, score "70.01", outcome manual-review |
| 8 | `maple-exact-data-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `lotus-data-upper-border` | accepted: unsanctioned, TH, personal=true, score "69.99", outcome manual-review |
| 10 | `alpine-data-midrange-risk` | accepted: unsanctioned, CH, personal=true, score "55.5", outcome manual-review |
| 11 | `seabrook-data-below-threshold` | accepted: unsanctioned, AU, personal=true, score "39.99", outcome clear |
| 12 | `fjord-zero-risk-data` | accepted: unsanctioned, NO, personal=true, score "0", outcome clear |
| 13 | `cobalt-no-data-midrange` | accepted: unsanctioned, PL, personal=false, score "40", outcome clear |
| 14 | `solstice-no-data-upper-border` | accepted: unsanctioned, ES, personal=false, score "69.999", outcome clear |
| 15 | `sakura-low-risk-data` | accepted: unsanctioned, JP, personal=true, score "18.25", outcome clear |
