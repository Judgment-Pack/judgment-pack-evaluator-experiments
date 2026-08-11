# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5988 of 5988; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "5", outcome reject |
| 1 | `cedar-sanctions-embargoed` | accepted: sanctioned, IR, personal=true, score "88.5", outcome reject |
| 2 | `chollima-kp-registration` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `pars-iris-ir-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-sy-registration` | accepted: unsanctioned, SY, personal=true, score "100", outcome reject |
| 5 | `alpine-risk-seventy` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `harbor-high-risk-data` | accepted: unsanctioned, AU, personal=true, score "91.25", outcome manual-review |
| 7 | `iberia-high-risk-no-data` | accepted: unsanctioned, ES, personal=false, score "70.01", outcome manual-review |
| 8 | `lotus-data-risk-forty` | accepted: unsanctioned, SG, personal=true, score "40", outcome manual-review |
| 9 | `baltic-data-below-seventy` | accepted: unsanctioned, EE, personal=true, score "69.99", outcome manual-review |
| 10 | `maple-data-below-forty` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 11 | `sakura-data-zero-risk` | accepted: unsanctioned, JP, personal=true, score "0", outcome clear |
| 12 | `rhein-no-data-forty` | accepted: unsanctioned, DE, personal=false, score "40", outcome clear |
| 13 | `andes-no-data-near-seventy` | accepted: unsanctioned, CL, personal=false, score "69.999", outcome clear |
| 14 | `nile-no-data-mid-risk` | accepted: unsanctioned, EG, personal=false, score "55.5", outcome clear |
| 15 | `savanna-data-low-risk` | accepted: unsanctioned, KE, personal=true, score "12.75", outcome clear |
