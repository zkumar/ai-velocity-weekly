"""Builds models.json for AI Velocity Weekly 05 and prints the section 2 table.

Workload: 10,000 clinical documents at 4,000 input and 500 output tokens.
  cost_no_cache = 40 * in + 5 * out                 (USD; prices are $ per million tokens)
  cost_cached   = 8 * in + 32 * cached + 5 * out    (80% of input served from cache)
Cache-write fees excluded. Prices are vendor list, read 2 October 2026; hosted open models use
Together AI this week (Nebius Token Factory's price page could not be read). AA is the Artificial
Analysis Intelligence Index, still v4.3.2, read from artificialanalysis.ai/leaderboards/models
on 2 October. "med" is the AA Healthcare & Medical Index, an independent measurement; this week
only its top three rows could be read (the rest of the page is script-rendered), so every other
row carries None and "med_25sep" keeps the value read for Issue 04 where there was one.
"verified" is False where the price was not read on the vendor's own API price page.
"""
import json


def cost(p):
    c1 = round(40 * p["in"] + 5 * p["out"], 2)
    c2 = round(8 * p["in"] + 32 * p["cached"] + 5 * p["out"], 2) if p["cached"] is not None else None
    return c1, c2


R = lambda **k: k  # noqa: E731
OA = "https://developers.openai.com/api/docs/pricing"
AN = "https://platform.claude.com/docs/en/about-claude/pricing"
ROWS = [
 R(model="GPT-6 Astra", licence="closed", price={"in": 10, "out": 50, "cached": 1.0}, aa=53, med=None, med_25sep=51.7,
   verified=True, note="unchanged", src=OA),
 R(model="Claude Fable 5.1", licence="closed", price={"in": 10, "out": 50, "cached": 0.25}, aa=53, med=58, med_25sep=58.0,
   verified=True, note="unchanged", src=AN),
 R(model="Claude Opus 5.5", licence="closed", price={"in": 4, "out": 20, "cached": 0.2}, aa=58, med=61, med_25sep=60.5,
   verified=True, note="unchanged; medical index read as 61 this week, 60.5 last week", src=AN),
 R(model="Claude Sonnet 5.5", licence="closed", price={"in": 2, "out": 10, "cached": 0.2}, aa=56, med=58, med_25sep=None,
   verified=True, note="NEW 28 Sept; same price as Sonnet 5; forced tool_choice returns 400", src=AN),
 R(model="GPT-6.1 Sol", licence="closed", price={"in": 2, "out": 10, "cached": 0.1}, aa=52, med=None, med_25sep=None,
   verified=True, note="NEW 29 Sept, replaces GPT-6 Sol after seven days; cached input 0.20 to 0.10; AA 48 to 52", src=OA),
 R(model="Gemini 4 Argon", licence="closed", price={"in": 2, "out": 10, "cached": 0.1}, aa=53, med=None, med_25sep=None,
   verified=False, note="announced 30 Sept, limited access; introductory price from the Google blog (4/20 regular), cached taken as 95% off input; not on the Gemini API price page",
   src="https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/"),
 R(model="Kimi K3", licence="API", price={"in": 3.0, "out": 15.0, "cached": 0.3}, aa=44, med=None, med_25sep=None,
   verified=True, note="first week in the table", src="https://platform.kimi.ai/docs/pricing/chat"),
 R(model="Grok 4.7", licence="closed", price={"in": 2, "out": 6, "cached": 0.5}, aa=46, med=None, med_25sep=47.2,
   verified=True, note="unchanged", src="https://docs.x.ai/developers/pricing"),
 R(model="Mistral Medium 3.5", licence="open, modified MIT", price={"in": 1.5, "out": 7.5, "cached": None}, aa=None, med=None, med_25sep=None,
   verified=True, note="first week in the table; cache discount listed only as -90%; AA score not read", src="https://mistral.ai/pricing/api"),
 R(model="GLM-5.3", licence="open, custom licence", price={"in": 1.40, "out": 4.40, "cached": 0.26}, aa=45, med=None, med_25sep=46.7,
   verified=False, note="Together AI host price, equal to last week's vendor price; GA on Mistral's platform 28 Sept at the same rate", src="https://www.together.ai/pricing"),
 R(model="DeepSeek-V4-Pro", licence="API", price={"in": 1.32, "out": 3.96, "cached": 0.044}, aa=36, med=None, med_25sep=None,
   verified=True, note="first week in the table; peak rate, off-peak is half", src="https://api-docs.deepseek.com/quick_start/pricing"),
 R(model="Claude Haiku 4.5", licence="closed", price={"in": 1, "out": 5, "cached": 0.1}, aa=17, med=None, med_25sep=None,
   verified=True, note="first week in the table", src=AN),
 R(model="Kimi K2.6", licence="API", price={"in": 0.95, "out": 4.0, "cached": 0.16}, aa=None, med=None, med_25sep=None,
   verified=True, note="first week in the table; AA score not read", src="https://platform.kimi.ai/docs/pricing/chat"),
 R(model="Gemini 3.8 Flash", licence="closed", price={"in": 0.75, "out": 3.75, "cached": 0.075}, aa=41, med=None, med_25sep=41.8,
   verified=True, note="unchanged; promo to 31 Dec, 1.50 input from 1 Jan 2027", src="https://ai.google.dev/gemini-api/docs/pricing"),
 R(model="DeepSeek-V4.1-Flash", licence="open, MIT", price={"in": 0.30, "out": 1.20, "cached": 0.006}, aa=39, med=None, med_25sep=40.6,
   verified=True, note="unchanged; peak rate, off-peak is half", src="https://api-docs.deepseek.com/quick_start/pricing"),
 R(model="gpt-oss-120B", licence="open weights", price={"in": 0.15, "out": 0.60, "cached": None}, aa=12, med=None, med_25sep=None,
   verified=False, note="Together AI host price; no cached rate listed", src="https://www.together.ai/pricing"),
 R(model="GPT-6 Luna", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=38, med=None, med_25sep=36.7,
   verified=True, note="unchanged price; AA 37 to 38", src=OA),
]
for r in ROWS:
    r["cost_10k_docs_no_cache"], r["cost_10k_docs_80pct_cached"] = cost(r["price"])

doc = {"issue": 5, "week_ending": "2026-10-02", "prices_read": "2026-10-02",
       "workload": "10,000 docs x (4,000 in + 500 out) tokens",
       "aa_index": "v4.3.2, read 2 Oct 2026; healthcare index top three rows only", "models": ROWS}
json.dump(doc, open("models.json", "w"), indent=1)
for r in sorted(ROWS, key=lambda r: r["cost_10k_docs_no_cache"]):
    p = r["price"]
    c2 = r["cost_10k_docs_80pct_cached"]
    print(f'{r["model"]:20s} {p["in"]:>5}/{p["out"]:<5}/{str(p["cached"]):6s} AA {str(r["aa"]):4s} med {str(r["med"]):5s} '
          f'${r["cost_10k_docs_no_cache"]:>7} / {("$" + str(c2)) if c2 is not None else "n.a.":>8}'
          f'{"" if r["verified"] else "  (not a vendor API price page)"}')
