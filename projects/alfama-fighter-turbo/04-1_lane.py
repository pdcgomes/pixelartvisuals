"""4.1 A lane's life: the ten steps one piece of work went through, from the producer picking it to the
producer answering its questions, and below them the same lane in git: the bridge stage's lane on the night of
7 to 8 October, cut from main, merging main into itself twice while other lanes landed, then merged clean.

Animated: a packet walks the ten steps in turn and the step it's on lights. While it's at RUN, a playhead sweeps
the git timeline from 23:49 to 01:55 and the two merges of main into the lane rise from main as the playhead
passes them; at MERGE the lane drops into main. Loops seamlessly.

Numbers, all from alfamafighterturbo at 74e2f64 unless noted:
- The ten steps and who does them: docs/studio/studio-model.md, "A lane's life", and
  .cursor/skills/running-an-agent-studio/SKILL.md, "Run a lane".
- The bridge stage's lane (branch `ponte`): cut from main at 1de4182, 7 Oct 23:46; launched 23:49 (the producer's
  chat, its subagent's first message); main merged in at 01:09 (b397423) and 01:50 (a73d449); merged into main at
  01:56 (d82ac9b). Other lanes merged into main meanwhile: Adamastor's engine 01:02 (2bc2b60), network play 01:12
  (720eaf0), the music 01:23 (e861502). `git log --merges --format='%ad %s' --date=format:'%d %H:%M'`.
"""

from pixelkit import ease_in_out, phase
from series import ART, PRODUCER, along, export, frame, packet

STEPS = [
    # title, who, two lines
    ("PICK", PRODUCER, "WORK THAT NEEDS NO", "DECISION FROM PEDRO"),
    ("WORKTREE", PRODUCER, "ITS OWN COPY, BRANCH", "AND SERVER PORT"),
    ("BRIEF", PRODUCER, "WHAT'S NEW, THE JOB,", "THE LANES BESIDE IT"),
    ("LAUNCH", PRODUCER, "IN THE BACKGROUND,", "RESUMED OR FRESH"),
    ("RUN", ART, "WORKS ON ITS BRANCH,", "MERGES MAIN INTO IT"),
    ("REPORT", ART, "DONE, WITH PREVIEWS", "AND OPEN QUESTIONS"),
    ("REVIEW", PRODUCER, "CHECKS THE PICTURES", "AND THE RISKY DIFFS"),
    ("MERGE", PRODUCER, "INTO MAIN, THEN THE", "TESTS AND A PLAYTEST"),
    ("SHIP", PRODUCER, "PUSH, STOP SERVER,", "REMOVE THE WORKTREE"),
    ("ANSWER", PRODUCER, "SETTLE QUESTIONS,", "ASK PEDRO THE REST"),
]
# Each step's turn as a window of t; RUN's is long, for the playhead to sweep the night.
TURNS = [(0.02, 0.05), (0.07, 0.11), (0.13, 0.16), (0.18, 0.21), (0.23, 0.60), (0.63, 0.66), (0.68, 0.71),
         (0.73, 0.79), (0.81, 0.84), (0.86, 0.90)]


def mins(hhmm: str) -> int:
    """Minutes after 23:00 on 7 October."""
    h, m = map(int, hhmm.split(":"))
    return (h + 24 - 23 if h < 12 else h - 23) * 60 + m


START, END = mins("23:40"), mins("02:00")
CUT, LAUNCH, IN1, IN2, MERGED = mins("23:46"), mins("23:49"), mins("01:09"), mins("01:50"), mins("01:56")
OTHERS = [mins("01:02"), mins("01:12"), mins("01:23")]


def clock(t: float) -> float:
    """The git timeline's time at t: still before the worktree, sweeping through RUN, at the merge after."""
    keys = [(0.0, START), (TURNS[1][0], START), (TURNS[1][1], CUT), (TURNS[3][1], LAUNCH), (TURNS[4][0], LAUNCH),
            (TURNS[4][1], mins("01:55")), (TURNS[7][0], mins("01:55")), (TURNS[7][1], MERGED), (1.0, MERGED)]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * (phase(t, t0, t1) if t1 > t0 else 1)
    return MERGED


def draw(c, t):
    top, bottom = frame(c, 4, 1, "A LANE'S LIFE",
                        "THE EXAMPLE IS THE BRIDGE STAGE'S LANE, NIGHT OF 7 TO 8 OCT, FROM GIT AND THE PRODUCER'S CHAT.")
    active = next((i for i, (a, b) in enumerate(TURNS) if a <= t < b), None)

    c.text(7, top + 5, "TEN STEPS: ONE PIECE OF WORK, ONE AGENT, ONE WORKTREE", "white")
    c.spans(473, top + 5, [("■ ", PRODUCER), ("THE PRODUCER   ", "text"), ("■ ", ART), ("THE LANE'S AGENT", "text")],
            align="right")

    nodes = []
    for i, (title, who, line1, line2) in enumerate(STEPS):
        row, col = divmod(i, 5)
        x, y = 7 + col * 95, top + 17 + row * 44
        on = i == active
        n = c.node(x, y, 86, 26, title, color="white" if on else who, sub=line1, badge=str(i + 1),
                   badge_color="white" if on else "dim", border="white" if on else "line")
        c.text(n.x + 3, n.y + 18, line2, "text" if on else "dim")
        nodes.append(n)
    for a, b in zip(nodes[:4], nodes[1:5]):
        c.arrow(a.x2, a.cy, b.x - 1, a.cy, "white")
    for a, b in zip(nodes[5:9], nodes[6:]):
        c.arrow(a.x2, a.cy, b.x - 1, a.cy, "white")
    via = nodes[0].y2 + 8
    down = c.connect(nodes[4], nodes[5], "white", ax=nodes[4].cx, bx=nodes[5].cx, via=via)

    # The packet between steps, on the arrow from one step's turn to the next.
    for i, ((_, end), (start, _)) in enumerate(zip(TURNS, TURNS[1:])):
        if end <= t < start:
            a, b = nodes[i], nodes[i + 1]
            if i == 4:
                path = [(down[0][0], a.y2 + 2)] + down[1:-1] + [(down[-1][0], b.y - 3)]
            else:
                path = [(a.x2 + 2, a.cy), (b.x - 3, a.cy)]
            x, y = along(path, ease_in_out(phase(t, end, start)))
            packet(c, x, y, "white")

    # The same lane in git.
    g = c.panel(7, nodes[5].y2 + 11, 466, bottom - nodes[5].y2 - 13, "THE SAME LANE IN GIT",
                color=c.light(ART), sub="THE BRIDGE STAGE, NIGHT OF 7 TO 8 OCTOBER")
    x0, x1 = g.x + 74, g.x2 - 6
    X = lambda m: x0 + round((m - START) * (x1 - x0) / (END - START))
    lane_y, main_y = g.y + 26, g.y + 64
    now = clock(t)
    px = X(now)

    c.text(g.x, lane_y - 2, "THE LANE'S", c.light(ART))
    c.text(g.x, lane_y + 5, "OWN BRANCH", c.light(ART))
    c.text(g.x, main_y - 2, "MAIN, THE", "white")
    c.text(g.x, main_y + 5, "SHARED GAME", "white")

    c.rect(x0, main_y, x1 - x0, 3, "raised")
    c.rect(x0, main_y, max(0, px - x0), 3, "text")
    c.rect(X(CUT), lane_y, X(MERGED) - X(CUT) + 1, 3, "raised")
    if now > CUT:
        c.rect(X(CUT), lane_y, max(1, min(px, X(MERGED)) - X(CUT)), 3, c.light(ART))

    def link(m, up, lit, solid=False):
        """A merge between the tracks at minute m: main into the lane (up) or the lane into main."""
        x = X(m)
        colour = "white" if lit else ("text" if up else c.light(ART) if solid else ART)
        for y in range(lane_y + 4, main_y - 1):
            if (y - lane_y) % 2 == 0 or lit or solid:
                c.px(x, y, colour)
        if up:
            c.px(x - 1, lane_y + 5, colour)
            c.px(x + 1, lane_y + 5, colour)
        else:
            c.px(x - 1, main_y - 2, colour)
            c.px(x + 1, main_y - 2, colour)

    link(CUT, True, CUT <= now < LAUNCH)
    link(IN1, True, abs(now - IN1) < 4)
    link(IN2, True, abs(now - IN2) < 4)
    merged = t >= TURNS[7][0]

    # Other lanes landing in main meanwhile.
    for m in OTHERS:
        x = X(m)
        lit = abs(now - m) < 4
        c.vdots(x, main_y - 9, 8, "white" if lit else "dim")
        c.rect(x - 1, main_y - 1, 3, 5, "white" if lit else "dim")

    c.text(X(CUT) + 4, lane_y - 9, "MADE FROM MAIN 23:46, LAUNCHED 23:49", "white" if CUT <= now <= LAUNCH + 2 else "dim")
    c.text(X(IN1) - 3, lane_y + 9, "MAIN MERGED IN 01:09", "white" if abs(now - IN1) < 4 else "dim", align="right")
    c.text(X(IN2) - 3, lane_y + 9, "AGAIN 01:50", "white" if abs(now - IN2) < 4 else "dim", align="right")
    c.text(X(OTHERS[0]) - 3, main_y - 9, "OTHER LANES LAND IN MAIN", "white" if any(abs(now - m) < 4 for m in OTHERS)
           else "dim", align="right")
    c.text(X(MERGED) - 3, main_y + 6, "MERGED INTO MAIN 01:56", "white" if active == 7 else c.light(ART) if merged
           else "dim", align="right")

    # The time axis.
    axis_y = main_y + 16
    c.hline(x0, axis_y, x1 - x0 + 1, "line")
    for label in ("23:40", "00:00", "00:30", "01:00", "01:30", "02:00"):
        x = X(mins(label))
        c.vline(x, axis_y, 2, "dim")
        c.text(x, axis_y + 4, label, "dim", align="center" if label not in ("23:40", "02:00") else
               ("left" if label == "23:40" else "right"))
    if merged:
        link(MERGED, False, active == 7, solid=True)
    else:
        c.vline(px, lane_y - 3, axis_y - lane_y + 4, "white")
        link(MERGED, False, False)
    if active == 4:
        packet(c, px, lane_y + 1, c.light(ART))
    if active == 7:
        x, y = along([(X(MERGED), lane_y + 1), (X(MERGED), main_y + 1)], ease_in_out(phase(t, *TURNS[7])))
        packet(c, x, y, c.light(ART))
    for m in (IN1, IN2):
        p = phase(now, m - 4, m)
        if 0 < p < 1:
            x, y = along([(X(m), main_y + 1), (X(m), lane_y + 1)], p)
            packet(c, x, y, "white")

    y = c.paragraph(g.x, axis_y + 15, "WHILE IT RAN, THREE OTHER LANES WERE MERGED INTO MAIN: ADAMASTOR'S FIGHT CODE AT 01:02, "
                    "NETWORK PLAY AT 01:12 AND THE MUSIC AT 01:23.", g.w, "dim")
    c.paragraph(g.x, y + 3, "ITS BRIEF HADN'T ASKED IT TO MERGE MAIN IN, AND ITS MERGE INTO MAIN WAS CLEAN. "
                "FROM 9 OCTOBER NEARLY EVERY BRIEF ASKED.", g.w, "white")


export(draw, __file__, preset="hd", seconds=10, fps=20, seamless=True, poster=0.95)
