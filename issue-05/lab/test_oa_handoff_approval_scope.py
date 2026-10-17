"""openai-agents 0.22.3 against 0.23.1: how far an "always approve" reaches.

Commit de25d82 (#5144), "scope function tool approvals to their owning agent", first released in
0.23.0 (2 Oct 2026). Before it, RunContextWrapper kept sticky approvals in a dict keyed by the
tool NAME, so `state.approve(item, always_approve=True)` given for one agent's tool also covered
a same-named tool owned by any agent the run later handed off to. From 0.23.0 the key is a
_FunctionToolApprovalKey(owner agent, tool name) and RunState moves to schema 1.18.

Scenario, synthetic data only. An intake agent and an anticoagulation agent each own a tool
called place_order, both with needs_approval=True. The scripted model has intake order a saline
flush and hand off; the anticoagulation agent then orders warfarin 10 mg. The nurse is asked
once, about the saline flush, and answers "always approve". The script counts what the nurse
was shown against what reached the record.

Run 2 keeps one agent and has it place a second order after the sticky yes, first resumed in the
same process (2a), then with the paused state serialised to JSON and resumed against freshly built
agents (2b), the way an approval service in another process would do it.

No model, no API key: Scripted is a Model subclass that replays a fixed list of outputs.
"""
import asyncio
import importlib.metadata as md

from agents import Agent, ModelResponse, Runner, RunState, Usage, function_tool, set_tracing_disabled
from agents.models.interface import Model
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText

set_tracing_disabled(True)
V = md.version("openai-agents")


def call(name, call_id, args="{}"):
    return ResponseFunctionToolCall(id="fc_" + call_id, call_id=call_id, type="function_call",
                                    name=name, arguments=args)


def text(t):
    return ResponseOutputMessage(id="m1", type="message", role="assistant", status="completed",
                                 content=[ResponseOutputText(text=t, type="output_text", annotations=[], logprobs=[])])


class Scripted(Model):
    def __init__(self, turns):
        self.turns = list(turns)

    async def get_response(self, *a, **k):
        return ModelResponse(output=[self.turns.pop(0)], usage=Usage(), response_id=None)

    def stream_response(self, *a, **k):
        raise NotImplementedError


def build(record, intake_turns, anticoag_turns):
    """Two agents, each owning its own place_order tool that appends to `record`."""
    def tool_for(owner):
        @function_tool(name_override="place_order", needs_approval=True)
        def place_order(order: str) -> str:
            """Write a medication order to the patient record."""
            record.append((owner, order))
            return f"order written by {owner}: {order}"
        return place_order

    anticoag = Agent(name="anticoag", tools=[tool_for("anticoag")], model=Scripted(anticoag_turns))
    intake = Agent(name="intake", tools=[tool_for("intake")], handoffs=[anticoag], model=Scripted(intake_turns))
    return intake


INTAKE = [call("place_order", "c1", '{"order":"saline flush 10 mL"}'), call("transfer_to_anticoag", "h1")]
ANTICOAG = [call("place_order", "c2", '{"order":"warfarin 10 mg daily"}'), text("Both orders placed.")]


def shown(result):
    return [(i.agent.name, i.raw_item.call_id, i.raw_item.arguments) for i in result.interruptions]


async def run1():
    record = []
    intake = build(record, INTAKE, ANTICOAG)
    r = await Runner.run(intake, "admit pt-123")
    asked = shown(r)
    state = r.to_state()
    state.approve(r.interruptions[0], always_approve=True)        # nurse: "always approve" for the saline flush
    r = await Runner.run(intake, state)
    asked += shown(r)
    print("  run 1, in-process resume after always_approve on intake.place_order")
    for a in asked:
        print(f"    nurse was shown: agent={a[0]} call={a[1]} args={a[2]}")
    print(f"    record: {record}")
    print(f"    still waiting on: {shown(r)} | model said: {r.final_output!r}")
    return len(asked), len(record)


INTAKE_TWICE = [call("place_order", "c1", '{"order":"saline flush 10 mL"}'),
                call("place_order", "c3", '{"order":"heparin 5,000 units SC"}'), text("Both orders placed.")]


async def run2(rebuild):
    """Same agent, same tool, a second order after the sticky yes. In-process, or through JSON and rebuilt agents."""
    record = []
    intake = build(record, INTAKE_TWICE, [])
    r = await Runner.run(intake, "admit pt-123")
    asked = shown(r)
    state = r.to_state()
    state.approve(r.interruptions[0], always_approve=True)
    schema = "-"
    if rebuild:
        blob = state.to_json()                                     # what an approval service stores
        schema = blob.get("$schemaVersion")
        intake = build(record, INTAKE_TWICE[1:], [])               # a new process rebuilds the agents
        state = await RunState.from_json(intake, blob)
    r = await Runner.run(intake, state)
    asked += shown(r)
    how = f"through to_json (schema {schema}) and rebuilt agents" if rebuild else "in-process"
    print(f"  run {'2b' if rebuild else '2a'}, one agent, second order after the sticky yes, resumed {how}")
    for a in asked:
        print(f"    nurse was shown: agent={a[0]} call={a[1]} args={a[2]}")
    print(f"    record: {record}")
    print(f"    still waiting on: {shown(r)} | model said: {r.final_output!r}")
    return len(asked), len(record)


if __name__ == "__main__":
    print(f"openai-agents {V} (openai {md.version('openai')})")
    a1, w1 = asyncio.run(run1())
    a2, w2 = asyncio.run(run2(False))
    a3, w3 = asyncio.run(run2(True))
    print(f"  SUMMARY {V}: handoff shown={a1} written={w1} | same agent in-process shown={a2} written={w2}"
          f" | same agent rebuilt shown={a3} written={w3}")
