# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5912 of 5912; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "91.75", outcome reject |
| 2 | `oryx-sanctions-low-risk` | accepted: sanctioned, DE, personal=true, score "0", outcome reject |
| 3 | `pyongyang-freight-embargo` | accepted: unsanctioned, KP, personal=false, score "8.2", outcome reject |
| 4 | `levant-data-embargo` | accepted: unsanctioned, SY, personal=true, score "39.999", outcome reject |
| 5 | `tehran-industrial-embargo` | accepted: unsanctioned, IR, personal=false, score "88", outcome reject |
| 6 | `atlas-risk-threshold` | accepted: unsanctioned, FR, personal=false, score "70", outcome manual-review |
| 7 | `cedar-high-risk-data` | accepted: unsanctioned, US, personal=true, score "70.001", outcome manual-review |
| 8 | `harbor-high-risk-nondata` | accepted: unsanctioned, AU, personal=false, score "96.4", outcome manual-review |
| 9 | `maple-data-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 10 | `tulip-data-upper-border` | accepted: unsanctioned, NL, personal=true, score "69.999", outcome manual-review |
| 11 | `alpine-data-midrange` | accepted: unsanctioned, CH, personal=true, score "55.25", outcome manual-review |
| 12 | `sakura-data-below-threshold` | accepted: unsanctioned, JP, personal=true, score "39.999", outcome clear |
| 13 | `baltic-nondata-upper-border` | accepted: unsanctioned, EE, personal=false, score "69.999", outcome clear |
| 14 | `andes-nondata-forty` | accepted: unsanctioned, CL, personal=false, score "40", outcome clear |
| 15 | `fjord-data-zero-risk` | accepted: unsanctioned, NO, personal=true, score "0", outcome clear |
