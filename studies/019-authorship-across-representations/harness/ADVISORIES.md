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

**Line cites** are against the commit the round read (`b7e755a`, round 9's opening commit)
and are not re-anchored as the files move; the surrounding text names the function or table
so an entry stays findable.

---

## R9-3 — MAJOR — the round-state schema accepts mistyped scalars

**Surface:** review-support (ceremony tooling / round-state block).
**Status:** OPEN, recorded.

Despite round-8 finding R8-4's "mistyped members" disposition, `blockVersion: 1.0`,
`findings.first: 1.0` and `findings.first: true` all parse successfully, because Python
equates each of them with the integer `1`: the guard tests the VALUE and, for
`blockVersion`, only the boolean type.

- `harness/render_round_status.py:212` — `block["blockVersion"] != 1 or isinstance(…, bool)`
- `harness/render_round_status.py:250` — the `findings` object's member check
- `PREREG-REVIEW.md:690` — the R8-4 disposition this leaves partial

**Reviewer's fix, recorded unadopted:** require non-boolean integers for both fields, and
add `1.0`, `1e0` and `true` mutations to the suite.

**Why recorded:** a mistyped scalar in the round-state block changes no registered claim,
no published rate and no freeze pin; it changes the block's own strictness, and reaching it
requires editing the block. Under §4b that is the honest-operator drift surface.

## R9-5 — MAJOR — the shared liveness helper can manufacture live structure

**Surface:** review-support (currency suite).
**Status:** OPEN, recorded.

`_live_lines()` strips all indentation when recognizing closing fences, resumes parsing
after `-->` on the terminating line of an HTML block, and does not mask indented code. Its
row and heading consumers then strip and count whatever it returns.

- `harness/tests/test_prereg_currency.py:1151` — `_live_lines()`
- `harness/tests/test_prereg_currency.py:1330` — the disposition-row consumer
- `harness/tests/test_prereg_currency.py:2288` — the required-heading consumer

Three constructions were demonstrated: a four-space-indented false fence closer made all
round-8 rows sitting inside a code block count as dispositions; prefixing the real R8-1 row
with `<!-- closed -->` left round 8 complete although CommonMark renders that whole line as
raw HTML; and required headings inside indented code pass the same way.

**Reviewer's fix, recorded unadopted:** use a CommonMark-aware block lexer — or implement
fence indentation, whole-line HTML termination and indented-code masking correctly — with
line-stable output for the Setext lookahead.

**Why recorded:** each construction is an edit to the review record made by the person
whose review record it is, in order to make the record's own currency test read a
completion that the rendered document does not show. No registered artifact, payload or
published number is reachable through it.

## R9-6 — MAJOR — the required status sentences may be structurally inactive

**Surface:** review-support (render machinery / front-door status sentence).
**Status:** OPEN, recorded.

`marker_span()` and `surface_problems()` operate on raw byte offsets and flattened text
without checking Markdown context, so a complete marker span placed inside a fenced code
block — or inside an invisible raw `<script type="text/plain">` block — yields
`surface_problems() == []` and `--check == 0` while the three front doors do not present
the required status sentence to a reader.

- `harness/render_round_status.py:353` — `marker_span()`
- `harness/render_round_status.py:378` — `surface_problems()`
- `PREREG-REVIEW.md:9` — the registration these enforce ("three front doors … carry ONE
  sentence rendered from this block")

**Reviewer's fix, recorded unadopted:** require BEGIN, payload and END to occupy a live
top-level Markdown context; add fenced-code and raw-HTML constructions to the suite.

**Why recorded:** the status sentence is a navigational courtesy rendered from the
round-state block; the block itself, not the sentence, is the data, and hiding the sentence
is an edit to the three documents by their own author. Nothing in the decision, the scoring
chain or the freeze set reads it.

## R9-7 — MINOR — `--write` is not preflighted across all surfaces

**Surface:** review-support (ceremony tooling).
**Status:** OPEN, recorded.

`write()` validates and immediately writes each surface inside one loop, so with
stale-but-valid README markers and reversed markers in the second surface, `README.md` was
rewritten before the command refused. The existing test makes the FIRST surface malformed
and therefore cannot see the ordering.

- `harness/render_round_status.py:420` — `write()`
- `harness/tests/test_prereg_currency.py:2188` — the test that misses it

The refusal remains nonzero and no malformed bytes are overwritten, which is why the
reviewer rated it MINOR.

**Reviewer's fix, recorded unadopted:** read, validate and stage all surfaces before
writing any.

**Why recorded:** the failure mode is a partially re-rendered set of status sentences after
a refused ceremony command, repaired by running the command again once the markers are
fixed. It cannot reach an artifact the manifest covers.
