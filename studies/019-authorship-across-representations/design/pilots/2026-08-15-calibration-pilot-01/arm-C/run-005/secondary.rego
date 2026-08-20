package study_test

import data.study

expected_approve := {"disposition": "approve", "reasons": []}
expected_review := {"disposition": "review", "reasons": []}
expected_enhanced_review := {"disposition": "enhanced-review", "reasons": []}
expected_reject := {"disposition": "reject", "reasons": []}
expected_missing_evidence := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]}
expected_unknown := {"disposition": "unresolved", "reasons": ["unknown"]}
expected_no_match := {"disposition": "unresolved", "reasons": ["no-match"]}
expected_escalation := {"disposition": "unresolved", "reasons": ["exception-escalation"]}

cases := {
	"all_members_omitted_is_unknown_at_p1": {
		"input": {},
		"expected": expected_unknown,
	},
	"p1_absent_preempts_everything": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 3000000,
				"sanctionsStatus": "MATCH",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "absent"},
		},
		"expected": expected_missing_evidence,
	},
	"p1_unreported_preempts_clear_escalation": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 3000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"insurance-certificate": "present"},
		},
		"expected": expected_unknown,
	},
	"sanctions_match_rejects_critical_supplier": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 3000000,
				"sanctionsStatus": "MATCH",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_reject,
	},
	"sanctions_unknown_is_no_match": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 100,
				"sanctionsStatus": "UNKNOWN",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_no_match,
	},
	"o3_preempts_o2_and_rejections": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 2000000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_escalation,
	},
	"o3_does_not_apply_at_two_million": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 2000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_reject,
	},
	"o2_replaces_approval": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"o2_replaces_rejection": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 2000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"o2_replaces_enhanced_review": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 1000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"expected": expected_review,
	},
	"o2_replaces_unreported_insurance_limb": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 1000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"d3_starts_at_ninety": {
		"input": {
			"vendor": {
				"riskScore": 90,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_reject,
	},
	"d3_below_ninety_falls_through": {
		"input": {
			"vendor": {
				"riskScore": 89,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"d4_starts_at_seventy": {
		"input": {
			"vendor": {
				"riskScore": 70,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_reject,
	},
	"d4_below_seventy_reviews": {
		"input": {
			"vendor": {
				"riskScore": 69,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"d5_prior_enforcement_rejects": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_reject,
	},
	"unreported_prior_enforcement_is_no": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_approve,
	},
	"d6a_includes_five_hundred_thousand": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 500000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_approve,
	},
	"insurance_absent_is_irrelevant_to_d6a": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 500000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"expected": expected_approve,
	},
	"d6b_available_just_above_five_hundred_thousand": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 500000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "present",
			},
		},
		"expected": expected_approve,
	},
	"d6b_absent_is_enhanced_review": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 1000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"expected": expected_enhanced_review,
	},
	"d6b_unreported_is_unknown": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 1000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_unknown,
	},
	"d6b_includes_two_million": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 2000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "present",
			},
		},
		"expected": expected_approve,
	},
	"low_country_above_two_million_reviews": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 2000000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"d6c_starts_at_risk_forty": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "no",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_approve,
	},
	"d6c_includes_risk_sixty_nine": {
		"input": {
			"vendor": {
				"riskScore": 69,
				"requestedSpend": 100000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_approve,
	},
	"o1_suspends_d6c": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"o1_does_not_suspend_d6a": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_approve,
	},
	"d6c_spend_above_limit_reviews": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "no",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"d7_includes_its_upper_boundaries": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 100000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_approve,
	},
	"d7_risk_forty_reviews": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"d7_spend_above_limit_reviews": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 100000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"high_country_low_risk_reviews": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"u1_country_unreadable_d3_rejects": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 1000000,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_reject,
	},
	"u1_spend_unreadable_high_country_is_mixed": {
		"input": {
			"vendor": {
				"riskScore": 50,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_unknown,
	},
	"u1_risk_unreadable_critical_supplier_reviews": {
		"input": {
			"vendor": {
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"u1_country_and_spend_unreadable_critical_supplier_is_mixed": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"sanctionsStatus": "CLEAR",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_unknown,
	},
	"u1_risk_unreadable_noncritical_case_is_mixed": {
		"input": {
			"vendor": {
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_unknown,
	},
	"u1_spend_unreadable_medium_country_is_mixed": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_unknown,
	},
	"u1_country_unreadable_low_risk_case_is_mixed": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_unknown,
	},
	"u1_spend_unreadable_d3_rejects": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_reject,
	},
	"u1_risk_unreadable_o3_escalates": {
		"input": {
			"vendor": {
				"requestedSpend": 3000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_escalation,
	},
	"u1_risk_and_spend_unreadable_o2_reviews": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_review,
	},
	"u1_spend_unreadable_prior_enforcement_is_mixed_in_high_country": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"expected": expected_unknown,
	},
}

test_vendor_approval_cases[name] if {
	some name, test_case in cases
	actual := study.decision with input as test_case.input
	actual == test_case.expected
}
