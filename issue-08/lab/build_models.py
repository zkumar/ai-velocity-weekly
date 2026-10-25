"""Builds models.json for AI Velocity Weekly 08 and prints the section 2 table.

Workload: 10,000 clinical documents at 4,000 input and 500 output tokens.
  cost_no_cache = 40 * in + 5 * out                 (USD; prices are $ per million tokens)
  cost_cached   = 8 * in + 32 * cached + 5 * out    (80% of input served from cache)
Cache-write fees excluded. Prices are vendor list prices read on 25 October 2026 from the pages
in "src". AA is the Artificial Analysis Intelligence Index, still v4.3.2 (the changelog names no
newer version after its 19 September entry), best listed variant, read from
artificialanalysis.ai/leaderboards/models on 25 October. "med" is the Artificial Analysis
Healthcare & Medical Index read the same day from
artificialanalysis.ai/models/capabilities/healthcare-and-medical. That page now describes a
six-evaluation composition and its readable scores moved against last week's, so no medical
score is carried from Issue 07: rows whose score could not be read today are None.
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
KIMI = "https://platform.kimi.ai/docs/pricing/chat"
ROWS = [
 R(model="GPT-6 Astra", id="gpt-6-astra", licence="closed", price={"in": 10, "out": 50, "cached": 1.00}, aa=53, med=None, verified=True,
   note="unchanged; the long-context tier 20/75/2.00 carried last week is no longer on the page, which now prints Fast 20/100/2.00 and Ultrafast 60/300/6.00", src=OPENAI),
 R(model="Claude Fable 5.1", id="claude-fable-5-1", licence="closed", price={"in": 10, "out": 50, "cached": 0.25}, aa=53, med=None, verified=True,
   note="unchanged; its medical score (58 last week) could not be read from the recomposed index page; a Claude Mythos 5.1 row at the same price now appears on the page, launch date unverified, not on the AA leaderboard", src=ANTH),
 R(model="Claude Opus 5.5", id="claude-opus-5-5", licence="closed", price={"in": 4, "out": 20, "cached": 0.20}, aa=58, med=55, verified=True,
   note="unchanged; medical index reads 55 today against 61 on 16 Oct after the index was recomposed; fast mode 8/40", src=ANTH),
 R(model="Kimi K3", id="kimi-k3", licence="API only", price={"in": 3, "out": 15, "cached": 0.30}, aa=None, med=None, verified=False,
   note="price carried from 16 Oct: the vendor's pricing tables did not render on 25 Oct; demoted to previous-generation flagship; no longer listed on the AA leaderboard", src=KIMI),
 R(model="Kimi K3.1 Pro", id="kimi-k3.1-pro", licence="API only, weights promised by 4 Nov", price={"in": 2, "out": 10, "cached": 0.20}, aa=55, med=None, verified=False,
   note="new flagship about 23 Oct; AA 55, fourth on the index; price is a third-party figure (benchlm.ai, synced 23 Oct) because the vendor's tables did not render", src=KIMI),
 R(model="Claude Sonnet 5.5", id="claude-sonnet-5-5", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=56, med=53, verified=True,
   note="unchanged; medical index reads 53 today against 58 on 16 Oct after the index was recomposed", src=ANTH),
 R(model="GPT-6.1 Sol", id="gpt-6.1-sol", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=52, med=None, verified=True,
   note="unchanged; the 12/60/0.60 row sits in the Ultrafast position, label still inferred; last week's long-context tier 4/15/0.20 is no longer on the page",
   src=OPENAI),
 R(model="Gemini 4 Argon", id="gemini-4-argon", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=53, med=None, verified=True,
   note="unchanged; 2/10/0.10 through 30 Nov 2026, then 4/20/0.20 from 1 Dec; implicit caching only",
   src=GOOG),
 R(model="Grok 4.7", id="grok-4.7", licence="closed", price={"in": 2, "out": 6, "cached": 0.50}, aa=46, med=None, verified=True,
   note="unchanged; page dated 10 Oct; at or above 200k prompt tokens 4/12/1.00 on every token of the request",
   src="https://docs.x.ai/developers/pricing"),
 R(model="Mistral Large 4", id="mistral-large-4", licence="open weights announced, licence not named", price={"in": 1.36, "out": 4.18, "cached": 0.14}, aa=38, med=None, verified=True,
   note="list price; the launch sale shown last week is gone from the page, so it ended as inferred; the 'preview' label is gone from the price page while AA keeps it",
   src="https://docs.mistral.ai/inference/pricing"),
 R(model="Gemini 3.8 Flash", id="gemini-3.8-flash", licence="closed", price={"in": 0.75, "out": 3.75, "cached": 0.075}, aa=41, med=None, verified=True,
   note="0.75/3.75/0.075 through 31 Dec; 1.50/7.50/0.15 from 1 Jan 2027; cache storage 0.50 per million tokens per hour, 1.00 from 1 Jan",
   src=GOOG),
 R(model="DeepSeek V4.1 Flash", id="deepseek-flash", licence="open, MIT", price={"in": 0.30, "out": 1.20, "cached": 0.006}, aa=45, med=None, verified=True,
   note="peak rate; off-peak 0.15/0.60/0.003 ($9.00); AA 45 for the 1017 build (18 Oct entry) against 39 last week; the model id is now plain deepseek-flash and the v4 names are retired", src="https://api-docs.deepseek.com/quick_start/pricing"),
 R(model="gpt-oss-120b on Nebius", id="gpt-oss-120b", licence="open, Apache 2.0", price={"in": 0.15, "out": 0.60, "cached": None}, aa=12, med=None, verified=True,
   note="unchanged; read from Nebius's Token Factory catalogue; currency not stated, USD assumed; no cached rate listed",
   src="https://tokenfactory.nebius.com/model-catalog.md"),
 R(model="Claude Haiku 5.5", id="claude-haiku-5-5", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=43, med=None, verified=True,
   note="unchanged; prompts over 100,000 tokens pay 0.50/2.50/0.05", src=ANTH),
 R(model="GPT-6 Luna", id="gpt-6-luna", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=38, med=None, verified=True,
   note="unchanged; the 12-hour cache write (20 Oct) costs 2.5x the input price; the Decisions API went GA on this model on 22 Oct", src=OPENAI),
]

if __name__ == "__main__":
    out = []
    for r in ROWS:
        c1, c2 = cost(r["price"])
        out.append({**r, "cost_10k_docs_no_cache": c1, "cost_10k_docs_80pct_cached": c2})
    out.sort(key=lambda r: r["cost_10k_docs_no_cache"])
    doc = {"issue": 8, "week_ending": "2026-10-25", "prices_read": "2026-10-25",
           "workload": "10,000 docs x (4,000 in + 500 out) tokens",
           "aa_index": "v4.3.2 (no newer version in the changelog), read 25 Oct 2026; healthcare index read 25 Oct, two rows readable, composition changed since 16 Oct",
           "models": out}
    json.dump(doc, open("models.json", "w"), indent=1)
    print(f"{'model':28} {'in/out/cached':>20} {'AA':>4} {'med':>4} {'no cache':>10} {'80% cached':>11}  verified")
    for r in out:
        p = r["price"]
        cached = "n/a" if p["cached"] is None else f"{p['cached']:g}"
        c2 = "n/a" if r["cost_10k_docs_80pct_cached"] is None else f"${r['cost_10k_docs_80pct_cached']:.2f}"
        med = "-" if r["med"] is None else str(r["med"])
        aa = "-" if r["aa"] is None else str(r["aa"])
        print(f"{r['model']:28} {p['in']:g}/{p['out']:g}/{cached:>6} {aa:>4} {med:>4} "
              f"${r['cost_10k_docs_no_cache']:>9.2f} {c2:>11}  {r['verified']}")
