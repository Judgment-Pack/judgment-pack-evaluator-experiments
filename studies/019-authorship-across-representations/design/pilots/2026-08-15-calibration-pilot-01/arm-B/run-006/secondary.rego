package study_test

import data.study

approve := {"disposition": "approve", "reasons": []}
review := {"disposition": "review", "reasons": []}
enhanced_review := {"disposition": "enhanced-review", "reasons": []}
reject := {"disposition": "reject", "reasons": []}
missing_evidence := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]}
unknown := {"disposition": "unresolved", "reasons": ["unknown"]}
no_match := {"disposition": "unresolved", "reasons": ["no-match"]}
escalation := {"disposition": "unresolved", "reasons": ["exception-escalation"]}

financial_present := {"financial-evidence": "present"}
financial_with_insurance := {
	"financial-evidence": "present",
	"insurance-certificate": "present",
}
financial_without_insurance := {
	"financial-evidence": "present",
	"insurance-certificate": "absent",
}

make_case(vendor_facts, evidence_facts, expected) := result if {
	result := {
		"input": {
			"vendor": vendor_facts,
			"evidence": evidence_facts,
		},
		"want": expected,
	}
}

cases := {
	# P1
	"p1_absent_preempts_o3": make_case(
		{"riskScore": 99, "requestedSpend": 2000000.01, "sanctionsStatus": "CLEAR", "countryRisk": "HIGH", "criticalSupplier": "yes", "priorEnforcement": "yes"},
		{"financial-evidence": "absent"},
		missing_evidence,
	),
	"p1_unreported_preempts_match": make_case(
		{"sanctionsStatus": "MATCH"},
		{},
		unknown,
	),

	# D1 and D2 stand for MATCH and UNKNOWN.
	"d1_match_stands_with_critical_and_unreadables": make_case(
		{"sanctionsStatus": "MATCH", "criticalSupplier": "yes"},
		financial_present,
		reject,
	),
	"d2_unknown_stands_with_critical_and_unreadables": make_case(
		{"sanctionsStatus": "UNKNOWN", "criticalSupplier": "yes"},
		financial_present,
		no_match,
	),

	# O3 and O2
	"o3_precedes_o2_d3_d4_and_d5": make_case(
		{"riskScore": 99, "requestedSpend": 2000000.01, "sanctionsStatus": "CLEAR", "countryRisk": "HIGH", "criticalSupplier": "yes", "priorEnforcement": "yes"},
		financial_present,
		escalation,
	),
	"o3_does_not_apply_at_exactly_2000000": make_case(
		{"riskScore": 95, "requestedSpend": 2000000, "sanctionsStatus": "CLEAR", "countryRisk": "HIGH", "criticalSupplier": "yes"},
		financial_present,
		review,
	),
	"o2_displaces_automatic_approval": make_case(
		{"riskScore": 10, "requestedSpend": 100, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "criticalSupplier": "yes"},
		financial_present,
		review,
	),
	"o2_displaces_d4": make_case(
		{"riskScore": 70, "requestedSpend": 100, "sanctionsStatus": "CLEAR", "countryRisk": "HIGH", "criticalSupplier": "yes"},
		financial_present,
		review,
	),
	"o2_displaces_d5": make_case(
		{"riskScore": 10, "requestedSpend": 100, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "criticalSupplier": "yes", "priorEnforcement": "yes"},
		financial_present,
		review,
	),
	"o2_displaces_d6b_enhanced_review": make_case(
		{"riskScore": 10, "requestedSpend": 1000000, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "criticalSupplier": "yes"},
		financial_without_insurance,
		review,
	),
	"o2_displaces_d6b_unknown": make_case(
		{"riskScore": 10, "requestedSpend": 1000000, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "criticalSupplier": "yes"},
		financial_present,
		review,
	),

	# D3–D5
	"d3_below_90_is_not_automatic_rejection": make_case(
		{"riskScore": 89, "requestedSpend": 100000, "sanctionsStatus": "CLEAR", "countryRisk": "MEDIUM"},
		financial_present,
		review,
	),
	"d3_starts_at_90": make_case(
		{"riskScore": 90, "requestedSpend": 100000, "sanctionsStatus": "CLEAR", "countryRisk": "MEDIUM"},
		financial_present,
		reject,
	),
	"d4_below_70_is_review": make_case(
		{"riskScore": 69, "requestedSpend": 2000000, "sanctionsStatus": "CLEAR", "countryRisk": "HIGH"},
		financial_present,
		review,
	),
	"d4_starts_at_70": make_case(
		{"riskScore": 70, "requestedSpend": 2000000, "sanctionsStatus": "CLEAR", "countryRisk": "HIGH"},
		financial_present,
		reject,
	),
	"d5_prior_enforcement_rejects": make_case(
		{"riskScore": 0, "requestedSpend": 0, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "priorEnforcement": "yes"},
		financial_present,
		reject,
	),

	# D6a and D6b
	"d6a_includes_500000_and_ignores_insurance": make_case(
		{"riskScore": 39, "requestedSpend": 500000, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_without_insurance,
		approve,
	),
	"d6b_starts_above_500000_with_insurance": make_case(
		{"riskScore": 39, "requestedSpend": 500000.01, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_with_insurance,
		approve,
	),
	"d6b_absent_insurance_is_enhanced_review": make_case(
		{"riskScore": 39, "requestedSpend": 500000.01, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_without_insurance,
		enhanced_review,
	),
	"d6b_unreported_insurance_is_unknown": make_case(
		{"riskScore": 39, "requestedSpend": 500000.01, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_present,
		unknown,
	),
	"d6b_includes_2000000": make_case(
		{"riskScore": 39, "requestedSpend": 2000000, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_with_insurance,
		approve,
	),
	"d6b_absent_insurance_at_2000000": make_case(
		{"riskScore": 39, "requestedSpend": 2000000, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_without_insurance,
		enhanced_review,
	),
	"low_country_above_2000000_is_review": make_case(
		{"riskScore": 39, "requestedSpend": 2000000.01, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_with_insurance,
		review,
	),
	"d6b_is_not_suspended_for_new_vendors": make_case(
		{"riskScore": 20, "requestedSpend": 500000.01, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "newVendor": "yes"},
		financial_without_insurance,
		enhanced_review,
	),

	# D6c and O1
	"d6c_includes_risk_40_and_spend_100000": make_case(
		{"riskScore": 40, "requestedSpend": 100000, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_present,
		approve,
	),
	"d6c_includes_risk_69": make_case(
		{"riskScore": 69, "requestedSpend": 100000, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_present,
		approve,
	),
	"d6c_excludes_spend_above_100000": make_case(
		{"riskScore": 40, "requestedSpend": 100000.01, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_present,
		review,
	),
	"o1_suspends_d6c": make_case(
		{"riskScore": 40, "requestedSpend": 100000, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "newVendor": "yes"},
		financial_present,
		review,
	),
	"o1_does_not_suspend_d6a": make_case(
		{"riskScore": 20, "requestedSpend": 500000, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "newVendor": "yes"},
		financial_present,
		approve,
	),

	# D7
	"d7_includes_risk_39_and_spend_100000": make_case(
		{"riskScore": 39, "requestedSpend": 100000, "sanctionsStatus": "CLEAR", "countryRisk": "MEDIUM"},
		financial_present,
		approve,
	),
	"d7_excludes_risk_40": make_case(
		{"riskScore": 40, "requestedSpend": 100000, "sanctionsStatus": "CLEAR", "countryRisk": "MEDIUM"},
		financial_present,
		review,
	),
	"d7_excludes_spend_above_100000": make_case(
		{"riskScore": 39, "requestedSpend": 100000.01, "sanctionsStatus": "CLEAR", "countryRisk": "MEDIUM"},
		financial_present,
		review,
	),

	# U1 worked examples
	"u1_worked_example_1": make_case(
		{"riskScore": 95, "requestedSpend": 1000000, "sanctionsStatus": "CLEAR", "criticalSupplier": "no", "priorEnforcement": "no"},
		financial_present,
		reject,
	),
	"u1_worked_example_2": make_case(
		{"riskScore": 50, "sanctionsStatus": "CLEAR", "countryRisk": "HIGH", "criticalSupplier": "no"},
		financial_present,
		unknown,
	),
	"u1_worked_example_3": make_case(
		{"requestedSpend": 100, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "criticalSupplier": "yes"},
		financial_present,
		review,
	),
	"u1_worked_example_4": make_case(
		{"riskScore": 10, "sanctionsStatus": "CLEAR", "criticalSupplier": "yes"},
		financial_present,
		unknown,
	),

	# Additional U1 invariance and divergence checks
	"u1_missing_spend_can_be_stable_review": make_case(
		{"riskScore": 75, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_present,
		review,
	),
	"u1_missing_risk_can_be_stable_reject": make_case(
		{"requestedSpend": 100, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "priorEnforcement": "yes"},
		financial_present,
		reject,
	),
	"u1_high_country_missing_spend_mixes_rejection_and_escalation": make_case(
		{"riskScore": 95, "sanctionsStatus": "CLEAR", "countryRisk": "HIGH"},
		financial_present,
		unknown,
	),
	"u1_missing_country_mixes_approval_and_review": make_case(
		{"riskScore": 50, "requestedSpend": 50000, "sanctionsStatus": "CLEAR"},
		financial_present,
		unknown,
	),
	"u1_high_exposure_ignores_missing_risk": make_case(
		{"requestedSpend": 2000000.01, "sanctionsStatus": "CLEAR", "countryRisk": "HIGH"},
		financial_present,
		escalation,
	),
	"u1_o1_makes_missing_spend_stable_review": make_case(
		{"riskScore": 50, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "newVendor": "yes"},
		financial_present,
		review,
	),
	"u1_missing_risk_low_small_spend_diverges": make_case(
		{"requestedSpend": 100, "sanctionsStatus": "CLEAR", "countryRisk": "LOW"},
		financial_present,
		unknown,
	),
	"u1_high_exposure_missing_country_diverges": make_case(
		{"riskScore": 95, "requestedSpend": 3000000, "sanctionsStatus": "CLEAR"},
		financial_present,
		unknown,
	),
	"u1_critical_low_missing_spend_is_stable_review": make_case(
		{"riskScore": 10, "sanctionsStatus": "CLEAR", "countryRisk": "LOW", "criticalSupplier": "yes"},
		financial_present,
		review,
	),
}

test_vendor_approval_policy[name] if {
	some name, test_case in cases
	study.decision == test_case.want with input as test_case.input
}
