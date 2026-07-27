# Interpretation decisions

1. **“Within the last 24 hrs” includes the exact 24-hour boundary.**

   Text:

   > “The booking was made within the last 24 hrs”

   Alternatives were `< 24` and `<= 24`. The pack uses `less-than-or-equal` because a booking
   exactly 24 elapsed hours old is still at the stated boundary; the policy does not say “less than
   24 hours.” This choice should be confirmed by a policy owner before operational use.

2. **“Business flight” means the reservation's cabin class is `business`.**

   Text:

   > “It is a business flight”

   Alternatives included a business-purpose trip or the defined business cabin. The policy defines
   `business` as one of three cabin classes and defines no business-purpose trip type, so the pack
   compares `reservation.cabinClass` with `business`.

3. **A segment counts as already flown once it has departed.**

   Text:

   > “If any portion of the flight has already been flown, the agent cannot help and transfer is needed.”

   Alternatives were “only a completed segment” and “a segment that has taken off, including one
   currently flying.” The latter is used because the policy says “any portion,” and its domain
   definition says a `flying` flight has taken off. The upstream determination must apply this
   reading.

4. **Insurance-covered cancellation reasons are health and weather.**

   Text:

   > “The user has travel insurance and the reason for cancellation is covered by insurance.”
   >
   > “The travel insurance is 30 dollars per passenger and enables full refund if the user needs to cancel the flight given health or weather reasons.”

   Alternatives were to leave coverage as an externally prepared Boolean or to use the only
   coverage categories the policy supplies. The pack uses the latter, testing the requester's
   reason directly for `health` or `weather`; this avoids migrating a policy determination out of
   the pack.

5. **An airline cancellation must be verified independently of the requester's reason.**

   Text:

   > “The agent must also obtain the reason for cancellation (change of plan, airline cancelled flight, or other reasons)”
   >
   > “The flight is cancelled by airline”

   Alternatives were to treat the requester selecting `airline cancelled flight` as sufficient or
   to read verified reservation/flight status. The pack uses a separate
   `reservation.airlineCancelled` fact because the policy says the flight “is” cancelled and warns
   that the agent must ensure the rules are met.

6. **No eligibility ground means the agent may not cancel.**

   Text:

   > “Otherwise, flight can be cancelled if any of the following is true:”
   >
   > “You should deny user requests that are against this policy.”

   The alternatives were an unresolved result when all four grounds are false or a negative
   cancellation outcome. The pack uses `may-not-cancel` as the fallback because the “if any”
   sentence supplies the permitted set and the policy generally requires requests against policy
   to be denied. Unknown facts do not reach this fallback because `onUnknown: escalate` blocks it.

7. **The flown-portion clause overrides every positive eligibility ground.**

   Text:

   > “If any portion of the flight has already been flown, the agent cannot help and transfer is needed.”
   >
   > “Otherwise, flight can be cancelled if any of the following is true:”

   Alternatives were to let a positive cancellation ground compete with transfer or to treat the
   first sentence as a prerequisite. The word “Otherwise” makes it a prerequisite, so the pack
   uses a direct escalation exception that resolves before normal rules.
