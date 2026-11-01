"""Builds models.json for AI Velocity Weekly 09 and prints the section 2 table.

Workload: 10,000 clinical documents at 4,000 input and 500 output tokens.
  cost_no_cache = 40 * in + 5 * out                 (USD; prices are $ per million tokens)
  cost_cached   = 8 * in + 32 * cached + 5 * out    (80% of input served from cache)
Cache-write fees excluded. Prices are vendor list prices read on 30 October 2026 from the pages
in "src". AA is the Artificial Analysis Intelligence Index, now v5.0 (announced 27 October, nine
evaluations, "majority of the Index is now built on private datasets"), best listed variant, read
from artificialanalysis.ai/leaderboards/models on 30 October. v5.0 scores are not comparable with
the v4.3.2 scores in Issues 01 to 08. "med" is the Artificial Analysis Healthcare & Medical score
read from the homepage capability-index comparison on 30 October; the page that states its
composition returned an error on every read, so the composition is recorded as unreadable and
the scores are carried as unversioned. "verified" is False where the price could not be read on
the vendor's own current price page.
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
XAI = "https://docs.x.ai/docs/models"
ROWS = [
 R(model="GPT-6 Astra", id="gpt-6-astra", licence="closed", price={"in": 10, "out": 50, "cached": 1.00}, aa=57, med=54, verified=True,
   note="unchanged; Fast 20/100/2.00 and Ultrafast 60/300/6.00 still printed; HealthBench Professional 66.0% on AA's separate leaderboard", src=OPENAI),
 R(model="Claude Fable 5.1", id="claude-fable-5-1", licence="closed", price={"in": 10, "out": 50, "cached": 0.25}, aa=50, med=51, verified=True,
   note="unchanged; 1-hour cache write 20.00; the Claude Mythos 5.1 row at the same price is on the docs page but not on claude.com/pricing", src=ANTH),
 R(model="Claude Opus 5.5", id="claude-opus-5-5", licence="closed", price={"in": 4, "out": 20, "cached": 0.20}, aa=58, med=58, verified=True,
   note="unchanged; first on both AA indexes this week; fast mode 8/40", src=ANTH),
 R(model="Gemini 4 Carbon", id="gemini-4-carbon", licence="closed, restricted rollout", price={"in": 4, "out": 20, "cached": None}, aa=59, med=None, verified=False,
   note="announced 28 Oct and new first on AA v5.0 at 59; not on the Gemini API pricing page on 30 Oct; 4/20 is Artificial Analysis's figure, Reuters reported 2/10; access phased through Google's Fairwind programme", src=GOOG),
 R(model="Kimi K3", id="kimi-k3", licence="API only", price={"in": 3, "out": 15, "cached": 0.30}, aa=None, med=None, verified=True,
   note="now read from the vendor's page (tables recovered from its script); previous-generation flagship, not on the AA leaderboard; 5-minute cache write 3.00, 1-hour 6.00", src=KIMI),
 R(model="Kimi K3.1 Pro", id="kimi-k3.1-pro", licence="API only, weights promised by 4 Nov", price={"in": 2, "out": 10, "cached": 0.20}, aa=46, med=52, verified=True,
   note="now read from the vendor's page; AA v5.0 46 against 55 on v4.3.2; a highspeed variant is 4/20/0.20; K2 models closed to new users from 31 Oct", src=KIMI),
 R(model="Claude Sonnet 5.5", id="claude-sonnet-5-5", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=54, med=54, verified=True,
   note="unchanged; second on both AA indexes; HealthBench Professional 63.0%", src=ANTH),
 R(model="GPT-6.1 Sol", id="gpt-6.1-sol", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=55, med=52, verified=True,
   note="unchanged; HealthBench Professional 65.1%", src=OPENAI),
 R(model="Gemini 4 Argon", id="gemini-4-argon", licence="closed", price={"in": 2, "out": 10, "cached": 0.10}, aa=50, med=None, verified=True,
   note="unchanged; 4/20/0.20 from 1 Dec 2026 ($260.00, $138.40); implicit caching only; not in the healthcare comparison", src=GOOG),
 R(model="Grok 4.7", id="grok-4.7", licence="closed", price={"in": 2, "out": 6, "cached": 0.50}, aa=35, med=47, verified=True,
   note="unchanged on docs.x.ai; x.ai/api now lists a grok-4.3 at 1.25/2.50/0.20 as the newest flagship with no release date and no AA score, so it is not a row yet", src=XAI),
 R(model="GPT-6.1 Terra", id="gpt-6.1-terra", licence="closed", price={"in": 1, "out": 5, "cached": 0.05}, aa=51, med=45, verified=True,
   note="new 26 Oct; Fast 2/10/0.10; AA's 26 Oct article calls it the new cost-efficiency frontier", src=OPENAI),
 R(model="Mistral Large 4", id="mistral-large-4", licence="open weights 29 Oct, Mistral Ecosystem Open-Weight licence", price={"in": 0.70, "out": 2.10, "cached": 0.07}, aa=25, med=None, verified=True,
   note="list price down from 1.36/4.18/0.14 last week; weights released 29 Oct as mistralai/Mistral-Large-4-1T-A52B; AA v5.0 25 (preview build)", src="https://docs.mistral.ai/models/mistral-large-4-0"),
 R(model="Gemini 3.8 Flash", id="gemini-3.8-flash", licence="closed", price={"in": 0.75, "out": 3.75, "cached": 0.075}, aa=31, med=38, verified=True,
   note="0.75/3.75/0.075 through 31 Dec; 1.50/7.50/0.15 from 1 Jan 2027; cache storage 0.50 per million tokens per hour, 1.00 from 1 Jan", src=GOOG),
 R(model="DeepSeek V4.1 Flash", id="deepseek-flash", licence="open, MIT", price={"in": 0.30, "out": 1.20, "cached": 0.006}, aa=32, med=41, verified=True,
   note="peak rate; off-peak 0.15/0.60/0.003 ($9.00); Search and Fetch tool calls start billing at $0.75 per 1,000 on 1 Nov", src="https://api-docs.deepseek.com/quick_start/pricing/"),
 R(model="gpt-oss-120b on Nebius", id="gpt-oss-120b", licence="open, Apache 2.0", price={"in": 0.15, "out": 0.60, "cached": None}, aa=None, med=None, verified=True,
   note="unchanged on the AI Studio price page, which lists no 2026 models and may be stale; the Token Factory price page refuses automated reads; AA v5.0 prints no score", src="https://nebius.com/prices-ai-studio"),
 R(model="Claude Haiku 5.5", id="claude-haiku-5-5", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=36, med=37, verified=True,
   note="unchanged; prompts over 100,000 tokens pay 0.50/2.50/0.05", src=ANTH),
 R(model="GPT-6 Luna", id="gpt-6-luna", licence="closed", price={"in": 0.10, "out": 0.50, "cached": 0.01}, aa=28, med=None, verified=True,
   note="unchanged; AA v5.0 28 against 38 on v4.3.2, the largest fall in the table", src=OPENAI),
]

if __name__ == "__main__":
    out = []
    for r in ROWS:
        c1, c2 = cost(r["price"])
        out.append({**r, "cost_10k_docs_no_cache": c1, "cost_10k_docs_80pct_cached": c2})
    out.sort(key=lambda r: r["cost_10k_docs_no_cache"])
    doc = {"issue": 9, "week_ending": "2026-10-30", "prices_read": "2026-10-30",
           "workload": "10,000 docs x (4,000 in + 500 out) tokens",
           "aa_index": "v5.0 (announced 27 Oct 2026, nine evaluations: AA-Briefcase 15%, AutomationBench-AA 5%, GDP.pdf 5%, FrontierCode 2.0 15%, Terminal-Bench 4.0 10%, Terminal-Bench-Science 15%, CritPt v2 Hard 10%, AA-Omniscience 15%, HLE-Diamond 10%), read 30 Oct 2026; not comparable with v4.3.2",
           "med_index": "Healthcare & Medical score from the homepage comparison, read 30 Oct 2026; composition page unreadable, scores unversioned",
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
