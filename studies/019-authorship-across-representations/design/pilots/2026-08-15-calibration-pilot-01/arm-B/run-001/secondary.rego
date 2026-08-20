package study_test

import data.study

approve_result := {"disposition": "approve", "reasons": []}
review_result := {"disposition": "review", "reasons": []}
enhanced_review_result := {"disposition": "enhanced-review", "reasons": []}
reject_result := {"disposition": "reject", "reasons": []}
missing_evidence_result := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]}
unknown_result := {"disposition": "unresolved", "reasons": ["unknown"]}
no_match_result := {"disposition": "unresolved", "reasons": ["no-match"]}
escalation_result := {"disposition": "unresolved", "reasons": ["exception-escalation"]}

cases := {
	"p1_absent_preempts_match": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 3000000.00,
				"sanctionsStatus": "MATCH",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "absent"},
		},
		"want": missing_evidence_result,
	},
	"p1_absent_preempts_clear_escalation": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 3000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "absent"},
		},
		"want": missing_evidence_result,
	},
	"p1_unreported_is_unknown": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"insurance-certificate": "present"},
		},
		"want": unknown_result,
	},
	"d1_match_ignores_unreadable_inputs_and_critical_status": {
		"input": {
			"vendor": {
				"sanctionsStatus": "MATCH",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": reject_result,
	},
	"d2_unknown_screening_ignores_unreadable_inputs": {
		"input": {
			"vendor": {
				"sanctionsStatus": "UNKNOWN",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": no_match_result,
	},
	"o3_starts_above_2000000_and_preempts_everything": {
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
		"want": escalation_result,
	},
	"o3_does_not_include_2000000": {
		"input": {
			"vendor": {
				"riskScore": 50,
				"requestedSpend": 2000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": review_result,
	},
	"o2_preempts_d3_d4_and_d5": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 2000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": review_result,
	},
	"o2_preempts_d6b_enhanced_review": {
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
		"want": review_result,
	},
	"o2_preempts_d6b_unreported_insurance": {
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
		"want": review_result,
	},
	"d3_rejects_at_90": {
		"input": {
			"vendor": {
				"riskScore": 90,
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": reject_result,
	},
	"d3_does_not_reject_at_89": {
		"input": {
			"vendor": {
				"riskScore": 89,
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": review_result,
	},
	"d4_rejects_at_70": {
		"input": {
			"vendor": {
				"riskScore": 70,
				"requestedSpend": 2000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": reject_result,
	},
	"d4_does_not_reject_at_69": {
		"input": {
			"vendor": {
				"riskScore": 69,
				"requestedSpend": 2000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": review_result,
	},
	"d5_prior_enforcement_rejects": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"requestedSpend": 10.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": reject_result,
	},
	"d6a_includes_500000_and_does_not_require_insurance": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 500000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "yes",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"want": approve_result,
	},
	"d6b_approves_just_above_500000_with_insurance": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 500000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "yes",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "present",
			},
		},
		"want": approve_result,
	},
	"d6b_absent_insurance_is_enhanced_review_at_upper_bound": {
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
		"want": enhanced_review_result,
	},
	"d6b_unreported_insurance_is_unknown": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 1000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": unknown_result,
	},
	"d6b_does_not_extend_above_2000000": {
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
		"want": review_result,
	},
	"d6c_includes_risk_40_and_spend_100000": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": approve_result,
	},
	"d6c_includes_risk_69": {
		"input": {
			"vendor": {
				"riskScore": 69,
				"requestedSpend": 100000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": approve_result,
	},
	"o1_suspends_d6c_for_new_vendor": {
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
		"want": review_result,
	},
	"d6c_excludes_spend_above_100000": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": review_result,
	},
	"d7_includes_risk_39_and_spend_100000": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 100000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": approve_result,
	},
	"d7_excludes_risk_40": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": review_result,
	},
	"d7_excludes_spend_above_100000": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 100000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": review_result,
	},
	"u1_worked_example_1": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 1000000.00,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": reject_result,
	},
	"u1_worked_example_2": {
		"input": {
			"vendor": {
				"riskScore": 50,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": unknown_result,
	},
	"u1_worked_example_3": {
		"input": {
			"vendor": {
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": review_result,
	},
	"u1_worked_example_4": {
		"input": {
			"vendor": {
				"riskScore": 10,
				"sanctionsStatus": "CLEAR",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": unknown_result,
	},
	"u1_o3_does_not_depend_on_unreadable_risk": {
		"input": {
			"vendor": {
				"requestedSpend": 3000000.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": escalation_result,
	},
	"u1_unreadable_risk_can_change_low_country_outcome": {
		"input": {
			"vendor": {
				"requestedSpend": 100.00,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": unknown_result,
	},
	"u1_d3_rejection_does_not_depend_on_unreadable_spend_in_low_country": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": reject_result,
	},
	"u1_unreadable_country_always_reviews_for_risk_50_and_spend_200000": {
		"input": {
			"vendor": {
				"riskScore": 50,
				"requestedSpend": 200000.00,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": review_result,
	},
	"u1_unreadable_country_changes_low_risk_small_spend_outcome": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 50000.00,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": unknown_result,
	},
	"u1_unreadable_country_can_change_rejection_to_escalation": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 3000000.00,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": unknown_result,
	},
	"u1_prior_action_always_rejects_with_low_country": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": reject_result,
	},
	"u1_new_vendor_risk_50_always_reviews_with_low_country": {
		"input": {
			"vendor": {
				"riskScore": 50,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": review_result,
	},
	"u1_critical_supplier_with_unreadable_country_still_reviews_below_o3": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 1000000.00,
				"sanctionsStatus": "CLEAR",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": review_result,
	},
	"u1_critical_supplier_with_high_country_and_unreadable_spend_can_escalate": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": unknown_result,
	},
}

test_vendor_approval_policy[name] if {
	some name, tc in cases
	actual := study.decision with input as tc.input
	actual == tc.want
}
