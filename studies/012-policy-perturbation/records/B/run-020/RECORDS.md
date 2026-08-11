# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6010 of 6010; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `cedar-sanctions-high-risk` | accepted: sanctioned, US, personal=true, score "92.4", outcome reject |
| 2 | `paektu-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "3", outcome reject |
| 3 | `zagros-embargo-registration` | accepted: unsanctioned, IR, personal=true, score "39.999", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 5 | `atlas-seventy-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `harbor-above-seventy` | accepted: unsanctioned, SG, personal=true, score "70.001", outcome manual-review |
| 7 | `andes-high-risk-no-data` | accepted: unsanctioned, CL, personal=false, score "84.75", outcome manual-review |
| 8 | `maple-personal-data-forty` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `tulip-personal-data-midband` | accepted: unsanctioned, NL, personal=true, score "55.6", outcome manual-review |
| 10 | `southern-cross-below-seventy` | accepted: unsanctioned, AU, personal=true, score "69.999", outcome manual-review |
| 11 | `fjord-no-data-upper-bound` | accepted: unsanctioned, NO, personal=false, score "69.999", outcome clear |
| 12 | `sakura-personal-data-below-forty` | accepted: unsanctioned, JP, personal=true, score "39.999", outcome clear |
| 13 | `baltic-low-risk-personal-data` | accepted: unsanctioned, EE, personal=true, score "18.25", outcome clear |
| 14 | `alpine-no-data-forty` | accepted: unsanctioned, CH, personal=false, score "40", outcome clear |
| 15 | `acacia-zero-risk` | accepted: unsanctioned, KE, personal=false, score "0", outcome clear |
