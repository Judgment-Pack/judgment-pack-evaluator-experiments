# Vendor screening policy — the arbiter

Synthetic policy for this study. Every other artifact in this study is checked
against this text; a divergence between a pack and this text is a pack bug.
This is also the exact policy text the record author receives (inlined in the
registered prompt), so it is the whole of what the two sides share.

- **P1.** If a vendor has a sanctions hit, the outcome is **reject**,
  whatever else the file shows.
- **P2.** With no sanctions hit, a vendor whose registration is in an
  embargoed country — **KP, IR, or SY** — is also **rejected**.
- **P3.** With neither a sanctions hit nor an embargoed registration, any
  vendor carrying a risk score of **70 or more** is sent to **manual
  review**.
- **P4.** With neither a sanctions hit nor an embargoed registration, a
  vendor that **handles personal data** and carries a risk score of **40 or
  more** but **below 70** is likewise sent to **manual review**.
- **P5.** With neither a sanctions hit nor an embargoed registration, a
  vendor scoring **below 70** is **cleared** except where P4 catches it: a
  vendor that handles no personal data clears anywhere below 70, while one
  that does handle personal data clears only below 40.

Risk scores are decimal strings and compare numerically. Registered
countries are two-letter uppercase codes in the ISO 3166-1 alpha-2 style;
the policy consults no registry — embargo-list membership is exact,
case-sensitive string comparison against KP, IR, and SY, and any other
two-letter code is a non-embargoed registration. The three outcomes —
clear, manual review, reject — are exhaustive over complete inputs (all
four facts present and well-formed, which is what the study's gates admit);
the policy takes no position on incomplete inputs, which no admitted
record can present. The office's risk scale runs from zero to one hundred.
