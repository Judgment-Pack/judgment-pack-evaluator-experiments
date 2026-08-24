<!-- GENERATED FILE. Do not edit by hand; regenerate with deformalize.py. -->

# What your policy must produce (arm B)

Your policy must produce a decision object. It must have a disposition field, and its value is one of "approve", "review", "enhanced-review", "reject" or "unresolved". It must have a reasons field, which is a list whose entries are drawn from "missing-required-evidence", "unknown", "no-match" and "exception-escalation". When the disposition is "unresolved", the reasons list has at least one entry. When the disposition is anything other than "unresolved", the reasons list is empty. It has no fields other than "disposition" and "reasons".

Use those field names and those values exactly as spelled here.
