# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6050 of 6050; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo-overlap` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `daedong-kp-registration` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `pars-iran-registration` | accepted: unsanctioned, IR, personal=true, score "22.75", outcome reject |
| 4 | `levant-syria-high-risk` | accepted: unsanctioned, SY, personal=true, score "91.4", outcome reject |
| 5 | `atlas-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `harbor-high-risk-no-personal-data` | accepted: unsanctioned, SG, personal=false, score "84.25", outcome manual-review |
| 7 | `cedar-high-risk-personal-data` | accepted: unsanctioned, US, personal=true, score "73.1", outcome manual-review |
| 8 | `lumen-personal-data-threshold` | accepted: unsanctioned, FR, personal=true, score "40", outcome manual-review |
| 9 | `birch-personal-data-mid-risk` | accepted: unsanctioned, GB, personal=true, score "55.6", outcome manual-review |
| 10 | `southern-cross-upper-border` | accepted: unsanctioned, AU, personal=true, score "69.99", outcome manual-review |
| 11 | `tulip-personal-data-lower-border` | accepted: unsanctioned, NL, personal=true, score "39.99", outcome clear |
| 12 | `maple-low-risk-personal-data` | accepted: unsanctioned, CA, personal=true, score "18.4", outcome clear |
| 13 | `alpine-nonpersonal-mid-risk` | accepted: unsanctioned, CH, personal=false, score "40", outcome clear |
| 14 | `sakura-nonpersonal-upper-border` | accepted: unsanctioned, JP, personal=false, score "69.999", outcome clear |
| 15 | `fjord-zero-risk` | accepted: unsanctioned, NO, personal=false, score "0", outcome clear |
