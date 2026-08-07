# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6037 of 6037; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-screen` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `oriel-sanctions-override` | accepted: sanctioned, GB, personal=true, score "85", outcome reject |
| 2 | `taedong-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "8", outcome reject |
| 3 | `persis-embargo-borderline` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "70", outcome reject |
| 5 | `atlas-exact-seventy` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `saffron-high-risk-data` | accepted: unsanctioned, IN, personal=true, score "92.75", outcome manual-review |
| 7 | `cobalt-high-risk-no-data` | accepted: unsanctioned, JP, personal=false, score "70.01", outcome manual-review |
| 8 | `harbor-data-exact-forty` | accepted: unsanctioned, US, personal=true, score "40", outcome manual-review |
| 9 | `meridian-data-midrange` | accepted: unsanctioned, AU, personal=true, score "55.5", outcome manual-review |
| 10 | `cedar-data-below-seventy` | accepted: unsanctioned, IE, personal=true, score "69.99", outcome manual-review |
| 11 | `lumen-data-below-forty` | accepted: unsanctioned, NL, personal=true, score "39.99", outcome clear |
| 12 | `maple-data-zero-risk` | accepted: unsanctioned, CA, personal=true, score "0", outcome clear |
| 13 | `granite-no-data-forty` | accepted: unsanctioned, NO, personal=false, score "40", outcome clear |
| 14 | `solstice-no-data-near-threshold` | accepted: unsanctioned, ES, personal=false, score "69.99", outcome clear |
| 15 | `alpine-low-risk-clearance` | accepted: unsanctioned, CH, personal=false, score "18.25", outcome clear |
