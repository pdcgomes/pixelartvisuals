"""Personal site, the story's third act: breadth. Pedro on a tiny planet, with the domains he's worked
in orbiting it like moons, each lighting up as the narration on the right types out its line."""

import math
import random
from pathlib import Path

from pixelkit import Canvas, animate
from pixelkit.fonts import FONTS

CX, CY = 103, 86
# Each world: its orbit (x radius; the y radius is half, as the kit's isometric 2:1), its start angle,
# speed in turns a loop, colour, size, and the line the narration types as it lights up.
WORLDS = [
    ("BANKING", 30, 0.10, 1.0, "red", 3.0, "A BANK'S PAYROLL."),
    ("TELECOM", 30, 0.60, 1.0, "orange", 3.5, "PHONE NETWORKS AND NUMBER PORTABILITY."),
    ("HEALTH", 52, 0.30, 0.6, "lime", 3.0, "HOSPITALS TALKING HL7."),
    ("TELEVISION", 52, 0.75, 0.6, "sky", 4.0, "A REMOTE FOR THE COUNTRY'S TV."),
    ("EDUCATION", 52, 0.05, 0.6, "cyan", 3.5, "CLASSROOMS ON IPADS."),
    ("NEWS", 76, 0.20, 0.4, "violet", 4.0, "NEWSROOMS, MARKETS AND LIVE SPORT."),
    ("MESSAGING", 76, 0.50, 0.4, "lime.light", 5.0, "MESSAGES FOR BILLIONS."),
    ("AR AUDIO", 76, 0.85, 0.4, "sky.light", 4.0, "SOUND FOR AUGMENTED REALITY."),
    ("GLASSES", 94, 0.40, 0.3, "red.light", 3.0, "GLASSES WITH A CAMERA."),
    ("DEV TOOLS", 94, 0.90, 0.3, "gold", 3.5, "TOOLS FOR THOUSANDS OF ENGINEERS."),
]
OUTRO = "EACH ONE A NEW LANGUAGE, LEARNED FAST. THAT'S THE PART I LIKE."
HERO = ["..hh..", ".hhhh.", "..ss..", ".bbbb.", "bbbbbb", "..bb..", ".b..b.", ".k..k."]
STEP, FLIGHT, TYPE_CPS = 1.1, 0.4, 32
SECONDS = len(WORLDS) * STEP + 3.2
STARS = [(random.Random(k).randrange(206), random.Random(k + 7).randrange(167), random.Random(k + 3).random())
         for k in range(80)]


def position(world, t):
    _, rx, start, speed, *_ = world
    a = 2 * math.pi * (start + speed * t)
    return CX + rx * math.cos(a), CY + rx / 2 * math.sin(a), math.sin(a)


def orbit(c, rx, color):
    for k in range(0, 360, 6):
        a = math.radians(k)
        c.px(round(CX + rx * math.cos(a)), round(CY + rx / 2 * math.sin(a)), color)


def scene(c, t, sec):
    c.rect(0, 0, c.w, c.h, "#05060f")
    for x, y, phase in STARS:
        on = (sec * 0.8 + phase) % 1 < 0.75
        c.px(x, y, "white" if on and phase > 0.6 else "dim" if on else "#14182a")
    lit = reached(sec)
    for rx in sorted({w[1] for w in WORLDS}):
        orbit(c, rx, "#1c2240")
    placed = sorted(((position(w, t), i, w) for i, w in enumerate(WORLDS)), key=lambda p: p[0][2])
    def body(i, w, x, y):
        name, *_, color, size, _ = w
        if i < lit:
            c.sphere(x, y, size, color)
        else:
            c.circle(x, y, size, "#14182a", outline="#2a3050")
    for (x, y, depth), i, w in placed:
        if depth < 0:
            body(i, w, x, y)
    c.sphere(CX, CY, 11, "#c8a860", shades=["#6a5428", "#a08848", "#c8a860", "#f0d890"])
    c.sprite(CX - 3, CY - 18, HERO, {"h": "#3a2a20", "s": "#f0c8a0", "b": "sky", "k": "#202024"})
    for (x, y, depth), i, w in placed:
        if depth >= 0:
            body(i, w, x, y)
    k = int(sec / STEP)
    if k < len(WORLDS):
        (x, y, _), name = position(WORLDS[k], t), WORLDS[k][0]
        since = sec - k * STEP
        if since < FLIGHT:
            rocket(c, sec, k)
            return
        if since < FLIGHT + 0.25:
            c.circle(x, y, WORLDS[k][5] + 3 + (since - FLIGHT) * 12, None, outline="white")
        w = c.measure(name) + 6
        tx = max(1, min(c.w - w - 1, round(x - w / 2)))
        ty = round(y + WORLDS[k][5] + 4)
        c.rect(tx, ty, w, 9, "#000000")
        c.box(tx, ty, w, 9, WORLDS[k][4])
        c.text(tx + 3, ty + 2, name, "white", check=False)


def reached(sec):
    """How many worlds the rocket has landed on."""
    k = int(sec / STEP)
    return min(len(WORLDS), k + (1 if sec - k * STEP >= FLIGHT else 0))


def rocket(c, sec, k):
    """A spark flying from Pedro's planet to world k, with a trail of embers."""
    since = sec - k * STEP
    for j in range(7):
        p = max(0.0, since - j * 0.025) / FLIGHT
        (x, y, _) = position(WORLDS[k], (sec - j * 0.025) / SECONDS)
        sx, sy = CX, CY - 12
        e = p * p * (3 - 2 * p)
        px, py = sx + (x - sx) * e, sy + (y - sy) * e - 14 * math.sin(math.pi * e)
        c.px(round(px), round(py), ["white", "gold", "gold", "orange", "orange", "red", "red.dark"][j])


def typed(c, x, y, w, parts, rows):
    """Word-wrapped (text, colour, characters shown) parts, typed out with a block cursor, showing
    only the last `rows` lines, like a terminal that scrolls."""
    lines, cursor = [], None
    for text, color, chars in parts:
        left = chars
        for line in FONTS["small"].wrap(text, w):
            if left <= 0 and cursor is not None:
                break
            shown = line[: max(0, left)]
            lines.append((shown, color))
            if left < len(line):
                cursor = len(lines) - 1
                break
            left -= len(line) + 1
        if chars < len(text):
            break
    view = lines[-rows:]
    for i, (shown, color) in enumerate(view):
        width = c.text(x, y + i * 7, shown, color, check=False) if shown else 0
        if cursor is not None and i == len(view) - 1 and len(lines) - 1 == cursor:
            c.rect(x + width + 1, y + i * 7, 3, 5, "white")


def draw(c, t):
    sec = t * SECONDS
    top = c.header("PEDRO GOMES", sub="PDCGOMES", right="STORY · ACT III OF VI")
    m = Canvas(206, c.h - top, theme=c.theme)
    scene(m, t, sec)
    c.img.paste(m.img, (0, top))

    card = c.panel(208, top + 1, 112, 120, "ACT III", color="gold")
    c.text(card.x, card.y + 1, "MANY WORLDS", "white", font="large")
    lit = reached(sec)
    parts = []
    for i, w in enumerate(WORLDS[:lit]):
        landed = i * STEP + FLIGHT
        parts.append((w[6], "text", min(len(w[6]), int((sec - landed) * TYPE_CPS))))
    outro_at = len(WORLDS) * STEP + 0.3
    if sec >= outro_at:
        parts.append((OUTRO, "gold", min(len(OUTRO), int((sec - outro_at) * TYPE_CPS))))
    typed(c, card.x, card.y + 14, card.w, parts, 13)

    stats = c.panel(208, top + 123, 112, c.h - top - 125, "PEDRO", color="dim")
    c.kv(stats.x, stats.y + 1, stats.w, [("WORLDS", f"{lit}"), ("TRAIT", "BREADTH" if sec >= outro_at else "...")])


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=SECONDS, fps=10, hold=2.5, poster=1.0)
