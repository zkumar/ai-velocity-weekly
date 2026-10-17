"""Builds models.json for AI Velocity Weekly 03 and prints the section 2 table.

Workload: 10,000 clinical documents at 4,000 input and 500 output tokens.
  cost_no_cache = 40 * in + 5 * out                 (USD; prices are $ per million tokens)
  cost_cached   = 8 * in + 32 * cached + 5 * out    (80% of input served from cache)
Cache-write fees excluded. Prices are vendor list, read 20 September 2026; hosted open models
use OpenRouter. AA is the Artificial Analysis Intelligence Index v4.3 (unchanged since the
7 September rebase), read from artificialanalysis.ai/leaderboards/models on 20 September.
"verified" is False where the price page could not be read and last week's figure is carried.
"""
import json

def cost(p):
    c1 = round(40 * p["in"] + 5 * p["out"], 2)
    c2 = round(8 * p["in"] + 32 * p["cached"] + 5 * p["out"], 2) if p["cached"] is not None else None
    return c1, c2

R = lambda **k: k
ROWS = [
 R(model="GPT-6 Astra", licence="closed", price={"in": 10, "out": 50, "cached": 1.0}, aa=53, verified=True,
   note="unchanged; Batch/Flex 5/25/0.50, long context 20/75/2.00", src="https://developers.openai.com/api/docs/pricing"),
 R(model="Claude Fable 5.1", licence="closed", price={"in": 10, "out": 50, "cached": 0.25}, aa=53, verified=True,
   note="unchanged", src="https://platform.claude.com/docs/en/about-claude/pricing"),
 R(model="Claude Opus 5", licence="closed", price={"in": 5, "out": 25, "cached": 0.5}, aa=51, verified=True,
   note="unchanged", src="https://platform.claude.com/docs/en/about-claude/pricing"),
 R(model="GPT-5.6 Sol", licence="closed", price={"in": 4, "out": 20, "cached": 0.4}, aa=47, verified=True,
   note="CORRECTION: issue 02 listed 5/30/0.50; the pricing page shows 4/20/0.40, promotional to at least 21 Nov",
   src="https://developers.openai.com/api/docs/pricing"),
 R(model="Muse Spark 1.3", licence="closed", price={"in": 1.25, "out": 4.25, "cached": 0.15}, aa=48, verified=True,
   note="unchanged (OpenRouter listing)", src="https://openrouter.ai/meta/muse-spark-1.3"),
 R(model="GLM-5.3", licence="open, custom licence", price={"in": 1.40, "out": 4.40, "cached": 0.26}, aa=45, verified=True,
   note="unchanged", src="https://docs.z.ai/guides/overview/pricing"),
 R(model="Qwen3.8-Max-0902", licence="API only", price={"in": 2, "out": 6, "cached": 0.25}, aa=45, verified=False,
   note="price page shows no prices, last week's carried; AA reads 45 where issue 02 printed 40, reason not established",
   src="https://artificialanalysis.ai/leaderboards/models"),
 R(model="GLM-5.3-Flash", licence="open, MIT", price={"in": 0.15, "out": 0.50, "cached": 0.03}, aa=42, verified=True,
   note="unchanged", src="https://docs.z.ai/guides/overview/pricing"),
 R(model="Gemini 3.8 Flash", licence="closed", price={"in": 0.75, "out": 3.75, "cached": 0.075}, aa=41, verified=True,
   note="promo to 31 Dec; 1.50/7.50/0.15 from 1 Jan 2027", src="https://ai.google.dev/gemini-api/docs/pricing"),
 R(model="DeepSeek-V4.1-Flash", licence="open, MIT", price={"in": 0.30, "out": 1.20, "cached": 0.006}, aa=40, verified=True,
   note="unchanged; off-peak half", src="https://api-docs.deepseek.com/quick_start/pricing"),
 R(model="Qwen3.8-27B", licence="open, Apache 2.0", price={"in": 0.10, "out": 1.80, "cached": None}, aa=22, verified=True,
   note="REPRICED on OpenRouter from 0.22/2.42; AA reads 22 where issue 02 printed 34, reason not established",
   src="https://openrouter.ai/qwen/qwen3.8-27b"),
 R(model="Granite 4.2 8B", licence="open, Apache 2.0", price={"in": 0.06, "out": 0.25, "cached": 0.015}, aa=12, verified=False,
   note="price page not read this week, last week's carried", src="https://artificialanalysis.ai/leaderboards/models"),
 R(model="Qwen3.8-Omni-Flash", licence="API only", price={"in": 0.15, "out": 0.47, "cached": 0.016}, aa=None, verified=False,
   note="NEW 18 Sept per a release tracker; not confirmed on a vendor page", src="https://www.digitalapplied.com/blog/ai-model-releases-september-2026-tracker"),
]
for r in ROWS:
    r["cost_10k_docs_no_cache"], r["cost_10k_docs_80pct_cached"] = cost(r["price"])

doc = {"issue": 3, "week_ending": "2026-09-18", "prices_read": "2026-09-20",
       "workload": "10,000 docs x (4,000 in + 500 out) tokens", "aa_index": "v4.3, unchanged in window",
       "models": ROWS}
json.dump(doc, open("models.json", "w"), indent=1)
for r in sorted(ROWS, key=lambda r: r["cost_10k_docs_no_cache"]):
    p = r["price"]
    print(f'{r["model"]:20s} {p["in"]:>5}/{p["out"]:<5}/{str(p["cached"]):6s} AA {str(r["aa"]):4s} '
          f'${r["cost_10k_docs_no_cache"]:>7} / {("$"+str(r["cost_10k_docs_80pct_cached"])) if r["cost_10k_docs_80pct_cached"] is not None else "n.a.":>8}'
          f'{"" if r["verified"] else "  (unverified)"}')
