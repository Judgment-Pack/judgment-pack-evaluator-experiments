# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5952 of 5952; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-sanctions-precedence` | accepted: sanctioned, IR, personal=true, score "100", outcome reject |
| 2 | `choson-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `pars-embargo-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-embargo-precedence` | accepted: unsanctioned, SY, personal=true, score "85.4", outcome reject |
| 5 | `alpine-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `iberia-high-risk-data` | accepted: unsanctioned, ES, personal=true, score "70.01", outcome manual-review |
| 7 | `pacific-maximum-risk` | accepted: unsanctioned, AU, personal=false, score "100", outcome manual-review |
| 8 | `maple-data-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `tulip-data-midrange` | accepted: unsanctioned, NL, personal=true, score "55.5", outcome manual-review |
| 10 | `sakura-data-upper-bound` | accepted: unsanctioned, JP, personal=true, score "69.99", outcome manual-review |
| 11 | `fjord-zero-risk` | accepted: unsanctioned, NO, personal=false, score "0", outcome clear |
| 12 | `cedar-data-below-threshold` | accepted: unsanctioned, NZ, personal=true, score "39.99", outcome clear |
| 13 | `baltic-no-data-forty` | accepted: unsanctioned, EE, personal=false, score "40", outcome clear |
| 14 | `andes-no-data-upper-bound` | accepted: unsanctioned, CL, personal=false, score "69.99", outcome clear |
| 15 | `atlas-low-risk-data` | accepted: unsanctioned, MA, personal=true, score "12.375", outcome clear |
