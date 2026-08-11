# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-5997 of 5997; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-override` | accepted: sanctioned, CA, personal=false, score "12", outcome reject |
| 1 | `meridian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "95.5", outcome reject |
| 2 | `baekdu-kp-registration` | accepted: unsanctioned, KP, personal=false, score "3", outcome reject |
| 3 | `pars-iran-registration` | accepted: unsanctioned, IR, personal=true, score "39.999", outcome reject |
| 4 | `levant-syria-registration` | accepted: unsanctioned, SY, personal=true, score "70", outcome reject |
| 5 | `alpine-review-threshold` | accepted: unsanctioned, CH, personal=false, score "70", outcome manual-review |
| 6 | `solstice-high-risk` | accepted: unsanctioned, AU, personal=true, score "88.25", outcome manual-review |
| 7 | `fjord-maximum-risk` | accepted: unsanctioned, NO, personal=false, score "100", outcome manual-review |
| 8 | `cedar-personal-threshold` | accepted: unsanctioned, US, personal=true, score "40", outcome manual-review |
| 9 | `tulip-personal-midrange` | accepted: unsanctioned, NL, personal=true, score "55.75", outcome manual-review |
| 10 | `harbor-just-below-review` | accepted: unsanctioned, SG, personal=true, score "69.999", outcome manual-review |
| 11 | `maple-below-personal-threshold` | accepted: unsanctioned, CA, personal=true, score "39.999", outcome clear |
| 12 | `sakura-low-personal-risk` | accepted: unsanctioned, JP, personal=true, score "18.4", outcome clear |
| 13 | `cobalt-nonpersonal-midrange` | accepted: unsanctioned, DE, personal=false, score "40", outcome clear |
| 14 | `andes-nonpersonal-borderline` | accepted: unsanctioned, CL, personal=false, score "69.999", outcome clear |
| 15 | `greenfield-zero-risk` | accepted: unsanctioned, GB, personal=false, score "0", outcome clear |
