# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5969 of 5969; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `cedar-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `paektu-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `damascus-embargo-data` | accepted: unsanctioned, SY, personal=true, score "44.99", outcome reject |
| 4 | `tehran-embargo-high-risk` | accepted: unsanctioned, IR, personal=false, score "100", outcome reject |
| 5 | `alpine-exact-high-threshold` | accepted: unsanctioned, CH, personal=false, score "72", outcome manual-review |
| 6 | `harbor-above-high-threshold` | accepted: unsanctioned, AU, personal=true, score "72.01", outcome manual-review |
| 7 | `baltic-maximum-risk` | accepted: unsanctioned, EE, personal=false, score "100", outcome manual-review |
| 8 | `maple-exact-data-threshold` | accepted: unsanctioned, CA, personal=true, score "45", outcome manual-review |
| 9 | `rhine-data-upper-edge` | accepted: unsanctioned, DE, personal=true, score "71.999", outcome manual-review |
| 10 | `sakura-data-midrange` | accepted: unsanctioned, JP, personal=true, score "58.4", outcome manual-review |
| 11 | `linden-data-below-threshold` | accepted: unsanctioned, NL, personal=true, score "44.999", outcome clear |
| 12 | `fjord-data-zero-risk` | accepted: unsanctioned, NO, personal=true, score "0", outcome clear |
| 13 | `atlas-no-data-upper-edge` | accepted: unsanctioned, FR, personal=false, score "71.999", outcome clear |
| 14 | `savanna-no-data-midrange` | accepted: unsanctioned, KE, personal=false, score "45", outcome clear |
| 15 | `pacific-low-risk-clear` | accepted: unsanctioned, SG, personal=false, score "23.75", outcome clear |
