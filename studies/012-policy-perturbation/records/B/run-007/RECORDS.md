# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5976 of 5976; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `blue-orchid-sanctions-high-risk` | accepted: sanctioned, SG, personal=true, score "70", outcome reject |
| 3 | `pyongyang-machinery-embargo` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 4 | `levant-digital-embargo` | accepted: unsanctioned, SY, personal=true, score "39.99", outcome reject |
| 5 | `tehran-logistics-embargo-high-risk` | accepted: unsanctioned, IR, personal=false, score "100", outcome reject |
| 6 | `alpine-threshold-seventy` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 7 | `baltic-high-risk-data` | accepted: unsanctioned, EE, personal=true, score "92.75", outcome manual-review |
| 8 | `sakura-data-threshold-forty` | accepted: unsanctioned, JP, personal=true, score "40", outcome manual-review |
| 9 | `iberia-data-below-seventy` | accepted: unsanctioned, ES, personal=true, score "69.99", outcome manual-review |
| 10 | `atlas-high-risk-no-data` | accepted: unsanctioned, MA, personal=false, score "84.2", outcome manual-review |
| 11 | `maple-zero-risk-clear` | accepted: unsanctioned, CA, personal=false, score "0", outcome clear |
| 12 | `kiwi-data-below-forty` | accepted: unsanctioned, NZ, personal=true, score "39.99", outcome clear |
| 13 | `rhine-no-data-below-seventy` | accepted: unsanctioned, DE, personal=false, score "69.99", outcome clear |
| 14 | `andes-data-low-risk` | accepted: unsanctioned, CL, personal=true, score "18.6", outcome clear |
| 15 | `nordic-no-data-forty` | accepted: unsanctioned, SE, personal=false, score "40", outcome clear |
