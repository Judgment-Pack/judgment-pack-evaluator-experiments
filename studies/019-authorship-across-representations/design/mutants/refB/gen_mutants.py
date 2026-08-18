#!/usr/bin/env python3
"""Study 019 — arm-B (Rego) adequacy mutant generator.

DETERMINISTIC. Re-running on the pinned reference reproduces byte-identical
m-b-NNN.rego files and a byte-identical MANIFEST.json (no timestamps, no
randomness, no wall-clock or host-dependent fields).

What it does
------------
1. Parses `reference/refB/policy.rego` (sha256 pinned below) into ladders /
   rungs / conjuncts by a small structural parser.
2. Emits ONE-EDIT text mutants over the seven registered mutation classes,
   realized in Rego (see CLASSES below). Mutant ids are assigned in class order
   (1..7) and, inside a class, in reference-file order, so ids are stable.
3. Validates every mutant with the pinned
   `opa check --strict --capabilities caps-filtered.json`. A mutant that fails
   is DROPPED with a recorded code (never silently); the file is still written
   so the drop is inspectable.
4. Computes each valid mutant's WITNESS SET: the gold row ids on which the
   mutant's *alignment-scope* output (disposition kind + outcomeId + reason
   set) differs from the unmutated reference's, over the 76 gold rows, using
   `opa eval` with exactly the flags gold/check_gold.py uses (TZ=UTC).
5. Empty-witness mutants are KEPT and flagged `notAdequate: true` — the gold
   adequacy gate needs a killing row or a registered drop for each at prereg.

Scored surface: kind + outcomeId + reasons ONLY ("alignment scope"). The Rego
entrypoint's value is exactly {"disposition", "reasons"}, so the whole returned
value is in scope; nothing is projected away on this arm.

Usage: python3 gen_mutants.py [--jobs N]
"""

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
SCRATCH = "/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad"
REF = os.path.join(DESIGN, "reference", "refB", "policy.rego")
GOLD = os.path.join(DESIGN, "gold", "gold.json")
OPA = os.environ.get("OPA_BIN", SCRATCH + "/pins/opa/opa_linux_amd64_static")
CAPS = os.environ.get("OPA_CAPS", SCRATCH + "/pins/opa/caps-filtered.json")

# Pinned reference: the parser's line-number overrides and the whole class
# enumeration are only meaningful against this exact text.
REF_SHA256 = "1f2e1ad1d423240dd262852f19057a8e906387d5a1b71db8b8a15bc010fc12e2"

OUTCOMES = ["approve", "review", "enhanced-review", "reject"]  # registered JPS outcome ids

CLASSES = {
    "operator-flip": "each ordered comparison operator in a rung conjunct flipped "
                     "(>= <-> >, <= <-> <), one occurrence per mutant",
    "boundary-shift": "each threshold numeral in a rung conjunct shifted by one "
                      "representable step (risk +/-1, spend +/-0.01), one per mutant",
    "unknown-guard-flip": "each three-valued sentinel guard (null for the unreadable "
                          "numerics/country; present/absent/OMITTED for the two evidence "
                          "states; the omitted-key-treated-as-no yes/no guards) inverted "
                          "or deleted, one per mutant",
    "outcome-swap": "each disposition string literal in a rule head that names one of the "
                    "four registered JPS outcome ids swapped for each of the other three",
    "default-swap": "the registered `default decision` value edited: reasons no-match -> "
                    "unknown; disposition unresolved -> review (two mutants)",
    "guard-deletion": "each non-sentinel rung conjunct (the mutual-exclusion / scoping "
                      "conjuncts: sanctions gate, country gate, numeric range bounds) "
                      "deleted, one per mutant",
    "rung-deletion": "each `else` rung of the `determine` ladder deleted, one per mutant",
}

CLASS_ORDER = ["operator-flip", "boundary-shift", "unknown-guard-flip", "outcome-swap",
               "default-swap", "guard-deletion", "rung-deletion"]


# ---------------------------------------------------------------------------
# Structural parse of the reference
# ---------------------------------------------------------------------------

HEAD_RE = re.compile(r'^(?P<name>determine\(risk, spend, country\)|[a-z_][a-z0-9_]*|else)'
                     r' := (?P<value>.*?)(?P<iftail> if \{)?$')
CLAUSE_COMMENT_RE = re.compile(r'^# (?P<id>P1|U1|O[123]|D[1-8][abc]?)\b')

# Clause labels the "nearest preceding clause comment" heuristic gets wrong.
# Keyed by the rung's 1-based head line number in the pinned reference.
CLAUSE_OVERRIDES = {
    132: "D6b",   # enhanced-review limb (comment block sits above the approve limb)
    156: "D6c",   # rung serves D6c; its v_new conjunct is O1 (see CONJUNCT_OVERRIDES)
    145: "D6b",   # unreported-availability limb
    182: "D2",    # total-function backstop: carries D2's no-match value
    212: "U1",    # risk_candidates
    216: "U1",    # spend_candidates
    220: "U1",    # country_candidates
    224: "U1",    # u1_determinations comprehension
    244: "P1",    # unreported-availability rung of the entrypoint ladder
    268: "U1",
    275: "U1",
    21:  "D2",    # default decision := no-match
}

# Conjuncts whose governing prose clause differs from their rung's.
CONJUNCT_OVERRIDES = {
    162: "O1",    # `v_new != "yes"` inside the D6c rung is O1's suspension
    72:  "O3/P1",  # O3's explicit financial-evidence conjunct
}


class Rung:
    def __init__(self, ladder, index, head_line, name, value, body_lines, clause, kind,
                 close_line):
        self.ladder = ladder          # ladder name ("determine", "decision", ...)
        self.index = index            # 0-based rung index within the ladder
        self.head_line = head_line    # 1-based line number of the head
        self.name = name              # "determine(...)" / "decision" / "else"
        self.value = value            # head value text
        self.body_lines = body_lines  # list of 1-based line numbers of body conjuncts
        self.clause = clause          # prose clause id this rung serves
        self.kind = kind              # "head" | "else"
        self.close_line = close_line  # 1-based line number of the rung's last line

    def label(self):
        return f"{self.ladder}[{self.index}]"


def parse(lines):
    """lines: list WITHOUT trailing newlines. Returns list[Rung]."""
    rungs, ladder, index = [], None, 0
    i = 0
    while i < len(lines):
        line = lines[i]
        m = HEAD_RE.match(line)
        if not m:
            i += 1
            continue
        name = m.group("name")
        head_line = i + 1
        body = []
        if m.group("iftail"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("}"):
                if lines[j].strip():
                    body.append(j + 1)
                j += 1
            close = j
        else:
            close = i
        if name == "else":
            index += 1
        else:
            ladder = "determine" if name.startswith("determine") else name
            index = 0
        # clause label
        clause = CLAUSE_OVERRIDES.get(head_line)
        if clause is None:
            for k in range(head_line - 2, -1, -1):
                cm = CLAUSE_COMMENT_RE.match(lines[k])
                if cm:
                    clause = cm.group("id")
                    break
        rungs.append(Rung(ladder, index, head_line, name, m.group("value"), body,
                          clause or "?", "head" if name != "else" else "else",
                          close + 1 if m.group("iftail") else head_line))
        # a `} else := ...` closing line is a body-less else rung of the same ladder
        if close < len(lines) and lines[close].startswith("} else := "):
            index += 1
            rungs.append(Rung(ladder, index, close + 1, "else",
                              lines[close][len("} else := "):], [],
                              CLAUSE_OVERRIDES.get(head_line, clause or "?"), "else",
                              close + 1))
        i = max(close, i) + 1
    return rungs


# ---------------------------------------------------------------------------
# Conjunct classification
# ---------------------------------------------------------------------------

SENTINEL_PATTERNS = [
    (re.compile(r'^(?P<lhs>v_risk|v_spend|v_country) (?P<op>==|!=) null$'),
     "unreadable-input sentinel (omitted key)"),
    (re.compile(r'^(?P<lhs>fin_state|ins_state) (?P<op>==|!=) "(?P<rhs>present|absent|OMITTED)"$'),
     "evidence-availability tri-state"),
    (re.compile(r'^(?P<lhs>v_new|v_critical|v_prior) (?P<op>==|!=) "(?P<rhs>yes)"$'),
     "unreported-status-treated-as-no guard"),
]

CMP_RE = re.compile(r'^(?P<lhs>[A-Za-z_][A-Za-z0-9_]*(?:\([^()]*\))?) '
                    r'(?P<op>>=|<=|==|!=|>|<) (?P<rhs>\S+)$')


def sentinel_kind(text):
    t = text.strip()
    for pat, desc in SENTINEL_PATTERNS:
        if pat.match(t):
            return desc
    return None


def conjunct_clause(rung, lineno):
    return CONJUNCT_OVERRIDES.get(lineno, rung.clause)


def set_rhs(text, rhs, new_rhs):
    """Replace the comparison's right operand only (it ends the line)."""
    return re.sub(r'(\s)' + re.escape(rhs) + r'$', r'\g<1>' + new_rhs, text)


def is_binding(text):
    t = text.strip()
    return t.startswith("some ") or t.startswith("d := ")


# ---------------------------------------------------------------------------
# Mutant construction helpers (all operate on a list of lines, return new list)
# ---------------------------------------------------------------------------

def repl_line(lines, lineno, new):
    out = list(lines)
    out[lineno - 1] = new
    return out


def del_lines(lines, linenos):
    drop = set(linenos)
    return [l for n, l in enumerate(lines, 1) if n not in drop]


def del_conjunct(lines, rung, lineno):
    """Delete one body conjunct. If it was the rung's only conjunct the body
    would become empty (a Rego parse error), so it is replaced by `true`, which
    is the minimal faithful realization of 'this guard no longer constrains'."""
    if len(rung.body_lines) == 1:
        indent = lines[lineno - 1][:len(lines[lineno - 1]) - len(lines[lineno - 1].lstrip())]
        return repl_line(lines, lineno, indent + "true"), True
    return del_lines(lines, [lineno]), False


# ---------------------------------------------------------------------------
# Build the mutant specs
# ---------------------------------------------------------------------------

def build_specs(lines, rungs):
    specs = []  # dicts: class, lines, meta

    body_rungs = [r for r in rungs if r.body_lines]

    # ---- (1) operator-flip -------------------------------------------------
    FLIP = {">=": ">", ">": ">=", "<=": "<", "<": "<="}
    for r in body_rungs:
        for ln in r.body_lines:
            text = lines[ln - 1]
            m = CMP_RE.match(text.strip())
            if not m or m.group("op") not in FLIP:
                continue
            op = m.group("op")
            new_op = FLIP[op]
            new = text.replace(f" {op} ", f" {new_op} ", 1)
            cl = conjunct_clause(r, ln)
            specs.append(dict(cls="operator-flip", lines=repl_line(lines, ln, new),
                              meta=dict(line=ln, rung=r.label(), clause=cl,
                                        target=text.strip(),
                                        edit={"from": op, "to": new_op},
                                        description=f"{cl}: `{text.strip()}` -> "
                                                    f"`{new.strip()}`")))

    # ---- (2) boundary-shift ------------------------------------------------
    for r in body_rungs:
        for ln in r.body_lines:
            text = lines[ln - 1]
            m = CMP_RE.match(text.strip())
            if not m or m.group("op") not in (">=", ">", "<=", "<"):
                continue
            rhs = m.group("rhs")
            try:
                val = Decimal(rhs)
            except Exception:
                continue
            lhs = m.group("lhs")
            if lhs in ("risk", "v_risk"):
                step, axis = Decimal("1"), "risk"
            elif lhs in ("spend", "v_spend"):
                step, axis = Decimal("0.01"), "spend"
            else:
                continue
            cl = conjunct_clause(r, ln)
            for sign, tag in ((Decimal("1"), "+"), (Decimal("-1"), "-")):
                nv = val + sign * step
                nv_s = format(nv.normalize(), "f")
                new = set_rhs(text, rhs, nv_s)
                assert new != text, (ln, rhs)
                specs.append(dict(cls="boundary-shift", lines=repl_line(lines, ln, new),
                                  meta=dict(line=ln, rung=r.label(), clause=cl,
                                            target=text.strip(), axis=axis,
                                            edit={"from": rhs, "to": nv_s},
                                            description=f"{cl}: {axis} threshold "
                                                        f"{rhs} {tag}{step} -> {nv_s}")))

    # ---- (3) unknown-guard-flip -------------------------------------------
    INV = {"==": "!=", "!=": "=="}
    for r in body_rungs:
        for ln in r.body_lines:
            text = lines[ln - 1]
            kind = sentinel_kind(text)
            if not kind:
                continue
            m = CMP_RE.match(text.strip())
            op = m.group("op")
            cl = conjunct_clause(r, ln)
            new = text.replace(f" {op} ", f" {INV[op]} ", 1)
            specs.append(dict(cls="unknown-guard-flip", lines=repl_line(lines, ln, new),
                              meta=dict(line=ln, rung=r.label(), clause=cl,
                                        guardKind=kind, variant="invert",
                                        target=text.strip(),
                                        edit={"from": op, "to": INV[op]},
                                        description=f"{cl} ({kind}): invert "
                                                    f"`{text.strip()}`")))
            muts, made_true = del_conjunct(lines, r, ln)
            specs.append(dict(cls="unknown-guard-flip", lines=muts,
                              meta=dict(line=ln, rung=r.label(), clause=cl,
                                        guardKind=kind, variant="delete",
                                        target=text.strip(),
                                        emptyBodyReplacedWithTrue=made_true,
                                        edit={"from": text.strip(),
                                              "to": "true" if made_true else "<deleted>"},
                                        description=f"{cl} ({kind}): delete "
                                                    f"`{text.strip()}`")))

    # ---- (4) outcome-swap --------------------------------------------------
    DISP_RE = re.compile(r'"disposition": "(?P<d>[a-z-]+)"')
    for r in rungs:
        if r.ladder not in ("determine", "decision"):
            continue
        m = DISP_RE.search(r.value)
        if not m or m.group("d") not in OUTCOMES:
            continue
        cur = m.group("d")
        head = lines[r.head_line - 1]
        for other in OUTCOMES:
            if other == cur:
                continue
            new = head.replace(f'"disposition": "{cur}"', f'"disposition": "{other}"', 1)
            specs.append(dict(cls="outcome-swap", lines=repl_line(lines, r.head_line, new),
                              meta=dict(line=r.head_line, rung=r.label(), clause=r.clause,
                                        target=r.value,
                                        edit={"from": cur, "to": other},
                                        description=f"{r.clause}: rule-head outcome "
                                                    f"{cur} -> {other}")))

    # ---- (5) default-swap --------------------------------------------------
    dflt = [n for n, l in enumerate(lines, 1) if l.startswith("default decision := ")]
    assert len(dflt) == 1, dflt
    dln = dflt[0]
    dtext = lines[dln - 1]
    specs.append(dict(cls="default-swap",
                      lines=repl_line(lines, dln, dtext.replace('"no-match"', '"unknown"', 1)),
                      meta=dict(line=dln, rung="default", clause="D2",
                                target=dtext.strip(),
                                edit={"from": "no-match", "to": "unknown"},
                                description="registered default: reasons no-match -> unknown")))
    specs.append(dict(cls="default-swap",
                      lines=repl_line(lines, dln,
                                      dtext.replace('"disposition": "unresolved"',
                                                    '"disposition": "review"', 1)),
                      meta=dict(line=dln, rung="default", clause="D2",
                                target=dtext.strip(),
                                edit={"from": "unresolved", "to": "review"},
                                description="registered default: disposition unresolved -> "
                                            "review (reasons left as authored)")))

    # ---- (6) guard-deletion ------------------------------------------------
    for r in body_rungs:
        for ln in r.body_lines:
            text = lines[ln - 1]
            if sentinel_kind(text) or is_binding(text):
                continue          # sentinel guards belong to class (3)
            m = CMP_RE.match(text.strip())
            if not m:
                continue
            muts, made_true = del_conjunct(lines, r, ln)
            cl = conjunct_clause(r, ln)
            specs.append(dict(cls="guard-deletion", lines=muts,
                              meta=dict(line=ln, rung=r.label(), clause=cl,
                                        rungKind=r.kind, target=text.strip(),
                                        emptyBodyReplacedWithTrue=made_true,
                                        edit={"from": text.strip(),
                                              "to": "true" if made_true else "<deleted>"},
                                        description=f"{cl}: delete scoping conjunct "
                                                    f"`{text.strip()}`")))

    # ---- (7) rung-deletion -------------------------------------------------
    for r in [x for x in rungs if x.ladder == "determine"]:
        if r.kind != "else":
            continue           # class is "each else rung of the determine ladder"
        # span = the rung's own leading comment block (if any) through its close line,
        # plus one following blank line when that leaves the file's blank-line shape
        # unchanged. Comment removal is cosmetic: comments have no semantics.
        start = r.head_line
        while start > 1 and lines[start - 2].lstrip().startswith("#"):
            start -= 1
        end = r.close_line
        if (end < len(lines) and lines[end].strip() == ""
                and start > 1 and lines[start - 2].strip() == ""):
            end += 1
        span = list(range(start, end + 1))
        specs.append(dict(cls="rung-deletion", lines=del_lines(lines, span),
                          meta=dict(line=r.head_line, rung=r.label(), clause=r.clause,
                                    target=r.value,
                                    edit={"from": f"rung {r.label()} ({r.clause})",
                                          "to": "<deleted>"},
                                    description=f"delete `determine` ladder rung "
                                                f"{r.index} ({r.clause})")))

    specs.sort(key=lambda s: (CLASS_ORDER.index(s["cls"]), s["meta"]["line"],
                              json.dumps(s["meta"]["edit"], sort_keys=True)))
    return specs


# ---------------------------------------------------------------------------
# Execution: opa check + opa eval over the gold rows
# ---------------------------------------------------------------------------

def opa_check(path):
    p = subprocess.run([OPA, "check", "--strict", "--capabilities", CAPS, path],
                       capture_output=True, text=True, env=dict(os.environ, TZ="UTC"))
    return p.returncode, (p.stderr or p.stdout).strip()


def build_input_doc(i):
    """Exactly the projection gold/check_gold.py:opa_eval builds."""
    vendor_parts = []
    for src, dst in [("risk", "riskScore"), ("spend", "requestedSpend")]:
        if i[src] is not None:
            vendor_parts.append(f'"{dst}": {i[src]}')  # unquoted: exact JSON number
    for src, dst in [("sanctions", "sanctionsStatus"), ("country", "countryRisk"),
                     ("newVendor", "newVendor"), ("critical", "criticalSupplier"),
                     ("prior", "priorEnforcement")]:
        if i[src] is not None:
            vendor_parts.append(f'"{dst}": "{i[src]}"')
    ev_parts = []
    if i["finEvidence"] is not None:
        ev_parts.append(f'"financial-evidence": "{i["finEvidence"]}"')
    if i["insurance"] is not None:
        ev_parts.append(f'"insurance-certificate": "{i["insurance"]}"')
    return '{"vendor": {%s}, "evidence": {%s}}' % (", ".join(vendor_parts),
                                                   ", ".join(ev_parts))


def eval_row(policy_path, doc):
    """Alignment-scope output for one row. Flags exactly as check_gold.py's opa_eval."""
    with tempfile.TemporaryDirectory(dir=SCRATCH) as td:
        inp = os.path.join(td, "in.json")
        open(inp, "w").write(doc)
        env = dict(os.environ, TZ="UTC")
        p = subprocess.run([OPA, "eval", "--format", "json", "--fail",
                            "--strict-builtin-errors", "--capabilities", CAPS,
                            "--timeout", "10s",
                            "--data", policy_path,
                            "--input", inp, "data.study.decision"],
                           capture_output=True, text=True, env=env, cwd=td)
        try:
            v = json.loads(p.stdout)["result"][0]["expressions"][0]["value"]
        except Exception as ex:
            # PATH-SCRUBBED. The OPA error payload carries the ABSOLUTE path of the
            # policy file it was handed, and a diagnostic that embeds an absolute path
            # makes this manifest reproducible only from the directory it was first
            # generated in -- which the R1-12 byte-comparison test caught (three runs,
            # three digests, differing in exactly this string). Every directory this
            # program knows about is replaced by a stable token before the text is
            # recorded; the diagnostic keeps its meaning and loses its address.
            diag = (p.stderr or p.stdout).strip()
            for real, token in ((os.path.dirname(policy_path), "<mutant-dir>"),
                                (td, "<work-dir>"), (HERE, "<mutants-refB>"),
                                (DESIGN, "<design>"), (SCRATCH, "<scratch>")):
                if real:
                    diag = diag.replace(real, token)
            raise RuntimeError(f"opa eval rc={p.returncode}: {diag[:200]} ({ex})")
    return [v["disposition"], sorted(v["reasons"])]


def eval_all(policy_path, docs, jobs):
    out = [None] * len(docs)
    err = [None] * len(docs)
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(eval_row, policy_path, d): n for n, d in enumerate(docs)}
        for f in concurrent.futures.as_completed(futs):
            n = futs[f]
            try:
                out[n] = f.result()
            except Exception as e:
                err[n] = str(e)
    return out, err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=12)
    args = ap.parse_args()

    raw = open(REF, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    if got != REF_SHA256:
        sys.exit(f"reference sha256 mismatch: {got} != pinned {REF_SHA256}. "
                 "The class enumeration and line overrides are pinned to that text; "
                 "re-derive before regenerating.")
    lines = raw.decode().split("\n")
    if lines and lines[-1] == "":
        lines.pop()          # keep a trailing newline on write, not a phantom line

    rungs = parse(lines)
    specs = build_specs(lines, rungs)

    gold = json.load(open(GOLD))
    rows = gold["rows"]
    docs = [build_input_doc(r["inputs"]) for r in rows]
    row_ids = [r["id"] for r in rows]

    # unmutated reference outputs
    ref_out, ref_err = eval_all(REF, docs, args.jobs)
    if any(ref_err):
        sys.exit("reference evaluation failed: " +
                 str([(row_ids[n], e) for n, e in enumerate(ref_err) if e][:3]))

    # The witness set is defined against the unmutated reference, so the reference
    # had better still be the one the gold floor gate accepted. Recorded, not assumed.
    ref_vs_gold = [row_ids[n] for n, r in enumerate(rows)
                   if ref_out[n] != [r["expect"]["disposition"],
                                     sorted(r["expect"]["reasons"])]]

    # write mutant files
    entries = []
    for n, s in enumerate(specs, 1):
        mid = f"m-b-{n:03d}"
        path = os.path.join(HERE, mid + ".rego")
        text = "\n".join(s["lines"]) + "\n"
        open(path, "w").write(text)
        entries.append(dict(spec=s, id=mid, path=path, text=text,
                            sha256=hashlib.sha256(text.encode()).hexdigest()))

    ref_text_sha = hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()

    mutants, dropped = [], []
    for e in entries:
        m = dict(id=e["id"], mutationClass=e["spec"]["cls"], file=os.path.basename(e["path"]),
                 sha256=e["sha256"], **e["spec"]["meta"])
        if e["sha256"] == ref_text_sha:
            m.update(status="dropped", dropCode="EQUIVALENT_TEXT",
                     dropDetail="mutant text is identical to the reference")
            dropped.append(m); mutants.append(m); continue
        rc, msg = opa_check(e["path"])
        if rc != 0:
            code = "OPA_CHECK_PARSE" if "rego_parse_error" in msg else (
                "OPA_CHECK_TYPE" if "rego_type_error" in msg else (
                    "OPA_CHECK_COMPILE" if "rego_compile_error" in msg else "OPA_CHECK_OTHER"))
            m.update(status="dropped", dropCode=code, dropDetail=msg.replace(HERE + "/", ""))
            dropped.append(m); mutants.append(m); continue
        m["status"] = "valid"
        mutants.append(m)

    valid = [m for m in mutants if m["status"] == "valid"]
    by_id = {e["id"]: e for e in entries}
    for m in valid:
        out, err = eval_all(by_id[m["id"]]["path"], docs, args.jobs)
        bad = [(row_ids[n], e) for n, e in enumerate(err) if e]
        if bad:
            m.update(status="dropped", dropCode="EVAL_ERROR",
                     dropDetail=f"{len(bad)} row(s) failed to evaluate; first: {bad[0]}")
            m.pop("witnessSet", None)
            dropped.append(m)
            continue
        witness = [row_ids[n] for n in range(len(rows)) if out[n] != ref_out[n]]
        m["witnessSet"] = witness
        m["witnessCount"] = len(witness)
        m["notAdequate"] = (len(witness) == 0)

    # duplicate-text census (kept, not dropped: distinct labelled edits)
    seen = {}
    for m in mutants:
        seen.setdefault(m["sha256"], []).append(m["id"])
    dup_groups = [v for v in seen.values() if len(v) > 1]

    counts = {}
    for c in CLASS_ORDER:
        cm = [m for m in mutants if m["mutationClass"] == c]
        v = [m for m in cm if m["status"] == "valid"]
        counts[c] = dict(generated=len(cm), valid=len(v),
                         dropped=len(cm) - len(v),
                         emptyWitness=len([m for m in v if m["notAdequate"]]))

    manifest = dict(
        manifestVersion="1",
        study="019-authorship-across-representations",
        set="adequacy",
        arm="B",
        language="rego",
        generator="gen_mutants.py",
        scoredSurface="kind + outcomeId + reasons (alignment scope); the Rego entrypoint "
                      "value {disposition, reasons} is entirely in scope",
        reference=dict(path="reference/refB/policy.rego", sha256=REF_SHA256),
        toolchain=dict(opa="1.19.0", opaBin=OPA, capabilities=CAPS,
                       checkFlags=["check", "--strict", "--capabilities", "<caps>"],
                       evalFlags=["eval", "--format", "json", "--fail",
                                  "--strict-builtin-errors", "--capabilities", "<caps>",
                                  "--timeout", "10s", "--data", "<policy>",
                                  "--input", "<row>", "data.study.decision"],
                       env={"TZ": "UTC"}),
        gold=dict(path="gold/gold.json", goldVersion=gold.get("goldVersion"),
                  rows=len(rows), sha256=hashlib.sha256(open(GOLD, "rb").read()).hexdigest(),
                  referenceReproducesGold=(not ref_vs_gold),
                  referenceGoldMismatches=ref_vs_gold),
        classes=CLASSES,
        conventions=dict(
            oneEditPerMutant=True,
            emptyBodyRule="deleting a rung's only conjunct is realized as `true`, recorded "
                          "per mutant as emptyBodyReplacedWithTrue",
            outcomeSwapConvention="every ordered pair over the registered JPS outcome id "
                                  "list [approve, review, enhanced-review, reject]",
            guardDeletionScope="non-sentinel comparison conjuncts of both ladders "
                               "(rungKind records head vs else); sentinel guards are "
                               "class unknown-guard-flip so the two classes are disjoint",
            boundaryShiftScope="threshold numerals in comparison conjuncts only; the U1 "
                               "candidate representative lists are not thresholds and are "
                               "not mutated",
            rungDeletionScope="else rungs of the `determine` ladder only (the head rung is "
                              "excluded by the class definition; its conjuncts are covered "
                              "by guard-deletion)",
            emptyWitnessPolicy="kept and flagged notAdequate; the gold adequacy gate needs "
                               "a killing row or a registered drop at prereg time",
        ),
        counts=dict(generated=len(mutants),
                    valid=len([m for m in mutants if m["status"] == "valid"]),
                    dropped=len([m for m in mutants if m["status"] == "dropped"]),
                    emptyWitness=len([m for m in mutants if m.get("notAdequate")]),
                    perClass=counts),
        duplicateTextGroups=dup_groups,
        mutants=mutants,
    )
    with open(os.path.join(HERE, "MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=False)
        f.write("\n")

    w = sys.stdout.write
    w(f"reference: {os.path.relpath(REF, DESIGN)}  sha256={REF_SHA256[:12]}\n")
    w(f"gold rows: {len(rows)}; reference reproduces gold: "
      f"{'yes' if not ref_vs_gold else 'NO -> ' + str(ref_vs_gold)}\n\n")
    w(f"{'class':22} {'gen':>4} {'valid':>6} {'drop':>5} {'empty-witness':>14}\n")
    for c in CLASS_ORDER:
        k = counts[c]
        w(f"{c:22} {k['generated']:>4} {k['valid']:>6} {k['dropped']:>5} "
          f"{k['emptyWitness']:>14}\n")
    tot = manifest["counts"]
    w(f"{'TOTAL':22} {tot['generated']:>4} "
      f"{tot['generated'] - tot['dropped']:>6} {tot['dropped']:>5} "
      f"{tot['emptyWitness']:>14}\n")
    if dropped:
        w("\ndropped:\n")
        for m in dropped:
            w(f"  {m['id']} [{m['mutationClass']}] {m['dropCode']}: "
              f"{m.get('dropDetail','')[:160]}\n")
    if dup_groups:
        w(f"\nduplicate-text groups (kept): {dup_groups}\n")
    ew = [m["id"] for m in mutants if m.get("notAdequate")]
    if ew:
        w(f"\nempty-witness (notAdequate, kept): {' '.join(ew)}\n")


if __name__ == "__main__":
    main()
