"""Reference implementation of the portable derivation rule (SPEC.md).

Maps one acquired artifact plus named parameters to a derived claim -- facts,
evidence availability, acquisition status, reason, and basis -- by applying a
data-driven rule. Standard library only, so a second implementation can be
built clean-room from SPEC.md alone and agreement-tested against this one
(ADR-0002: the derivation is data two implementations agree on, not code checked
against itself).
"""

import json
import re

RULE_VERSION = "1"
_DECIMAL_RE = re.compile(r"^(0|[1-9][0-9]*)$")
_TIMESTAMP_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z$"
)
_SAFE_INT_MAX = (1 << 53) - 1
_ABSENT = object()  # get() result for a pointer that does not resolve


class RuleError(Exception):
    """The rule (or its application to an artifact) is not well-formed. A
    conforming implementation raises on the same inputs; rejection is not a
    claim."""


# --- canonicalization (identical to the attestation core's canon) ---


def _check_domain(value):
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if not (-_SAFE_INT_MAX <= value <= _SAFE_INT_MAX):
            raise RuleError("integer outside the canon safe range: %r" % value)
        return
    if isinstance(value, float):
        raise RuleError("non-integer number is outside the canon domain: %r" % value)
    if isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise RuleError("string with a lone surrogate is outside the canon domain")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise RuleError("non-string object member name")
            _check_domain(item)
        return
    if isinstance(value, list):
        for item in value:
            _check_domain(item)
        return
    raise RuleError("value outside the canon domain: %r" % (value,))


def canon(value):
    _check_domain(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


# --- pointers ---


def _unescape(token):
    return token.replace("~1", "/").replace("~0", "~")


def get(artifact, pointer):
    """Resolve an RFC 6901 pointer, or return _ABSENT."""
    if pointer == "":
        return artifact
    if not pointer.startswith("/"):
        raise RuleError("pointer must be empty or start with '/': %r" % pointer)
    current = artifact
    for raw in pointer.split("/")[1:]:
        token = _unescape(raw)
        if isinstance(current, dict):
            if token not in current:
                return _ABSENT
            current = current[token]
        elif isinstance(current, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", token):
                return _ABSENT
            index = int(token)
            if index >= len(current):
                return _ABSENT
            current = current[index]
        else:
            return _ABSENT
    return current


def _set(document, pointer, value):
    """Set value at an RFC 6901 pointer, creating intermediate objects."""
    if pointer == "" or not pointer.startswith("/"):
        raise RuleError("fact pointer must start with '/': %r" % pointer)
    tokens = [_unescape(t) for t in pointer.split("/")[1:]]
    current = document
    for token in tokens[:-1]:
        nxt = current.get(token)
        if not isinstance(nxt, dict):
            nxt = {}
            current[token] = nxt
        current = nxt
    current[tokens[-1]] = value


# --- time ---


def _days_from_civil(year, month, day):
    # Howard Hinnant's algorithm: days since 1970-01-01, proleptic Gregorian.
    y = year - (1 if month <= 2 else 0)
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    doy = (153 * ((month + 9) if month <= 2 else (month - 3)) + 2) // 5 + day - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def instant(value):
    """Seconds since 1970-01-01T00:00:00Z for a SPEC timestamp, or None."""
    if not isinstance(value, str):
        return None
    match = _TIMESTAMP_RE.match(value)
    if not match:
        return None
    year, month, day, hour, minute, second = (int(g) for g in match.groups())
    if not (1 <= month <= 12 and hour <= 23 and minute <= 59 and second <= 59):
        return None
    if not (1 <= day <= _days_in_month(year, month)):  # real calendar validity: no Feb 30
        return None
    return _days_from_civil(year, month, day) * 86400 + hour * 3600 + minute * 60 + second


def _days_in_month(year, month):
    if month == 2:
        leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        return 29 if leap else 28
    return 30 if month in (4, 6, 9, 11) else 31


# --- conditions ---


def _json_equal(a, b):
    if a is _ABSENT or b is _ABSENT:
        return False
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if isinstance(a, str) and isinstance(b, str):
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_json_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_json_equal(a[k], b[k]) for k in a)
    if a is None or b is None:
        return a is None and b is None
    return False


def _evaluate(condition, artifact, params, reads):
    """Evaluate a condition, recording into `reads` the artifact pointers it
    actually resolves. `all`/`any` short-circuit, so a pointer behind a
    short-circuited branch is not read -- which is what makes the cumulative
    `basis` path-sensitive: a clause that fails on /status never reads the
    fields its later terms would have."""
    op = condition.get("op")
    if op == "always":
        return True
    if op == "exists":
        reads.add(condition["field"])
        return get(artifact, condition["field"]) is not _ABSENT
    if op == "equals":
        reads.add(condition["field"])
        return _json_equal(get(artifact, condition["field"]), condition["to"])
    if op == "equalsParam":
        reads.add(condition["field"])
        return _json_equal(get(artifact, condition["field"]), params[condition["param"]])
    if op == "isTrue":
        reads.add(condition["field"])
        return get(artifact, condition["field"]) is True
    if op == "isDecimalString":
        reads.add(condition["field"])
        value = get(artifact, condition["field"])
        return isinstance(value, str) and _DECIMAL_RE.match(value) is not None
    if op == "freshWithin":
        reads.add(condition["field"])
        observed = instant(get(artifact, condition["field"]))
        as_of = instant(params.get(condition["asOf"]))
        max_age = params.get(condition["maxAge"])
        if observed is None or as_of is None or not isinstance(max_age, int):
            return False
        return 0 <= (as_of - observed) <= max_age
    if op == "all":
        for c in condition["of"]:
            if not _evaluate(c, artifact, params, reads):
                return False
        return True
    if op == "any":
        for c in condition["of"]:
            if _evaluate(c, artifact, params, reads):
                return True
        return False
    if op == "not":
        return not _evaluate(condition["of"], artifact, params, reads)
    raise RuleError("unknown condition op: %r" % (op,))


# --- rule application ---


def _validate_rule(rule):
    if not isinstance(rule, dict) or rule.get("ruleVersion") != RULE_VERSION:
        raise RuleError("rule must declare ruleVersion %r" % RULE_VERSION)
    # The rule document is itself in the canon domain: a float literal, NaN, or
    # out-of-range integer anywhere in the rule (e.g. an `equals` `to` of 1.5)
    # rejects it. Artifacts, by contrast, are arbitrary JSON (a source returns
    # what it returns); only the claim built from an artifact must be in-domain.
    _check_domain(rule)
    parameters = rule.get("parameters", {})
    if not isinstance(parameters, dict):
        raise RuleError("parameters must be an object")
    for name, kind in parameters.items():
        if kind not in ("string", "integer", "timestamp"):
            raise RuleError("parameter %r has unknown type %r" % (name, kind))
    clauses = rule.get("clauses")
    if not isinstance(clauses, list) or not clauses:
        raise RuleError("clauses must be a non-empty array")
    if clauses[-1].get("when", {}).get("op") != "always":
        raise RuleError("the final clause's when must be {\"op\":\"always\"}")
    for clause in clauses:
        _validate_condition(clause.get("when", {}))
        claim = clause.get("claim", {})
        status = claim.get("acquisitionStatus")
        if status not in ("resolved", "absent", "unknown"):
            raise RuleError("claim acquisitionStatus must be resolved|absent|unknown")
        for entry in claim.get("facts", []):
            if "pointer" not in entry or "from" not in entry:
                raise RuleError("a facts entry needs pointer and from")
        for state in claim.get("evidence", {}).values():
            if state not in ("present", "absent", "unknown"):
                raise RuleError("evidence state must be present|absent|unknown")


def _validate_condition(condition):
    if not isinstance(condition, dict) or "op" not in condition:
        raise RuleError("a condition must be an object with an op")
    op = condition["op"]
    if op not in ("always", "exists", "equals", "equalsParam", "isTrue",
                  "isDecimalString", "freshWithin", "all", "any", "not"):
        raise RuleError("unknown condition op: %r" % (op,))
    if op in ("all", "any"):
        for c in condition["of"]:
            _validate_condition(c)
    elif op == "not":
        _validate_condition(condition["of"])


def derive(rule, artifact, params):
    """Apply a derivation rule to an artifact and parameters, returning the
    derived claim (a dict). Raises RuleError on a malformed rule or artifact."""
    _validate_rule(rule)
    clauses = rule["clauses"]
    read = set()
    for clause in clauses:
        condition = clause["when"]
        if _evaluate(condition, artifact, params, read):
            claim = clause.get("claim", {})
            facts = {}
            for entry in claim.get("facts", []):
                value = get(artifact, entry["from"])
                if value is _ABSENT:
                    raise RuleError(
                        "matched claim reads absent field %r" % (entry["from"],)
                    )
                _set(facts, entry["pointer"], value)
            derived = {
                "facts": facts,
                "evidenceAvailability": dict(claim.get("evidence", {})),
                "acquisitionStatus": claim["acquisitionStatus"],
                "reason": clause.get("reason", ""),
                "basis": sorted(read),
            }
            _check_domain(derived)  # a claim outside the canon domain is a rule error
            return derived
    raise RuleError("no clause matched (a rule must end with an always clause)")


def derive_canonical(rule, artifact, params):
    """The derived claim's canonical bytes, for agreement comparison."""
    return canon(derive(rule, artifact, params))
