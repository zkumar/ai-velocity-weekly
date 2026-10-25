# LinkedIn post candidate, Issue 08

The pharmacy agent stopped for the pharmacist. Its parent was handed an empty string. The clinician was told the order was placed.

You build the sensible thing: an assistant that does not write orders itself but delegates to a pharmacy agent, whose order tool needs a pharmacist's confirmation. Then you compose them the way the framework shows, child as tool. I built that in Google ADK with no model and no API key, and let the child pause for its pharmacist.

On 2.12.0 the parent received {"result": ""}. No request to approve anything reached the caller. The record held no row. And the parent, with an empty string and nothing else, told the clinician the order was placed. 2.13.0, out on Thursday, hands the parent an error naming the pending call instead, which is better and still unanswerable: a gate inside an agent-as-tool cannot be reached by anyone on either version. Wire the child as a sub-agent and the pause surfaces; on 2.13.0 the answer even comes back to the agent that delegated. A second check: a hold appended to nested state never reached the session store on 2.12.0.

The same seam moved elsewhere this week. pydantic-ai stopped sub-agents handing approval requests to a parent that cannot resolve them. The Claude Agent SDK stopped dropping whole branches of parallel tool calls from session transcripts. Agent Framework stopped a thread snapshot from keeping only the last of several approval results. When you wrap an agent as a tool, ask what the parent is handed the moment the child stops for a person. Code in the issue.

#HealthcareAI #AIVelocity #AgentArchitecture #FHIR #ClinicalSafety
