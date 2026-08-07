# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6044 of 6044; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-sanctions-precedence` | accepted: sanctioned, IR, personal=true, score "91", outcome reject |
| 2 | `paektu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "8", outcome reject |
| 3 | `caspian-embargo-precedence` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "70", outcome reject |
| 5 | `summit-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `atlas-high-risk-data` | accepted: unsanctioned, FR, personal=true, score "84.25", outcome manual-review |
| 7 | `harbor-high-risk-no-data` | accepted: unsanctioned, AU, personal=false, score "99.9", outcome manual-review |
| 8 | `cedar-data-threshold` | accepted: unsanctioned, US, personal=true, score "40", outcome manual-review |
| 9 | `lighthouse-data-upper-bound` | accepted: unsanctioned, GB, personal=true, score "69.99", outcome manual-review |
| 10 | `meadow-data-below-threshold` | accepted: unsanctioned, NL, personal=true, score "39.99", outcome clear |
| 11 | `birch-data-zero-risk` | accepted: unsanctioned, SE, personal=true, score "0", outcome clear |
| 12 | `granite-no-data-mid-risk` | accepted: unsanctioned, CA, personal=false, score "40", outcome clear |
| 13 | `silverline-no-data-upper-bound` | accepted: unsanctioned, JP, personal=false, score "69.999", outcome clear |
| 14 | `tulip-low-risk-logistics` | accepted: unsanctioned, BE, personal=false, score "18.75", outcome clear |
| 15 | `pacific-data-high-risk-boundary` | accepted: unsanctioned, NZ, personal=true, score "70", outcome manual-review |
