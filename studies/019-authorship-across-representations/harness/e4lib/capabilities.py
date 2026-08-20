"""The registered OPA capability sandbox, derived from the pinned binary.

WHAT THIS FILE DOES
-------------------
PREREGISTRATION.md section 2 registers, of the pinned OPA: "Capabilities file
generated from the pinned binary with the registered denylist; **the
`time.now_ns` canary must be refused** (verified; re-verified at attempt time as
a control gate)." Section 5's decision-rule row 3 makes "capabilities canary
passes" a control-gate FAILURE and section 6 lists the refusal among the
validity gates. `harness/PINS.json` carries the freeze pin `opaCapabilities`
(`opa.capabilitiesSha256`) over the file this module writes.

Every scored Rego invocation already names a capabilities file:
`e4lib/engines.py`'s `opa_check()`, `eval_rego()` and the canary all pass
`--capabilities <tools.caps>`, and `Toolchain` resolves that path from
`$OPA_CAPS` and hashes it against the registry pin. What was missing was the
FILE — the bytes those invocations are registered to run under. This module is
its generator, and `controls/opa-capabilities.json` is its committed output.

Two things follow from "generated", and both are load-bearing:

* The **full** capability set is read out of the pinned binary itself
  (`opa capabilities --current`, through `engines._run()`, after the resolved
  path has been hashed against `opa.assetSha256`). Nothing here carries a copy
  of OPA 1.19.0's builtin list; a list typed from memory would pin this study to
  what the author believed the binary contains.
* The **denylist** is a set of RULES over each builtin's own capability record,
  not a list of builtin names. That distinction is the whole reason this module
  is more than four lines, and it was earned twice over against this binary:

  - The registered family "print/trace" reads like the two builtins named
    `print` and `trace`. Deny exactly those two and `print("x")` **still
    compiles**, measured against the pinned binary: the compiler lowers a
    `print` call to `internal.print`, and with `internal.print` restored and
    `print` still removed `opa check --strict` returns 0. The rule here is "the
    last dotted segment is `print`", which catches both, and the test that
    proves the difference is the one that would have caught a name list.
  - The registered families clock / network / rand / uuid / `opa.runtime` are
    five names for one property: a result that is not a function of the call's
    arguments. The pinned binary declares that property directly, per builtin,
    as `"nondeterministic": true`. Reading the flag catches three builtins whose
    names advertise no such family — `io.jwt.decode_verify`,
    `io.jwt.encode_sign` and `io.jwt.encode_sign_raw` — which a family-word
    reading of the denylist leaves in place.

`engines.capabilities_canary()` closes the loop and keeps the probe's three
lines in reviewed source rather than in a fixture. This module supplies the
UNFILTERED arm of that control (`write_full_capabilities()`): the same probe,
under the binary's own set, written to a file, so the two arms differ in exactly
one thing — which capability file is named — and an accepted/refused split
cannot be an artefact of one arm passing `--capabilities` and the other not.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
* **It does not decide the denylist.** `harness/PINS.json` registers the nine
  family words at `opa.capabilitiesDenylist`; :data:`REGISTERED_DENYLIST` is a
  transcription of that member and `tests/test_score_capabilities.py` binds the
  two together in both directions, so a family cannot be added or dropped here
  without the registry disagreeing.
* **It does not claim to know why upstream flags a builtin nondeterministic.**
  The capability record carries the flag and no reason. It is tempting to write
  "`io.jwt.decode_verify` reads the wall clock to check `exp`" — that is an
  inference from OPA's source, not something derivable from the bytes this
  module reads. What is stated is what the record says: the binary declares the
  result is not determined by the arguments, and a study executing
  model-authored code cannot admit that.
* **It does not fill `opa.capabilitiesSha256`.** The pin is null pre-freeze and
  `tests/test_pins.py` asserts it. Committing the artifact does not fill the
  pin; :func:`check_committed` is what binds the bytes until the freeze does.
* **It does not resolve `$OPA_CAPS`, and no gate in this study points at the
  committed file yet.** `Toolchain` reads the path from the environment and
  records a null pin as unenforced, which is the registered pre-freeze
  behaviour; making the committed file a default would change which suites run
  and is a wiring decision for the round that owns `engines.Toolchain`'s seat.
  :data:`REGISTERED_RELPATH` is where the registry says the file lives, and
  that is all this module asserts about it.
* **It does not touch `features`, `future_keywords` or `wasm_abi_versions`.**
  The registered denylist is over builtins. Those members are carried through
  by reference into a new document; `rego_v1` in particular is what makes
  section 2's v1 dialect pin meaningful, and a filter that quietly dropped it
  would change the language the arms are authoring in.
* **It does not fetch, repair or regenerate on read.** :func:`check_committed`
  compares and raises. A study whose sandbox regenerates itself when it fails to
  match cannot tell a pin from a suggestion.
* **It does not claim completeness.** A nondeterminism reachable through a
  builtin nobody denied would be invisible here. The canary establishes that the
  gate has power over the builtins on the list and says nothing about the ones
  that are not.

PROVENANCE. The rules, their `why` prose, the catch-all and its observed
over-denial were derived against this study's own pinned binary on the design
line that preceded the E4 pivot; they are re-measured here rather than trusted
(`tests/test_score_capabilities.py`'s pinned-binary section re-derives every one
against `$OPA_BIN`). This is NOT a port from another study: it names no source
digest and adds no row to `harness/PORTS.md`, whose registered destination set
is closed at seven.

ONE REGISTRATION GAP, RECORDED RATHER THAN PAPERED OVER. Section 2 names "the
registered denylist" and the phrase has no referent anywhere else in the
registered tree. `opa.capabilitiesDenylist` is that referent, added to the
registry so the nine words are pinned bytes rather than prose read out of a
sentence. It is a registry addition made before the freeze, and the reviewer
should decide whether section 2 should also name the nine words in place.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import sys
import tempfile

from . import engines

#: The study root, resolved from this file rather than from the caller's cwd.
STUDY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#: Study-relative path of the committed artifact, matching the registry's
#: `opa.capabilitiesPath`. `controls/` because that is where this study keeps
#: derived control artifacts (`controls/off-gold-equivalence.json`).
REGISTERED_RELPATH = "controls/opa-capabilities.json"

#: `opa capabilities --current` prints the capability set **of the running
#: binary**. Bare `opa capabilities` prints the list of historical version
#: names, which is a different thing entirely and would silently produce a file
#: with no builtins at all — checked against `opa capabilities --help` on the
#: pinned binary rather than recalled.
CAPABILITY_ARGV = ("capabilities", "--current")

#: The registered denylist, transcribed from `harness/PINS.json`'s
#: `opa.capabilitiesDenylist`. Order is the registry's.
REGISTERED_DENYLIST = (
    "clock",
    "network",
    "rand",
    "uuid",
    "opa.runtime",
    "print",
    "trace",
    "timezone-taking time forms",
    "net.cidr_expand",
)


class CapabilitiesError(Exception):
    """The capability set could not be derived, or is not what is committed."""


# ---------------------------------------------------------------------------
# Reading one builtin's capability record
# ---------------------------------------------------------------------------

def namespace(name):
    """The first dotted segment of a builtin name (`"time"` for `time.date`)."""
    return str(name).split(".")[0]


def leaf(name):
    """The last dotted segment (`"print"` for `internal.print`)."""
    return str(name).split(".")[-1]


def declared_args(record):
    """The builtin's declared argument list, or `()` when it declares none.

    A builtin with no `args` member is nullary — OPA omits the key rather than
    emitting an empty list — and a nullary function's result cannot be a
    function of anything the policy supplies. That is what the `clock` rule
    below reads."""
    decl = record.get("decl") or {}
    args = decl.get("args")
    return tuple(args) if isinstance(args, list) else ()


def takes_timezone(record):
    """Does any argument admit the `[ns, tz]` form?

    Derived from the declaration, not from the name. OPA declares the
    timezone-taking arguments as a union (`"type": "any"` with an `"of"` list)
    one branch of which is a **static** array whose first two members are a
    number and a string — the nanoseconds and the timezone name. The rule
    separates the forms correctly where a name-prefix rule would not:
    `time.clock`, `time.date`, `time.diff`, `time.format` and `time.weekday`
    match, and `time.add_date` — also in the `time` namespace, also taking
    nanoseconds — does not, because its arguments are plain numbers with no
    timezone branch."""
    for arg in declared_args(record):
        if not isinstance(arg, dict):
            continue
        for branch in arg.get("of") or ():
            if not isinstance(branch, dict) or branch.get("type") != "array":
                continue
            static = branch.get("static") or ()
            if len(static) < 2:
                continue
            first, second = static[0], static[1]
            if (isinstance(first, dict) and first.get("type") == "number"
                    and isinstance(second, dict)
                    and second.get("type") == "string"):
                return True
    return False


def is_nondeterministic(record):
    """Does the pinned binary itself declare this builtin nondeterministic?"""
    return record.get("nondeterministic") is True


# ---------------------------------------------------------------------------
# The denylist, as rules
# ---------------------------------------------------------------------------

#: One registered family. `registered` is the exact word from the registry, so
#: the mapping from prose to predicate is checkable in both directions; `why`
#: says what the rule reads and why that reading rather than a name list.
Family = collections.namedtuple("Family", "id registered why predicate")

FAMILIES = (
    Family(
        id="clock",
        registered="clock",
        why="a builtin in the `time` namespace that declares NO arguments can "
            "only be reading the wall clock: it has no input to be a function "
            "of. Derived from the declaration, so it does not depend on the "
            "name `now_ns` staying what it is.",
        predicate=lambda r: (namespace(r["name"]) == "time"
                             and not declared_args(r)),
    ),
    Family(
        id="network",
        registered="network",
        why="a builtin in the `http` or `net` namespace that the binary flags "
            "nondeterministic is one that leaves the process for its answer. "
            "The namespace alone would take the pure `net.cidr_*` predicates "
            "with it; the flag alone would take the JWT signers.",
        predicate=lambda r: (namespace(r["name"]) in ("http", "net")
                             and is_nondeterministic(r)),
    ),
    Family(
        id="rand",
        registered="rand",
        why="the whole `rand.` namespace. The registry names the family, not a "
            "builtin, and every member of a namespace called `rand` is by "
            "construction a thing this study must not let a policy read.",
        predicate=lambda r: namespace(r["name"]) == "rand",
    ),
    Family(
        id="uuid",
        registered="uuid",
        why="the whole `uuid.` namespace, on the same reading as `rand`. This "
            "removes `uuid.parse`, which is a deterministic parser and is "
            "denied anyway: the registry names the namespace, and a denylist "
            "that argues its way to a narrower reading is a denylist with a "
            "hole in it. The cost is a parser no spend-approval policy has a "
            "use for.",
        predicate=lambda r: namespace(r["name"]) == "uuid",
    ),
    Family(
        id="opa.runtime",
        registered="opa.runtime",
        why="registered as an exact builtin name rather than a family word, "
            "and matched as one. It returns the process's own configuration "
            "and environment — the operator's machine, read from inside a "
            "model-authored policy.",
        predicate=lambda r: r["name"] == "opa.runtime",
    ),
    Family(
        id="print",
        registered="print",
        why="the last dotted segment, which catches BOTH `print` and "
            "`internal.print`. Measured against the pinned binary: with "
            "`internal.print` restored and `print` removed, a policy calling "
            "`print(\"x\")` passes `opa check --strict` with exit 0, because "
            "the compiler lowers the call to `internal.print`. Denying the "
            "name the registry says and nothing else would have left the "
            "family working.",
        predicate=lambda r: leaf(r["name"]) == "print",
    ),
    Family(
        id="trace",
        registered="trace",
        why="the binary's own `tracing` category, so a tracing builtin added "
            "under another name is caught by the same rule.",
        predicate=lambda r: "tracing" in (r.get("categories") or ()),
    ),
    Family(
        id="timezone",
        registered="timezone-taking time forms",
        why="the `[ns, tz]` argument branch, read from the declaration. A "
            "timezone name is a lookup against the host's zone database, so "
            "the same policy on the same input can answer differently on two "
            "machines — which is the property `env -i` with `TZ=UTC` "
            "(`engines.clean_env`) is there to remove and this rule finishes.",
        predicate=takes_timezone,
    ),
    Family(
        id="net.cidr_expand",
        registered="net.cidr_expand",
        why="registered as an exact name, and not for nondeterminism: it "
            "expands a CIDR block to every host in it, so a `/8` in a "
            "model-authored policy is sixteen million allocations under the "
            "only bound this study registers over an evaluation, which is "
            "TIME — `engines.OPA_EVAL_TIMEOUT` and `engines.ENGINE_TIMEOUT_S`. "
            "This study registers NO memory bound (there is no `rlimit` or "
            "`ulimit` anywhere in the registered apparatus), so the cost is "
            "stated as allocation against the process the harness is sharing "
            "and not as a breach of a ceiling that does not exist.",
        predicate=lambda r: r["name"] == "net.cidr_expand",
    ),
)

#: The catch-all layer, separate from :data:`FAMILIES` because it implements no
#: single registry word. It denies every builtin the **pinned binary itself**
#: declares nondeterministic. The registered families clock / network / rand /
#: uuid / `opa.runtime` are five names for one property, and this reads that
#: property where the binary states it instead of inferring it from a name.
#:
#: It is deliberately a SUPERSET of the registered families and that over-denial
#: is recorded rather than hidden — see :data:`CATCH_ALL_ONLY_AT_PIN`. Denying
#: more than the registry names costs an author a builtin; denying less costs
#: the study the sandbox section 2's claim rests on.
CATCH_ALL = Family(
    id="nondeterministic",
    registered=None,
    why="the pinned binary's own `\"nondeterministic\": true` flag: its "
        "statement that the result is not a function of the arguments.",
    predicate=is_nondeterministic,
)

#: The builtins the catch-all removes that NO registered family word names,
#: **observed against the pinned binary** and pinned here so the over-denial is
#: a reviewed fact rather than a surprise. This is an observation, not a
#: definition: the rule is the flag, and if a different binary flagged forty
#: more builtins this constant would be wrong and the test that reads it would
#: say so. Nothing in the derivation consults it.
CATCH_ALL_ONLY_AT_PIN = (
    "io.jwt.decode_verify",
    "io.jwt.encode_sign",
    "io.jwt.encode_sign_raw",
)


def classify(record):
    """Every rule that denies `record`, in registered order, catch-all last.

    Empty means the builtin survives the filter."""
    if not isinstance(record, dict) or "name" not in record:
        raise CapabilitiesError(
            "a capability record must be an object with a `name`; got %r"
            % (record,))
    hits = [family.id for family in FAMILIES if family.predicate(record)]
    if CATCH_ALL.predicate(record):
        hits.append(CATCH_ALL.id)
    return tuple(hits)


# ---------------------------------------------------------------------------
# The derivation
# ---------------------------------------------------------------------------

#: What :func:`derive` hands back. `removals` maps builtin name -> the tuple of
#: rule ids that denied it, so every removed capability can be attributed to the
#: rule that removed it without re-running anything.
Derivation = collections.namedtuple("Derivation",
                                    "full filtered removals rendered")


def pinned_opa(pins, environ=None):
    """The pinned OPA binary's resolved path, hashed against `opa.assetSha256`.

    NOT `engines.Toolchain`, and the difference is the point: `Toolchain` is
    fail-closed over three seats at once, one of which is `$OPA_CAPS` — the file
    this module exists to produce. A generator that required its own output to
    already exist could never write it. What this resolves is the ONE seat whose
    bytes the derivation reads, and it enforces that seat exactly as `Toolchain`
    does: realpath first, then hash, then invoke the resolved path.

    The pin is enforced whether or not the freeze has happened; `opa.assetSha256`
    is a design-time resolution, not a freeze pin, and section 2 records that
    "the operator PATH binary is v0.10.0 and must never be invoked"."""
    environ = os.environ if environ is None else environ
    raw = environ.get("OPA_BIN")
    if not raw:
        raise CapabilitiesError(
            "OPA_BIN is unset and there is no default: the capability set is "
            "read out of the PINNED binary, and the operator's PATH holds a "
            "different version that must never be invoked "
            "(PREREGISTRATION.md section 2)")
    path = os.path.realpath(raw)
    if not os.path.isfile(path):
        raise CapabilitiesError("OPA_BIN names %s, which is not a file" % path)
    pin = (pins.get("opa") or {}).get("assetSha256")
    if not pin:
        raise CapabilitiesError(
            "harness/PINS.json records no opa.assetSha256; the derivation "
            "refuses to read an unpinned binary")
    observed = engines._digest(path)
    if observed != pin:
        raise CapabilitiesError(
            "opa.assetSha256 pins %s and the resolved file hashes to %s"
            % (pin, observed))
    return path


def capability_set(opa_path, workdir):
    """The pinned binary's own capability set, parsed.

    Runs through `engines._run()` — the module that owns every subprocess in
    this study's scoring path — so the derivation inherits the same scrubbed
    environment (`env -i`, `TZ=UTC`, `HOME`/`TMPDIR` inside `workdir`) and the
    same timeout as every other engine call. The output is parsed as JSON and
    nothing is read from the message prose."""
    try:
        code, out, err = engines._run([opa_path] + list(CAPABILITY_ARGV),
                                      workdir)
    except OSError as error:
        raise CapabilitiesError("`opa %s` could not be invoked: %s"
                                % (" ".join(CAPABILITY_ARGV), error))
    if code != 0:
        raise CapabilitiesError(
            "`opa %s` exited %d; stderr: %s"
            % (" ".join(CAPABILITY_ARGV), code, err[:500]))
    try:
        document = json.loads(out)
    except ValueError as error:
        raise CapabilitiesError(
            "`opa %s` did not emit JSON: %s"
            % (" ".join(CAPABILITY_ARGV), error))
    return document


def filter_capabilities(full):
    """Apply the denylist to a parsed capability document.

    Returns `(filtered_document, removals)`. The input is not modified: every
    other top-level member is carried through by reference into a new dict, and
    only `builtins` is rebuilt.

    Refuses rather than guesses when the document is not the shape the binary
    emits, because a shape change that silently produced an empty `builtins`
    list would produce a *maximally* restrictive file that passes every test in
    this module's suite except the survivor one."""
    if not isinstance(full, dict):
        raise CapabilitiesError("a capability document is an object, got %r"
                                % (type(full),))
    if not isinstance(full.get("builtins"), list):
        raise CapabilitiesError(
            "a capability document has a `builtins` list; this one has %r. "
            "Refusing rather than emitting a file with no builtins, which "
            "would be a sandbox that refuses everything and would look like a "
            "very effective filter." % (type(full.get("builtins")),))

    kept, removals = [], {}
    for record in full["builtins"]:
        hits = classify(record)
        if hits:
            removals[record["name"]] = hits
        else:
            kept.append(record)

    matched = set()
    for names in removals.values():
        matched.update(names)
    idle = [family.registered for family in FAMILIES
            if family.id not in matched]
    if idle:
        raise CapabilitiesError(
            "these registered denylist families matched NOTHING in the pinned "
            "binary's capability set: %s. A rule that matches nothing is not a "
            "filter that found nothing to remove; against this binary it is a "
            "rule that has stopped reading what it used to read." % (idle,))
    if not kept:
        raise CapabilitiesError(
            "the filter removed every builtin. A capability file with no "
            "builtins refuses every policy, including the canary, which would "
            "make the negative control pass for the wrong reason.")

    filtered = dict(full)
    filtered["builtins"] = kept
    return filtered, removals


def render(document):
    """The committed bytes: 2-space indent, sorted keys, one trailing newline.

    ASCII-escaped on purpose. The file is committed and digested, and a
    rendering whose bytes depend on the writer's locale or Python version is not
    a pin."""
    return (json.dumps(document, indent=2, sort_keys=True).encode("utf-8")
            + b"\n")


def derive(opa_path, workdir):
    """Read the pinned binary, apply the denylist, render the committed bytes."""
    full = capability_set(opa_path, workdir)
    filtered, removals = filter_capabilities(full)
    return Derivation(full=full, filtered=filtered, removals=removals,
                      rendered=render(filtered))


def catch_all_only(removals):
    """The removed builtins no registered family word names — the over-denial."""
    return tuple(sorted(name for name, hits in removals.items()
                        if tuple(hits) == (CATCH_ALL.id,)))


def digest(data):
    """sha256 of bytes, `sha256:`-prefixed — the registry's own digest form."""
    return "sha256:" + hashlib.sha256(data).hexdigest()


def committed_path(study=None):
    return os.path.join(study or STUDY, REGISTERED_RELPATH)


def committed_bytes(study=None):
    path = committed_path(study)
    if not os.path.isfile(path):
        raise CapabilitiesError(
            "%s is absent; generate it with `python3 -m e4lib.capabilities "
            "--write` from the harness directory, with OPA_BIN naming the "
            "pinned binary" % REGISTERED_RELPATH)
    with open(path, "rb") as handle:
        return handle.read()


def committed_document(study=None):
    return json.loads(committed_bytes(study).decode("utf-8"))


def check_committed(opa_path, workdir, study=None):
    """Re-derive and compare against the committed file, byte for byte.

    Returns the digest on success and raises on any difference. Byte equality
    rather than structural equality: the registry pins a digest over these
    bytes, so two documents that parse the same and render differently are a
    mismatch here as surely as they would be at the gate."""
    rendered = derive(opa_path, workdir).rendered
    committed = committed_bytes(study)
    if rendered != committed:
        raise CapabilitiesError(
            "%s is not what the pinned binary and the registered denylist "
            "derive.\n  derived   %s (%d bytes)\n  committed %s (%d bytes)\n"
            "Regenerate with `python3 -m e4lib.capabilities --write` and record "
            "the change; do NOT edit the file by hand."
            % (REGISTERED_RELPATH, digest(rendered), len(rendered),
               digest(committed), len(committed)))
    return digest(committed)


def write_full_capabilities(opa_path, workdir, name="caps-full.json"):
    """Render the binary's UNFILTERED set into `workdir`; return its path.

    The unfiltered arm of the canary needs a FILE, not an omitted flag: both
    arms must differ in exactly one thing — which capability file is named — or
    an accepted/refused split is an artefact of one arm passing
    `--capabilities` and the other not."""
    path = os.path.join(workdir, name)
    with open(path, "wb") as handle:
        handle.write(render(capability_set(opa_path, workdir)))
    return path


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def registry(study=None):
    path = os.path.join(study or STUDY, "harness", "PINS.json")
    with open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def _report(derivation):
    lines = ["derived from the pinned OPA binary's own capability set",
             "  builtins: %d full -> %d filtered (%d removed)"
             % (len(derivation.full["builtins"]),
                len(derivation.filtered["builtins"]),
                len(derivation.removals)),
             "  digest:   %s" % digest(derivation.rendered),
             "removed, with the rule that removed each:"]
    for name in sorted(derivation.removals):
        lines.append("  %-28s %s" % (name, ", ".join(derivation.removals[name])))
    lines.append("removed by the catch-all alone (no registered family word "
                 "names these): %s"
                 % (", ".join(catch_all_only(derivation.removals)) or "none",))
    return "\n".join(lines)


def main(argv):
    write = "--write" in argv[1:]
    opa_path = pinned_opa(registry())
    workdir = tempfile.mkdtemp(prefix="study019-caps-")
    derivation = derive(opa_path, workdir)
    print(_report(derivation))
    if write:
        with open(committed_path(), "wb") as handle:
            handle.write(derivation.rendered)
        print("wrote %s" % REGISTERED_RELPATH)
        print("opa.capabilitiesSha256 stays NULL: the freeze fills it, not this "
              "command.")
        return 0
    try:
        print("committed file matches, %s" % check_committed(opa_path, workdir))
    except CapabilitiesError as error:
        print(str(error))
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - the generator's own entry point
    sys.exit(main(sys.argv))
