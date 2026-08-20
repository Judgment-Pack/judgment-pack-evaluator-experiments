package study

default decision := {"disposition": "unresolved", "reasons": ["no-match"]}

decision := result if {
	ctx := {
		"vendor": object.get(input, "vendor", {}),
		"evidence": object.get(input, "evidence", {}),
	}
	result := policy_result(ctx)
}

# P1, D1, and D2 are resolved before CLEAR-screening evaluation.
policy_result(ctx) := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	object.get(ctx.evidence, "financial-evidence", "unreported") == "absent"
} else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	object.get(ctx.evidence, "financial-evidence", "unreported") == "unreported"
} else := {"disposition": "reject", "reasons": []} if {
	object.get(ctx.evidence, "financial-evidence", "unreported") == "present"
	object.get(ctx.vendor, "sanctionsStatus", "unreported") == "MATCH"
} else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	object.get(ctx.evidence, "financial-evidence", "unreported") == "present"
	object.get(ctx.vendor, "sanctionsStatus", "unreported") == "UNKNOWN"
} else := result if {
	object.get(ctx.evidence, "financial-evidence", "unreported") == "present"
	object.get(ctx.vendor, "sanctionsStatus", "unreported") == "CLEAR"
	result := clear_result(ctx)
} else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	is_object(ctx)
}

# These representatives partition every readable value into equivalence classes
# for all comparisons made by the policy.
risk_candidates(vendor) := [risk] if {
	risk := object.get(vendor, "riskScore", -1)
	risk != -1
} else := [0, 40, 70, 90] if {
	object.get(vendor, "riskScore", -1) == -1
}

spend_candidates(vendor) := [spend] if {
	spend := object.get(vendor, "requestedSpend", -1)
	spend != -1
} else := [0, 100000.01, 500000.01, 2000000.01] if {
	object.get(vendor, "requestedSpend", -1) == -1
}

country_candidates(vendor) := [country] if {
	country := object.get(vendor, "countryRisk", "UNREADABLE")
	country != "UNREADABLE"
} else := ["LOW", "MEDIUM", "HIGH"] if {
	object.get(vendor, "countryRisk", "UNREADABLE") == "UNREADABLE"
}

# U1 issues the concrete outcome only when every possible readable assignment
# produces that same outcome.
clear_result(ctx) := result if {
	risks := risk_candidates(ctx.vendor)
	spends := spend_candidates(ctx.vendor)
	countries := country_candidates(ctx.vendor)

	outcomes := {outcome |
		some risk in risks
		some spend in spends
		some country in countries

		concrete := {
			"vendor": ctx.vendor,
			"evidence": ctx.evidence,
			"risk": risk,
			"spend": spend,
			"country": country,
		}
		outcome := concrete_outcome(concrete)
	}

	count(outcomes) == 1
	result := outcomes[_]
} else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	is_object(ctx)
}

# O3
concrete_outcome(ctx) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	ctx.country == "HIGH"
	ctx.spend > 2000000
# O2
} else := {"disposition": "review", "reasons": []} if {
	object.get(ctx.vendor, "criticalSupplier", "no") == "yes"
# D3
} else := {"disposition": "reject", "reasons": []} if {
	ctx.risk >= 90
# D4
} else := {"disposition": "reject", "reasons": []} if {
	ctx.country == "HIGH"
	ctx.risk >= 70
# D5
} else := {"disposition": "reject", "reasons": []} if {
	object.get(ctx.vendor, "priorEnforcement", "no") == "yes"
# D6a
} else := {"disposition": "approve", "reasons": []} if {
	object.get(ctx.vendor, "priorEnforcement", "no") == "no"
	ctx.country == "LOW"
	ctx.risk < 40
	ctx.spend <= 500000
# D6b: insurance present
} else := {"disposition": "approve", "reasons": []} if {
	object.get(ctx.vendor, "priorEnforcement", "no") == "no"
	ctx.country == "LOW"
	ctx.risk < 40
	ctx.spend > 500000
	ctx.spend <= 2000000
	object.get(ctx.evidence, "insurance-certificate", "unreported") == "present"
# D6b: insurance absent
} else := {"disposition": "enhanced-review", "reasons": []} if {
	object.get(ctx.vendor, "priorEnforcement", "no") == "no"
	ctx.country == "LOW"
	ctx.risk < 40
	ctx.spend > 500000
	ctx.spend <= 2000000
	object.get(ctx.evidence, "insurance-certificate", "unreported") == "absent"
# D6b: insurance availability unreported
} else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	object.get(ctx.vendor, "priorEnforcement", "no") == "no"
	ctx.country == "LOW"
	ctx.risk < 40
	ctx.spend > 500000
	ctx.spend <= 2000000
	object.get(ctx.evidence, "insurance-certificate", "unreported") == "unreported"
# D6c, as modified by O1
} else := {"disposition": "approve", "reasons": []} if {
	object.get(ctx.vendor, "priorEnforcement", "no") == "no"
	object.get(ctx.vendor, "newVendor", "no") == "no"
	ctx.country == "LOW"
	ctx.risk >= 40
	ctx.risk < 70
	ctx.spend <= 100000
# D7
} else := {"disposition": "approve", "reasons": []} if {
	object.get(ctx.vendor, "priorEnforcement", "no") == "no"
	ctx.country == "MEDIUM"
	ctx.risk < 40
	ctx.spend <= 100000
# D8
} else := {"disposition": "review", "reasons": []} if {
	is_object(ctx)
}
