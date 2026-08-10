"""Drives the node probe layer against the pinned clone.

Each probe entrypoint under `probes/` is bundled by the pinned clone's own esbuild —
the transpiler the platform's toolchain itself uses, at the version upstream's lockfile
resolves — with every `@gadgets/*` import aliased into the clone's source and
`cloudflare:workers` aliased to the study stub (the one injected seam). The bundle then
runs under plain Node. Nothing upstream is vendored, modified, or reimplemented; the
bundle is a per-invocation temporary artifact of pinned inputs.

(Upstream's own node-env test path uses vitest; vitest's native rollup binary requires a
newer glibc than this apparatus provides, so the study drives esbuild directly instead.
Recorded in PINS.json as an apparatus note.)

Three operations:

    ceremony(cells)    -> the per-cell cf verdicts + apparatus self-report
    build_helpers(req) -> upstream identity values for the fixture builder
    probe_suite()      -> the upstream-behavior demonstration suite (exit code, output)

Requires CFOS_SOURCE (the pinned clone, dependencies installed) and `node` on PATH.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent
PROBES = STUDY / "probes"

ALIASES = {
    "cloudflare:workers": "{probes}/stubs/cloudflare-workers.ts",
    "@gadgets/typed-storage": "{source}/packages/typed-storage/src/index.ts",
    "@gadgets/mcp-shared/tools": "{source}/packages/mcp-shared/src/tools.ts",
    "@gadgets/mcp-shared/scope": "{source}/packages/mcp-shared/src/scope.ts",
    "@gadgets/workshop-backend/auto-approval":
        "{source}/packages/workshop-backend/src/auto-approval.ts",
    "@gadgets/workshop-backend/mock-storage":
        "{source}/packages/workshop-backend/__tests__/mock-storage.ts",
    "@gadgets/workshop-shared/api": "{source}/packages/workshop-shared/src/api.ts",
    "@gadgets/workshop-shared/gatekeeper":
        "{source}/packages/workshop-shared/src/gatekeeper.ts",
}


class CfRunnerError(RuntimeError):
    pass


def source_root():
    source = os.environ.get("CFOS_SOURCE")
    if not source or not Path(source).is_dir():
        raise CfRunnerError("CFOS_SOURCE must point at the pinned cloudflare-os clone")
    return Path(source).resolve()


def esbuild_binary(source):
    candidate = source / "node_modules" / ".pnpm" / "node_modules" / ".bin" / "esbuild"
    if not candidate.is_file():
        raise CfRunnerError(
            "the pinned clone's esbuild is not installed (pnpm install first): %s"
            % candidate
        )
    return candidate


def esbuild_version(source):
    completed = subprocess.run(
        [str(esbuild_binary(source)), "--version"], capture_output=True, timeout=60
    )
    return completed.stdout.decode("utf-8").strip()


def _bundle(source, entry, out_path):
    command = [
        str(esbuild_binary(source)),
        str(PROBES / entry),
        "--bundle",
        "--platform=node",
        "--format=esm",
        "--target=node22",
        "--log-level=warning",
        "--banner:js=import { createRequire } from 'node:module'; "
        "const require = createRequire(import.meta.url);",
        "--outfile=%s" % out_path,
    ]
    for name, template in ALIASES.items():
        resolved = template.format(source=source, probes=PROBES)
        command.append("--alias:%s=%s" % (name, resolved))
    completed = subprocess.run(command, capture_output=True, timeout=300)
    if completed.returncode != 0:
        raise CfRunnerError(
            "esbuild bundling failed for %s: %s"
            % (entry, completed.stderr.decode("utf-8", "replace")[-2000:])
        )


def _run(source, entry, extra_env, timeout=600):
    environment = dict(os.environ)
    environment["CFOS_SOURCE"] = str(source)
    environment.update(extra_env)
    with tempfile.TemporaryDirectory(prefix="study015-bundle-") as scratch:
        out_path = Path(scratch) / (Path(entry).stem + ".mjs")
        _bundle(source, entry, out_path)
        return subprocess.run(
            ["node", str(out_path)],
            capture_output=True,
            env=environment,
            timeout=timeout,
        )


def ceremony(cells):
    """cells: iterable of (cell_id, directory). Returns the parsed CF_OUT document."""
    source = source_root()
    with tempfile.TemporaryDirectory(prefix="study015-cf-") as scratch:
        request = Path(scratch) / "cells.json"
        out = Path(scratch) / "verdicts.json"
        request.write_text(
            json.dumps(
                [{"id": cell_id, "dir": str(Path(directory).resolve())}
                 for cell_id, directory in cells]
            ),
            encoding="utf-8",
        )
        completed = _run(
            source, "ceremony.ts", {"CF_CELLS": str(request), "CF_OUT": str(out)}
        )
        if completed.returncode != 0 or not out.is_file():
            raise CfRunnerError(
                "cf ceremony run failed (exit %d): %s"
                % (
                    completed.returncode,
                    completed.stderr.decode("utf-8", "replace")[-2000:],
                )
            )
        document = json.loads(out.read_text(encoding="utf-8"))
    apparatus = document.get("apparatus")
    if isinstance(apparatus, dict):
        apparatus["esbuildVersion"] = esbuild_version(source)
    return document


def build_helpers(request_document):
    """Compute upstream identity values (actionKindFor, catalogRevision) for the builder."""
    source = source_root()
    with tempfile.TemporaryDirectory(prefix="study015-build-") as scratch:
        request = Path(scratch) / "request.json"
        out = Path(scratch) / "out.json"
        request.write_text(json.dumps(request_document), encoding="utf-8")
        completed = _run(
            source,
            "build-helpers.ts",
            {"BUILD_REQUEST": str(request), "BUILD_OUT": str(out)},
        )
        if completed.returncode != 0 or not out.is_file():
            raise CfRunnerError(
                "build helper run failed (exit %d): %s"
                % (
                    completed.returncode,
                    completed.stderr.decode("utf-8", "replace")[-2000:],
                )
            )
        return json.loads(out.read_text(encoding="utf-8"))


def probe_suite():
    """Run the upstream-behavior demonstration suite; returns (exit code, output text)."""
    source = source_root()
    completed = _run(source, "upstream-probes.ts", {})
    text = completed.stdout.decode("utf-8", "replace") + completed.stderr.decode(
        "utf-8", "replace"
    )
    return completed.returncode, text
