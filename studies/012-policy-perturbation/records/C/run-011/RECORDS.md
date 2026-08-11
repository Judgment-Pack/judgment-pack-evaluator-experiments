# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6003 of 6003; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `sanctions-hit-low-risk` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `sanctions-hit-embargoed` | accepted: sanctioned, IR, personal=true, score "85.4", outcome reject |
| 2 | `sanctions-hit-review-band` | accepted: sanctioned, DE, personal=true, score "55", outcome reject |
| 3 | `north-korea-zero-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 4 | `iran-personal-data` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 5 | `syria-high-risk` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 6 | `personal-data-zero-risk` | accepted: unsanctioned, CA, personal=true, score "0", outcome clear |
| 7 | `personal-data-below-forty` | accepted: unsanctioned, JP, personal=true, score "39.99", outcome clear |
| 8 | `personal-data-at-forty` | accepted: unsanctioned, CH, personal=true, score "40", outcome manual-review |
| 9 | `personal-data-mid-band` | accepted: unsanctioned, EE, personal=true, score "54.375", outcome manual-review |
| 10 | `personal-data-below-seventy` | accepted: unsanctioned, CL, personal=true, score "69.99", outcome manual-review |
| 11 | `no-personal-data-at-forty` | accepted: unsanctioned, AU, personal=false, score "40", outcome clear |
| 12 | `no-personal-data-below-seventy` | accepted: unsanctioned, KE, personal=false, score "69.99", outcome clear |
| 13 | `no-personal-data-at-seventy` | accepted: unsanctioned, DK, personal=false, score "70", outcome manual-review |
| 14 | `personal-data-at-seventy` | accepted: unsanctioned, NL, personal=true, score "70", outcome manual-review |
| 15 | `non-embargoed-high-risk` | accepted: unsanctioned, PT, personal=false, score "92.6", outcome manual-review |
