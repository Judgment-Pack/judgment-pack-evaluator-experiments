# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6069 of 6069; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `cedar-sanctions-embargoed` | accepted: sanctioned, IR, personal=true, score "88.4", outcome reject |
| 2 | `paektu-embargo-zero-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `damascus-embargo-personal-data` | accepted: unsanctioned, SY, personal=true, score "44.9", outcome reject |
| 4 | `tehran-embargo-high-risk` | accepted: unsanctioned, IR, personal=false, score "100", outcome reject |
| 5 | `atlas-exact-high-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "72", outcome manual-review |
| 6 | `harbor-above-high-risk-threshold` | accepted: unsanctioned, AU, personal=true, score "72.001", outcome manual-review |
| 7 | `fjord-maximum-risk-no-data` | accepted: unsanctioned, NO, personal=false, score "100", outcome manual-review |
| 8 | `sakura-exact-personal-data-threshold` | accepted: unsanctioned, JP, personal=true, score "45", outcome manual-review |
| 9 | `lumen-midrange-personal-data` | accepted: unsanctioned, FR, personal=true, score "58.25", outcome manual-review |
| 10 | `tulip-just-below-high-risk` | accepted: unsanctioned, NL, personal=true, score "71.999", outcome manual-review |
| 11 | `maple-zero-risk-personal-data` | accepted: unsanctioned, CA, personal=true, score "0", outcome clear |
| 12 | `kiwi-just-below-personal-data-threshold` | accepted: unsanctioned, NZ, personal=true, score "44.999", outcome clear |
| 13 | `alpine-exact-threshold-no-data` | accepted: unsanctioned, CH, personal=false, score "45", outcome clear |
| 14 | `baltic-just-below-high-risk-no-data` | accepted: unsanctioned, EE, personal=false, score "71.999", outcome clear |
| 15 | `andes-low-risk-no-data` | accepted: unsanctioned, CL, personal=false, score "23.7", outcome clear |
