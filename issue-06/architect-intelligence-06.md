# Architect Intelligence 06: While It Waits

Week Of Oct 3–9, 2026 · Vijay Zharotia

**Last week the yes travelled between agents and stores. This week the pause itself was the problem: a thread kept listing an answered question as open, one pharmacist's approval became three signatures, and a hold was written before the question sent with it was answered.**

Issue 05 followed the yes to the agent it belongs to and the store it waits in. This week the waiting itself: a run that has asked a person and not yet heard back is neither working nor done, and five frameworks changed what that state reports, what it has already done, and what the caller is told afterwards.

This week: 40 releases read from notes and wheels, 5 mechanisms executed, 10 papers read, 14 models priced.

## Five changes, one home each

Each fact appears once below. This list says where.

1. **An answered approval stayed in the inbox and its gate signed on every later resume** (Langgraph 1.2.13, executed), section 08
2. **A write that shares a response with a question for a human now runs before the answer** (Agent Framework 1.21.0, executed), section 04
3. **The approved tool runs once, then the resume throws on its turn budget** (Openai Agents Sdk Js 0.20.0, executed), section 04
4. **A timeout is reported for a write that committed** (Fastmcp 4.1.0, executed), section 05
5. **A wrapper that answers from cache leaves no audit row** (Pydantic-Ai 2.54.0, executed), section 05

## The Write That Went First, the Tool That Ran and Threw, the Stamp

Two executed with scripted clients, one read from the changelog and the installed wheel. The LangGraph gate is executed on slide 08.

### A question for the clinician and a medication hold in one response, and the hold is written first

*Microsoft · Agent Framework 1.21.0* · executed

PR #9050. A model response carrying a host-answered tool and a local write used to pause as a whole and the write never ran. On 1.21.0 the batch is split. Without a session the hold was in the record before the clinician saw the question. With a session it waited under deferred_function_calls, then ran after the clinician answered "No. Do not hold".

**What changed.** The human no longer sees the write as a request. A session orders it after the answer; nothing makes it depend on the answer.

**What to change.** Pass a session on every path, and never let a write that depends on a clinician's reply share a response with the question. Put it in a later turn behind its own approval.

[Read the mechanism](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-06/lab)

### Approved, executed once, then MaxTurnsExceededError with no hint that a write happened

*Openai · Agents Sdk For Javascript 0.19.0 And 0.20.0* · executed

#2032 in 0.20.0 counts the model call after an approval resume against maxTurns: with a budget of 1 the discharge tool ran, then the resume threw. 0.19.0, read from the changelog, moves RunState to schema 1.21, re-evaluates the approval policy on a durable resume instead of trusting the stored decision, and rejects checkpoints without a guardrail marker, which is every older snapshot past turn zero.

**What changed.** "The tool ran and the run failed" is an ordinary outcome of a tight budget, and some paused runs from before the upgrade will not restore.

**What to change.** Catch the turn-budget exception on resume and reconcile against the record before reporting failure. Count the paused runs you hold before upgrading past 0.19.0.

[Read the mechanism](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-06/lab)

### An HMAC stamp on every function call, verified before the tool runs, except for workflow nodes

*Google · Adk 2.11.0 And Adk-Js 2.2.1* · docs

ToolCallIntegrityPlugin(secret_key, allow_unstamped_calls=False) stamps each call into custom_metadata over app, user, session, invocation, branch, author, name, id and arguments; before_tool_callback refuses any call without a valid stamp with ToolCallIntegrityError. Tools run as workflow nodes are not checked. A call aborted through the new abort_signal is sealed with error_code INVOCATION_ABORTED and not replayed on resume.

**What changed.** The call that runs is provably the call the model emitted, under a key you hold. It does not sign what the reviewer saw, and the confirmation flow lives in the nodes it skips.

**What to change.** Turn it on, keep the key out of session state, store the stamp in the approval row, and cover workflow-node tools yourself.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-06/details.html)

> **Architect signal.** Ordering is not consent. A framework can promise that the write runs after the answer; whether the answer permits it is still a decision only your gate records.

## An Error With a Row Behind It, and an Audit Hook a Cache Can Skip

Two executed, one read from a wheel diff. In each the report and the event came apart.

### is_error=True, "timed out after 0.2s", and one order in the record

*Fastmcp 4.1.0* · executed

PR #5379. A synchronous tool with timeout=0.2 took one second and wrote an order. 4.0.11 returned success and "ORDER PLACED". 4.1.0 rejects the late result and returns an error. The row was written on both. The same release expires idle HTTP sessions after 30 minutes by default (#5229) and re-scopes MultiAuth client ids, so tasks pending across the upgrade change owner (#5455).

**What changed.** The timeout is now honoured in the report and not in the world, and an agent that sees an error retries.

**What to change.** Treat a timeout on a write tool as outcome unknown and look the write up by idempotency key before any retry. Set the idle timeout above your longest human approval.

[Read the mechanism](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-06/lab)

### before and after hooks moved inside the wrapper, and a cache hit ran neither

*Pydantic-Ai 2.54.0* · executed

PR #7053. An audit capability counted requests in before_model_request and after_model_request and also wrapped the request. When the wrapper answered from a cache without calling the handler, 2.53.0 still ran both hooks; 2.54.0 ran neither, and the pull request says a skipped provider call records no usage and no span attributes. 2.53.0 also carries GHSA-6fqq-452j-qhrp, a concurrency-slot leak on streamed requests from 2.10.0.

**What changed.** A cache or a guard written as a wrapper now removes whatever the inner hooks were doing, including redaction and authorisation.

**What to change.** Put mandatory checks in the outermost wrapper or outside the agent, and add a test that a short-circuited request still writes the audit row.

[Read the mechanism](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-06/lab)

### The summariser overflows, retries once with the middle omitted, and logs it at DEBUG

*Langchain 1.4.4* · docs

PR #41159, read from the wheel. SummarizationMiddleware used to re-send the same prompt three times after a ContextOverflowError. It now retries once with the head and tail and the marker "[... middle of conversation omitted ...]", budgeted at half the tokens and capped at 40% of max_input_tokens. langchain-core 1.6.8 (#41151) also hardens the SSRF policy for IPv6-mapped localhost and metadata addresses under a relaxed policy.

**What changed.** A summary can be missing the middle of a chart review with nothing at the default log level to say so.

**What to change.** Raise that logger for clinical agents, or wrap the middleware and record when the fallback fired beside the summary it produced.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-06/details.html)

> **Architect signal.** Error, timeout and exception are statements about the call. None is a statement about the record, and a retry policy that reads them as one writes the second row.

## A Price Cliff at 100,000 Tokens and Two $130 Rows Now Identical

4,000 input and 500 output tokens per document, list prices read 9 October. Artificial Analysis is still v4.3.2; its healthcare index page did not load, so no medical score is quoted this week.

### Haiku 5.5 does the workload for $6.50 and reads 43, until the prompt passes 100,000 tokens

*Anthropic · Claude Haiku 5.5, New 7 Oct*

$0.10 in, $0.50 out, $0.01 cached: the same as GPT-6 Luna to the cent, and five index points above it. A request whose prompt exceeds 100,000 tokens pays 0.50, 2.50 and 0.05 on the whole request, cache hits included, so the same token volume costs $32.50. Anthropic's "90% cheaper than Haiku 4.5"* matches the list prices; its 39.2% on Terminal-Bench 4.0* is its own.

**What changed.** The cheapest tier now has a price cliff set by prompt length, and long-context chart review sits on the wrong side of it.

**What to change.** Measure your prompt-length distribution before you budget, and route requests over the threshold deliberately.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-06/details.html)

### Sonnet 5.5's cache read halved to $0.10, so the two $130 rows match in both columns

*Anthropic · Claude Sonnet 5.5 And Openai · Gpt-6.1 Sol*

Sonnet 5.5, released 28 September, had its cache read cut from $0.20 to $0.10 on 7 October, matching GPT-6.1 Sol: $130 uncached and $69.20 with 80% of input cached for both. They read 56 and 52; Opus 5.5 is 58 at $260. gpt-6-sol, released 22 September, has already left OpenAI's price page. Mistral Large 4 arrived in preview at list $75.30 and a two-week half price; Kimi K3 enters the table at $195 and 44.

**What changed.** The second tier sits two index points under the first at half the price, and a three-week-old model id is already gone from the price list.

**What to change.** Record the model id, the date read and the cache rate in the validation file, and re-run validation when you move tiers.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-06/details.html)

> **Architect signal.** A price that depends on prompt length makes context size a cost decision per request. The router that decides it needs the same audit as the model it routes to.

## The Altered Call, the Gate That Refused Everything, the Payer Benchmark

Three results on the distance between the call the model wrote and the call that ran. Numbers are the authors' own, from the abstracts.

### 12% of shell calls carrying code or escapes were altered on the way to execution, 80.7% of those ran the wrong action silently

*Intent-Execution Correspondence · 2610.04375*

47,828 production shell calls. One agent's shell tool altered 12.0% of calls that carried code, escapes or long text; 80.7% of the calls altered by backslash handling ran the wrong action with no error. All ten harnesses tested altered at least one call. The authors' repair recovers 79.2%, measured on their own product*.

**What changed.** The transcript records what the model emitted. What executed can differ, and nothing raises.

**What to change.** Log the call as received at every hop, model, harness, wrapper and tool, and diff the hops.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-06/details.html)

### Policy compiled into gates cut violations from 66.3% to 2.6%, and one development gate refused 95.9% of valid calls

*Nomos · 2610.11030*

Natural-language policy compiled into deterministic tool-call gates on two agent benchmarks; violations among state-changing calls fell from 66.3% to 2.6% in one domain and 30.8% to 6.9% in another. A development binding wrongly refused almost every valid call until the gates were replayed over past transcripts.

**What changed.** Policy enforcement outside the model works, and an untested gate fails in the direction that looks safe.

**What to change.** Replay every new gate over recorded traffic before it ships, and report false refusals beside violations.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-06/details.html)

### 87 MCP tools, 20 simulated healthcare apps, and the best configuration resolves 28% of prior-auth and UM tasks

*Chi-Bench · 2605.16679, V3 30 Sept*

Prior authorisation, utilisation management and care management with a 1,290-document handbook. No configuration of 30 clears 20% when a task must pass three times in three, and running all tasks in one session drops the best to 3.8%. A separate Northwestern study (2610.05778) attributes about a quarter of outcome variance to the harness and its interaction with the model.

**What changed.** A long-horizon payer benchmark exists, and session reuse is its single largest failure factor.

**What to change.** One case per session, gate on pass-every-repeat, and re-validate when the harness changes, not only when the model does.

[Read the mechanism](https://zkumar.github.io/ai-velocity-weekly/issue-06/details.html)

> **Architect signal.** Five harness releases in one week each changed what a paused run does. A validation result belongs to a model and a harness version together, and this week the harness half expired.

## Mechanism of the week: The answered question that stayed open

*Langgraph 1.2.13 · No Model, 1.2.12 Against 1.2.13, Sqlite Checkpointer For The Upgrade Run*

Two parallel approval gates, pharmacy and physician; each calls interrupt(), signs the order and returns no state. The pharmacist answers by id. On 1.2.12 the thread still listed both questions, a second reviewer's rejection was accepted and discarded, and the pharmacy gate signed again on that resume and again when the physician answered. On 1.2.13 one question remained and each gate ran once. A thread paused on 1.2.12 and opened on 1.2.13 signed twice. Gates returning a state key wrote two rows on both.

**4 → 2** signature rows for 2 approvals, 1.2.12 to 1.2.13 · **2 → 1** inbox items after one of two answers · **3** rows when a thread paused before the upgrade finished after it

**What changed.** PR #9103 gives the paused thread one reader of task status and marks a finished gate with no output as finished. Its docstring says older writes "read as unfinished" and the executor "runs them again". A resume addressed to an already-answered interrupt id is still accepted silently on both versions.

**Move.** Build the inbox from your own table of asked and answered interrupt ids and refuse a second answer yourself. Give every gate an idempotency key before upgrading, and drain paused threads first. Search the record for duplicate writes from any node that follows an interrupt and returns nothing. test_lg_pending_interrupts.py runs all of it in seconds.

[Open the lab package](https://github.com/zkumar/ai-velocity-weekly/tree/main/issue-06/lab)

> **Architect signal.** A fix that changes how a checkpoint is read does not rewrite the checkpoints already stored. Every approval in flight on upgrade day runs on the old rules.

## What the architects shipped

- **Astp/Onc And Medstar.** A 2026 LEAP in Health IT award for open-source agent middleware titled "Sovereign Execution: Vigilant, Gated and Verifiable Agentic Care": durable long-running processes, patient-gated data pods on the Solid protocol, tamper-evident certificates for AI routing. Two awards, $1.5M in total; no FHIR or MCP binding named.
- **Openai.** In-product BAA acceptance and a HIPAA compliance setting under organisation settings (5 Oct), a Decisions API beta on gpt-6-luna (6 Oct), and a builder's guide to GPT-6 covering effort, cache-friendly prompt order, compaction and cost per successful task; its numbers are OpenAI's and its customers'*.
- **Anthropic.** A Usage Policy effective 12 November that keeps a qualified human in the loop and AI disclosure for health-affecting uses; Managed Agents web_fetch restricted to URLs already seen in the session, with allowed_hosts on both web tools; SDK 1.12.0 browser and computer toolsets gated by a confirm callable that declines on any exception.
- **Anaconda.** Anaconda MCP at general availability, remote and read-only with four tools, with advice to remove the beta local package; and a guide to indirect prompt injection that puts human approval at an MCP gateway. The 73% figure for vulnerable MCP servers comes from a company Anaconda owns*. Read from the blog; the emailed edition could not be opened.
- **Hl7 And Arpa-H.** HL7's 2026 AI Challenge winners from 73 submissions, an MCP server for health information exchange among them, with showcases on 14 and 28 October; no Da Vinci, US Core or CDS Hooks publication in window. ARPA-H's SURPASS solicitation (30 Sept) asks for an "agentic operations layer" for trial start-up and dataset construction, summaries due 30 November.

Nothing in window from Epic, FDA on AI, OCR, the MCP specification, Moonshot or NVIDIA beyond a startup profile. Mistral Large 4 and Matt Pocock's Skills v1.3 are in the long-form edition. Nebius announced the Inferize acquisition on 1 October with no user-facing change. The editor's newsletter inbox was not readable this run; the vendors' public pages were read instead.

> **Architect signal.** A federal grant title now reads gated and verifiable. When funders adopt the vocabulary, the reference implementation they pay for becomes what an auditor expects to see.

## A Rule With File Formats and a Deadline With No New Notice

### Transparency in Coverage is final: one rate file per provider network, two new files, an attestation and a named official on each

*Cms, Treasury, Labor · Cms-9882-F, 91 Fr 63748, Effective 7 Dec*

Published 6 October. In-network files move to one per provider network; taxonomy and utilisation files are new; cadence goes from monthly to quarterly; each file carries an attestation and a named senior official. CMS intends to specify JSON in later guidance; no schema is published. No AI, FHIR or prior-authorisation content.

**Move.** If an agent assembles or checks these files, the attestation makes its output a signed statement. Decide now who reviews it and what evidence of that review you keep.

### Twelve weeks to the prior authorisation APIs with no new notice, and two dates for agents that act on records

*Cms-0057-F · Arpa-H Surpass Sol-26-164 · Fda-2026-N-7874*

The CMS-0057-F page, modified 8 October, still says API requirements are due "primarily" 1 January 2027; the February 2024 enforcement discretion is the only posted notice. ARPA-H wants solution summaries for an agentic trial-operations layer by 30 November. FDA's generative-AI device discussion paper takes comments until 19 October and FDA published nothing on AI in window.

**Move.** Freeze the agent framework versions behind your prior authorisation API before January, with this week's upgrade notes read. If you propose to ARPA-H, specify the evidence the operations layer leaves.

Every dated source for this week is in the long-form edition. The cumulative Radar was not refreshed this week. [Open the Radar](https://zkumar.github.io/ai-velocity-weekly/index.html)

> **Architect signal.** A compliance date twelve weeks out turns every framework upgrade between now and then into a change to a regulated interface. Schedule them, or stop taking them.

---

Full mechanism, code and sources for every card are in the long-form edition. The architect's position on this week's decision is in My Take. The code runs from a clean virtual environment with no API key. Everything is at https://github.com/zkumar/ai-velocity-weekly .
