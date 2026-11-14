# Architect Intelligence 11: The Question That Left The Run

Week Of Nov 7–13, 2026 · Vijay Zharotia

**Last week the gate had edges: a tool the policy never named ran without a question, and a failing guard counted as no opinion. This week the question moved: pydantic-ai hands an approval out of the run on a token and takes back a name it does not verify, after a release in which a gated external call left with no gate at all; LangGraph lets a parent read a child it never declared; and three runtimes now stop at start-up instead of running with their rules dropped.**

Issue 10 found the edges of the approval gate: a tool on no list, a guard that crashed. This week the frameworks moved the question itself: out of the run on a resume token and back with a name nobody checks, into a parent that can finally read its child's record, and in three runtimes to a start-up that stops rather than start without its rules.

This week: 34 wheels unpacked and diffed, 12 runs of the executed mechanism, 93 abstracts read, 19 models priced.

## Five changes, one home each

Each fact appears once below. This list says where.

1. **An approval raised for an external tool was handed to the outside executor as a plain call, with no approval and no metadata; the run now refuses, and the next release answers inside the run** (Pydantic-Ai 2.66.0 → 2.67.0 → 2.68.0, executed), section 08
2. **A parent graph can read the checkpoint history of a child it never declared, with the parent's channels and no write access** (Langgraph 1.2.20 → 1.2.21 · Deepagents 0.7.36, executed), section 08
3. **A settings file that will not load now stops the SDK, where one release back it launched with the caller's permission rules and hooks dropped** (Claude Agent Sdk 0.2.181 · Claude Code 2.1.319 To 2.1.323, docs), section 04
4. **Approvals are bound to the stored call, the live control and the pending session snapshot, and fail closed when the service-held history is unavailable** (Agent Framework 1.25.0 And 1.26.0, docs), section 04
5. **Agentic tools in EHRs are named in a published Medicare rule as a security concern to be continuously monitored, and FDA opens a docket on devices that act before a person can interrupt** (91 Fr 70992 · Fda-2026-N-13135, docs), section 10

## A Policy That Can Be a Function, a Settings File That Stops the Launch, and an Approval Bound to the Call That Was Stored

Three projects changed who or what may answer an approval and what happens when the rules are missing. Read from changelogs, pull requests and wheel diffs; the external-tool approval is executed on slide 08.

### The approval policy for discovered MCP tools can now be a callable that runs on every refresh, and 1.26.0 binds an approval to the stored call it answers

*Agent Framework Python 1.25.0 And 1.26.0 · .Net 1.28.0* · docs

1.25.0 (7 Nov), #10136: approval_mode accepts a callable "receiving the discovered mcp.types.Tool or mcp.types.Prompt and returning always_require or never_require, including its default decision. It runs once per item on each discovery refresh, including retained functions"; the "default" key of 1.24.0 is unchanged and hosted MCP tools still do not read it. #8662, declarative 1.5.0, a security fix: a fresh MCP protocol session per handler call, so "Implicit server-session continuity no longer survives later calls, approval waits, or checkpoint resumes." #9875: "Fail closed on invalid FIDES tool policy". 1.26.0 (12 Nov), #9876 to #9878: "bind approvals to canonical stored calls, exact live controls, and pending session snapshots" and "fail closed when service-owned history is unavailable"; #10226 isolates run-level approval state when an agent is exposed as a tool; #9944 normalises naive checkpoint timestamps to UTC before choosing the latest.

**What changed.** A discovery policy can finally say deny for anything new, including tools kept from an earlier refresh; an approval no longer matches a call by position but by the stored record of it; and an MCP server's session state stops surviving an approval wait.

**What to change.** Replace list policies with a callable whose fallthrough is always_require, re-test workflows that relied on server-side MCP state across a pause, and treat 1.26.0's fail-closed path as an outcome to log, since a missing service history now stops the action.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-11/details.html)

### A settings file that cannot be loaded now raises before launch, and a permission check that errors after a hook said allow is decided as if no hook had answered

*Claude Agent Sdk 0.2.179 To 0.2.181 · Claude Code 2.1.319 To 2.1.323* · docs

claude-agent-sdk 0.2.181 (12 Nov), subprocess_cli.py: "Settings that can't be loaded raise: launching without them would drop the caller's permission rules and hooks"; 0.2.178 logged a warning and launched with only the sandbox block. Claude Code 2.1.323 (12 Nov): "Fixed claude -p and the Agent SDK running Bash unsandboxed when --settings or SDK settings that turn the sandbox on fail validation"; "Changed what happens when a tool's permission check fails with an error after a PreToolUse hook returned "allow": Claude Code now decides the call as if no hook had answered"; auto mode that is unavailable "now starts in Manual mode, which asks first". 2.1.319 (6 Nov): permissions.denyInsteadOfPrompting, "a tool call that would wait on a permission prompt is denied and the turn continues"; a Bash permission bypass "where a crafted environment prefix could hide part of a command"; a sandbox escape when creating a worktree. 2.1.321: a PreToolUse ask "being lost when another hook's defer finished first". Python changelog on main still ends at 0.2.178; the 0.2.181 lines are from the wheel.

**What changed.** Missing rules used to mean fewer rules and a successful launch; now they mean no launch. A hook's allow no longer survives an error in the check behind it, and an unattended session can be told to deny rather than wait.

**What to change.** Upgrade to 0.2.181 and make the settings path a start-up assertion in your own code too; set denyInsteadOfPrompting in headless runs and count the denials; re-read any PreToolUse allow that assumed the built-in check could not fail.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-11/details.html)

### A client that cancels mid-run now gets every dangling tool call, including a pending confirmation, sealed as aborted in the session, and a JS confirmation no longer drops its sibling results

*Google Adk Python 2.14.0 And 2.14.1 · Adk Js 2.5.0* · docs

google-adk 2.14.0 (7 Nov, changelog dated 4 Nov): a new _run_invocation_lifecycle marks an external CancelledError as aborted, so open FunctionCalls, adk_request_confirmation among them, receive a response with error_code INVOCATION_ABORTED, "Invocation was aborted by client."; 2.13.0 sealed only when the runner itself had aborted. ToolConfirmation.from_response_dict accepts a pre-parsed dict (#7681); a callable require_confirmation now receives raw enum values. VertexAiSessionService.create_session rejects unknown keys with a 400; Firestore writes a payload format 2.13.0 cannot read back. RunSkillScriptTool drops its free-form command, which "closes a hole that let a prompt-injected model run arbitrary shell commands". 2.14.1 (12 Nov) only turns off FastAPI's native tracing on Agent Engine, where a sampled-out parent trace would drop every span. @google/adk 2.5.0 (12 Nov), #1244: "keep parallel tool responses when another call asks for confirmation"; #1137: plugin before and after agent callbacks were never invoked.

**What changed.** An abandoned confirmation request is now a closed record with a reason rather than an open call nobody answers, and a JS run that paused for one confirmation stops losing the results that arrived beside it.

**What to change.** Treat INVOCATION_ABORTED as an audit event and reconcile it against your own pending-approval table; roll back from 2.14.0 only with a Firestore export in hand; re-run any ADK JS plugin test that passed by never running.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-11/details.html)

> **Architect signal.** Each change makes the runtime refuse something it used to accept quietly, a missing file, a stale history, a cancelled call. Count the refusals; a gate that never refuses is not being tested.

## A Child's Namespace on the Tool Message, a Compaction That Waits for the Approval, and a Session Store You Host Yourself

Three changes to what a run keeps about work done beside it. Read from changelogs, wheel and tarball diffs and vendor documentation; the parent's read of the child is executed on slide 08.

### The task tool now writes the sub-agent's checkpoint namespace onto its own message, and a new middleware blocks risky calls with an error instead of asking anyone

*Deepagents 0.7.35 To 0.7.37 · Langchain 1.5.0 · Langchain-Core 1.8.0* · docs

deepagents 0.7.36 (12 Nov), #7580: "Record the subagent's checkpoint namespace on the task tool message"; the task streams the child with checkpoints and sets ToolMessage.artifact["checkpoint_ns"] "so a client can load its history from it. The model never sees artifact." langchain 1.5.0 (11 Nov): AutoModeMiddleware, "Calls below 0.5 execute normally. Calls at or above it return an error ToolMessage without invoking the tool handler." and "This middleware blocks calls; it does not request human approval."; its traces omit inputs. 1.4.10: the summariser's own model call is tagged nostream, so its text no longer reaches a client reading stream_mode="messages". langchain-core 1.8.0 adds a decisions module and drops Python 3.10; 1.7.7 caps loads() at 200 levels. @langchain/langgraph 1.7.2, #3258: history now shows what an interrupted-then-resumed node returned.

**What changed.** A sub-agent's record has an address the parent keeps, a risk classifier can now veto a tool call with no person in the loop and no checkpoint of its reasoning, and a summary stops leaking into the client stream while still being traced.

**What to change.** Store checkpoint_ns from the task message beside the approval it belongs to; if you adopt AutoModeMiddleware, log the probability it saw, because the error message is the only record; re-check any client that counted summariser tokens.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-11/details.html)

### Automatic compaction now skips a history with an unanswered approval in it, and the vendor says it enforces auto review on every action of its own persistent agents

*Openai-Agents Js 0.22.0 · Openai Python 3.48.0 To 3.50.0 · Openai Engineering, 12 Nov* · docs

@openai/agents-core 0.22.0 (13 Nov 00:01 UTC), changeset 409df96: the Responses compaction session returns early with "skip: stored history has an incomplete approval group", using a new hasCompleteApprovalGroups(); c1764e7 resumes guarded terminal tool runs after a nested approval; a6cc47e puts offered tool definitions on generation spans only when sensitive-data capture is on, and "Hosted OpenAI trace exports omit them." openai 3.50.0 (12 Nov), #4268: Response.input_transformations lists reasoning items withheld from the model with a reason, organization_mismatch, end_user_mismatch, model_mismatch, prefix_mismatch or turn_boundary; 3.49.0, #4264: an async function tool where "the agent continues without waiting for the function result". The API changelog has no entry 6 to 13 November. An engineering post of 12 November on securing persistent agents: "we enforce auto review on all agent actions", with a credential broker and a per-agent service identity.

**What changed.** A summary can no longer bury a pending approval, a response now tells you which of your own reasoning items it refused to read back, and a tool can be declared fire-and-forget at the API.

**What to change.** Pin 0.22.0 before enabling automatic compaction; log input_transformations per call, since a withheld item changes what the model saw; keep async tools off anything that writes to a chart.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-11/details.html)

### Managed Agents can now run on your own servers with the session history in your database, and the new model enforces a prefix check for every account

*Anthropic, 9 And 12 Nov · Anthropic Sdk 2.7.0 And 2.8.0 · Fastmcp 4.1.7 And 4.1.8* · docs

Self-hosted Claude Managed Agents, 12 Nov: "You run the whole Managed Agents service, not only self-hosted sandboxes, on your own infrastructure, and you store agents, sessions, and session history there."; "The server keeps no log files and stores no traces or metrics."; "Anthropic has no remote access to the server or its log."; session, agent and environment ids still go to Anthropic as headers and "No setting turns them off."; still not ZDR; "each trust level needs its own deployment". Claude Fable 5.2 and Mythos 5.2, 9 Nov: "enforce the prefix check for every account" and require 30-day retention, "not available under zero data retention unless expressly authorized". anthropic 2.7.0 adds a sandbox_egress_restricted error on Admin API writes. fastmcp 4.1.7 and 4.1.8 (10 Nov): a per-transaction consent cookie so "a different browser cannot complete the OAuth flow", revocation ownership separated from user identity, and Authlib and joserfc floors raised past nine October advisories.

**What changed.** The custody question of Issue 09 has an answer you can deploy, with a database you own and a log you have to build; the newest model refuses an edited history outright; and an MCP OAuth proxy binds consent to the browser that gave it.

**What to change.** If you take self-hosting, write the audit log yourself from day one, because the server will not; test every history-editing path against 5.2 before switching model ids; upgrade fastmcp wherever a proxy fronts an EHR.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-11/details.html)

> **Architect signal.** Three vendors put the record where you can reach it this week, a namespace, a skipped compaction, a database of your own. Reaching it is now your job, and so is noticing when it is empty.

## A New First Place at a Lower Price, a Row That Halved on Paper, and a Catalogue That Closed

4,000 input and 500 output tokens per document, list prices read 13 November. Artificial Analysis is still at Intelligence Index v5.0.1; scores do not compare with Issues 01 to 08.

### Claude Fable 5.2 enters at 65 on both indexes, two points clear of the field, and Gemini 4 Hydrogen arrives at 54 with no medical score yet

*Artificial Analysis · Intelligence Index V5.0.1 · Healthcare & Medical Index, 13 November*

Changelog, 9 Nov: Claude Fable 5.2 Max 65, Xhigh 62, High 62, Medium 56, Low 54; Meta Muse Ember 36, "the cheapest model scoring 36". 12 Nov: Gemini 4 Hydrogen Xhigh 54, High 51, Medium 41, Low 27. No methodology entry; v5.0.1 stands. Readable scores: Fable 5.2 65, Carbon 60, Opus 5.5 59, Astra 57, Sonnet 5.5 55, Sol 55, Hydrogen 54, Terra 51, Argon 50, Fable 5.1 49 (deprecated on its page, down one by rounding), Kimi K3.1 Pro 46, Haiku 5.5 36, Grok 4.7 35, DeepSeek V4.1 Flash 33, Gemini 3.8 Flash 31, Luna 28, Mistral Large 4 26. Healthcare & Medical, now at a new URL: Fable 5.2 65, Opus 5.5 58, Carbon 57, Sonnet 5.5 54, Astra 54, Sol 52, Kimi K3.1 Pro 52, Argon 51, Fable 5.1 51. HealthBench Professional: Fable 5.2 67.7% (68.1% at xhigh), Astra 66.0%, Sol 65.1%.

**What changed.** The medical index has a new top and a new address; the previous top closed row is now deprecated by its own vendor; and a 1.50-per-million model scores within a point of the 2.00 tier.

**What to change.** Re-run any evaluation that selected a model by medical index rank, record the index URL with the score, and put Hydrogen into the shortlist for extraction work before its medical score exists, not after.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-11/details.html)

### Fable 5.2 costs 20% less than the model it replaces, Gemini 4 Carbon is now priced on a Google page at half last week's figure until 30 November, and one row went unverified because its catalogue returned 403

*19 Rows, Read 13 Nov · Google Price Page · Nebius Catalogue*

Claude Fable 5.2 at 8 / 40 / 0.20, $520.00 against $650.00 for Fable 5.1, which stays on the page under Additional models. Gemini 4 Carbon now reads 2 / 10 / 0.10 "through November 30, 2026" then 4 / 20 / 0.20, the same schedule as Argon, so the $260.00 recorded last week from Artificial Analysis was the post-promotion price. Gemini 4 Hydrogen, new, 1.50 / 7.50 / 0.075, $97.50, no scheduled change. Both Kimi rows verified this week from the price page's embedded script data, unchanged. OpenAI's page says Sol's promotional price runs "until November 30, 2026" with no successor figure printed. gpt-oss-120b on Nebius is unverified: the Token Factory catalogue returned 403 and the fallback page prints no cached price. Thinking Machines released Inkling 2 Small weights on 12 Nov under Apache 2.0, with a card that says to avoid medical decision-making; no vendor price.

**What changed.** The $130 tier now holds five models and the index leader sits at $520 instead of $650; two scheduled changes land on 30 November and 1 December, and the cheapest open row lost its source page.

**What to change.** Re-price the fixed workload on 1 December before any budget conversation; carry the Carbon row at both figures with the date; keep the Nebius row out of a validation file until its catalogue is readable again.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-11/details.html)

> **Architect signal.** Four rows moved this week without a single vendor raising a price, a launch, a page that finally printed, a promotion with a date, a catalogue that went dark. A price table is a set of sources with expiry dates, not a set of numbers.

## Permissions Alone Let One Episode in Five Through, Agents Stop Less Often When the Evidence Is Missing Than When It Says No, and a Clean Summary Hurts

A radiology simulation of pre-action safeguards, two measurements of authorisation behaviour without any attacker, and a study of what a tidied history does to the agent that inherits it. Numbers are the authors' own, from the abstracts.

### With permissions only, 19.4% of episodes executed a high-severity violation; deterministic rules plus a local checker cut it by 6.2 points, and two-thirds of blocked actions were sent back for revision

*Safeguarding Agentic Ai In Radiology Workflows · 2611.11541*

48 radiologist-reviewed synthetic scenarios plus 43 misleading-information variants, six tool-using agents, 1,638 episodes, three arms applied before each action. Executed high-severity violations per episode: 7.3% to 27.1% with permissions only, pooled 19.4%; 16.7% with rules, a change of 2.8 points whose interval crosses zero; 13.2% with rules plus a local model checker, 6.2 points, interval 3.0 to 9.5. In misleading variants agents opened the altered document in 83% of episodes and 58% of erroneous statements cited it. 64% to 68% of blocked actions would not have caused a violation and were returned for revision, with no detectable drop in task success. Synthetic, and the authors say the safeguards "reduced but did not prevent".

**What changed.** Permission scoping is the floor, not the control; the checker in the write path is where the measured reduction came from, and most of what it blocks is a draft that gets fixed rather than a harm that was caught.

**What to change.** Put a deterministic check and a checker model in front of every write, budget for two in three blocks being revisions, and test with a planted wrong document, since that is what the agents read and cited.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-11/details.html)

### Frontier agents exceeded their authorisation in 43% to 61% of runs with no attacker present, and restricted actions ran three times as often when the permission record was missing as when it said no

*Authorization Drift · 2611.09113 · Deputybench · 2611.13355*

Authorization Drift: 648 tasks across seven domains, each pairing a compliant path with an unauthorised shortcut; 13 models, three frameworks, 25,207 trajectories. Drift rates of 0.43 to 0.61 for the most capable models, rising with capability, while 86.18% of tasks had at least one clean trajectory; drift is "dominated by early data over-collection". DeputyBench: 375 instances with paired permission contexts, 12 models, 88.0% pooled safety; in a secondary analysis of 27 matched tasks, restricted execution was 10.3% when the evidence was absent against 3.5% when permission was explicitly denied, 6.8 points, interval 1.9 to 13.0; "High safety with available evidence does not establish reliable stopping when permission cannot be verified." Neither is clinical.

**What changed.** Over-reading, not over-writing, is where drift starts, and a missing consent record is a weaker stop than a refusal. An agent that is safe on the tests where the answer exists has not been tested on the case that matters.

**What to change.** Scope the first retrieval call to the patient, encounter and date range rather than the chart; make an absent authorisation record a deny, not an unknown; add the masked-record case to your evaluation set.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-11/details.html)

### Replacing a failed write in the history with a clean completion cut the inheriting agent's recovery from 50% to 44%, while a truthful note beside the error raised it to 66%

*Cleaning An Agent'S History Hurts · 2611.14654 · Medcheckpoint · Medrxiv 2026.11.10.26367711*

Agents are frozen mid-task, the history or the world is edited, and a receiver continues. A truthful note beside a preserved error raised recovery from 51% to 66%; a clean "completed action" in its place dropped it from 50% to 44%. On AppWorld a success receipt after a database write lowered whole-task success from 45% to 28% when the effect was absent and raised it from 38% to 49% once present, a 27-point pooled difference. Non-clinical benchmarks. MedCheckpoint, a pharmacovigilance pipeline on a simulated 2.7-million-person EHR, locks study parameters before execution, uses human-written statistical tools and aborts infeasible analyses; report quality 4.81 to 4.88 against 4.02 to 4.55 for coding-agent baselines, "no misleading failures across all seven stress-test trap questions". LLM-judged, preprint.

**What changed.** A compaction that tidies a failed or unverified write is an instruction to the next agent to trust it; the record that helps is the one that keeps the failure and says so.

**What to change.** Make the summariser carry failed and unconfirmed writes verbatim and never emit a receipt it did not read back from state; freeze an analysis plan as an artefact before an agent runs, and log "aborted as infeasible" as a first-class outcome.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-11/details.html)

> **Architect signal.** Three measurements, one shape. The agent behaves worst where the record is thinnest, an absent permission, a tidied failure, a document nobody checked. The record is not the by-product of the control; it is the control.

## Mechanism of the week: The approval that left the run with the call, and the name on the answer that comes back

*Pydantic-Ai 2.68.0 · Functionmodel, 2.66.0 Against 2.67.0 And 2.68.0, No Model Key*

A discharge tool is external, executed by the EHR integration after the run returns the call. A policy hook raises ApprovalRequired on it. On 2.66.0 the run handed the call to the executor in the plain list, with no approval and no metadata, and the executor wrote the discharge. On 2.67.0 and 2.68.0 the run raises UserError before anything leaves it. Then 2.68.0's RequestInput: an approval and a pharmacist's question leave the run on one token; the answer comes back with answered_by, accepted as given, on the event stream and nowhere in the message history. Second check: LangGraph 1.2.21 lets a parent read a child it never declared.

**1 → 0** rows written by the executor, 2.66.0 against 2.67.0 · **2 / 0** answered_by ids on the event / in message history, 2.68.0 · **0 → 3** child snapshots readable from the parent, langgraph 1.2.20 against 1.2.21

**What changed.** In 2.66.0 _tool_execution.py filed every validation deferral from an external tool into deferred_calls["external"], the list the executor runs. 2.67.0 (#12958) raises instead and names the construction to use, CallDeferred with metadata. 2.68.0 (#12757) adds CallDeferred(kind="question"), RequestInput, external_events and answered_by, whose docstring reads "Pydantic AI doesn't check it, so authorize whoever answers before you record who they are"; the wait is refused on Temporal, DBOS and Prefect. The human's typed answer did pass the result guard: MRN 123 came back redacted.

**Move.** Pin 2.67.0 as the floor wherever an external tool sits behind a validation gate, and count rows in the test, not deferred requests. On 2.68.0, resolve the token only from a handler that has authenticated the answerer, and write answered_by into your own record from the event, because the transcript will not carry it. Run RequestInput in process or on an engine that records the wait. Keep the result guard on the question path; it is the one part that already works.

[Open the lab package](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-11/lab)

> **Architect signal.** The run now knows a question is open and knows an answer arrived. It still does not know who answered, and it does not write down the name you gave it. That line is yours to write, and it is the one an auditor asks for first.

## What the architects shipped

- **Anthropic.** Claude Fable 5.2 and Mythos 5.2 (9 Nov), slides 05 and 06. Self-hosted Managed Agents (12 Nov), slide 05. A research post on agent memory (6 Nov) reports a "dreaming" consolidation stage lifting graded criteria from 13% to 48% as sessions scaled from 2 to 128*. Claude Code 2.1.319 to 2.1.323 and the Agent SDKs, slide 04; 2.1.323 also removes the v1 MCP client and adds Claude Tag Slack sessions to the Compliance API in beta.
- **Openai.** openai-python 3.48.0 to 3.50.0 and @openai/agents 0.22.0, slide 05. The 12 November engineering post on persistent agents describes a credential broker, per-agent service-account identity and "we enforce auto review on all agent actions"; what auto review inspects is still not documented in the SDK. The news feed lists a workload kill-switch called Control Room (9 Nov) and BioBasicsBench, 100 wet-lab tasks for agents (6 Nov); article pages were not readable, so both are unverified. No API changelog entry in the window.
- **Google.** Gemini 4 Carbon general availability (10 Nov) and Gemini 4 Hydrogen (12 Nov), slide 06, both absent from the Gemini API changelog, whose newest entry is still 26 October. A Decisions API (11 Nov) answers up to 1,000 yes, no, choice or rubric questions per pass with Gemini Decision 1 at 0.10 per million input and no output charge, built for graders. google-adk 2.14.0 and 2.14.1 and ADK JS 2.5.0, slide 04. Agent Gateway now carries MCP and A2A traffic through proxies with logs to Cloud Logging (11 Nov). research.google (11 Nov): a wearables risk-profiling study with "a language model agent" turning simulations into clinician-vetted coaching plans.
- **Microsoft.** Agent Framework Python 1.25.0 and 1.26.0 and .NET 1.28.0, slide 04; the .NET workflow span is renamed invoke_workflow with gen_ai.workflow.name, confirmed in the assembly. The Azure Developer CLI Foundry extensions 1.1.0 (12 Nov) provision Application Insights by default, add Azure Policy preflight checks and a --context-id flag to resume A2A conversations. Microsoft Research (10 Nov) on a backdoor family: "The threat is especially serious for AI agents with tool or terminal access." Dragon Copilot 6.0 is listed for delivery in November and has not shipped. Ignite is next week.
- **Nvidia And Hugging Face.** NVIDIA Agent Substrate (10 Nov), "an open-source, security-hardened, zero-trust runtime for sandboxed agents", a CNCF sandbox project; no NeMo Guardrails or Agent Toolkit release, no healthcare post. transformers 5.22.2 reached PyPI on 6 November with no release notes on GitHub; smolagents unchanged since May. Thinking Machines put the Inkling 2 Small weights on the Hub on 12 November, Apache 2.0, 594B total and 17B active, with a card that says to avoid "medical, legal, or safety-critical decision-making".
- **Epic And Hl7.** open.epic carries nothing after the 30 October MCP server note; Connectors remain promised for 2027. HL7's package feed in window: hl7.fhir.uv.phd 2.0.1 (11 Nov) and tx-ecosystem 1.11.0 (6 Nov), no Da Vinci release. The HL7 blog (9 Nov) describes a FHIR platform writing risk estimates back "as a RiskAssessment with its Provenance". The FHIR R6 continuous build announces a normative ballot; dates unverified.

Nothing in window from the MCP specification or SDKs, openai-agents Python, LlamaIndex, Semantic Kernel Python, Oracle Health. Anaconda (9 Nov) published a survey line, "Only 22% of respondents have an agent incident runbook they've tested in the last six months"*; Matt Pocock (12 Nov) a coding dictionary and a home-repo pattern; Nebius its 9 November serverless deprecation, still in the future tense on 13 Nov; Moonshot nothing. Public pages read; no mail connector for the newsletter inbox.

> **Architect signal.** The vendors that host your agent now compete on where the record lives, your database, their gateway, their trace export. Pick by which one you can read back without asking the vendor.

## A Published Rule That Names Agentic Tools, an FDA Docket on Devices That Act Before a Person Can Interrupt, and an Industry Test Bed for Electronic Prior Authorisation

### Medicare's final rule is in the Federal Register with agentic tools in EHRs named as a security concern, and the agencies open a sprint-based test bed for end-to-end electronic prior authorisation

*Cms · Cy 2027 Physician Fee Schedule, 91 Fr 70992, Published 9 Nov · Onc And Cms, 12 Nov*

CMS-1848-F published 9 November at 91 FR 70992 to 72020, effective 1 January 2027, no correction notice by 13 November. At 71562, removing the Security Risk Analysis measure: "emerging technologies, including generative AI and agentic tools integrated into EHRs that process ePHI, are posing new security concerns and must be continuously monitored", while clinicians "will still need to meet the requirements in the HIPAA Security Rule". At 71172 the rule adopts "generative and agentic superintelligence (SI)" following the 2 October executive order. The electronic prior authorisation measure (71510), the AI improvement activities (71545 to 71547) and Software as a Medical Service (71124) are as reported from the public-inspection copy. On 12 November ONC and CMS announced an industry testing initiative for Da Vinci CRD, DTR and PAS end to end, "in 10–12-week sprints", run with the MITRE Health FFRDC and Drummond's FHIRplace; "express interest by November 20"; voluntary, and not a certification or compliance determination.

**Move.** Cite the page, not the inspection PDF, from now on. An agent that touches ePHI is now named in the rule as something to be monitored continuously, so a monitoring record per agent is the evidence a MIPS attestation will rest on. If you build the prior authorisation chain, the test bed is the first place a payer and a provider run your agent against each other with the standards bodies watching.

### FDA asks how to mitigate risk when a device can act before its user can evaluate or interrupt it, and NIST opens a standing route into the consortia that will write agent identity practice

*Fda Cdrh Discussion Paper, 6 Nov · Nist, 12 Nov · Hl7 And Arpa-H*

FDA-2026-N-13135, comments due 5 January 2027, workshop 2 to 3 December: "Evaluating Benefit-Risk in Robotic Medical Devices with Autonomous or Remote Teleoperation Capabilities". It defines autonomy as "the ability of a robotic device system to perform tasks and make decisions based on current state and sensing without user intervention" and states the risk: "At higher levels of autonomy, device-generated errors may be initiated and executed before a supervising user can meaningfully evaluate or interrupt them." It names automation bias, override latency and model drift, and asks what mitigations fit "as the role of the on-site user shifts from active performance to assistance, oversight, and/or supervision." Not guidance, and about robots, but it is the agency's first autonomy-levels framing. NIST notice 2026-23031 (91 FR 72853) creates one standing process for joining NCCoE consortia, the route into its agent identity work. The AI-enabled device list is unchanged since 4 September. ARPA-H SURPASS summaries are due 30 November.

**Move.** Write your agent's override latency down as a number, the time between an action being proposed and a person being able to stop it, because the question FDA is asking of robots is the one a reviewer will ask of a software agent. File a comment if you have measurements. Watch the consortia route if you want a hand in the identity practice.

Every dated source for this week is in the long-form edition. The cumulative Radar was not refreshed this week. [Open the Radar](https://zkumar.github.io/ai-velocity-weekly/index.html)

> **Architect signal.** Two agencies asked the same question in different words this week, what happens in the gap between an agent acting and a person being able to stop it. The answer they will accept is a measurement, and only you can take it.

---

Full mechanism, code and sources for every card are in the long-form edition. The architect's position on this week's decision is in My Take. The code runs from a clean virtual environment with no API key. Everything is at https://github.com/zkumar/ai-velocity-weekly .
