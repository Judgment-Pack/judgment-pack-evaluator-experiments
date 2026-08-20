# Toolchain resolution notes (design time, 2026-08-14)

**These are design-time resolutions, not enforced pins.** The enforced pins land in
`harness/PINS.json` when the harness exists, stay null until the freeze, and are verified
fail-closed before any scored invocation. Everything below was resolved and verified
empirically on 2026-08-14; nothing is carried from model memory.

## OPA

- Release: **v1.19.0** (latest stable, published 2026-07-30T20:05:58Z, not a prerelease),
  resolved from the GitHub releases API at design time.
- Asset: `opa_linux_amd64_static` (60,526,763 bytes).
- Published checksum: `opa_linux_amd64_static.sha256` →
  `1dd5c5591ff856f5e20a1d66bafae9511ddf3c5552ed3b5070c70b2b6580ee3f` — downloaded and
  verified with `sha256sum -c`: OK. Checksums are per-asset files; no aggregated
  `checksums.txt` is published.
- `opa version` (semantic fields recorded; output never hashed — it embeds build metadata):
  Version 1.19.0, Go go1.26.5, Platform linux/amd64, **Rego Version: v1** (default),
  Build Timestamp 2026-07-30T19:38:54Z (present → **no reproducible-build claim is
  available**; the pin is against the published artifact only). Note: this static build
  reports `WebAssembly: available`, correcting an earlier design assumption that the static
  asset ships without the WASM runtime.
- License: **Apache-2.0**, verified from `LICENSE` at tag v1.19.0 in the upstream
  repository (not from memory).
- Empirical checks against this exact binary:
  - `opa capabilities --current` lists all 7 candidate denylist builtins (`time.now_ns`,
    `rand.intn`, `uuid.rfc4122`, `http.send`, `net.lookup_ip_addr`, `opa.runtime`,
    `net.cidr_expand`); a filtered capabilities file leaves 199 builtins.
  - Canary (`time.now_ns` policy): **passes** `opa check` without the filter (exit 0),
    **refused** with it — `rego_type_error: undefined function time.now_ns`, exit 1. The
    gate has power.
  - **`opa exec` does not accept `--capabilities`** (v1.19.0) — the harness must enforce
    capabilities via `opa build --capabilities` (fails at build time) or per-row
    `opa eval --capabilities`.
  - Undefined-query trap confirmed: `opa eval` on a fully undefined query prints `{}` with
    exit 0 **without** `--fail`, exit 1 with it. The result contract therefore requires a
    `default` decision and scored invocations use `--fail`.
  - `opa test` with a failing test exits **2**.

## jpack

- Release: **v0.17.0** (published 2026-08-10T02:00:53Z),
  `Judgment-Pack/judgment-pack-runtime`.
- Asset: `judgment-pack_0.17.0_linux_amd64.tar.gz`; archive sha256
  `4046a101e3b638eee87f5d3f2f17b8337d2e4be35a34d45060789639b816d8dc`, verified against the
  release's `checksums.txt`: OK.
- Extracted binary sha256:
  `42f35f7900bea6dfce215631b50729ab22dd347289e1bde3412604fb043a22e9`.
- `jpack version`: `jpack 0.17.0` / `JPS: 0.1.0-draft, 0.2.0-draft (immutable-git-ref)`.
- Reproducible-build attestation (local build from the tag reproducing the published binary
  digest, the Study 013 pattern) is deferred to harness time.
- Reminder from the design survey: the binary on the operator PATH is v0.10.0 and predates
  ADR-0023/0024/0025 — the harness must invoke the pinned build only, and refuses on digest
  mismatch.

## Authoring stack

- `codex-cli 0.145.0`, local binary sha256
  `a2a05dafaa1acb002a45eaec0a462de5b13694fcfcd7bc43305f14781ce7be14` — **byte-identical to
  Study 012's pinned digest**, so continuity with the 011/012 baselines holds with no
  re-pin. Model selection is named by explicit flag at batch time; a model name is not a
  digest (Study 012 correction), and the golden-context capture re-runs for this study's
  environment regardless.
