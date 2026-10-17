# LinkedIn post candidate, Issue 01

The human step in your agent loop just moved. Four times, in one week.

LangChain 1.4 lets an MCP tool server demand a clinician's signature mid-call and park the run in a checkpoint. OpenAI's Responses API lets the model keep drafting while your FHIR lookup runs, and lets you steer it mid-turn. Microsoft's Agent Framework now binds an approval to a stable occurrence id, so a replayed history can't re-arm an old approval against a new write. Anthropic's ant apply puts the whole agent under a lock file that refuses to deploy over drift.

I cloned the repos and ran the two mechanisms that matter most. Two things I did not expect: the LangChain PR text advertises an elicitation flag that isn't in the merged code (it's on by default), and in the Agent Framework a forged approval id is correctly rejected but the model still answers "Order placed." while nothing ran. The model's text is never your source of truth for whether a write happened.

For regulated deployments the pattern is now clear. Approval lives in the tool protocol or the session store, not the prompt. State is mandatory, so idempotency at the FHIR layer is part of your correctness argument. Audit gets three new objects: the elicitation record, the occurrence id, and the lock-file hash. Code and diagram in the issue.

#HealthcareAI #AIVelocity #AgentArchitecture #FHIR #MCP
