from __future__ import annotations

from pathlib import Path

import pytest

from jps_evaluator import (
    EvaluationError,
    canonicalize_disposition,
    evaluate,
    load_json_file,
)


CORPUS_DIR = (
    Path(__file__).parents[2] / "reference" / "conformance-evaluation"
)
MANIFEST = load_json_file(CORPUS_DIR / "manifest.json")
CASES = MANIFEST["cases"]


def _fixture_path(case: dict) -> Path:
    declared = CORPUS_DIR / case["pack"]
    if declared.is_file():
        return declared
    # This clean-room snapshot places its supplied fixture beside the manifest,
    # while the manifest retains the upstream packs/<name>.json spelling.
    return CORPUS_DIR / Path(case["pack"]).name


def test_corpus_version_and_case_count_are_pinned():
    assert MANIFEST["suiteVersion"] == "0.2.0-draft"
    assert MANIFEST["specVersion"] == "0.2.0-draft"
    assert len(CASES) == 20


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_corpus_case_matches_canonical_bytes_or_error_contract(case):
    pack_path = _fixture_path(case)
    if not pack_path.is_file():
        pytest.xfail(
            "reference snapshot omits the manifest-declared pack fixture "
            f"{case['pack']!r}"
        )

    pack = load_json_file(pack_path)
    evidence = case.get("evidenceAvailability")
    work_limit = case.get("workBudget")
    kwargs = {}
    if work_limit is not None:
        # No 0.2.0-draft row uses this optional carrier member.
        kwargs["evaluation_work_limit"] = int(work_limit.lexeme)

    if "expectedDisposition" in case:
        disposition = evaluate(
            pack,
            case["facts"],
            evidence,
            case["supportedExtensions"],
            **kwargs,
        )
        assert canonicalize_disposition(disposition) == canonicalize_disposition(
            case["expectedDisposition"]
        )
        return

    with pytest.raises(EvaluationError) as raised:
        evaluate(
            pack,
            case["facts"],
            evidence,
            case["supportedExtensions"],
            **kwargs,
        )
    assert raised.value.error_class == case["expectedErrorClass"]
    if "expectedErrorPhase" in case:
        assert raised.value.phase == case["expectedErrorPhase"]
