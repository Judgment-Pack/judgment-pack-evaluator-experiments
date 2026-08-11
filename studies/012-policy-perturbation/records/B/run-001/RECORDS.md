# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5962 of 5962; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `cobalt-sanctions-high-risk` | accepted: sanctioned, DE, personal=true, score "91.5", outcome reject |
| 2 | `hanul-kp-registration` | accepted: unsanctioned, KP, personal=false, score "3", outcome reject |
| 3 | `pars-iran-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-syria-registration` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 5 | `atlas-risk-seventy` | accepted: unsanctioned, FR, personal=false, score "70", outcome manual-review |
| 6 | `cedar-above-seventy` | accepted: unsanctioned, US, personal=true, score "70.01", outcome manual-review |
| 7 | `quartz-maximum-risk` | accepted: unsanctioned, SG, personal=false, score "100", outcome manual-review |
| 8 | `willow-personal-data-forty` | accepted: unsanctioned, GB, personal=true, score "40", outcome manual-review |
| 9 | `harbor-personal-data-midrange` | accepted: unsanctioned, AU, personal=true, score "55.25", outcome manual-review |
| 10 | `maple-personal-data-below-seventy` | accepted: unsanctioned, CA, personal=true, score "69.99", outcome manual-review |
| 11 | `fjord-no-data-below-seventy` | accepted: unsanctioned, NO, personal=false, score "69.99", outcome clear |
| 12 | `solstice-no-data-forty` | accepted: unsanctioned, ES, personal=false, score "40", outcome clear |
| 13 | `sakura-personal-data-under-forty` | accepted: unsanctioned, JP, personal=true, score "39.99", outcome clear |
| 14 | `alpine-personal-data-zero` | accepted: unsanctioned, CH, personal=true, score "0", outcome clear |
| 15 | `delta-no-data-low-risk` | accepted: unsanctioned, NL, personal=false, score "18.75", outcome clear |
