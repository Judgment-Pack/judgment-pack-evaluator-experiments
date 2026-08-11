# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6061 of 6061; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `cedar-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "85", outcome reject |
| 2 | `paektu-embargo-low-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `zagros-embargo-borderline` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-embargo-high-risk` | accepted: unsanctioned, SY, personal=false, score "100", outcome reject |
| 5 | `atlas-exact-seventy` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `harbor-above-seventy` | accepted: unsanctioned, SG, personal=false, score "70.01", outcome manual-review |
| 7 | `solstice-personal-high-risk` | accepted: unsanctioned, AU, personal=true, score "92.4", outcome manual-review |
| 8 | `juniper-personal-exact-forty` | accepted: unsanctioned, FR, personal=true, score "40", outcome manual-review |
| 9 | `bluefin-personal-midrange` | accepted: unsanctioned, NL, personal=true, score "55.75", outcome manual-review |
| 10 | `maple-personal-below-seventy` | accepted: unsanctioned, CA, personal=true, score "69.99", outcome manual-review |
| 11 | `granite-nonpersonal-below-seventy` | accepted: unsanctioned, NO, personal=false, score "69.99", outcome clear |
| 12 | `willow-personal-below-forty` | accepted: unsanctioned, GB, personal=true, score "39.99", outcome clear |
| 13 | `saffron-personal-zero-risk` | accepted: unsanctioned, IN, personal=true, score "0", outcome clear |
| 14 | `andes-nonpersonal-exact-forty` | accepted: unsanctioned, CL, personal=false, score "40", outcome clear |
| 15 | `sakura-nonpersonal-moderate-risk` | accepted: unsanctioned, JP, personal=false, score "27.6", outcome clear |
