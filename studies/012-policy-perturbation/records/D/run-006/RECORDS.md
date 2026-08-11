# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5970 of 5970; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-critical` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `cedar-sanctions-low-risk` | accepted: sanctioned, US, personal=true, score "0", outcome reject |
| 2 | `oryx-sanctions-embargo-overlap` | accepted: sanctioned, IR, personal=true, score "88.4", outcome reject |
| 3 | `taedong-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "3.25", outcome reject |
| 4 | `pars-embargo-registration` | accepted: unsanctioned, IR, personal=true, score "44.99", outcome reject |
| 5 | `levant-embargo-registration` | accepted: unsanctioned, SY, personal=false, score "72", outcome reject |
| 6 | `helix-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "72", outcome manual-review |
| 7 | `solstice-high-risk-data` | accepted: unsanctioned, AU, personal=true, score "100", outcome manual-review |
| 8 | `quartz-high-risk-no-data` | accepted: unsanctioned, FR, personal=false, score "86.375", outcome manual-review |
| 9 | `amber-data-threshold` | accepted: unsanctioned, NL, personal=true, score "45", outcome manual-review |
| 10 | `maple-data-upper-bound` | accepted: unsanctioned, CA, personal=true, score "71.999", outcome manual-review |
| 11 | `sakura-data-midrange` | accepted: unsanctioned, JP, personal=true, score "58.6", outcome manual-review |
| 12 | `fjord-data-below-threshold` | accepted: unsanctioned, NO, personal=true, score "44.999", outcome clear |
| 13 | `atlas-no-data-at-forty-five` | accepted: unsanctioned, ES, personal=false, score "45", outcome clear |
| 14 | `tulip-no-data-below-seventy-two` | accepted: unsanctioned, BE, personal=false, score "71.999", outcome clear |
| 15 | `alpine-zero-risk-data` | accepted: unsanctioned, CH, personal=true, score "0", outcome clear |
