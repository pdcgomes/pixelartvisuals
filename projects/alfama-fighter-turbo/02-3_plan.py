"""2.3 How the plan grew: the fifteen milestones of the studio's plan in their five phases, by their
plain names, and the day each was added. Six came in the first plan, written on the morning of 5
October from Pedro's ask; the other nine were his ideas, added on 6, 7, 9 and 10 October.
Animated, an intro that holds: a playhead sweeps the days from 5 to 10 October, and each milestone
lights in its phase as the playhead passes the time it was added, with the count climbing to 15.

Numbers and sources (alfamafighterturbo at 74e2f64, Lisbon time):
- The first six (the vertical slice to polish and launch) and the three phases: the studio plan's first
  commit, cd8f5c6, 5 October 10:56 (docs/plans/2026-10-05-studio-design.md).
- Network play, 6 October (proposed 09:45, in the plan at 10:05, f583187); the front end, 6 October (12:56,
  in the plan at 12:59, 133f31a); tooling, 7 October 21:27, and Steam, 7 October 23:38
  (docs/studio/making-of.md, timeline; decisions.md rows "A Tooling milestone..." and "For a later stage:
  the game packaged for Steam..."); performance and resources, 9 October (07:05, ed201d9); the credits,
  9 October (09:41, 4f4e524); feel, combos and learning, 9 October (17:28, 82a59bd); leaderboards and
  tournaments, 10 October (09:37, 1e1282b). Each is "the user" in the studio plan or decisions.md.
- The phases each milestone sits in, and their plain names: the production board (PHASES and ROADMAP in
  docs/studio/board.canvas.tsx for the first ten; the live board of 12 October for the last five).
"""

from pixelkit import Rect, phase
from series import DIRECTOR, PRODUCER, export, frame

PHASES = [
    ("PROVE IT", [("THE VERTICAL SLICE:\nO FADISTA IN ALFAMA", 5.45), ("PRE-PRODUCTION:\nTHE BIBLES", 5.45)]),
    ("SCALE IT", [("THE SECOND FIGHTER:\nD. AFONSO HENRIQUES", 5.45), ("THE ROSTER, IN\nWAVES OF TWO", 5.45),
                  ("THE FRONT END", 6.54)]),
    ("SHIP IT", [("MODES AND THE BOSS", 5.45), ("POLISH AND LAUNCH", 5.45), ("PERFORMANCE AND\nRESOURCES", 9.29),
                 ("THE CREDITS", 9.40), ("FEEL, COMBOS\nAND LEARNING", 9.73)]),
    ("PLAY TOGETHER", [("NETWORK PLAY", 6.42), ("STEAM", 7.98), ("LEADERBOARDS AND\nTHE HALL OF FAME", 10.40),
                       ("TOURNAMENTS\nFOR FRIENDS", 10.40)]),
    ("ALONGSIDE", [("TOOLING", 7.89)]),
]
FIRST = 5.45
DAYS = [5, 6, 7, 8, 9, 10]
START, END = 5.0, 11.0
SWEEP = (0.04, 0.92)
TILE_H, TILE_GAP = 26, 3


def date(day: float) -> str:
    return f"{int(day)} OCTOBER"


def draw(c, t):
    top, bottom = frame(c, 2, 3, "HOW THE PLAN GREW",
                        "DATES FROM THE STUDIO PLAN'S HISTORY AND THE MAKING-OF NOTES; PHASES FROM THE PRODUCTION BOARD.")
    now = START + (END - START) * phase(t, *SWEEP)

    cols = c.bounds.inset(4, 0)
    x, w_all = cols.x, cols.w
    widths = [(w_all - 4 * 4) // 5] * 5
    widths[-1] = w_all - 4 * 4 - sum(widths[:-1])
    count = 0
    for (name, items), w in zip(PHASES, widths):
        started = any(day <= now for _, day in items)
        c.text(x, top + 4, name, "white" if started else "muted", font="large")
        y = top + 17
        for title, day in items:
            on = day <= now
            fresh = on and now - day < 0.35
            pedro = day > FIRST
            accent = DIRECTOR if pedro else PRODUCER
            c.rect(x, y, w, TILE_H, "panel")
            c.box(x, y, w, TILE_H, "white" if fresh else "line")
            c.hline(x + 1, y + 1, w - 2, c.light(accent) if on else "raised")
            c.claim(Rect(x, y, w, TILE_H), title.replace("\n", " "))
            c.paragraph(x + 4, y + 4, title, w - 8, "white" if on else "muted")
            c.text(x + 4, y + TILE_H - 8, date(day), c.light(accent) if on else "raised")
            count += on
            y += TILE_H + TILE_GAP
        x += w + 4

    # The days, a playhead, and a mark for each milestone at the time it was added.
    axis_y = top + 17 + 5 * (TILE_H + TILE_GAP) + 18
    ax, aw = cols.x + 4, cols.w - 8
    px = lambda d: ax + round((d - START) / (END - START) * (aw - 1))
    c.hline(ax, axis_y, aw, "line")
    for d in DAYS:
        c.vline(px(d), axis_y - 2, 5, "line")
        c.text(px(d) + 3, axis_y + 4, f"{d} OCT", "dim")
    c.vline(px(END), axis_y - 2, 5, "line")
    marks = sorted(day for _, items in PHASES for _, day in items)
    stack = {}
    for day in marks:
        k = stack.get(day, 0)
        stack[day] = k + 1
        on = day <= now
        colour = (c.light(DIRECTOR) if day > FIRST else c.light(PRODUCER)) if on else "raised"
        c.rect(px(day) - 1, axis_y - 5 - k * 4, 3, 3, colour)
    hx = px(now)
    c.vline(hx, axis_y - 30, 34, "white")
    c.rect(hx - 1, axis_y + 3, 3, 2, "white")

    # The count, and what the colours mean.
    ly = axis_y + 14
    c.text(cols.x + 4, ly, str(count), "white", font="large", scale=2, shadow="line")
    c.text(cols.x + 30, ly + 1, "MILESTONES IN THE PLAN", "text")
    c.text(cols.x + 30, ly + 8, "6 IN THE FIRST, 9 ADDED", "dim")
    lx = cols.x + 150
    c.rect(lx, ly + 1, 5, 5, c.light(PRODUCER))
    c.text(lx + 9, ly + 1, "THE FIRST PLAN, WRITTEN ON 5 OCTOBER FROM PEDRO'S ASK", "text")
    c.rect(lx, ly + 9, 5, 5, c.light(DIRECTOR))
    c.text(lx + 9, ly + 9, "PEDRO'S IDEAS, EACH ADDED TO THE PLAN THE DAY HE HAD IT", "text")


export(draw, __file__, preset="hd", seconds=6, fps=20, hold=3)
