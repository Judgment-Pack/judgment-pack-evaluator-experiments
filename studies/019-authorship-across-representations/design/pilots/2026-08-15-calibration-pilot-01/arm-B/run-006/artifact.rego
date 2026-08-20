package study

approve_result := {"disposition": "approve", "reasons": []}
review_result := {"disposition": "review", "reasons": []}
enhanced_review_result := {"disposition": "enhanced-review", "reasons": []}
reject_result := {"disposition": "reject", "reasons": []}
missing_evidence_result := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]}
unknown_result := {"disposition": "unresolved", "reasons": ["unknown"]}
no_match_result := {"disposition": "unresolved", "reasons": ["no-match"]}
escalation_result := {"disposition": "unresolved", "reasons": ["exception-escalation"]}

vendor_facts := object.get(input, "vendor", {})
evidence_facts := object.get(input, "evidence", {})

financial_status := object.get(evidence_facts, "financial-evidence", "unreported")
insurance_status := object.get(evidence_facts, "insurance-certificate", "unreported")
sanctions_status := object.get(vendor_facts, "sanctionsStatus", "UNKNOWN")
new_vendor_status := object.get(vendor_facts, "newVendor", "no")
critical_supplier_status := object.get(vendor_facts, "criticalSupplier", "no")
prior_enforcement_status := object.get(vendor_facts, "priorEnforcement", "no")

# P1 is applied before sanctions handling or evaluation under U1.
decision := missing_evidence_result if {
	financial_status == "absent"
} else := unknown_result if {
	financial_status == "unreported"
} else := reject_result if {
	financial_status == "present"
	sanctions_status == "MATCH"
} else := no_match_result if {
	financial_status == "present"
	sanctions_status == "UNKNOWN"
} else := clear_decision if {
	financial_status == "present"
	sanctions_status == "CLEAR"
}

# These values cover every behaviorally distinct interval and each threshold.
risk_candidates := [risk] if {
	risk := object.get(vendor_facts, "riskScore", -1)
	risk >= 0
	risk <= 100
} else := [0, 39, 40, 69, 70, 89, 90, 100] if true

spend_candidates := [spend] if {
	spend := object.get(vendor_facts, "requestedSpend", -1)
	spend >= 0
	spend <= 10000000
} else := [
	0,
	100000,
	100000.01,
	500000,
	500000.01,
	2000000,
	2000000.01,
	10000000,
] if true

country_candidates := [country] if {
	country := object.get(vendor_facts, "countryRisk", "unreadable")
	country in {"LOW", "MEDIUM", "HIGH"}
} else := ["LOW", "MEDIUM", "HIGH"] if true

# U1 compares complete outcomes, so escalation and unresolved limbs remain
# distinguishable even though they share the unresolved disposition.
candidate_outcomes := {
	outcome |
	some risk in risk_candidates
	some spend in spend_candidates
	some country in country_candidates
	outcome := outcome_for(risk, spend, country)
}

clear_decision := outcome if {
	outcomes := candidate_outcomes
	count(outcomes) == 1
	outcome := outcomes[_]
} else := unknown_result if true

readable_assignment(risk, spend, country) if {
	risk >= 0
	risk <= 100
	spend >= 0
	spend <= 10000000
	country in {"LOW", "MEDIUM", "HIGH"}
}

# O3
outcome_for(risk, spend, country) := escalation_result if {
	readable_assignment(risk, spend, country)
	country == "HIGH"
	spend > 2000000
# O2
} else := review_result if {
	readable_assignment(risk, spend, country)
	critical_supplier_status == "yes"
# D3
} else := reject_result if {
	readable_assignment(risk, spend, country)
	risk >= 90
# D4
} else := reject_result if {
	readable_assignment(risk, spend, country)
	country == "HIGH"
	risk >= 70
# D5
} else := reject_result if {
	readable_assignment(risk, spend, country)
	prior_enforcement_status == "yes"
# D6a
} else := approve_result if {
	readable_assignment(risk, spend, country)
	prior_enforcement_status != "yes"
	country == "LOW"
	risk < 40
	spend <= 500000
# D6b: insurance available
} else := approve_result if {
	readable_assignment(risk, spend, country)
	prior_enforcement_status != "yes"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_status == "present"
# D6b: insurance absent
} else := enhanced_review_result if {
	readable_assignment(risk, spend, country)
	prior_enforcement_status != "yes"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_status == "absent"
# D6b: insurance availability unreported
} else := unknown_result if {
	readable_assignment(risk, spend, country)
	prior_enforcement_status != "yes"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_status == "unreported"
# D6c, as modified by O1
} else := approve_result if {
	readable_assignment(risk, spend, country)
	prior_enforcement_status != "yes"
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	new_vendor_status != "yes"
# D7
} else := approve_result if {
	readable_assignment(risk, spend, country)
	prior_enforcement_status != "yes"
	country == "MEDIUM"
	risk < 40
	spend <= 100000
# D8
} else := review_result if {
	readable_assignment(risk, spend, country)
}
