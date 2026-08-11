# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6012 of 6012; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-override` | accepted: sanctioned, IR, personal=true, score "100", outcome reject |
| 2 | `daedong-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `persis-embargo-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-embargo-registration` | accepted: unsanctioned, SY, personal=true, score "70", outcome reject |
| 5 | `maple-zero-risk` | accepted: unsanctioned, CA, personal=false, score "0", outcome clear |
| 6 | `fjord-personal-data-below-forty` | accepted: unsanctioned, NO, personal=true, score "39.99", outcome clear |
| 7 | `sakura-personal-data-at-forty` | accepted: unsanctioned, JP, personal=true, score "40", outcome manual-review |
| 8 | `alpine-personal-data-midrange` | accepted: unsanctioned, CH, personal=true, score "55.5", outcome manual-review |
| 9 | `baltic-personal-data-below-seventy` | accepted: unsanctioned, EE, personal=true, score "69.99", outcome manual-review |
| 10 | `andes-nonpersonal-at-forty` | accepted: unsanctioned, CL, personal=false, score "40", outcome clear |
| 11 | `rhine-nonpersonal-below-seventy` | accepted: unsanctioned, DE, personal=false, score "69.99", outcome clear |
| 12 | `acacia-nonpersonal-at-seventy` | accepted: unsanctioned, AU, personal=false, score "70", outcome manual-review |
| 13 | `atlas-personal-data-at-seventy` | accepted: unsanctioned, FR, personal=true, score "70", outcome manual-review |
| 14 | `savanna-high-risk` | accepted: unsanctioned, KE, personal=false, score "87.25", outcome manual-review |
| 15 | `emerald-maximum-risk` | accepted: unsanctioned, IE, personal=true, score "100", outcome manual-review |
