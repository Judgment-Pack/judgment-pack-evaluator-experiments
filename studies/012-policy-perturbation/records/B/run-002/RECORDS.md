# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6013 of 6013; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `cedar-sanctions-embargoed` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `hanul-embargoed-zero-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `damascus-data-services` | accepted: unsanctioned, SY, personal=true, score "39.99", outcome reject |
| 4 | `persis-logistics-high-risk` | accepted: unsanctioned, IR, personal=false, score "100", outcome reject |
| 5 | `atlas-risk-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `harbor-analytics-high-risk` | accepted: unsanctioned, AU, personal=true, score "92.75", outcome manual-review |
| 7 | `fjord-systems-over-threshold` | accepted: unsanctioned, NO, personal=false, score "70.01", outcome manual-review |
| 8 | `maple-identity-data-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `sakura-cloud-mid-risk` | accepted: unsanctioned, JP, personal=true, score "55.5", outcome manual-review |
| 10 | `alpine-payments-below-seventy` | accepted: unsanctioned, CH, personal=true, score "69.99", outcome manual-review |
| 11 | `baltic-hardware-near-threshold` | accepted: unsanctioned, EE, personal=false, score "69.99", outcome clear |
| 12 | `lotus-support-below-data-threshold` | accepted: unsanctioned, SG, personal=true, score "39.99", outcome clear |
| 13 | `andes-stationery-zero-risk` | accepted: unsanctioned, CL, personal=false, score "0", outcome clear |
| 14 | `savanna-office-supplies` | accepted: unsanctioned, KE, personal=false, score "40", outcome clear |
| 15 | `emerald-benefits-low-risk` | accepted: unsanctioned, IE, personal=true, score "18.25", outcome clear |
