# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6043 of 6043; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-high-risk` | accepted: sanctioned, GB, personal=true, score "92.5", outcome reject |
| 1 | `cedar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "8.25", outcome reject |
| 2 | `paektu-embargoed-registration` | accepted: unsanctioned, KP, personal=false, score "12", outcome reject |
| 3 | `persian-orchid-embargoed-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-systems-embargoed-high-risk` | accepted: unsanctioned, SY, personal=true, score "87", outcome reject |
| 5 | `summit-exactly-seventy` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `blue-harbor-high-risk-data` | accepted: unsanctioned, FR, personal=true, score "70.001", outcome manual-review |
| 7 | `ironwood-high-risk-no-data` | accepted: unsanctioned, AU, personal=false, score "96.75", outcome manual-review |
| 8 | `silverline-data-exactly-forty` | accepted: unsanctioned, NL, personal=true, score "40", outcome manual-review |
| 9 | `maplebridge-data-midrange` | accepted: unsanctioned, CA, personal=true, score "55.4", outcome manual-review |
| 10 | `sakura-data-below-seventy` | accepted: unsanctioned, JP, personal=true, score "69.999", outcome manual-review |
| 11 | `fjord-data-just-below-forty` | accepted: unsanctioned, NO, personal=true, score "39.999", outcome clear |
| 12 | `alpine-data-zero-risk` | accepted: unsanctioned, CH, personal=true, score "0", outcome clear |
| 13 | `copperfield-no-data-exactly-forty` | accepted: unsanctioned, PL, personal=false, score "40", outcome clear |
| 14 | `solstice-no-data-below-seventy` | accepted: unsanctioned, ES, personal=false, score "69.999", outcome clear |
| 15 | `acacia-no-data-moderate-risk` | accepted: unsanctioned, KE, personal=false, score "52.625", outcome clear |
