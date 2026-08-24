# Your task

Using the policy above, the naming appendix above, and the language reference above, produce two
artifacts:

1. **A Judgment Pack** — one JSON document that implements the policy, declaring `specVersion`
   `"0.2.0-draft"`. Evaluated with the facts and evidence availability of a case, it should reach
   the determination the policy text states for that case.
2. **A test matrix** — one JSON document declaring `matrixVersion` `"2"`, whose `cases` state, per
   case, the disposition the policy text yields. You derive each `expectedDisposition` from the
   policy text yourself; nothing here tells you which cases to write or what they should expect.

Answer in a single message. No tools are available, and there is no opportunity to revise: what
you write is what will be evaluated.

## Output format

Your completion must contain, in this form:

- a line consisting of `PACK:`, followed immediately by a fenced code block tagged `json`
  containing the complete pack document, and nothing else;
- a line consisting of `MATRIX:`, followed immediately by a fenced code block tagged `json`
  containing the complete matrix document, and nothing else.

~~~text
PACK:
```json
{ ... the pack ... }
```

MATRIX:
```json
{ ... the matrix ... }
```
~~~

Each fenced block must hold one JSON document on its own — no comments, no commentary inside the
fence, no ellipses, no placeholder. Anything you want to say about your work goes outside the two
blocks.

If a marker line appears more than once, **the last occurrence of that marker governs**: the
block extracted is the one immediately following the final `PACK:` line, and likewise for the
final `MATRIX:` line.
