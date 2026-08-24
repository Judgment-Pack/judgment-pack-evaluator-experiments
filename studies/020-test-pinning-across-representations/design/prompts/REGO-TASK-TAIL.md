<!--
DESIGN DRAFT, NOT REGISTERED. Study 019 arms B and C, shared task tail (output form).
BYTE-IDENTICAL in both arms' prompts.
-->

## Required output form

Think and explain as much as you like first; only the blocks below are read. End your reply
with **exactly** these two blocks, in this order:

    POLICY:
    ```rego
    <the complete policy file>
    ```

    TESTS:
    ```rego
    <the complete test file>
    ```

- The marker is a line on its own containing exactly `POLICY:` (and exactly `TESTS:`),
  immediately followed by a fenced block.
- The fence may be ```` ```rego ```` or a bare ```` ``` ````.
- If a marker appears more than once, **the last one is the one read**. Everything outside
  these two blocks is ignored.
- Each block must contain one complete file and nothing else — no prose outside comments, no
  ellipsis, no placeholder, no second package.
