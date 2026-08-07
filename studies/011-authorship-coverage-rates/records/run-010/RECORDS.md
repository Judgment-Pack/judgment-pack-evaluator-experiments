# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6011 of 6011; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `caspian-sanctions-override` | accepted: sanctioned, IR, personal=true, score "88.5", outcome reject |
| 2 | `paektu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `tehran-embargo-low-risk` | accepted: unsanctioned, IR, personal=true, score "0", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "92.75", outcome reject |
| 5 | `granite-risk-seventy` | accepted: unsanctioned, US, personal=false, score "70", outcome manual-review |
| 6 | `silverline-high-risk-data` | accepted: unsanctioned, DE, personal=true, score "70.01", outcome manual-review |
| 7 | `atlas-high-risk-no-data` | accepted: unsanctioned, FR, personal=false, score "99.9", outcome manual-review |
| 8 | `maple-data-risk-forty` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `cedar-data-mid-risk` | accepted: unsanctioned, GB, personal=true, score "54.625", outcome manual-review |
| 10 | `harbor-data-below-seventy` | accepted: unsanctioned, AU, personal=true, score "69.999", outcome manual-review |
| 11 | `sakura-data-below-forty` | accepted: unsanctioned, JP, personal=true, score "39.999", outcome clear |
| 12 | `fjord-data-zero-risk` | accepted: unsanctioned, NO, personal=true, score "0", outcome clear |
| 13 | `alpine-no-data-forty` | accepted: unsanctioned, CH, personal=false, score "40", outcome clear |
| 14 | `tulip-no-data-below-seventy` | accepted: unsanctioned, NL, personal=false, score "69.999", outcome clear |
| 15 | `andean-low-risk-clear` | accepted: unsanctioned, CL, personal=false, score "18.25", outcome clear |
