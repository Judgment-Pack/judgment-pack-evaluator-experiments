# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5946 of 5946; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-precedence` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo-overlap` | accepted: sanctioned, IR, personal=true, score "85", outcome reject |
| 2 | `paektu-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "3", outcome reject |
| 3 | `levant-embargo-data-services` | accepted: unsanctioned, SY, personal=true, score "39.999", outcome reject |
| 4 | `tehran-embargo-high-risk` | accepted: unsanctioned, IR, personal=false, score "92.75", outcome reject |
| 5 | `alpine-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `baltic-high-risk-data` | accepted: unsanctioned, EE, personal=true, score "70.001", outcome manual-review |
| 7 | `andes-high-risk-nondata` | accepted: unsanctioned, CL, personal=false, score "88.4", outcome manual-review |
| 8 | `maple-data-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `rhine-data-upper-border` | accepted: unsanctioned, DE, personal=true, score "69.999", outcome manual-review |
| 10 | `sakura-data-midrange` | accepted: unsanctioned, JP, personal=true, score "55.25", outcome manual-review |
| 11 | `harbor-nondata-upper-border` | accepted: unsanctioned, AU, personal=false, score "69.999", outcome clear |
| 12 | `cedar-nondata-forty` | accepted: unsanctioned, LB, personal=false, score "40", outcome clear |
| 13 | `tulip-data-below-threshold` | accepted: unsanctioned, NL, personal=true, score "39.999", outcome clear |
| 14 | `savanna-data-zero-risk` | accepted: unsanctioned, KE, personal=true, score "0", outcome clear |
| 15 | `fjord-low-risk-nondata` | accepted: unsanctioned, NO, personal=false, score "18.75", outcome clear |
