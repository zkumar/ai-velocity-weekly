"""Builds models.json for AI Velocity Weekly 10 and prints the section 2 table.

Workload: 10,000 clinical documents at 4,000 input and 500 output tokens.
  cost_no_cache = 40 * in + 5 * out                 (USD; prices are $ per million tokens)
  cost_cached   = 8 * in + 32 * cached + 5 * out    (80% of input served from cache)
Cache-write fees excluded. Prices are vendor list prices read on 6 November 2026 from the pages
in "src". AA is the Artificial Analysis Intelligence Index, now v5.0.1 (changelog entry dated
3 November: "Incorporated grading robustness improvements from the CritPt authors and regraded
all models on CritPt v2."; same nine evaluations and weights as v5.0), best listed variant, read
from artificialanalysis.ai/leaderboards/models on 6 November. v5.0.x scores are not comparable
with the v4.3.2 scores in Issues 01 to 08. "med" is the Artificial Analysis Healthcare & Medical
score read from the homepage capability-index comparison on 6 November; the page that states its
composition was readable this week (five evaluations, weights in models.json), but it prints no
version for the index, so the scores remain unversioned. "verified" is False where the price
could not be read on the vendor's own current price page on 6 November.
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
   note="unchanged; Fast 20/100/2.00 and Ultrafast 60/300/6.00 still printed; HealthBench Professional 66.0%, unchanged", src=OPENAI),
 R(model="Claude Fable 5.1", id="claude-fable-5-1", licence="closed", price={"in": 10, "out": 50, "cached": 0.25}, aa=50, med=51, verified=True,
   note="unchanged; AA best variant is xhigh at 50, max scores 49; 1-hour cache write 20.00; Claude Mythos 5.1 row at the same price still on the page", src=ANTH),
 R(model="Claude Opus 5.5", id="claude-opus-5-5", licence="closed", price={"in": 4, "out": 20, "cached": 0.20}, aa=59, med=58, verified=True,
   note="price unchanged; AA 59 on v5.0.1 against 58 recorded on v5.0, second behind Gemini 4 Carbon; still first on Healthcare & Medical; fast mode 8/40", src=ANTH),
 R(model="Gemini 4 Carbon", id="gemini-4-carbon", licence="closed, restricted rollout", price={"in": 4, "out": 20, "cached": None}, aa=60, med=None, verified=False,
   note="still not on the Gemini API pricing page or changelog on 6 Nov; 4/20 is Artificial Analysis's figure and could not be read on a Google page; AA 60 on v5.0.1 against 59 recorded last week, first; medium 58 and low 54 added 1 and 2 Nov; not in the healthcare comparison", src=GOOG),
 R(model="Kimi K3", id="kimi-k3", licence="open weights (moonshotai/Kimi-K3, 2.8T), licence text not read", price={"in": 3, "out": 15, "cached": 0.30}, aa=None, med=None, verified=False,
   note="price tables came back empty on the vendor page on 6 Nov, so 3/15/0.30 is carried from 30 Oct; Nebius Token Factory lists Kimi-K3 at the same 3/15/0.30; not on the AA leaderboard; last week's 'API only' licence was wrong, the weights repo dates from 2 Sep", src=KIMI),
 R(model="Kimi K3.1 Pro", id="kimi-k3.1-pro", licence="open weights, Kimi K3.1-Pro License", price={"in": 2, "out": 10, "cached": 0.20}, aa=46, med=52, verified=False,
   note="weights are public as moonshotai/Kimi-K3.1-Pro (2.8T total, 104B active; repository created 2 Nov, last modified 5 Nov, against a 4 Nov promise); licence needs a separate agreement for model-as-a-service businesses above $20M revenue in 12 months; price tables came back empty on the vendor page on 6 Nov, so 2/10/0.20 is carried from 30 Oct", src=KIMI),
 R(model="Claude Sonnet 5.5", id="claude-sonnet-5-5", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=55, med=54, verified=True,
   note="price unchanged; AA 55 on v5.0.1 against 54 on v5.0; second on Healthcare & Medical; HealthBench Professional 63.0%, unchanged", src=ANTH),
 R(model="GPT-6.1 Sol", id="gpt-6.1-sol", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=55, med=52, verified=True,
   note="unchanged; HealthBench Professional 65.1%, unchanged", src=OPENAI),
 R(model="Gemini 4 Argon", id="gemini-4-argon", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=50, med=None, verified=True,
   note="unchanged; 4/20/0.20 from 1 Dec 2026 ($260.00, $138.40); implicit caching only; not in the healthcare comparison", src=GOOG),
 R(model="Grok 4.7", id="grok-4.7", licence="closed", price={"in": 2, "out": 6, "cached": 0.50}, aa=35, med=47, verified=True,
   note="unchanged; the cached price is on the pricing page (last updated 10 Oct), not the models page; requests of 200k tokens or more pay 4/12/1.00; grok-4.3 is on the same table at 1.25/2.50/0.20 but still has no release date, release note or AA score, so it is not a row", src=XAI),
 R(model="GPT-6.1 Terra", id="gpt-6.1-terra", licence="closed", price={"in": 1, "out": 5, "cached": 0.05}, aa=51, med=45, verified=True,
   note="unchanged; Fast 2/10/0.10", src=OPENAI),
 R(model="Mistral Large 4", id="mistral-large-4", licence="open weights 29 Oct, Mistral Ecosystem Open Weight License", price={"in": 0.70, "out": 2.10, "cached": 0.07}, aa=26, med=None, verified=True,
   note="price unchanged; AA 26 (high) against 25 recorded last week; still labelled Public Preview; no Mistral changelog entry since 22 Oct", src="https://docs.mistral.ai/models/mistral-large-4-0"),
 R(model="Gemini 3.8 Flash", id="gemini-3.8-flash", licence="closed", price={"in": 0.75, "out": 3.75, "cached": 0.075}, aa=31, med=38, verified=True,
   note="unchanged; 0.75/3.75/0.075 through 31 Dec; 1.50/7.50/0.15 from 1 Jan 2027; cache storage 0.50 per million tokens per hour, 1.00 from 1 Jan", src=GOOG),
 R(model="DeepSeek V4.1 Flash", id="deepseek-flash", licence="open, MIT", price={"in": 0.30, "out": 1.20, "cached": 0.006}, aa=33, med=41, verified=True,
   note="price unchanged, peak rate; off-peak 0.15/0.60/0.003 ($9.00); AA 33 (max) on v5.0.1 against 32 on v5.0; Search and Fetch listed at $0.75 per 1,000 requests", src="https://api-docs.deepseek.com/quick_start/pricing/"),
 R(model="gpt-oss-120b on Nebius", id="gpt-oss-120b", licence="open, Apache 2.0", price={"in": 0.15, "out": 0.60, "cached": 0.10}, aa=None, med=None, verified=True,
   note="Token Factory catalog readable this week: 0.15/0.60 unchanged, with a cached-input price of 0.10 that this row did not carry before (currency not printed on the catalog); the AI Studio price page still shows 0.15/0.60; AA prints no score", src="https://tokenfactory.nebius.com/model-catalog.md"),
 R(model="Claude Haiku 5.5", id="claude-haiku-5-5", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=36, med=37, verified=True,
   note="unchanged; prompts over 100,000 tokens pay 0.50/2.50/0.05", src=ANTH),
 R(model="GPT-6 Luna", id="gpt-6-luna", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=28, med=None, verified=True,
   note="unchanged", src=OPENAI),
]

if __name__ == "__main__":
    out = []
    for r in ROWS:
        c1, c2 = cost(r["price"])
        out.append({**r, "cost_10k_docs_no_cache": c1, "cost_10k_docs_80pct_cached": c2})
    out.sort(key=lambda r: r["cost_10k_docs_no_cache"])
    doc = {"issue": 10, "week_ending": "2026-11-06", "prices_read": "2026-11-06",
           "workload": "10,000 docs x (4,000 in + 500 out) tokens",
           "aa_index": "v5.0.1 (changelog 3 Nov 2026: 'Incorporated grading robustness improvements from the CritPt authors and regraded all models on CritPt v2.'; nine evaluations unchanged from v5.0: AA-Briefcase v1.1 15%, AutomationBench-AA 5%, GDP.pdf 5%, FrontierCode 2.0 15%, Terminal-Bench 4.0 10%, Terminal-Bench-Science 0.1 15%, CritPt v2 Hard 10%, AA-Omniscience v1.1 15%, HLE-Diamond 10%), read 6 Nov 2026; not comparable with v4.3.2",
           "med_index": "Healthcare & Medical score from the homepage comparison, read 6 Nov 2026; composition page readable this week (AA-Omniscience v1.1 Health Accuracy 25%, AA-Briefcase v1.1 25%, MLCR-AA 15%, AutomationBench-AA Support and Operations 15%, AA-Omniscience v1.1 Health Non-Hallucination 10%, HLE-Diamond 10%); no index version printed, scores unversioned",
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
