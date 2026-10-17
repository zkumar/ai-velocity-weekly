"""llama-index-core 0.14.24 against 0.14.25: a failing write that ran twice.

Commit e07b962 (#22841), "fix(core): avoid retrying failed function tools", first released in
0.14.25 (21 Sept 2026). In llama_index/core/tools/calling.py the old call_tool() tried a
one-parameter FunctionTool positionally, caught any exception, and called it again with
keyword arguments. A tool that committed its side effect and then raised was executed twice.

One call, no model, no API key: append_note() appends to an in-memory "record", then raises
the way an EHR gateway does when the commit succeeded but the acknowledgement timed out.
"""
import importlib.metadata as md

from llama_index.core.tools import FunctionTool
from llama_index.core.tools.calling import call_tool

RECORD = []


def append_note(note: str) -> str:
    """Append a clinical note to the patient record."""
    RECORD.append(note)                                   # the write commits ...
    raise RuntimeError("EHR gateway: timeout after commit")  # ... then the call fails


if __name__ == "__main__":
    tool = FunctionTool.from_defaults(fn=append_note)
    out = call_tool(tool, {"note": "BP 120/80, K+ 6.1 mmol/L"})
    print(f"llama-index-core {md.version('llama-index-core')}")
    print(f"  one call_tool() | is_error={out.is_error} | tool output: {str(out.content)[:70]!r}")
    print(f"  writes in the record: {len(RECORD)} {RECORD}")
    print(f"  SUMMARY {md.version('llama-index-core')}: calls=1 errors=1 writes={len(RECORD)}")
