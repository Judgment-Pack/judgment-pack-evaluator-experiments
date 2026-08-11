# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6001 of 6001; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-office-supplies` | accepted: unsanctioned, CA, personal=false, score "0", outcome clear |
| 1 | `alpine-parts-logistics` | accepted: unsanctioned, CH, personal=false, score "40", outcome clear |
| 2 | `cedar-industrial-tools` | accepted: unsanctioned, US, personal=false, score "69.99", outcome clear |
| 3 | `blue-harbor-analytics` | accepted: unsanctioned, AU, personal=true, score "39.99", outcome clear |
| 4 | `maple-customer-systems` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 5 | `rhein-data-services` | accepted: unsanctioned, DE, personal=true, score "55.5", outcome manual-review |
| 6 | `sakura-benefits-platform` | accepted: unsanctioned, JP, personal=true, score "69.99", outcome manual-review |
| 7 | `iberia-facilities-group` | accepted: unsanctioned, ES, personal=false, score "70", outcome manual-review |
| 8 | `tulip-workforce-cloud` | accepted: unsanctioned, NL, personal=true, score "70", outcome manual-review |
| 9 | `baltic-freight-exchange` | accepted: unsanctioned, EE, personal=false, score "100", outcome manual-review |
| 10 | `daedong-machinery-export` | accepted: unsanctioned, KP, personal=false, score "5", outcome reject |
| 11 | `pars-medical-distribution` | accepted: unsanctioned, IR, personal=true, score "39.5", outcome reject |
| 12 | `levant-network-solutions` | accepted: unsanctioned, SY, personal=true, score "82", outcome reject |
| 13 | `meridian-commodity-brokers` | accepted: sanctioned, GB, personal=false, score "12", outcome reject |
| 14 | `orion-identity-labs` | accepted: sanctioned, SG, personal=true, score "70", outcome reject |
| 15 | `caspian-state-procurement` | accepted: sanctioned, IR, personal=true, score "100", outcome reject |
