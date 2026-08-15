package study_test

import data.study

cases := {
	"p1_absent_precedes_everything": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"riskScore": 99,
				"requestedSpend": 3000000,
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "absent"},
		},
		"want": {"disposition": "unresolved", "reasons": ["missing-required-evidence"]},
	},
	"p1_unreported_is_unknown": {
		"input": {
			"vendor": {"sanctionsStatus": "MATCH"},
			"evidence": {"insurance-certificate": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"d1_match_rejects_even_if_critical": {
		"input": {
			"vendor": {
				"sanctionsStatus": "MATCH",
				"countryRisk": "HIGH",
				"requestedSpend": 3000000,
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"d2_unknown_screening_has_no_match": {
		"input": {
			"vendor": {
				"sanctionsStatus": "UNKNOWN",
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["no-match"]},
	},
	"d3_rejects_at_90": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 90,
				"requestedSpend": 0,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"d3_does_not_apply_at_89": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 89,
				"requestedSpend": 0,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"d4_rejects_at_70_in_high_country": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"riskScore": 70,
				"requestedSpend": 100,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"d4_does_not_apply_at_69": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"riskScore": 69,
				"requestedSpend": 100,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"d5_prior_enforcement_rejects": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 0,
				"requestedSpend": 0,
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"d5_unreported_prior_enforcement_is_no": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 0,
				"requestedSpend": 0,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d6a_includes_both_upper_boundaries": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 39,
				"requestedSpend": 500000,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"o1_does_not_suspend_d6a": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 39,
				"requestedSpend": 100,
				"newVendor": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d6b_present_just_above_500k": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 39,
				"requestedSpend": 500000.01,
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "present",
			},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d6b_includes_2m": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 0,
				"requestedSpend": 2000000,
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "present",
			},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d6b_absent_insurance_enhances_review": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 10,
				"requestedSpend": 1000000,
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
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 10,
				"requestedSpend": 1000000,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"d6b_does_not_reach_spend_above_2m": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 10,
				"requestedSpend": 2000000.01,
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "present",
			},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"d6c_includes_40_and_100k": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 40,
				"requestedSpend": 100000,
				"newVendor": "no",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d6c_includes_risk_69": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 69,
				"requestedSpend": 100000,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"o1_suspends_d6c_for_new_vendor": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 40,
				"requestedSpend": 100000,
				"newVendor": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"d6c_excludes_spend_above_100k": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 40,
				"requestedSpend": 100000.01,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"d7_includes_39_and_100k": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
				"riskScore": 39,
				"requestedSpend": 100000,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "approve", "reasons": []},
	},
	"d7_excludes_risk_40": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
				"riskScore": 40,
				"requestedSpend": 100000,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"d7_excludes_spend_above_100k": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
				"riskScore": 39,
				"requestedSpend": 100000.01,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"o2_displaces_automatic_rejection": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 99,
				"requestedSpend": 100,
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"o2_displaces_d6b_enhanced_review": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 10,
				"requestedSpend": 1000000,
				"criticalSupplier": "yes",
			},
			"evidence": {
				"financial-evidence": "present",
				"insurance-certificate": "absent",
			},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"o2_displaces_d6b_unknown_insurance": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 10,
				"requestedSpend": 1000000,
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"o2_applies_at_exactly_2m": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"riskScore": 99,
				"requestedSpend": 2000000,
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"o3_precedes_o2_and_rejections": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"riskScore": 99,
				"requestedSpend": 2000000.01,
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["exception-escalation"]},
	},
	"o3_escalates_low_risk_noncritical_vendor": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"riskScore": 0,
				"requestedSpend": 3000000,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["exception-escalation"]},
	},
	"u1_country_unreadable_but_d3_always_rejects": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"riskScore": 95,
				"requestedSpend": 1000000,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"u1_high_country_unreadable_spend_changes_outcome": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"riskScore": 50,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_critical_supplier_does_not_need_risk": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"requestedSpend": 100,
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"u1_critical_supplier_with_country_and_spend_unreadable": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"riskScore": 20,
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_critical_supplier_country_unreadable_at_2m": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"riskScore": 20,
				"requestedSpend": 2000000,
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"u1_critical_supplier_low_country_spend_unreadable": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 20,
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "review", "reasons": []},
	},
	"u1_critical_supplier_high_country_spend_unreadable": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"riskScore": 20,
				"criticalSupplier": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_low_country_missing_spend_d3_always_rejects": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"riskScore": 95,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"u1_country_unreadable_changes_approval_to_review": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"riskScore": 30,
				"requestedSpend": 50000,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_country_unreadable_d3_rejects_everywhere": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"riskScore": 95,
				"requestedSpend": 1000000,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"u1_missing_risk_does_not_prevent_o3": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"requestedSpend": 3000000,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["exception-escalation"]},
	},
	"u1_missing_risk_prior_action_rejects_everywhere": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "HIGH",
				"requestedSpend": 1000000,
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"u1_missing_risk_changes_low_country_outcome": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"requestedSpend": 50000,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"u1_missing_spend_prior_action_rejects_in_medium_country": {
		"input": {
			"vendor": {
				"sanctionsStatus": "CLEAR",
				"countryRisk": "MEDIUM",
				"riskScore": 10,
				"priorEnforcement": "yes",
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "reject", "reasons": []},
	},
	"u1_all_numeric_inputs_unreadable": {
		"input": {
			"vendor": {"sanctionsStatus": "CLEAR"},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["unknown"]},
	},
	"unmatched_screening_shape_uses_no_match": {
		"input": {
			"vendor": {
				"countryRisk": "LOW",
				"riskScore": 10,
				"requestedSpend": 100,
			},
			"evidence": {"financial-evidence": "present"},
		},
		"want": {"disposition": "unresolved", "reasons": ["no-match"]},
	},
}

test_vendor_policy[name] if {
	some name, tc in cases
	actual := study.decision with input as tc["input"]
	actual == tc["want"]
}
