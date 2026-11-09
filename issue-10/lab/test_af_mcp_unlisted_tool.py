"""Mechanism of the week, Issue 10: the tool nobody listed.

A ward-assistant agent reaches a pharmacy MCP server through Agent Framework's local MCP tool.
The approval policy names the write the team knew about (place_order: always ask) and the read
(read_chart: never ask). The server also offers discontinue_order, a write added later, which the
policy names in neither list. A scripted chat client (no model, no key) asks for one tool call and
then closes the turn with whatever the tool returned. The "system of record" is a JSON-lines file
the server appends to; the script counts its rows, not the model's words.

LAB_CASE selects the policy and the call:
  listed      lists only; the model calls place_order (the control: a listed write)
  unlisted    lists only; the model calls discontinue_order
  default     lists plus "default": "always_require"; the model calls discontinue_order
  approved    as default, then the clinician approves the pending request
  joined      always_require_approval given as one comma-joined string instead of a list
"""
import asyncio
import json
import os
import sys
import tempfile
import warnings
from importlib.metadata import version

from agent_framework import (Agent, BaseChatClient, ChatResponse, Content, FunctionInvocationLayer,
                             MCPStdioTool, Message)

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.environ.get("LAB_CASE", "unlisted")
LISTS = {"always_require_approval": ["place_order"], "never_require_approval": ["read_chart"]}
POLICY = {
    "listed": LISTS,
    "unlisted": LISTS,
    "default": {**LISTS, "default": "always_require"},
    "approved": {**LISTS, "default": "always_require"},
    "joined": {"always_require_approval": "place_order,discontinue_order", "never_require_approval": ["read_chart"]},
}[CASE]
CALL = (("place_order", {"patient_id": "pt-123", "drug": "apixaban", "dose": "5 mg"}) if CASE == "listed"
        else ("discontinue_order", {"patient_id": "pt-123", "order_id": "order-1"}))


class ScriptedChat(FunctionInvocationLayer, BaseChatClient):
    """Stands in for the model: one function call, then one closing sentence from the tool result."""

    def __init__(self) -> None:
        super().__init__()
        self.turns = 0

    async def _inner_get_response(self, *, messages, stream, options, **kwargs):
        self.turns += 1
        results = [c for m in messages for c in m.contents if c.type == "function_result"]
        if not results:
            call = Content.from_function_call(call_id="call-1", name=CALL[0], arguments=json.dumps(CALL[1]))
            return ChatResponse(messages=[Message(role="assistant", contents=[call])], response_id="r1")
        return ChatResponse(messages=[Message(role="assistant", contents=[f"Done. {results[-1].result}"])],
                            response_id="r2")


def rows(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


async def main() -> None:
    record = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False).name
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        pharmacy = MCPStdioTool(name="pharmacy", command=sys.executable,
                                args=[os.path.join(HERE, "pharmacy_server.py")],
                                env={**os.environ, "LAB_RECORD": record}, approval_mode=POLICY)
    chat = ScriptedChat()
    async with pharmacy:
        agent = Agent(client=chat, name="ward-assistant", instructions="Act on the clinician's request.",
                      tools=pharmacy)
        session = agent.create_session() if hasattr(agent, "create_session") else agent.get_new_session()
        resolved = {f.name: f.approval_mode for f in pharmacy.functions}
        reply = await agent.run("Stop the apixaban for pt-123." if CASE != "listed" else "Start apixaban for pt-123.",
                                session=session)
        asked = [c for c in reply.user_input_requests if c.type == "function_approval_request"]
        rows_before = len(rows(record))
        text = reply.text
        if CASE == "approved" and asked:
            answer = asked[0].to_function_approval_response(approved=True)
            reply = await agent.run(Message(role="user", contents=[answer]), session=session)
            text = reply.text
    final = rows(record)
    os.unlink(record)
    print(f"agent-framework-core {version('agent-framework-core')}  case={CASE}  call={CALL[0]}")
    print(f"  policy passed          : {json.dumps(POLICY)}")
    print(f"  resolved per tool      : {json.dumps(resolved, sort_keys=True)}")
    print(f"  warnings at construct  : {len(caught)}" + "".join(f"\n      {w.category.__name__}: {w.message}" for w in caught))
    print(f"  approval requests      : {len(asked)}" + (f" ({asked[0].function_call.name})" if asked else ""))
    print(f"  rows before any answer : {rows_before}")
    print(f"  rows at end            : {len(final)}" + (f"  {json.dumps(final[-1])}" if final else ""))
    print(f"  model turns            : {chat.turns}")
    print(f"  final text             : {text!r}")


asyncio.run(main())
