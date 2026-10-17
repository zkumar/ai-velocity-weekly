# AI Velocity Weekly 03, lab package

Week ending 18 September 2026. Synthetic data only; no model key is needed for any script.
Issue: [details.html](../details.html).

This week's question is what the approval covered. Both scripts put a scripted model in front of
a MedicationRequest tool that needs a clinician, and compare what the approval step saw with what
the tool actually wrote. Each runs twice, on the week's release and on the release before it.

## Files

| File | What it demonstrates | Install |
|---|---|---|
| `test_oa_approval_arguments.py` | OpenAI Agents SDK 0.22.3, commit `1d17ca4` (#5066): a conditional `needs_approval` policy now runs only when validation leaves the model's arguments unchanged; otherwise the call goes to a human. Four calls: explicit oral order, route omitted (tool default IV), and the same pair through a `Dose` model that normalises grams to milligrams. The mechanism of the week. | `pip install "openai-agents==0.22.3"` (and `==0.22.2` to compare) |
| `test_lc_hitl_edit.py` | LangChain 1.4.2, commit `5bf6a15` (#40463): after a pharmacist edits a proposed dose, the transcript keeps the model's proposal and the executed arguments live in a private checkpoint key and in the ToolMessage text. Also run with `edit_notice=None`. | `pip install "langchain==1.4.2"` (and `==1.4.1`) |
| `build_models.py` | Regenerates `models.json` and the section 2 cost columns. | none |
| `models.json` | Model table: licence, list prices read 20 Sept, AA v4.3 score, cost of the 10,000-document workload with and without cache, source, what changed. | none |
| `requirements.txt`, `requirements-previous.txt` | Pinned versions for the week's releases and the ones before them. | |
| `run_all.sh` | Builds `.venv/current` and `.venv/previous`, installs each set, runs every `test_*.py` in both, then the model table. | |

## Observed output (20 Sept 2026, clean directory, Python 3.11, Linux)

`test_oa_approval_arguments.py`

    openai-agents 0.22.2
      A flat, oral 500 mg explicit        policy saw route PO       paused False  FHIR 500 mg PO
      B flat, route omitted (default IV)  policy saw no route key   paused False  FHIR 500 mg IV
      C model, oral 500 mg                policy saw 500 mg         paused False  FHIR 500 mg PO
      D model, 1.5 g (runs as 1,500 mg)   policy saw 1.5 g          paused False  FHIR 1500 mg PO
      SUMMARY: policy-required approvals missed=2 of 2 | approvals added on safe calls=0 of 2 | unapproved writes=2

    openai-agents 0.22.3
      A flat, oral 500 mg explicit        policy saw route PO       paused False  FHIR 500 mg PO
      B flat, route omitted (default IV)  policy not called         paused True   clinician shown {"patient_id": "pt-123", "rxnorm": "860975", "dose_mg": 500}   FHIR 500 mg IV
      C model, oral 500 mg                policy not called         paused True   FHIR 500 mg PO
      D model, 1.5 g (runs as 1,500 mg)   policy not called         paused True   clinician shown {... "dose": {"amount": 1.5, "unit": "g"}}   FHIR 1500 mg PO
      SUMMARY: policy-required approvals missed=0 of 2 | approvals added on safe calls=1 of 2 | unapproved writes=0

The model says "Order placed." in all eight runs. (Lines condensed; the script prints the full dicts.)

`test_lc_hitl_edit.py`

    langchain 1.4.1   transcript tool_call dose_mg 500 | tool received 500 | checkpoint key absent            | transcript == executed: True
    langchain 1.4.2   transcript tool_call dose_mg 1000 | tool received 500 | ToolMessage begins "Note: a human reviewer replaced this tool call before it ran ..."
                      checkpoint hitl_edited_tool_calls: {'call_1': {... 'dose_mg': 500}} | invoke() output keys: ['messages'] | transcript == executed: False
    1.4.2, edit_notice=None   ToolMessage 'MedicationRequest written: 500 mg' | executed args only in the checkpoint key

`build_models.py`: see the table in section 2 of the issue. GPT-5.6 Sol is $260 for the workload at
the 4/20/0.40 list price; issue 02 printed 5/30/0.50, which was wrong.

## What each result means

1. **0.22.2 approved on arguments that never ran.** The policy saw the model's JSON; the tool ran on
   the validated, defaulted values. An omitted route became IV and 1.5 g became 1,500 mg, both
   written with no clinician. 0.22.3 closes that: when validation changes anything, or the tool takes
   an application model or custom validator, the policy is skipped and the call goes to a human.
2. **The human is shown the same JSON the policy used to see.** In 0.22.3 the interruption carries
   `raw_item.arguments`, the model's text. The clinician approving case B sees no route; the order is
   written IV. Render the validated arguments yourself before you ask for a signature.
3. **Fail-closed has a cost.** Any tool with a Pydantic model argument now pauses on every call
   (case C), so the conditional policy is dead code for it. Flatten the arguments of tools that
   need conditional approval, or expect approval fatigue.
4. **LangChain now keeps two records.** From 1.4.2 an audit exporter that reads executed arguments
   off `AIMessage.tool_calls` records what the model proposed, not what ran. Read
   `agent.get_state(config).values["hitl_edited_tool_calls"]`, and do not set `edit_notice=None`
   unless you persist that key.

## Things to change and rerun

1. In `test_oa_approval_arguments.py`, replace the `print` of `raw_item.arguments` with the
   validated arguments (run the tool's `params_json_schema` through your own validator) and show
   that to the approver. Check that case B now displays `route: IV`.
2. Point `needs_clinician` at your real CPOE policy and run each of your write tools through the
   four cases. Every tool that pauses on case A or C is a tool whose policy the SDK will not run.
3. In `test_lc_hitl_edit.py`, write your audit row from the checkpoint key and the ToolMessage
   `name`, and assert that the row matches `RECEIVED`.

## Verified from a clean install

On 20 Sept 2026 these files were copied into an empty directory and `bash run_all.sh` was run with
no API key in the environment. It created both virtual environments, installed the pinned versions
and printed the output above. If a script fails on your machine, compare `pip freeze` with the
requirements file first.
