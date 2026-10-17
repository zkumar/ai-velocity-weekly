"""AI Velocity Weekly 01, lab 5.1 (rebuilt 12 Sept 2026).

LangChain 1.4.0 turns an MCP server's elicitation (SEP-2322,
InputRequiredResult) into a LangGraph interrupt. Here a FHIR MCP tool
refuses to write a MedicationRequest until a clinician signs; the run
parks in a checkpoint; the resume re-issues the whole tools/call with the
answers. No model is involved: a ToolNode stands in for the agent's tool
step and a hand-written AIMessage plays the model's tool call.

Run:  pip install "langchain[mcp]==1.4.0" langgraph fastmcp
      python test_lc_elicitation.py
Then break it: move WRITES.append above the guard in the tool and watch
the resume double-write.
"""

from __future__ import annotations

import asyncio
import json

from fastmcp import Context, FastMCP
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from mcp.types import (
    ElicitRequest,
    ElicitRequestFormParams,
    ElicitResult,
    InputRequiredResult,
    TextContent,
)

from langchain.mcp import MCPAdapter

WRITES: list[dict] = []
fhir = FastMCP("fhir")


@fhir.tool
async def create_medication_order(
    patient_id: str, rxnorm: str, ctx: Context
) -> list[TextContent] | InputRequiredResult:
    """Write a MedicationRequest. Asks the clinician to sign first."""
    answers = ctx.input_responses  # empty on the first round
    if not answers or "confirm" not in answers:  # guard BEFORE doing work: resume re-runs the call
        return InputRequiredResult(
            request_state="awaiting-signature",
            input_requests={
                "confirm": ElicitRequest(
                    method="elicitation/create",
                    params=ElicitRequestFormParams(
                        mode="form",
                        message=f"Sign MedicationRequest {rxnorm} for {patient_id}?",
                        requested_schema={
                            "type": "object",
                            "properties": {"signed": {"type": "boolean"}, "npi": {"type": "string"}},
                            "required": ["signed", "npi"],
                        },
                    ),
                )
            },
        )
    a = answers["confirm"]
    if not isinstance(a, ElicitResult) or a.action != "accept" or not a.content.get("signed"):
        return [TextContent(type="text", text="Order not written: clinician declined.")]
    WRITES.append({"patient_id": patient_id, "rxnorm": rxnorm, "npi": a.content["npi"]})
    return [TextContent(type="text", text=f"MedicationRequest written, signed by NPI {a.content['npi']}.")]


async def main() -> None:
    async with MCPAdapter(fhir) as adapter:  # a str target must be an http(s) URL; local servers go in as objects
        tools = await adapter.list_tools()

    graph = StateGraph(MessagesState)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "tools")
    graph.add_edge("tools", END)
    app = graph.compile(checkpointer=InMemorySaver())  # checkpointer is mandatory for interrupt/resume
    cfg = {"configurable": {"thread_id": "encounter-8812"}}

    # The "model" asks for the write.
    call = AIMessage(content="", tool_calls=[{
        "id": "call_1", "name": "create_medication_order",
        "args": {"patient_id": "pt-123", "rxnorm": "197361"}}])
    paused = await app.ainvoke({"messages": [call]}, cfg)
    q = paused["__interrupt__"][0].value
    print("interrupt payload:", json.dumps(q, default=str)[:300])
    print("writes before signature:", len(WRITES))

    # The clinician signs. Try {"action": "decline"} to see the refusal path.
    answer = {"action": "accept", "content": {"signed": True, "npi": "1234567893"}}
    done = await app.ainvoke(Command(resume={"responses": {q["requests"][0]["key"]: answer}}), cfg)
    print("tool result:", done["messages"][-1].content)
    print("writes after signature:", len(WRITES), WRITES)


if __name__ == "__main__":
    asyncio.run(main())
