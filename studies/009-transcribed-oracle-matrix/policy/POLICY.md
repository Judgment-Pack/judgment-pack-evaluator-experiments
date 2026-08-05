# Vendor screening policy — the arbiter

Synthetic policy for Study 009. Every other artifact in this study is checked
against this text; a divergence between a pack and this text is a pack bug.

- **P1.** A vendor with a sanctions hit is **rejected**, regardless of risk
  score.
- **P2.** Absent a sanctions hit, a vendor whose risk score is **70 or above**
  goes to **manual review**.
- **P3.** Absent a sanctions hit, a vendor whose risk score is **below 70** is
  **cleared**.

Risk scores are decimal strings and compare numerically. The three outcomes
are exhaustive over known inputs; an unknown input is nobody's outcome and
escalates.
