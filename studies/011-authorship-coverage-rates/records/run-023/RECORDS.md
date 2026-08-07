# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5992 of 5992; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-hit` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `redwood-sanctions-override` | accepted: sanctioned, US, personal=true, score "88.4", outcome reject |
| 2 | `taedong-embargo-registration` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `persis-embargo-override` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "91.75", outcome reject |
| 5 | `atlas-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `cedar-high-risk-no-data` | accepted: unsanctioned, FR, personal=false, score "70.01", outcome manual-review |
| 7 | `blueharbor-high-risk-data` | accepted: unsanctioned, AU, personal=true, score "96.2", outcome manual-review |
| 8 | `maple-data-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `fjord-data-midrisk` | accepted: unsanctioned, NO, personal=true, score "55.6", outcome manual-review |
| 10 | `sakura-data-upper-border` | accepted: unsanctioned, JP, personal=true, score "69.99", outcome manual-review |
| 11 | `lowveld-data-below-threshold` | accepted: unsanctioned, ZA, personal=true, score "39.99", outcome clear |
| 12 | `alpine-data-minimal-risk` | accepted: unsanctioned, CH, personal=true, score "0", outcome clear |
| 13 | `copperleaf-no-data-midrisk` | accepted: unsanctioned, PL, personal=false, score "40", outcome clear |
| 14 | `solstice-no-data-upper-border` | accepted: unsanctioned, ES, personal=false, score "69.99", outcome clear |
| 15 | `delta-no-data-low-risk` | accepted: unsanctioned, NL, personal=false, score "18.375", outcome clear |
