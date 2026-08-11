# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6059 of 6059; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargo` | accepted: sanctioned, IR, personal=true, score "88", outcome reject |
| 2 | `baekdu-embargo-zero-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `damascus-embargo-high-risk` | accepted: unsanctioned, SY, personal=true, score "70", outcome reject |
| 4 | `tehran-embargo-mid-risk` | accepted: unsanctioned, IR, personal=false, score "55.25", outcome reject |
| 5 | `juniper-personal-below-forty` | accepted: unsanctioned, DE, personal=true, score "39.99", outcome clear |
| 6 | `cedar-personal-at-forty` | accepted: unsanctioned, US, personal=true, score "40", outcome manual-review |
| 7 | `harbor-personal-mid-band` | accepted: unsanctioned, GB, personal=true, score "54.6", outcome manual-review |
| 8 | `linden-personal-below-seventy` | accepted: unsanctioned, NL, personal=true, score "69.999", outcome manual-review |
| 9 | `granite-nonpersonal-zero-risk` | accepted: unsanctioned, AU, personal=false, score "0", outcome clear |
| 10 | `maple-nonpersonal-at-forty` | accepted: unsanctioned, CA, personal=false, score "40", outcome clear |
| 11 | `alpine-nonpersonal-below-seventy` | accepted: unsanctioned, CH, personal=false, score "69.999", outcome clear |
| 12 | `sakura-nonpersonal-at-seventy` | accepted: unsanctioned, JP, personal=false, score "70", outcome manual-review |
| 13 | `fjord-personal-at-seventy` | accepted: unsanctioned, NO, personal=true, score "70", outcome manual-review |
| 14 | `acacia-high-risk-ceiling` | accepted: unsanctioned, ZA, personal=false, score "100", outcome manual-review |
| 15 | `solstice-personal-minimal-risk` | accepted: unsanctioned, FR, personal=true, score "0.01", outcome clear |
