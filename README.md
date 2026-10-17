# AI Velocity Technology Update

A weekly technical brief for people building healthcare AI systems, by
[Vijay Zharotia](https://www.linkedin.com/in/vijayzharotia/). Every issue reads the
source of the agent frameworks we build on, runs at least one mechanism, and
reports what changed for anyone putting an agent into a clinical or payer
workflow. The code behind each finding is in this repository.


## How an issue is laid out

Each issue has two layers.

**`summary.html`** and **`architect-intelligence-NN.pdf`** are the two-minute scan: the week in
one line, five changes tagged executed, docs or unverified, WHAT CHANGED and WHAT TO
CHANGE per card, and the mechanism of the week with its observed numbers. The PDF is
the same content as a square carousel for LinkedIn. Both are generated from one manifest
in `tools/architect-intelligence/`.

**`details.html`** is the long-form technical edition it links to:
framework and API changes read from source with runnable code, a model table
priced on one real workload, papers with an implementation note each, what the
architects shipped, and the lab.

Claims carry a tag. **Executed** means the mechanism was run in a sandbox and the
quoted output is what came back. **Docs** means the documentation or source was
read but not run. **Unverified** means it could not be confirmed from a primary
source. An asterisk on a number means the vendor reported it; unasterisked
numbers come from a named independent measurement.

## Issues

| Issue | Week ending | Subject |
|---|---|---|
| [01](issue-01/summary.html) | 5 September 2026 | The clinician's signature belongs in the tool protocol, not the prompt |
| [02](issue-02/summary.html) | 11 September 2026 | Prior authorisation: let the model read the chart, let a solver decide |

## Running a lab

Every issue ships the code behind its findings, with pinned versions. Synthetic
data only; no model key is needed for any script.

```bash
cd issue-02/lab && bash run_all.sh
```

That builds a clean virtual environment, installs `requirements.txt`, and runs
every script. Each lab's `README.md` records the output observed when it was
written, so you can tell immediately whether your run matches.

## Corrections

Errors get corrected in the next issue with a note saying what changed. In
Issue 01 a list of risk-adjustment category codes was wrong by one entry; the
rerun caught it and the issue text was corrected. Quiet edits are worse.

## Licence

Code is [MIT](LICENSE): everything under `issue-NN/lab/` and any helper scripts.
The writing is [CC BY 4.0](LICENSE-CONTENT): the issues, `start-here.html` and
these README files. Benchmark figures, quoted release notes and paper results
belong to their original publishers and are cited in each issue.
`assets/mermaid.min.js` is Mermaid 12.0.0, vendored under its own MIT licence.

## Notes

The diagrams render from `assets/mermaid.min.js`, kept in the repository so the
pages work offline and without a CDN. Research and code execution are done with
Claude; the judgement, the corrections and the positions are mine, and are mine
alone rather than my employer's.
