# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6003 of 6003; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-match` | accepted: sanctioned, CA, personal=false, score "18.5", outcome reject |
| 1 | `caspian-sanctions-and-embargo` | accepted: sanctioned, IR, personal=true, score "92.4", outcome reject |
| 2 | `blue-harbor-sanctions-low-risk` | accepted: sanctioned, DE, personal=true, score "12", outcome reject |
| 3 | `pyongyang-industrial-registration` | accepted: unsanctioned, KP, personal=false, score "5.25", outcome reject |
| 4 | `tehran-data-systems` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 5 | `levant-risk-advisory` | accepted: unsanctioned, SY, personal=true, score "88", outcome reject |
| 6 | `alpine-threshold-review` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 7 | `pacific-high-risk-review` | accepted: unsanctioned, AU, personal=true, score "70.01", outcome manual-review |
| 8 | `baltic-extreme-risk-review` | accepted: unsanctioned, EE, personal=false, score "100", outcome manual-review |
| 9 | `maple-data-threshold-review` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 10 | `iberian-midrange-data-review` | accepted: unsanctioned, ES, personal=true, score "54.375", outcome manual-review |
| 11 | `sakura-upper-bound-review` | accepted: unsanctioned, JP, personal=true, score "69.99", outcome manual-review |
| 12 | `tulip-data-below-threshold` | accepted: unsanctioned, NL, personal=true, score "39.99", outcome clear |
| 13 | `andean-nondata-upper-bound` | accepted: unsanctioned, CL, personal=false, score "69.99", outcome clear |
| 14 | `savanna-nondata-midrange` | accepted: unsanctioned, KE, personal=false, score "40", outcome clear |
| 15 | `fjord-zero-risk-clearance` | accepted: unsanctioned, NO, personal=true, score "0", outcome clear |
