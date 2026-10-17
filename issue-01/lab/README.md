# AI Velocity Weekly 01, lab package (rebuilt 12 Sept 2026)

Week ending 5 September 2026. The original package was delivered in the
5 Sept session and lost; these scripts were rebuilt from the Issue 01 text
and re-run on 12 Sept. Synthetic data only. Issue:
https://zkumar.github.io/ai-velocity-weekly/issue-01/details.html

| File | What it does | Install |
|---|---|---|
| `test_lc_elicitation.py` | LangChain 1.4.0 `langchain.mcp.MCPAdapter`: a FastMCP FHIR tool returns `InputRequiredResult` (SEP-2322), the run parks in a LangGraph checkpoint, the resume carries the clinician's signature. No model; a ToolNode plays the tool step. | `pip install "langchain[mcp]==1.4.0" langgraph fastmcp` |
| `test_af_approval.py` | Agent Framework 1.17.0 approval bound to the `af-call-<hex>` occurrence id: a forged id is ignored and the pending request retained; the write happens only after the matching approval; the scripted model says "Order placed." either way. Runs on 1.18.0 too. | `pip install "agent-framework-core>=1.17.0"` |
| `raf_gap_lab.py` | The RAF gap lab: hand-coded MEAT extraction from a synthetic note scored by hccinfhir under CMS-HCC V24 and V28 against the claims-only baseline; `--model` swaps in a Pydantic AI agent and prints the disagreement rate. | `pip install hccinfhir pydantic-ai-slim` |
| `models.json` | Issue 01 model table, rebuilt from the Radar Models tab (AA index v4.2; not comparable with Issue 02's v4.3 scores). | none |

## Observed output (12 Sept 2026 rerun)

    test_lc_elicitation.py
      interrupt payload: {"type": "mcp_elicitation", "tool_name": "create_medication_order", "requests": [{"key": "confirm", ...}]}
      writes before signature: 0
      writes after signature: 1 [{'patient_id': 'pt-123', 'rxnorm': '197361', 'npi': '1234567893'}]

    test_af_approval.py
      audit record: {'approval_request_id': 'af-call-4de0...', 'occurrence_id': 'af-call-4de0...', 'provider_call_id': 'call_abc', ...}
      after forged id: writes = 0 | results = [] | model said: 'Order placed.'
      after real approval: writes = 1 | results = ['MedicationRequest written for pt-123']

    raf_gap_lab.py (offline)
      CMS-HCC Model V24   claims 0.560   claims + note 3.059   delta 2.499   HCCs added 18, 22, 59, 85, 111, 189
      CMS-HCC Model V28   claims 0.688   claims + note 3.004   delta 2.316   HCCs added 37, 48, 155, 226, 280, 409

The V28 list in the issue originally read "48, 155, 226, 280, 328, 409"; the
rerun with hccinfhir 0.3.3 and the 2026 mapping gives 37 in place of 328.
Scores are identical. The issue text was corrected on 13 Sept 2026 to match.

Versions: langchain 1.4.0, langchain-core 1.6.3, langgraph 1.2.11, fastmcp 4.0.3,
mcp 2.2.0, agent-framework-core 1.18.0, hccinfhir 0.3.3, Python 3.11.

## Verified from a clean install

On 12 Sept 2026 the zip was unpacked into an empty directory and `bash run_all.sh` was run: it creates a fresh virtual environment, installs the exact versions in `requirements.txt`, and runs every script. All passed with the output shown above (Python 3.11, Linux). To repeat that check yourself: `bash run_all.sh`. If a script fails on your machine, the first thing to compare is `pip freeze` against `requirements.txt`.
