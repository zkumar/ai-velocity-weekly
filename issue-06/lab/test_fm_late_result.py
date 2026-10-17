"""fastmcp 4.0.11 against 4.1.0: a tool that finishes after its timeout.

PR #5379 (fixes #5378, in 4.1.0, 8 Oct 2026): late results after a tool timeout are rejected.
A synchronous tool with timeout=0.2 s takes 1 s, writes an order, then returns. In-memory client,
no model, no API key. Two questions: did the write happen, and what was the caller told?
"""
import asyncio
import time

import fastmcp
from fastmcp import Client, FastMCP

mcp = FastMCP("orders")
RECORD = []


@mcp.tool(timeout=0.2)
def place_order(patient_id: str, order: str) -> str:
    """Place an order; the downstream system is slow today."""
    time.sleep(1.0)
    RECORD.append((patient_id, order))      # the write commits after the deadline
    return "ORDER PLACED"


async def main():
    async with Client(mcp) as c:
        t0 = time.monotonic()
        try:
            r = await c.call_tool("place_order", {"patient_id": "pt-123", "order": "BMP stat"}, raise_on_error=False)
            told = f"is_error={r.is_error} content={[getattr(x, 'text', x) for x in r.content]}"
        except Exception as e:  # noqa: BLE001
            told = f"raised {type(e).__name__}: {str(e)[:120]}"
        dt = time.monotonic() - t0
        await asyncio.sleep(1.2)            # let a still-running worker thread finish
        print(f"fastmcp {fastmcp.__version__}: caller told after {dt:.1f}s: {told}")
        print(f"  rows in the record: {len(RECORD)} {RECORD}")
        verdict = "error" if "is_error=True" in told or "raised" in told else "success"
        print(f"  SUMMARY {fastmcp.__version__}: caller sees {verdict}; the write ran {len(RECORD)} time(s)")


asyncio.run(main())
