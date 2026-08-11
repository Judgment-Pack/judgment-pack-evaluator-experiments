# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6008 of 6008; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-logistics-sanctions` | accepted: sanctioned, CA, personal=false, score "0", outcome reject |
| 1 | `redwood-analytics-sanctions` | accepted: sanctioned, DE, personal=true, score "85.5", outcome reject |
| 2 | `taedong-industrial-embargo` | accepted: unsanctioned, KP, personal=false, score "12", outcome reject |
| 3 | `pars-cloud-embargo` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-systems-embargo` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 5 | `atlas-infrastructure-threshold` | accepted: unsanctioned, FR, personal=false, score "70", outcome manual-review |
| 6 | `silverline-data-high-risk` | accepted: unsanctioned, AU, personal=true, score "91.25", outcome manual-review |
| 7 | `harbor-machinery-near-threshold` | accepted: unsanctioned, JP, personal=false, score "69.99", outcome clear |
| 8 | `cedar-payments-personal-data-threshold` | accepted: unsanctioned, US, personal=true, score "40", outcome manual-review |
| 9 | `fjord-health-personal-data-midrisk` | accepted: unsanctioned, NO, personal=true, score "55.7", outcome manual-review |
| 10 | `maple-research-below-data-threshold` | accepted: unsanctioned, CA, personal=true, score "39.99", outcome clear |
| 11 | `alpine-office-zero-risk` | accepted: unsanctioned, CH, personal=false, score "0", outcome clear |
| 12 | `solstice-advisory-low-data-risk` | accepted: unsanctioned, GB, personal=true, score "18.5", outcome clear |
| 13 | `baltic-components-midrisk` | accepted: unsanctioned, EE, personal=false, score "40", outcome clear |
| 14 | `sakura-hosting-fractional-high-risk` | accepted: unsanctioned, JP, personal=false, score "70.01", outcome manual-review |
| 15 | `andes-records-upper-data-band` | accepted: unsanctioned, CL, personal=true, score "69.99", outcome manual-review |
