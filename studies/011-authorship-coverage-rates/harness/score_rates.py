#!/usr/bin/env python3
"""The scorer: an authoring slot tree in, per-class coverage rates out.

It is the study's one counting authority (PREREGISTRATION.md §3-§5). For every
slot it re-derives admission from the retained bytes — it never trusts the
batch's own refusal record, and a slot the batch refused whose bytes now admit
it is itself invalid, code `refusal-conflict` — recompiles the completion with
the ported compiler, splits the accepted records into H and Q with the ported
mirror, and intersects them with FAMILY.json's six predicates. The valid-run
population is computed by `admit()` and by nothing else (§6 C5, the Study 001
lesson: a preregistration constrains what you may claim, only code can enforce
the population a claim was computed on).

The partition that decides every denominator (§3.3):

  pipeline-invalid  the apparatus or the transport failed and the run says
                    nothing about authorship — excluded from denominators,
                    counted, and reported with its code
  authoring-empty   admissible evidence, and the author produced nothing
                    usable (no parseable array, or every element dropped, or
                    no policy-concordant record) — VALID, counted, coverage
                    zero in every class. Excluding these would quietly
                    condition every rate on the author having succeeded.

Pipeline-invalid codes, in the order admission evaluates them (the same set
CODE_PARTITION carries, which PREREGISTRATION.md §3.3 enumerates member for
member and harness/tests/test_admission.py diffs against both this source and
that table):

  slot-shape             a required slot file is missing or not a regular file
  call-unreadable        CALL.json is not duplicate-free JSON
  model-mismatch         CALL.json names a model other than the pinned one
  binary-mismatch        CALL.json names a binary digest other than the pinned one
  cli-mismatch           CALL.json names a CLI version other than the pinned one
  isolation-unproven     CALL.json does not record the per-run isolation (C6)
  session-count          the run produced other than exactly one new session
  call-nonzero-exit      the process did not exit with integer status 0
  no-session             session.jsonl was not retained
  no-completion          completion.txt was not retained (exit-0 only)
  no-context             context.json was not retained
  transcript-refused     the ported transcript binding refused (detail retained)
  context-mismatch       the retained context.json is not what the session yields
  completion-unreadable  completion.txt is not decodable UTF-8
  compile-refused        the compiler failed other than by finding no array
  regeneration-mismatch  the compiler does not regenerate its own output bytes
  refusal-conflict       the batch refused this slot but the bytes now admit it
  scorer-error           admission raised: the run is recorded invalid with the
                         error, because a scorer that dies mid-tree scores
                         nothing (§7 totality)

Before it reads a slot it verifies, and refuses on, the ported-byte digest
table (harness/integrity.py, §6 C1), the golden capture against the digest
harness/PINS.json registers for it (§3.2), the preregistration's own digest
once that pin is filled (§2.6), and the batch's terminality (§2.4).

Endpoints: the six primary rates c_i with exact Clopper-Pearson 95% intervals
(§4.2, §4.3), and the secondaries S1-S8 (§4.4) — raw intersection, Q
intersection and mislabel share, coverage breadth and the all-six rate, record
volumes and drop codes, label accuracy, distinct outputs, coverage against run
index, and the pipeline-invalid rate. §5's review-depth mapping is applied
here, in code, from thresholds registered before the batch.

What this file deliberately does NOT do: run the evaluator (jpack never
executes in this study — the mirror is the reference semantics), apply a
FAMILY patch or build a pack D, fit or tune §5's mapping, consult a clock, or
use randomness. Per-slot wall clock is retained in each CALL.json and stays
there: RESULTS.json carries no timestamp, so two scorings of one slot tree are
byte-identical.

RESULTS.json and RATES.md are always written to the study root: there is no
`--out`, because a rate table written somewhere else would let the operator
read six rates while leaving the marker the driver refuses new slots on
(§2.4). `--emit-records DIR` still takes a directory: it writes derived
record trees, not rates.

Usage:
  score_rates.py score --slots DIR [--pins PATH] [--family PATH]
                       [--prompt PATH] [--golden PATH] [--emit-records DIR]
"""
from __future__ import annotations
import contextlib
import hashlib
import io
import json
import math
import os
import sys
import tempfile
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import integrity  # noqa: E402
import policy_mirror  # noqa: E402
import records_compile  # noqa: E402
import transcript_check  # noqa: E402

DEFAULT_PINS = os.path.join(HERE, "PINS.json")
DEFAULT_FAMILY = os.path.join(STUDY, "FAMILY.json")
DEFAULT_PROMPT = os.path.join(STUDY, "transcription", "PROMPT.txt")
DEFAULT_GOLDEN = os.path.join(STUDY, "transcription", "GOLDEN-CONTEXT.json")

SLOT_FILES = ("CALL.json", "stdout.raw", "stderr.raw")
ALPHA = Fraction(1, 40)          # one tail of a two-sided 95% interval
BISECTIONS = 200                 # fixed; no early exit, no tolerance
TIERS = ("LIGHT", "STANDARD", "FULL")
# §5, registered before the batch. The tier is decided by the exact
# Clopper-Pearson lower bound alone — one criterion in one unit, so the
# boundary does not move with V the way a point-estimate conjunction did.
LIGHT_LOWER_BOUND = 0.80
STANDARD_LOWER_BOUND = 0.40
MISLABEL_ESCALATION = 0.20
# Not a tier change: a high pipeline-invalid rate is one stated caution on the
# whole batch (§5), never a per-class escalation on top of a widened interval.
PIPELINE_CAUTION = 0.10

# §3.3's partition, member for member. Every code admit() and score_run() can
# name is here; harness/tests/test_admission.py diffs this table against the
# codes the two functions can actually return AND against the enumeration
# PREREGISTRATION.md §3.3 registers, so prose and code cannot drift apart.
CODE_PARTITION = {
    "slot-shape": "pipeline-invalid",
    "call-unreadable": "pipeline-invalid",
    "model-mismatch": "pipeline-invalid",
    "binary-mismatch": "pipeline-invalid",
    "cli-mismatch": "pipeline-invalid",
    "isolation-unproven": "pipeline-invalid",
    "session-count": "pipeline-invalid",
    "call-nonzero-exit": "pipeline-invalid",
    "no-session": "pipeline-invalid",
    "no-completion": "pipeline-invalid",
    "no-context": "pipeline-invalid",
    "transcript-refused": "pipeline-invalid",
    "context-mismatch": "pipeline-invalid",
    "completion-unreadable": "pipeline-invalid",
    "compile-refused": "pipeline-invalid",
    "regeneration-mismatch": "pipeline-invalid",
    "refusal-conflict": "pipeline-invalid",
    "scorer-error": "pipeline-invalid",
}
# The two outcomes that carry no code and stay in the denominator (§3.3).
VALID_OUTCOMES = ("valid", "authoring-empty")


class ScoreError(Exception):
    """A population-level refusal: the scoring itself cannot be trusted, as
    distinct from a single run being invalid."""


def _refuse_duplicate_keys(pairs):
    keys = [key for key, _ in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate object keys")
    return dict(pairs)


def load_json(path: str):
    """Duplicate-key-rejecting JSON: a shadowed member cannot mean one thing
    to this scorer and another to a reader."""
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"),
                          object_pairs_hook=_refuse_duplicate_keys)


def file_digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def tree_digest(files: dict) -> str:
    """One digest over a compiled record tree: relative paths in sorted
    order, each length-prefixed, so no rename or split can collide."""
    hasher = hashlib.sha256()
    for relative in sorted(files):
        body = files[relative]
        hasher.update(relative.encode("utf-8"))
        hasher.update(b"\n%d\n" % len(body))
        hasher.update(body)
    return "sha256:" + hasher.hexdigest()


# --- the interval (PREREGISTRATION.md §4.3, normative) ---------------------

def _tail_ge(k: int, n: int, p: Fraction) -> Fraction:
    """P(X >= k) for X ~ Binomial(n, p), summed in ascending j as exact
    rationals: math.comb is exact, and a double is an exact binary rational,
    so nothing here rounds."""
    q = 1 - p
    total = Fraction(0)
    for j in range(k, n + 1):
        total += math.comb(n, j) * p ** j * q ** (n - j)
    return total


def _tail_le(k: int, n: int, p: Fraction) -> Fraction:
    """P(X <= k) for X ~ Binomial(n, p)."""
    q = 1 - p
    total = Fraction(0)
    for j in range(0, k + 1):
        total += math.comb(n, j) * p ** j * q ** (n - j)
    return total


def _bisect(predicate) -> float:
    """The crossing point of a monotone predicate — true on [0, root), false
    after — found by EXACTLY 200 halvings of [0, 1] in IEEE-754 doubles. A
    fixed iteration count and an exact comparison mean the same inputs give
    the same bits on any platform: no libm, no tolerance, no seed."""
    low, high = 0.0, 1.0
    for _ in range(BISECTIONS):
        middle = (low + high) / 2.0
        if predicate(middle):
            low = middle
        else:
            high = middle
    return low


def clopper_pearson(k: int, n: int) -> tuple:
    """The exact (Clopper-Pearson) 95% interval for k successes in n trials.

    The bounds are the p values that make the observed count exactly as
    extreme as alpha/2 allows: the lower bound solves P(X >= k | p) = alpha
    (increasing in p), the upper solves P(X <= k | p) = alpha (decreasing in
    p), with the degenerate ends pinned at 0 and 1.
    """
    if n <= 0:
        raise ValueError("an interval needs at least one trial")
    if not 0 <= k <= n:
        raise ValueError("k=%d is not a count out of n=%d" % (k, n))
    return lower_bound(k, n), upper_bound(k, n)


def lower_bound(k: int, n: int) -> float:
    """The interval's lower bound alone — §5's whole criterion, so it is worth
    computing without the upper root nobody asked for."""
    return 0.0 if k == 0 else _bisect(lambda p: _tail_ge(k, n, Fraction(p)) < ALPHA)


def upper_bound(k: int, n: int) -> float:
    return 1.0 if k == n else _bisect(lambda p: _tail_le(k, n, Fraction(p)) > ALPHA)


def rate_block(k: int, n: int) -> dict:
    """The reported shape for one proportion: the integers, the point
    estimate, and the exact interval — never a rate without its denominator,
    and never a bound a reader cannot recompute from the integers."""
    if n <= 0:
        return {"count": k, "trials": n, "rate": None, "ci95": None}
    lower, upper = clopper_pearson(k, n)
    return {"count": k, "trials": n, "rate": k / n, "ci95": [lower, upper]}


def review_tier(coverage: dict, mislabel_share) -> dict:
    """§5's registered mapping, applied — never fitted.

    ONE criterion in ONE unit: the exact Clopper-Pearson lower bound. LIGHT
    iff lower >= 0.80, STANDARD iff lower >= 0.40, FULL otherwise. The earlier
    draft conjoined a point estimate with a bound, which made the operative
    threshold in observed-coverage units a function of V — that is, of the
    data — while calling itself frozen. A bound already carries the sample
    size, so this cut is fixed before the batch in the unit it is stated in.

    One escalation, on distinct evidence: a class reached mostly with wrong
    labels moves one step toward FULL. The pipeline-invalid rate does NOT
    escalate a class — it already widens every interval by shrinking V, and
    charging it twice would count one event twice. §5 reports it as one
    stated caution over the whole batch instead.
    """
    if coverage["rate"] is None:
        return {"base": None, "escalations": [], "tier": None, "lower": None}
    lower = coverage["ci95"][0]
    if lower >= LIGHT_LOWER_BOUND:
        base = "LIGHT"
    elif lower >= STANDARD_LOWER_BOUND:
        base = "STANDARD"
    else:
        base = "FULL"
    escalations = []
    if mislabel_share is not None and mislabel_share >= MISLABEL_ESCALATION:
        escalations.append("mislabel")
    index = min(len(TIERS) - 1, TIERS.index(base) + len(escalations))
    return {"base": base, "escalations": escalations, "tier": TIERS[index],
            "lower": lower}


def light_threshold(n: int) -> int:
    """The smallest k whose exact lower bound reaches §5's LIGHT cut at n
    trials. The lower bound is increasing in k, so this is a bisection over k
    and not a scan."""
    low, high = 0, n
    while low < high:
        middle = (low + high) // 2
        if lower_bound(middle, n) >= LIGHT_LOWER_BOUND:
            high = middle
        else:
            low = middle + 1
    return low


def probability_at_least(k: int, n: int, p: Fraction) -> Fraction:
    """P(X >= k) for X ~ Binomial(n, p), exactly. Same arithmetic as the
    interval: math.comb and Fractions, no libm and no rounding."""
    return _tail_ge(k, n, p)


def light_operating_characteristics(n: int, probabilities) -> dict:
    """P(this mapping assigns LIGHT | true coverage p), exactly, at n trials.

    §5 registers this table rather than leaving the mapping's power implicit:
    a cut on an exact lower bound is conservative by construction, and a
    reader is entitled to know how often a genuinely well-covered class is
    still called STANDARD at N = 50.
    """
    threshold = light_threshold(n)
    return {"trials": n, "lightThresholdK": threshold,
            "lightThresholdRate": threshold / n,
            "probabilities": {str(p): float(probability_at_least(threshold, n, p))
                              for p in probabilities}}


# --- the classes -----------------------------------------------------------

def load_family(path: str, pinned: str) -> list:
    """The six coverage classes: FAMILY.json's predicate members, at the
    pinned digest. The patches are not read — this study plants nothing."""
    actual = file_digest(path)
    if actual != pinned:
        raise ScoreError("FAMILY.json is %s, not the pinned %s" % (actual, pinned))
    family = load_json(path)
    mutations = family.get("mutations")
    if not isinstance(mutations, list) or not mutations:
        raise ScoreError("FAMILY.json carries no mutations")
    classes = [{"index": mutation["index"], "title": mutation["title"],
                "predicate": mutation["predicate"],
                "predicateProse": mutation["predicateProse"]}
               for mutation in mutations]
    indexes = [entry["index"] for entry in classes]
    if indexes != list(range(len(classes))):
        raise ScoreError("FAMILY.json's indexes are not contiguous from 0: %r" % indexes)
    return classes


def split_records(accepted: dict) -> tuple:
    """(H ids, Q ids): H is the records whose own recorded outcome equals the
    mirror's verdict, Q is the rest. Both are kept; neither is repaired."""
    high, quarantine = [], []
    for case_id, record in accepted.items():
        if policy_mirror.verdict(record["vendor"]) == record["decision"]["outcome"]:
            high.append(case_id)
        else:
            quarantine.append(case_id)
    return sorted(high), sorted(quarantine)


def class_members(accepted: dict, ids: list, predicate: dict) -> list:
    return sorted(case_id for case_id in ids
                  if policy_mirror.predicate_matches(predicate, accepted[case_id]["vendor"]))


# --- admission -------------------------------------------------------------

def _regular(path: str) -> bool:
    return os.path.isfile(path) and not os.path.islink(path)


def compiled_files(completion_path: str) -> dict:
    """{relative path: bytes} for one run's records, regenerated from the
    retained completion bytes every time it is asked. Study 010 compared a
    committed records/ tree to this; Study 011 has no committed tree — every
    run has its own — so the regeneration IS the artifact, and its digest is
    published per run so a reader recomputes rather than trusts."""
    raw = records_compile.read_completion(completion_path)
    accepted, ledger, span = records_compile.compile_records(raw)
    return records_compile.render(accepted, ledger, span)


def admit(slot: str, prompt_path: str, golden_path: str, pins: dict) -> tuple:
    """(code, detail, authoring-empty): code is None when the run is valid.

    The checks run in the documented order and the FIRST failure names the
    run. Nothing here consults the batch's own refusal record; reconciling
    with it is score_run()'s job, so that a batch refusal can never make an
    inadmissible run look examined or an admissible one look refused.
    """
    for name in SLOT_FILES:
        if not _regular(os.path.join(slot, name)):
            return "slot-shape", "%s is missing or not a regular file" % name, False
    try:
        call = load_json(os.path.join(slot, "CALL.json"))
    except ValueError as error:
        return "call-unreadable", str(error), False
    if not isinstance(call, dict):
        return "call-unreadable", "CALL.json is not a JSON object", False
    if call.get("model") != pins["codex"]["model"]:
        return "model-mismatch", "CALL.json names model %r" % call.get("model"), False
    if call.get("binarySha256") != pins["codex"]["binarySha256"]:
        return "binary-mismatch", "CALL.json names binary %r" % call.get("binarySha256"), False
    if call.get("cli") != pins["codex"]["version"]:
        return "cli-mismatch", "CALL.json names CLI %r" % call.get("cli"), False
    # C6: isolation demonstrated per run, not asserted once. The wrapper's own
    # record of what it did — a fresh home, a scrubbed environment, and an
    # isolated home whose RECURSIVE inventory is exactly the .codex directory
    # and, when one was copied, the credential inside it. Both branches carry
    # information: a stray config.toml, an AGENTS.md, or a skills tree in the
    # isolated home refuses, and a machine with no operator credential is
    # admissible rather than uniformly isolation-unproven (§2.3 item 6). The
    # golden context match below is still the evidence that bites hardest.
    for flag in ("homeIsolated", "codexHomeIsolated", "environmentScrubbed",
                 "ignoreUserConfig"):
        if call.get(flag) is not True:
            return "isolation-unproven", "CALL.json does not record %s" % flag, False
    if not isinstance(call.get("home"), str) or not call["home"]:
        return "isolation-unproven", "CALL.json records no isolated home", False
    expected_inventory = ([".codex", ".codex/auth.json"]
                          if call.get("credentialCopied") else [".codex"])
    if call.get("isolatedHomeInventory") != expected_inventory:
        return ("isolation-unproven",
                "the isolated home held %r before the call, not the %r a fresh home "
                "with %s accounts for"
                % (call.get("isolatedHomeInventory"), expected_inventory,
                   "the copied credential" if call.get("credentialCopied")
                   else "no credential to copy"), False)
    if call.get("newSessionCount") != 1:
        return ("session-count",
                "the call produced %r new sessions" % call.get("newSessionCount"), False)
    status = call.get("exitStatus")
    if not isinstance(status, int) or isinstance(status, bool) or status != 0:
        return "call-nonzero-exit", "exit status %r" % status, False
    session = os.path.join(slot, "session.jsonl")
    completion = os.path.join(slot, "completion.txt")
    context = os.path.join(slot, "context.json")
    if not _regular(session):
        return "no-session", "session.jsonl was not retained", False
    if not _regular(completion):
        return "no-completion", "completion.txt was not retained", False
    if not _regular(context):
        return "no-context", "context.json was not retained", False
    try:
        transcript_check.check(session, prompt_path, completion,
                               os.path.join(slot, "CALL.json"), golden_path,
                               model=pins["codex"]["model"])
    except (transcript_check.TranscriptError, ValueError) as error:
        return "transcript-refused", str(error), False
    try:
        retained = load_json(context)
    except ValueError as error:
        return "context-mismatch", str(error), False
    if retained != transcript_check.context_digests(session, call):
        return "context-mismatch", "context.json is not what session.jsonl yields", False
    try:
        raw = records_compile.read_completion(completion)
    except (UnicodeDecodeError, OSError) as error:
        return "completion-unreadable", str(error), False
    try:
        records_compile.compile_records(raw)
    except records_compile.CompileError as error:
        # §3.3: a completion with no parseable array is an AUTHORING outcome,
        # not a pipeline failure. The run is valid and covers nothing.
        return None, str(error), True
    except ValueError as error:
        return "compile-refused", str(error), False
    # Study 010 checked its committed records/ tree against the retained
    # completion. Study 011 has no committed tree, so the same check runs
    # against a throwaway one: compile it, then require the ported verify to
    # regenerate it byte-for-byte with the exact file set.
    try:
        with tempfile.TemporaryDirectory() as root:
            with contextlib.redirect_stdout(io.StringIO()):
                records_compile.cmd_compile(completion, root)
                records_compile.cmd_verify(completion, root)
    except (records_compile.CompileError, ValueError, OSError) as error:
        return "regeneration-mismatch", str(error), False
    return None, None, False


# --- scoring ---------------------------------------------------------------

def score_run(slot: str, prompt_path: str, golden_path: str, pins: dict,
              classes: list) -> dict:
    """One slot's row: valid or not, and — when valid — its coverage."""
    name = os.path.basename(slot)
    refusal_path = os.path.join(slot, "REFUSAL.json")
    batch_code = None
    if os.path.exists(refusal_path):
        try:
            batch_code = load_json(refusal_path).get("code")
        except ValueError:
            batch_code = "unreadable-refusal-record"
    try:
        code, detail, empty = admit(slot, prompt_path, golden_path, pins)
    except Exception as error:  # noqa: BLE001 — totality is the point
        # §7: a malformed or missing slot artifact yields a recorded verdict,
        # never a bare exception that stops the scoring of every other slot.
        code, detail, empty = "scorer-error", "%s: %s" % (type(error).__name__, error), False
    if batch_code is not None and code is None:
        code, detail, empty = "refusal-conflict", (
            "the batch recorded %r but the retained bytes admit the run" % batch_code), False
    row = {"slot": name, "valid": code is None, "code": code, "detail": detail,
           "batchCode": batch_code}
    if code is not None:
        return row
    completion = os.path.join(slot, "completion.txt")
    if empty:
        accepted, ledger = {}, []
    else:
        raw = records_compile.read_completion(completion)
        accepted, ledger, _ = records_compile.compile_records(raw)
    drops: dict = {}
    for _, case_id, drop in ledger:
        if not case_id:
            drops[drop] = drops.get(drop, 0) + 1
    high, quarantine = split_records(accepted)
    covered, raw_covered, q_reached, q_only = [], [], [], []
    members = {}
    for entry in classes:
        index = entry["index"]
        in_h = class_members(accepted, high, entry["predicate"])
        in_q = class_members(accepted, quarantine, entry["predicate"])
        if in_h:
            covered.append(index)
        if in_h or in_q:
            raw_covered.append(index)
        if in_q:
            q_reached.append(index)
        if in_q and not in_h:
            q_only.append(index)
        members[str(index)] = {"h": in_h, "q": in_q}
    row.update({
        "accepted": len(accepted),
        "dropped": len(ledger) - len(accepted),
        "dropCodes": dict(sorted(drops.items())),
        "h": len(high), "q": len(quarantine),
        # §3.3's third authoring outcome: admissible evidence, nothing usable.
        "authoringEmpty": empty or not accepted or not high,
        "noParseableArray": empty,
        "coveredClasses": covered,
        "rawClasses": raw_covered,
        "qClasses": q_reached,
        "qOnlyClasses": q_only,
        "classesCovered": len(covered),
        "classMembers": members,
        "completionSha256": file_digest(completion),
        "compiledSha256": None if empty else tree_digest(compiled_files(completion)),
    })
    return row


def collect_slots(slots_dir: str) -> tuple:
    """(slot paths in run order, unexpected entry names). A slot is a
    directory named run-<digits>; anything else is reported, never scored.
    The indices must be exactly the contiguous range 1…N (§6 C5): a gap is a
    slot that was created and removed, and no rate may be computed over a
    population with a hole in it."""
    if not os.path.isdir(slots_dir):
        raise ScoreError("%s is not a directory" % slots_dir)
    slots, unexpected, indexes = [], [], []
    for name in sorted(os.listdir(slots_dir)):
        path = os.path.join(slots_dir, name)
        parts = name.split("-", 1)
        if os.path.isdir(path) and not os.path.islink(path) \
                and len(parts) == 2 and parts[0] == "run" and parts[1].isdigit():
            slots.append(path)
            indexes.append(int(parts[1]))
        elif name not in ("BATCH.json", "SHORTFALL.json"):
            unexpected.append(name)
    if indexes != list(range(1, len(indexes) + 1)):
        raise ScoreError("the slot indices are not the contiguous range 1..%d: %r"
                         % (len(indexes), indexes))
    return slots, unexpected


def _sequence_halves(sequence: list) -> dict:
    """S7: the ordered 0/1 sequence over valid runs, split in half. A drift
    check, published rather than tested — no trend statistic is registered."""
    half = len(sequence) // 2
    return {"sequence": sequence,
            "firstHalf": sum(sequence[:half]),
            "secondHalf": sum(sequence[half:])}


def verify_preconditions(pins_path: str, prompt_path: str, golden_path: str,
                         study: str = STUDY) -> dict:
    """Everything that must hold before a single slot is read (§6 C1, §3.2,
    §2.6). A drifted port, an unregistered golden capture, or a
    post-freeze-edited preregistration refuses the whole scoring — none of
    them can be discovered afterwards from a published rate."""
    try:
        ported = integrity.verify(study=study, pins_path=pins_path)
    except integrity.IntegrityError as error:
        raise ScoreError("the ported bytes are not the registered ones: %s" % error)
    pins = load_json(pins_path)
    prompt_digest = file_digest(prompt_path)
    if prompt_digest != pins["prompt"]["sha256"]:
        raise ScoreError("the prompt is %s, not the pinned %s"
                         % (prompt_digest, pins["prompt"]["sha256"]))
    if not os.path.isfile(golden_path):
        raise ScoreError("no golden context at %s: recapture it before the batch "
                         "(batch.py capture --scratch-parent DIR)" % golden_path)
    # §3.2 step 3: the capture's digest replaces the null in the registry, and
    # both are committed BEFORE the first slot runs. A golden file that is not
    # the registered one — including one derived after the batch from the
    # batch's own slots — scores nothing.
    golden_pin = pins.get("golden", {}).get("sha256")
    if not golden_pin:
        raise ScoreError(
            "harness/PINS.json registers no golden.sha256: the golden capture must be "
            "captured, registered and committed before the first slot (§3.2)")
    golden_digest = file_digest(golden_path)
    if golden_digest != golden_pin:
        raise ScoreError("the golden capture at %s is %s, not the registered %s"
                         % (golden_path, golden_digest, golden_pin))
    prereg_pin = pins.get("preregistration", {}).get("sha256")
    prereg_digest = None
    if prereg_pin:
        prereg_path = os.path.join(study, pins["preregistration"]["path"])
        if not os.path.isfile(prereg_path):
            raise ScoreError("the preregistration is missing from %s" % study)
        prereg_digest = file_digest(prereg_path)
        if prereg_digest != prereg_pin:
            raise ScoreError("PREREGISTRATION.md is %s, not the %s registered at the "
                             "freeze: it was edited after the freeze"
                             % (prereg_digest, prereg_pin))
    return {"portedFiles": ported["portedFiles"],
            "study010LockSha256": ported["study010LockSha256"],
            "promptSha256": prompt_digest,
            "goldenSha256": golden_digest,
            "preregistrationSha256": prereg_digest}


def terminality(slots: list, slots_dir: str, registered) -> dict:
    """§2.4: exactly N slots, XOR a shortfall declaration whose recorded count
    is the contiguous slots actually present. Both, or neither, refuses —
    a shortfall over a full batch is not a short batch, and an over-full batch
    is not a population this study contemplates."""
    shortfall_path = os.path.join(slots_dir, "SHORTFALL.json")
    shortfall = load_json(shortfall_path) if os.path.isfile(shortfall_path) else None
    if registered is None:
        return shortfall
    complete = len(slots) == registered
    if complete and shortfall is not None:
        raise ScoreError("all %d registered slots are present and SHORTFALL.json also "
                         "declares a short batch: the batch cannot be both" % registered)
    if not complete and shortfall is None:
        raise ScoreError("%d of %d registered slots are present and no SHORTFALL.json "
                         "declares why: the batch is not terminal"
                         % (len(slots), registered))
    if not complete:
        if len(slots) > registered:
            raise ScoreError("%d slots are present but only %d were registered: a "
                             "shortfall declaration does not admit an over-full batch"
                             % (len(slots), registered))
        if shortfall.get("completedSlots") != len(slots):
            raise ScoreError("SHORTFALL.json records %r completed slots and %d are "
                             "present: the declaration is not this batch's"
                             % (shortfall.get("completedSlots"), len(slots)))
    return shortfall


def score(slots_dir: str, pins_path: str, family_path: str, prompt_path: str,
          golden_path: str) -> dict:
    preconditions = verify_preconditions(pins_path, prompt_path, golden_path)
    pins = load_json(pins_path)
    prompt_digest = preconditions["promptSha256"]
    classes = load_family(family_path, pins["family"]["sha256"])
    slots, unexpected = collect_slots(slots_dir)

    # §2.4: no rate before the batch is terminal.
    registered = pins.get("batch", {}).get("runs")
    shortfall = terminality(slots, slots_dir, registered)

    rows = [score_run(slot, prompt_path, golden_path, pins, classes) for slot in slots]
    valid = [row for row in rows if row["valid"]]
    invalid = [row for row in rows if not row["valid"]]
    n = len(valid)
    codes: dict = {}
    for row in invalid:
        codes[row["code"]] = codes.get(row["code"], 0) + 1
    pipeline_rate = len(invalid) / len(rows) if rows else None

    class_rows = []
    for entry in classes:
        index = entry["index"]
        coverage_sequence = [1 if index in row["coveredClasses"] else 0 for row in valid]
        raw_covered = sum(1 for row in valid if index in row["rawClasses"])
        q_reached = sum(1 for row in valid if index in row["qClasses"])
        q_only = sum(1 for row in valid if index in row["qOnlyClasses"])
        coverage = rate_block(sum(coverage_sequence), n)
        # S2's mislabel share: of the runs that reached the class at all, the
        # share that reached it only with a wrong label. 0 when none reached it.
        share = q_only / raw_covered if raw_covered else 0.0
        class_rows.append({
            "index": index,
            "title": entry["title"],
            "predicateProse": entry["predicateProse"],
            "coverage": coverage,
            "rawIntersection": rate_block(raw_covered, n),
            "qIntersection": rate_block(q_reached, n),
            "qOnlyIntersection": rate_block(q_only, n),
            "mislabelShare": share,
            "drift": _sequence_halves(coverage_sequence),
            "reviewTier": review_tier(coverage, share),
        })

    # §4.2: the six denominators are identical by construction — and the
    # scorer asserts it rather than asking the reader to trust the
    # construction. A per-class denominator would make the six rates
    # incomparable and no published integer would show it.
    denominators = set(row["coverage"]["trials"] for row in class_rows)
    if denominators != {n}:
        raise ScoreError("the class denominators are %r, not the %d valid runs: the "
                         "rates are not comparable" % (sorted(denominators), n))

    distribution = {str(k): 0 for k in range(len(classes) + 1)}
    for row in valid:
        distribution[str(row["classesCovered"])] += 1
    all_six = sum(1 for row in valid if row["classesCovered"] == len(classes))

    h_total = sum(row["h"] for row in valid)
    q_total = sum(row["q"] for row in valid)
    accuracies = [row["h"] / (row["h"] + row["q"]) for row in valid if row["h"] + row["q"]]
    accepted_total = sum(row["accepted"] for row in valid)
    dropped_total = sum(row["dropped"] for row in valid)
    drop_codes: dict = {}
    for row in valid:
        for code, count in row["dropCodes"].items():
            drop_codes[code] = drop_codes.get(code, 0) + count

    outputs: dict = {}
    for row in valid:
        outputs.setdefault(row["completionSha256"], []).append(row["slot"])

    return {
        "resultsVersion": "1",
        "study": "011-authorship-coverage-rates",
        "cell": {
            "model": pins["codex"]["model"],
            "cli": pins["codex"]["version"],
            "binarySha256": pins["codex"]["binarySha256"],
            "promptSha256": prompt_digest,
            "familySha256": pins["family"]["sha256"],
            "goldenSha256": preconditions["goldenSha256"],
            "preregistrationSha256": preconditions["preregistrationSha256"],
            "portedFiles": preconditions["portedFiles"],
            "study010LockSha256": preconditions["study010LockSha256"],
            "note": "One cell: this prompt, this model, this policy. Nothing here "
                    "is a claim about other prompts, other models, or real "
                    "operational records. The digests above were verified before "
                    "any slot was read, not copied from the registry.",
        },
        "population": {
            "slots": len(rows),
            "valid": n,
            "invalid": len(invalid),
            "pipelineInvalidRate": rate_block(len(invalid), len(rows)) if rows else None,
            "invalidCodes": dict(sorted(codes.items())),
            "authoringEmpty": sum(1 for row in valid if row["authoringEmpty"]),
            "registeredRuns": registered,
            "shortfall": None if registered is None else max(0, registered - len(slots)),
            "shortfallDeclaration": shortfall,
            "unexpectedEntries": unexpected,
            # §5: one stated caution over the whole batch, never a per-class
            # tier change — the invalid runs already widened every interval.
            "pipelineCaution": (pipeline_rate is not None
                                and pipeline_rate >= PIPELINE_CAUTION),
            "note": "Rates are computed over valid runs only; admit() is the whole "
                    "population filter (§6 C5). An authoring-empty run is VALID and "
                    "covers nothing; a pipeline-invalid run leaves the denominator "
                    "and its rate is itself an endpoint (S8). A pipeline-invalid "
                    "rate of %.2f or more raises pipelineCaution over the whole "
                    "batch and changes no class's tier." % PIPELINE_CAUTION,
        },
        "classes": class_rows,
        "coverageBreadth": {
            "distribution": distribution,
            "mean": sum(row["classesCovered"] for row in valid) / n if n else None,
            "allSix": rate_block(all_six, n) if n else None,
        },
        "labelAccuracy": {
            "h": h_total, "q": q_total,
            "rate": h_total / (h_total + q_total) if h_total + q_total else None,
            "perRunMean": sum(accuracies) / len(accuracies) if accuracies else None,
            "perRunMin": min(accuracies) if accuracies else None,
            "perRunMax": max(accuracies) if accuracies else None,
            "note": "Pooled over the valid runs' accepted records. No interval: "
                    "records within one completion are not independent trials, "
                    "and a binomial interval here would overstate its precision.",
        },
        "records": {
            "acceptedTotal": accepted_total,
            "droppedTotal": dropped_total,
            "dropCodes": dict(sorted(drop_codes.items())),
            "acceptedPerRun": {
                "min": min((row["accepted"] for row in valid), default=None),
                "max": max((row["accepted"] for row in valid), default=None),
                "mean": accepted_total / n if n else None,
            },
        },
        "distinctOutputs": {
            "validRuns": n,
            "distinctCompletions": len(outputs),
            "largestIdenticalGroup": max((len(group) for group in outputs.values()),
                                         default=0),
            "bySlot": {digest: sorted(group) for digest, group in sorted(outputs.items())},
            "note": "Identical completions across runs are data about the model, not "
                    "a defect in the batch — but they weaken the independence premise "
                    "the rates rest on, so they are read beside every rate.",
        },
        "runs": rows,
    }


# --- reporting -------------------------------------------------------------

def _rate_cell(block: dict) -> str:
    """Two markdown cells — the rate and its interval — or two dashes when
    there is no valid run to compute them from."""
    if block is None or block["rate"] is None:
        return "— | — |"
    return "%d/%d = %.3f | [%.4f, %.4f] |" % (
        block["count"], block["trials"], block["rate"],
        block["ci95"][0], block["ci95"][1])


def _rate_inline(block: dict) -> str:
    """One rate in running prose, integers first."""
    if block is None or block["rate"] is None:
        return "—"
    return "%d/%d = %.3f, 95%% CI [%.4f, %.4f]" % (
        block["count"], block["trials"], block["rate"],
        block["ci95"][0], block["ci95"][1])


def _number(value, places: int = 4) -> str:
    return "—" if value is None else ("%." + str(places) + "f") % value


def render_markdown(results: dict) -> str:
    population = results["population"]
    breadth = results["coverageBreadth"]
    lines = [
        "# Coverage rates — Study 011",
        "",
        "Generated by `harness/score_rates.py` from the retained authoring slots;",
        "every number recomputes from those bytes, and every bound recomputes from",
        "the integers in `RESULTS.json`. No clock and no randomness enter this file,",
        "so re-scoring the same slots reproduces it byte-for-byte.",
        "",
        "## The cell",
        "",
        "| what | value |",
        "|------|-------|",
        "| model | `%s` |" % results["cell"]["model"],
        "| CLI | `%s` |" % results["cell"]["cli"],
        "| binary | `%s` |" % results["cell"]["binarySha256"],
        "| prompt | `%s` |" % results["cell"]["promptSha256"],
        "| family | `%s` |" % results["cell"]["familySha256"],
        "| golden context | `%s` |" % results["cell"]["goldenSha256"],
        "",
        "## Population",
        "",
        "%d slots: **%d valid**, %d pipeline-invalid. Authoring-empty runs (valid,"
        % (population["slots"], population["valid"], population["invalid"]),
        "admissible, covering nothing): %d — counted, never excluded."
        % population["authoringEmpty"],
        "",
    ]
    if population["registeredRuns"] is not None:
        lines += ["Registered batch size %d; shortfall %d."
                  % (population["registeredRuns"], population["shortfall"]), ""]
    if population["shortfallDeclaration"]:
        lines += ["Shortfall declared: %s"
                  % population["shortfallDeclaration"].get("reason", "(no reason given)"), ""]
    if population["invalidCodes"]:
        lines += ["| refusal code | runs |", "|--------------|------|"]
        for code, count in population["invalidCodes"].items():
            lines.append("| `%s` | %d |" % (code, count))
        lines.append("")
    if population["pipelineInvalidRate"] and population["pipelineInvalidRate"]["rate"] is not None:
        lines += ["Pipeline-invalid rate (S8): %s."
                  % _rate_inline(population["pipelineInvalidRate"]), ""]
    if population["unexpectedEntries"]:
        lines += ["Entries under the slot tree that are not slots (reported, not "
                  "scored): %s." % ", ".join("`%s`" % name for name in
                                             population["unexpectedEntries"]), ""]

    lines += [
        "## Primary: per-class coverage rate",
        "",
        "c_i = the fraction of valid runs in which a correctly-labelled record (H)",
        "falls in class i. Intervals are exact Clopper-Pearson at 95%, marginal per",
        "class — they are not a simultaneous region, and no joint coverage is claimed.",
        "",
        "| # | class | c_i | 95% CI |",
        "|---|-------|-----|--------|",
    ]
    for entry in results["classes"]:
        lines.append("| %d | %s | %s" % (
            entry["index"], entry["predicateProse"], _rate_cell(entry["coverage"])))
    lines += [
        "",
        "## Review depth, from the mapping registered before the batch",
        "",
        "§5's thresholds applied, not fitted, and decided by ONE quantity: the exact",
        "Clopper-Pearson lower bound. LIGHT needs lower ≥ %.2f, STANDARD needs lower ≥"
        % LIGHT_LOWER_BOUND,
        "%.2f, below that is FULL. A class whose mislabel share reaches %.2f escalates"
        % (STANDARD_LOWER_BOUND, MISLABEL_ESCALATION),
        "one step toward FULL. The pipeline-invalid rate escalates nothing: it already",
        "widened every interval, and it is reported as one caution over the batch.",
        "",
        "| # | c_i | lower bound | mislabel share | base | escalations | tier |",
        "|---|-----|-------------|----------------|------|-------------|------|",
    ]
    for entry in results["classes"]:
        tier = entry["reviewTier"]
        lines.append("| %d | %s | %s | %s | %s | %s | **%s** |" % (
            entry["index"],
            "—" if entry["coverage"]["rate"] is None else "%.3f" % entry["coverage"]["rate"],
            _number(tier["lower"]),
            _number(entry["mislabelShare"], 3), tier["base"] or "—",
            ", ".join(tier["escalations"]) or "none", tier["tier"] or "—"))
    if population.get("pipelineCaution"):
        lines += [
            "",
            "**Stated caution (§5).** The pipeline-invalid rate is %.2f or more: this"
            % PIPELINE_CAUTION,
            "batch's authoring pipeline failed often enough that every rate above is",
            "computed over a reduced V and every tier is read under that caution. No",
            "class's tier was changed for it — one event, charged once.",
        ]
    lines += [
        "",
        "## Secondary",
        "",
        "`raw` ignores the record's own label (any accepted record in the class);",
        "`Q` counts runs where a mislabelled record falls in the class; `Q-only`",
        "counts the runs where the class was reached ONLY by such records —",
        "Study 010's authoring-label-failure mode, per class.",
        "",
        "| # | raw | 95% CI | Q | 95% CI | Q-only | 95% CI |",
        "|---|-----|--------|---|--------|--------|--------|",
    ]
    for entry in results["classes"]:
        lines.append("| %d | %s %s %s" % (
            entry["index"], _rate_cell(entry["rawIntersection"]),
            _rate_cell(entry["qIntersection"]),
            _rate_cell(entry["qOnlyIntersection"])))
    lines += [
        "",
        "### Coverage breadth per run",
        "",
        "| classes covered | runs |",
        "|-----------------|------|",
    ]
    for covered, count in sorted(breadth["distribution"].items(),
                                 key=lambda item: int(item[0])):
        lines.append("| %s | %d |" % (covered, count))
    lines += [
        "",
        "Mean classes covered: %s. All six covered: %s."
        % (_number(breadth["mean"], 3), _rate_inline(breadth["allSix"])),
        "",
    ]
    accuracy = results["labelAccuracy"]
    records = results["records"]
    lines += [
        "### Records and labels",
        "",
        "| what | value |",
        "|------|-------|",
        "| accepted records (valid runs) | %d |" % records["acceptedTotal"],
        "| dropped elements | %d |" % records["droppedTotal"],
        "| drop codes | %s |" % (", ".join("`%s`×%d" % (code, count) for code, count
                                           in records["dropCodes"].items()) or "none"),
        "| accepted per run (min/mean/max) | %s / %s / %s |" % (
            records["acceptedPerRun"]["min"], _number(records["acceptedPerRun"]["mean"], 3),
            records["acceptedPerRun"]["max"]),
        "| H / Q | %d / %d |" % (accuracy["h"], accuracy["q"]),
        "| label accuracy \\|H\\|/(\\|H\\|+\\|Q\\|) | %s |" % _number(accuracy["rate"]),
        "| per-run label accuracy (min/mean/max) | %s / %s / %s |" % (
            _number(accuracy["perRunMin"]), _number(accuracy["perRunMean"]),
            _number(accuracy["perRunMax"])),
        "| distinct completions | %d of %d valid runs (largest identical group %d) |" % (
            results["distinctOutputs"]["distinctCompletions"],
            results["distinctOutputs"]["validRuns"],
            results["distinctOutputs"]["largestIdenticalGroup"]),
        "",
        "No interval is given for label accuracy: records inside one completion",
        "are not independent trials.",
        "",
        "### Coverage against run index",
        "",
        "The ordered 0/1 sequence per class over valid runs, and its halves. A",
        "drift check, descriptive only: no trend statistic is registered.",
        "",
        "| # | first half | second half | sequence |",
        "|---|------------|-------------|----------|",
    ]
    for entry in results["classes"]:
        drift = entry["drift"]
        lines.append("| %d | %d | %d | `%s` |" % (
            entry["index"], drift["firstHalf"], drift["secondHalf"],
            "".join(str(value) for value in drift["sequence"]) or "—"))
    lines += [
        "",
        "### Every run, in run order",
        "",
        "| run | valid | accepted | dropped | H | Q | classes covered |",
        "|-----|-------|----------|---------|---|---|-----------------|",
    ]
    for row in results["runs"]:
        if row["valid"]:
            lines.append("| `%s` | yes%s | %d | %d | %d | %d | %s |" % (
                row["slot"], " (authoring-empty)" if row["authoringEmpty"] else "",
                row["accepted"], row["dropped"], row["h"], row["q"],
                ", ".join(str(index) for index in row["coveredClasses"]) or "none"))
        else:
            lines.append("| `%s` | no — `%s` | — | — | — | — | — |" % (
                row["slot"], row["code"]))
    lines += [
        "",
        "## What these rates are and are not",
        "",
        "They are frequencies of one prompt against one model on one synthetic",
        "policy, counted by this study's own mirror. The mirror is the reference",
        "semantics, not ground truth; a record is \"correctly labelled\" here when",
        "the model's recorded outcome agrees with it. Coverage of a class means a",
        "record fell in the class, not that any defect was found — no pack is",
        "evaluated in this study. The review tiers are a registered sketch, not a",
        "validated instrument. Byte-lineage, not truth.",
        "",
    ]
    return "\n".join(lines)


def emit_records(rows: list, slots_dir: str, out_dir: str) -> None:
    """Optional: write each valid run's compiled record tree, so a reader can
    diff the records themselves. Deterministic and derived — nothing here
    enters a rate."""
    for row in rows:
        if not row["valid"] or row.get("noParseableArray"):
            continue
        target = os.path.join(out_dir, row["slot"])
        for relative, body in compiled_files(
                os.path.join(slots_dir, row["slot"], "completion.txt")).items():
            path = os.path.join(target, relative)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as handle:
                handle.write(body)


def write_outputs(results: dict, out_dir: str, slots_dir: str = None,
                  records_dir: str = None) -> None:
    """RESULTS.json and RATES.md, and optionally the derived record trees.

    `main()` always passes the study root — there is no CLI flag that moves
    the rate table anywhere else (§2.4). The parameter exists so the
    determinism test can score the same tree into two throwaway directories
    and compare the bytes without writing into the committed study."""
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "RESULTS.json"), "wb") as handle:
        handle.write((json.dumps(results, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    with open(os.path.join(out_dir, "RATES.md"), "wb") as handle:
        handle.write(render_markdown(results).encode("utf-8"))
    if records_dir:
        emit_records(results["runs"], slots_dir, records_dir)


def _argument(argv: list, flag: str, default=None):
    if flag not in argv:
        return default
    index = argv.index(flag)
    if index + 1 >= len(argv):
        raise ScoreError("%s needs a value" % flag)
    return argv[index + 1]


def main(argv: list) -> int:
    if len(argv) < 2 or argv[1] != "score":
        print("usage: score_rates.py score --slots DIR [--pins P] [--family F] "
              "[--prompt P] [--golden G] [--emit-records DIR]",
              file=sys.stderr)
        return 2
    try:
        if "--out" in argv:
            raise ScoreError(
                "--out was removed: RESULTS.json and RATES.md go to the study root, "
                "and nowhere else. A rate table written elsewhere would let the "
                "operator see six rates while the driver still accepted new slots "
                "(§2.4). --emit-records DIR still takes a directory.")
        slots_dir = _argument(argv, "--slots")
        if slots_dir is None:
            raise ScoreError("--slots is required")
        results = score(slots_dir, _argument(argv, "--pins", DEFAULT_PINS),
                        _argument(argv, "--family", DEFAULT_FAMILY),
                        _argument(argv, "--prompt", DEFAULT_PROMPT),
                        _argument(argv, "--golden", DEFAULT_GOLDEN))
        write_outputs(results, STUDY, slots_dir, _argument(argv, "--emit-records"))
    except ScoreError as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1
    print("scored: %d valid of %d slots" % (
        results["population"]["valid"], results["population"]["slots"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
