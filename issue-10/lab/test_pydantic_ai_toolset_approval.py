"""Supporting check, Issue 10: a toolset that says every tool needs approval, and a Tool it did not cover.

FunctionToolset(..., requires_approval=True) is the pydantic-ai way to say "every tool in this
set waits for a person". Two write tools are registered: one as a plain function, one as a prebuilt
Tool(...) instance, which is how tools arrive from a shared library. FunctionModel stands in for the
model (no key) and calls both. The script counts which bodies ran before anyone approved anything.
"""
import asyncio
from importlib.metadata import version

from pydantic_ai import Agent, DeferredToolRequests, Tool
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.toolsets import FunctionToolset

RECORD: list[str] = []


def place_order(patient_id: str, drug: str) -> str:
    """Place a medication order."""
    RECORD.append(f"place_order {drug} {patient_id}")
    return f"ORDER PLACED {drug} for {patient_id}"


def discontinue_order(patient_id: str, order_id: str) -> str:
    """Discontinue an active medication order."""
    RECORD.append(f"discontinue_order {order_id} {patient_id}")
    return f"ORDER DISCONTINUED {order_id} for {patient_id}"


def scripted(messages, info):
    returned = [p for m in messages for p in m.parts if isinstance(p, ToolReturnPart)]
    if returned:
        return ModelResponse(parts=[TextPart("Done. " + "; ".join(str(p.content) for p in returned))])
    return ModelResponse(parts=[
        ToolCallPart("place_order", {"patient_id": "pt-123", "drug": "apixaban"}, tool_call_id="call-1"),
        ToolCallPart("discontinue_order", {"patient_id": "pt-123", "order_id": "order-1"}, tool_call_id="call-2"),
    ])


async def main() -> None:
    pharmacy = FunctionToolset([place_order, Tool(discontinue_order)], requires_approval=True)
    agent = Agent(FunctionModel(scripted), toolsets=[pharmacy], output_type=[str, DeferredToolRequests])
    result = await agent.run("Start apixaban and stop order-1 for pt-123.")
    out = result.output
    waiting = [c.tool_name for c in out.approvals] if isinstance(out, DeferredToolRequests) else []
    print(f"pydantic-ai-slim {version('pydantic-ai-slim')}")
    print(f"  toolset requires_approval=True, tools: place_order (function), discontinue_order (Tool instance)")
    print(f"  waiting for approval   : {len(waiting)} {waiting}")
    print(f"  ran before any approval: {len(RECORD)} {RECORD}")
    print(f"  output type            : {type(out).__name__}")


asyncio.run(main())
