# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6056 of 6056; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-sanctions-precedence` | accepted: sanctioned, IR, personal=true, score "100", outcome reject |
| 2 | `paektu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `caspian-embargo-registration` | accepted: unsanctioned, IR, personal=true, score "44.99", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "72", outcome reject |
| 5 | `alpine-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "72", outcome manual-review |
| 6 | `borealis-just-above-threshold` | accepted: unsanctioned, FI, personal=false, score "72.01", outcome manual-review |
| 7 | `meridian-maximum-risk` | accepted: unsanctioned, AU, personal=true, score "100", outcome manual-review |
| 8 | `harbor-personal-data-threshold` | accepted: unsanctioned, GB, personal=true, score "45", outcome manual-review |
| 9 | `cedar-personal-data-midrange` | accepted: unsanctioned, US, personal=true, score "58.4", outcome manual-review |
| 10 | `atlas-personal-data-upper-edge` | accepted: unsanctioned, FR, personal=true, score "71.999", outcome manual-review |
| 11 | `willow-personal-data-below-threshold` | accepted: unsanctioned, DE, personal=true, score "44.999", outcome clear |
| 12 | `lotus-personal-data-zero-risk` | accepted: unsanctioned, SG, personal=true, score "0", outcome clear |
| 13 | `bluewater-no-data-at-forty-five` | accepted: unsanctioned, NL, personal=false, score "45", outcome clear |
| 14 | `kestrel-no-data-upper-edge` | accepted: unsanctioned, JP, personal=false, score "71.999", outcome clear |
| 15 | `savanna-no-data-moderate-risk` | accepted: unsanctioned, ZA, personal=false, score "63.25", outcome clear |
