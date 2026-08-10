# Work routing policy

- Work marked for track A is routed to track A.
- Work marked for track B is routed to track B.
- Work whose review has been decided is routed to track A; if it cannot be
  determined whether the review has been decided, the decision is blocked.
- If the rules select more than one distinct track, that conflict blocks the
  decision and is escalated to the Routing coordinator (a human role).
- Deliberately, ONLY conflicts are escalated to the coordinator: a decision
  blocked for any other reason (such as the undecidable review status above)
  remains unresolved with no configured destination.
- There is no default track.
