"""AI Velocity Weekly 09, supporting check.

The checkpoint a client resumes from, LangGraph 1.2.17 against 1.2.18 (#9409).

Three plain-Python nodes, no model: draft_order writes a draft, review is where a pharmacist
would look at it, write_order commits. The graph is compiled with interrupt_after=["draft_order"]
so the run stops at the pause, and the caller consumes stream_mode="checkpoints", the way an
approval UI that drives its "resume" button off the checkpoint stream does.

Question: is the checkpoint the run stopped on emitted on that stream, and if the client resumes
from the last checkpoint it saw, does draft_order run again?
"""
from importlib.metadata import version
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

RUNS = {"draft_order": 0, "write_order": 0}
RECORD: list[str] = []


class S(TypedDict, total=False):
    draft: str
    written: bool


def draft_order(state: S) -> S:
    RUNS["draft_order"] += 1
    return {"draft": f"apixaban 5 mg oral BID for pt-123 (draft #{RUNS['draft_order']})"}


def write_order(state: S) -> S:
    RUNS["write_order"] += 1
    RECORD.append(state["draft"])
    return {"written": True}


g = StateGraph(S)
g.add_node("draft_order", draft_order)
g.add_node("write_order", write_order)
g.add_edge(START, "draft_order")
g.add_edge("draft_order", "write_order")
g.add_edge("write_order", END)
graph = g.compile(checkpointer=InMemorySaver(), interrupt_after=["draft_order"])

config = {"configurable": {"thread_id": "t1"}}
seen: list[str] = []
for ev in graph.stream({}, config, stream_mode="checkpoints"):
    seen.append(ev["config"]["configurable"]["checkpoint_id"])

paused = graph.get_state(config)
paused_id = paused.config["configurable"]["checkpoint_id"]
print(f"langgraph {version('langgraph')}")
print(f"checkpoints streamed before the pause: {len(seen)}")
print(f"last streamed checkpoint is the paused one: {seen[-1] == paused_id}")
print(f"draft_order ran: {RUNS['draft_order']}; next on the paused state: {list(paused.next)}")

# the client resumes from the last checkpoint it was shown
resume_from = {"configurable": {"thread_id": "t1", "checkpoint_id": seen[-1]}}
graph.invoke(None, resume_from)
print(f"after resume from last streamed checkpoint: draft_order ran {RUNS['draft_order']} time(s), "
      f"write_order ran {RUNS['write_order']} time(s)")
print(f"record: {RECORD}")
