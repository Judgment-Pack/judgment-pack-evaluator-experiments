package study

default decision := {"disposition": "unresolved", "reasons": ["no-match"]}

approve_result := {"disposition": "approve", "reasons": []}
review_result := {"disposition": "review", "reasons": []}
enhanced_review_result := {"disposition": "enhanced-review", "reasons": []}
reject_result := {"disposition": "reject", "reasons": []}

missing_evidence_result := {
	"disposition": "unresolved",
	"reasons": ["missing-required-evidence"],
}

unknown_result := {
	"disposition": "unresolved",
	"reasons": ["unknown"],
}

no_match_result := {
	"disposition": "unresolved",
	"reasons": ["no-match"],
}

exception_escalation_result := {
	"disposition": "unresolved",
	"reasons": ["exception-escalation"],
}

vendor := object.get(input, "vendor", {})
evidence := object.get(input, "evidence", {})

financial_evidence := object.get(evidence, "financial-evidence", "unreported")
insurance_certificate := object.get(evidence, "insurance-certificate", "unreported")

sanctions_status := object.get(vendor, "sanctionsStatus", "unreported")
new_vendor := object.get(vendor, "newVendor", "unreported")
critical_supplier := object.get(vendor, "criticalSupplier", "unreported")
prior_enforcement := object.get(vendor, "priorEnforcement", "unreported")

# The representatives below cover every equivalence class induced by the
# policy's thresholds. They permit U1's universal test without enumerating
# every possible cent value.

risk_values contains value if {
	value := object.get(vendor, "riskScore", -1)
	value != -1
}

risk_values contains value if {
	object.get(vendor, "riskScore", -1) == -1
	some value in [0, 40, 70, 90]
}

spend_values contains value if {
	value := object.get(vendor, "requestedSpend", -1)
	value != -1
}

spend_values contains value if {
	object.get(vendor, "requestedSpend", -1) == -1
	some value in [0, 100000.01, 500000.01, 2000000.01]
}

country_values contains value if {
	value := object.get(vendor, "countryRisk", "unreported")
	value != "unreported"
}

country_values contains value if {
	object.get(vendor, "countryRisk", "unreported") == "unreported"
	some value in ["LOW", "MEDIUM", "HIGH"]
}

valid_assignment(risk, spend, country) if {
	risk >= 0
	risk <= 100
	spend >= 0
	spend <= 10000000
	country in {"LOW", "MEDIUM", "HIGH"}
}

outcome_for(risk, spend, country) := exception_escalation_result if {
	valid_assignment(risk, spend, country)
	country == "HIGH"
	spend > 2000000
} else := review_result if {
	valid_assignment(risk, spend, country)
	critical_supplier == "yes"
} else := reject_result if {
	valid_assignment(risk, spend, country)
	risk >= 90
} else := reject_result if {
	valid_assignment(risk, spend, country)
	country == "HIGH"
	risk >= 70
} else := reject_result if {
	valid_assignment(risk, spend, country)
	prior_enforcement == "yes"
} else := approve_result if {
	valid_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend <= 500000
} else := approve_result if {
	valid_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_certificate == "present"
} else := enhanced_review_result if {
	valid_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_certificate == "absent"
} else := unknown_result if {
	valid_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_certificate == "unreported"
} else := approve_result if {
	valid_assignment(risk, spend, country)
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	new_vendor != "yes"
} else := approve_result if {
	valid_assignment(risk, spend, country)
	country == "MEDIUM"
	risk < 40
	spend <= 100000
} else := review_result if {
	valid_assignment(risk, spend, country)
}

candidate_outcomes contains outcome if {
	some risk in risk_values
	some spend in spend_values
	some country in country_values
	outcome := outcome_for(risk, spend, country)
}

decision := missing_evidence_result if {
	financial_evidence == "absent"
} else := unknown_result if {
	financial_evidence == "unreported"
} else := reject_result if {
	sanctions_status == "MATCH"
} else := no_match_result if {
	sanctions_status == "UNKNOWN"
} else := only_outcome if {
	sanctions_status == "CLEAR"
	count(candidate_outcomes) == 1
	some only_outcome in candidate_outcomes
} else := unknown_result if {
	sanctions_status == "CLEAR"
	count(candidate_outcomes) != 1
}
