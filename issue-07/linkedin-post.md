# LinkedIn post candidate, Issue 07

The allergy check failed. The order beside it went in. The transcript said neither had happened.

A model asks for two things at once: look up the patient's allergies, and place the apixaban order. The agent runs both. The order is written in milliseconds; the allergy service is down and raises a moment later. The framework fails the run, which is right. I built that in pydantic-ai with no model and no API key, then did what any durable executor does after an error: resumed from the history I had kept.

On 2.54.0, under the ordered-events mode DBOS uses by default, that history held no return for the order. The resume told the model the call had been "interrupted before a result was produced." The model ordered again. One patient, two apixaban orders, and the model's closing sentence was word for word the same as in the run that wrote one. 2.55.0, out last Friday, keeps the return. The default mode never lost it. A caller that cancels the run gets the same result as a sibling that raises.

The same seam moved elsewhere this week. OpenAI's Agents SDK stopped dropping a finished tool's output when a sibling's guardrail trips, and stopped compacting a history with an approval still open. LangChain's gate can now pause once per call instead of once per turn. Agent Framework stopped a browser's shared state from overwriting what the server thinks was approved. And a framework shipped a reviewer that lets a model approve low-risk calls before a person sees them. When a batch fails, ask the record what happened before the history tells the model. Code in the issue.

#HealthcareAI #AIVelocity #AgentArchitecture #FHIR #ClinicalSafety
