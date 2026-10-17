"""Builds models.json for AI Velocity Weekly 02 and prints the section 2 table.

Workload: 10,000 clinical documents at 4,000 input and 500 output tokens.
  cost_no_cache = 40 * in + 5 * out            (USD, prices are $/M tokens)
  cost_cached   = 8 * in + 32 * cached + 5 * out   (80% of input from cache)
Cache-write fees are excluded. "*" marks vendor-reported numbers.
Rows marked changed_this_week were added or repriced in the window
5 to 11 September 2026; the rest are carried forward from issue 01.
"""

import json

W = "2026-09-11"

def cost(p):
    if p["in"] is None or p["out"] is None:
        return None, None
    c1 = round(40 * p["in"] + 5 * p["out"], 2)
    c2 = round(8 * p["in"] + 32 * p["cached"] + 5 * p["out"], 2) if p["cached"] is not None else None
    return c1, c2

ROWS = [
 dict(model="GPT-6 Astra", vendor="OpenAI", date="2026-09-03", open_weights=False, licence="proprietary",
      context="1.05M (922K in)", max_output="128K", price=dict(**{"in":10.0,"out":50.0,"cached":1.0}),
      aa_index="53 (v4.3, max)", coding="Terminal-Bench 4.0: 59.1 (AA, independent)",
      health="HealthBench Pro 63.4*, HealthBench 58.1*, Hard 36.3* (system card); not on llm-stats",
      throughput="54.4 tok/s, TTFT 323 s at max (AA)", changed_this_week="AA index rebased to v4.3 (was 61 on v4.2)",
      src="https://artificialanalysis.ai/models/gpt-6-astra"),
 dict(model="Claude Fable 5.1", vendor="Anthropic", date="2026-09-01", open_weights=False, licence="proprietary",
      context="1M", max_output="128K", price={"in":10.0,"out":50.0,"cached":0.25},
      aa_index="53 (v4.3, max with fallback)", coding="Terminal-Bench 4.0: 52.0 (AA, independent)",
      health="none published", throughput="5.4 tok/s, TTFT 295 s at max effort (AA)",
      changed_this_week="AA index rebased to v4.3 (was 66 on v4.2)", src="https://artificialanalysis.ai/models/claude-fable-5-1"),
 dict(model="Claude Opus 5", vendor="Anthropic", date="2026-07-24", open_weights=False, licence="proprietary",
      context="1M", max_output="128K", price={"in":5.0,"out":25.0,"cached":0.5},
      aa_index="51 (v4.3, max)", coding="Terminal-Bench 4.0: 49.0 (AA, independent)", health="none published",
      throughput="52.0 tok/s, TTFT 86 s (AA)", changed_this_week="AA v4.3 (was 54)", src="https://artificialanalysis.ai/models/claude-opus-5"),
 dict(model="Gemini 3.8 Flash", vendor="Google", date="2026-09-02", open_weights=False, licence="proprietary",
      context="1M", max_output="64K", price={"in":0.75,"out":3.75,"cached":0.075},
      aa_index="41 (v4.3, high)", coding="unverified on Terminal-Bench 4.0", health="none published",
      throughput="261 tok/s, TTFT 12 s (AA)", changed_this_week="AA v4.3 (was 59); promo price to 31 Dec 2026 unchanged",
      src="https://artificialanalysis.ai/models/gemini-3-8-flash"),
 dict(model="GPT-5.6 Sol", vendor="OpenAI", date="2026-07-09", open_weights=False, licence="proprietary",
      context="1.05M", max_output="128K", price={"in":5.0,"out":30.0,"cached":0.5},
      aa_index="47 (v4.3, max)", coding="Terminal-Bench 4.0: 39.9 (AA, independent)",
      health="HealthBench 0.570 (llm-stats); HealthBench Pro 60.5*", throughput="57.3 tok/s (AA)",
      changed_this_week="Repriced to list 5/30/0.50 as shown on openai.com/api/pricing; the 4/20 promo quoted in issue 01 is unverified as live",
      src="https://openai.com/api/pricing/"),
 dict(model="Muse Spark 1.3", vendor="Meta", date="2026-09-02", open_weights=False, licence="proprietary; open weights on roadmap*",
      context="1M", max_output="unverified", price={"in":1.25,"out":4.25,"cached":0.15},
      aa_index="48 (v4.3, max)", coding="unverified", health="none published", throughput="201 tok/s (AA); 97 tok/s (OpenRouter)",
      changed_this_week="AA v4.3 (was 53)", src="https://artificialanalysis.ai/models/muse-spark-1-3"),
 dict(model="Qwen3.8-Max-0902", vendor="Alibaba", date="2026-09-02", open_weights=False, licence="API only; base open under Qwen3.8-Max License",
      context="1M", max_output="131K", price={"in":2.0,"out":6.0,"cached":0.25},
      aa_index="40 (v4.3, Qwen3.8 Max page)", coding="unverified", health="HealthBench 0.602 (llm-stats, #1 of 10 self-reported)",
      throughput="37.9 tok/s (AA)", changed_this_week="AA v4.3 (was 58)", src="https://artificialanalysis.ai/models/qwen3-8-max"),
 dict(model="Qwen3.8-Flash-Next", vendor="Alibaba", date="2026-08-26", open_weights=True, licence="Qwen Community License 1.0",
      context="262K native, 1M YaRN", max_output="unverified", price={"in":0.15,"out":0.47,"cached":None},
      aa_index="40 (v4.3)", coding="unverified", health="none published", throughput="53.2 tok/s (AA)",
      changed_this_week="AA v4.3 (was 56)", src="https://artificialanalysis.ai/models/qwen3-8-flash-next"),
 dict(model="Qwen3.8-27B", vendor="Alibaba", date="2026-08-14", open_weights=True, licence="Apache 2.0",
      context="262K native, 1M YaRN", max_output="32K", price={"in":0.22,"out":2.42,"cached":0.05},
      aa_index="34 (v4.3, xhigh)", coding="unverified", health="none published", throughput="39.0 tok/s (AA)",
      changed_this_week="AA v4.3 (was unscored)", src="https://artificialanalysis.ai/models/qwen3-8-27b"),
 dict(model="GLM-5.3", vendor="Z.ai", date="2026-08-28", open_weights=True, licence="custom GLM-5.3 License",
      context="1M", max_output="262K", price={"in":1.4,"out":4.4,"cached":0.26},
      aa_index="45 (v4.3, max)", coding="AutomationBench-AA 62.2 (AA)", health="none published", throughput="61.6 tok/s (AA)",
      changed_this_week="AA v4.3 (was 49)", src="https://artificialanalysis.ai/models/glm-5-3"),
 dict(model="GLM-5.3-Flash", vendor="Z.ai", date="2026-08-26", open_weights=True, licence="MIT",
      context="1M", max_output="unverified", price={"in":0.15,"out":0.5,"cached":0.03},
      aa_index="42 (v4.3)", coding="unverified", health="none published", throughput="90.5 tok/s (AA)",
      changed_this_week="Launch promo (0.075/0.25) ended 9 Sept; list price now applies. AA v4.3 (was 46)",
      src="https://docs.z.ai/guides/overview/pricing"),
 dict(model="Hy4 Preview", vendor="Tencent", date="2026-08-28", open_weights=True, licence="Apache 2.0 per third parties, unverified",
      context="1M", max_output="64K", price={"in":0.834,"out":2.501,"cached":0.042},
      aa_index="not scored", coding="unverified", health="none published", throughput="unverified",
      changed_this_week=None, src="https://openrouter.ai/tencent/hy4-preview"),
 dict(model="Granite 4.2 8B", vendor="IBM", date="2026-08-25", open_weights=True, licence="Apache 2.0",
      context="131K", max_output="unverified", price={"in":0.06,"out":0.25,"cached":0.015},
      aa_index="12 (v4.3, reasoning)", coding="unverified", health="none published", throughput="89.3 tok/s, TTFT 0.64 s (AA)",
      changed_this_week="AA v4.3 (was unscored)", src="https://artificialanalysis.ai/models/granite-4-2-8b"),
 dict(model="Mercury 2.5 Preview", vendor="Inception", date="2026-08-31", open_weights=False, licence="proprietary, diffusion",
      context="260K", max_output="65,536", price={"in":0.2,"out":0.75,"cached":0.02},
      aa_index="not scored", coding="unverified", health="none published", throughput="1,107 tok/s claimed*; 52 tok/s measured (OpenRouter)",
      changed_this_week="80% preview discount reported to expire 8 Sept; OpenRouter page still showed the discount on 12 Sept: unverified",
      src="https://openrouter.ai/inception/mercury-2.5-preview"),
 dict(model="DeepSeek-V4.1-Flash", vendor="DeepSeek", date="2026-09-10", open_weights=True, licence="MIT",
      context="1M", max_output="384K", price={"in":0.30,"out":1.20,"cached":0.006},
      aa_index="40 (v4.3, reasoning max effort)", coding="Terminal-Bench 2.1: 90.6*; DeepSWE v1.1: 74.2*; Terminal-Bench 4.0: 27 (AA comparison page, independent)",
      health="none published", throughput="217 tok/s, TTFT 1.13 s (AA); 127 tok/s (OpenRouter, DeepSeek provider)",
      changed_this_week="New. Peak price shown; off-peak is half (0.15/0.60/0.003). 552B MoE, 8B active prefill, 16B decode, native vision",
      src="https://api-docs.deepseek.com/quick_start/pricing"),
 dict(model="Fugu Max", vendor="Sakana AI", date="2026-09-11", open_weights=False, licence="hosted orchestrator over open models",
      context="1M", max_output="128K", price={"in":2.0,"out":6.0,"cached":0.25},
      aa_index="not scored", coding="vendor cites Terminal-Bench 2.1 and SWEFish, figures unverified", health="none published",
      throughput="13 tok/s, 5.4 s P50 (OpenRouter)", changed_this_week="New", src="https://openrouter.ai/sakana/fugu-max"),
 dict(model="Fugu Ultra v2", vendor="Sakana AI", date="2026-09-11", open_weights=False, licence="hosted orchestrator over open models",
      context="1M", max_output="128K", price={"in":5.0,"out":30.0,"cached":None},
      aa_index="not scored", coding="DeepSWE 74.3*", health="none published", throughput="unverified",
      changed_this_week="New; higher rate above 272K prompt tokens", src="https://openrouter.ai/sakana/fugu-ultra-v2"),
 dict(model="Cohere Parse 5", vendor="Cohere", date="2026-08-27", open_weights=False, licence="proprietary parser",
      context="8,192 per page", max_output="n/a", price={"in":None,"out":None,"cached":None},
      aa_index="n/a", coding="n/a", health="ParseBench 79.2*", throughput="unverified",
      changed_this_week=None, src="https://www.eesel.ai/blog/cohere-parse-5-review", flat_cost="$15.00 at $1.50 per 1,000 pages, one page each"),
 dict(model="MedGemma 1.5 4B", vendor="Google", date="2026-01-13", open_weights=True, licence="Health AI Developer Foundations terms",
      context="128K", max_output="8,192", price={"in":None,"out":None,"cached":None},
      aa_index="not scored", coding="n/a", health="MedQA 69.1*, MedMCQA 59.8*; ObGynLongBench 64.0 evidence-only, 41.3 history-level (arXiv 2609.07601, independent)",
      throughput="self-host", changed_this_week="Independent longitudinal-EHR score appeared this week", src="https://huggingface.co/google/medgemma-1.5-4b-it"),
]

for r in ROWS:
    r["cost_10k_docs_no_cache"], r["cost_10k_docs_80pct_cached"] = cost(r["price"])

doc = {"issue": "02", "week_ending": W, "workload": "10,000 docs x (4,000 in + 500 out) tokens",
       "formulas": {"no_cache": "40*in + 5*out", "cached_80": "8*in + 32*cached + 5*out"},
       "aa_index_note": "Artificial Analysis Intelligence Index v4.3 published 7 Sept 2026 (Terminal-Bench 4.0, AutomationBench-AA); scores are not comparable with v4.2 numbers in issue 01",
       "models": ROWS}
json.dump(doc, open("models.json", "w"), indent=1)

if __name__ == "__main__":
    for r in ROWS:
        p = r["price"]
        ps = f'{p["in"]} / {p["out"]} / {p["cached"] if p["cached"] is not None else "n.a."}' if p["in"] is not None else r.get("flat_cost", "n/a")
        print(f'{r["model"]:22s} {ps:28s} AA {r["aa_index"]:34s} ${r["cost_10k_docs_no_cache"]} / ${r["cost_10k_docs_80pct_cached"]}')
