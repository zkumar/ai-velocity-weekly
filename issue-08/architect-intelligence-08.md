# Architect Intelligence 08: The Gate Inside The Tool

Week Of Oct 17–25, 2026 · Vijay Zharotia

**Last week a batch failed and the write that finished was dropped from the history. This week the pharmacist's gate sat inside a child agent: the parent was handed an empty string, told the clinician the order was placed, and no request to approve it ever left the tool.**

Issue 07 read what the history keeps when one call in a batch fails. This week the unit became the delegate: an agent wrapped as another agent's tool, what the layer above receives when the child stops for a person, and whether the person it stopped for can be reached from there at all.

This week: 2 wheels unpacked and diffed, 12 runs of the executed mechanism, 12 papers read, 15 models priced.

## Five changes, one home each

Each fact appears once below. This list says where.

1. **A child agent paused for the pharmacist and its parent received an empty string, then an error, never the request** (Google Adk 2.13.0, executed), section 08
2. **Approval results released from separate resumes were kept in the thread snapshot only for the last one** (Agent Framework 1.23.0, docs), section 05
3. **A resumed Command's update is applied once and a finished subgraph is not rerun on resume** (Langgraph 1.2.16, docs), section 05
4. **Harness sub-agents stop handing approval requests to a parent that cannot resolve them** (Pydantic-Ai 2.58.0, docs), section 04
5. **Tool calls made in parallel were missing from session messages because one branch of the transcript was read** (Claude Agent Sdk 0.2.170, docs), section 04

## A Request Nobody Above Could Answer, a Branch Nobody Read, a Child Reporting Back

Three frameworks changed what a parent learns about a child's pause, cancellation or parallel work. All three read from release notes and changelogs; the delegate's pause is executed on slide 08.

### A harness sub-agent returned DeferredToolRequests to a parent with no way to resolve them

*Pydantic-Ai 2.58.0 And 2.61.0* · docs

2.58.0 (20 Oct), #10497: "Stop harness sub-agents from returning DeferredToolRequests to a parent that cannot resolve them." 2.61.0 (24 Oct), #11163: a sub-agent's RunCancelled is carried across the durable tool-call boundary as a failed tool result. In between, 2.60.0 added a ToolAvailabilityDeltaPart for every mid-run change to the tool set (#9405), deprecated RetryPromptPart in favour of ToolReturnPart(outcome='retried') (#8094), and showed the ApprovalReviewer the arguments as written (#10727).

**What changed.** A nested approval request now stops at the layer that can answer it instead of surfacing where nothing can, and a cancelled child is a failed tool result rather than a missing one. The history gains a part that records which tools existed at each step.

**What to change.** Pin 2.58.0 or later for any harness with sub-agents that gate writes; migrate history readers off RetryPromptPart; and log ToolAvailabilityDeltaPart, because an approval given when a tool was absent is a different approval.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-08/details.html)

### Session messages dropped tool calls made in parallel, and an MCP call was sent twice when the connection closed

*Claude Agent Sdk 0.2.170 · Claude Code 2.1.307 To 2.1.310* · docs

Python SDK 0.2.170 (21 Oct), #1422: get_session_messages "now return every tool call and result from turns that ran tools in parallel. Previously only one branch of the forked transcript was followed." Claude Code 2.1.307: HTTP MCP tool calls "being sent twice when the connection closed mid-call; only read-only or idempotent tools are now retried", and a claude_code.safety_event OpenTelemetry event for every tool call a rule, hook or sandbox stopped. 2.1.309: a session moved to a new runner "now sees the tool call that was interrupted, marked as outcome unknown." 2.1.310: a timed-out MCP call with an unanswered elicitation tells the model not to repeat it.

**What changed.** The transcript an audit reads from the SDK was missing whole branches of parallel tool use, and a write over HTTP MCP could run twice on a dropped connection. Three sentences now say what the model is told about an interrupted or unanswered call.

**What to change.** Re-export any session transcript produced before 0.2.170 that held parallel tool use, mark every HTTP MCP write tool idempotent or expect no retry, and subscribe your audit sink to safety_event.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-08/details.html)

### An async sub-agent now reports status, cancellation and completion to the agent that started it

*Deepagents 0.7.27 To 0.7.31* · docs

0.7.27 (16 Oct), #6853: "tell the main agent about async subagent status updates." 0.7.30 (22 Oct): follow-ups are queued "without interrupting active work" (#7082), notify_parent (#7132) and a webhook (#7072) on AsyncSubAgent, runs cancelled on the server are reported (#7060), and reasoning blocks bound to history a summary replaced are dropped (#7127). 0.7.31 exposes execution output retention metadata in tracing (#6876) and removes the handoff mode alias (#7165).

**What changed.** A parent that launched background work used to learn its outcome only by asking; now the child can push status, completion and cancellation, and a summary no longer leaves orphaned reasoning behind.

**What to change.** Route notify_parent and the webhook into the same audit table as the parent's own tool calls, keyed by the child's run id, and grep for the handoff alias before upgrading.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-08/details.html)

> **Architect signal.** Each framework chose a sentence for the parent to read when a child stops. None of the sentences carries the child's pending request; the parent is told about the gate, never handed it.

## One Result for Two Answers, One Update Applied Twice, One Scope for the Store

Two frameworks changed what happens when answers to approvals arrive and are released. Both read from pull requests and release notes.

### The AG-UI thread snapshot kept only the approval result whose answer arrived in the final request

*Microsoft · Agent Framework 1.23.0* · docs

PR #8851, closing #8789: with ToolApprovalMiddleware, decisions collected across separate resumes release as one batch, both calls run and both results stream, but the MESSAGES_SNAPSHOT and the persisted thread kept only the result matched to the current request. "The next user turn then replays both calls with one result, leaving an orphaned call in history." Each result is now recorded as it streams and persisted after the message that issued its call. #9413, breaking: every AG-UI registration must declare an authorization_scope_resolver or single_user=True, because thread ids are "client-owned protocol correlation values, not authorization boundaries". #9535 tightens settled-approval matching so a duplicate approval id cannot enable execution.

**What changed.** An approval answered one request earlier left no result in the record the next turn was built from, and approval state had no owner unless you configured one. Both are closed; the second one will not start until you name the scope.

**What to change.** Before upgrading, add the scope resolver to every AG-UI endpoint and search persisted threads for a call with no result beside a sibling that has one; those are the replays.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-08/details.html)

### A resumed Command's update was applied more than once and a finished subgraph reran on resume

*Langgraph 1.2.16* · docs

Released 16 October at 22:11 UTC, an hour after Issue 07 closed. #9322: "apply a resumed Command's update once." #9314: "save a resumed exit run's pending writes once." #9315: "stop a subgraph from rerunning its finished tasks on resume." #9265: "let other tasks finish when a resume value is invalid." PostgresSaver gains prune (#9290). 1.2.17 (24 Oct) is housekeeping and a certificate bump.

**What changed.** Four separate ways a resume could do work twice, or stop work that had nothing to do with the bad answer, are closed in one release. The approval answer you pass in Command(resume=...) now has one effect on state.

**What to change.** Pin 1.2.16 or later for any graph that resumes into a write; on earlier versions, compare the count of state updates after a resume with the count of answers given, per thread.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-08/details.html)

### A UI adapter could run a tool with client-chosen arguments and no model request; MCP credentials reached the traces

*Pydantic-Ai 2.58.0 · Two Security Advisories* · docs

GHSA-5pfm-2g3g-gh85: with server-side message_history and the default manage_system_prompt='server', "Vercel AI and AG-UI adapters could execute an available tool with client-chosen arguments without a model request." The advisory adds: "Approval-required tools are not executed by this path." GHSA-xv4x-g8mx-ch56: provider-native MCP configuration could put server URLs, authorization tokens and header values into OpenTelemetry request traces even with include_content=False. Fixed in 2.58.0 and 1.107.8; the advisory recommends rotating exposed credentials.

**What changed.** A client, not a model, could choose a tool call that the server ran; the gate you set on a tool was the only thing that kept it out of that path. Trace exports may hold MCP tokens for every run before 20 October.

**What to change.** Treat the approval requirement as the boundary it turned out to be and apply it to every write tool, rotate MCP credentials that passed through traced runs, and restrict who can read historical traces.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-08/details.html)

> **Architect signal.** Approval answers are now matched, scoped and applied once in two more frameworks. The remaining question is older than any of them, which party may release a batch of answers, and still has no field.

## A Medical Score That Fell Six Points Without a Model Changing

4,000 input and 500 output tokens per document, list prices read 25 October. Artificial Analysis is still v4.3.2; its healthcare index was recomposed and two rows could be read.

### Opus 5.5 reads 55 and Sonnet 5.5 reads 53 on an index that now names six evaluations

*Artificial Analysis · Healthcare & Medical Index, Read 25 Oct*

On 16 October the page gave Opus 5.5 at 61, Sonnet 5.5 at 58 and Fable 5.1 at 58. Today it describes six evaluations, Omniscience Health Accuracy at 30%, GDPval-AA and Briefcase at 25%, MLCR at 15%, Health Non-Hallucination 10%, HLE 10% and AutomationBench Support and Operations 10%, and its readable scores are Opus 5.5 at 55 and Sonnet 5.5 at 53; the Fable row could not be read. The 19 October changelog entry launched HealthBench and HealthBench Professional leaderboards. No cause is stated on the page.

**What changed.** The one independent medical number this series relies on changed its composition without a version string, so last week's figures and this week's are not the same measurement.

**What to change.** Store the index composition with every score you file, treat a score without a composition as unversioned, and do not compare a 16 October medical figure with a 25 October one.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-08/details.html)

### A new fourth-place model whose price page would not render, and a cache write that costs 2.5 times input

*Moonshot · Kimi K3.1 Pro, About 23 Oct · Openai 12-Hour Cache, 20 Oct*

Kimi K3.1 Pro appears on the Artificial Analysis changelog on 23 October at 55, "4th on the Intelligence Index", with weights promised by 4 November; the vendor's pricing tables returned empty on three reads, so its row carries a third-party price of 2, 10 and 0.20 and K3's row carries last week's. K2 models close to new users on 31 October. OpenAI's API changelog (20 Oct) adds a 12-hour prompt cache for Responses: "12-hour cache writes cost 2.5x the input token price." No tracked list price moved; Mistral's launch sale is gone from its page.

**What changed.** A model at the $130 price point now scores one below Sonnet 5.5 on the general index, with no vendor price readable and no medical score. A cache tier long enough for a working day exists, at a write price the table's cached column does not include.

**What to change.** Keep both Kimi rows out of a validation file until the vendor page renders, and model the 12-hour write as a per-document cost before assuming the 80% cached column.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-08/details.html)

> **Architect signal.** Two numbers in this table are independent and both moved this week without a model release behind them. A score is a measurement only when its method is pinned beside it.

## A Forged Approval That Survives Compaction, Two Allowed Calls That Add Up to a Breach

A summarizer that erases who said what, an authorization that does not compose, and a ledger written once for audits not yet designed. Numbers are the authors' own, from the abstracts.

### A forged user approval survived compaction 87% to 100% of the time in harnesses that flatten roles to text

*Compaction Laundering · 2610.29869*

Harnesses that flatten typed conversation into one string with labels like "[User]:" before summarising lose message provenance; content the agent merely read can be written as a user turn and come out of the summary as a standing instruction. "The forged approval launders into the agent's memory 87–100% of the time" across five flattening harnesses, "0% of the time" across four role-typed ones; a code-level provenance check "catches 77% of laundering while demoting 2% of legitimate summary content".

**What changed.** A compacted history is a place an approval can be invented, not only lost, and the summarizer is the party that signs it.

**What to change.** Keep role typing through every summary step and keep clinical approvals in a typed, signed channel the summarizer never reads; check your framework's compaction code for a flattening step.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-08/details.html)

### Nine judges approved two individually allowed calls that together violated the purpose a record was read for

*Local Allow, Global Deny · 2610.27620*

Individually authorized tool calls can jointly violate a policy over purpose, consent and delegation; the authors prove relational purpose violations are a 2-safety hyperproperty invisible to any per-action monitor, and synthesize minimal two-call witnesses with a solver and no model. "Across nine LLM judges the per-action view approves the synthesized witness almost without exception", while the same judges flag it when shown both executions together. None of six surveyed guardrails monitors across executions.

**What changed.** A per-call approval gate, the thing this series has been measuring for eight weeks, cannot see the violation that spans a read for one purpose and a disclosure for another.

**What to change.** Add a session-scoped monitor over pairs of calls to one patient record, and give any reviewer the prior calls beside the one it is judging.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-08/details.html)

### A 12B reader of one-time action ledgers matched or beat the same model reading the full trajectory, at a fifth of the tokens

*Write Once, Check Many · 2610.24483*

A writer model converts each trajectory once into a policy-independent ledger of actions and outcomes; any later policy is checked against the ledger alone. On 900 trajectories the ledger reader "can either match or in fact achieve higher AUC" than full-trajectory reading, beats a 31B trajectory reader on multi-fact policies at .777 against .713, and "ledgers use about 5x fewer tokens, including the cost of writing them". Caveat from the authors: ledgers "can miss evidence in long tool outputs".

**What changed.** The audit question a payer or regulator asks next year can be answered from a record written at run time, if the record is a ledger of actions rather than a transcript.

**What to change.** Emit a structured action ledger per patient session from the tool layer, not from a model summarising the transcript, and keep the long tool outputs it points to.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-08/details.html)

> **Architect signal.** Three papers, three places evidence is manufactured or missed between the action and the audit. The ledger has to be written by the layer that acted, in its own voice.

## Mechanism of the week: The child that stopped for the pharmacist, and what its parent was handed

*Google Adk 2.13.0 · Scripted Basellm, 2.12.0 Against 2.13.0, No Model Key*

A clinician-assistant agent delegates an apixaban order to a pharmacy agent wrapped as an AgentTool; the pharmacy agent's place_order requires confirmation. On 2.12.0 the child paused, AgentTool discarded its session, handed the parent {"result": ""}, and the scripted parent, with nothing else to go on, told the clinician the order was placed. No confirmation request reached the caller and the record held no row. On 2.13.0 the parent is handed an error naming the pending call id; the gate is still unreachable. Listed under sub_agents instead, the pause surfaces on both versions, and on 2.13.0 the answered turn routes back to the delegator. In a second check, a hold appended to nested session state was absent from the persisted session on 2.12.0 and present on 2.13.0.

**"" → Error** what the parent was handed when the child paused · **0** confirmation requests that reached the caller through agenttool, either version · **[] → [apixaban]** the nested hold in the persisted session, 2.12.0 against 2.13.0

**What changed.** AgentTool returned last_error_message or an empty string when the child's final content had no text; 2.13.0 tracks the child's long_running_tool_ids, subtracts those answered before the run ends, and returns a named error for the rest. A gate inside an AgentTool cannot be answered on any version. The state fix compares each container a read handed out with a copy and records the changed ones when the event is built.

**Move.** Find every AgentTool whose child owns a tool with require_confirmation or a long-running pause and move the child under sub_agents with mode single_turn, or lift the gated tool to the parent. Search transcripts from 2.12.0 and earlier for an AgentTool result of "" followed by a success sentence. Write holds and flags as top-level state keys until 2.13.0 is everywhere, and diff persisted session state against what the tool saw in its tests.

[Open the lab package](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-08/lab)

> **Architect signal.** The parent's sentence was correct as a reading of an empty string and wrong as a statement about the record. A tool result that is empty because a person was never asked needs its own name, and the frameworks have just started giving it one.

## What the architects shipped

- **Epic.** Connectors, announced at Open@Epic on 21 October: Epic's agents call third-party apps over the Model Context Protocol, each Connector enabled only after a health system's security, legal and compliance review. Johnston Thayer, per Fierce Healthcare: "There will not be new autonomous actions taken as a result of these capabilities." Testing with partners by year end, Showroom listing from the first quarter. The same day open.epic added USCDI v5 and US Core 8 support, _lastUpdated search on results and labs, and playbooks for utilization review and payer medical-necessity guideline creation. A developer MCP server was promised "at the end of this month".
- **Anthropic.** Python SDK 2.0.0 (21 Oct) moves to API version 2026-10-21 and the SDK family to Apache 2.0; the breaking list is on slide 10. 2.2.0 adds message threads and four tool-runner fixes, one of which leaves the runner's history to the caller after append_messages. Agent Skills, its name and agentskills.io were donated to the Agentic AI Foundation on 22 October with a roadmap line on "security guidance for people who write and install skills".
- **Openai.** The Decisions API reached general availability on gpt-6-luna on 22 October with 400 questions per request and structured input; Python 3.37.0 the same day breaks the Decisions types. Projects can now be restricted to named service tiers (21 Oct). The 23 October legacy shutdown happened as dated: the deprecations page reads "Access to these models was shut down on October 23, 2026." @openai/agents-core 0.21.0 moves run-state snapshots to schema 1.23.
- **Google.** ADK 2.13.0 (23 Oct) is on slide 08 for its delegation and state fixes. Also in it, breaking: telemetry defaults to the OpenTelemetry GenAI v2 schema and drops the call_llm span unless ADK_TELEMETRY_SCHEMA_VERSION_OPT_IN keeps the old one; tool call content is reported under the semconv attributes; compactions are counted per workflow; twelve experimental features are promoted to stable; MongoDB session and memory services arrive experimental.
- **Anaconda.** Two governance posts: "Bank Model Risk Guidance No Longer Covers Generative AI. Who Owns the Testing?" (21 Oct), on the US banking regulators' model-risk guidance withdrawal, and "The State of AI Regulation Heading Into 2027" (20 Oct). Read from the public blog; the emailed edition could not be opened this run.
- **Nvidia.** OpenShell, "a secure runtime boundary for autonomous agents", and Sentry, out-of-band monitoring of agent behaviour on BlueField-4, both announced 21 October; healthcare is named as a target industry, no clinical integration is. A GTC Berlin release lists Avelios, Corti, Dedalus and Sword building scribes and clinical assistants on Nemotron.

Nothing in window from the MCP specification or Python SDK, Semantic Kernel, llama-index-core, transformers, ASTP/ONC, OCR or ARPA-H on agents; HL7's feed carried only tx-ecosystem 1.10.0 and SMART Scheduling Links 1.0.0. Matt Pocock's site has no dated post in window. The editor's newsletter inbox was not readable this run; the senders' public pages were read instead.

> **Architect signal.** Three vendors shipped the parent's side of delegation this week, a connector, a thread and a decision endpoint. Each one adds a party that can act on a patient's behalf and none adds a field for the person who allowed it.

## A Drug-Software Guidance Finalised, Two Comment Windows Closing Wednesday, and an API Version With a Date

### Software output disseminated for a prescription drug is labeling, and the ePA stack reaches self-funded plans by pledge rather than rule

*Fda · Prescription Drug Use-Related Software, Final 20 October · Cms And Hl7, 21 And 28 October*

FDA's final guidance "describes FDA's application of its drug labeling authorities to certain software outputs that are disseminated by or on behalf of a drug sponsor for use with a prescription drug product", finalising the September 2023 draft; it names no AI. The generative-AI device docket FDA-2026-N-7874 closed on 19 October with 129 comments posted and none posted since 30 September. CMS announced on 21 October that Amazon, Axon, Google, Meta and Oracle extend the prior-authorization pledge to self-funded plans, restating 1 January 2027 for CMS-0057-F. HL7's Da Vinci roundtable on ePA with CMS staff is Wednesday 28 October; NIH's proposed Chief AI Officer notice takes comments until the same day.

**Move.** If an agent surfaces sponsor-supplied dosing or coaching content in a workflow, route it through the drug sponsor's labeling review, not the device file. Put 28 October in the calendar twice, and check the FDA docket again in two weeks when the deadline-day comments post.

### temperature, top_p and top_k return 400 on the new API version, the key moves to a Bearer header, and four frameworks bumped certifi in one week

*Anthropic · Api Version 2026-10-21 · Certificate Authority Incident, 19 To 23 October*

Per the migration guide, requests on 2026-10-21 that send temperature, top_p or top_k fail "even at default values"; document blocks in assistant messages and citations in user messages fail; API keys are sent as Authorization: Bearer; a client holds one credential; client-side compaction is removed from the TypeScript and Ruby tool runners in favour of server-side context_management; MessageParam becomes a union by role. Older SDK majors keep 2023-06-01. Separately, fastmcp 4.1.3 requires certifi 2026.10.19 "following the eMudhra CA compromise" and says upgrading FastMCP alone is insufficient; langgraph 1.2.17, langchain 1.4.7 and deepagents 0.7.30 carry the same bump, and Nebius published the advisory on 23 October.

**Move.** A validated prompt with a non-default temperature cannot move to the new version unchanged; re-validate or pin the old version per request. Proxies that read X-Api-Key break on 2.0.0. Update operating-system and container trust stores, not only Python packages, and record the certifi version in the validation file.

Every dated source for this week is in the long-form edition. The cumulative Radar was not refreshed this week. [Open the Radar](https://zkumar.github.io/ai-velocity-weekly/index.html)

> **Architect signal.** One guidance decides which review a model's words must pass before a patient sees them, and one API version decides which validated requests still run. Both are change-control entries with a date, not news.

---

Full mechanism, code and sources for every card are in the long-form edition. The architect's position on this week's decision is in My Take. The code runs from a clean virtual environment with no API key. Everything is at https://github.com/zkumar/ai-velocity-weekly .
