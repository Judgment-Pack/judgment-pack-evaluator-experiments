# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5996 of 5996; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "85", outcome reject |
| 2 | `pyongyang-low-risk-embargo` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `damascus-analytics-embargo` | accepted: unsanctioned, SY, personal=true, score "40", outcome reject |
| 4 | `tehran-logistics-embargo` | accepted: unsanctioned, IR, personal=false, score "100", outcome reject |
| 5 | `maple-data-below-threshold` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 6 | `rhein-privacy-lower-bound` | accepted: unsanctioned, DE, personal=true, score "40", outcome manual-review |
| 7 | `sakura-midrange-personal-data` | accepted: unsanctioned, JP, personal=true, score "55.5", outcome manual-review |
| 8 | `andean-privacy-upper-edge` | accepted: unsanctioned, CL, personal=true, score "69.99", outcome manual-review |
| 9 | `alpine-zero-risk-clearance` | accepted: unsanctioned, CH, personal=false, score "0", outcome clear |
| 10 | `baltic-nonpersonal-midrange` | accepted: unsanctioned, EE, personal=false, score "40", outcome clear |
| 11 | `kiwi-nonpersonal-upper-edge` | accepted: unsanctioned, NZ, personal=false, score "69.99", outcome clear |
| 12 | `iberian-risk-seventy` | accepted: unsanctioned, ES, personal=false, score "70", outcome manual-review |
| 13 | `nordic-data-risk-seventy` | accepted: unsanctioned, SE, personal=true, score "70", outcome manual-review |
| 14 | `savanna-high-risk-review` | accepted: unsanctioned, ZA, personal=false, score "87.25", outcome manual-review |
| 15 | `pacific-maximum-risk-review` | accepted: unsanctioned, AU, personal=true, score "100", outcome manual-review |
