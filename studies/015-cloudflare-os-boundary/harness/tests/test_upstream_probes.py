"""The upstream-behavior probe suite, run as a registered part of the study's own suite.

Round 1 found `probes/upstream-probes.ts` defined a suite that nothing executed, so its
coverage was implied rather than delivered. It runs here, through the same bundler and
node the ceremony uses, and a failure fails the study's tests.

What it demonstrates: the exact `classifyTool` and `AutoApprovalDrainer` branches the
registry's controls and the s02 cell depend on; the portal's action-kind grammar; and the two
source facts PREREGISTRATION section 4c rests on (the pinned MCP connector opts out of
simulation; the generic contract blesses that opt-out). The adapter's *reproduction* of the tag
rule is compared against the pinned function in `test_study.py`, not here.
"""

import cf_runner


def test_upstream_probe_suite_passes(cfos_source):
    del cfos_source
    code, text = cf_runner.probe_suite()
    assert code == 0, text[-4000:]
    # Guard against a vacuously-empty suite: the count must be non-zero and complete.
    import re

    match = re.search(r"(\d+)/(\d+) upstream probes passed", text)
    assert match, text[-2000:]
    passed, total = int(match.group(1)), int(match.group(2))
    assert passed == total and total >= 10, text[-2000:]
