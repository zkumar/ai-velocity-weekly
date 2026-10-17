# LinkedIn post candidate, Issue 04

The pharmacist approved two writes. One of them ran zero times. Nobody was told.

deepagents 0.7.16 shipped on Sunday with a sensible fix: if one model response carries two changes to the same file, the second is refused. I put the write tool behind human-in-the-loop, had a scripted model propose two care-plan writes, approved both, and counted. On 0.7.15: two approvals, two writes, the record holds Plan B. On 0.7.16: two approvals, one write, the record holds Plan A. The check runs after the approval middleware, so the reviewer signs a call the framework has already decided not to run. The model said "Both plans written." on both versions. No API key.

The same week llama-index-core 0.14.25 stopped executing a failing single-argument tool twice. Below that version, a tool that commits to the record and then raises was called again with keyword arguments: one call, one error, two rows. And Microsoft's Agent Framework team wrote, about checkpoint-and-recover hosting, "Recovery does not imply exactly-once execution of external effects."

Last week's question was what a yes is bound to. This week's is how many times it runs. Zero and two are both audit gaps, and both were reachable from a clean install. Reconcile approvals against tool results by call id, and make every write idempotent, because nothing between the yes and the record will do it for you. Code and diagram in the issue.

#HealthcareAI #AIVelocity #AgentArchitecture #FHIR #ClinicalSafety
