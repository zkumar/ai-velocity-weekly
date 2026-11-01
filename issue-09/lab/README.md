# AI Velocity Weekly 09: lab

Week ending 30 October 2026. One mechanism and one supporting check, each run on the release
before this week's window and on the release that opened it, plus the model table. No API key is
read or needed: the "model" is a scripted `ChatCompletionClientBase` subclass in the first script
and absent from the second, and the "record" is an in-memory list. Synthetic data only.

```
./run_all.sh
```

`run_all.sh` creates two virtual environments (`.venv-prev` from `requirements-previous.txt`,
`.venv` from `requirements.txt`) and runs both scripts on both. The installs take a few minutes;
the runs finish in seconds. Python 3.11 or later; the output below is from Python 3.13 on Linux,
run on 30 October 2026 from clean environments, twice, with output identical apart from the
`Duration:` figures on Semantic Kernel's timing lines.

| Pinned | previous | this week |
|---|---|---|
| semantic-kernel | 1.45.0 (6 Oct) | 1.46.0 (28 Oct, 14:18 UTC) |
| langgraph | 1.2.17 (24 Oct) | 1.2.18 (26 Oct, 20:04 UTC) |

Dates are PyPI upload times.

## What the scripts demonstrate

### `test_sk_function_log.py` (mechanism of the week)

A clinician-assistant agent asks the model to start apixaban for a patient. The scripted model
answers with a function call to `pharmacy.place_order`; Semantic Kernel's auto function-invocation
loop runs it, appends the result to the chat history, calls the model again, and the model closes
the turn. An `AuditSink` handler is attached to the framework's own loggers
(`semantic_kernel.kernel`, `semantic_kernel.functions`, `semantic_kernel.connectors.ai`) at DEBUG,
standing in for a log shipper that someone, somewhere, has pointed at the application log and
called the audit trail. `LAB_CASE=placed` lets the order write; `LAB_CASE=refused` makes the
pharmacy tool raise, the way a contraindication check would.

What the sink received, counted per run:

| case | version | lines naming the function | carrying `pt-123` | carrying `apixaban` | carrying the result | carrying the refusal reason | rows |
|---|---|---|---|---|---|---|---|
| placed | 1.45.0 | 3 | 3 | 3 | 1 | 0 | 1 |
| placed | 1.46.0 | 3 | **0** | **0** | **0** | 0 | 1 |
| refused | 1.45.0 | 3 | 4 | 4 | 0 | 2 | 0 |
| refused | 1.46.0 | 3 | **0** | **0** | 0 | **0** | 0 |

The lines themselves, 1.45.0 then 1.46.0, `placed`:

```
[INFO]  semantic_kernel.kernel: Calling pharmacy-place_order function with args: {"patient_id": "pt-123", "drug": "apixaban", "dose": "5 mg", "route": "oral", "frequency": "BID"}
[DEBUG] semantic_kernel.functions.kernel_function: Function arguments: {'patient_id': 'pt-123', 'drug': 'apixaban', ...}
[DEBUG] semantic_kernel.functions.kernel_function: Function result: ORDER PLACED order-1 apixaban 5 mg oral BID for pt-123

[INFO]  semantic_kernel.kernel: Calling pharmacy-place_order function.
[DEBUG] semantic_kernel.functions.kernel_function: Function arguments provided: 5.
[DEBUG] semantic_kernel.functions.kernel_function: Function result available.
```

and `refused`:

```
[ERROR] semantic_kernel.functions.kernel_function: Function failed. Error: contraindicated: apixaban for pt-123, documented allergy; order refused
[ERROR] semantic_kernel.kernel: Error invoking function pharmacy-place_order: contraindicated: apixaban for pt-123, documented allergy; order refused. [traceback attached]

[ERROR] semantic_kernel.functions.kernel_function: Function failed. Error type: ValueError.
[ERROR] semantic_kernel.kernel: Error invoking function pharmacy-place_order. Error type: ValueError.
```

In every run the model turns (2), the final text, the tool result handed to the model (the full
`ORDER PLACED ...` string, or `An error occurred while invoking the function
pharmacy-place_order: contraindicated: apixaban for pt-123, ...`) and the record (1 row or 0) were
the same on both versions. What changed is only what the framework writes about the call in its
own log: on 1.45.0 an INFO line at the kernel carried the full argument JSON and the function
logger carried the arguments, the result and the exception text; on 1.46.0 the same lines carry
the function name, the number of arguments, the words "result available" and the exception's type.

Source for the cause, read from both wheels: `semantic_kernel/kernel.py`, `invoke_function_call`,
`logger.info(f"Calling {function_call.name} function with args: {function_call.arguments}")` is
now `logger.info("Calling %s function.", function_call.name)`, and the `except` branch logs
`type(exc).__name__` instead of `logger.exception(... {exc})`;
`semantic_kernel/functions/kernel_function_log_messages.py`, `log_function_arguments` logs
`len(arguments)`, `log_function_result_value` logs "Function result available.", and
`log_function_error` logs `type(error).__name__`. Release note for 1.46.0: "Avoid logging
function argument values", #14574. The OpenTelemetry span for the function still carries the
arguments and the result when `SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE`
is set (`kernel_function.py`, `are_sensitive_events_enabled()`); that channel is unchanged and is
the deliberate one.

### `test_langgraph_interrupt_checkpoint.py` (supporting check)

Three plain-Python nodes and no model: `draft_order` writes a draft, `write_order` commits it to
the record, and the graph is compiled with `interrupt_after=["draft_order"]`, so the run pauses
where a pharmacist would review the draft. The caller consumes `stream_mode="checkpoints"`, the
way an approval screen that drives its "resume" button off the checkpoint stream does, then
resumes from the last checkpoint it was shown.

| version | checkpoints streamed before the pause | last streamed is the paused one | `draft_order` runs after resume | `write_order` runs | rows |
|---|---|---|---|---|---|
| 1.2.17 | 2 | False | **2** | **0** | **0** |
| 1.2.18 | 3 | True | 1 | 1 | 1 |

On 1.2.17 the checkpoint the run stopped on was saved but never streamed, so the client's "last
seen" checkpoint was the one before `draft_order` ran. Resuming from it ran `draft_order` again,
produced `draft #2`, and paused again; the draft the pharmacist looked at was replaced and
nothing was written. On 1.2.18 one more `checkpoints` event is emitted, its id equals
`graph.get_state(config)`'s, and the resume writes the reviewed draft once. Source:
`langgraph/pregel/_loop.py`, the task-preparation and checkpoint-emit block of `tick()` moved into
`_prepare_tasks_and_emit_checkpoint()` and called on the `interrupt_after` and recursion-limit
exits (release note: "stream the last checkpoint of a run stopped by interrupt_after or the
recursion limit", #9409, fixes #9180).

### `build_models.py`

Regenerates `models.json` and prints the section 2 table: 17 models on 10,000 documents at 4,000
input and 500 output tokens, list prices read on 30 October from the pages named in each row,
Artificial Analysis Intelligence Index v5.0 scores (announced 27 October; not comparable with the
v4.3.2 scores of Issues 01 to 08) and the Healthcare & Medical score where the homepage comparison
showed one, with the composition recorded as unreadable. Gemini 4 Carbon is the one unverified
price.

```
model                               in/out/cached   AA  med   no cache  80% cached  verified
Claude Haiku 5.5             0.1/0.5/  0.01   36   37 $     6.50       $3.62  True
GPT-6 Luna                   0.1/0.5/  0.01   28    - $     6.50       $3.62  True
gpt-oss-120b on Nebius       0.15/0.6/   n/a    -    - $     9.00         n/a  True
DeepSeek V4.1 Flash          0.3/1.2/ 0.006   32   41 $    18.00       $8.59  True
Mistral Large 4              0.7/2.1/  0.07   25    - $    38.50      $18.34  True
Gemini 3.8 Flash             0.75/3.75/ 0.075   31   38 $    48.75      $27.15  True
GPT-6.1 Terra                1/5/  0.05   51   45 $    65.00      $34.60  True
Grok 4.7                     2/6/   0.5   35   47 $   110.00      $62.00  True
Kimi K3.1 Pro                2/10/   0.2   46   52 $   130.00      $72.40  True
Claude Sonnet 5.5            2/10/   0.1   54   54 $   130.00      $69.20  True
GPT-6.1 Sol                  2/10/   0.1   55   52 $   130.00      $69.20  True
Gemini 4 Argon               2/10/   0.1   50    - $   130.00      $69.20  True
Kimi K3                      3/15/   0.3    -    - $   195.00     $108.60  True
Claude Opus 5.5              4/20/   0.2   58   58 $   260.00     $138.40  True
Gemini 4 Carbon              4/20/   n/a   59    - $   260.00         n/a  False
GPT-6 Astra                  10/50/     1   57   54 $   650.00     $362.00  True
Claude Fable 5.1             10/50/  0.25   50   51 $   650.00     $338.00  True
```

## Files

- `test_sk_function_log.py`: the mechanism. `LAB_CASE` selects `placed` or `refused`.
- `test_langgraph_interrupt_checkpoint.py`: the supporting check.
- `build_models.py`, `models.json`: the model table and its sources.
- `requirements.txt`, `requirements-previous.txt`: the two pin sets.
- `run_all.sh`: builds both environments and runs everything.

Synthetic data only. Nothing here talks to a FHIR server or to any model API. The scripted model
says what it was scripted to say; "the model asked for the order" means the stand-in emitted the
function call it was written to emit, not that any particular model did.
