# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6061 of 6061; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `cedar-sanctions-embargo-overlap` | accepted: sanctioned, IR, personal=true, score "84", outcome reject |
| 2 | `paektu-embargo-zero-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `pars-embargo-personal-data` | accepted: unsanctioned, IR, personal=true, score "39.999", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 5 | `granite-review-threshold` | accepted: unsanctioned, US, personal=false, score "70", outcome manual-review |
| 6 | `blueharbor-above-review-threshold` | accepted: unsanctioned, DE, personal=false, score "70.001", outcome manual-review |
| 7 | `lumen-high-risk-personal-data` | accepted: unsanctioned, FR, personal=true, score "92.75", outcome manual-review |
| 8 | `silverfern-personal-threshold` | accepted: unsanctioned, NZ, personal=true, score "40", outcome manual-review |
| 9 | `sakura-personal-midband` | accepted: unsanctioned, JP, personal=true, score "55.5", outcome manual-review |
| 10 | `fjord-personal-below-review` | accepted: unsanctioned, NO, personal=true, score "69.999", outcome manual-review |
| 11 | `atlas-nonpersonal-below-review` | accepted: unsanctioned, ES, personal=false, score "69.999", outcome clear |
| 12 | `maple-nonpersonal-personal-threshold` | accepted: unsanctioned, CA, personal=false, score "40", outcome clear |
| 13 | `sunbird-personal-just-below-threshold` | accepted: unsanctioned, AU, personal=true, score "39.999", outcome clear |
| 14 | `delta-personal-zero-risk` | accepted: unsanctioned, NL, personal=true, score "0", outcome clear |
| 15 | `andes-nonpersonal-midband` | accepted: unsanctioned, CL, personal=false, score "55.5", outcome clear |
