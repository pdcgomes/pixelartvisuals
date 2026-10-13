"""7.3 The credits on the medley's bars: the scene at the Pastelaria Paraíso is timed to its music, a
long medley of 74 bars at 100 BPM (a bar 2.4 s, 2 min 58 s in all). Each fighter walks in on his own
bar, the band opening out of the pastelaria's radio into the room for his turn; between the visits the
radio plays while the friends talk. Twice the tram 28 crosses the window, and while it covers the glass
the light outside jumps on (gold to sunset, sunset to dusk), so the time cut is never seen. On bar 73
the shutter starts down, and on bar 74 it's closed with THE END on it.

Animated intro, then a hold: a playhead sweeps the 74 bars, slowing at the two tram crossings and the
shutter; a small window above shows the light outside, the tram crossing in front of it as the light
changes, and the shutter coming down; a readout says the bar, the time, who's in the room and the
light. Every label stays on screen.

Numbers and sources (alfamafighterturbo at 74e2f64):
- 74 bars at 100 BPM, 2.4 s a bar, 177.6 s; THE END held 4 s: docs/plans/2026-10-09-credits-design.md,
  "In short", 3.2 and "Music delivered"; src/game/credits/script.ts MEDLEY (bars counted there from 0).
- The visits' bells and turns, 1-based here: A Padeira 5 (5 bars), A Avó 13 (5), A Varina 21 (3),
  Camões 27 (5), O Calceteiro 35 (5), Zé Povinho 43 (5), D. Afonso 51 (5), Adamastor 59 (5, or the
  storm passing on the radio when the run didn't meet him), O Fadista 68 (7): script.ts MEDLEY.visits.
- Trams in the radio's bars 32 and 48, a beat into the bar, 150 steps across the glass; the look changes
  72 steps after it starts, while it covers both: script.ts MEDLEY.trams, TRAM, TRAM_COVERS, credits().
  Gold, then sunset after the first, dusk and the lamps after the second: credits-design 1.3.
- Closing time bar 64, the radio off on bar 67's last beat, the shutter down from bar 73, closed and
  THE END on bar 74: script.ts MEDLEY.closing, off, run, chord; credits-design "Music delivered".
"""

from pixelkit import ease_in_out, lerp, phase
from series import export, frame

BAR_S = 2.4
VISITS = [("A PADEIRA", 5, 5), ("A AVÓ", 13, 5), ("A VARINA", 21, 3), ("CAMÕES", 27, 5), ("O CALCETEIRO", 35, 5),
          ("ZÉ POVINHO", 43, 5), ("D. AFONSO", 51, 5), ("ADAMASTOR", 59, 5), ("O FADISTA", 68, 7)]
TRAMS = [(32.25, "SUNSET"), (48.25, "DUSK")]
TRAM_BARS = 150 / 144
COVER_BARS = 72 / 144
SHUTTER = 73
LOOKS = {"GOLD": ("#f2c14e", "#e7a33a"), "SUNSET": ("#e8784a", "#b8486a"), "DUSK": ("#3a4a8a", "#232a55")}
LIGHT = {"GOLD": "gold", "SUNSET": "red", "DUSK": "blue"}
# The playhead's pace: (t, bar) knots, slow over the trams and the shutter.
KNOTS = [(0.0, 1.0), (0.12, 31.6), (0.27, 33.6), (0.40, 47.6), (0.55, 49.6), (0.70, 72.6), (0.88, 75.0)]


def bar_at(t: float) -> float:
    for (t0, b0), (t1, b1) in zip(KNOTS, KNOTS[1:]):
        if t <= t1:
            return lerp(b0, b1, phase(t, t0, t1))
    return KNOTS[-1][1]


def look_at(b: float) -> str:
    if b >= TRAMS[1][0] + COVER_BARS:
        return "DUSK"
    if b >= TRAMS[0][0] + COVER_BARS:
        return "SUNSET"
    return "GOLD"


def clock(b: float) -> str:
    s = max(0.0, (b - 1) * BAR_S)
    return f"{int(s // 60)}:{int(s % 60):02d}"


def draw(c, t):
    top, bottom = frame(c, 7, 3, "THE CREDITS ON THE MEDLEY'S BARS",
                        "ADAMASTOR COMES ONLY IF YOUR RUN MET HIM. IF NOT, A STORM PASSES.")
    b = bar_at(t)
    look = look_at(b)
    room, rest = c.bounds._replace(y=top + 1, h=bottom - top - 3).cut_top(66, gap=2)
    win_r, now_r = room.cols([128, 190])

    # The window: the street outside in its light, the tram, the shutter.
    win = c.panel(*win_r, "THE WINDOW", color="gold", sub="THE STREET OUTSIDE")
    wx, wy, ww, wh = win.x, win.y, win.w, win.h - 1
    sky, low = LOOKS[look]
    c.gradient(wx, wy, ww, wh - 14, [sky, low])
    for i, (x, w, h) in enumerate(((0, 22, 26), (24, 30, 32), (56, 18, 22), (76, 26, 30), (104, ww - 104, 24))):
        c.rect(wx + x, wy + wh - h, w, h, "#8a6a4e" if look != "DUSK" else "#4a3a46")
        for k in range(2, w - 3, 6):
            c.rect(wx + x + k, wy + wh - h + 5, 3, 4, "#ffd27a" if look == "DUSK" else "#5a4636")
    c.rect(wx, wy + wh - 5, ww, 5, "#6e6a64" if look != "DUSK" else "#3a3842")
    for (start, _) in TRAMS:
        p = (b - start) / TRAM_BARS
        if 0 <= p <= 1:
            tw = ww + 40
            tx = wx + ww - round(p * (ww + tw))
            ty = wy + wh - 30
            x0, x1 = max(wx, tx), min(wx + ww, tx + tw)
            if x1 > x0:
                c.rect(x0, ty, x1 - x0, 25, "yellow")
                c.rect(x0, ty + 18, x1 - x0, 2, "orange")
                for k in range(tx + 4, tx + tw - 8, 12):
                    if x0 <= k and k + 8 <= x1:
                        c.rect(k, ty + 4, 8, 9, "#2a3a4a")
    shut = phase(b, SHUTTER, SHUTTER + 1)
    if shut > 0:
        h = round(wh * shut)
        c.rect(wx, wy, ww, h, "#8a8f9a")
        for y in range(wy + 1, wy + h, 3):
            c.hline(wx, y, ww, "#6a6f7a")
        if shut >= 1:
            c.rect(wx + ww // 2 - 27, wy + wh // 2 - 7, 54, 14, "shadow")
            c.text(wx + ww // 2, wy + wh // 2 - 3, "THE END", "yellow", font="large", align="center")

    # What's happening on the bar the playhead is on.
    now = c.panel(*now_r, "NOW", color="white", sub="BAR · TIME · WHO · LIGHT")
    shown = min(74, max(1, int(b)))
    c.text(now.x, now.y, f"BAR {shown} OF 74", "white", font="large")
    c.text(now.x2 - 1, now.y, clock(min(b, 75)) if b < 75 else "2:58", "white", font="large", align="right")
    who = next((n for n, s, l in VISITS if s <= b < s + l), None)
    if b >= SHUTTER and b < 75:
        line, colour = ("THE SHUTTER COMES DOWN" if b < 74 else "THE END, HELD 4 S"), "yellow"
    elif b >= 75:
        line, colour = "THE END, HELD 4 S", "yellow"
    elif who:
        line, colour = f"IN THE ROOM: {who}", c.light("orange")
    elif 64 <= b < 68:
        line, colour = "CLOSING TIME, THE RADIO WINDS DOWN", "text"
    else:
        line, colour = "ON THE RADIO: THE FRIENDS TALK", "text"
    c.text(now.x, now.y + 14, line, colour)
    c.spans(now.x, now.y + 22, [("OUTSIDE: ", "dim"), (look, c.light(LIGHT[look]))])
    crossing = any(0 <= (b - s) / TRAM_BARS <= 1 for s, _ in TRAMS)
    c.text(now.x, now.y + 33, "THE TRAM CROSSES: THE LIGHT" if crossing else "", "yellow")
    c.text(now.x, now.y + 40, "JUMPS ON BEHIND IT" if crossing else "", "yellow")

    # The 74 bars.
    tl = c.panel(*rest, "74 BARS AT 100 BPM", color="orange", sub="A BAR 2.4 S · 2 MIN 58 S",
                 right=[("■", c.light("orange")), (" A FIGHTER'S TURN  ", "dim"), ("■", "raised"), (" THE RADIO", "dim")])
    x0, span = tl.x + 26, tl.w - 26

    def X(bar: float) -> int:
        return x0 + round((bar - 1) * span / 74)

    names_y, music_y = tl.y, tl.y + 19
    tram_y, light_y, axis_y = music_y + 9, music_y + 19, music_y + 28
    c.text(tl.x, music_y, "MUSIC", "dim")
    c.text(tl.x, tram_y, "TRAM", "dim")
    c.text(tl.x, light_y, "LIGHT", "dim")
    c.rect(X(1), music_y, X(75) - X(1), 6, "raised")
    for i, (name, start, length) in enumerate(VISITS):
        on = start <= b
        c.rect(X(start), music_y, X(start + length) - X(start) - 1, 6, c.light("orange") if on else "orange.dark")
        ny = names_y + (0 if i % 2 == 0 else 9)
        last = i == len(VISITS) - 1
        tick = names_y + 16 if last else ny + 6
        c.vline(X(start), tick, music_y - tick - 1, "line")
        c.text(X(start + length) if last else X(start), ny, name, "white" if on else "dim",
               align="right" if last else "left")
    for start, after in TRAMS:
        tx = X(start)
        c.rect(tx, tram_y, 6, 5, "yellow" if b >= start else "yellow.dark")
        c.text(tx + 9, tram_y, f"TO {after}", c.light(LIGHT[after]) if b >= start else "dim")
    c.rect(X(SHUTTER), tram_y, X(75) - X(SHUTTER), 5, "#8a8f9a" if b >= SHUTTER else "raised")
    c.text(X(SHUTTER) - 3, tram_y, "SHUTTER", "white" if b >= SHUTTER else "dim", align="right")
    edges = [1, TRAMS[0][0] + COVER_BARS, TRAMS[1][0] + COVER_BARS, 75]
    for (a, z), name in zip(zip(edges, edges[1:]), ("GOLD", "SUNSET", "DUSK")):
        c.rect(X(a), light_y, X(z) - X(a), 5, LIGHT[name] if b >= a else f"{LIGHT[name]}.dark")
    c.hline(X(1), axis_y, X(75) - X(1), "line")
    for bar, label in ((1, "0:00"), (26, "1:00"), (51, "2:00")):
        c.vline(X(bar), axis_y, 2, "dim")
        c.text(X(bar), axis_y + 3, f"{label} · BAR {bar}", "dim")
    c.text(X(75), axis_y + 3, "2:58 · 74", "dim", align="right")
    if b < 75:
        c.vline(X(b), names_y + 16, axis_y - names_y - 15, "white")


export(draw, __file__, preset="wide", seconds=10, fps=20, hold=3)
