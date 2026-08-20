package study

default decision := {"disposition": "unresolved", "reasons": ["no-match"]}

financial_status := object.get(input, ["evidence", "financial-evidence"], "unreported")
insurance_status := object.get(input, ["evidence", "insurance-certificate"], "unreported")
sanctions_status := object.get(input, ["vendor", "sanctionsStatus"], "unreported")
new_vendor_status := object.get(input, ["vendor", "newVendor"], "no")
critical_supplier_status := object.get(input, ["vendor", "criticalSupplier"], "no")
prior_enforcement_status := object.get(input, ["vendor", "priorEnforcement"], "no")

# P1 and the sanctions clauses do not depend on unreadable risk, spend,
# or country values, so U1 cannot displace their outcomes.
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	financial_status == "absent"
} else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	financial_status == "unreported"
} else := {"disposition": "reject", "reasons": []} if {
	financial_status == "present"
	sanctions_status == "MATCH"
} else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	financial_status == "present"
	sanctions_status == "UNKNOWN"
} else := result if {
	financial_status == "present"
	sanctions_status == "CLEAR"
	result := clear_decision
}

# Each fallback array contains one representative from every equivalence
# class created by the policy's thresholds.
risk_candidates := [reported] if {
	reported := object.get(input, ["vendor", "riskScore"], -1)
	reported >= 0
} else := [0, 40, 70, 90] if {
	true
}

spend_candidates := [reported] if {
	reported := object.get(input, ["vendor", "requestedSpend"], -1)
	reported >= 0
} else := [0, 100000.01, 500000.01, 2000000.01] if {
	true
}

country_candidates := [reported] if {
	reported := object.get(input, ["vendor", "countryRisk"], "unreadable")
	reported in {"LOW", "MEDIUM", "HIGH"}
} else := ["LOW", "MEDIUM", "HIGH"] if {
	true
}

valid_assignment(assignment) if {
	assignment.risk >= 0
	assignment.risk <= 100
	assignment.spend >= 0
	assignment.spend <= 10000000
	assignment.country in {"LOW", "MEDIUM", "HIGH"}
}

# O3, O2, and D3-D8 in governing order for a fully readable CLEAR case.
readable_clear_outcome(assignment) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	valid_assignment(assignment)
	assignment.country == "HIGH"
	assignment.spend > 2000000
} else := {"disposition": "review", "reasons": []} if {
	valid_assignment(assignment)
	critical_supplier_status == "yes"
} else := {"disposition": "reject", "reasons": []} if {
	valid_assignment(assignment)
	assignment.risk >= 90
} else := {"disposition": "reject", "reasons": []} if {
	valid_assignment(assignment)
	assignment.country == "HIGH"
	assignment.risk >= 70
} else := {"disposition": "reject", "reasons": []} if {
	valid_assignment(assignment)
	prior_enforcement_status == "yes"
} else := {"disposition": "approve", "reasons": []} if {
	valid_assignment(assignment)
	assignment.country == "LOW"
	assignment.risk < 40
	assignment.spend <= 500000
} else := {"disposition": "approve", "reasons": []} if {
	valid_assignment(assignment)
	assignment.country == "LOW"
	assignment.risk < 40
	assignment.spend > 500000
	assignment.spend <= 2000000
	insurance_status == "present"
} else := {"disposition": "enhanced-review", "reasons": []} if {
	valid_assignment(assignment)
	assignment.country == "LOW"
	assignment.risk < 40
	assignment.spend > 500000
	assignment.spend <= 2000000
	insurance_status == "absent"
} else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	valid_assignment(assignment)
	assignment.country == "LOW"
	assignment.risk < 40
	assignment.spend > 500000
	assignment.spend <= 2000000
	insurance_status == "unreported"
} else := {"disposition": "approve", "reasons": []} if {
	valid_assignment(assignment)
	assignment.country == "LOW"
	assignment.risk >= 40
	assignment.risk < 70
	assignment.spend <= 100000
	new_vendor_status == "no"
} else := {"disposition": "approve", "reasons": []} if {
	valid_assignment(assignment)
	assignment.country == "MEDIUM"
	assignment.risk < 40
	assignment.spend <= 100000
} else := {"disposition": "review", "reasons": []} if {
	valid_assignment(assignment)
}

possible_clear_outcomes contains outcome if {
	some risk in risk_candidates
	some spend in spend_candidates
	some country in country_candidates
	assignment := {
		"risk": risk,
		"spend": spend,
		"country": country,
	}
	outcome := readable_clear_outcome(assignment)
}

# U1 compares complete outcomes, including unresolved grounds.
clear_decision := outcome if {
	count(possible_clear_outcomes) == 1
	some outcome in possible_clear_outcomes
} else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	count(possible_clear_outcomes) > 1
}
