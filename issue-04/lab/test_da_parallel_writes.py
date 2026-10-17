"""deepagents 0.7.15 against 0.7.16: an approved write that executes zero times.

Commit 2e2ee91 (#6446, 20 Sept 2026), "fix(sdk): reject parallel same-file edits", adds
_parallel_file_mutation_error() to FilesystemMiddleware.wrap_tool_call. When one model
response carries two mutations of the same path, every call after the first is answered
with a ToolMessage(status="error") and never runs.

Two runs, scripted model, no API key:
  1. No approval gate. The model writes a care plan, then in ONE response edits the dose
     and, in parallel, rewrites the plan to hold the drug. Which content survives?
  2. HumanInTheLoop on write_file. The reviewer is shown both writes and approves both.
     How many of the two approved writes execute?

Synthetic data only. The "record" is deepagents' in-state virtual filesystem.
"""
import importlib.metadata as md

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from deepagents import create_deep_agent

VERSION = md.version("deepagents")
PLAN = "/patients/pt-123/plan.md"


class Scripted(GenericFakeChatModel):
    """GenericFakeChatModel that ignores bind_tools so create_deep_agent can attach tools."""

    def bind_tools(self, tools, **kwargs):
        return self


def tool_messages(out):
    return [m for m in out["messages"] if isinstance(m, ToolMessage)]


def file_content(out):
    f = (out.get("files") or {}).get(PLAN)
    return f.get("content") if isinstance(f, dict) else f


def run_no_gate():
    script = iter([
        AIMessage("", tool_calls=[{"name": "write_file", "id": "c1",
                                    "args": {"file_path": PLAN, "content": "Plan: start lisinopril 10 mg daily\n"}}]),
        # one response, two mutations of the same path
        AIMessage("", tool_calls=[
            {"name": "edit_file", "id": "c2",
             "args": {"file_path": PLAN, "old_string": "10 mg", "new_string": "20 mg"}},
            {"name": "write_file", "id": "c3",
             "args": {"file_path": PLAN, "content": "Plan: HOLD lisinopril, K+ 6.1 mmol/L, repeat BMP\n"}},
        ]),
        AIMessage("Plan updated."),
    ])
    agent = create_deep_agent(model=Scripted(messages=script), tools=[])
    out = agent.invoke({"messages": [{"role": "user", "content": "Update the plan for pt-123."}]})
    print(f"  run 1, no gate: model response 2 carried c2 edit_file(10->20 mg) and c3 write_file(HOLD)")
    for m in tool_messages(out):
        print(f"    {m.tool_call_id} status={m.status:5s} {str(m.content)[:88]!r}")
    print(f"    final file: {file_content(out)!r}")
    print(f"    model said: {out['messages'][-1].content!r}")
    return out


def run_with_gate():
    script = iter([
        AIMessage("", tool_calls=[
            {"name": "write_file", "id": "c1", "args": {"file_path": PLAN, "content": "Plan A: continue lisinopril 20 mg\n"}},
            {"name": "write_file", "id": "c2", "args": {"file_path": PLAN, "content": "Plan B: HOLD lisinopril, K+ 6.1\n"}},
        ]),
        AIMessage("Both plans written."),
    ])
    agent = create_deep_agent(model=Scripted(messages=script), tools=[],
                              interrupt_on={"write_file": True}, checkpointer=InMemorySaver())
    cfg = {"configurable": {"thread_id": "pt-123"}}
    out = agent.invoke({"messages": [{"role": "user", "content": "Write the plan for pt-123."}]}, cfg)
    reqs = out["__interrupt__"][0].value["action_requests"]
    print(f"  run 2, HITL on write_file: reviewer shown {len(reqs)} action requests: "
          f"{[r['args']['content'].strip() for r in reqs]}")
    out = agent.invoke(Command(resume={"decisions": [{"type": "approve"}, {"type": "approve"}]}), cfg)
    executed = sum(1 for m in tool_messages(out) if m.status != "error")
    for m in tool_messages(out):
        print(f"    {m.tool_call_id} status={m.status:5s} {str(m.content)[:88]!r}")
    print(f"    approved writes: 2 | executed writes: {executed} | final file: {file_content(out)!r}")
    print(f"    model said: {out['messages'][-1].content!r}")
    return executed, file_content(out)


if __name__ == "__main__":
    print(f"deepagents {VERSION} (langgraph {md.version('langgraph')}, langchain-core {md.version('langchain-core')})")
    run_no_gate()
    executed, final = run_with_gate()
    print(f"  SUMMARY {VERSION}: approved=2 executed={executed} record={final.strip()!r}")
