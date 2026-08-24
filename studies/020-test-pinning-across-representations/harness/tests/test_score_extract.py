"""The registered marker rule, and the three properties of it that decide runs.

Section 3 registers the rule in one sentence; each clause of that sentence is a
way a scorer can quietly score the wrong bytes, so each gets a case here.
"""
import pytest

from e4lib import extract


def completion(*parts):
    return "\n".join(parts) + "\n"


def test_the_arms_markers_are_the_registered_pairs():
    """Section 3: `PACK:`/`MATRIX:` for A, `POLICY:`/`TESTS:` for B/C."""
    assert extract.ARM_MARKERS["A"][0] == "PACK"
    assert extract.ARM_MARKERS["A"][2] == "MATRIX"
    for arm in ("B", "C"):
        assert extract.ARM_MARKERS[arm][0] == "POLICY"
        assert extract.ARM_MARKERS[arm][2] == "TESTS"
        assert extract.ARM_MARKERS[arm][1] == "rego"


def test_a_plain_block_is_extracted():
    text = completion("PACK:", "```json", '{"a": 1}', "```")
    block, why = extract.extract_block(text, "PACK", "json")
    assert why is None
    assert block == '{"a": 1}\n'


def test_the_last_occurrence_governs():
    """An author that emits a draft and then a final block is scored on the
    final one. A scorer taking the first would score the draft."""
    text = completion("PACK:", "```json", '{"draft": true}', "```",
                      "on reflection:", "PACK:", "```json", '{"final": true}',
                      "```")
    block, _why = extract.extract_block(text, "PACK", "json")
    assert block == '{"final": true}\n'


def test_blank_lines_between_marker_and_fence_are_not_prose():
    text = completion("POLICY:", "", "", "```rego", "package study", "```")
    block, why = extract.extract_block(text, "POLICY", "rego")
    assert why is None and block == "package study\n"


def test_prose_between_marker_and_fence_means_the_marker_does_not_govern():
    """…and the search falls back to an EARLIER marker rather than reaching
    forward past the prose."""
    text = completion("POLICY:", "```rego", "package earlier", "```",
                      "POLICY:", "here it is:", "```rego", "package later",
                      "```")
    block, _why = extract.extract_block(text, "POLICY", "rego")
    assert block == "package earlier\n"


def test_a_foreign_info_string_is_not_the_expected_artifact():
    """A ```python block under POLICY: is not a Rego policy, and admitting it
    would file a language error as a policy defect."""
    text = completion("POLICY:", "```python", "print(1)", "```")
    block, why = extract.extract_block(text, "POLICY", "rego")
    assert block is None and why == extract.NO_MARKER


def test_an_empty_info_string_is_accepted():
    text = completion("POLICY:", "```", "package study", "```")
    block, why = extract.extract_block(text, "POLICY", "rego")
    assert why is None and block == "package study\n"


def test_an_unterminated_fence_does_not_govern_and_is_not_repaired():
    """Section 3: single-shot, no repair. An unterminated fence is an artifact
    the author did not finish emitting; inventing a terminator would be repair."""
    text = completion("PACK:", "```json", '{"first": 1}', "```",
                      "PACK:", "```json", '{"second": 2}')
    block, _why = extract.extract_block(text, "PACK", "json")
    assert block == '{"first": 1}\n'


def test_no_marker_at_all_is_the_registered_code():
    block, why = extract.extract_block("nothing here\n", "PACK", "json")
    assert block is None and why == "no-marker-block"


def test_extract_pair_returns_both_artifacts_under_one_rule():
    text = completion("PACK:", "```json", '{"pack": 1}', "```",
                      "MATRIX:", "```json", '{"cases": []}', "```")
    pair = extract.extract_pair(text, "A")
    assert pair["policy"] == '{"pack": 1}\n'
    assert pair["suite"] == '{"cases": []}\n'
    assert pair["policyCode"] is None and pair["suiteCode"] is None
    assert pair["suiteBytes"] == len('{"cases": []}\n'.encode("utf-8"))


def test_extract_pair_reports_an_absent_suite_as_absent():
    """The prototype's `secondaryArtifact.present` said `true` while the file on
    disk was absent; returning both from one call makes the record a
    description of what this function returned."""
    text = completion("PACK:", "```json", '{"pack": 1}', "```")
    pair = extract.extract_pair(text, "A")
    assert pair["suite"] is None
    assert pair["suiteCode"] == extract.NO_MARKER
    assert pair["suiteBytes"] == 0


def test_an_unknown_arm_refuses():
    with pytest.raises(KeyError):
        extract.extract_pair("", "D")
