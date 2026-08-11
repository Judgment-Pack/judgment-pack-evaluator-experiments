# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5984 of 5984; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `damascus-sanctions-embargo` | accepted: sanctioned, SY, personal=true, score "85", outcome reject |
| 2 | `caspian-iran-registration` | accepted: unsanctioned, IR, personal=false, score "0", outcome reject |
| 3 | `paektu-korea-registration` | accepted: unsanctioned, KP, personal=true, score "39.99", outcome reject |
| 4 | `levant-syria-high-risk` | accepted: unsanctioned, SY, personal=true, score "100", outcome reject |
| 5 | `atlas-seventy-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `cedar-high-risk-data` | accepted: unsanctioned, US, personal=true, score "91.25", outcome manual-review |
| 7 | `harbor-high-risk-no-data` | accepted: unsanctioned, SG, personal=false, score "70.01", outcome manual-review |
| 8 | `maple-data-forty-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `fjord-data-mid-risk` | accepted: unsanctioned, NO, personal=true, score "55.5", outcome manual-review |
| 10 | `southern-cross-data-upper-bound` | accepted: unsanctioned, AU, personal=true, score "69.99", outcome manual-review |
| 11 | `alpine-data-below-forty` | accepted: unsanctioned, CH, personal=true, score "39.99", outcome clear |
| 12 | `sakura-data-zero-risk` | accepted: unsanctioned, JP, personal=true, score "0", outcome clear |
| 13 | `baltic-no-data-upper-bound` | accepted: unsanctioned, EE, personal=false, score "69.99", outcome clear |
| 14 | `andes-no-data-forty` | accepted: unsanctioned, CL, personal=false, score "40", outcome clear |
| 15 | `luso-no-data-low-risk` | accepted: unsanctioned, PT, personal=false, score "18.75", outcome clear |
