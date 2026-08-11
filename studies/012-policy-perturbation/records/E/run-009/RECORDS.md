# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6067 of 6067; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `paragon-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `chollima-kp-registration` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `caspian-ir-registration` | accepted: unsanctioned, IR, personal=true, score "39.99", outcome reject |
| 4 | `levant-sy-registration` | accepted: unsanctioned, SY, personal=false, score "70", outcome reject |
| 5 | `atlas-review-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `redwood-above-review-threshold` | accepted: unsanctioned, US, personal=false, score "70.01", outcome manual-review |
| 7 | `harbor-maximum-risk` | accepted: unsanctioned, AU, personal=true, score "100", outcome manual-review |
| 8 | `sakura-personal-threshold` | accepted: unsanctioned, JP, personal=true, score "40", outcome manual-review |
| 9 | `meridian-personal-midrange` | accepted: unsanctioned, GB, personal=true, score "55.75", outcome manual-review |
| 10 | `aurora-personal-below-review` | accepted: unsanctioned, NO, personal=true, score "69.999", outcome manual-review |
| 11 | `maple-personal-below-threshold` | accepted: unsanctioned, CA, personal=true, score "39.999", outcome clear |
| 12 | `lumen-personal-zero-risk` | accepted: unsanctioned, NL, personal=true, score "0", outcome clear |
| 13 | `andes-nonpersonal-personal-threshold` | accepted: unsanctioned, CL, personal=false, score "40", outcome clear |
| 14 | `cedar-nonpersonal-below-review` | accepted: unsanctioned, FR, personal=false, score "69.999", outcome clear |
| 15 | `baobab-nonpersonal-low-risk` | accepted: unsanctioned, ZA, personal=false, score "18.25", outcome clear |
