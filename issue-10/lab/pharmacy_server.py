"""A pharmacy MCP server for the lab: three tools over stdio, no network, synthetic data.

read_chart is a read. place_order and discontinue_order are writes: each appends one row to the
"system of record", a JSON-lines file named by LAB_RECORD. discontinue_order stands in for the tool
the server team added after the agent team wrote its approval lists.
"""
import json
import os

from mcp.server import MCPServer

RECORD = os.environ["LAB_RECORD"]
server = MCPServer("pharmacy")


def _write(row: dict) -> None:
    with open(RECORD, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


@server.tool()
def read_chart(patient_id: str) -> str:
    """Read the active medication list for a patient."""
    return f"{patient_id}: apixaban 5 mg oral BID (order-1), metformin 500 mg oral BID (order-2)"


@server.tool()
def place_order(patient_id: str, drug: str, dose: str) -> str:
    """Place a medication order."""
    _write({"action": "place_order", "patient_id": patient_id, "drug": drug, "dose": dose})
    return f"ORDER PLACED {drug} {dose} for {patient_id}"


@server.tool()
def discontinue_order(patient_id: str, order_id: str) -> str:
    """Discontinue an active medication order."""
    _write({"action": "discontinue_order", "patient_id": patient_id, "order_id": order_id})
    return f"ORDER DISCONTINUED {order_id} for {patient_id}"


if __name__ == "__main__":
    server.run()
