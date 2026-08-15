package study_test

import data.study

want_approve := {"disposition": "approve", "reasons": []}
want_review := {"disposition": "review", "reasons": []}
want_enhanced_review := {"disposition": "enhanced-review", "reasons": []}
want_reject := {"disposition": "reject", "reasons": []}
want_missing_evidence := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]}
want_unknown := {"disposition": "unresolved", "reasons": ["unknown"]}
want_no_match := {"disposition": "unresolved", "reasons": ["no-match"]}
want_escalation := {"disposition": "unresolved", "reasons": ["exception-escalation"]}

cases := {
	# P1.
	"p1_absent_precedes_match": {
		"input": {
			"vendor": {"sanctionsStatus": "MATCH"},
			"evidence": {"financial-evidence": "absent"},
		},
		"want": want_missing_evidence,
	},
	"p1_absent_precedes_o3_o2_and_rejections": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 3000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "absent"},
		},
		"want": want_missing_evidence,
	},
	"p1_unreported_precedes_match": {
		"input": {
			"vendor": {"sanctionsStatus": "MATCH"},
			"evidence": {"insurance-certificate": "present"},
		},
		"want": want_unknown,
	},
	"empty_input_has_unknown_financial_evidence": {
		"input": {},
		"want": want_unknown,
	},

	# Sanctions.
	"match_rejects_despite_critical_and_unreadable_core": {
		"input": {
			"vendor": {
				"sanctionsStatus": "MATCH",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_reject,
	},
	"unknown_sanctions_is_no_match_despite_unreadable_core": {
		"input": {
			"vendor": {
				"sanctionsStatus": "UNKNOWN",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_no_match,
	},

	# O3 and O2.
	"o3_precedes_o2_d3_and_d5": {
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
		"want": want_escalation,
	},
	"o3_does_not_apply_at_two_million": {
		"input": {
			"vendor": {
				"riskScore": 0,
				"requestedSpend": 2000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},
	"o3_does_not_apply_in_medium_country": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 3000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_reject,
	},
	"o2_precedes_d3_and_d5": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},
	"o2_precedes_d6b_enhanced_review": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 600000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"want": want_review,
	},
	"o2_precedes_d6b_unreported_insurance": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 600000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},
	"o2_applies_in_high_country_at_exactly_two_million": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 2000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},

	# D3-D5.
	"d3_rejects_at_90": {
		"input": {
			"vendor": {
				"riskScore": 90,
				"requestedSpend": 0,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_reject,
	},
	"d3_does_not_reject_at_89": {
		"input": {
			"vendor": {
				"riskScore": 89,
				"requestedSpend": 100000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},
	"d4_rejects_high_country_at_70": {
		"input": {
			"vendor": {
				"riskScore": 70,
				"requestedSpend": 2000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_reject,
	},
	"d4_does_not_reject_high_country_at_69": {
		"input": {
			"vendor": {
				"riskScore": 69,
				"requestedSpend": 100000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},
	"d5_prior_enforcement_rejects": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_reject,
	},

	# D6.
	"d6a_includes_500000_and_ignores_insurance_and_new_status": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 500000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "yes",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"want": want_approve,
	},
	"d6b_starts_one_cent_above_500000": {
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
		"want": want_approve,
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
		"want": want_approve,
	},
	"d6b_absent_insurance_is_enhanced_review": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 600000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "yes",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"want": want_enhanced_review,
	},
	"d6b_unreported_insurance_is_unknown": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 600000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_unknown,
	},
	"d6b_does_not_apply_at_risk_40": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 600000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"want": want_review,
	},
	"d6b_does_not_apply_above_two_million": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"requestedSpend": 2000000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "present",
			},
		},
		"want": want_review,
	},
	"d6c_includes_risk_40_and_spend_100000": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_approve,
	},
	"d6c_includes_risk_69": {
		"input": {
			"vendor": {
				"riskScore": 69,
				"requestedSpend": 100000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_approve,
	},
	"d6c_excludes_one_cent_above_100000": {
		"input": {
			"vendor": {
				"riskScore": 69,
				"requestedSpend": 100000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},
	"d6c_excludes_risk_70": {
		"input": {
			"vendor": {
				"riskScore": 70,
				"requestedSpend": 100000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
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
		"want": want_review,
	},

	# D7 and D8.
	"d7_includes_risk_39_and_spend_100000": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 100000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_approve,
	},
	"d7_excludes_one_cent_above_100000": {
		"input": {
			"vendor": {
				"riskScore": 39,
				"requestedSpend": 100000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},
	"d7_excludes_risk_40": {
		"input": {
			"vendor": {
				"riskScore": 40,
				"requestedSpend": 100000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},

	# U1 worked examples and invariant cases.
	"u1_unreadable_country_risk_95_spend_one_million_rejects": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 1000000,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_reject,
	},
	"u1_unreadable_spend_high_country_risk_50_is_unknown": {
		"input": {
			"vendor": {
				"riskScore": 50,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_unknown,
	},
	"u1_unreadable_risk_critical_low_country_is_review": {
		"input": {
			"vendor": {
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},
	"u1_unreadable_country_and_spend_critical_is_unknown": {
		"input": {
			"vendor": {
				"riskScore": 20,
				"sanctionsStatus": "CLEAR",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_unknown,
	},
	"u1_unreadable_risk_does_not_displace_fixed_o3": {
		"input": {
			"vendor": {
				"requestedSpend": 2000000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_escalation,
	},
	"u1_unreadable_risk_is_stably_rejected_by_prior_action": {
		"input": {
			"vendor": {
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_reject,
	},
	"u1_unreadable_risk_with_varying_outcomes_is_unknown": {
		"input": {
			"vendor": {
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_unknown,
	},
	"u1_unreadable_spend_low_country_risk_70_is_review": {
		"input": {
			"vendor": {
				"riskScore": 70,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},
	"u1_unreadable_spend_high_country_risk_95_is_unknown": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_unknown,
	},
	"u1_unreadable_country_risk_50_spend_200000_is_review": {
		"input": {
			"vendor": {
				"riskScore": 50,
				"requestedSpend": 200000,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},
	"u1_unreadable_country_risk_75_can_review_or_reject": {
		"input": {
			"vendor": {
				"riskScore": 75,
				"requestedSpend": 100,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_unknown,
	},
	"u1_unreadable_country_above_two_million_can_reject_or_escalate": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 2000000.01,
				"sanctionsStatus": "CLEAR",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_unknown,
	},
	"u1_unreadable_country_critical_at_two_million_is_review": {
		"input": {
			"vendor": {
				"riskScore": 95,
				"requestedSpend": 2000000,
				"sanctionsStatus": "CLEAR",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_review,
	},
	"u1_all_core_inputs_unreadable_clear_is_unknown": {
		"input": {
			"vendor": {"sanctionsStatus": "CLEAR"},
			"evidence": {"financial-evidence": "present"},
		},
		"want": want_unknown,
	},
}

test_policy_case[name] if {
	some name, test_case in cases
	actual := study.decision with input as test_case.input
	actual == test_case.want
}
