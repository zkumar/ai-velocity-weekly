# AI Velocity Weekly 07: lab

Week ending 16 October 2026. One mechanism, run on the release before this week's window and on
the release that opened it, in two tool-execution modes and two failure cases, plus the model
table. No API key is read or needed: the model is pydantic-ai's `FunctionModel` with a scripted
function, and the "record" is an in-memory list. Synthetic data only.

```
./run_all.sh
```

`run_all.sh` creates two virtual environments (`.venv-prev` from `requirements-previous.txt`,
`.venv` from `requirements.txt`) and runs the script eight times. The installs take a minute or
two; the runs finish in seconds. Python 3.11 or later; the output below is from Python 3.13.16 on
Linux, run on 16 October 2026 from clean environments, twice, with identical output.

| Pinned | previous | this week |
|---|---|---|
| pydantic-ai-slim | 2.54.0 | 2.55.0 |

2.55.0 was uploaded to PyPI on 9 October at 19:40 UTC. 2.56.0 (13 October) and 2.57.0 (16 October)
followed inside the window; neither touches `_tool_execution.py`'s cancellation handlers, so the
pin stays on the release that carries the change.

## What the script demonstrates

### `test_pai_sibling_failure.py` (mechanism of the week)

One scripted model response carries two tool calls for the same patient. `lookup_allergies` is
emitted first; it sleeps 300 ms and raises, because the allergy service is down. `place_order` is
emitted second; it appends one row to the order record and returns `ORDER PLACED order-1 ...`.
pydantic-ai runs both in parallel, the order is written in a few milliseconds, and since 2.54.0
(PR #9434) an unexpected exception in a tool ends the run and cancels its siblings, so `agent.run()`
raises. The script then does what a durable executor or an approval service does after an error:
it keeps the message history it captured and starts a new run from it. The scripted model reads
what that history says about `place_order`. If it says the order was placed, the model answers in
text. If it says the call was interrupted before a result was produced, the model orders again,
which is what a real model does with that sentence.

Two modes. `parallel_ordered_events` runs the calls in parallel and emits their events in order
once every call is done; the pull request that fixed this notes DBOS durable runs use it by
default. `parallel` is pydantic-ai's default. Two cases. In the first the sibling raises. In the
second the caller gives up: `asyncio.wait_for(..., timeout=0.1)` cancels the run while the allergy
lookup is still running and after the order has been written.

What it printed, with the record counted after each run:

| mode | case | version | rows after run 1 | history after run 1 | what the model was told at run 2 | rows after run 2 |
|---|---|---|---|---|---|---|
| parallel_ordered_events | sibling raises | 2.54.0 | 1 | no tool returns | both calls "interrupted before a result was produced" | **2** |
| parallel_ordered_events | sibling raises | 2.55.0 | 1 | `return[place_order]='ORDER PLACED order-1 ...'` | order placed; lookup interrupted | 1 |
| parallel_ordered_events | caller cancels | 2.54.0 | 1 | no tool returns | both calls interrupted | **2** |
| parallel_ordered_events | caller cancels | 2.55.0 | 1 | order placed | order placed; lookup interrupted | 1 |
| parallel | sibling raises | 2.54.0 | 1 | order placed | order placed; lookup interrupted | 1 |
| parallel | sibling raises | 2.55.0 | 1 | order placed | order placed; lookup interrupted | 1 |
| parallel | caller cancels | 2.54.0 | 1 | order placed | order placed; lookup interrupted | 1 |
| parallel | caller cancels | 2.55.0 | 1 | order placed | order placed; lookup interrupted | 1 |

The two bold cells are the finding. On 2.54.0 under `parallel_ordered_events` the interrupted
`ModelRequest` carried no return for the write that had finished, the resume filled both calls in
with `The tool call was interrupted before a result was produced.`, the model placed the order
again, and the record held two apixaban orders for one patient. The final text was the scripted
line `Apixaban ordered; allergy check still pending.` in every one of the eight runs; it says
nothing about how many rows exist.

Source for the cause: pydantic-ai PR #10049, which closes issue #9942. The ordered mode settled a
segment only after every task was done, so an exception from index 0 propagated before index 1 was
recorded, and an external cancellation recorded nothing. 2.55.0 records every task that finished
successfully in both cancellation handlers, emits no event for them, and leaves the exception
unchanged.

What the script does not show: a model that reasons about the sentence rather than obeying it.
The scripted model orders again on seeing "interrupted" because that is the conservative reading
of a transcript with no result; a real model may or may not. The record is the only thing that
knows.

Full output of `./run_all.sh` is in the long-form edition, section 5.

### `build_models.py`

Regenerates `models.json` and prints the section 2 table: 14 models on 10,000 documents at 4,000
input and 500 output tokens, list prices read on 16 October from the pages named in each row,
Artificial Analysis Intelligence Index v4.3.2 scores, and the Healthcare & Medical Index for the
three rows whose score could be read from that page. Every price was read on a vendor's own page
this week; no cached rate is carried from an earlier issue.

```
model                               in/out/cached   AA  med   no cache  80% cached  verified
Claude Haiku 5.5             0.1/0.5/  0.01   43    - $     6.50       $3.62  True
GPT-6 Luna                   0.1/0.5/  0.01   38    - $     6.50       $3.62  True
gpt-oss-120b on Nebius       0.15/0.6/   n/a   12    - $     9.00         n/a  True
DeepSeek V4.1 Flash          0.3/1.2/ 0.006   39    - $    18.00       $8.59  True
Gemini 3.8 Flash             0.75/3.75/ 0.075   41    - $    48.75      $27.15  True
Mistral Large 4 (preview)    1.36/4.18/  0.14   38    - $    75.30      $36.26  True
Grok 4.7                     2/6/   0.5   46    - $   110.00      $62.00  True
Claude Sonnet 5.5            2/10/   0.1   56   58 $   130.00      $69.20  True
GPT-6.1 Sol                  2/10/   0.1   52    - $   130.00      $69.20  True
Gemini 4 Argon               2/10/   0.1   53    - $   130.00      $69.20  True
Kimi K3                      3/15/   0.3   44    - $   195.00     $108.60  True
Claude Opus 5.5              4/20/   0.2   58   61 $   260.00     $138.40  True
GPT-6 Astra                  10/50/     1   53    - $   650.00     $362.00  True
Claude Fable 5.1             10/50/  0.25   53   58 $   650.00     $338.00  True
```

## Files

- `test_pai_sibling_failure.py`: the mechanism. `LAB_MODE` selects the execution mode,
  `LAB_CANCEL=1` selects the cancellation case.
- `build_models.py`, `models.json`: the model table and its sources.
- `requirements.txt`, `requirements-previous.txt`: the two pins.
- `run_all.sh`: builds both environments and runs everything.

Synthetic data only. Nothing here talks to a FHIR server or to any model API.
