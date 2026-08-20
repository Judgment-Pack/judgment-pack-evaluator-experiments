package study

approve_result := {"disposition": "approve", "reasons": []}
review_result := {"disposition": "review", "reasons": []}
enhanced_review_result := {"disposition": "enhanced-review", "reasons": []}
reject_result := {"disposition": "reject", "reasons": []}
missing_evidence_result := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]}
unknown_result := {"disposition": "unresolved", "reasons": ["unknown"]}
no_match_result := {"disposition": "unresolved", "reasons": ["no-match"]}
escalation_result := {"disposition": "unresolved", "reasons": ["exception-escalation"]}

financial_evidence_status := object.get(input, ["evidence", "financial-evidence"], "unreported")
insurance_status := object.get(input, ["evidence", "insurance-certificate"], "unreported")
sanctions_status := object.get(input, ["vendor", "sanctionsStatus"], "unreported")
new_vendor_status := object.get(input, ["vendor", "newVendor"], "no")
critical_supplier_status := object.get(input, ["vendor", "criticalSupplier"], "no")
prior_enforcement_status := object.get(input, ["vendor", "priorEnforcement"], "no")

# The representatives below cover every interval on which policy behavior is
# constant. This makes the U1 universal test finite without changing its result.
candidate_risks contains risk if {
	risk := object.get(input, ["vendor", "riskScore"], -1)
	risk >= 0
}

candidate_risks contains risk if {
	object.get(input, ["vendor", "riskScore"], -1) == -1
	some risk in {0, 40, 70, 90}
}

candidate_spends contains spend if {
	spend := object.get(input, ["vendor", "requestedSpend"], -1)
	spend >= 0
}

candidate_spends contains spend if {
	object.get(input, ["vendor", "requestedSpend"], -1) == -1
	some spend in {0, 100000.01, 500000.01, 2000000.01}
}

candidate_countries contains country if {
	country := object.get(input, ["vendor", "countryRisk"], "")
	country != ""
}

candidate_countries contains country if {
	object.get(input, ["vendor", "countryRisk"], "") == ""
	some country in {"LOW", "MEDIUM", "HIGH"}
}

valid_readable_facts(facts) if {
	facts.risk >= 0
	facts.risk <= 100
	facts.spend >= 0
	facts.spend <= 10000000
	facts.country in {"LOW", "MEDIUM", "HIGH"}
}

# O3, then O2, then D3-D8.
readable_outcome(facts) := escalation_result if {
	valid_readable_facts(facts)
	facts.country == "HIGH"
	facts.spend > 2000000
} else := review_result if {
	valid_readable_facts(facts)
	critical_supplier_status == "yes"
} else := reject_result if {
	valid_readable_facts(facts)
	facts.risk >= 90
} else := reject_result if {
	valid_readable_facts(facts)
	facts.country == "HIGH"
	facts.risk >= 70
} else := reject_result if {
	valid_readable_facts(facts)
	prior_enforcement_status == "yes"
} else := approve_result if {
	valid_readable_facts(facts)
	facts.country == "LOW"
	facts.risk < 40
	facts.spend <= 500000
} else := approve_result if {
	valid_readable_facts(facts)
	facts.country == "LOW"
	facts.risk < 40
	facts.spend > 500000
	facts.spend <= 2000000
	insurance_status == "present"
} else := enhanced_review_result if {
	valid_readable_facts(facts)
	facts.country == "LOW"
	facts.risk < 40
	facts.spend > 500000
	facts.spend <= 2000000
	insurance_status == "absent"
} else := unknown_result if {
	valid_readable_facts(facts)
	facts.country == "LOW"
	facts.risk < 40
	facts.spend > 500000
	facts.spend <= 2000000
	insurance_status == "unreported"
} else := approve_result if {
	valid_readable_facts(facts)
	facts.country == "LOW"
	facts.risk >= 40
	facts.risk < 70
	facts.spend <= 100000
	new_vendor_status == "no"
} else := approve_result if {
	valid_readable_facts(facts)
	facts.country == "MEDIUM"
	facts.risk < 40
	facts.spend <= 100000
} else := review_result if {
	valid_readable_facts(facts)
}

candidate_outcomes contains result if {
	some risk in candidate_risks
	some spend in candidate_spends
	some country in candidate_countries
	result := readable_outcome({
		"risk": risk,
		"spend": spend,
		"country": country,
	})
}

# P1.
decision := missing_evidence_result if {
	financial_evidence_status == "absent"
}

decision := unknown_result if {
	financial_evidence_status == "unreported"
}

# D1 and D2 stand independently of unreadable risk, spend, or country.
decision := reject_result if {
	financial_evidence_status == "present"
	sanctions_status == "MATCH"
}

decision := no_match_result if {
	financial_evidence_status == "present"
	sanctions_status == "UNKNOWN"
}

# CLEAR cases, including U1.
decision := result if {
	financial_evidence_status == "present"
	sanctions_status == "CLEAR"
	count(candidate_outcomes) == 1
	some result in candidate_outcomes
}

decision := unknown_result if {
	financial_evidence_status == "present"
	sanctions_status == "CLEAR"
	count(candidate_outcomes) > 1
}
