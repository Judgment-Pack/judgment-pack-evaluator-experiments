# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6009 of 6009; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-match` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `parallax-sanctions-precedence` | accepted: sanctioned, DE, personal=true, score "85", outcome reject |
| 2 | `taedong-dual-rejection` | accepted: sanctioned, KP, personal=true, score "91.2", outcome reject |
| 3 | `pyongyang-machinery-embargo` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 4 | `caspian-ledger-embargo` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 5 | `levant-freight-embargo` | accepted: unsanctioned, SY, personal=false, score "70", outcome reject |
| 6 | `meridian-risk-threshold` | accepted: unsanctioned, US, personal=false, score "70", outcome manual-review |
| 7 | `cedar-identity-high-risk` | accepted: unsanctioned, GB, personal=true, score "70.01", outcome manual-review |
| 8 | `atlas-logistics-maximum-risk` | accepted: unsanctioned, MA, personal=false, score "100", outcome manual-review |
| 9 | `bluefin-personal-data-threshold` | accepted: unsanctioned, AU, personal=true, score "40", outcome manual-review |
| 10 | `rhein-payroll-mid-risk` | accepted: unsanctioned, CH, personal=true, score "55.5", outcome manual-review |
| 11 | `sakura-crm-upper-border` | accepted: unsanctioned, JP, personal=true, score "69.99", outcome manual-review |
| 12 | `tulip-hosting-below-data-threshold` | accepted: unsanctioned, NL, personal=true, score "39.99", outcome clear |
| 13 | `baltic-records-zero-risk` | accepted: unsanctioned, EE, personal=true, score "0", outcome clear |
| 14 | `andes-hardware-upper-clearance` | accepted: unsanctioned, CL, personal=false, score "69.99", outcome clear |
| 15 | `fjord-office-moderate-risk` | accepted: unsanctioned, NO, personal=false, score "40", outcome clear |
