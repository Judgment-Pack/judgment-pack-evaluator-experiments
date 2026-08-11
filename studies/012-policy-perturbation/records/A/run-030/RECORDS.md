# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6026 of 6026; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `taedong-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `levant-embargo-mid-risk` | accepted: unsanctioned, SY, personal=true, score "39.99", outcome reject |
| 4 | `tehran-embargo-high-risk` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `bluepeak-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `silverline-above-threshold` | accepted: unsanctioned, AU, personal=false, score "70.01", outcome manual-review |
| 7 | `redwood-maximum-risk` | accepted: unsanctioned, US, personal=true, score "100", outcome manual-review |
| 8 | `harbor-personal-data-threshold` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `maple-personal-data-midband` | accepted: unsanctioned, CA, personal=true, score "55.5", outcome manual-review |
| 10 | `fjord-personal-data-upper-edge` | accepted: unsanctioned, NO, personal=true, score "69.99", outcome manual-review |
| 11 | `cedar-personal-data-below-threshold` | accepted: unsanctioned, NZ, personal=true, score "39.99", outcome clear |
| 12 | `lotus-personal-data-zero-risk` | accepted: unsanctioned, SG, personal=true, score "0", outcome clear |
| 13 | `alpine-nonpersonal-forty` | accepted: unsanctioned, CH, personal=false, score "40", outcome clear |
| 14 | `sunfield-nonpersonal-upper-edge` | accepted: unsanctioned, ES, personal=false, score "69.999", outcome clear |
| 15 | `atlas-nonpersonal-low-risk` | accepted: unsanctioned, FR, personal=false, score "18.25", outcome clear |
