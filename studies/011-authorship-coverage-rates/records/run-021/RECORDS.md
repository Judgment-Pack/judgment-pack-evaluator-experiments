# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6020 of 6020; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "91.4", outcome reject |
| 2 | `paektu-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "3", outcome reject |
| 3 | `damascus-embargo-mid-risk` | accepted: unsanctioned, SY, personal=true, score "40", outcome reject |
| 4 | `tehran-embargo-high-risk` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `atlas-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `helix-high-risk-data` | accepted: unsanctioned, FR, personal=true, score "84.25", outcome manual-review |
| 7 | `meridian-high-risk-no-data` | accepted: unsanctioned, AU, personal=false, score "99.99", outcome manual-review |
| 8 | `cedar-data-threshold` | accepted: unsanctioned, US, personal=true, score "40", outcome manual-review |
| 9 | `lotus-data-upper-border` | accepted: unsanctioned, SG, personal=true, score "69.99", outcome manual-review |
| 10 | `fjord-data-mid-band` | accepted: unsanctioned, NO, personal=true, score "55.5", outcome manual-review |
| 11 | `maple-data-below-threshold` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 12 | `sakura-data-zero-risk` | accepted: unsanctioned, JP, personal=true, score "0", outcome clear |
| 13 | `andes-no-data-upper-border` | accepted: unsanctioned, CL, personal=false, score "69.999", outcome clear |
| 14 | `baltic-no-data-forty` | accepted: unsanctioned, EE, personal=false, score "40", outcome clear |
| 15 | `savanna-no-data-routine` | accepted: unsanctioned, KE, personal=false, score "18.75", outcome clear |
