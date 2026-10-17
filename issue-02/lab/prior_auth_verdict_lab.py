"""AI Velocity Weekly 02, lab 5.3: prior authorisation as a solver problem.

Derived from VERDICT (arXiv 2609.03366, Stanford/UCLA/Emory/Mayo): let the
LLM compile facts and policy into constraints, and let a solver make the
decision so the same policy is applied the same way to every request, and
so every determination comes with the "pivotal conditions" that would
flip it. Here the policy is hand-written for one payer rule (MRI brain
with contrast, CPT 70553) and the "extraction" step is a stub returning
facts a model would pull from the clinical attachment. Swap the stub for
a typed Pydantic AI agent when you have a model key.

CMS-0057-F framing: the payer must return a decision with a specific
reason for denial. The pivotal-condition list is that reason, computed
rather than written.

Run:  pip install z3-solver
      python prior_auth_verdict_lab.py
Synthetic data only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from z3 import And, Bool, BoolRef, Implies, Not, Or, Solver, sat

# 1. Facts an extraction model would return from the attached note, each with
#    the verbatim span that supports it (the span is the audit trail).
FACTS = {
    "new_focal_neuro_deficit": ("Right-sided weakness of new onset, 2 days.", True),
    "headache_with_red_flag": ("Worst headache of life, thunderclap onset.", False),
    "ct_head_nondiagnostic": ("CT head 09/03: no acute finding.", True),
    "known_intracranial_tumour": ("", False),
    "mri_brain_within_90_days": ("No prior MRI in record.", False),
    "contrast_contraindicated": ("eGFR 71; no contrast allergy documented.", False),
}


@dataclass
class Policy:
    """Payer medical-necessity rule for CPT 70553, written as propositional logic."""

    def vars(self) -> dict[str, BoolRef]:
        return {k: Bool(k) for k in FACTS}

    def approve(self, v: dict[str, BoolRef]) -> BoolRef:
        indication = Or(
            v["new_focal_neuro_deficit"],
            And(v["headache_with_red_flag"], v["ct_head_nondiagnostic"]),
            v["known_intracranial_tumour"],
        )
        exclusion = Or(v["mri_brain_within_90_days"], v["contrast_contraindicated"])
        return And(indication, Not(exclusion))


def decide(policy: Policy, facts: dict[str, bool]) -> tuple[bool, list[str]]:
    v = policy.vars()
    s = Solver()
    for k, val in facts.items():
        s.add(v[k] == val)
    s.add(policy.approve(v))
    approved = s.check() == sat
    # Pivotal conditions: single facts whose flip changes the outcome.
    pivotal = []
    for k in facts:
        flipped = dict(facts, **{k: not facts[k]})
        s2 = Solver()
        for kk, val in flipped.items():
            s2.add(v[kk] == val)
        s2.add(policy.approve(v))
        if (s2.check() == sat) != approved:
            pivotal.append(k)
    return approved, pivotal


def main() -> None:
    policy = Policy()
    facts = {k: val for k, (_, val) in FACTS.items()}
    approved, pivotal = decide(policy, facts)
    print("Decision:", "APPROVED" if approved else "DENIED")
    print("Pivotal conditions (flipping any one changes the decision):")
    for k in pivotal:
        span = FACTS[k][0] or "(no supporting text found)"
        print(f"  {k} = {facts[k]}   evidence: {span}")

    # 2. Self-faithfulness check from the paper: changing a pivotal condition
    #    must change the decision; changing a non-pivotal one must not.
    for k in facts:
        alt, _ = decide(policy, dict(facts, **{k: not facts[k]}))
        expect_change = k in pivotal
        assert (alt != approved) == expect_change, k
    print("Self-faithfulness check passed for", len(facts), "facts")

    # 3. A ClaimResponse-shaped stub with a computed reason. Field names below
    #    are illustrative; validate against the Da Vinci PAS IG before use.
    stub = {
        "resourceType": "ClaimResponse",
        "outcome": "complete",
        "item": [{"itemSequence": 1, "adjudication": [{
            "category": {"coding": [{"code": "approved" if approved else "denied"}]},
            "reason": {"text": "Pivotal conditions: " + ", ".join(pivotal)}}]}],
    }
    print(json.dumps(stub, indent=1))

    # 4. Now the case that matters for appeals: same note, but the MRI was done
    #    80 days ago. The reason changes, and it is computed, not drafted.
    facts2 = dict(facts, mri_brain_within_90_days=True)
    approved2, pivotal2 = decide(policy, facts2)
    print("\nWith a prior MRI 80 days ago ->", "APPROVED" if approved2 else "DENIED", "; pivotal:", pivotal2)


if __name__ == "__main__":
    main()
