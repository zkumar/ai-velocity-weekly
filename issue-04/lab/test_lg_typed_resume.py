"""langgraph 1.2.11 against 1.2.12: a typed approval, and what the checkpoint keeps.

Commit 448a763 (#8886), shipped in 1.2.12 by 19273fa (#8987, 21 Sept 2026): interrupt() takes
response_schema. A Pydantic model, TypedDict or dataclass validates the resume value before the
node sees it; a JSON Schema dict is passed to clients "as-is, resume values are not validated".

Three resumes against a one-node approval gate, no model, no API key:
  1. Pydantic schema, resume {"action": "aprove"}  (typo, reviewer_id missing)
  2. Pydantic schema, resume {"action": "approve", "reviewer_id": "rn-42"}
  3. dict schema,     resume {"action": "aprove"}
Then: what did the checkpoint persist as the resume value?
"""
import importlib.metadata as md
from typing import Literal, TypedDict

from pydantic import BaseModel
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

VERSION = md.version("langgraph")


class Decision(BaseModel):
    action: Literal["approve", "reject"]
    reviewer_id: str


class S(TypedDict):
    note: str
    written: str
    decision: object


def build(schema):
    def gate(s):
        kw = {"response_schema": schema} if schema is not None else {}
        d = interrupt({"proposed_note": s["note"]}, **kw)
        act = d.action if isinstance(d, Decision) else d.get("action")
        return {"written": s["note"] if act == "approve" else "", "decision": repr(d)}
    g = StateGraph(S)
    g.add_node("gate", gate)
    g.add_edge(START, "gate")
    g.add_edge("gate", END)
    return g.compile(checkpointer=InMemorySaver())


def persisted_resume(app, cfg):
    """The raw resume write kept in the checkpoint's scratchpad, if any."""
    for snap in app.get_state_history(cfg):
        pw = snap.metadata.get("writes") if snap.metadata else None
        if pw:
            return pw
    return None


def resume(app, cfg, value, label):
    try:
        r = app.invoke(Command(resume=value), cfg)
        print(f"    {label}: committed | written={r.get('written')!r} | node received {r.get('decision')}")
    except Exception as e:  # noqa: BLE001
        first = str(e).splitlines()[0]
        print(f"    {label}: raised {type(e).__name__}: {first[:80]}")
    st = app.get_state(cfg)
    print(f"      state.next={st.next} | pending interrupts={sum(len(t.interrupts) for t in st.tasks)}")


if __name__ == "__main__":
    print(f"langgraph {VERSION}")
    note = "K+ 6.1 mmol/L, hold lisinopril, repeat BMP"
    try:
        app = build(Decision)
    except TypeError as e:
        raise SystemExit(f"  {e}")
    cfg = {"configurable": {"thread_id": "pydantic"}}
    try:
        out = app.invoke({"note": note, "written": "", "decision": None}, cfg)
    except TypeError as e:
        print(f"  interrupt(response_schema=...) -> TypeError: {e}")
        app0 = build(None)
        cfg0 = {"configurable": {"thread_id": "none"}}
        app0.invoke({"note": note, "written": "", "decision": None}, cfg0)
        resume(app0, cfg0, {"action": "aprove"}, "0 no schema, typo")
        print(f"  SUMMARY {VERSION}: no typed approvals; the typo is committed as a rejection")
        raise SystemExit(0)
    intr = out["__interrupt__"][0]
    print(f"  surfaced response_schema properties: {list((intr.response_schema or {}).get('properties', {}))}")
    resume(app, cfg, {"action": "aprove"}, "1 pydantic, typo")
    resume(app, cfg, {"action": "approve", "reviewer_id": "rn-42"}, "2 pydantic, valid")

    app2 = build({"type": "object", "required": ["action", "reviewer_id"],
                  "properties": {"action": {"enum": ["approve", "reject"]}, "reviewer_id": {"type": "string"}}})
    cfg2 = {"configurable": {"thread_id": "dict"}}
    app2.invoke({"note": note, "written": "", "decision": None}, cfg2)
    resume(app2, cfg2, {"action": "aprove"}, "3 dict schema, typo")
    print(f"  SUMMARY {VERSION}: pydantic schema rejects the typo and stays paused; dict schema commits it")
