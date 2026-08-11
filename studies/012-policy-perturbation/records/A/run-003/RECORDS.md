# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6017 of 6017; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-match` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-precedence` | accepted: sanctioned, IR, personal=true, score "100", outcome reject |
| 2 | `cedar-sanctions-low-risk` | accepted: sanctioned, US, personal=false, score "0", outcome reject |
| 3 | `paektu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "8", outcome reject |
| 4 | `tehran-embargo-low-risk` | accepted: unsanctioned, IR, personal=true, score "39.999", outcome reject |
| 5 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "70", outcome reject |
| 6 | `alpine-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 7 | `baltic-high-risk-data` | accepted: unsanctioned, EE, personal=true, score "84.25", outcome manual-review |
| 8 | `atlas-maximum-risk` | accepted: unsanctioned, MA, personal=false, score "100", outcome manual-review |
| 9 | `harbor-personal-data-threshold` | accepted: unsanctioned, AU, personal=true, score "40", outcome manual-review |
| 10 | `maple-personal-data-midrange` | accepted: unsanctioned, CA, personal=true, score "55.5", outcome manual-review |
| 11 | `delta-personal-data-upper-edge` | accepted: unsanctioned, NL, personal=true, score "69.999", outcome manual-review |
| 12 | `sakura-zero-risk-clearance` | accepted: unsanctioned, JP, personal=false, score "0", outcome clear |
| 13 | `fjord-data-below-threshold` | accepted: unsanctioned, NO, personal=true, score "39.999", outcome clear |
| 14 | `savanna-nondata-forty` | accepted: unsanctioned, KE, personal=false, score "40", outcome clear |
| 15 | `andes-nondata-upper-edge` | accepted: unsanctioned, CL, personal=false, score "69.999", outcome clear |
