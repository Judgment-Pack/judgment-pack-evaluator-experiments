# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6051 of 6051; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `orion-sanctions-review-range` | accepted: sanctioned, DE, personal=true, score "85", outcome reject |
| 2 | `taedong-embargoed-registration` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `pars-cloud-embargoed-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-logistics-embargoed-registration` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 5 | `cedar-analytics-review-threshold` | accepted: unsanctioned, US, personal=false, score "70", outcome manual-review |
| 6 | `bluehaven-high-risk-data` | accepted: unsanctioned, GB, personal=true, score "70.01", outcome manual-review |
| 7 | `summit-maximum-risk` | accepted: unsanctioned, AU, personal=false, score "100", outcome manual-review |
| 8 | `tulip-health-personal-threshold` | accepted: unsanctioned, NL, personal=true, score "40", outcome manual-review |
| 9 | `maple-payroll-midrange-data` | accepted: unsanctioned, CA, personal=true, score "55.5", outcome manual-review |
| 10 | `fjord-crm-below-review` | accepted: unsanctioned, NO, personal=true, score "69.99", outcome manual-review |
| 11 | `alpine-tools-zero-risk` | accepted: unsanctioned, CH, personal=false, score "0", outcome clear |
| 12 | `sakura-office-low-risk` | accepted: unsanctioned, JP, personal=false, score "39.99", outcome clear |
| 13 | `baltic-freight-just-below-review` | accepted: unsanctioned, EE, personal=false, score "69.99", outcome clear |
| 14 | `iberia-support-below-personal-threshold` | accepted: unsanctioned, ES, personal=true, score "39.99", outcome clear |
| 15 | `kiwi-directory-minimal-data-risk` | accepted: unsanctioned, NZ, personal=true, score "0.01", outcome clear |
