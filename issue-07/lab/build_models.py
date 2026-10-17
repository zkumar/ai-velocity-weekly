"""Builds models.json for AI Velocity Weekly 07 and prints the section 2 table.

Workload: 10,000 clinical documents at 4,000 input and 500 output tokens.
  cost_no_cache = 40 * in + 5 * out                 (USD; prices are $ per million tokens)
  cost_cached   = 8 * in + 32 * cached + 5 * out    (80% of input served from cache)
Cache-write fees excluded. Prices are vendor list prices read on 16 October 2026 from the pages in
"src". AA is the Artificial Analysis Intelligence Index, v4.3.2 (changelog entry 19 September
2026, no newer version in window), best listed variant, read from
artificialanalysis.ai/leaderboards/models on 16 October. "med" is the Artificial Analysis
Healthcare & Medical Index read the same day from
artificialanalysis.ai/models/capabilities/healthcare-and-medical; only three rows could be read
from that page's text, the rest is None rather than a carried value.
"verified" is False where the price could not be read on the vendor's own current price page.
"""
import json


def cost(p):
    c1 = round(40 * p["in"] + 5 * p["out"], 2)
    c2 = round(8 * p["in"] + 32 * p["cached"] + 5 * p["out"], 2) if p["cached"] is not None else None
    return c1, c2


R = lambda **k: k
OPENAI = "https://developers.openai.com/api/docs/pricing"
ANTH = "https://platform.claude.com/docs/en/about-claude/pricing"
GOOG = "https://ai.google.dev/gemini-api/docs/pricing"
ROWS = [
 R(model="GPT-6 Astra", id="gpt-6-astra", licence="closed", price={"in": 10, "out": 50, "cached": 1.00}, aa=53, med=None, verified=True,
   note="unchanged; long-context tier 20/75/2.00", src=OPENAI),
 R(model="Claude Fable 5.1", id="claude-fable-5-1", licence="closed", price={"in": 10, "out": 50, "cached": 0.25}, aa=53, med=58, verified=True,
   note="unchanged; 1M context at the standard price", src=ANTH),
 R(model="Claude Opus 5.5", id="claude-opus-5-5", licence="closed", price={"in": 4, "out": 20, "cached": 0.20}, aa=58, med=61, verified=True,
   note="unchanged; fast mode left research preview on 15 Oct, no beta header; first on both indexes", src=ANTH),
 R(model="Kimi K3", id="kimi-k3", licence="API only", price={"in": 3, "out": 15, "cached": 0.30}, aa=44, med=None, verified=True,
   note="unchanged; cache writes billed at 3.00 (5-minute TTL) or 6.00 (1 hour)", src="https://platform.kimi.ai/docs/pricing/chat"),
 R(model="Claude Sonnet 5.5", id="claude-sonnet-5-5", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=56, med=58, verified=True,
   note="unchanged since the 7 Oct cache-read cut", src=ANTH),
 R(model="GPT-6.1 Sol", id="gpt-6.1-sol", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=52, med=None, verified=True,
   note="unchanged; long-context tier 4/15/0.20; the Ultrafast tier row (12/60/0.60) is on the page but its label did not survive the read, so that mapping is unverified",
   src=OPENAI),
 R(model="Gemini 4 Argon", id="gemini-4-argon", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=53, med=None, verified=True,
   note="GA 13 Oct and now on Google's own price page; 2/10/0.10 through 30 Nov 2026, then 4/20/0.20 from 1 Dec; implicit caching only; Issue 06 carried this row unverified",
   src=GOOG),
 R(model="Grok 4.7", id="grok-4.7", licence="closed", price={"in": 2, "out": 6, "cached": 0.50}, aa=46, med=None, verified=True,
   note="unchanged; cached rate read from docs.x.ai/developers/pricing this week rather than carried; above 200k prompt tokens 4/12/1.00 on every token of the request",
   src="https://docs.x.ai/developers/pricing"),
 R(model="Mistral Large 4 (preview)", id="mistral-large-4", licence="open weights announced, licence not named", price={"in": 1.36, "out": 4.18, "cached": 0.14}, aa=38, med=None, verified=True,
   note="list price; the price page shows the launch sale 0.68/2.09/0.07 ($37.65 and $18.13) with list struck through; the changelog said 50% off for two weeks from 6 Oct, so the sale should end around 20 Oct, an inference",
   src="https://docs.mistral.ai/inference/pricing"),
 R(model="Gemini 3.8 Flash", id="gemini-3.8-flash", licence="closed", price={"in": 0.75, "out": 3.75, "cached": 0.075}, aa=41, med=None, verified=True,
   note="0.75/3.75/0.075 through 31 Dec; 1.50/7.50/0.15 from 1 Jan 2027; cached rate read this week rather than carried; gemini-3.7-flash and 3.5-flash deprecated 8 Oct",
   src=GOOG),
 R(model="DeepSeek V4.1 Flash", id="deepseek-flash", licence="open, MIT", price={"in": 0.30, "out": 1.20, "cached": 0.006}, aa=39, med=None, verified=True,
   note="peak rate; off-peak 0.15/0.60/0.003 ($9.00); cached rate read this week rather than carried", src="https://api-docs.deepseek.com/quick_start/pricing"),
 R(model="gpt-oss-120b on Nebius", id="gpt-oss-120b", licence="open, Apache 2.0", price={"in": 0.15, "out": 0.60, "cached": None}, aa=12, med=None, verified=True,
   note="read from Nebius's own Token Factory catalogue (model-catalog.md); currency not stated on the page, USD assumed; no cached rate listed",
   src="https://tokenfactory.nebius.com/model-catalog.md"),
 R(model="Claude Haiku 5.5", id="claude-haiku-5-5", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=43, med=None, verified=True,
   note="unchanged; prompts over 100,000 tokens pay 0.50/2.50/0.05", src=ANTH),
 R(model="GPT-6 Luna", id="gpt-6-luna", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=38, med=None, verified=True,
   note="unchanged; long-context tier 0.20/0.75/0.02; named 14 Oct as the replacement for the GPT-4 family ids removed 14 Jan 2027", src=OPENAI),
]

if __name__ == "__main__":
    out = []
    for r in ROWS:
        c1, c2 = cost(r["price"])
        out.append({**r, "cost_10k_docs_no_cache": c1, "cost_10k_docs_80pct_cached": c2})
    out.sort(key=lambda r: r["cost_10k_docs_no_cache"])
    doc = {"issue": 7, "week_ending": "2026-10-16", "prices_read": "2026-10-16",
           "workload": "10,000 docs x (4,000 in + 500 out) tokens",
           "aa_index": "v4.3.2 (changelog 19 Sept 2026), read 16 Oct 2026; healthcare index read 16 Oct for three rows only",
           "models": out}
    json.dump(doc, open("models.json", "w"), indent=1)
    print(f"{'model':28} {'in/out/cached':>20} {'AA':>4} {'med':>4} {'no cache':>10} {'80% cached':>11}  verified")
    for r in out:
        p = r["price"]
        cached = "n/a" if p["cached"] is None else f"{p['cached']:g}"
        c2 = "n/a" if r["cost_10k_docs_80pct_cached"] is None else f"${r['cost_10k_docs_80pct_cached']:.2f}"
        med = "-" if r["med"] is None else str(r["med"])
        print(f"{r['model']:28} {p['in']:g}/{p['out']:g}/{cached:>6} {r['aa']:>4} {med:>4} "
              f"${r['cost_10k_docs_no_cache']:>9.2f} {c2:>11}  {r['verified']}")
