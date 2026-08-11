# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6016 of 6016; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `helios-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "92", outcome reject |
| 2 | `baekdu-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "3", outcome reject |
| 3 | `damascus-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "88.4", outcome reject |
| 4 | `pars-embargo-threshold` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `redwood-review-threshold` | accepted: unsanctioned, US, personal=false, score "70", outcome manual-review |
| 6 | `sumida-above-review-threshold` | accepted: unsanctioned, JP, personal=false, score "70.01", outcome manual-review |
| 7 | `linden-high-risk-personal-data` | accepted: unsanctioned, DE, personal=true, score "96.75", outcome manual-review |
| 8 | `rivermark-personal-data-threshold` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `cedar-personal-data-midband` | accepted: unsanctioned, CA, personal=true, score "55.5", outcome manual-review |
| 10 | `azimuth-personal-data-below-review` | accepted: unsanctioned, AU, personal=true, score "69.999", outcome manual-review |
| 11 | `fjord-personal-data-below-threshold` | accepted: unsanctioned, NO, personal=true, score "39.999", outcome clear |
| 12 | `quartz-nonpersonal-at-forty` | accepted: unsanctioned, FR, personal=false, score "40", outcome clear |
| 13 | `pampas-nonpersonal-below-review` | accepted: unsanctioned, AR, personal=false, score "69.999", outcome clear |
| 14 | `tulip-zero-risk` | accepted: unsanctioned, NL, personal=false, score "0", outcome clear |
| 15 | `andes-maximum-risk` | accepted: unsanctioned, CL, personal=false, score "100", outcome manual-review |
