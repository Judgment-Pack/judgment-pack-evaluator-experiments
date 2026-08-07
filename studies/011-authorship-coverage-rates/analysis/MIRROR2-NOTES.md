# Interpretive decisions — clean-room mirror of POLICY.md

Sole input: the bytes of `POLICY.md` (Study 010 vendor screening policy) plus
the task prompt's statement of the four fact members and the three outcome
spellings. No other artifact was read.

The text is unusually tight: precedence, both boundaries, and membership
semantics are all stated explicitly, and the trailer even closes the
exhaustiveness question. What follows is every place where I had to choose,
separated into decisions the text determined and decisions it left open.

## Determined by the text — recorded so the reading is auditable

1. **Clause precedence is the "absent ..." chain, not clause order alone.**
   P1 says "regardless of anything else"; P2 says "absent a sanctions hit";
   P3/P4/P5 each say "absent a sanctions hit or an embargoed registration".
   That yields a strict cascade P1 → P2 → P3 → P4 → P5 with early return. In
   particular a sanctions hit rejects even when the country is embargoed and
   the score is low, and an embargoed registration rejects even when the score
   would otherwise clear.

2. **P3's boundary is inclusive at 70** — "70 or above" → `risk >= 70`. A score
   of exactly `70` is manual review, never clear.

3. **P4's band is `[40, 70)`** — "40 or above but below 70". 40 inclusive, 70
   exclusive. Because P3 already returned for `>= 70`, the code tests only the
   lower bound and lets control flow carry the upper bound; this is equivalent
   to the written band, not a loosening of it.

4. **P5 is the residual, and the two readings of it agree.** P5 states both a
   rule ("below 70 is cleared, unless P4 applies") and its own gloss ("does not
   handle personal data clears below 70; handles personal data clears only
   below 40"). Both describe exactly the set left over after P1–P4, so P5 is
   implemented as the fall-through `return "clear"` rather than as a re-tested
   condition. No input can reach the end uncovered — matching the trailer's
   claim that the three outcomes are exhaustive over complete inputs.

5. **Embargo membership is exact and case-sensitive, with no normalisation.**
   The trailer is explicit: "the policy consults no registry — embargo-list
   membership is exact, case-sensitive string comparison against KP, IR, and
   SY, and any other two-letter code is a non-embargoed registration."
   Therefore `"kp"`, `"Kp"`, `" KP"`, `"PRK"` are *not* embargoed. I
   deliberately did **not** call `.upper()`, `.strip()`, or map any alias — a
   normalising mirror would diverge from the text on exactly the inputs the
   trailer singles out. (The facts are declared uppercase two-letter, so this
   should be unobservable on admitted records; the point is that the mirror
   does not silently repair a violation.)

6. **Risk comparison is exact decimal, never binary float.** The trailer says
   scores are decimal strings compared numerically. `decimal.Decimal` is used
   so that e.g. `"39.9999999999999999"` stays below 40 and `"70.000"` is not
   nudged under 70. `float` inputs are refused with `TypeError` rather than
   coerced, since coercion is precisely the failure mode the exact-arithmetic
   requirement exists to prevent.

## Left undetermined by the text — my choice, and why

7. **Truthiness vs. identity for the two boolean facts.** The text says
   "a vendor with a sanctions hit" and "handles personal data" without saying
   how a non-bool would be read. The facts are declared `bool`, so I used plain
   truthiness (`if sanctions_hit:`), which is identical to `is True` over the
   declared domain. Consequence outside the domain: `1`, `"false"`, and any
   non-empty value would count as a hit. Nothing in the text picks a different
   answer, and admitted records cannot present one.

8. **Missing or malformed members raise rather than resolve.** The policy
   "takes no position on incomplete inputs, which no admitted record can
   present." I chose to let a missing key raise `KeyError` and an unparseable
   score raise `decimal.InvalidOperation` (via `Decimal`), rather than invent a
   default or a fourth outcome. Rationale: silently defaulting would let the
   mirror emit a verdict on an input the policy never covers, which is worse
   than a loud failure for an arbiter whose job is to detect divergence. This
   is a behaviour on inputs the text explicitly declines to govern, so it can
   only be a *choice*, not a reading.

9. **Accepted spellings of `riskScore`.** The text says "decimal string". I
   accept `str`, and additionally `int`/`Decimal` (both exact) for caller
   convenience, while rejecting `float` and `bool`. Accepting exact numeric
   types cannot change any verdict; it only avoids a spurious failure if a
   caller hands over an already-exact value.

10. **`Decimal`'s wider string grammar is accepted as-is.** `Decimal` also
    parses `"1e2"`, `"+40"`, `"NaN"`, `"Infinity"`. The text does not define
    the decimal-string grammar, and I did not add a stricter regex. Notable
    consequence I am flagging rather than hiding: a `"NaN"` score compares
    false against every bound and would therefore fall through to `"clear"`.
    I judged an extra validation layer to be an addition to the policy rather
    than an implementation of it, and the study's gates admit only well-formed
    scores — but if the arbiter should be strict about the grammar, this is the
    line to change.

11. **Score sign and range are unbounded.** Nothing in the text caps a score at
    100 or forbids negatives. `"-5"` clears (no personal data) or clears
    (personal data, below 40); `"1000"` is manual review. I implemented the
    bounds as written and added no range check.

12. **Only the two stated thresholds exist.** There is no clause pushing a very
    high score to `reject` — P3 sends *everything* at 70 or above to manual
    review, with no upper cutoff. I resisted the plausible-but-unwritten
    "extremely high risk should reject" reading; rejection is reachable only
    via P1 and P2.
