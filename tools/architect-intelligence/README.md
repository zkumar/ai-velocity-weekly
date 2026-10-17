# Architect Intelligence generator

One manifest per issue, three outputs. The manifest is the only thing edited by hand.

    python3 build_issue.py issues/issue-NN.yaml ../../issue-NN/

Writes into the issue folder:

    architect-intelligence-NN.pptx   square 12.5 in carousel, the LinkedIn document post
    architect-intelligence-NN.pdf    the same, exported with LibreOffice
    architect-intelligence-NN.html   the web page for GitHub Pages
    architect-intelligence-NN.md     newsletter text for the LinkedIn article editor

Requirements: python3 with pyyaml, node with pptxgenjs, LibreOffice for the PDF
(the script skips the PDF if soffice is absent). Validate the deck after a
layout change with the pptx skill's validate.py.

Manifest shape (see issues/issue-02.yaml): header stats, one_line, three
pillars (approval, state, audit), five tagged changes, four sections of cards
with WHAT CHANGED and WHAT TO CHANGE, mechanism of the week with observed
numbers, what the architects shipped, constraints and radar, a close line.
Every card carries a link key (longform, mytake, lab, radar) that resolves to
the repo path in the web page and to the GitHub Pages URL in the deck and text.

Tags: EXECUTED means the mechanism was run and the numbers are observed output;
DOCS means read from documentation or source; UNVERIFIED means not confirmed.
Palette and type follow the Velocity Intelligence executive deck so the two
read as one family.

## The one-home rule

Every fact appears exactly once in an issue. Slide 02 is synthesis and carries
no item names; its three pillars are the questions the week forced, each with
the slide numbers that answer it. Slide 03 is an index: short label, tag, and
the slide that holds the fact, nothing more. The executed finding lives only on
slide 08, never as a card on a section slide. Signal bars add a consequence,
they do not restate the cards above them. When adding a manifest entry, ask
where its single home is before writing it.

## The series rule

One home per fact holds across issues, not only inside one. `ledger.py` runs
at the start of every build and compares the new manifest's framing lines
(one-line, pillars, section titles and signals, card headlines, mechanism,
constraints) with every earlier manifest in `issues/`. A repeated sentence, an
identical pillar set, or the same mechanism framework two weeks running fails
the build and prints the pair. `LEDGER=warn` builds anyway; use it only to
inspect, never to publish.

Three habits keep the ledger quiet. Standing positions (own the gate, the
model's text is never proof, no independent medical score, verification
outside the model, regulation as constraint) live once on the Start-here page
and are not restated in signal bars. Each issue's one-line is written as the
delta from the previous issue ("last week X moved; this week Y"), so the thesis
is not re-derived weekly. Pillar labels and the mechanism framework rotate with
the week's story.
