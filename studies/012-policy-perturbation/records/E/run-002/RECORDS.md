# Compiled records — the authoring ledger

Every element of the authored array, in source order: accepted as its
caseId, or dropped with a stable code (records_compile.py's docstring
names them). Regenerable byte-for-byte from the retained completion.

Selected array span: characters 0-6080 of 6080; everything outside the
span was retained and ignored.

| # | caseId | disposition |
|---|--------|-------------|
| 0 | `northstar-sanctions-low-risk` | accepted: sanctioned, CA, personal=false, score "12.5", outcome reject |
| 1 | `caspian-sanctions-embargoed` | accepted: sanctioned, IR, personal=true, score "92", outcome reject |
| 2 | `paektu-embargoed-zero-risk` | accepted: unsanctioned, KP, personal=false, score "0", outcome reject |
| 3 | `levant-embargoed-mid-risk` | accepted: unsanctioned, SY, personal=true, score "55", outcome reject |
| 4 | `tehran-embargoed-review-threshold` | accepted: unsanctioned, IR, personal=false, score "70", outcome reject |
| 5 | `summit-review-threshold` | accepted: unsanctioned, DE, personal=false, score "70", outcome manual-review |
| 6 | `harbor-above-review-threshold` | accepted: unsanctioned, SG, personal=false, score "70.01", outcome manual-review |
| 7 | `cedar-high-risk-personal-data` | accepted: unsanctioned, US, personal=true, score "100", outcome manual-review |
| 8 | `bluebird-just-below-review` | accepted: unsanctioned, FR, personal=true, score "69.99", outcome manual-review |
| 9 | `maple-personal-data-threshold` | accepted: unsanctioned, CA, personal=true, score "40", outcome manual-review |
| 10 | `seabrook-above-personal-threshold` | accepted: unsanctioned, AU, personal=true, score "40.01", outcome manual-review |
| 11 | `alpine-just-below-personal-threshold` | accepted: unsanctioned, CH, personal=true, score "39.99", outcome clear |
| 12 | `willow-zero-risk-personal-data` | accepted: unsanctioned, GB, personal=true, score "0", outcome clear |
| 13 | `granite-threshold-without-personal-data` | accepted: unsanctioned, NO, personal=false, score "40", outcome clear |
| 14 | `meridian-just-below-review-no-data` | accepted: unsanctioned, NL, personal=false, score "69.99", outcome clear |
| 15 | `sakura-low-risk-no-data` | accepted: unsanctioned, JP, personal=false, score "18.75", outcome clear |
