#!/usr/bin/env python3
"""AI Velocity Weekly 08, mechanism of the week.

A pharmacy agent wrapped as an AgentTool pauses for a pharmacist's confirmation on
place_order. What does the parent agent get back as the tool result, and does the
order ever reach the record?

Google ADK 2.12.0 against 2.13.0. No model key: both agents run on a scripted BaseLlm.
Synthetic data only; the "record" is an in-memory list.

LAB_CASE=tool     the pharmacy agent is an AgentTool of the parent (the finding)
LAB_CASE=direct   the pharmacy agent is run on its own, paused, and resumed with a
                  confirmation (the control: what a working gate looks like)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import AsyncGenerator

from google.adk import __version__ as ADK_VERSION
from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

CASE = os.environ.get("LAB_CASE", "tool")
RECORD: list[tuple[str, str, str]] = []          # the system of record
PARENT_TOOL_RESULTS: list[str] = []                # what the parent model was handed


def place_order(patient_id: str, drug: str, dose: str) -> dict:
  """Writes one medication order to the record."""
  RECORD.append((patient_id, drug, dose))
  return {"status": f"ORDER PLACED order-{len(RECORD)} {drug} {dose} for {patient_id}"}


def _text(s: str) -> LlmResponse:
  return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=s)]))


def _call(name: str, args: dict, cid: str) -> LlmResponse:
  return LlmResponse(content=types.Content(
      role="model",
      parts=[types.Part(function_call=types.FunctionCall(name=name, args=args, id=cid))]))


def _last_function_responses(req: LlmRequest) -> list[types.FunctionResponse]:
  for c in reversed(req.contents):
    frs = [p.function_response for p in (c.parts or []) if p.function_response]
    if frs:
      return frs
    if any(p.text for p in (c.parts or [])):
      break
  return []


class ScriptedPharmacy(BaseLlm):
  """The child. Turn 1: call place_order. Later: say what the tool said."""
  model: str = "scripted-pharmacy"

  async def generate_content_async(self, llm_request: LlmRequest, stream: bool = False
                                   ) -> AsyncGenerator[LlmResponse, None]:
    frs = _last_function_responses(llm_request)
    if not frs:
      yield _call("place_order",
                  {"patient_id": "pt-123", "drug": "apixaban", "dose": "5 mg BID"},
                  "call-order-1")
      return
    yield _text("Pharmacy: " + json.dumps(frs[-1].response))


class ScriptedParent(BaseLlm):
  """The parent. Turn 1: delegate to the pharmacy agent. Turn 2: report to the clinician."""
  model: str = "scripted-parent"

  async def generate_content_async(self, llm_request: LlmRequest, stream: bool = False
                                   ) -> AsyncGenerator[LlmResponse, None]:
    frs = _last_function_responses(llm_request)
    if not frs:
      yield _call("pharmacy", {"request": "Start apixaban 5 mg BID for pt-123"}, "call-delegate-1")
      return
    result = frs[-1].response
    PARENT_TOOL_RESULTS.append(json.dumps(result))
    # A scripted stand-in for what a real model does with an empty tool result:
    # it has nothing to report and reports success.
    text = result.get("result") if isinstance(result, dict) else result
    if not text:
      yield _text("Apixaban 5 mg BID ordered for pt-123 via the pharmacy agent.")
    elif str(text).startswith("Error"):
      yield _text("The pharmacy agent could not complete the order: " + str(text))
    else:
      yield _text("Pharmacy agent reported: " + str(text))


def make_pharmacy() -> LlmAgent:
  return LlmAgent(
      name="pharmacy",
      model=ScriptedPharmacy(),
      description="Places medication orders after pharmacist confirmation.",
      instruction="Place the requested order.",
      tools=[FunctionTool(place_order, require_confirmation=True)],
  )


async def run(runner: Runner, session_id: str, content: types.Content) -> list:
  events = []
  async for ev in runner.run_async(user_id="u", session_id=session_id, new_message=content):
    events.append(ev)
  return events


def describe(events) -> None:
  for ev in events:
    parts = []
    for p in (ev.content.parts if ev.content and ev.content.parts else []):
      if p.function_call:
        parts.append(f"call[{p.function_call.name}]")
      elif p.function_response:
        parts.append(f"response[{p.function_response.name}]={json.dumps(p.function_response.response)[:90]}")
      elif p.text:
        parts.append(f"text={p.text!r}")
    lr = f" long_running_tool_ids={sorted(ev.long_running_tool_ids)}" if ev.long_running_tool_ids else ""
    print(f"    event author={ev.author} {' '.join(parts)}{lr}")


async def main() -> None:
  print(f"google-adk {ADK_VERSION}  case={CASE}")
  svc = InMemorySessionService()
  user = types.Content(role="user", parts=[types.Part(text="Start apixaban 5 mg BID for pt-123.")])

  if CASE == "tool":
    parent = LlmAgent(name="clinician_assistant", model=ScriptedParent(),
                      instruction="Delegate medication orders to the pharmacy agent.",
                      tools=[AgentTool(agent=make_pharmacy())])
    runner = Runner(agent=parent, app_name="lab", session_service=svc)
    s = await svc.create_session(app_name="lab", user_id="u")
    events = await run(runner, s.id, user)
    describe(events)
    pending = sorted(set().union(*[ev.long_running_tool_ids or set() for ev in events]))
    print(f"  parent was handed tool result: {PARENT_TOOL_RESULTS}")
    print(f"  confirmation requests visible to the caller: {pending}")
    print(f"  final text: {events[-1].content.parts[0].text!r}")
    print(f"  rows in the record: {len(RECORD)}")
    print(f"  session events kept for the caller: {len((await svc.get_session(app_name='lab', user_id='u', session_id=s.id)).events)}")
    await runner.close()
    return

  # control: the pharmacy agent on its own, paused and resumed
  pharmacy = make_pharmacy()
  runner = Runner(agent=pharmacy, app_name="lab", session_service=svc)
  s = await svc.create_session(app_name="lab", user_id="u")
  events = await run(runner, s.id, user)
  describe(events)
  req = next(p.function_call for ev in events for p in (ev.content.parts or [])
             if p.function_call and p.function_call.name == "adk_request_confirmation")
  print(f"  paused on {req.name} id={req.id}; rows in the record: {len(RECORD)}")
  answer = types.Content(role="user", parts=[types.Part(function_response=types.FunctionResponse(
      name="adk_request_confirmation", id=req.id, response={"confirmed": True}))])
  events2 = await run(runner, s.id, answer)
  describe(events2)
  print(f"  final text: {events2[-1].content.parts[0].text!r}")
  print(f"  rows in the record after the pharmacist confirmed: {len(RECORD)}")
  await runner.close()


if __name__ == "__main__" and CASE != "subagent":
  asyncio.run(main())


# ---------------------------------------------------------------- the documented alternative
class ScriptedDelegator(BaseLlm):
  """Parent that hands off with transfer_to_agent, then reports whatever comes back."""
  model: str = "scripted-delegator"

  async def generate_content_async(self, llm_request: LlmRequest, stream: bool = False
                                   ) -> AsyncGenerator[LlmResponse, None]:
    frs = _last_function_responses(llm_request)
    if not frs:
      yield _call("pharmacy", {"request": "Start apixaban 5 mg BID for pt-123"}, "call-delegate-1")
      return
    PARENT_TOOL_RESULTS.append(json.dumps(frs[-1].response))
    yield _text("Delegator saw: " + json.dumps(frs[-1].response))


async def main_subagent() -> None:
  print(f"google-adk {ADK_VERSION}  case=subagent")
  svc = InMemorySessionService()
  user = types.Content(role="user", parts=[types.Part(text="Start apixaban 5 mg BID for pt-123.")])
  pharmacy = make_pharmacy()
  pharmacy.mode = "single_turn"
  parent = LlmAgent(name="clinician_assistant", model=ScriptedDelegator(),
                    instruction="Delegate medication orders to the pharmacy agent.",
                    sub_agents=[pharmacy])
  runner = Runner(agent=parent, app_name="lab", session_service=svc)
  s = await svc.create_session(app_name="lab", user_id="u")
  events = await run(runner, s.id, user)
  describe(events)
  reqs = [p.function_call for ev in events for p in (ev.content.parts or [])
          if p.function_call and p.function_call.name == "adk_request_confirmation"]
  print(f"  confirmation requests visible to the caller: {[r.id for r in reqs]}; rows: {len(RECORD)}")
  if reqs:
    answer = types.Content(role="user", parts=[types.Part(function_response=types.FunctionResponse(
        name="adk_request_confirmation", id=reqs[0].id, response={"confirmed": True}))])
    events2 = await run(runner, s.id, answer)
    describe(events2)
    print(f"  final text: {events2[-1].content.parts[0].text!r}")
  print(f"  rows in the record: {len(RECORD)}")
  await runner.close()


if __name__ == "__main__" and CASE == "subagent":
  asyncio.run(main_subagent())
