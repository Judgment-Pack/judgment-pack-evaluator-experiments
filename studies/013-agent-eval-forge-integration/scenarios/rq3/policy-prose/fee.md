# Fee assessment policy

The fee for a request is determined by its declared amount, which policy
requires to be recorded as an exact decimal string.

- An amount of 1000 or more incurs the standard fee.
- An amount below 1000 incurs the reduced fee.
- A request whose declared amount is recorded as exactly the string "1000"
  is exempt from fees (an exact-declaration exemption, matched literally
  against the recorded string, not by numeric value — "1000.00" is the same
  number but not the same declaration).
- If the amount cannot be ordered against the threshold — including an
  amount recorded as a JSON number rather than a decimal string — the fee
  cannot be assessed; that undecidable state blocks the decision and is
  escalated to the Fee review queue.
- Conflicting rule outcomes are NOT escalated anywhere by configuration:
  only undecidable amounts route to the Fee review queue. Any other blocked
  state simply remains unresolved with no configured destination.
- There is no default fee: if no rule applies, the request remains
  undecided.
