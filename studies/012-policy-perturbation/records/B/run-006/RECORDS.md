# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6029 of 6029; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `pyongyang-industrial-supply` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `tehran-analytics-network` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-logistics-group` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 5 | `alpine-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `sakura-high-risk-services` | accepted: unsanctioned, JP, personal=true, score "70.01", outcome manual-review |
| 7 | `atlas-maximum-risk` | accepted: unsanctioned, MA, personal=false, score "100", outcome manual-review |
| 8 | `harbor-personal-data-threshold` | accepted: unsanctioned, AU, personal=true, score "40", outcome manual-review |
| 9 | `baltic-personal-data-upper-edge` | accepted: unsanctioned, EE, personal=true, score "69.99", outcome manual-review |
| 10 | `maple-personal-data-midrange` | accepted: unsanctioned, CA, personal=true, score "55.5", outcome manual-review |
| 11 | `fjord-no-data-upper-edge` | accepted: unsanctioned, NO, personal=false, score "69.99", outcome clear |
| 12 | `cedar-no-data-midrange` | accepted: unsanctioned, US, personal=false, score "40", outcome clear |
| 13 | `lotus-personal-data-below-threshold` | accepted: unsanctioned, SG, personal=true, score "39.99", outcome clear |
| 14 | `andes-personal-data-zero-risk` | accepted: unsanctioned, CL, personal=true, score "0", outcome clear |
| 15 | `savanna-no-data-minimal-risk` | accepted: unsanctioned, KE, personal=false, score "0.01", outcome clear |
