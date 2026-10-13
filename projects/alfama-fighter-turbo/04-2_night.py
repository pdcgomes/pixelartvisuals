"""4.2 The night of six lanes, 7 to 8 October: each lane a row on a time axis from 23:40 to 06:15, its bar from
the moment the producer launched it to the moment it was merged into main, with the times it merged main into
itself marked on it, and its merge dropping into main. Pedro's two messages bracket the night.

Animated: a playhead sweeps the night; bars fill in their lane's colour behind it, each merge drops a packet into
main as the playhead passes, and the counters below count up. Then it holds.

Numbers, from alfamafighterturbo at 74e2f64 and the producer's chat:
- 23:41 "continue working overnight with phase 3..." and 06:11 "I'm back, status update please":
  docs/studio/director-prompts.md, 7 Oct 23:41 and 8 Oct 06:11.
- Launch times: each lane's first brief in the producer's chat (its subagent transcript's first timestamp): the
  six at 23:48 to 23:49; the phone performance pass at 02:16; the two follow-ups, resumed agents, at 02:25.
- Merge times into main, and the merges of main into each lane: `git log --merges --format='%ad %s'
  --date=format:'%d %H:%M'`: boss-engine 01:02, netplay 01:12, m5-music 01:23, ponte 01:56 (main into it 01:09,
  01:50), catarina 02:08 (01:16, 02:04), m5-modes 02:19 (01:26, 01:31, 02:03, 02:11), m5-front2 02:47, m5-endings
  02:52 (02:48), perf 07:14 (03:01; again 07:08, after the axis).
- No question was put to Pedro between 23:41 and 06:11: the producer's chat has no AskQuestion call in between.
"""

from pixelkit import ease_out, phase
from series import ART, AUDIO, DIRECTOR, ENGINE, NET, export, frame, packet


def mins(hhmm: str) -> int:
    """Minutes after 23:00 on 7 October."""
    h, m = map(int, hhmm.split(":"))
    return (h + 24 - 23 if h < 12 else h - 23) * 60 + m


LANES = [
    # label, colour, launched, merged, main merged into it
    ("ADAMASTOR'S FIGHT CODE", ENGINE, "23:48", "01:02", []),
    ("NETWORK PLAY", NET, "23:48", "01:12", []),
    ("MUSIC: BOSS, BRIDGE, MENUS", AUDIO, "23:49", "01:23", []),
    ("THE BRIDGE STAGE", ART, "23:49", "01:56", ["01:09", "01:50"]),
    ("SANTA CATARINA STAGE", ART, "23:48", "02:08", ["01:16", "02:04"]),
    ("SELECT, VS, ARCADE", ENGINE, "23:49", "02:19", ["01:26", "01:31", "02:03", "02:11"]),
]
THEN = [
    ("PHONE PERFORMANCE", ENGINE, "02:16", "07:14", ["03:01"]),
    ("PORTRAITS OF THE BEATEN", ENGINE, "02:25", "02:47", []),
    ("ENDINGS, CREDITS MUSIC", AUDIO, "02:25", "02:52", ["02:48"]),
]
START, END = mins("23:40"), mins("06:15")
ASKED, BACK = mins("23:41"), mins("06:11")
SWEEP = (0.0, 0.82)


def draw(c, t):
    top, bottom = frame(c, 4, 2, "THE NIGHT OF SIX LANES",
                        "LAUNCHES FROM THE PRODUCER'S CHAT, MERGES FROM GIT.")
    now = START + (END - START) * phase(t, *SWEEP)
    x0, x1 = 112, 315
    X = lambda m: x0 + round((m - START) * (x1 - x0) / (END - START))

    # Pedro's two messages.
    for m, text, align in ((ASKED, "23:41 PEDRO: CONTINUE OVERNIGHT", "left"), (BACK, "06:11 PEDRO: I'M BACK", "right")):
        lit = now >= m
        c.text(X(m) + (0 if align == "left" else 1), top + 3, text, c.light(DIRECTOR) if lit else "dim", align=align)

    rows = [(lane, top + 13 + i * 9) for i, lane in enumerate(LANES)]
    then_y = rows[-1][1] + 11
    c.text(4, then_y, "THEN", "dim")
    rows += [(lane, then_y + 8 + i * 9) for i, lane in enumerate(THEN)]
    main_y = rows[-1][1] + 12
    axis_y = main_y + 7

    for m in (ASKED, BACK):
        c.vdots(X(m), top + 10, axis_y - top - 10, DIRECTOR if now >= m else "raised")

    merged = 0
    ins = 0
    for (label, colour, a, b, into), y in rows:
        a, b = mins(a), mins(b)
        xa, xb = X(a), min(X(b), x1)
        on = a <= now < b
        c.text(4, y, label, "white" if on else c.light(colour) if now >= b else "text")
        c.rect(xa, y, xb - xa + 1, 5, "raised")
        if now > a:
            c.rect(xa, y, min(X(now), xb) - xa + 1, 5, colour)
            c.hline(xa, y, min(X(now), xb) - xa + 1, c.light(colour))
        for m in map(mins, into):
            done = now >= m
            ins += done and m <= END
            if m <= END:
                c.rect(X(m), y + 1, 1, 3, "white" if done else "line")
        if b <= END:
            c.vline(xb + 1, y, 5, "white" if now >= b else "line")
            drop = phase(now, b, b + 9)
            if 0 < drop < 1:
                packet(c, xb + 1, round(y + 2 + (main_y + 1 - y - 2) * ease_out(drop)), c.light(colour))
            merged += now >= b
        else:
            c.text(x1 - 3, y - 8, "STILL RUNNING AT 06:15, MERGED 07:14", "dim", align="right")

    # Main, with a tick for every lane merged into it.
    c.text(4, main_y, "MAIN", "white")
    c.rect(x0, main_y, x1 - x0 + 1, 3, "raised")
    c.rect(x0, main_y, X(now) - x0 + 1, 3, "text")
    for (label, colour, a, b, into), y in rows:
        if mins(b) <= END and now >= mins(b) + 9:
            c.rect(X(mins(b)), main_y - 1, 3, 5, c.light(colour))

    px = X(mins("03:12"))
    y = c.paragraph(px, rows[1][1], "AFTER 02:52 ONLY THE PHONE PASS RAN ON. EVERY QUESTION WAITED FOR "
                    "THE MORNING.", X(mins("05:55")) - px, "dim")
    c.rect(px, y + 6, 1, 3, "white")
    c.text(px + 4, y + 5, "MAIN MERGED INTO IT", "dim")

    c.hline(x0, axis_y, x1 - x0 + 1, "line")
    for h in ("00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00"):
        c.vline(X(mins(h)), axis_y, 2, "dim")
        c.text(X(mins(h)), axis_y + 4, h, "dim", align="center")
    if now < END:
        c.vline(X(now), top + 10, axis_y - top - 9, "white")

    stats = [(f"{6 if now >= mins('23:49') else 0}", "LANES LAUNCHED", "23:48 AND 23:49"),
             (f"{merged}", "MERGED INTO MAIN", "BY 02:52"),
             (f"{ins}", "MERGES OF MAIN", "INTO A LANE"),
             ("0", "QUESTIONS", "FOR PEDRO")]
    sy = axis_y + 13
    for i, (value, line1, line2) in enumerate(stats):
        sx = 4 + i * 79
        w = c.text(sx, sy, value, "white", font="large")
        c.text(sx + w + 4, sy, line1, "text")
        c.text(sx + w + 4, sy + 7, line2, "dim")


export(draw, __file__, preset="wide", seconds=6, fps=20, hold=3)
