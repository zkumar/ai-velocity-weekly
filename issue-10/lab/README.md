# AI Velocity Weekly 10: lab

Week ending 6 November 2026. One mechanism and one supporting check, each run on the release
before this week's window and on the release in it, plus the model table. No API key is read or
needed: the "model" is a scripted `BaseChatClient` subclass in the first script and a
`FunctionModel` in the second, the MCP server is a local stdio process started by the script, and
the "record" is a JSON-lines file (first script) or an in-memory list (second). Synthetic data only.

```
./run_all.sh
```

`run_all.sh` creates two virtual environments (`.venv-prev` from `requirements-previous.txt`,
`.venv` from `requirements.txt`) and runs both scripts on both. Python 3.11 or later; the output
below is from Python 3.13 on Linux, run on 6 November 2026 from clean environments, twice, with
byte-identical output.

| Pinned | previous | this week |
|---|---|---|
| agent-framework-core | 1.23.0 (22 Oct, 17:01 UTC) | 1.24.0 (30 Oct, 21:38 UTC) |
| pydantic-ai-slim | 2.65.0 (3 Nov, 01:53 UTC) | 2.66.0 (4 Nov, 10:28 UTC) |
| mcp, tenacity | 2.3.0, 9.1.4 | 2.3.0, 9.1.4 |

Dates are PyPI upload times. `mcp` and `tenacity` are the two optional dependencies Agent
Framework's local MCP tool imports; they are pinned to the same versions on both sides so the
only variable is the framework.

## What the scripts demonstrate

### `test_af_mcp_unlisted_tool.py` (mechanism of the week)

A ward-assistant agent reaches a pharmacy MCP server (`pharmacy_server.py`, three tools) through
Agent Framework's `MCPStdioTool`. The approval policy names the write the team knew about and the
read: `{"always_require_approval": ["place_order"], "never_require_approval": ["read_chart"]}`.
The server also offers `discontinue_order`, a write the policy names in neither list, the way a
tool added by the server team after the lists were written would be. The scripted model asks for
one tool call and closes the turn with whatever the tool returned. `LAB_CASE` selects the policy
and the call. What was counted, per run:

| case | version | policy resolves `discontinue_order` to | warnings | approval requests | rows before any answer | rows at end |
|---|---|---|---|---|---|---|
| listed (calls `place_order`) | 1.23.0 | never_require | 0 | 1 | 0 | 0 |
| listed (calls `place_order`) | 1.24.0 | never_require | 1 | 1 | 0 | 0 |
| unlisted | 1.23.0 | never_require | 0 | **0** | **1** | 1 |
| unlisted | 1.24.0 | never_require | 1 | **0** | **1** | 1 |
| default (`"default": "always_require"` added) | 1.23.0 | **never_require** | 0 | **0** | **1** | 1 |
| default | 1.24.0 | always_require | 0 | 1 | 0 | 0 |
| approved (default, then the clinician approves) | 1.23.0 | never_require | 0 | 0 | 1 | 1 |
| approved | 1.24.0 | always_require | 0 | 1 | 0 | 1 |
| joined (`"always_require_approval": "place_order,discontinue_order"`) | 1.23.0 | always_require | 0 | 1 | 0 | 0 |
| joined | 1.24.0 | **never_require** | 1 | **0** | **1** | 1 |

Three findings.

1. **The unlisted write runs without a question on both versions.** A tool named in neither list
   resolves to `never_require`. On 1.23.0 nothing says so. On 1.24.0 constructing the tool emits
   one `FutureWarning`: "approval_mode sets `never_require_approval` without `default`. Tools and
   prompts named in neither list use "never_require" today, and this fallback may change in a
   future release."
2. **The key that closes it is ignored, in silence, one release back.** 1.24.0 adds
   `"default": "always_require"` to the policy dict: the unlisted write then waits (1 approval
   request, 0 rows) and writes once after the approval. The same dict on 1.23.0 is accepted with no
   error and no warning, the `default` key is never read, and the write runs: 0 approval requests,
   1 row. A policy file rolled out ahead of the package, or a package rolled back under the policy
   file, has a gate on paper and none in the process.
3. **One misconfiguration flips the other way on upgrade.** A name list supplied as one
   comma-joined string (what an environment variable or a YAML scalar gives you) was tested with
   Python's `in` on 1.23.0, a substring match, so `"place_order,discontinue_order"` gated both
   writes by accident. 1.24.0 treats a bare string as one name ("A name list given as a single
   string is treated as one name"), nothing matches it, and both writes, `place_order` included,
   resolve to `never_require`: 1 approval request and 0 rows on 1.23.0, 0 approval requests and
   1 row on 1.24.0.

In every run where the write happened, the model's closing text was the same sentence, `Done.
{"result": "ORDER DISCONTINUED order-1 for pt-123"}`. Nothing in the reply distinguishes a write
a clinician approved from one nobody was asked about; the approval-request count and the record
do.

Source for the cause, read from both wheels, `agent_framework/_mcp.py`. On 1.23.0 the per-tool
resolver returned `"always_require"` if the name was in `always_require_approval`,
`"never_require"` if it was in `never_require_approval`, and otherwise `None`, which
`FunctionTool.__init__` turns into `"never_require"` (`self.approval_mode = approval_mode or
"never_require"`, `_tools.py`). 1.24.0 adds `default` to the `MCPSpecificApproval` TypedDict,
routes the fall-through to `_mcp_approval_default()`, raises `ValueError` for a `default` that is
neither `"always_require"` nor `"never_require"`, and warns once at construction when
`never_require_approval` is set without `default`. Changelog: "Add an explicit default approval
mode for local MCP tools and prompts outside the per-tool approval lists, and warn when
`never_require_approval` leaves the default implicit while preserving the existing fallback"
(#9828). The docstring adds: "Hosted MCP tools do not read `default`."

Full output of the mechanism runs:

```
=== 1 agent-framework: the tool the approval policy does not name (mechanism of the week) ===
--- case=listed ---
agent-framework-core 1.23.0  case=listed  call=place_order
  policy passed          : {"always_require_approval": ["place_order"], "never_require_approval": ["read_chart"]}
  resolved per tool      : {"discontinue_order": "never_require", "place_order": "always_require", "read_chart": "never_require"}
  warnings at construct  : 0
  approval requests      : 1 (place_order)
  rows before any answer : 0
  rows at end            : 0
  model turns            : 1
  final text             : ''
agent-framework-core 1.24.0  case=listed  call=place_order
  policy passed          : {"always_require_approval": ["place_order"], "never_require_approval": ["read_chart"]}
  resolved per tool      : {"discontinue_order": "never_require", "place_order": "always_require", "read_chart": "never_require"}
  warnings at construct  : 1
      FutureWarning: approval_mode sets `never_require_approval` without `default`. Tools and prompts named in neither list use "never_require" today, and this fallback may change in a future release. Set `default` to "never_require" to keep the current behavior or to "always_require" to require approval for them.
  approval requests      : 1 (place_order)
  rows before any answer : 0
  rows at end            : 0
  model turns            : 1
  final text             : ''
--- case=unlisted ---
agent-framework-core 1.23.0  case=unlisted  call=discontinue_order
  policy passed          : {"always_require_approval": ["place_order"], "never_require_approval": ["read_chart"]}
  resolved per tool      : {"discontinue_order": "never_require", "place_order": "always_require", "read_chart": "never_require"}
  warnings at construct  : 0
  approval requests      : 0
  rows before any answer : 1
  rows at end            : 1  {"action": "discontinue_order", "patient_id": "pt-123", "order_id": "order-1"}
  model turns            : 2
  final text             : 'Done. {"result": "ORDER DISCONTINUED order-1 for pt-123"}'
agent-framework-core 1.24.0  case=unlisted  call=discontinue_order
  policy passed          : {"always_require_approval": ["place_order"], "never_require_approval": ["read_chart"]}
  resolved per tool      : {"discontinue_order": "never_require", "place_order": "always_require", "read_chart": "never_require"}
  warnings at construct  : 1
      FutureWarning: approval_mode sets `never_require_approval` without `default`. Tools and prompts named in neither list use "never_require" today, and this fallback may change in a future release. Set `default` to "never_require" to keep the current behavior or to "always_require" to require approval for them.
  approval requests      : 0
  rows before any answer : 1
  rows at end            : 1  {"action": "discontinue_order", "patient_id": "pt-123", "order_id": "order-1"}
  model turns            : 2
  final text             : 'Done. {"result": "ORDER DISCONTINUED order-1 for pt-123"}'
--- case=default ---
agent-framework-core 1.23.0  case=default  call=discontinue_order
  policy passed          : {"always_require_approval": ["place_order"], "never_require_approval": ["read_chart"], "default": "always_require"}
  resolved per tool      : {"discontinue_order": "never_require", "place_order": "always_require", "read_chart": "never_require"}
  warnings at construct  : 0
  approval requests      : 0
  rows before any answer : 1
  rows at end            : 1  {"action": "discontinue_order", "patient_id": "pt-123", "order_id": "order-1"}
  model turns            : 2
  final text             : 'Done. {"result": "ORDER DISCONTINUED order-1 for pt-123"}'
agent-framework-core 1.24.0  case=default  call=discontinue_order
  policy passed          : {"always_require_approval": ["place_order"], "never_require_approval": ["read_chart"], "default": "always_require"}
  resolved per tool      : {"discontinue_order": "always_require", "place_order": "always_require", "read_chart": "never_require"}
  warnings at construct  : 0
  approval requests      : 1 (discontinue_order)
  rows before any answer : 0
  rows at end            : 0
  model turns            : 1
  final text             : ''
--- case=approved ---
agent-framework-core 1.23.0  case=approved  call=discontinue_order
  policy passed          : {"always_require_approval": ["place_order"], "never_require_approval": ["read_chart"], "default": "always_require"}
  resolved per tool      : {"discontinue_order": "never_require", "place_order": "always_require", "read_chart": "never_require"}
  warnings at construct  : 0
  approval requests      : 0
  rows before any answer : 1
  rows at end            : 1  {"action": "discontinue_order", "patient_id": "pt-123", "order_id": "order-1"}
  model turns            : 2
  final text             : 'Done. {"result": "ORDER DISCONTINUED order-1 for pt-123"}'
agent-framework-core 1.24.0  case=approved  call=discontinue_order
  policy passed          : {"always_require_approval": ["place_order"], "never_require_approval": ["read_chart"], "default": "always_require"}
  resolved per tool      : {"discontinue_order": "always_require", "place_order": "always_require", "read_chart": "never_require"}
  warnings at construct  : 0
  approval requests      : 1 (discontinue_order)
  rows before any answer : 0
  rows at end            : 1  {"action": "discontinue_order", "patient_id": "pt-123", "order_id": "order-1"}
  model turns            : 2
  final text             : 'Done. {"result": "ORDER DISCONTINUED order-1 for pt-123"}'
--- case=joined ---
agent-framework-core 1.23.0  case=joined  call=discontinue_order
  policy passed          : {"always_require_approval": "place_order,discontinue_order", "never_require_approval": ["read_chart"]}
  resolved per tool      : {"discontinue_order": "always_require", "place_order": "always_require", "read_chart": "never_require"}
  warnings at construct  : 0
  approval requests      : 1 (discontinue_order)
  rows before any answer : 0
  rows at end            : 0
  model turns            : 1
  final text             : ''
agent-framework-core 1.24.0  case=joined  call=discontinue_order
  policy passed          : {"always_require_approval": "place_order,discontinue_order", "never_require_approval": ["read_chart"]}
  resolved per tool      : {"discontinue_order": "never_require", "place_order": "never_require", "read_chart": "never_require"}
  warnings at construct  : 1
      FutureWarning: approval_mode sets `never_require_approval` without `default`. Tools and prompts named in neither list use "never_require" today, and this fallback may change in a future release. Set `default` to "never_require" to keep the current behavior or to "always_require" to require approval for them.
  approval requests      : 0
  rows before any answer : 1
  rows at end            : 1  {"action": "discontinue_order", "patient_id": "pt-123", "order_id": "order-1"}
  model turns            : 2
  final text             : 'Done. {"result": "ORDER DISCONTINUED order-1 for pt-123"}'
```

### `test_pydantic_ai_toolset_approval.py` (supporting check)

`FunctionToolset([...], requires_approval=True)` is pydantic-ai's way of saying every tool in the
set waits for a person. Two writes are registered: `place_order` as a plain function and
`discontinue_order` as a prebuilt `Tool(...)` instance, which is how a tool arrives from a shared
library. `FunctionModel` stands in for the model and calls both in one response.

| version | waiting for approval | ran before any approval |
|---|---|---|
| 2.65.0 | 1 (`place_order`) | **1** (`discontinue_order`) |
| 2.66.0 | 2 | 0 |

On 2.65.0 only tools added as functions consulted the toolset's flag; a `Tool` instance kept its
own `requires_approval=False` and ran. 2.66.0 (`pydantic_ai/toolsets/function.py`,
`FunctionToolset.add_tool`: `if self.requires_approval: tool.requires_approval = True`, #12378)
applies the flag to instances too. The run output is `DeferredToolRequests` on both versions, so
a caller that only checks the output type sees a pause either way; the record shows that on
2.65.0 one of the two writes had already happened.

### `build_models.py`

Regenerates `models.json` and prints the section 2 table: 17 models on 10,000 documents at 4,000
input and 500 output tokens, list prices read on 6 November from the pages named in each row,
Artificial Analysis Intelligence Index v5.0.1 scores (changelog 3 November; not comparable with
the v4.3.2 scores of Issues 01 to 08) and the Healthcare & Medical score where the homepage
comparison showed one. Three prices are unverified this week: Gemini 4 Carbon (no vendor price
page) and both Kimi rows (the vendor's price tables did not render to a text reader on 6 November).

```
model                               in/out/cached   AA  med   no cache  80% cached  verified
Claude Haiku 5.5             0.1/0.5/  0.01   36   37 $     6.50       $3.62  True
GPT-6 Luna                   0.1/0.5/  0.01   28    - $     6.50       $3.62  True
gpt-oss-120b on Nebius       0.15/0.6/   0.1    -    - $     9.00       $7.40  True
DeepSeek V4.1 Flash          0.3/1.2/ 0.006   33   41 $    18.00       $8.59  True
Mistral Large 4              0.7/2.1/  0.07   26    - $    38.50      $18.34  True
Gemini 3.8 Flash             0.75/3.75/ 0.075   31   38 $    48.75      $27.15  True
GPT-6.1 Terra                1/5/  0.05   51   45 $    65.00      $34.60  True
Grok 4.7                     2/6/   0.5   35   47 $   110.00      $62.00  True
Kimi K3.1 Pro                2/10/   0.2   46   52 $   130.00      $72.40  False
Claude Sonnet 5.5            2/10/   0.1   55   54 $   130.00      $69.20  True
GPT-6.1 Sol                  2/10/   0.1   55   52 $   130.00      $69.20  True
Gemini 4 Argon               2/10/   0.1   50    - $   130.00      $69.20  True
Kimi K3                      3/15/   0.3    -    - $   195.00     $108.60  False
Claude Opus 5.5              4/20/   0.2   59   58 $   260.00     $138.40  True
Gemini 4 Carbon              4/20/   n/a   60    - $   260.00         n/a  False
GPT-6 Astra                  10/50/     1   57   54 $   650.00     $362.00  True
Claude Fable 5.1             10/50/  0.25   50   51 $   650.00     $338.00  True
```

## Files

- `test_af_mcp_unlisted_tool.py`: the mechanism. `LAB_CASE` selects `listed`, `unlisted`,
  `default`, `approved` or `joined`.
- `pharmacy_server.py`: the local MCP server the mechanism starts over stdio.
- `test_pydantic_ai_toolset_approval.py`: the supporting check.
- `build_models.py`, `models.json`: the model table and its sources.
- `requirements.txt`, `requirements-previous.txt`: the two pin sets.
- `run_all.sh`: builds both environments and runs everything.

Synthetic data only. Nothing here talks to a FHIR server or to any model API. The scripted model
says what it was scripted to say; "the model called discontinue_order" means the stand-in emitted
the function call it was written to emit, not that any particular model did.
