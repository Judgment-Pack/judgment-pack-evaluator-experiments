# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5999 of 5999; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `meridian-sanctions-embargoed` | accepted: sanctioned, IR, personal=true, score "88.5", outcome reject |
| 2 | `paektu-embargoed-registration` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `zagros-embargoed-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-embargoed-high-risk` | accepted: unsanctioned, SY, personal=true, score "92", outcome reject |
| 5 | `atlas-risk-threshold` | accepted: unsanctioned, ES, personal=false, score "70", outcome manual-review |
| 6 | `cedar-high-risk-data` | accepted: unsanctioned, US, personal=true, score "70.01", outcome manual-review |
| 7 | `summit-high-risk-no-data` | accepted: unsanctioned, DE, personal=false, score "84.7", outcome manual-review |
| 8 | `harbor-data-risk-floor` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `willow-data-mid-risk` | accepted: unsanctioned, AU, personal=true, score "55.25", outcome manual-review |
| 10 | `fjord-data-below-seventy` | accepted: unsanctioned, NO, personal=true, score "69.99", outcome manual-review |
| 11 | `maple-data-below-forty` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 12 | `sakura-data-zero-risk` | accepted: unsanctioned, JP, personal=true, score "0", outcome clear |
| 13 | `alpine-no-data-risk-forty` | accepted: unsanctioned, CH, personal=false, score "40", outcome clear |
| 14 | `tulip-no-data-near-threshold` | accepted: unsanctioned, NL, personal=false, score "69.99", outcome clear |
| 15 | `andean-no-data-low-risk` | accepted: unsanctioned, CL, personal=false, score "18.6", outcome clear |
