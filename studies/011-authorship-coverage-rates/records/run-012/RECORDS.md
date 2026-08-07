# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5969 of 5969; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `sanctions-hit-low-risk` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `sanctions-hit-embargoed` | accepted: sanctioned, IR, personal=true, score "88.4", outcome reject |
| 2 | `sanctions-hit-risk-boundary` | accepted: sanctioned, GB, personal=true, score "40", outcome reject |
| 3 | `north-korea-registration` | accepted: unsanctioned, KP, personal=false, score "5.5", outcome reject |
| 4 | `iran-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 5 | `syria-registration-high-risk` | accepted: unsanctioned, SY, personal=true, score "92", outcome reject |
| 6 | `risk-exactly-seventy` | accepted: unsanctioned, EE, personal=false, score "70", outcome manual-review |
| 7 | `risk-above-seventy` | accepted: unsanctioned, CL, personal=false, score "70.01", outcome manual-review |
| 8 | `personal-data-high-risk` | accepted: unsanctioned, JP, personal=true, score "84.25", outcome manual-review |
| 9 | `personal-data-exactly-forty` | accepted: unsanctioned, CH, personal=true, score "40", outcome manual-review |
| 10 | `personal-data-mid-band` | accepted: unsanctioned, NZ, personal=true, score "55.75", outcome manual-review |
| 11 | `personal-data-just-below-seventy` | accepted: unsanctioned, PT, personal=true, score "69.999", outcome manual-review |
| 12 | `personal-data-just-below-forty` | accepted: unsanctioned, CA, personal=true, score "39.999", outcome clear |
| 13 | `personal-data-zero-risk` | accepted: unsanctioned, SE, personal=true, score "0", outcome clear |
| 14 | `no-personal-data-mid-band` | accepted: unsanctioned, ZA, personal=false, score "40", outcome clear |
| 15 | `no-personal-data-just-below-seventy` | accepted: unsanctioned, AT, personal=false, score "69.999", outcome clear |
