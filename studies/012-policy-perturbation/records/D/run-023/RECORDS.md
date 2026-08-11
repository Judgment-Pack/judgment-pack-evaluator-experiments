# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6036 of 6036; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `redwood-sanctions-overrides-embargo` | accepted: sanctioned, IR, personal=true, score "88.4", outcome reject |
| 2 | `chollima-kp-registration` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `pars-iran-registration` | accepted: unsanctioned, IR, personal=true, score "44.99", outcome reject |
| 4 | `levant-syria-high-risk` | accepted: unsanctioned, SY, personal=true, score "100", outcome reject |
| 5 | `bluepeak-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "72", outcome manual-review |
| 6 | `solstice-high-risk-data` | accepted: unsanctioned, FR, personal=true, score "91.25", outcome manual-review |
| 7 | `harbor-risk-just-over-threshold` | accepted: unsanctioned, SG, personal=false, score "72.01", outcome manual-review |
| 8 | `cedar-personal-data-threshold` | accepted: unsanctioned, US, personal=true, score "45", outcome manual-review |
| 9 | `maple-data-midrange-risk` | accepted: unsanctioned, CA, personal=true, score "58.7", outcome manual-review |
| 10 | `orion-data-just-below-seventy-two` | accepted: unsanctioned, GB, personal=true, score "71.99", outcome manual-review |
| 11 | `alpine-data-below-threshold` | accepted: unsanctioned, CH, personal=true, score "44.99", outcome clear |
| 12 | `sakura-data-zero-risk` | accepted: unsanctioned, JP, personal=true, score "0", outcome clear |
| 13 | `fjord-no-data-at-forty-five` | accepted: unsanctioned, NO, personal=false, score "45", outcome clear |
| 14 | `outback-no-data-near-threshold` | accepted: unsanctioned, AU, personal=false, score "71.99", outcome clear |
| 15 | `bosphorus-low-risk-services` | accepted: unsanctioned, TR, personal=false, score "18.375", outcome clear |
