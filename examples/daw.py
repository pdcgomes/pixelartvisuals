"""Pixel Loops Studio: a FruityLoops-style DAW. Channel rack of 16-step patterns, a piano roll and
a mixer with live meters; the playing step runs across one bar on a loop."""

from pathlib import Path

from pixelkit import animate

STEPS = 16
CHANNELS = [
    ("KICK", "red", {0, 4, 8, 12}), ("CLAP", "orange", {4, 12}), ("HI-HAT", "gold", {2, 6, 10, 14}),
    ("OPEN HAT", "yellow", {7, 15}), ("SNARE", "violet", {15}), ("BASS", "lime", {0, 3, 6, 8, 11, 14}),
    ("LEAD", "cyan", {0, 3, 6, 10, 12}), ("VOX", "sky", {8}),
]
LEAD = [(0, 0, 3), (3, 3, 3), (7, 6, 4), (5, 10, 2), (3, 12, 4)]
KEYS = 12
UI = {"bg": "#1c2026", "panel": "#2a3038", "dark": "#14171c", "step": "#3a414c", "step2": "#464e5a",
      "ink": "#d6dbe2", "orange": "#ff9a2a"}


def draw(c, t):
    step = round(t * STEPS) % STEPS
    c.rect(0, 0, 320, 180, UI["bg"])

    c.rect(0, 0, 320, 12, UI["dark"])
    c.text(4, 3, "PIXEL LOOPS", UI["orange"])
    c.text(52, 3, "STUDIO", "dim")
    for i, (glyph, colour) in enumerate((("play", "lime"), ("stop", "muted"))):
        c.rect(88 + i * 12, 2, 10, 8, UI["panel"])
        if glyph == "play":
            c.sprite(91, 3, ["#...", "##..", "###.", "##..", "#..."], {"#": colour})
        else:
            c.rect(103, 4, 4, 4, colour)
    c.circle(117.5, 6, 3.5, "red")
    c.rect(126, 2, 46, 8, "#000000")
    c.text(170, 3, "150.000", "lime", align="right")
    c.text(176, 3, "BPM", "dim")
    c.rect(194, 2, 52, 8, "#000000")
    c.text(244, 3, f"3:0{step // 4 + 1}:{(step % 4) * 24:02d}", UI["orange"], align="right")
    c.text(252, 3, "PAT 3", "white")
    c.text(286, 3, "CPU", "dim")
    c.meter(300, 4, 16, 4, 0.34, "lime", rim=False)

    # Channel rack.
    c.rect(0, 13, 197, 98, UI["panel"])
    c.text(4, 16, "CHANNEL RACK", "white")
    c.text(193, 16, "ALL", "dim", align="right")
    for row, (name, colour, hits) in enumerate(CHANNELS):
        y = 25 + row * 10
        c.circle(6, y + 3.5, 2.5, "lime" if row != 7 else "dim")
        c.rect(11, y, 46, 8, UI["dark"])
        c.text(14, y + 2, name, colour)
        for s in range(STEPS):
            x = 61 + s * 8 + (s // 4) * 2
            on = s in hits
            base = UI["step"] if (s // 4) % 2 == 0 else UI["step2"]
            fill = colour if on else base
            if s == step:
                fill = "white" if on else "#5d6676"
            c.rect(x, y, 7, 8, fill)
            if on:
                c.hline(x, y, 7, c.light(colour) if s != step else "white")
                c.hline(x, y + 7, 7, c.dark(colour))
    c.rect(61 + step * 8 + (step // 4) * 2, 105, 7, 2, UI["orange"])

    # Piano roll for the lead.
    px0, py0 = 199, 13
    c.rect(px0, py0, 121, 98, UI["dark"])
    c.text(px0 + 4, py0 + 3, "PIANO ROLL · LEAD", "cyan")
    gx, gy, cw, rh = px0 + 14, py0 + 12, 6, 7
    for k in range(KEYS):
        y = gy + (KEYS - 1 - k) * rh
        black = k % 12 in (1, 3, 6, 8, 10)
        c.rect(px0 + 2, y, 11, rh - 1, "#1a1a20" if black else "#d8dbe2")
        c.rect(gx, y, STEPS * cw, rh - 1, "#20242c" if black else "#262b34")
    for s in range(STEPS + 1):
        c.vline(gx + s * cw, gy, KEYS * rh - 1, "#3a414c" if s % 4 == 0 else "#2a3038")
    for key, start, length in LEAD:
        y = gy + (KEYS - 1 - key) * rh
        playing = start <= step < start + length
        colour = "white" if playing else "cyan"
        c.rect(gx + start * cw + 1, y, length * cw - 1, rh - 1, colour)
        c.hline(gx + start * cw + 1, y, length * cw - 1, "cyan.light" if not playing else "white")
        c.vline(gx + start * cw + 1, y, rh - 1, "cyan.dark")
    c.vline(gx + step * cw + cw // 2, gy - 2, KEYS * rh + 2, UI["orange"])

    # Mixer.
    c.rect(0, 112, 320, 68, UI["panel"])
    c.text(4, 115, "MIXER", "white")
    for i, (name, colour, hits) in enumerate(CHANNELS + [("MASTER", "white", set().union(*(h for *_, h in CHANNELS)))]):
        x = 6 + i * 35
        since = min(((step - h) % STEPS for h in hits), default=STEPS)
        level = max(0.1, 1 - since * 0.18) * (0.8 if name != "MASTER" else 1)
        c.rect(x, 124, 30, 50, UI["dark"])
        c.seg_column(x + 3, 127, 4, 34, level, "lime", seg=1, gap=1, empty="#20242c", cap="gold" if level > 0.85 else None)
        c.seg_column(x + 8, 127, 4, 34, level * 0.92, "lime", seg=1, gap=1, empty="#20242c")
        c.rect(x + 18, 127, 2, 34, "#000000")
        fader = 127 + round((1 - (0.7 if name != "MASTER" else 0.8)) * 30)
        c.rect(x + 15, fader, 8, 4, "muted")
        c.hline(x + 15, fader, 8, "white")
        c.text(x + 15, 165, name[:6] if name != "OPEN HAT" else "OHAT", colour, align="center")


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=1.6, fps=10, seamless=True)
