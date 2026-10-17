# LinkedIn post candidate, Issue 05

The nurse said "always" to a saline flush. A warfarin order from a different agent went through on it.

Two agents, intake and anticoagulation, each own a tool called place_order behind an approval gate. A scripted model has intake order a saline flush; the nurse answers "always approve"; the run hands off; the second agent orders warfarin 10 mg. On openai-agents 0.22.3 the nurse was shown one order and two reached the record, because the sticky yes was stored under the tool's name. On 0.23.1, released Friday, it is stored under the owning agent and the name, and the warfarin call stops and asks. On both versions the same "always" also covered heparin from the same agent: the key has no argument in it. No API key.

The same day agent-framework-core 1.20.0 moved the pending approval out of the transcript and into the session. On 1.19.0 a request the framework never issued, sent with its own yes, submitted a prior authorisation. On 1.20.0 it is dropped. So is a genuine approval replayed without a session: no submission, an empty reply, one warning in a log. And pydantic-ai 2.53.0 stopped running the wrong tool when two calls share an id; on 2.52.0 the chart was never read and the prior auth went out twice.

Issue 03 asked which arguments a yes covers. Issue 04 asked how many times it runs. This week's question is how far it reaches. Find every place a reviewer can say "always" and write down what the framework keys it by, then find where your pending approvals are stored. Five scripts, both versions each, in the issue.

#HealthcareAI #AIVelocity #AgentArchitecture #FHIR #ClinicalSafety
