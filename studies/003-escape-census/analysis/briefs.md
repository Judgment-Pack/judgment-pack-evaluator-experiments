# Run provenance — the two reader briefs, verbatim, with run metadata

The 25/25 expressibility agreement in this directory is agreement between **two separate blinded
model runs under author-written briefs, in isolated contexts** — not between independent human
experts. This file records exactly what each run was told and what produced it, so the
characterization can be checked instead of trusted.

| | Run 1 (`shapes-classifier-1.json`) | Run 2 (`shapes-classifier-2.json`) |
| --- | --- | --- |
| Model | Anthropic `claude-opus-5` | Anthropic `claude-opus-5` |
| Date | 2026-07-27 | 2026-07-27 |
| Context | Isolated workflow subagent (structured-output schema), evidence phase of the RFC-drafting workflow — ran **before** any RFC draft existed | Isolated asynchronous subagent, ran **after** a draft existed and was explicitly barred from reading it |
| Brief author | The RFC 0008 author | The RFC 0008 author |

Both briefs were written by the same person, and the **adjudicator of the three shape
disagreements was Anthropic `claude-fable-5`** — the session that also directed the RFC drafting.
Same-vendor runs plus a same-session adjudicator is the weakest link in this record, and it is why
the analysis claims output agreement, not independence.

## Brief 1 — verbatim

Authored as a JavaScript template literal in the drafting workflow's script; `${CENSUS}` resolved
to this study's directory and `${CONTEXT}` to the repository-orientation block reproduced after it.

```
Sub-classify EVERY collection-quantification prepared-determination from the
census — all 25 of them — by the construct actually needed. Read ${CENSUS}/measurement/adjudicated.json
(device == "collection-quantification") and, for each, the producing room's FACTS-LEDGER.md and pack.json
to understand precisely what the upstream computation does.

Shapes:
- element-predicate: exists/every element satisfying a predicate over THAT ELEMENT's own fields only
  (e.g. "any segment has status cancelled-by-airline", "every item is available").
- uniformity: all elements equal at some sub-path (e.g. "cabin class uniform across flights").
- cross-collection-membership: every/some element of list A is a member of list B (a join).
- pairwise-cross-list: element-by-element comparison of two lists (e.g. "proposed segments preserve
  origin of stored segments").
- count / cardinality-exact: number of (matching) elements compared to a bound.
- other: describe.

Then say which are expressible with (a) a bare exists/every quantifier whose inner predicate sees only
the element, (b) a dedicated uniformity op, (c) neither. Also scan the 12 rooms' RESIDUE.md for
residues that a quantifier would have prevented, and note them. Output exact counts — the RFC's
honesty depends on these numbers. ${CONTEXT}
```

The interpolated `${CONTEXT}` block:

```
Repos (read-only for you unless told otherwise):
  Spec: /home/onword/repo/judgment-pack/judgment-pack-spec — normative core at spec/judgment-pack-core.md (§7 conditions incl. three-valued
  logic, §7.4 fact conditions, §8 resolution), RFC process at rfcs/0000-rfc-process.md, house style
  in rfcs/0001..0007, non-goals at docs/non-goals.md (excludes a general-purpose query/rules
  language).
  Census: <this study's directory> — RESULTS.md (D1 12/12, quantification 25/40), measurement/adjudicated.json
  (per-fact classifications with notes), rooms/<id>/ (the 12 packs + FACTS-LEDGER.md + RESIDUE.md).
The proposal under construction: bounded collection quantifiers for JPS — new condition ops that
test a predicate over the elements of an array-valued fact, WITHOUT arithmetic and WITHOUT becoming
a query language. Prior art in this project: RFC 0007 question D (upgraded by the census) proposes
exactly this and defers the count-shaped cases.
```

Note the disclosure this implies: brief 1 named the proposal under construction (a quantifier RFC),
so run 1 was blind to any draft text but **not** blind to the design direction. Brief 2 was written
to be more neutral on both counts.

## Brief 2 — verbatim

```
You are an independent classifier in a measurement exercise. Work ONLY from the files named here; do not read any RFC drafts, any files under /tmp, or anything outside the paths given. Do not speculate about what other classifiers found — you are the independent second reading.

Corpus: /home/onword/repo/judgment-pack/judgment-pack-evaluator-experiments/studies/003-escape-census/
- measurement/adjudicated.json — the adjudicated census. Select every fact with device "collection-quantification" (there are 25).
- rooms/<id>/FACTS-LEDGER.md and rooms/<id>/pack.json — read the producing room's ledger entry and pack usage for each selected fact to understand precisely what the upstream computation does.

Reference for expressibility judgments: /home/onword/repo/judgment-pack/judgment-pack-spec/spec/judgment-pack-core.md §7 (conditions: literal/all/any/not/fact/evidence-present; fact conditions compare a value at an RFC 6901 pointer against a LITERAL; three-valued logic).

Classify EACH of the 25 facts into exactly one SHAPE:
- element-predicate: exists/every element satisfying a predicate over THAT ELEMENT's own fields only (no reference to other elements, other collections, or outer facts).
- uniformity: all elements equal at some sub-path (set-of-values-has-one-member tests).
- cross-collection-membership: every/some element of list A must be a member of list B (a join).
- pairwise-cross-list: element-by-element comparison of two lists (aligned or cross-product).
- count: number of (matching) elements compared to a bound (at most N, at least N).
- cardinality-exact: exactly-N tests.
- other: none of the above — describe what it actually needs.

And for each, judge EXPRESSIBLE_WITH, strictly:
- exists-every: expressible by a bounded exists/every condition over an array-valued fact pointer whose inner predicate is a §7 condition tree seeing ONLY the element as document root (fact paths element-rooted, comparisons against literals only).
- uniform: expressible by a dedicated all-elements-equal-at-sub-path operator (empty and singleton arrays vacuously true).
- neither: needs more (counts, joins, comparing two fields, ordinal selection, outer-scope access, emitting a value...). Name the specific blocker.

Be strict: if the predicate must compare an element field against ANOTHER fact or another element rather than a literal, it is NOT exists-every-expressible.

Return ONLY a JSON object (no prose around it):
{"cases":[{"room":"A1","pointer":"/booking/...","shape":"...","expressible_with":"...","blocker_or_note":"..."}], "counts":{"element-predicate":N,"uniformity":N,"cross-collection-membership":N,"pairwise-cross-list":N,"count":N,"cardinality-exact":N,"other":N,"exists-every":N,"uniform":N,"neither":N}}
Cover all 25; use the exact pointer strings from adjudicated.json.
```

(Brief 2 split `count` / `cardinality-exact` into separate buckets and defined the shapes in its own
words, but the taxonomy is structurally brief 1's — unavoidable, since one author wrote both.)
