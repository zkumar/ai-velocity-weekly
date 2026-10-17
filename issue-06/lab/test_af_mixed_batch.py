"""agent-framework-core 1.20.0 against 1.21.0: one model response, one question for a human
and one local write.

PR #9050 (fixes #8898, in 1.21.0, 8 Oct 2026). The model returns two tool calls in one response:
  ask_clinician  a declaration-only tool (func=None): the host owns it and a human answers it
  hold_medication  a local tool that writes to the record
Before: the whole batch became a user-input pause and the local call never ran.
Now: the batch is split. Without a session the local sibling runs immediately. With an
AgentSession the local call is persisted and released after the host result arrives.

Scripted chat client, no model, no API key. The question this answers: when the model asks the
clinician "is it safe to hold lisinopril?" and writes the hold in the same breath, has the write
happened by the time the clinician sees the question?
"""
import asyncio
import importlib.metadata as md

from agent_framework import (Agent, BaseChatClient, ChatResponse, Content, FunctionInvocationLayer,
                             FunctionTool, Message, tool)

VERSION = md.version("agent-framework-core")
RECORD = []


@tool
def hold_medication(patient_id: str, drug: str) -> str:
    """Write a medication hold to the record."""
    RECORD.append((patient_id, drug))
    return "hold written"


ask_clinician = FunctionTool(
    name="ask_clinician", description="Ask the responsible clinician a question (host-owned).", func=None,
    input_model={"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]})


class Scripted(FunctionInvocationLayer, BaseChatClient):
    def __init__(self):
        super().__init__()
        self.calls = 0

    async def _inner_get_response(self, *, messages, stream, options, **kwargs):
        self.calls += 1
        if self.calls == 1:
            return ChatResponse(messages=[Message(role="assistant", contents=[
                Content.from_function_call(call_id="c1", name="ask_clinician",
                                           arguments='{"question": "K+ 6.1. Safe to hold lisinopril?"}'),
                Content.from_function_call(call_id="c2", name="hold_medication",
                                           arguments='{"patient_id": "pt-123", "drug": "lisinopril"}'),
            ])], response_id="r1")
        return ChatResponse(messages=[Message(role="assistant", contents=["Lisinopril held."])], response_id=f"r{self.calls}")


def pending(resp):
    return [(c.name, c.call_id) for c in resp.user_input_requests]


async def run(with_session):
    RECORD.clear()
    client = Scripted()
    agent = Agent(client=client, tools=[ask_clinician, hold_medication])
    session = agent.create_session() if with_session else None
    kw = {"session": session} if session is not None else {}
    try:
        r = await agent.run("Review pt-123 potassium.", **kw)
    except Exception as e:  # noqa: BLE001
        print(f"  session={with_session}: raised {type(e).__name__}: {str(e).splitlines()[0][:120]}")
        return
    label = "with AgentSession" if with_session else "no session      "
    print(f"  {label}: shown to the human={pending(r)} | model calls={client.calls} | "
          f"writes before the human answers={len(RECORD)} {RECORD}")
    if not r.user_input_requests:
        return
    # The clinician answers the question: the host returns the function result for c1.
    answer = Message(role="tool", contents=[Content.from_function_result(call_id="c1", result="No. Do not hold; recheck K+ first.")])
    try:
        r2 = await agent.run(answer, **kw)
        print(f"  {label}: clinician answered 'No. Do not hold' -> model calls={client.calls} | "
              f"writes={len(RECORD)} | final={r2.text!r}")
    except Exception as e:  # noqa: BLE001
        print(f"  {label}: answering raised {type(e).__name__}: {str(e).splitlines()[0][:140]} | writes={len(RECORD)}")


if __name__ == "__main__":
    print(f"agent-framework-core {VERSION}")
    asyncio.run(run(False))
    asyncio.run(run(True))
