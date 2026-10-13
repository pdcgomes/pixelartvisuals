"""2.2 The studio's memory: the documents every brief points at (the design document, the studio plan,
the six bibles, the decisions log, the feature designs and the prompts kept beside the pictures), a
lane that reads them and writes back, and what happens when a bible and the decisions log disagree.
Animated, a seamless loop: a lane reads the bibles, then the decisions log; the example below shows the
log winning over the art bible; the lane works, then writes its as-built note back into a bible.

Numbers and sources (alfamafighterturbo at 74e2f64):
- The documents and their jobs: docs/studio/studio-model.md, "The documents are the studio's memory".
- 11 rows "Asked and answered" and 250 "Recommendations accepted": docs/studio/decisions.md (count of
  table rows, headers excluded). Shown as "250 more calls", since 133 of the 250 are the producer's or
  another role agent's own calls rather than recommendations Pedro accepted.
- 20 feature designs and plans besides the design document and the studio plan: docs/plans/ (22 files).
- The disagreement: the art bible's size classes put A Padeira in "large", 106 to 112 px (art bible,
  section 2.1's table); the decisions log, 7 October: "A Padeira keeps her size: 95–100 px upright"; the
  art bench takes 95 to 100 from "decision, 7 October" (src/game/artbench/roster.ts, HEIGHTS).
- Write-back notes headed "First build" or "In the game": studio-model.md, same section.
"""

from pixelkit import ease_in_out, phase
from series import ART, AUDIO, DIRECTOR, ENGINE, PRODUCER, QA, along, export, frame, packet

ROWS = [
    # key, icon, colour, name, what it is
    ("design", "file", "text", "THE DESIGN DOCUMENT", "WHAT THE GAME IS"),
    ("plan", "file", PRODUCER, "THE STUDIO PLAN", "ROLES, HOW WORK MOVES, MILESTONES"),
    ("bibles", "folder", ART, "THE BIBLES", "ONE PER AREA, READ BEFORE ANY WORK"),
    ("log", "file", DIRECTOR, "THE DECISIONS LOG", "EVERY DECISION, DATED · WINS OVER A BIBLE"),
    ("features", "folder", ENGINE, "FEATURE DESIGNS AND PLANS", "20 MORE, FROM NETWORK PLAY TO THE CREDITS"),
    ("prompts", "file", AUDIO, "PROMPTS", "KEPT BESIDE THE PICTURES THEY MADE"),
]
BIBLES = [["ART", "ANIMATION", "AUDIO"], ["ROSTER", "STAGES", "FRONT END"]]
# The loop's windows of t.
READ_BIBLE, READ_LOG, OVERRIDE, WORK, WRITE = (0.04, 0.2), (0.22, 0.38), (0.4, 0.58), (0.58, 0.68), (0.68, 0.86)
NOTE_ON = (0.84, 0.98)


def draw(c, t):
    top, bottom = frame(c, 2, 2, "THE STUDIO'S MEMORY", "FROM THE STUDIO MODEL, THE DECISIONS LOG AND THE ART BENCH.")
    on = lambda w: w[0] <= t < w[1]

    lit = set()
    if on(READ_BIBLE) or on(WRITE) or on(NOTE_ON):
        lit.add("bibles")
    if on(READ_LOG) or on(OVERRIDE):
        lit.add("log")

    docs = c.panel(0, top + 1, 190, bottom - top - 3, "IN THE REPO", color="white", sub="EVERY BRIEF POINTS HERE")
    ys = {}
    y = docs.y
    for key, icon, colour, name, what in ROWS:
        hot = key in lit
        c.icon(docs.x, y, icon, "white" if hot else colour)
        c.text(docs.x + 12, y, name, c.light(colour) if hot and colour != "text" else "white")
        c.text(docs.x + 12, y + 7, what, "text" if hot else "dim")
        ys[key] = y
        y += 17
        if key == "bibles":
            for row in BIBLES:
                parts = []
                for i, b in enumerate(row):
                    if i:
                        parts.append((" · ", "muted"))
                    parts.append((b, c.light(ART) if hot else "muted"))
                c.spans(docs.x + 12, y, parts)
                y += 8
            y += 1
        if key == "log":
            c.spans(docs.x + 12, y, [("11", "white"), (" ASKED AND ANSWERED · ", "dim"), ("250", "white"),
                                     (" MORE CALLS", "dim")])
            y += 9

    # The lane, on the right, joined to the documents by a line down the gutter.
    rx = docs.x2 + 10
    working = on(WORK)
    lane = c.node(rx, top + 4, c.w - rx - 4, 19, "A LANE", color="white" if working else PRODUCER,
                  sub="ONE AGENT, ONE JOB", border="white" if working else "line")
    gx = docs.x2 + 4
    rows_y = {k: ys[k] + 3 for k in ("bibles", "log")}
    c.hline(gx, lane.cy, lane.x - gx - 1, "line")
    c.vline(gx, lane.cy, rows_y["log"] - lane.cy + 1, "line")
    for k, ry in rows_y.items():
        c.arrow(gx, ry, docs.x2 + 1, ry, "line", head=False)
    c.text(lane.x, lane.y2 + 3, "READS THEM, THEN WRITES BACK", "dim")
    c.text(lane.x, lane.y2 + 10, "THE NUMBERS AS BUILT", "dim")

    if on(READ_BIBLE):
        packet(c, *along([(gx, rows_y["bibles"]), (gx, lane.cy), (lane.x - 2, lane.cy)],
                         ease_in_out(phase(t, *READ_BIBLE))), c.light(ART))
    if on(READ_LOG):
        packet(c, *along([(gx, rows_y["log"]), (gx, lane.cy), (lane.x - 2, lane.cy)],
                         ease_in_out(phase(t, *READ_LOG))), c.light(DIRECTOR))
    if on(WRITE):
        packet(c, *along([(lane.x - 2, lane.cy), (gx, lane.cy), (gx, rows_y["bibles"])],
                         ease_in_out(phase(t, *WRITE))), "white")

    # When a bible and the log disagree.
    wy = lane.y2 + 20
    w = c.panel(rx - 4, wy, c.w - rx + 4, bottom - wy - 2, "IF THEY DISAGREE", color=c.light(DIRECTOR),
                sub="THE LOG WINS")
    overruled = OVERRIDE[0] + 0.06 <= t < WRITE[1] + 0.12
    bible = "dim" if overruled else "text"
    c.text(w.x, w.y, "ART BIBLE: A PADEIRA IS", c.light(ART) if not overruled else "dim")
    c.text(w.x, w.y + 7, "LARGE,", bible)
    old = c.text(w.x + 28, w.y + 7, "106–112 PX", bible)
    if overruled:
        c.text(w.x + 28 + old + 5, w.y + 7, "OVERRULED", c.light(ART))
    log = "white" if on(OVERRIDE) else "text"
    c.text(w.x, w.y + 17, "DECISIONS LOG, 7 OCTOBER:", c.light(DIRECTOR))
    c.text(w.x, w.y + 24, "SHE STANDS 95–100 PX", log)
    tool = c.light(QA) if overruled else "dim"
    c.text(w.x, w.y + 34, "THE TOOL THAT MEASURES THE", tool)
    c.text(w.x, w.y + 41, "CAST CHECKS HER AT 95–100", tool)
    if on(NOTE_ON):
        c.text(docs.x + 12 + c.measure("THE BIBLES") + 6, ys["bibles"], "+ A NOTE OF WHAT WAS BUILT", "white")


export(draw, __file__, preset="wide", seconds=6, fps=20, seamless=True, poster=0.9)
