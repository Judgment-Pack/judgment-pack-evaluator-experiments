# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6025 of 6025; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-logistics-sanctions` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `meridian-data-sanctions` | accepted: sanctioned, DE, personal=true, score "88.5", outcome reject |
| 2 | `chollima-industrial-embargo` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `persia-cloud-embargo` | accepted: unsanctioned, IR, personal=true, score "44.999", outcome reject |
| 4 | `levant-analytics-embargo` | accepted: unsanctioned, SY, personal=true, score "95", outcome reject |
| 5 | `atlas-facilities-risk-threshold` | accepted: unsanctioned, FR, personal=false, score "72", outcome manual-review |
| 6 | `pacific-payments-high-risk` | accepted: unsanctioned, AU, personal=true, score "72.001", outcome manual-review |
| 7 | `andean-minerals-maximum-risk` | accepted: unsanctioned, CL, personal=false, score "100", outcome manual-review |
| 8 | `sakura-hr-personal-threshold` | accepted: unsanctioned, JP, personal=true, score "45", outcome manual-review |
| 9 | `baltic-insights-personal-midrisk` | accepted: unsanctioned, EE, personal=true, score "58.25", outcome manual-review |
| 10 | `alpine-benefits-below-upper-bound` | accepted: unsanctioned, CH, personal=true, score "71.999", outcome manual-review |
| 11 | `cedar-office-zero-risk` | accepted: unsanctioned, US, personal=false, score "0", outcome clear |
| 12 | `fjord-equipment-nonpersonal` | accepted: unsanctioned, NO, personal=false, score "45", outcome clear |
| 13 | `tulip-maintenance-below-seventy-two` | accepted: unsanctioned, NL, personal=false, score "71.999", outcome clear |
| 14 | `maple-research-personal-lowrisk` | accepted: unsanctioned, CA, personal=true, score "44.999", outcome clear |
| 15 | `kiwi-archive-personal-minimal-risk` | accepted: unsanctioned, NZ, personal=true, score "0.01", outcome clear |
