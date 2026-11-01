# LinkedIn post candidate, Issue 09

The pharmacy tool refused the order and said why. The model was told. The framework's log was told "Error type: ValueError."

Semantic Kernel 1.46.0, out Wednesday, stops writing function arguments, results and exception text to its own loggers. Good: on 1.45.0 every tool call's argument JSON, patient id included, went into the application log at INFO. I ran one apixaban order through both versions with a scripted model, no API key, and a sink on the framework's loggers.

1.45.0: three log lines carried the patient id; when the pharmacy tool refused the order, two carried the reason. 1.46.0: zero and zero, while the model received the full refusal text on both and the record held the same rows. If any part of your audit trail was that log, it lost three columns in a minor release. If you are still on 1.45.0, it is a disclosure review before it is an upgrade.

Same week, same seam. LangGraph 1.2.18 streams the checkpoint a run stopped on; on 1.2.17 a client resuming from the last one it saw re-drafted the order the pharmacist had approved and wrote nothing. Claude Code withdrew the safety_event telemetry it added three weeks ago. And HHS finalised HTI-5, which removes the model-card requirements for predictive decision support from certification on 28 December and names MCP in the rule text. The record did not change this week. The record about the record did. Write your own ledger from the layer that acts. Code in the issue.

#HealthcareAI #AIVelocity #AgentArchitecture #FHIR #ClinicalSafety
