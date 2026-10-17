"""AI Velocity Weekly 01, lab 5.2: the RAF gap lab (rebuilt 12 Sept 2026).

A synthetic progress note is read for MEAT-supported ICD-10 codes, each
with a verbatim evidence span, and hccinfhir (Apache-2.0) scores the
result under CMS-HCC V24 and V28 beside the claims-only baseline.

Two modes:
  offline (default): the hand-coded extraction below stands in for the model.
  --model <name>:    a Pydantic AI agent with a typed output does the
                     extraction; diff it against the hand-coded one. That
                     disagreement rate is your first eval number.

Run:  pip install hccinfhir pydantic-ai-slim
      python raf_gap_lab.py
      python raf_gap_lab.py --model anthropic:claude-opus-5   (needs a key)
Guardrail test: change "recurrent major depression" in the note to
"history of depression" and check the extractor drops F33.1.
Everything here is synthetic.
"""

from __future__ import annotations

import argparse
import asyncio

from hccinfhir import Demographics, HCCInFHIR
from pydantic import BaseModel, Field

NOTE = """72-year-old woman seen for follow-up. Type 2 diabetes with stage 3b chronic
kidney disease (eGFR 38), on metformin; A1c 7.4. Hypertension controlled on
lisinopril. Chronic systolic heart failure, NYHA II, euvolaemic today, continue
carvedilol and furosemide. COPD with daily inhaler use, no exacerbation this
year, continue tiotropium. Recurrent major depression, moderate, stable on
sertraline 100 mg, PHQ-9 of 9. Morbid obesity, BMI 41, discussed GLP-1 referral.
Status post left below-knee amputation 2019, prosthesis fits well, skin intact."""

CLAIMS_ONLY = ["E119", "I10", "N1832"]   # what came through on claims this year


class Finding(BaseModel):
    icd10: str = Field(description="ICD-10-CM code without the dot, e.g. I5022")
    evidence: str = Field(description="verbatim span from the note that supports MEAT (monitor, evaluate, assess, treat)")


class Extraction(BaseModel):
    findings: list[Finding]


HAND_CODED = Extraction(findings=[
    Finding(icd10="E1122", evidence="Type 2 diabetes with stage 3b chronic kidney disease (eGFR 38), on metformin"),
    Finding(icd10="N1832", evidence="stage 3b chronic kidney disease (eGFR 38)"),
    Finding(icd10="I10", evidence="Hypertension controlled on lisinopril"),
    Finding(icd10="I5022", evidence="Chronic systolic heart failure, NYHA II, euvolaemic today, continue carvedilol"),
    Finding(icd10="J449", evidence="COPD with daily inhaler use, no exacerbation this year, continue tiotropium"),
    Finding(icd10="F331", evidence="Recurrent major depression, moderate, stable on sertraline 100 mg, PHQ-9 of 9"),
    Finding(icd10="E6601", evidence="Morbid obesity, BMI 41, discussed GLP-1 referral"),
    Finding(icd10="Z89511", evidence="Status post left below-knee amputation 2019, prosthesis fits well"),
])


def score(codes: list[str], model: str, demo: Demographics):
    return HCCInFHIR(model_name=model).calculate_from_diagnosis(codes, demo)


def report(extraction: Extraction, label: str) -> None:
    flat = " ".join(NOTE.split())
    bad = [f for f in extraction.findings if " ".join(f.evidence.split()) not in flat]
    if bad:
        print(f"  {label}: {len(bad)} finding(s) with evidence not found verbatim in the note:", [f.icd10 for f in bad])
    demo = Demographics(age=72, sex="F")
    note_codes = [f.icd10 for f in extraction.findings]
    print(f"\n{label}")
    print(f"{'Model':18s} {'Claims only':>12s} {'Claims + note':>14s} {'Delta':>7s}  HCCs added by the note")
    for model in ["CMS-HCC Model V24", "CMS-HCC Model V28"]:
        a = score(CLAIMS_ONLY, model, demo)
        b = score(CLAIMS_ONLY + note_codes, model, demo)
        added = sorted(set(b.hcc_list) - set(a.hcc_list), key=int)
        print(f"{model:18s} {a.risk_score:12.3f} {b.risk_score:14.3f} {b.risk_score - a.risk_score:7.3f}  {', '.join(added)}")


async def extract_with_model(model_name: str) -> Extraction:
    from pydantic_ai import Agent
    agent = Agent(model_name, output_type=Extraction, instructions=(
        "Extract ICD-10-CM codes that are MEAT-supported in the note (monitored, evaluated, assessed or treated "
        "at this visit). Historical or resolved conditions do not count. Every finding must carry a verbatim span."))
    result = await agent.run(NOTE)
    return result.output


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", help="Pydantic AI model name, e.g. anthropic:claude-opus-5")
    args = ap.parse_args()
    report(HAND_CODED, "Offline (hand-coded extraction)")
    if args.model:
        ext = asyncio.run(extract_with_model(args.model))
        report(ext, f"Model extraction ({args.model})")
        hand = {f.icd10 for f in HAND_CODED.findings}
        got = {f.icd10 for f in ext.findings}
        print("\nDisagreement: missed", sorted(hand - got), "| extra", sorted(got - hand),
              f"| rate {len(hand ^ got) / len(hand | got):.2f}")


if __name__ == "__main__":
    main()
