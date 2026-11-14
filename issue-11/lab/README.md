# AI Velocity Weekly 11: lab

Week ending 13 November 2026. One mechanism in two parts and one supporting check, each run on
the release before this week's window and on the releases in it, plus the model table. No API
key is read or needed: the "model" is a `FunctionModel` with a scripted reply in the pydantic-ai
scripts and there is no model at all in the LangGraph script; the "EHR integration" is a function
that appends a row to a list; the "clinician" is a task that answers fifty milliseconds later.
Synthetic data only.

```
./run_all.sh
```

`run_all.sh` creates three virtual environments (`.venv-prev` from `requirements-previous.txt`,
`.venv-mid` from `requirements-2.67.0.txt`, `.venv` from `requirements.txt`) and runs every script
on every environment that has the package it needs. Python 3.11 or later; the output below is from
Python 3.13 on Linux, run on 13 November 2026 from clean environments, twice, with byte-identical
output (the one LangGraph task id that differs per run is masked by the script).

| Pinned | previous | fix | this week |
|---|---|---|---|
| pydantic-ai-slim | 2.66.0 (4 Nov, 10:28 UTC) | 2.67.0 (11 Nov, 00:23 UTC) | 2.68.0 (12 Nov, 02:30 UTC) |
| langgraph | 1.2.20 (5 Nov, 02:20 UTC) | | 1.2.21 (12 Nov, 18:06 UTC) |
| langgraph-checkpoint | 4.3.1 | | 4.3.1 |

Dates are PyPI upload times. `langgraph-checkpoint` is pinned to the same version on both sides so
the only variable is `langgraph`.

## What the scripts demonstrate

### `test_pydantic_ai_external_approval.py` (mechanism of the week, part 1)

A discharge agent has one tool it does not execute itself. `discharge_patient` is an *external*
tool in pydantic-ai's sense: the run returns the call and the EHR integration carries it out. A
policy capability gates it by name: its `after_tool_validate` hook raises `ApprovalRequired` with
metadata (`policy`, `requested_by`) so that a clinician signs off before the discharge. The
scripted model asks for the discharge once. The script then does what an external executor does
with `DeferredToolRequests.calls`: it runs every call in it, appending one row per call to the
record. It never looks at `approvals`, because an external executor has no reason to.

| version | calls handed to the executor | approvals waiting | metadata keys | rows written |
|---|---|---|---|---|
| 2.66.0 | **1** | **0** | **0** | **1** |
| 2.67.0 | 0 (`UserError` before anything is handed out) | 0 | 0 | 0 |
| 2.68.0 | 0 (`UserError`) | 0 | 0 | 0 |

On 2.66.0 the gate fired and the write happened anyway. `ToolManager.validate_tool_call` turned the
hook's `ApprovalRequired` into a `_ValidationDeferral`, and `_tool_execution.py` routed every
deferral from an external tool into `deferred_calls['external']`, the plain list of calls for the
outside executor, dropping the approval and its metadata. Nothing in the output said that a gate
had been in the way; the executor saw an ordinary call and ran it. 2.67.0 (`#12958`) adds the check
quoted in the error above and a `_route_deferred_call()` that routes a deferral raised during
validation by its own type; the run stops before the call is handed out, and the message tells you
the construction that works: raise `CallDeferred(metadata=...)` and approve inside the executor.

Output, 2.66.0:

```
pydantic-ai 2.66.0
calls handed to the executor: 1   approvals waiting: 0   metadata keys: 0   rows written: 1
  record: DISCHARGED MRN-123 via discharge_patient (call call-1)
```

Output, 2.67.0 and 2.68.0 (identical apart from the version line):

```
pydantic-ai 2.67.0
UserError before anything was handed out: `ApprovalRequired` was raised while validating a call to external tool 'discharge_patient', but an external tool call is executed outside the agent run, so the run cannot approve it. Raise `CallDeferred` instead to pass `metadata` to the code that executes the call, and approve it there.
calls handed to the executor: 0   approvals waiting: 0   metadata keys: 0   rows written: 0
```

### `test_pydantic_ai_request_input.py` (mechanism of the week, part 2)

2.68.0 (`#12757`) moves the question inside the run. A ward agent asks the pharmacist a free-text
question (a tool that raises `CallDeferred(kind='question')`) and places an order (a tool with
`requires_approval=True`). A `RequestInput(ask=...)` capability receives both pending calls and a
resume token; `ask` prints them, hands the token to a task that answers fifty milliseconds later
and returns `None`, which means wait. The answer is a `DeferredToolResults` with `approvals`, the
pharmacist's typed answer as a `ToolReturn`, and `answered_by` naming who answered. A
`RedactPhi` capability's `after_tool_execute` hook counts how many times it saw the human's answer.
The script then counts where `answered_by` went: on the `DeferredToolResultsEvent`, and in the
message history. A second run sets `LAB_ANSWERER` to a name nobody authorised.

| version | pending requests | kinds | `answered_by` on the event | `answered_by` in history | redaction hook saw the answer | rows written |
|---|---|---|---|---|---|---|
| 2.66.0 | script stops: `RequestInput` does not exist | | | | | |
| 2.67.0 | script stops: `RequestInput` does not exist | | | | | |
| 2.68.0, `dr.okafor@hospital.example` | 2 | approval, question | 2 ids | **0** | 1 | 1 |
| 2.68.0, `anyone@example.invalid` | 2 | approval, question | 2 ids | **0** | 1 | 1 |

Three observations. The run suspends on a token and resumes with the answer, inside one `agent.run`
call, so the approval no longer has to be reconstructed by a second run with `deferred_tool_results`.
Who answered is carried on the event stream and accepted as given: the docstring on
`DeferredToolResults.answered_by` reads "Pydantic AI doesn't check it, so authorize whoever answers
before you record who they are", and the second run shows that any string is taken; it is also "not
yet recorded in the message history", which the zero in the table confirms, so a transcript-based
audit does not see it. And the pharmacist's typed answer passed through the result guard exactly as a
tool return would (`MRN 123` became `MRN ***` in the history), which is the part of the design to
copy.

Output, 2.68.0, first run:

```
pydantic-ai 2.68.0
  event DeferredToolRequestsEvent: approvals=['place_order'] questions=['ask_pharmacist']
  pending: place_order kind=approval
  pending: ask_pharmacist kind=question
  resume token handed out (43 chars); the run is now waiting
  event DeferredToolResultsEvent: answered_by=['dr.okafor@hospital.example']
  history tool-return place_order: 'order placed: apixaban 5 mg bd for MRN-123'
  history tool-return ask_pharmacist: 'Yes, go ahead. Patient is MRN ***.'
answered by 'dr.okafor@hospital.example': accepted without a check, 2 ids on the event, 0 mentions in message history; redaction guard saw the human's answer 1 time(s); rows written: 1
```

The second run differs only in the two `answered_by` lines, which read `anyone@example.invalid`.
On 2.66.0 and 2.67.0 the script prints `not available on this release: ImportError: cannot import
name 'RequestInput' from 'pydantic_ai.capabilities'` and exits 0.

Note that `wait_for_external_event` waits in the current process by default. In a durable run on
an engine that does not record the wait (the module names Temporal, DBOS and Prefect) the wait is
refused, because "a replay would ask again, could get a different answer than the one the run
already acted on". This lab runs in process.

### `test_langgraph_subgraph_state.py` (supporting check)

A parent graph's node invokes a child graph it looks up from a dictionary at runtime, the way a
`task` tool invokes a sub-agent, so LangGraph cannot see the child as a declared subgraph. The child
checkpoints under its own namespace on the same thread. The parent then calls `get_state`,
`get_state_history` and `update_state` with that namespace.

| version | declared subgraphs | `get_state(child ns)` | snapshots in history | child-only key visible | `update_state(child ns)` |
|---|---|---|---|---|---|
| 1.2.20 | none | `ValueError: Subgraph task not found` | 0 | | `ValueError` |
| 1.2.21 | none | returns the child's values | 3 | **no** | `ValueError` |

On 1.2.21 the parent can read the record of a child it never declared, which is what deepagents
0.7.36 relies on when it writes the child's `checkpoint_ns` onto the `task` tool message. The read
uses the parent's channels: `pharmacist_note`, a key only the child's state has, is absent from the
snapshot, and writing into the child's state is still refused.

```
langgraph 1.2.20
declared subgraphs: []
checkpoint namespaces on the thread: ['', 'task:<task id>']
get_state(child ns) raised ValueError: Subgraph task not found
update_state(child ns) raised ValueError: Subgraph task not found
child record readable from the parent: 0   snapshots: 0
langgraph 1.2.21
declared subgraphs: []
checkpoint namespaces on the thread: ['', 'task:<task id>']
get_state(child ns): values={'messages': ['start apixaban', 'pharmacist agent: interaction checked']}  ('pharmacist_note' present: False)
get_state_history(child ns): 3 snapshots
update_state(child ns) raised ValueError: Subgraph task not found
child record readable from the parent: 1   snapshots: 3
```

### `build_models.py`

Regenerates `models.json` from the prices in section 2 of the issue (vendor list prices read on
13 November 2026) and prints the table: 19 rows, `cost_10k_docs_no_cache = 40 × in + 5 × out`,
`cost_10k_docs_80pct_cached = 8 × in + 32 × cached + 5 × out`. Two new rows this week, Claude
Fable 5.2 and Gemini 4 Hydrogen; one row changed price on paper, Gemini 4 Carbon, now on Google's
page at 2/10/0.10 until 30 November; one row unverified, gpt-oss-120b on Nebius, whose catalogue
returned 403. Change the workload constants in `cost()` to your own document mix.

## Files

- `test_pydantic_ai_external_approval.py`, `test_pydantic_ai_request_input.py`: the mechanism.
- `test_langgraph_subgraph_state.py`: the supporting check.
- `build_models.py`, `models.json`: the model table.
- `requirements-previous.txt`, `requirements-2.67.0.txt`, `requirements.txt`, `run_all.sh`.

MIT, like every lab in this repository. Synthetic data only; nothing writes to a FHIR server.
