#!/usr/bin/env python3
"""Architect Intelligence: one manifest, three outputs.

    python build_issue.py issues/issue-02.yaml out/

Writes:
    out/architect-intelligence-NN.pptx   square LinkedIn carousel (via build_pptx.js)
    out/architect-intelligence-NN.pdf    same, for the LinkedIn document post (LibreOffice)
    out/architect-intelligence-NN.html   web page for the repo / GitHub Pages
    out/architect-intelligence-NN.md     newsletter text for the LinkedIn editor
    out/issue-NN.json                    the manifest as JSON (input to build_pptx.js)
"""
import html, json, os, subprocess, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
M = yaml.safe_load(open(src, encoding="utf-8"))
NN = f"{M['issue']:02d}"

# series ledger: framing lines and the mechanism must not repeat an earlier issue
sys.path.insert(0, HERE)
import ledger
_priors, _hits = ledger.check(src)
print(f"ledger: {len(_priors)} prior issue(s), {len(_hits)} repeat(s)")
for _h in _hits:
    print("  -", _h)
if _hits and os.environ.get("LEDGER") != "warn":
    sys.exit("ledger: fix the repeats above, or run with LEDGER=warn to build anyway")
SITE = M["site"].rstrip("/")
LINKS = {"longform": M["longform"], "mytake": M["mytake"], "lab": M["lab"], "radar": "index.html"}
def url(key): return f"{SITE}/{LINKS.get(key, key)}"
def rel(key): return "../" + LINKS.get(key, key)   # from issue-NN/ up to repo root
E = html.escape

jpath = os.path.join(outdir, f"issue-{NN}.json")
json.dump(M, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)

# ------------------------------------------------------------------ HTML
CSS = """
:root{--ink:#1B2432;--ground:#F7F5F0;--panel:#FFFFFF;--muted:#66707F;--line:#DDD8CC;--accent:#0F6E6B;--soft:#E3EFEE;
--ok:#2E7D4F;--docs:#1D5FA8;--un:#A0522D}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ink:#E6E8EC;--ground:#0F1419;--panel:#171D26;--muted:#98A2B3;--line:#2A3340;--accent:#4FB3AE;--soft:#15302F;--ok:#6CC08B;--docs:#7FB3F0;--un:#E0946A}}
:root[data-theme="dark"]{--ink:#E6E8EC;--ground:#0F1419;--panel:#171D26;--muted:#98A2B3;--line:#2A3340;--accent:#4FB3AE;--soft:#15302F;--ok:#6CC08B;--docs:#7FB3F0;--un:#E0946A}
body{background:var(--ground);color:var(--ink);font-family:"IBM Plex Sans","Segoe UI",Helvetica,Arial,sans-serif;font-size:16px;line-height:1.55;margin:0}
.wrap{max-width:860px;margin:0 auto;padding:40px 24px 80px}
.mono{font-family:"IBM Plex Mono",Menlo,monospace}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:0 0 6px}
h1{font-family:"IBM Plex Serif",Georgia,serif;font-weight:600;font-size:36px;line-height:1.15;margin:0 0 8px;text-wrap:balance}
h2{font-family:"IBM Plex Serif",Georgia,serif;font-weight:600;font-size:26px;margin:56px 0 12px;padding-top:18px;border-top:1px solid var(--line)}
h3{font-size:18px;margin:0 0 6px}
p{margin:0 0 12px;max-width:70ch}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--soft)}
.stamp{font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--muted);margin-bottom:24px}
.thesis{border-left:3px solid var(--accent);padding:4px 0 4px 18px;margin:22px 0 10px}.thesis p{font-size:18px;font-weight:500}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0 8px}
.stats div{border-top:1px solid var(--line);padding-top:10px}.stats b{display:block;font-size:26px;font-family:"IBM Plex Mono",monospace}
.stats span{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.pillars{display:grid;gap:14px;margin:16px 0}@media(min-width:700px){.pillars{grid-template-columns:1fr 1fr 1fr}}
.pillars div{border-top:2px solid var(--accent);padding-top:10px}.pillars h4{margin:0 0 6px;font-family:"IBM Plex Mono",monospace;font-size:12px;letter-spacing:.1em}
.pillars p{font-size:15px}
.five{list-style:none;padding:0;margin:0}.five li{display:grid;grid-template-columns:2.2em 1fr;gap:10px;padding:12px 0;border-bottom:1px solid var(--line)}
.five .n{font-family:"IBM Plex Mono",monospace;font-size:22px;color:var(--accent)}.five .src{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.06em;color:var(--muted)}
.five .t{font-weight:600;margin:2px 0 4px}
.tag{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;border:1px solid currentColor;padding:1px 7px;border-radius:2px;margin-left:8px;vertical-align:middle}
.tag.EXECUTED{color:var(--ok)}.tag.DOCS{color:var(--docs)}.tag.UNVERIFIED{color:var(--un)}
.card{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);padding:16px 20px;margin:14px 0}
.card .k{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.08em;color:var(--accent)}
.cols{display:grid;gap:16px;margin-top:10px}@media(min-width:700px){.cols{grid-template-columns:1fr 1fr}}
.cols h5{margin:0 0 4px;font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.cols p{font-size:14.5px;margin:0}
.signal{background:var(--soft);padding:12px 16px;margin:16px 0 0;font-size:15px}.signal b{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.1em;color:var(--accent);margin-right:10px}
.mstats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0}.mstats div{border:1px solid var(--line);padding:12px}
.mstats b{display:block;font-size:26px;font-family:"IBM Plex Mono",monospace;color:var(--accent)}.mstats span{font-family:"IBM Plex Mono",monospace;font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.shipped{list-style:none;padding:0;margin:0}.shipped li{display:grid;grid-template-columns:7em 1fr;gap:12px;padding:10px 0;border-bottom:1px solid var(--line);font-size:15px}
.shipped .w{font-family:"IBM Plex Mono",monospace;font-size:12px;letter-spacing:.08em;color:var(--accent)}
.note{font-size:13.5px;color:var(--muted)}.links{font-size:13.5px}
"""
def card_html(it, acc_var="var(--accent)"):
    tag = f'<span class="tag {it["tag"]}">{E(it["tag"])}</span>' if it.get("tag") else ""
    cols = ""
    if it.get("changed") and it.get("change"):
        cols = f'<div class="cols"><div><h5>What changed</h5><p>{E(it["changed"])}</p></div><div><h5>What to change</h5><p>{E(it["change"])}</p></div></div>'
    elif it.get("move"):
        cols = f'<div class="cols"><div><h5>Move</h5><p>{E(it["move"])}</p></div></div>'
    lk = f'<p class="links"><a href="{rel(it["link"])}">Read the mechanism</a></p>' if it.get("link") else ""
    return f'<div class="card"><div class="k">{E(it["kicker"])}{tag}</div><h3>{E(it["headline"])}</h3><p>{E(it["body"])}</p>{cols}{lk}</div>'

H = []
H.append(f'<title>Architect Intelligence {NN}</title>\n<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@500;600&display=swap" rel="stylesheet">\n<style>{CSS}</style>\n<div class="wrap">')
H.append(f'<p class="eyebrow">{E(M["series"])} · {E(M["strapline"])}</p><h1>{E(M["theme"]["title"].title())}</h1><div class="stamp">Issue {NN} · {E(M["week_label"].title())} · {E(M["author"])}</div>')
H.append(f'<div class="thesis"><p>{E(M["one_line"])}</p></div><p>{E(M["theme"]["text"])}</p>')
H.append('<div class="stats">' + "".join(f'<div><b>{E(s["n"])}</b><span>{E(s["label"])}</span></div>' for s in M["stats"]) + '</div>')
H.append(f'<p class="links">Two minutes here. Ten minutes in <a href="{rel("mytake")}">My Take</a>. The full mechanism, code and sources in the <a href="{rel("longform")}">long-form edition</a>, and the <a href="{rel("lab")}">lab</a> runs with no API key.</p>')
H.append('<h2>The week in one line</h2><div class="pillars">' + "".join(f'<div><h4>{E(p["name"])}</h4><p>{E(p["text"])}</p></div>' for p in M["pillars"]) + '</div>')
H.append('<h2>Five changes, one home each</h2><p class="note">Each fact appears once on this page. This list says where.</p><ol class="five">' + "".join(
    f'<li><span class="n">{i+1:02d}</span><div><div class="src">{E(f["source"])}<span class="tag {f["tag"]}">{E(f["tag"])}</span></div><div class="t"><a href="#s{f["where"]}">{E(f["label"])}</a></div></div></li>' for i, f in enumerate(M["five"])) + '</ol>')
for sec in M["sections"]:
    H.append(f'<p class="eyebrow" id="s{sec["num"]}" style="margin-top:48px">{E(sec["num"])} · {E(sec["label"])}</p><h2 style="margin-top:0;border:0;padding:0">{E(sec["title"])}</h2><p>{E(sec["intro"])}</p>')
    H.extend(card_html(it) for it in sec["items"])
    H.append(f'<div class="signal"><b>ARCHITECT SIGNAL</b>{E(sec["signal"])}</div>')
m = M["mechanism"]
H.append(f'<p class="eyebrow" id="s{m["num"]}" style="margin-top:48px">{E(m["num"])} · {E(m["label"])}</p><h2 style="margin-top:0;border:0;padding:0">{E(m["title"])}</h2><div class="card"><div class="k">{E(m["kicker"])}<span class="tag EXECUTED">EXECUTED</span></div><p>{E(m["body"])}</p><div class="mstats">' + "".join(f'<div><b>{E(s["n"])}</b><span>{E(s["label"])}</span></div>' for s in m["stats"]) + f'</div><div class="cols"><div><h5>What changed</h5><p>{E(m["changed"])}</p></div><div><h5>Move</h5><p>{E(m["move"])}</p></div></div><p class="links"><a href="{rel(m["link"])}">Open the lab package</a></p></div><div class="signal"><b>ARCHITECT SIGNAL</b>{E(m["signal"])}</div>')
sh = M["shipped"]
H.append(f'<p class="eyebrow" style="margin-top:48px">{E(sh["num"])} · {E(sh["label"])}</p><h2 style="margin-top:0;border:0;padding:0">{E(sh["title"])}</h2><ul class="shipped">' + "".join(f'<li><span class="w">{E(i["who"])}</span><span>{E(i["text"])}</span></li>' for i in sh["items"]) + f'</ul><p class="note">{E(sh["quiet"])}</p><div class="signal"><b>ARCHITECT SIGNAL</b>{E(sh["signal"])}</div>')
c = M["constraints"]
H.append(f'<p class="eyebrow" id="s{c["num"]}" style="margin-top:48px">{E(c["num"])} · {E(c["label"])}</p><h2 style="margin-top:0;border:0;padding:0">{E(c["title"])}</h2>')
H.extend(card_html(it) for it in c["items"])
H.append(f'<p class="note">{E(c["radar"]["text"])} <a href="{rel(c["radar"]["link"])}">Open the Radar</a>.</p><div class="signal"><b>ARCHITECT SIGNAL</b>{E(c["signal"])}</div>')
H.append(f'<p class="note" style="margin-top:40px">{E(M["close"]["text"])} Source and every prior issue: <a href="{M["repo"]}">{E(M["repo"].replace("https://",""))}</a>.</p></div>')
core = "\n".join(H)
wrapped = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>\n' + core + '\n</body></html>\n'
open(os.path.join(outdir, f"architect-intelligence-{NN}.html"), "w", encoding="utf-8").write(wrapped)
open(os.path.join(outdir, f"architect-intelligence-{NN}.artifact.html"), "w", encoding="utf-8").write(core)  # no wrapper, for Artifact publish

# ------------------------------------------------------------------ Newsletter text
T = []
T.append(f"# Architect Intelligence {NN}: {M['theme']['title'].title()}\n")
T.append(f"{M['week_label'].title()} · {M['author']}\n")
T.append(f"**{M['one_line']}**\n")
T.append(M["theme"]["text"] + "\n")
T.append("This week: " + ", ".join(f"{s['n']} {s['label'].lower()}" for s in M["stats"]) + ".\n")
T.append("## Five changes, one home each\n\nEach fact appears once below. This list says where.\n")
for i, f in enumerate(M["five"], 1):
    T.append(f"{i}. **{f['label']}** ({f['source'].title()}, {f['tag'].lower()}), section {f['where']}")
T.append("")
for sec in M["sections"]:
    T.append(f"## {sec['title']}\n\n{sec['intro']}\n")
    for it in sec["items"]:
        T.append(f"### {it['headline']}\n\n*{it['kicker'].title()}*" + (f" · {it['tag'].lower()}" if it.get("tag") else "") + f"\n\n{it['body']}\n")
        if it.get("changed"): T.append(f"**What changed.** {it['changed']}\n\n**What to change.** {it['change']}\n")
        elif it.get("move"): T.append(f"**Move.** {it['move']}\n")
        if it.get("link"): T.append(f"[Read the mechanism]({url(it['link'])})\n")
    T.append(f"> **Architect signal.** {sec['signal']}\n")
T.append(f"## Mechanism of the week: {m['title']}\n\n*{m['kicker'].title()}*\n\n{m['body']}\n\n" + " · ".join(f"**{s['n']}** {s['label'].lower()}" for s in m["stats"]) + f"\n\n**What changed.** {m['changed']}\n\n**Move.** {m['move']}\n\n[Open the lab package]({url(m['link'])})\n\n> **Architect signal.** {m['signal']}\n")
T.append("## What the architects shipped\n")
for i in sh["items"]: T.append(f"- **{i['who'].title()}.** {i['text']}")
T.append(f"\n{sh['quiet']}\n\n> **Architect signal.** {sh['signal']}\n")
T.append(f"## {c['title']}\n")
for it in c["items"]: T.append(f"### {it['headline']}\n\n*{it['kicker'].title()}*\n\n{it['body']}\n\n**Move.** {it['move']}\n")
T.append(f"{c['radar']['text']} [Open the Radar]({url(c['radar']['link'])})\n\n> **Architect signal.** {c['signal']}\n")
T.append(f"---\n\n{M['close']['text']} Everything is at {M['repo']} .\n")
open(os.path.join(outdir, f"architect-intelligence-{NN}.md"), "w", encoding="utf-8").write("\n".join(T))

# ------------------------------------------------------------------ PPTX + PDF
pptx = os.path.join(outdir, f"architect-intelligence-{NN}.pptx")
subprocess.run(["node", os.path.join(HERE, "build_pptx.js"), jpath, pptx], check=True)
soffice = "/mnt/skills/public/pptx/scripts/office/soffice.py"
if os.path.exists(soffice):
    subprocess.run(["python3", soffice, "--headless", "--convert-to", "pdf", "--outdir", outdir, pptx], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("done:", sorted(os.listdir(outdir)))
