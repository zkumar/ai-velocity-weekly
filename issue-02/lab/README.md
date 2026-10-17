# AI Velocity Weekly 02, lab package

Week ending 11 September 2026. Synthetic data only; no model key needed
for any script. Issue: https://claude.ai/code/artifact/35160807-b786-4045-ad18-0655d3b6356c

## Files

| File | What it does | Install |
|---|---|---|
| `test_af_duration_budget.py` | Microsoft Agent Framework 1.18.0 `max_duration_seconds`: three scenarios showing what happens to a clinician's approval that arrives after the tool-loop budget, with the session serialised to JSON in between. Executed for section 1.1. | `pip install "agent-framework-core==1.18.0"` |
| `test_mcp_token_audience.py` | MCP Python SDK 2.2.0: `BearerAuthBackend(resource_server_url=...)` refusing a token issued for another MCP server; the `ContentBlock` alias change. Executed for section 1.2. | `pip install "mcp==2.2.0"` |
| `prior_auth_verdict_lab.py` | Prior authorisation as a solver problem (after VERDICT, arXiv 2609.03366): one payer rule for CPT 70553 in z3, pivotal conditions, self-faithfulness assertion, ClaimResponse-shaped stub. | `pip install z3-solver` |
| `build_models.py` | Regenerates `models.json` and the section 2 cost columns. | none |
| `models.json` | Model table with every column (dates, licence, context, max output, prices, AA v4.3 index, coding and health benchmarks, throughput, source URL, what changed this week). | none |

## Observed output (12 Sept 2026, sandbox)

`test_af_duration_budget.py`

    Scenario A: 30 s budget, clinician answers in 1 s, ToolApprovalMiddleware on
      FHIR writes performed: 1 ... final assistant text: 'Done.'
    Scenario B: 2 s budget, clinician answers in 3 s, ToolApprovalMiddleware on
      tool_choice seen by the model per call: ['auto', 'none']
      FHIR writes performed: 0
      function_result returned to model: []
      final assistant text: 'Order placed.'
    Scenario C: 2 s budget, clinician answers in 3 s, bare Agent (no harness middleware)
      budget in session after request 1: None
      FHIR writes performed: 1

`test_mcp_token_audience.py`

    tok-fhir    loose=accepted strict=accepted
    tok-sched   loose=accepted strict=refused
    tok-legacy  loose=accepted strict=refused
    ContentBlock.model_validate -> AttributeError

`prior_auth_verdict_lab.py`

    Decision: APPROVED
    Pivotal: new_focal_neuro_deficit, mri_brain_within_90_days, contrast_contraindicated
    With a prior MRI 80 days ago -> DENIED ; pivotal: ['mri_brain_within_90_days']

## Things to change and rerun

1. In `test_af_duration_budget.py`, replace the scripted "Order placed." with a
   real chat client and see what your model says when tools are withdrawn and
   no tool result exists. Then read `session.state["_function_invocation_budget_state"]`
   before presenting an approval and refuse to collect a signature the loop will
   not honour.
2. In `test_mcp_token_audience.py`, point `StubVerifier` at your introspection
   endpoint and test one token per MCP server you run.
3. In `prior_auth_verdict_lab.py`, replace `FACTS` with a Pydantic AI agent that
   returns the same typed shape from a synthetic note; the diff between its facts
   and yours is your extraction eval. The solver does not change.

Versions used: agent-framework-core 1.18.0, mcp 2.2.0, fastmcp 4.0.3, z3-solver
(latest on 12 Sept 2026), Python 3.11.

## Verified from a clean install

On 12 Sept 2026 the zip was unpacked into an empty directory and `bash run_all.sh` was run: it creates a fresh virtual environment, installs the exact versions in `requirements.txt`, and runs every script. All passed with the output shown above (Python 3.11, Linux). To repeat that check yourself: `bash run_all.sh`. If a script fails on your machine, the first thing to compare is `pip freeze` against `requirements.txt`.
