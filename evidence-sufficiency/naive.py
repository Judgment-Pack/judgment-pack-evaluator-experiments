"""The naive arm: artifact existence mapped straight to an availability state.

This is deliberately not a strawman. It is the shape three shipped in-project
practices already have, strongest first (README, "Where the naive arm comes
from"):

1. the runtime's graph composition seam, where an edge-fed evidence requirement
   reads `present` because a determination exists upstream, whatever that
   determination said;
2. the Slack demo's drafting contract, where a model emits the availability
   document directly, with no sufficiency step at all;
3. hand-authored availability fixtures across the demo projects.

What every one of them has in common is `naive_availability` below: read the one
field that says an artifact came back, and write an availability state from it.
No field of the artifact's content is consulted, so nothing about the artifact's
subject, currency, completeness, or terms can change the answer.

The three do **not** all have the same facts behaviour, and this module carries
both shapes rather than averaging them:

* `naive_facts` -- the *plain* arm, which emits an availability document and
  nothing else. Groundings 1 and 3 have this shape: a graph edge that declares
  only an `evidence` feed contributes a tri-state and no fact, and a
  hand-authored availability fixture is an availability document by
  construction.
* `credulous_facts` -- the *credulous* arm, which emits the fact the pack asks
  about as well, asserted from existence alone. Grounding 2 has this shape:
  the Slack demo's `DRAFT_CONTRACT` asks a model for `"facts"` and `"evidence"`
  in the same JSON object, and the runtime's `Edge` likewise feeds an upstream
  disposition "as a fact, as evidence availability, or both".

Keeping both is what makes the README's fails-closed claim checkable instead of
asserted: the fact route closes the *omission* mode (the plain arm) and leaves
the *assertion* mode (the credulous arm) exactly where the evidence-only pack
left it. Both are recorded here as mappings. Neither is a defect report about
any of the three practices, and the README states each one's bound.
"""

# The pointer the fact-conditioned pack conditions on. The credulous arm knows
# it for the same reason the Slack demo's model knows it: it was shown the pack
# and asked to fill in a facts document. Knowing the pointer is not the failure
# being modelled -- asserting a value for it without checking the artifact is.
CREDULOUS_FACT_POINTER = "/agreement/executedGrants/onwardTransfer"


def naive_availability(artifact, requirement_id):
    """Map an acquired artifact to an availability document by existence alone.

    `found`     -> present   (a document came back, so the requirement is met)
    `not_found` -> absent    (the source says there is none on file)
    anything else -> unknown (the source did not answer)
    """

    status = artifact.get("status") if isinstance(artifact, dict) else None
    if status == "found":
        state = "present"
    elif status == "not_found":
        state = "absent"
    else:
        state = "unknown"
    return {requirement_id: state}


def naive_facts(artifact):
    """The plain naive arm derives no facts at all.

    Scope of the claim, stated exactly: *this function* returns an empty facts
    document for every artifact, and that models groundings 1 and 3 -- a graph
    edge carrying only an `evidence` feed, and a hand-authored availability
    fixture. It does **not** model grounding 2, whose drafting contract emits
    facts and availability together; `credulous_facts` models that one.

    Returning an empty facts document is therefore part of this arm, not a
    simplification of it -- and it is why a pack that states its predicate as a
    fact condition sees `unknown` rather than a wrong outcome under this arm.
    """

    return {}


def credulous_facts(artifact):
    """The credulous naive arm: assert the pack's fact from existence alone.

    Same existence test as `naive_availability`, applied to a fact instead of to
    an availability state: a document came back, so the grant the pack asks
    about is asserted true without any field of the document being read. If
    nothing came back there is nothing to assert and the facts document is
    empty.

    This is the fabrication direction the README names for availability tokens,
    written for facts: a caller who maps existence to `present` maps existence
    to whatever else is asked of it. Against this arm the fact-conditioned pack
    fails open exactly as the evidence-only pack does, which is why the
    fails-closed claim in the README is scoped to the omission mode.
    """

    status = artifact.get("status") if isinstance(artifact, dict) else None
    if status != "found":
        return {}
    facts = {}
    current = facts
    tokens = CREDULOUS_FACT_POINTER.split("/")[1:]
    for token in tokens[:-1]:
        current = current.setdefault(token, {})
    current[tokens[-1]] = True
    return facts
