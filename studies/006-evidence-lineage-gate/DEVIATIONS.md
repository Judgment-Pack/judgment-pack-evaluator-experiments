# Deviations — Study 006

Deviations from [`PREREGISTRATION.md`](PREREGISTRATION.md) are recorded here as they occur,
never by editing the preregistration.

## Post-Phase-A reporting repair

1. The first deterministic tamper run reported D1–D3 but omitted the registered D4 summary even
   though it had retained the exact verified evaluator inputs, outputs, and receipts required to
   compute it. The original `TAMPER-RESULTS.json` and `TAMPER-RESULTS.md` are not rerun or changed.
   Before any model trial, a separate `audit-d4` command was added to read those retained artifacts
   and report D4 without changing attack semantics, expected stages, or D1–D3 scoring.
