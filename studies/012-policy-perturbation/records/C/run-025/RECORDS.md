# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5950 of 5950; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-sanctions-high-risk` | accepted: sanctioned, US, personal=true, score "88", outcome reject |
| 2 | `daedong-sanctions-embargo` | accepted: sanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `tehran-office-supply` | accepted: unsanctioned, IR, personal=false, score "18", outcome reject |
| 4 | `levant-data-systems` | accepted: unsanctioned, SY, personal=true, score "55.5", outcome reject |
| 5 | `pyongyang-risk-advisory` | accepted: unsanctioned, KP, personal=true, score "100", outcome reject |
| 6 | `maple-zero-risk` | accepted: unsanctioned, CA, personal=false, score "0", outcome clear |
| 7 | `harbor-data-below-forty` | accepted: unsanctioned, AU, personal=true, score "39.99", outcome clear |
| 8 | `alpine-data-at-forty` | accepted: unsanctioned, DE, personal=true, score "40", outcome manual-review |
| 9 | `sakura-midrange-data` | accepted: unsanctioned, JP, personal=true, score "52.75", outcome manual-review |
| 10 | `baltic-data-below-seventy` | accepted: unsanctioned, EE, personal=true, score "69.999", outcome manual-review |
| 11 | `andes-logistics-below-seventy` | accepted: unsanctioned, CL, personal=false, score "69.999", outcome clear |
| 12 | `nordic-tools-midrange` | accepted: unsanctioned, SE, personal=false, score "40", outcome clear |
| 13 | `iberia-freight-at-seventy` | accepted: unsanctioned, ES, personal=false, score "70", outcome manual-review |
| 14 | `lotus-cloud-at-seventy` | accepted: unsanctioned, SG, personal=true, score "70", outcome manual-review |
| 15 | `cape-engineering-maximum-risk` | accepted: unsanctioned, ZA, personal=false, score "100", outcome manual-review |
