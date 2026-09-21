# Staged evaluation rows (vendored)

The specification's **staged** evaluation rows, copied byte for byte from
`conformance/evaluation/staged/` in
[judgment-pack-spec](https://github.com/Judgment-Pack/judgment-pack-spec) at the commit
[`provenance.json`](provenance.json) names. They are the five rows RFC 0013 proposed: the first to
use `expectedErrorClass`, two of them inputs to which more than one Core §8.4 class applies.

**They are in no corpus.** No `suiteVersion` contains them, no claim of evaluator conformance may
cite them, and the specification's own README for that directory says so first. They are vendored
here for one purpose: `harness/error_class_agreement.py` runs them through both evaluators to
check that the two report the same §8.4 class for the same inputs, which the frozen corpus beside
this directory ([`../conformance-evaluation/`](../conformance-evaluation/)) cannot check, because
none of its twenty rows expects an error.

A staged row may still change, or be withdrawn, in the specification. `provenance.json` records the
SHA-256 of each file, and a test holds the files to it, so an edit here is either a deliberate
re-vendoring from a named specification commit or a failing test. The shape to refuse is the same
as for the runtime pin: a row's expectation changed in the same commit as an implementation, which
is indistinguishable from making the evidence agree by moving what it was evidence about.

To re-vendor: copy each file with `git show <commit>:conformance/evaluation/staged/<file>`, update
`specCommit` and the digests, and say in the pull request what the specification changed.
