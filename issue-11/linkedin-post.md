# LinkedIn post candidate, Issue 11

The policy said the discharge needed a clinician. The run handed the discharge to the EHR integration anyway, and left the approval behind.

In pydantic-ai a tool can be external: the run returns the call and your integration executes it. I gave a discharge agent one such tool, a validation hook that raises ApprovalRequired for it, and a scripted model, no API key, on 2.66.0, last week's release.

The run came back with the discharge in calls, the list an executor runs, approvals empty, metadata gone. My stand-in executor wrote the row. 2.67.0, out Tuesday, raises before anything leaves the run and tells you the construction to use. 2.68.0, out Wednesday, moves the question: an approval and a pharmacist's free-text answer leave the run on a resume token and come back with answered_by. I ran that too: the name is on the event stream, accepted as given (I sent anyone@example.invalid and it took it), and nowhere in the message history. The typed answer did go through the redaction hook, which is the part to copy.

Same week, same seam. LangGraph 1.2.21: a parent can finally read a child it never declared (0 to 3 snapshots in the lab). Agent Framework 1.26.0 binds an approval to the stored call and fails closed when the history is unavailable. Claude Agent SDK 0.2.181 stops launching when settings will not load, where last week it launched with the rules dropped. A new paper: permissions alone let one radiology episode in five execute a high-severity violation.

The run knows a question is open and knows an answer arrived. It does not know who answered and does not write the name down. That line is yours. Code in the issue.

#HealthcareAI #AIVelocity #AgentArchitecture #ClinicalSafety #MCP
