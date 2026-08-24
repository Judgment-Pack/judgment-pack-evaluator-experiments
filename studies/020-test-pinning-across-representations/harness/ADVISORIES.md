# Advisory register — findings recorded against the review-support apparatus

**What this file is.** `PREREGISTRATION.md` §4b registers two surfaces. The REGISTERED
surface — the preregistration, the policy prose, gold, the mutant corpora, the references,
the off-gold certificate, the arm prompts, the sealed reviewer set, and the harness's
scoring, driver, integrity, pins and manifest chain — is reviewed adversarially and gated:
a finding against it is a finding the freeze answers. The REVIEW-SUPPORT APPARATUS — the
currency suite, the ceremony tooling and the render machinery — has a registered purpose,
**drift detection under an honest operator**, which is not and cannot be a root of trust
against a maintainer attacking their own record. Findings against it are RECORDED here,
with their cites, and are not freeze gates.

**What recording is not.** An advisory is not a dismissal and not a disposition. It is the
maintainer stating, on the record and before the freeze, that a named weakness exists, that
it is reachable only by an operator who is editing the record they are also attesting, and
that the study's registered claims do not rest on it. Anyone reading this record later can
see the whole list and judge it. Every entry keeps the reviewer's severity as returned — an
advisory is not a downgrade of a finding, it is a statement about which surface the finding
lands on.

**Appendable by design.** This file grows by one entry whenever a review round lands a
finding on the review-support apparatus, including after the freeze — which is when a
recorded-not-gated weakness is most likely to be revisited. It is therefore excluded from
the exact-set manifest by named constant (`make_manifest.EXCLUDED_DOCUMENTS`, with its
reason, ADR 0004's own rule and the same treatment `DEVIATIONS.md` and `PREREG-REVIEW.md`
get), and `harness/tests/test_manifest.py` asserts the exclusion so a future widening fails
the suite rather than passing quietly.

**Line cites** name the function or the table rather than a line number, because 020's
harness is a PORT and every line moved. Where an inherited advisory cites Study 019's own
line numbers, they are 019's and stay 019's.

---

## Study 020's register opens EMPTY

**No advisory is on this study's record.** The four entries below the line are **Study
019's**, carried with the ported apparatus so a reviewer of 020 can see which known
weaknesses the machinery they are reading already has a recorded finding for. They are
recorded here as INHERITED CONTEXT and are not Study 020 dispositions: 020 has held no
review round (`harness/render_round_status.py` renders `0 review rounds are on the
record`), so it has returned no finding to record. A finding raised against Study 020's
review-support apparatus is appended ABOVE this line, with its own round number and cite,
and carries the reviewer's severity as returned.

**Nothing inherited below is a claim that the weakness is closed here.** Where 019's entry
names a mechanism this port changed — R9-6's status sentences, in particular, whose surface
list narrows to two under §7 delta 10 — the entry's reasoning must be re-made against 020's
bytes before it is relied on.

---

# Study 019's register, carried as inherited context

## R9-3 — MAJOR — the round-state schema accepts mistyped scalars

**None.** No review round has opened, so this study has recorded no advisory of its own.
The first entry lands when a round returns a finding whose only reachable exploit requires
the maintainer to edit the record they are attesting (§4b).

---

## Inherited from Study 019, and re-recorded because THE BYTES CARRY THEM

Study 019 closed its rounds with four advisories open against the review-support apparatus.
`harness/render_round_status.py` and the currency suite's `_live_lines()` are PORTED into
this study (`harness/PORTS.md`), so those findings are properties of bytes that are in this
tree now — and an advisory that stopped being recorded because the study number changed
would be a finding laundered by a port.

Each is re-recorded below by id, surface and mechanism, with 019's severity as the reviewer
returned it and 019's disposition unchanged: recorded, not gated, fix unadopted. **None of
them is re-verified here** — that would be this study claiming a measurement it did not
make. What is claimed is narrower and checkable: the code they were filed against was
carried, so the findings travel with it until a 020 round retires them.

| id | severity | surface | mechanism, in one line | still in the ported bytes? |
|---|---|---|---|---|
| **R9-3** | MAJOR | ceremony tooling / round-state block | the schema accepts mistyped scalars — `blockVersion: 1.0`, `findings.first: true` — because Python equates each with the integer `1`; re-verified open by 019's round 10 | yes: `render_round_status.py`'s block reader is ported unchanged apart from §7 delta 10's two registered changes |
| **R9-5** | MAJOR | currency suite | `_live_lines()` strips indentation when recognising closing fences, resumes after `-->` on a terminating line, and does not mask indented code, so an indented false fence closer or an `<!-- closed -->` prefix can manufacture live structure | yes: `_live_lines()` is carried verbatim into `harness/tests/test_prereg_currency.py` |
| **R9-6** | MAJOR | render machinery / front-door status sentence | `marker_span()` and `surface_problems()` read raw offsets, so a complete marker span inside a fenced block satisfies `--check` while presenting no sentence to a reader | yes, and 020 has TWO front doors rather than three, which narrows the surface and does not close it |
| **R9-7** | MINOR | ceremony tooling | `write()` validates and writes each surface inside one loop, so a valid first surface is rewritten before a malformed second one refuses | yes |

**Why they are still recorded rather than fixed.** §4b's rule has not changed: each of these
is reachable only by an operator editing the record they are also attesting, none of them
reaches a registered artifact, a published rate, a freeze pin or the decision, and every
reviewer's proposed fix is recorded in 019's own register unadopted. Recording is not
dismissal — it is the maintainer stating on the record, before the freeze, that a named
weakness exists and that no registered claim rests on it.

**What a 020 round may do with them.** Re-raise any of the four against this study's bytes,
in which case the finding gets a 020 id and a written disposition like any other; or adopt
a fix, in which case the row above moves to a "closed" section naming the commit. What a
round may NOT do is treat the port as having answered them.
