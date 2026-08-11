# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6010 of 6010; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-match` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-priority-sanctions` | accepted: sanctioned, IR, personal=true, score "100", outcome reject |
| 2 | `taedong-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `persis-embargo-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-embargo-registration` | accepted: unsanctioned, SY, personal=false, score "85", outcome reject |
| 5 | `alpine-review-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `borealis-above-review-threshold` | accepted: unsanctioned, NO, personal=false, score "70.01", outcome manual-review |
| 7 | `sakura-high-risk-data` | accepted: unsanctioned, JP, personal=true, score "92.75", outcome manual-review |
| 8 | `meridian-personal-data-threshold` | accepted: unsanctioned, AU, personal=true, score "40", outcome manual-review |
| 9 | `cobalt-data-below-review` | accepted: unsanctioned, GB, personal=true, score "69.99", outcome manual-review |
| 10 | `maple-data-just-below-threshold` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 11 | `delta-data-zero-risk` | accepted: unsanctioned, NL, personal=true, score "0", outcome clear |
| 12 | `solstice-nondata-below-review` | accepted: unsanctioned, DE, personal=false, score "69.99", outcome clear |
| 13 | `harbor-nondata-personal-threshold` | accepted: unsanctioned, SG, personal=false, score "40", outcome clear |
| 14 | `andes-nondata-midrange` | accepted: unsanctioned, CL, personal=false, score "55.5", outcome clear |
| 15 | `atlas-maximum-risk` | accepted: unsanctioned, MA, personal=false, score "100", outcome manual-review |
