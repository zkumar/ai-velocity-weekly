#!/usr/bin/env python3
"""Build a clean, GitHub-ready copy of the repo in ./publish.

Per issue-NN folder it produces:
  architect-intelligence-NN.pdf   newest .pptx in the folder, converted with LibreOffice
  summary.html                    from architect-intelligence-NN.html
  details.html                    from ai-velocity-weekly-NN.html
  *.md                            copied as is
  lab/                            copied as is (minus .venv, __pycache__, .DS_Store)

Top-level files (README, licences, index, start-here, assets, tools) are copied and
links to the renamed pages are rewritten. Source files are never modified.

Usage:  python3 tools/publish/publish.py [--out publish] [--skip-pdf]
"""
import argparse, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = "https://github.com/zkumar/ai-velocity-weekly"
SITE = "https://zkumar.github.io/ai-velocity-weekly"
OLD_REPO = "https://github.com/zkumar/AI-Velocity-Technology-Update-"
OLD_SITE = "https://zkumar.github.io/AI-Velocity-Technology-Update-"
IGNORE = shutil.ignore_patterns(".venv", "__pycache__", "*.pyc", ".DS_Store", "node_modules", "~$*", ".git")
TOP_FILES = ["README.md", "LICENSE", "LICENSE-CONTENT", ".nojekyll", ".gitignore", "index.html", "start-here.html"]
TOP_DIRS = ["assets", "tools"]

def find_soffice():
    for c in ("soffice", "libreoffice",
              "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        p = shutil.which(c) or (c if os.path.exists(c) else None)
        if p:
            return p
    return None

def latest_pptx(folder: Path):
    files = [p for p in folder.glob("*.pptx") if not p.name.startswith("~$")]
    return max(files, key=lambda p: p.stat().st_mtime) if files else None

def patch_pptx(src: Path, dst: Path):
    """Copy the deck, replacing the old repo URL in slide text and hyperlinks."""
    try:
        from pptx import Presentation
    except ImportError:
        print("WARN python-pptx not installed (pip3 install python-pptx); PDF keeps the old repo URL")
        shutil.copyfile(src, dst); return
    prs = Presentation(str(src))
    old_short, new_short = OLD_REPO.split("//")[1], REPO.split("//")[1]
    for slide in prs.slides:
        for sh in slide.shapes:
            if not sh.has_text_frame: continue
            for para in sh.text_frame.paragraphs:
                for r in para.runs:
                    if old_short in r.text:
                        r.text = r.text.replace(old_short, new_short)
                    if r.hyperlink.address and old_short in r.hyperlink.address:
                        r.hyperlink.address = r.hyperlink.address.replace(old_short, new_short)
    prs.save(str(dst))

def to_pdf(soffice, pptx: Path, dest: Path):
    with tempfile.TemporaryDirectory() as tmp:
        patched = Path(tmp) / pptx.name
        patch_pptx(pptx, patched)
        pptx = patched
        profile = Path(tmp) / "profile"
        cmd = [soffice, f"-env:UserInstallation=file://{profile}", "--headless",
               "--convert-to", "pdf", "--outdir", tmp, str(pptx)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=300)
        out = Path(tmp) / (pptx.stem + ".pdf")
        if not out.exists():
            raise RuntimeError(f"LibreOffice produced no PDF for {pptx.name}")
        shutil.copyfile(out, dest)

REWRITES = [
    (re.compile(r"ai-velocity-weekly-\d{2}\.html"), "details.html"),
    (re.compile(r"architect-intelligence-\d{2}\.html"), "summary.html"),
]
MYTAKE = [  # the hand-built mytakeNN.html pages are not published; remove every reference
    (re.compile(r'Ten minutes in <a href="[^"]*mytake\d\d\.html">My Take</a>\. '), ""),
    (re.compile(r" The architect&#x27;s position on this week&#x27;s decision is in My Take\."), ""),
    (re.compile(r"The architect's edition, <span class=\"mono\">mytakeNN\.html</span>, .*?the takeaway\. ", re.S), ""),
    (re.compile(r"\*\*`mytakeNN\.html`\*\*.*?takeaway\.\n\n", re.S), ""),
    (re.compile(r"issue-(\d\d)/mytake\d\d\.html"), r"issue-\1/summary.html"),
    (re.compile(r"mytakeNN\.html,\nai-velocity-weekly-NN\.html,"), "summary.html,\ndetails.html,"),
    (re.compile(r"Three layers\."), "Two layers."),
    (re.compile(r"three layers\."), "two layers."),
    (re.compile(r'<span class="mono">architect-intelligence-NN</span>'), '<span class="mono">summary.html</span>'),
    (re.compile(r'<span class="mono">ai-velocity-weekly-NN\.html</span>'), '<span class="mono">details.html</span>'),
    (re.compile(r"\*\*`architect-intelligence-NN\.html`\*\* and \*\*`\.pdf`\*\*"), "**`summary.html`** and **`architect-intelligence-NN.pdf`**"),
    (re.compile(r"\*\*`ai-velocity-weekly-NN\.html`\*\*"), "**`details.html`**"),
]
CLAUDE = [  # no claude.ai links in the public repo
    (re.compile(r' ?Companion tracker: <a href="https://claude\.ai/[^"]*">AI Velocity Radar</a>\.'), ""),
    (re.compile(r'\s*<li><a href="https://claude\.ai/[^"]*">AI Velocity Radar</a>.*?</li>', re.S), ""),
    (re.compile(r'<a href="https://claude\.ai/code/artifact/39c39d20-3764-4a11-ab1b-8f0a456e2b96">'), '<a href="../issue-01/details.html">'),
    (re.compile(r'<a href="https://claude\.ai/code/artifact/b0c4dd42-5843-474f-9993-5339c0281bf1">'), '<a href="../start-here.html">'),
    (re.compile(r'https://claude\.ai/code/artifact/39c39d20-3764-4a11-ab1b-8f0a456e2b96'), SITE + "/issue-01/details.html"),
    (re.compile(r'https://claude\.ai/code/artifact/35160807-b786-4045-ad18-0655d3b6356c'), SITE + "/issue-02/details.html"),
    (re.compile(r'<a href="https://claude\.ai/[^"]*">(.*?)</a>', re.S), r"\1"),  # any other: keep text, drop link
]
REPO_LINKS = [
    (re.compile(re.escape(OLD_SITE)), SITE),
    (re.compile(re.escape(OLD_REPO)), REPO),
    (re.compile(re.escape(SITE) + r"/(issue-\d\d)/lab/?"), REPO + r"/tree/main/\1/lab"),
    (re.compile(r"AI-Velocity-Technology-Update-"), "ai-velocity-weekly"),  # link text, clone dir names
]
def rewrite(text, issue=None):
    for rx, rep in REWRITES + MYTAKE + CLAUDE + REPO_LINKS:
        text = rx.sub(rep, text)
    # relative links to a lab/ folder: Pages has no index there, so point at the GitHub folder view
    def lab(m):
        n = m.group(2) or issue
        return f'href="{REPO}/tree/main/issue-{n}/lab"' if n else m.group(0)
    text = re.sub(r'href="((?:\.\./)?(?:issue-(\d\d)/)?)lab/?"', lab, text)
    return text

def copy_text(src: Path, dst: Path, do_rewrite=True, issue=None):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if do_rewrite:
        dst.write_text(rewrite(src.read_text(encoding="utf-8"), issue), encoding="utf-8")
    else:
        shutil.copyfile(src, dst)

def check_links(out: Path):
    bad = []
    rx = re.compile(r'(?:href|src)="([^"#?]+)"')
    for html in out.rglob("*.html"):
        for ref in rx.findall(html.read_text(encoding="utf-8", errors="ignore")):
            if re.match(r"^(https?:|mailto:|data:|//|javascript:)", ref):
                continue
            target = (html.parent / ref).resolve()
            if not target.exists() or (target.is_dir() and not (target / "index.html").exists()):
                bad.append((html.relative_to(out), ref))
    for f in out.rglob("*"):
        if f.suffix in (".html", ".md") and "tools" not in f.relative_to(out).parts[:1]:
            t = f.read_text(encoding="utf-8", errors="ignore")
            for needle in ("claude.ai/", OLD_REPO.split("//")[1], OLD_SITE.split("//")[1]):
                if needle in t:
                    bad.append((f.relative_to(out), needle))
    return bad

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="publish")
    ap.add_argument("--skip-pdf", action="store_true")
    a = ap.parse_args()
    out = (ROOT / a.out).resolve()
    if out.exists():  # clear the previous build but keep publish/.git
        for child in out.iterdir():
            if child.name == ".git": continue
            try:
                shutil.rmtree(child) if child.is_dir() and not child.is_symlink() else child.unlink()
            except OSError as e:
                print(f"WARN could not remove {child}: {e}")
    out.mkdir(parents=True, exist_ok=True)

    soffice = None if a.skip_pdf else find_soffice()
    if not a.skip_pdf and not soffice:
        sys.exit("LibreOffice not found. Install it (brew install --cask libreoffice) or use --skip-pdf.")

    for f in TOP_FILES:
        if (ROOT / f).exists():
            copy_text(ROOT / f, out / f, do_rewrite=f.endswith((".html", ".md")) or f == "LICENSE-CONTENT")
    for d in TOP_DIRS:
        if (ROOT / d).exists():
            shutil.copytree(ROOT / d, out / d, ignore=IGNORE, dirs_exist_ok=True)

    for folder in sorted(ROOT.glob("issue-[0-9][0-9]")):
        n = folder.name.split("-")[1]
        dst = out / folder.name
        dst.mkdir(parents=True, exist_ok=True)
        # HTML: summary + details
        for src_name, dst_name in ((f"architect-intelligence-{n}.html", "summary.html"),
                                   (f"ai-velocity-weekly-{n}.html", "details.html")):
            s = folder / src_name
            if s.exists():
                copy_text(s, dst / dst_name, issue=n)
            else:
                print(f"WARN {folder.name}: {src_name} missing")
        # Markdown as is
        for md in folder.glob("*.md"):
            copy_text(md, dst / md.name, issue=n)
        # Lab as is
        if (folder / "lab").is_dir():
            shutil.copytree(folder / "lab", dst / "lab", ignore=IGNORE, dirs_exist_ok=True)
            for md in (dst / "lab").rglob("*.md"):  # fix links only; code untouched
                md.write_text(rewrite(md.read_text(encoding="utf-8"), n), encoding="utf-8")
        # PDF from newest pptx
        p = latest_pptx(folder)
        if p is None:
            print(f"WARN {folder.name}: no .pptx found")
        elif a.skip_pdf:
            print(f"{folder.name}: would convert {p.name}")
        else:
            to_pdf(soffice, p, dst / f"architect-intelligence-{n}.pdf")
            print(f"{folder.name}: {p.name} -> architect-intelligence-{n}.pdf")

    bad = check_links(out)
    if bad:
        print(f"\n{len(bad)} dangling local link(s):")
        for page, ref in bad:
            print(f"  {page}: {ref}")
    print(f"\nDone: {out}")

if __name__ == "__main__":
    main()
