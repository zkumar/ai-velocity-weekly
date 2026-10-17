# AI Velocity Weekly 06: lab

Week ending 9 October 2026. Five mechanisms, each run on the release before this week's and on
this week's, plus the model table. No API key is read or needed: every model is a scripted stub
and every "record" is an in-memory list or a local sqlite file. Synthetic data only.

```
./run_all.sh
```

`run_all.sh` creates two virtual environments (`.venv-prev` from `requirements-previous.txt`,
`.venv` from `requirements.txt`), and two small Node folders for the one JavaScript script
(skipped if `node` is not installed). First run takes a few minutes for the installs; the
scripts themselves finish in seconds. Python 3.11 or later; the output below is from Python 3.13.16
and Node 22.22.0 on Linux, run on 9 October 2026 from clean environments.

| Pinned | previous | this week |
|---|---|---|
| langgraph | 1.2.12 | 1.2.13 |
| agent-framework-core | 1.20.0 | 1.21.0 |
| fastmcp | 4.0.11 | 4.1.0 |
| pydantic-ai-slim | 2.53.0 | 2.54.0 |
| @openai/agents-core | 0.19.0 | 0.20.0 |

langgraph-checkpoint-sqlite 3.1.1 is the same on both sides; it had no release this week.

## What each script demonstrates

### 1. `test_lg_pending_interrupts.py` (mechanism of the week)

A discharge packet with two parallel approval gates, pharmacy and physician. Each gate calls
`interrupt()`, then writes one signature row to an external record and returns no state update.
The pharmacist answers by interrupt id. The script then reads the approval inbox from
`get_state(cfg).interrupts`, answers the already-answered item a second time, lets the physician
answer, and counts signature rows.

What it printed:

- **1.2.12.** After one of two answers the inbox still listed both questions. The second answer to
  the pharmacy item ("REJECT by rph-9") was accepted without error, the pharmacy gate ran again
  with the first answer, and it ran once more when the physician answered. Two approvals,
  **four signature rows**, three of them the pharmacy's.
- **1.2.13.** The inbox listed one question. The second answer was accepted without error and
  changed nothing. Two approvals, **two rows**.
- **Control** (`LAB_GATE_OUTPUT=1`, each gate also returns a state key). Two rows on both
  versions. The stale inbox item on 1.2.12 remains; the repeated execution does not. The repeat
  needs a gate that finishes without writing state.
- **Upgrade in flight.** A thread paused and half-answered on 1.2.12 (sqlite checkpointer), then
  opened by a second process on 1.2.13: the inbox listed the pharmacy question again, `next`
  held both nodes, and when the physician answered the pharmacy signature was written a second
  time. **Three rows**, one stamped 1.2.12 and two stamped 1.2.13. Finishing the same thread on
  1.2.12 also gave three. The same thread shape created on 1.2.13 gave two.

Source for the cause: the docstring of `langgraph/pregel/_task_status.py`, new in 1.2.13 (PR #9103).

### 2. `test_af_mixed_batch.py`

One scripted model response carries two calls: `ask_clinician`, a declaration-only tool the host
answers, and `hold_medication`, a local write. Run with and without an `AgentSession`, then the
clinician answers "No. Do not hold".

- **1.20.0.** Both calls were surfaced as user-input requests and the write never ran, with or
  without a session.
- **1.21.0, no session.** Only the question was surfaced, and the hold was **already written**
  before the clinician answered.
- **1.21.0, with a session.** Zero writes while the question was open; **one write after the
  answer**, although the answer was no. The session orders the write after the answer. It does
  not make the write depend on it.

The final text "Lisinopril held." is the scripted model's line in every run and says nothing
about any real model.

### 3. `test_fm_late_result.py`

A synchronous MCP tool with `timeout=0.2` sleeps one second, writes an order, and returns.

- **4.0.11.** The caller was told `is_error=False`, "ORDER PLACED". One row.
- **4.1.0.** The caller was told `is_error=True`, "execution timed out after 0.2s". One row.

The write happened on both. What changed is what the caller is told about it.

### 4. `test_pai_wrap_hooks.py`

A capability counts model requests in `before_model_request` and `after_model_request` and also
wraps the request. Second run: the wrapper answers from a cache and never calls the handler.

- **2.53.0.** Order `before, wrap-enter, MODEL, wrap-exit, after`. With the cache hit the two
  audit hooks still ran: 2 audit rows.
- **2.54.0.** Order `wrap-enter, before, MODEL, after, wrap-exit`. With the cache hit the audit
  hooks did not run: **0 audit rows** for an answer the caller received.

### 5. `test_oa_maxturns_after_approval.mjs`

A discharge tool that needs approval. The run pauses, is serialised with `RunState.toString()`,
restored, approved, and resumed with `maxTurns: 1`.

- **0.19.0.** The tool ran once, the model was called again, the caller got "Discharge signed."
- **0.20.0.** The tool ran once, then `MaxTurnsExceededError: Max turns (1) exceeded`. One write
  in the record and an exception in the caller.

### 6. `build_models.py` and `models.json`

The section 2 table: 14 models priced on 10,000 documents at 4,000 input and 500 output tokens,
with and without 80% of input served from cache. Each row carries its source URL, whether the
price was read on the vendor's own page, and whether the cache rate was carried from an earlier
read. One row (Gemini 4 Argon) is UNVERIFIED and marked so.

## Change one thing

1. In script 1, add an idempotency key to `sign()` (who plus thread id) and re-run on 1.2.12.
   The count drops to two and the inbox is still wrong; they are separate problems.
2. In script 2, give `hold_medication` an approval requirement of its own and see which of the
   two questions reaches the human first on 1.21.0.
3. In script 3, make `place_order` async and compare what each version does with the write.

## Full output, 9 October 2026

```
=== 1 langgraph: what the paused thread says is still waiting (mechanism of the week) ===
langgraph 1.2.12 | phase inbox | gates return nothing
  paused: inbox=['pharmacy', 'physician'] next=('pharmacy', 'physician') record=[]
  pharmacist answered by id: inbox=['pharmacy', 'physician'] next=('physician',) record=[('pharmacy', 'approve by rph-7')]
    answered question still listed as pending: True
    second answer to the answered item: accepted
    after it: inbox=['pharmacy', 'physician'] next=('physician',) record=[('pharmacy', 'approve by rph-7'), ('pharmacy', 'approve by rph-7')]
    physician answers by id: accepted
  end: inbox=[] next=()
  record rows: 4 -> [('pharmacy', 'approve by rph-7'), ('pharmacy', 'approve by rph-7'), ('pharmacy', 'approve by rph-7'), ('physician', 'approve by md-3')]
  SUMMARY 1.2.12 inbox: after one of two answers the inbox listed 2 item(s); record holds 4 signature row(s) for 2 approvals
langgraph 1.2.13 | phase inbox | gates return nothing
  paused: inbox=['pharmacy', 'physician'] next=('pharmacy', 'physician') record=[]
  pharmacist answered by id: inbox=['physician'] next=('physician',) record=[('pharmacy', 'approve by rph-7')]
    answered question still listed as pending: False
    second answer to the answered item: accepted
    after it: inbox=['physician'] next=('physician',) record=[('pharmacy', 'approve by rph-7')]
    physician answers by id: accepted
  end: inbox=[] next=()
  record rows: 2 -> [('pharmacy', 'approve by rph-7'), ('physician', 'approve by md-3')]
  SUMMARY 1.2.13 inbox: after one of two answers the inbox listed 1 item(s); record holds 2 signature row(s) for 2 approvals
--- control: the same gates, each returning a state update ---
  SUMMARY 1.2.12 inbox: after one of two answers the inbox listed 2 item(s); record holds 2 signature row(s) for 2 approvals
  SUMMARY 1.2.13 inbox: after one of two answers the inbox listed 1 item(s); record holds 2 signature row(s) for 2 approvals
--- a thread paused and half-answered on 1.2.12, then opened after the upgrade ---
langgraph 1.2.12 | phase legacy-pause | gates return nothing
  paused and pharmacist answered on 1.2.12: inbox=['pharmacy', 'physician'] next=('physician',)
  record rows: [('pharmacy', 'approve by rph-7', '1.2.12')]
langgraph 1.2.13 | phase legacy-read | gates return nothing
  opened on 1.2.13: inbox=['pharmacy', 'physician'] next=('pharmacy', 'physician') record rows=1
    physician answers by id: accepted
  end: inbox=[] next=()
    record: ('pharmacy', 'approve by rph-7', '1.2.12')
    record: ('pharmacy', 'approve by rph-7', '1.2.13')
    record: ('physician', 'approve by md-3', '1.2.13')
  SUMMARY legacy thread read on 1.2.13: pharmacy signature rows=2, total rows=3, thread finished=True
--- the same half-answered thread finished on 1.2.12 ---
  record rows: [('pharmacy', 'approve by rph-7', '1.2.12')]
  SUMMARY legacy thread read on 1.2.12: pharmacy signature rows=2, total rows=3, thread finished=True
--- the same thread shape created and finished on 1.2.13 ---
langgraph 1.2.13 | phase legacy-pause | gates return nothing
  paused and pharmacist answered on 1.2.13: inbox=['physician'] next=('physician',)
  record rows: [('pharmacy', 'approve by rph-7', '1.2.13')]
langgraph 1.2.13 | phase legacy-read | gates return nothing
  opened on 1.2.13: inbox=['physician'] next=('physician',) record rows=1
    physician answers by id: accepted
  end: inbox=[] next=()
    record: ('pharmacy', 'approve by rph-7', '1.2.13')
    record: ('physician', 'approve by md-3', '1.2.13')
  SUMMARY legacy thread read on 1.2.13: pharmacy signature rows=1, total rows=2, thread finished=True

=== 2 agent-framework-core: a question for a human and a write in one response ===
agent-framework-core 1.20.0
  no session      : shown to the human=[('ask_clinician', 'c1'), ('hold_medication', 'c2')] | model calls=1 | writes before the human answers=0 []
  no session      : clinician answered 'No. Do not hold' -> model calls=2 | writes=0 | final='Lisinopril held.'
  with AgentSession: shown to the human=[('ask_clinician', 'c1'), ('hold_medication', 'c2')] | model calls=1 | writes before the human answers=0 []
  with AgentSession: clinician answered 'No. Do not hold' -> model calls=2 | writes=0 | final='Lisinopril held.'
agent-framework-core 1.21.0
  no session      : shown to the human=[('ask_clinician', 'c1')] | model calls=1 | writes before the human answers=1 [('pt-123', 'lisinopril')]
  no session      : clinician answered 'No. Do not hold' -> model calls=2 | writes=1 | final='Lisinopril held.'
  with AgentSession: shown to the human=[('ask_clinician', 'c1')] | model calls=1 | writes before the human answers=0 []
  with AgentSession: clinician answered 'No. Do not hold' -> model calls=2 | writes=1 | final='Lisinopril held.'

=== 3 fastmcp: a tool that finishes after its timeout ===
fastmcp 4.0.11: caller told after 1.1s: is_error=False content=['ORDER PLACED']
  rows in the record: 1 [('pt-123', 'BMP stat')]
  SUMMARY 4.0.11: caller sees success; the write ran 1 time(s)
fastmcp 4.1.0: caller told after 1.0s: is_error=True content=["Error calling tool 'place_order': Tool 'place_order' execution timed out after 0.2s"]
  rows in the record: 1 [('pt-123', 'BMP stat')]
  SUMMARY 4.1.0: caller sees error; the write ran 1 time(s)

=== 4 pydantic-ai-slim: audit hooks and a wrapper that short-circuits ===
pydantic-ai-slim 2.53.0
  wrapper calls the model  : ['audit:before', 'wrap:enter', 'MODEL', 'wrap:exit', 'audit:after'] | output='K+ 6.1 mmol/L is critical; hold lisinopril.'
  wrapper answers from cache: ['audit:before', 'wrap:enter', 'wrap:cache-hit', 'audit:after'] | output='(cached) hold lisinopril.'
  SUMMARY 2.53.0: audit hook rows, model called=2, wrapper short-circuit=2
pydantic-ai-slim 2.54.0
  wrapper calls the model  : ['wrap:enter', 'audit:before', 'MODEL', 'audit:after', 'wrap:exit'] | output='K+ 6.1 mmol/L is critical; hold lisinopril.'
  wrapper answers from cache: ['wrap:enter', 'wrap:cache-hit'] | output='(cached) hold lisinopril.'
  SUMMARY 2.54.0: audit hook rows, model called=2, wrapper short-circuit=0

=== 5 @openai/agents-core: the turn budget after an approval ===
@openai/agents-core 0.19.0
  paused: interruptions=1 model calls=1 writes=0
  approved and resumed with maxTurns 1: returned finalOutput="Discharge signed."
  model calls=2 writes=1 ["pt-123"]
  SUMMARY 0.19.0: approved tool ran 1 time(s); caller got a final answer
@openai/agents-core 0.20.0
  paused: interruptions=1 model calls=1 writes=0
  approved and resumed with maxTurns 1: threw MaxTurnsExceededError: Max turns (1) exceeded
  model calls=1 writes=1 ["pt-123"]
  SUMMARY 0.20.0: approved tool ran 1 time(s); caller got an exception

=== 6 model table ===
model                               in/out/cached   AA   no cache  80% cached  verified
Claude Haiku 5.5             0.1/0.5/  0.01   43 $     6.50       $3.62  True
GPT-6 Luna                   0.1/0.5/  0.01   38 $     6.50       $3.62  True
gpt-oss-120b on Nebius       0.15/0.6/   n/a   12 $     9.00         n/a  False
DeepSeek V4.1 Flash          0.3/1.2/ 0.006   39 $    18.00       $8.59  True
Gemini 3.8 Flash             0.75/3.75/ 0.075   41 $    48.75      $27.15  True
Mistral Large 4 (preview)    1.36/4.18/  0.14   38 $    75.30      $36.26  True
Grok 4.7                     2/6/   0.5   46 $   110.00      $62.00  True
Claude Sonnet 5.5            2/10/   0.1   56 $   130.00      $69.20  True
GPT-6.1 Sol                  2/10/   0.1   52 $   130.00      $69.20  True
Gemini 4 Argon               2/10/   n/a   53 $   130.00         n/a  False
Kimi K3                      3/15/   0.3   44 $   195.00     $108.60  True
Claude Opus 5.5              4/20/   0.2   58 $   260.00     $138.40  True
GPT-6 Astra                  10/50/     1   53 $   650.00     $362.00  True
Claude Fable 5.1             10/50/  0.25   53 $   650.00     $338.00  True
```
