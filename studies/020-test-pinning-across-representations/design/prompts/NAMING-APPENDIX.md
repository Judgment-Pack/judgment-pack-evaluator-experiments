# Naming appendix (registered study conventions — shared across all arms)

These are fixed identifiers and encodings, not policy content. Use them exactly.

## Outcomes and grounds

- Determination identifiers, exactly: `approve`, `review`, `enhanced-review`, `reject`.
- Unresolved ground tokens, exactly: `missing-required-evidence`, `unknown`, `no-match`,
  `exception-escalation` (the escalated-for-human-determination ground). An unresolved
  case carries one or more of these tokens; a determination carries none.

## Input identifiers

- Vendor facts live under `/vendor/`: `riskScore`, `requestedSpend`, `sanctionsStatus`
  (`"CLEAR"` | `"MATCH"` | `"UNKNOWN"` — UNKNOWN is a present string value),
  `countryRisk` (`"LOW"` | `"MEDIUM"` | `"HIGH"`), `newVendor`, `criticalSupplier`,
  `priorEnforcement` (each `"yes"` | `"no"`).
- Evidence availability identifiers: `financial-evidence`, `insurance-certificate`, with
  availability values `"present"` (= available) and `"absent"`; an omitted entry means
  the availability is unreported.
- An input that is unreadable/unreported is an **omitted member** — never a null, never a
  sentinel string. Inputs never carry malformed or out-of-range values.

## Arm A (Judgment Pack) bindings

- `riskScore` and `requestedSpend` arrive as decimal **strings** — integer scale for risk
  (e.g. `"70"`), two decimals for spend (e.g. `"100000.00"`), no leading zeros, no
  exponent.
- Evidence availability arrives as the separate evidence document mapping the two
  requirement ids above to `"present"` / `"absent"` (omitted = unreported).
- The pack's `escalation` member uses target kind `queue`, name `vendor-compliance-desk`,
  and the trigger list exactly `["missing-required-evidence", "no-match", "unknown"]`.
- Do not use the `applicability` member.

## Arms B and C (Rego) bindings

- Rego v1 (OPA 1.x default dialect). Package `study`; the decision entrypoint is the rule
  `decision` (evaluated as `data.study.decision`).
- `input.vendor` carries the vendor fields above, with `riskScore` and `requestedSpend`
  as JSON **numbers**; `input.evidence` carries the two evidence identifiers with values
  `"present"` / `"absent"` (omitted = unreported).
