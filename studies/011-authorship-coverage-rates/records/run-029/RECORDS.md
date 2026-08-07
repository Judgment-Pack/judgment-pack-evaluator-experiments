# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5938 of 5938; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-priority` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-sanctions-embargo-overlap` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `oryx-sanctions-low-risk` | accepted: sanctioned, DE, personal=true, score "0", outcome reject |
| 3 | `paektu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "15", outcome reject |
| 4 | `caspian-embargo-low-risk` | accepted: unsanctioned, IR, personal=true, score "39.999", outcome reject |
| 5 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "70", outcome reject |
| 6 | `alpine-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 7 | `harbor-high-risk-data` | accepted: unsanctioned, SG, personal=true, score "70.001", outcome manual-review |
| 8 | `andes-maximum-risk` | accepted: unsanctioned, CL, personal=false, score "100", outcome manual-review |
| 9 | `cedar-data-threshold` | accepted: unsanctioned, US, personal=true, score "40", outcome manual-review |
| 10 | `tulip-data-upper-bound` | accepted: unsanctioned, NL, personal=true, score "69.999", outcome manual-review |
| 11 | `acacia-data-midrange` | accepted: unsanctioned, AU, personal=true, score "54.25", outcome manual-review |
| 12 | `maple-data-below-threshold` | accepted: unsanctioned, CA, personal=true, score "39.999", outcome clear |
| 13 | `sakura-data-zero-risk` | accepted: unsanctioned, JP, personal=true, score "0", outcome clear |
| 14 | `baltic-nondata-upper-bound` | accepted: unsanctioned, EE, personal=false, score "69.999", outcome clear |
| 15 | `atlas-nondata-threshold-forty` | accepted: unsanctioned, MA, personal=false, score "40", outcome clear |
