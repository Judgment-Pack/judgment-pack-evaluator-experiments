# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6080 of 6080; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo-overlap` | accepted: sanctioned, IR, personal=true, score "91", outcome reject |
| 2 | `paektu-embargo-zero-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `damascus-embargo-mid-risk` | accepted: unsanctioned, SY, personal=true, score "55.4", outcome reject |
| 4 | `tehran-embargo-review-threshold` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `alpine-exact-review-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `baltic-above-review-threshold` | accepted: unsanctioned, EE, personal=false, score "70.01", outcome manual-review |
| 7 | `iberia-maximum-risk` | accepted: unsanctioned, ES, personal=true, score "100", outcome manual-review |
| 8 | `maple-personal-data-at-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `sakura-personal-data-mid-band` | accepted: unsanctioned, JP, personal=true, score "54.75", outcome manual-review |
| 10 | `kiwi-personal-data-below-review` | accepted: unsanctioned, NZ, personal=true, score "69.999", outcome manual-review |
| 11 | `andes-nonpersonal-at-data-threshold` | accepted: unsanctioned, CL, personal=false, score "40", outcome clear |
| 12 | `rhine-nonpersonal-below-review` | accepted: unsanctioned, DE, personal=false, score "69.999", outcome clear |
| 13 | `cedar-personal-data-below-threshold` | accepted: unsanctioned, LB, personal=true, score "39.999", outcome clear |
| 14 | `nordic-personal-data-zero-risk` | accepted: unsanctioned, SE, personal=true, score "0", outcome clear |
| 15 | `atlas-nonpersonal-routine-clearance` | accepted: unsanctioned, AU, personal=false, score "18.25", outcome clear |
