# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5945 of 5945; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-precedence` | accepted: sanctioned, IR, personal=true, score "100", outcome reject |
| 2 | `oryx-high-risk-sanctions` | accepted: sanctioned, AE, personal=true, score "84.2", outcome reject |
| 3 | `pyongyang-low-risk-embargo` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 4 | `tehran-mid-risk-embargo` | accepted: unsanctioned, IR, personal=true, score "40", outcome reject |
| 5 | `levant-high-risk-embargo` | accepted: unsanctioned, SY, personal=false, score "92.75", outcome reject |
| 6 | `alpine-risk-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 7 | `baltic-high-risk-data` | accepted: unsanctioned, EE, personal=true, score "70.01", outcome manual-review |
| 8 | `andes-maximum-risk` | accepted: unsanctioned, CL, personal=false, score "100", outcome manual-review |
| 9 | `cedar-data-threshold` | accepted: unsanctioned, US, personal=true, score "40", outcome manual-review |
| 10 | `sakura-data-upper-border` | accepted: unsanctioned, JP, personal=true, score "69.99", outcome manual-review |
| 11 | `atlas-data-midband` | accepted: unsanctioned, FR, personal=true, score "55.6", outcome manual-review |
| 12 | `harbor-nondata-upper-border` | accepted: unsanctioned, AU, personal=false, score "69.99", outcome clear |
| 13 | `maple-data-lower-border` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 14 | `rhine-nondata-forty` | accepted: unsanctioned, DE, personal=false, score "40", outcome clear |
| 15 | `fjord-zero-risk-data` | accepted: unsanctioned, NO, personal=true, score "0", outcome clear |
