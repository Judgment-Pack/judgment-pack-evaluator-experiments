# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5998 of 5998; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `pyongyang-industrial-registration` | accepted: unsanctioned, KP, personal=false, score "3", outcome reject |
| 3 | `levant-data-registration` | accepted: unsanctioned, SY, personal=true, score "39.99", outcome reject |
| 4 | `tehran-logistics-registration` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `alpine-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `iberian-high-risk-data` | accepted: unsanctioned, ES, personal=true, score "70.01", outcome manual-review |
| 7 | `pacific-extreme-risk` | accepted: unsanctioned, AU, personal=false, score "99.9", outcome manual-review |
| 8 | `maple-data-forty` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `rhine-data-midrange` | accepted: unsanctioned, DE, personal=true, score "55.5", outcome manual-review |
| 10 | `sakura-data-upper-bound` | accepted: unsanctioned, JP, personal=true, score "69.999", outcome manual-review |
| 11 | `baltic-nondata-upper-bound` | accepted: unsanctioned, EE, personal=false, score "69.999", outcome clear |
| 12 | `andes-nondata-forty` | accepted: unsanctioned, CL, personal=false, score "40", outcome clear |
| 13 | `cedar-data-below-forty` | accepted: unsanctioned, GB, personal=true, score "39.999", outcome clear |
| 14 | `kiwi-data-zero-risk` | accepted: unsanctioned, NZ, personal=true, score "0", outcome clear |
| 15 | `nordic-low-risk-supply` | accepted: unsanctioned, SE, personal=false, score "18.75", outcome clear |
