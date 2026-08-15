#!/usr/bin/env python3
"""Study 019 language-excerpt derivation -- DESIGN DRAFT, NOT REGISTERED.

Builds the two arm excerpts by the registered derivation rules in EXCERPT-DERIVATION.md
and writes a provenance record (source path/URL, pinned commit, per-source sha256) beside
each. No excerpt is ever hand-edited: re-run this script instead.

    arm A     the JPS Core 0.2.0-draft specification document AND its normative JSON Schema,
              EACH VERBATIM AND IN FULL, from the judgment-pack-spec working tree at the
              pinned commit (see build_jps() for why the schema is in the excerpt).
    arms B/C  named OPA documentation pages, EACH IN FULL, from the open-policy-agent/opa
              repository at the pinned commit, with site scaffolding stripped by the
              mechanical rule below, plus a built-in signature list generated from the
              pinned capabilities file (the built-in tables are rendered by an MDX
              component and are not present in the documentation sources).

Scaffolding strip rule (arms B/C, the only edit made to any upstream page):
    1. a leading YAML front-matter block delimited by `---` lines is removed;
    2. lines that are exactly a Docusaurus `import ... from "@site/...";` statement are
       removed;
    3. lines that are exactly a self-closing MDX component tag (`<Foo ... />`) are
       replaced by a single line naming the component, so the removal is visible.
Nothing else is added, removed, reordered, or reworded.

Usage:
    python3 derive_excerpts.py            # build from the stored upstream sources
    python3 derive_excerpts.py --fetch    # re-download the pinned OPA sources first
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "generated")
UP = os.path.join(HERE, "upstream")
SCRATCH = "/tmp/claude-1000/-home-onword-repo-judgment-pack-judgment-pack-runtime/e3978f36-2e67-46bb-868c-8df975356ef9/scratchpad"

# ---- pins -------------------------------------------------------------------------
JPS_SPEC_REPO = os.environ.get("JPS_SPEC_REPO", "/home/onword/repo/judgment-pack/judgment-pack-spec")
JPS_SPEC_PATH = "spec/judgment-pack-core.md"
JPS_SCHEMA_PATH = "schema/judgment-pack-core.schema.json"
JPS_SPEC_COMMIT = "c2faf4937037ae88b57fdb3e297f9aafefed3997"

OPA_REPO = "open-policy-agent/opa"
OPA_COMMIT = "16b5a013726fff3c2197f98ac4afcd6d2218588a"
OPA_PAGES = [
    "docs/docs/policy-language.md",
    "docs/docs/policy-reference/index.md",
    "docs/docs/policy-reference/keywords/if.md",
    "docs/docs/policy-reference/keywords/contains.md",
    "docs/docs/policy-reference/keywords/default.md",
    "docs/docs/policy-reference/keywords/every.md",
    "docs/docs/policy-reference/keywords/some.md",
    "docs/docs/policy-reference/keywords/not.md",
    "docs/docs/policy-reference/keywords/import.md",
    "docs/docs/policy-testing.md",
]
CAPS = os.environ.get("OPA_CAPS", os.path.join(SCRATCH, "pins", "opa", "caps-filtered.json"))

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
IMPORT_LINE = re.compile(r'^import\s+.*from\s+"@site/.*";\s*$')
MDX_TAG = re.compile(r"^<([A-Z][A-Za-z0-9]*)\b[^>]*/>\s*$")


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def fetch_opa_pages():
    os.makedirs(os.path.join(UP, "opa"), exist_ok=True)
    for page in OPA_PAGES:
        url = "https://raw.githubusercontent.com/%s/%s/%s" % (OPA_REPO, OPA_COMMIT, page)
        dest = os.path.join(UP, "opa", page.replace("/", "__"))
        rc = subprocess.call(["curl", "-sfL", "-o", dest, url])
        if rc != 0:
            print("FETCH FAILED: %s" % url, file=sys.stderr)
            return False
        print("fetched %s (%d bytes)" % (page, os.path.getsize(dest)))
    return True


def strip_scaffolding(text):
    text = FRONTMATTER.sub("", text, count=1)
    out = []
    for line in text.split("\n"):
        if IMPORT_LINE.match(line.strip()):
            continue
        m = MDX_TAG.match(line.strip())
        if m:
            out.append("[site component removed by the derivation rule: <%s/>]" % m.group(1))
            continue
        out.append(line)
    return "\n".join(out)


def build_jps():
    """The specification document AND its normative JSON Schema, both verbatim and in full.

    The schema is part of the excerpt because the specification's prose defines the model
    but not every JSON member spelling the carrier uses (`op`, `evidenceRequirement`, ...):
    the check_excerpt_sufficiency.py run of 2026-08-15 failed on exactly those members with
    the prose alone. Both documents are normative artifacts of the same pinned spec release
    (JPS Core 0.2.0-draft, section 1.1's precedence list), so including both is a
    document-granularity rule, not a curated slice."""
    src = os.path.join(JPS_SPEC_REPO, JPS_SPEC_PATH)
    schema_src = os.path.join(JPS_SPEC_REPO, JPS_SCHEMA_PATH)
    dest = os.path.join(GEN, "JPS-EXCERPT.md")
    with open(src, encoding="utf-8") as fh:
        spec_text = fh.read()
    with open(schema_src, encoding="utf-8") as fh:
        schema_text = fh.read()
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("<!-- BEGIN normative document: %s (judgment-pack-spec @ %s) -->\n\n"
                 % (JPS_SPEC_PATH, JPS_SPEC_COMMIT[:12]))
        fh.write(spec_text.rstrip("\n") + "\n")
        fh.write("\n<!-- END normative document: %s -->\n\n" % JPS_SPEC_PATH)
        fh.write("<!-- BEGIN normative document: %s (judgment-pack-spec @ %s) -->\n\n"
                 % (JPS_SCHEMA_PATH, JPS_SPEC_COMMIT[:12]))
        fh.write("## Normative JSON Schema for a Judgment Pack\n\n```json\n")
        fh.write(schema_text.rstrip("\n") + "\n```\n")
        fh.write("\n<!-- END normative document: %s -->\n" % JPS_SCHEMA_PATH)
    return {
        "arm": "A",
        "rule": "the JPS Core specification document and its normative JSON Schema, "
                "each verbatim and in full",
        "sources": [
            {"repo": "judgment-pack-spec", "commit": JPS_SPEC_COMMIT, "path": JPS_SPEC_PATH,
             "sha256": sha256_file(src), "bytes": os.path.getsize(src), "edits": "none"},
            {"repo": "judgment-pack-spec", "commit": JPS_SPEC_COMMIT, "path": JPS_SCHEMA_PATH,
             "sha256": sha256_file(schema_src), "bytes": os.path.getsize(schema_src),
             "edits": "none (wrapped in a fenced json block)"},
        ],
        "bytes": os.path.getsize(dest),
    }


def builtin_section():
    with open(CAPS) as fh:
        caps = json.load(fh)
    lines = [
        "## Built-in functions admitted by this environment",
        "",
        "Generated from the pinned OPA capabilities file the checker and the evaluator are",
        "both run with. A built-in that is not in this list is refused at check time. The",
        "signatures are the pinned binary's own declarations.",
        "",
    ]
    by_cat = {}
    for b in caps.get("builtins", []):
        cat = ", ".join(b.get("categories") or ["(uncategorised)"])
        by_cat.setdefault(cat, []).append(b)
    for cat in sorted(by_cat):
        lines.append("### %s" % cat)
        lines.append("")
        for b in sorted(by_cat[cat], key=lambda x: x["name"]):
            decl = b.get("decl", {})
            args = ", ".join(
                "%s: %s" % (a.get("name", "_"), render_type(a))
                for a in (decl.get("args") or []))
            res = decl.get("result")
            sig = "%s(%s)" % (b["name"], args)
            if res:
                sig += " -> %s" % render_type(res)
            lines.append("- `%s`  %s" % (sig, (b.get("description") or "").strip()))
        lines.append("")
    lines.append("Language features enabled by this capabilities file: %s."
                 % ", ".join("`%s`" % f for f in caps.get("features", [])))
    lines.append("")
    return "\n".join(lines)


def render_type(node):
    t = node.get("type", "any")
    if t == "array" and isinstance(node.get("static"), list):
        return "array"
    if t == "any" and node.get("of"):
        return "any"
    return t


def build_rego():
    parts = []
    sources = []
    for page in OPA_PAGES:
        raw = os.path.join(UP, "opa", page.replace("/", "__"))
        if not os.path.exists(raw):
            print("missing upstream source %s -- run with --fetch" % raw, file=sys.stderr)
            sys.exit(2)
        with open(raw, encoding="utf-8") as fh:
            text = fh.read()
        parts.append("<!-- BEGIN upstream page: %s (open-policy-agent/opa @ %s) -->\n"
                     % (page, OPA_COMMIT[:12]))
        parts.append(strip_scaffolding(text).strip("\n") + "\n")
        parts.append("<!-- END upstream page: %s -->\n" % page)
        sources.append({"repo": OPA_REPO, "commit": OPA_COMMIT, "path": page,
                        "sha256": sha256_file(raw), "bytes": os.path.getsize(raw),
                        "edits": "front matter, @site imports, MDX component tags"})
    parts.append("<!-- BEGIN generated from the pinned capabilities file -->\n")
    parts.append(builtin_section())
    parts.append("<!-- END generated from the pinned capabilities file -->\n")
    dest = os.path.join(GEN, "REGO-EXCERPT.md")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    sources.append({"generatedFrom": os.path.abspath(CAPS), "sha256": sha256_file(CAPS),
                    "edits": "generated table (built-in tables are not in the doc sources)"})
    return {
        "arm": "B/C",
        "rule": "named OPA documentation pages, each in full, plus the pinned built-in list",
        "sources": sources,
        "bytes": os.path.getsize(dest),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    args = ap.parse_args()
    os.makedirs(GEN, exist_ok=True)
    os.makedirs(os.path.join(UP, "opa"), exist_ok=True)
    if args.fetch and not fetch_opa_pages():
        return 1
    prov = {
        "note": "DESIGN DRAFT, NOT REGISTERED. Regenerate with derive_excerpts.py.",
        "excerpts": [build_jps(), build_rego()],
    }
    for e in prov["excerpts"]:
        e["excerptSha256"] = sha256_file(
            os.path.join(GEN, "JPS-EXCERPT.md" if e["arm"] == "A" else "REGO-EXCERPT.md"))
    with open(os.path.join(GEN, "EXCERPT-PROVENANCE.json"), "w") as fh:
        json.dump(prov, fh, indent=2, sort_keys=True)
        fh.write("\n")
    for e in prov["excerpts"]:
        print("arm %-3s excerpt %7d bytes  sha256=%s" % (e["arm"], e["bytes"], e["excerptSha256"][:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
