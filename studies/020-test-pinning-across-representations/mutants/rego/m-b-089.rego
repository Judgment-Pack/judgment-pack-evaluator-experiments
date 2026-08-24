# Study 019 — contest policy draft v0.1, Rego reference implementation (arm C shape).
#
# Rego v1. Package `study`, entrypoint `data.study.decision`.
# Result shape: {"disposition": "approve|review|enhanced-review|reject|unresolved",
#                "reasons": [<sorted unresolved reason tokens>]}  (reasons [] for outcomes).
#
# Input projection (registered): vendor facts under /vendor, evidence availability under
# /evidence keyed by requirement id. An OMITTED key means "unreadable" (risk, spend,
# country) or "unreported" (yes/no statuses, evidence availability). Sanctions is always a
# present string; UNKNOWN is a value, not an omission. risk/spend arrive as JSON numbers
# (OPA parses them as exact big rationals, so all six thresholds compare exactly).

package study

# ---------------------------------------------------------------------------
# Registered default: D2's no-match is the fallback value for this entrypoint.
# (This build also names D2 explicitly inside `determine`, so that the U1
# comprehension below can quantify over it; the default is kept as registered
# and as a guard against any uncovered input.)
# ---------------------------------------------------------------------------
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}

# ---------------------------------------------------------------------------
# Readers. `null` / "OMITTED" are sentinels for an omitted key; the projection
# never emits a JSON null, so the sentinels cannot collide with a real value.
# ---------------------------------------------------------------------------
v_risk := object.get(input, ["vendor", "riskScore"], null)

v_spend := object.get(input, ["vendor", "requestedSpend"], null)

v_country := object.get(input, ["vendor", "countryRisk"], null)

v_sanctions := object.get(input, ["vendor", "sanctionsStatus"], null)

v_new := object.get(input, ["vendor", "newVendor"], null)

v_critical := object.get(input, ["vendor", "criticalSupplier"], null)

v_prior := object.get(input, ["vendor", "priorEnforcement"], null)

fin_state := object.get(input, ["evidence", "financial-evidence"], "OMITTED")

ins_state := object.get(input, ["evidence", "insurance-certificate"], "OMITTED")

# ---------------------------------------------------------------------------
# determine(risk, spend, country): the policy's clause ladder evaluated at a
# fully-readable assignment of the three unreadable-capable inputs. Every other
# input (sanctions, the three yes/no statuses, both evidence availabilities) is
# read from `input` directly, because none of them can be "unreadable" in U1's
# sense.
#
# Order inside the ladder mirrors the "Order of application" section:
#   O3, then O2, then D1, D2, then D3-D8 as modified by O1.
# The `else` chain gives exactly that precedence, and it also realizes the
# "earliest clause governs" tie-break: where two clauses yield the same
# determination (D3 and D4 at HIGH/risk>=90; D5 and D3; O1-suspended D6c and
# D8) the earlier rung is the one that fires.
#
# The function is TOTAL: the last rung returns the no-match value, so the U1
# comprehension below can never silently drop a candidate assignment.
# ---------------------------------------------------------------------------

# O3 — large exposure in a high-risk country. Carries the explicit financial-
# evidence conjunct the prose states; P1 has already gated above, so this is
# belt-and-braces, not a behavioural difference. O3 reads country risk,
# requested spend, sanctions and financial evidence; it does not read the risk
# score, so `risk` is deliberately unconstrained in this rung.
determine(risk, spend, country) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	spend > 2000000
	fin_state == "present"
}

# O2 — critical-supplier override. Never applies on MATCH/UNKNOWN.
# (Unreported critical-supplier status is an omitted key, so != "yes" -> treated as no.)
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_critical == "yes"
}

# D1 — sanctions match.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "MATCH"
}

# D2 — unreported sanctions: no determination clause applies, no clause matches.
else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	v_sanctions == "UNKNOWN"
}

# D3 — critical risk.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	risk >= 90
}

# D4 — elevated risk in a high-risk country.
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	risk >= 70
}

# D5 — prior enforcement action (unreported treated as no).
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_prior == "yes"
}

# D6a — LOW country, risk < 40, spend <= 500,000.00.
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend <= 500000
}

# D6b — LOW country, risk < 40, 500,000.00 < spend <= 2,000,000.00.
#   insurance available  -> approve
#   insurance absent     -> enhanced-review
#   availability unreported (omitted key) -> unresolved / unknown
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "present"
}

else := {"disposition": "enhanced-review", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "absent"
}

# Remainder of the D6b region: availability unreported. Written as the region
# without an insurance conjunct so that the branch is region-total (the two
# rungs above have already consumed present/absent), i.e. D6b decides every
# request in its region and D8 never reaches them.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
}

# D6c — LOW country, 40 <= risk < 70, spend <= 100,000.00, as modified by O1.
# O1 suspends D6c for new vendors (yes); an unreported new-vendor status is an
# omitted key and is treated as no, so the conjunct is v_new != "yes".
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	v_new != "yes"
}

# D7 — MEDIUM country, risk < 40, spend <= 100,000.00.
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "MEDIUM"
	risk < 40
	spend <= 100000
}

# D8 — catch-all review for every remaining CLEAR request, including the
# requests O1 removed from D6c.
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
}

# Total-function backstop: a sanctions value outside {CLEAR, MATCH, UNKNOWN},
# or an omitted sanctions key, is governed by no clause of this policy. It
# takes the registered default value. (Not reachable on the canonical grid.)
else := {"disposition": "unresolved", "reasons": ["no-match"]}

# ---------------------------------------------------------------------------
# U1 — unreadable risk score / requested spend / country risk.
#
# Candidate substitution sets. Each set has one representative per interval of
# the input's domain that the clause set can distinguish, so quantifying over
# the set is equivalent to quantifying over the whole domain:
#
#   risk (integer 0..100). The only risk thresholds anywhere in the policy are
#   40 (D6a/D6b/D7 upper, D6c lower), 70 (D6c upper, D4 lower) and 90 (D3), all
#   read as `< 40`, `>= 40`, `< 70`, `>= 70`, `>= 90`. That partitions 0..100
#   into [0,39], [40,69], [70,89], [90,100]; every clause is constant on each
#   block. Endpoints of each block are used (min and max), which also exercises
#   the boundary literals.
#
#   spend (0.00 .. 10,000,000.00, cents). The only spend thresholds are
#   100,000.00 (D6c/D7 upper, inclusive), 500,000.00 (D6a upper inclusive /
#   D6b lower exclusive), 2,000,000.00 (D6b upper inclusive / O3 lower
#   exclusive). Blocks: [0, 100000], (100000, 500000], (500000, 2000000],
#   (2000000, 10000000]. Representatives are each block's endpoints, using the
#   next representable cent (x.01) as each open lower endpoint.
#
#   country: the domain is exactly {LOW, MEDIUM, HIGH}.
#
# A readable input contributes only its own value, so the comprehension ranges
# over exactly the unreadable inputs. If the collected determination set is a
# singleton, U1 issues it ("every readable value ... would yield the same
# determination"); otherwise the case is unresolved as unknown.
# ---------------------------------------------------------------------------
risk_candidates := [v_risk] if {
	v_risk != null
} else := [0, 39, 40, 69, 70, 89, 90, 100]

spend_candidates := [v_spend] if {
	v_spend != null
} else := [0, 100000, 100000.01, 500000, 500000.01, 2000000, 2000000.01, 10000000]

country_candidates := [v_country] if {
	v_country != null
} else := ["LOW", "MEDIUM", "HIGH"]

u1_determinations := {d |
	some r in risk_candidates
	some s in spend_candidates
	some c in country_candidates
	d := determine(r, s, c)
}

# ---------------------------------------------------------------------------
# Entrypoint ladder: P1 first; then O3; then O2; then U1 (which subsumes the
# fully-readable case, where the comprehension is a singleton by construction).
# ---------------------------------------------------------------------------

# P1 — financial evidence absent: unresolved for missing required evidence.
# P1 is checked before every other clause and no override displaces it, so it
# is the first rung and nothing below it can contribute a second reason.
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	fin_state == "absent"
}

# P1 — financial-evidence availability unreported: unresolved as unknown.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "OMITTED"
}

# O3 — decided here (above O2) whenever country risk and requested spend are
# both readable. When either is unreadable, O3 cannot be settled on its own
# terms and instead takes part in U1's quantification via `determine`.
else := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	fin_state == "present"
	v_sanctions == "CLEAR"
	v_country == "HIGH"
	v_spend != null
	v_spend > 2000000
}

# O2 is NOT settled at the entrypoint. Adjudication of the one A/B divergence
# (2026-08-15, policy v0.2): U1's counterfactual governs O2 cases like any other
# clause. Where O3's applicability cannot be excluded (country or spend
# unreadable with a critical supplier), the candidate determinations split
# between escalation and review, and the case is unresolved as unknown; where
# O3 is determinately inapplicable, every candidate lands on review and the
# singleton path issues it. O2 therefore lives only inside `determine`.

# U1 — singleton over the candidate substitutions: issue that determination.
else := d if {
	fin_state == "present"
	count(u1_determinations) == 1
	some d in u1_determinations
}

# U1 — otherwise unresolved as unknown.
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state != "present"
	count(u1_determinations) != 1
}

# ---------------------------------------------------------------------------
# Diagnostics (not the scored entrypoint).
# ---------------------------------------------------------------------------
debug := {
	"decision": decision,
	"u1_determinations": u1_determinations,
	"u1_size": count(u1_determinations),
	"fin_state": fin_state,
	"ins_state": ins_state,
}
