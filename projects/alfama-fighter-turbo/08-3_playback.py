"""8.3 A score the server plays back: a ranked run from its token to the boards. The server issues a token
(the seed the CPU plays with, the fights in order, the build, the time); the run is played on the device with
the CPU seeded from it; only player 1's inputs go back, with the score the game reached; the server's cheap
checks come first, then it plays the inputs through the game's own simulation, fight by fight, its own CPU
answering from the seed; its score is the score, and a score or a fight's fingerprint that differs is
refused and flagged. The run goes on this week's boards, and each closed week's champions go into the hall
of fame.

Animated as a loop: the run moves from stage to stage, a cursor plays the nine fights in turn inside the
playback, each fight ticked as its end matches, and each measurement lights while the stage it times is at
work.

Numbers, from docs/plans/2026-10-10-leaderboards-design.md (alfamafighterturbo at 74e2f64):
- the token: run id, simulation version, a 32-bit seed, the fighter, NORMAL, the fights in order, the time
  issued, kept three hours (2.2 and its As built);
- the checks, cheapest first: body size (128 KB), signature, token spent once, build, time window,
  monthly budget, then the playback (2.2 and its As built);
- a ranked part's inputs: 1 to 12 KB of JSON, 0.3 to 2.5 KB gzipped (2.2's As built);
- verifying as built, measured: about 2 microseconds a step warm; a one-credit clear 72 to 293 ms of CPU
  warm, 0.43 to 0.66 s in a fresh Node; all 48 runs verified (2.3's "As built, measured again");
- the week from Monday 00:00 in Lisbon, closed at 03:00; the hall keeps each week's champions (6, 7).
"""

from pixelkit import ease_in_out, phase
from series import ENGINE, NET, along, export, frame, packet

STAGES = [
    # key, title, side, two lines of detail
    ("TOKEN", "1 THE TICKET", NET, "FROM THE SERVER: A SEED,", "THE FIGHTS, VERSION, TIME"),
    ("RUN", "2 THE RUN", ENGINE, "ON THE DEVICE, THE", "OPPONENT USES THE SEED"),
    ("INPUTS", "3 THE INPUTS", ENGINE, "PLAYER 1'S ONLY, AND", "THE SCORE THE GAME GOT"),
    ("CHECKS", "4 THE CHECKS", NET, "SIZE · KEY · USED ONCE", "VERSION · TIME · BUDGET"),
    ("PLAYBACK", "5 THE PLAYBACK", NET, "THE GAME'S OWN FIGHTS, ITS OPPONENT FROM THE SEED", "THE SCORE IT REACHES IS THE SCORE"),
    ("BOARDS", "6 THE BOARDS", NET, "THIS WEEK'S, FROM", "MONDAY 00:00 IN LISBON"),
    ("HALL", "7 THE HALL OF FAME", NET, "EACH CLOSED WEEK'S", "CHAMPIONS, KEPT"),
]
FIGHTS = 9
TIMES = [("~2", ("MICROSECONDS A STEP,", "CODE ALREADY LOADED"), {"PLAYBACK"}),
         ("72 TO 293 MS", ("OF PROCESSOR TIME TO", "CHECK ALL NINE FIGHTS"), {"PLAYBACK"}),
         ("0.43 TO 0.66 S", ("THE SAME IN A NEWLY", "STARTED PROCESS"), {"PLAYBACK"}),
         ("1 TO 12 KB", ("OF INPUTS FOR A RUN,", "UNDER 3 KB COMPRESSED"), {"INPUTS"})]

TURNS = [(0.02, 0.08), (0.10, 0.22), (0.24, 0.30), (0.32, 0.38), (0.46, 0.74), (0.80, 0.86), (0.88, 0.95)]
SCAN = (0.48, 0.72)


def draw(c, t):
    top, bottom = frame(c, 8, 3, "A SCORE THE SERVER PLAYS BACK",
                        "MEASURED ON THE STUDIO'S MAC UNDER LOAD, ON RUNS PLAYED BY THE GAME'S OWN COMPUTER OPPONENT.")
    active = next((i for i, (a, b) in enumerate(TURNS) if a <= t < b), None)
    key = STAGES[active][0] if active is not None else None

    def stage(i, x, y, w):
        _, title, accent, line1, line2 = STAGES[i]
        on = i == active
        n = c.node(x, y, w, 26, title, color="white" if on else accent, sub=line1, border="white" if on else "line")
        c.text(n.x + 3, n.y + 18, line2, "text" if on else "dim")
        return n

    row1 = [stage(i, 9 + i * 118, top + 24, 108) for i in range(4)]
    for a, b in zip(row1, row1[1:]):
        c.arrow(a.x2, a.cy, b.x - 1, a.cy, "white")
    # The device's part, between the server's.
    dev = (row1[1].x - 4, row1[1].y - 9, row1[2].x2 - row1[1].x + 8, row1[1].h + 13)
    for x, y, n, vertical in ((dev[0], dev[1], dev[2], False), (dev[0], dev[1] + dev[3] - 1, dev[2], False),
                              (dev[0], dev[1], dev[3], True), (dev[0] + dev[2] - 1, dev[1], dev[3], True)):
        c.dashes(x, y, n, c.dark(ENGINE), vertical=vertical)
    c.text(dev[0] + 4, dev[1] - 7, "ON THE DEVICE", c.light(ENGINE))
    c.text(9, row1[0].y - 7, "ON THE SERVER", c.light(NET))
    c.text(row1[3].x2, row1[0].y - 7, "VERCEL FUNCTIONS", "dim", align="right")

    y2 = row1[0].y2 + 24
    playback = stage(4, 9, y2, 226)
    boards = stage(5, 245, y2, 108)
    hall = stage(6, 363, y2, 108)
    down = c.connect(row1[-1], playback, "white", ax=row1[-1].cx, bx=playback.cx, via=row1[0].y2 + 11)
    c.arrow(playback.x2, playback.cy, boards.x - 1, playback.cy, "white")
    c.arrow(boards.x2, boards.cy, hall.x - 1, boards.cy, "white")

    nodes = row1 + [playback, boards, hall]
    for i, ((_, end), (start, _)) in enumerate(zip(TURNS, TURNS[1:])):
        if end <= t < start:
            a, b = nodes[i], nodes[i + 1]
            if i == 3:
                path = [(down[0][0], a.y2 + 2)] + down[1:-1] + [(down[-1][0], b.y - 3)]
            else:
                path = [(a.x2 + 2, a.cy), (b.x - 3, a.cy)]
            x, y = along(path, ease_in_out(phase(t, end, start)))
            packet(c, x, y, "white")

    # The playback opened up: the fights in turn, each held to the game's own end.
    band_y = playback.y2 + 18
    on = active == 4
    c.text(9, band_y - 9, "INSIDE THE PLAYBACK, FIGHT BY FIGHT", "white" if on else "text")
    c.text(235, band_y - 9, "ALL NINE FIGHTS", "dim", align="right")
    cursor = phase(t, *SCAN) * FIGHTS
    cell = 25
    for f in range(FIGHTS):
        x = 9 + f * cell
        here = on and f <= cursor < f + 1
        done = cursor >= f + 1 if t < TURNS[4][1] + 0.02 else True
        c.rect(x, band_y, cell - 2, 7, "white" if here else c.dark(NET) if not done else NET)
        c.text(x + (cell - 2) // 2, band_y + 1, str(f + 1), "bg" if here else "white", align="center")
        if done:
            c.icon(x + 8, band_y + 9, "check", c.light(ENGINE))
    y = c.paragraph(9, band_y + 20, "EACH FIGHT MUST END EXACTLY WHERE ITS INPUTS DO, WITH THE GAME'S FINGERPRINT "
                    "AND SCORE.", 226, "text")
    c.paragraph(9, y + 2, "IF EITHER DIFFERS, NOTHING IS POSTED AND THE RUN IS FLAGGED.", 226, c.light("red"))

    # The week, and what can't be stopped.
    side = c.panel(245, playback.y2 + 9, 226, 50, "WHAT IT CAN'T CATCH", color=c.light("red"),
                   sub="THE DESIGN'S OWN LIST")
    c.paragraph(side.x, side.y, "A BOT MADE TO PLAY LIKE A PERSON, OR A RUN PLAYED FRAME BY FRAME WITH TOOLS AND SENT "
                "IN A BELIEVABLE TIME. THE CHECKS FOR INHUMAN PLAY HAVE MET ONLY SCRIPTED PLAYERS.", side.w, "text")

    sy = bottom - 39
    stats = c.panel(9, sy, 462, bottom - sy - 2, "MEASURED", color="white",
                    sub="THE CHECKER AS IT SHIPS, 10 OCT · ALL 48 RUNS PASSED")
    for i, (value, caption, timed) in enumerate(TIMES):
        sx = stats.x + i * 116
        c.text(sx, stats.y + 1, value, c.light(NET), font="large")
        for k, line in enumerate(caption):
            c.text(sx, stats.y + 12 + k * 7, line, "white" if key in timed else "dim")


export(draw, __file__, preset="hd", seconds=8, fps=20, seamless=True, poster=0.95)
