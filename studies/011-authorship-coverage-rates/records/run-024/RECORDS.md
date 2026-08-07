# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6005 of 6005; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88.4", outcome reject |
| 2 | `baekdu-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "3", outcome reject |
| 3 | `damascus-embargo-borderline` | accepted: unsanctioned, SY, personal=true, score "39.99", outcome reject |
| 4 | `tehran-embargo-high-risk` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `alpine-exact-seventy` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `harbor-above-seventy` | accepted: unsanctioned, AU, personal=false, score "70.01", outcome manual-review |
| 7 | `sakura-high-risk-data` | accepted: unsanctioned, JP, personal=true, score "94.7", outcome manual-review |
| 8 | `linden-just-below-seventy-data` | accepted: unsanctioned, DE, personal=true, score "69.99", outcome manual-review |
| 9 | `ibex-exact-forty-data` | accepted: unsanctioned, ES, personal=true, score "40", outcome manual-review |
| 10 | `maple-midrange-data` | accepted: unsanctioned, CA, personal=true, score "55.6", outcome manual-review |
| 11 | `fjord-just-below-forty-data` | accepted: unsanctioned, NO, personal=true, score "39.99", outcome clear |
| 12 | `kiwi-zero-risk-data` | accepted: unsanctioned, NZ, personal=true, score "0", outcome clear |
| 13 | `tulip-exact-forty-no-data` | accepted: unsanctioned, NL, personal=false, score "40", outcome clear |
| 14 | `andes-just-below-seventy-no-data` | accepted: unsanctioned, CL, personal=false, score "69.99", outcome clear |
| 15 | `lagos-midrange-no-data` | accepted: unsanctioned, NG, personal=false, score "52.25", outcome clear |
