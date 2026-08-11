# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6090 of 6090; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `redwood-sanctions-match` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `orion-sanctions-embargo-overlap` | accepted: sanctioned, IR, personal=true, score "100", outcome reject |
| 2 | `taedong-kp-registration` | accepted: unsanctioned, KP, personal=false, score "8", outcome reject |
| 3 | `pars-iran-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-syria-registration` | accepted: unsanctioned, SY, personal=false, score "70", outcome reject |
| 5 | `northstar-risk-seventy` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `azimuth-personal-risk-seventy` | accepted: unsanctioned, AU, personal=true, score "70", outcome manual-review |
| 7 | `summit-maximum-risk` | accepted: unsanctioned, US, personal=false, score "100", outcome manual-review |
| 8 | `harbor-personal-risk-forty` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `cedar-personal-midrange-risk` | accepted: unsanctioned, CA, personal=true, score "55.5", outcome manual-review |
| 10 | `meridian-personal-below-seventy` | accepted: unsanctioned, FR, personal=true, score "69.99", outcome manual-review |
| 11 | `willow-personal-below-forty` | accepted: unsanctioned, SE, personal=true, score "39.99", outcome clear |
| 12 | `bluebird-personal-zero-risk` | accepted: unsanctioned, JP, personal=true, score "0", outcome clear |
| 13 | `granite-nonpersonal-risk-forty` | accepted: unsanctioned, NO, personal=false, score "40", outcome clear |
| 14 | `delta-nonpersonal-below-seventy` | accepted: unsanctioned, NL, personal=false, score "69.999", outcome clear |
| 15 | `solstice-nonpersonal-low-risk` | accepted: unsanctioned, ES, personal=false, score "18.25", outcome clear |
