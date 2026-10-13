"""6.1 The match conducts the band: one stage theme's four layers as tracker rows, bar by bar, through
an example first round and an example final round on Alfama's theme.

Animated: a playhead runs through round 1, then the final round. The lower of the two fighters' health
falls in steps above the rows; the layers' cells fill as the playhead passes, and each rule's box
lights the moment it acts. Every label is on screen from the first frame. Holds on the final frame.

What it shows, from the game's audio bible at 74e2f64 (sections 1.4, 3.1 to 3.7, 4.2 and 9.1):
- The four layers: core (viola, bass, main drums) and lead (the guitarra's melody) play from "FIGHT!";
  duet (a second guitarra and the pad) at level 2 and in the final round; rush (extra percussion and a
  pumping octave bass that replaces the core bass) in danger (3.1).
- Level 2, the duet, from round 2 on and in round 1 once either fighter is at 60% health or less; it
  enters at the next four-bar phrase (3.2, 3.7).
- Danger, once either fighter is at 25% or less: the tempo x1.125 (Alfama's 144 BPM becomes 162) and
  the rush layer, at the next bar line, until the round ends (1.4 rule 1, 3.3, 3.7, 9.1).
- The final round: the theme a semitone up (E minor to F minor for Alfama), the duet from the first
  bar (3.4, 9.1).
- The KO: the music cuts at the knockout blow, fading over 40 ms, the only change not on the beat
  (3.5, 3.7).
- The Turbo setting never changes the music's tempo (3.8).
The rounds themselves are examples: where the health falls and the knockouts land are made up for the
picture; the rules and the numbers are the game's.
"""

from pixelkit import Rect, ease_in_out, phase
from series import AUDIO, export, frame

BARS, BAR_W, ROW_H = 16, 13, 8
LAYERS = [
    # name, colour, instruments
    ("CORE", "orange", "VIOLA·BASS·DRUMS"),
    ("LEAD", "yellow", "GUITARRA"),
    ("DUET", "purple", "GUITARRA 2·PAD"),
    ("RUSH", "red", "PERCUSSION·BASS"),
]
# Two example rounds: health steps of the lower fighter (bar position, health), when each layer plays
# (bar positions), the trigger that queued it, and the knockout.
ROUNDS = [
    {"title": "ROUND 1", "sub": "E MINOR",
     "health": [(0, 1.0), (1.5, 0.88), (3.2, 0.76), (5.4, 0.58), (7.0, 0.5), (9.1, 0.38), (10.6, 0.22),
                (12.2, 0.12), (13.4, 0.0)],
     "duet": 8, "duet_cue": 5.4, "rush": 11, "rush_cue": 10.6, "ko": 13.4},
    {"title": "FINAL ROUND", "sub": "F MINOR, A SEMITONE UP",
     "health": [(0, 1.0), (1.8, 0.85), (3.5, 0.66), (5.0, 0.48), (6.6, 0.33), (7.5, 0.2), (9.0, 0.1),
                (10.4, 0.0)],
     "duet": 0, "duet_cue": None, "rush": 8, "rush_cue": 7.5, "ko": 10.4},
]
# The playhead's windows of t for each round.
SWEEPS = [(0.03, 0.44), (0.52, 0.86)]
RULES = [
    ("DUET · AT THE NEXT 4-BAR PHRASE", "purple", ["ONCE A FIGHTER IS AT 60% OR LESS,", "AND IN EVERY ROUND AFTER THE FIRST"]),
    ("DANGER · AT THE NEXT BAR", "red", ["ONCE A FIGHTER IS AT 25% OR LESS:", "TEMPO 144 → 162 BPM, RUSH JOINS"]),
    ("FINAL ROUND · FROM THE FIRST BAR", "violet", ["THE WHOLE THEME A SEMITONE UP,", "THE DUET PLAYING FROM THE START"]),
    ("KNOCKOUT · AT ONCE", "white", ["THE MUSIC CUTS ON THE BLOW,", "GONE IN 40 MS: THEN SILENCE"]),
]


def health_at(steps, p):
    return [h for b, h in steps if b <= p][-1]


def playhead(t, i):
    """Bar position of round i's playhead (None before it starts), stopping at its knockout."""
    a, b = SWEEPS[i]
    if t < a:
        return None
    return ROUNDS[i]["ko"] * ease_in_out(phase(t, a, b)) if t < b else ROUNDS[i]["ko"]


def cell_marks(c, layer, x, y, bar, colour, *, muted_bass=False):
    """The notes of one bar of one layer, tracker style, inside a 12x7 cell at (x, y)."""
    if layer == 0:
        for k in range(4):
            h = 3 if muted_bass and k % 2 == 0 else 5
            c.rect(x + 1 + k * 3, y + 6 - h, 2, h, colour)
    elif layer == 1:
        rise = (0, 2, 1, 3, 2, 0, 1, 3)[bar % 8]
        c.rect(x + 1, y + 1 + rise, 6, 2, colour)
        c.rect(x + 8, y + 4 - rise // 2, 3, 2, colour)
    elif layer == 2:
        c.rect(x + 1, y + 2 + bar % 2, 11, 2, colour)
    else:
        for k in range(6):
            c.rect(x + 1 + k * 2, y + 2 + (k % 2) * 2, 1, 3, colour)


def round_panel(c, t, i, x, y, w, h):
    r = ROUNDS[i]
    p = playhead(t, i)
    danger = p is not None and p >= r["rush"]
    knocked = p is not None and p >= r["ko"]
    bpm = "162 BPM" if danger else "144 BPM"
    body = c.panel(x, y, w, h, r["title"], color=AUDIO, sub=r["sub"],
                   right=[("TEMPO ", "dim"), (bpm, "white" if danger and not knocked else "text")])
    label_w = 86
    gx = body.x + label_w
    bx = lambda pos: gx + round(pos * BAR_W)  # noqa: E731

    # The lower fighter's health, with the two thresholds.
    hy, hh = body.y, 16
    c.text(body.x, hy + 1, "LOWER HEALTH", "dim")
    c.text(gx - 3, hy + 4, "60%", "purple.light", align="right")
    c.text(gx - 3, hy + 10, "25%", "red.light", align="right")
    c.rect(gx, hy, BARS * BAR_W, hh, "bg")
    y60, y25 = hy + round((1 - 0.6) * (hh - 1)), hy + round((1 - 0.25) * (hh - 1))
    c.dots(gx, y60, BARS * BAR_W, "purple.dark")
    c.dots(gx, y25, BARS * BAR_W, "red.dark")
    steps = r["health"]
    for (b0, v0), (b1, _) in zip(steps, steps[1:] + [(BARS, 0)]):
        if b0 > r["ko"]:
            break
        reached = p is not None and p >= b0
        top = hy + round((1 - v0) * (hh - 1))
        end = min(b1, p) if reached and p < b1 else b1
        colour = "green.light" if reached else "line"
        c.hline(bx(b0), top, max(1, bx(end if reached else b1) - bx(b0)), colour)
        if reached and p >= b1 and b1 <= r["ko"]:
            nxt = hy + round((1 - health_at(steps, b1)) * (hh - 1))
            c.vline(bx(b1), top, nxt - top + 1, colour)
            if b1 == r["ko"]:
                break
    # The cues: where a threshold is crossed, and the knockout.
    for cue, colour, thresh in ((r["duet_cue"], "purple", 0.6), (r["rush_cue"], "red", 0.25)):
        if cue is not None:
            on = p is not None and p >= cue
            cy = hy + round((1 - health_at(steps, cue)) * (hh - 1))
            c.rect(bx(cue) - 1, cy - 1, 3, 3, colour if on else "line")
    ko_on = knocked
    c.text(bx(r["ko"]) + 3, hy + 1, "KO", "white" if ko_on else "muted")

    # The layers, as tracker rows.
    ry = hy + hh + 2
    for k, (name, colour, inst) in enumerate(LAYERS):
        yy = ry + k * ROW_H
        c.text(body.x, yy + 1, name, colour)
        c.text(body.x + 20, yy + 1, inst, "dim")
        start = {0: 0, 1: 0, 2: r["duet"], 3: r["rush"]}[k]
        cue = {2: r["duet_cue"], 3: r["rush_cue"]}.get(k)
        for b in range(BARS):
            cx = bx(b) + 1
            if b >= r["ko"]:
                continue
            playing = b >= start and b < r["ko"]
            reached = p is not None and p > b
            if playing and reached:
                c.rect(cx, yy, BAR_W - 1, ROW_H - 1, c.dark(colour))
                current = p < b + 1 and not knocked
                cell_marks(c, k, cx, yy, b, "white" if current else colour,
                           muted_bass=k == 0 and b >= r["rush"])
            else:
                c.rect(cx, yy, BAR_W - 1, ROW_H - 1, "shadow")
                c.dots(cx + 2, yy + 3, BAR_W - 4, "raised", step=3)
        # A queued layer waits, dotted, from its cue to its bar line.
        if cue is not None and p is not None and p >= cue:
            c.dots(bx(cue), yy + 3, bx(min(p, start)) - bx(cue) + 1, colour)
    rows_h = len(LAYERS) * ROW_H
    # The knockout: the rows stop on the blow; silence after it.
    kx = bx(r["ko"])
    c.vline(kx, hy, hh + 2 + rows_h - 1, "white" if ko_on else "line")
    silent = Rect(kx + 2, ry, gx + BARS * BAR_W - kx - 2, rows_h - 1)
    c.text(silent.cx, silent.cy - 2, "SILENCE", "white" if ko_on else "muted", align="center")
    # Phrase lines every four bars, and the bar numbers.
    ny = ry + rows_h + 1
    for b in range(BARS):
        c.text(bx(b) + BAR_W // 2 + 1, ny, str(b + 1), "text" if b % 4 == 0 else "muted", align="center")
    for b in range(0, BARS + 1, 4):
        c.vline(bx(b), ry, rows_h - 1, "dim")
    # The playhead.
    if p is not None and not knocked:
        c.vline(bx(p), hy - 1, hh + 2 + rows_h + 1, "white")
    return r


def rules_fired(t):
    """Which rule boxes have acted by t: duet, danger, final round, knockout."""
    p0, p1 = playhead(t, 0), playhead(t, 1)
    r0, r1 = ROUNDS
    return [
        p0 is not None and p0 >= r0["duet"],
        p0 is not None and p0 >= r0["rush"],
        p1 is not None,
        p0 is not None and p0 >= r0["ko"],
    ]


FIRST = [next(n / 2000 for n in range(2001) if rules_fired(n / 2000)[k]) for k in range(len(RULES))]


def draw(c, t):
    top, bottom = frame(c, 6, 1, "THE MATCH CONDUCTS THE BAND",
                        "TWO EXAMPLE ROUNDS ON ALFAMA'S THEME; THE RULES ARE THE GAME'S.")
    panel_h = 72
    round_panel(c, t, 0, 0, top + 1, c.w, panel_h)
    round_panel(c, t, 1, 0, top + 2 + panel_h, c.w, panel_h)
    ry = top + 3 + 2 * panel_h
    fired = rules_fired(t)
    latest = max((k for k in range(len(RULES)) if fired[k]), key=lambda k: FIRST[k], default=None)
    boxes = Rect(0, ry, c.w, bottom - ry - 2)
    rows = boxes.rows(2, gap=1)
    for k, (title, colour, lines) in enumerate(RULES):
        r = rows[k // 2].cols(2, gap=1)[k % 2]
        on = fired[k]
        body = c.panel(r.x, r.y, r.w, r.h, title, color=colour if on else "muted",
                       border="white" if k == latest and t < 0.9 else "line")
        for j, line in enumerate(lines):
            c.text(body.x, body.y + j * 7, line, "text" if on else "dim")


if __name__ == "__main__":
    export(draw, __file__, preset="standard", seconds=9, fps=20, hold=3)
