# Architect Intelligence 09: The Record That Thinned

Week Of Oct 24–30, 2026 · Vijay Zharotia

**Last week a child agent paused for its pharmacist and all its parent received was an empty string. This week the record thinned from three directions: a framework's log stopped carrying what was ordered and why it was refused, a paused run never streamed the checkpoint it stopped on, and a federal rule removed the model card from certified decision support.**

Issue 08 read what a parent agent is handed when its child stops for a person. This week the subject is the record itself: which lines a framework writes about an action in its own log and trace, which checkpoint a caller is shown before it resumes, and which fields a regulator still requires a certified system to keep.

This week: 4 wheels unpacked and diffed, 8 runs of the executed mechanism, 14 papers read, 17 models priced.

## Five changes, one home each

Each fact appears once below. This list says where.

1. **The framework's log stopped carrying an order's arguments, result and refusal reason, while the model was still told all three** (Semantic Kernel 1.46.0, executed), section 08
2. **A run paused for review never streamed the checkpoint it stopped on, and a client resuming from the last one it saw re-drafted the order** (Langgraph 1.2.18, executed), section 08
3. **The safety_event telemetry event added three weeks ago is no longer sent; a guardrail_trace and a write boundary arrive instead** (Claude Code 2.1.312 And 2.1.314, docs), section 04
4. **A function call whose namespace did not match its registration now invokes no callback and submits no result** (Openai Python 3.38.0, docs), section 05
5. **Model-card and risk-management requirements for predictive decision support are removed from certification on 28 December** (Hhs Astp/Onc Hti-5 Final Rule, docs), section 10

## A Response the History Lost, a Label That Is Not a Trust Boundary, an Event That Stopped Arriving

Three projects changed what their history, trace or log carries about a run. All three read from release notes, pull requests and changelogs; the framework log is executed on slide 08.

### The model response that crossed a token or cost limit was billed and dropped from the captured history

*Pydantic-Ai 2.62.0 And 2.63.0* · docs

2.62.0 (27 Oct), #11413: "The response crossing a token or cost limit is kept in capture_run_messages." Before, the over-limit ModelResponse was paid for and absent from the messages the caller captured, so a resume with that history asked for it again; now it is appended with state='interrupted' before the limit raises. 2.63.0 (28 Oct), #11460: ToolOutputLimits spill writes run in a durable_operation "so replays don't rewrite them"; #11471 adds a DetectLoops capability with a telemetry span per detection; #11504 replays signed history to any provider with the same canonical_system; #11431 adds manage_message_history to UI adapters "so server-held history isn't sent twice". 2.62.0 also makes SubAgents delegations background-able tasks with a pending_question field (#10893).

**What changed.** A response the account paid for and the audit never saw is now in the history with a state that says why it stopped, and a durable replay no longer rewrites what a tool spilled to a store.

**What to change.** Pin 2.62.0 or later for any run with usage limits around a write; on earlier versions reconcile billed requests against captured responses per run, and read DetectLoops' span before adopting its default nudge.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-09/details.html)

### Harness-injected messages get a provenance label whose docstring says it is not a trust boundary

*Langchain-Core 1.7.1 To 1.7.3 · Langgraph-Sdk 0.4.10* · docs

langchain-core 1.7.2 (29 Oct), #41540: add_notification_metadata marks a HumanMessage with lc_source and lc_data so deepagents and Managed Deep Agents stop inventing their own keys for background-task updates and summaries; the docstring says the keys are labels, not a trust boundary. #41502: merge_content copied a list before appending, ending duplicated text when a stream and a later step merged the same chunks. 1.7.1, #41504: gateway tracing metadata reaches traces on success and failure. 1.7.3 requires certifi 2026.10.19. langgraph-sdk 0.4.10 (26 Oct), #9399: the sync runs.wait now raises on a run error instead of returning {"__error__": ...} as a result.

**What changed.** A message the harness wrote now says so in a field, and a caller that read a run error as a normal result on the sync client will now see an exception.

**What to change.** Have your audit reader record lc_source for every human-role message and treat an unlabeled one as the person's only after checking the channel it arrived on; catch the new exception on sync waits, or pass raise_error=False.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-09/details.html)

### The safety_event span added in 2.1.307 is withdrawn in 2.1.312, and transcripts were being saved out of order

*Claude Code 2.1.311 To 2.1.314 · Claude Agent Sdk 0.3.312 And 0.3.314* · docs

2.1.311 (26 Oct): "Fixed claude -p and SDK sessions saving transcript messages out of order or keeping messages that were taken back"; retries of requests "the API marked not to retry" stopped; a finished sub-agent skill "running a second time when a cloud or background session restarts" fixed. 2.1.312 (27 Oct): "Changed Claude Code to stop sending the claude_code.safety_event OpenTelemetry event". 2.1.314 (30 Oct): permissions.blockWritesOutsideWorkingDirectories, "Write, Edit and NotebookEdit refuse paths outside the working directories in every permission mode"; guardrail_trace logs which Bedrock guardrail fired "without the matched text"; blocked shell and MCP calls no longer read as if they ran. SDK 0.3.312 adds an unanswered annotation (skipped, replied_in_chat, dismissed) to AskUserQuestion answers.

**What changed.** The event Issue 08 told you to subscribe to lasted three weeks. The transcript a session saved could be in a different order from the one the model saw, and a question a person never answered now says so instead of reading as silence.

**What to change.** Move any alert that keyed on safety_event to hooks or to the gateway's guardrail_trace, re-export SDK transcripts saved before 2.1.311 that an audit relies on, and record the unanswered annotation beside every clinical question an agent asked.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-09/details.html)

> **Architect signal.** Each project moved a fact about an action from one carrier to another this week, a field, a state, a different span. An audit that reads one carrier reads a record that is complete until the next minor release.

## A Callback That No Longer Runs, a Stale Session That Is Refused, a Token for the Wrong Server

Three SDKs changed what a caller is shown, or allowed to do, when the state in hand is not the state on the server. Read from changelogs, wheel diffs and advisories.

### The Responses tool runner dispatched a call whose namespace did not match the tool it was registered under

*Openai Python 3.38.0 To 3.41.0* · docs

3.38.0 (26 Oct), #4167 "validate tool namespaces before runner dispatch" and #4166 "resolve function arguments within their namespace". In the wheel, _Run.validate now raises "Function namespace does not match its registration." and "Typed function arguments were not parsed."; get_input_tool_by_name takes a namespace and returns None instead of falling back to a same-named top-level tool. The PR text: "Rejected calls must invoke no callback and submit no tool result." The same release adds client.beta.agents.automations, scheduled runs that target a new or existing session, and a PromptCacheBreakpoint ttl of 30m or 12h; 3.41.0 (28 Oct) filters agent sessions by metadata and adds tool usage models to Response.

**What changed.** A call could reach the callback of a tool other than the one the model named, with arguments parsed against the wrong schema, and the runner would submit the result as if it were the right one. It now stops before the callback.

**What to change.** Pin 3.38.0 or later wherever two tools share a name across namespaces; before upgrading, grep run logs for function_call items whose namespace differs from the registered tool. Treat an automation as a new principal in the approval model.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-09/details.html)

### appendEvent on a stale session throws instead of quietly reloading, and duplicate approval ids are rejected in .NET

*Google Adk Js 2.4.0 · Semantic Kernel .Net And Agent Framework .Net* · docs

ADK JS 2.4.0 (28 Oct), #1182: "reject a stale session in appendEvent instead of reloading it". DatabaseSessionService used to persist the event and silently reload stored state, so a stale handle could overwrite state or commit events out of order; it now throws StaleSessionError inside the transaction before any delta or event is written, with a deprecated staleSession: 'reload' to restore the old path. #956 reports tool error types on spans. Agent Framework .NET 1.26.0 (23 Oct, missed last week): ".NET: Reject duplicate tool approval request IDs (#9542)" and "reset compiled workflow state between runs (#9540)". Agent Framework Python and ADK Python had no release in window.

**What changed.** A session that fell behind the store was corrected by the store without telling the caller; now the caller is told and nothing is written. A second approval carrying an already-used id is refused.

**What to change.** Catch StaleSessionError at every append into a patient session and re-read before retrying; do not set staleSession to reload in production; on .NET, make the approval id a database key, not a correlation hint.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-09/details.html)

### A bearer token issued for a different resource server was accepted, and a store path reached other namespaces

*Mcp Python Sdk · Langgraph · Fastmcp, Five Advisories Published 23 To 28 October* · docs

mcp python-sdk, three advisories dated 27 Oct, fixed in 2.2.0 and 1.30.0: GHSA-w4fh-qvv9-3v23 "Server bearer-token authentication accepts tokens issued for a different resource server" when the token_verifier does not check aud; GHSA-5h93-6whr-6q8j, client transports followed cross-origin redirects carrying custom headers and bodies; GHSA-rwrf-2pqf-9j8j, the client fetched server-chosen $ref URLs while validating tool results. LangGraph: GHSA-3fx2-cqw9-xr3c (28 Oct), unencoded identifiers in SDK v3 streaming redirected authenticated GETs; GHSA-6hmw-9432-67qq (23 Oct), namespace labels containing "." reached other namespaces in the Postgres and SQLite stores, with checkpoint 4.3.1 (26 Oct) also rejecting NUL bytes. fastmcp 4.1.4 (26 Oct) escapes server text in the elicitation prompt and ties each client context to its own session.

**What changed.** An MCP server protecting a FHIR tool could accept a token minted for another service, and an approval store keyed by namespace could be read across a boundary with a dot in a label.

**What to change.** Verify aud on every MCP bearer token yourself and pin mcp 2.2.0 or later; upgrade the LangGraph stores and search labels for "." and control characters; pin fastmcp 4.1.4.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-09/details.html)

> **Architect signal.** Three of the five advisories are about a party being accepted as someone it is not, a token, a label, a namespace. The gate checked the request; it did not check who was asking.

## An Index Rebased to Private Data, a Price Halved, and a New Leader With No Price Page

4,000 input and 500 output tokens per document, list prices read 30 October. Artificial Analysis moved to Intelligence Index v5.0 on 27 October, so no score in this table compares with last week's.

### Nine evaluations, four of them private, and every tracked model's score changed without a model changing

*Artificial Analysis · Intelligence Index V5.0, 27 October*

The methodology page now reads "Artificial Analysis Intelligence Index v5.0 incorporates 9 evaluations" weighted across Knowledge Work, Coding, Science and General at 25% each, adding FrontierCode 2.0 and Terminal-Bench-Science and removing GDPval-AA v2, SciCode and AA-LCR; the announcement says "the majority of the Index is now built on private datasets". Readable v5.0 scores: Gemini 4 Carbon 59, Opus 5.5 58, GPT-6 Astra 57, GPT-6.1 Sol 55, Sonnet 5.5 54, Terra 51, Fable 5.1 50, Argon 50, Kimi K3.1 Pro 46 (55 on v4.3.2), Haiku 5.5 36, Grok 4.7 35, DeepSeek V4.1 Flash 32, Gemini 3.8 Flash 31, Luna 28 (38 on v4.3.2), Mistral Large 4 25. The Healthcare & Medical comparison reads Opus 5.5 58, Sonnet 5.5 54, Astra 54, Sol 52, Kimi K3.1 Pro 52, Fable 5.1 51; the page that states its composition returned an error on every read. HealthBench Professional is reported separately: Astra 66.0%, Sol 65.1%, Sonnet 5.5 63.0%.

**What changed.** The series' independent general score is a new instrument, and the medical score has a number again but still no readable composition. A validation file that cites "AA 56" now has to say which version.

**What to change.** Write the index version beside every score you file, keep v4.3.2 and v5.0 columns apart, and treat the medical figure as unversioned until its composition page renders.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-09/details.html)

### The only list price that moved fell by half, a new mid-tier model costs $65 on the workload, and the new leader has no vendor price

*Mistral Large 4, 29 Oct · Gpt-6.1 Terra, 26 Oct · Gemini 4 Carbon, 28 Oct*

Mistral Large 4 is 0.70 / 2.10 / 0.07 on the model page against 1.36 / 4.18 / 0.14 last week, $38.50 for the workload, and its weights were released on 29 October under the "Mistral Ecosystem Open-Weight license", a modified MIT that requires a commercial licence for model-as-a-service providers. GPT-6.1 Terra arrived on 26 October at 1.00 / 5.00 / 0.05, $65.00, Fast tier double. Gemini 4 Carbon (28 Oct) is first on v5.0 at 59 and absent from the Gemini API pricing page on 30 October; Artificial Analysis prints 4 / 20, a Reuters report says 2 / 10, access is phased through a programme for cybersecurity defenders, so the row is unverified. Both Kimi rows are now read from the vendor page (its tables render only through its script); K2 models close to new users on 31 October. Gemini 4 Argon doubles on 1 December and 3.8 Flash on 1 January, as printed.

**What changed.** The $130 price point now has four models within five index points, with a 1.00 / 5.00 model eight points below them, and the open-weight option at the bottom of the table halved its price in the week it published its weights.

**What to change.** Re-run any cost model built on last week's Mistral price; keep Carbon out of a validation file until Google prints a price; and record the licence class, not just the word open, for Mistral Large 4.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-09/details.html)

> **Architect signal.** Two of the three numbers an architect would copy into a validation file this week, a score and a price, changed for reasons unrelated to the model being validated. A table cell without a date and a method is a rumour.

## A Third of Tool Results Cut Mid-Object, One in Eight Successful Runs Writing Where It Should Not, and a Vancomycin Agent Run for Two Months

A harness that truncated the evidence, a benchmark that scores the writes a task did not ask for, and a silent deployment that found the stricter pipeline less safe. Numbers are the authors' own, from the abstracts.

### A third of tool results were cut before they reached the model, every cut result became broken JSON, and the largest prompt used 5.75% of the window

*Information Attrition · 2610.36114*

Measured in a fault-diagnosis agent over 720 runs: "a third of all tool results (3,827 of 11,189) were cut before they reached the model, and every cut result became broken JSON", while "the single largest prompt used only 5.75%" of the context window. Fixed-length slicing deleted end-of-record fields: "One field reached the model in only 4.7% of calls. A second field, in the very same results, reached the model in 99.3%." The cut showed first as work, "43% more tool calls, twice the computation, and yield falling from 0.61 to 0.31"; one production trace "deletes all 128 records of the fault's evidence". A survey of seven frameworks "finds two that cut tool output the same unsafe way".

**What changed.** The context window was not the constraint; a string slice in the harness was, and it removed exactly the fields at the end of each record, which in a FHIR bundle are the ones added last.

**What to change.** Find every place your harness truncates a tool result by characters and replace it with structure-aware paging per resource; log the count of cut results per run, because the model cannot report what it never saw.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-09/details.html)

### Among runs that satisfied their goal, 12.8% also produced unauthorized writes; collateral damage varied 4.7 times across models at the same success rate

*Side-Effect-Aware Evaluation, Sabench · 2610.34167*

201 email, calendar and ticket tasks with "a deterministic trace-based oracle for both goal satisfaction and authorization compliance". "Across 2,211 model-task pairs from 11 frontier LLMs ... 15.2% of all runs incur CD, with risk concentrated in ambiguity tasks (38.8% violation rate) while non-ambiguous traps average 8.4%." "Among goal-satisfied runs, 12.8% still produce unauthorized writes." Cross-tool and dependent states carry about twice the rate of independent ones, and "CD rates vary by 4.7x across models at comparable goal rates".

**What changed.** A task-success metric certifies one in eight runs that also wrote somewhere the task did not authorize, and the models that pass the task equally do not write equally.

**What to change.** Add an authorization oracle to every agent evaluation, a trace check that each write falls inside the scope the task granted, and report it beside the pass rate when you select a model.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-09/details.html)

### In a two-month silent deployment, the higher-autonomy dosing agent was within 25% of the pharmacist's order in 73.4% of events against 50.9% for the stricter pipeline

*Pharmaagent, Stanford · Medrxiv 2026.10.23.26365968*

"Across 403 dosing events in 316 patients, mean absolute percentage error against the treating pharmacist's order was 21.8% with high autonomy versus 37.8% with low autonomy, and recommendations were within 25% of the order in 73.4% versus 50.9% of events (P < 0.001); a second pharmacist was within 25% in 90.2%." Review of 196 out-of-tolerance recommendations "found a safety concern in 65.8%, more often with low autonomy (odds ratio 2.37)". The authors' reading: an agent "that self-debugged its intermediate steps proved more robust than stricter engineering, but neither configuration is ready to dose patients without pharmacist oversight".

**What changed.** The engineering instinct this series shares, constrain the agent's steps, produced the less accurate and less safe dosing in a real hospital, while the gate on the pharmacist stayed necessary in both arms.

**What to change.** Let the agent inspect and retry its intermediate tool steps, and spend the rigidity on the boundary instead, a tolerance check and a pharmacist approval that no configuration bypasses.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-09/details.html)

> **Architect signal.** Three papers measured what a success metric hides, a cut record, an extra write, a brittle pipeline. In each case the number that mattered came from a trace, not from the answer.

## Mechanism of the week: The order the framework's log stopped describing, and the checkpoint the caller was never shown

*Semantic Kernel 1.46.0 · Scripted Chat Client, 1.45.0 Against 1.46.0, No Model Key*

A clinician-assistant agent asks a scripted model to start apixaban for pt-123; the model calls pharmacy.place_order and Semantic Kernel's auto-invocation loop runs it, with an audit sink on the framework's own loggers. On 1.45.0 the kernel logged the full argument JSON and the function logger logged the arguments, the result and, on refusal, the exception text. On 1.46.0 the same lines carry the function name, "arguments provided: 5", "result available" and "Error type: ValueError". In every run the model was handed the result or refusal reason and the record held the same rows. Second check: a LangGraph run paused by interrupt_after never streamed the checkpoint it stopped on, so a client resuming from its last one re-drafted the order; 1.2.18 streams it.

**3 → 0** log lines carrying the patient id for one order, 1.45.0 against 1.46.0 · **2 → 0** log lines carrying why the order was refused, while the model was told in both · **2 → 3** checkpoints streamed before the pause, langgraph 1.2.17 against 1.2.18

**What changed.** In kernel.py, invoke_function_call logs "Calling %s function." instead of the arguments, and the except branch logs type(exc).__name__ instead of logger.exception with the message; kernel_function_log_messages.py logs len(arguments), "Function result available." and the error type. The OpenTelemetry span still carries arguments and result when SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE is set; that channel is unchanged. In LangGraph, the task-preparation and checkpoint-emit block of tick() became _prepare_tasks_and_emit_checkpoint() and is now called on the interrupt_after and recursion-limit exits.

**Move.** If any part of your audit trail is the framework's log, it lost the order and the refusal reason on 28 October; write the ledger from an auto-function-invocation filter into a store you own, and route the sensitive OpenTelemetry attributes to a restricted exporter rather than the application log. On LangGraph, resume from graph.get_state, never from the last streamed checkpoint, until 1.2.18 is everywhere, and count drafts per thread in your tests.

[Open the lab package](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-09/lab)

> **Architect signal.** Both changes are improvements, and both removed something a record somewhere depended on. A fact that reaches the audit only because a framework happened to print it was never in the record; it was in the output.

## What the architects shipped

- **Anthropic.** Platform release notes: a Usage and Cost Analytics API in beta on 29 October (header analytics-usage-cost-2026-08-24, endpoints /v1/organizations/analytics/usage and /cost, grouped by model, workspace, key and user), with the older usage and cost endpoints now legacy; the Messages and Token Counting request limit raised from 32 MB to 128 MB on 28 October. A 27 October research post on drug development names six developers and reports Enveda's manufacturing-document review catching "all 11 issues humans found plus 7 they missed" across 1,061 pages*. Claude Agent SDK 0.2.175 (30 Oct) bundles CLI 2.1.314, slide 04. An S-1 was filed on 26 October.
- **Openai.** GPT-6.1 Terra on 26 October, slide 06; openai-python 3.38.0 to 3.41.0, slide 05, with scheduled agent automations and a 12-hour cache breakpoint arriving through the SDK with no API changelog entry; the API changelog itself carries only Terra and up to $500 a month of API credit for ChatGPT Pro and Business subscribers (28 Oct). Two 29 October posts, an updated Model Spec and "How we detect frontier model misalignment", describe the vendor's own monitoring of agents acting without authorization; not read as engineering guidance. openai-agents Python and JS had no release.
- **Google.** Gemini 4 Carbon announced 28 October with phased access and no price page, slide 06. ADK JS 2.4.0 (28 Oct), slide 05. ADK Python stayed at 2.13.0; the ADK JS changelog is mostly parity ports from the Python 0.x line. The Gemini API pricing page prints the 1 December and 1 January increases unchanged.
- **Microsoft And Mistral.** Semantic Kernel Python 1.46.0 (28 Oct) is on slide 08; also in it, "preserve empty tool results in chat history" (#14472), a runtime that no longer hangs when an intervention handler drops a message (#14656), and five path and DNS hardening fixes in the sessions and HTTP plugins. Agent Framework Python had no release; .NET 1.26.0 is on slide 05. Mistral Large 4 weights on 29 October with transformers 5.22.0 the same day adding the architecture, per-request reasoning effort and native strict-JSON function calling.
- **Anaconda · Nebius · Nvidia · Moonshot.** Anaconda joined the Open Secure AI Alliance (28 Oct), committing to test agents' multi-step decisions and "converting AI policies into verifiable records", and published an LLMOps guide (27 Oct) that argues evaluation "has to score the path an agent took as well as its final answer". Nebius (26 Oct) benchmarked replica against tensor-parallel serving for world models; nothing on agents. NVIDIA published Nemotron 3.5 Transcribe 30B-A4B on 28 October, a 40-language speech model whose card names synthetic text over "more than 55 PII/PHI categories" in training, the only PHI reference in the window. Moonshot's K3.1 Pro blog (24 Oct) reports a claim-level hallucination rate falling from 23.4% to 8.3% on its own bench*. Read from the public pages; the newsletter inbox was not readable this run, and Matt Pocock's sites carry no dated post in window.
- **Epic And Hl7.** No new open.epic item after 21 October; the Open@Epic site restates a public MCP server for documents and API specifications, with Connectors delivered through Showroom "starting in March 2027" and FHIR admission and discharge notifications in the November release. HL7 published the FHIR Extensions Registry 5.4.0 and an R6-based Orders and Observations incubator snapshot on 28 October and tx-ecosystem 1.10.0 on 25 October. The Da Vinci roundtable with CMS staff happened on 28 October as scheduled; no recording or recap was posted by 30 October.

Nothing in window from the MCP specification (draft changelog still empty, revision 2026-07-28) or Python SDK beyond slide 05's advisories, Agent Framework Python, ADK Python, openai-agents, LlamaIndex, smolagents, NeMo Agent Toolkit, ARPA-H news, CMS on prior authorization, or FDA press releases.

> **Architect signal.** Four vendors shipped a way to see what an agent cost, used or logged this week, an analytics API, a usage model, a guardrail trace, a label. Each is read-side; none adds a field the acting side must fill before it acts.

## A Final Rule That Removes the Model Card, a Payer Pilot Whose Own Records Show Four Vendors Under Correction, and Three De Novo Orders for Software

### Source-attribute and risk-management requirements for predictive decision support are gone from certification, and MCP is named in the rule text

*Hhs Astp/Onc · Hti-5 Final Rule, Released 26 October, Published 28 October, Effective 28 December*

91 FR 67916, FR Doc 2026-21943: "This final rule is effective on December 28, 2026, except for amendatory instructions 7, 10, and 12 which are effective January 1, 2027." Of 60 certification criteria, 14 are removed and 7 revised. § 170.315(b)(11) Decision Support Interventions loses (b)(11)(iv) source-attribute support, (b)(11)(v) source-attribute access and modification, and (b)(11)(vi) intervention risk management for predictive DSIs; the assurances maintenance requirement at § 170.402(b)(4) goes with them. ONC writes that "A large majority of commenters were not supportive of our proposal" and that it has "identified no evidence through peer reviewed publication or trade press indicating that users of certified health IT have relied on the transparency requirements". The rule replaces "artificial intelligence" with "super intelligence (SI)" throughout, citing Executive Order 14434, and says the change "will allow more creative super intelligence (SI)-enabled interoperability solutions that combine FHIR with newer standards to emerge, such as Model Context Protocol (MCP)". Information-blocking proposals "remain under consideration". The (g)(7) and (g)(9) API criteria are removed on 1 January 2027, leaving (g)(10).

**Move.** The 31 attributes your vendor had to supply about a predictive DSI stop being a certification obligation on 28 December; make them a contract obligation before then, and keep the 45 CFR 92.210 nondiscrimination duty in view, which the rule leaves standing. If your agent integration leans on (g)(7) or (g)(9), move it to (g)(10) before 1 January.

### CMS sent corrective-action or information requests to at least four of six prior-authorization AI vendors in the pilot's first three months

*Cms Wiser, Records Released 27 October · Fda, 30 October · Hl7 And Arpa-H*

Over 800 pages obtained by the Electronic Frontier Foundation in its FOIA suit against CMS, published 27 October: requests for information or corrective action plans to at least four of the six WISeR vendors, citing "determination turnaround times that exceed established guidelines", "denials that appear inaccurate or inconsistent with applicable criteria" and a non-functional provider portal; one vendor cites "technical and workflow stabilization challenges ... due to the compressed implementation timeframe". The CMS FAQ in the records: "Non-affirmations will require the review of a human clinician and cannot be performed solely by technology." Secondhand figures (62% initial AI approval rate rising to 84% after human review) are not confirmed from the records themselves. FDA published three De Novo classification orders for software devices on 30 October, each effective that day, with special controls for a radiology referral tool, a skin-lesion adjunct and an over-the-counter sleep-apnoea risk device; no AI guidance, PCCP or advisory-committee notice appeared in the window. HL7 Extensions 5.4.0 is published without readable release notes. ARPA-H SURPASS, which calls for "an agentic operations layer", takes solution summaries until 30 November.

**Move.** If you build for a payer, the pilot's own record is now the reference for what "human clinician review" has to mean operationally: turnaround, letter timeliness, portal availability. Put the 30 October special controls on the reading list for any adjunct that returns a risk score, and the 30 November SURPASS date in the calendar.

Every dated source for this week is in the long-form edition. The cumulative Radar was not refreshed this week. [Open the Radar](https://zkumar.github.io/ai-velocity-weekly/index.html)

> **Architect signal.** One rule removes the fields that described a model, and one set of records shows a programme discovering, vendor by vendor, which fields it should have required. Between them is the architect's job this quarter.

---

Full mechanism, code and sources for every card are in the long-form edition. The architect's position on this week's decision is in My Take. The code runs from a clean virtual environment with no API key. Everything is at https://github.com/zkumar/ai-velocity-weekly .
