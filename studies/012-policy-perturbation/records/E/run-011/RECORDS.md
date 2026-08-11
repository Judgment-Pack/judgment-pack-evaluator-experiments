# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6015 of 6015; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-logistics-sanctions` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `caspian-data-sanctions-override` | accepted: sanctioned, IR, personal=true, score "88.5", outcome reject |
| 2 | `paektu-industrial-embargo` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 3 | `damascus-office-supply-embargo` | accepted: unsanctioned, SY, personal=true, score "39.99", outcome reject |
| 4 | `tehran-metrics-embargo` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `alpine-security-review-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `harbor-analytics-high-risk` | accepted: unsanctioned, AU, personal=true, score "70.01", outcome manual-review |
| 7 | `summit-infrastructure-maximum-risk` | accepted: unsanctioned, US, personal=false, score "100", outcome manual-review |
| 8 | `maple-hr-personal-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 9 | `rhine-customer-care-mid-risk` | accepted: unsanctioned, DE, personal=true, score "55.25", outcome manual-review |
| 10 | `sakura-identity-below-review` | accepted: unsanctioned, JP, personal=true, score "69.99", outcome manual-review |
| 11 | `baltic-machinery-low-risk` | accepted: unsanctioned, EE, personal=false, score "39.99", outcome clear |
| 12 | `andes-components-personal-boundary` | accepted: unsanctioned, CL, personal=false, score "40", outcome clear |
| 13 | `nordic-freight-below-review` | accepted: unsanctioned, NO, personal=false, score "69.99", outcome clear |
| 14 | `lotus-payroll-below-personal-threshold` | accepted: unsanctioned, IN, personal=true, score "39.99", outcome clear |
| 15 | `kiwi-archive-zero-risk` | accepted: unsanctioned, NZ, personal=true, score "0", outcome clear |
