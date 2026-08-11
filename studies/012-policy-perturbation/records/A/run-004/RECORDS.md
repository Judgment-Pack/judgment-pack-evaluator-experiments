# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5969 of 5969; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-priority` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-over-embargo` | accepted: sanctioned, IR, personal=true, score "95", outcome reject |
| 2 | `taedong-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `damascus-embargo-data-services` | accepted: unsanctioned, SY, personal=true, score "55.4", outcome reject |
| 4 | `tehran-embargo-high-risk` | accepted: unsanctioned, IR, personal=false, score "100", outcome reject |
| 5 | `alpine-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `pacific-high-risk-no-data` | accepted: unsanctioned, AU, personal=false, score "70.01", outcome manual-review |
| 7 | `iberia-high-risk-data` | accepted: unsanctioned, ES, personal=true, score "88.75", outcome manual-review |
| 8 | `maple-data-forty-boundary` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `rhine-data-midrange` | accepted: unsanctioned, DE, personal=true, score "54.6", outcome manual-review |
| 10 | `sakura-data-below-seventy` | accepted: unsanctioned, JP, personal=true, score "69.99", outcome manual-review |
| 11 | `baltic-zero-risk-clearance` | accepted: unsanctioned, EE, personal=false, score "0", outcome clear |
| 12 | `andes-no-data-below-seventy` | accepted: unsanctioned, CL, personal=false, score "69.99", outcome clear |
| 13 | `emerald-data-below-forty` | accepted: unsanctioned, IE, personal=true, score "39.99", outcome clear |
| 14 | `fjord-data-low-risk` | accepted: unsanctioned, NO, personal=true, score "18.25", outcome clear |
| 15 | `savanna-no-data-forty-boundary` | accepted: unsanctioned, ZA, personal=false, score "40", outcome clear |
