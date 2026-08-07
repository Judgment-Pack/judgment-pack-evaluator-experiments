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

  slot-symlink           the slot tree holds a symlink — anywhere, under any
                         name, dangling or not (§3.3)
  slot-irregular         the slot tree holds an entry that is neither a regular
                         file nor a directory nor a symlink — a FIFO, a socket,
                         a device, a door (§3.3). Decided by lstat BEFORE
                         anything is opened, because opening a FIFO blocks
  slot-shape             a required slot file is missing or not a regular file
  call-unreadable        CALL.json is not duplicate-free JSON
  model-mismatch         CALL.json names a model other than the pinned one
  binary-mismatch        CALL.json names a binary digest other than the pinned one
  cli-mismatch           CALL.json names a CLI version other than the pinned one
  registry-mismatch      the run was made under a registry that is not the
                         committed harness/PINS.json (§2.6)
  golden-mismatch        the run was made against a golden capture that is not
                         the one this scoring is using (§3.2)
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

Before it reads a slot it verifies, and refuses on: the ported-byte digest
table with every source bound to Study 010's own lock and the running
interpreter bound to the registry (harness/integrity.py, §6 C1, §2.6); the
golden capture against the digest harness/PINS.json registers for it (§3.2);
the preregistration's own digest, which must be registered and must match —
a null there is a refusal, not a skip (§2.6); and the batch's terminality
(§2.4). Then, per slot, it requires the run to name the registry and the
golden capture it was made under (`registry-mismatch`, `golden-mismatch`), so
neither an alternate `--pins` registry nor a capture derived after the batch
can redefine what a counted run meant.

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

**The registered scoring interface is `score_registered()`, and it is the only
thing in this harness that publishes** (§7). It takes the slot directory and
an optional record-emission directory and NOTHING ELSE: the registry, the
family, the prompt and the golden capture are all derived from this module's
own location, so there is no flag, default, argument or environment variable
through which an alternate registry could redefine N, the class definitions,
or which model a run had to be made by — this module reads no environment at
all. It computes the results and hands them straight to the module-private
`_write_outputs()`, which writes RESULTS.json and RATES.md to the study root
and nowhere else; no results dict crosses a public boundary into publication,
because there is no public writer to hand one to. A rate table written
somewhere else would let the operator read six rates while leaving the marker
the driver refuses new slots on (§2.4).

The `registry_sha256` override on `score()`, `score_run()` and `admit()`
exists for library callers whose slots were made under a stand-in registry
(the wrapper-driven harness tests). Those callers get a dict and no way to
publish it: `score()` records the override in `cell.registryOverride`, and
`_write_outputs()` refuses any results carrying one AND re-derives the
committed registry's digest, the registered N, and the prompt/family/golden/
preregistration digests from the study tree, requiring the results to agree —
so a results dict edited to hide its override still cannot be published under
a registry that is not the committed one. What no check inside a file can
refuse is a caller who edits this file or rebinds its module constants in
process; §7 states that ceiling once and does not restate it.

Usage:
  score_rates.py score --slots DIR [--emit-records DIR]

Any other argument refuses. An ignored flag is how a stale command line lies
silently, so an unknown one is a refusal rather than a no-op.
"""
from __future__ import annotations
import contextlib
import hashlib
import io
import json
import math
import os
import stat
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

SLOT_FILES = ("CALL.json", "stdout.raw", "stderr.raw")
# §2.6: the registry of record is the COMMITTED harness/PINS.json, and the
# scorer computes its digest rather than accepting one. The registered command
# has no flag that supplies any of the four paths below — they are derived from
# this module's own location, so a stand-in registry cannot be handed to the
# thing that publishes. `batch.py --pins` still exists, because the harness
# tests drive the real wrapper against a stand-in binary; a slot stamped with
# any other registry's digest is pipeline-invalid.
REGISTRY_OF_RECORD = os.path.join(HERE, "PINS.json")
REGISTERED_FAMILY = os.path.join(STUDY, "FAMILY.json")
REGISTERED_PROMPT = os.path.join(STUDY, "transcription", "PROMPT.txt")
REGISTERED_GOLDEN = os.path.join(STUDY, "transcription", "GOLDEN-CONTEXT.json")
# The member every scoring carries: null when the registry digest was computed
# from REGISTRY_OF_RECORD (the registered path), and the supplied digest when a
# library caller overrode it. The module-private _write_outputs() refuses to
# publish a table whose cell does not carry this member, or carries it non-null,
# and re-derives every other cell digest from the study tree (§7).
REGISTRY_OVERRIDE = "registryOverride"
# §2.2 / C6: the environment the wrapper constructs rather than inherits. The
# child PATH is exactly these six system directories plus one per-run directory
# holding a single symlink to the pinned binary.
SYSTEM_PATH = ("/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin",
               "/sbin", "/bin")
ENVIRONMENT_NAMES = ["PATH", "HOME", "TMPDIR", "CODEX_HOME"]
CLOSED_STDIN = "closed (/dev/null)"
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
    "slot-symlink": "pipeline-invalid",
    "slot-irregular": "pipeline-invalid",
    "slot-shape": "pipeline-invalid",
    "call-unreadable": "pipeline-invalid",
    "model-mismatch": "pipeline-invalid",
    "binary-mismatch": "pipeline-invalid",
    "cli-mismatch": "pipeline-invalid",
    "registry-mismatch": "pipeline-invalid",
    "golden-mismatch": "pipeline-invalid",
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


def row_review_tier(tiers) -> str:
    """§5's row-level composition rule: the review depth for ONE matrix row,
    given the tiers of every class its facts fall in.

    The classes are not disjoint — 010's ANALYSIS.md says so, and a
    non-embargoed row at risk exactly 70 matches classes 0 and 1 — so "the
    class its facts fall in" was not a function. Two clauses make it one:

      * a row matching several classes takes the STRICTEST of their tiers.
        Review depth is a floor on effort, and the class with the worst blind
        coverage is the one that says how much of this row nobody looked at;
      * a row matching NO registered class takes FULL. This study measured six
        predicates and says nothing about a row outside all of them, and the
        conservative reading of "nothing is known" is full review.

    Registered here and exercised by a harness test rather than left as prose,
    because a mapping with an undefined case is not a registered mapping. This
    study computes per-class tiers only — no row is scored here — so this
    function is the registration, not a step in the batch.
    """
    for tier in tiers:
        if tier not in TIERS:
            raise ScoreError("%r is not one of this study's review tiers %r"
                             % (tier, list(TIERS)))
    ranks = [TIERS.index(tier) for tier in tiers]
    return TIERS[max(ranks)] if ranks else TIERS[-1]


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
    """A regular file, decided by lstat: a symlink to one is not one, and
    nothing here is opened to find out."""
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except OSError:
        return False


# The file types a slot tree may not hold, named so a refusal says which one
# was found rather than "not a regular file". Anything not in this table and
# not a regular file, directory or symlink is reported as `unknown type`.
IRREGULAR_KINDS = (
    (stat.S_ISFIFO, "FIFO"),
    (stat.S_ISSOCK, "socket"),
    (stat.S_ISCHR, "character device"),
    (stat.S_ISBLK, "block device"),
    (stat.S_ISDOOR if hasattr(stat, "S_ISDOOR") else (lambda mode: False), "door"),
)


def _kind(mode: int) -> str:
    for predicate, name in IRREGULAR_KINDS:
        if predicate(mode):
            return name
    return "unknown type"


def slot_irregularities(slot: str) -> tuple:
    """(symlinks, irregular entries) in a slot tree, relative to the slot and
    sorted — everything in it that is not a regular file or a directory.

    Study 010's seal used the general rule and this study needed it: a slot
    tree may hold REGULAR FILES AND DIRECTORIES ONLY. The defect that made the
    rule necessary here was narrow — `REFUSAL.json` as a DANGLING symlink
    passes `os.path.exists()`, so the strict refusal loader was never reached
    and the slot proceeded as if the batch had never terminated it — but the
    class is not, and it is not only symlinks. A link is a retained byte the
    slot does not contain, or a file whose existence depends on a target
    outside the published evidence. A FIFO, a socket or a device is worse: it
    is not retained evidence at all, and a FIFO named `REFUSAL.json` does not
    merely mislead a reader — `open()` on it BLOCKS, so a scorer that reached
    it would hang over the whole batch rather than refuse one slot. That is
    why every entry's type is decided by `os.lstat` BEFORE anything in the
    tree is opened, and why this runs before every other check in `admit()`.

    Two codes, because the two say different things and §3.3 registers both:
    `slot-symlink` for links (dangling or resolving), `slot-irregular` for
    every other non-regular, non-directory type.

    Nothing here follows a link: the walk is iterative over `os.scandir`,
    descends only into entries `lstat` calls directories, and a dangling link
    is found because `S_ISLNK` is a question about the entry and not about its
    target.
    """
    symlinks, irregular = [], []

    def classify(path: str, relative: str) -> bool:
        """True when this entry is a directory to descend into."""
        try:
            mode = os.lstat(path).st_mode
        except OSError as error:
            irregular.append("%s (unreadable: %s)" % (relative, error.strerror))
            return False
        if stat.S_ISLNK(mode):
            symlinks.append(relative)
            return False
        if stat.S_ISDIR(mode):
            return True
        if stat.S_ISREG(mode):
            return False
        irregular.append("%s (%s)" % (relative, _kind(mode)))
        return False

    if classify(slot, "."):
        pending = [(slot, "")]
        while pending:
            base, prefix = pending.pop()
            try:
                names = sorted(os.listdir(base))
            except OSError as error:
                irregular.append("%s (unreadable: %s)" % (prefix or ".", error.strerror))
                continue
            for name in names:
                relative = os.path.join(prefix, name) if prefix else name
                if classify(os.path.join(base, name), relative):
                    pending.append((os.path.join(base, name), relative))
    return sorted(symlinks), sorted(irregular)


def compiled_files(completion_path: str) -> dict:
    """{relative path: bytes} for one run's records, regenerated from the
    retained completion bytes every time it is asked. Study 010 compared a
    committed records/ tree to this; Study 011 has no committed tree — every
    run has its own — so the regeneration IS the artifact, and its digest is
    published per run so a reader recomputes rather than trusts."""
    raw = records_compile.read_completion(completion_path)
    accepted, ledger, span = records_compile.compile_records(raw)
    return records_compile.render(accepted, ledger, span)


def _under(path: str, root: str) -> bool:
    """True when `path` is strictly inside `root`. String containment on
    normalized paths: these are recorded strings from a run that has already
    ended, not live paths to resolve, and a symlink question cannot be asked
    of them."""
    if not isinstance(path, str) or not isinstance(root, str) or not root:
        return False
    return os.path.normpath(path).startswith(os.path.normpath(root) + os.sep)


def _same(first: str, second: str) -> bool:
    """The case `_under()` does not cover, and the one C6 needs covered: two
    recorded paths that are the SAME directory. `_under()` tests strict
    descent, so `cwd == home` passed the un-nested-workspace clause while §6 C6
    registers a workspace that is not the home it was given."""
    if not isinstance(first, str) or not isinstance(second, str) or not first:
        return False
    return os.path.normpath(first) == os.path.normpath(second)


def _resolved(path) -> bool:
    """C6 registers the RESOLVED isolated home and working directory, and this
    is as much of "resolved" as a recorded string can be held to: absolute,
    and already in normal form, so no `..`, no `.`, and no doubled separator
    can make two names for one directory read as two directories."""
    return isinstance(path, str) and bool(path) and os.path.isabs(path) \
        and os.path.normpath(path) == path


def check_environment(call: dict) -> str:
    """C6's environment clauses, or a sentence saying which one failed.

    §6 C6 registers that the slot retains *and admission requires* the
    resolved isolated HOME and CODEX_HOME, the exact PATH and TMPDIR the child
    was given, and closed stdin. An earlier draft required only four booleans,
    a non-empty home and the inventory, so a slot could drop every environment
    member and stay admissible while C6 claimed otherwise. These are checks on
    the wrapper's own record — §7 says plainly that CALL.json is self-reported
    — but a record that contradicts the registered invocation is not evidence
    of it, and that much is checkable.
    """
    home, codex_home, cwd = call.get("home"), call.get("codexHome"), call.get("cwd")
    if call.get("isolation") != "isolated":
        return "CALL.json records isolation %r, not the registered isolated run" % (
            call.get("isolation"),)
    # C6 registers the RESOLVED isolated home and working directory. A relative
    # or unnormalized one is not resolved, and — worse for the clauses below —
    # `../home` and `home` are two names the nesting test would not relate.
    if not _resolved(home):
        return ("CALL.json records the isolated home %r, which is not a resolved "
                "absolute path" % (home,))
    if not isinstance(codex_home, str) or codex_home != os.path.join(home, ".codex"):
        return ("CALL.json records CODEX_HOME %r, which is not the .codex directory "
                "of its own isolated home %r" % (codex_home, home))
    if not _resolved(cwd):
        return ("CALL.json records the working directory %r, which is not a resolved "
                "absolute path" % (cwd,))
    if _same(cwd, home) or _under(cwd, home) or _under(home, cwd):
        return ("the isolated home %r and the working directory %r are the same "
                "directory or nested: the registered invocation puts the model's "
                "workspace outside the home it was given" % (home, cwd))
    if call.get("environment") != ENVIRONMENT_NAMES:
        return ("CALL.json records the environment %r, not the registered %r"
                % (call.get("environment"), ENVIRONMENT_NAMES))
    values = call.get("environmentValues")
    if not isinstance(values, dict) or sorted(values) != sorted(ENVIRONMENT_NAMES) \
            or not all(isinstance(value, str) and value for value in values.values()):
        return ("CALL.json records environmentValues %r, not one string per registered "
                "variable" % (values,))
    if values["HOME"] != home or values["CODEX_HOME"] != codex_home:
        return ("the recorded HOME/CODEX_HOME values %r do not agree with the isolated "
                "home this run reports" % ({"HOME": values["HOME"],
                                            "CODEX_HOME": values["CODEX_HOME"]},))
    entries = values["PATH"].split(":")
    if tuple(entries[:len(SYSTEM_PATH)]) != SYSTEM_PATH or len(entries) != len(SYSTEM_PATH) + 1:
        return ("the child PATH %r is not the six registered system directories plus "
                "one per-run binary directory" % (values["PATH"],))
    if not entries[-1].startswith("/") or _under(entries[-1], home):
        return ("the per-run binary directory %r is not an absolute path outside the "
                "isolated home: Study 010's PATH ended in the operator's real home, "
                "which is the defect this clause exists to catch" % (entries[-1],))
    if values["TMPDIR"] == "/tmp" or not _under(values["TMPDIR"], cwd):
        return ("TMPDIR %r is not inside this run's own scratch: the pinned CLI's "
                "sandbox is writable at [workdir, /tmp, $TMPDIR], so a shared TMPDIR "
                "puts every other run's tree in this run's writable set"
                % (values["TMPDIR"],))
    if call.get("stdin") != CLOSED_STDIN:
        return "CALL.json records stdin %r, not %r" % (call.get("stdin"), CLOSED_STDIN)
    if call.get("credentialRemoved") is not bool(call.get("credentialCopied")):
        return ("the run copied a credential %r and records credentialRemoved %r: a "
                "copy that was made and not removed is a live credential left on disk, "
                "and a removal recorded without a copy is a record of nothing"
                % (call.get("credentialCopied"), call.get("credentialRemoved")))
    return None


def admit(slot: str, prompt_path: str, golden_path: str, pins: dict,
          registry_sha256: str = None) -> tuple:
    """(code, detail, authoring-empty): code is None when the run is valid.

    The checks run in the documented order and the FIRST failure names the
    run. Nothing here consults the batch's own refusal record; reconciling
    with it is score_run()'s job, so that a batch refusal can never make an
    inadmissible run look examined or an admissible one look refused.

    `registry_sha256` defaults to the digest of the committed
    `harness/PINS.json` — the strict value, and the only one `main()` can
    produce, because the registered interface (`score_registered()`) has no
    parameter for it. The override exists so the wrapper-driven tests, whose
    slots are made under a stand-in registry naming a stand-in binary, can say
    which registry their slots' stamps are supposed to name; a scoring that
    uses it can never be published: there is no public writer at all, and the
    private one refuses results carrying an override (§7).
    """
    if registry_sha256 is None:
        registry_sha256 = file_digest(REGISTRY_OF_RECORD)
    # §3.3, first: regular files and directories only, anywhere in the tree,
    # decided by lstat before anything is opened. This precedes every other
    # check for two reasons — a symlink decides what a later check reads (a
    # dangling REFUSAL.json link answers `exists()` with False and made the
    # batch's own refusal record disappear), and a FIFO decides whether a later
    # check RETURNS at all (open() on one blocks forever).
    links, irregular = slot_irregularities(slot)
    if links:
        return ("slot-symlink",
                "the slot tree holds %d symlink(s) (%s): a slot may hold regular "
                "files and directories only, and a link — dangling or not — is a "
                "retained byte the slot does not contain"
                % (len(links), ", ".join(links)), False)
    if irregular:
        return ("slot-irregular",
                "the slot tree holds %d entry/entries that are neither regular files "
                "nor directories (%s): a slot may hold regular files and directories "
                "only. These are not retained evidence at all, and one of them — a "
                "FIFO — would block the scorer in open() rather than refuse a slot"
                % (len(irregular), ", ".join(irregular)), False)
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
    # §2.6: the cell is defined by the committed registry, and a run made under
    # another one is not a run in this cell. Without this a `--pins` registry
    # naming a different model, binary or N would define its own study and
    # publish under this one's name.
    if call.get("pinsSha256") != registry_sha256:
        return ("registry-mismatch",
                "the run was made under registry %r and this study's registry of "
                "record is %s: a slot made under another registry is not a slot in "
                "this cell" % (call.get("pinsSha256"), registry_sha256), False)
    # §3.2: the golden capture the batch verified at preflight, stamped per
    # slot. The scorer's own precondition binds the golden FILE to the pin;
    # this binds each RUN to that file, so a capture derived after the batch
    # and re-pinned cannot change which runs were admissible.
    golden_digest = file_digest(golden_path)
    if call.get("goldenSha256") != golden_digest:
        return ("golden-mismatch",
                "the run was made against golden capture %r and this scoring uses %s: "
                "a golden capture is registered before the first slot and a run cannot "
                "be re-admitted against a later one"
                % (call.get("goldenSha256"), golden_digest), False)
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
    environment_failure = check_environment(call)
    if environment_failure is not None:
        return "isolation-unproven", environment_failure, False
    # An integer 1, and not `True`: Python calls those equal, so a slot
    # recording `newSessionCount: true` — a record of nothing counted — passed
    # this clause while §6 C6 registers exactly one new session file.
    sessions = call.get("newSessionCount")
    if not isinstance(sessions, int) or isinstance(sessions, bool) or sessions != 1:
        return ("session-count",
                "the call records %r new sessions, not the integer 1" % (sessions,), False)
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

def batch_refusal_code(slot: str):
    """The code the batch recorded for this slot, or None when it recorded no
    refusal at all.

    Every read of REFUSAL.json goes through this, and through the
    duplicate-key-rejecting loader: a shadowed `code` member cannot mean one
    thing here and another to a reader. A file that exists and is not a JSON
    object, or carries no code, or carries a code that is not a string, is
    MALFORMED refusal evidence and raises — score_run() turns that into the
    slot's own pipeline-invalid verdict. The batch writes a code on every
    refusal it records, so an honest slot never reaches these raises; a slot
    whose refusal record says nothing is a slot whose provenance is
    unexplained, and §3.3 does not let an unexplained slot into a denominator.
    """
    path = os.path.join(slot, "REFUSAL.json")
    if not os.path.exists(path):
        return None
    record = load_json(path)
    if not isinstance(record, dict):
        raise ValueError("REFUSAL.json is not a JSON object")
    code = record.get("code")
    if not isinstance(code, str) or not code:
        raise ValueError("REFUSAL.json records code %r, not a refusal code" % (code,))
    return code


def score_run(slot: str, prompt_path: str, golden_path: str, pins: dict,
              classes: list, registry_sha256: str = None) -> dict:
    """One slot's row: valid or not, and — when valid — its coverage."""
    name = os.path.basename(slot)
    batch_code = None
    try:
        code, detail, empty = admit(slot, prompt_path, golden_path, pins,
                                    registry_sha256)
        # §7 totality: the refusal record is read INSIDE the total path. It was
        # read outside it in an earlier draft, so a REFUSAL.json that was a
        # directory, a list, or `null` reached the caller as a bare traceback
        # and stopped the scoring of every other slot — and an empty one
        # silently let a refused run into V. It is read only from a slot whose
        # tree is regular files and directories: a symlinked REFUSAL.json is
        # not this slot's refusal evidence, and the link already refused the
        # slot with its own code, which is the more exact verdict of the two.
        # The same holds, and matters more, for `slot-irregular`: a FIFO named
        # REFUSAL.json is not this slot's refusal evidence either, and reading
        # it would block the whole scoring instead of refusing one slot.
        if code not in ("slot-symlink", "slot-irregular"):
            batch_code = batch_refusal_code(slot)
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
    population with a hole in it.

    An entry named run-NNN is collected as a slot WHATEVER ITS TYPE — a
    directory, a symlink, a FIFO, a regular file. Skipping the ones that are
    not directories punched a hole in the indices and refused the whole
    scoring, where §3.3 wants the entry named: `admit()` scores it
    `slot-symlink`, `slot-irregular` or `slot-shape` on its first checks, so it
    enters no denominator and the other slots are still counted. The name is
    what claims the index, so the name is what has to answer for it."""
    if not os.path.isdir(slots_dir):
        raise ScoreError("%s is not a directory" % slots_dir)
    slots, unexpected, indexes = [], [], []
    for name in sorted(os.listdir(slots_dir)):
        path = os.path.join(slots_dir, name)
        parts = name.split("-", 1)
        if len(parts) == 2 and parts[0] == "run" and parts[1].isdigit():
            slots.append(path)
            indexes.append(int(parts[1]))
        elif name not in ("BATCH.json", "SHORTFALL.json"):
            unexpected.append(name)
    if indexes != list(range(1, len(indexes) + 1)):
        raise ScoreError("the slot indices are not the contiguous range 1..%d: %r"
                         % (len(indexes), indexes))
    return slots, unexpected


def _range_block(valid: list, member: str) -> dict:
    """S4's per-run range for one count: min, max and mean over the valid runs,
    all None when there are none. Integers in, one mean out — no interval, and
    no rate: these are volumes, not proportions."""
    values = [row[member] for row in valid]
    return {"min": min(values) if values else None,
            "max": max(values) if values else None,
            "mean": sum(values) / len(values) if values else None}


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
    §2.6). A drifted port, an unregistered interpreter, an unregistered golden
    capture, or an unregistered or post-freeze-edited preregistration refuses
    the whole scoring — none of them can be discovered afterwards from a
    published rate."""
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
    # §2.6: the freeze digest is not optional at scoring time. An earlier draft
    # skipped this check while the pin was null, which meant the registry could
    # be merged with its null intact and no rate would ever notice — the very
    # shape of unenforced claim §7's discipline exists to refuse.
    prereg_pin = pins.get("preregistration", {}).get("sha256")
    if not prereg_pin:
        raise ScoreError(
            "harness/PINS.json registers no preregistration.sha256: this file's "
            "digest at the freeze must replace the null before any rate is computed, "
            "or a post-freeze edit would be undetectable (§2.6)")
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
          golden_path: str, registry_sha256: str = None) -> dict:
    """The counting, with the registry of record either computed or supplied.

    `registry_sha256` is the LIBRARY override (§2.6, §7): it exists so the
    wrapper-driven harness tests, whose slots are stamped with a stand-in
    registry naming a stand-in binary, can say which registry their own slots
    are supposed to name. Whether it was used is recorded in the results —
    `cell.registryOverride` — and this function has no way to publish anything:
    the writer is module-private and is called by `score_registered()` alone, on
    results it computed itself. So an override can produce a dict in memory and
    never a published rate table. The registered command calls
    `score_registered()`, which has no such parameter — and no path parameter
    either.
    """
    override = registry_sha256
    if registry_sha256 is None:
        registry_sha256 = file_digest(REGISTRY_OF_RECORD)
    preconditions = verify_preconditions(pins_path, prompt_path, golden_path)
    pins = load_json(pins_path)
    prompt_digest = preconditions["promptSha256"]
    classes = load_family(family_path, pins["family"]["sha256"])
    slots, unexpected = collect_slots(slots_dir)

    # §2.4: no rate before the batch is terminal.
    registered = pins.get("batch", {}).get("runs")
    shortfall = terminality(slots, slots_dir, registered)

    rows = [score_run(slot, prompt_path, golden_path, pins, classes, registry_sha256)
            for slot in slots]
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
            "registryOfRecordSha256": registry_sha256,
            REGISTRY_OVERRIDE: override,
            "portedFiles": preconditions["portedFiles"],
            "study010LockSha256": preconditions["study010LockSha256"],
            "note": "One cell: this prompt, this model, this policy. Nothing here "
                    "is a claim about other prompts, other models, or real "
                    "operational records. The digests above were verified before "
                    "any slot was read, not copied from the registry, and every "
                    "counted run names the registry and the golden capture it was "
                    "made under (§2.6, §3.2).",
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
            # §4.4 S5 registers this denominator rather than leaving it to be
            # discovered: a run with no policy-concordant record at all has no
            # label accuracy, and averaging it in as 0 would be inventing one.
            "perRunTrials": len(accuracies),
            "perRunExcluded": n - len(accuracies),
            "note": "Pooled over the valid runs' accepted records. No interval: "
                    "records within one completion are not independent trials, "
                    "and a binomial interval here would overstate its precision. "
                    "The per-run mean and range are over the perRunTrials valid "
                    "runs with at least one accepted record (|H|+|Q| > 0); the "
                    "perRunExcluded runs have no accuracy to average and are "
                    "counted rather than scored 0.",
        },
        # S4 names four per-run quantities and their ranges over the batch:
        # |A|, |H|, |Q| and the dropped count. All four are published as ranges
        # here as well as per run in `runs` — an earlier draft registered the
        # ranges and emitted only the accepted one, which is a claim the file
        # did not support.
        "records": {
            "acceptedTotal": accepted_total,
            "droppedTotal": dropped_total,
            "dropCodes": dict(sorted(drop_codes.items())),
            "acceptedPerRun": _range_block(valid, "accepted"),
            "hPerRun": _range_block(valid, "h"),
            "qPerRun": _range_block(valid, "q"),
            "droppedPerRun": _range_block(valid, "dropped"),
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


def score_registered(slots_dir: str, records_dir: str = None) -> dict:
    """THE REGISTERED SCORING INTERFACE (§7): the only thing that publishes.

    Every input except the slot directory is DERIVED from this module's own
    location — the registry, the family, the prompt, the golden capture, and
    the study root the tables are written to. There is no parameter, flag,
    default or environment variable through which any of them could be
    supplied, so an alternate registry cannot redefine N, the class
    definitions, the model a run had to be made by, or where a rate table
    lands. The round-2 finding closed `--pins` for the registry *stamp*; the
    round-3 finding was that a same-digest-discipline registry supplied on the
    command line still defined the population arithmetic. It cannot be
    supplied now.

    It computes and publishes in ONE call: the results it hands to
    `_write_outputs()` are the results it just computed, so no dict crosses a
    public boundary on its way to RESULTS.json. The emission directory is
    validated BEFORE anything is scored or written, so a target that would
    write into the slot tree refuses the whole command rather than refusing
    after the rates are on disk.
    """
    if records_dir is not None:
        _check_records_target(slots_dir, records_dir)
    results = score(slots_dir, REGISTRY_OF_RECORD, REGISTERED_FAMILY,
                    REGISTERED_PROMPT, REGISTERED_GOLDEN)
    _write_outputs(results)
    if records_dir is not None:
        _emit_records(results["runs"], slots_dir, records_dir)
    return results


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


def _range_cell(block: dict) -> str:
    """One S4 per-run range: integers at the ends, a mean in the middle."""
    if block["min"] is None:
        return "— / — / —"
    return "%d / %s / %d" % (block["min"], _number(block["mean"], 3), block["max"])


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
        "| accepted per run (min/mean/max) | %s |" % _range_cell(records["acceptedPerRun"]),
        "| H per run (min/mean/max) | %s |" % _range_cell(records["hPerRun"]),
        "| Q per run (min/mean/max) | %s |" % _range_cell(records["qPerRun"]),
        "| dropped per run (min/mean/max) | %s |" % _range_cell(records["droppedPerRun"]),
        "| H / Q | %d / %d |" % (accuracy["h"], accuracy["q"]),
        "| label accuracy \\|H\\|/(\\|H\\|+\\|Q\\|) | %s |" % _number(accuracy["rate"]),
        "| per-run label accuracy (min/mean/max) | %s / %s / %s, over %d of %d "
        "valid runs |" % (
            _number(accuracy["perRunMin"]), _number(accuracy["perRunMean"]),
            _number(accuracy["perRunMax"]), accuracy["perRunTrials"],
            accuracy["perRunTrials"] + accuracy["perRunExcluded"]),
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


def _check_records_target(slots_dir: str, records_dir: str) -> None:
    """`--emit-records DIR` may not write anywhere inside the slot tree (§8).

    The round-3 finding: `--emit-records <slots>/run-002` emitted a phantom
    slot into the population that had just been scored, so the retained tree no
    longer reproduced the output published from it — and the next scoring
    refused, because a full batch and a shortfall declaration now coexisted.
    Emission is a DERIVED artifact of a scored population; it may not be a
    member of one. The two directories must therefore be disjoint in both
    directions: not equal, not one inside the other.

    Checked on normalized absolute paths before the target exists, so the
    refusal happens before anything is scored and before anything is written.
    Nothing is resolved through symlinks here — the target usually does not
    exist yet — which is why the slot tree's own rule (regular files and
    directories only, no links anywhere) is what keeps a link from making two
    disjoint names for one directory.
    """
    slots = os.path.normpath(os.path.abspath(slots_dir))
    target = os.path.normpath(os.path.abspath(records_dir))
    if target == slots or target.startswith(slots + os.sep) \
            or slots.startswith(target + os.sep):
        raise ScoreError(
            "--emit-records %s is inside the slot tree %s (or contains it): the "
            "compiled record trees are DERIVED from a scored population and may "
            "not be written into one. Emitting a run-NNN directory there adds a "
            "slot to the batch that was just scored, so the retained tree no "
            "longer reproduces the published rates (§8). Name a directory outside "
            "the slot tree." % (records_dir, slots_dir))


def _emit_records(rows: list, slots_dir: str, out_dir: str) -> None:
    """Write each valid run's compiled record tree, so a reader can diff the
    records themselves. Deterministic and derived — nothing here enters a rate.

    It READS only each slot's `completion.txt` and WRITES only under `out_dir`,
    which `_check_records_target()` has already required to be outside the slot
    tree. That is what makes it safe to run after `RESULTS.json` exists: it
    emits from the population that was just scored and cannot alter it. Runs
    with no parseable array have no compiled tree and are skipped, which §8
    states rather than implies.
    """
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


def _write_outputs(results: dict) -> None:
    """RESULTS.json and RATES.md, into the study root and nowhere else.

    MODULE-PRIVATE, and called by `score_registered()` alone, on the results it
    computed in the same call. There is no public writer: the round-3 finding
    was that a public one trusted a mutable member of an ordinary dict, so
    editing `cell.registryOverride` to None published an alternate-registry
    scoring anywhere the caller named. The output directory is not a parameter
    either — a rate table written elsewhere would let the operator read six
    rates while the driver still accepted new slots (§2.4).

    What it still checks, because "called by one caller" is a property of this
    file and the checks are properties of the study tree: every digest the
    results claim is re-derived here from the committed tree and must agree,
    including the registered N. So even a hand-built dict must describe a
    scoring of THIS cell under THIS registry to be written.

    What no check inside a file can refuse is a caller who edits this file or
    rebinds its module constants in process. §7 states that ceiling once.
    """
    cell = results.get("cell") if isinstance(results, dict) else None
    population = results.get("population") if isinstance(results, dict) else None
    if not isinstance(cell, dict) or REGISTRY_OVERRIDE not in cell \
            or not isinstance(population, dict):
        raise ScoreError(
            "these results did not come from score(): they carry no cell.%s, so "
            "there is no saying which registry of record they were counted under, "
            "and an unattributable rate table is not published (§7)"
            % REGISTRY_OVERRIDE)
    if cell[REGISTRY_OVERRIDE] is not None:
        raise ScoreError(
            "this scoring was given the registry digest %s as an override; "
            "RESULTS.json and RATES.md are written only for a scoring that "
            "computed the committed harness/PINS.json's digest itself (§2.6, §7)"
            % cell[REGISTRY_OVERRIDE])
    pins = load_json(REGISTRY_OF_RECORD)
    expected = {
        "registryOfRecordSha256": file_digest(REGISTRY_OF_RECORD),
        "promptSha256": file_digest(REGISTERED_PROMPT),
        "familySha256": pins["family"]["sha256"],
        "goldenSha256": pins.get("golden", {}).get("sha256"),
        "preregistrationSha256": pins.get("preregistration", {}).get("sha256"),
        "model": pins["codex"]["model"],
        "cli": pins["codex"]["version"],
        "binarySha256": pins["codex"]["binarySha256"],
    }
    for member, value in sorted(expected.items()):
        if cell.get(member) != value:
            raise ScoreError(
                "these results record cell.%s = %r and the committed harness/PINS.json "
                "and study tree give %r: a rate table is published only for a scoring "
                "of this cell under the committed registry (§2.6, §7)"
                % (member, cell.get(member), value))
    registered = pins.get("batch", {}).get("runs")
    if population.get("registeredRuns") != registered:
        raise ScoreError(
            "these results were counted against a registered batch size of %r and the "
            "committed harness/PINS.json registers %r: N is the committed registry's "
            "to state, and a scoring over another one is not this study's (§2.4, §7)"
            % (population.get("registeredRuns"), registered))
    os.makedirs(STUDY, exist_ok=True)
    with open(os.path.join(STUDY, "RESULTS.json"), "wb") as handle:
        handle.write((json.dumps(results, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    with open(os.path.join(STUDY, "RATES.md"), "wb") as handle:
        handle.write(render_markdown(results).encode("utf-8"))


# The registered command's whole argument surface. `--slots` names the slot
# tree; `--emit-records` names a derived-output directory outside it. Nothing
# else is accepted, and an unknown argument REFUSES rather than being ignored:
# a flag that is silently dropped is how a stale command line lies about what
# it ran (§7).
SCORE_FLAGS = ("--slots", "--emit-records")
WITHDRAWN_FLAGS = {
    "--out": "--out was removed: RESULTS.json and RATES.md go to the study root, and "
             "nowhere else. A rate table written elsewhere would let the operator see "
             "six rates while the driver still accepted new slots (§2.4).",
    "--pins": "--pins was removed from the scorer: the registry of record is the "
              "COMMITTED harness/PINS.json and the registered command derives it from "
              "its own location. A supplied registry — even one whose cell values match "
              "— would define N and the class definitions of the population it "
              "published (§2.6, §7). batch.py still takes --pins, for the stand-in "
              "binary the harness tests drive.",
    "--family": "--family was removed: the six coverage classes are FAMILY.json at the "
                "committed pin, derived from the harness's own location (§2.6, §7).",
    "--prompt": "--prompt was removed: the registered prompt is derived from the "
                "harness's own location and checked against the committed pin (§2.6).",
    "--golden": "--golden was removed: the golden capture is derived from the harness's "
                "own location and checked against the committed pin (§3.2).",
    "--registry-sha256": "there is no flag for the registry digest and never was: the "
                         "registered interface computes the committed harness/PINS.json's "
                         "digest itself (§2.6, §7).",
}
USAGE = "usage: score_rates.py score --slots DIR [--emit-records DIR]"


def _parse_score(argv: list) -> dict:
    """{flag: value} for the `score` command, or ScoreError. Strict: every
    token must be a registered flag with a value, no flag twice."""
    options: dict = {}
    index = 0
    while index < len(argv):
        token = argv[index]
        if token in WITHDRAWN_FLAGS:
            raise ScoreError(WITHDRAWN_FLAGS[token])
        if token not in SCORE_FLAGS:
            raise ScoreError(
                "unknown argument %r. The registered scoring command takes %s and "
                "nothing else, and an argument it does not know is a refusal rather "
                "than a no-op: a silently ignored flag is how a stale command line "
                "lies about what it ran (§7). %s"
                % (token, " and ".join(SCORE_FLAGS), USAGE))
        if index + 1 >= len(argv):
            raise ScoreError("%s needs a value" % token)
        if token in options:
            raise ScoreError("%s was given twice" % token)
        options[token] = argv[index + 1]
        index += 2
    return options


def main(argv: list) -> int:
    if len(argv) < 2 or argv[1] != "score":
        print(USAGE, file=sys.stderr)
        return 2
    try:
        options = _parse_score(argv[2:])
        slots_dir = options.get("--slots")
        if slots_dir is None:
            raise ScoreError("--slots is required. " + USAGE)
        # §7: the registered interface. It scores and publishes in one call and
        # derives every other input from its own location, so no argv, no
        # default and no environment can reach the registry, the family, the
        # prompt, the golden capture, or where the tables land.
        results = score_registered(slots_dir, options.get("--emit-records"))
    except ScoreError as error:
        print("refused: %s" % error, file=sys.stderr)
        return 1
    print("scored: %d valid of %d slots" % (
        results["population"]["valid"], results["population"]["slots"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
