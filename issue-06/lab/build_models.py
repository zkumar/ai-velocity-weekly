"""Builds models.json for AI Velocity Weekly 06 and prints the section 2 table.

Workload: 10,000 clinical documents at 4,000 input and 500 output tokens.
  cost_no_cache = 40 * in + 5 * out                 (USD; prices are $ per million tokens)
  cost_cached   = 8 * in + 32 * cached + 5 * out    (80% of input served from cache)
Cache-write fees excluded. Prices are vendor list prices read on 9 October 2026 from the pages in
"src". AA is the Artificial Analysis Intelligence Index, v4.3.2 (changelog entry 19 September
2026), best listed variant, read from artificialanalysis.ai/leaderboards/models on 9 October.
The AA Healthcare & Medical Index page did not load on 9 October, so this file carries no
medical-index column this week rather than repeat an older reading.
"verified" is False where the price could not be read on the vendor's own current price page.
"cached_carried" is True where the cache-read rate is the one read on 25 September (Issue 04)
because this week's read of the vendor page returned input and output only.
"""
import json


def cost(p):
    c1 = round(40 * p["in"] + 5 * p["out"], 2)
    c2 = round(8 * p["in"] + 32 * p["cached"] + 5 * p["out"], 2) if p["cached"] is not None else None
    return c1, c2


R = lambda **k: k
ROWS = [
 R(model="GPT-6 Astra", id="gpt-6-astra", licence="closed", price={"in": 10, "out": 50, "cached": 1.00}, aa=53, verified=True,
   note="unchanged; long-context tier 20/75/2.00", src="https://developers.openai.com/api/docs/pricing"),
 R(model="Claude Fable 5.1", id="claude-fable-5-1", licence="closed", price={"in": 10, "out": 50, "cached": 0.25}, aa=53, verified=True,
   note="unchanged", src="https://platform.claude.com/docs/en/about-claude/pricing"),
 R(model="Claude Opus 5.5", id="claude-opus-5-5", licence="closed", price={"in": 4, "out": 20, "cached": 0.20}, aa=58, verified=True,
   note="unchanged; first on the index", src="https://platform.claude.com/docs/en/about-claude/pricing"),
 R(model="Kimi K3", id="kimi-k3", licence="API only", price={"in": 3, "out": 15, "cached": 0.30}, aa=44, verified=True,
   note="not in the Issue 04 table; 1,048,576-token context; no price change in window", src="https://platform.kimi.ai/docs/pricing/chat"),
 R(model="Claude Sonnet 5.5", id="claude-sonnet-5-5", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=56, verified=True,
   note="released 28 Sept; cache read cut from 0.20 to 0.10 on 7 Oct (release notes)", src="https://platform.claude.com/docs/en/about-claude/pricing"),
 R(model="GPT-6.1 Sol", id="gpt-6.1-sol", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=52, verified=True,
   note="released 29 Sept; gpt-6-sol is no longer on the price page; long-context tier 4/15/0.20; Ultrafast service tier added 8 Oct",
   src="https://developers.openai.com/api/docs/pricing"),
 R(model="Gemini 4 Argon", id="gemini-4-argon", licence="closed", price={"in": 2, "out": 10, "cached": None}, aa=53, verified=False,
   note="UNVERIFIED price: not on the Gemini API price, models or changelog pages on 9 Oct; 2/10 is a third-party report of an introductory price",
   src="https://ai.google.dev/gemini-api/docs/pricing"),
 R(model="Grok 4.7", id="grok-4.7", licence="closed", price={"in": 2, "out": 6, "cached": 0.50}, aa=46, verified=True, cached_carried=True,
   note="unchanged; above 200k prompt tokens 4/12", src="https://docs.x.ai/developers/models"),
 R(model="Mistral Large 4 (preview)", id="mistral-large-4", licence="open weights announced, licence not named", price={"in": 1.36, "out": 4.18, "cached": 0.14}, aa=38, verified=True,
   note="NEW 6 Oct, public preview, 1M context; launch sale 0.68/2.09/0.07 makes the workload $37.65 and $18.13 cached",
   src="https://docs.mistral.ai/models/model-cards/mistral-large-4-0"),
 R(model="Gemini 3.8 Flash", id="gemini-3.8-flash", licence="closed", price={"in": 0.75, "out": 3.75, "cached": 0.075}, aa=41, verified=True, cached_carried=True,
   note="promotional to 31 Dec; 1.50/7.50 from 1 Jan 2027", src="https://ai.google.dev/gemini-api/docs/pricing"),
 R(model="DeepSeek V4.1 Flash", id="deepseek-flash", licence="open, MIT", price={"in": 0.30, "out": 1.20, "cached": 0.006}, aa=39, verified=True, cached_carried=True,
   note="peak rate; off-peak is half (0.15/0.60, $9.00)", src="https://api-docs.deepseek.com/quick_start/pricing"),
 R(model="gpt-oss-120b on Nebius", id="gpt-oss-120b", licence="open, Apache 2.0", price={"in": 0.15, "out": 0.60, "cached": None}, aa=12, verified=False,
   note="read on nebius.com/prices-ai-studio, which still lists a model Nebius deprecated on 31 Aug; the current Token Factory price page could not be read",
   src="https://nebius.com/prices-ai-studio"),
 R(model="Claude Haiku 5.5", id="claude-haiku-5-5", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=43, verified=True,
   note="NEW 7 Oct; prompts over 100,000 tokens pay 0.50/2.50/0.05; AA 29 at low effort",
   src="https://platform.claude.com/docs/en/about-claude/pricing"),
 R(model="GPT-6 Luna", id="gpt-6-luna", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=38, verified=True,
   note="unchanged; AA 18 non-reasoning", src="https://developers.openai.com/api/docs/pricing"),
]

if __name__ == "__main__":
    out = []
    for r in ROWS:
        c1, c2 = cost(r["price"])
        out.append({**r, "cost_10k_docs_no_cache": c1, "cost_10k_docs_80pct_cached": c2})
    out.sort(key=lambda r: r["cost_10k_docs_no_cache"])
    doc = {"issue": 6, "week_ending": "2026-10-09", "prices_read": "2026-10-09",
           "workload": "10,000 docs x (4,000 in + 500 out) tokens",
           "aa_index": "v4.3.2 (changelog 19 Sept 2026), read 9 Oct 2026; healthcare index page did not load, no medical column this week",
           "models": out}
    json.dump(doc, open("models.json", "w"), indent=1)
    print(f"{'model':28} {'in/out/cached':>20} {'AA':>4} {'no cache':>10} {'80% cached':>11}  verified")
    for r in out:
        p = r["price"]
        cached = "n/a" if p["cached"] is None else f"{p['cached']:g}"
        c2 = "n/a" if r["cost_10k_docs_80pct_cached"] is None else f"${r['cost_10k_docs_80pct_cached']:.2f}"
        print(f"{r['model']:28} {p['in']:g}/{p['out']:g}/{cached:>6} {r['aa']:>4} "
              f"${r['cost_10k_docs_no_cache']:>9.2f} {c2:>11}  {r['verified']}")
