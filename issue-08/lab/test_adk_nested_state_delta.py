#!/usr/bin/env python3
"""AI Velocity Weekly 08, supporting check.

A tool writes into a nested container in session state: it appends a hold to
state['patient']['holds'] instead of assigning a top-level key. Is that write
recorded in the event's state_delta, which is what a session service persists
and what an audit of state changes reads? Google ADK 2.12.0 against 2.13.0.
No model key: the agent runs on a scripted BaseLlm. Synthetic data only.
"""
from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

from google.adk import __version__ as ADK_VERSION
from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool, ToolContext
from google.genai import types


def hold_medication(drug: str, tool_context: ToolContext) -> dict:
  """Puts a hold on a medication by writing into the patient's state record."""
  tool_context.state["patient"]["holds"].append(drug)          # nested write
  tool_context.state["holds_written"] = tool_context.state.get("holds_written", 0) + 1  # top-level control
  return {"status": f"hold placed on {drug}"}


class Scripted(BaseLlm):
  model: str = "scripted"

  async def generate_content_async(self, llm_request: LlmRequest, stream: bool = False
                                   ) -> AsyncGenerator[LlmResponse, None]:
    for c in reversed(llm_request.contents):
      if any(p.function_response for p in (c.parts or [])):
        yield LlmResponse(content=types.Content(role="model", parts=[types.Part(text="Hold placed.")]))
        return
      if any(p.text for p in (c.parts or [])):
        break
    yield LlmResponse(content=types.Content(role="model", parts=[types.Part(
        function_call=types.FunctionCall(name="hold_medication", args={"drug": "apixaban"}, id="call-hold-1"))]))


async def main() -> None:
  print(f"google-adk {ADK_VERSION}")
  svc = InMemorySessionService()
  agent = LlmAgent(name="meds", model=Scripted(), instruction="Place holds.",
                   tools=[FunctionTool(hold_medication)])
  runner = Runner(agent=agent, app_name="lab", session_service=svc)
  s = await svc.create_session(app_name="lab", user_id="u",
                               state={"patient": {"id": "pt-123", "holds": []}})
  deltas = []
  async for ev in runner.run_async(user_id="u", session_id=s.id, new_message=types.Content(
      role="user", parts=[types.Part(text="Hold apixaban for pt-123.")])):
    if ev.actions and ev.actions.state_delta:
      deltas.append(ev.actions.state_delta)
  stored = (await svc.get_session(app_name="lab", user_id="u", session_id=s.id)).state
  print(f"  state_delta on the tool event: {json.dumps(deltas)}")
  print(f"  nested write in any delta: {any('patient' in d for d in deltas)}   "
        f"top-level write in a delta: {any('holds_written' in d for d in deltas)}")
  print(f"  session state the service holds: {json.dumps(stored)}")
  await runner.close()


if __name__ == "__main__":
  asyncio.run(main())
