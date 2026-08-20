package study

vendor := object.get(input, "vendor", {})
evidence := object.get(input, "evidence", {})

financial_status := object.get(evidence, "financial-evidence", "unreported")
insurance_status := object.get(evidence, "insurance-certificate", "unreported")
sanctions_status := object.get(vendor, "sanctionsStatus", "unreported")
critical_status := object.get(vendor, "criticalSupplier", "no")
prior_status := object.get(vendor, "priorEnforcement", "no")
new_status := object.get(vendor, "newVendor", "no")

determination(disposition) := {
	"disposition": disposition,
	"reasons": [],
}

unresolved(reason) := {
	"disposition": "unresolved",
	"reasons": [reason],
}

# P1 and the sanctions clauses do not depend on unreadable numeric or
# country inputs, so they are resolved before applying U1.
decision := unresolved("missing-required-evidence") if {
	financial_status == "absent"
} else := unresolved("unknown") if {
	financial_status == "unreported"
} else := determination("reject") if {
	financial_status == "present"
	sanctions_status == "MATCH"
} else := unresolved("no-match") if {
	financial_status == "present"
	sanctions_status == "UNKNOWN"
} else := clear_decision if {
	financial_status == "present"
	sanctions_status == "CLEAR"
}

# These representatives cover every behaviorally distinct interval.
risk_representatives := [0, 40, 70, 90]
spend_representatives := [0, 100000.01, 500000.01, 2000000.01]
country_representatives := ["LOW", "MEDIUM", "HIGH"]

risk_values contains risk if {
	risk := object.get(vendor, "riskScore", -1)
	risk >= 0
}

risk_values contains risk if {
	object.get(vendor, "riskScore", -1) == -1
	some risk in risk_representatives
}

spend_values contains spend if {
	spend := object.get(vendor, "requestedSpend", -1)
	spend >= 0
}

spend_values contains spend if {
	object.get(vendor, "requestedSpend", -1) == -1
	some spend in spend_representatives
}

country_values contains country if {
	country := object.get(vendor, "countryRisk", "unreadable")
	country != "unreadable"
}

country_values contains country if {
	object.get(vendor, "countryRisk", "unreadable") == "unreadable"
	some country in country_representatives
}

valid_assignment(risk, spend, country) if {
	risk >= 0
	risk <= 100
	spend >= 0
	spend <= 10000000
	country in country_representatives
}

# Ordered readable-case evaluation: O3, O2, then D3-D8 as modified by O1.
clear_outcome(risk, spend, country) := unresolved("exception-escalation") if {
	valid_assignment(risk, spend, country)
	country == "HIGH"
	spend > 2000000
} else := determination("review") if {
	valid_assignment(risk, spend, country)
	critical_status == "yes"
} else := determination("reject") if {
	valid_assignment(risk, spend, country)
	risk >= 90
} else := determination("reject") if {
	valid_assignment(risk, spend, country)
	country == "HIGH"
	risk >= 70
} else := determination("reject") if {
	valid_assignment(risk, spend, country)
	prior_status == "yes"
} else := determination("approve") if {
	valid_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend <= 500000
} else := determination("approve") if {
	valid_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_status == "present"
} else := determination("enhanced-review") if {
	valid_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_status == "absent"
} else := unresolved("unknown") if {
	valid_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_status == "unreported"
} else := determination("approve") if {
	valid_assignment(risk, spend, country)
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	new_status == "no"
} else := determination("approve") if {
	valid_assignment(risk, spend, country)
	country == "MEDIUM"
	risk < 40
	spend <= 100000
} else := determination("review") if {
	valid_assignment(risk, spend, country)
}

possible_outcomes contains outcome if {
	some risk in risk_values
	some spend in spend_values
	some country in country_values
	outcome := clear_outcome(risk, spend, country)
}

clear_decision := outcome if {
	count(possible_outcomes) == 1
	some outcome in possible_outcomes
} else := unresolved("unknown") if {
	count(possible_outcomes) > 1
}
