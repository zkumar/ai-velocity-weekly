"""Series ledger: a sentence, a headline or a mechanism appears once in the SERIES, not once per issue.

Called by build_issue.py after the manifest loads. Compares the new manifest's framing lines
(one-line, pillars, section titles and signals, card headlines, mechanism, constraints) with every
earlier manifest in issues/. Fails the build on a repeat unless LEDGER=warn is set.

    python ledger.py issues/issue-02.yaml        # standalone report
"""
import glob, os, re, sys
import yaml

STOP = set("the a an and or of to in on for is are was were be it its this that with what who when which your you one "
           "two three four each every not no now still into from by at as than then week this whose can do does".split())
JACCARD = 0.45      # word-set overlap that counts as the same sentence
NGRAM = 6           # a shared run of this many words also counts


def words(s):
    return [w for w in re.findall(r"[a-z0-9][a-z0-9\-\.']*", s.lower()) if w not in STOP]


def similar(a, b):
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return False, 0.0
    j = len(set(wa) & set(wb)) / len(set(wa) | set(wb))
    ga = {tuple(wa[i:i + NGRAM]) for i in range(len(wa) - NGRAM + 1)}
    gb = {tuple(wb[i:i + NGRAM]) for i in range(len(wb) - NGRAM + 1)}
    return (j >= JACCARD or bool(ga & gb)), j


def framing_lines(m):
    """(slot, text) pairs that must be unique across the series."""
    out = [("one_line", m["one_line"])]
    for p in m.get("pillars", []):
        out.append(("pillar", p["text"]))
    for s in m.get("sections", []):
        out.append((f"s{s['num']} title", s["title"]))
        if s.get("signal"):
            out.append((f"s{s['num']} signal", s["signal"]))
        for c in s.get("cards", []):
            out.append((f"s{s['num']} headline", c["headline"]))
    mm = m["mechanism"]
    out.append(("mechanism title", mm["title"]))
    for c in m["constraints"]["items"]:
        out.append(("constraint", c["headline"]))
    if m.get("shipped", {}).get("signal"):
        out.append(("s09 signal", m["shipped"]["signal"]))
    if m["constraints"].get("signal"):
        out.append(("s10 signal", m["constraints"]["signal"]))
    return out


def framework(m):
    """First token of the mechanism kicker: LANGCHAIN, AGENT FRAMEWORK, MCP ..."""
    return re.split(r"\s+\d|·", m["mechanism"]["kicker"].upper())[0].strip()


def check(src):
    here = os.path.dirname(os.path.abspath(src))
    new = yaml.safe_load(open(src, encoding="utf-8"))
    priors = []
    for f in sorted(glob.glob(os.path.join(here, "issue-*.yaml"))):
        m = yaml.safe_load(open(f, encoding="utf-8"))
        if m["issue"] < new["issue"]:
            priors.append(m)
    hits = []
    for pm in priors:
        pn = f"{pm['issue']:02d}"
        plines = framing_lines(pm)
        for slot, text in framing_lines(new):
            for pslot, ptext in plines:
                ok, j = similar(text, ptext)
                if ok:
                    hits.append(f"{slot} repeats issue {pn} {pslot} (overlap {j:.2f}):\n    new: {text[:110]}\n    old: {ptext[:110]}")
        if pm["issue"] == new["issue"] - 1 and framework(pm) == framework(new):
            hits.append(f"mechanism framework {framework(new)!r} was also last week's mechanism (issue {pn})")
        if [p.get("label") or list(p.values())[0] for p in pm.get("pillars", [])] == \
           [p.get("label") or list(p.values())[0] for p in new.get("pillars", [])]:
            hits.append(f"pillar labels identical to issue {pn}; rotate them with the week's story")
    return priors, hits


if __name__ == "__main__":
    priors, hits = check(sys.argv[1])
    print(f"ledger: {len(priors)} prior issue(s), {len(hits)} repeat(s)")
    for h in hits:
        print("  -", h)
    sys.exit(1 if hits else 0)
