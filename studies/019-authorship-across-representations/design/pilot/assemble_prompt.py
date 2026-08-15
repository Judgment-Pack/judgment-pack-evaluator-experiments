#!/usr/bin/env python3
"""Study 019 prompt assembler -- DESIGN-TIME, NON-CITABLE HARNESS-VALIDATION TOOLING.
NOT the registered study harness (the registered assembler is 012's `arm_assembly.py`,
ported by digest at preregistration time).

Assembles one arm's prompt from the design materials:

    [policy prose stimulus] + [naming appendix] + [arm suffix materials]

  arm A   prompts/generated/JPS-EXCERPT.md, prompts/ARM-A-INSTRUCTIONS.md
  arm B   prompts/generated/REGO-EXCERPT.md, prompts/REGO-TASK-HEAD.md,
          prompts/generated/ARM-B-CONTRACT.md, prompts/REGO-TASK-TAIL.md
  arm C   prompts/generated/REGO-EXCERPT.md, prompts/REGO-TASK-HEAD.md,
          prompts/ARM-C-CONVENTION.md, prompts/REGO-TASK-TAIL.md

Two mechanical rules the assembler enforces, because both are fairness-relevant:

  STIMULUS SLICE. The policy prose is POLICY-DRAFT.md from the line `## Vendor Approval
  Policy` up to (not including) the horizontal rule preceding `## Design notes (not part of
  the stimulus)`. The draft's status header and its design notes NEVER enter a prompt: they
  name the panel findings, the reference build's encoding decisions and the registered
  exclusions, which are answers.

  COMMENT STRIP. HTML comment blocks (`<!-- ... -->`) are removed from every material file.
  The design headers that label these files DESIGN DRAFT and record the fairness rule are
  written as HTML comments precisely so they cannot reach a model.

Usage:
    python3 assemble_prompt.py --arm A --out /path/prompt-A.txt
"""

import argparse
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, ".."))
PROMPTS = os.path.join(DESIGN, "prompts")

POLICY_DRAFT = os.path.join(DESIGN, "POLICY-DRAFT.md")
STIMULUS_START = "## Vendor Approval Policy"
STIMULUS_END = "## Design notes (not part of the stimulus)"

SHARED = [os.path.join(PROMPTS, "NAMING-APPENDIX.md")]
ARM_PARTS = {
    "A": [os.path.join(PROMPTS, "generated", "JPS-EXCERPT.md"),
          os.path.join(PROMPTS, "ARM-A-INSTRUCTIONS.md")],
    "B": [os.path.join(PROMPTS, "generated", "REGO-EXCERPT.md"),
          os.path.join(PROMPTS, "REGO-TASK-HEAD.md"),
          os.path.join(PROMPTS, "generated", "ARM-B-CONTRACT.md"),
          os.path.join(PROMPTS, "REGO-TASK-TAIL.md")],
    "C": [os.path.join(PROMPTS, "generated", "REGO-EXCERPT.md"),
          os.path.join(PROMPTS, "REGO-TASK-HEAD.md"),
          os.path.join(PROMPTS, "ARM-C-CONVENTION.md"),
          os.path.join(PROMPTS, "REGO-TASK-TAIL.md")],
}

HTML_COMMENT = re.compile(r"<!--.*?-->\s*", re.S)


def stimulus():
    with open(POLICY_DRAFT, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == STIMULUS_START)
        end = next(i for i, l in enumerate(lines) if l.strip() == STIMULUS_END)
    except StopIteration:
        print("POLICY-DRAFT.md does not carry the expected stimulus delimiters",
              file=sys.stderr)
        sys.exit(2)
    body = lines[start:end]
    while body and body[-1].strip() in ("", "---"):
        body.pop()
    return "\n".join(body) + "\n"


def read_part(path):
    if not os.path.exists(path):
        print("missing prompt material: %s" % path, file=sys.stderr)
        sys.exit(2)
    with open(path, encoding="utf-8") as fh:
        return HTML_COMMENT.sub("", fh.read()).strip("\n") + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=list("ABCabc"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    arm = args.arm.upper()

    parts = [("POLICY-DRAFT.md (stimulus slice)", stimulus())]
    for path in SHARED + ARM_PARTS[arm]:
        parts.append((os.path.relpath(path, DESIGN), read_part(path)))

    prompt = "\n\n---\n\n".join(p[1].strip("\n") for p in parts) + "\n"
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(prompt)

    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    print("arm %s prompt -> %s" % (arm, os.path.abspath(args.out)))
    for name, text in parts:
        print("    %-42s %7d bytes" % (name, len(text.encode("utf-8"))))
    print("    %-42s %7d bytes  sha256=%s" % ("TOTAL", len(prompt.encode("utf-8")), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
