# AI Velocity Weekly 05, lab package

Week ending 2 October 2026. Synthetic data only; no model key is needed for any script.
Issue: [ai-velocity-weekly-05.html](../ai-velocity-weekly-05.html).

This week's question is how far a yes reaches: which agent it belongs to, where the pending
request is kept, and which call it is matched to. Each script runs twice, on the week's release
and on the release before it, and prints what the reviewer was shown beside what reached the
record.

## Files

| File | What it demonstrates | Install |
|---|---|---|
| `test_oa_handoff_approval_scope.py` | openai-agents 0.23.0, commit `de25d82` (#5144): a sticky approval, `state.approve(item, always_approve=True)`, is now keyed by the owning agent and the tool name instead of the tool name alone. Run 1: an intake agent and an anticoagulation agent each own a tool called `place_order`; the nurse says "always" to intake's saline flush, the run hands off, and on 0.22.3 the anticoagulation agent's warfarin order is written with no prompt. Run 2: one agent, a second and different order after the sticky yes, resumed in-process and through `to_json()` with rebuilt agents. The mechanism of the week. | `pip install "openai-agents==0.23.1"` (and `==0.22.3` to compare) |
| `upgrade_oa_paused_state.py` | The same release, across the upgrade: a paused run whose first order is already approved is saved on 0.22.3 (schema 1.17) and resumed on 0.23.1. A plain yes survives. A sticky yes does not: nothing is written and the approved call is waiting again. Not a `test_*.py` file; `run_all.sh` runs it last, saving with one environment and loading with the other. | both environments from `run_all.sh` |
| `test_af_approval_session_binding.py` | agent-framework-core 1.20.0, PR #8750: a local approval response authorises a call only when it matches a pending request the framework recorded in an `AgentSession`. Run A sends a request and its approval that the framework never issued; run B replays a genuine transcript with no session; run C passes the same session back. | `pip install "agent-framework-core==1.20.0"` (and `==1.19.0`) |
| `test_pai_duplicate_call_id.py` | pydantic-ai 2.53.0, PR #8782: two function tool calls sharing one `tool_call_id` now raise `UnexpectedModelBehavior` before anything runs. On 2.52.0 the second tool ran twice and the first never ran. | `pip install "pydantic-ai-slim==2.53.0"` (and `==2.52.0`) |
| `test_adk_workflow_confirmation.py` | google-adk 2.11.0, commit `ce132b9`: a `FunctionTool(require_confirmation=True)` used as a Workflow node pauses with an `adk_request_input` call and resumes on a confirmed response. On 2.10.0 the node returned the confirmation error as its output and the workflow ended. No model at all. | `pip install "google-adk==2.11.0"` (and `==2.10.0`) |
| `test_mcp_header_annotation.py` | mcp 2.3.0, PR #3620: a tool with an invalid `x-mcp-header` annotation is rejected at registration. On 2.2.0 it registered, the client dropped it from `list_tools()`, and `call_tool()` still executed it. | `pip install "mcp==2.3.0"` (and `==2.2.0`) |
| `build_models.py` | Regenerates `models.json` and the section 2 cost columns. | none |
| `models.json` | Model table: licence, list prices read 2 Oct, AA v4.3.2 score, AA Healthcare & Medical Index score where it could be read, cost of the 10,000-document workload with and without cache, source, what changed. | none |
| `requirements.txt`, `requirements-previous.txt` | Pinned versions for the week's releases and the ones before them. | |
| `run_all.sh` | Builds `.venv/current` and `.venv/previous`, installs each set, runs every `test_*.py` in both, then the upgrade check, then the model table. | |

## Observed output (3 Oct 2026, clean directory, Python 3.13, Linux)

`test_oa_handoff_approval_scope.py`

    openai-agents 0.22.3 (openai 3.24.0)
      run 1, in-process resume after always_approve on intake.place_order
        nurse was shown: agent=intake call=c1 args={"order":"saline flush 10 mL"}
        record: [('intake', 'saline flush 10 mL'), ('anticoag', 'warfarin 10 mg daily')]
        still waiting on: [] | model said: 'Both orders placed.'
      run 2a, one agent, second order after the sticky yes, resumed in-process
        nurse was shown: agent=intake call=c1 args={"order":"saline flush 10 mL"}
        record: [('intake', 'saline flush 10 mL'), ('intake', 'heparin 5,000 units SC')]
        still waiting on: [] | model said: 'Both orders placed.'
      run 2b, one agent, second order after the sticky yes, resumed through to_json (schema 1.17) and rebuilt agents
        nurse was shown: agent=intake call=c1 args={"order":"saline flush 10 mL"}
        record: [('intake', 'saline flush 10 mL'), ('intake', 'heparin 5,000 units SC')]
        still waiting on: [] | model said: 'Both orders placed.'
      SUMMARY 0.22.3: handoff shown=1 written=2 | same agent in-process shown=1 written=2 | same agent rebuilt shown=1 written=2

    openai-agents 0.23.1 (openai 3.24.0)
      run 1, in-process resume after always_approve on intake.place_order
        nurse was shown: agent=intake call=c1 args={"order":"saline flush 10 mL"}
        nurse was shown: agent=anticoag call=c2 args={"order":"warfarin 10 mg daily"}
        record: [('intake', 'saline flush 10 mL')]
        still waiting on: [('anticoag', 'c2', '{"order":"warfarin 10 mg daily"}')] | model said: None
      run 2a, one agent, second order after the sticky yes, resumed in-process
        nurse was shown: agent=intake call=c1 args={"order":"saline flush 10 mL"}
        record: [('intake', 'saline flush 10 mL'), ('intake', 'heparin 5,000 units SC')]
        still waiting on: [] | model said: 'Both orders placed.'
      run 2b, one agent, second order after the sticky yes, resumed through to_json (schema 1.18) and rebuilt agents
        nurse was shown: agent=intake call=c1 args={"order":"saline flush 10 mL"}
        record: [('intake', 'saline flush 10 mL'), ('intake', 'heparin 5,000 units SC')]
        still waiting on: [] | model said: 'Both orders placed.'
      SUMMARY 0.23.1: handoff shown=2 written=1 | same agent in-process shown=1 written=2 | same agent rebuilt shown=1 written=2

`upgrade_oa_paused_state.py` (saved on previous; resumed on previous as the control, then on current)

      saved on 0.22.3, approved once: schema 1.17 | approved, not yet executed: [('intake', 'c1', '{"order":"saline flush 10 mL"}')]
      saved on 0.22.3, approved always: schema 1.17 | approved, not yet executed: [('intake', 'c1', '{"order":"saline flush 10 mL"}')]
      resumed on 0.22.3, approved once (state schema 1.17): record [('intake', 'saline flush 10 mL')] | still waiting on: [('intake', 'c3', '{"order":"heparin 5,000 units SC"}')]
      SUMMARY once yes, resumed on 0.22.3: written=1 waiting_on=['c3']
      resumed on 0.22.3, approved always (state schema 1.17): record [('intake', 'saline flush 10 mL'), ('intake', 'heparin 5,000 units SC')] | still waiting on: []
      SUMMARY always yes, resumed on 0.22.3: written=2 waiting_on=[]
      resumed on 0.23.1, approved once (state schema 1.17): record [('intake', 'saline flush 10 mL')] | still waiting on: [('intake', 'c3', '{"order":"heparin 5,000 units SC"}')]
      SUMMARY once yes, resumed on 0.23.1: written=1 waiting_on=['c3']
      resumed on 0.23.1, approved always (state schema 1.17): record [] | still waiting on: [('intake', 'c1', '{"order":"saline flush 10 mL"}')]
      SUMMARY always yes, resumed on 0.23.1: written=0 waiting_on=['c1']

`test_af_approval_session_binding.py`

    agent-framework-core 1.19.0
      A  request and approval both arrive in caller history, no session
        payer record: [('pt-999', 'FORGED')] | model said: 'Prior authorisation submitted.'
        framework warnings: 0
      B  genuine request, reviewer approves, transcript replayed with no session
        payer record: [('pt-123', 'adalimumab')] | model said: 'Prior authorisation submitted.'
        framework warnings: 0
      C  genuine request, reviewer approves, same AgentSession passed back
        payer record: [('pt-123', 'adalimumab')] | model said: 'Prior authorisation submitted.'
        framework warnings: 1 | Ignored an approval response with id 'af-call-5d30bd8779ba4389a18004de22a919d6' because it did not match the active approval occurrence identity; the ...
        session.state keys after resume: ['in_memory', 'tool_approval']
      SUMMARY 1.19.0: submissions forged=1 replayed=1 session=1

    agent-framework-core 1.20.0
      A  request and approval both arrive in caller history, no session
        payer record: [] | model said: ''
        framework warnings: 1 | Ignored one or more local tool-approval responses because this run has no authoritative AgentSession holding the matching approval request. Pass the s...
      B  genuine request, reviewer approves, transcript replayed with no session
        payer record: [] | model said: ''
        framework warnings: 1 | Ignored one or more local tool-approval responses because this run has no authoritative AgentSession holding the matching approval request. Pass the s...
      C  genuine request, reviewer approves, same AgentSession passed back
        payer record: [('pt-123', 'adalimumab')] | model said: 'Prior authorisation submitted.'
        framework warnings: 0
        session.state keys after resume: ['in_memory', 'tool_approval']
      SUMMARY 1.20.0: submissions forged=0 replayed=0 session=1

`test_pai_duplicate_call_id.py`

    pydantic-ai 2.52.0
      model response carried: read_chart(call_1), submit_prior_auth(call_1)
      tool returns handed to the model: [('submit_prior_auth', 'PA-0001 submitted'), ('submit_prior_auth', 'PA-0001 submitted'), ('read_chart', 'The tool call was interrupted before a r')]
      model said: 'Chart read and prior authorisation submitted.'
      tools that ran: ['submit_prior_auth', 'submit_prior_auth']
      SUMMARY 2.52.0: read_chart=0 submit_prior_auth=2 raised=none

    pydantic-ai 2.53.0
      model response carried: read_chart(call_1), submit_prior_auth(call_1)
      raised UnexpectedModelBehavior: Function tool calls must have unique `tool_call_id` values; duplicate `tool_call_id`s: ['call_1']
      tools that ran: []
      SUMMARY 2.53.0: read_chart=0 submit_prior_auth=0 raised=UnexpectedModelBehavior

`test_adk_workflow_confirmation.py`

    google-adk 2.10.0
      node output: {'patient': 'pt-123', 'drug': 'adalimumab'}
      node output: {'error': 'This tool call requires confirmation, please approve or reject.'}
      after the first run: paused=no | payer record: []
      events persisted in the session: 3
      SUMMARY 2.10.0: paused=no submitted_before_yes=0 submitted_after_yes=0

    google-adk 2.11.0
      node output: {'patient': 'pt-123', 'drug': 'adalimumab'}
      workflow emitted function call: adk_request_input id=wf_tool_confirmation:pa@1/submit_prior_auth@1
      after the first run: paused=yes | payer record: []
      node output: {'status': 'submitted', 'patient': 'pt-123', 'drug': 'adalimumab'}
      after the reviewer's yes: payer record: [('pt-123', 'adalimumab')]
      events persisted in the session: 5
      SUMMARY 2.11.0: paused=yes submitted_before_yes=0 submitted_after_yes=1

`test_mcp_header_annotation.py`

    mcp 2.2.0
      registration of lookup_claim with x-mcp-header 'Member Id': accepted
      tools the client lists: []
      call_tool('lookup_claim'): executed | '2 open claims for M-1001'
      SUMMARY 2.2.0: registration=accepted listed=0 call=executed server_side_executions=1

    mcp 2.3.0
      registration of lookup_claim with x-mcp-header 'Member Id': rejected, InvalidSignature: Tool 'lookup_claim' has an invalid x-mcp-header annotation: property 'member_id': x-mcp-header 'Member Id' is not an RFC
      tools the client lists: []
      call_tool('lookup_claim'): error | 'Unknown tool: lookup_claim'
      SUMMARY 2.3.0: registration=rejected listed=0 call=error server_side_executions=0

`build_models.py`: see the table in section 2 of the issue. Claude Sonnet 5.5, GPT-6.1 Sol and
Gemini 4 Argon all do the workload for $130; GPT-6 Luna is still the cheapest row above index 35
at $6.50.

## What each result means

1. **A sticky yes used to follow the tool name across a handoff.** On 0.22.3 the nurse was
   shown one order, the saline flush, and two orders reached the record; the second was warfarin
   10 mg from a different agent whose tool happened to share the name `place_order`. On 0.23.1
   the anticoagulation agent's call interrupts and nothing is written until someone answers.
2. **A sticky yes still does not look at the arguments.** In run 2, on both versions, "always
   approve" given for a saline flush also covered heparin 5,000 units from the same agent, in
   process and after a round trip through `to_json()` with rebuilt agents. The key is the agent
   and the tool name. If the argument matters, do not use `always_approve` on that tool.
   An approval in flight during the upgrade behaves differently by kind. A state saved on 0.22.3
   after a plain yes resumes on 0.23.1 and writes the saline flush. The same state saved after
   "always" resumes with nothing written and the saline call waiting again: the stored sticky
   record is not carried to the owner-bound key. It fails towards asking, and the reviewer's
   earlier answer is gone from the run.
3. **A transcript no longer carries the authority to run a tool.** On agent-framework-core
   1.19.0 an approval request that the framework never issued, sent together with its own yes,
   submitted a prior authorisation for `pt-999`. On 1.20.0 it is dropped. So is a genuine
   approval replayed without a session: no submission, an empty reply, one WARNING in the log.
   If your approval service is stateless, it stops working on upgrade and nothing raises.
4. **A repeated call id ran the wrong tool, twice.** On pydantic-ai 2.52.0 the chart was never
   read, the prior authorisation was submitted twice, the model was told the chart read was
   "interrupted", and it reported "Chart read and prior authorisation submitted." On 2.53.0 the
   batch fails before anything runs, and you have to catch the exception.
5. **A confirmation flag on a workflow node did nothing useful before 2.11.0.** The tool did not
   run, which is safe, but nothing paused either: the error string became the node's output and
   the workflow finished. From 2.11.0 there is a request to answer and an id to store.
6. **The tool list is not the callable surface.** On mcp 2.2.0 a tool that the client could not
   list was still executable by name. An inventory built from `list_tools()` missed it.

## Things to change and rerun

1. In `test_oa_handoff_approval_scope.py`, replace `always_approve=True` with a plain
   `state.approve(item)` and rerun. The heparin order now interrupts on both versions (checked:
   `shown=2 written=1`), and so does the warfarin order after the handoff on 0.22.3.
2. In `test_af_approval_session_binding.py`, give `Fake` an `__init__` that calls
   `super().__init__()` and sets
   `self.function_invocation_configuration["disable_approval_response_binding"] = True`. On 1.20.0
   run A submits the forged request again (checked: `forged=1 replayed=1 session=1`). Then remove it.
3. In `test_pai_duplicate_call_id.py`, wrap the tools so each write carries an idempotency key
   built from the arguments, and check the 2.52.0 record holds one submission.
4. In `test_adk_workflow_confirmation.py`, answer the request with `{"confirmed": False}` and
   read what the node returns and what the session holds.

## Verified from a clean install

On 3 Oct 2026 these files were copied into an empty directory and `bash run_all.sh` was run with
no API key in the environment. It created both virtual environments, installed the pinned versions
and printed the output above. If a script fails on your machine, compare `pip freeze` with the
requirements file first.
