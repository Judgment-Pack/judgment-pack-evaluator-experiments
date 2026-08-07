# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6038 of 6038; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-precedence` | accepted: sanctioned, IR, personal=true, score "88.4", outcome reject |
| 2 | `paektu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "8", outcome reject |
| 3 | `zagros-embargo-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "94.75", outcome reject |
| 5 | `alpine-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `blueharbor-high-risk-data` | accepted: unsanctioned, AU, personal=true, score "70.01", outcome manual-review |
| 7 | `iberian-high-risk-logistics` | accepted: unsanctioned, ES, personal=false, score "86.3", outcome manual-review |
| 8 | `cedar-personal-data-threshold` | accepted: unsanctioned, US, personal=true, score "40", outcome manual-review |
| 9 | `sakura-personal-data-midrisk` | accepted: unsanctioned, JP, personal=true, score "55.6", outcome manual-review |
| 10 | `tulip-personal-data-upper-edge` | accepted: unsanctioned, NL, personal=true, score "69.999", outcome manual-review |
| 11 | `maple-data-below-threshold` | accepted: unsanctioned, CA, personal=true, score "39.999", outcome clear |
| 12 | `baltic-nondata-at-forty` | accepted: unsanctioned, EE, personal=false, score "40", outcome clear |
| 13 | `andes-nondata-upper-edge` | accepted: unsanctioned, CL, personal=false, score "69.999", outcome clear |
| 14 | `fjord-low-risk-data` | accepted: unsanctioned, NO, personal=true, score "0.25", outcome clear |
| 15 | `savanna-low-risk-supply` | accepted: unsanctioned, KE, personal=false, score "18.7", outcome clear |
