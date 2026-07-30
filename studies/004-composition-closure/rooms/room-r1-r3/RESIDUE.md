# Residue

`relationships.graph.json` declares two nodes and **zero edges**.

The policy does relate these two decisions, so this is not a "no relationship exists" finding.
It is a "the relationship exists and this graph format cannot carry it" finding. Every sentence
that relates them is below, verbatim, with what I did instead.

## Why no edge is faithful (the finding that produced every entry below)

An edge in this format writes **the upstream node's outcome id, verbatim**, at a JSON Pointer in
the downstream node's facts document. There is no value mapping, no per-outcome selection, and no
edge that expresses sequencing without also injecting a value (the schema requires `fact` or
`evidence` on every edge).

The policy relates these two decisions through exactly one channel: **the order record's status**.
`r3` says taking the modify-items action sets the status to `'pending (items modifed)'`; `r1` denies
cancellation whenever the status is not `'pending'`. So the only candidate edge is one that feeds an
outcome id into the other node's `/order/status`. I built that edge and ran it. It fails three ways:

1. **It is wrong on the branch where nothing happened.** With `r3` → `r1` on `/order/status`, an
   `r3` disposition of `deny-item-modification` (probed: product-type change, order still `pending`)
   injects the literal string `deny-item-modification` as the order's status, so `r1`'s
   `deny-status-not-pending` fires and cancellation is denied. The policy permits that cancellation —
   the order was never modified. The reverse direction fails identically: an `r1` disposition of
   `deny-cancellation` (probed: reason `'changed my mind'`, order still `pending`) injects
   `deny-cancellation` as the status and denies the item modification, which the policy permits.
2. **It confuses permission with performance even when the conclusion looks right.** On the allow
   branch the composite reports `deny-cancellation`, which is the answer the policy gives *after the
   tool has been called*. But `allow-item-modification` means only "the agent may proceed to call the
   tool once". The edge would assert that *being permitted* to modify forecloses cancellation. The
   policy conditions that on the action having been **taken**.
3. **It replaces the order record rather than augmenting it.** An injected value never overwrites a
   caller's fact — supplying the true status alongside the edge is refused outright
   (`the facts document already carries a value at "/order/status"`, exit 3). So the edge does not
   add the consequence to a true status; it takes the status pointer over and states a value that is
   not a status at all. `r1`'s required evidence `order-status-check` is specifically "the order's
   current status, **retrieved from the order record**"; an outcome id is not that.

No other pointer helps. Every remaining `r1` fact path expects a boolean, a reason from a
two-value enum, or a payment-method type; every remaining `r3` fact path expects a boolean. An edge
aimed at a pointer no rule reads would change no disposition and declare no relationship. An
`evidence` edge is worse: it would claim that `r3` having resolved *is* the order-status check for
`r1`, which is false.

I could not modify the packs (the brief forbids it), and the faithful encoding would require either
a value-mapping edge (outcome → the status string `'pending (items modifed)'`) or a fact in `r1`
distinct from the order status, such as `/order/priorActions/itemsModified`. Neither exists.

Declaring zero edges leaves each pack's own status gate as the sole carrier of the relationship —
which is where the packs already put it, and which is correct when the caller supplies the order's
real status. The schema notes that `edges` is "required even when empty, so a single-node graph
states its emptiness rather than implying it"; the empty array here is that explicit statement, not
an omission. `result` names `cancel-pending-order` because the sentences below constrain
cancellation; with no edges it is only a headline echo and composes nothing.

---

## Entry 1 — the direct statement (modify-items forecloses cancellation)

> This action can only be called once, and will change the order status to 'pending (items modifed)'.

> The agent will not be able to modify or cancel the order anymore.

**What I did instead.** Nothing declared between the nodes. The first sentence is already carried
*inside* `r3` alone (rule `deny-when-items-already-modified`, `/order/status` equals
`'pending (items modifed)'`). Its cross-decision half — that the same status also forecloses `r1` —
is carried *inside* `r1` alone (rule `deny-status-not-pending`), reached only if the caller supplies
the true status to the `r1` node. The link between them stays implicit in the shared meaning of
`/order/status` and is **not** declared as an edge, for the three reasons above. Consequence for a
reader of this graph: evaluating the two nodes together tells you nothing about their interaction;
the composite's headline is `r1`'s own disposition against whatever status the caller states.

## Entry 2 — the converse statement (cancellation forecloses modification)

> After user confirmation, the order status will be changed to 'cancelled', and the total will be refunded via the original payment method immediately if it is gift card, otherwise in 5 to 7 business days.

**What I did instead.** Nothing declared. Read against `r3`'s status gate, a cancelled order can no
longer be modified — but the sentence states an *effect of the cancel action having been taken*, and
an edge from `r1` can only carry `r1`'s *permission* outcome. Probed and rejected: it denies
modification even when cancellation was denied and the order is untouched. The `'cancelled'` status
reaches `r3` only as a caller-supplied fact.

## Entry 3 — the single-use rule read across decisions

> Exchange or modify order tools can only be called once per order.

**What I did instead.** Left undeclared as a cross-node relationship. Its modify-items half is inside
`r3` (`deny-when-items-already-modified`). Its exchange half names a decision this project does not
declare — `jpack.json` declares only `r1` and `r3` — so there is no node to attach it to, and a
once-per-order constraint is state about the order's history rather than an outcome any declared
node produces.

---

## Sentences considered and deliberately **not** recorded as residue

- "Generally, you can only take action on pending or delivered orders." — constrains each decision
  against the order status; it does not relate the two decisions to each other. Both packs encode it
  (`deny-status-not-pending`, `deny-when-order-not-pending`).
- The remaining `Modify items` sentences (caution, completeness confirmation, price-difference
  payment) and the remaining `Cancel pending order` sentences (confirmation, acceptable reasons) are
  internal to one pack each and are already encoded there.
- The conversation-level rules (authentication, one user per conversation, explicit confirmation
  before a database update, one tool call at a time, transfer to a human agent) bind the agent, not
  these two decisions to each other. `r1` and `r3` both route unresolved cases to
  `transfer_to_human_agents` through their own `escalation` blocks.
