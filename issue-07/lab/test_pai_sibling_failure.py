"""Mechanism of the week, Issue 07: the write that finished beside a tool that failed.

One scripted model response carries two tool calls for the same patient:

    lookup_allergies(patient_id)            emitted first; the allergy service is down and it raises
    place_order(patient_id, drug, dose)     emitted second; writes one row to the order record

pydantic-ai runs both in parallel. The order is written in a few milliseconds; the allergy
lookup raises a little later. Since 2.54.0 (#9434) an unexpected exception in a tool ends the
run and cancels its siblings, so `agent.run()` raises. The question is what the message
history the caller holds says about `place_order` after that, and what a resume does with it.

Run on pydantic-ai-slim 2.54.0 and 2.55.0. No model key: the model is `FunctionModel`.
The "record" is an in-memory list. Synthetic data only.
"""
from __future__ import annotations

import asyncio
import os
import sys
from importlib.metadata import version

from pydantic_ai import Agent, RunContext, capture_run_messages
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    RetryPromptPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel

VER = version('pydantic-ai-slim')
MODE = os.environ.get('LAB_MODE', 'parallel_ordered_events')   # DBOS durable runs default to this
CANCEL = os.environ.get('LAB_CANCEL') == '1'                       # 1: cancel the run instead of a sibling raising

RECORD: list[tuple[str, str, str]] = []            # the system of record: (patient, drug, dose)
MODEL_CALLS: list[str] = []


def scripted_model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """Turn 1: ask for both tools. Later turns: read what the history says about place_order."""
    last = messages[-1]
    assert isinstance(last, ModelRequest)
    returns = {p.tool_name: p for p in last.parts if isinstance(p, (ToolReturnPart, RetryPromptPart))}
    if not any(isinstance(p, (ToolReturnPart, RetryPromptPart)) for p in last.parts):
        MODEL_CALLS.append('turn-1: emit lookup_allergies + place_order')
        return ModelResponse(parts=[
            ToolCallPart('lookup_allergies', {'patient_id': 'pt-123'}, tool_call_id='call-allergy'),
            ToolCallPart('place_order', {'patient_id': 'pt-123', 'drug': 'apixaban', 'dose': '5 mg BID'},
                         tool_call_id='call-order'),
        ])
    order = returns.get('place_order')
    text = order.content if isinstance(order, ToolReturnPart) else None
    MODEL_CALLS.append(f'turn-{len(MODEL_CALLS) + 1}: history says place_order -> {text!r}')
    if isinstance(text, str) and text.startswith('ORDER PLACED'):
        return ModelResponse(parts=[TextPart('Apixaban ordered; allergy check still pending.')])
    # What a model does when the transcript says the order never produced a result: order again.
    return ModelResponse(parts=[
        ToolCallPart('place_order', {'patient_id': 'pt-123', 'drug': 'apixaban', 'dose': '5 mg BID'},
                     tool_call_id='call-order-2'),
    ])


agent = Agent(FunctionModel(scripted_model))


@agent.tool
async def lookup_allergies(ctx: RunContext[None], patient_id: str) -> str:
    await asyncio.sleep(0.3)                          # the allergy service is slow, then down
    raise RuntimeError('allergy service 503')


@agent.tool
async def place_order(ctx: RunContext[None], patient_id: str, drug: str, dose: str) -> str:
    RECORD.append((patient_id, drug, dose))          # the write happens here
    return f'ORDER PLACED order-{len(RECORD)} {drug} {dose} for {patient_id}'


def describe(messages: list[ModelMessage]) -> str:
    """What the last ModelRequest in the history says about each tool call."""
    out = []
    for m in messages:
        if isinstance(m, ModelRequest):
            for p in m.parts:
                if isinstance(p, ToolReturnPart):
                    out.append(f'return[{p.tool_name}]={p.content!r}')
                elif isinstance(p, RetryPromptPart):
                    out.append(f'retry[{p.tool_name}]')
    return '; '.join(out) if out else '(no tool returns in history)'


async def main() -> None:
    print(f'pydantic-ai-slim {VER}  mode={MODE}  case={"caller cancels" if CANCEL else "sibling raises"}')
    RECORD.clear(); MODEL_CALLS.clear()

    # 1. The batch: one write succeeds, its sibling raises.
    with agent.parallel_tool_call_execution_mode(MODE):
        with capture_run_messages() as messages:
            try:
                if CANCEL:   # the caller gives up while the allergy lookup is still running
                    await asyncio.wait_for(agent.run('Start anticoagulation for pt-123.'), timeout=0.1)
                else:
                    await agent.run('Start anticoagulation for pt-123.')
                print('  run 1: finished without error (unexpected)')
            except BaseException as e:
                print(f'  run 1: raised {type(e).__name__}: {e}')
    print(f'  rows in the record after run 1: {len(RECORD)}')
    print(f'  history after run 1: {describe(messages)}')

    # 2. The resume: the caller keeps the captured history and starts a new run from it,
    #    which is what a durable executor or an approval service does after an error.
    history = list(messages)
    with agent.parallel_tool_call_execution_mode(MODE):
        with capture_run_messages() as messages2:
            try:
                result = await agent.run('Continue.', message_history=history)
                print(f'  run 2: final text {result.output!r}')
            except Exception as e:
                print(f'  run 2: raised {type(e).__name__}: {e}')
    print(f'  history seen by the model at run 2: {describe(messages2[:len(history) + 1])}')
    print(f'  rows in the record after run 2: {len(RECORD)}   -> {RECORD}')
    for c in MODEL_CALLS:
        print(f'  model: {c}')


if __name__ == '__main__':
    asyncio.run(main())
