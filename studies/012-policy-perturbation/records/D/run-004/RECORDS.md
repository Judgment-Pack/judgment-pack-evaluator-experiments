# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5968 of 5968; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `cedar-sanctions-embargo-overlap` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `chollima-embargo-zero-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `persia-embargo-mid-risk` | accepted: unsanctioned, IR, personal=true, score "44.99", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "72", outcome reject |
| 5 | `bluepeak-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "72", outcome manual-review |
| 6 | `solstice-high-risk-data` | accepted: unsanctioned, FR, personal=true, score "72.01", outcome manual-review |
| 7 | `andes-maximum-risk` | accepted: unsanctioned, CL, personal=false, score "100", outcome manual-review |
| 8 | `harborview-data-threshold` | accepted: unsanctioned, AU, personal=true, score "45", outcome manual-review |
| 9 | `mapleline-data-upper-border` | accepted: unsanctioned, CA, personal=true, score "71.99", outcome manual-review |
| 10 | `sakura-data-mid-band` | accepted: unsanctioned, JP, personal=true, score "58.4", outcome manual-review |
| 11 | `oakridge-data-below-threshold` | accepted: unsanctioned, US, personal=true, score "44.99", outcome clear |
| 12 | `fjord-data-zero-risk` | accepted: unsanctioned, NO, personal=true, score "0", outcome clear |
| 13 | `sunfield-no-data-upper-border` | accepted: unsanctioned, NL, personal=false, score "71.99", outcome clear |
| 14 | `silverfern-no-data-threshold` | accepted: unsanctioned, NZ, personal=false, score "45", outcome clear |
| 15 | `cape-bay-no-data-low-risk` | accepted: unsanctioned, ZA, personal=false, score "18.75", outcome clear |
