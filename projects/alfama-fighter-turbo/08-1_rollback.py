"""8.1 Rollback, step by step: two games of one network match, each playing its own player's presses at
once and guessing the other's by repeating the last one it has. The friend's inputs reach your game three
steps late; while he walks, the guesses are right and nothing happens. When he punches at step 5 the news
reaches your game at step 8: the three steps it guessed wrong (5, 6 and 7) are struck through, the game
goes back to step 5 and plays 5 to 8 again before it draws the next frame, and carries on guessing his new
input. His game's guesses of you were right all along, so it plays nothing again.

Animated: both games step together under a highlighted column; the friend's inputs climb the gutter as
packets, each landing three steps after it left; at step 8 the wrong guesses are struck, an arrow goes back
to step 5, a green column sweeps 5 to 8 while the clock stands still, and the steps go on to 9. Holds.

Numbers, from docs/plans/2026-10-07-network-play-design.md (alfamafighterturbo at 74e2f64):
- the guess repeats the other side's last input; never more than 8 steps past the last remote input,
  then the game waits ("The session", "A step of the session");
- a step costs 3 to 5 microseconds in Node and a snapshot 35, so an 8-step rollback is under a
  millisecond on a laptop ("The simulation");
- a step is 1/60 s, so 3 steps late is 50 ms. The lateness and the inputs are illustrated, with no
  input delay (the game uses 0 to 2 steps of it, chosen from the round trip).
"""

from pixelkit import ease_in_out, phase
from series import ENGINE, NET, along, export, frame, packet

STEPS = 9
LATE = 3                         # steps an input takes to reach the other game
PUNCH = 5                        # the friend's first punch
YOU = ["←"] * STEPS              # you hold back: guarding
FRIEND = ["→"] * (PUNCH - 1) + ["P"] * (STEPS - PUNCH + 1)

# The timeline: the game clock in steps, standing still while the rollback is played inside one frame.
RUN1 = (0.04, 0.42)              # steps 1 to 8
ARRIVE = RUN1[1]                 # step 5's punch lands at step 8
STRIKE, BACK, REPLAY = 0.45, (0.49, 0.55), (0.57, 0.65)
RUN2 = (0.68, 0.76)              # steps 8 to 9
LABEL_W, CELL = 28, 24


def clock(t: float) -> float:
    if t < RUN1[1]:
        return 1 + (PUNCH + LATE - 1) * phase(t, *RUN1)
    if t < RUN2[0]:
        return PUNCH + LATE
    return PUNCH + LATE + (STEPS - PUNCH - LATE) * phase(t, *RUN2)


def draw(c, t):
    top, bottom = frame(c, 8, 1, "ROLLBACK, STEP BY STEP",
                        "ILLUSTRATED: NO INPUT DELAY, EACH INPUT 3 STEPS (50 MS) LATE, 60 STEPS A SECOND.")
    g = clock(t)
    now = int(g + 1e-6)
    struck = t >= STRIKE

    panel_h = 103
    p = c.panel(0, top + 1, 320, panel_h, "ONE MATCH, TWO GAMES", color=c.light(ENGINE),
                sub="EACH GUESSES THE OTHER BY REPEATING HIS LAST INPUT")
    note_x = p.x + LABEL_W + STEPS * CELL + 3
    indent = c.measure("1 ")
    x0 = p.x + LABEL_W

    def cx(step):
        return x0 + (step - 1) * CELL

    numbers_y = p.y + 8
    rewind_y = numbers_y + 7
    rows = {"you": rewind_y + 9, "friend_guess": rewind_y + 20}
    gutter = rows["friend_guess"] + 11
    rows["friend"] = gutter + 12
    rows["you_guess"] = rows["friend"] + 11

    c.text(p.x, p.y, "YOUR GAME", c.light(ENGINE))
    c.text(p.x + 40, p.y, "· ITS GUESSES OF YOUR FRIEND", "dim")
    c.text(p.x2, p.y, "← GUARD · → WALK · P PUNCH", "dim", align="right")
    c.text(p.x, rows["you_guess"] + 13, "YOUR FRIEND'S GAME", c.light(ENGINE))
    c.text(p.x + 76, rows["you_guess"] + 13, "· ITS GUESSES OF YOU: ALL RIGHT, NOTHING PLAYED AGAIN", "dim")
    for key, label in (("you", "YOU"), ("friend_guess", "FRIEND"), ("friend", "FRIEND"), ("you_guess", "YOU")):
        c.text(p.x, rows[key] + 2, label, "text" if key in ("you", "friend") else "dim")
    c.text(p.x, numbers_y, "STEP", "dim")
    for s in range(1, STEPS + 1):
        c.text(cx(s) + CELL // 2, numbers_y, str(s), "white" if s == now else "dim", align="center")

    # The column being played: white as the games step, green while the rollback sweeps 5 to 8.
    sweeping = REPLAY[0] <= t < REPLAY[1]
    col = PUNCH + int((LATE + 1) * phase(t, *REPLAY) - 1e-6) if sweeping else now
    c.box(cx(col), rows["you"] - 2, CELL - 1, rows["you_guess"] + 11 - rows["you"] + 2,
          ENGINE if sweeping else "white")

    def chip(x, y, s, colour, border="line"):
        return c.tag(x, y, s, colour, border=border)

    for s in range(1, STEPS + 1):
        x = cx(s) + 2
        if g >= s:
            chip(x + 6, rows["you"], YOU[s - 1], "white")
            chip(x + 6, rows["friend"], FRIEND[s - 1], "white")
            chip(x + 6, rows["you_guess"], YOU[s - 1], "white" if g >= s + LATE else "dim",
                 border="line" if g >= s + LATE else "raised")
        # Your game's guess of the friend, then what really came.
        if g < s:
            continue
        real = g >= s + LATE
        wrong = PUNCH <= s < PUNCH + LATE
        if wrong and struck:
            old = chip(x, rows["friend_guess"], "→", "dim", border="raised")
            c.line(old.x, old.y2 - 1, old.x2 - 1, old.y, "red")
            chip(x + 11, rows["friend_guess"], "P", "white" if real else "dim", border="line" if real else "raised")
        else:
            guess = FRIEND[s - 1] if s < PUNCH or s >= PUNCH + LATE else "→"
            chip(x + 6, rows["friend_guess"], guess, "white" if real else "dim", border="line" if real else "raised")

    # The friend's inputs on their way: each leaves at its step and lands three steps later.
    for s in range(1, STEPS + 1):
        k = (g - s) / LATE
        if 0 <= k < 1:
            px = cx(s) + CELL // 2
            y = round(rows["friend"] - 3 + (rows["friend_guess"] + 11 - rows["friend"]) * k)
            packet(c, px, y, "white" if FRIEND[s - 1] == "P" else c.light(NET))
    c.text(p.x, gutter + 2, "SENT", "dim")

    # The punch lands late: the wrong guesses struck, back to step 5, 5 to 7 played again and 8 for the first time.
    if t >= ARRIVE:
        c.text(note_x, gutter - 1, "1 STEP 5'S PUNCH", "white")
        c.text(note_x + indent, gutter + 6, "3 STEPS LATE", "white")
    if t >= BACK[0]:
        reach = round((cx(PUNCH + LATE) + CELL // 2 - cx(PUNCH) - 3) * ease_in_out(phase(t, *BACK)))
        end = cx(PUNCH + LATE) + CELL // 2
        c.hline(end - reach, rewind_y + 3, reach, "red")
        if phase(t, *BACK) >= 1:
            c.arrow(end, rewind_y + 3, cx(PUNCH) + 3, rewind_y + 3, "red")
            c.text(note_x, rewind_y + 1, "2 BACK TO STEP 5", c.light("red"))
    if t >= REPLAY[1]:
        c.hline(cx(PUNCH) + 1, rows["friend_guess"] + 10, (LATE + 1) * CELL - 3, ENGINE)
        c.text(note_x, rows["you"] + 2, "3 5 TO 7 AGAIN", c.light(ENGINE))
        c.text(note_x + indent, rows["friend_guess"] + 2, "AND 8, AT ONCE", c.light(ENGINE))

    # What the rule is, and what it costs.
    fy = top + 1 + panel_h + 2
    f = c.panel(0, fy, 320, bottom - fy - 2, "THE LIMITS", color=c.light(NET), sub="AS BUILT, 7 OCT")
    for i, (big, line) in enumerate((("8", "STEPS OF GUESSING AT MOST, THEN IT WAITS"),
                                     ("<1 MS", "TO PLAY 8 STEPS AGAIN, ON A LAPTOP"),
                                     ("0 TO 2", "STEPS OF INPUT DELAY, FROM THE ROUND TRIP"))):
        fx = f.x + i * 104
        w = c.text(fx, f.y, big, "white", font="large")
        c.paragraph(fx + w + 4, f.y, line, 100 - w - 6, "text")


export(draw, __file__, seconds=7, fps=20, hold=3)
