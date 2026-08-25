"""The two-engine execution layer, and the gate in front of it.

ASSEMBLED FROM the design prototypes, carried with their invocation flags
unchanged because those flags are pinned by `design/TOOLCHAIN-NOTES.md` and were
verified empirically against the pinned binaries:

* `design/pilot/pilot_run.py`
  (sha256 `09da06b334f6b3ae3224b03f6e49e2f0f3c5519401e94e72f23df7333cffd295`):
  `clean_env()` (232-241), `facts_documents()` (316-327),
  `render_rego_input()` (328-346), `eval_arm_a()` (347-376),
  `eval_arm_rego()` (377-414), `jpack_json()` (217-229);
* `design/mutants/e4_score.py`
  (sha256 `beb42b3903284dc2c33baff33000325814a1e53171d8268ca4d56820e4f995fb`):
  `opa_test()` (337-374);
* `design/gold/check_gold.py`
  (sha256 `a3aa62ea51491f370f4423f4945b79aa9bae06d03dd60489b9c8952ec6e9294b`):
  the floor-gate invocation, which is the same `opa eval` line under a
  different caller and is why the flags below are stated once.

`harness/PORTS.md` carries the two-sided row and the enumerated change list.

WHAT IS NEW HERE, and why each piece exists
-------------------------------------------

**The binaries are verified fail-closed before any of them is invoked.** The
prototypes read `JPACK_BIN`/`OPA_BIN`/`OPA_CAPS` from the environment and
invoked whatever was there. PREREGISTRATION.md section 2 pins jpack v0.17.0 by
binary digest and OPA v1.19.0 by asset digest, and records the specific hazard:
"The operator PATH binary is v0.10.0 and must never be invoked." `Toolchain()`
therefore resolves each path, hashes it, and REFUSES on any mismatch — with the
pin, the observed digest and the resolved path named — before the first
subprocess. A digest mismatch is the section 1a apparatus code
`binary-digest-mismatch`, never an authoring outcome.

**The capabilities canary is a control gate, re-run at attempt time.** Section 2
registers that the filtered capabilities file must REFUSE `time.now_ns`, and
section 5's decision rule row 2 makes "capabilities canary passes" a
control-gate FAILURE — a canary that evaluates is a capabilities file that does
not constrain, and every non-determinism argument built on it is void.
`capabilities_canary()` compiles a three-line probe under the pinned
capabilities and requires the compile to fail; the probe's bytes are in this
reviewed source rather than in a data file, so the gate cannot be defanged by
editing a fixture. It also compiles the same probe under the binary's OWN
unfiltered set (`e4lib/capabilities.py`), because refused-both-ways is a broken
probe rather than a working filter: `bothDirections` is accepted-unfiltered AND
refused-filtered, and it is REPORTED here while `score.py`'s gate still reads
`refused` alone.

**`opa exec` is not used.** Verified at v1.19.0: `opa exec` does not accept
`--capabilities`, so an `exec`-based scorer would evaluate under the FULL
builtin set while claiming the filtered one. Scored invocations are per-row
`opa eval --format json --fail --strict-builtin-errors --capabilities <file>
--timeout <t>` under a scrubbed environment with `TZ=UTC` and a per-run
exclusive directory.

**Verdicts are read from the payload, never from the exit code.** Section 2:
jpack exit codes distinguish invocation failure (3/4/5) from an evaluator
answer (0/1/2), and an undefined `opa eval` result without `--fail` prints `{}`
and exits 0. Every function below reads the JSON document and treats the status
as evidence only about the invocation.

**The `opa test` exit taxonomy, settled empirically at v1.19.0 (round-1 R1-8).**
The review found this module's own table reversed. It was, and the correction is
in the direction the pinned binary says rather than the direction the review's
summary suggested — measured on `design/reference/refB/policy.rego` with a pilot
suite, a paired mutant, a deliberate parse error, a deliberate runtime error, a
missing file, an empty suite and `--strict`:

    exit 0   every test passed (and an empty suite, which passes vacuously)
    exit 2   at least one test FAILED — an assertion, or a runtime error that
             made the assertion undefined
    exit 1   the invocation never got as far as running tests: a load, parse or
             compile error, or a file that is not there

`design/TOOLCHAIN-NOTES.md` ("`opa test` with a failing test exits **2**") and
PREREGISTRATION.md §2 were therefore already RIGHT, and this file's
`{1: "test-failure", 2: "error"}` was the wrong document. Nothing is keyed on the
exit code any more regardless: `opa_test()` consumes `--format json`, and the
status it returns is derived from the RESULT DOCUMENT — which is what makes an
assertion failure (a kill) distinguishable from a compile failure (an apparatus
refusal) rather than both being "nonzero".
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess

# The row-level engine bound. It is NOT the section 2 per-call ceiling (2700 s,
# which bounds an AUTHORING call and is the wrapper's); this is the bound past
# which one evaluation of one row is abandoned, and it exists so a mutant that
# makes an engine loop cannot stall a batch's scoring.
ENGINE_TIMEOUT_S = 60
# The `--timeout` the pinned OPA is given for its own evaluation, from
# design/TOOLCHAIN-NOTES.md. Two bounds, deliberately: OPA's own is the one that
# produces a diagnosable error document, and the subprocess bound above is the
# one that survives an engine that ignores its own.
OPA_EVAL_TIMEOUT = "10s"

# The registered entrypoint both Rego references and every authored policy must
# answer at (the naming appendix's `Rego package/entrypoint`).
REGO_ENTRYPOINT = "data.study.decision"

# The capabilities canary, in this reviewed source. Section 2: "the `time.now_ns`
# canary must be refused (verified; re-verified at attempt time as a control
# gate)."
CANARY_REGO = "package canary\nimport rego.v1\nx if { time.now_ns() > 0 }\n"

# gold/matrix input key -> (facts member, wire kind), from the naming appendix.
VENDOR_FIELDS = (
    ("risk", "riskScore", "number"),
    ("spend", "requestedSpend", "number"),
    ("sanctions", "sanctionsStatus", "string"),
    ("country", "countryRisk", "string"),
    ("newVendor", "newVendor", "string"),
    ("critical", "criticalSupplier", "string"),
    ("prior", "priorEnforcement", "string"),
)
EVIDENCE_FIELDS = (("finEvidence", "financial-evidence"),
                   ("insurance", "insurance-certificate"))


class EngineError(Exception):
    """A refusal in the execution layer, with a named code as its first word.

    Every code this class carries is an APPARATUS failure in section 1a's sense:
    it says the pipeline could not be trusted to ask the question, never that
    the author's artifact was wrong."""


def _digest(path: str) -> str:
    with open(path, "rb") as handle:
        return "sha256:" + hashlib.sha256(handle.read()).hexdigest()


def clean_env(home: str) -> dict:
    """The scrubbed environment every engine call runs under.

    `env -i` in a dict: no inherited `JPACK_CONFIG` (which would let an operator
    config file change what the evaluator does), `TZ` pinned to UTC, and `HOME`
    and `TMPDIR` pointed at a per-run exclusive directory that holds no
    `jpack.json` — section 2: "Harness runs outside any `jpack.json` declaring
    an `audit` member."""
    return {"PATH": "/usr/bin:/bin", "TZ": "UTC", "HOME": home, "TMPDIR": home}


class Toolchain:
    """The pinned binaries, resolved and verified once, then carried.

    Constructed from the pin registry and the environment. Every path is
    resolved to an absolute real path before it is hashed, so a symlink swapped
    between the hash and the call cannot be what runs — and the resolved path is
    what is invoked, not the name that was passed in.

    `capabilitiesSha256` is null in the registry pre-freeze. A NULL pin is not
    silently satisfied and it is not fatal either: the file's observed digest is
    recorded in `unenforced` so the attempt record says, in its own bytes, which
    pins were declarations rather than enforcements. Every NON-null pin is
    enforced under both the REGISTERED and the PILOT label, which is the
    registry's own rule."""

    def __init__(self, pins: dict, environ: dict = None):
        environ = os.environ if environ is None else environ
        self.problems = []
        self.unenforced = []
        self.jpack = self._resolve(environ, "JPACK_BIN", "jpack binary")
        self.opa = self._resolve(environ, "OPA_BIN", "opa binary")
        self.caps = self._resolve(environ, "OPA_CAPS", "opa capabilities file")
        self._enforce(self.jpack, (pins.get("jpack") or {}).get("binarySha256"),
                      "jpack.binarySha256")
        self._enforce(self.opa, (pins.get("opa") or {}).get("assetSha256"),
                      "opa.assetSha256")
        self._enforce(self.caps, (pins.get("opa") or {}).get("capabilitiesSha256"),
                      "opa.capabilitiesSha256")

    def _resolve(self, environ, variable, what):
        raw = environ.get(variable)
        if not raw:
            self.problems.append(
                "binary-digest-mismatch %s is unset and there is no default: the "
                "%s must be named explicitly, because the operator's PATH holds a "
                "different version that must never be invoked "
                "(PREREGISTRATION.md section 2)" % (variable, what))
            return None
        path = os.path.realpath(raw)
        if not os.path.isfile(path):
            self.problems.append(
                "binary-digest-mismatch %s names %s, which is not a file"
                % (variable, path))
            return None
        return path

    def _enforce(self, path, pin, name):
        if path is None:
            return
        observed = _digest(path)
        if pin is None:
            self.unenforced.append({"pin": name, "observedSha256": observed})
            return
        if observed != pin:
            self.problems.append(
                "binary-digest-mismatch %s pins %s and the resolved file hashes "
                "to %s" % (name, pin, observed))

    def require(self):
        """Fail-closed: raise unless every resolved path matched every non-null
        pin. Called before the first invocation, never after."""
        if self.problems:
            raise EngineError("; ".join(self.problems))
        return self

    def record(self) -> dict:
        """What the attempt publishes about the toolchain: digests and pin
        names, never absolute paths — no output of this scorer embeds one."""
        return {
            "jpackSha256": None if self.jpack is None else _digest(self.jpack),
            "opaSha256": None if self.opa is None else _digest(self.opa),
            "capabilitiesSha256": None if self.caps is None else _digest(self.caps),
            "unenforcedPins": list(self.unenforced),
            "problems": list(self.problems),
        }


def _run(argv, cwd, timeout=ENGINE_TIMEOUT_S):
    try:
        finished = subprocess.run(argv, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, timeout=timeout,
                                  cwd=cwd, env=clean_env(cwd))
    except subprocess.TimeoutExpired:
        return 124, "", ""
    return (finished.returncode,
            finished.stdout.decode("utf-8", "replace"),
            finished.stderr.decode("utf-8", "replace"))


#: ROUND-1 FINDING R1-1: the typed third state. An invocation that produced
#: NO ANSWER AT ALL — a timeout, a self-declared invocation failure, an
#: answering exit whose stream is not a document — is an APPARATUS event in
#: §1a's sense, and it is typed here at the source so no admission or E1 layer
#: can file it as something the author emitted.
INVOCATION_TIMEOUT = "engine-timeout"
INVOCATION_FAILURE = "invocation-failure"
UNREADABLE_INVOCATION = "unreadable-invocation-output"
#: jpack's own exit taxonomy (§2, and this module's docstring): 0/1/2 are
#: evaluator ANSWERS, 3/4/5 are the binary declaring its own invocation
#: failed.
JPACK_ANSWER_EXITS = (0, 1, 2)


def invocation_refusal(code: int, payload_readable: bool,
                       answer_exits=JPACK_ANSWER_EXITS):
    """The R1-1 discrimination, in one place: None for a live answer, else the
    typed refusal class."""
    if code == 124:
        return INVOCATION_TIMEOUT
    if code not in answer_exits:
        return "%s:%d" % (INVOCATION_FAILURE, code)
    if not payload_readable:
        return UNREADABLE_INVOCATION
    return None


def jpack_json(tools: Toolchain, argv_tail, workdir: str) -> tuple:
    """Run a jpack command and return
    `(payload_or_None, rc, stdout, stderr, refusal_or_None)`.

    The payload is the answer; `rc` is evidence about the INVOCATION only
    (section 2); `refusal` is R1-1's typed apparatus state — a timeout, a
    3/4/5 invocation failure, or an answering exit with an unreadable stream —
    and a caller that files a non-None refusal as an authoring outcome is the
    defect R1-1 names."""
    code, out, err = _run([tools.jpack] + list(argv_tail), workdir)
    try:
        payload = json.loads(out)
        readable = True
    except ValueError:
        payload = None
        readable = False
    return payload, code, out, err, invocation_refusal(code, readable)


def opa_check(tools: Toolchain, path: str, workdir: str,
              v0_compatible: bool = False, capabilities: str = None) -> tuple:
    """`opa check --strict --capabilities <caps>` on one file.

    Returns `(exit_code, sorted error codes)`. Codes only, never message prose:
    an error message is upstream's wording and would put upstream's prose in
    this study's published record.

    `capabilities` overrides the pinned file for ONE caller only: the canary's
    unfiltered arm, which has to name a DIFFERENT capabilities file rather than
    omit the flag, so that the two arms of the control differ in exactly one
    thing. Every scored invocation leaves it None and gets `tools.caps`."""
    argv = [tools.opa, "check", "--strict", "--capabilities",
            tools.caps if capabilities is None else capabilities,
            "--format", "json"]
    if v0_compatible:
        argv.append("--v0-compatible")
    argv.append(path)
    code, out, err = _run(argv, workdir)
    # R1-1: a timed-out `opa check` produced no verdict about the policy; it
    # must surface as the typed apparatus refusal, never as the authoring
    # code the unreadable-stream fallback below maps to.
    if code == 124:
        raise EngineError(
            "ENGINE-INVOCATION-REFUSED opa check timed out at %ds on %s: the "
            "invocation produced no verdict about the artifact and §1a files "
            "that on the apparatus side (R1-1)" % (ENGINE_TIMEOUT_S, path))
    if code == 0:
        return code, []
    codes = []
    for stream in (err, out):
        try:
            document = json.loads(stream)
        except ValueError:
            continue
        codes = sorted({str(entry.get("code", "?"))
                        for entry in document.get("errors", [])})
        if codes:
            break
    return code, codes or ["unparseable-check-output"]


def opa_parse_tree(tools: Toolchain, path: str, workdir: str) -> tuple:
    """NEW IN 020. `opa parse --format json` on one file: `(exit, stdout, stderr)`.

    NAMED APART FROM `opa_parse()` BELOW, and the name is the whole of the fix.
    Study 019 already had an `opa_parse()` on this module returning `(exit,
    stdout)` — `e4lib/domain.py` and `e4lib/e4.py` read it that way — so a
    second definition under the same name did not add a function, it REPLACED
    one at import: the later `def` won, `presence_idiom.parse_policy()` unpacked
    two values into three, and §3.2's detector raised `ValueError` on its first
    real call. Nothing caught it because every unit case monkeypatches
    `opa_parse` with a three-tuple stub and the one case that uses the pinned
    binary calls `subprocess.run` directly and then `memberships()`, so no test
    on either line ever executed `parse_policy()`.

    The one read-only addition to the two-engine execution layer, and it is here
    rather than in `e4lib/presence_idiom.py` for the reason every other
    invocation is here: the pinned binary is invoked from ONE module, under
    `_run()`'s scrubbed environment and the one engine timeout, so a second
    call site cannot acquire a second environment. It takes no capabilities file
    — `parse` performs no evaluation and accepts no `--capabilities` at the
    pinned version — and it is never scored: `e4lib/presence_idiom.py` reads the
    syntax tree and the syntax tree only.
    """
    return _run([tools.opa, "parse", "--format", "json", path], workdir)


def capabilities_canary(tools: Toolchain, workdir: str) -> dict:
    """The registered control gate: the filtered capabilities file must REFUSE
    `time.now_ns`.

    `passed` here means the CANARY WAS REFUSED, which is the outcome the study
    wants — named `refused` in the record as well, because "the canary passed"
    reads both ways in English and section 5's decision rule row 2 spells the
    failure as "capabilities canary passes". A canary that compiles means the
    capabilities file constrains nothing and every determinism claim built on
    it is void.

    THE SECOND ARM. A canary refused under the pinned file is half a control:
    refused BOTH ways is a broken probe (a typo refuses everywhere) and proves
    nothing about the filter. `acceptedUnfiltered` is the other half — the same
    probe, under the binary's OWN capability set, freshly derived and written to
    a file so the two arms differ in exactly one thing, which capabilities file
    is named. `bothDirections` is the conjunction and is the only thing that
    means "the filter has demonstrated power".

    `bothDirections` is REPORTED, not yet gated: `score.py`'s
    `capabilities-canary-refused` gate reads `refused`, and moving a gate's
    answer is a change to the registered decision surface rather than to this
    module. The unfiltered arm never turns a refusal into a pass — it can only
    add a problem — so recording it is strictly more evidence than before."""
    path = os.path.join(workdir, "canary.rego")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(CANARY_REGO)
    code, codes = opa_check(tools, path, workdir)
    record = {"refused": code != 0, "exitCode": code, "errorCodes": codes,
              "gate": "the filtered capabilities file must refuse time.now_ns"}
    record.update(_canary_unfiltered(tools, path, workdir))
    record["bothDirections"] = bool(record["refused"]
                                    and record["acceptedUnfiltered"] is True)
    return record


def _canary_unfiltered(tools: Toolchain, policy_path: str,
                       workdir: str) -> dict:
    """The canary under the pinned binary's OWN unfiltered capability set.

    Refuses to lie about what it could not measure: when the full set cannot be
    derived — no `opa` on this seat, a stub in a unit test, a binary that will
    not answer — `acceptedUnfiltered` is None and `unfilteredProblem` names the
    reason. None is not False: "the second arm did not run" and "the second arm
    ran and the probe was refused unfiltered too" are different facts and a
    boolean would merge them."""
    from . import capabilities  # deferred: capabilities imports this module
    blank = {"acceptedUnfiltered": None, "unfilteredExitCode": None,
             "unfilteredErrorCodes": [], "unfilteredProblem": None}
    try:
        full_path = capabilities.write_full_capabilities(tools.opa, workdir)
    except (capabilities.CapabilitiesError, OSError) as error:
        blank["unfilteredProblem"] = str(error)
        return blank
    code, codes = opa_check(tools, policy_path, workdir,
                            capabilities=full_path)
    return {"acceptedUnfiltered": code == 0, "unfilteredExitCode": code,
            "unfilteredErrorCodes": codes, "unfilteredProblem": None}


def facts_documents(inputs: dict) -> tuple:
    """`(facts, evidence)` for arm A, from a canonical input signature.

    An OMITTED member is the wire form of "unreadable / unreported" — section 4's
    input-domain closure turns on that being a distinct state from a present
    value, so a `None` is dropped rather than serialised as null."""
    vendor = {}
    for source, member, _kind in VENDOR_FIELDS:
        if inputs.get(source) is not None:
            vendor[member] = inputs[source]
    evidence = {}
    for source, member in EVIDENCE_FIELDS:
        if inputs.get(source) is not None:
            evidence[member] = inputs[source]
    return {"vendor": vendor}, evidence


def render_rego_input(inputs: dict) -> str:
    """The Rego input document, built TEXTUALLY.

    `riskScore` and `requestedSpend` are spliced from the canonical decimal
    STRINGS so OPA parses them as exact JSON numbers. Round-tripping them
    through a Python float would put a binary approximation of `500000.01` on
    one side of a threshold the policy tests with `>`, which is precisely the
    kind of silent boundary flip the mutant classes are built to detect."""
    vendor, evidence = [], []
    for source, member, kind in VENDOR_FIELDS:
        value = inputs.get(source)
        if value is None:
            continue
        vendor.append('"%s": %s' % (member, value if kind == "number"
                                    else json.dumps(value)))
    for source, member in EVIDENCE_FIELDS:
        value = inputs.get(source)
        if value is None:
            continue
        evidence.append('"%s": %s' % (member, json.dumps(value)))
    return '{"vendor": {%s}, "evidence": {%s}}\n' % (", ".join(vendor),
                                                     ", ".join(evidence))


def eval_pack(tools: Toolchain, pack_path: str, facts: dict, evidence: dict,
              workdir: str) -> tuple:
    """Evaluate a JPS pack on one input point.

    Returns the SCORED-SURFACE tuple `(kind, outcomeId, sorted reasons)` — PREREG
    section 5: "Scored surface: kind + outcomeId + reasons (as sorted sets)".
    `handoff` and `trace[]` are outside every endpoint and are not read here at
    all, so no later filter can forget to drop them. A refusal is
    `("ROW-ERROR", <class>, ())` and never an exception: a mutant that makes the
    evaluator refuse is a mutant the suite may legitimately kill."""
    facts_path = os.path.join(workdir, "facts.json")
    evidence_path = os.path.join(workdir, "evidence.json")
    with open(facts_path, "w", encoding="utf-8") as handle:
        json.dump(facts, handle, sort_keys=True)
    with open(evidence_path, "w", encoding="utf-8") as handle:
        json.dump(evidence, handle, sort_keys=True)
    payload, code, _out, _err, refusal = jpack_json(
        tools, ["experimental", "evaluate", pack_path, "--facts", facts_path,
                "--evidence", evidence_path, "--format", "json"], workdir)
    if refusal is not None:
        # R1-1: the typed no-answer classes. Callers scoring an AUTHORED
        # artifact route these to the apparatus side; the kill path keeps them
        # as ROW-ERROR because a mutant that provokes an engine refusal is a
        # signal the suite may legitimately carry (`refusedAll` and §6's gate
        # adjudicate that separately).
        return ("ROW-ERROR", refusal, ())
    if payload is None:
        return ("ROW-ERROR", "non-json-payload", ())
    if payload.get("status") != "evaluated":
        diagnostics = payload.get("diagnostics") or []
        error_class = ((payload.get("error") or {}).get("class")
                       or (diagnostics[0].get("code") if diagnostics else None)
                       or payload.get("status") or "refused")
        return ("ROW-ERROR", str(error_class), ())
    disposition = payload.get("disposition") or {}
    kind = disposition.get("kind")
    reasons = tuple(sorted(str(reason)
                           for reason in (disposition.get("reasons") or [])))
    if kind == "outcome":
        return ("outcome", disposition.get("outcomeId"), reasons)
    if kind == "unresolved":
        return ("unresolved", None, reasons)
    return ("ROW-ERROR", "unexpected-kind:%s" % kind, ())


def eval_rego(tools: Toolchain, policy_path: str, inputs: dict,
              workdir: str) -> tuple:
    """Evaluate a Rego policy on one input point, on the same scored surface.

    The B/C result contract carries `disposition` and `reasons`; the alignment
    map turns that into the same three-tuple arm A produces, so the two
    languages are compared on one surface rather than on two shapes that happen
    to agree."""
    input_path = os.path.join(workdir, "input.json")
    with open(input_path, "w", encoding="utf-8") as handle:
        handle.write(render_rego_input(inputs))
    code, out, _err = _run(
        [tools.opa, "eval", "--format", "json", "--fail",
         "--strict-builtin-errors", "--capabilities", tools.caps,
         "--timeout", OPA_EVAL_TIMEOUT, "--data", policy_path,
         "--input", input_path, REGO_ENTRYPOINT], workdir)
    if code == 124:
        return ("ROW-ERROR", "engine-timeout", ())
    try:
        document = json.loads(out)
    except ValueError:
        return ("ROW-ERROR", "non-json-payload", ())
    if isinstance(document, dict) and document.get("errors"):
        codes = sorted({str(entry.get("code", "?"))
                        for entry in document["errors"]})
        return ("ROW-ERROR", ",".join(codes), ())
    try:
        value = document["result"][0]["expressions"][0]["value"]
    except (KeyError, IndexError, TypeError):
        return ("ROW-ERROR", "undefined", ())
    if not isinstance(value, dict) or "disposition" not in value:
        return ("ROW-ERROR", "contract-shape", ())
    disposition = value.get("disposition")
    reasons = value.get("reasons", [])
    if not isinstance(disposition, str) or not isinstance(reasons, list) \
            or not all(isinstance(reason, str) for reason in reasons):
        return ("ROW-ERROR", "contract-shape", ())
    if disposition == "unresolved":
        return ("unresolved", None, tuple(sorted(reasons)))
    return ("outcome", disposition, tuple(sorted(reasons)))


# --- arms B/C: the machine-readable test result, and the syntax tree -------
#
# ROUND-1 FINDING R1-8. `opa test`'s exit status was the whole of what arms B/C
# read: identity passed on 0 and every mutant was killed on "nonzero". A compile
# failure, a load failure and a harness timeout are all nonzero, so a transient
# apparatus failure in the mutant phase made a weak suite high-kill, and the same
# failure against the reference made a correct suite fail identity and score
# zero. Both directions are closed by reading the RESULT DOCUMENT: an assertion
# failure is a kill, and everything else is a refusal that never enters a rate.

TEST_PASS = "pass"
TEST_FAILED = "failed"
TEST_ERRORED = "errored"
TEST_INVOCATION_REFUSED = "invocation-refused"
TEST_TIMEOUT = "timeout"
TEST_UNREADABLE = "unreadable-result-document"

# The two statuses that are EVIDENCE ABOUT THE SUITE. Every other status is
# evidence about the apparatus, and `e4.py` routes it accordingly.
TEST_SUITE_STATUSES = (TEST_PASS, TEST_FAILED)


def opa_test(tools: Toolchain, policy_path: str, suite_path: str,
             workdir: str) -> dict:
    """`opa test <policy> <suite> --format json` — arm B/C's identity control
    and kill probe, read from the result document.

    Returns a record whose `status` is one of the constants above:

        pass                 the document lists tests and none failed or errored
        failed               at least one test FAILED — the only kill signal
        errored              a test ERRORED, or its assertion never decided
                             because an EVALUATION FAULT made the body undefined
        invocation-refused   `opa test` never ran the tests (load/parse/compile)
        timeout              the harness's own bound
        unreadable-result-document   a nonempty stdout that is not a result list

    The exit status is RECORDED and read by nothing. At v1.19.0 it is 0/2/1 for
    pass/failure/invocation-error (module docstring), but a status is a contract
    that can move between versions and a result document is data.

    ROUND-2 FINDING R2-3, and the result document alone was not enough. §2
    registers the taxonomy — "a kill is an assertion failure on a named test, and
    a load/parse/compile/RUNTIME/timeout failure is an apparatus refusal" — and
    upstream's own testing document distinguishes a failed assertion from an
    evaluation error. But `opa test` has NO `--strict-builtin-errors` at v1.19.0
    (verified against the pinned binary), so a builtin fault inside a test body
    is not an error at all: it makes the expression UNDEFINED, the body
    undefined, and the test reports `fail: true` with no `error` member. The
    reviewer's probe is exactly that — a reference-passing test containing
    `1 / denominator == 1` against a valid mutant that sets the denominator to
    zero — and the harness credited a kill for a division by zero.

    The failure is therefore ADJUDICATED rather than read off one document: every
    test the run reports as failed is re-evaluated as a query, once, under
    `opa eval --strict-builtin-errors` over the same two files. Strict mode is
    where the pinned binary itself distinguishes the two — an evaluation fault
    comes back as an `errors` list carrying `eval_builtin_error`, and a genuine
    assertion failure comes back undefined (`{}`, exit 0). An adjudication whose
    own output cannot be read counts the test as ERRORED: fail-closed is a
    refusal, never a kill.

    ROUND-3 FINDING R3-3, and it reverses this function's stopping rule. The
    scan used to stop at the first test that survived adjudication, on the
    reading that "one real assertion failure is a kill and the rest is
    diagnosis". The reviewer's two-failure probe shows why that reading is not
    available: a suite whose LEXICALLY FIRST reported failure is a genuine
    assertion failure and whose later one is a division by zero returned
    `status: "failed"`, an empty `evaluationFaults` list, and `killed` from
    `e4.kill_arm_rego()` — an invocation in which the pinned engine faulted,
    scored as evidence about the suite. §2 registers the opposite: "a
    load/parse/compile/RUNTIME/timeout failure is an apparatus refusal", and an
    apparatus refusal is a property of the INVOCATION, not of whichever test
    happened to sort first. So EVERY reported failure is adjudicated, and any
    evaluation fault or unreadable adjudication anywhere in the run refuses the
    whole invocation regardless of how many genuine assertion failures sit
    beside it. `errored` therefore outranks `failed` when the status is chosen
    — the fail-closed direction, and the only one under which the reported
    status does not depend on a lexical accident."""
    code, out, err = _run(
        [tools.opa, "test", policy_path, suite_path,
         "--capabilities", tools.caps, "--timeout", OPA_EVAL_TIMEOUT,
         "--format", "json"], workdir)
    record = {"exitCode": code, "tests": 0, "failed": [], "errored": [],
              "status": None, "evaluationFaults": []}
    if code == 124:
        record["status"] = TEST_TIMEOUT
        return record
    try:
        document = json.loads(out)
    except ValueError:
        document = None
    if not isinstance(document, list):
        # An invocation that never got as far as running tests emits no result
        # list at all. Its diagnostics are upstream's prose, so only the
        # presence of a message is recorded, never its wording.
        record["status"] = (TEST_INVOCATION_REFUSED if not out.strip()
                            else TEST_UNREADABLE)
        record["diagnosticBytes"] = len(err.encode("utf-8"))
        return record
    reported_failures = []
    for entry in document:
        if not isinstance(entry, dict):
            record["status"] = TEST_UNREADABLE
            return record
        record["tests"] += 1
        name = "%s.%s" % (entry.get("package"), entry.get("name"))
        if entry.get("error") is not None:
            record["errored"].append(name)
        elif entry.get("fail"):
            reported_failures.append(name)
    # DETERMINISM, and it is a registered property of what this produces.
    # `opa test --format json` does not order its result list (`--sort` defaults
    # to `none`), so the retained lists are not a stable choice unless something
    # orders them. Sorting here makes the adjudication order — and therefore the
    # published `failedTests` and `evaluationFaults` — a function of the data
    # and not of the run.
    #
    # ROUND-3 R3-3: EVERY reported failure is adjudicated. There is no early
    # exit, because an early exit makes the answer depend on which name sorted
    # first, and the fault the scan skipped is an apparatus event that already
    # happened.
    for name in sorted(reported_failures):
        fault = evaluation_fault(tools, [policy_path, suite_path], name,
                                 workdir)
        if fault is None:
            record["failed"].append(name)
            continue
        record["evaluationFaults"].append({"test": name, "fault": fault})
        record["errored"].append(name)
    record["failed"].sort()
    record["errored"].sort()
    record["evaluationFaults"].sort(key=lambda entry: entry["test"])
    # ROUND-3 R3-3: `errored` OUTRANKS `failed`. An evaluation fault or an
    # unreadable adjudication anywhere in this invocation means the pinned
    # engine did not answer the question the run asked, and §2 routes that to
    # the `engine-execution-clean` control gate rather than into a rate — even
    # when a genuine assertion failure sits beside it, because the genuine
    # failure is evidence about the suite and the fault is evidence about the
    # apparatus, and the apparatus is what decides whether the invocation is
    # readable at all.
    if record["errored"]:
        record["status"] = TEST_ERRORED
    elif record["failed"]:
        record["status"] = TEST_FAILED
    else:
        record["status"] = TEST_PASS
    return record


def evaluation_fault(tools: Toolchain, data_paths, test_name: str,
                     workdir: str):
    """The named test re-evaluated in STRICT builtin-error mode: the fault code
    when the body could not be evaluated, or `None` when it merely did not hold.

    `test_name` is the result document's `"<package>.<name>"`, which is already
    a query path (`data.study_test.test_x`). A sub-test name carries a `/`
    suffix; the rule is what is queried, so the suffix is dropped and a fault
    anywhere in the rule counts — the conservative direction, since the outcome
    of a fault is a refusal.

    `None` means "a real assertion failure": under strict mode the query is
    undefined (`{}`, exit 0) or false, and neither is an apparatus event."""
    query = test_name.split("/")[0]
    code, raw = opa_eval_document(tools, list(data_paths), query, workdir)
    try:
        document = json.loads(raw.decode("utf-8", "replace") or "{}")
    except ValueError:
        return "unreadable-adjudication"
    if not isinstance(document, dict):
        return "unreadable-adjudication"
    errors = document.get("errors")
    if isinstance(errors, list) and errors:
        codes = sorted({entry.get("code") for entry in errors
                        if isinstance(entry, dict)
                        and isinstance(entry.get("code"), str)})
        return ",".join(codes) or "eval-error"
    if code != 0:
        # Nonzero with no readable error list: the adjudication itself did not
        # answer, and an unanswered adjudication is not evidence of a kill.
        return "adjudication-exit-%d" % code
    return None


def opa_eval_document(tools: Toolchain, data_paths, query: str,
                      workdir: str) -> tuple:
    """`opa eval <query>` over a set of data files — the RESOLVED document.

    Used by `e4lib/domain.py` to recover the case inputs of a table-driven
    `opa test` file (round-1 R1-3): real authored suites build their input points
    out of named constants and helper functions, so the syntax tree carries a ref
    where the point is, and only evaluation resolves it. This is the pinned
    binary's own reading, under the pinned capabilities and the registered flags
    — the same invocation `eval_rego()` uses, at a different query.

    Returns `(exit code, stdout bytes)`; the caller decodes."""
    argv = [tools.opa, "eval", "--format", "json",
            "--strict-builtin-errors", "--capabilities", tools.caps,
            "--timeout", OPA_EVAL_TIMEOUT]
    for path in data_paths:
        argv += ["--data", path]
    argv.append(query)
    code, out, _err = _run(argv, workdir)
    return code, out.encode("utf-8")


def opa_parse(tools: Toolchain, path: str, workdir: str) -> tuple:
    """`opa parse --format json <path>` — the syntax tree, for enumerating the
    case inputs of an `opa test` file (`e4lib/domain.py`, round-1 R1-3).

    Returns `(exit code, stdout bytes)`. Parsing is a SYNTAX operation and takes
    no capabilities file: the builtin set constrains evaluation, and a file that
    parses under one capabilities set parses under any."""
    code, out, _err = _run([tools.opa, "parse", "--format", "json", path],
                           workdir)
    return code, out.encode("utf-8")


def scope_str(scored) -> str:
    """One printable spelling of a scored-surface tuple, so a published
    disagreement reads the same in every table."""
    if scored is None:
        return "<unreadable-expectation>"
    if scored[0] == "ROW-ERROR":
        return "ROW-ERROR:%s" % scored[1]
    if scored[0] == "outcome":
        return "outcome:%s" % scored[1]
    return "unresolved:[%s]" % ",".join(scored[2])
