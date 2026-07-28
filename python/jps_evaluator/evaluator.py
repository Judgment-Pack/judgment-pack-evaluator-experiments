"""RFC 0006 evaluation with an explicitly opt-in RFC 0008 prototype."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping

from .conditions import (
    DEFAULT_EVALUATION_WORK_LIMIT,
    EvaluationBudget,
    TriValue,
    _pointer_tokens,
    evaluate_condition,
    is_decimal_string,
)
from .errors import EvaluationInputError, PointerSyntaxError, UnsupportedExtensionError
from .json_input import normalize_json


_LOCAL_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_CORE_CONDITION_OPS = {"literal", "all", "any", "not", "fact", "evidence-present"}
_RFC0008_AGGREGATE_OPS = {"exists", "every", "uniform"}
_FACT_OPERATORS = {
    "equals",
    "not-equals",
    "greater-than",
    "greater-than-or-equal",
    "less-than",
    "less-than-or-equal",
    "in",
}
_ORDERED_OPERATORS = {
    "greater-than",
    "greater-than-or-equal",
    "less-than",
    "less-than-or-equal",
}
_TRIGGERS = {
    "not-applicable",
    "missing-required-evidence",
    "unknown",
    "conflict",
    "no-match",
}
_REASON_ORDER = {
    "not-applicable": 0,
    "missing-required-evidence": 1,
    "unknown": 2,
    "conflict": 3,
    "no-match": 4,
    "exception-escalation": 5,
}


@dataclass(frozen=True)
class _PackView:
    applicability: dict[str, Any] | None
    requirements: tuple[dict[str, Any], ...]
    requirement_ids: frozenset[str]
    outcomes: frozenset[str]
    rules: tuple[dict[str, Any], ...]
    exceptions: tuple[dict[str, Any], ...]
    fallback: str | None
    escalation: dict[str, Any] | None


def evaluate(
    pack: Any,
    facts: Any,
    evidence: Any = None,
    supported_extensions: Iterable[str] = (),
    *,
    enable_rfc0008: bool = False,
    evaluation_work_limit: int = DEFAULT_EVALUATION_WORK_LIMIT,
) -> dict[str, Any]:
    """Evaluate one conformant pack and return an experimental disposition.

    RFC 0008 aggregate operators are accepted only when ``enable_rfc0008`` is
    explicitly true. Invalid inputs, structural aggregate-depth violations, and
    unsupported required extensions raise EvaluationError subclasses.
    """

    if not isinstance(enable_rfc0008, bool):
        raise EvaluationInputError("enable_rfc0008 must be a Boolean")
    normalized_pack = normalize_json(pack, source="pack")
    normalized_facts = normalize_json(facts, source="facts")
    normalized_evidence = (
        {} if evidence is None else normalize_json(evidence, source="evidence availability")
    )
    supported = _normalize_supported_extensions(supported_extensions)
    view = _prepare_pack(
        normalized_pack,
        supported,
        enable_rfc0008=enable_rfc0008,
    )
    evidence_states = _prepare_evidence(normalized_evidence, view.requirement_ids)
    budget = EvaluationBudget(evaluation_work_limit)

    if view.applicability is None:
        applicability = TriValue.TRUE
    else:
        applicability = evaluate_condition(
            view.applicability,
            normalized_facts,
            evidence_states,
            budget=budget,
            enable_rfc0008=enable_rfc0008,
        )
    if applicability is TriValue.FALSE:
        return _make_disposition(
            "not-applicable",
            reasons={"not-applicable"},
            escalation=view.escalation,
        )
    if applicability is TriValue.UNKNOWN:
        return _make_disposition(
            "unresolved", reasons={"unknown"}, escalation=view.escalation
        )

    reasons: set[str] = set()
    absent_required = False
    unknown_required = False
    for requirement in view.requirements:
        if not requirement["required"]:
            continue
        state = evidence_states.get(requirement["id"], "unknown")
        absent_required = absent_required or state == "absent"
        unknown_required = unknown_required or state == "unknown"
    if absent_required:
        reasons.add("missing-required-evidence")
    elif unknown_required:
        reasons.add("unknown")

    suppressed_rules: set[str] = set()
    forced_outcomes: set[str] = set()
    direct_escalation = False
    for exception in view.exceptions:
        result = evaluate_condition(
            exception["when"],
            normalized_facts,
            evidence_states,
            budget=budget,
            enable_rfc0008=enable_rfc0008,
        )
        if result is TriValue.UNKNOWN:
            if exception["onUnknown"] == "escalate":
                reasons.add("unknown")
            continue
        if result is TriValue.FALSE:
            continue
        effect = exception["effect"]
        if effect == "suppress-rule":
            suppressed_rules.add(exception["targetRule"])
        elif effect == "force-outcome":
            forced_outcomes.add(exception["outcome"])
        else:
            direct_escalation = True

    if direct_escalation:
        reasons.add("exception-escalation")
    if len(forced_outcomes) > 1:
        reasons.add("conflict")
    if reasons:
        return _make_disposition(
            "unresolved",
            reasons=reasons,
            escalation=view.escalation,
            direct_escalation=direct_escalation,
        )
    if len(forced_outcomes) == 1:
        return _make_disposition("outcome", outcome_id=next(iter(forced_outcomes)))

    candidate_outcomes: set[str] = set()
    rule_reasons: set[str] = set()
    for rule in view.rules:
        if rule["id"] in suppressed_rules:
            continue
        result = evaluate_condition(
            rule["when"],
            normalized_facts,
            evidence_states,
            budget=budget,
            enable_rfc0008=enable_rfc0008,
        )
        if result is TriValue.TRUE:
            candidate_outcomes.add(rule["outcome"])
        elif result is TriValue.UNKNOWN and rule["onUnknown"] == "escalate":
            rule_reasons.add("unknown")

    if len(candidate_outcomes) > 1:
        rule_reasons.add("conflict")
    if rule_reasons:
        return _make_disposition(
            "unresolved", reasons=rule_reasons, escalation=view.escalation
        )
    if len(candidate_outcomes) == 1:
        return _make_disposition("outcome", outcome_id=next(iter(candidate_outcomes)))
    if view.fallback is not None:
        return _make_disposition("outcome", outcome_id=view.fallback)
    return _make_disposition(
        "unresolved", reasons={"no-match"}, escalation=view.escalation
    )


def _prepare_pack(
    pack: Any,
    supported: frozenset[str],
    *,
    enable_rfc0008: bool,
) -> _PackView:
    if not isinstance(pack, dict):
        raise EvaluationInputError("pack must be a JSON object")
    for member in ("specVersion", "id", "version", "title", "decision", "outcomes", "rules"):
        if member not in pack:
            raise EvaluationInputError(f"pack is missing required member {member!r}")
    if pack["specVersion"] != "0.1.0-draft":
        raise EvaluationInputError("pack specVersion must be '0.1.0-draft'")

    required_extensions = _required_extensions(pack)
    missing_values = [
        name for name in required_extensions if not _has_extension_value(pack, name)
    ]
    if missing_values:
        raise EvaluationInputError(
            "required extension has no corresponding value: " + ", ".join(sorted(missing_values))
        )
    unsupported = required_extensions - supported
    if unsupported:
        raise UnsupportedExtensionError(
            "unsupported required extension(s): " + ", ".join(sorted(unsupported))
        )

    outcomes_raw = pack["outcomes"]
    if not isinstance(outcomes_raw, list) or len(outcomes_raw) < 2:
        raise EvaluationInputError("pack outcomes must be an array with at least two items")
    outcomes = _collect_object_ids(outcomes_raw, "outcome")

    requirements_raw = pack.get("evidenceRequirements", [])
    if not isinstance(requirements_raw, list):
        raise EvaluationInputError("evidenceRequirements must be an array")
    requirements: list[dict[str, Any]] = []
    requirement_ids: set[str] = set()
    for index, requirement in enumerate(requirements_raw):
        if not isinstance(requirement, dict):
            raise EvaluationInputError(f"evidence requirement {index} must be an object")
        requirement_id = _require_local_id(requirement.get("id"), "evidence requirement id")
        if requirement_id in requirement_ids:
            raise EvaluationInputError(f"duplicate evidence requirement id {requirement_id!r}")
        if not isinstance(requirement.get("required"), bool):
            raise EvaluationInputError(
                f"evidence requirement {requirement_id!r} has invalid required flag"
            )
        requirement_ids.add(requirement_id)
        requirements.append(requirement)

    if "applicability" in pack and pack["applicability"] is None:
        raise EvaluationInputError("applicability must be a condition when present")
    applicability = pack.get("applicability")
    if applicability is not None:
        _validate_condition(
            applicability,
            requirement_ids,
            "applicability",
            enable_rfc0008=enable_rfc0008,
        )

    rules_raw = pack["rules"]
    if not isinstance(rules_raw, list) or not rules_raw:
        raise EvaluationInputError("pack rules must be a non-empty array")
    rule_ids: set[str] = set()
    rules: list[dict[str, Any]] = []
    for index, rule in enumerate(rules_raw):
        if not isinstance(rule, dict):
            raise EvaluationInputError(f"rule {index} must be an object")
        rule_id = _require_local_id(rule.get("id"), "rule id")
        if rule_id in rule_ids:
            raise EvaluationInputError(f"duplicate rule id {rule_id!r}")
        if not isinstance(rule.get("outcome"), str) or rule["outcome"] not in outcomes:
            raise EvaluationInputError(f"rule {rule_id!r} names an undeclared outcome")
        if (
            not isinstance(rule.get("onUnknown"), str)
            or rule["onUnknown"] not in {"ignore", "escalate"}
        ):
            raise EvaluationInputError(f"rule {rule_id!r} has invalid onUnknown")
        _validate_condition(
            rule.get("when"),
            requirement_ids,
            f"rule {rule_id!r}",
            enable_rfc0008=enable_rfc0008,
        )
        evidence_refs = rule.get("evidenceRequirementRefs", [])
        if not isinstance(evidence_refs, list) or any(
            not isinstance(ref, str) or ref not in requirement_ids
            for ref in evidence_refs
        ):
            raise EvaluationInputError(
                f"rule {rule_id!r} has invalid evidenceRequirementRefs"
            )
        rule_ids.add(rule_id)
        rules.append(rule)

    exceptions_raw = pack.get("exceptions", [])
    if not isinstance(exceptions_raw, list):
        raise EvaluationInputError("exceptions must be an array")
    exceptions: list[dict[str, Any]] = []
    exception_ids: set[str] = set()
    for index, exception in enumerate(exceptions_raw):
        if not isinstance(exception, dict):
            raise EvaluationInputError(f"exception {index} must be an object")
        exception_id = _require_local_id(exception.get("id"), "exception id")
        if exception_id in exception_ids:
            raise EvaluationInputError(f"duplicate exception id {exception_id!r}")
        if (
            not isinstance(exception.get("onUnknown"), str)
            or exception["onUnknown"] not in {"ignore", "escalate"}
        ):
            raise EvaluationInputError(f"exception {exception_id!r} has invalid onUnknown")
        _validate_condition(
            exception.get("when"),
            requirement_ids,
            f"exception {exception_id!r}",
            enable_rfc0008=enable_rfc0008,
        )
        effect = exception.get("effect")
        if effect == "suppress-rule":
            if (
                not isinstance(exception.get("targetRule"), str)
                or exception["targetRule"] not in rule_ids
                or "outcome" in exception
            ):
                raise EvaluationInputError(
                    f"exception {exception_id!r} has invalid suppress-rule fields"
                )
        elif effect == "force-outcome":
            if (
                not isinstance(exception.get("outcome"), str)
                or exception["outcome"] not in outcomes
                or "targetRule" in exception
            ):
                raise EvaluationInputError(
                    f"exception {exception_id!r} has invalid force-outcome fields"
                )
        elif effect == "escalate":
            if "outcome" in exception or "targetRule" in exception:
                raise EvaluationInputError(
                    f"exception {exception_id!r} has invalid escalate fields"
                )
        else:
            raise EvaluationInputError(f"exception {exception_id!r} has invalid effect")
        exception_ids.add(exception_id)
        exceptions.append(exception)

    if "fallbackOutcome" in pack and pack["fallbackOutcome"] is None:
        raise EvaluationInputError("fallbackOutcome must name an outcome when present")
    fallback = pack.get("fallbackOutcome")
    if fallback is not None:
        if not isinstance(fallback, str) or fallback not in outcomes:
            raise EvaluationInputError("fallbackOutcome names an undeclared outcome")
    if "escalation" in pack and pack["escalation"] is None:
        raise EvaluationInputError("escalation must be an object when present")
    escalation = _validate_escalation(pack.get("escalation"))

    return _PackView(
        applicability=applicability,
        requirements=tuple(requirements),
        requirement_ids=frozenset(requirement_ids),
        outcomes=frozenset(outcomes),
        rules=tuple(rules),
        exceptions=tuple(exceptions),
        fallback=fallback,
        escalation=escalation,
    )


def _collect_object_ids(items: list[Any], kind: str) -> set[str]:
    identifiers: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise EvaluationInputError(f"{kind} {index} must be an object")
        identifier = _require_local_id(item.get("id"), f"{kind} id")
        if identifier in identifiers:
            raise EvaluationInputError(f"duplicate {kind} id {identifier!r}")
        identifiers.add(identifier)
    return identifiers


def _require_local_id(value: Any, description: str) -> str:
    if not isinstance(value, str) or _LOCAL_ID_RE.fullmatch(value) is None:
        raise EvaluationInputError(f"{description} is invalid")
    return value


def _validate_condition(
    condition: Any,
    requirement_ids: set[str],
    description: str,
    *,
    enable_rfc0008: bool,
    aggregate_depth: int = 0,
) -> None:
    if not isinstance(condition, dict):
        raise EvaluationInputError(f"{description} condition must be an object")
    op = condition.get("op")
    if not isinstance(op, str):
        raise EvaluationInputError(f"{description} condition has unsupported op")
    if op in _RFC0008_AGGREGATE_OPS and not enable_rfc0008:
        raise EvaluationInputError(
            f"{description} condition uses RFC 0008 op {op!r}; "
            "pass enable_rfc0008=True to opt in"
        )
    if op not in _CORE_CONDITION_OPS | _RFC0008_AGGREGATE_OPS:
        raise EvaluationInputError(f"{description} condition has unsupported op")
    if op == "literal":
        if set(condition) != {"op", "value"} or not isinstance(condition["value"], bool):
            raise EvaluationInputError(f"{description} literal condition is malformed")
        return
    if op in {"all", "any"}:
        if set(condition) != {"op", "conditions"}:
            raise EvaluationInputError(f"{description} {op} condition is malformed")
        children = condition["conditions"]
        if not isinstance(children, list) or not children:
            raise EvaluationInputError(f"{description} {op} condition needs children")
        for child in children:
            _validate_condition(
                child,
                requirement_ids,
                description,
                enable_rfc0008=enable_rfc0008,
                aggregate_depth=aggregate_depth,
            )
        return
    if op == "not":
        if set(condition) != {"op", "condition"}:
            raise EvaluationInputError(f"{description} not condition is malformed")
        _validate_condition(
            condition["condition"],
            requirement_ids,
            description,
            enable_rfc0008=enable_rfc0008,
            aggregate_depth=aggregate_depth,
        )
        return
    if op == "evidence-present":
        if set(condition) != {"op", "evidenceRequirement"}:
            raise EvaluationInputError(
                f"{description} evidence-present condition is malformed"
            )
        if (
            not isinstance(condition["evidenceRequirement"], str)
            or condition["evidenceRequirement"] not in requirement_ids
        ):
            raise EvaluationInputError(
                f"{description} condition names an undeclared evidence requirement"
            )
        return

    if op in _RFC0008_AGGREGATE_OPS:
        next_depth = aggregate_depth + 1
        if next_depth > 2:
            raise EvaluationInputError(
                f"{description} condition exceeds RFC 0008 aggregate depth 2"
            )
        if op == "uniform":
            if set(condition) != {"op", "path", "at"}:
                raise EvaluationInputError(
                    f"{description} uniform condition is malformed"
                )
            _validate_pointer(condition["path"], description)
            _validate_pointer(condition["at"], description)
            return

        if set(condition) != {"op", "path", "where"}:
            raise EvaluationInputError(f"{description} {op} condition is malformed")
        _validate_pointer(condition["path"], description)
        _validate_condition(
            condition["where"],
            requirement_ids,
            description,
            enable_rfc0008=enable_rfc0008,
            aggregate_depth=next_depth,
        )
        return

    if set(condition) != {"op", "path", "operator", "value"}:
        raise EvaluationInputError(f"{description} fact condition is malformed")
    path = condition["path"]
    operator = condition["operator"]
    if (
        not isinstance(path, str)
        or not isinstance(operator, str)
        or operator not in _FACT_OPERATORS
    ):
        raise EvaluationInputError(f"{description} fact condition is malformed")
    _validate_pointer(path, description)
    if operator in _ORDERED_OPERATORS and not is_decimal_string(condition["value"]):
        raise EvaluationInputError(
            f"{description} ordered condition operand is not a decimal string"
        )
    if operator == "in" and (
        not isinstance(condition["value"], list) or not condition["value"]
    ):
        raise EvaluationInputError(f"{description} in operand must be a non-empty array")


def _validate_pointer(path: Any, description: str) -> None:
    if not isinstance(path, str):
        raise EvaluationInputError(f"{description} condition has invalid JSON Pointer")
    try:
        _pointer_tokens(path)
    except PointerSyntaxError as exc:
        raise EvaluationInputError(f"{description} has invalid JSON Pointer") from exc


def _validate_escalation(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise EvaluationInputError("escalation must be an object")
    triggers = value.get("triggers")
    target = value.get("target")
    if (
        not isinstance(triggers, list)
        or not triggers
        or any(not isinstance(trigger, str) for trigger in triggers)
        or len(set(triggers)) != len(triggers)
        or any(trigger not in _TRIGGERS for trigger in triggers)
    ):
        raise EvaluationInputError("escalation triggers are invalid")
    if (
        not isinstance(target, dict)
        or not isinstance(target.get("kind"), str)
        or target["kind"] not in {"human-role", "queue", "system"}
        or not isinstance(target.get("name"), str)
        or not target["name"]
    ):
        raise EvaluationInputError("escalation target is invalid")
    return value


def _required_extensions(pack: Mapping[str, Any]) -> frozenset[str]:
    if "metadata" in pack and pack["metadata"] is None:
        raise EvaluationInputError("metadata must be an object when present")
    metadata = pack.get("metadata")
    if metadata is None:
        return frozenset()
    if not isinstance(metadata, dict):
        raise EvaluationInputError("metadata must be an object")
    required = metadata.get("requiredExtensions", [])
    if (
        not isinstance(required, list)
        or any(not isinstance(name, str) for name in required)
        or len(set(required)) != len(required)
    ):
        raise EvaluationInputError("metadata.requiredExtensions is invalid")
    return frozenset(required)


def _has_extension_value(value: Any, name: str) -> bool:
    if isinstance(value, dict):
        extensions = value.get("extensions")
        if isinstance(extensions, dict) and name in extensions:
            return True
        return any(_has_extension_value(child, name) for child in value.values())
    if isinstance(value, list):
        return any(_has_extension_value(child, name) for child in value)
    return False


def _normalize_supported_extensions(value: Iterable[str]) -> frozenset[str]:
    if isinstance(value, (str, bytes)) or value is None:
        raise EvaluationInputError("supported_extensions must be an iterable of strings")
    try:
        names = tuple(value)
    except TypeError as exc:
        raise EvaluationInputError(
            "supported_extensions must be an iterable of strings"
        ) from exc
    if any(not isinstance(name, str) for name in names):
        raise EvaluationInputError("supported extension names must be strings")
    return frozenset(names)


def _prepare_evidence(
    evidence: Any, declared: frozenset[str]
) -> dict[str, str]:
    if not isinstance(evidence, dict):
        raise EvaluationInputError("evidence availability must be a JSON object")
    result: dict[str, str] = {}
    for requirement, state in evidence.items():
        if requirement not in declared:
            raise EvaluationInputError(
                f"evidence availability names undeclared requirement {requirement!r}"
            )
        if not isinstance(state, str) or state not in {"present", "absent", "unknown"}:
            raise EvaluationInputError(
                f"evidence availability for {requirement!r} must be "
                "'present', 'absent', or 'unknown'"
            )
        result[requirement] = state
    return result


def _make_disposition(
    kind: str,
    *,
    outcome_id: str | None = None,
    reasons: set[str] | None = None,
    escalation: Mapping[str, Any] | None = None,
    direct_escalation: bool = False,
) -> dict[str, Any]:
    reasons = reasons or set()
    ordered_reasons = sorted(
        reasons, key=lambda reason: (_REASON_ORDER.get(reason, 100), reason)
    )
    requested = direct_escalation or (
        escalation is not None
        and bool(reasons.intersection(escalation.get("triggers", [])))
    )
    result: dict[str, Any] = {
        "kind": kind,
        "reasons": ordered_reasons,
        "handoff": "requested" if requested else "none",
        "experimental": True,
        "conformanceClaim": "none",
    }
    if kind == "outcome":
        if outcome_id is None:
            raise AssertionError("outcome disposition requires outcome id")
        result["outcomeId"] = outcome_id
    return result
