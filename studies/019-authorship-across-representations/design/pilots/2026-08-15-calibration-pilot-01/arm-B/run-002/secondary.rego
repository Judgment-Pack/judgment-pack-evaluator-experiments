package study_test

import data.study

outcomes := {
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
	"missing-required-evidence": {
		"disposition": "unresolved",
		"reasons": ["missing-required-evidence"],
	},
	"unknown": {
		"disposition": "unresolved",
		"reasons": ["unknown"],
	},
	"no-match": {
		"disposition": "unresolved",
		"reasons": ["no-match"],
	},
	"exception-escalation": {
		"disposition": "unresolved",
		"reasons": ["exception-escalation"],
	},
}

financial_present := {
	"financial-evidence": "present",
}

financial_absent := {
	"financial-evidence": "absent",
}

financial_and_insurance_present := {
	"financial-evidence": "present",
	"insurance-certificate": "present",
}

financial_and_insurance_absent := {
	"financial-evidence": "present",
	"insurance-certificate": "absent",
}

test_preconditions_and_sanctions[name] if {
	some name, tc in {
		"financial absence beats sanctions match": {
			"given": {
				"vendor": {
					"sanctionsStatus": "MATCH",
					"criticalSupplier": "yes",
				},
				"evidence": financial_absent,
			},
			"want": "missing-required-evidence",
		},
		"financial omission beats O3 and O2": {
			"given": {
				"vendor": {
					"riskScore": 99,
					"requestedSpend": 5000000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "HIGH",
					"criticalSupplier": "yes",
					"priorEnforcement": "yes",
				},
				"evidence": {},
			},
			"want": "unknown",
		},
		"financial absence beats O3": {
			"given": {
				"vendor": {
					"riskScore": 99,
					"requestedSpend": 5000000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "HIGH",
					"criticalSupplier": "yes",
				},
				"evidence": financial_absent,
			},
			"want": "missing-required-evidence",
		},
		"sanctions match stands against O2 and O3": {
			"given": {
				"vendor": {
					"riskScore": 99,
					"requestedSpend": 5000000,
					"sanctionsStatus": "MATCH",
					"countryRisk": "HIGH",
					"criticalSupplier": "yes",
					"priorEnforcement": "yes",
				},
				"evidence": financial_present,
			},
			"want": "reject",
		},
		"sanctions unknown stands against O2": {
			"given": {
				"vendor": {
					"sanctionsStatus": "UNKNOWN",
					"criticalSupplier": "yes",
				},
				"evidence": financial_present,
			},
			"want": "no-match",
		},
	}

	actual := study.decision with input as tc.given
	actual == outcomes[tc.want]
}

test_thresholds_and_determinations[name] if {
	some name, tc in {
		"zero risk and spend are readable": {
			"given": {
				"vendor": {
					"riskScore": 0,
					"requestedSpend": 0,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_present,
			},
			"want": "approve",
		},
		"D3 does not apply at risk 89": {
			"given": {
				"vendor": {
					"riskScore": 89,
					"requestedSpend": 0,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"D3 begins at risk 90": {
			"given": {
				"vendor": {
					"riskScore": 90,
					"requestedSpend": 0,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_present,
			},
			"want": "reject",
		},
		"D4 does not apply at risk 69": {
			"given": {
				"vendor": {
					"riskScore": 69,
					"requestedSpend": 100,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "HIGH",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"D4 begins at risk 70": {
			"given": {
				"vendor": {
					"riskScore": 70,
					"requestedSpend": 100,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "HIGH",
				},
				"evidence": financial_present,
			},
			"want": "reject",
		},
		"D5 rejects an otherwise approvable request": {
			"given": {
				"vendor": {
					"riskScore": 1,
					"requestedSpend": 1,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
					"priorEnforcement": "yes",
				},
				"evidence": financial_present,
			},
			"want": "reject",
		},
		"D6a includes 500000 and ignores absent insurance": {
			"given": {
				"vendor": {
					"riskScore": 39,
					"requestedSpend": 500000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_and_insurance_absent,
			},
			"want": "approve",
		},
		"D6b approves with insurance": {
			"given": {
				"vendor": {
					"riskScore": 39,
					"requestedSpend": 500000.01,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_and_insurance_present,
			},
			"want": "approve",
		},
		"D6b absent insurance gives enhanced review": {
			"given": {
				"vendor": {
					"riskScore": 39,
					"requestedSpend": 500000.01,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_and_insurance_absent,
			},
			"want": "enhanced-review",
		},
		"D6b unreported insurance is unresolved": {
			"given": {
				"vendor": {
					"riskScore": 39,
					"requestedSpend": 500000.01,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_present,
			},
			"want": "unknown",
		},
		"D6b includes 2000000": {
			"given": {
				"vendor": {
					"riskScore": 10,
					"requestedSpend": 2000000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_and_insurance_present,
			},
			"want": "approve",
		},
		"D8 begins above the D6b ceiling": {
			"given": {
				"vendor": {
					"riskScore": 10,
					"requestedSpend": 2000000.01,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_and_insurance_present,
			},
			"want": "review",
		},
		"D6c includes risk 40": {
			"given": {
				"vendor": {
					"riskScore": 40,
					"requestedSpend": 100000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_present,
			},
			"want": "approve",
		},
		"D6c includes risk 69": {
			"given": {
				"vendor": {
					"riskScore": 69,
					"requestedSpend": 100000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_present,
			},
			"want": "approve",
		},
		"D6c excludes spend above 100000": {
			"given": {
				"vendor": {
					"riskScore": 69,
					"requestedSpend": 100000.01,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"D6c excludes risk 70": {
			"given": {
				"vendor": {
					"riskScore": 70,
					"requestedSpend": 100000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"D7 includes risk 39 and spend 100000": {
			"given": {
				"vendor": {
					"riskScore": 39,
					"requestedSpend": 100000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "MEDIUM",
				},
				"evidence": financial_present,
			},
			"want": "approve",
		},
		"D7 excludes spend above 100000": {
			"given": {
				"vendor": {
					"riskScore": 39,
					"requestedSpend": 100000.01,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "MEDIUM",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"D7 excludes risk 40": {
			"given": {
				"vendor": {
					"riskScore": 40,
					"requestedSpend": 100000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "MEDIUM",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
	}

	actual := study.decision with input as tc.given
	actual == outcomes[tc.want]
}

test_overrides_and_precedence[name] if {
	some name, tc in {
		"O3 does not apply at exactly 2000000": {
			"given": {
				"vendor": {
					"riskScore": 50,
					"requestedSpend": 2000000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "HIGH",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"O3 beats O2 D3 D4 and D5": {
			"given": {
				"vendor": {
					"riskScore": 99,
					"requestedSpend": 10000000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "HIGH",
					"newVendor": "yes",
					"criticalSupplier": "yes",
					"priorEnforcement": "yes",
				},
				"evidence": financial_and_insurance_absent,
			},
			"want": "exception-escalation",
		},
		"O2 beats D3 D4 and D5 at the O3 boundary": {
			"given": {
				"vendor": {
					"riskScore": 95,
					"requestedSpend": 2000000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "HIGH",
					"criticalSupplier": "yes",
					"priorEnforcement": "yes",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"O2 displaces D6b enhanced review": {
			"given": {
				"vendor": {
					"riskScore": 20,
					"requestedSpend": 600000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
					"criticalSupplier": "yes",
				},
				"evidence": financial_and_insurance_absent,
			},
			"want": "review",
		},
		"O2 displaces D6b unreported insurance": {
			"given": {
				"vendor": {
					"riskScore": 20,
					"requestedSpend": 600000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
					"criticalSupplier": "yes",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"O1 suspends D6c": {
			"given": {
				"vendor": {
					"riskScore": 40,
					"requestedSpend": 100000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
					"newVendor": "yes",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"O1 does not suspend D6a": {
			"given": {
				"vendor": {
					"riskScore": 39,
					"requestedSpend": 100000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
					"newVendor": "yes",
				},
				"evidence": financial_present,
			},
			"want": "approve",
		},
		"O1 does not suspend D7": {
			"given": {
				"vendor": {
					"riskScore": 39,
					"requestedSpend": 100000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "MEDIUM",
					"newVendor": "yes",
				},
				"evidence": financial_present,
			},
			"want": "approve",
		},
		"O3 is limited to HIGH countries": {
			"given": {
				"vendor": {
					"riskScore": 20,
					"requestedSpend": 5000000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "MEDIUM",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
	}

	actual := study.decision with input as tc.given
	actual == outcomes[tc.want]
}

test_unreadable_inputs_u1[name] if {
	some name, tc in {
		"country unreadable but D3 always rejects": {
			"given": {
				"vendor": {
					"riskScore": 95,
					"requestedSpend": 1000000,
					"sanctionsStatus": "CLEAR",
				},
				"evidence": financial_present,
			},
			"want": "reject",
		},
		"unreadable spend can produce review or O3": {
			"given": {
				"vendor": {
					"riskScore": 50,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "HIGH",
				},
				"evidence": financial_present,
			},
			"want": "unknown",
		},
		"O2 makes unreadable risk immaterial": {
			"given": {
				"vendor": {
					"requestedSpend": 100,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
					"criticalSupplier": "yes",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"unreadable country and spend can produce O2 or O3": {
			"given": {
				"vendor": {
					"riskScore": 50,
					"sanctionsStatus": "CLEAR",
					"criticalSupplier": "yes",
				},
				"evidence": financial_present,
			},
			"want": "unknown",
		},
		"O3 makes unreadable risk immaterial": {
			"given": {
				"vendor": {
					"requestedSpend": 3000000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "HIGH",
				},
				"evidence": financial_present,
			},
			"want": "exception-escalation",
		},
		"D3 makes unreadable spend immaterial in LOW": {
			"given": {
				"vendor": {
					"riskScore": 95,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
				},
				"evidence": financial_present,
			},
			"want": "reject",
		},
		"unreadable risk can produce D7 D8 or D3": {
			"given": {
				"vendor": {
					"requestedSpend": 100000,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "MEDIUM",
				},
				"evidence": financial_present,
			},
			"want": "unknown",
		},
		"O1 makes unreadable spend invariant": {
			"given": {
				"vendor": {
					"riskScore": 50,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
					"newVendor": "yes",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"without O1 unreadable spend is ambiguous": {
			"given": {
				"vendor": {
					"riskScore": 50,
					"sanctionsStatus": "CLEAR",
					"countryRisk": "LOW",
					"newVendor": "no",
				},
				"evidence": financial_present,
			},
			"want": "unknown",
		},
		"O1 makes unreadable country invariant": {
			"given": {
				"vendor": {
					"riskScore": 50,
					"requestedSpend": 100000,
					"sanctionsStatus": "CLEAR",
					"newVendor": "yes",
				},
				"evidence": financial_present,
			},
			"want": "review",
		},
		"without O1 unreadable country is ambiguous": {
			"given": {
				"vendor": {
					"riskScore": 50,
					"requestedSpend": 100000,
					"sanctionsStatus": "CLEAR",
					"newVendor": "no",
				},
				"evidence": financial_present,
			},
			"want": "unknown",
		},
		"D5 makes unreadable risk and country immaterial at 2000000": {
			"given": {
				"vendor": {
					"requestedSpend": 2000000,
					"sanctionsStatus": "CLEAR",
					"priorEnforcement": "yes",
				},
				"evidence": financial_present,
			},
			"want": "reject",
		},
	}

	actual := study.decision with input as tc.given
	actual == outcomes[tc.want]
}
