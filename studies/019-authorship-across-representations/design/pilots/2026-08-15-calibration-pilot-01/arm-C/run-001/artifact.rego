package study

default decision := {"disposition": "unresolved", "reasons": ["no-match"]}

vendor := object.get(input, "vendor", {})
evidence := object.get(input, "evidence", {})

has_vendor_field(field) if {
	field in object.keys(vendor)
}

has_evidence_field(field) if {
	field in object.keys(evidence)
}

financial_evidence_absent if {
	evidence["financial-evidence"] == "absent"
}

financial_evidence_unreported if {
	not has_evidence_field("financial-evidence")
}

financial_evidence_present if {
	evidence["financial-evidence"] == "present"
}

insurance_certificate_present if {
	evidence["insurance-certificate"] == "present"
}

insurance_certificate_absent if {
	evidence["insurance-certificate"] == "absent"
}

insurance_certificate_unreported if {
	not has_evidence_field("insurance-certificate")
}

critical_supplier if {
	vendor.criticalSupplier == "yes"
}

prior_enforcement if {
	vendor.priorEnforcement == "yes"
}

new_vendor if {
	vendor.newVendor == "yes"
}

# These representatives cover every risk interval separated by a policy
# threshold. Risk scores are integers.
risk_values := [vendor.riskScore] if {
	has_vendor_field("riskScore")
} else := [0, 40, 70, 90] if {
	not has_vendor_field("riskScore")
}

# These representatives cover every spend interval separated by a policy
# threshold. Spend has cents precision.
spend_values := [vendor.requestedSpend] if {
	has_vendor_field("requestedSpend")
} else := [0, 100000.01, 500000.01, 2000000.01] if {
	not has_vendor_field("requestedSpend")
}

country_values := [vendor.countryRisk] if {
	has_vendor_field("countryRisk")
} else := ["LOW", "MEDIUM", "HIGH"] if {
	not has_vendor_field("countryRisk")
}

readable_completion(risk, spend, country) if {
	risk >= 0
	risk <= 100
	spend >= 0
	spend <= 10000000
	country in {"LOW", "MEDIUM", "HIGH"}
}

# Evaluation of a fully readable case with financial evidence available and
# sanctions CLEAR. The else chain makes clause precedence explicit.
readable_outcome(risk, spend, country) := "exception-escalation" if {
	readable_completion(risk, spend, country)
	country == "HIGH"
	spend > 2000000
} else := "review" if {
	readable_completion(risk, spend, country)
	critical_supplier
} else := "reject" if {
	readable_completion(risk, spend, country)
	risk >= 90
} else := "reject" if {
	readable_completion(risk, spend, country)
	country == "HIGH"
	risk >= 70
} else := "reject" if {
	readable_completion(risk, spend, country)
	prior_enforcement
} else := "approve" if {
	readable_completion(risk, spend, country)
	country == "LOW"
	risk < 40
	spend <= 500000
} else := "approve" if {
	readable_completion(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_certificate_present
} else := "enhanced-review" if {
	readable_completion(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_certificate_absent
} else := "unknown" if {
	readable_completion(risk, spend, country)
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	insurance_certificate_unreported
} else := "approve" if {
	readable_completion(risk, spend, country)
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	not new_vendor
} else := "approve" if {
	readable_completion(risk, spend, country)
	country == "MEDIUM"
	risk < 40
	spend <= 100000
} else := "review" if {
	readable_completion(risk, spend, country)
}

possible_outcomes contains outcome if {
	some risk in risk_values
	some spend in spend_values
	some country in country_values
	outcome := readable_outcome(risk, spend, country)
}

outcome_results := {
	"approve": {
		"disposition": "approve",
		"reasons": [],
	},
	"review": {
		"disposition": "review",
		"reasons": [],
	},
	"enhanced-review": {
		"disposition": "enhanced-review",
		"reasons": [],
	},
	"reject": {
		"disposition": "reject",
		"reasons": [],
	},
	"unknown": {
		"disposition": "unresolved",
		"reasons": ["unknown"],
	},
	"exception-escalation": {
		"disposition": "unresolved",
		"reasons": ["exception-escalation"],
	},
}

decision := {
	"disposition": "unresolved",
	"reasons": ["missing-required-evidence"],
} if {
	financial_evidence_absent
} else := {
	"disposition": "unresolved",
	"reasons": ["unknown"],
} if {
	financial_evidence_unreported
} else := {
	"disposition": "reject",
	"reasons": [],
} if {
	financial_evidence_present
	vendor.sanctionsStatus == "MATCH"
} else := {
	"disposition": "unresolved",
	"reasons": ["no-match"],
} if {
	financial_evidence_present
	vendor.sanctionsStatus == "UNKNOWN"
} else := result if {
	financial_evidence_present
	vendor.sanctionsStatus == "CLEAR"
	count(possible_outcomes) == 1
	some outcome in possible_outcomes
	result := outcome_results[outcome]
} else := {
	"disposition": "unresolved",
	"reasons": ["unknown"],
} if {
	financial_evidence_present
	vendor.sanctionsStatus == "CLEAR"
	count(possible_outcomes) > 1
}
