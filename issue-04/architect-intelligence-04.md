# Architect Intelligence 04: After The Yes

Week Of Sep 19–25, 2026 · Vijay Zharotia

**Last week the yes was bound to arguments. This week a reviewer approved two writes and one ran zero times, a failing write ran twice, and a vendor put in writing that recovery is not exactly-once.**

Issue 03 asked which arguments a clinician's approval covers. This week the frameworks answered a later question, how many times the approved write actually runs, and the answers were zero, two, and not promised.

This week: 22 repos cloned and read, 3 mechanisms executed, 8 papers read, 17 models priced.

## Five changes, one home each

Each fact appears once below. This list says where.

1. **An approved second write executes zero times after the signature** (Deepagents 0.7.16, executed), section 08
2. **A failing single-argument tool was called again, one error, two rows** (Llama-Index-Core 0.14.25, executed), section 04
3. **A typed approval validates for the node and persists the raw value** (Langgraph 1.2.12, executed), section 04
4. **A child agent's unresolved approval fails the parent tool** (Agent Framework Main, docs), section 04
5. **The PHI-on-span flag answered for the wrong instrumentation** (Pydantic-Ai 2.49.0, docs), section 05

## How Many Times an Approved Write Runs

Two executed, one read from source. The deepagents change is executed on slide 08.

### One tool call, one error in the trace, two rows in the record

*Llama-Index-Core 0.14.25* · executed

Below 0.14.25 call_tool() ran a one-parameter FunctionTool positionally, caught any exception, and ran it again with keyword arguments. A tool that appends a note then raises a gateway timeout wrote twice on 0.14.24 and once on 0.14.25. The caller saw one call and is_error=True both times.

**What changed.** The retry lived inside the framework, below the trace and the transcript. Nothing you export could have shown the second row.

**What to change.** Give every write an idempotency key the tool checks before it commits, and count duplicate rows created within seconds of a tool error on any llama-index deployment below 0.14.25.

[Read the mechanism](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-04/lab)

### interrupt(response_schema=Decision) refuses "aprove" and stays paused

*Langgraph 1.2.12* · executed

A Pydantic schema validates the resume value before the node sees it; a typo raises out of invoke() and the graph stays at the gate. A JSON Schema dict validates nothing, and the same typo is committed and read as a rejection, as 1.2.11 did with no schema. The checkpoint persists the raw value the client sent.

**What changed.** The approval can be a typed object with an approver id, and a bad one is refused before the checkpoint moves.

**What to change.** Use a Pydantic model, never a dict. Catch ValidationError in the approval service and re-prompt. Store the validated decision from inside the node; the checkpoint holds the unvalidated one.

[Read the mechanism](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-04/lab)

### Unresolved child approvals fail closed, and a matched result is terminal

*Microsoft · Agent Framework Main* · docs

On main since 1.19.0. An agent used as a tool that returns only an approval request now fails the parent call; delayed approval belongs in a workflow. A matched function result is terminal "regardless of its text, including an exact or embedded [APPROVAL_PENDING]". Sequential output waits for approval; .NET consumes stored approvals only when the run succeeds.

**What changed.** Placeholder-text approvals are gone, a parent cannot forward a child's yes to the human, and one approval can now authorise a retried run.

**What to change.** Migrate any session store holding [APPROVAL_PENDING] before upgrading, give parent and child middleware distinct source_id values, and make the idempotency key cover the retry.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-04/details.html)

> **Architect signal.** An approval with no matching success result is a claim about the record, not a fact about it. Join approvals to tool results by call id before anything is reported as done.

## Secrets and PHI Outside the Policy's Reach

Both read from source and commit messages, neither executed. Each is data that left by a path the redaction setting did not govern.

### ctx.trace_include_content answered for the global settings, not the run's

*Pydantic-Ai 2.49.0* · docs

With instrument_all(include_content=True) and an agent-level Instrumentation(include_content=False), the run context reported True and handed tools the global tracer. A tool that put a patient id on a span only when the flag allowed it wrote PHI to a second tracer provider. From 2.49.0 the context follows the capability that instruments the run.

**What changed.** Two records again, the run's spans redacted and your own audit spans not, on different providers feeding the same collector.

**What to change.** Upgrade, then search custom spans from tools since you set a per-agent redaction. Add a test that a tool span carries no PHI attribute when the agent's setting is off.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-04/details.html)

### A client secret in the session table, a user token in the compaction prompt

*Google Adk Main* · docs

Unreleased since 2.9.2. One commit keeps the client secret out of session state, and says a session already persisted by a durable backend "still holds the secret in clear text, so rotate any OAuth2 client secret". Another keeps credential-request events, "the end user's token, PKCE verifier and auth code", out of the compaction prompt. A third skips confirmation requests authored by another agent, matched by name.

**What changed.** The FHIR server's client secret and the end user's token both had paths into stores and prompts that no policy covered.

**What to change.** Rotate the client secret for every durable session backend now, search summarised sessions for credential events, and give every sub-agent a unique name before you rely on the confirmation fix.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-04/details.html)

> **Architect signal.** A redaction setting governs the spans the framework writes. Everything your own code writes, and everything the framework persisted before the fix, is a separate audit.

## The Frontier Repriced and the Index Re-anchored

4,000 input and 500 output tokens per document, list prices read 25 September. Artificial Analysis moved to v4.3.2 on 19 September; two rows dropped a point with no release.

### Opus 5.5 does the job for $260 and leads both indexes, 58 and 60.5

*Anthropic · Claude Opus 5.5, New 22 Sept*

$4 in, $20 out, $0.20 cached, against Opus 5 at 5/25/0.50. That is $65 under Opus 5 uncached and $43 under it cached, and first on the Intelligence Index and the Healthcare & Medical Index. Anthropic says the 4.7-and-later tokenizer yields about 30% more tokens for the same text*, so real documents may cost up to a third more than the table.

**What changed.** The cheapest frontier row is now also the strongest, and the cache-read rate fell by more than the list price did.

**What to change.** Re-tokenise a sample of your own documents before you budget on the table, and price the cached run, because the cache rate is where this release moved most.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-04/details.html)

### Sol at $130 is half its predecessor and two points lower on the medical index

*Openai · Gpt-6 Sol And Luna, New 22 Sept*

Sol is 2/10/0.20, Luna 0.10/0.50/0.01, with Batch and Flex at half. Sol reads 48 on the general index against GPT-5.6 Sol's 47, and 43.5 on the medical index against 45.4, with a long-context sub-score of 16 against 26. Luna at $6.50 is the cheapest row above index 35. AA marks GPT-5.6 Sol and Opus 5 deprecated.

**What changed.** A successor can be cheaper and higher on the general index while lower on the medical one. The two indexes disagreed this week for the first time in the series.

**What to change.** Record both index scores, the date read and the deprecation flag in the validation file. A deprecated model is a migration deadline you do not control.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-04/details.html)

> **Architect signal.** Two new cache rates and a new tokenizer moved the cached column more than the sticker did. Price the run you will actually make, with your own documents.

## Approve A, Execute B, and the Rows Nobody Counted

Three results on substitution after approval, effects beyond the approved call, and successes a tool never reported. Each is a claim; each note is the build change.

### A human approves A and the system executes B, in 7 Agno and 12 LangGraph server versions

*Loopjacking · 2609.21081, Approval Laundering · 2609.28586*

Substitution after approval, by misrepresentation or by mutating workflow state, reproduced in seven Agno AgentOS releases and 12 LangGraph Agent Server compositions; OpenAI Agents SDK 0.22.x rejected the mutated call. The companion paper counts what an approval record omits, 40 residual effects under explicit fields down to 13 with decision-time metadata.

**What changed.** The approval object needs the canonical payload and the predicted downstream effects, not the entry call alone.

**What to change.** Hash the full action payload at approval and compare it at execution; write linked orders and notifications into the approval row, not only the top-level call.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-04/details.html)

### 1,268 synthetic patients behind a function-calling EHR, and the best model misses half the findings

*Synthetic Hospital · 2609.30027*

A PHI-free longitudinal record, every finding coded and traceable, served through a simulated hospital system with interoperability APIs and role-based access. Physicians told it from real charts at 53%. The best model rebuilds the problem list at severity-weighted F1 0.73, level with the mean of seven physicians, and "misses roughly half of clinically relevant findings when summarizing a chart".

**What changed.** A CI harness for a tool-calling EHR agent now exists with no PHI in it.

**What to change.** Put it in the pipeline and gate chart summarisation on recall of findings, not on fluency or a task score.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-04/details.html)

### 91 tool calls that looked like successes and returned incomplete data

*Silent Failures · 2609.26836*

An audit of 15 biomedical tools for calls that return missing fields, unapplied filters or inconsistent rankings with no error signal to the agent. 51 of the 91 failures were in the API layer and 25 in the wrapper. The agent proceeded on every one of them.

**What changed.** A tool result with status success is a claim from the wrapper, and the wrapper was wrong 91 times.

**What to change.** Validate every tool response for expected fields, plausible counts and applied filters before the model sees it, and record a failed check as provenance on the answer.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-04/details.html)

> **Architect signal.** Substitution after the yes, effects beyond the call, successes the tool never earned. Each is a row the audit table needs and the framework does not write.

## Mechanism of the week: The approved write that was refused after the signature

*Deepagents 0.7.16 · Scripted Model, 0.7.15 Against 0.7.16, No Model Key*

A care plan behind human-in-the-loop on write_file. The scripted model proposes two writes to the same plan in one response; the reviewer is shown both and approves both. On 0.7.15 both ran and the record held the second, Plan B. On 0.7.16 a new check in wrap_tool_call, after the approval middleware, answered the second with an error ToolMessage and never ran it; the record held Plan A. Without a gate, which write wins flipped from last to first. The model said "Both plans written." on both versions.

**2 → 1** writes executed for 2 approvals, 0.7.15 to 0.7.16 · **0** notices to the reviewer that an approved call was refused · **last → first** which parallel write wins the record

**What changed.** The gap moved from the screen to the count. The reviewer signed a call the framework had already decided not to run, and the only record of that is a status field on a ToolMessage.

**Move.** After every resume, join each approved action request to a success ToolMessage by call id and treat a miss as an incident, not a retry. Re-run any evaluation that scored a final plan, because first-wins is a different system from last-wins. test_da_parallel_writes.py runs both versions in under two minutes.

[Open the lab package](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-04/lab)

> **Architect signal.** The fix is defensible and the reviewer is not told. Whether an approval became a write is a join you have to run yourself, every time.

## What the architects shipped

- **Chai.** Takes stewardship of OVERT, an open specification for cryptographically signed runtime evidence of agent tool calls, from Glacis. The first candidate record format for the evidence this series keeps asking for.
- **Langchain.** A healthcare reliability write-up with Abridge's five-stage release gates and clinician annotation queues, and Trajectories, a readable per-session projection over traces in LangSmith.
- **Microsoft.** Checkpoint-and-recover hosting for Agent Framework with the line "Recovery does not imply exactly-once execution of external effects", and Foundry egress policies with Audit and Enforced modes.
- **Uk Aisi.** Verified transcript-level results on five benchmarks including HealthBench across six frontier models, published with Hugging Face and EvalEval in the Every Eval Ever schema.
- **Openai.** Seven principles for third-party assessments, pre-registered claims and remediation time among them, and MentalHealthBench, built with 80-plus licensed clinicians across 19 languages.

Nothing in window from HL7 beyond a webinar notice, FDA on generative AI, ONC, CMS on AI, NIST, Epic, the MCP blog, the Anthropic engineering blog, NVIDIA healthcare or Google Health. Oracle Health launched write-side agents for oncology and revenue cycle with no published approval or audit contract.

> **Architect signal.** A signed-evidence specification found a health-sector home the same week two EHR agent launches published no evidence format at all.

## Autonomy Gets a Docket and Critical Care Gets a Budget

### The first FDA forum on benefit-risk for autonomous devices, comments on surgical robots due 24 November

*Fda · Docket Fda-2026-N-9505 And A December Workshop*

A public workshop on 2 to 3 December on robotic devices with "autonomous and/or remote teleoperation capabilities", and a draft guidance on robotically-assisted surgical device submissions, described as "teleoperated, software-controlled systems". The generative-AI discussion paper is unchanged and its comments close 19 October.

**Move.** How FDA frames autonomy for a robot in December is the vocabulary it will reuse for an agent. File on both dockets; the earlier one closes in three weeks.

### $144.9M over five years for ICU decision support, and no data or audit standard named

*Arpa-H · Circle*

Performers selected 22 September, Stanford, Vermont, Novelna, Verily, Sage Bionetworks and Vanderbilt, for real-time monitoring and immunotherapy guidance in critical care. Like ADVOCATE in Issue 02, the announcement names an AI decision-support role and no record format for what the system recommended and who acted.

**Move.** If you are on a performer team, propose the evidence record now, before the platform is built around a log that cannot answer an auditor.

Every dated source for this week is in the long-form edition. The cumulative Radar was not refreshed this week. [Open the Radar](https://zkumar.github.io/ai-velocity-weekly/index.html)

> **Architect signal.** One regulator opened a vocabulary for autonomy and one funder opened a budget for it. Neither said what the record of a decision must contain; that is still yours to write.

---

Full mechanism, code and sources for every card are in the long-form edition. The architect's position on this week's decision is in My Take. The code runs from a clean virtual environment with no API key. Everything is at https://github.com/zkumar/ai-velocity-weekly .
