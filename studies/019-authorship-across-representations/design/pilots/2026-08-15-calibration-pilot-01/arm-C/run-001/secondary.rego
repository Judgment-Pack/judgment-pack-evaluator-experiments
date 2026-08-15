package study_test

import data.study

approved := {"disposition": "approve", "reasons": []}
reviewed := {"disposition": "review", "reasons": []}
enhanced := {"disposition": "enhanced-review", "reasons": []}
rejected := {"disposition": "reject", "reasons": []}

unresolved_missing := {
	"disposition": "unresolved",
	"reasons": ["missing-required-evidence"],
}

unresolved_unknown := {
	"disposition": "unresolved",
	"reasons": ["unknown"],
}

unresolved_no_match := {
	"disposition": "unresolved",
	"reasons": ["no-match"],
}

unresolved_escalation := {
	"disposition": "unresolved",
	"reasons": ["exception-escalation"],
}

make_input(status, vendor_facts, evidence_facts) := {
	"vendor": object.union({"sanctionsStatus": status}, vendor_facts),
	"evidence": object.union(
		{"financial-evidence": "present"},
		evidence_facts,
	),
}

cases := {
	"p1_absent_precedes_everything": {
		"input": make_input("CLEAR", {
			"riskScore": 95,
			"requestedSpend": 3000000,
			"countryRisk": "HIGH",
			"criticalSupplier": "yes",
			"priorEnforcement": "yes",
		}, {"financial-evidence": "absent"}),
		"want": unresolved_missing,
	},
	"p1_unreported_precedes_sanctions_match": {
		"input": {
			"vendor": {
				"sanctionsStatus": "MATCH",
				"riskScore": 95,
				"requestedSpend": 3000000,
				"countryRisk": "HIGH",
			},
			"evidence": {"insurance-certificate": "present"},
		},
		"want": unresolved_unknown,
	},
	"empty_input_has_unreported_financial_evidence": {
		"input": {},
		"want": unresolved_unknown,
	},
	"sanctions_match_rejects_despite_critical_status_and_unreadable_inputs": {
		"input": make_input("MATCH", {
			"criticalSupplier": "yes",
		}, {}),
		"want": rejected,
	},
	"unknown_sanctions_is_no_match": {
		"input": make_input("UNKNOWN", {
			"criticalSupplier": "yes",
		}, {}),
		"want": unresolved_no_match,
	},
	"o3_precedes_o2_d3_d4_and_d5": {
		"input": make_input("CLEAR", {
			"riskScore": 95,
			"requestedSpend": 2000000.01,
			"countryRisk": "HIGH",
			"criticalSupplier": "yes",
			"priorEnforcement": "yes",
		}, {}),
		"want": unresolved_escalation,
	},
	"o3_is_strictly_above_two_million": {
		"input": make_input("CLEAR", {
			"riskScore": 95,
			"requestedSpend": 2000000,
			"countryRisk": "HIGH",
			"criticalSupplier": "yes",
		}, {}),
		"want": reviewed,
	},
	"o3_is_high_country_only": {
		"input": make_input("CLEAR", {
			"riskScore": 50,
			"requestedSpend": 3000000,
			"countryRisk": "MEDIUM",
		}, {}),
		"want": reviewed,
	},
	"o2_displaces_approval": {
		"input": make_input("CLEAR", {
			"riskScore": 20,
			"requestedSpend": 100,
			"countryRisk": "LOW",
			"criticalSupplier": "yes",
		}, {}),
		"want": reviewed,
	},
	"o2_displaces_d3_rejection": {
		"input": make_input("CLEAR", {
			"riskScore": 95,
			"requestedSpend": 100,
			"countryRisk": "LOW",
			"criticalSupplier": "yes",
		}, {}),
		"want": reviewed,
	},
	"o2_displaces_d5_rejection": {
		"input": make_input("CLEAR", {
			"riskScore": 20,
			"requestedSpend": 100,
			"countryRisk": "LOW",
			"criticalSupplier": "yes",
			"priorEnforcement": "yes",
		}, {}),
		"want": reviewed,
	},
	"o2_displaces_d6b_enhanced_review": {
		"input": make_input("CLEAR", {
			"riskScore": 20,
			"requestedSpend": 1000000,
			"countryRisk": "LOW",
			"criticalSupplier": "yes",
		}, {"insurance-certificate": "absent"}),
		"want": reviewed,
	},
	"o2_displaces_d6b_unreported_insurance": {
		"input": make_input("CLEAR", {
			"riskScore": 20,
			"requestedSpend": 1000000,
			"countryRisk": "LOW",
			"criticalSupplier": "yes",
		}, {}),
		"want": reviewed,
	},
	"unreported_critical_supplier_is_no": {
		"input": make_input("CLEAR", {
			"riskScore": 90,
			"requestedSpend": 100,
			"countryRisk": "LOW",
		}, {}),
		"want": rejected,
	},
	"d3_below_boundary_reviews": {
		"input": make_input("CLEAR", {
			"riskScore": 89,
			"requestedSpend": 3000000,
			"countryRisk": "LOW",
		}, {}),
		"want": reviewed,
	},
	"d3_boundary_rejects": {
		"input": make_input("CLEAR", {
			"riskScore": 90,
			"requestedSpend": 3000000,
			"countryRisk": "LOW",
		}, {}),
		"want": rejected,
	},
	"d4_below_boundary_reviews": {
		"input": make_input("CLEAR", {
			"riskScore": 69,
			"requestedSpend": 2000000,
			"countryRisk": "HIGH",
		}, {}),
		"want": reviewed,
	},
	"d4_boundary_rejects": {
		"input": make_input("CLEAR", {
			"riskScore": 70,
			"requestedSpend": 2000000,
			"countryRisk": "HIGH",
		}, {}),
		"want": rejected,
	},
	"d5_rejects_at_zero_risk_and_spend": {
		"input": make_input("CLEAR", {
			"riskScore": 0,
			"requestedSpend": 0,
			"countryRisk": "LOW",
			"priorEnforcement": "yes",
		}, {}),
		"want": rejected,
	},
	"unreported_prior_enforcement_is_no": {
		"input": make_input("CLEAR", {
			"riskScore": 0,
			"requestedSpend": 0,
			"countryRisk": "LOW",
		}, {}),
		"want": approved,
	},
	"d6a_includes_five_hundred_thousand": {
		"input": make_input("CLEAR", {
			"riskScore": 39,
			"requestedSpend": 500000,
			"countryRisk": "LOW",
		}, {}),
		"want": approved,
	},
	"d6b_present_insurance_approves": {
		"input": make_input("CLEAR", {
			"riskScore": 39,
			"requestedSpend": 500000.01,
			"countryRisk": "LOW",
		}, {"insurance-certificate": "present"}),
		"want": approved,
	},
	"d6b_absent_insurance_enhances": {
		"input": make_input("CLEAR", {
			"riskScore": 39,
			"requestedSpend": 500000.01,
			"countryRisk": "LOW",
		}, {"insurance-certificate": "absent"}),
		"want": enhanced,
	},
	"d6b_unreported_insurance_is_unknown": {
		"input": make_input("CLEAR", {
			"riskScore": 39,
			"requestedSpend": 500000.01,
			"countryRisk": "LOW",
		}, {}),
		"want": unresolved_unknown,
	},
	"d6b_requires_risk_below_forty": {
		"input": make_input("CLEAR", {
			"riskScore": 40,
			"requestedSpend": 1000000,
			"countryRisk": "LOW",
		}, {"insurance-certificate": "present"}),
		"want": reviewed,
	},
	"d6b_includes_two_million": {
		"input": make_input("CLEAR", {
			"riskScore": 39,
			"requestedSpend": 2000000,
			"countryRisk": "LOW",
		}, {"insurance-certificate": "absent"}),
		"want": enhanced,
	},
	"d6b_ends_above_two_million": {
		"input": make_input("CLEAR", {
			"riskScore": 39,
			"requestedSpend": 2000000.01,
			"countryRisk": "LOW",
		}, {"insurance-certificate": "present"}),
		"want": reviewed,
	},
	"d6c_includes_lower_boundaries": {
		"input": make_input("CLEAR", {
			"riskScore": 40,
			"requestedSpend": 100000,
			"countryRisk": "LOW",
		}, {"insurance-certificate": "absent"}),
		"want": approved,
	},
	"d6c_includes_risk_sixty_nine": {
		"input": make_input("CLEAR", {
			"riskScore": 69,
			"requestedSpend": 100000,
			"countryRisk": "LOW",
		}, {}),
		"want": approved,
	},
	"d6c_ends_at_risk_seventy": {
		"input": make_input("CLEAR", {
			"riskScore": 70,
			"requestedSpend": 100000,
			"countryRisk": "LOW",
		}, {}),
		"want": reviewed,
	},
	"d6c_ends_above_one_hundred_thousand": {
		"input": make_input("CLEAR", {
			"riskScore": 69,
			"requestedSpend": 100000.01,
			"countryRisk": "LOW",
		}, {}),
		"want": reviewed,
	},
	"o1_suspends_d6c": {
		"input": make_input("CLEAR", {
			"riskScore": 40,
			"requestedSpend": 100000,
			"countryRisk": "LOW",
			"newVendor": "yes",
		}, {}),
		"want": reviewed,
	},
	"o1_does_not_suspend_d6a": {
		"input": make_input("CLEAR", {
			"riskScore": 39,
			"requestedSpend": 500000,
			"countryRisk": "LOW",
			"newVendor": "yes",
		}, {"insurance-certificate": "absent"}),
		"want": approved,
	},
	"d7_includes_upper_spend_and_risk_thirty_nine": {
		"input": make_input("CLEAR", {
			"riskScore": 39,
			"requestedSpend": 100000,
			"countryRisk": "MEDIUM",
		}, {}),
		"want": approved,
	},
	"d7_ends_at_risk_forty": {
		"input": make_input("CLEAR", {
			"riskScore": 40,
			"requestedSpend": 100000,
			"countryRisk": "MEDIUM",
		}, {}),
		"want": reviewed,
	},
	"d7_ends_above_one_hundred_thousand": {
		"input": make_input("CLEAR", {
			"riskScore": 39,
			"requestedSpend": 100000.01,
			"countryRisk": "MEDIUM",
		}, {}),
		"want": reviewed,
	},
	"ordinary_high_country_request_reviews": {
		"input": make_input("CLEAR", {
			"riskScore": 0,
			"requestedSpend": 0,
			"countryRisk": "HIGH",
		}, {}),
		"want": reviewed,
	},
	"u1_worked_example_one_rejects": {
		"input": make_input("CLEAR", {
			"riskScore": 95,
			"requestedSpend": 1000000,
		}, {}),
		"want": rejected,
	},
	"u1_worked_example_two_is_unknown": {
		"input": make_input("CLEAR", {
			"riskScore": 50,
			"countryRisk": "HIGH",
		}, {}),
		"want": unresolved_unknown,
	},
	"u1_worked_example_three_reviews": {
		"input": make_input("CLEAR", {
			"requestedSpend": 100,
			"countryRisk": "LOW",
			"criticalSupplier": "yes",
		}, {}),
		"want": reviewed,
	},
	"u1_worked_example_four_is_unknown": {
		"input": make_input("CLEAR", {
			"criticalSupplier": "yes",
		}, {}),
		"want": unresolved_unknown,
	},
	"u1_fixed_o3_escalates_despite_unreadable_risk": {
		"input": make_input("CLEAR", {
			"requestedSpend": 2000000.01,
			"countryRisk": "HIGH",
		}, {}),
		"want": unresolved_escalation,
	},
	"u1_unreadable_risk_with_prior_action_always_rejects": {
		"input": make_input("CLEAR", {
			"requestedSpend": 100,
			"countryRisk": "LOW",
			"priorEnforcement": "yes",
		}, {}),
		"want": rejected,
	},
	"u1_unreadable_risk_at_high_country_two_million_is_unknown": {
		"input": make_input("CLEAR", {
			"requestedSpend": 2000000,
			"countryRisk": "HIGH",
		}, {}),
		"want": unresolved_unknown,
	},
	"u1_unreadable_spend_with_d3_in_low_country_rejects": {
		"input": make_input("CLEAR", {
			"riskScore": 95,
			"countryRisk": "LOW",
		}, {}),
		"want": rejected,
	},
	"u1_unreadable_spend_with_mid_risk_in_low_country_reviews": {
		"input": make_input("CLEAR", {
			"riskScore": 70,
			"countryRisk": "LOW",
		}, {}),
		"want": reviewed,
	},
	"u1_unreadable_spend_with_low_risk_is_unknown": {
		"input": make_input("CLEAR", {
			"riskScore": 20,
			"countryRisk": "LOW",
		}, {"insurance-certificate": "present"}),
		"want": unresolved_unknown,
	},
	"u1_unreadable_country_can_be_stably_reviewed": {
		"input": make_input("CLEAR", {
			"riskScore": 50,
			"requestedSpend": 200000,
		}, {}),
		"want": reviewed,
	},
	"u1_unreadable_country_can_mix_approval_and_review": {
		"input": make_input("CLEAR", {
			"riskScore": 50,
			"requestedSpend": 50000,
		}, {}),
		"want": unresolved_unknown,
	},
	"u1_unreadable_country_above_two_million_can_mix_reject_and_escalation": {
		"input": make_input("CLEAR", {
			"riskScore": 20,
			"requestedSpend": 2000000.01,
			"priorEnforcement": "yes",
		}, {}),
		"want": unresolved_unknown,
	},
	"u1_unreadable_risk_and_spend_with_low_country_prior_action_rejects": {
		"input": make_input("CLEAR", {
			"countryRisk": "LOW",
			"priorEnforcement": "yes",
		}, {}),
		"want": rejected,
	},
	"u1_unreadable_risk_and_country_at_two_million_critical_reviews": {
		"input": make_input("CLEAR", {
			"requestedSpend": 2000000,
			"criticalSupplier": "yes",
		}, {}),
		"want": reviewed,
	},
	"u1_all_primary_inputs_unreadable_without_override_is_unknown": {
		"input": make_input("CLEAR", {}, {}),
		"want": unresolved_unknown,
	},
}

test_vendor_policy[name] if {
	some name, test_case in cases
	study.decision == test_case["want"] with input as test_case["input"]
}
