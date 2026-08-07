# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5958 of 5958; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `choson-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `persia-embargo-high-risk` | accepted: unsanctioned, IR, personal=true, score "92.75", outcome reject |
| 4 | `levant-embargo-threshold` | accepted: unsanctioned, SY, personal=false, score "70", outcome reject |
| 5 | `alpine-risk-seventy` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `baltic-high-risk-data` | accepted: unsanctioned, EE, personal=true, score "84.3", outcome manual-review |
| 7 | `andes-high-risk-nondata` | accepted: unsanctioned, CL, personal=false, score "99.99", outcome manual-review |
| 8 | `sakura-data-risk-forty` | accepted: unsanctioned, JP, personal=true, score "40", outcome manual-review |
| 9 | `iberia-data-upper-border` | accepted: unsanctioned, ES, personal=true, score "69.99", outcome manual-review |
| 10 | `savanna-data-midrange` | accepted: unsanctioned, KE, personal=true, score "55.5", outcome manual-review |
| 11 | `maple-data-below-forty` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 12 | `kiwi-data-zero-risk` | accepted: unsanctioned, NZ, personal=true, score "0", outcome clear |
| 13 | `rhine-nondata-risk-forty` | accepted: unsanctioned, DE, personal=false, score "40", outcome clear |
| 14 | `atlas-nondata-upper-border` | accepted: unsanctioned, MA, personal=false, score "69.999", outcome clear |
| 15 | `nordic-nondata-low-risk` | accepted: unsanctioned, SE, personal=false, score "18.25", outcome clear |
