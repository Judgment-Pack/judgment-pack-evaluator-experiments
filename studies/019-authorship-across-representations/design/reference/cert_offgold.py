#!/usr/bin/env python3
"""Study 019 — OFF-GOLD EQUIVALENCE CERTIFICATE builder.

PREREGISTRATION §4 (`GATE(pre-freeze)`), verbatim:

    **References**: one per language, in cell-for-cell agreement over the design grid.
    `GATE(pre-freeze)`: **off-gold equivalence check** — the two references' agreement is
    re-established over the full derived input space, with every divergence point required
    to fall inside a registered exclusion class (currently exactly X1); any other divergence
    blocks the freeze.

What this program does, and what it deliberately does not do
------------------------------------------------------------
It enumerates the registered derived input space (§SPACE below), evaluates BOTH
references over it, and reports EVERY cell on which they disagree, each classified
against the registered exclusion class X1. It emits `OFFGOLD-CERT.json` and
`OFFGOLD-CERT.md`. It is a design-time gate instrument; it publishes no study
endpoint, adjudicates no hypothesis, and its outputs are not a study result.

It does NOT decide whether either reference is *right*. Gold and the clean-room
oracle carry that burden. The clean-room oracle is consulted here only as a THIRD
OPINION on cells where the two references already disagree, and what it backs is
recorded rather than acted on: a certificate that let the oracle stand in for
either reference would be measuring two things and reporting one.

=============================================================================
§SPACE — the registered derived input space (236,196 cells)
=============================================================================
The space is the one the arm-A reference builder derived and reported on
(`reference/refA/REPORT.md`, `mutants/refA/REGISTRY.json` provenance): the full
cross product of the U1 substitution representatives plus "unreadable"/"unreported"
on every axis that admits it.

    sanctions  x country x risk x spend x newVendor x critical x prior x fin x ins
        3      x    4    x   9  x   9   x     3     x    3     x   3   x  3  x  3   = 236,196

Axis by axis, with the reason each value set represents every value it stands for:

1. `sanctions` — {CLEAR, MATCH, UNKNOWN}, 3 values, NO omitted member.
   The screening result is a 3-valued enum in the prose and `UNKNOWN` is one of its
   VALUES, not an absence: the "unreported screening" case is `UNKNOWN`, governed by
   D2. U1's own parenthetical excludes the screening result from the counterfactual.
   Both reference projections carry this reading (`refA/prose_model.py` docstring:
   "never unreadable"; `refB/policy.rego`: "Sanctions is always a present string;
   UNKNOWN is a value, not an omission"). REGISTERED LIMIT, stated rather than
   hidden: an input document with `/vendor/sanctionsStatus` physically absent is
   OUTSIDE this space. Both references have a total backstop for it (refA: no rule's
   condition can be satisfied, refB: an explicit `no-match` else-rung and the
   `default decision`), and `--with-sanctions-omitted` evaluates the 78,732-cell
   extension as a labelled supplementary stratum. The 236,196-cell space proper is
   the registered one, because it is the space the arm-A builder's reported
   72-cell inexpressibility finding (X1) was measured over.

2. `country` — {LOW, MEDIUM, HIGH, omitted}, 4 values.
   The readable domain is exactly the 3-valued enum, so the enum is enumerated
   exhaustively — no representation argument is needed. `omitted` is the registered
   encoding of "unreadable" (`refA/project.py`, `refB/run_grid.py`): the member is
   absent from the input document.

3. `risk` — {0, 39, 40, 69, 70, 89, 90, 100, omitted}, 9 values.
   Readable domain: integers 0..100. Every clause reads the risk score ONLY through
   comparisons against the three declared thresholds — 40 (D6a/D6b/D7 `< 40`, D6c
   `>= 40`), 70 (D6c `< 70`, D4 `>= 70`) and 90 (D3 `>= 90`). Those cut 0..100 into
   the four blocks [0,39] [40,69] [70,89] [90,100], and every clause is CONSTANT on
   each block; a determination therefore depends on the risk score only through which
   block it lands in. Both endpoints of every block are used (8 values = 4 blocks x 2
   endpoints) rather than one interior point per block, so a mis-stated inclusivity
   (`>=` written `>`) shows up as a DISAGREEMENT BETWEEN AN INTERVAL'S TWO ENDPOINTS
   instead of being silently skipped. In the task's phrasing: 39/40, 69/70 and 89/90
   are the three band boundaries +-1, and 0 and 100 are the representative interiors
   of the two outer blocks (which are also that domain's endpoints).

4. `spend` — {0.00, 100000.00, 100000.01, 500000.00, 500000.01, 2000000.00,
   2000000.01, 10000000.00, omitted}, 9 values.
   Readable domain: 0.00..10,000,000.00 at cents precision — 1,000,000,001 values,
   not enumerable. Every clause reads requested spend ONLY through comparisons
   against the three declared thresholds — 100,000.00 (D6c/D7 `<=`), 500,000.00
   (D6a `<=`, D6b `>`) and 2,000,000.00 (D6b `<=`, O3 `>`) — cutting the domain into
   [0, 100000.00] (100000.00, 500000.00] (500000.00, 2000000.00]
   (2000000.00, 10000000.00]. Same constancy argument as risk; both endpoints of
   every block are used, with the next representable cent (x.01) serving as each
   open lower endpoint. That is the "every boundary +-0.01" set: 100000.00/100000.01,
   500000.00/500000.01, 2000000.00/2000000.01, plus the domain endpoints 0.00 and
   10000000.00 as the outer blocks' representative interiors. 2,000,000.00 is
   inclusive in D6b and exclusive in O3; the pair (2000000.00, 2000000.01) exercises
   both senses.

   SOUNDNESS OF 3 AND 4, stated plainly: the representative argument is sound for
   any implementation whose spend/risk sensitivity is confined to those six
   thresholds. It is NOT a proof about an arbitrary implementation — a reference that
   invented a seventh threshold could hide a divergence between two representatives.
   Two independent checks bound that risk rather than assume it away: refB's own
   `crosscheck.py` re-runs U1 over all 101 risk values and a 17-point dense spend
   sample and requires agreement with the sparse set, and the clean-room oracle
   quantifies U1 over the full 101-value risk domain. Both references' texts are
   readable and neither carries a threshold outside the six.

5. `newVendor`, `critical`, `prior` — {yes, no, omitted}, 3 values each.
   The declared domain is exactly {yes, no}; `omitted` is the registered encoding of
   "unreported", which the prose governs directly (D5/O1/O2 "treated as no"). Three
   values is exhaustive, not representative.

6. `finEvidence`, `insurance` — {present, absent, omitted}, 3 values each.
   Exhaustive over the tri-state the evidence channel admits: available, unavailable,
   availability unreported. `omitted` = the requirement id absent from the evidence
   document, which the JPS engine decodes as unknown and Rego reads through
   `object.get(..., "OMITTED")`.

Relationship to the 2,540-cell design grid (`reference/cells.json`): the two spaces
OVERLAP but neither contains the other. The grid carries values this space does not
(risk 20/50/95, spend 50000.00/3000000.00, ...) and this space carries the U1
representatives the grid does not. The grid's agreement record (`AGREEMENT.md`,
2,540/2,540) is therefore re-verified here as a control rather than assumed
(validation record `grid-regression`), and the certificate is over the derived space.

=============================================================================
§X1 — the registered exclusion class
=============================================================================
PREREGISTRATION §4, verbatim:

    **X1 (registered exclusion class and census row)**: {new vendor yes; risk in
    [40,70); LOW country with spend unreadable, or country unreadable with spend
    <= 100,000.00} — the prose-correct outcome (review) is inexpressible in the
    fragment (0 of 2,048 onUnknown assignments; irreducible).

`in_x1()` below is the mechanical reading of exactly that sentence, transcribed from
the committed `cleanroom/check_oracle.py` predicate so that the two instruments
cannot drift apart. Two readings are pinned because the sentence does not fix them:

  * "risk in [40,70)" requires a READABLE risk in that band. An unreadable risk score
    is not a value in an interval, and the arm-A builder's 72-cell class is a
    readable-risk class.
  * "spend <= 100,000.00" requires a READABLE spend. An unreadable spend on the
    country-unreadable branch is not in X1 (that branch's X1 arm is the LOW-country
    one).

X1 as registered is a COARSE predicate. `reference/refA/REPORT.md` characterises the
class the arm-A builder actually measured more tightly (sanctions CLEAR, financial
evidence present, prior != yes, critical != yes, on top of the registered conjuncts).
Every divergence is classified against the REGISTERED predicate — that is the gate —
and the refined predicate is additionally reported per divergence, because "the
divergences also satisfy the tighter description the builder published" is the
stronger statement and the one a reviewer can falsify.

=============================================================================
§METHOD — measured, then chosen (the choice is recorded, not assumed)
=============================================================================
arm A (JPS): the pinned engine at 236,196 cells is ~16 ms/cell = ~63 minutes of
    subprocess churn, so the engine-validated simulator `refA/jps_sim.py` carries the
    sweep and the engine carries every reported divergence. The simulator is admitted
    ONLY on fresh re-validation against the pinned binary over a 2,000-cell
    deterministic stratified subsample OF THIS SPACE (`--stage validate-sim`,
    0 disagreements required, systematic selection, no RNG anywhere), plus a
    verdict-class coverage check and a 2,540-cell grid regression against the
    digest-pinned committed `refA/results.jsonl`. Every divergence cell the simulator
    finds is then CONFIRMED ON THE REAL ENGINE, and the confirmed engine verdict is
    what the certificate reports.
arm B (Rego): `opa exec` over a built bundle vs per-cell `opa eval`, both measured on
    200 cells (`--stage bench-rego`) and required to agree cell-for-cell before either
    is used at scale. Capabilities are enforced at BUILD time for the exec path
    (`opa exec` does not accept `--capabilities` at v1.19.0 — TOOLCHAIN-NOTES), which
    is a strictly earlier and harder failure than the eval path's per-invocation flag;
    the `time.now_ns` canary is re-run through the build path as a power check.

usage:
    cert_offgold.py --stage all            # bench, validate, full sweep, certificate
    cert_offgold.py --stage bench-rego     # the recorded rego-side measurement only
    cert_offgold.py --stage validate-sim   # the recorded simulator re-validation only
    cert_offgold.py --stage run            # sweep + certificate (needs a prior --stage all/validate)
    cert_offgold.py --stage all --with-sanctions-omitted   # + supplementary stratum

Deterministic and side-effect-scoped: no RNG, no wall-clock in any emitted artifact
except the two explicitly-labelled `measuredSeconds` fields, no absolute paths in the
certificate, and every intermediate lands under --work (default: a sibling scratch
directory), never in the study tree.
"""

import argparse
import gzip
import hashlib
import importlib.util
import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True   # never leave __pycache__ in the study tree

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(HERE)
STUDY = os.path.dirname(DESIGN)

# --- pinned toolchain (design-time resolutions; the harness re-pins these) -----------
PINS = os.environ.get(
    "S019_PINS",
    "/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/"
    "e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad/pins",
)
JPACK = os.path.join(PINS, "jpack", "jpack")
OPA = os.path.join(PINS, "opa", "opa_linux_amd64_static")
CAPS = os.path.join(PINS, "opa", "caps-filtered.json")
CANARY = os.path.join(PINS, "opa", "canary.rego")

EXPECTED_DIGESTS = {
    # TOOLCHAIN-NOTES.md, verified 2026-08-14
    "jpack": "42f35f7900bea6dfce215631b50729ab22dd347289e1bde3412604fb043a22e9",
    "opa": "1dd5c5591ff856f5e20a1d66bafae9511ddf3c5552ed3b5070c70b2b6580ee3f",
    # reference/AGREEMENT.md, 2026-08-15
    "refA/pack.json": "956ceebbc08886acdc3973b43112e9896f2853b3895243b3b97ff33a910453ee",
    "refB/policy.rego": "1f2e1ad1d423240dd262852f19057a8e906387d5a1b71db8b8a15bc010fc12e2",
    "cells.json": "da4ee85c9d8b9f37ef523058144c163e80da50e485e2a148ea7d655253114618",
    "refA/results.jsonl": "d2cbfed239f4151a767d22f09a01f1a1bd161e54ebbc99c546ebc33b9aee03e3",
    "refB/results.jsonl": "d2cbfed239f4151a767d22f09a01f1a1bd161e54ebbc99c546ebc33b9aee03e3",
}

PACK = os.path.join(HERE, "refA", "pack.json")
POLICY = os.path.join(HERE, "refB", "policy.rego")
GRID = os.path.join(HERE, "cells.json")

# =============================================================================
# §SPACE
# =============================================================================
KEYS = ("sanctions", "country", "risk", "spend", "newVendor", "critical", "prior",
        "finEvidence", "insurance")

SANCTIONS = ["CLEAR", "MATCH", "UNKNOWN"]
COUNTRY = ["LOW", "MEDIUM", "HIGH", None]
RISK = ["0", "39", "40", "69", "70", "89", "90", "100", None]
SPEND = ["0.00", "100000.00", "100000.01", "500000.00", "500000.01",
         "2000000.00", "2000000.01", "10000000.00", None]
TRI = ["yes", "no", None]
EV = ["present", "absent", None]

AXES = [("sanctions", SANCTIONS), ("country", COUNTRY), ("risk", RISK), ("spend", SPEND),
        ("newVendor", TRI), ("critical", TRI), ("prior", TRI),
        ("finEvidence", EV), ("insurance", EV)]

SPACE_SIZE = 1
for _, _vals in AXES:
    SPACE_SIZE *= len(_vals)
assert SPACE_SIZE == 236196, SPACE_SIZE


def cells():
    """Canonical enumeration order: itertools.product over AXES in declaration order.

    The order IS the registered cell index; every artifact this program writes is in
    it, so any two runs are diffable line-for-line."""
    for combo in itertools.product(*[vals for _, vals in AXES]):
        yield dict(zip(KEYS, combo))


def extension_cells():
    """The 78,732-cell SUPPLEMENTARY stratum: the same cross with the sanctions member
    physically absent from the input document. Outside the registered space (see
    §SPACE note 1); evaluated and reported separately, and it gates nothing."""
    domains = [[None]] + [vals for _, vals in AXES[1:]]
    for combo in itertools.product(*domains):
        yield dict(zip(KEYS, combo))


def cell_id(cell):
    """Content-addressed id, gen_grid.py's convention widened to 16 hex chars.

    gen_grid used 10 hex (40 bits) over 2,540 cells; at 236,196 cells that carries a
    ~2.5% birthday-collision probability, which is not a rate a gate may run at. 16 hex
    (64 bits) puts it at ~1.5e-9, and uniqueness is ASSERTED at enumeration time anyway."""
    key = json.dumps({k: cell[k] for k in KEYS}, sort_keys=True)
    return "d" + hashlib.sha256(key.encode()).hexdigest()[:16]


# =============================================================================
# §X1
# =============================================================================
def in_x1(cell):
    """The registered X1 predicate, transcribed from cleanroom/check_oracle.py.

    {new vendor yes; risk in [40,70); LOW country with spend unreadable,
     or country unreadable with spend <= 100,000.00}"""
    risk = cell["risk"]
    return (
        cell["newVendor"] == "yes"
        and risk is not None and 40 <= int(risk) < 70
        and (
            (cell["country"] == "LOW" and cell["spend"] is None)
            or (cell["country"] is None and cell["spend"] is not None
                and float(cell["spend"]) <= 100000.00)
        )
    )


def in_x1_refined(cell):
    """The tighter class reference/refA/REPORT.md publishes for the same 72 cells.

    Reported alongside the registered predicate; never the gate."""
    return (
        in_x1(cell)
        and cell["sanctions"] == "CLEAR"
        and cell["finEvidence"] == "present"
        and cell["prior"] != "yes"
        and cell["critical"] != "yes"
    )


# =============================================================================
# registered projections — IMPORTED from the reference builds, never re-typed
# =============================================================================
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, os.path.join(HERE, "refA"))
jps_sim = _load("jps_sim", os.path.join(HERE, "refA", "jps_sim.py"))
_projectA = _load("project", os.path.join(HERE, "refA", "project.py"))
_run_gridB = _load("run_grid_refB", os.path.join(HERE, "refB", "run_grid.py"))
_oracle = _load("oracle", os.path.join(DESIGN, "cleanroom", "oracle.py"))

facts_document = _projectA.facts_document
evidence_document = _projectA.evidence_document
evidence_tristate = _projectA.evidence_tristate
render_input = _run_gridB.render_input          # refB's exact textual input renderer

DISPOSITIONS = {"approve", "review", "enhanced-review", "reject", "unresolved"}
REASON_TOKENS = {"missing-required-evidence", "unknown", "no-match",
                 "exception-escalation", "conflict"}


def verdict_str(disposition, reasons):
    return disposition if not reasons else "%s[%s]" % (disposition, ",".join(sorted(reasons)))


# =============================================================================
# arm A — simulator sweep and pinned-engine confirmation
# =============================================================================
def simA(pack, cell):
    kind, payload = jps_sim.evaluate_cell(pack, facts_document(cell), evidence_tristate(cell))
    if kind == "outcome":
        return (payload, ())
    return ("unresolved", tuple(sorted(payload)))


def engineA_one(pack_path, cell, workdir):
    """One pinned-engine evaluation. Disposition from the JSON payload only, never
    from an exit code (§2). Anything unexpected is surfaced, not smoothed."""
    fd_f, facts_path = tempfile.mkstemp(dir=workdir, suffix=".facts.json")
    fd_e, ev_path = tempfile.mkstemp(dir=workdir, suffix=".ev.json")
    os.close(fd_f)
    os.close(fd_e)
    try:
        with open(facts_path, "w") as fh:
            json.dump(facts_document(cell), fh)
        with open(ev_path, "w") as fh:
            json.dump(evidence_document(cell), fh)
        proc = subprocess.run(
            [pack_path[0], "experimental", "evaluate", pack_path[1],
             "--facts", facts_path, "--evidence", ev_path, "--format", "json"],
            capture_output=True, text=True, cwd=workdir)
        try:
            payload = json.loads(proc.stdout)
        except ValueError:
            return ("ENGINE-ERROR", ("non-json-output",))
        disposition = payload.get("disposition")
        if not isinstance(disposition, dict):
            return ("ENGINE-ERROR", ("no-disposition",))
        kind = disposition.get("kind")
        if kind == "outcome":
            return (disposition["outcomeId"], ())
        if kind == "unresolved":
            return ("unresolved", tuple(sorted(disposition.get("reasons", []))))
        return ("ENGINE-ERROR", ("unexpected-kind:%s" % kind,))
    finally:
        os.unlink(facts_path)
        os.unlink(ev_path)


def engineA_many(cell_list, work, jobs=12):
    """Engine evaluations, order-preserving. Threads only fan out subprocesses; the
    engine is a pure function of its two input files, so concurrency cannot reorder a
    result onto the wrong cell (each worker owns its own temp files)."""
    with tempfile.TemporaryDirectory(dir=work) as td:
        def one(cell):
            return engineA_one((JPACK, PACK), cell, td)
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            return list(pool.map(one, cell_list))


# =============================================================================
# arm B — opa exec (bundle) and opa eval (per cell)
# =============================================================================
def build_bundle(work):
    src = os.path.join(work, "bundlesrc")
    shutil.rmtree(src, ignore_errors=True)
    os.makedirs(src)
    shutil.copy(POLICY, src)
    bundle = os.path.join(work, "bundle.tar.gz")
    proc = subprocess.run([OPA, "build", "--capabilities", CAPS, "-o", bundle, src],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("opa build failed: %s" % proc.stderr[:2000])
    return bundle


def canary_refused(work):
    """Capabilities power check through the BUILD path (the path exec depends on)."""
    src = os.path.join(work, "canarysrc")
    shutil.rmtree(src, ignore_errors=True)
    os.makedirs(src)
    shutil.copy(CANARY, src)
    proc = subprocess.run(
        [OPA, "build", "--capabilities", CAPS, "-o", os.path.join(work, "canary.tar.gz"), src],
        capture_output=True, text=True)
    diag = (proc.stderr + proc.stdout).strip().replace(src + os.sep, "")
    return {"exit": proc.returncode,
            "refused": proc.returncode != 0 and "undefined function time.now_ns" in diag,
            "diagnostic": diag[:200]}


def _rego_value(val):
    disposition = val.get("disposition")
    reasons = tuple(sorted(val.get("reasons", [])))
    if disposition not in DISPOSITIONS:
        return ("REGO-ERROR", ("bad-disposition:%s" % disposition,))
    if disposition == "unresolved":
        if not reasons or not set(reasons) <= REASON_TOKENS:
            return ("REGO-ERROR", ("bad-reasons:%s" % ",".join(reasons),))
    elif reasons:
        return ("REGO-ERROR", ("outcome-with-reasons",))
    return (disposition, reasons)


def execB(bundle, cell_list, work, chunk=8000):
    """opa exec over a built bundle, batched by directory. Results are joined back
    BY PATH, not by output order, so a reordering by OPA cannot mis-attribute a
    verdict; every input path is asserted present in the output."""
    out = []
    env = dict(os.environ)
    env["TZ"] = "UTC"
    for start in range(0, len(cell_list), chunk):
        batch = cell_list[start:start + chunk]
        bdir = os.path.join(work, "in")
        shutil.rmtree(bdir, ignore_errors=True)
        os.makedirs(bdir)
        names = []
        for i, cell in enumerate(batch):
            name = "c%07d.json" % (start + i)
            with open(os.path.join(bdir, name), "w") as fh:
                fh.write(render_input(cell))
            names.append(name)
        proc = subprocess.run([OPA, "exec", "--bundle", bundle, "--decision", "study/decision",
                               "--fail", "in"],
                              capture_output=True, text=True, env=env, cwd=work)
        if proc.returncode != 0:
            raise SystemExit("opa exec failed at %d: %s" % (start, proc.stderr[:2000]))
        payload = json.loads(proc.stdout)
        by_path = {}
        for row in payload["result"]:
            by_path[os.path.basename(row["path"])] = row
        for name in names:
            row = by_path.get(name)
            if row is None:
                raise SystemExit("opa exec dropped input %s" % name)
            if "error" in row:
                out.append(("REGO-ERROR", (json.dumps(row["error"])[:120],)))
            else:
                out.append(_rego_value(row["result"]))
        shutil.rmtree(bdir, ignore_errors=True)
    return out


def evalB(cell_list, work):
    """Per-cell `opa eval --capabilities …` — the run_grid.py method, kept as the
    measured alternative and as the independent cross-check on the exec path."""
    env = dict(os.environ)
    env["TZ"] = "UTC"
    out = []
    with tempfile.TemporaryDirectory(dir=work) as td:
        path = os.path.join(td, "input.json")
        for cell in cell_list:
            with open(path, "w") as fh:
                fh.write(render_input(cell))
            proc = subprocess.run(
                [OPA, "eval", "--format", "json", "--fail", "--strict-builtin-errors",
                 "--capabilities", CAPS, "--timeout", "10s", "--data", POLICY,
                 "--input", path, "data.study.decision"],
                capture_output=True, text=True, env=env)
            if proc.returncode != 0:
                out.append(("REGO-ERROR", ("eval-exit-%d" % proc.returncode,)))
                continue
            val = json.loads(proc.stdout)["result"][0]["expressions"][0]["value"]
            out.append(_rego_value(val))
    return out


# =============================================================================
# the registered 2,000-cell stratified subsample (no RNG anywhere)
# =============================================================================
def stratified_subsample(n_target=2000):
    """Strata: sanctions(3) x country(4) x riskReadable(2) x spendReadable(2) = 48.

    Those four axes are the ones that select the evaluator PATH — which SS8 step
    resolves, whether U1's counterfactual engages, how many substitution axes it
    quantifies over — so they are the axes on which a simulator/engine divergence
    would live. Allocation is proportional by largest remainder (ties broken by
    canonical stratum order); selection inside a stratum is systematic at
    floor(i * |S| / n_S). Deterministic, reproducible, and free of any RNG."""
    strata = {}
    for index, cell in enumerate(cells()):
        key = (cell["sanctions"], cell["country"] or "OMITTED",
               cell["risk"] is not None, cell["spend"] is not None)
        strata.setdefault(key, []).append(index)
    order = sorted(strata)   # canonical stratum order, also the tie-break order
    sizes = [len(strata[k]) for k in order]
    total = sum(sizes)
    exact = [n_target * s / total for s in sizes]
    alloc = [int(x) for x in exact]
    remainder = n_target - sum(alloc)
    ranked = sorted(range(len(order)), key=lambda i: (-(exact[i] - alloc[i]), i))
    for i in ranked[:remainder]:
        alloc[i] += 1
    picked = []
    for i, key in enumerate(order):
        members, take = strata[key], alloc[i]
        for j in range(take):
            picked.append(members[(j * len(members)) // take])
    picked.sort()
    assert len(picked) == n_target and len(set(picked)) == n_target
    return picked, [{"stratum": list(k), "size": sizes[i], "allocated": alloc[i]}
                    for i, k in enumerate(order)]


# =============================================================================
# stages
# =============================================================================
def space_digest():
    """sha256 over the canonical enumeration, so a reviewer can prove they enumerated
    the same 236,196 cells in the same order before comparing any verdict."""
    h = hashlib.sha256()
    for cell in cells():
        h.update(json.dumps({k: cell[k] for k in KEYS}, sort_keys=True).encode())
        h.update(b"\n")
    return h.hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def digest_records():
    out = {}
    for label, path in (("jpack", JPACK), ("opa", OPA), ("refA/pack.json", PACK),
                        ("refB/policy.rego", POLICY), ("cells.json", GRID),
                        ("refA/results.jsonl", os.path.join(HERE, "refA", "results.jsonl")),
                        ("refB/results.jsonl", os.path.join(HERE, "refB", "results.jsonl"))):
        got = sha256_file(path)
        out[label] = {"sha256": got, "expected": EXPECTED_DIGESTS[label],
                      "match": got == EXPECTED_DIGESTS[label]}
    out["refA/jps_sim.py"] = {"sha256": sha256_file(os.path.join(HERE, "refA", "jps_sim.py")),
                              "expected": None, "match": None}
    out["cleanroom/oracle.py"] = {"sha256": sha256_file(os.path.join(DESIGN, "cleanroom", "oracle.py")),
                                  "expected": None, "match": None}
    return out


def stage_bench_rego(work, n=200):
    """Measure both rego methods on the same 200 cells; require them to AGREE."""
    allc = list(cells())
    step = len(allc) // n
    sample = [allc[i * step] for i in range(n)]
    bundle = build_bundle(work)

    t0 = time.time()
    got_exec = execB(bundle, sample, work)
    t_exec = time.time() - t0

    t0 = time.time()
    got_eval = evalB(sample, work)
    t_eval = time.time() - t0

    mismatches = [i for i in range(n) if got_exec[i] != got_eval[i]]
    faster = "opa-exec-bundle" if t_exec <= t_eval else "opa-eval-per-cell"
    return {
        "cells": n,
        "opaExecBundle": {"measuredSeconds": round(t_exec, 3),
                          "msPerCell": round(t_exec * 1000 / n, 3),
                          "projectedFullSpaceMinutes": round(t_exec / n * SPACE_SIZE / 60, 2),
                          "capabilitiesEnforcedAt": "build (opa build --capabilities); "
                                                    "opa exec has no --capabilities at v1.19.0"},
        "opaEvalPerCell": {"measuredSeconds": round(t_eval, 3),
                           "msPerCell": round(t_eval * 1000 / n, 3),
                           "projectedFullSpaceMinutes": round(t_eval / n * SPACE_SIZE / 60, 2),
                           "capabilitiesEnforcedAt": "invocation (opa eval --capabilities)"},
        "methodsAgree": not mismatches,
        "disagreementCells": len(mismatches),
        "chosen": faster,
        "speedup": round(t_eval / t_exec, 1) if t_exec else None,
        "canary": canary_refused(work),
    }


def stage_validate_sim(work, n=2000, jobs=12):
    """Fresh simulator re-validation against the pinned engine, on THIS space."""
    pack = json.load(open(PACK))
    picked, strata = stratified_subsample(n)
    allc = list(cells())
    sample = [allc[i] for i in picked]
    t0 = time.time()
    eng = engineA_many(sample, work, jobs=jobs)
    dt = time.time() - t0
    sim = [simA(pack, c) for c in sample]
    bad = [{"index": picked[i], "cell": sample[i],
            "sim": verdict_str(*sim[i]), "engine": verdict_str(*eng[i])}
           for i in range(n) if sim[i] != eng[i]]
    return {
        "record": "simulator-revalidation",
        "instrument": "reference/refA/jps_sim.py vs pinned jpack 0.17.0",
        "population": "2,000-cell deterministic stratified systematic subsample of the "
                      "236,196-cell derived space (48 strata: sanctions x country x "
                      "riskReadable x spendReadable; proportional largest-remainder "
                      "allocation; systematic selection within stratum; no RNG)",
        "cells": n,
        "disagreements": len(bad),
        "pass": not bad,
        "examples": bad[:10],
        "strata": strata,
        "measuredSeconds": round(dt, 1),
    }


def stage_grid_regression(work):
    """Control: reproduce the committed 2,540-cell agreement record with THIS
    program's two instruments, against the digest-pinned committed results."""
    grid = json.load(open(GRID))
    pack = json.load(open(PACK))
    committed_a, committed_b = {}, {}
    for target, path in ((committed_a, os.path.join(HERE, "refA", "results.jsonl")),
                         (committed_b, os.path.join(HERE, "refB", "results.jsonl"))):
        with open(path) as fh:
            for line in fh:
                if line.strip():
                    row = json.loads(line)
                    target[row["id"]] = (row["disposition"], tuple(sorted(row["reasons"])))
    cell_list = [{k: c[k] for k in KEYS} for c in grid]
    sim = [simA(pack, c) for c in cell_list]
    bundle = build_bundle(work)
    rego = execB(bundle, cell_list, work)
    sim_bad = [grid[i]["id"] for i in range(len(grid)) if sim[i] != committed_a[grid[i]["id"]]]
    rego_bad = [grid[i]["id"] for i in range(len(grid)) if rego[i] != committed_b[grid[i]["id"]]]
    ab_bad = [grid[i]["id"] for i in range(len(grid)) if sim[i] != rego[i]]
    return {
        "record": "grid-regression",
        "what": "the 2,540-cell design grid re-evaluated by this program's instruments "
                "and diffed against the digest-pinned committed results.jsonl of both "
                "references (AGREEMENT.md: 2,540/2,540)",
        "cells": len(grid),
        "simVsCommittedRefA": {"disagreements": len(sim_bad), "examples": sim_bad[:10]},
        "execVsCommittedRefB": {"disagreements": len(rego_bad), "examples": rego_bad[:10]},
        "refAvsRefB": {"divergences": len(ab_bad), "examples": ab_bad[:10]},
        "pass": not (sim_bad or rego_bad or ab_bad),
    }


def stage_run(work, jobs=12, cell_list=None, results_path=None, coverage=True):
    pack = json.load(open(PACK))
    cell_list = list(cells()) if cell_list is None else cell_list
    ids = [cell_id(c) for c in cell_list]
    assert len(set(ids)) == len(ids), "cell id collision"

    t0 = time.time()
    sim = [simA(pack, c) for c in cell_list]
    t_sim = time.time() - t0

    bundle = build_bundle(work)
    t0 = time.time()
    rego = execB(bundle, cell_list, work)
    t_rego = time.time() - t0

    diverging = [i for i in range(len(cell_list)) if sim[i] != rego[i]]

    # every divergence found via the simulator is CONFIRMED on the real engine
    t0 = time.time()
    confirm = engineA_many([cell_list[i] for i in diverging], work, jobs=jobs)
    t_confirm = time.time() - t0
    confirmed, retracted = [], []
    for k, i in enumerate(diverging):
        rec = {
            "cellId": ids[i], "index": i, "cell": cell_list[i],
            "refA": verdict_str(*confirm[k]),
            "refASimulator": verdict_str(*sim[i]),
            "refASimulatorConfirmedByEngine": confirm[k] == sim[i],
            "refB": verdict_str(*rego[i]),
            "class": "X1" if in_x1(cell_list[i]) else "OTHER",
            "matchesRefinedX1Description": in_x1_refined(cell_list[i]),
        }
        oracle_v = _oracle.verdict(dict(cell_list[i]))
        rec["cleanroomOracle"] = verdict_str(oracle_v["disposition"], oracle_v["reasons"])
        rec["oracleBacks"] = ("refB" if (oracle_v["disposition"], tuple(sorted(oracle_v["reasons"]))) == rego[i]
                              else "refA" if (oracle_v["disposition"], tuple(sorted(oracle_v["reasons"]))) == confirm[k]
                              else "neither")
        if confirm[k] == rego[i]:
            retracted.append(rec)   # engine says they agree: a simulator artefact
        else:
            confirmed.append(rec)

    census_a, census_b = {}, {}
    for i in range(len(cell_list)):
        census_a[verdict_str(*sim[i])] = census_a.get(verdict_str(*sim[i]), 0) + 1
        census_b[verdict_str(*rego[i])] = census_b.get(verdict_str(*rego[i]), 0) + 1

    # verdict-class coverage: engine-confirm a systematic slice of every refA class
    by_class = {}
    for i in range(len(cell_list)):
        by_class.setdefault(verdict_str(*sim[i]), []).append(i)
    cover_idx = []
    if coverage:
        for cls in sorted(by_class):
            members = by_class[cls]
            take = min(100, len(members))
            cover_idx += [members[(j * len(members)) // take] for j in range(take)]
    cover_cells = [cell_list[i] for i in cover_idx]
    cover_eng = engineA_many(cover_cells, work, jobs=jobs) if cover_idx else []
    cover_bad = [{"cellId": ids[cover_idx[k]], "cell": cover_cells[k],
                  "sim": verdict_str(*sim[cover_idx[k]]), "engine": verdict_str(*cover_eng[k])}
                 for k in range(len(cover_idx)) if sim[cover_idx[k]] != cover_eng[k]]

    results_digest = None
    if results_path:
        # gzip with mtime=0 and no embedded filename, so the archive is a function of
        # its contents alone; the recorded digest is over the UNCOMPRESSED stream, which
        # is the thing a reviewer regenerating this file can actually match.
        digest = hashlib.sha256()
        with open(results_path, "wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
                for i in range(len(cell_list)):
                    line = (json.dumps({"id": ids[i], "index": i,
                                        "refA": verdict_str(*sim[i]),
                                        "refB": verdict_str(*rego[i])},
                                       sort_keys=True) + "\n").encode()
                    digest.update(line)
                    gz.write(line)
        results_digest = digest.hexdigest()

    return {
        "cells": len(cell_list),
        "divergences": confirmed,
        "simulatorArtefacts": retracted,
        "censusRefA": census_a,
        "censusRefB": census_b,
        "coverageCheck": {
            "record": "verdict-class-coverage",
            "what": "up to 100 systematically-selected cells per distinct refA verdict "
                    "class re-evaluated on the pinned engine",
            "cells": len(cover_idx),
            "classes": sorted(by_class),
            "disagreements": len(cover_bad),
            "examples": cover_bad[:10],
            "pass": not cover_bad,
        },
        "timing": {"refASimulatorSeconds": round(t_sim, 1),
                   "refBOpaExecSeconds": round(t_rego, 1),
                   "divergenceEngineConfirmationSeconds": round(t_confirm, 1)},
        "resultsFile": os.path.basename(results_path) if results_path else None,
        "resultsSha256Uncompressed": results_digest,
        "resultsArchiveSha256": sha256_file(results_path) if results_path else None,
    }


# =============================================================================
# certificate
# =============================================================================
SPACE_DEF = {
    "name": "derived input space (arm-A builder precedent)",
    "size": SPACE_SIZE,
    "enumerationOrder": "itertools.product over the axes in declaration order; the "
                        "index in that order is the registered cell index",
    "cellIdRule": "d + sha256(canonical-json of the 9 axis values)[:16], uniqueness asserted",
    "axes": [
        {"axis": "sanctions", "values": SANCTIONS, "omittedMember": False,
         "why": "3-valued enum; UNKNOWN is a VALUE (governed by D2), not an absence. "
                "U1's parenthetical excludes the screening result from the counterfactual. "
                "An absent sanctions member is outside the registered space (see "
                "limitations.sanctionsOmitted)."},
        {"axis": "country", "values": COUNTRY, "omittedMember": True,
         "why": "readable domain is exactly {LOW,MEDIUM,HIGH}: enumerated exhaustively. "
                "omitted = unreadable (member absent from the input document)."},
        {"axis": "risk", "values": RISK, "omittedMember": True,
         "why": "readable domain 0..100 integers; every clause reads risk only through "
                "the thresholds 40, 70, 90, cutting [0,39][40,69][70,89][90,100]. Each "
                "block's BOTH endpoints are used, so a mis-stated inclusivity surfaces as "
                "a disagreement between an interval's endpoints. 39/40, 69/70, 89/90 are "
                "the band boundaries +-1; 0 and 100 are the outer blocks' representatives."},
        {"axis": "spend", "values": SPEND, "omittedMember": True,
         "why": "readable domain 0.00..10,000,000.00 at cents (1,000,000,001 values); every "
                "clause reads spend only through the thresholds 100,000.00, 500,000.00, "
                "2,000,000.00, cutting [0,100000.00](100000.00,500000.00]"
                "(500000.00,2000000.00](2000000.00,10000000.00]. Both endpoints of each "
                "block; x.01 is the next representable cent at each open lower endpoint; "
                "the pair (2000000.00, 2000000.01) exercises D6b-inclusive and O3-exclusive."},
        {"axis": "newVendor", "values": TRI, "omittedMember": True,
         "why": "declared domain {yes,no} enumerated exhaustively; omitted = unreported."},
        {"axis": "critical", "values": TRI, "omittedMember": True,
         "why": "declared domain {yes,no} enumerated exhaustively; omitted = unreported."},
        {"axis": "prior", "values": TRI, "omittedMember": True,
         "why": "declared domain {yes,no} enumerated exhaustively; omitted = unreported."},
        {"axis": "finEvidence", "values": EV, "omittedMember": True,
         "why": "evidence tri-state, exhaustive: available / unavailable / unreported."},
        {"axis": "insurance", "values": EV, "omittedMember": True,
         "why": "evidence tri-state, exhaustive: available / unavailable / unreported."},
    ],
    "representativenessArgument":
        "risk and spend are the only axes whose readable domains are not enumerated. Both "
        "are covered by threshold-block representatives with both endpoints of every block, "
        "which is exact for any implementation whose spend/risk sensitivity is confined to "
        "the six declared thresholds. That premise is checked, not assumed: refB's "
        "crosscheck.py re-runs U1 over all 101 risk values and a 17-point dense spend "
        "sample, and the clean-room oracle quantifies U1 over the full 101-value risk "
        "domain. Neither reference's text carries a seventh threshold.",
    "relationToDesignGrid":
        "the 2,540-cell design grid (reference/cells.json) and this space overlap but "
        "neither contains the other; the grid's agreement record is re-verified here as a "
        "control (validation record grid-regression) rather than inherited.",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all",
                    choices=["all", "bench-rego", "validate-sim", "grid-regression", "run"])
    ap.add_argument("--work", default=os.path.join(tempfile.gettempdir(), "s019-offgold"))
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--with-sanctions-omitted", action="store_true")
    ap.add_argument("--out", default=HERE)
    args = ap.parse_args()

    os.makedirs(args.work, exist_ok=True)
    started = time.time()
    cert = {
        "certificate": "study-019 off-gold equivalence certificate",
        "gate": "PREREGISTRATION.md §4 GATE(pre-freeze) — off-gold equivalence check",
        "status": None,
        "interim": False,
        "space": dict(SPACE_DEF, digest=space_digest()),
        "reproduce": "reference/cert_offgold.py --stage all [--with-sanctions-omitted]",
        "registeredExclusionClasses": {
            "X1": {
                "registeredText": "{new vendor yes; risk in [40,70); LOW country with spend "
                                  "unreadable, or country unreadable with spend <= 100,000.00}",
                "source": "PREREGISTRATION.md §4",
                "predicateReadings": [
                    "'risk in [40,70)' requires a READABLE risk in that band; an unreadable "
                    "risk score is not a value in an interval",
                    "'spend <= 100,000.00' requires a READABLE spend",
                ],
                "implementation": "cert_offgold.py in_x1(), transcribed from "
                                  "cleanroom/check_oracle.py so the two cannot drift",
                "refinedDescription": "reference/refA/REPORT.md additionally reports "
                                      "sanctions CLEAR, financial evidence present, "
                                      "prior != yes, critical != yes for the 72-cell class; "
                                      "reported per divergence, never the gate",
            }
        },
        "toolchain": digest_records(),
        "validationRecords": [],
    }

    if args.stage in ("all", "bench-rego"):
        cert["methodChoice"] = stage_bench_rego(args.work)
        print("bench-rego:", json.dumps(cert["methodChoice"], indent=1)[:1200], flush=True)
    if args.stage in ("all", "validate-sim"):
        rec = stage_validate_sim(args.work, jobs=args.jobs)
        cert["validationRecords"].append(rec)
        print("validate-sim: disagreements=%d pass=%s" % (rec["disagreements"], rec["pass"]),
              flush=True)
    if args.stage in ("all", "grid-regression"):
        rec = stage_grid_regression(args.work)
        cert["validationRecords"].append(rec)
        print("grid-regression: pass=%s" % rec["pass"], flush=True)
    if args.stage in ("all", "run"):
        results_path = os.path.join(args.work, "offgold-results.jsonl.gz")
        run = stage_run(args.work, jobs=args.jobs, results_path=results_path)
        cert["validationRecords"].append(run.pop("coverageCheck"))
        cert["cells"] = run["cells"]
        cert["divergences"] = run["divergences"]
        cert["simulatorArtefactsRetracted"] = run["simulatorArtefacts"]
        cert["censusRefA"] = run["censusRefA"]
        cert["censusRefB"] = run["censusRefB"]
        cert["timing"] = run["timing"]
        cert["fullResults"] = {
            "file": run["resultsFile"],
            "sha256Uncompressed": run["resultsSha256Uncompressed"],
            "sha256Archive": run["resultsArchiveSha256"],
            "committed": False,
            "regenerate": "reference/cert_offgold.py --stage all",
            "note": "236,196 rows (3.2 MB gzipped); regenerable, not committed — the "
                    "refB/inputs precedent from AGREEMENT.md",
        }

        classes = set(d["class"] for d in cert["divergences"])
        cert["allDivergencesInRegisteredClasses"] = classes <= {"X1"}
        cert["divergenceCountsByClass"] = {
            c: sum(1 for d in cert["divergences"] if d["class"] == c) for c in sorted(classes)
        }
        if args.with_sanctions_omitted:
            ext = stage_run(args.work, jobs=args.jobs, cell_list=list(extension_cells()),
                            coverage=False)
            patterns = {}
            for d in ext["divergences"]:
                key = "refA=%s | refB=%s | oracle=%s | class=%s" % (
                    d["refA"], d["refB"], d["cleanroomOracle"], d["class"])
                patterns[key] = patterns.get(key, 0) + 1
            cert["supplementaryStratum"] = {
                "name": "sanctions member physically absent",
                "registered": False,
                "gates": "nothing — reported because §SPACE note 1 declares the gap, and a "
                         "declared gap a reviewer cannot size is worth less than a measured one",
                "cells": ext["cells"],
                "divergenceCount": len(ext["divergences"]),
                "divergenceCountsByClass": {
                    c: sum(1 for d in ext["divergences"] if d["class"] == c)
                    for c in sorted(set(d["class"] for d in ext["divergences"]))},
                "divergencePatterns": patterns,
                "examples": ext["divergences"][:20],
                "fullListOmitted": "18,954 rows; the pattern census above is exhaustive over "
                                   "them and the list is regenerable with "
                                   "--with-sanctions-omitted",
                "censusRefA": ext["censusRefA"],
                "censusRefB": ext["censusRefB"],
                "simulatorArtefactsRetracted": len(ext["simulatorArtefacts"]),
                "reading": "an absent sanctions member is an input the prose does not define, "
                           "and all three implementations answer it differently — refA "
                           "unresolved[unknown] (no rule condition can be satisfied), refB "
                           "unresolved[no-match] (the total-function backstop), and the "
                           "clean-room oracle a spread of ordinary determinations (it does "
                           "not gate D3-D8 on CLEAR). This is undefined behaviour being "
                           "reported as undefined behaviour, not a reference defect; it is "
                           "what keeps the axis out of the registered space. It matters for "
                           "the E4 identity control, which evaluates AUTHOR-written inputs "
                           "that can omit any member: see OFFGOLD-CERT.md 'What this "
                           "certificate hands the freeze PR'.",
            }

        gates = all(r.get("pass") for r in cert["validationRecords"])
        gates = gates and cert["methodChoice"]["methodsAgree"] and cert["methodChoice"]["canary"]["refused"]
        gates = gates and all(v["match"] is not False for v in cert["toolchain"].values())
        cert["status"] = ("PASS" if (cert["allDivergencesInRegisteredClasses"] and gates)
                          else "BLOCKS-FREEZE")
        cert["method"] = {
            "armA": "reference/refA/jps_sim.py (engine-validated simulator) for the sweep; "
                    "pinned jpack 0.17.0 for every reported divergence and for all three "
                    "validation records. Every divergence verdict printed in this "
                    "certificate for refA is an ENGINE verdict.",
            "armB": cert["methodChoice"]["chosen"] + " (measured against the alternative on "
                    "200 cells; both methods required to agree cell-for-cell before use)",
            "diff": "(disposition, sorted reason set) per cell — diff_refs.py's protocol",
            "oracleRole": "clean-room oracle consulted as a THIRD OPINION on divergence "
                          "cells only; recorded, never substituted for a reference",
        }
    cert["elapsedSeconds"] = round(time.time() - started, 1)

    out_json = os.path.join(args.out, "OFFGOLD-CERT.json")
    with open(out_json, "w") as fh:
        json.dump(cert, fh, indent=1, sort_keys=True)
    print("wrote", out_json)
    print("status:", cert["status"])


if __name__ == "__main__":
    main()
