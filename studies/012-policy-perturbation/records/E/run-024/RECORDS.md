# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5967 of 5967; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "95", outcome reject |
| 2 | `paektu-industrial-embargo` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `damascus-ledger-embargo` | accepted: unsanctioned, SY, personal=true, score "39.999", outcome reject |
| 4 | `tehran-analytics-embargo` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `alpine-review-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `sakura-above-review` | accepted: unsanctioned, JP, personal=true, score "70.001", outcome manual-review |
| 7 | `andes-maximum-risk` | accepted: unsanctioned, CL, personal=false, score "100", outcome manual-review |
| 8 | `harbor-personal-threshold` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `maple-personal-midrange` | accepted: unsanctioned, CA, personal=true, score "55.25", outcome manual-review |
| 10 | `baltic-personal-below-review` | accepted: unsanctioned, EE, personal=true, score "69.999", outcome manual-review |
| 11 | `cedar-zero-risk-clear` | accepted: unsanctioned, US, personal=false, score "0", outcome clear |
| 12 | `fjord-nonpersonal-below-review` | accepted: unsanctioned, NO, personal=false, score "69.999", outcome clear |
| 13 | `savanna-nonpersonal-at-forty` | accepted: unsanctioned, AU, personal=false, score "40", outcome clear |
| 14 | `lotus-personal-below-threshold` | accepted: unsanctioned, IN, personal=true, score "39.999", outcome clear |
| 15 | `rhine-routine-clear` | accepted: unsanctioned, DE, personal=false, score "18.75", outcome clear |
