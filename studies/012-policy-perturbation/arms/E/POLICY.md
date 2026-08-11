# Vendor screening policy — the arbiter

Synthetic policy for this study. Every other artifact in this study is checked
against this text; a divergence between a pack and this text is a pack bug.
This is also the exact policy text the record author receives (inlined in the
registered prompt), so it is the whole of what the two sides share.

- **P1.** A vendor with a sanctions hit is **rejected**, regardless of
  anything else.
- **P2.** Absent a sanctions hit, a vendor registered in an embargoed
  country — **KP, IR, or SY** — is **rejected**.
- **P3.** Absent a sanctions hit or an embargoed registration, a vendor
  whose risk score is **at or above the review threshold** goes to **manual
  review**.
- **P4.** Absent a sanctions hit or an embargoed registration, a vendor that
  **handles personal data** and whose risk score is **at or above the
  personal-data threshold but below the review threshold** goes to **manual
  review**.
- **P5.** Absent a sanctions hit or an embargoed registration, a vendor
  whose risk score is **below the review threshold** is **cleared**, unless
  P4 applies — that is, a vendor that does not handle personal data clears
  below the review threshold, and a vendor that does handle personal data
  clears only below the personal-data threshold.

Risk scores are decimal strings and compare numerically. Registered
countries are two-letter uppercase codes in the ISO 3166-1 alpha-2 style;
the policy consults no registry — embargo-list membership is exact,
case-sensitive string comparison against KP, IR, and SY, and any other
two-letter code is a non-embargoed registration. The three outcomes —
clear, manual review, reject — are exhaustive over complete inputs (all
four facts present and well-formed, which is what the study's gates admit);
the policy takes no position on incomplete inputs, which no admitted
record can present. The office's risk scale runs from zero to one hundred.
The **review threshold** is seven tenths of that full range; the
**personal-data threshold** is four tenths of that same full range.
