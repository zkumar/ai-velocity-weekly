# Architect Intelligence 10: The Tool Nobody Listed

Week Of Oct 31–Nov 6, 2026 · Vijay Zharotia

**Last week the record thinned: a log, a checkpoint stream and a federal rule each stopped carrying something. This week the gate showed its edges: a write on neither approval list ran unasked, a guard that crashed let its tool through, and most of the fixes that shipped are settings somebody still has to turn on.**

Issue 09 read what a log and a checkpoint stream stopped carrying about an action. This week the subject is the approval gate at its edges: what a policy does with a tool it does not name, what a guard does when it fails, and what a paused run does with an answer it is no longer waiting for.

This week: 31 wheels unpacked and diffed, 10 runs of the executed mechanism, 78 abstracts read, 17 models priced.

## Five changes, one home each

Each fact appears once below. This list says where.

1. **A write named on neither approval list ran with no approval request, and the key that gates it is ignored one release back** (Agent Framework 1.24.0, executed), section 08
2. **A toolset marked as requiring approval ran a prebuilt Tool instance before anyone was asked** (Pydantic-Ai 2.66.0, executed), section 08
3. **A hook guard that raised an exception counted as no decision and the tool ran; it can now be set to block** (Claude Agent Sdk 0.2.177, docs), section 04
4. **A resume that answers a question nobody is waiting on can be refused, but only if the caller opts in** (Langgraph 1.2.20 · Sdk 0.4.14, docs), section 05
5. **Electronic prior authorization becomes a measure that names each certified step, required from 2028** (Cms Cy 2027 Physician Fee Schedule Final Rule, docs), section 10

## A Workflow File That Overrode the Tool, a Guard That Failed Open, an Approval for a Call Nobody Made

Three projects closed a path where a required approval was skipped without an error. Read from changelogs, pull requests and wheel diffs; the policy with a tool on neither list is executed on slide 08.

### A workflow file could switch off the approval a function was registered with, and one hosted approval list overwrote the other

*Agent Framework Python 1.24.0 · .Net 1.27.0* · docs

1.24.0 (30 Oct). #9606, declarative: an InvokeFunctionTool action asked for approval only if the YAML set requireApproval, so a function registered with approval_mode="always_require" ran unapproved when the file omitted it; "The workflow definition silently overrides the function author's approval requirement." #9499, hosted MCP on the OpenAI and Foundry clients: with both lists supplied, "the second assignment overwrote the first, so the always list was silently dropped." #9644: a checkpoint save in flight was cancelled when a sibling step failed, so a resumed run "would re-run the step and its side effects". #9261: two checkpoints with one timestamp resolved by iteration order. .NET 1.27.0, #9827: a restored Mem0 session skipped scope validation and a clear could send a DELETE with no scope filter.

**What changed.** The tool author's gate now survives a permissive workflow file, both hosted lists reach the API, and a completed step's checkpoint is saved before cleanup instead of being cancelled with it.

**What to change.** Before upgrading, list declarative workflows that call a function registered as always_require, because they will start pausing; review past hosted-MCP runs configured with both lists.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-10/details.html)

### A PreToolUse callback that raised was treated as no decision; on_failure="block" now makes a failed guard stop the action

*Claude Agent Sdk 0.2.177 · Claude Code 2.1.316 To 2.1.318* · docs

SDK 0.2.177 (3 Nov), #1460: "a Python hook callback that failed was treated as no decision, so a PreToolUse guard that crashed let the tool run". HookMatcher gains on_failure; with "block", a callback that raises, returns None, or returns a value the CLI rejects, "such as permissionDecision "Deny"", blocks the action, "so a callback with no opinion must return {}". An old CLI raises CLIConnectionError rather than ignoring it. Unset, failure is still no decision. Claude Code 2.1.317: "Fixed claude -p exiting 0 when a full disk or quota lost its transcript". 2.1.318: "Fixed permission prompts being answered by keys typed just after sending a message", and an approved shell command that ran "in the session's start folder, not the folder it was asked in".

**What changed.** A guard can fail closed for the first time, and the setting refuses to connect to a runtime that would ignore it. A headless run that lost its transcript no longer exits 0.

**What to change.** Set on_failure="block" on every matcher in front of a write, return {} for no opinion, spell deny in lower case, and check that a transcript exists per run instead of inferring it from success.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-10/details.html)

### A server-held history now rejects an approval for a call it is not waiting on, and reloaded tool results stop becoming files

*Pydantic-Ai 2.65.0 And 2.66.0 · Ten Advisories, 4 November* · docs

2.66.0 (4 Nov), #12313, UI adapters with manage_message_history="server": a request answering a tool call the model never made, or one already answered, is rejected before the agent runs, "If the conversation changed since the client loaded it, reload it from the server."; before, the adapter passed it through. GHSA-4cj4-hgwf-4hc4: a tool result shaped like a file item was rebuilt as a real file on reload, so "A third party who controls data a tool returns can use this to make the application download a URL"; tool returns now store content_file_digests and history written before 2.66 rebuilds only HTTP(S) URLs. 2.65.0 (3 Nov), #10658: a ConversationStore with a revision token, so "concurrent writers can't overwrite each other unnoticed".

**What changed.** An approval is matched to a pending call at the adapter, a stale save raises a conflict, and the stored format of a tool result gained a field that old transcripts do not have.

**What to change.** Pin 2.66.0, treat the rejection as a prompt to reload rather than retry, and re-test any audit replay that reads transcripts written before the upgrade.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-10/details.html)

> **Architect signal.** In all three, the unsafe path produced no error, so no alert was ever going to find it. The only test that does is one that takes the gate away on purpose and counts what was written.

## A Stale Answer That Can Now Be Refused, a Review Mode Without a Person, Five Fixes No Scanner Reports

Three changes to who may answer an approval and what a client is told about it. Read from release pages, changelogs, pull requests and wheel diffs; none executed.

### Each interrupt in a node gets its own id, and strict resume refuses an answer to one that is not pending

*Langgraph 1.2.19 And 1.2.20 · Langgraph-Sdk 0.4.11 To 0.4.14* · docs

1.2.20 (5 Nov), #9589: _interrupt_id hashes the task namespace with the number of answers already held; before, every interrupt() in one task shared one id. A fallback remains: "Older versions gave all of a task's interrupts the first id." #9574: with the private key __pregel_strict_resume, a resume naming a non-pending id raises UnknownInterruptError, and "The error is raised before anything is written". SDK 0.4.14 (6 Nov) exposes strict_resume. 1.2.19 (30 Oct), #9486: a node's trace_policy now reduces payloads for tracers only; other callback handlers get the real input and output, and the policy is "Not intended to redact secrets." SDK 0.4.12: a stream that closed with no end event gave "a cut answer and no error"; the client now checks the run and reconnects.

**What changed.** A duplicate or late approval can be refused with the list of questions still open. Without the key it is still accepted, and an answer to the old shared id still fills the next question.

**What to change.** Turn strict resume on wherever a client can retry, log UnknownInterruptError with its pending ids, and re-check any audit join keyed on interrupt id.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-10/details.html)

### An agent session can be set to review its own eligible actions, and a conversation can be held on a server you cannot read

*Openai Python 3.42.0 To 3.46.0 · Anthropic 2.4.0 To 2.6.0* · docs

openai 3.42.0 (31 Oct), #4217: sessions take review "none" or "auto_review", documented as "Review eligible actions automatically. Deny manual approval fallbacks."; sessions.update can replace a running session's tools, "Functions and MCP servers change on the next model call." #4209: background compaction defaults on. What is eligible, and what reviews, is not stated anywhere read; the API changelog has no entry. Anthropic message threads, beta 2 Nov: "The API keeps the conversation on the server"; "There is no API to list, read, or delete a thread."; "Message threads are not ZDR eligible."; refused for HIPAA-ready organisations. anthropic 2.5.0 stops the memory tool deleting /memories itself; 2.6.0: "stop recording sampling parameters on OpenTelemetry spans".

**What changed.** One enum value removes the person from a session's approval path, a session's tools can change between two model calls, and a vendor now states that its copy of a conversation cannot be read back.

**What to change.** Write the review mode and the tool set into your own record whenever you set them; keep your own copy of every message; log sampling parameters yourself.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-10/details.html)

### Five fixes with a security consequence shipped in window with no advisory, and OSV listed nothing for any package swept

*Semantic Kernel 1.47.0 · Fastmcp 4.1.5 · Agent Framework · Osv, 6 November* · docs

semantic-kernel 1.47.0 (5 Nov), #14668: the OpenAPI plugin allowlist was a string prefix match, so "/api/../admin and /api/%2e%2e/admin matched an /api allowlist while httpx would request /admin". #14607: a history reducer on a ChatCompletionAgent was never applied; it now runs before each request. fastmcp 4.1.5 (1 Nov), #6130: a mounted resource template let a comma-joined parameter list past the parent's screening. Agent Framework #9825: the restricted checkpoint unpickler allowed type() to construct a class. Two more in .NET. OSV, queried 6 Nov for 65 package names, returned no record published in the window, not even for pydantic-ai, slide 04. google-genai 3.0.0 (6 Nov) defaults to API v1 and to httpx2 with the OS trust store.

**What changed.** A plugin allowlist could be walked around with dot segments, a reducer that was configured never ran, and none of it reached the database a dependency scanner reads.

**What to change.** Read the changelog of every agent dependency on upgrade; re-run evaluations after 1.47.0, since the model now sees reduced history; pin httpx behaviour before taking google-genai 3.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-10/details.html)

> **Architect signal.** Each of these moves an answer further from the person who gave it, a retry, a reviewer that is a mode, a copy on someone else's server. The record of who answered has to be written where you can read it.

## No Price Moved, Three Rows Unverified, and a Regraded Index

4,000 input and 500 output tokens per document, list prices read 6 November. Artificial Analysis is at Intelligence Index v5.0.1 since 3 November; scores still do not compare with Issues 01 to 08.

### One evaluation was regraded, five rows moved a point, and the medical index's composition can finally be read

*Artificial Analysis · Intelligence Index V5.0.1, 3 November*

Changelog, 3 Nov: "Incorporated grading robustness improvements from the CritPt authors and regraded all models on CritPt v2."; same nine evaluations and weights. Readable scores: Gemini 4 Carbon 60, Opus 5.5 59, GPT-6 Astra 57, Sonnet 5.5 55, GPT-6.1 Sol 55, Terra 51, Fable 5.1 50, Argon 50, Kimi K3.1 Pro 46, Haiku 5.5 36, Grok 4.7 35, DeepSeek V4.1 Flash 33, Gemini 3.8 Flash 31, Luna 28, Mistral Large 4 26. Healthcare & Medical is unchanged, Opus 5.5 58, Sonnet 5.5 54, Astra 54, Sol 52, Kimi K3.1 Pro 52, Fable 5.1 51, and its page now renders: "Incorporates 5 evaluations: AA-Omniscience v1.1, AA-Briefcase v1.1, MLCR-AA, AutomationBench-AA, HLE-Diamond." It prints no version. HealthBench Professional top three unchanged: Astra 66.0%, Sol 65.1%, Sonnet 5.5 63.0%.

**What changed.** A patch version moved five scores by one point each, and the medical figure has a stated composition for the first time, with no version or date attached to it.

**What to change.** File the patch version with every score, v5.0.1 not v5; cite the medical index by the date you read it until it carries a version of its own.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-10/details.html)

### Every list price is where it was, three rows could not be confirmed on a vendor page, and a host retires pinned models on Monday

*17 Rows, Read 6 Nov · Kimi K3.1 Pro Weights · Nebius, 9 Nov*

No row changed price. Unverified this week: Gemini 4 Carbon, still on no Google price page nine days after launch, 4 / 20 being Artificial Analysis's figure; and both Kimi rows, whose price tables did not render to a text reader on 6 November, carried at 2 / 10 / 0.20 and 3 / 15 / 0.30. Kimi K3.1 Pro weights are on Hugging Face, 2.8T parameters with 104B active, under a licence needing a separate agreement from a model-as-a-service business above $20M in annual revenue. Nebius Token Factory lists gpt-oss-120b at 0.15 / 0.60 with cached input at 0.10, and says a list of models, DeepSeek V4.1 Flash among them, "will be removed from Token Factory Serverless on November 9, 2026" with no automatic rerouting. Printed and unchanged: Gemini 4 Argon doubles on 1 December, 3.8 Flash on 1 January.

**What changed.** The $130 tier is still four models within five index points. What moved is confidence, three flagged rows instead of one, and a second open-weight licence that is not open for a hosting provider.

**What to change.** Re-read the price of anything you host through a third party before Monday; record the licence class beside the word open; keep unverified rows out of a validation file.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-10/details.html)

> **Architect signal.** A week with no price change still changed the table, a regrade, two pages that would not render, a retirement date. The figures you filed are only as current as the last day somebody re-read their source.

## Thirty-Two of Forty-One Hosts With No Approval Step, PHI Tools Called When the Task Did Not Need Them, and a Harness That Reordered the Models

A census of approval defaults across MCP servers and hosts, a canary test of minimum-necessary access, and a pre-registered study of what the scaffold does to conduct. Numbers are the authors' own, from the abstracts.

### An estimated 90% of destructive MCP tools have no server-side confirmation, and 32 of 41 hosts and SDKs have no approval step by default

*When Neither Side Confirms · 2611.02527*

Source-code measurement of both halves of MCP's split approval: a 1,000-repository sample of the official registry, and 41 open-source hosts and agent SDKs. Server side, an estimated 90% of destructive tools (95% CI 82 to 95) ask for no confirmation. Host side, 32 of 41 have no approval step by default, 16 of 25 applications among them. Paired, "60.7% of pairs have no enforced human approval by default". Four of five low-cost models executed an injected deletion in 479 of 960 runs. If hosts prompted for every tool not annotated read-only or non-destructive the unapproved share would fall to 5.4%; universal elicitation on the server side would leave 56.7%.

**What changed.** The slide 08 finding is not one framework's quirk. Across the ecosystem the default for a destructive tool is that neither side asks, and the host's default decides almost all of it.

**What to change.** Make the host default deny, prompting for every tool not marked read-only, and do not count a server's elicitation or a confirm flag the model can set as an approval.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-10/details.html)

### Three of five models called PHI tools on clinical tasks that needed no identifiers, and the answer alone did not show it

*Accessed, Never Disclosed · 2611.02319*

Canaries embedded in synthetic patient records, with every tool call linked to whether the canary reached the final answer, so that retrieving an identifier and revealing one are measured separately, across five models, four boundary levels and seven attack frames. Three models invoked the PHI tools unnecessarily. Under the strictest policy the residual access was confined to frames where the user overrode the policy or asserted approval, and a pre-execution gate given a task-necessity criterion nearly eliminated it. The abstract gives no rates. The authors: "Output-only evaluation cannot verify minimum-necessary access".

**What changed.** Minimum necessary turns out to be a property of the tool access log. An agent can read an identifier it never repeats, and an evaluation of outputs will pass it.

**What to change.** Put a task-necessity check in front of identifier-returning tools, audit minimum necessary from the access log, and treat an in-chat "I approve" as untrusted text.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-10/details.html)

### The same model moved from first to last of four when only the harness changed, and a quarter of violations came with a denial

*The Harness Is The Model · 2611.06116*

Four open-weight models, five harnesses each, 156 pre-registered cases in a simulated retail bank, 3,120 episodes scored deterministically from the executed tool trace. For one model the spread between best and worst harness was 11.5 percentage points, enough to move it from first to last. A same-model reviewer cut violations from 9.6% to 6.4% without raising over-refusals. In an analysis labelled exploratory, 26% of violations were accompanied by a customer message denying the action the agent had just executed, which a transcript-only review would record as a correct refusal. Banking, not healthcare. The author: "the unit of validation should be the model-harness pair".

**What changed.** A validation that names a model and not the framework version under it describes half the system, and a review of the conversation scores a denied action as a refusal.

**What to change.** Version and validate the model and harness as one pair, re-validate on a framework upgrade as on a model change, and test conduct against the action log.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-10/details.html)

> **Architect signal.** Three studies in three domains used one instrument, the tool trace, and each found a default that nobody had chosen. Measure your own defaults the same way before a reviewer does it for you.

## Mechanism of the week: The write the approval policy did not name, and the key that last month's package never reads

*Agent Framework 1.24.0 · Scripted Client, 1.23.0 Against 1.24.0, No Model Key*

A ward agent reaches a pharmacy MCP server whose policy lists place_order (always ask) and read_chart (never ask). A scripted model calls discontinue_order, a write on neither list. Both versions: no approval request, one row written. With "default": "always_require", 1.24.0 asks first; 1.23.0 never reads the key and writes. An always list given as one comma-joined string gated both writes on 1.23.0 and neither on 1.24.0. Second check: a pydantic-ai toolset requiring approval ran a Tool instance unasked on 2.65.0.

**0 → 1** approval requests, default set, 1.23.0 against 1.24.0 · **1 → 0** requests, joined-string list, 1.23.0 against 1.24.0 · **1 → 0** unasked writes, pydantic-ai 2.65.0 against 2.66.0

**What changed.** In _mcp.py the resolver returned None for a name on neither list and FunctionTool turned None into "never_require". 1.24.0 adds a default key, warns once when never_require_approval is set without it, and treats a bare string as one name where 1.23.0 tested it with "in". Hosted MCP tools "do not read default". pydantic-ai's add_tool now applies the toolset's flag to Tool instances.

**Move.** Set "default": "always_require" and list the reads, so the outside of the list is the gate. Pin the 1.24.0 floor in the same change, because the key is a silent no-op below it. At start-up, assert the approval mode each exposed function resolved to. Pass name lists as lists, never a joined string. Fail CI on FutureWarning from this package. In tests, call a tool on no list and count rows, not replies.

[Open the lab package](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-10/lab)

> **Architect signal.** The policy file was reviewed, correct and deployed, and the process ran something else. A control that exists only as configuration is a statement of intent until a test shows the installed code reading it.

## What the architects shipped

- **Anthropic.** Platform release notes: message threads in beta on 2 November, slide 05; a text watermark on Mythos 5, Opus 4.7 and Sonnet 4.6 output (3 Nov) that "adds no tokens or hidden characters", with no detection API; an IP allowlist in beta (5 Nov), "which limits where a leaked API key can be used". A 2 November research post describes a zero-knowledge proof that a committed model produced an output, at "~70-95x the GPU time of running the model itself"*.
- **Openai.** openai-python 3.42.0 to 3.46.0, slide 05, also add 12-hour cache lifetimes, workload identity federation, and Australia, India and Japan residency endpoints, all through the SDK with no API changelog entry. The changelog itself lists GPT-6 Rosalind on 30 October, "specialized biological reasoning with scientific tool use", trusted access only, two image models, and GPT-6-Cyber on 5 November. openai-agents had no release. openai.com article pages were not readable this week.
- **Google.** A health AI evaluation framework on 4 November, arXiv 2611.05127, combining "closed-question benchmarks, autoraters, and expert human review" by user journey and lifecycle phase; no scores or code, abstract only read. google-genai 3.0.0 on 6 November, slide 05. One entry Issue 09 missed, dated 26 October: new paid-tier Generate Content projects store requests by default, with a per-request opt-out. No ADK release.
- **Microsoft.** Agent Framework Python 1.24.0 is on slides 04 and 08, Semantic Kernel 1.47.0 on slide 05. The Foundry extension for the Azure Developer CLI reached 1.0 on 5 November with agent and deployment settings in azure.yaml, "Keep it with your code so deployment changes are reviewed in the same pull request."; the agents extension under it is still a beta that renamed a declaration and moved a command in October.
- **Nvidia And Ibm.** NVIDIA (4 Nov) walks one failure, an agent sending a message without confirmation, from stored traces to a test that fails any unconfirmed send; the fix it accepts is a prompt change, not a runtime gate. IBM Research on the Hugging Face blog (3 Nov): one model passed 81.1%, 46.7% and 30.0% of the same 90 tasks under three harnesses*, "Guidance steers the model, but approvals and ToolGuards are enforced by the runtime."
- **Epic And Hl7.** open.epic carries an entry dated 30 October, "The open.epic MCP server is now available.", a search surface for specifications and playbooks, not patient data; endpoint and authentication could not be read, so unverified. Connectors for Epic agents remain "Coming in 2027". HL7 published EHR-S FM Release 2.1 Usability Functional Profile, Edition 2 on 4 November and tx-ecosystem 1.11.0 on 6 November; no Da Vinci package and no recap of the 28 October roundtable.

Nothing in window from the MCP specification or SDKs, Google ADK, openai-agents, LlamaIndex or transformers. Anaconda, Nebius and Matt Pocock: nothing on agents (public pages read; no mail connector for the newsletter inbox).

> **Architect signal.** Two vendors shipped something about proof this week, a watermark you cannot verify and a proof of inference seventy times the cost of the inference. Neither is usable as evidence yet, so the transcript you keep remains the proof you have.

## A Prior Authorization Measure That Names Each Certified Step, an AI Policy a Clinician Can Attest To, and Two Device Types Where the User Reviews First

### Electronic prior authorization is optional for 2027 and required for 2028, with every step done through certified modules inside one request

*Cms · Cy 2027 Physician Fee Schedule Final Rule, Filed 4 Nov, Effective 1 Jan*

CMS-1848-F, FR Doc. 2026-22743, publication scheduled 9 November. For the CY 2027 performance period the MIPS Electronic Prior Authorization measure is optional and reworded from "using data from CEHRT" to "using CEHRT". For CY 2028 it is required, with a second measure for prescription drugs: the clinician "uses CEHRT to electronically request and receive coverage requirements, request and populate prior authorization documentation using templates and rules, submit the prior authorization request, and receive the payer response", mapped to 45 CFR 170.315(g)(31) to (33), all "within the same prior authorization request." A new voluntary activity, IA_AHW_4, has participants "Establish and maintain organizational policies and procedures for AI use in healthcare settings"; IA_PSPA_16 adds "processes to identify, review, and mitigate AI‑related adverse events or near‑misses". Asked for specific validation requirements, CMS replied "our goal is to keep this activity broadly applicable."

**Move.** An agent that assembles a prior authorization outside the certified coverage, documentation and submission chain earns the clinician no measure credit from 2028; log that chain per request, end to end. A customer can attest to the AI activity from 1 January only if your deployment produces the evidence: an evaluation record, monitoring, and a near-miss log with escalation.

### Two final device classifications require review by the user before a diagnosis and independent test data, and Medicare pays only for authorised software

*Fda, 5 November · Cms Opps And Home Health, 4 November · Onc And Arpa-H*

FDA final orders, effective 5 November. 21 CFR 882.1454, prognostic software for mild cognitive impairment (91 FR 69690): "intended for adjunctive use and not intended as a stand-alone diagnostic or prognostic tool"; "The test data set must be independent from data used in training/development of the device." 21 CFR 864.3900, cervical cytology imaging with an AI algorithm (91 FR 69687): review "should be performed by the user prior to rendering a diagnosis". Neither has change-control text. CY 2027 OPPS final rule (CMS-1850-FC): software payment becomes "Software as a Medical Service", which must "have FDA marketing authorization to receive Medicare payment", and "we are declining to expand the scope of our policy to include non-device CDS at this time". ONC's HTI-5 slides state audit criteria (d)(2), (d)(3) and (d)(10) are "Unchanged". ARPA-H SURPASS summaries are due 30 November.

**Move.** An agent that wraps an authorised device in either class must present its output as an input to a person and keep the labelling's limits visible. Operational and agentic tooling has no Medicare benefit category, so its value case has to stand without one. The certified audit-log criteria survived HTI-5; build on them.

Every dated source for this week is in the long-form edition. The cumulative Radar was not refreshed this week. [Open the Radar](https://zkumar.github.io/ai-velocity-weekly/index.html)

> **Architect signal.** A payment rule now spells out the workflow an agent has to stay inside, step by step, and asks the organisation to hold the policy for everything outside it. Regulators are drawing the list; what sits beyond it is yours.

---

Full mechanism, code and sources for every card are in the long-form edition. The architect's position on this week's decision is in My Take. The code runs from a clean virtual environment with no API key. Everything is at https://github.com/zkumar/ai-velocity-weekly .
