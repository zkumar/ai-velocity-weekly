"""langgraph 1.2.12 against 1.2.13: what the paused thread says is still waiting.

PR #9103 (in 1.2.13, 5 Oct 2026) adds langgraph/pregel/_task_status.py as the single reader of
"which tasks are finished and which interrupts are pending". Before it, execution, snapshots and
resume validation each read the checkpoint's pending writes separately and could disagree.

A discharge packet with two parallel approval gates, no model, no API key:
  pharmacy  -> interrupt("pharmacy: approve apixaban 5 mg BID?")   then signs the order
  physician -> interrupt("physician: approve discharge order?")    then signs the order
Each gate writes one row to an external "record" (a list, or a sqlite table in the legacy runs)
and returns NO state update, which is what a gate that only performs a side effect looks like.
Set LAB_GATE_OUTPUT=1 for the control: the same gates, each also returning one state key.

  phase inbox         in-memory. The pharmacist answers by interrupt id. What does the approval
                      inbox, built from get_state(cfg).interrupts, show next? Then the stale item
                      is answered a second time.
  phase legacy-pause  sqlite checkpointer on disk. Pause, pharmacist answers, process exits.
  phase legacy-read   a second process (run it on the other version) opens the same thread,
                      reads the inbox, then lets the physician answer. Count the rows.
"""
import importlib.metadata as md
import os
import sqlite3
import sys
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

VERSION = md.version("langgraph")
Q_PHARM = "pharmacy: approve apixaban 5 mg BID?"
Q_PHYS = "physician: approve discharge order?"


# LAB_GATE_OUTPUT=1 makes each gate also return a state update (the control case).
GATE_OUTPUT = os.environ.get("LAB_GATE_OUTPUT") == "1"


class S(TypedDict, total=False):
    patient: str
    pharmacy_signed: bool
    physician_signed: bool


def build(checkpointer, sign):
    def pharmacy(state):
        decision = interrupt(Q_PHARM)
        sign("pharmacy", decision)          # the side effect: a signature row in the record
        return {"pharmacy_signed": True} if GATE_OUTPUT else None

    def physician(state):
        decision = interrupt(Q_PHYS)
        sign("physician", decision)
        return {"physician_signed": True} if GATE_OUTPUT else None

    g = StateGraph(S)
    g.add_node("pharmacy", pharmacy)
    g.add_node("physician", physician)
    g.add_edge(START, "pharmacy")
    g.add_edge(START, "physician")
    g.add_edge("pharmacy", END)
    g.add_edge("physician", END)
    return g.compile(checkpointer=checkpointer)


def inbox(app, cfg):
    st = app.get_state(cfg)
    return {i.value: i.id for i in st.interrupts}, st.next


def short(qs):
    return [q.split(":")[0] for q in sorted(qs)]


def try_resume(app, cfg, value, label):
    try:
        app.invoke(Command(resume=value), cfg)
        return f"{label}: accepted"
    except Exception as e:  # noqa: BLE001
        return f"{label}: raised {type(e).__name__}: {str(e).splitlines()[0][:110]}"


def phase_inbox():
    from langgraph.checkpoint.memory import InMemorySaver
    record = []
    app = build(InMemorySaver(), lambda who, d: record.append((who, d)))
    cfg = {"configurable": {"thread_id": "pt-123-discharge"}}
    app.invoke({"patient": "pt-123"}, cfg)
    ids, nxt = inbox(app, cfg)
    print(f"  paused: inbox={short(ids)} next={nxt} record={record}")

    app.invoke(Command(resume={ids[Q_PHARM]: "approve by rph-7"}), cfg)
    after, nxt = inbox(app, cfg)
    print(f"  pharmacist answered by id: inbox={short(after)} next={nxt} record={record}")
    stale = Q_PHARM in after
    print(f"    answered question still listed as pending: {stale}")

    # A second reviewer works the inbox and answers the pharmacy item again, differently.
    print("    " + try_resume(app, cfg, {ids[Q_PHARM]: "REJECT by rph-9"}, "second answer to the answered item"))
    after2, nxt = inbox(app, cfg)
    print(f"    after it: inbox={short(after2)} next={nxt} record={record}")

    print("    " + try_resume(app, cfg, {ids[Q_PHYS]: "approve by md-3"}, "physician answers by id"))
    final, nxt = inbox(app, cfg)
    print(f"  end: inbox={short(final)} next={nxt}")
    print(f"  record rows: {len(record)} -> {record}")
    print(f"  SUMMARY {VERSION} inbox: after one of two answers the inbox listed {len(after)} item(s); "
          f"record holds {len(record)} signature row(s) for 2 approvals")


def _sqlite_app(path):
    from langgraph.checkpoint.sqlite import SqliteSaver
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("create table if not exists record (who text, decision text, by_version text)")
    conn.commit()

    def sign(who, d):
        conn.execute("insert into record values (?,?,?)", (who, d, VERSION))
        conn.commit()

    return build(SqliteSaver(conn), sign), conn


def rows(conn):
    return conn.execute("select who, decision, by_version from record").fetchall()


def phase_legacy_pause(path):
    app, conn = _sqlite_app(path)
    cfg = {"configurable": {"thread_id": "pt-456-discharge"}}
    app.invoke({"patient": "pt-456"}, cfg)
    ids, nxt = inbox(app, cfg)
    app.invoke(Command(resume={ids[Q_PHARM]: "approve by rph-7"}), cfg)
    after, nxt = inbox(app, cfg)
    print(f"  paused and pharmacist answered on {VERSION}: inbox={short(after)} next={nxt}")
    print(f"  record rows: {rows(conn)}")


def phase_legacy_read(path):
    app, conn = _sqlite_app(path)
    cfg = {"configurable": {"thread_id": "pt-456-discharge"}}
    before = rows(conn)
    ids, nxt = inbox(app, cfg)
    print(f"  opened on {VERSION}: inbox={short(ids)} next={nxt} record rows={len(before)}")
    if Q_PHYS in ids:
        print("    " + try_resume(app, cfg, {ids[Q_PHYS]: "approve by md-3"}, "physician answers by id"))
    final, nxt = inbox(app, cfg)
    r = rows(conn)
    print(f"  end: inbox={short(final)} next={nxt}")
    for row in r:
        print(f"    record: {row}")
    pharm = sum(1 for x in r if x[0] == "pharmacy")
    print(f"  SUMMARY legacy thread read on {VERSION}: pharmacy signature rows={pharm}, "
          f"total rows={len(r)}, thread finished={nxt == ()}")


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "inbox"
    print(f"langgraph {VERSION} | phase {phase} | gates return {'a state update' if GATE_OUTPUT else 'nothing'}")
    if phase == "inbox":
        phase_inbox()
    elif phase == "legacy-pause":
        phase_legacy_pause(sys.argv[2])
    elif phase == "legacy-read":
        phase_legacy_read(sys.argv[2])
