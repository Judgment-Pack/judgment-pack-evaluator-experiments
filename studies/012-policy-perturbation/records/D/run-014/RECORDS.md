# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6054 of 6054; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, US, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "38", outcome reject |
| 2 | `rhein-sanctions-high-risk` | accepted: sanctioned, DE, personal=true, score "91.25", outcome reject |
| 3 | `paektu-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "4", outcome reject |
| 4 | `zagros-embargo-personal-data` | accepted: unsanctioned, IR, personal=true, score "44.999", outcome reject |
| 5 | `levant-embargo-maximum-risk` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 6 | `redwood-risk-threshold` | accepted: unsanctioned, US, personal=false, score "72", outcome manual-review |
| 7 | `maple-data-risk-threshold` | accepted: unsanctioned, CA, personal=true, score "72", outcome manual-review |
| 8 | `britannia-maximum-risk` | accepted: unsanctioned, GB, personal=false, score "100", outcome manual-review |
| 9 | `lumiere-personal-data-threshold` | accepted: unsanctioned, FR, personal=true, score "45", outcome manual-review |
| 10 | `elbe-personal-data-upper-edge` | accepted: unsanctioned, DE, personal=true, score "71.999", outcome manual-review |
| 11 | `sakura-personal-data-below-threshold` | accepted: unsanctioned, JP, personal=true, score "44.999", outcome clear |
| 12 | `coral-personal-data-zero-risk` | accepted: unsanctioned, AU, personal=true, score "0", outcome clear |
| 13 | `verde-nonpersonal-upper-edge` | accepted: unsanctioned, BR, personal=false, score "71.999", outcome clear |
| 14 | `deccan-nonpersonal-midrange` | accepted: unsanctioned, IN, personal=false, score "45", outcome clear |
| 15 | `cape-nonpersonal-zero-risk` | accepted: unsanctioned, ZA, personal=false, score "0", outcome clear |
