# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6073 of 6073; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `sanctions-hit-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `sanctions-hit-embargoed` | accepted: sanctioned, KP, personal=true, score "100", outcome reject |
| 2 | `sanctions-hit-review-range` | accepted: sanctioned, DE, personal=true, score "45", outcome reject |
| 3 | `iran-registration-zero-risk` | accepted: unsanctioned, IR, personal=false, score "0", outcome reject |
| 4 | `syria-registration-personal-data` | accepted: unsanctioned, SY, personal=true, score "39.999", outcome reject |
| 5 | `north-korea-registration-high-risk` | accepted: unsanctioned, KP, personal=false, score "88.4", outcome reject |
| 6 | `exact-seventy-no-personal-data` | accepted: unsanctioned, GB, personal=false, score "70", outcome manual-review |
| 7 | `exact-seventy-personal-data` | accepted: unsanctioned, JP, personal=true, score "70", outcome manual-review |
| 8 | `maximum-risk-non-embargoed` | accepted: unsanctioned, US, personal=false, score "100", outcome manual-review |
| 9 | `just-below-seventy-personal-data` | accepted: unsanctioned, AU, personal=true, score "69.999", outcome manual-review |
| 10 | `exact-forty-personal-data` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 11 | `midrange-personal-data` | accepted: unsanctioned, NL, personal=true, score "55.25", outcome manual-review |
| 12 | `just-below-forty-personal-data` | accepted: unsanctioned, CH, personal=true, score "39.999", outcome clear |
| 13 | `zero-risk-personal-data` | accepted: unsanctioned, NO, personal=true, score "0", outcome clear |
| 14 | `just-below-seventy-no-personal-data` | accepted: unsanctioned, EE, personal=false, score "69.999", outcome clear |
| 15 | `exact-forty-no-personal-data` | accepted: unsanctioned, CL, personal=false, score "40", outcome clear |
