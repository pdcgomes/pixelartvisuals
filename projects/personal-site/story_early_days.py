"""Personal site, the story's first chapter: the early days as an Amiga demo. Copper bars, a
parallax starfield, the chapter's logo, the era's chips lighting in turn, and a sine scroller."""

import math
import random
from pathlib import Path

from pixelkit import Canvas, animate

SCROLL = ("SPECTRUM TAPES ... AN AMIGA AND A MODEM ... A BBS IN THE BEDROOM ... IRC AT 3 AM ... PASCAL, "
          "ASSEMBLY, LINUX ... GREETINGS TO EVERYONE WHO DIALLED IN ...   ")
CHIPS = [("SPECTRUM", "red"), ("AMIGA", "orange"), ("BBS", "gold"), ("IRC", "lime"), ("PASCAL", "cyan"),
         ("ASM", "sky"), ("LINUX", "violet"), ("GAMES", "red.light")]
COPPER = [["#2a0a10", "red.dark", "red", "red.light", "white", "red.light", "red", "red.dark", "#2a0a10"],
          ["#2a1a04", "orange.dark", "orange", "gold", "white", "gold", "orange", "orange.dark", "#2a1a04"],
          ["#04142a", "sky.dark", "sky", "sky.light", "white", "sky.light", "sky", "sky.dark", "#04142a"]]
SPEED = 90
STARS = [(random.Random(k).randrange(320), random.Random(k + 99).randrange(14, 150), 1 + k % 3) for k in range(70)]
SCALE = 2


def scroll_width(c):
    return c.measure(SCROLL, "large", SCALE) + 2 * SCALE


def draw(c, t, seconds):
    top = c.header("PEDRO GOMES", sub="PDCGOMES", right="STORY · CHAPTER 1 OF 5")
    c.rect(0, top, 320, 180 - top, "#000000")
    for x0, y, layer in STARS:
        x = round(x0 - t * 320 * layer) % 320
        c.px(x, y, ["dim", "text", "white"][layer - 1])

    for k, bar in enumerate(COPPER):
        y = round(70 + 46 * math.sin(2 * math.pi * (t * 2 + k / 3)))
        for j, color in enumerate(bar):
            c.hline(0, y + j, 320, color)

    c.text(160, 30, "CHAPTER 1", "gold", align="center", check=False)
    c.text(160, 40, "THE EARLY DAYS", "white", font="large", scale=3, align="center", shadow="sky.dark",
           outline="#000000", check=False)
    c.text(160, 66, "BEFORE IT WAS A JOB", "text", align="center", outline="#000000", check=False)

    chips_w = sum(c.measure(n) + 8 for n, _ in CHIPS) + 3 * (len(CHIPS) - 1)
    x = 160 - chips_w // 2
    lit = int(t * seconds * 2) % len(CHIPS)
    for i, (name, color) in enumerate(CHIPS):
        w = c.measure(name) + 8
        on = i == lit
        c.rect(x, 128, w, 11, color if on else "#000000")
        c.box(x, 128, w, 11, color)
        c.text(x + 4, 131, name, "#000000" if on else color, check=False)
        x += w + 3

    sub = Canvas(320, 32, theme=c.theme, bg="#000000")
    width = scroll_width(c)
    shift = round(t * width)
    pos = 320 - shift
    rainbow = ["red", "orange", "gold", "lime", "cyan", "sky", "violet"]
    advance = lambda ch: sub.measure(ch + "A", "large", SCALE) - sub.measure("A", "large", SCALE)
    for lap in (0, 1):
        x = pos + lap * width
        for i, ch in enumerate(SCROLL):
            a = advance(ch)
            if -20 < x < 340 and ch != " ":
                y = round(9 + 6 * math.sin(x / 26 + 2 * math.pi * t * 3))
                sub.text(x, y, ch, rainbow[(i // 3) % len(rainbow)], font="large", scale=SCALE, check=False)
            x += a
    c.img.paste(sub.img, (0, 146))
    c.hline(0, 145, 320, "dim")
    c.hline(0, 178, 320, "dim")


if __name__ == "__main__":
    probe = Canvas(preset="wide")
    seconds = scroll_width(probe) / SPEED
    animate(lambda c, t: draw(c, t, seconds), Path(__file__).with_suffix(".gif"), preset="wide",
            seconds=seconds, fps=12, seamless=True, poster=0.3)
