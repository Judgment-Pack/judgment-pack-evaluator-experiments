# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5979 of 5979; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "86", outcome reject |
| 2 | `paektu-embargo-zero-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `damascus-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "92.75", outcome reject |
| 4 | `tehran-embargo-threshold` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `alpine-review-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `iberia-high-risk-personal-data` | accepted: unsanctioned, ES, personal=true, score "100", outcome manual-review |
| 7 | `harbor-high-risk-no-data` | accepted: unsanctioned, AU, personal=false, score "83.2", outcome manual-review |
| 8 | `maple-data-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `rhine-data-below-review` | accepted: unsanctioned, DE, personal=true, score "69.999", outcome manual-review |
| 10 | `sakura-data-mid-risk` | accepted: unsanctioned, JP, personal=true, score "55.5", outcome manual-review |
| 11 | `tulip-below-data-threshold` | accepted: unsanctioned, NL, personal=true, score "39.999", outcome clear |
| 12 | `fjord-zero-risk-data` | accepted: unsanctioned, NO, personal=true, score "0", outcome clear |
| 13 | `cedar-no-data-at-forty` | accepted: unsanctioned, NZ, personal=false, score "40", outcome clear |
| 14 | `baltic-no-data-near-review` | accepted: unsanctioned, EE, personal=false, score "69.999", outcome clear |
| 15 | `atlas-low-risk-no-data` | accepted: unsanctioned, MA, personal=false, score "18.25", outcome clear |
