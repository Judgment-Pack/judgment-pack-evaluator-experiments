# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6068 of 6068; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `sanctions-hit-low-risk` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `sanctions-hit-embargoed` | accepted: sanctioned, SY, personal=true, score "88.5", outcome reject |
| 2 | `iran-registration-zero-risk` | accepted: unsanctioned, IR, personal=false, score "0", outcome reject |
| 3 | `north-korea-registration` | accepted: unsanctioned, KP, personal=true, score "39.99", outcome reject |
| 4 | `syria-registration-high-risk` | accepted: unsanctioned, SY, personal=false, score "70", outcome reject |
| 5 | `exact-high-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `fraction-above-high-risk-threshold` | accepted: unsanctioned, EE, personal=false, score "70.01", outcome manual-review |
| 7 | `personal-data-exact-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 8 | `personal-data-mid-band` | accepted: unsanctioned, JP, personal=true, score "55.7", outcome manual-review |
| 9 | `personal-data-just-below-seventy` | accepted: unsanctioned, CL, personal=true, score "69.999", outcome manual-review |
| 10 | `personal-data-just-below-forty` | accepted: unsanctioned, IN, personal=true, score "39.999", outcome clear |
| 11 | `personal-data-zero-risk` | accepted: unsanctioned, NZ, personal=true, score "0", outcome clear |
| 12 | `no-personal-data-exact-forty` | accepted: unsanctioned, DE, personal=false, score "40", outcome clear |
| 13 | `no-personal-data-mid-band` | accepted: unsanctioned, KE, personal=false, score "58.25", outcome clear |
| 14 | `no-personal-data-just-below-seventy` | accepted: unsanctioned, NO, personal=false, score "69.999", outcome clear |
| 15 | `personal-data-above-seventy` | accepted: unsanctioned, AU, personal=true, score "92.4", outcome manual-review |
