"""Second part of the mechanism. pydantic-ai 2.68.0 (#12757), no model key.

2.68.0 moves the question inside the run. `RequestInput(ask=...)` hands a resume token to whoever
will answer, the run suspends, and `resolve_external_event(token, DeferredToolResults(...))`
resumes it, with an `answered_by` field naming who answered. This script counts what the run
records about the answer: who answered on the event stream, who answered in the message history,
and whether a result guard (`after_tool_execute`) saw the human's free-text answer.

A second answer is sent with `answered_by` set to a name nobody authorised; the framework's own
docstring says it does not check it. On 2.66.0 and 2.67.0 the import fails and the script says so.
"""
import asyncio
import json
import os

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

import pydantic_ai
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import (DeferredToolRequestsEvent, DeferredToolResultsEvent, ModelMessage, ModelResponse,
                                  TextPart, ToolCallPart, ToolReturn)
from pydantic_ai.models.function import AgentInfo, DeltaToolCall, FunctionModel

print(f"pydantic-ai {pydantic_ai.__version__}")
try:
    from pydantic_ai.capabilities import RequestInput
    from pydantic_ai.external_events import resolve_external_event
    from pydantic_ai.exceptions import CallDeferred
    from pydantic_ai.tools import DeferredToolRequests, DeferredToolResults
    CallDeferred(kind="question")
    DeferredToolResults(answered_by={})
except (ImportError, TypeError) as e:
    print(f"not available on this release: {type(e).__name__}: {e}")
    raise SystemExit(0)

ANSWERER = os.environ.get("LAB_ANSWERER", "dr.okafor@hospital.example")
RECORD: list[str] = []


def scripted(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """The model: one question and one order in the first turn, then a closing line."""
    if len(messages) == 1:
        return ModelResponse(parts=[
            ToolCallPart("ask_pharmacist", {"question": "Any interaction with the current list?"}, tool_call_id="q-1"),
            ToolCallPart("place_order", {"mrn": "MRN-123", "drug": "apixaban 5 mg bd"}, tool_call_id="o-1"),
        ])
    return ModelResponse(parts=[TextPart("Order placed after the pharmacist agreed.")])


async def scripted_stream(messages: list[ModelMessage], info: AgentInfo):
    """The same script, streamed, which is what an event_stream_handler asks the model for."""
    if len(messages) == 1:
        yield {0: DeltaToolCall(name="ask_pharmacist", json_args=json.dumps({"question": "Any interaction with the current list?"}), tool_call_id="q-1"),
               1: DeltaToolCall(name="place_order", json_args=json.dumps({"mrn": "MRN-123", "drug": "apixaban 5 mg bd"}), tool_call_id="o-1")}
    else:
        yield "Order placed after the pharmacist agreed."


agent = Agent(FunctionModel(scripted, stream_function=scripted_stream))


@agent.tool
def ask_pharmacist(ctx: RunContext[None], question: str) -> str:
    """Ask the on-call pharmacist a free-text question; the answer comes from outside the run."""
    raise CallDeferred(kind="question", metadata={"question": question})


@agent.tool(requires_approval=True)
def place_order(ctx: RunContext[None], mrn: str, drug: str) -> str:
    """Place a medication order. Needs approval."""
    RECORD.append(f"ORDER {drug} for {mrn}")
    return f"order placed: {drug} for {mrn}"


class RedactPhi(AbstractCapability[None]):
    """A result guard. Whatever comes back through a tool, including a person's typed answer, is scrubbed."""
    seen = 0

    async def after_tool_execute(self, ctx, *, call, tool_def, args, result):  # noqa: ANN001
        if isinstance(result, str) and "MRN 123" in result:
            RedactPhi.seen += 1
            return result.replace("MRN 123", "MRN ***")
        return result


EVENT_ANSWERED_BY: dict[str, str] = {}


async def ask(ctx: RunContext[None], requests: DeferredToolRequests, token: str) -> None:
    """Hand the token out. Here a task answers 50 ms later; in production a Slack bot or an inbox does."""
    for call in [*requests.approvals, *requests.calls]:
        print(f"  pending: {call.tool_name} kind={requests.kind(call.tool_call_id)}")
    print(f"  resume token handed out ({len(token)} chars); the run is now waiting")

    async def answer_later() -> None:
        await asyncio.sleep(0.05)
        every = [*requests.approvals, *requests.calls]
        decision = DeferredToolResults(
            approvals={c.tool_call_id: True for c in requests.approvals},
            calls={c.tool_call_id: ToolReturn(return_value="Yes, go ahead. Patient is MRN 123.") for c in requests.calls},
            answered_by={c.tool_call_id: ANSWERER for c in every},
        )
        resolve_external_event(token, decision)

    asyncio.get_running_loop().create_task(answer_later())
    return None  # None means: wait for the token


async def on_event(ctx: RunContext[None], stream) -> None:  # noqa: ANN001
    async for event in stream:
        if isinstance(event, DeferredToolRequestsEvent):
            print(f"  event DeferredToolRequestsEvent: approvals={[c.tool_name for c in event.requests.approvals]} "
                  f"questions={[c.tool_name for c in event.requests.calls]}")
        if isinstance(event, DeferredToolResultsEvent):
            EVENT_ANSWERED_BY.update(event.results.answered_by)
            print(f"  event DeferredToolResultsEvent: answered_by={sorted(set(event.results.answered_by.values()))}")


async def main() -> None:
    result = await agent.run(
        "Start apixaban for MRN 123 if the pharmacist agrees.",
        capabilities=[RedactPhi(), RequestInput(ask=ask)],
        event_stream_handler=on_event,
    )
    msgs = result.all_messages()
    history_mentions = sum(1 for m in msgs for p in m.parts if ANSWERER in repr(p))
    returns = [p for m in msgs for p in m.parts if p.part_kind == "tool-return"]
    for p in returns:
        print(f"  history tool-return {p.tool_name}: {p.content!r}")
    print(f"answered by {ANSWERER!r}: accepted without a check, {len(EVENT_ANSWERED_BY)} ids on the event, "
          f"{history_mentions} mentions in message history; redaction guard saw the human's answer {RedactPhi.seen} time(s); "
          f"rows written: {len(RECORD)}")


asyncio.run(main())
