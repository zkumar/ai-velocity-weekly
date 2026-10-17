// Architect Intelligence: manifest JSON -> square LinkedIn carousel (.pptx)
// Usage: node build_pptx.js out/issue-02.json out/architect-intelligence-02.pptx
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const [,, inPath, outPath] = process.argv;
const M = JSON.parse(fs.readFileSync(inPath, "utf8"));

// ---------- palette (from the Velocity Intelligence deck) ----------
const C = {
  bg: "0D1117", bg2: "06090F", card: "1A2A3A", card2: "132030", line: "2B3A4E",
  text: "E2E8F0", body: "CBD5E1", muted: "94A3B8", dim: "64748B",
  blue: "0EA5E9", teal: "00B4A0", amber: "F59E0B", violet: "A78BFA", green: "34D399", rose: "FB7185",
};
const TAG = { EXECUTED: C.green, DOCS: C.blue, UNVERIFIED: C.amber };
const MONO = "Courier New", SANS = "Arial";
const S = 12.5;                 // slide is 12.5in square
const MX = 0.6;                 // side margin
const W = S - 2 * MX;           // content width
const NN = String(M.issue).padStart(2, "0");
const link = (key) => {
  const map = { longform: M.longform, mytake: M.mytake, lab: M.lab, radar: "index.html" };
  return M.site.replace(/\/$/, "") + "/" + (map[key] || key);
};

const pres = new pptxgen();
pres.defineLayout({ name: "SQ", width: S, height: S });
pres.layout = "SQ";
pres.author = M.author; pres.title = `${M.series} ${NN}`;

// ---------- helpers ----------
function base(slide) {
  slide.background = { color: C.bg };
}
function mono(slide, text, x, y, w, h, o = {}) {
  slide.addText(text, { x, y, w, h, fontFace: MONO, fontSize: o.size || 8.5, color: o.color || C.muted,
    charSpacing: o.spacing ?? 2, bold: !!o.bold, align: o.align || "left", valign: o.valign || "top",
    margin: 0, isTextBox: true, fit: "shrink" });
}
function sans(slide, text, x, y, w, h, o = {}) {
  slide.addText(text, { x, y, w, h, fontFace: SANS, fontSize: o.size || 10, color: o.color || C.body,
    bold: !!o.bold, align: o.align || "left", valign: o.valign || "top", margin: 0, isTextBox: true,
    lineSpacingMultiple: o.lh || 1.15, paraSpaceAfter: o.para || 0, fit: "shrink" });
}
function topbar(slide, num, label, accent) {
  mono(slide, `${M.series.replace(" INTELLIGENCE", "")} / ${M.strapline}`, MX, 0.42, W / 2, 0.25, { color: C.dim, size: 9 });
  mono(slide, `${num} · ${label}`, S / 2, 0.42, W / 2, 0.25, { color: accent, size: 9, align: "right", bold: true });
}
function header(slide, num, title, intro, accent) {
  sans(slide, [{ text: num + " ", options: { color: accent, bold: true, fontFace: SANS } },
               { text: title, options: { color: C.text, bold: true, fontFace: SANS } }],
       MX, 0.85, W, 0.65, { size: 27 });
  if (intro) sans(slide, intro, MX, 1.55, W, 0.6, { size: 13, color: C.muted });
}
function chip(slide, text, x, y, color) {
  const w = 0.16 + text.length * 0.075;
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h: 0.22, rectRadius: 0.03, line: { color, width: 0.75 }, fill: { color: C.bg } });
  mono(slide, text, x, y + 0.03, w, 0.18, { color, size: 7, align: "center", bold: true, spacing: 1 });
  return w;
}
function signalBar(slide, text, accent, y = S - 1.05) {
  slide.addShape(pres.ShapeType.rect, { x: MX, y, w: W, h: 0.62, fill: { color: C.card2 }, line: { color: C.line, width: 0.5 } });
  slide.addShape(pres.ShapeType.rect, { x: MX, y, w: 0.06, h: 0.62, fill: { color: accent }, line: { color: accent, width: 0 } });
  mono(slide, "ARCHITECT SIGNAL", MX + 0.25, y + 0.2, 1.9, 0.25, { color: accent, size: 9, bold: true, valign: "middle" });
  sans(slide, text, MX + 2.2, y + 0.06, W - 2.45, 0.52, { size: 12, color: C.body, valign: "middle" });
}
function footer(slide) {
  mono(slide, `${M.series} · ISSUE ${NN}`, MX, S - 0.34, W / 2, 0.2, { color: C.dim, size: 7 });
  mono(slide, M.site.replace("https://", ""), S / 2, S - 0.34, W / 2, 0.2, { color: C.dim, size: 7, align: "right" });
}
// A card with kicker/tag, headline, body, and two columns (WHAT CHANGED / WHAT TO CHANGE)
function card(slide, it, x, y, w, h, accent) {
  slide.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { color: C.card }, line: { color: C.line, width: 0.5 } });
  slide.addShape(pres.ShapeType.rect, { x, y, w: 0.07, h, fill: { color: accent }, line: { color: accent, width: 0 } });
  const ix = x + 0.32, iw = w - 0.55;
  mono(slide, it.kicker, ix, y + 0.18, iw - 1.4, 0.22, { color: accent, size: 9, bold: true });
  if (it.tag) chip(slide, it.tag, x + w - 0.25 - (0.16 + it.tag.length * 0.075), y + 0.13, TAG[it.tag] || C.muted);
  const twoCol = it.changed && it.change, tight = h < 3.3;
  // top-down layout: kicker, headline, body, then the columns take what is left
  const F = tight ? { hl: 15.5, body: 11, col: 10.5, hlH: 0.58, bodyH: 0.66 } : { hl: 19, body: 13, col: 12, hlH: 0.78, bodyH: 1.0 };
  const hlY = y + 0.46, bodyY = hlY + F.hlH + 0.04, cy = bodyY + F.bodyH + 0.12, colH = y + h - cy - 0.38;
  sans(slide, it.headline, ix, hlY, iw, F.hlH, { size: F.hl, bold: true, color: C.text, lh: 1.08 });
  sans(slide, it.body, ix, bodyY, iw, F.bodyH, { size: F.body, color: C.body, lh: 1.22 });
  if (twoCol) {
    const cw = (iw - 0.3) / 2;
    mono(slide, "WHAT CHANGED", ix, cy, cw, 0.22, { color: C.muted, size: 8.5 });
    sans(slide, it.changed, ix, cy + 0.26, cw, colH - 0.26, { size: F.col, color: C.body, lh: 1.2 });
    mono(slide, "WHAT TO CHANGE", ix + cw + 0.3, cy, cw, 0.22, { color: accent, size: 8.5 });
    sans(slide, it.change, ix + cw + 0.3, cy + 0.26, cw, colH - 0.26, { size: F.col, color: C.text, lh: 1.2 });
  } else if (it.move) {
    mono(slide, "MOVE", ix, cy + 0.05, 0.7, 0.22, { color: accent, size: 8.5 });
    sans(slide, it.move, ix + 0.8, cy, iw - 0.8, colH, { size: 12.5, color: C.text, lh: 1.22 });
  }
  if (it.link) {
    slide.addText("Read the mechanism", { x: x + w - 2.1, y: y + h - 0.32, w: 1.85, h: 0.22, fontFace: MONO, fontSize: 8,
      color: accent, align: "right", margin: 0, isTextBox: true, hyperlink: { url: link(it.link) } });
  }
}

// ---------- slide 1: cover ----------
{
  const s = pres.addSlide(); base(s);
  s.background = { color: C.bg2 };
  mono(s, M.series, MX, 0.5, W / 2, 0.25, { color: C.teal, size: 9, bold: true, spacing: 3 });
  mono(s, M.week_label, S / 2, 0.5, W / 2, 0.25, { color: C.muted, size: 9, align: "right", spacing: 2 });
  s.addShape(pres.ShapeType.line, { x: MX, y: 0.9, w: W, h: 0, line: { color: C.line, width: 0.75 } });
  mono(s, `${M.strapline} · ISSUE ${NN}`, MX, 1.9, W, 0.25, { color: C.muted, size: 9, spacing: 3 });
  sans(s, "Architect\nIntelligence", MX, 2.3, W, 2.4, { size: 54, bold: true, color: C.text, lh: 1.0 });
  s.addShape(pres.ShapeType.rect, { x: MX, y: 5.2, w: W, h: 2.0, fill: { color: C.card }, line: { color: C.line, width: 0.5 } });
  s.addShape(pres.ShapeType.rect, { x: MX, y: 5.2, w: 0.07, h: 2.0, fill: { color: C.teal }, line: { color: C.teal, width: 0 } });
  mono(s, M.theme.label, MX + 0.35, 5.45, W, 0.25, { color: C.muted, size: 8, spacing: 3 });
  sans(s, M.theme.title, MX + 0.35, 5.75, W - 0.7, 0.55, { size: 24, bold: true, color: C.teal });
  sans(s, M.theme.text, MX + 0.35, 6.35, W - 0.7, 0.75, { size: 13.5, color: C.body });
  const sw = W / M.stats.length;
  M.stats.forEach((st, i) => {
    const x = MX + i * sw;
    sans(s, st.n, x, 7.9, sw - 0.2, 0.7, { size: 30, bold: true, color: C.text });
    mono(s, st.label, x, 8.65, sw - 0.2, 0.5, { color: C.muted, size: 7.5, spacing: 2 });
  });
  s.addShape(pres.ShapeType.line, { x: MX, y: 9.7, w: W, h: 0, line: { color: C.line, width: 0.75 } });
  sans(s, M.author, MX, 9.95, W / 2, 0.35, { size: 13, bold: true, color: C.text });
  mono(s, M.author_line, MX, 10.3, W / 2, 0.25, { color: C.muted, size: 8, spacing: 2 });
  mono(s, "SWIPE  >>>", S / 2, 10.1, W / 2, 0.3, { color: C.teal, size: 10, bold: true, align: "right", spacing: 3 });
  sans(s, M.close.text, MX, 10.9, W, 0.9, { size: 11, color: C.dim });
}

// ---------- slide 2: the week in one line + pillars ----------
{
  const s = pres.addSlide(); base(s);
  topbar(s, "02", "THE TAKEAWAY", C.teal);
  header(s, "02", "The Week In One Line", null, C.teal);
  s.addShape(pres.ShapeType.rect, { x: MX, y: 1.6, w: W, h: 1.55, fill: { color: C.card }, line: { color: C.teal, width: 1 } });
  sans(s, M.one_line, MX + 0.3, 1.72, W - 0.6, 1.32, { size: 17, bold: true, color: C.text, lh: 1.22 });
  const pw = (W - 0.4) / 3;
  const cols = [C.blue, C.teal, C.violet];
  M.pillars.forEach((p, i) => {
    const x = MX + i * (pw + 0.2), y = 3.5, h = 3.3;
    s.addShape(pres.ShapeType.rect, { x, y, w: pw, h, fill: { color: C.card }, line: { color: C.line, width: 0.5 } });
    s.addShape(pres.ShapeType.rect, { x, y, w: pw, h: 0.06, fill: { color: cols[i] }, line: { color: cols[i], width: 0 } });
    mono(s, p.name, x + 0.25, y + 0.3, pw - 0.5, 0.25, { color: cols[i], size: 9, bold: true, spacing: 3 });
    sans(s, p.text, x + 0.25, y + 0.75, pw - 0.5, h - 1.0, { size: 14.5, color: C.body, lh: 1.32 });
  });
  sans(s, "Approval, state and audit are the three obligations an agent inherits the moment it acts on a patient record. Each week this deck reports where the frameworks moved them.", MX, 7.2, W, 0.95, { size: 12.5, color: C.muted });
  footer(s);
}

// ---------- slide 3: the index (short label, tag, and the slide that holds the fact) ----------
{
  const s = pres.addSlide(); base(s);
  topbar(s, "03", "WHERE TO LOOK", C.blue);
  header(s, "03", "Five Changes, One Home Each", "Each fact appears once in this deck. This page says where.", C.blue);
  const y0 = 2.35, rh = 1.5;
  M.five.forEach((f, i) => {
    const y = y0 + i * rh, col = TAG[f.tag] || C.muted;
    s.addShape(pres.ShapeType.rect, { x: MX, y, w: W, h: rh - 0.18, fill: { color: C.card }, line: { color: C.line, width: 0.5 } });
    s.addShape(pres.ShapeType.rect, { x: MX, y, w: 0.07, h: rh - 0.18, fill: { color: col }, line: { color: col, width: 0 } });
    sans(s, String(i + 1).padStart(2, "0"), MX + 0.3, y + 0.3, 0.8, 0.6, { size: 22, bold: true, color: col });
    mono(s, f.source, MX + 1.2, y + 0.24, W - 4.2, 0.22, { color: col, size: 9, bold: true });
    sans(s, f.label, MX + 1.2, y + 0.52, W - 4.2, 0.65, { size: 16, bold: true, color: C.text, lh: 1.12 });
    chip(s, f.tag, MX + W - 2.45 - (0.16 + f.tag.length * 0.075), y + 0.25, col);
    mono(s, "SLIDE", MX + W - 1.75, y + 0.28, 1.5, 0.2, { color: C.muted, size: 8, align: "right" });
    sans(s, f.where, MX + W - 1.75, y + 0.5, 1.5, 0.6, { size: 26, bold: true, color: col, align: "right" });
  });
  sans(s, "Tags: EXECUTED means I ran it and the numbers are observed output. DOCS means read from documentation or source. UNVERIFIED means not confirmed either way.", MX, y0 + 5 * rh + 0.1, W, 0.8, { size: 11, color: C.muted });
  footer(s);
}

// ---------- slides 4 to 7: sections ----------
M.sections.forEach((sec) => {
  const s = pres.addSlide(); base(s);
  const acc = sec.accent;
  topbar(s, sec.num, sec.label, acc);
  header(s, sec.num, sec.title, sec.intro, acc);
  const top = 2.25, bottom = S - 1.05 - 0.2;
  const n = sec.items.length, gap = 0.18;
  const h = (bottom - top - gap * (n - 1)) / n;
  sec.items.forEach((it, i) => card(s, it, MX, top + i * (h + gap), W, h, acc));
  signalBar(s, sec.signal, acc);
  footer(s);
});

// ---------- slide 8: mechanism of the week ----------
{
  const m = M.mechanism; const s = pres.addSlide(); base(s);
  topbar(s, m.num, m.label, C.amber);
  header(s, m.num, "Mechanism Of The Week", "One thing I ran, and what came back.", C.amber);
  const y = 2.3, h = 7.6;
  s.addShape(pres.ShapeType.rect, { x: MX, y, w: W, h, fill: { color: C.card }, line: { color: C.line, width: 0.5 } });
  s.addShape(pres.ShapeType.rect, { x: MX, y, w: 0.07, h, fill: { color: C.amber }, line: { color: C.amber, width: 0 } });
  chip(s, "EXECUTED", MX + 0.35, y + 0.3, TAG.EXECUTED);
  mono(s, m.kicker, MX + 1.6, y + 0.32, W - 2, 0.22, { color: C.amber, size: 9, bold: true });
  sans(s, m.title, MX + 0.35, y + 0.75, W - 0.7, 0.8, { size: 26, bold: true, color: C.text, lh: 1.05 });
  sans(s, m.body, MX + 0.35, y + 1.7, W - 0.7, 1.35, { size: 13.5, color: C.body, lh: 1.3 });
  const bw = (W - 0.7 - 0.3 * (m.stats.length - 1)) / m.stats.length;
  m.stats.forEach((st, i) => {
    const x = MX + 0.35 + i * (bw + 0.3), sy = y + 3.0;
    s.addShape(pres.ShapeType.rect, { x, y: sy, w: bw, h: 1.35, fill: { color: C.bg }, line: { color: C.line, width: 0.5 } });
    sans(s, st.n, x + 0.2, sy + 0.18, bw - 0.4, 0.65, { size: 28, bold: true, color: C.amber });
    mono(s, st.label, x + 0.2, sy + 0.9, bw - 0.4, 0.35, { color: C.muted, size: 8.5 });
  });
  mono(s, "WHAT CHANGED", MX + 0.35, y + 4.7, 1.6, 0.2, { color: C.muted, size: 8.5, bold: true });
  sans(s, m.changed, MX + 2.0, y + 4.66, W - 2.4, 0.7, { size: 13, color: C.body, lh: 1.3 });
  mono(s, "MOVE", MX + 0.35, y + 5.5, 1.6, 0.2, { color: C.amber, size: 8.5, bold: true });
  sans(s, m.move, MX + 2.0, y + 5.46, W - 2.4, 1.5, { size: 13.5, color: C.text, lh: 1.3 });
  s.addText("Open the lab package", { x: MX + 0.35, y: y + h - 0.5, w: 3, h: 0.25, fontFace: MONO, fontSize: 8, color: C.amber,
    margin: 0, isTextBox: true, hyperlink: { url: link(m.link) } });
  signalBar(s, m.signal, C.amber);
  footer(s);
}

// ---------- slide 9: what the architects shipped ----------
{
  const sh = M.shipped; const s = pres.addSlide(); base(s);
  topbar(s, sh.num, sh.label, C.green);
  header(s, sh.num, "What The Architects Shipped", sh.title, C.green);
  const y0 = 2.3, rh = 1.35;
  sh.items.forEach((it, i) => {
    const y = y0 + i * rh;
    s.addShape(pres.ShapeType.line, { x: MX, y: y + rh - 0.1, w: W, h: 0, line: { color: C.line, width: 0.5 } });
    mono(s, it.who, MX, y + 0.15, 2.0, 0.3, { color: C.green, size: 10.5, bold: true, spacing: 2 });
    sans(s, it.text, MX + 2.2, y + 0.08, W - 2.2, rh - 0.25, { size: 14, color: C.body, lh: 1.3 });
  });
  sans(s, sh.quiet, MX, y0 + sh.items.length * rh + 0.25, W, 0.8, { size: 12.5, color: C.muted });
  signalBar(s, sh.signal, C.green);
  footer(s);
}

// ---------- slide 10: constraints and radar ----------
{
  const c = M.constraints; const s = pres.addSlide(); base(s);
  topbar(s, c.num, c.label, C.rose);
  header(s, c.num, c.title, "Two moves that change what a compliant deployment has to look like.", C.rose);
  const top = 2.25, n = c.items.length, gap = 0.18, h = 3.55;
  c.items.forEach((it, i) => card(s, it, MX, top + i * (h + gap), W, h, C.rose));
  const ry = top + n * (h + gap) + 0.1;
  s.addShape(pres.ShapeType.rect, { x: MX, y: ry, w: W, h: 1.3, fill: { color: C.card2 }, line: { color: C.line, width: 0.5 } });
  mono(s, "RADAR", MX + 0.3, ry + 0.22, 1.2, 0.25, { color: C.teal, size: 8.5, bold: true, spacing: 3 });
  sans(s, c.radar.text, MX + 1.5, ry + 0.16, W - 3.6, 1.0, { size: 12.5, color: C.body });
  s.addText("Open the Radar", { x: MX + W - 2.1, y: ry + 0.98, w: 1.85, h: 0.22, fontFace: MONO, fontSize: 8, color: C.teal,
    align: "right", margin: 0, isTextBox: true, hyperlink: { url: link(c.radar.link) } });
  signalBar(s, c.signal, C.rose);
  footer(s);
}

pres.writeFile({ fileName: outPath }).then(() => console.log("wrote", outPath));
