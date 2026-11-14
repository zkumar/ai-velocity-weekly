"""Supporting check. langgraph 1.2.20 against 1.2.21, no model.

A parent graph's node invokes a child graph it looks up at runtime, the way a tool such as
deepagents' `task` invokes a sub-agent. The child checkpoints under its own namespace on the same
thread. The question: can the parent's `get_state` read the child's record by that namespace?
1.2.20 raises because the child is not a declared subgraph; 1.2.21 reads it with the parent's
channels, so keys only the child has are invisible, and `update_state` still refuses.
"""
import importlib.metadata as md
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class ChildState(TypedDict):
    messages: list
    pharmacist_note: str


class ParentState(TypedDict):
    messages: list
    approved: bool


def child_node(state: ChildState):
    return {"messages": state["messages"] + ["pharmacist agent: interaction checked"], "pharmacist_note": "child-only key"}


child = StateGraph(ChildState).add_node("check", child_node).add_edge(START, "check").add_edge("check", END).compile()
SUBAGENTS = {"pharmacist": child}  # looked up at runtime: langgraph cannot see this as a subgraph


def task_node(state: ParentState, config):
    out = SUBAGENTS["pharmacist"].invoke({"messages": state["messages"], "pharmacist_note": ""}, config)
    return {"messages": out["messages"], "approved": True}


parent = StateGraph(ParentState).add_node("task", task_node).add_edge(START, "task").add_edge("task", END).compile(checkpointer=InMemorySaver())
cfg = {"configurable": {"thread_id": "t1"}}
parent.invoke({"messages": ["start apixaban"], "approved": False}, cfg)

print(f"langgraph {md.version('langgraph')}")
print(f"declared subgraphs: {[ns for ns, _ in parent.get_subgraphs(recurse=True)]}")
namespaces = sorted(parent.checkpointer.storage["t1"].keys())
child_ns = next(ns for ns in namespaces if ns)
print(f"checkpoint namespaces on the thread: {[ns.split(':')[0] + (':<task id>' if ns else '') for ns in namespaces]}")
sub = {"configurable": {"thread_id": "t1", "checkpoint_ns": child_ns}}
readable = history = 0
try:
    snap = parent.get_state(sub)
    readable = 1
    print(f"get_state(child ns): values={snap.values}  ('pharmacist_note' present: {'pharmacist_note' in snap.values})")
    history = len(list(parent.get_state_history(sub)))
    print(f"get_state_history(child ns): {history} snapshots")
except Exception as e:  # noqa: BLE001
    print(f"get_state(child ns) raised {type(e).__name__}: {e}")
try:
    parent.update_state(sub, {"approved": False})
    print("update_state(child ns): accepted")
except Exception as e:  # noqa: BLE001
    print(f"update_state(child ns) raised {type(e).__name__}: {str(e)[:120]}")
print(f"child record readable from the parent: {readable}   snapshots: {history}")
