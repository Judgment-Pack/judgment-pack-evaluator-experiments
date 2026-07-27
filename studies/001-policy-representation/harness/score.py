#!/usr/bin/env python3
"""Score study-001 result JSONL files with a paired, instance-level design.

WHAT THIS FILE DOES
-------------------
::

    python score.py --instances <dir-or-index.json> --results a.jsonl b.jsonl ... \\
                    [--baseline "A::mock::mock/deterministic-v1"] \\
                    [--out-md report.md] [--out-json report.json] \\
                    [--bootstrap 2000] [--seed 20260727]

Reads one or more result files, groups rows into **conditions**
(``arm::backend::model`` --- a ``::`` separator, because model identifiers
themselves contain slashes), restricts every condition to the **intersection** of
the instance ids they all cover, and reports, for each condition:

* **accuracy** against gold, macro-averaged over instances (each instance
  contributes the mean of its trials, so an instance with more trials does not
  get more weight);
* **pass^k consistency** --- the probability that *all* k trials on an instance are
  correct. A model that is right on average but flips between runs is penalised
  here and nowhere else;
* **citation precision / recall / F1** against the gold ``relevant_rules`` set,
  reported both macro (per-instance mean) and micro (pooled counts);
* **escalation precision, recall and F1** on the redacted twins, from the full
  ``should-escalate x did-escalate`` 2x2 --- never recall alone, because an
  always-escalate agent achieves recall 1.0 and must be visibly punished for it
  by precision;
* **parse-failure rate** and, for arm B, **engine-refusal rate**.

Uncertainty comes from a **paired bootstrap**: instances are resampled with
replacement, the *same* resample is applied to every condition, and every metric
plus every baseline-relative difference is recomputed. Percentile intervals are
reported. ``random.Random`` with a fixed seed; the same inputs give the same
numbers.

SCORING CONVENTIONS (fixed here, so they cannot drift between analyses)
-----------------------------------------------------------------------
* Gold decision is ``"illegal"`` when ``gold.answer`` is true, ``"legal"`` when it
  is false, and ``"cannot_decide"`` for a redacted twin --- on a redacted
  instance, abstaining *is* the right answer.
* A **parse failure is a wrong answer** and is **not** an escalation. It is also
  counted separately so a condition cannot hide behind unparseable output.
* An **arm-B engine refusal** is likewise a wrong, non-escalating answer, per the
  preregistered rule.
* ``cited_rules`` is compared as a **set** after normalisation to lowercase
  alphanumerics. RuleArena's gold column spells a handful of identifiers
  inconsistently (``nontaxpayer_...`` vs ``non_taxpayer_...``); normalising means
  the citation metric measures rule identification, not spelling. Instances whose
  gold carries no ``relevant_rules`` are excluded from citation metrics only.
* Empty-vs-empty citation sets score 1.0; predicting a non-empty set against an
  empty gold scores precision 0.0.
* ``pass^k`` uses the first k trials in trial order, where k is the smallest trial
  count any condition has for that instance, so the comparison is like for like.

REDACTED-TWIN DETECTION (the contract this file consumes)
----------------------------------------------------------
An instance should escalate when, in priority order:

1. ``gold.should_escalate`` is a boolean --- that value wins;
2. ``variant`` is ``"redacted"`` / ``"answerable"`` --- ``redact.py``'s own label,
   which is authoritative because it stamps a ``redaction`` record into **both**
   twins of a pair (the answerable twin records what its counterpart lost);
3. ``expected_decision == "cannot_decide"``;
4. ``instance["redaction"]["applied"]`` is true, or, for documents that predate
   that key, ``instance["redaction"]`` is present and truthy;
5. the ``instance_id`` ends with ``#redacted`` / ``-redacted`` or contains
   ``#redacted-``.

Its non-redacted partner is ``pair_id`` when present, else
``redaction.base_instance_id``, else the id with that suffix stripped. Every other
instance is a should-NOT-escalate case and is included in the 2x2, which is what
makes always-escalate score badly.

INSTANCE IDENTITY
-----------------
``redact.py`` gives the two twins of a pair the **same** ``instance_id`` --- they
are the same problem --- and tells them apart with ``twin_id``. Rows and
instances are therefore keyed by ``twin_id`` when it is present (``arms.
instance_key``), matching the ``row_id`` that ``run.py`` writes. Keying on
``instance_id`` would collapse each pair into one instance and silently destroy
the escalation design.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
* No unpaired comparisons and no "best of the trials". Conditions are only ever
  compared on the shared instance set.
* No recall-only escalation number, anywhere.
* No significance test beyond the bootstrap interval and the bootstrap
  probability that a difference exceeds zero. No p-value dressing.
* No repair of malformed rows, no imputation of missing trials.

Python 3.10+ (``from __future__ import annotations`` keeps it importable on 3.8).
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from arms import instance_key  # noqa: E402
from run import load_instances  # noqa: E402

DECISIONS = ("legal", "illegal", "cannot_decide")
_NORM_RE = re.compile(r"[^a-z0-9]+")
_REDACTED_SUFFIXES = ("#redacted", "-redacted")


# --------------------------------------------------------------------------- #
# Gold / redaction contract
# --------------------------------------------------------------------------- #


def should_escalate(instance: Mapping[str, Any]) -> bool:
    gold = instance.get("gold") or {}
    if isinstance(gold.get("should_escalate"), bool):
        return bool(gold["should_escalate"])
    variant = instance.get("variant")
    if variant == "redacted":
        return True
    if variant == "answerable":
        return False
    if instance.get("expected_decision") == "cannot_decide":
        return True
    redaction = instance.get("redaction")
    if isinstance(redaction, Mapping) and isinstance(redaction.get("applied"), bool):
        return bool(redaction["applied"])
    if redaction:
        return True
    iid = str(instance.get("instance_id", ""))
    if any(iid.endswith(sfx) for sfx in _REDACTED_SUFFIXES):
        return True
    return "#redacted-" in iid


def base_instance_id(instance: Mapping[str, Any]) -> str:
    iid = str(instance.get("instance_id", ""))
    if isinstance(instance.get("pair_id"), str) and instance["pair_id"]:
        return instance["pair_id"]
    redaction = instance.get("redaction")
    if isinstance(redaction, Mapping) and isinstance(redaction.get("base_instance_id"), str):
        return redaction["base_instance_id"]
    for sfx in _REDACTED_SUFFIXES:
        if iid.endswith(sfx):
            return iid[: -len(sfx)]
    if "#redacted-" in iid:
        return iid.split("#redacted-", 1)[0]
    return iid


def gold_decision(instance: Mapping[str, Any]) -> Optional[str]:
    if should_escalate(instance):
        return "cannot_decide"
    gold = instance.get("gold") or {}
    answer = gold.get("answer")
    if isinstance(answer, bool):
        return "illegal" if answer else "legal"
    if isinstance(gold.get("decision"), str) and gold["decision"] in DECISIONS:
        return gold["decision"]
    return None


def gold_rules(instance: Mapping[str, Any]) -> Optional[set]:
    gold = instance.get("gold") or {}
    rules = gold.get("relevant_rules")
    if not isinstance(rules, list):
        return None
    return {normalise_rule_id(r) for r in rules if isinstance(r, str)}


def normalise_rule_id(rule_id: str) -> str:
    return _NORM_RE.sub("", rule_id.lower())


# --------------------------------------------------------------------------- #
# Result loading
# --------------------------------------------------------------------------- #


def condition_key(row: Mapping[str, Any]) -> str:
    return "%s::%s::%s" % (row.get("arm"), row.get("backend"), row.get("model"))


def load_results(paths: Sequence[str]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """Return ``{condition: {row_id: [rows sorted by trial]}}``.

    Rows are keyed by ``row_id`` (``run.py``'s twin-aware identity) and fall back
    to ``instance_id`` for documents that are not twins.
    """
    out: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for path in paths:
        with open(path, "r", encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError as exc:
                    raise ValueError("%s line %d: %s" % (path, lineno, exc))
                cond = condition_key(row)
                iid = row.get("row_id") or row.get("instance_id")
                if not isinstance(iid, str):
                    raise ValueError("%s line %d: missing row_id/instance_id" % (path, lineno))
                out.setdefault(cond, {}).setdefault(iid, []).append(row)
    for by_instance in out.values():
        for rows in by_instance.values():
            rows.sort(key=lambda r: r.get("trial", 0))
    return out


# --------------------------------------------------------------------------- #
# Per-instance sufficient statistics
# --------------------------------------------------------------------------- #


class InstanceStats:
    """Everything a metric needs from one (condition, instance), precomputed.

    Keeping the bootstrap on these aggregates rather than on raw rows makes 2000
    replicates over 216 instances cheap and, more importantly, guarantees that the
    resample is at the *instance* level --- the paired unit of the design.
    """

    __slots__ = ("k", "n_correct", "all_correct", "n_parse_ok", "n_engine_refusal",
                 "cite_precision", "cite_recall", "cite_f1", "has_citation_gold",
                 "cite_tp", "cite_pred", "cite_gold",
                 "esc_tp", "esc_fp", "esc_fn", "esc_tn")

    def __init__(self) -> None:
        self.k = 0
        self.n_correct = 0
        self.all_correct = False
        self.n_parse_ok = 0
        self.n_engine_refusal = 0
        self.cite_precision = 0.0
        self.cite_recall = 0.0
        self.cite_f1 = 0.0
        self.has_citation_gold = False
        self.cite_tp = 0
        self.cite_pred = 0
        self.cite_gold = 0
        self.esc_tp = 0
        self.esc_fp = 0
        self.esc_fn = 0
        self.esc_tn = 0


def _prf(pred: set, gold: set) -> Tuple[float, float, float]:
    tp = len(pred & gold)
    if not pred and not gold:
        return (1.0, 1.0, 1.0)
    precision = tp / len(pred) if pred else 0.0
    recall = tp / len(gold) if gold else 1.0
    f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
    return (precision, recall, f1)


def compute_instance_stats(rows: Sequence[Mapping[str, Any]],
                           instance: Mapping[str, Any],
                           k: int) -> InstanceStats:
    stats = InstanceStats()
    stats.k = k
    target = gold_decision(instance)
    g_rules = gold_rules(instance)
    stats.has_citation_gold = g_rules is not None
    escalate_expected = should_escalate(instance)

    p_sum = r_sum = f_sum = 0.0
    all_correct = True
    for row in rows[:k]:
        parse_ok = bool(row.get("parse_ok"))
        prediction = row.get("prediction") if parse_ok else None
        decision = (prediction or {}).get("decision")
        correct = bool(parse_ok and target is not None and decision == target)
        stats.n_correct += int(correct)
        all_correct = all_correct and correct
        stats.n_parse_ok += int(parse_ok)
        error = row.get("error") or ""
        if isinstance(error, str) and (error.startswith("engine-refusal")
                                       or error.startswith("outcome-map-failure")):
            stats.n_engine_refusal += 1

        if g_rules is not None:
            pred_rules = set()
            if parse_ok:
                pred_rules = {normalise_rule_id(x)
                              for x in (prediction or {}).get("cited_rules", [])
                              if isinstance(x, str)}
            precision, recall, f1 = _prf(pred_rules, g_rules)
            p_sum += precision
            r_sum += recall
            f_sum += f1
            stats.cite_tp += len(pred_rules & g_rules)
            stats.cite_pred += len(pred_rules)
            stats.cite_gold += len(g_rules)

        did_escalate = bool(parse_ok and decision == "cannot_decide")
        if escalate_expected and did_escalate:
            stats.esc_tp += 1
        elif (not escalate_expected) and did_escalate:
            stats.esc_fp += 1
        elif escalate_expected and (not did_escalate):
            stats.esc_fn += 1
        else:
            stats.esc_tn += 1

    stats.all_correct = all_correct and k > 0
    if k and g_rules is not None:
        stats.cite_precision = p_sum / k
        stats.cite_recall = r_sum / k
        stats.cite_f1 = f_sum / k
    return stats


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #


def aggregate(stats_by_instance: Mapping[str, InstanceStats],
              instance_ids: Sequence[str]) -> Dict[str, float]:
    """Aggregate per-instance stats over a (possibly resampled) list of ids."""
    n = len(instance_ids)
    if n == 0:
        return {}
    acc = pass_k = parse_ok = refusal = 0.0
    cp = cr = cf = 0.0
    cite_n = 0
    tp_sum = pred_sum = gold_sum = 0
    e_tp = e_fp = e_fn = e_tn = 0
    for iid in instance_ids:
        s = stats_by_instance[iid]
        acc += (s.n_correct / s.k) if s.k else 0.0
        pass_k += 1.0 if s.all_correct else 0.0
        parse_ok += (s.n_parse_ok / s.k) if s.k else 0.0
        refusal += (s.n_engine_refusal / s.k) if s.k else 0.0
        if s.has_citation_gold:
            cite_n += 1
            cp += s.cite_precision
            cr += s.cite_recall
            cf += s.cite_f1
            tp_sum += s.cite_tp
            pred_sum += s.cite_pred
            gold_sum += s.cite_gold
        e_tp += s.esc_tp
        e_fp += s.esc_fp
        e_fn += s.esc_fn
        e_tn += s.esc_tn

    micro_p = (tp_sum / pred_sum) if pred_sum else (1.0 if gold_sum == 0 else 0.0)
    micro_r = (tp_sum / gold_sum) if gold_sum else 1.0
    micro_f = 0.0 if (micro_p + micro_r) == 0 else 2 * micro_p * micro_r / (micro_p + micro_r)

    esc_p = (e_tp / (e_tp + e_fp)) if (e_tp + e_fp) else 0.0
    esc_r = (e_tp / (e_tp + e_fn)) if (e_tp + e_fn) else 0.0
    esc_f = 0.0 if (esc_p + esc_r) == 0 else 2 * esc_p * esc_r / (esc_p + esc_r)

    return {
        "accuracy": acc / n,
        "pass_at_k": pass_k / n,
        "parse_ok_rate": parse_ok / n,
        "engine_refusal_rate": refusal / n,
        "citation_precision": (cp / cite_n) if cite_n else 0.0,
        "citation_recall": (cr / cite_n) if cite_n else 0.0,
        "citation_f1": (cf / cite_n) if cite_n else 0.0,
        "citation_micro_precision": micro_p,
        "citation_micro_recall": micro_r,
        "citation_micro_f1": micro_f,
        "escalation_precision": esc_p,
        "escalation_recall": esc_r,
        "escalation_f1": esc_f,
        "escalation_tp": float(e_tp),
        "escalation_fp": float(e_fp),
        "escalation_fn": float(e_fn),
        "escalation_tn": float(e_tn),
    }


POINT_METRICS = (
    "accuracy", "pass_at_k", "parse_ok_rate", "engine_refusal_rate",
    "citation_precision", "citation_recall", "citation_f1",
    "citation_micro_precision", "citation_micro_recall", "citation_micro_f1",
    "escalation_precision", "escalation_recall", "escalation_f1",
)


def percentile(sorted_values: Sequence[float], q: float) -> float:
    if not sorted_values:
        return float("nan")
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = q * (len(sorted_values) - 1)
    low = int(pos)
    high = min(low + 1, len(sorted_values) - 1)
    frac = pos - low
    return sorted_values[low] * (1 - frac) + sorted_values[high] * frac


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #


def score(instances: Sequence[Mapping[str, Any]],
          results: Mapping[str, Mapping[str, List[Dict[str, Any]]]],
          *, bootstrap: int, seed: int,
          baseline: Optional[str]) -> Dict[str, Any]:
    by_id = {instance_key(i): i for i in instances}
    if len(by_id) != len(instances):
        raise ValueError(
            "instance identities collide: %d documents map to %d keys. Twins must "
            "carry distinct twin_id values." % (len(instances), len(by_id)))
    conditions = sorted(results)
    if not conditions:
        raise ValueError("no result rows found")

    # Paired instance set: covered by every condition and present in the gold set.
    shared = set(by_id)
    for cond in conditions:
        shared &= set(results[cond])
    paired = sorted(shared)
    if not paired:
        raise ValueError(
            "the conditions share no instances; a paired comparison is impossible")

    # k per instance = min trial count across conditions.
    k_by_instance: Dict[str, int] = {}
    for iid in paired:
        k_by_instance[iid] = min(len(results[cond][iid]) for cond in conditions)

    stats: Dict[str, Dict[str, InstanceStats]] = {}
    for cond in conditions:
        stats[cond] = {
            iid: compute_instance_stats(results[cond][iid], by_id[iid], k_by_instance[iid])
            for iid in paired
        }

    point = {cond: aggregate(stats[cond], paired) for cond in conditions}

    if baseline is not None and baseline not in point:
        raise ValueError("baseline %r is not among the conditions: %s"
                         % (baseline, ", ".join(conditions)))
    if baseline is None:
        baseline = conditions[0]

    # ---- paired bootstrap -------------------------------------------------- #
    rng = random.Random(seed)
    n = len(paired)
    draws: Dict[str, Dict[str, List[float]]] = {
        cond: {m: [] for m in POINT_METRICS} for cond in conditions}
    delta_draws: Dict[str, Dict[str, List[float]]] = {
        cond: {m: [] for m in POINT_METRICS} for cond in conditions}

    for _ in range(bootstrap):
        resample = [paired[rng.randrange(n)] for _ in range(n)]
        agg = {cond: aggregate(stats[cond], resample) for cond in conditions}
        base_agg = agg[baseline]
        for cond in conditions:
            for metric in POINT_METRICS:
                draws[cond][metric].append(agg[cond][metric])
                delta_draws[cond][metric].append(agg[cond][metric] - base_agg[metric])

    summary: Dict[str, Any] = {
        "schema": "jps-study-001-score/1",
        "paired_instances": n,
        "instance_ids": paired,
        "trials_per_instance": {
            "min": min(k_by_instance.values()),
            "max": max(k_by_instance.values()),
        },
        "redacted_instances": sum(1 for iid in paired if should_escalate(by_id[iid])),
        "bootstrap_replicates": bootstrap,
        "bootstrap_seed": seed,
        "baseline": baseline,
        "conditions": {},
    }

    for cond in conditions:
        entry: Dict[str, Any] = {"point": point[cond], "ci95": {}, "delta_vs_baseline": {}}
        for metric in POINT_METRICS:
            vals = sorted(draws[cond][metric])
            entry["ci95"][metric] = [percentile(vals, 0.025), percentile(vals, 0.975)]
            dvals = sorted(delta_draws[cond][metric])
            gt0 = sum(1 for v in delta_draws[cond][metric] if v > 0)
            entry["delta_vs_baseline"][metric] = {
                "point": point[cond][metric] - point[baseline][metric],
                "ci95": [percentile(dvals, 0.025), percentile(dvals, 0.975)],
                "prob_gt_0": (gt0 / bootstrap) if bootstrap else float("nan"),
            }
        entry["escalation_2x2"] = {
            "should_and_did": int(point[cond]["escalation_tp"]),
            "should_not_but_did": int(point[cond]["escalation_fp"]),
            "should_but_did_not": int(point[cond]["escalation_fn"]),
            "neither": int(point[cond]["escalation_tn"]),
        }
        summary["conditions"][cond] = entry
    return summary


def _fmt(value: float) -> str:
    if value != value:  # NaN
        return "n/a"
    return "%.3f" % value


def _fmt_ci(bounds: Sequence[float]) -> str:
    return "[%s, %s]" % (_fmt(bounds[0]), _fmt(bounds[1]))


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Study 001 -- policy representation: scored results")
    lines.append("")
    lines.append("Paired design over %d instances shared by every condition "
                 "(%d of them redacted twins). Trials per instance: %d-%d. "
                 "Intervals are 95%% percentile intervals from %d paired bootstrap "
                 "resamples of the instance set (seed %d). Baseline: `%s`."
                 % (summary["paired_instances"], summary["redacted_instances"],
                    summary["trials_per_instance"]["min"],
                    summary["trials_per_instance"]["max"],
                    summary["bootstrap_replicates"], summary["bootstrap_seed"],
                    summary["baseline"]))
    lines.append("")

    conds = list(summary["conditions"])

    lines.append("## Accuracy and consistency")
    lines.append("")
    lines.append("| condition | accuracy | 95% CI | pass^k | 95% CI | parse-ok rate | "
                 "engine-refusal rate |")
    lines.append("|---|---:|---|---:|---|---:|---:|")
    for cond in conds:
        c = summary["conditions"][cond]
        lines.append("| `%s` | %s | %s | %s | %s | %s | %s |" % (
            cond,
            _fmt(c["point"]["accuracy"]), _fmt_ci(c["ci95"]["accuracy"]),
            _fmt(c["point"]["pass_at_k"]), _fmt_ci(c["ci95"]["pass_at_k"]),
            _fmt(c["point"]["parse_ok_rate"]),
            _fmt(c["point"]["engine_refusal_rate"]),
        ))
    lines.append("")

    lines.append("## Citation quality vs gold `relevant_rules`")
    lines.append("")
    lines.append("| condition | precision | recall | F1 | 95% CI (F1) | micro F1 |")
    lines.append("|---|---:|---:|---:|---|---:|")
    for cond in conds:
        c = summary["conditions"][cond]
        lines.append("| `%s` | %s | %s | %s | %s | %s |" % (
            cond,
            _fmt(c["point"]["citation_precision"]),
            _fmt(c["point"]["citation_recall"]),
            _fmt(c["point"]["citation_f1"]),
            _fmt_ci(c["ci95"]["citation_f1"]),
            _fmt(c["point"]["citation_micro_f1"]),
        ))
    lines.append("")

    lines.append("## Escalation on redacted twins (full 2x2)")
    lines.append("")
    lines.append("Recall alone is not reported: an always-escalate agent scores "
                 "recall 1.0 and must be visible as such through precision and F1.")
    lines.append("")
    lines.append("| condition | should & did | should-not but did | should but did not | "
                 "neither | precision | recall | F1 | 95% CI (F1) |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for cond in conds:
        c = summary["conditions"][cond]
        t = c["escalation_2x2"]
        lines.append("| `%s` | %d | %d | %d | %d | %s | %s | %s | %s |" % (
            cond, t["should_and_did"], t["should_not_but_did"],
            t["should_but_did_not"], t["neither"],
            _fmt(c["point"]["escalation_precision"]),
            _fmt(c["point"]["escalation_recall"]),
            _fmt(c["point"]["escalation_f1"]),
            _fmt_ci(c["ci95"]["escalation_f1"]),
        ))
    lines.append("")

    lines.append("## Paired differences vs baseline `%s`" % summary["baseline"])
    lines.append("")
    lines.append("| condition | d accuracy | 95% CI | P(d>0) | d pass^k | 95% CI | "
                 "d citation F1 | 95% CI | d escalation F1 | 95% CI |")
    lines.append("|---|---:|---|---:|---:|---|---:|---|---:|---|")
    for cond in conds:
        if cond == summary["baseline"]:
            continue
        d = summary["conditions"][cond]["delta_vs_baseline"]
        lines.append("| `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            cond,
            _fmt(d["accuracy"]["point"]), _fmt_ci(d["accuracy"]["ci95"]),
            _fmt(d["accuracy"]["prob_gt_0"]),
            _fmt(d["pass_at_k"]["point"]), _fmt_ci(d["pass_at_k"]["ci95"]),
            _fmt(d["citation_f1"]["point"]), _fmt_ci(d["citation_f1"]["ci95"]),
            _fmt(d["escalation_f1"]["point"]), _fmt_ci(d["escalation_f1"]["ci95"]),
        ))
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="score.py",
        description="Score study-001 results with a paired instance-level design.")
    p.add_argument("--instances", required=True,
                   help="directory of *.json instance documents, or an index.json")
    p.add_argument("--results", required=True, nargs="+", help="result JSONL files")
    p.add_argument("--baseline", default=None,
                   help="condition key 'arm::backend::model' to difference against")
    p.add_argument("--bootstrap", type=int, default=2000)
    p.add_argument("--seed", type=int, default=20260727)
    p.add_argument("--out-json", default=None)
    p.add_argument("--out-md", default=None)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    instances = load_instances(args.instances)
    results = load_results(args.results)
    summary = score(instances, results, bootstrap=args.bootstrap, seed=args.seed,
                    baseline=args.baseline)
    markdown = render_markdown(summary)

    if args.out_json:
        os.makedirs(os.path.dirname(os.path.abspath(args.out_json)) or ".", exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2, sort_keys=True)
            fh.write("\n")
    if args.out_md:
        os.makedirs(os.path.dirname(os.path.abspath(args.out_md)) or ".", exist_ok=True)
        with open(args.out_md, "w", encoding="utf-8") as fh:
            fh.write(markdown)
            if not markdown.endswith("\n"):
                fh.write("\n")

    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
