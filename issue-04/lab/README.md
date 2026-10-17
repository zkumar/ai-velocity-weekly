# AI Velocity Weekly 04, lab package

Week ending 25 September 2026. Synthetic data only; no model key is needed for any script.
Issue: [ai-velocity-weekly-04.html](../ai-velocity-weekly-04.html).

This week's question is what happens after the yes: how many times an approved write actually
runs, and what the record holds afterwards. Each script runs twice, on the week's release and
on the release before it, and prints the count of executions beside the count of approvals.

## Files

| File | What it demonstrates | Install |
|---|---|---|
| `test_da_parallel_writes.py` | deepagents 0.7.16, commit `2e2ee91` (#6446): when one model response carries two mutations of the same file, every call after the first is answered with an error ToolMessage and never runs. Run 1 has no gate: an edit and a rewrite in one response, and which content survives flips between versions. Run 2 puts `write_file` behind human-in-the-loop, the reviewer approves both writes, and one of the two approved writes executes zero times. The mechanism of the week. | `pip install "deepagents==0.7.16"` (and `==0.7.15` to compare) |
| `test_li_failed_tool_twice.py` | llama-index-core 0.14.25, commit `e07b962` (#22841): `call_tool()` no longer retries a one-parameter `FunctionTool` with keyword arguments after it raises. On 0.14.24 a tool that commits and then raises is executed twice; the caller sees one call and one error. | `pip install "llama-index-core==0.14.25"` (and `==0.14.24`) |
| `test_lg_typed_resume.py` | langgraph 1.2.12, commit `448a763` (#8886): `interrupt(value, response_schema=...)` validates a resume value against a Pydantic model before the node sees it. A typo'd decision raises and the graph stays paused; the same typo against a JSON Schema dict, or on 1.2.11 with no schema, is committed and read as a rejection. | `pip install "langgraph==1.2.12"` (and `==1.2.11`) |
| `build_models.py` | Regenerates `models.json` and the section 2 cost columns. | none |
| `models.json` | Model table: licence, list prices read 25 Sept, AA v4.3.2 score, AA Healthcare & Medical Index score, cost of the 10,000-document workload with and without cache, source, what changed. | none |
| `requirements.txt`, `requirements-previous.txt` | Pinned versions for the week's releases and the ones before them. | |
| `run_all.sh` | Builds `.venv/current` and `.venv/previous`, installs each set, runs every `test_*.py` in both, then the model table. | |

## Observed output (25 Sept 2026, clean directory, Python 3.11, Linux)

`test_da_parallel_writes.py`

    deepagents 0.7.15 (langgraph 1.2.11, langchain-core 1.6.5)
      run 1, no gate: model response 2 carried c2 edit_file(10->20 mg) and c3 write_file(HOLD)
        c1 status=success 'Updated file /patients/pt-123/plan.md'
        c2 status=success "Successfully replaced 1 instance(s) of the string in '/patients/pt-123/plan.md'"
        c3 status=success 'Updated file /patients/pt-123/plan.md'
        final file: 'Plan: HOLD lisinopril, K+ 6.1 mmol/L, repeat BMP\n'
        model said: 'Plan updated.'
      run 2, HITL on write_file: reviewer shown 2 action requests: ['Plan A: continue lisinopril 20 mg', 'Plan B: HOLD lisinopril, K+ 6.1']
        c1 status=success 'Updated file /patients/pt-123/plan.md'
        c2 status=success 'Updated file /patients/pt-123/plan.md'
        approved writes: 2 | executed writes: 2 | final file: 'Plan B: HOLD lisinopril, K+ 6.1\n'
        model said: 'Both plans written.'
      SUMMARY 0.7.15: approved=2 executed=2 record='Plan B: HOLD lisinopril, K+ 6.1'

    deepagents 0.7.16 (langgraph 1.2.12, langchain-core 1.6.5)
      run 1, no gate: model response 2 carried c2 edit_file(10->20 mg) and c3 write_file(HOLD)
        c1 status=success 'Updated file /patients/pt-123/plan.md'
        c2 status=success "Successfully replaced 1 instance(s) of the string in '/patients/pt-123/plan.md'"
        c3 status=error 'Error: parallel file mutations to the same path are not allowed.'
        final file: 'Plan: start lisinopril 20 mg daily\n'
        model said: 'Plan updated.'
      run 2, HITL on write_file: reviewer shown 2 action requests: ['Plan A: continue lisinopril 20 mg', 'Plan B: HOLD lisinopril, K+ 6.1']
        c1 status=success 'Updated file /patients/pt-123/plan.md'
        c2 status=error 'Error: parallel file mutations to the same path are not allowed.'
        approved writes: 2 | executed writes: 1 | final file: 'Plan A: continue lisinopril 20 mg\n'
        model said: 'Both plans written.'
      SUMMARY 0.7.16: approved=2 executed=1 record='Plan A: continue lisinopril 20 mg'

`test_li_failed_tool_twice.py`

    llama-index-core 0.14.24
      one call_tool() | is_error=True | tool output: 'Encountered error: EHR gateway: timeout after commit'
      writes in the record: 2 ['BP 120/80, K+ 6.1 mmol/L', 'BP 120/80, K+ 6.1 mmol/L']
      SUMMARY 0.14.24: calls=1 errors=1 writes=2

    llama-index-core 0.14.25
      one call_tool() | is_error=True | tool output: 'Encountered error: EHR gateway: timeout after commit'
      writes in the record: 1 ['BP 120/80, K+ 6.1 mmol/L']
      SUMMARY 0.14.25: calls=1 errors=1 writes=1

`test_lg_typed_resume.py`

    langgraph 1.2.11
      interrupt(response_schema=...) -> TypeError: interrupt() got an unexpected keyword argument 'response_schema'
        0 no schema, typo: committed | written='' | node received {'action': 'aprove'}
          state.next=() | pending interrupts=0
      SUMMARY 1.2.11: no typed approvals; the typo is committed as a rejection

    langgraph 1.2.12
      surfaced response_schema properties: ['action', 'reviewer_id']
        1 pydantic, typo: raised ValidationError: 2 validation errors for Decision
          state.next=('gate',) | pending interrupts=1
        2 pydantic, valid: committed | written='K+ 6.1 mmol/L, hold lisinopril, repeat BMP' | node received Decision(action='approve', reviewer_id='rn-42')
          state.next=() | pending interrupts=0
        3 dict schema, typo: committed | written='' | node received {'action': 'aprove'}
          state.next=() | pending interrupts=0
      SUMMARY 1.2.12: pydantic schema rejects the typo and stays paused; dict schema commits it

`build_models.py`: see the table in section 2 of the issue. Claude Opus 5.5 and GPT-6 Sol both
do the workload for $260 and $130; GPT-6 Luna is the cheapest row above index 35 at $6.50.

## What each result means

1. **An approval is not an execution.** On 0.7.16 the reviewer approved two writes and the
   second one executed zero times. The transcript holds two approvals and one error
   ToolMessage; the record holds Plan A. The scripted model still said "Both plans written."
   Nothing in deepagents tells the reviewer that a thing they signed did not happen; that
   reconciliation is yours.
2. **Which write wins flipped.** On 0.7.15 the last call in the model's response wrote the
   file; on 0.7.16 the first one does. Any evaluation that scored the agent's final plan on
   0.7.15 measures a different system on 0.7.16. The check runs in `wrap_tool_call`, after
   the approval middleware, and only inspects the arg key `file_path` on the most recent
   AIMessage, so it covers deepagents' own file tools and nothing else.
3. **A failing write is not a failed write.** On 0.14.24 one tool call, one error, two writes
   in the record. The retry is invisible to the caller and to the trace. A gateway that
   commits and then times out is the ordinary case, not the edge case; if you run
   llama-index below 0.14.25, count the rows you have.
4. **A typed approval validates what it is told to.** With a Pydantic `response_schema` the
   typo never reaches the node and the graph stays paused; with a dict it is committed and
   read as a rejection, which is what 1.2.11 did with no schema at all. In both versions the
   raw resume value, not the validated object, is what the checkpoint persists.

## Things to change and rerun

1. In `test_da_parallel_writes.py`, add a reconciliation step after resume: for every
   approved action request, assert that a `ToolMessage` with `status="success"` and the same
   `tool_call_id` exists, and raise otherwise. Run 2 on 0.7.16 should now fail loudly.
2. In `test_li_failed_tool_twice.py`, give `append_note` an idempotency key and make the
   second call a no-op. Then run it on 0.14.24 and check the record has one row.
3. In `test_lg_typed_resume.py`, replace the dict schema with the `Decision` model and add
   `reason: str`. Then read `get_state_history()` and find where the reviewer's id is stored.

## Verified from a clean install

On 25 Sept 2026 these files were copied into an empty directory and `bash run_all.sh` was run with
no API key in the environment. It created both virtual environments, installed the pinned versions
and printed the output above. If a script fails on your machine, compare `pip freeze` with the
requirements file first.
