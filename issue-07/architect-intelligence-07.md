# Architect Intelligence 07: The Sibling That Failed

Week Of Oct 10–16, 2026 · Vijay Zharotia

**Last week a paused run was state that nobody read correctly. This week a batch failed as a unit: an apixaban order written beside a failed allergy lookup vanished from the history, the resume was told it never ran, and the record got a second one.**

Issue 06 read what a paused run believes is still open. This week the unit became the batch: two tool calls in one model response, one of them a write, and what the history keeps about the one that succeeded when the other fails.

This week: 14 packages unpacked and read, 8 runs of the executed mechanism, 8 papers read, 14 models priced.

## Five changes, one home each

Each fact appears once below. This list says where.

1. **A completed write dropped from the history when its sibling raised, and ran again on resume** (Pydantic-Ai 2.55.0, executed), section 08
2. **Finished tool outputs survive a sibling's failure, and compaction waits for an open approval** (Openai Agents Sdk 0.24.0, docs), section 04
3. **The human-in-the-loop gate can pause once per tool call with a validated answer** (Langchain 1.4.6, docs), section 04
4. **Client shared state could replace the server's tool-approval state through a wrapped agent** (Agent Framework 1.22.0, docs), section 05
5. **A harness reviewer lets a model approve low-risk tool calls before a person sees them** (Pydantic-Ai 2.57.0, docs), section 05

## The Surviving Output, the Pause Per Call, the Eaten Answer

All three read from pull requests and installed wheels. The lost return is executed on slide 08.

### A finished tool call was dropped from the history when a parallel tool's guardrail tripped

*Openai · Agents Sdk For Python 0.24.0* · docs

PR #5332, closing issue #5327, keeps accepted call and output pairs through session history, error details, streamed results and RunState recovery when another tool in the turn fails; the run still reports the failure. PR #5363 stops automatic compaction while an approval is unresolved, where it used to send the open call to the API and get a 400 before the caller saw the question. RunState snapshots move to schema 1.21.

**What changed.** The output of a call that ran is no longer discarded by a sibling's failure, and a background rewrite can no longer erase a pending question. Exactly-once side effects across a crash are stated as out of scope.

**What to change.** Drain paused runs before the upgrade, since 1.21 snapshots are one-way, then handle tool_error_formatter calls with kind="tool_exception" and reconcile every failed turn against the record, not the history.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/ai-velocity-weekly-07.html)

### One validated interrupt per gated call, where the batched default matched answers by position

*Langchain 1.4.6* · docs

PR #41062, read from the installed wheel. Each gated call pauses with its own tool_approval interrupt and a response_schema of the decisions that tool allows; LangGraph checks the answer before saving it, an edit cannot switch tools, and each answered call resumes alone. Batched mode, still the default, carries every call in one interrupt with unchecked decisions in a separate list.

**What changed.** The gate can match the unit of execution for the first time. Middleware listed before it runs again up to the pause, and one invalid answer in a multi-answer resume may land after the others have run.

**What to change.** Switch any agent whose gated tools write to per_call, make everything ahead of the HITL middleware side-effect free, and send answers one at a time.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/ai-velocity-weekly-07.html)

### ToolNode treated an invalid human answer as bad model arguments and the interrupt was gone

*Langgraph 1.2.15* · docs

PR #9232. interrupt(response_schema=...) raises a pydantic ValidationError on a bad answer; inside a tool, ToolNode handed that error to the model as a request to fix its call, and the interrupt was no longer pending. The error is now marked, is_invalid_resume() names it, and ToolNode re-raises it whatever handle_tool_errors says. Same release: astream_events no longer drops interrupts (#9219) and a cached node's writes are saved as if it had run (#9259).

**What changed.** A malformed answer to a tool-level gate used to resume the run as though nobody had been asked, and the person was never told.

**What to change.** On 1.2.14 and earlier, search model turns for a validation-error message that follows an interrupt; each is a gate that closed without a decision.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/ai-velocity-weekly-07.html)

> **Architect signal.** Three fixes, three places a true fact left the history before the next turn was built from it. Build the next turn from a history you have reconciled, and log what the reconciliation changed.

## A Client, a Snapshot and a Model Writing the Approval

Three frameworks changed who can put an approval where the middleware reads it. All three read from changelogs and pull requests.

### Shared state from a client, or a stored snapshot of it, could supply the approvals a wrapped agent read

*Microsoft · Agent Framework 1.22.0* · docs

PR #9368, breaking. AG-UI merged client Shared State into AgentSession.state minus server-owned namespaces found on optional agent attributes; a wrapper that hid them left the approval namespace open to the client, including state replayed from a Thread Snapshot. Any client value holding a non-empty rules, queued_approval_requests or collected_approval_responses list is now dropped with a warning, and restored server state wins. #9316 binds interrupts to the resolved thread id.

**What changed.** The browser is off the approval store's write path, by shape rather than by key, so a legitimate client key with one of those three names is dropped too. Older runtimes cannot read 1.22 records.

**What to change.** Grep client state for the three list names before upgrading, alert on the new warning text, and do not run mixed workers against one session store.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/ai-velocity-weekly-07.html)

### ApprovalReviewer puts a model in front of the human for calls it judges low-risk

*Pydantic-Ai 2.57.0* · docs

PR #10143, released 16 October: "Adds a Harness ApprovalReviewer that lets a model approve low-risk tool calls before a person sees them." The release page carries no more; the source was not read. A tool-call judge paper the same week found all seven judges tested "favored a visible incorrect value over a correct value whose source was hidden".

**What changed.** An approval can now be granted by something with no credentials, under a risk tier the framework decides unless you do.

**What to change.** Keep the tiering in your code, record every model-granted approval with the reviewer model id and version, and keep any write to a patient record out of the tier it may see.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/ai-velocity-weekly-07.html)

### A delivery id on every trigger, a callback on every tool result, and siblings cancelled together

*Google · Adk 2.12.0* · docs

Triggers expose a delivery id "so tools can detect redeliveries" (#7322); after_tool_callback screens a tool's output before the model reads it (#6966); require_confirmation now works on @node and FunctionNode; sibling tools are cancelled on a child-originated cancellation (#7172) and id-less responses are counted when a parallel batch resumes (#7387); auth credentials stay out of the caller's tool arguments (#7162).

**What changed.** Idempotency gets a key the framework hands you, and a FHIR response gets a named place to be checked against its request before the model sees it. What a resume does with a cancelled batch changed without a flag.

**What to change.** Store the delivery id with every write it causes, put the request-versus-response check in after_tool_callback, and re-run your resume tests on 2.12.0.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/ai-velocity-weekly-07.html)

> **Architect signal.** Each release names one more party that can touch an approval before the person does. The field that says which party did is still one you have to add.

## A Price That Doubles in December and a Shared Medical Score

4,000 input and 500 output tokens per document, list prices read 16 October. Artificial Analysis is still v4.3.2; the healthcare index loaded this week, for three rows.

### Argon is $130 on Google's own page through 30 November, and $260 from 1 December

*Google · Gemini 4 Argon, Ga 13 Oct*

$2 in, $10 out, $0.10 implicit cache read, listed as valid through 30 November 2026, then $4, $20 and $0.20. It reads 53 on the Intelligence Index, the same as GPT-6 Astra at $650 and Claude Fable 5.1 at $650, and joins Sonnet 5.5 and GPT-6.1 Sol as the third $130 row with identical cached and uncached figures. Issue 06 carried this price as a third-party report; it is now the vendor's.

**What changed.** A validated $130 model becomes Opus 5.5's price for a model four index points below it, on a date the price page states.

**What to change.** Write 1 December into the validation file now, and decide before then whether the workload moves to Sonnet 5.5 at 56 or stays at Argon at 53 for double the cost.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/ai-velocity-weekly-07.html)

### Opus 5.5 reads 61, and Sonnet 5.5 at $130 shares 58 with Fable 5.1 at $650

*Artificial Analysis · Healthcare & Medical Index, Read 16 Oct*

The index weights medical knowledge 30%, agentic knowledge work 25%, long-context reasoning 15%, non-hallucination 10%, reasoning 10% and tool use 10%. Only three scores could be read from the page text: Opus 5.5 at 61, Sonnet 5.5 and Fable 5.1 at 58. No list price moved this week; Mistral Large 4's half-price launch sale ends about 20 October and Gemini 3.8 Flash's lower price on 31 December.

**What changed.** The one independent medical number that exists separates the two Claude tiers by three points and the $130 and $650 rows by none.

**What to change.** Record the three scores with the date read, leave the other eleven rows blank rather than carried, and run your own evaluation set before paying five times the price for the same medical score.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/ai-velocity-weekly-07.html)

> **Architect signal.** Three rows in this table carry a price with an end date printed beside it. A cost model that reads the list price today is wrong for the first quarter.

## The Judge, the Invented Summary Step, the Missed Escalation

A judge that approves what it can see, a summary entry with no source behind it, and escalation gated on stated confidence. Numbers are the authors' own, from the abstracts.

### Seven tool-call judges favoured a visible wrong argument over a correct one whose source was hidden

*Derivation Gap · 2610.18497*

Judges accept a correct argument value less often when the input does not state what the value should be, across schema defaults, inferred values and truncated sources. A reference derived separately from the full history, without seeing the candidate, lifts controlled-test AUROC from chance or below to between 98.40 and 99.59.

**What changed.** A model reviewing a write's arguments verifies the proposing model's framing, not the value. The week's ApprovalReviewer is this judge.

**What to change.** Give any model reviewer the full derivation context or an independently derived reference, and never only the call.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/ai-velocity-weekly-07.html)

### 83% of failed runs traced to an action taken on a summary entry with no environment output behind it

*Source-Judged Compaction · 2610.20927*

In a widely used structured compressor, most failures followed a summary claim nothing had produced. Scoring each entry for provenance and dropping the unsupported ones, one judge call per compaction, improves reliability on AppWorld and OfficeBench by 2.1 to 8.9 points at no extra agent tokens.

**What changed.** A compacted history is a second place a write can be asserted or denied without a tool result, beside the one on slide 08.

**What to change.** Check every compaction entry against a tool output before it is kept, and put the check in the summarizer hook LangChain 1.4.5 added.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/ai-velocity-weekly-07.html)

### Clean accuracy 0.97, and 32% to 97% of required escalations missed when gated on stated confidence

*Escalation Reliability · 2610.21270*

400 synthetic healthcare workflow episodes with a declared 5:1 cost for a missed escalation. Verbalised confidence has an ECE of 0.10 to 0.54 and a confidence-only policy gives no utility gain; a workflow-aware controller cuts missed escalations to 0.12 to 0.24, and its rule detectors fall from recall 1.00 on trigger phrases to 0.00 on paraphrases. Labels are single-author.

**What changed.** Asking the model whether it is sure is not an escalation policy, and a phrase-matched one is not either.

**What to change.** Make escalation an explicit workflow state in the harness, and paraphrase-test the detector before it guards a record.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/ai-velocity-weekly-07.html)

> **Architect signal.** A judge, a summary and a confidence score each stood in for evidence this week. The record is the evidence; everything else is a claim about it.

## Mechanism of the week: The order that finished beside the lookup that failed

*Pydantic-Ai 2.55.0 · Functionmodel, 2.54.0 Against 2.55.0, No Model Key*

One scripted response carries lookup_allergies, which raises after 300 ms, and place_order, which writes a row. The run fails and is resumed from its own history; the scripted model orders again if that history says the order was interrupted. On 2.54.0 under parallel_ordered_events, the DBOS default, the history held no return for the order, the resume showed both calls as interrupted, and the record held two rows. On 2.55.0 the return was kept and one row stood. A cancelled run gave the same pair.

**0 → 1** tool returns in the history after the failed run · **2 → 1** orders in the record after the resume · **8** runs, and the model's closing sentence in all of them was the same

**What changed.** The ordered-events executor settled a segment only after every call was done, so an exception from the first call propagated before the second was recorded, and a cancellation recorded nothing. Both handlers now record every task that finished, emit no event for it, and leave the exception alone. A history saved before the upgrade is not repaired.

**Move.** Search records for duplicate writes with an "interrupted" return in the transcript on 2.54.0 and earlier under ordered events. On every version, treat that sentence as outcome unknown and look the write up by its idempotency key before a resumed run may act, then put the real result into the history yourself. Pin 2.55.0 or later explicitly, because Python 3.10 resolves to 2.54.0.

[Open the lab package](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-07/lab/)

> **Architect signal.** The exception was correct and the history was wrong, and nothing connected the two. A failed run needs a reconciliation step whose input is the record, not the transcript.

## What the architects shipped

- **Anthropic.** SDK 1.14.0 creates OpenTelemetry spans by default when a global tracer provider exists and adds execution_identity to Managed Agents; the platform put OTel export for Messages and sessions in beta. The TypeScript agent SDK 0.3.300 now validates updatedInput from hooks and drops unknown keys, so an approver id stamped into a tool's input from a hook disappears.
- **Openai.** The Python SDK 3.27.0 to 3.31.0 adds agent environment suspension and expiration, session spending limits and a billing_not_active error, three more ways a session stops that are not completions. GPT-Live can call the Decisions API natively on transcript deltas (15 Oct), a typed check that can run before the speaker finishes the sentence.
- **Anaconda.** A 14 October post proposes an agency score of 0 to 3 where "a score of 3 requires per-action human approval" and an evidence package whose enforcement logs record "each decision with a policy ID and reason code". A companion post reports 4.25% of 99,643 scanned skills as unsafe, Anaconda's own scan. Read from the blog; the emailed edition could not be opened.
- **Google.** Gemini 4 Argon reached GA on 13 October with a published price and a published date on which it doubles. ADK 2.12.0 is on slide 05. Artificial Analysis published a separate Decision Index v1.0 the same day with results for Argon and GPT-6 Luna; it is not the index the model slide uses.
- **Fda.** Nothing published, and one deadline. Comments on the generative-AI device discussion paper, docket FDA-2026-N-7874, close Monday 19 October. One posted comment argues that "human in the loop" is not a sufficient safety claim and that agents be regulated by their authority to act, with audit records of approval points and resulting state changes.

Nothing in window from the MCP specification, Semantic Kernel, llama-index-core, huggingface_hub, HL7's package feed, CMS, ASTP/ONC, OCR, NVIDIA healthcare, Moonshot or Nebius. deepagents, llama-index-workflows, transformers and @google/adk released but their notes could not be read. Open@Epic is 21 and 22 October. The editor's newsletter inbox was not readable this run.

> **Architect signal.** Spans, identities and scores arrived this week for the agent and the session. The approver is still the one party without a field of its own in any of them.

## A Comment Window Closing Monday and Model Ids With an End Date

### The generative-AI device discussion paper takes comments until Monday, and the posted ones argue for authority-to-act tiers

*Fda · Docket Fda-2026-N-7874, Comments Close 19 October*

The paper "is for discussion only and does not constitute draft or final guidance." Comment FDA-2026-N-7874-0054 argues that "human in the loop" is not a sufficient safety claim, that "high-consequence or irreversible actions should ordinarily retain mandatory human checkpoints", and that audit records should capture "the objective, planned sequence, tools invoked, inputs and outputs, approval points, and resulting state changes". Its posting date could not be read.

**Move.** If you build agents that write to a record and have a position on how they should be classed, it is due Monday. The audit record that comment describes is the one slide 08 found a framework unable to keep; say so.

### Five GPT-4o and GPT-4.1 ids are removed on 14 January 2027, and the April legacy shutdown lands next Friday

*Openai · Deprecations Page, 14 October*

gpt-4o-2024-08-06, gpt-4o-2024-11-20, gpt-4o-mini-2024-07-18, gpt-4.1-2025-04-14 and gpt-4.1-mini-2025-04-14 shut down on 14 January 2027 with gpt-6-luna named as the replacement; fine-tuned versions follow their base. The shutdown announced on 22 April covering gpt-4, gpt-4-turbo, o1, o3-mini, o4-mini and gpt-image-1 takes effect on 23 October. Existing evals become read-only on 31 October.

**Move.** A validation record naming any of those ids now has an expiry. Replacing a model is a change under a change-control plan: write the re-validation protocol for the GPT-4 family before the January date, and run the 23 October list against production configs this week.

Every dated source for this week is in the long-form edition. The cumulative Radar was not refreshed this week. [Open the Radar](https://zkumar.github.io/AI-Velocity-Technology-Update-/index.html)

> **Architect signal.** One regulator is collecting positions on who may authorise an agent's action, and one vendor has dated the removal of models those positions were validated on. Both are inputs to the same change-control file.

---

Full mechanism, code and sources for every card are in the long-form edition. The architect's position on this week's decision is in My Take. The code runs from a clean virtual environment with no API key. Everything is at https://github.com/zkumar/AI-Velocity-Technology-Update- .
