"""LangChain 1.4.2: when a clinician edits a tool call, which record says what ran?

Synthetic data, scripted chat model, InMemorySaver checkpointer, no API key.
run_all.sh runs this under langchain 1.4.1 and 1.4.2.

The model proposes metformin 1000 mg; the pharmacist edits it to 500 mg and approves.
We print four places an auditor might look: the AIMessage tool call in the transcript,
the arguments the tool actually received, the ToolMessage text, and the checkpoint state.
Then the same with edit_notice=None (1.4.2 only).
"""
import json
from importlib.metadata import version
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

RECEIVED: list[dict] = []


@tool
def write_medication_request(patient_id: str, rxnorm: str, dose_mg: int) -> str:
    """Write a MedicationRequest to the FHIR server."""
    RECEIVED.append({"patient_id": patient_id, "rxnorm": rxnorm, "dose_mg": dose_mg})
    return f"MedicationRequest written: {dose_mg} mg"


class Scripted(BaseChatModel):
    turns: list[AIMessage]
    i: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools: Any, **kw: Any):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kw) -> ChatResult:
        msg = self.turns[min(self.i, len(self.turns) - 1)]
        self.i += 1
        return ChatResult(generations=[ChatGeneration(message=msg)])


PROPOSED = {"patient_id": "pt-123", "rxnorm": "860975", "dose_mg": 1000}
EDITED = {"patient_id": "pt-123", "rxnorm": "860975", "dose_mg": 500}


def run(edit_notice_kw: dict, label: str):
    RECEIVED.clear()
    model = Scripted(turns=[
        AIMessage(content="", tool_calls=[{"name": "write_medication_request", "args": PROPOSED, "id": "call_1"}]),
        AIMessage(content="Order placed."),
    ])
    hitl = HumanInTheLoopMiddleware(
        interrupt_on={"write_medication_request": {"allowed_decisions": ["approve", "edit", "reject"]}},
        **edit_notice_kw)
    agent = create_agent(model=model, tools=[write_medication_request], middleware=[hitl],
                         checkpointer=InMemorySaver())
    cfg = {"configurable": {"thread_id": "t1"}}
    agent.invoke({"messages": [("user", "Start metformin for pt-123")]}, cfg)
    out = agent.invoke(Command(resume={"decisions": [{"type": "edit", "edited_action": {
        "name": "write_medication_request", "args": EDITED}}]}), cfg)
    msgs = out["messages"]
    ai = next(m for m in msgs if isinstance(m, AIMessage) and m.tool_calls)
    tm = next(m for m in msgs if isinstance(m, ToolMessage))
    state = agent.get_state(cfg).values
    print(f"  {label}")
    print(f"    transcript AIMessage.tool_calls args : {ai.tool_calls[0]['args']}")
    print(f"    tool actually received               : {RECEIVED}")
    print(f"    ToolMessage.content                  : {tm.content!r}")
    print(f"    invoke() output keys                 : {sorted(out.keys())}")
    print(f"    checkpoint hitl_edited_tool_calls    : {state.get('hitl_edited_tool_calls', 'absent')}")
    agree = ai.tool_calls[0]["args"] == RECEIVED[0]
    print(f"    transcript args == executed args     : {agree}")


print(f"langchain {version('langchain')}")
run({}, "edit decision, default settings")
if version("langchain") >= "1.4.2":
    run({"edit_notice": None}, "edit decision, edit_notice=None")
