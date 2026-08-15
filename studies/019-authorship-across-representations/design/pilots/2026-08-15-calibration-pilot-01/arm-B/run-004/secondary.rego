package study_test

import data.study

financial_present := {"financial-evidence": "present"}

make_input(vendor, evidence) := {
	"vendor": vendor,
	"evidence": evidence,
}

present_input(vendor) := make_input(vendor, financial_present)

certificate_input(vendor, status) := make_input(vendor, {
	"financial-evidence": "present",
	"insurance-certificate": status,
})

determination(disposition) := {
	"disposition": disposition,
	"reasons": [],
}

unresolved(reason) := {
	"disposition": "unresolved",
	"reasons": [reason],
}

decision_for(doc) := result if {
	result := study.decision with input as doc
}

allowed_dispositions := {
	"approve",
	"review",
	"enhanced-review",
	"reject",
	"unresolved",
}

determination_dispositions := {
	"approve",
	"review",
	"enhanced-review",
	"reject",
}

allowed_reasons := {
	"missing-required-evidence",
	"unknown",
	"no-match",
	"exception-escalation",
}

valid_common(result) if {
	is_object(result)
	object.keys(result) == {"disposition", "reasons"}
	is_string(result.disposition)
	result.disposition in allowed_dispositions
	is_array(result.reasons)

	every reason in result.reasons {
		is_string(reason)
		reason in allowed_reasons
	}

	distinct_reasons := {item | some item in result.reasons}
	count(distinct_reasons) == count(result.reasons)
}

valid_result(result) if {
	valid_common(result)
	result.disposition == "unresolved"
	count(result.reasons) > 0
}

valid_result(result) if {
	valid_common(result)
	result.disposition in determination_dispositions
	count(result.reasons) == 0
}

cases := {
	"p1_absent_precedes_everything": {
		"input": make_input(
			{
				"riskScore": 100,
				"requestedSpend": 10000000,
				"sanctionsStatus": "MATCH",
				"countryRisk": "HIGH",
				"newVendor": "yes",
				"criticalSupplier": "yes",
				"priorEnforcement": "yes",
			},
			{
				"financial-evidence": "absent",
				"insurance-certificate": "present",
			}
		),
		"want": unresolved("missing-required-evidence"),
	},
	"p1_unreported_precedes_everything": {
		"input": make_input(
			{
				"riskScore": 100,
				"requestedSpend": 10000000,
				"sanctionsStatus": "MATCH",
				"countryRisk": "HIGH",
				"criticalSupplier": "yes",
			},
			{"insurance-certificate": "present"}
		),
		"want": unresolved("unknown"),
	},
	"d1_match_ignores_unreadable_dimensions_and_critical_status": {
		"input": present_input({
			"sanctionsStatus": "MATCH",
			"criticalSupplier": "yes",
		}),
		"want": determination("reject"),
	},
	"d2_unknown_precedes_overrides_and_rejections": {
		"input": present_input({
			"riskScore": 100,
			"requestedSpend": 10000000,
			"sanctionsStatus": "UNKNOWN",
			"countryRisk": "HIGH",
			"criticalSupplier": "yes",
			"priorEnforcement": "yes",
		}),
		"want": unresolved("no-match"),
	},
	"d2_unknown_ignores_all_unreadable_dimensions": {
		"input": present_input({
			"sanctionsStatus": "UNKNOWN",
			"criticalSupplier": "yes",
		}),
		"want": unresolved("no-match"),
	},
	"o3_starts_one_cent_above_two_million": {
		"input": present_input({
			"riskScore": 0,
			"requestedSpend": 2000000.01,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
		}),
		"want": unresolved("exception-escalation"),
	},
	"o3_overrides_o2_d3_d4_and_d5": {
		"input": present_input({
			"riskScore": 100,
			"requestedSpend": 10000000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
			"criticalSupplier": "yes",
			"priorEnforcement": "yes",
		}),
		"want": unresolved("exception-escalation"),
	},
	"o3_does_not_depend_on_risk_score": {
		"input": present_input({
			"requestedSpend": 3000000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
		}),
		"want": unresolved("exception-escalation"),
	},
	"o3_does_not_apply_at_exactly_two_million": {
		"input": present_input({
			"riskScore": 70,
			"requestedSpend": 2000000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
		}),
		"want": determination("reject"),
	},
	"o2_replaces_an_approval": {
		"input": present_input({
			"riskScore": 10,
			"requestedSpend": 100,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
			"criticalSupplier": "yes",
		}),
		"want": determination("review"),
	},
	"o2_replaces_d3_and_d4_rejection": {
		"input": present_input({
			"riskScore": 100,
			"requestedSpend": 2000000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
			"criticalSupplier": "yes",
		}),
		"want": determination("review"),
	},
	"o2_replaces_d5_rejection": {
		"input": present_input({
			"riskScore": 10,
			"requestedSpend": 100,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "MEDIUM",
			"criticalSupplier": "yes",
			"priorEnforcement": "yes",
		}),
		"want": determination("review"),
	},
	"o2_replaces_d6b_enhanced_review": {
		"input": certificate_input(
			{
				"riskScore": 20,
				"requestedSpend": 1000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"criticalSupplier": "yes",
			},
			"absent"
		),
		"want": determination("review"),
	},
	"o2_replaces_d6b_unreported_insurance_limb": {
		"input": present_input({
			"riskScore": 20,
			"requestedSpend": 1000000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
			"criticalSupplier": "yes",
		}),
		"want": determination("review"),
	},
	"d3_below_threshold_does_not_reject_in_low_country": {
		"input": present_input({
			"riskScore": 89,
			"requestedSpend": 100,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": determination("review"),
	},
	"d3_rejects_at_ninety": {
		"input": present_input({
			"riskScore": 90,
			"requestedSpend": 100,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": determination("reject"),
	},
	"d4_does_not_reject_at_sixty_nine": {
		"input": present_input({
			"riskScore": 69,
			"requestedSpend": 2000000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
		}),
		"want": determination("review"),
	},
	"d4_rejects_at_seventy": {
		"input": present_input({
			"riskScore": 70,
			"requestedSpend": 100,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
		}),
		"want": determination("reject"),
	},
	"d5_rejects_low_risk_zero_spend": {
		"input": present_input({
			"riskScore": 0,
			"requestedSpend": 0,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
			"priorEnforcement": "yes",
		}),
		"want": determination("reject"),
	},
	"unreported_yes_no_statuses_are_treated_as_no": {
		"input": present_input({
			"riskScore": 0,
			"requestedSpend": 0,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": determination("approve"),
	},
	"d6a_includes_risk_thirty_nine_and_five_hundred_thousand": {
		"input": present_input({
			"riskScore": 39,
			"requestedSpend": 500000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": determination("approve"),
	},
	"d6b_lower_boundary_with_insurance": {
		"input": certificate_input(
			{
				"riskScore": 39,
				"requestedSpend": 500000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"present"
		),
		"want": determination("approve"),
	},
	"d6b_lower_boundary_without_insurance": {
		"input": certificate_input(
			{
				"riskScore": 39,
				"requestedSpend": 500000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"absent"
		),
		"want": determination("enhanced-review"),
	},
	"d6b_lower_boundary_with_unreported_insurance": {
		"input": present_input({
			"riskScore": 39,
			"requestedSpend": 500000.01,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": unresolved("unknown"),
	},
	"d6b_includes_two_million_with_insurance": {
		"input": certificate_input(
			{
				"riskScore": 39,
				"requestedSpend": 2000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"present"
		),
		"want": determination("approve"),
	},
	"d6b_includes_two_million_without_insurance": {
		"input": certificate_input(
			{
				"riskScore": 39,
				"requestedSpend": 2000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"absent"
		),
		"want": determination("enhanced-review"),
	},
	"d6b_ends_one_cent_above_two_million": {
		"input": certificate_input(
			{
				"riskScore": 39,
				"requestedSpend": 2000000.01,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
			},
			"present"
		),
		"want": determination("review"),
	},
	"o1_does_not_suspend_d6b": {
		"input": certificate_input(
			{
				"riskScore": 20,
				"requestedSpend": 1000000,
				"sanctionsStatus": "CLEAR",
				"countryRisk": "LOW",
				"newVendor": "yes",
			},
			"present"
		),
		"want": determination("approve"),
	},
	"d6c_starts_at_risk_forty": {
		"input": present_input({
			"riskScore": 40,
			"requestedSpend": 100000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": determination("approve"),
	},
	"d6c_includes_risk_sixty_nine": {
		"input": present_input({
			"riskScore": 69,
			"requestedSpend": 100000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": determination("approve"),
	},
	"d6c_ends_one_cent_above_one_hundred_thousand": {
		"input": present_input({
			"riskScore": 40,
			"requestedSpend": 100000.01,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": determination("review"),
	},
	"d6c_does_not_include_risk_seventy": {
		"input": present_input({
			"riskScore": 70,
			"requestedSpend": 100000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": determination("review"),
	},
	"o1_suspends_d6c_for_new_vendor": {
		"input": present_input({
			"riskScore": 40,
			"requestedSpend": 100000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
			"newVendor": "yes",
		}),
		"want": determination("review"),
	},
	"o1_does_not_suspend_d6a": {
		"input": present_input({
			"riskScore": 39,
			"requestedSpend": 500000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
			"newVendor": "yes",
		}),
		"want": determination("approve"),
	},
	"d7_includes_its_upper_boundaries": {
		"input": present_input({
			"riskScore": 39,
			"requestedSpend": 100000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "MEDIUM",
		}),
		"want": determination("approve"),
	},
	"d7_does_not_include_risk_forty": {
		"input": present_input({
			"riskScore": 40,
			"requestedSpend": 100000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "MEDIUM",
		}),
		"want": determination("review"),
	},
	"d7_ends_one_cent_above_one_hundred_thousand": {
		"input": present_input({
			"riskScore": 39,
			"requestedSpend": 100000.01,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "MEDIUM",
		}),
		"want": determination("review"),
	},
	"d8_handles_high_country_below_d4": {
		"input": present_input({
			"riskScore": 0,
			"requestedSpend": 100,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
		}),
		"want": determination("review"),
	},
	"u1_worked_example_one": {
		"input": present_input({
			"riskScore": 95,
			"requestedSpend": 1000000,
			"sanctionsStatus": "CLEAR",
		}),
		"want": determination("reject"),
	},
	"u1_worked_example_two": {
		"input": present_input({
			"riskScore": 50,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
		}),
		"want": unresolved("unknown"),
	},
	"u1_worked_example_three": {
		"input": present_input({
			"requestedSpend": 100,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
			"criticalSupplier": "yes",
		}),
		"want": determination("review"),
	},
	"u1_worked_example_four": {
		"input": present_input({
			"sanctionsStatus": "CLEAR",
			"criticalSupplier": "yes",
		}),
		"want": unresolved("unknown"),
	},
	"u1_critical_with_unreadable_risk_and_spend_in_low_country": {
		"input": present_input({
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
			"criticalSupplier": "yes",
		}),
		"want": determination("review"),
	},
	"u1_critical_with_unreadable_country_at_exactly_two_million": {
		"input": present_input({
			"riskScore": 100,
			"requestedSpend": 2000000,
			"sanctionsStatus": "CLEAR",
			"criticalSupplier": "yes",
		}),
		"want": determination("review"),
	},
	"u1_critical_high_country_with_unreadable_spend": {
		"input": present_input({
			"riskScore": 10,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
			"criticalSupplier": "yes",
		}),
		"want": unresolved("unknown"),
	},
	"u1_critical_with_unreadable_country_and_large_spend": {
		"input": present_input({
			"riskScore": 10,
			"requestedSpend": 2000000.01,
			"sanctionsStatus": "CLEAR",
			"criticalSupplier": "yes",
		}),
		"want": unresolved("unknown"),
	},
	"u1_unreadable_risk_changes_low_country_outcome": {
		"input": present_input({
			"requestedSpend": 100,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": unresolved("unknown"),
	},
	"u1_unreadable_risk_is_irrelevant_with_prior_action": {
		"input": present_input({
			"requestedSpend": 100,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
			"priorEnforcement": "yes",
		}),
		"want": determination("reject"),
	},
	"u1_unreadable_risk_is_irrelevant_to_o3": {
		"input": present_input({
			"requestedSpend": 3000000,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
		}),
		"want": unresolved("exception-escalation"),
	},
	"u1_unreadable_spend_changes_low_country_risk_fifty": {
		"input": present_input({
			"riskScore": 50,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": unresolved("unknown"),
	},
	"u1_unreadable_spend_is_always_review_after_o1": {
		"input": present_input({
			"riskScore": 50,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
			"newVendor": "yes",
		}),
		"want": determination("review"),
	},
	"u1_unreadable_spend_is_always_review_for_low_risk_eighty": {
		"input": present_input({
			"riskScore": 80,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": determination("review"),
	},
	"u1_unreadable_spend_is_always_reject_for_low_risk_ninety_five": {
		"input": present_input({
			"riskScore": 95,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "LOW",
		}),
		"want": determination("reject"),
	},
	"u1_unreadable_spend_changes_medium_country_low_risk": {
		"input": present_input({
			"riskScore": 39,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "MEDIUM",
		}),
		"want": unresolved("unknown"),
	},
	"u1_unreadable_spend_is_always_review_for_medium_risk_fifty": {
		"input": present_input({
			"riskScore": 50,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "MEDIUM",
		}),
		"want": determination("review"),
	},
	"u1_unreadable_spend_in_high_country_can_escalate": {
		"input": present_input({
			"riskScore": 80,
			"sanctionsStatus": "CLEAR",
			"countryRisk": "HIGH",
		}),
		"want": unresolved("unknown"),
	},
	"u1_unreadable_country_with_d3_below_o3_rejects": {
		"input": present_input({
			"riskScore": 95,
			"requestedSpend": 1000000,
			"sanctionsStatus": "CLEAR",
		}),
		"want": determination("reject"),
	},
	"u1_unreadable_country_with_d3_at_two_million_rejects": {
		"input": present_input({
			"riskScore": 95,
			"requestedSpend": 2000000,
			"sanctionsStatus": "CLEAR",
		}),
		"want": determination("reject"),
	},
	"u1_unreadable_country_with_d3_and_large_spend_can_escalate": {
		"input": present_input({
			"riskScore": 95,
			"requestedSpend": 2000000.01,
			"sanctionsStatus": "CLEAR",
		}),
		"want": unresolved("unknown"),
	},
	"u1_unreadable_country_is_always_review_for_risk_fifty_and_mid_spend": {
		"input": present_input({
			"riskScore": 50,
			"requestedSpend": 200000,
			"sanctionsStatus": "CLEAR",
		}),
		"want": determination("review"),
	},
	"u1_unreadable_country_changes_risk_fifty_small_spend": {
		"input": present_input({
			"riskScore": 50,
			"requestedSpend": 100000,
			"sanctionsStatus": "CLEAR",
		}),
		"want": unresolved("unknown"),
	},
	"u1_unreadable_country_is_review_for_new_vendor_d6c_shape": {
		"input": present_input({
			"riskScore": 50,
			"requestedSpend": 100000,
			"sanctionsStatus": "CLEAR",
			"newVendor": "yes",
		}),
		"want": determination("review"),
	},
	"u1_unreadable_country_changes_low_risk_small_spend": {
		"input": present_input({
			"riskScore": 30,
			"requestedSpend": 50000,
			"sanctionsStatus": "CLEAR",
		}),
		"want": unresolved("unknown"),
	},
	"u1_compares_outcomes_not_governing_clause_names": {
		"input": present_input({
			"riskScore": 80,
			"requestedSpend": 1000000,
			"sanctionsStatus": "CLEAR",
			"priorEnforcement": "yes",
		}),
		"want": determination("reject"),
	},
	"u1_prior_action_and_large_spend_with_unreadable_country": {
		"input": present_input({
			"riskScore": 10,
			"requestedSpend": 3000000,
			"sanctionsStatus": "CLEAR",
			"priorEnforcement": "yes",
		}),
		"want": unresolved("unknown"),
	},
	"u1_unreadable_risk_and_spend_with_prior_action_in_medium": {
		"input": present_input({
			"sanctionsStatus": "CLEAR",
			"countryRisk": "MEDIUM",
			"priorEnforcement": "yes",
		}),
		"want": determination("reject"),
	},
	"u1_unreadable_risk_and_spend_without_override_in_medium": {
		"input": present_input({
			"sanctionsStatus": "CLEAR",
			"countryRisk": "MEDIUM",
		}),
		"want": unresolved("unknown"),
	},
	"u1_d6b_absent_insurance_with_unreadable_country": {
		"input": certificate_input(
			{
				"riskScore": 39,
				"requestedSpend": 1000000,
				"sanctionsStatus": "CLEAR",
			},
			"absent"
		),
		"want": unresolved("unknown"),
	},
}

test_expected_decisions[name] if {
	some name, test_case in cases
	actual := decision_for(test_case.input)
	actual == test_case.want
}

test_result_contract[name] if {
	some name, test_case in cases
	result := decision_for(test_case.input)
	valid_result(result)
}
