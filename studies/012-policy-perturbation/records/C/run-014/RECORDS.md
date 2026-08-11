# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6012 of 6012; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-logistics-sanctions` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-data-sanctions-override` | accepted: sanctioned, IR, personal=true, score "85", outcome reject |
| 2 | `pyongyang-industrial-supply` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `tehran-analytics-low-risk` | accepted: unsanctioned, IR, personal=true, score "20", outcome reject |
| 4 | `levant-systems-high-risk` | accepted: unsanctioned, SY, personal=false, score "92.75", outcome reject |
| 5 | `maple-office-zero-risk` | accepted: unsanctioned, CA, personal=false, score "0", outcome clear |
| 6 | `alpine-payroll-below-forty` | accepted: unsanctioned, CH, personal=true, score "39.99", outcome clear |
| 7 | `baltic-hosting-forty-boundary` | accepted: unsanctioned, EE, personal=true, score "40", outcome manual-review |
| 8 | `andes-research-midrange-personal` | accepted: unsanctioned, CL, personal=true, score "55.5", outcome manual-review |
| 9 | `pacific-components-midrange` | accepted: unsanctioned, AU, personal=false, score "55.5", outcome clear |
| 10 | `rhein-facilities-below-seventy` | accepted: unsanctioned, DE, personal=false, score "69.99", outcome clear |
| 11 | `sakura-cloud-below-seventy` | accepted: unsanctioned, JP, personal=true, score "69.99", outcome manual-review |
| 12 | `nordic-freight-seventy-boundary` | accepted: unsanctioned, SE, personal=false, score "70", outcome manual-review |
| 13 | `iberia-health-seventy-boundary` | accepted: unsanctioned, ES, personal=true, score "70", outcome manual-review |
| 14 | `savanna-security-high-risk` | accepted: unsanctioned, KE, personal=false, score "87.25", outcome manual-review |
| 15 | `atlantic-biometric-maximum-risk` | accepted: unsanctioned, US, personal=true, score "100", outcome manual-review |
