"""pydantic-ai-slim 2.53.0 against 2.54.0: where the before/after hooks sit relative to a wrapper.

PR #7053 (in 2.54.0, uploaded 3 Oct 2026): wrap_* hooks now enclose the whole stage lifecycle.
An audit capability counts model requests in before_model_request / after_model_request, and
wraps the request. Second run: the wrapper answers from a cache and never calls the handler.
FunctionModel, no API key. The question: when the wrapper short-circuits, does the audit row
still get written?
"""
import importlib.metadata as md
from dataclasses import dataclass

from pydantic_ai import Agent
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ModelResponse, TextPart
from pydantic_ai.models.function import FunctionModel

VERSION = md.version("pydantic-ai-slim")
LOG = []


def model(messages, info):
    LOG.append("MODEL")
    return ModelResponse(parts=[TextPart("K+ 6.1 mmol/L is critical; hold lisinopril.")])


@dataclass
class AuditAndCache(AbstractCapability):
    cached: bool = False

    async def before_model_request(self, ctx, request_context):
        LOG.append("audit:before")
        return request_context

    async def after_model_request(self, ctx, *, request_context, response):
        LOG.append("audit:after")
        return response

    async def wrap_model_request(self, ctx, *, request_context, handler):
        LOG.append("wrap:enter")
        if self.cached:
            LOG.append("wrap:cache-hit")
            return ModelResponse(parts=[TextPart("(cached) hold lisinopril.")])
        r = await handler(request_context)
        LOG.append("wrap:exit")
        return r


if __name__ == "__main__":
    print(f"pydantic-ai-slim {VERSION}")
    counts = {}
    for cached in (False, True):
        LOG.clear()
        out = Agent(FunctionModel(model), capabilities=[AuditAndCache(cached=cached)]).run_sync("Review pt-123 potassium.")
        n = sum(1 for x in LOG if x.startswith("audit:"))
        counts[cached] = n
        print(f"  wrapper {'answers from cache' if cached else 'calls the model  '}: {LOG} | output={out.output!r}")
    print(f"  SUMMARY {VERSION}: audit hook rows, model called={counts[False]}, wrapper short-circuit={counts[True]}")
