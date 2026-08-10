"""The upstream-behavior probe suite, run as a registered part of the study's own suite.

Round 1 found `probes/upstream-probes.ts` defined a suite that nothing executed, so its
coverage was implied rather than delivered. It runs here, through the same bundler and
node the ceremony uses, and a failure fails the study's tests.

What it demonstrates: the exact `classifyTool` and `AutoApprovalDrainer` branches the
registry's controls and the s02 cell depend on; that the adapter's reproduction of the
platform's action-kind rule agrees with upstream's own `actionKindFor`; and the two source
facts PREREGISTRATION section 4c rests on (the pinned MCP connector opts out of simulation;
the generic contract blesses that opt-out).
"""

import cf_runner


def test_upstream_probe_suite_passes(cfos_source):
    del cfos_source
    code, text = cf_runner.probe_suite()
    assert code == 0, text[-4000:]
    assert "upstream probes passed" in text
