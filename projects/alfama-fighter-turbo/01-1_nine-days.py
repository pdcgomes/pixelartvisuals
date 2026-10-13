"""1.1 Nine days, row by row: what each part of Alfama Fighter Turbo had by the end of each day,
4 to 12 October 2026, with the commits made each day underneath.

Animated: a playhead sweeps from Sunday to Monday; each milestone lights as it passes (every label is
on screen from the start, dim until then), each day's commit bar rises as the day goes by, and a
counter adds them up; then it holds.

Sources (alfamafighterturbo at 74e2f64):
- Sunday to Thursday: docs/studio/making-of.md, the timeline. Design document and research (Sun);
  studio founded and five bibles, pre-production signed off 15:52, O Fadista in Alfama with its theme
  (Mon); D. Afonso Henriques and the Castelo, the front end (Tue); waves 1 and 2, four fighters and
  four stages, the sound bench 23:04 (Wed); network play with rollback, the bridge and Santa Catarina,
  the arcade and endings overnight, the roster complete 11:38, the art bench 10:37, the phone pass,
  every stage, fighter and the music approved (Thu).
- Friday to Monday: the git log. The game public 09:25 (9d3652c), memory budgets from 07:05 (ed201d9),
  the credits (credits-scene, 21:49), the balance lab (17:27) (Fri); the feel pass, training and trials
  overnight, ranked play and the boards built in the day (m11-*, m12-*) (Sat); tournaments live 09:30
  (0a509ca), the Easter egg (egg-life 20:07), the punch list (d049903) (Sun); the mix approved 09:47
  (43f475d), the logo picked and built 11:18 (66ec920) (Mon).
- Commits a day: git log --format=%ad --date=short 74e2f64 | sort | uniq -c, 12 October to 16:00.
"""

from pixelkit import ease_out, phase
from series import ART, AUDIO, ENGINE, NET, PRODUCER, TOOLS, export, frame

DAYS = ["SUN 4", "MON 5", "TUE 6", "WED 7", "THU 8", "FRI 9", "SAT 10", "SUN 11", "MON 12"]
COMMITS = [6, 41, 45, 181, 282, 227, 348, 310, 108]
POLISH = "yellow"

# Row label, accent, and the milestones in it: (day index, first line, second line).
ROWS = [
    ("STUDIO", PRODUCER, [(0, "DESIGN", "DOCUMENT"), (1, "5 BIBLES", "SIGNED OFF"), (5, "PUBLIC", "LINK")]),
    ("FIGHTERS", ART, [(1, "O FADISTA", ""), (2, "D. AFONSO", ""), (3, "FOUR", "MORE"), (4, "ALL EIGHT", "AND A BOSS")]),
    ("STAGES", "orange", [(1, "ALFAMA", ""), (2, "CASTELO", ""), (3, "FOUR", "MORE"), (4, "ALL TEN", "")]),
    ("MUSIC", AUDIO, [(1, "ALFAMA'S", "THEME"), (4, "ALL MUSIC", "APPROVED"), (8, "THE MIX", "APPROVED")]),
    ("MODES", ENGINE, [(2, "TITLE AND", "MENUS"), (4, "ARCADE AND", "ENDINGS"), (5, "THE", "CREDITS"),
                       (6, "TRAINING", "AND FEEL"), (7, "EASTER", "EGG")]),
    ("ONLINE", NET, [(4, "NETWORK", "PLAY"), (6, "RANKED", "BOARDS"), (7, "TOURNAMENTS", "LIVE")]),
    ("TOOLS", TOOLS, [(3, "SOUND", "BENCH"), (4, "ART BENCH", ""), (5, "BALANCE", "TESTER")]),
    ("POLISH", POLISH, [(4, "FASTER ON", "PHONES"), (5, "MEMORY", "LIMITS"), (7, "LIST OF", "FIXES"), (8, "LOGO", "PICKED")]),
]

LABEL_W, COL, ROW = 54, 46, 17
SWEEP = (0.03, 0.82)


def draw(c, t):
    top, bottom = frame(c, 1, 1, "NINE DAYS, ROW BY ROW",
                        "WHAT EACH PART OF THE GAME HAD BY THE END OF EACH DAY. 12 OCTOBER TO 16:00.")
    p = c.panel(0, top + 1, c.w, bottom - top - 3, "4 TO 12 OCTOBER 2026", color="white",
                sub="A ROW FOR EACH KIND OF WORK")
    x0 = p.x + LABEL_W
    now = len(DAYS) * ease_out(phase(t, *SWEEP)) if t < SWEEP[1] else float(len(DAYS))

    # The counter, top right of the panel.
    done = sum(n * min(1.0, max(0.0, now - i)) for i, n in enumerate(COMMITS))
    day = min(len(DAYS), int(now) + 1)
    c.spans(p.x2, p.y - 12, [(f"DAY {day} OF 9 · ", "dim"), (f"{c.num(round(done))} COMMITS", "white")],
            align="right")

    # Day headers.
    hy = p.y
    for i, name in enumerate(DAYS):
        cx = x0 + i * COL + COL // 2
        c.text(cx, hy, name, "white" if now > i else "dim", align="center")
    c.hline(x0, hy + 8, COL * len(DAYS), "line")

    # Rows of milestones.
    ry0 = hy + 12
    for r, (label, accent, events) in enumerate(ROWS):
        y = ry0 + r * ROW
        c.text(p.x, y + 4, label, c.light(accent))
        if r:
            c.dots(x0, y - 3, COL * len(DAYS), "line")
        for d, first, second in events:
            x = x0 + d * COL + 2
            lit = now > d + 0.5
            c.rect(x, y, 2, 12, c.light(accent) if lit else "raised")
            c.text(x + 4, y, first, "white" if lit else "dim")
            if second:
                c.text(x + 4, y + 7, second, "text" if lit else "dim")

    # Commits a day, rising as each day goes by.
    base = p.y2 - 1
    by = ry0 + len(ROWS) * ROW + 2
    c.text(p.x, by + 4, "COMMITS", "white")
    c.text(p.x, by + 11, "A DAY", "dim")
    full = base - by - 9
    peak = max(COMMITS)
    for i, n in enumerate(COMMITS):
        grow = ease_out(min(1.0, max(0.0, now - i)))
        h = round(full * n / peak * grow)
        bx = x0 + i * COL + 9
        colour = "white" if n == peak else c.light(PRODUCER)
        if h:
            c.rect(bx, base - h, COL - 18, h, c.dark(PRODUCER) if n != peak else "muted")
            c.rect(bx, base - h, COL - 18, 1, colour)
        if grow > 0:
            c.text(bx + (COL - 18) // 2, base - h - 7, c.num(round(n * grow)), colour, align="center")

    # The playhead.
    if t < SWEEP[1]:
        px = x0 + round(now * COL)
        c.vline(min(px, x0 + COL * len(DAYS) - 1), hy + 9, base - hy - 9, "white")


export(draw, __file__, preset="hd", seconds=6, fps=20, hold=3)
