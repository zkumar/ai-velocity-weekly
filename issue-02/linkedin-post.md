# LinkedIn post candidate, Issue 02

I gave an agent a 30-minute budget and a clinician who took 40. The order vanished and the model said "Order placed."

Microsoft's Agent Framework 1.18.0 added a wall-clock budget to the tool loop, and the docstring says the budget includes time spent waiting for human approval. Intentional, and sensible for unattended runs. So I ran it with a scripted model and no API key: a MedicationRequest write that requires approval, the session serialised to JSON while the clinician thinks, then the approval comes back after the budget.

Result: zero writes, no function result, no rejection, no exception. One INFO log line. The model is called with tools withdrawn, and with nothing to go on it says the order was placed. Your audit table records an approval by NPI at 10:41; the FHIR server has no order. And the budget only survives the round trip when ToolApprovalMiddleware is attached; without it the clock quietly restarts.

The same week, the MCP Python SDK let a FHIR tool server refuse a token minted for the scheduling server, Anthropic added a server-side permission policy that decides before a human sees the call, and Google's ADK started re-running failed workflow nodes on resume. The human step is getting clocks, audiences and pre-checks. Each is a place your approval record and your system of record can disagree. Code and diagram in the issue.

#HealthcareAI #AIVelocity #AgentArchitecture #FHIR #MCP
