"""pydantic-ai 2.52.0 against 2.53.0: two tool calls that share one tool_call_id.

PR #8782, first released in 2.53.0 (2 Oct 2026): "Raise UnexpectedModelBehavior instead of running
the wrong tool when function tool calls share a tool_call_id". Results are matched back to calls
by tool_call_id; in pydantic_ai/_tool_execution.py a batch with a repeated id now fails closed
before any call in it executes. On 2.52.0 the last call with that id won the binding.

One model response carries read_chart and submit_prior_auth, both with tool_call_id "call_1", as a
provider or gateway that reuses ids would send them. The script counts which tools ran and what
the model was told came back. Synthetic data only.

No API key: FunctionModel is pydantic-ai's own scripted model.
"""
import pydantic_ai
from pydantic_ai import Agent
from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

RAN = []


def model(messages, info: AgentInfo):
    if len(messages) == 1:
        return ModelResponse(parts=[
            ToolCallPart("read_chart", {"patient": "pt-123"}, tool_call_id="call_1"),
            ToolCallPart("submit_prior_auth", {"patient": "pt-123"}, tool_call_id="call_1"),
        ])
    returns = [(p.tool_name, str(p.content)[:40]) for m in messages if isinstance(m, ModelRequest)
               for p in m.parts if isinstance(p, ToolReturnPart)]
    print(f"  tool returns handed to the model: {returns}")
    return ModelResponse(parts=[TextPart("Chart read and prior authorisation submitted.")])


agent = Agent(FunctionModel(model))


@agent.tool_plain
def read_chart(patient: str) -> str:
    """Read the patient's chart."""
    RAN.append("read_chart")
    return "A1c 9.1%, metformin 2 g"


@agent.tool_plain
def submit_prior_auth(patient: str) -> str:
    """Submit a prior authorisation request."""
    RAN.append("submit_prior_auth")
    return "PA-0001 submitted"


if __name__ == "__main__":
    V = pydantic_ai.__version__
    print(f"pydantic-ai {V}")
    print("  model response carried: read_chart(call_1), submit_prior_auth(call_1)")
    try:
        out = agent.run_sync("work up the semaglutide PA for pt-123").output
        print(f"  model said: {out!r}")
        raised = "none"
    except Exception as e:  # noqa: BLE001
        raised = type(e).__name__
        print(f"  raised {raised}: {e}")
    print(f"  tools that ran: {RAN}")
    print(f"  SUMMARY {V}: read_chart={RAN.count('read_chart')} submit_prior_auth={RAN.count('submit_prior_auth')} raised={raised}")
