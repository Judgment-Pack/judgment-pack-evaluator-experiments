# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6003 of 6003; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-sanctions-precedence` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `taedong-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `persis-embargo-low-risk` | accepted: unsanctioned, IR, personal=false, score "0", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "100", outcome reject |
| 5 | `atlas-risk-seventy` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `solstice-high-risk-data` | accepted: unsanctioned, FR, personal=true, score "91.25", outcome manual-review |
| 7 | `harbor-risk-just-above-seventy` | accepted: unsanctioned, AU, personal=false, score "70.01", outcome manual-review |
| 8 | `cedar-data-risk-forty` | accepted: unsanctioned, US, personal=true, score "40", outcome manual-review |
| 9 | `fjord-data-midrange-risk` | accepted: unsanctioned, NO, personal=true, score "55.5", outcome manual-review |
| 10 | `maple-data-just-below-seventy` | accepted: unsanctioned, CA, personal=true, score "69.999", outcome manual-review |
| 11 | `orchid-data-just-below-forty` | accepted: unsanctioned, SG, personal=true, score "39.999", outcome clear |
| 12 | `alpine-data-zero-risk` | accepted: unsanctioned, CH, personal=true, score "0", outcome clear |
| 13 | `meridian-no-data-midrange` | accepted: unsanctioned, MX, personal=false, score "40", outcome clear |
| 14 | `baltic-no-data-just-below-seventy` | accepted: unsanctioned, EE, personal=false, score "69.999", outcome clear |
| 15 | `sakura-no-data-low-risk` | accepted: unsanctioned, JP, personal=false, score "18.75", outcome clear |
