# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5969 of 5969; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-sanctions-override` | accepted: sanctioned, DE, personal=true, score "85", outcome reject |
| 2 | `paektu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `pars-embargo-override` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 5 | `atlas-exact-high-risk-threshold` | accepted: unsanctioned, FR, personal=false, score "70", outcome manual-review |
| 6 | `cedar-high-risk-personal-data` | accepted: unsanctioned, US, personal=true, score "92.4", outcome manual-review |
| 7 | `bluehaven-high-risk-no-data` | accepted: unsanctioned, AU, personal=false, score "70.01", outcome manual-review |
| 8 | `lumen-exact-data-threshold` | accepted: unsanctioned, NL, personal=true, score "40", outcome manual-review |
| 9 | `sakura-mid-risk-personal-data` | accepted: unsanctioned, JP, personal=true, score "55.75", outcome manual-review |
| 10 | `harbor-data-below-seventy` | accepted: unsanctioned, GB, personal=true, score "69.99", outcome manual-review |
| 11 | `maple-no-data-below-seventy` | accepted: unsanctioned, CA, personal=false, score "69.99", outcome clear |
| 12 | `fjord-no-data-mid-risk` | accepted: unsanctioned, NO, personal=false, score "40", outcome clear |
| 13 | `alpine-data-below-forty` | accepted: unsanctioned, CH, personal=true, score "39.99", outcome clear |
| 14 | `baltic-data-zero-risk` | accepted: unsanctioned, EE, personal=true, score "0", outcome clear |
| 15 | `andes-low-risk-no-data` | accepted: unsanctioned, CL, personal=false, score "18.6", outcome clear |
