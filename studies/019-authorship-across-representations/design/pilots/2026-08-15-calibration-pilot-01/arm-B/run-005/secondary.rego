package study_test

import data.study

test_vendor_policy_cases[name] if {
	some name, tc in cases
	actual := study.decision with input as tc.input
	actual == tc.want
}

cases := {
	"p1_absent_preempts_everything": {
		"input": {
			"vendor": {
				"riskScore": 100,
				"requestedSpend": 3000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "absent"},
		},
		"want": {"disposition": "unresolved", "reasons": ["missing-required-evidence"]},
	},
	"p1_unreported_preempts_match": {
		"input": {
			"vendor": {"sanctionsStatus": "MATCH"},
			"evidence": {"insurance-certificate": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"match_rejects_without_other_readable_fields": {
		"input": {
			"vendor": {"sanctionsStatus": "MATCH"},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"match_rejects_critical_supplier": {
		"input": {
			"vendor": {
				"sanctionsStatus": "MATCH",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"unknown_sanctions_gives_no_match": {
		"input": {
			"vendor": {
				"riskScore": 100,
				"requestedSpend": 3000000.00,
				"sanctionsStatus": "UNKNOWN",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["no-match"]},
	},
	"o3_beats_o2_and_rejections": {
		"input": {
			"vendor": {
				"riskScore": 100,
				"requestedSpend": 2000000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["exception-escalation"]},
	},
	"o3_does_not_apply_at_two_million": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 2000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "no",
				"priorEnforcement": "no",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"o2_replaces_approval": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"o2_replaces_d3_rejection": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"o2_replaces_prior_action_rejection": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"o2_replaces_d6b_enhanced_review": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 1000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"o2_replaces_d6b_unreported_insurance": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 1000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"unreported_critical_supplier_means_no": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d3_starts_at_90": {
		"input": {
			"vendor": {
				"riskScore": 90,
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"d3_does_not_reach_89": {
		"input": {
			"vendor": {
				"riskScore": 89,
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"d4_starts_at_70": {
		"input": {
			"vendor": {
				"riskScore": 70,
				"requestedSpend": 2000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"d4_does_not_reach_69": {
		"input": {
			"vendor": {
				"riskScore": 69,
				"requestedSpend": 2000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"d5_rejects_prior_action": {
		"input": {
			"vendor": {
				"riskScore": 0,
				"requestedSpend": 0.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"unreported_prior_action_means_no": {
		"input": {
			"vendor": {
				"riskScore": 0,
				"requestedSpend": 0.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d6a_includes_500000_and_ignores_new_vendor": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 500000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d6b_present_insurance_approves": {
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
		"want": {"disposition": "approve", "reasons": []},
	},
	"d6b_absent_insurance_enhanced_review": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 500000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"want": {"disposition": "enhanced-review", "reasons": []},
	},
	"d6b_unreported_insurance_is_unknown": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 500000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"d6b_includes_two_million": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 2000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"want": {"disposition": "enhanced-review", "reasons": []},
	},
	"low_country_above_d6b_reviews": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 2000000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "present",
			},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"d6c_starts_at_risk_40": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "no",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d6c_reaches_risk_69": {
		"input": {
			"vendor": {
				"riskScore": 69,
				"requestedSpend": 100000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "no",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d6c_stops_above_100000": {
		"input": {
			"vendor": {
				"riskScore": 69,
				"requestedSpend": 100000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "no",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"d6c_stops_at_risk_70": {
		"input": {
			"vendor": {
				"riskScore": 70,
				"requestedSpend": 100000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "no",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"o1_suspends_d6c": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"unreported_new_vendor_does_not_suspend_d6c": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d7_includes_its_boundaries": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 100000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d7_stops_at_risk_40": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"d7_stops_above_100000": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 100000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"u1_missing_risk_is_ambiguous": {
		"input": {
			"vendor": {
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_missing_risk_still_rejects_prior_action": {
		"input": {
			"vendor": {
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"u1_worked_example_one": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 1000000.00,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"u1_worked_example_two": {
		"input": {
			"vendor": {
				"riskScore": 50,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "no",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_worked_example_three": {
		"input": {
			"vendor": {
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"u1_worked_example_four": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_missing_risk_still_escalates_o3": {
		"input": {
			"vendor": {
				"requestedSpend": 3000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["exception-escalation"]},
	},
	"u1_missing_spend_all_reviews_at_low_risk_80": {
		"input": {
			"vendor": {
				"riskScore": 80,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"u1_missing_spend_is_ambiguous_at_low_risk_20": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "present",
			},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_missing_spend_all_reviews_at_medium_risk_50": {
		"input": {
			"vendor": {
				"riskScore": 50,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"u1_missing_country_can_approve_or_review": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 50000.00,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_missing_country_all_review": {
		"input": {
			"vendor": {
				"riskScore": 50,
				"requestedSpend": 200000.00,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"u1_missing_country_can_reject_or_escalate": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 3000000.00,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_critical_missing_country_at_two_million_reviews": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 2000000.00,
				"sanctionsStatus": "CLEAR",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"u1_critical_missing_country_above_two_million_is_ambiguous": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 2000000.01,
				"sanctionsStatus": "CLEAR",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_critical_low_country_missing_spend_reviews": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"u1_critical_high_country_missing_spend_is_ambiguous": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_prior_action_missing_country_below_o3_threshold_rejects": {
		"input": {
			"vendor": {
				"requestedSpend": 1000000.00,
				"sanctionsStatus": "CLEAR",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"u1_prior_action_missing_country_above_o3_threshold_is_ambiguous": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 3000000.00,
				"sanctionsStatus": "CLEAR",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_all_three_readability_inputs_missing_is_unknown": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
}
