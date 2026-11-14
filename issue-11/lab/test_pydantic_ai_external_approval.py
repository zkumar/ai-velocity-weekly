"""Mechanism of the week. pydantic-ai 2.66.0, 2.67.0 and 2.68.0, no model key.

A discharge agent has one tool it does not execute itself: `discharge_patient` is an *external*
tool, carried out by the EHR integration after the run returns the call. A policy capability
gates it: its `after_tool_validate` hook raises `ApprovalRequired` so a clinician signs off first.
The scripted model (`FunctionModel`) calls the tool. The question is what the run hands back.

Observed: on 2.66.0 the gated call is filed with the plain external calls, `approvals` is empty
and the gate's metadata is gone, so the stand-in executor below writes the discharge; on 2.67.0
and 2.68.0 (#12958) the run raises `UserError` before anything is handed out.

The "EHR integration" is `execute_external()`: it does what an external executor does, which is
run every call in `DeferredToolRequests.calls`, and it appends one row per call to RECORD.
"""
import asyncio
import os

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

import pydantic_ai
from pydantic_ai import Agent
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.exceptions import ApprovalRequired, UserError
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.tools import DeferredToolRequests, ToolDefinition
from pydantic_ai.toolsets import ExternalToolset

RECORD: list[str] = []


class DischargeNeedsSignoff(AbstractCapability[None]):
    """Policy: a discharge always waits for a clinician. Written once, applied to every tool by name."""

    async def after_tool_validate(self, ctx, *, call, tool_def, args):  # noqa: ANN001
        if tool_def.name == "discharge_patient":
            raise ApprovalRequired(metadata={"policy": "discharge-needs-signoff", "requested_by": "ward-agent"})
        return args


ehr = ExternalToolset([
    ToolDefinition(
        name="discharge_patient",
        description="Discharge a patient. Executed by the EHR integration outside the agent run.",
        parameters_json_schema={"type": "object", "properties": {"mrn": {"type": "string"}}, "required": ["mrn"]},
    )
])


def scripted(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """The model: asks for the discharge once, then closes the turn."""
    if len(messages) == 1:
        return ModelResponse(parts=[ToolCallPart("discharge_patient", {"mrn": "MRN-123"}, tool_call_id="call-1")])
    return ModelResponse(parts=[TextPart("Done.")])


def execute_external(requests: DeferredToolRequests) -> None:
    """What an external executor does with `calls`: run them. It never sees `approvals`."""
    for call in requests.calls:
        RECORD.append(f"DISCHARGED {call.args_as_dict().get('mrn')} via {call.tool_name} (call {call.tool_call_id})")


async def main() -> None:
    agent = Agent(
        FunctionModel(scripted),
        toolsets=[ehr],
        capabilities=[DischargeNeedsSignoff()],
        output_type=[str, DeferredToolRequests],
    )
    print(f"pydantic-ai {pydantic_ai.__version__}")
    try:
        result = await agent.run("Discharge MRN 123 to home with the new anticoagulant.")
    except UserError as e:
        print(f"UserError before anything was handed out: {e}")
        print(f"calls handed to the executor: 0   approvals waiting: 0   metadata keys: 0   rows written: {len(RECORD)}")
        return
    out = result.output
    if isinstance(out, DeferredToolRequests):
        execute_external(out)
        print(f"calls handed to the executor: {len(out.calls)}   approvals waiting: {len(out.approvals)}   "
              f"metadata keys: {len(out.metadata)}   rows written: {len(RECORD)}")
        for row in RECORD:
            print(f"  record: {row}")
    else:
        print(f"text output (no deferred requests): {out!r}   rows written: {len(RECORD)}")


asyncio.run(main())
