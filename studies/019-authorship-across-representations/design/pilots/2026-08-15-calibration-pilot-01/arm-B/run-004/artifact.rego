package study

vendor := object.get(input, "vendor", {})
evidence := object.get(input, "evidence", {})

financial_status := object.get(evidence, "financial-evidence", "unreported")
insurance_status := object.get(evidence, "insurance-certificate", "unreported")
sanctions_status := object.get(vendor, "sanctionsStatus", "UNKNOWN")

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

escalation_result := {
	"disposition": "unresolved",
	"reasons": ["exception-escalation"],
}

# Each list contains one representative from every interval in which the
# policy's outcome can differ. A reported value is retained unchanged.
risk_values := [risk_score] if {
	risk_score := object.get(vendor, "riskScore", -1)
	risk_score != -1
}

risk_values := [0, 40, 70, 90] if {
	object.get(vendor, "riskScore", -1) == -1
}

spend_values := [requested_spend] if {
	requested_spend := object.get(vendor, "requestedSpend", -1)
	requested_spend != -1
}

spend_values := [0, 100000.01, 500000.01, 2000000.01] if {
	object.get(vendor, "requestedSpend", -1) == -1
}

country_values := [country_risk] if {
	country_risk := object.get(vendor, "countryRisk", "unreadable")
	country_risk != "unreadable"
}

country_values := ["LOW", "MEDIUM", "HIGH"] if {
	object.get(vendor, "countryRisk", "unreadable") == "unreadable"
}

# This function is called only after P1 is satisfied and sanctions are CLEAR.
# Its else chain implements O3, O2, and D3-D8 in governing order.
readable_outcome(candidate) := escalation_result if {
	candidate.countryRisk == "HIGH"
	candidate.requestedSpend > 2000000
} else := review_result if {
	object.get(candidate, "criticalSupplier", "no") == "yes"
} else := reject_result if {
	candidate.riskScore >= 90
} else := reject_result if {
	candidate.countryRisk == "HIGH"
	candidate.riskScore >= 70
} else := reject_result if {
	object.get(candidate, "priorEnforcement", "no") == "yes"
} else := approve_result if {
	candidate.countryRisk == "LOW"
	candidate.riskScore < 40
	candidate.requestedSpend <= 500000
} else := approve_result if {
	candidate.countryRisk == "LOW"
	candidate.riskScore < 40
	candidate.requestedSpend > 500000
	candidate.requestedSpend <= 2000000
	insurance_status == "present"
} else := enhanced_review_result if {
	candidate.countryRisk == "LOW"
	candidate.riskScore < 40
	candidate.requestedSpend > 500000
	candidate.requestedSpend <= 2000000
	insurance_status == "absent"
} else := unknown_result if {
	candidate.countryRisk == "LOW"
	candidate.riskScore < 40
	candidate.requestedSpend > 500000
	candidate.requestedSpend <= 2000000
	insurance_status == "unreported"
} else := approve_result if {
	candidate.countryRisk == "LOW"
	candidate.riskScore >= 40
	candidate.riskScore < 70
	candidate.requestedSpend <= 100000
	object.get(candidate, "newVendor", "no") != "yes"
} else := approve_result if {
	candidate.countryRisk == "MEDIUM"
	candidate.riskScore < 40
	candidate.requestedSpend <= 100000
} else := review_result if {
	candidate.riskScore >= 0
	candidate.riskScore <= 100
	candidate.requestedSpend >= 0
	candidate.requestedSpend <= 10000000
	candidate.countryRisk in {"LOW", "MEDIUM", "HIGH"}
}

# U1 compares the complete outcomes produced by every relevant readable
# completion. Sets intentionally collapse identical outcomes reached through
# different clauses.
clear_outcomes contains outcome if {
	some risk_score in risk_values
	some requested_spend in spend_values
	some country_risk in country_values

	completed_vendor := object.union(vendor, {
		"riskScore": risk_score,
		"requestedSpend": requested_spend,
		"countryRisk": country_risk,
	})

	outcome := readable_outcome(completed_vendor)
}

# P1
decision := missing_evidence_result if {
	financial_status == "absent"
}

decision := unknown_result if {
	financial_status == "unreported"
}

# D1 and D2 do not depend on the U1-readable dimensions.
decision := reject_result if {
	financial_status == "present"
	sanctions_status == "MATCH"
}

decision := no_match_result if {
	financial_status == "present"
	sanctions_status == "UNKNOWN"
}

# CLEAR with a unanimous readable-completion outcome.
decision := outcome if {
	financial_status == "present"
	sanctions_status == "CLEAR"
	count(clear_outcomes) == 1
	some outcome in clear_outcomes
}

# CLEAR with non-unanimous readable-completion outcomes.
decision := unknown_result if {
	financial_status == "present"
	sanctions_status == "CLEAR"
	count(clear_outcomes) > 1
}
