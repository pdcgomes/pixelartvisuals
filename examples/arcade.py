"""Arcade attract screen: marching invaders, a passing saucer, a rainbow HALL OF FAME, the score table
with a freshly entered name, and a blinking INSERT COIN."""

from pathlib import Path

from pixelkit import animate

SQUID = (["...##...", "..####..", ".######.", "##.##.##", "########", "..#..#..", ".#.##.#.", "#.#..#.#"],
         ["...##...", "..####..", ".######.", "##.##.##", "########", ".#.##.#.", "#......#", ".#....#."])
CRAB = (["..#.....#..", "...#...#...", "..#######..", ".##.###.##.", "###########", "#.#######.#",
         "#.#.....#.#", "...##.##..."],
        ["..#.....#..", "#..#...#..#", "#.#######.#", "###.###.###", "###########", ".#########.",
         "..#.....#..", ".#.......#."])
UFO = [".....######.....", "...##########...", "..############..", ".##.##.##.##.##.", "################",
       "..###..##..###..", "...#........#..."]
CANNON = ["......#......", ".....###.....", ".....###.....", ".###########.", "#############",
          "#############", "#############"]
RAINBOW = ["red", "orange", "gold", "lime", "cyan", "sky", "violet"]
SCORES = [(99999, "PIX", 32), (87650, "ACE", 28), (76540, "NEO", 25), (65430, "ZAP", 22), (54320, "MOM", 19),
          (43210, "CPU", 16), (32100, "LOL", 12), (21000, "DAD", 9), (12340, "YOU", 6), (10000, "AAA", 5)]
ORDINALS = ["1ST", "2ND", "3RD", "4TH", "5TH", "6TH", "7TH", "8TH", "9TH", "10TH"]


def triangle(t, steps):
    """0, 1, ... steps, ... 1, 0 over one loop, in whole steps."""
    k = int(t * 2 * steps) % (2 * steps)
    return k if k <= steps else 2 * steps - k


def draw(c, t):
    c.rect(0, 0, 320, 180, "#000000")
    c.text(6, 3, "1UP", "red")
    c.text(22, 3, "12,340", "white")
    c.text(160, 3, "HI-SCORE 99,999", "white", align="center")
    c.text(314, 3, "2UP 00000", "dim", align="right")

    ux = round(-20 + t * 360)
    c.sprite(ux, 11, UFO, {"#": "red"})

    step = triangle(t, 8)
    legs = step % 2
    march = 2 * step - 8
    for row, (frames, color, w) in enumerate([(SQUID, "violet.light", 8), (CRAB, "cyan", 11)]):
        for i in range(10):
            x = 160 - 10 * 18 // 2 + i * 18 + (18 - w) // 2 + march
            c.sprite(x, 21 + row * 11, frames[legs], {"#": color})

    title = "HALL OF FAME"
    tw = c.measure(title, "large", 2)
    x = 160 - tw // 2
    shift = int(t * 14)
    for i, ch in enumerate(title):
        if ch != " ":
            c.text(x, 43, ch, RAINBOW[(i + shift) % len(RAINBOW)], font="large", scale=2, shadow="#3a1418")
        x += c.measure(ch + "A", "large", 2) - c.measure("A", "large", 2)

    cols = (84, 150, 178, 236)
    head_y = 62
    for x, label, align in zip(cols, ["RANK", "SCORE", "NAME", "STAGE"], ["left", "right", "left", "right"]):
        c.text(x, head_y, label, "white", align=align)
    c.dots(84, head_y + 7, 152, "line")
    blink = (t * 8) % 2 < 1.2
    for i, (score, name, stage) in enumerate(SCORES):
        y = head_y + 10 + i * 8
        color = RAINBOW[i % len(RAINBOW)]
        if name == "YOU":
            if not blink:
                continue
            color = "white"
        c.text(cols[0], y, ORDINALS[i], color)
        c.text(cols[1], y, c.num(score), color, align="right")
        c.text(cols[2], y, name, color)
        c.text(cols[3], y, str(stage), color, align="right")
    c.text(250, head_y + 10 + 8 * 8, "← NEW!", "gold" if blink else "orange")

    if (t * 4) % 2 < 1:
        c.text(160, 157, "INSERT COIN", "gold", font="large", align="center")
    c.hline(0, 174, 320, "lime")
    cx = 24 + 6 * triangle(t, 6)
    c.sprite(cx, 167, CANNON, {"#": "lime"})
    for bx in (226, 270):
        c.rect(bx, 168, 14, 6, "lime.dark")
        c.rect(bx + 4, 171, 6, 3, "#000000")
    c.text(314, 175, "CREDIT 00", "white", align="right")


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=4, fps=8, seamless=True, poster=0.0)
