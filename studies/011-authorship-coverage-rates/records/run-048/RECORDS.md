# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6015 of 6015; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `pyongyang-low-risk-embargo` | accepted: unsanctioned, KP, personal=false, score "3.25", outcome reject |
| 3 | `damascus-high-risk-embargo` | accepted: unsanctioned, SY, personal=true, score "94.7", outcome reject |
| 4 | `tehran-borderline-embargo` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `alpine-risk-seventy` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `baltic-risk-above-seventy` | accepted: unsanctioned, EE, personal=true, score "70.01", outcome manual-review |
| 7 | `andes-high-risk-no-data` | accepted: unsanctioned, CL, personal=false, score "91.4", outcome manual-review |
| 8 | `maple-data-risk-forty` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `rhine-data-midrange-risk` | accepted: unsanctioned, DE, personal=true, score "55.75", outcome manual-review |
| 10 | `pacific-data-below-seventy` | accepted: unsanctioned, AU, personal=true, score "69.99", outcome manual-review |
| 11 | `cedar-data-below-forty` | accepted: unsanctioned, GB, personal=true, score "39.99", outcome clear |
| 12 | `sakura-data-zero-risk` | accepted: unsanctioned, JP, personal=true, score "0", outcome clear |
| 13 | `tulip-no-data-risk-forty` | accepted: unsanctioned, NL, personal=false, score "40", outcome clear |
| 14 | `fjord-no-data-near-seventy` | accepted: unsanctioned, NO, personal=false, score "69.999", outcome clear |
| 15 | `atlas-low-risk-no-data` | accepted: unsanctioned, MA, personal=false, score "18.6", outcome clear |
