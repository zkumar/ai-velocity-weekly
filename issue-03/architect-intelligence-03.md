# Architect Intelligence 03: What The Yes Covered

Week Of Sep 12–18, 2026 · Vijay Zharotia

**Last week a clock and a token audience could decide before the clinician. This week the question moved inside the call itself, to whether a yes is bound to the arguments that run or to the ones the model wrote.**

Issue 02 asked who may answer before the clinician. This week three frameworks changed which arguments an approval is attached to, and one of them now keeps the proposed call and the executed call in different places.

This week: 22 repos cloned and read, 2 mechanisms executed, 7 papers read, 13 models priced.

## Five changes, one home each

Each fact appears once below. This list says where.

1. **A conditional policy is skipped when validation changes the call** (Openai Agents Sdk 0.22.3, executed), section 08
2. **An edited call now leaves the proposal and the execution apart** (Langchain 1.4.2, executed), section 04
3. **A repaired argument voids the approval and asks again** (Agent Framework 1.19.0, docs), section 04
4. **A redaction flag leaked instructions through a fallback model** (Pydantic-Ai 2.44.0, docs), section 05
5. **Strict tool fields were coerced for four releases** (Fastmcp 4.0.5, docs), section 05

## What an Approval Is Attached To

One executed, two read from source. The OpenAI Agents SDK change is executed on slide 08.

### A pharmacist cuts 1000 mg to 500 mg and the transcript still says 1000

*Langchain 1.4.2* · executed

Edits no longer rewrite the AIMessage. The executed call lives in a private checkpoint key, hitl_edited_tool_calls, and a notice on the ToolMessage. On 1.4.1 transcript and tool agreed; on 1.4.2 they do not, and with edit_notice=None the key is the only record.

**What changed.** The model's proposal is now preserved, which is right for review. Any exporter reading AIMessage.tool_calls as what ran is now wrong.

**What to change.** Write the audit row from the checkpoint key and the ToolMessage name, never the AIMessage. Keep the notice on. test_lc_hitl_edit.py runs both versions.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-03/lab/)

### A middleware that repairs an approved argument voids the approval

*Microsoft · Agent Framework 1.19.0* · docs

Approval binds to the normalised arguments with a float-bit-exact comparison. A changed approval-bound call executes zero times and yields a replacement request with a fresh generation id. A user turn now delimits stateless approval batches, and .NET rejects approvals it did not itself record.

**What changed.** The strongest statement this week that the signed arguments and the executed arguments must be the same object.

**What to change.** Put argument-repair middleware before policy middleware, as the spec requires, and treat a replacement request as a second signature event in the transcript.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-03/ai-velocity-weekly-03.html)

### An approval is revoked when the approved content's digest changes

*Mcp Spec · Sep-2640 Skills, Final* · docs

The skills extension says a persisted approval MUST be bound to the resource set and digests observed at approval, and MUST be treated as revoked and re-prompted when they change. It also says the allowed-tools field MUST be ignored for server-origin skills unless the user approved it.

**What changed.** The first normative MCP text that ties a remembered yes to what was shown, not to a name.

**What to change.** Key cached tool approvals on a hash of name, description and input schema. Re-prompt on any change.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-03/ai-velocity-weekly-03.html)

> **Architect signal.** Three vendors answered the binding question three ways in one week. Pick the strictest one for your write tools and make it the tested contract.

## Two Settings That Were Quietly Ignored

Both read from source and changelog, neither executed. Each was a control you had switched on that did not hold.

### include_content=False could still export instructions to your traces

*Pydantic-Ai 2.44.0* · docs

A FallbackModel refresh treated an unset policy as permission to export, and streamed consumers lost the policy entirely. The fix fails closed per span, and unserialisable request parameters are now dropped instead of exported as a string.

**What changed.** Instruction text carrying PHI could reach an OTel collector configured not to receive it.

**What to change.** Upgrade, then search spans from FallbackModel and streamed runs since you enabled redaction. A leak you cannot bound is a breach assessment, not a bug ticket.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-03/ai-velocity-weekly-03.html)

### A StrictInt dose field accepted the string "5" since the SDK v2 migration

*Fastmcp 4.0.4 And 4.0.5* · docs

The server's lax default overrode Field(strict=True), StrictInt and strict model configs on direct calls and task submission. 4.0.5 restores them. 4.0.4 stops logging argument values in validation warnings and rejects ID-JAG tokens when identity assertion is off.

**What changed.** A strict schema is part of a validated tool contract, and for weeks it was a suggestion.

**What to change.** Add a test that "42" is rejected for every strict field on every write tool, and alert on the new ID-JAG rejection warning.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-03/ai-velocity-weekly-03.html)

> **Architect signal.** A control that is configured but not enforced produces a clean audit trail. Only a test that tries to break it tells you which you have.

## A Correction and a Cheaper Floor

4,000 input and 500 output tokens per document, list prices read 20 September. Artificial Analysis stayed on v4.3, so scores compare with Issue 02.

### Sol does the job for $260, not the $350 Issue 02 printed

*Correction · Gpt-5.6 Sol*

The pricing page lists $4 in, $20 out, $0.40 cached, promotional until at least 21 November. Issue 02 said the promotion had ended at $5/$30; it had not. AA v4.3 score 47, unchanged.

**What changed.** Sol sits $65 under Opus 5 for the workload, four points lower on the index, with an end date on the price.

**What to change.** If you moved a workload off Sol on last week's number, reverse it only with the November expiry written into the budget.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-03/ai-velocity-weekly-03.html)

### GLM-5.3-Flash at $8.50 scores 42, above DeepSeek-V4.1-Flash at $18

*Open Weights · Mit*

Unchanged prices; the ordering is what moved. Qwen3.8-27B was repriced on OpenRouter to $0.10/$1.80, $13 for the job, but the leaderboard now reads 22 where Issue 02 printed 34, and 45 for Qwen3.8-Max where it printed 40. Unverified why.

**What changed.** The cheapest row is no longer the weakest, and open-model scores moved without a version change.

**What to change.** Re-read the scores the day you decide, and store the read date beside the model choice in your validation file.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-03/ai-velocity-weekly-03.html)

> **Architect signal.** An index can shift under a fixed version label. A model decision needs the score, the date read and the price expiry as one record.

## Runs, Traces and Who Checks Them

Three results on repeatability, trace-level policy and audit independence. Each is a claim; each note is the build change.

### 43 of 43 ordering groups write different orders across five identical runs

*Medagentbench · 2609.13582*

1,000 evaluations over 50 tasks. With an 8B model at temperature 0.7 the benchmark score was identical across runs while the actual doses, tests and referrals differed every time.

**What changed.** A pass rate says nothing about which order the agent writes on a given day.

**What to change.** Add a five-run repeat to your eval and fail it on any difference in emitted orders or arguments, not on the score.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-03/ai-velocity-weekly-03.html)

### Every step passes its check and the run still breaks the policy

*Compositional Violations · 2609.18820*

Four named patterns, authority creep, threshold laundering, cumulative sum violation and context collapse, with a provenance-tracking runtime that checks policy over the whole trace. No quantitative results in the abstract.

**What changed.** A dose limit checked per call is defeated by three calls under the limit.

**What to change.** Keep running totals per patient and per encounter across the trace and check the limit there, not only at the tool.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-03/ai-velocity-weekly-03.html)

### An internal audit surfaces 5.9 percent of the faults it could see

*Independence-Graded Audit · 2609.18272*

Grades audit independence on control, shared technical substrate and attestable evidence, borrowing the beta-factor common-cause model. In simulation a conventional internal audit finds none at all in half the fault classes.

**What changed.** An auditor built on the agent's own logging stack shares its blind spots.

**What to change.** Write audit evidence to a store the agent cannot write to, read by a stack it does not share.

[Read the mechanism](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-03/ai-velocity-weekly-03.html)

> **Architect signal.** Same input, different orders. Legal steps, illegal sum. A shared stack auditing itself. Each needs a test the agent's own logs cannot pass by construction.

## Mechanism of the week: The policy that stopped approving arguments it never saw

*Openai Agents Sdk 0.22.3 · Scriptedmodel, 0.22.2 Against 0.22.3, No Model Key*

A write tool with a conditional policy, IV or above 1,000 mg needs a clinician. Four scripted calls. On 0.22.2 the policy read the model's JSON while the tool ran the validated values, so an omitted route was written as the default IV and 1.5 g as 1,500 mg, both with no clinician. On 0.22.3 both paused. But the clinician is shown the same raw JSON, no route and 1.5 g, and a tool taking a Pydantic model now pauses on every call, safe or not.

**2** writes the policy missed on 0.22.2 · **0** unapproved writes on 0.22.3 · **1 of 2** safe calls now paused

**What changed.** The gap moved from the policy to the screen. The SDK hands the decision to a human, and the human sees what the policy used to see.

**Move.** Render the validated arguments, defaults filled in, on the approval screen, and flatten the arguments of tools that need a conditional policy. test_oa_approval_arguments.py runs both versions in under two minutes.

[Open the lab package](https://zkumar.github.io/AI-Velocity-Technology-Update-/issue-03/lab/)

> **Architect signal.** The fix is fail-closed and correct. What the approver reads is still yours to build, and it is the line an auditor will ask about.

## What the architects shipped

- **Epic.** Agent Factory build-a-thon, 25 health systems building refill, critical-care-time and med-reconciliation agents inside Epic. No published audit contract for write-back.
- **Langchain.** Included Health's federated agents on Deep Agents and LangGraph, with annotation queues as the clinical oversight layer.
- **Openai.** A framework for reporting model misalignment, including acting without authorisation and concealing information, with six disclosed cases.
- **Willison.** A write-up showing an operator's own logs could not reconstruct what its agents had done to RubyGems in May.
- **Aiuc.** AIUC-1 on Latent Space, an agent certification that insurers price against, with third-party adversarial testing and evidence specifications.

Nothing in window from LangGraph or Semantic Kernel releases, HL7, FDA on AI, ONC, NIST, the MCP blog or the Anthropic engineering blog.

> **Architect signal.** Insurers, a lab and a large EHR vendor all talked about evidence for agent actions this week. None published the record format.

## Contracts and Payment Rules That Set the Evidence Bar

### Medicare will pay on outcomes for AI-enabled chronic care

*Cms · Access Model*

Announced 15 September for spring 2027, adding heart failure, COPD and substance use disorder, with payment tied to outcomes and access to AI-enabled technologies and remote monitoring named in the release. No data standard is named.

**Move.** If you build for a participant, design the outcome measurement as an audited pipeline now. The payment depends on it and no standard will tell you its shape.

### Tool inputs in compliance transcripts are capped at 10,000 bytes, kept six years

*Anthropic · Compliance Api, Managed Agents*

Compliance transcripts carry tool_use and tool_result with a truncated flag and 10,000-byte defaults, retained six years; the documented fields include no approval record. The Managed Agents overview states it is not eligible for zero-data-retention or BAA coverage.

**Move.** Keep your own full-fidelity tool log for PHI workflows; a vendor transcript truncated at 10 KB is not the record of a FHIR bundle.

Every dated source for this week is in the long-form edition. The cumulative Radar was not refreshed this week. [Open the Radar](https://zkumar.github.io/AI-Velocity-Technology-Update-/index.html)

> **Architect signal.** A payer rule and a vendor contract each fix what evidence must exist. You decide where it lives.

---

Full mechanism, code and sources for every card are in the long-form edition. The architect's position on this week's decision is in My Take. The code runs from a clean virtual environment with no API key. Everything is at https://github.com/zkumar/AI-Velocity-Technology-Update- .
