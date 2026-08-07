# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5992 of 5992; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `aster-data-sanctions-override` | accepted: sanctioned, DE, personal=true, score "85", outcome reject |
| 2 | `taedong-embargoed-registration` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `persia-cloud-embargoed` | accepted: unsanctioned, IR, personal=true, score "39.999", outcome reject |
| 4 | `levant-logistics-embargoed` | accepted: unsanctioned, SY, personal=false, score "70", outcome reject |
| 5 | `summit-risk-threshold` | accepted: unsanctioned, US, personal=false, score "70", outcome manual-review |
| 6 | `cedar-high-risk-data` | accepted: unsanctioned, CA, personal=true, score "91.25", outcome manual-review |
| 7 | `fjord-above-threshold` | accepted: unsanctioned, NO, personal=false, score "70.001", outcome manual-review |
| 8 | `olive-personal-data-threshold` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `harbor-data-mid-risk` | accepted: unsanctioned, AU, personal=true, score "55.5", outcome manual-review |
| 10 | `maple-data-just-below-seventy` | accepted: unsanctioned, CA, personal=true, score "69.999", outcome manual-review |
| 11 | `alpine-data-below-forty` | accepted: unsanctioned, CH, personal=true, score "39.999", outcome clear |
| 12 | `sakura-data-zero-risk` | accepted: unsanctioned, JP, personal=true, score "0", outcome clear |
| 13 | `delta-nondata-forty` | accepted: unsanctioned, NL, personal=false, score "40", outcome clear |
| 14 | `lumen-nondata-just-below-seventy` | accepted: unsanctioned, IT, personal=false, score "69.999", outcome clear |
| 15 | `andes-low-risk-supplier` | accepted: unsanctioned, CL, personal=false, score "18.75", outcome clear |
