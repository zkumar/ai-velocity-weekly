"""openai-agents: a paused, already-approved run saved on 0.22.3 and resumed on 0.23.1.

The approval-scoping change in 0.23.0 (#5144) re-keys stored approvals by owning agent and moves
RunState to schema 1.18. This script asks what happens to an approval that is in flight when the
upgrade lands: the nurse has said yes, the state has been written to disk, and the process that
resumes it runs the new version.

    python upgrade_oa_paused_state.py save state     # run in the OLD environment
    python upgrade_oa_paused_state.py load state     # run in the NEW environment

Two states are saved: one where the nurse approved the saline flush once, one where she said
"always". Each is then resumed; the model's next call is a heparin order.

run_all.sh does both, saving with .venv/previous and loading with .venv/current, and also loads
the same file back in .venv/previous as the control. Synthetic data only, no model, no API key.
"""
import asyncio
import importlib.util
import json
import pathlib
import sys

from agents import Runner, RunState

spec = importlib.util.spec_from_file_location("t", pathlib.Path(__file__).with_name("test_oa_handoff_approval_scope.py"))
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

mode, path = sys.argv[1], sys.argv[2]
KINDS = ("once", "always")                                  # a plain yes for one call, and a sticky yes


async def save(kind):
    record = []
    intake = t.build(record, t.INTAKE_TWICE, [])
    r = await Runner.run(intake, "admit pt-123")
    state = r.to_state()
    state.approve(r.interruptions[0], always_approve=(kind == "always"))
    blob = state.to_json()
    json.dump(blob, open(f"{path}.{kind}", "w"))
    print(f"  saved on {t.V}, approved {kind}: schema {blob.get('$schemaVersion')} | approved, not yet executed: {t.shown(r)}")


async def load(kind):
    record = []
    intake = t.build(record, t.INTAKE_TWICE[1:], [])
    blob = json.load(open(f"{path}.{kind}"))
    try:
        state = await RunState.from_json(intake, blob)
        r = await Runner.run(intake, state)
        print(f"  resumed on {t.V}, approved {kind} (state schema {blob.get('$schemaVersion')}): record {record} | still waiting on: {t.shown(r)}")
        print(f"  SUMMARY {kind} yes, resumed on {t.V}: written={len(record)} waiting_on={[i.raw_item.call_id for i in r.interruptions]}")
    except Exception as e:  # noqa: BLE001
        print(f"  resume on {t.V}, approved {kind}, raised {type(e).__name__}: {str(e)[:200]}")


for kind in KINDS:
    asyncio.run(save(kind) if mode == "save" else load(kind))
