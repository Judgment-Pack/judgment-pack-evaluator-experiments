<!-- Study 019 prompt suffix, arm B. Assembled prompt = policy prose + naming appendix + rego-excerpt.md + this file.
    Assembly rule: HTML comments are stripped from every material before the assembled prompt is shown to an author. -->
<!-- SHARED:1:begin -->
# Your task

Working from the policy stated above, author both of the following.

**(a) One Rego v1 policy** that implements that policy. Put the whole policy in the package
`study`, and make the decision entrypoint the rule `decision`, so that the policy's answer
for a case is the value of `data.study.decision` when that case is supplied as `input`. The
shape of `input` is the one given in the naming appendix.

**(b) OPA tests** for that policy, in a separate file. Write them as `test_`-prefixed rules
that supply a case with `with input as {...}` and assert the value of the entrypoint. Cover
the cases you consider decisive for showing that your policy is faithful to the prose; there
is no required number of tests.

Both files are saved side by side in one directory and run with the pinned OPA v1.19.0
binary (Rego v1 is its default dialect): the policy is evaluated per case, and the tests are
run with `opa test .`. Use only ordinary language constructs and built-in functions — no
built-in that reads the clock, the network, or a source of randomness is available.

Everything you need to know about the decision the policy makes is in the prose above. The
material below fixes only the form of the answer.
<!-- SHARED:1:end -->

<!-- EMBED:begin -->
<!-- GENERATED FILE. Do not edit by hand; regenerate with deformalize.py. -->

# What your policy must produce (arm B)

Your policy must produce a decision object. It must have a disposition field, and its value is one of "approve", "review", "enhanced-review", "reject" or "unresolved". It must have a reasons field, which is a list whose entries are drawn from "missing-required-evidence", "unknown", "no-match" and "exception-escalation". When the disposition is "unresolved", the reasons list has at least one entry. When the disposition is anything other than "unresolved", the reasons list is empty. It has no fields other than "disposition" and "reasons".

Use those field names and those values exactly as spelled here.
<!-- EMBED:end -->

<!-- SHARED:2:begin -->
# Output format

Reply with exactly two blocks, in this order:

1. a line containing only `POLICY:`, immediately followed by a fenced code block tagged
   `rego` containing the complete policy file;
2. a line containing only `TESTS:`, immediately followed by a fenced code block tagged
   `rego` containing the complete test file.

Like this:

    POLICY:
    ```rego
    package study

    # ... your policy ...
    ```

    TESTS:
    ```rego
    package study_test

    # ... your tests ...
    ```

Each fenced block must be a complete, self-contained Rego file, starting with its own
`package` line. You may write whatever explanation you like outside the two blocks; it is
not read. If a marker line appears more than once, **the last occurrence of each marker
governs** — so if you revise your answer, emit the marker and its block again at the end.
<!-- SHARED:2:end -->
