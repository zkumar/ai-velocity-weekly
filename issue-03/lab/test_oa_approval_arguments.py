"""OpenAI Agents SDK 0.22.3: does the approval policy see the arguments the tool runs with?

Synthetic data, scripted model (agents.testing.ScriptedModel), no API key.
run_all.sh runs this file under openai-agents 0.22.2 and 0.22.3 so the two can be compared.

The policy a CPOE team would write: an IV order, or a dose above 1,000 mg, needs a clinician.
Two tools carry it:
  flat   write_order(patient_id, rxnorm, dose_mg: int, route: str = "IV")    data-only schema
  model  write_order_v(patient_id, rxnorm, dose: Dose, route: str = "PO")   Dose normalises g to mg
Four model tool calls:
  A  flat,  everything explicit, oral 500 mg          (should run)
  B  flat,  route omitted, the tool default is IV     (should need a clinician)
  C  model, oral 500 mg                               (should run)
  D  model, dose sent as 1.5 g, executes as 1,500 mg  (should need a clinician)
For each: what the policy callable saw, whether the run paused, what the clinician is shown,
how many writes happened before any approval, and what reached the FHIR stub.
"""
import asyncio, copy, json

from pydantic import BaseModel, model_validator
import agents
from agents import Agent, RunConfig, Runner, function_tool
from agents.testing import ScriptedModel
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText

FHIR: list[dict] = []
SAW: list[dict] = []


async def needs_clinician(_ctx, params, _call_id) -> bool:
    SAW.append(copy.deepcopy(params))
    mg = params.get("dose_mg", params.get("dose", {}).get("amount", 0))   # doses are stored in mg
    return params.get("route") == "IV" or mg > 1000


@function_tool(needs_approval=needs_clinician, strict_mode=False)
def write_order(patient_id: str, rxnorm: str, dose_mg: int, route: str = "IV") -> str:
    """Write a MedicationRequest to the FHIR server."""
    FHIR.append({"tool": "write_order", "dose_mg": dose_mg, "route": route})
    return "MedicationRequest written"


class Dose(BaseModel):
    amount: float
    unit: str = "mg"

    @model_validator(mode="after")
    def to_mg(self):                       # the ordinary normalisation step
        if self.unit == "g":
            self.amount, self.unit = self.amount * 1000, "mg"
        return self


@function_tool(needs_approval=needs_clinician, strict_mode=False)
def write_order_v(patient_id: str, rxnorm: str, dose: Dose, route: str = "PO") -> str:
    """Write a MedicationRequest to the FHIR server (dose normalised to mg)."""
    FHIR.append({"tool": "write_order_v", "dose_mg": dose.amount, "route": route})
    return "MedicationRequest written"


def call(name: str, args: dict) -> ResponseFunctionToolCall:
    return ResponseFunctionToolCall(id="fc_1", call_id="call_1", type="function_call",
                                    name=name, arguments=json.dumps(args))


def text(s: str) -> ResponseOutputMessage:
    return ResponseOutputMessage(id="m1", type="message", role="assistant", status="completed",
                                 content=[ResponseOutputText(type="output_text", text=s, annotations=[])])


PT = {"patient_id": "pt-123", "rxnorm": "860975"}
CASES = [
    ("A flat, oral 500 mg explicit", "write_order", {**PT, "dose_mg": 500, "route": "PO"}),
    ("B flat, route omitted (default IV)", "write_order", {**PT, "dose_mg": 500}),
    ("C model, oral 500 mg", "write_order_v", {**PT, "dose": {"amount": 500, "unit": "mg"}}),
    ("D model, 1.5 g (runs as 1,500 mg)", "write_order_v", {**PT, "dose": {"amount": 1.5, "unit": "g"}}),
]


async def run_case(label, tool, args):
    FHIR.clear(); SAW.clear()
    model = ScriptedModel([[call(tool, args)], [text("Order placed.")]])
    agent = Agent(name="orders", model=model, tools=[write_order, write_order_v])
    cfg = RunConfig(tracing_disabled=True)
    r = await Runner.run(agent, "Start metformin for pt-123", run_config=cfg)
    paused = bool(r.interruptions)
    shown = r.interruptions[0].raw_item.arguments if paused else None
    before = len(FHIR)
    if paused:                                   # the clinician approves what they were shown
        state = r.to_state()
        state.approve(r.interruptions[0])
        r = await Runner.run(agent, state, run_config=cfg)
    print(f"  {label}")
    print(f"    policy saw   : {SAW[0] if SAW else 'policy not called'}")
    print(f"    paused       : {paused}" + (f" | clinician shown: {shown}" if paused else ""))
    print(f"    writes before approval: {before} | FHIR: {FHIR} | model said: {r.final_output!r}")
    return {"case": label[0], "paused": paused, "unapproved_writes": before,
            "executed": FHIR[0] if FHIR else None, "shown": shown}


async def main():
    print(f"openai-agents {agents.__version__}")
    rows = [await run_case(*c) for c in CASES]
    should_pause = {"B", "D"}
    missed = sum(1 for x in rows if x["case"] in should_pause and not x["paused"])
    extra = sum(1 for x in rows if x["case"] not in should_pause and x["paused"])
    print(f"  SUMMARY: policy-required approvals missed={missed} of 2 | "
          f"approvals added on safe calls={extra} of 2 | "
          f"unapproved writes={sum(x['unapproved_writes'] for x in rows if x['case'] in should_pause)}")

asyncio.run(main())
