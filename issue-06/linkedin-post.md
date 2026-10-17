# LinkedIn post candidate, Issue 06

The pharmacist approved once. The record holds three pharmacy signatures.

A discharge needs two approvals, pharmacy and physician, so the agent pauses and asks both. I built that in LangGraph with no model and no API key: two parallel gates, each of which signs the order and returns nothing. The pharmacist answered. On 1.2.12 the paused thread still listed the pharmacist's question as open. A second reviewer answered it again, with a rejection; it was accepted without error and ignored, and the gate signed again. When the physician answered, it signed a third time. Two approvals, four rows.

LangGraph 1.2.13, released Monday, fixes it: one question left in the inbox, two rows. But a thread that was already paused when I upgraded wrote the pharmacy signature again on the new version. The fix is real and it does not reach back.

Four other frameworks moved the same seam this week. One now runs a write before the human answers the question that came with it. One reports a timeout for a write that committed. One runs the approved tool and then throws. One lets a cache skip the audit hook. A paused run is state. Keep your own list of what was asked and what was answered, make the write idempotent, and after any error ask the record before you retry. Code in the issue.

#HealthcareAI #AIVelocity #AgentArchitecture #FHIR #ClinicalSafety
