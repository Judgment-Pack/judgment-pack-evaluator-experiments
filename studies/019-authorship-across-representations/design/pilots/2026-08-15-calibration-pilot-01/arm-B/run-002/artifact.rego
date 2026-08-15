package study

vendor := object.get(input, "vendor", {})

evidence := object.get(input, "evidence", {})

financial_evidence_status := object.get(evidence, "financial-evidence", "unreported")

insurance_status := object.get(evidence, "insurance-certificate", "unreported")

sanctions_status := object.get(vendor, "sanctionsStatus", "UNREPORTED")

new_vendor_status := object.get(vendor, "newVendor", "no")

critical_supplier_status := object.get(vendor, "criticalSupplier", "no")

prior_enforcement_status := object.get(vendor, "priorEnforcement", "no")

approve_result := {
	"disposition": "approve",
	"reasons": [],
}

review_result := {
	"disposition": "review",
	"reasons": [],
}

enhanced_review_result := {
	"disposition": "enhanced-review",
	"reasons": [],
}

reject_result := {
	"disposition": "reject",
	"reasons": [],
}

missing_required_evidence_result := {
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

decision := missing_required_evidence_result if {
	financial_evidence_status == "absent"
} else := unknown_result if {
	financial_evidence_status != "present"
} else := reject_result if {
	sanctions_status == "MATCH"
} else := no_match_result if {
	sanctions_status == "UNKNOWN"
} else := clear_decision if {
	sanctions_status == "CLEAR"
} else := no_match_result if {
	true
}

clear_decision := result if {
	count(possible_outcomes) == 1
	some result in possible_outcomes
} else := unknown_result if {
	true
}

possible_outcomes contains result if {
	some risk in possible_risks
	some spend in possible_spends
	some country in possible_countries
	result := outcome_for(risk, spend, country)
}

# These representatives cover all policy-equivalent risk intervals:
# 0–39, 40–69, 70–89, and 90–100.
possible_risks contains risk if {
	risk := object.get(vendor, "riskScore", -1)
	risk != -1
}

possible_risks contains risk if {
	object.get(vendor, "riskScore", -1) == -1
	some risk in [0, 40, 70, 90]
}

# These representatives cover all policy-equivalent spend intervals:
# <=100,000; >100,000–500,000; >500,000–2,000,000; and >2,000,000.
possible_spends contains spend if {
	spend := object.get(vendor, "requestedSpend", -1)
	spend != -1
}

possible_spends contains spend if {
	object.get(vendor, "requestedSpend", -1) == -1
	some spend in [100000, 500000, 2000000, 10000000]
}

possible_countries contains country if {
	country := object.get(vendor, "countryRisk", "")
	country != ""
}

possible_countries contains country if {
	object.get(vendor, "countryRisk", "") == ""
	some country in ["LOW", "MEDIUM", "HIGH"]
}

readable_assignment(risk, spend, country) if {
	risk >= 0
	risk <= 100
	spend >= 0
	spend <= 10000000
	country in {"LOW", "MEDIUM", "HIGH"}
}

outcome_for(risk, spend, country) := exception_escalation_result if {
	readable_assignment(risk, spend, country)
	country == "HIGH"
	spend > 2000000
} else := review_result if {
	readable_assignment(risk, spend, country)
	critical_supplier_status == "yes"
} else := reject_result if {
	readable_assignment(risk, spend, country)
	risk >= 90
} else := reject_result if {
	readable_assignment(risk, spend, country)
	country == "HIGH"
	risk >= 70
} else := reject_result if {
	readable_assignment(risk, spend, country)
	prior_enforcement_status == "yes"
} else := approve_result if {
	readable_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend <= 500000
} else := approve_result if {
	readable_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_status == "present"
} else := enhanced_review_result if {
	readable_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_status == "absent"
} else := unknown_result if {
	readable_assignment(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_status == "unreported"
} else := approve_result if {
	readable_assignment(risk, spend, country)
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	new_vendor_status != "yes"
} else := approve_result if {
	readable_assignment(risk, spend, country)
	country == "MEDIUM"
	risk < 40
	spend <= 100000
} else := review_result if {
	readable_assignment(risk, spend, country)
}
