# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6039 of 6039; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `cedar-sanctions-high-risk` | accepted: sanctioned, US, personal=true, score "92", outcome reject |
| 2 | `daedong-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "8", outcome reject |
| 3 | `persia-embargo-low-risk` | accepted: unsanctioned, IR, personal=true, score "2.75", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "88.4", outcome reject |
| 5 | `alpine-exact-seventy` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `boreal-above-seventy` | accepted: unsanctioned, FI, personal=true, score "70.01", outcome manual-review |
| 7 | `atlas-maximum-risk` | accepted: unsanctioned, FR, personal=false, score "100", outcome manual-review |
| 8 | `harbor-personal-data-at-forty` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `maple-personal-data-mid-band` | accepted: unsanctioned, CA, personal=true, score "55.6", outcome manual-review |
| 10 | `cobalt-personal-data-below-seventy` | accepted: unsanctioned, DE, personal=true, score "69.99", outcome manual-review |
| 11 | `lotus-personal-data-below-forty` | accepted: unsanctioned, SG, personal=true, score "39.99", outcome clear |
| 12 | `southern-cross-zero-risk` | accepted: unsanctioned, AU, personal=true, score "0", outcome clear |
| 13 | `tulip-nonpersonal-at-forty` | accepted: unsanctioned, NL, personal=false, score "40", outcome clear |
| 14 | `sakura-nonpersonal-below-seventy` | accepted: unsanctioned, JP, personal=false, score "69.999", outcome clear |
| 15 | `andean-low-risk-clearance` | accepted: unsanctioned, CL, personal=false, score "18.25", outcome clear |
