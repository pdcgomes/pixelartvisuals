"""10.1 The punch list filling in: the 24 items a fresh-eyes review found, the night they were fixed.

Every item of the polish punch list is a cell, in its group: 6 musts, 10 shoulds and 8 coulds. The
7 bugs it handed to QA aren't cells of their own, since each is also one of the 24 (B1 is M1, B2 to
B4 are S2, B5 is S5, B6 is S6, B7 is S9), so each item is counted once. A clock runs from 23:50 on
11 October to 01:20 on 12 October, and each cell fills at the time its fix was committed: green
for the UI programmer's lane on the musts, blue for the QA engineer's second sweep (green is the
series' colour for the engine, the game's own code), split when both
fixed the same thing. The list of fixes on the right lights line by line as they land, then the
picture holds on the state at the game's commit 74e2f64 (16:00 on 12 October): nothing more from
the list had been done by then.

Numbers, and where they come from (alfamafighterturbo at 74e2f64):
- 6 musts, 10 shoulds, 8 coulds, 7 bugs: docs/plans/2026-10-12-polish-punch-list.md, "Counts".
- The list merged at 23:51 on 11 October: `git log` (d049903, "Merge branch 'polish-review'").
- Done and when, by commit time (git log, 12 October unless said):
  - the select screen's arrows (M1's first half, B1): 12c3130, 00:16, QA;
  - the swatches named by their keys (S2's first part, B2): 55d44da, 00:19, QA;
  - the title takes START and Escape opens nothing (B3): 8707eb6 at 23:41 on 11 October and
    7808b56 at 00:20, QA;
  - TOUCH LAYOUT [TODO] hidden (M4): b004529, 00:24, UI;
  - the win quote's ghost WINS line (S5, B5): a4fa43e 00:28 (QA) and f2a557f 00:40 (UI, the one kept);
  - BACK ERASES ONE (M5): ff959e6, 00:30, UI;
  - CREDITS' LOADING... (S6, B6): 8047f17 00:31 (QA, the one kept) and 44679d3 00:39 (UI);
  - training's readout (M3): 67a6f1b, 00:52, UI;
  - the host's room named after him (S9, B7): 3eb4a08, 00:53, QA;
  - phones held upright fill the width (M2): f8edbfc, 01:07, UI.
  The QA sweep's own account: docs/plans/2026-10-12-qa-sweep-2.md (its fixes 2 to 6 and 10, and
  "Left for the polish phase" 3 and 5). The musts' lane: the punch list's "Done" lines.
- Part done: M1 (the arrows move him; the screen still doesn't name the keys that move) and S2 (the
  swatches and the title's START done; the pads' ESC and ENTER, B4, not): qa-sweep-2.md "Left for
  the polish phase" 3 and 5.
- M6, player 2's kicks on a laptop, waits on the director's hands: docs/plans/2026-10-12-polishing-phase.md,
  "Your decisions this morning" 3.
- 7 done (M2 to M5, S5, S6, S9), 2 part done (M1, S2), 15 to do, of 24: counted from the above.
  Counting each bug a second time beside its item, as the punch list's own tally of 31 does, gives
  13, 2 and 16; the post and this picture count each item once.
- None of them touches the simulation: the punch list's opening ("None of these items changes the
  simulation").
- The shoulds and coulds are the director's to pick: polishing-phase.md, "Your decisions this morning" 3.
"""

from pixelkit import Rect
from series import ENGINE, QA, DIRECTOR, export, frame

UI, SWEEP = ENGINE, QA
START, END = 23 * 60 + 50, 25 * 60 + 20          # the clock, in minutes from midnight on 11 October
RUN = 0.82                                       # share of the loop the clock takes; the rest holds

GROUPS = [("MUSTS", 6), ("SHOULDS", 10), ("COULDS", 8)]
TOTAL = sum(n for _, n in GROUPS)

# Each fixed cell: (group, index) -> list of (minute, lane). Two entries means both lanes fixed it.
M = lambda h, m: (24 + h if h < 12 else h) * 60 + m
FIXES = {
    ("MUSTS", 0): [(M(0, 16), SWEEP)], ("MUSTS", 3): [(M(0, 24), UI)], ("MUSTS", 4): [(M(0, 30), UI)],
    ("MUSTS", 2): [(M(0, 52), UI)], ("MUSTS", 1): [(M(1, 7), UI)],
    ("SHOULDS", 1): [(M(0, 19), SWEEP)], ("SHOULDS", 4): [(M(0, 28), SWEEP), (M(0, 40), UI)],
    ("SHOULDS", 5): [(M(0, 31), SWEEP), (M(0, 39), UI)], ("SHOULDS", 8): [(M(0, 53), SWEEP)],
}
PART = {("MUSTS", 0), ("SHOULDS", 1)}
WAITING = {("MUSTS", 5)}

# The fixes in the order they landed: minute, lane (or both), what changed.
LINES = [
    (M(0, 16), SWEEP, "ARROWS ON THE SELECT SCREEN"),
    (M(0, 19), SWEEP, "SWATCHES NAME THEIR KEYS"),
    (M(0, 20), SWEEP, "TITLE TAKES START, NOT ESC"),
    (M(0, 24), UI, "NO [TODO] IN SETTINGS"),
    (M(0, 28), None, "WIN QUOTE'S GHOST, TWICE"),
    (M(0, 30), UI, "BACK ERASES ONE"),
    (M(0, 31), None, "CREDITS SAY LOADING, TWICE"),
    (M(0, 52), UI, "TRAINING'S READOUT MOVED"),
    (M(0, 53), SWEEP, "HOST'S ROOM GETS HIS NAME"),
    (M(1, 7), UI, "PHONES UPRIGHT, FULL WIDTH"),
]
CELL, GAP = 9, 2


def hhmm(minute):
    minute = int(minute) % (24 * 60)
    return f"{minute // 60:02d}:{minute % 60:02d}"


def draw(c, t):
    top, bottom = frame(c, 10, 1, "THE PUNCH LIST, ONE NIGHT",
                        "COMMIT TIMES, LISBON. 7 OF THE 24 WERE ALSO LOGGED AS BUGS FOR QA.")
    now = START + (END - START) * min(1.0, t / RUN)

    left, right = Rect(0, top + 1, c.w, bottom - top - 3).cut_left(162, gap=2)
    p = c.panel(*left, f"{TOTAL} ITEMS FROM A FRESH-EYES REVIEW", color="white")

    # The clock and the running count.
    states = {}
    for g, n in GROUPS:
        for i in range(n):
            key = (g, i)
            landed = [(m, lane) for m, lane in FIXES.get(key, []) if m <= now]
            states[key] = landed
    done = sum(1 for k, v in states.items() if v and k not in PART)
    part = sum(1 for k, v in states.items() if v and k in PART)
    todo = TOTAL - done - part
    c.text(p.x, p.y + 1, hhmm(now), "white", font="large", scale=2, shadow="dim")
    c.text(p.x, p.y + 19, "11 → 12 OCTOBER" if now < 24 * 60 else "12 OCTOBER", "dim")
    kx = p.x + 64
    c.kv(kx, p.y + 1, p.x2 - kx, [("DONE", f"{done}", "white"), ("PART DONE", f"{part}", "text"),
                                 ("TO DO", f"{todo}", "dim")], step=8)

    # The cells, a row per group.
    y = p.y + 30
    lx = p.x + 44
    for g, n in GROUPS:
        c.text(p.x, y + 2, g, "text")
        c.text(lx - 6, y + 2, f"{n}", "dim", align="right")
        for i in range(n):
            key = (g, i)
            x = lx + i * (CELL + GAP)
            landed = states[key]
            if not landed:
                c.tile(x, y, CELL, "raised")
                if key in WAITING:
                    c.box(x - 1, y - 1, CELL + 2, CELL + 2, DIRECTOR)
                continue
            # A pop of white for the first steps after a fix lands.
            fresh = any(0 <= now - m < 2 for m, _ in landed)
            if fresh:
                c.tile(x, y, CELL, "white")
            elif len(landed) == 2:
                c.tile(x, y, CELL, landed[0][1])
                c.rect(x + CELL // 2, y, CELL - CELL // 2, CELL, landed[1][1])
                c.vline(x + CELL // 2, y, CELL, "shadow")
            elif key in PART:
                c.tile(x, y, CELL, "raised")
                c.pattern(x, y, CELL, CELL, landed[0][1], kind="checker")
            else:
                c.tile(x, y, CELL, landed[0][1])
        y += CELL + 5

    # The key, in two columns.
    ky = y + 1
    kx2 = p.x + 85
    c.tile(p.x, ky, 5, UI)
    c.text(p.x + 8, ky, "THE UI PROGRAMMER", "text")
    c.tile(kx2, ky, 5, SWEEP)
    c.text(kx2 + 8, ky, "THE QA ENGINEER", "text")
    ky += 9
    c.tile(p.x, ky, 5, "raised")
    c.pattern(p.x, ky, 5, 5, SWEEP, kind="checker")
    c.text(p.x + 8, ky, "PART DONE", "text")
    c.tile(kx2, ky, 5, "raised")
    c.box(kx2 - 1, ky - 1, 7, 7, DIRECTOR)
    c.text(kx2 + 8, ky, "WAITS ON PEDRO", "text")
    c.paragraph(p.x, p.y2 - 13, "THE SHOULDS AND COULDS LEFT ARE PEDRO'S TO PICK", p.w, "dim")

    # What was fixed, lighting up as each lands.
    r = c.panel(*right, "WHAT WAS FIXED", color="white", sub="BY COMMIT TIME")
    ly = r.y + 1
    for m, lane, label in LINES:
        on = m <= now
        if on and lane is None:
            c.tile(r.x, ly, 5, SWEEP)
            c.rect(r.x + 3, ly, 2, 5, UI)
        else:
            c.tile(r.x, ly, 5, (lane if on else "raised"))
        c.text(r.x + 8, ly, hhmm(m), "white" if on else "muted")
        c.text(r.x + 30, ly, label, "text" if on else "muted")
        ly += 8
    ly += 3
    c.tile(r.x, ly, 5, "raised")
    c.box(r.x - 1, ly - 1, 7, 7, DIRECTOR)
    c.text(r.x + 8, ly, "PLAYER 2'S KICKS ON A LAPTOP", "text")
    c.text(r.x + 8, ly + 7, "WAIT FOR PEDRO TO TRY THE KEYS", DIRECTOR)
    c.paragraph(r.x, r.y2 - 13, f"NONE OF THE {TOTAL} CHANGES HOW A FIGHT PLAYS", r.w, "dim")


export(draw, __file__, preset="wide", seconds=6, fps=20, hold=3)
