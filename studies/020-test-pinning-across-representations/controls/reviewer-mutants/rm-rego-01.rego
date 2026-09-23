package study
default decision := {"disposition": "unresolved", "reasons": ["no-match"]}
v_risk := object.get(input, ["vendor", "riskScore"], null)
v_spend := object.get(input, ["vendor", "requestedSpend"], null)
v_country := object.get(input, ["vendor", "countryRisk"], null)
v_sanctions := object.get(input, ["vendor", "sanctionsStatus"], null)
v_new := object.get(input, ["vendor", "newVendor"], null)
v_critical := object.get(input, ["vendor", "criticalSupplier"], null)
v_prior := object.get(input, ["vendor", "priorEnforcement"], null)
fin_state := object.get(input, ["evidence", "financial-evidence"], "OMITTED")
ins_state := object.get(input, ["evidence", "insurance-certificate"], "OMITTED")
determine(risk, spend, country) := {"disposition": "unresolved", "reasons": ["exception-escalation"]} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	spend > 2000000
	fin_state == "present"
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_critical == "yes"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "MATCH"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]} if {
	v_sanctions == "UNKNOWN"
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	risk >= 90
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "HIGH"
	risk >= 70
}
else := {"disposition": "reject", "reasons": []} if {
	v_sanctions == "CLEAR"
	v_prior == "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend <= 500000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "present"
}
else := {"disposition": "enhanced-review", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
	ins_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk < 40
	spend > 500000
	spend <= 2000000
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "LOW"
	risk >= 40
	risk < 70
	spend <= 100000
	v_new != "yes"
}
else := {"disposition": "approve", "reasons": []} if {
	v_sanctions == "CLEAR"
	country == "MEDIUM"
	risk < 40
	spend <= 100000
}
else := {"disposition": "review", "reasons": []} if {
	v_sanctions == "CLEAR"
}
else := {"disposition": "unresolved", "reasons": ["no-match"]}
risk_candidates := [v_risk] if {
	v_risk != null
} else := [0, 39, 40, 69, 70, 89, 90, 100]
spend_candidates := [v_spend] if {
	v_spend != null
} else := [0, 100000, 100000.01, 500000, 500000.01, 2000000, 2000000.01, 10000000]
country_candidates := [v_country] if {
	v_country != null
} else := ["LOW", "MEDIUM", "HIGH"]
u1_determinations := {d |
	some r in risk_candidates
	some s in spend_candidates
	some c in country_candidates
	d := determine(r, s, c)
}
decision := {"disposition": "unresolved", "reasons": ["missing-required-evidence"]} if {
	fin_state == "absent"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "OMITTED"
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "present"
	v_sanctions == "CLEAR"
	v_country == "HIGH"
	v_spend != null
	v_spend > 2000000
}
else := d if {
	fin_state == "present"
	count(u1_determinations) == 1
	some d in u1_determinations
}
else := {"disposition": "unresolved", "reasons": ["unknown"]} if {
	fin_state == "present"
	count(u1_determinations) != 1
}
debug := {
	"decision": decision,
	"u1_determinations": u1_determinations,
	"u1_size": count(u1_determinations),
	"fin_state": fin_state,
	"ins_state": ins_state,
}
