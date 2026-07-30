# Feature-pass notes — Study 004

One classifier applied the total rule of [`../PREREGISTRATION.md`](../PREREGISTRATION.md) §4 to
the five frozen frame items, before any encoding room opened. Labels are in
[`feature-pass.json`](feature-pass.json): A1 3 non-scalar, A1 7 non-scalar, A3 4 non-scalar,
A7 2 scalar-status, R3 1 scalar-status. The registered predictor therefore predicts, before any
graph exists: A7 2 and R3 1 close; A1 3, A1 7, and A3 4 do not.

Non-scalar bases: A1 3 needs the certificate-remainder amount (a magnitude carved out of A7's
refundable base); A1 7 needs A1's insurance-purchased fact plus the cancellation *reason* (an
A6 input, not its outcome) and carries the "full refund" scope; A3 4 needs the price
difference, which A3's outcome names but never carries as a value.

Scalar bases, checked against the census packs: A7 2's clause reduces to a membership test over
the change/cancel outcomes, which A7 already reads as a boolean completion fact; R3 1's clause
is consumed as an order-status equality, so only the modification outcome's identity crosses.

One judgment call recorded for the measurement pass, since it bears on the predictor: A7 2's
upstream outcomes are *eligibility* findings, while the downstream fact asserts the act was
*completed*. That gap is none of the rule's non-scalar triggers, so the total rule places the
item in the scalar branch — but it is a plausible fidelity loss at scoring time (§5 step 3)
rather than a feature-rule matter.
