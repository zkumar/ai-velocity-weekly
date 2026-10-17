# LinkedIn post candidate, Issue 03

My approval rule said IV orders need a clinician. The agent wrote an IV order and nobody was asked.

The model left out the route. The tool's default route was IV. The approval rule read the model's JSON, saw no route, and let it through; the tool ran on the validated arguments and wrote IV. Same with a dose sent as 1.5 g that a validator turned into 1,500 mg. I ran it with a scripted model and no API key on OpenAI's Agents SDK 0.22.2: two writes the rule should have stopped, zero approvals.

0.22.3, released on Thursday, fixes it properly: if validation would change the call, the rule is skipped and a human decides. Both writes now pause. But the human is shown the model's JSON too: no route, 1.5 g. They sign, and the order goes in IV at 1,500 mg. The gap moved from the policy to the screen.

The same week LangChain started keeping the model's proposed call in the transcript and the pharmacist's edited call in a private checkpoint key, and Microsoft's Agent Framework made any post-approval change to an argument void the approval. The question is no longer only who approves. It is what, exactly, they approved. Code and diagram in the issue.

#HealthcareAI #AIVelocity #AgentArchitecture #FHIR #ClinicalSafety
