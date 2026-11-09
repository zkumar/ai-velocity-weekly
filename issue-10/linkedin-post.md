# LinkedIn post candidate, Issue 10

The approval policy named the write that needed a clinician and the read that did not. The pharmacy server had a second write. Nobody was asked.

Microsoft Agent Framework's approval policy for a local MCP server is two lists of tool names. I gave it place_order (always ask) and read_chart (never ask), then had a scripted model, no API key, call discontinue_order, a tool on neither list, on 1.23.0 and on 1.24.0.

Both versions: zero approval requests, one row in the record, and a closing sentence identical to the one for an approved write. A tool nobody listed resolves to "never require". 1.24.0 adds a warning and one key, "default": "always_require", that closes it. The same policy file on 1.23.0 is accepted in silence, the key is never read, and the write runs. And a name list written as one comma-joined string gated both writes by accident on 1.23.0 and gates nothing on 1.24.0.

Same week, same seam. pydantic-ai 2.66.0: a toolset marked "requires approval" ran a prebuilt Tool instance without asking on 2.65.0 (ran that too: one call waiting, one write already made). Claude Agent SDK: a PreToolUse guard that crashed let the tool run until this week's on_failure="block". LangGraph 1.2.20: a duplicate approval is refused only if you opt in. A new arXiv paper read 41 MCP hosts and found 32 with no approval step by default.

A gate is configured for the cases its author thought of. Find out what yours does with the rest: add a tool, call it, count the rows. Code in the issue.

#HealthcareAI #AIVelocity #AgentArchitecture #MCP #ClinicalSafety
