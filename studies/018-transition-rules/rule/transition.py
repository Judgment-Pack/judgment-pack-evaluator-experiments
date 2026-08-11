"""Layer TRANSITION — a relying party's rule over cited registry state.

RFC 0011 §2a states that membership at a snapshot does not determine continued
reliance: that second question is a **transition rule** and belongs to the
relying party, not to the registry and not to the currency verifier. This
module is the study's prototype of such a rule evaluator, kept deliberately
separate from Study 016's frozen currency verifier — which is consumed
unmodified and whose output remains exactly "membership at snapshot".

The evidence it consumes is the construction a reader proposed publicly on the
Study 016 announcement thread (RFC 0011 Unresolved #11): the deciding artifact
records the registry **head** it validated against. That citation is *one
possible input* to a rule, never an ordering: it attests the state an
artifact's author claims to have relied on, never when the artifact was
created — a party able to re-mint can cite an older head deliberately, and
this study registers that as an expected non-detection rather than repairing
it.

Three rules are registered, as configuration rather than code paths so that no
rule is privileged by construction:

- `stop-at-retirement` — no reliance once the version has left the supported
  set at the auditor's snapshot. Needs no citation at all.
- `position-window` — reliance permitted for a bounded number of registry
  **positions** after the position at which the version left the set. Needs
  the citation, and is computable only because the ordering it uses is
  positional; a duration window is `transition-unavailable`, because
  `effectiveFrom` is inert in the pinned upstream and nothing here holds a
  clock.
- `run-to-expiry` — reliance permitted if the artifact cites a head at which
  the version was still in the supported set. Needs the citation.

The verdict vocabulary is about **usability under a stated rule**, never about
currency, and never about truth.
"""

import json
import re

RULES = ("stop-at-retirement", "position-window", "run-to-expiry")

CODES = (
    "transition-unavailable",
    "not-usable-version-retired",
    "not-usable-window-elapsed",
    "not-usable-created-after-retirement",
)

DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

RULECONFIG_MEMBERS = {"ruleConfigVersion", "seriesId", "rule", "windowPositions",
                      "windowDuration"}
CITATION_MEMBERS = {"citationVersion", "seriesId", "citedHead"}


def result(verdict, code=None, detail=None, **fields):
    record = {"verdict": verdict, "code": code, "detail": detail,
              "citedPosition": None, "retiredAtPosition": None}
    record.update(fields)
    return record


def _unusable(code, detail, **fields):
    return result("not-usable", code, detail, **fields)


def _unavailable(detail, **fields):
    return result("unavailable", "transition-unavailable", detail, **fields)


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _strict_json(data):
    def no_duplicates(pairs):
        members = {}
        for key, value in pairs:
            if key in members:
                raise ValueError("duplicate member name: %s" % key)
            members[key] = value
        return members
    return json.loads(bytes(data).decode("utf-8"), object_pairs_hook=no_duplicates)


def _ruleconfig_problem(config):
    if not isinstance(config, dict) or set(config) != RULECONFIG_MEMBERS:
        return "rule configuration is not an object with exactly its five members"
    if config["ruleConfigVersion"] != "1":
        return "rule configuration is not version 1"
    if not isinstance(config["seriesId"], str) or not config["seriesId"]:
        return "no series is bound: a transition rule is stated per series"
    if config["rule"] not in RULES:
        return "rule is not one of %s" % ", ".join(RULES)
    window = config["windowPositions"]
    if window is not None and (not _is_int(window) or window < 0):
        return "windowPositions is neither null nor a non-negative integer"
    duration = config["windowDuration"]
    if duration is not None and not isinstance(duration, str):
        return "windowDuration is neither null nor a string"
    if config["rule"] == "position-window" and window is None and duration is None:
        return "position-window names no window"
    return None


def _citation_problem(citation):
    if not isinstance(citation, dict) or set(citation) != CITATION_MEMBERS:
        return "citation is not an object with exactly its three members"
    if citation["citationVersion"] != "1":
        return "citation is not version 1"
    if not isinstance(citation["seriesId"], str) or not citation["seriesId"]:
        return "citation seriesId is not a non-empty string"
    head = citation["citedHead"]
    if not isinstance(head, str) or not DIGEST_PATTERN.match(head):
        return "citedHead is not a sha256-prefixed digest"
    return None


def _fold_positions(payloads, series_id, member):
    """Positions at which `member` entered and left the supported set.

    Returns `(entered, left)` as 1-based positions or None. Uses the same
    add/retire/reinstate semantics as the pinned upstream, over the same
    payload shape, but computes *positions* rather than a set — the upstream's
    fold answers membership and this layer needs where the transition happened.
    """
    version, digest = member
    entered = left = None
    current = False
    for index, payload in enumerate(payloads, start=1):
        if payload["seriesId"] != series_id or payload["packVersion"] != version:
            continue
        if payload["event"] == "add" and payload.get("packDigest") == digest:
            current, entered, left = True, index, None
        elif payload["event"] == "retire" and current:
            current, left = False, index
        elif payload["event"] == "reinstate" and not current:
            current, entered, left = True, index, None
    return entered, left


def layer_transition(commitment, snapshot_digests, snapshot_payloads,
                     citation_bytes, ruleconfig_bytes, currency_outcome):
    """Evaluate the registered rule. Ordered, fail-closed.

    `currency_outcome` is Study 016's Layer CURRENCY verdict string, consumed
    as a fact and never recomputed here: membership is the registry's answer
    and usability is this layer's, which is the separation RFC 0011 §2a draws.
    """
    if not isinstance(ruleconfig_bytes, (bytes, bytearray)):
        return _unavailable("rule configuration is absent or not bytes")
    try:
        config = _strict_json(ruleconfig_bytes)
    except Exception as error:
        return _unavailable("rule configuration is not strict JSON: %s" % error)
    problem = _ruleconfig_problem(config)
    if problem is not None:
        return _unavailable(problem)

    if not isinstance(commitment, dict):
        return _unavailable("no conforming commitment to evaluate")
    judgment = commitment.get("judgment")
    if not isinstance(judgment, dict):
        return _unavailable("the commitment carries no judgment object")
    series_id = judgment.get("packId")
    member = (judgment.get("packVersion"), judgment.get("packDigest"))
    if not isinstance(series_id, str) or series_id != config["seriesId"]:
        return _unavailable("the rule configuration is stated for a different series")
    if not all(isinstance(part, str) for part in member):
        return _unavailable("the commitment carries no complete identity tuple")

    # A duration window is not computable here, and saying so is the point:
    # the only ordering available offline is positional, `effectiveFrom` is
    # inert in the pinned upstream, and nothing carries a trusted clock.
    if config["rule"] == "position-window" and config["windowPositions"] is None:
        return _unavailable(
            "this rule names a duration window; no trusted ordering between the "
            "artifact and the registry exists offline, so it is not evaluable "
            "here (RFC 0011 Unresolved #3)")

    # `stop-at-retirement` consumes the registry's own answer and needs no
    # citation — the rule for which the citation buys nothing.
    if config["rule"] == "stop-at-retirement":
        if currency_outcome == "pass":
            return result("usable", None, "in the supported set at the auditor's snapshot")
        return _unusable("not-usable-version-retired",
                         "not in the supported set at the auditor's snapshot, and this "
                         "rule permits no reliance beyond that point")

    # The remaining rules need the citation.
    if not isinstance(citation_bytes, (bytes, bytearray)):
        return _unavailable("this rule needs a cited registry head and none is retained")
    try:
        citation = _strict_json(citation_bytes)
    except Exception as error:
        return _unavailable("the retained citation is not strict JSON: %s" % error)
    problem = _citation_problem(citation)
    if problem is not None:
        return _unavailable(problem)
    if citation["seriesId"] != series_id:
        return _unavailable("the citation names a different series")
    if not isinstance(snapshot_digests, list) or not snapshot_digests:
        return _unavailable("no usable snapshot to locate the cited head in")
    if citation["citedHead"] not in snapshot_digests:
        return _unavailable(
            "the cited head is not a position of the auditor's snapshot: this "
            "rule cannot place the artifact in the history it is auditing")
    cited_position = snapshot_digests.index(citation["citedHead"]) + 1
    entered, left = _fold_positions(snapshot_payloads, series_id, member)
    fields = {"citedPosition": cited_position, "retiredAtPosition": left}

    if config["rule"] == "run-to-expiry":
        if entered is not None and cited_position >= entered and (
                left is None or cited_position < left):
            return result("usable", None,
                          "the cited head is a position at which the version was in the "
                          "supported set; this rule lets such decisions run to their own "
                          "terms. NOTE: the citation attests the state its author claims, "
                          "not when the artifact was created", **fields)
        return _unusable("not-usable-created-after-retirement",
                         "the cited head is not a position at which the version was in "
                         "the supported set", **fields)

    # position-window
    if left is None:
        return result("usable", None,
                      "the version has not left the supported set at this snapshot",
                      **fields)
    if cited_position >= left:
        return _unusable("not-usable-created-after-retirement",
                         "the cited head is at or after the position at which the "
                         "version left the supported set", **fields)
    elapsed = len(snapshot_digests) - left
    if elapsed <= config["windowPositions"]:
        return result("usable", None,
                      "%d position(s) elapsed since the version left the supported set; "
                      "the window permits %d" % (elapsed, config["windowPositions"]),
                      **fields)
    return _unusable("not-usable-window-elapsed",
                     "%d position(s) elapsed since the version left the supported set; "
                     "the window permits %d" % (elapsed, config["windowPositions"]),
                     **fields)
