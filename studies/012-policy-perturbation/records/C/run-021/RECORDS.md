# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5967 of 5967; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-logistics-sanctions` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `cedar-analytics-sanctions-low-risk` | accepted: sanctioned, US, personal=true, score "0", outcome reject |
| 2 | `orion-trading-sanctions-embargo` | accepted: sanctioned, IR, personal=false, score "85", outcome reject |
| 3 | `taedong-machinery-kp` | accepted: unsanctioned, KP, personal=false, score "18", outcome reject |
| 4 | `pars-cloud-services-ir` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 5 | `levant-industrial-sy` | accepted: unsanctioned, SY, personal=true, score "100", outcome reject |
| 6 | `maple-office-zero-risk` | accepted: unsanctioned, CA, personal=false, score "0", outcome clear |
| 7 | `alpine-payroll-below-forty` | accepted: unsanctioned, DE, personal=true, score "39.99", outcome clear |
| 8 | `sakura-data-forty` | accepted: unsanctioned, JP, personal=true, score "40", outcome manual-review |
| 9 | `iberia-research-midrange` | accepted: unsanctioned, ES, personal=true, score "55.25", outcome manual-review |
| 10 | `fjord-health-below-seventy` | accepted: unsanctioned, NO, personal=true, score "69.99", outcome manual-review |
| 11 | `andes-hardware-below-seventy` | accepted: unsanctioned, CL, personal=false, score "69.99", outcome clear |
| 12 | `baltic-hosting-seventy` | accepted: unsanctioned, EE, personal=false, score "70", outcome manual-review |
| 13 | `pacific-identity-seventy` | accepted: unsanctioned, AU, personal=true, score "70", outcome manual-review |
| 14 | `savanna-security-high-risk` | accepted: unsanctioned, KE, personal=false, score "88.4", outcome manual-review |
| 15 | `delta-biometric-maximum-risk` | accepted: unsanctioned, NL, personal=true, score "100", outcome manual-review |
