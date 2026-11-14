"""Builds models.json for AI Velocity Weekly 11 and prints the section 2 table.

Workload: 10,000 clinical documents at 4,000 input and 500 output tokens.
  cost_no_cache = 40 * in + 5 * out                 (USD; prices are $ per million tokens)
  cost_cached   = 8 * in + 32 * cached + 5 * out    (80% of input served from cache)
Cache-write fees excluded. Prices are vendor list prices read on 13 November 2026 from the pages
in "src". AA is the Artificial Analysis Intelligence Index, still v5.0.1 (no methodology entry in
the changelog between 6 and 13 November), best listed variant, read from
artificialanalysis.ai/leaderboards/models and the model pages on 13 November. v5.0.x scores are
not comparable with the v4.3.2 scores in Issues 01 to 08. "med" is the Artificial Analysis
Healthcare & Medical Index read from artificialanalysis.ai/indexes/healthcare-and-medical (the
old capabilities URL now redirects there) on 13 November; it prints no version. "verified" is
False where the price could not be read on the vendor's own current price page on 13 November.
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
XAI = "https://docs.x.ai/developers/pricing"
ROWS = [
 R(model="GPT-6 Astra", id="gpt-6-astra", licence="closed", price={"in": 10, "out": 50, "cached": 1.00}, aa=57, med=54, verified=True,
   note="unchanged; Fast 20/100/2.00 and Ultrafast 60/300/6.00 still printed; HealthBench Professional 66.0%, now second to Fable 5.2", src=OPENAI),
 R(model="Claude Fable 5.1", id="claude-fable-5-1", licence="closed", price={"in": 10, "out": 50, "cached": 0.25}, aa=49, med=51, verified=True,
   note="price unchanged but the page moves it under Additional models; AA model page marks it deprecated and prints 49 (raw 49.16) against 50 last week, a rounding move; superseded by Fable 5.2 at a lower price", src=ANTH),
 R(model="Claude Fable 5.2", id="claude-fable-5-2", licence="closed", price={"in": 8, "out": 40, "cached": 0.20}, aa=65, med=65, verified=True,
   note="new row, launched 9 Nov; 5-minute cache write 10, 1-hour 16; fast mode 16/80; AA 65 at max (xhigh 62), first on the Intelligence Index, first on Healthcare & Medical at 65 and on HealthBench Professional at 67.7% (max; 68.1% xhigh); requires 30-day retention, not available under zero data retention unless Anthropic authorises it; Mythos 5.2 at the same price for verified organisations", src=ANTH),
 R(model="Claude Opus 5.5", id="claude-opus-5-5", licence="closed", price={"in": 4, "out": 20, "cached": 0.20}, aa=59, med=58, verified=True,
   note="unchanged; now third on the index behind Fable 5.2 and Carbon, second on Healthcare & Medical; fast mode 8/40", src=ANTH),
 R(model="Gemini 4 Carbon", id="gemini-4-carbon", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=60, med=57, verified=True,
   note="now on Google's price page: 2/10/0.10 through 30 Nov 2026, 4/20/0.20 from 1 Dec ($260.00, $138.40); last week's 4/20 was Artificial Analysis's figure, so the row halves on paper for seventeen days; GA on 10 Nov per the Gemini Enterprise Agent Platform notes, still absent from the Gemini API changelog; implicit caching only; Healthcare & Medical 57, listed for the first time", src=GOOG),
 R(model="Kimi K3", id="kimi-k3", licence="open weights (moonshotai/Kimi-K3, 2.8T), licence text not read", price={"in": 3, "out": 15, "cached": 0.30}, aa=None, med=None, verified=True,
   note="verified this week from the price page's embedded script data (the visible table is still empty to a text reader); 5-minute cache write 3, 1-hour 6; batch at 60% of list; not on the AA leaderboard", src=KIMI),
 R(model="Kimi K3.1 Pro", id="kimi-k3.1-pro", licence="open weights, Kimi K3.1-Pro License", price={"in": 2, "out": 10, "cached": 0.20}, aa=46, med=52, verified=True,
   note="verified this week from the price page's embedded script data; a highspeed variant at 4/20/0.20; Hugging Face repository unchanged since 5 Nov; AA added Bedrock, Databricks and DigitalOcean endpoints 9 to 11 Nov", src=KIMI),
 R(model="Claude Sonnet 5.5", id="claude-sonnet-5-5", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=55, med=54, verified=True,
   note="unchanged; HealthBench Professional 63.0%, now fourth", src=ANTH),
 R(model="GPT-6.1 Sol", id="gpt-6.1-sol", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=55, med=52, verified=True,
   note="unchanged, but the price page says promotional pricing for Sol (under its old GPT-5.6 name) 'is available until November 30, 2026', where the 21 Aug changelog said 21 Nov; what follows is not printed; HealthBench Professional 65.1%, third", src=OPENAI),
 R(model="Gemini 4 Argon", id="gemini-4-argon", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=50, med=51, verified=True,
   note="unchanged; 4/20/0.20 from 1 Dec 2026 ($260.00, $138.40); implicit caching only; Healthcare & Medical 51 read from the model page, not the index page", src=GOOG),
 R(model="Gemini 4 Hydrogen", id="gemini-4-hydrogen", licence="closed", price={"in": 1.50, "out": 7.50, "cached": 0.075}, aa=54, med=None, verified=True,
   note="new row; on the price page with no scheduled change; AA evaluated 12 Nov (xhigh 54, high 51, medium 41, low 27); GA per the Gemini Enterprise Agent Platform notes on 12 Nov, not in the Gemini API changelog; no Healthcare & Medical score yet", src=GOOG),
 R(model="Grok 4.7", id="grok-4.7", licence="closed", price={"in": 2, "out": 6, "cached": 0.50}, aa=35, med=47, verified=True,
   note="unchanged; requests of 200k tokens or more pay 4/12/1.00; grok-4.3 at 1.25/2.50/0.20 still has no release note or AA score, so it is not a row", src=XAI),
 R(model="GPT-6.1 Terra", id="gpt-6.1-terra", licence="closed", price={"in": 1, "out": 5, "cached": 0.05}, aa=51, med=45, verified=True,
   note="unchanged; Fast 2/10/0.10", src=OPENAI),
 R(model="Mistral Large 4", id="mistral-large-4", licence="open weights, Mistral Open Weight License v26.10", price={"in": 0.70, "out": 2.10, "cached": 0.07}, aa=26, med=37, verified=True,
   note="unchanged; the docs page now dates general availability 5 Nov; Healthcare & Medical 37 read for the first time; mistral.ai/pricing has no per-model table", src="https://docs.mistral.ai/models/mistral-large-4-0"),
 R(model="Gemini 3.8 Flash", id="gemini-3.8-flash", licence="closed", price={"in": 0.75, "out": 3.75, "cached": 0.075}, aa=31, med=38, verified=True,
   note="unchanged; 0.75/3.75/0.075 through 31 Dec; 1.50/7.50/0.15 from 1 Jan 2027; from 1 Jan it costs the same as Hydrogen does today", src=GOOG),
 R(model="DeepSeek V4.1 Flash", id="deepseek-flash", licence="open, MIT", price={"in": 0.30, "out": 1.20, "cached": 0.006}, aa=33, med=41, verified=True,
   note="unchanged, peak rate; off-peak 0.15/0.60/0.003 ($9.00); deepseek-flash now resolves to V4.1-Flash-1017 and the older V4 Flash names are retired to it", src="https://api-docs.deepseek.com/quick_start/pricing/"),
 R(model="gpt-oss-120b on Nebius", id="gpt-oss-120b", licence="open, Apache 2.0", price={"in": 0.15, "out": 0.60, "cached": 0.10}, aa=4, med=None, verified=False,
   note="the Token Factory catalogue returned 403 on 13 Nov; 0.15/0.60 was read on nebius.com/prices-ai-studio, which prints no cached price, so 0.10 is carried from 6 Nov and the row is unverified; AA 4 (high); the 9 Nov deprecation notice is still in the future tense", src="https://tokenfactory.nebius.com/model-catalog.md"),
 R(model="Claude Haiku 5.5", id="claude-haiku-5-5", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=36, med=37, verified=True,
   note="unchanged; prompts over 100,000 tokens pay 0.50/2.50/0.05; Healthcare & Medical prints 37.5 on the chart", src=ANTH),
 R(model="GPT-6 Luna", id="gpt-6-luna", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=28, med=35, verified=True,
   note="unchanged; Healthcare & Medical 35 read for the first time", src=OPENAI),
]

if __name__ == "__main__":
    out = []
    for r in ROWS:
        c1, c2 = cost(r["price"])
        out.append({**r, "cost_10k_docs_no_cache": c1, "cost_10k_docs_80pct_cached": c2})
    out.sort(key=lambda r: r["cost_10k_docs_no_cache"])
    doc = {"issue": 11, "week_ending": "2026-11-13", "prices_read": "2026-11-13",
           "workload": "10,000 docs x (4,000 in + 500 out) tokens",
           "aa_index": "v5.0.1 (since 3 Nov 2026; no methodology entry 6 to 13 Nov; nine evaluations: AA-Briefcase v1.1 15%, AutomationBench-AA 5%, GDP.pdf 5%, FrontierCode 2.0 15%, Terminal-Bench 4.0 10%, Terminal-Bench-Science 0.1 15%, CritPt v2 Hard 10%, AA-Omniscience v1.1 15%, HLE-Diamond 10%), read 13 Nov 2026; not comparable with v4.3.2",
           "med_index": "Healthcare & Medical Index read 13 Nov 2026 from artificialanalysis.ai/indexes/healthcare-and-medical (AA-Omniscience v1.1 Health Accuracy 25%, AA-Briefcase v1.1 25%, MLCR-AA 15%, AutomationBench-AA 15%, AA-Omniscience v1.1 Health Non-Hallucination 10%, HLE-Diamond 10%); no index version printed; HealthBench Professional is not a component",
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
