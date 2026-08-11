# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5991 of 5991; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `cedar-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "85", outcome reject |
| 2 | `taedong-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `parsa-embargo-borderline` | accepted: unsanctioned, IR, personal=true, score "39.999", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 5 | `alpine-review-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `harbor-above-review-threshold` | accepted: unsanctioned, AU, personal=true, score "70.001", outcome manual-review |
| 7 | `sakura-maximum-risk` | accepted: unsanctioned, JP, personal=false, score "100", outcome manual-review |
| 8 | `bluefjord-personal-threshold` | accepted: unsanctioned, NO, personal=true, score "40", outcome manual-review |
| 9 | `maple-personal-midband` | accepted: unsanctioned, CA, personal=true, score "55.25", outcome manual-review |
| 10 | `rhine-personal-below-review` | accepted: unsanctioned, DE, personal=true, score "69.999", outcome manual-review |
| 11 | `kiwi-nonpersonal-below-review` | accepted: unsanctioned, NZ, personal=false, score "69.999", outcome clear |
| 12 | `iberia-nonpersonal-personal-threshold` | accepted: unsanctioned, ES, personal=false, score "40", outcome clear |
| 13 | `tulip-personal-below-threshold` | accepted: unsanctioned, NL, personal=true, score "39.999", outcome clear |
| 14 | `andes-personal-zero-risk` | accepted: unsanctioned, CL, personal=true, score "0", outcome clear |
| 15 | `savanna-nonpersonal-low-risk` | accepted: unsanctioned, KE, personal=false, score "18.75", outcome clear |
