# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5880 of 5880; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-office-supplies` | accepted: unsanctioned, CA, personal=false, score "0", outcome clear |
| 1 | `blue-harbor-logistics` | accepted: unsanctioned, DE, personal=false, score "69.99", outcome clear |
| 2 | `cedar-analytics` | accepted: unsanctioned, FR, personal=true, score "39.99", outcome clear |
| 3 | `brightleaf-support` | accepted: unsanctioned, AU, personal=true, score "40", outcome manual-review |
| 4 | `silverline-payments` | accepted: unsanctioned, SG, personal=true, score "69.999", outcome manual-review |
| 5 | `alpine-facilities` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `meridian-cloud` | accepted: unsanctioned, US, personal=true, score "70.01", outcome manual-review |
| 7 | `solstice-industrial` | accepted: unsanctioned, SE, personal=false, score "100", outcome manual-review |
| 8 | `haneul-trading` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 9 | `pars-data-systems` | accepted: unsanctioned, IR, personal=true, score "39.5", outcome reject |
| 10 | `levant-networking` | accepted: unsanctioned, SY, personal=false, score "88.8", outcome reject |
| 11 | `redwood-components` | accepted: sanctioned, MX, personal=false, score "12.25", outcome reject |
| 12 | `atlas-identity` | accepted: sanctioned, GB, personal=true, score "75", outcome reject |
| 13 | `damascus-procurement` | accepted: sanctioned, SY, personal=true, score "20", outcome reject |
| 14 | `rivermark-research` | accepted: unsanctioned, NL, personal=false, score "40", outcome clear |
| 15 | `sakura-customer-care` | accepted: unsanctioned, JP, personal=true, score "0.01", outcome clear |
