"""AI Velocity Weekly 02, lab 5.2.

MCP Python SDK 2.2.0 (7 Sept 2026), commit 0c91368: the bearer-auth
backend can refuse a token that was issued for a different resource
(RFC 8707 audience). A token minted for the scheduling MCP server is
no longer accepted by the FHIR MCP server just because the same
authorization server signed it. This script exercises the check
without a network: a stub TokenVerifier returns AccessToken objects
with different `resource` values and we call the backend directly.

Also shown: the same release turned several wire types from Pydantic
RootModel wrappers into plain type aliases (commit 9972c21), so
`ContentBlock.model_validate(...)` no longer exists.

Run:  pip install "mcp==2.2.0"
      python test_mcp_token_audience.py
"""

from __future__ import annotations

import asyncio
import warnings

from pydantic import AnyHttpUrl, TypeAdapter
from starlette.requests import HTTPConnection

from mcp.server.auth.middleware.bearer_auth import BearerAuthBackend
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings

FHIR_MCP = AnyHttpUrl("https://fhir-mcp.hospital.example/mcp")

# What an introspection endpoint would tell us for three tokens.
ISSUED = {
    "tok-fhir": AccessToken(token="tok-fhir", client_id="orders-agent", scopes=["patient/MedicationRequest.write"],
                            resource="https://fhir-mcp.hospital.example/mcp"),
    "tok-sched": AccessToken(token="tok-sched", client_id="orders-agent", scopes=["patient/Appointment.write"],
                             resource="https://scheduling-mcp.hospital.example/mcp"),
    "tok-legacy": AccessToken(token="tok-legacy", client_id="orders-agent", scopes=["patient/*.write"],
                              resource=None),  # authorization server that ignores RFC 8707
}


class StubVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        return ISSUED.get(token)


def conn_with(token: str) -> HTTPConnection:
    scope = {"type": "http", "headers": [(b"authorization", f"Bearer {token}".encode())]}
    return HTTPConnection(scope)


async def main() -> None:
    print("1. AuthSettings warns when validate_token_resource is left unset")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        AuthSettings(issuer_url=AnyHttpUrl("https://idp.hospital.example"), resource_server_url=FHIR_MCP)
    print("   ", [str(w.message)[:90] for w in caught])

    print("\n2. Backend without resource pin (2.1 behaviour) vs with resource pin (2.2.0)")
    loose = BearerAuthBackend(StubVerifier())
    strict = BearerAuthBackend(StubVerifier(), resource_server_url=FHIR_MCP)
    for tok in ISSUED:
        a = await loose.authenticate(conn_with(tok))
        b = await strict.authenticate(conn_with(tok))
        print(f"   {tok:11s} loose={'accepted' if a else 'refused ':8s} strict={'accepted' if b else 'refused'}")

    print("\n3. Wire types are aliases now (commit 9972c21)")
    from mcp import types
    block = {"type": "text", "text": "MedicationRequest/123 written"}
    try:
        types.ContentBlock.model_validate(block)  # type: ignore[attr-defined]
    except AttributeError as e:
        print("    ContentBlock.model_validate ->", type(e).__name__, str(e)[:70])
    parsed = TypeAdapter(types.ContentBlock).validate_python(block)
    print("    TypeAdapter(ContentBlock).validate_python ->", type(parsed).__name__)


if __name__ == "__main__":
    asyncio.run(main())
