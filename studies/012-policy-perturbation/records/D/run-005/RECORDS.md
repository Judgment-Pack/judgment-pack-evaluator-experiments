# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6058 of 6058; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `sanctions-hit-low-risk` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `sanctions-hit-embargoed` | accepted: sanctioned, KP, personal=true, score "88.5", outcome reject |
| 2 | `sanctions-hit-review-range` | accepted: sanctioned, PT, personal=true, score "45", outcome reject |
| 3 | `iran-registration-low-risk` | accepted: unsanctioned, IR, personal=false, score "0", outcome reject |
| 4 | `syria-registration-personal-data` | accepted: unsanctioned, SY, personal=true, score "44.99", outcome reject |
| 5 | `north-korea-registration-high-risk` | accepted: unsanctioned, KP, personal=false, score "100", outcome reject |
| 6 | `risk-threshold-seventy-two` | accepted: unsanctioned, DE, personal=false, score "72", outcome manual-review |
| 7 | `high-risk-personal-data` | accepted: unsanctioned, CA, personal=true, score "92.75", outcome manual-review |
| 8 | `maximum-risk-no-personal-data` | accepted: unsanctioned, CH, personal=false, score "100", outcome manual-review |
| 9 | `personal-data-threshold-forty-five` | accepted: unsanctioned, EE, personal=true, score "45", outcome manual-review |
| 10 | `personal-data-just-below-seventy-two` | accepted: unsanctioned, ES, personal=true, score "71.999", outcome manual-review |
| 11 | `personal-data-midrange-risk` | accepted: unsanctioned, JP, personal=true, score "58.4", outcome manual-review |
| 12 | `personal-data-just-below-forty-five` | accepted: unsanctioned, NZ, personal=true, score "44.999", outcome clear |
| 13 | `personal-data-zero-risk` | accepted: unsanctioned, SE, personal=true, score "0", outcome clear |
| 14 | `no-personal-data-near-review-threshold` | accepted: unsanctioned, PE, personal=false, score "71.9999", outcome clear |
| 15 | `no-personal-data-at-forty-five` | accepted: unsanctioned, ZA, personal=false, score "45", outcome clear |
