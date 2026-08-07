#!/usr/bin/env python3
"""Run one arm x one backend over a set of instances and append JSONL results.

WHAT THIS FILE DOES
-------------------
::

    python run.py --arm A|Aprime|B --backend mock|anthropic|codex \\
                  --instances <dir-or-index.json> --trials N --seed S \\
                  --out <results>/<arm>-<backend>-<timestamp>.jsonl \\
                  [--limit N] [--dry-run]

One JSONL row per ``(instance, trial)``. The output file is **append-only** and
the run is **resumable**: rows already present for an ``(instance_id, trial)``
pair are skipped, so an interrupted run is finished by re-issuing the identical
command. A progress line goes to stderr; a summary goes to stdout.

Row schema (``schema: "jps-study-001-result/2"``)::

    instance_id, arm, backend, model, params, trial, seed,
    prediction {decision, cited_rules, reason, ...} | null,
    raw_text, parse_ok, parse_error, latency_ms, error,
    engine_returncode, engine_stderr,          # arm B only
    facts_sha256, prompt_sha256, harness_commit, harness_dirty, arm_config

``facts_sha256`` is the digest of the canonical gold-redacted facts document and
is the mechanical proof that all three arms saw the same bytes: the value for a
given ``instance_id`` must be identical across arms.

``/2`` differs from ``/1`` **only** by the two additive arm-B keys
``engine_returncode`` and ``engine_stderr``, which carry the runtime child
process's exit status (``null`` where no process completed) and its stderr
verbatim. They are absent from model-arm rows, which have no child process. No
``/1`` key was renamed or removed, so ``/1`` files stay parseable by everything
that parses ``/2`` --- ``score.py`` does not consult the schema string at all.
The keys exist so that an arm-B "0 engine refusals" claim can be audited from the
retained JSONL instead of being trusted; before them, the rows kept no refusal
signal whatsoever (``DEVIATIONS.md`` sections 3 and 4).

**Parseable is not comparable, and for arm B the two vintages are not the same
measurement.** The same change tightened the arm-B refusal rule: a ``/1`` arm-B
row could record a non-zero exit that printed an envelope as a *success*, and a
``/2`` row records it as a refusal. Pooling the two would give one file two
definitions of ``engine_refusal_rate``, and nothing downstream could tell them
apart, so **resuming refuses**: appending arm-B rows to a file that already holds
arm-B rows of a different ``schema`` is an error, not a warning
(``assert_uniform_arm_b_vintage``). Arm B is deterministic and its last full-corpus
run at k = 5 is recorded at 37 seconds (``DEVIATIONS.md`` section 1), so the
remedy is to re-run it into a fresh ``--out`` rather than to mix. Model arms are
unaffected: their ``/1`` and ``/2`` rows carry identical keys and identical
meanings, and they resume across the boundary.

DETERMINISM
-----------
Rows carry no wall-clock timestamp and the mock backend synthesises its own
latency, so two mock runs of the same command produce byte-identical files. The
only timestamp in the system is the one the operator puts in the output filename.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
* No scoring. It records what happened; ``score.py`` decides what it means.
* No retry-until-parseable and no fallback backend. A malformed reply and an
  engine refusal are both recorded as data.
* No concurrency, no batching, no caching of model responses.
* No mutation of the instance set. The RuleArena checkout is read-only and the
  facts documents are read, never rewritten.

Python 3.10+ (``from __future__ import annotations`` keeps it importable on 3.8).
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import arms  # noqa: E402
import arm_b  # noqa: E402
import backends  # noqa: E402

SCHEMA = "jps-study-001-result/2"
STUDY_ROOT = os.path.dirname(HERE)
DEFAULT_POLICY = os.path.join(
    STUDY_ROOT, "rulearena", "checkout", "nba", "reference_rules.txt")
DEFAULT_RULE_CATALOG = os.path.join(
    STUDY_ROOT, "rulearena", "checkout", "nba", "micro_evaluation.py")

ROW_KEYS = (
    "schema", "row_id", "instance_id", "variant", "arm", "backend", "model", "params", "trial", "seed",
    "prediction", "raw_text", "parse_ok", "parse_error", "latency_ms", "error",
    # Arm B only. ``write_row`` emits a key only when the row carries it, so
    # model-arm rows are unchanged by their presence here.
    "engine_returncode", "engine_stderr",
    "facts_sha256", "prompt_sha256", "harness_commit", "harness_dirty", "arm_config",
)


# --------------------------------------------------------------------------- #
# Instance loading
# --------------------------------------------------------------------------- #


def _validate_instance(obj: Any, origin: str) -> Dict[str, Any]:
    if not isinstance(obj, dict):
        raise ValueError("%s: instance is not a JSON object" % origin)
    for key in ("instance_id", "facts"):
        if key not in obj:
            raise ValueError("%s: instance is missing required key %r" % (origin, key))
    if not isinstance(obj["instance_id"], str):
        raise ValueError("%s: instance_id must be a string" % origin)
    return obj


def load_instances(path: str) -> List[Dict[str, Any]]:
    """Load instances from a directory of ``*.json`` files or from an index file.

    An index file may be a JSON array of instance objects, a JSON array of paths
    (absolute, or relative to the index file), or an object with an
    ``"instances"`` key holding either of those. Directory loading is sorted by
    filename so the run order is deterministic.
    """
    if os.path.isdir(path):
        out: List[Dict[str, Any]] = []
        for name in sorted(os.listdir(path)):
            if not name.endswith(".json"):
                continue
            # Pipeline stages write a sidecar manifest/index beside their
            # instances; it describes the run, it is not an instance.
            if name in ("manifest.json", "index.json"):
                continue
            full = os.path.join(path, name)
            with open(full, "r", encoding="utf-8") as fh:
                out.append(_validate_instance(json.load(fh), full))
        if not out:
            raise ValueError("no *.json instance files found in %s" % path)
        return out

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "instances" in data:
        data = data["instances"]
    if not isinstance(data, list):
        raise ValueError("%s: expected a JSON array (or an object with 'instances')" % path)

    base = os.path.dirname(os.path.abspath(path))
    out = []
    for entry in data:
        if isinstance(entry, str):
            full = entry if os.path.isabs(entry) else os.path.join(base, entry)
            with open(full, "r", encoding="utf-8") as fh:
                out.append(_validate_instance(json.load(fh), full))
        else:
            out.append(_validate_instance(entry, path))
    if not out:
        raise ValueError("%s: index contains no instances" % path)
    return out


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #


def harness_git_state() -> Tuple[str, bool]:
    """Return ``(commit, dirty)`` for the harness working tree."""
    try:
        commit = subprocess.run(  # noqa: S603
            ["git", "-C", HERE, "rev-parse", "HEAD"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=15,
        )
        if commit.returncode != 0:
            return ("unknown", False)
        sha = commit.stdout.decode().strip()
        status = subprocess.run(  # noqa: S603
            ["git", "-C", HERE, "status", "--porcelain", "--", HERE],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=15,
        )
        dirty = bool(status.stdout.decode().strip())
        return (sha, dirty)
    except (OSError, subprocess.SubprocessError):
        return ("unknown", False)


# --------------------------------------------------------------------------- #
# Resume
# --------------------------------------------------------------------------- #


def _iter_existing_rows(out_path: str) -> Iterable[Dict[str, Any]]:
    """Yield the rows of an existing results file; nothing when it does not exist.

    A line that is not valid JSON raises rather than being skipped: the file is
    about to be appended to, and a corrupt one must not be extended.
    """
    if not os.path.exists(out_path):
        return
    with open(out_path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                raise ValueError(
                    "%s line %d is not valid JSON; refusing to append to a corrupt "
                    "results file" % (out_path, lineno)
                )
            yield row


def existing_keys(out_path: str) -> set:
    """Return the ``(instance_id, trial)`` pairs already present in the file."""
    done = set()
    for row in _iter_existing_rows(out_path):
        done.add((row.get("row_id") or row.get("instance_id"), row.get("trial")))
    return done


def arm_b_schema_vintages(out_path: str) -> set:
    """Return the distinct ``schema`` strings of the arm-B rows already in a file.

    Arm B only, because arm B is the only arm whose row *meaning* changed with the
    schema: a ``jps-study-001-result/1`` arm-B row was written under a refusal rule
    that could score a non-zero exit as a success. Model-arm rows are identical
    across the two versions and are not looked at.
    """
    return {str(row.get("schema"))
            for row in _iter_existing_rows(out_path)
            if row.get("arm") == "B"}


def assert_uniform_arm_b_vintage(out_path: str, arm: str) -> None:
    """Refuse to append arm-B rows beside arm-B rows of another refusal vintage.

    Resuming keys on ``(row_id, trial)`` and cannot see this: the rows it would
    skip and the rows it would write are the same measurement only if they were
    scored by the same refusal rule. Raises ``ValueError`` when they were not; a
    no-op for the model arms and for a file with no arm-B rows in it.
    """
    if arm != "B":
        return
    stale = arm_b_schema_vintages(out_path) - {SCHEMA}
    if not stale:
        return
    raise ValueError(
        "%s already holds arm-B rows written under schema %s, and this run writes "
        "%s. The arm-B refusal rule differs between them --- a '/1' row could "
        "score a non-zero exit that printed an envelope as a success, a '/2' row "
        "records it as a refusal --- so the two vintages are not the same "
        "measurement and one file cannot carry both: every rate computed over it "
        "would silently mix two definitions. Arm B is deterministic; re-run the "
        "whole arm into a fresh --out instead of resuming this file."
        % (out_path, ", ".join(sorted(stale)), SCHEMA))


def write_row(handle, row: Mapping[str, Any]) -> None:
    ordered = {key: row[key] for key in ROW_KEYS if key in row}
    handle.write(json.dumps(ordered, ensure_ascii=False) + "\n")
    handle.flush()


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run.py",
        description="Run one arm x one backend over the study instance set.",
    )
    p.add_argument("--arm", required=True, choices=["A", "Aprime", "B"])
    p.add_argument("--backend", required=True, choices=["mock", "anthropic", "codex"])
    p.add_argument("--instances", required=True,
                   help="directory of *.json instance documents, or an index.json")
    p.add_argument("--trials", type=int, default=1, help="repeated trials per instance")
    p.add_argument("--seed", type=int, default=0,
                   help="base seed; trial t uses seed+t and it is recorded per row")
    p.add_argument("--out", required=True, help="append-only JSONL results path")
    p.add_argument("--limit", type=int, default=None,
                   help="use only the first N instances (after sorting)")
    p.add_argument("--dry-run", action="store_true",
                   help="build everything and report, but call no backend and write nothing")

    p.add_argument("--policy", default=DEFAULT_POLICY,
                   help="arm A: path to the verbatim policy text")
    p.add_argument("--pack-prose", default=None,
                   help="arm Aprime: path to the pack's semantic content as prose (required)")
    p.add_argument("--pack", default=None,
                   help="arm B: path to the judgment pack (required)")
    p.add_argument("--evidence-dir", default=None,
                   help="arm B: directory of <instance_id>.json evidence files")
    p.add_argument("--outcome-map", default=None,
                   help="arm B: JSON {outcomeId: legal|illegal|cannot_decide}")
    p.add_argument("--facts-root", default="instance", choices=["instance", "facts"],
                   help="arm B: hand the runtime the whole instance document (default) "
                        "or only its 'facts' sub-object")
    p.add_argument("--supported-extension", action="append", default=[],
                   help="arm B: repeatable, passed through to the runtime")
    p.add_argument("--judgment-pack-cli", default="judgment-pack")

    p.add_argument("--rule-catalog", default=DEFAULT_RULE_CATALOG,
                   help="rule identifier vocabulary: RuleArena micro_evaluation.py "
                        "or a JSON object/array. Pass 'none' to omit.")
    p.add_argument("--no-gold-vocabulary", action="store_true",
                   help="do not extend the rule vocabulary with identifiers observed "
                        "in the instance set's gold relevant_rules")

    p.add_argument("--model", default=None, help="model identifier for the backend")
    p.add_argument("--max-tokens", type=int, default=4096)
    p.add_argument("--temperature", type=float, default=None,
                   help="omitted by default; current Opus/Sonnet 5 models reject it")
    p.add_argument("--effort", default=None, choices=[None, "low", "medium", "high",
                                                      "xhigh", "max"])
    p.add_argument("--thinking", default=None, choices=[None, "adaptive", "disabled"])
    p.add_argument("--timeout", type=float, default=600.0)
    return p


def _gold_rule_ids(instances: Iterable[Mapping[str, Any]]) -> List[str]:
    seen: Dict[str, None] = {}
    for inst in instances:
        gold = inst.get("gold") or {}
        for rule_id in gold.get("relevant_rules") or []:
            if isinstance(rule_id, str):
                seen.setdefault(rule_id, None)
    return sorted(seen)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.trials < 1:
        print("--trials must be >= 1", file=sys.stderr)
        return 2

    instances = load_instances(args.instances)
    instances.sort(key=lambda i: i["instance_id"])

    # ---- rule vocabulary -------------------------------------------------- #
    # Built from the WHOLE instance set, before --limit is applied, so that the
    # vocabulary -- and therefore every prompt -- is identical whether the run is
    # a 10-instance smoke test, a resumed partial run, or the full 216.
    catalog: Dict[str, str] = {}
    if args.rule_catalog and args.rule_catalog.lower() != "none":
        catalog = arms.load_rule_catalog(args.rule_catalog)
    if not args.no_gold_vocabulary:
        catalog = arms.merge_rule_vocabulary(catalog, _gold_rule_ids(instances))

    if args.limit is not None:
        instances = instances[: args.limit]

    # ---- arm-specific inputs ---------------------------------------------- #
    policy_text = ""
    pack_prose = ""
    b_config: Optional[arm_b.ArmBConfig] = None
    arm_config: Dict[str, Any] = {"rule_vocabulary_size": len(catalog)}

    if args.arm == "A":
        with open(args.policy, "r", encoding="utf-8") as fh:
            policy_text = fh.read()
        arm_config["policy_path"] = args.policy
        arm_config["policy_sha256"] = _sha256_text(policy_text)
    elif args.arm == "Aprime":
        if not args.pack_prose:
            print("--pack-prose is required for --arm Aprime", file=sys.stderr)
            return 2
        with open(args.pack_prose, "r", encoding="utf-8") as fh:
            pack_prose = fh.read()
        arm_config["pack_prose_path"] = args.pack_prose
        arm_config["pack_prose_sha256"] = _sha256_text(pack_prose)
    else:  # arm B
        if not args.pack:
            print("--pack is required for --arm B", file=sys.stderr)
            return 2
        outcome_map: Dict[str, str] = {}
        if args.outcome_map:
            with open(args.outcome_map, "r", encoding="utf-8") as fh:
                outcome_map = {str(k): str(v) for k, v in json.load(fh).items()}
        b_config = arm_b.ArmBConfig(
            args.pack,
            cli=args.judgment_pack_cli,
            outcome_map=outcome_map,
            supported_extensions=args.supported_extension,
            facts_root=args.facts_root,
            evidence_dir=args.evidence_dir,
            timeout_s=args.timeout,
        )
        arm_config.update(b_config.describe())
        with open(args.pack, "rb") as bfh:
            arm_config["pack_sha256"] = _sha256_bytes(bfh.read())

    # ---- backend ----------------------------------------------------------- #
    # Arm B does not call a language model. The --backend flag is still recorded
    # so that arm-B rows join cleanly with the model arms in a paired analysis,
    # but the model identifier is the runtime, not a model.
    backend: Optional[backends.Backend] = None
    if args.arm == "B":
        model_id = "judgment-pack-runtime"
        backend_name = args.backend
        params: Dict[str, Any] = {"note": "arm B calls the runtime, not a model"}
        params.update(b_config.describe() if b_config else {})
    else:
        try:
            backend = backends.make_backend(
                args.backend,
                rule_ids=sorted(catalog) if catalog else None,
                model=args.model,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                effort=args.effort,
                thinking=args.thinking,
                timeout_s=args.timeout,
            )
        except backends.BackendError as exc:
            print("backend error: %s" % exc, file=sys.stderr)
            return 2
        described = backend.describe()
        backend_name = described["backend"]
        model_id = described["model"]
        params = described["params"]

    commit, dirty = harness_git_state()

    # ---- resume guard ------------------------------------------------------ #
    # Checked before the dry run as well: a plan that cannot legally be appended
    # is not a plan an operator should be shown a row count for.
    try:
        assert_uniform_arm_b_vintage(args.out, args.arm)
    except ValueError as exc:
        print("refusing to resume: %s" % exc, file=sys.stderr)
        return 2

    # ---- dry run ----------------------------------------------------------- #
    if args.dry_run:
        return _dry_run(args, instances, catalog, policy_text, pack_prose,
                        backend_name, model_id, params, b_config)

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    done = existing_keys(args.out)
    planned = len(instances) * args.trials
    skipped = 0
    written = 0
    counts = {"parse_ok": 0, "parse_fail": 0, "error": 0}
    decisions: Dict[str, int] = {}

    with open(args.out, "a", encoding="utf-8") as handle:
        for index, instance in enumerate(instances):
            # Key rows by twin_id where the instance set is redaction twins:
            # the answerable and redacted twins of one instance share an
            # instance_id, so keying by that would collide them and silently
            # destroy the paired analysis (and the resume check).
            instance_id = instance.get("twin_id") or instance["instance_id"]
            fsha = arms.facts_sha256(instance)
            for trial in range(1, args.trials + 1):
                if (instance_id, trial) in done:
                    skipped += 1
                    continue
                seed = args.seed + trial - 1
                row = _execute(
                    arm=args.arm, instance=instance, trial=trial, seed=seed,
                    backend=backend, backend_name=backend_name, model_id=model_id,
                    params=params, catalog=catalog, policy_text=policy_text,
                    pack_prose=pack_prose, b_config=b_config, facts_sha=fsha,
                    commit=commit, dirty=dirty, arm_config=arm_config,
                )
                write_row(handle, row)
                written += 1
                if row["parse_ok"]:
                    counts["parse_ok"] += 1
                    decision = (row["prediction"] or {}).get("decision", "?")
                    decisions[decision] = decisions.get(decision, 0) + 1
                else:
                    counts["parse_fail"] += 1
                if row["error"]:
                    counts["error"] += 1
                sys.stderr.write(
                    "\r[%s/%s] %d/%d instances  written=%d skipped=%d "
                    "parse_ok=%d parse_fail=%d error=%d   "
                    % (args.arm, backend_name, index + 1, len(instances),
                       written, skipped, counts["parse_ok"], counts["parse_fail"],
                       counts["error"])
                )
                sys.stderr.flush()
    sys.stderr.write("\n")

    print("run complete")
    print("  arm            : %s" % args.arm)
    print("  backend        : %s" % backend_name)
    print("  model          : %s" % model_id)
    print("  instances      : %d" % len(instances))
    print("  trials         : %d" % args.trials)
    print("  rows planned   : %d" % planned)
    print("  rows written   : %d" % written)
    print("  rows skipped   : %d (already present -- resumed)" % skipped)
    print("  parse ok       : %d" % counts["parse_ok"])
    print("  parse failures : %d" % counts["parse_fail"])
    print("  errors         : %d" % counts["error"])
    if decisions:
        print("  decisions      : %s"
              % ", ".join("%s=%d" % kv for kv in sorted(decisions.items())))
    print("  output         : %s" % args.out)
    print("  harness commit : %s%s" % (commit, " (dirty)" if dirty else ""))
    return 0


def _execute(*, arm: str, instance: Mapping[str, Any], trial: int, seed: int,
             backend: Optional[backends.Backend], backend_name: str, model_id: str,
             params: Mapping[str, Any], catalog: Mapping[str, str],
             policy_text: str, pack_prose: str,
             b_config: Optional[arm_b.ArmBConfig], facts_sha: str,
             commit: str, dirty: bool, arm_config: Mapping[str, Any]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "schema": SCHEMA,
        # Row identity is the twin where one exists: the answerable and redacted
        # twins share an instance_id, and collapsing them would destroy the
        # paired analysis. instance_id is kept alongside so twins can be paired.
        "row_id": instance.get("twin_id") or instance["instance_id"],
        "instance_id": instance["instance_id"],
        "variant": instance.get("variant"),
        "arm": arm,
        "backend": backend_name,
        "model": model_id,
        "params": dict(params),
        "trial": trial,
        "seed": seed,
        "facts_sha256": facts_sha,
        "harness_commit": commit,
        "harness_dirty": dirty,
        "arm_config": dict(arm_config),
    }

    if arm == "B":
        assert b_config is not None
        result = arm_b.evaluate_instance(instance, b_config)
        row.update({
            "prediction": result["prediction"],
            "raw_text": result["raw_text"],
            "parse_ok": bool(result["ok"]),
            "parse_error": None if result["ok"] else result["error"],
            "latency_ms": result["latency_ms"],
            "error": result["error"],
            # Retained on every arm-B row, refusal or not: a refusal *rate* is
            # only auditable if the non-refusals are on the record too.
            "engine_returncode": result["returncode"],
            "engine_stderr": result["stderr"],
            "prompt_sha256": None,
        })
        return row

    if arm == "A":
        system, user = arms.build_prompt_A(instance, policy_text, rule_catalog=catalog)
    else:
        system, user = arms.build_prompt_Aprime(instance, pack_prose, rule_catalog=catalog)

    assert backend is not None
    completion = backend.complete(system, user, seed=seed)
    parsed = arms.parse_prediction(completion["text"])
    row.update({
        "prediction": parsed.prediction,
        "raw_text": completion["text"],
        "parse_ok": parsed.ok,
        "parse_error": parsed.error,
        "latency_ms": completion["latency_ms"],
        "error": completion["error"],
        "prompt_sha256": arms.prompt_sha256(system, user),
    })
    return row


def _dry_run(args, instances, catalog, policy_text, pack_prose,
             backend_name, model_id, params, b_config) -> int:
    print("DRY RUN -- no backend called, nothing written")
    print("  arm            : %s" % args.arm)
    print("  backend        : %s" % backend_name)
    print("  model          : %s" % model_id)
    print("  params         : %s" % json.dumps(params, sort_keys=True, default=str))
    print("  instances      : %d" % len(instances))
    print("  trials         : %d" % args.trials)
    print("  rows planned   : %d" % (len(instances) * args.trials))
    print("  rule vocabulary: %d identifiers" % len(catalog))
    print("  would write to : %s" % args.out)
    already = existing_keys(args.out) if os.path.exists(args.out) else set()
    if already:
        print("  already present: %d rows (would be skipped)" % len(already))
    first = instances[0]
    print("  first instance : %s" % first["instance_id"])
    print("  facts sha256   : %s" % arms.facts_sha256(first))
    if args.arm == "B":
        print("  arm B config   : %s"
              % json.dumps(b_config.describe(), sort_keys=True, default=str))
    else:
        if args.arm == "A":
            system, user = arms.build_prompt_A(first, policy_text, rule_catalog=catalog)
        else:
            system, user = arms.build_prompt_Aprime(first, pack_prose, rule_catalog=catalog)
        print("  prompt sha256  : %s" % arms.prompt_sha256(system, user))
        print("  prompt chars   : system=%d user=%d" % (len(system), len(user)))
    return 0


def _sha256_text(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_bytes(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
