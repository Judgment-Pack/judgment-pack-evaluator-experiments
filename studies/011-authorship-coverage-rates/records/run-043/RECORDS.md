# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5971 of 5971; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `orion-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `paektu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "3", outcome reject |
| 3 | `damascus-embargo-registration` | accepted: unsanctioned, SY, personal=true, score "39.99", outcome reject |
| 4 | `tehran-embargo-high-risk` | accepted: unsanctioned, IR, personal=false, score "92.4", outcome reject |
| 5 | `atlas-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `cedar-high-risk-data` | accepted: unsanctioned, US, personal=true, score "84.25", outcome manual-review |
| 7 | `fjord-high-risk-no-data` | accepted: unsanctioned, NO, personal=false, score "70.01", outcome manual-review |
| 8 | `maple-data-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `lotus-data-mid-risk` | accepted: unsanctioned, SG, personal=true, score "55.5", outcome manual-review |
| 10 | `harbor-data-upper-border` | accepted: unsanctioned, AU, personal=true, score "69.999", outcome manual-review |
| 11 | `alpine-data-below-threshold` | accepted: unsanctioned, CH, personal=true, score "39.999", outcome clear |
| 12 | `sakura-data-low-risk` | accepted: unsanctioned, JP, personal=true, score "0", outcome clear |
| 13 | `baltic-no-data-threshold` | accepted: unsanctioned, EE, personal=false, score "40", outcome clear |
| 14 | `andes-no-data-upper-border` | accepted: unsanctioned, CL, personal=false, score "69.999", outcome clear |
| 15 | `savanna-no-data-low-risk` | accepted: unsanctioned, ZA, personal=false, score "18.75", outcome clear |
