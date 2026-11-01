"""AI Velocity Weekly 09, mechanism of the week.

What the framework's own log keeps about a medication order, Semantic Kernel 1.45.0 against 1.46.0.

A clinician-assistant agent asks the model to place an apixaban order. The model (a scripted
ChatCompletionClientBase subclass, no API key) answers with a function call to
pharmacy.place_order; Semantic Kernel's auto function-invocation loop runs it, puts the result in
the chat history, and asks the model again; the model closes the turn with a sentence.

A hospital that pointed its audit sink at Semantic Kernel's loggers (semantic_kernel.kernel and
semantic_kernel.functions.*) got, on 1.45.0, an INFO line carrying the function name and the full
argument JSON, a DEBUG line with the arguments again, a DEBUG line with the function result, and on
failure an ERROR line with the exception text and traceback. The script prints what that sink
captured on the installed version, then counts the lines that carry the patient id, the drug, the
result and the failure reason.

Two cases, selected with LAB_CASE: "placed" (the order writes) and "refused" (the pharmacy tool
raises, the way a contraindication check would). No network, no model, synthetic data only.
"""
import asyncio
import json
import logging
import os
import sys
from importlib.metadata import version
from typing import Any

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.contents import ChatHistory, ChatMessageContent, FunctionCallContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions import kernel_function

CASE = os.environ.get("LAB_CASE", "placed")
SK = version("semantic-kernel")
RECORD: list[dict] = []          # stands in for the system of record
ORDER = {"patient_id": "pt-123", "drug": "apixaban", "dose": "5 mg", "route": "oral", "frequency": "BID"}


class Pharmacy:
    @kernel_function(name="place_order", description="Place a medication order for a patient.")
    def place_order(self, patient_id: str, drug: str, dose: str, route: str, frequency: str) -> str:
        if CASE == "refused":
            raise ValueError(f"contraindicated: {drug} for {patient_id}, documented allergy; order refused")
        RECORD.append({"patient_id": patient_id, "drug": drug, "dose": dose, "route": route, "frequency": frequency})
        return f"ORDER PLACED order-{len(RECORD)} {drug} {dose} {route} {frequency} for {patient_id}"


class ScriptedChat(ChatCompletionClientBase):
    """First reply: call pharmacy.place_order with the order. Second reply: close the turn."""

    SUPPORTS_FUNCTION_CALLING = True
    calls: int = 0

    async def _inner_get_chat_message_contents(self, chat_history: ChatHistory, settings: PromptExecutionSettings, **kw: Any):
        self.calls += 1
        if self.calls == 1:
            fc = FunctionCallContent(id="call-1", plugin_name="pharmacy", function_name="place_order",
                                     arguments=json.dumps(ORDER))
            return [ChatMessageContent(role=AuthorRole.ASSISTANT, items=[fc], ai_model_id=self.ai_model_id)]
        last = chat_history.messages[-1]
        text = "".join(str(getattr(i, "result", "")) for i in last.items)
        if "ORDER PLACED" in text:
            reply = "Apixaban 5 mg oral BID ordered for pt-123."
        else:
            reply = f"The order was not placed. The pharmacy tool said: {text}"
        return [ChatMessageContent(role=AuthorRole.ASSISTANT, content=reply, ai_model_id=self.ai_model_id)]

    async def _inner_get_streaming_chat_message_contents(self, *a: Any, **kw: Any):  # pragma: no cover
        raise NotImplementedError
        yield

    def get_prompt_execution_settings_class(self):
        return PromptExecutionSettings


class AuditSink(logging.Handler):
    """What a log-shipping agent subscribed to the framework's loggers would receive."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.lines: list[tuple[str, str, str]] = []

    def emit(self, record: logging.LogRecord) -> None:
        msg = record.getMessage()
        if record.exc_info:
            msg += " [traceback attached]"
        self.lines.append((record.name, record.levelname, msg))


async def main() -> None:
    sink = AuditSink()
    for name in ("semantic_kernel.kernel", "semantic_kernel.functions", "semantic_kernel.connectors.ai"):
        lg = logging.getLogger(name)
        lg.setLevel(logging.DEBUG)
        lg.addHandler(sink)
        lg.propagate = False

    kernel = Kernel()
    kernel.add_plugin(Pharmacy(), plugin_name="pharmacy")
    chat = ScriptedChat(ai_model_id="scripted", service_id="scripted")
    kernel.add_service(chat)
    settings = PromptExecutionSettings(service_id="scripted",
                                       function_choice_behavior=FunctionChoiceBehavior.Auto())
    history = ChatHistory()
    history.add_user_message("Start apixaban 5 mg oral BID for pt-123.")
    reply = await chat.get_chat_message_contents(history, settings, kernel=kernel, arguments=None)

    print(f"semantic-kernel {SK}, case={CASE}")
    print(f"model turns: {chat.calls}; final text: {reply[0].content!r}")
    print(f"record rows: {len(RECORD)}")
    tool_msgs = [m for m in history.messages if m.role == AuthorRole.TOOL]
    tool_result = "".join(str(getattr(i, "result", "")) for m in tool_msgs for i in m.items)
    print(f"tool result handed to the model: {tool_result!r}")
    print("audit sink received, from the framework's loggers:")
    for name, level, msg in sink.lines:
        if "place_order" in msg or "Function" in msg or "function" in msg:
            print(f"  [{level}] {name}: {msg[:220]}")
    joined = "\n".join(m for _, _, m in sink.lines)
    counts = {
        "lines naming the function": sum("place_order" in m for _, _, m in sink.lines),
        "lines carrying the patient id (pt-123)": sum("pt-123" in m for _, _, m in sink.lines),
        "lines carrying the drug (apixaban)": sum("apixaban" in m for _, _, m in sink.lines),
        "lines carrying the result (ORDER PLACED)": sum("ORDER PLACED" in m for _, _, m in sink.lines),
        "lines carrying the refusal reason (contraindicated)": sum("contraindicated" in m for _, _, m in sink.lines),
    }
    for k, v in counts.items():
        print(f"  {k}: {v}")
    assert "pt-123" in joined or SK >= "1.46", "expected the 1.45.0 log to carry the patient id"


if __name__ == "__main__":
    asyncio.run(main())
