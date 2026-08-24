# Deviations — Study 020

Deviations from the frozen preregistration land here with a reason and a date — never by editing
the preregistration or any frozen artifact. **Nothing is frozen yet**, so nothing here is a
deviation: before the freeze, a change is a revision of a draft and belongs in the document
itself, under review.

This file is **outside the freeze set** by design, per ADR 0004's appendable-files rule and Study
018's lesson (018's `DEVIATIONS.md` was inside its freeze set and had to move out). It is excluded
from the exact-set manifest by named constant in `harness/make_manifest.py`, with an asserting
test, precisely so that recording a deviation can never stale the manifest.

**Freeze commit:** *(not yet — named by reference in `PREREGISTRATION.md` as the squash-merge
commit of the freeze PR on `main`)*.

## Entries that this study's registered rules will route here

Named in advance so a reader knows what a silent absence would mean. Each is registered in
`PREREGISTRATION.md` at the section cited.

| Trigger | Registered at | What the entry must carry |
|---|---|---|
| Adding a member to the eighteen-member sensitivity family after registration (removal is forbidden) | §5.2 | the member, the arm-blind reason, and **the pre-addition verdict published beside the post-addition one** |
| A second calibration pilot | §2a.6 | the reason; thereafter the derived threshold is the **maximum** over all pilots and the transfer bands the **tightest**, with every pilot's rates side by side |
| Raising the pre-pilot sweep's 27-call cap | §2.1 | the reason and the republished price |
| A post-freeze registry re-pin | §1a | the halt-and-restart record and the abandoned slots with their codes |
| Moving the identity gate from `referenceIdentity` to the conjunction with `ownPolicyIdentity` | §1.2, §11.10 | the obligation to re-derive every per-protocol member's population and §5.6's dispersion |
| Reinstating an author-side control gate | §2a.4, §5.7 | the stimulus degradation's computed per-arm miss-count shift **published before the pilot runs**, the authoring-call budget, and the realised-n arithmetic gap |
| Crossing the registered batch window | §2 | the window actually used and the cause |
| A corrected or retracted R1 | §10 | the entry, plus a banner at the head of `ANALYSIS.md`, per `CORRECTION-TARGETS.md` |

*(No entries.)*
