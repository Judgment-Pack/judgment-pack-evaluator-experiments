# Data request intake triage policy

This policy applies only to requests whose type is one of: new-data-pipeline,
pipeline-change, dataset-onboarding, one-time-extract, data-access,
reporting-feed. A request of any other type is outside this policy's scope.

Required evidence: the completed intake form, and a sponsor endorsement from
an accountable business sponsor. (Sensitive-data approvals may also exist but
are not required.) If a required piece of evidence is known to be missing, or
its availability cannot be determined, the request cannot be decided and must
go to the Intake reviewer.

Decision rules:
- Decline and redirect when the request fails an appropriateness criterion
  that more information cannot fix (appropriateness assessed as hard-fail).
- Return for clarification when the submission is incomplete, or when
  appropriateness is still pending or not yet evaluable.
- Proceed when the submission is complete, every appropriateness criterion
  passes, and both required pieces of evidence are present.
- If the value of a fact needed by one of these rules is not available, the
  decision is blocked and goes to the Intake reviewer rather than being
  guessed.

Exception (overrides everything above): if the request would put embargoed
material non-public information in front of unauthorized recipients, the
outcome is forced to decline-and-redirect. If it cannot be determined whether
this exception applies, the decision is blocked and goes to the Intake
reviewer.

If no rule produces an outcome, the default disposition is
return-for-clarification. Any blocked decision — not applicable, missing
required evidence, an undecidable fact, conflicting rules, or no matching
rule — is routed to the Intake reviewer (a human role).
