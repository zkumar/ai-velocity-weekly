# Architect Intelligence 05: The Reach Of A Yes

Week Of Sep 26–Oct 2, 2026 · Vijay Zharotia

**Last week an approved write ran zero times or twice. This week the yes itself travelled: an "always" given for one agent's saline flush covered another agent's warfarin, and a request nobody issued was approved from a transcript.**

Issue 04 counted how many times an approved write runs. This week four frameworks changed the key and the store behind the approval itself: which agent a yes belongs to, where the pending request is kept, and which call id it is matched to.

This week: 13 packages unpacked and read, 5 mechanisms executed, 6 papers read, 17 models priced.

## Five changes, one home each

Each fact appears once below. This list says where.

1. **A sticky yes for one agent's tool covered another agent's order** (Openai Agents Sdk 0.23.1, executed), section 08
2. **A request the framework never issued was approved from caller history** (Agent Framework 1.20.0, executed), section 04
3. **Two calls sharing one id ran the write twice and the read never** (Pydantic-Ai 2.53.0, executed), section 04
4. **A confirmation flag on a workflow node gave an error and no pause** (Google Adk 2.11.0, executed), section 04
5. **A tool hidden from the client's list still executed by name** (Mcp Python Sdk 2.3.0, executed), section 05

## The Store, the Call Id and the Node Behind an Approval

All three executed on both versions. The owner-scoped approval is executed on slide 08.

### A forged request and its own approval submitted a prior auth on 1.19.0

*Microsoft · Agent Framework 1.20.0* · executed

PR #8750 moves approval authority into the AgentSession. On 1.19.0 a caller-supplied history holding an approval request the framework never issued, plus its approval, ran the tool for pt-999. On 1.20.0 it is dropped with one WARNING. So is a genuine approval replayed with no session: nothing submitted, an empty reply, no exception.

**What changed.** The transcript stopped being an authority. A stateless approval service that replays the conversation now resumes nothing, and says nothing.

**What to change.** Persist the AgentSession and pass the same one to the resuming run, alert on the warning text, and leave disable_approval_response_binding unset: with it the forged request ran again.

[Read the mechanism](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-05/lab)

### One tool_call_id on two calls: the chart read never ran and the submission ran twice

*Pydantic-Ai 2.53.0* · executed

A response carrying read_chart and submit_prior_auth under the same id. On 2.52.0 the last call won the binding for both: submit_prior_auth executed twice, read_chart zero times, and the model was handed a synthesised "interrupted" return for the chart. On 2.53.0 the batch raises UnexpectedModelBehavior before any call executes.

**What changed.** A repeated id is a hard failure instead of a mis-bound result, and a new exception on the request path.

**What to change.** Catch UnexpectedModelBehavior, log the raw response and do not retry blindly. Below 2.53.0 behind any gateway that rewrites ids, count submissions against requests.

[Read the mechanism](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-05/lab)

### require_confirmation on a workflow tool node pauses, where 2.10.0 returned an error string

*Google Adk 2.11.0* · executed

A two-node workflow with no model. On 2.10.0 the gated node's output was "This tool call requires confirmation, please approve or reject.", the workflow finished and nobody was asked. On 2.11.0 it emits adk_request_input with an id built from the node path, runs nothing until a confirmed response arrives, then submits once.

**What changed.** A gate that failed safe and silent became a request with a stable id. The response carries a boolean and no approver.

**What to change.** Store the request id beside the approver's identity yourself, and search 2.10.0 workflow outputs for the confirmation error: each one is a submission that never happened.

[Read the mechanism](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-05/lab)

> **Architect signal.** None of the three needs a code change on your side to take effect. One turns a working resume into a silent no-op and one adds an exception, so a warning text and an exception class belong in monitoring before the pin moves.

## A Callable Tool Off the List and a Transcript the API Refuses

One executed, one read from the vendor's documentation. Each is a store that was treated as complete or portable.

### lookup_claim was missing from list_tools() and ran when called by name

*Mcp Python Sdk 2.3.0* · executed

A tool registered with the header annotation "Member Id", invalid because of the space. On 2.2.0 the server accepted it, the client listed zero tools, and call_tool executed it and returned two open claims. On 2.3.0 registration raises InvalidSignature and the call returns "Unknown tool".

**What changed.** The listed tools and the callable tools were different sets. An allow-list or a per-tool policy built from the list never covered the hidden one.

**What to change.** On 2.2.0 servers, compare the tools registered on the server with what a client lists, then upgrade so a bad annotation fails at start-up.

[Read the mechanism](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-05/lab)

### Forced tool choice returns 400, and so does a thinking block replayed after the prompt changed

*Anthropic · Claude Sonnet 5.5 Api* · docs

tool_choice of any or tool "returns a 400 invalid_request_error" on this model. Thinking blocks are checked against what preceded them: change the system prompt, the tools or an earlier message and a replay returns 400, by default for accounts created on or after 31 August 2026. Blocks work only in the account that produced them.

**What changed.** A stored transcript is not portable across a prompt edit, a tool change or a redaction, and a forced structured call is not available.

**What to change.** Keep the deployment version with every paused state and resume against it. Move forced-tool extraction to auto with strict schemas, and test that the tool is still called.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-05/details.html)

> **Architect signal.** An inventory read from the client and a transcript kept for replay both went stale with no error at write time. Reconcile each against its source on a schedule, not at the audit.

## Three Models at $130 and a Model Id That Lasted Seven Days

4,000 input and 500 output tokens per document, list prices read 2 October. Artificial Analysis is still v4.3.2; only the top three medical-index rows could be read.

### Sonnet 5.5 does the job for $130 and reads 56, two points under Opus 5.5 at half the cost

*Anthropic · Claude Sonnet 5.5, New 28 Sept*

$2 in, $10 out, $0.20 cached, the same list price as Sonnet 5. It reads 56 on the Intelligence Index against Opus 5.5 at 58, and 58 on the Healthcare & Medical Index against 61. Gemini 4 Argon, announced 30 September with limited access, reads 53 at an introductory $2 and $10 that is not yet on the API price page.

**What changed.** The $130 row moved from index 48 to 56 in a week, and the gap to the $260 row is two points general and three medical.

**What to change.** Run your own evaluation set on both before paying double. Record both index scores with the date read, and treat the Argon price as provisional.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-05/details.html)

### GPT-6 Sol was replaced seven days after launch, at the same price and half the cache rate

*Openai · Gpt-6.1 Sol, New 29 Sept*

GPT-6.1 Sol is $2 in and $10 out with cached input at $0.10, down from $0.20, so the cached run falls from $72.40 to $69.20. It reads 52, four points above its predecessor. The id gpt-6-sol is gone from the price page with no deprecation entry. Sonnet 4.5 retires 30 November; three GPT-5 ids shut down 1 April 2027.

**What changed.** A model priced in Issue 04 on the 25th could not be selected from the price page on the 29th.

**What to change.** Decide now what evidence a point release needs before it replaces a validated model, and give the validation file's owner both deprecation pages to watch.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-05/details.html)

> **Architect signal.** A validation record that names a model without naming its retirement path may describe something already gone. Put the deprecation page beside the price in the file.

## The False Success, the False Accusation and the Encounter Nobody Scored

Three results on success claimed after a failed tool, correct work undone on an unsupported complaint, and accuracy that hides a failed encounter. Each is the authors' own measurement.

### False success after a failed tool: 22.8% at baseline, 0.8% under an evidence contract

*Failure-Transparent Agents · 2609.35732*

100 tasks with the failed observation fixed before generation, six models, 3,600 human-annotated responses. A transparency instruction alone gives 9.3%. Fabricated detail falls from 28.3% to 14.3% to 0.8% across the three policies, while useful responses rise from 74.9% to 98.8%. The benchmark is the authors' own blocked-task set.

**What changed.** An instruction to be honest still leaves about one false success in eleven. A structured contract leaves fewer than one in a hundred.

**What to change.** Require every completion claim to carry the tool call id and the returned status, and have the harness reject a "done" without them.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-05/details.html)

### Told falsely that finished work was wrong, agents damaged it in up to 60% of runs

*Cave-Bench · 2609.32616*

365 tasks across six domains where the work is verified correct and the accusation cannot be checked locally. Across 14 models in one coding harness, false accusations damaged correct work in up to 60.06% of runs, stronger models often after recovering the supporting evidence. A harness gate cut replayed harm by 74%. Software tasks, not clinical.

**What changed.** After compaction or a handoff, a complaint about completed work is an input the agent tends to obey.

**What to change.** Put the amend tool behind its own gate, and route an unsupported complaint about a completed write to a person with the evidence attached.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-05/details.html)

### 90.7% diagnostic accuracy, and fewer than 30% of encounters completed correctly

*Klinikebench · 2609.38480*

333 clinician-authored sandbox tasks with a virtual patient, clinical tools and action constraints, more than 35 clinicians involved. Across 31 models the best succeed on fewer than 30% of tasks while their diagnosis accuracy reaches 90.7%. History taking, examination requests, constraints and the final record are scored separately and together.

**What changed.** Final-answer accuracy is no longer evidence that the encounter was conducted properly.

**What to change.** Gate releases on every step passing, constraints included, and report the diagnosis score beside the whole-encounter score, never alone.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-05/details.html)

> **Architect signal.** A claim, a complaint and a score each looked like evidence and was not. Whatever reaches the record should cite the result it rests on, and the citation is what the harness checks.

## Mechanism of the week: The always that followed a tool name across a handoff

*Openai Agents Sdk 0.23.1 · Scripted Model, 0.22.3 Against 0.23.1, No Model Key*

Two agents, intake and anticoagulation, each own a tool named place_order behind an approval gate. The scripted model has intake order a saline flush; the nurse answers "always approve"; the run hands off and the second agent orders warfarin 10 mg. On 0.22.3 the nurse was shown one order and two reached the record. On 0.23.1 the warfarin call interrupted and one order was written. On both versions the same always also covered heparin 5,000 units from the same agent, in process and after a JSON round trip.

**1 → 2** orders the nurse was shown in the handoff run · **2 → 1** orders written before anyone was asked again · **0** arguments in the key a sticky approval is stored under

**What changed.** The sticky approval was keyed by tool name. It is now keyed by owning agent and tool name, and saved run state moves to schema 1.18. Neither key contains an argument.

**Move.** List every tool gated with always_approve and remove it wherever the argument carries clinical meaning. Search order history for writes by one agent under a sticky approval granted to another. A paused run saved after a sticky yes on 0.22.3 came back on 0.23.1 asking for the approved call again, so drain paused runs before rollout.

[Open the lab package](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-05/lab)

> **Architect signal.** How wide an always may be is a decision to make per tool and to write down, because the framework's key will never be narrower than the tool name.

## What the architects shipped

- **Google.** ADK 2.11.0 adds an optional ToolCallIntegrityPlugin that stamps each stored function call with an HMAC and lets a tool run only on a valid stamp, plus plugin callbacks around workflow tool nodes. The first shipped control for a call altered after approval.
- **Microsoft.** Agent Framework 1.20.0 also gives generated MCP calls host runtime context only, "never model arguments, even when names collide", and pickles dict subclasses in checkpoints, so 1.19.0 and 1.20.0 encode the same state differently.
- **Openai.** Agents SDK 0.23.0 binds resumed MCP calls to their original recipients and leaves reasoning out of default trace exports. The Python SDK adds session traces, and the Agents API gains computer use.
- **Anthropic.** SDK 1.10.0 adds a refusal stop reason and stop_details to Managed Agents idle events, so a session that stopped on a refusal can be told from one that finished, and refuses credential files that group or others can write.
- **Ai Hero.** Matt Pocock's newsletter of 1 October announces a guardrail that blocks destructive git commands before a coding agent runs them. Read from the email only, so UNVERIFIED: a deterministic check in front of an irreversible tool.

Nothing in window from the MCP specification or blog, LangGraph, llama-index-core, Semantic Kernel, NVIDIA healthcare or Epic. FHIR R6 is not final. No HTI-5, TEFCA, HIPAA Security Rule or physician fee schedule final rule appeared. Nebius published Q3 notes with a stateless Responses API.

> **Architect signal.** Every control here binds a call to something: a stamp, a host, a recipient. None binds it to the person who approved, and that field is still yours to write.

## Change Control Gets a Fiscal Year and Trials Get an Agent Layer

### The AI lifecycle and change-control guidances are on the list FDA intends to publish as final this fiscal year

*Fda · Cdrh Fy2027 Proposed Guidances, Docket Fda-2012-N-1021*

The A-list, "priority guidance documents CDRH intends to publish during FY 2027", holds the final AI-enabled device software functions guidance, the final predetermined change control plans guidance, and a draft on generative-AI conversational devices for mental disorders. Comments on the list close 30 November.

**Move.** Three of this week's upgrades changed when a human is asked. Under a final change-control guidance that is a change to describe in advance: write the protocol now, with pinned versions, the tests that must pass before a pin moves, and who signs.

### A national trial platform will "create an agentic operations layer", and names no provenance format

*Hhs · Arpa-H · Surpass*

Launched 30 September. The layer is to automate trial startup, onboarding of new treatment arms and "data collection, cleaning, and dataset construction"; a companion project is to "enable access to regulatory-grade data". No funding figure is given, and nothing says what record shows which values an agent changed and on whose authority.

**Move.** An agent that cleans trial data writes to a record a regulator reads. If you bid, bring the provenance record with the proposal, before the platform defines a log without one.

Every dated source for this week is in the long-form edition. The cumulative Radar was not refreshed this week. [Open the Radar](https://zkumar.github.io/ai-velocity-weekly/index.html)

> **Architect signal.** A regulator scheduled the guidance on change and a funder scheduled the agents. Framework releases are the changes that guidance will expect you to have planned for.

---

Full mechanism, code and sources for every card are in the long-form edition. The architect's position on this week's decision is in My Take. The code runs from a clean virtual environment with no API key. Everything is at https://github.com/zkumar/ai-velocity-weekly .
