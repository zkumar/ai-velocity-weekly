# AI Velocity Weekly 08: lab

Week ending 25 October 2026. One mechanism and one supporting check, each run on the Google ADK
release before this week's window and on the release that opened it, plus the model table. No API
key is read or needed: every agent runs on a scripted `BaseLlm` subclass, and the "record" is an
in-memory list. Synthetic data only.

```
./run_all.sh
```

`run_all.sh` creates two virtual environments (`.venv-prev` from `requirements-previous.txt`,
`.venv` from `requirements.txt`) and runs the two scripts on both. The installs take a few
minutes; the runs finish in seconds. Python 3.11 or later; the output below is from Python 3.13.17
on Linux, run on 25 October 2026 from clean environments, twice, with output identical apart from
the generated confirmation ids.

| Pinned | previous | this week |
|---|---|---|
| google-adk | 2.12.0 | 2.13.0 |

2.13.0 was uploaded to PyPI on 23 October at 18:26 UTC. 2.12.0 is the 13 October release that
Issue 07 read from its changelog.

## What the scripts demonstrate

### `test_adk_agenttool_pause.py` (mechanism of the week)

A clinician-assistant agent delegates a medication order to a pharmacy agent. The pharmacy agent
owns one tool, `place_order`, declared with `require_confirmation=True`, so ADK pauses it with an
`adk_request_confirmation` call that a pharmacist is meant to answer. Three ways of wiring the
delegation, selected with `LAB_CASE`:

- `tool`: the pharmacy agent is wrapped as an `AgentTool` of the parent. This is the finding.
- `subagent`: the pharmacy agent is listed under the parent's `sub_agents` with
  `mode="single_turn"`, which is what 2.13.0's new warning tells you to do instead.
- `direct`: the pharmacy agent runs on its own, is paused, and is resumed with a confirmation.
  This is the control: what a working gate looks like.

The parent's scripted model does what a real model does with a tool result: if the result is an
empty string it reports success, if it starts with `Error` it reports the error, otherwise it
repeats what the child said.

What it printed, with the record counted after each run:

| case | version | what the parent was handed | confirmation request visible to the caller | final text | rows |
|---|---|---|---|---|---|
| tool | 2.12.0 | `{"result": ""}` | none | "Apixaban 5 mg BID ordered for pt-123 via the pharmacy agent." | **0** |
| tool | 2.13.0 | `Error: agent 'pharmacy' stopped waiting on unresolved long-running tool call(s) ... which AgentTool cannot resume.` | none | "The pharmacy agent could not complete the order: Error: ..." | 0 |
| subagent | 2.12.0 | nothing: the run ended inside the pharmacy agent after the confirmation | `adk_request_confirmation`, answered, order placed | "Pharmacy: {...ORDER PLACED order-1...}" from the child | 1 |
| subagent | 2.13.0 | `Pharmacy: {"status": "ORDER PLACED order-1 ..."}` after the confirmation | `adk_request_confirmation`, answered, order placed | "Delegator saw: ..." from the parent | 1 |
| direct | both | n/a | `adk_request_confirmation`, answered, order placed | "Pharmacy: {...ORDER PLACED order-1...}" | 1 |

The first row is the finding. On 2.12.0 the child paused for the pharmacist, `AgentTool` threw the
child's session away, found no text in the child's last content, and returned `""` to the parent.
No confirmation request reached the caller, the record stayed empty, and the parent's closing
sentence said the order was placed. On 2.13.0 the same wiring returns an error string naming the
pending call id, so the parent reports a failure; the gate is still unreachable, and the
pharmacist is still never asked. The `subagent` rows show the documented alternative: the pause
surfaces to the caller on both versions, and on 2.13.0 the turn after the confirmation routes back
to the delegating parent, where on 2.12.0 it ended in the child.

Source for the cause: `google/adk/tools/agent_tool.py`, read from both wheels. 2.12.0 returned
`last_error_message or ''` when the child's last content held no text parts; 2.13.0 collects
`long_running_tool_ids` from the child's events, removes those answered by a function response
before the run ends, and if any remain logs a warning and returns the error string instead
(changelog line: "surface HITL pauses in AgentTool instead of returning """, closes #7245).

### `test_adk_nested_state_delta.py` (supporting check)

A tool puts a hold on a medication by appending to `state["patient"]["holds"]`, a write into a
nested container, and separately bumps a top-level counter. The script prints the `state_delta` on
the tool event and the session state the service holds afterwards.

| version | `state_delta` on the tool event | session state held by the service |
|---|---|---|
| 2.12.0 | `{"holds_written": 1}` | `{"patient": {"id": "pt-123", "holds": []}, "holds_written": 1}` |
| 2.13.0 | `{"holds_written": 1, "patient": {"id": "pt-123", "holds": ["apixaban"]}}` | `{"patient": {"id": "pt-123", "holds": ["apixaban"]}, "holds_written": 1}` |

On 2.12.0 the tool saw the hold in its own view of the state, the delta did not carry it, and the
persisted session has no hold. Source: `google/adk/sessions/state.py` in 2.13.0 keeps a copy of
every container a read hands out and, when `ctx.actions` is read after the tool runs, records any
container that changed as a state change (changelog lines: "record a write into a nested state
container as a state change" and "record a nested state write only when its container converts
to JSON unchanged").

### `build_models.py`

Regenerates `models.json` and prints the section 2 table: 15 models on 10,000 documents at 4,000
input and 500 output tokens, list prices read on 25 October from the pages named in each row,
Artificial Analysis Intelligence Index v4.3.2 scores, and the Healthcare & Medical Index for the
two rows whose score could be read from that page today. The two Kimi rows are marked unverified:
the vendor's price tables did not render, so K3 carries last week's price and K3.1 Pro carries a
third-party figure.

```
model                               in/out/cached   AA  med   no cache  80% cached  verified
Claude Haiku 5.5             0.1/0.5/  0.01   43    - $     6.50       $3.62  True
GPT-6 Luna                   0.1/0.5/  0.01   38    - $     6.50       $3.62  True
gpt-oss-120b on Nebius       0.15/0.6/   n/a   12    - $     9.00         n/a  True
DeepSeek V4.1 Flash          0.3/1.2/ 0.006   45    - $    18.00       $8.59  True
Gemini 3.8 Flash             0.75/3.75/ 0.075   41    - $    48.75      $27.15  True
Mistral Large 4              1.36/4.18/  0.14   38    - $    75.30      $36.26  True
Grok 4.7                     2/6/   0.5   46    - $   110.00      $62.00  True
Kimi K3.1 Pro                2/10/   0.2   55    - $   130.00      $72.40  False
Claude Sonnet 5.5            2/10/   0.1   56   53 $   130.00      $69.20  True
GPT-6.1 Sol                  2/10/   0.1   52    - $   130.00      $69.20  True
Gemini 4 Argon               2/10/   0.1   53    - $   130.00      $69.20  True
Kimi K3                      3/15/   0.3    -    - $   195.00     $108.60  False
Claude Opus 5.5              4/20/   0.2   58   55 $   260.00     $138.40  True
GPT-6 Astra                  10/50/     1   53    - $   650.00     $362.00  True
Claude Fable 5.1             10/50/  0.25   53    - $   650.00     $338.00  True
```

## Files

- `test_adk_agenttool_pause.py`: the mechanism. `LAB_CASE` selects `tool`, `subagent` or `direct`.
- `test_adk_nested_state_delta.py`: the supporting check.
- `build_models.py`, `models.json`: the model table and its sources.
- `requirements.txt`, `requirements-previous.txt`: the two pins.
- `run_all.sh`: builds both environments and runs everything.

Synthetic data only. Nothing here talks to a FHIR server or to any model API. The scripted models
say what they were scripted to say; "the parent reported the order placed" means the stand-in did
what a model with an empty tool result and no other information tends to do, not that any
particular model did.
