"""mcp 2.2.0 against 2.3.0: a tool the client cannot see and can still call.

PR #3620, first released in mcp 2.3.0 (2 Oct 2026): "Reject a tool with an invalid x-mcp-header
annotation at registration". In src/mcp/server/mcpserver/tools/base.py a parameter whose
x-mcp-header value is not an RFC 9110 token now raises InvalidSignature when the tool is
registered. On 2.2.0 the server accepted the tool, the client dropped it from list_tools(), and
call_tool() by name still executed it.

A claims server registers lookup_claim with the header name "Member Id" (the space makes it
invalid). The script prints whether registration was accepted, what the client lists, and what a
direct call does. In-memory transport, synthetic data only, no model, no API key.
"""
import asyncio
import logging
from importlib.metadata import version
from typing import Annotated

from pydantic import Field

from mcp import Client
from mcp.server.mcpserver import MCPServer

logging.disable(logging.CRITICAL)
V = version("mcp")
CALLS = []
srv = MCPServer("claims")
print(f"mcp {V}")
try:
    @srv.tool()
    def lookup_claim(member_id: Annotated[str, Field(json_schema_extra={"x-mcp-header": "Member Id"})]) -> str:
        """Look up the open claims for a member."""
        CALLS.append(member_id)
        return f"2 open claims for {member_id}"
    registered = "accepted"
    print("  registration of lookup_claim with x-mcp-header 'Member Id': accepted")
except Exception as e:  # noqa: BLE001
    registered = "rejected"
    print(f"  registration of lookup_claim with x-mcp-header 'Member Id': rejected, {type(e).__name__}: {str(e)[:120]}")


async def main():
    listed, called = [], "not attempted"
    async with Client(srv) as c:
        listed = [t.name for t in (await c.list_tools()).tools]
        print(f"  tools the client lists: {listed}")
        try:
            r = await c.call_tool("lookup_claim", {"member_id": "M-1001"})
            called = "error" if getattr(r, "is_error", False) or getattr(r, "isError", False) else "executed"
            print(f"  call_tool('lookup_claim'): {called} | {r.content[0].text[:80]!r}")
        except Exception as e:  # noqa: BLE001
            called = "raised"
            print(f"  call_tool('lookup_claim'): raised {type(e).__name__}: {str(e)[:80]}")
    print(f"  SUMMARY {V}: registration={registered} listed={len(listed)} call={called} server_side_executions={len(CALLS)}")


asyncio.run(main())
