"""google-adk 2.10.0 against 2.11.0: a confirmation gate on a workflow tool node.

Commit ce132b9, "pause tool nodes for tool confirmation via RequestInput", first released in
2.11.0 (2 Oct 2026). A FunctionTool(require_confirmation=True) used as a node in a Workflow had
no way to pause on 2.10.0: the node returned the "requires confirmation" error as its output and
the workflow finished. On 2.11.0 the node emits an adk_request_input function call whose id is
"wf_tool_confirmation:<node path>", and a FunctionResponse {"confirmed": true} resumes it.

A two-node workflow, prep then submit_prior_auth, with no LLM anywhere. The script prints what
the workflow emitted, whether the tool ran before and after the reviewer's yes, and the events
left in the session. Synthetic data only. No model, no API key.
"""
import asyncio
import importlib.metadata as md
import warnings

warnings.filterwarnings("ignore")

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.adk.tools.function_tool import FunctionTool  # noqa: E402
from google.adk.workflow import Workflow  # noqa: E402
from google.genai import types  # noqa: E402

V = md.version("google-adk")
SUBMITTED = []


def submit_prior_auth(patient: str, drug: str) -> dict:
    """Submit a prior authorisation request to the payer."""
    SUBMITTED.append((patient, drug))
    return {"status": "submitted", "patient": patient, "drug": drug}


def prep(node_input) -> dict:
    return {"patient": "pt-123", "drug": "adalimumab"}


wf = Workflow(name="pa", edges=[("START", prep), (prep, FunctionTool(submit_prior_auth, require_confirmation=True))])


async def main():
    print(f"google-adk {V}")
    params = InMemoryRunner.__init__.__code__.co_varnames
    runner = InMemoryRunner(node=wf, app_name="app") if "node" in params else InMemoryRunner(agent=wf, app_name="app")
    s = await runner.session_service.create_session(app_name="app", user_id="u")
    request = None
    async for ev in runner.run_async(user_id="u", session_id=s.id,
                                     new_message=types.Content(role="user", parts=[types.Part(text="go")])):
        for c in ev.get_function_calls():
            request = c
            print(f"  workflow emitted function call: {c.name} id={c.id}")
        if getattr(ev, "output", None) is not None:
            print(f"  node output: {ev.output}")
    before = len(SUBMITTED)
    print(f"  after the first run: paused={'yes' if request else 'no'} | payer record: {SUBMITTED}")
    if request:
        yes = types.Content(role="user", parts=[types.Part(function_response=types.FunctionResponse(
            id=request.id, name=request.name, response={"confirmed": True}))])
        async for ev in runner.run_async(user_id="u", session_id=s.id, new_message=yes):
            if getattr(ev, "output", None) is not None:
                print(f"  node output: {ev.output}")
        print(f"  after the reviewer's yes: payer record: {SUBMITTED}")
    s = await runner.session_service.get_session(app_name="app", user_id="u", session_id=s.id)
    print(f"  events persisted in the session: {len(s.events)}")
    print(f"  SUMMARY {V}: paused={'yes' if request else 'no'} submitted_before_yes={before} submitted_after_yes={len(SUBMITTED)}")


asyncio.run(main())
