# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6014 of 6014; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-components-sanctions` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `caspian-data-sanctions-override` | accepted: sanctioned, IR, personal=true, score "100", outcome reject |
| 2 | `oryx-logistics-sanctions-low-risk` | accepted: sanctioned, DE, personal=true, score "0", outcome reject |
| 3 | `paektu-industrial-embargo` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 4 | `tehran-analytics-embargo` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 5 | `levant-machinery-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "85.5", outcome reject |
| 6 | `alpine-systems-review-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 7 | `harbor-health-high-risk` | accepted: unsanctioned, AU, personal=true, score "91.25", outcome manual-review |
| 8 | `mesa-freight-maximum-risk` | accepted: unsanctioned, US, personal=false, score "100", outcome manual-review |
| 9 | `cedar-identity-personal-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 10 | `tulip-payroll-below-review` | accepted: unsanctioned, NL, personal=true, score "69.99", outcome manual-review |
| 11 | `sakura-insights-midrange-personal` | accepted: unsanctioned, JP, personal=true, score "55.5", outcome manual-review |
| 12 | `fjord-office-zero-risk` | accepted: unsanctioned, NO, personal=false, score "0", outcome clear |
| 13 | `lumen-cloud-below-personal-threshold` | accepted: unsanctioned, FR, personal=true, score "39.99", outcome clear |
| 14 | `savanna-metals-midrange-nonpersonal` | accepted: unsanctioned, ZA, personal=false, score "40", outcome clear |
| 15 | `baltic-tools-review-edge` | accepted: unsanctioned, EE, personal=false, score "69.99", outcome clear |
