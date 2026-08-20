package study

default decision := {"disposition": "unresolved", "reasons": ["no-match"]}

vendor := object.get(input, "vendor", {})

evidence := object.get(input, "evidence", {})

financial_evidence_status := object.get(evidence, "financial-evidence", "unreported")

insurance_status := object.get(evidence, "insurance-certificate", "unreported")

sanctions_status := object.get(vendor, "sanctionsStatus", "unreported")

# P1 applies before every other clause. D1 and D2 then handle non-CLEAR
# sanctions results. CLEAR cases are evaluated through U1 below.
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	financial_evidence_status == "absent"
} else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	financial_evidence_status == "unreported"
} else := {"disposition": "reject", "reasons": []} if {
	financial_evidence_status == "present"
	sanctions_status == "MATCH"
} else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	financial_evidence_status == "present"
	sanctions_status == "UNKNOWN"
} else := result if {
	financial_evidence_status == "present"
	sanctions_status == "CLEAR"
	result := clear_decision
}

# The representatives cover every outcome-distinct interval for each unreadable
# input. Present values remain fixed, while omitted values range over these
# finite partitions as required by U1.
risk_score_domain := {risk_score} if {
	risk_score := object.get(vendor, "riskScore", -1)
	risk_score != -1
} else := {0, 40, 70, 90} if {
	object.get(vendor, "riskScore", -1) == -1
}

requested_spend_domain := {requested_spend} if {
	requested_spend := object.get(vendor, "requestedSpend", -1)
	requested_spend != -1
} else := {0, 100000.01, 500000.01, 2000000.01} if {
	object.get(vendor, "requestedSpend", -1) == -1
}

country_risk_domain := {country_risk} if {
	country_risk := object.get(vendor, "countryRisk", "UNREADABLE")
	country_risk != "UNREADABLE"
} else := {"LOW", "MEDIUM", "HIGH"} if {
	object.get(vendor, "countryRisk", "UNREADABLE") == "UNREADABLE"
}

clear_outcomes := {outcome |
	some risk_score in risk_score_domain
	some requested_spend in requested_spend_domain
	some country_risk in country_risk_domain
	outcome := readable_clear_outcome(risk_score, requested_spend, country_risk)
}

clear_decision := outcome if {
	count(clear_outcomes) == 1
	some outcome in clear_outcomes
} else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	count(clear_outcomes) > 1
}

valid_readable_inputs(risk_score, requested_spend, country_risk) if {
	risk_score >= 0
	risk_score <= 100
	requested_spend >= 0
	requested_spend <= 10000000
	country_risk in {"LOW", "MEDIUM", "HIGH"}
}

# O3, O2, and D1-D8 precedence for a CLEAR case whose three potentially
# unreadable inputs have been assigned readable values.
readable_clear_outcome(risk_score, requested_spend, country_risk) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
	country_risk == "HIGH"
	requested_spend > 2000000
} else := {"disposition": "review", "reasons": []} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
	object.get(vendor, "criticalSupplier", "no") == "yes"
} else := {"disposition": "reject", "reasons": []} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
	risk_score >= 90
} else := {"disposition": "reject", "reasons": []} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
	country_risk == "HIGH"
	risk_score >= 70
} else := {"disposition": "reject", "reasons": []} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
	object.get(vendor, "priorEnforcement", "no") == "yes"
} else := {"disposition": "approve", "reasons": []} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
	country_risk == "LOW"
	risk_score < 40
	requested_spend <= 500000
} else := {"disposition": "approve", "reasons": []} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
	country_risk == "LOW"
	risk_score < 40
	requested_spend > 500000
	requested_spend <= 2000000
	insurance_status == "present"
} else := {"disposition": "enhanced-review", "reasons": []} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
	country_risk == "LOW"
	risk_score < 40
	requested_spend > 500000
	requested_spend <= 2000000
	insurance_status == "absent"
} else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
	country_risk == "LOW"
	risk_score < 40
	requested_spend > 500000
	requested_spend <= 2000000
	insurance_status == "unreported"
} else := {"disposition": "approve", "reasons": []} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
	country_risk == "LOW"
	risk_score >= 40
	risk_score < 70
	requested_spend <= 100000
	object.get(vendor, "newVendor", "no") != "yes"
} else := {"disposition": "approve", "reasons": []} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
	country_risk == "MEDIUM"
	risk_score < 40
	requested_spend <= 100000
} else := {"disposition": "review", "reasons": []} if {
	valid_readable_inputs(risk_score, requested_spend, country_risk)
}
