"""Builds models.json for AI Velocity Weekly 04 and prints the section 2 table.

Workload: 10,000 clinical documents at 4,000 input and 500 output tokens.
  cost_no_cache = 40 * in + 5 * out                 (USD; prices are $ per million tokens)
  cost_cached   = 8 * in + 32 * cached + 5 * out    (80% of input served from cache)
Cache-write fees excluded. Prices are vendor list, read 25 September 2026; hosted open models
use OpenRouter. AA is the Artificial Analysis Intelligence Index, now v4.3.2 (changelog dated
19 September: GDPval-AA v2.1 Elo re-anchored to DeepSeek V4.1 Flash = 1600), read from
artificialanalysis.ai/leaderboards/models on 25 September. "med" is the AA Healthcare & Medical
Index, an independent measurement, read the same day; None where the model is not scored.
"verified" is False where the price could only be read from a reseller and not a vendor page.
"""
import json

def cost(p):
    c1 = round(40 * p["in"] + 5 * p["out"], 2)
    c2 = round(8 * p["in"] + 32 * p["cached"] + 5 * p["out"], 2) if p["cached"] is not None else None
    return c1, c2

R = lambda **k: k
ROWS = [
 R(model="GPT-6 Astra", licence="closed", price={"in": 10, "out": 50, "cached": 1.0}, aa=53, med=51.7, verified=True,
   note="unchanged; Batch/Flex 5/25/0.50", src="https://developers.openai.com/api/docs/pricing"),
 R(model="Claude Fable 5.1", licence="closed", price={"in": 10, "out": 50, "cached": 0.25}, aa=53, med=58.0, verified=True,
   note="unchanged", src="https://platform.claude.com/docs/en/about-claude/pricing"),
 R(model="Claude Opus 5", licence="closed", price={"in": 5, "out": 25, "cached": 0.5}, aa=51, med=53.3, verified=True,
   note="unchanged; AA now lists it deprecated; Anthropic retirement not sooner than 24 Jul 2027",
   src="https://platform.claude.com/docs/en/about-claude/pricing"),
 R(model="Claude Opus 5.5", licence="closed", price={"in": 4, "out": 20, "cached": 0.2}, aa=58, med=60.5, verified=True,
   note="NEW 22 Sept; cache read 0.20 against Opus 5's 0.50; Anthropic says the 4.7+ tokenizer yields about 30% more tokens for the same text*",
   src="https://platform.claude.com/docs/en/about-claude/pricing"),
 R(model="GPT-6 Sol", licence="closed", price={"in": 2, "out": 10, "cached": 0.2}, aa=48, med=43.5, verified=True,
   note="NEW 22 Sept; Batch/Flex 1/5/0.10; prices for prompts up to 272K tokens", src="https://developers.openai.com/api/docs/pricing"),
 R(model="GPT-5.6 Sol", licence="closed", price={"in": 4, "out": 20, "cached": 0.4}, aa=47, med=45.4, verified=True,
   note="unchanged, promotional to at least 21 Nov; AA now lists it deprecated; superseded by GPT-6 Sol",
   src="https://developers.openai.com/api/docs/pricing"),
 R(model="Grok 4.7", licence="closed", price={"in": 2, "out": 6, "cached": 0.5}, aa=46, med=47.2, verified=True,
   note="NEW 21 Sept; OpenRouter lists 1.60/4.80/0.40, 20% under the vendor page; vendor price used", src="https://docs.x.ai/docs/pricing"),
 R(model="Muse Spark 1.3", licence="closed", price={"in": 1.25, "out": 4.25, "cached": 0.15}, aa=48, med=49.7, verified=False,
   note="unchanged; OpenRouter listing with Meta as provider, no vendor page found", src="https://openrouter.ai/meta/muse-spark-1.3"),
 R(model="GLM-5.3", licence="open, custom licence", price={"in": 1.40, "out": 4.40, "cached": 0.26}, aa=45, med=46.7, verified=True,
   note="unchanged", src="https://docs.z.ai/guides/overview/pricing"),
 R(model="Qwen3.8-Max-0902", licence="API only", price={"in": 2, "out": 6, "cached": 0.25}, aa=45, med=41.4, verified=True,
   note="in/out now read on the Alibaba Model Studio page; cached rate is OpenRouter's, Alibaba gives no exact figure",
   src="https://www.alibabacloud.com/help/en/model-studio/model-pricing"),
 R(model="GLM-5.3-Flash", licence="open, MIT", price={"in": 0.15, "out": 0.50, "cached": 0.03}, aa=42, med=44.8, verified=True,
   note="unchanged", src="https://docs.z.ai/guides/overview/pricing"),
 R(model="Gemini 3.8 Flash", licence="closed", price={"in": 0.75, "out": 3.75, "cached": 0.075}, aa=41, med=41.8, verified=True,
   note="promo to 31 Dec; 1.50/7.50/0.15 from 1 Jan 2027", src="https://ai.google.dev/gemini-api/docs/pricing"),
 R(model="DeepSeek-V4.1-Flash", licence="open, MIT", price={"in": 0.30, "out": 1.20, "cached": 0.006}, aa=39, med=40.6, verified=True,
   note="unchanged; off-peak half; API name now deepseek-flash; AA 40 to 39 under v4.3.2", src="https://api-docs.deepseek.com/quick_start/pricing"),
 R(model="GPT-6 Luna", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=37, med=36.7, verified=True,
   note="NEW 22 Sept; Batch 0.05/0.25/0.005", src="https://developers.openai.com/api/docs/pricing"),
 R(model="Qwen3.8-27B", licence="open, Apache 2.0", price={"in": 0.10, "out": 1.80, "cached": None}, aa=34, med=34.4, verified=False,
   note="single FP4 host on OpenRouter; default listing now 0.42/3.00/0.085, Alibaba first-party 0.50/3.00 ($35); AA split into effort variants, xhigh 34, non-reasoning 20",
   src="https://openrouter.ai/qwen/qwen3.8-27b"),
 R(model="Qwen3.8-Omni-Flash", licence="API only", price={"in": 0.15, "out": 0.47, "cached": 0.016}, aa=None, med=None, verified=True,
   note="now read on the Alibaba Model Studio page (updated 24 Sept); not scored by AA", src="https://www.alibabacloud.com/help/en/model-studio/model-pricing"),
 R(model="Granite 4.2 8B", licence="open, Apache 2.0", price={"in": 0.06, "out": 0.25, "cached": 0.015}, aa=11, med=None, verified=False,
   note="OpenRouter (DeepInfra) only; IBM lists no first-party price; AA 12 to 11 under v4.3.2", src="https://openrouter.ai/ibm-granite/granite-4.2-8b"),
]
for r in ROWS:
    r["cost_10k_docs_no_cache"], r["cost_10k_docs_80pct_cached"] = cost(r["price"])

doc = {"issue": 4, "week_ending": "2026-09-25", "prices_read": "2026-09-25",
       "workload": "10,000 docs x (4,000 in + 500 out) tokens",
       "aa_index": "v4.3.2 (changelog 19 Sept 2026); healthcare index read 25 Sept", "models": ROWS}
json.dump(doc, open("models.json", "w"), indent=1)
for r in sorted(ROWS, key=lambda r: r["cost_10k_docs_no_cache"]):
    p = r["price"]
    print(f'{r["model"]:20s} {p["in"]:>5}/{p["out"]:<5}/{str(p["cached"]):6s} AA {str(r["aa"]):4s} med {str(r["med"]):5s} '
          f'${r["cost_10k_docs_no_cache"]:>7} / {("$"+str(r["cost_10k_docs_80pct_cached"])) if r["cost_10k_docs_80pct_cached"] is not None else "n.a.":>8}'
          f'{"" if r["verified"] else "  (reseller price)"}')
