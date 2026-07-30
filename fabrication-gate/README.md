# Receipt-required admission gate — the fabrication-elimination capstone

Layer 5 of the trustworthy-input-acquisition line ([ADR-0002](../docs/adr/0002-trustworthy-input-acquisition-research-line.md),
item 3): **admission**, the step that wires the attestation core (item 1) and the portable derivation
rule (item 2) into one gate and answers the line's sharpest question — *does receipt-required
admission eliminate fabrication?*

## The failure it targets

Across studies 005–007, every failure a model reached was a *rejected* envelope except one, which
reached a wrong **decision**: a source returns `not_found`, and the model authors a fabricated
`matchCount: "0"` into the facts, turning "we have no record" into a confident "screened clear."
That is the one failure worth eliminating structurally, because it is the one that decides wrong
rather than refusing.

## What the gate does

[`gate.py`](gate.py) makes the facts and evidence a pack evaluates be **exactly** the derivation
(item 2) over the bytes a named authority attested (item 1) for the acquisition — and nothing a
caller supplies. `admit()` has no facts or evidence parameter at all; its return **is** the
evaluator's input. So the fabricated fact has no path to evaluation, closed three ways at once,
each demonstrated in [`test_gate.py`](test_gate.py):

- **Author** — the model cannot write the fact, because the derivation is mechanical. A `not_found`
  artifact derives `absent`, no `matchCount`; the fabricated `"0"` is not, and cannot be, produced.
- **Tamper** — a fabricator who edits the retained `not_found` bytes to forge a clear record makes
  the artifact no longer re-digest to its signed `resultDigest`; the store fails verification and
  the gate refuses.
- **Forge** — a fabricator who writes a fresh receipt for a fabricated clear artifact cannot produce
  a valid HMAC without the attestation key; the store fails verification under the real key.

The end-to-end test runs the **real acquisition proxy** wrapping a synthetic screening source that
genuinely has no record, and shows the gate admits only `absent` across the whole pipeline. A
baseline-contrast test shows the study-005 world — where the model authors the facts document —
admitting the very `matchCount: "0"` the gate never produces.

## The finding, stated plainly

Under receipt-required admission, an admitted fact is a deterministic function of bytes a named
authority attested; a fabricated fact has no author-, tamper-, or forge-path to evaluation. This is
the strongest thing the line demonstrates, and it is demonstrated **deterministically** — the
property is architectural, so it is shown with a wired pipeline and a test, not model trials.

## What it does not claim

- **Byte-lineage, not truth.** An admitted fact derives from attested bytes; it does not follow that
  those bytes are correct, current, or complete. A source that lies under attestation is not caught
  here — that is out of scope for the whole line (ADR-0002).
- **Not an efficacy result.** This shows the architecture *forecloses* the fabrication path; it does
  not measure whether a model in the loop is more accurate, faster, or more useful, and it is not a
  preregistered efficacy study. A model-in-the-loop version — does an agent, given this pipeline,
  still find some other way to a wrong decision? — would be a separate preregistered study, and the
  efficacy question is one this project is the wrong author of (ADR-0002; repo README).
- **Same-UID / whole-session residuals stand.** The gate inherits item 1's boundary: it assumes the
  operator controls the key and store, and does not by itself detect whole-session replay or
  final-tail rollback (the hosted gateway's job).

## Run

```bash
python3 -m unittest test_gate -v
```

Standard library only. Imports the attestation core from `../acquisition-proxy` and the derivation
rule from `../derivation-rule`; both must be present (they are, on `main`).
