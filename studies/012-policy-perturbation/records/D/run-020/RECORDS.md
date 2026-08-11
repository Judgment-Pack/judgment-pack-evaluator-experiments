# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6001 of 6001; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88.4", outcome reject |
| 2 | `paektu-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "4.25", outcome reject |
| 3 | `damascus-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "93.7", outcome reject |
| 4 | `tehran-embargo-borderline` | accepted: unsanctioned, IR, personal=true, score "44.99", outcome reject |
| 5 | `alpine-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "72", outcome manual-review |
| 6 | `harbor-risk-above-threshold` | accepted: unsanctioned, AU, personal=false, score "72.01", outcome manual-review |
| 7 | `iberia-data-high-risk` | accepted: unsanctioned, ES, personal=true, score "86.75", outcome manual-review |
| 8 | `maple-data-threshold` | accepted: unsanctioned, CA, personal=true, score "45", outcome manual-review |
| 9 | `baltic-data-midrange` | accepted: unsanctioned, EE, personal=true, score "58.6", outcome manual-review |
| 10 | `sakura-data-upper-border` | accepted: unsanctioned, JP, personal=true, score "71.99", outcome manual-review |
| 11 | `cedar-data-below-threshold` | accepted: unsanctioned, GB, personal=true, score "44.99", outcome clear |
| 12 | `lotus-data-zero-risk` | accepted: unsanctioned, SG, personal=true, score "0", outcome clear |
| 13 | `andes-no-data-midrange` | accepted: unsanctioned, CL, personal=false, score "45", outcome clear |
| 14 | `rhine-no-data-upper-border` | accepted: unsanctioned, DE, personal=false, score "71.99", outcome clear |
| 15 | `atlas-no-data-low-risk` | accepted: unsanctioned, MA, personal=false, score "19.375", outcome clear |
