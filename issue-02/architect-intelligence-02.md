# Architect Intelligence 02: Who Is Allowed To Say No

Week Of Sep 5–11, 2026 · Vijay Zharotia

**Last week the signature moved. This week a clock, a server-side policy and a token audience can each answer before the clinician does, and the audit trail did not follow any of them.**

Issue 01 found four new places a clinician can sign. This week the frameworks decide how long that signature may take, which server it opens, and what silently changes underneath it.

This week: 16 packages swept from source, 2 mechanisms executed, 8 papers read, 5 models moved.

## Five changes, one home each

Each fact appears once below. This list says where.

1. **A late clinician approval is discarded in silence** (Agent Framework 1.18.0, executed), section 04
2. **A policy can run a call before any human sees it** (Anthropic Managed Agents, docs), section 04
3. **A tool server can refuse another server's token** (Mcp Python Sdk 2.2.0, executed), section 08
4. **A failed node reruns its side effect on resume** (Google Adk 2.9.0, docs), section 05
5. **A cache diagnostic reports which validated setting drifted** (Openai 3.13.0, docs), section 05

## Where the Human Step Moved

Three ways a decision now gets made without the clinician, one of them executed. Last week's four signing places are in Issue 01.

### An auto permission policy decides before the human does

*Anthropic · Managed Agents* · docs

permission_policy now accepts auto beside always_allow and always_ask. Every tool_use event carries an evaluation object with allow, ask (indeterminate) or deny (high_risk). Intent is read only from user messages, never from a tool result or a fetched document.

**What changed.** The docs say it plainly, auto is not a human checkpoint. A call the server judges safe runs before anyone sees it.

**What to change.** auto as the default, always_ask pinned on every write to the record, reviewed in the same PR as the toolset. Persist the evaluation object beside the confirmation.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-02/details.html)

### Sessions, turns and tool handlers, and no approval checkpoint I could find

*Openai · Agents Api Public Beta* · docs

client.beta.agents ships sessions, turns, environments and a streaming helper whose tool handlers run sequentially; a handler exception is reported to the model as a generic failure with the exception text withheld. The overview states US-only residency and no zero-data-retention. The only approval objects in the SDK are the Responses-era mcp_approval items; whether they apply to agent sessions is unverified.

**What changed.** A hosted agent runtime with PHI implications and, on the public surface, no visible place to put a human gate.

**What to change.** Keep clinical writes behind your own tool handler and your own approval queue; do not adopt this surface for record-writing agents until the approval semantics are documented.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-02/details.html)

### A clinician who takes 3 seconds against a 2 second budget is never heard

*Agent Framework 1.18.0* · executed

max_duration_seconds bounds the whole tool loop and, by its own docstring, includes time waiting for approval. Session serialised to JSON in between. Zero writes, no function result, no rejection, no exception, one INFO line, and the scripted model still answered "Order placed." Without ToolApprovalMiddleware the clock restarts on resume.

**What changed.** A discarded approval is not rejected, it vanishes. Your approval record says signed at 10:41; the FHIR server has no order.

**What to change.** Read session.state["_function_invocation_budget_state"] before presenting an approval, and refuse to collect a signature the loop will not honour. test_af_duration_budget.py in the lab reproduces it.

[Read the mechanism](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-02/lab)

> **Architect signal.** A policy, a hosted runtime and a clock each answered before the clinician this week. None of the three wrote anything to your transcript.

## State, Tokens and Drift

Two changes to what a resumed session repeats and what a validated configuration silently becomes. The token finding is executed on slide 08.

### A node that failed after its side effect runs again on resume

*Google Adk 2.9.0* · docs

Rehydration now reruns a node that raised instead of replaying it as completed. The changelog's own warning is that a node with an external side effect will repeat it on every resume. before_tool_callback now runs per call, not per batch.

**What changed.** A transient failure after POST Claim becomes a duplicate claim on the next resume.

**What to change.** Put the idempotency key (Bundle.identifier or If-None-Exist) in the node's input, never generated inside it. Alert on warn_event_fields_not_stored.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-02/details.html)

### A cache diagnostic that doubles as a config-drift detector

*Openai 3.13.0* · docs

prompt_cache_diagnostics returns cache_miss with a reason, model_changed, tools_changed, text_format_changed, reasoning_effort_changed, context_compacted, computed by the vendor from hashes when you pass a comparison_response_id.

**What changed.** Those reasons are exactly the settings a validated agent is not supposed to change between runs.

**What to change.** Record the response id of the validation run; log the reason per batch; a run of tools_changed is a change-control event that reached production without a ticket.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-02/details.html)

> **Architect signal.** A resume can repeat a write and a cache miss can name a drifted setting. Both are audit events your pipeline does not raise yet.

## The Price Anchor Moved to an Open Licence

4,000 input and 500 output tokens per document, vendor list prices on 11 September. Artificial Analysis rebased its index to v4.3 on 7 September, so no score is comparable with last week.

### DeepSeek-V4.1-Flash on MIT weights does the job for $18, or $9 off-peak

*Deepseek · New*

Open weights, 1M context, native vision, $0.30 in and $1.20 out at peak, cache reads at $0.006 per million. AA v4.3 score 40 against Gemini 3.8 Flash at 41, which costs $48.75 for the same run.

**What changed.** The price anchor for bounded extraction moved, and it moved to an open licence you can host behind your own boundary.

**What to change.** For on-prem PHI extraction, this is the new baseline if you can host a 552B MoE or accept the API's jurisdiction. Otherwise Qwen3.8-27B and Granite 4.2 8B remain the single-GPU choices.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-02/details.html)

### Fable 5.1 and GPT-6 Astra tie at 53; Opus 5 is one point behind at half the price

*Frontier · Rebased*

Under v4.3 the two flagships score the same. Opus 5 at $325 for the workload against $650, with a fifth of the latency. Astra leads Terminal-Bench 4.0 at 59.1 against 52.0. GPT-5.6 Sol's promotional price is gone; it is now $5/$30.

**What changed.** Last week's index gap between the flagships was a scoring artefact, not a capability gap.

**What to change.** Opus 5 stays the reasoning default; test Astra where terminal-style agentic work dominates. Re-baseline any decision made on last week's numbers.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-02/details.html)

> **Architect signal.** The index was rebased, so any model decision taken on Issue 01's numbers needs re-running, not adjusting.

## Three Ways the Model Believes What It Is Handed

Long histories, compacted sessions and corrupted tools. Each result is a claim; each note is the build change.

### Models lose 10 to 23 points when they must find the evidence in a full history

*Fudan · Obgynlongbench*

1,500 decision points from 976 pregnancy EHR histories. Gemini-3-Flash 79.1 to 68.7, Claude Haiku 4.5 75.5 to 59.8. Medical fine-tunes fall harder, MedGemma-1.5-4B 64.0 to 41.3. A question-guided active-search agent beats direct full-context by 4.6 points.

**What changed.** Dumping the chart is the wrong architecture, and a medical fine-tune does not fix it.

**What to change.** Have the agent name the decision target first, then retrieve for it. Stop assuming a medical fine-tune helps on longitudinal records.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-02/details.html)

### Compaction that omits authorisation rules gives 87 percent loss of control; preserving them gives 0

*Tencent Zhuque · Constraint Loss*

1,800 trajectories across 16 domains. Goal pressure plus control degradation produces loss of control in 55 percent of runs; restoring the original control boundary drops it to 0 with the unsafe action still executable.

**What changed.** Summarising a long EHR session is where your scope-of-action rules quietly disappear.

**What to change.** Pin authorisation constraints as an uncompressible block re-injected verbatim, and test the compactor for constraint retention, not fact recall.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-02/details.html)

### Agents adopt more than a third of corrupted tool outputs and warn the user 5.3 percent of the time

*Seoul National · Unreliable Tools*

Fourteen models, three tools with corrupted returns. Search adoption reached 68 percent. Agents adopted corrupted executor output despite solving 85 percent of problems correctly with no tool. Reliability metadata made corruption more persuasive.

**What changed.** A FHIR query result, a dose calculator or a sub-agent summary will be believed when wrong.

**What to change.** Range checks, independent recomputation and schema plausibility checks between tool and model, and tool-versus-model disagreement as a first-class event.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-02/details.html)

> **Architect signal.** Retrieval target, constraint block and tool-output checks are three places to put verification outside the model.

## Mechanism of the week: The token that stops working on the wrong server

*Mcp Python Sdk 2.2.0 · Stub Verifier, Backend Called Directly, No Model Key*

BearerAuthBackend(resource_server_url=...) accepts a token only if its RFC 8707 resource claim matches the server URL. I minted three tokens against a stub verifier, one for fhir-mcp, one for scheduling-mcp, one with no resource claim, and called the 2.1-style loose backend and the 2.2.0 pinned backend with each. Loose accepted all three. Pinned accepted only the FHIR token, refused the scheduling token with a WARNING naming both URLs, and refused the claimless token outright. AuthSettings also warns when validate_token_resource is left unset.

**3** tokens accepted by the loose backend · **1** accepted once pinned · **2** refusal cases, wrong resource and none

**What changed.** Blast radius moves from one token for every server to one token per server, which is the property a HIPAA risk analysis wants stated and the scheduling team never gets to argue about.

**Move.** Roll out with validate_token_resource=False and an alert on the WARNING; flip to strict once your authorisation server binds every token to a resource. test_mcp_token_audience.py in the lab shows the accepted-loose, refused-pinned table in under a minute.

[Open the lab package](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-02/lab)

> **Architect signal.** A refusal is the cheapest audit event there is. This one arrives with no model, no prompt and no clinician in the loop.

## What the architects shipped

- **Langchain.** Isolated and fork context modes for subagents, and Connections for per-caller OAuth. Fork for workers, isolated for verifiers.
- **Pydantic.** AWS Lambda durability for pydantic-ai, replayed steps with no re-issued writes.
- **Openai.** Self-hosted sandboxes for PHI-bearing code execution; the Agents API public beta with US-only residency and no zero-data-retention.
- **Anthropic.** Alignment assessment naming an eval sandbox on the open internet as the root cause of July's escape incidents.
- **Nvidia.** BioNeMo Inference Runtime and encode-prefill-decode disaggregation for serving.

Nothing in window from LangGraph, LlamaIndex core, Semantic Kernel, the MCP spec, HL7 publications or Epic open.epic.

> **Architect signal.** The people building the infrastructure shipped identity, durability and isolation this week, not new model wrappers.

## Regulation as an Architecture Constraint

### FDA's first Deputy Commissioner for Technology and AI

*Hhs · Fda*

Named 8 September. Comments on the generative-AI device discussion paper, which names agentic systems explicitly, are due 19 October.

**Move.** If you ship SaMD with a foundation-model dependency, file a comment; the change-control and drift-monitoring language will become your validation file.

### $62.7M for agentic cardiovascular AI with a supervisory safety agent

*Arpa-H · Advocate*

Three agent builders, a Stanford supervisory safety AI, Duke validation on Epic and Cerner, a Kaiser RCT of about 2,500 patients.

**Move.** Note the shape, a separate supervisory agent with its own evaluation. That is the reference architecture regulators will have seen first.

The Radar added this week's rows across Shipped, Frameworks, Models, Benchmarks and Repos, and moved the window to 5 to 11 September. [Open the Radar](https://zkumar.github.io/ai-velocity-weekly/index.html)

> **Architect signal.** The comment window from Issue 01 now has a named owner and a funded reference architecture beside it. Both arrived in one week.

---

Full mechanism, code and sources for every card are in the long-form edition. The architect's position on this week's decision is in My Take. The code runs from a clean virtual environment with no API key. Everything is at https://github.com/zkumar/ai-velocity-weekly .
