"""AI Velocity Weekly 02, lab 5.1.

Microsoft Agent Framework 1.18.0: the tool loop's wall-clock budget
(``max_duration_seconds``, PR #7772) keeps counting while a clinician
decides on an approval. This script shows, with a scripted model and
no API key, what happens to a FHIR write that is approved after the
budget has run out, and whether the budget survives session
serialisation (the clinician's answer usually arrives in a different
request, often a different worker).

Run:  pip install "agent-framework-core==1.18.0"
      python test_af_duration_budget.py
Synthetic data only. No FHIR server is contacted.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import MutableSequence
from typing import Annotated, Any

from agent_framework import (
    Agent,
    AgentSession,
    BaseChatClient,
    ChatResponse,
    Content,
    FunctionInvocationLayer,
    Message,
    ToolApprovalMiddleware,
    tool,
)

WRITES: list[dict[str, Any]] = []


@tool(approval_mode="always_require")
def write_medication_order(
    patient_id: Annotated[str, "FHIR Patient id"],
    rxnorm: Annotated[str, "RxNorm code"],
) -> str:
    """Write a MedicationRequest to the FHIR server (simulated)."""
    WRITES.append({"patient_id": patient_id, "rxnorm": rxnorm, "at": time.time()})
    return f"MedicationRequest written for {patient_id} ({rxnorm})"


class ScriptedClient(FunctionInvocationLayer, BaseChatClient):
    """A chat client whose 'model' follows a script. Composes the shipped
    FunctionInvocationLayer, which is where the approval gate and the
    duration budget live."""

    def __init__(self) -> None:
        super().__init__()
        self.turns: list[ChatResponse] = []
        self.seen_tool_choice: list[Any] = []

    async def _inner_get_response(
        self, *, messages: MutableSequence[Message], stream: bool, options: dict[str, Any], **kwargs: Any
    ) -> ChatResponse:
        if stream:
            raise NotImplementedError("scripted client is non-streaming")
        self.seen_tool_choice.append(options.get("tool_choice"))
        if options.get("tool_choice") == "none":
            # what a real model does when tools are withdrawn: answers in text
            return ChatResponse(messages=Message(role="assistant", contents=["Order placed."]))
        if self.turns:
            return self.turns.pop(0)
        return ChatResponse(messages=Message(role="assistant", contents=["Done."]))


def model_asks_for_the_write() -> ChatResponse:
    call = Content.from_function_call(
        call_id="call_provider_1",
        name="write_medication_order",
        arguments=json.dumps({"patient_id": "pt-123", "rxnorm": "197361"}),
    )
    return ChatResponse(messages=[Message(role="assistant", contents=[call])], finish_reason="tool_calls")


async def scenario(budget_seconds: float, clinician_takes_seconds: float, harness: bool) -> None:
    WRITES.clear()
    client = ScriptedClient()
    client.function_invocation_configuration["max_duration_seconds"] = budget_seconds
    client.turns = [model_asks_for_the_write()]
    # ToolApprovalMiddleware is what carries the budget clock across the approval round trip
    middleware = [ToolApprovalMiddleware()] if harness else []
    agent = Agent(client=client, name="orders", tools=[write_medication_order], middleware=middleware)

    # Request 1: model asks for the write, the gate produces an approval request.
    session = AgentSession()
    r1 = await agent.run("Start metformin 500 mg for pt-123", session=session)
    req = next(c for m in r1.messages for c in m.contents if c.type == "function_approval_request")
    budget = session.state.get("_function_invocation_budget_state")
    print(f"  approval request {req.id}; budget in session after request 1: {budget}")

    # The session goes to the store while the clinician reads the order.
    blob = json.dumps(session.to_dict())
    time.sleep(clinician_takes_seconds)

    # Request 2: session restored, clinician approves.
    session2 = AgentSession.from_dict(json.loads(blob))
    answer = Message(role="user", contents=[req.to_function_approval_response(approved=True)])
    r2 = await agent.run(answer, session=session2)
    results = [c for m in r2.messages for c in m.contents if c.type == "function_result"]
    print(f"  tool_choice seen by the model per call: {client.seen_tool_choice}")
    print(f"  FHIR writes performed: {len(WRITES)}")
    print(f"  function_result returned to model: {[str(r.result)[:60] for r in results]}")
    print(f"  final assistant text: {r2.text!r}")
    print(f"  budget state still in session: {'_function_invocation_budget_state' in session2.state}")


async def main() -> None:
    print("Scenario A: 30 s budget, clinician answers in 1 s, ToolApprovalMiddleware on")
    await scenario(budget_seconds=30.0, clinician_takes_seconds=1.0, harness=True)
    print("\nScenario B: 2 s budget, clinician answers in 3 s, ToolApprovalMiddleware on")
    await scenario(budget_seconds=2.0, clinician_takes_seconds=3.0, harness=True)
    print("\nScenario C: 2 s budget, clinician answers in 3 s, bare Agent (no harness middleware)")
    await scenario(budget_seconds=2.0, clinician_takes_seconds=3.0, harness=False)
    print("\nperf_counter on this host:", time.get_clock_info("perf_counter").implementation)


if __name__ == "__main__":
    asyncio.run(main())
