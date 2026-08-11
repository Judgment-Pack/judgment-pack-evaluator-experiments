# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6016 of 6016; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `caspian-sanctions-override` | accepted: sanctioned, IR, personal=true, score "88.5", outcome reject |
| 2 | `taedong-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "3", outcome reject |
| 3 | `persia-embargo-registration` | accepted: unsanctioned, IR, personal=true, score "44.99", outcome reject |
| 4 | `levant-embargo-registration` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 5 | `atlas-threshold-seventy-two` | accepted: unsanctioned, DE, personal=false, score "72", outcome manual-review |
| 6 | `sakura-high-risk-data` | accepted: unsanctioned, JP, personal=true, score "92.4", outcome manual-review |
| 7 | `andean-high-risk-logistics` | accepted: unsanctioned, CL, personal=false, score "72.01", outcome manual-review |
| 8 | `maple-data-threshold-forty-five` | accepted: unsanctioned, CA, personal=true, score "45", outcome manual-review |
| 9 | `baltic-data-midrange` | accepted: unsanctioned, EE, personal=true, score "58.25", outcome manual-review |
| 10 | `kiwi-data-below-seventy-two` | accepted: unsanctioned, NZ, personal=true, score "71.99", outcome manual-review |
| 11 | `alpine-data-below-forty-five` | accepted: unsanctioned, CH, personal=true, score "44.99", outcome clear |
| 12 | `iberian-data-zero-risk` | accepted: unsanctioned, ES, personal=true, score "0", outcome clear |
| 13 | `nordic-nondata-near-threshold` | accepted: unsanctioned, SE, personal=false, score "71.99", outcome clear |
| 14 | `savanna-nondata-at-forty-five` | accepted: unsanctioned, KE, personal=false, score "45", outcome clear |
| 15 | `pacific-low-risk-supply` | accepted: unsanctioned, AU, personal=false, score "18.7", outcome clear |
