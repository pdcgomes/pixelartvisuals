"""9.3 Filming the game a frame at a time: the trailer tool steps the game's own loop exactly 1/60 s
per frame and grabs each picture, the music is rendered offline, and the montage cuts land on the
music's bar lines.

Moves: a playhead sweeps five and a half bars of the montage (bars 10 to 15.5). Above it, a small
stand-in of the game screen shows the shot under the playhead (two figures and a blow, drawn here,
not the game's art), the frame counter steps on with its exact time (frame / 60), and the strip of
grabbed frames scrolls as each is taken. The pictures track lights up to the playhead; the music's
waveform is all there from the start, since it was rendered before the cut. Loops seamlessly.

Numbers, from tools/trailer.py at alfamafighterturbo 74e2f64 (its docstring and montage()):
- every frame exactly 1/60 s after the last, Math.random seeded, requestAnimationFrame taken over;
- the music's grid: 150 BPM, a bar of four beats is 96 frames, 1.6 s;
- the montage's shots on these bars: bar 10 A Avó's Já Vais Ver! (Bairro Alto, 1 bar), bar 11
  D. Afonso's Investida (the castle, 1 bar), bar 12 A Padeira's Fornada (Belém, 1.5 bars), bar 13.5
  A Varina's Sardinha Viva meeting Camões's Verso (Cais do Sodré, 1 bar), bar 14.5 Adamastor's Trovão
  (Santa Catarina, 1 bar);
- the montage: 27 bars, 43.2 s, the intro's cue then the title theme, rendered with render_audio.py.
Frame numbers are the montage's (bar x 96).
"""

import math
import random

from PIL import Image

from series import ART, AUDIO, TOOLS, export, frame

BAR, FPS = 96, 60
START, END = 10.0, 15.5
SHOTS = [
    # from bar, bars, who, what and where, the stage's sky and floor, the fighters' colours
    (10.0, 1.0, "A AVÓ", "A AVÓ'S JÁ VAIS VER!, BAIRRO ALTO", ("#1c2440", "#3a3348"), ("sky.light", "orange")),
    (11.0, 1.0, "D. AFONSO", "D. AFONSO'S INVESTIDA, THE CASTLE", ("#4f7fb8", "#7d7466"), ("blue.light", "orange")),
    (12.0, 1.5, "A PADEIRA", "A PADEIRA'S FORNADA, BELÉM", ("#8fc3e8", "#b9ad95"), ("orange", "sky.light")),
    (13.5, 1.0, "A VARINA", "A VARINA'S SARDINHA VIVA, CAIS DO SODRÉ", ("#5a8cc0", "#6a6a72"), ("red.light", "green.light")),
    (14.5, 1.0, "ADAMASTOR", "ADAMASTOR'S TROVÃO, SANTA CATARINA", ("#2a2040", "#4a4458"), ("green.dark", "white")),
]
SHOT_COLOURS = ["red", "orange", "gold", "sky", "violet"]
SCREEN_W, SCREEN_H = 104, 56

FIGHTER = [
    "..hh..",
    "..hh..",
    ".bbbb.",
    "bbbbbb",
    "b.bb.b",
    "..bb..",
    ".l..l.",
    ".l..l.",
    "l....l",
]


def shot_at(bar):
    return next(i for i, (b, n, *_) in enumerate(SHOTS) if b <= bar < b + n) if START <= bar < END else len(SHOTS) - 1


def screen(c, x, y, w, h, f):
    """A stand-in of the game's picture at montage frame f: the shot's stage and two figures."""
    i = shot_at(f / BAR)
    b, n, _, _, (sky, floor), (left, right) = SHOTS[i]
    local = f - round(b * BAR)
    c.rect(x, y, w, h, sky)
    r = random.Random(i)
    bx = x
    while bx < x + w:
        bw, bh = r.randint(8, 18), r.randint(10, 26)
        c.rect(bx, y + h - 12 - bh, min(bw, x + w - bx), bh, c.dark(floor) if i != 2 else "#e8e0cc")
        bx += bw + r.randint(0, 3)
    c.rect(x, y + h - 12, w, 12, floor)
    c.hline(x, y + h - 12, w, "line")
    if i == len(SHOTS) - 1 and local % 48 < 4:
        c.line(x + w - 20, y, x + w - 28, y + h - 13, "white")
    sway = round(2 * math.sin(f / 9))
    lx, rx = x + w // 2 - 30 + sway, x + w // 2 + 18 - sway
    fy = y + h - 26
    c.sprite(lx, fy, FIGHTER, {"h": "white", "b": left, "l": "dim"}, scale=2, flip=False)
    c.sprite(rx, fy, FIGHTER, {"h": "white", "b": right, "l": "dim"}, scale=2, flip=True)
    hit = local % 48
    if hit < 24:
        px = lx + 13 + round((rx - lx - 16) * hit / 24)
        c.rect(px, fy + 6, 4, 3, "white")
    elif hit < 30:
        c.rect(rx - 2, fy + 2, 3, 12, "gold")


def thumb(c, x, y, f):
    """The same picture at a quarter of the size, as a frame in the strip."""
    sub = c.sub(SCREEN_W, SCREEN_H)
    screen(sub, 0, 0, SCREEN_W, SCREEN_H, f)
    c.paste(sub.img.resize((SCREEN_W // 4, SCREEN_H // 4), Image.Resampling.NEAREST), x, y)


def wave(col):
    """The music's level at a column of the music track: four beats a bar, seeded jitter."""
    beat = col % 14
    r = random.Random(col).random()
    return 0.35 + 0.45 * max(0, 1 - beat / 6) + 0.2 * r


def draw(c, t):
    top, bottom = frame(c, 9, 3, "FILMING THE GAME A FRAME AT A TIME",
                        "FIGHTERS ABOVE ARE STAND-INS, NOT THE GAME'S ART. TRAILER OF 9 OCT 2026: 27 BARS, 43.2 S.")
    f = round(START * BAR + (END - START) * BAR * t)
    i = shot_at(f / BAR)

    # The game, stepped by the tool.
    game = c.panel(0, top + 1, 112, 76, "THE GAME", color=c.light(ART), sub="AS IT DRAWS")
    screen(c, game.x, game.y + 1, SCREEN_W, SCREEN_H, f)
    c.box(game.x - 1, game.y, SCREEN_W + 2, SCREEN_H + 2, "line")

    tool = c.panel(114, top + 1, 206, 76, "THE TOOL STEPS IT", color=c.light(TOOLS), sub="NO CLOCK, NO SCREEN RECORDING")
    c.kv(tool.x, tool.y, 116, [("FRAME", c.num(f)), ("TIME", f"{f / FPS:.3f} S"), ("STEP", "EXACTLY 1/60 S"),
                               ("RANDOM", "SEEDED")])
    c.text(tool.x + 122, tool.y, "THEN GRABS IT", "white")
    c.text(tool.x + 122, tool.y + 7, "SAME SEED,", "dim")
    c.text(tool.x + 122, tool.y + 14, "SAME FIGHT", "dim")
    c.text(tool.x, tool.y + 30, "SHOT: " + SHOTS[i][3], "text")
    # The strip of grabbed frames, newest at the right.
    tw, th = SCREEN_W // 4, SCREEN_H // 4
    sx, sy = tool.x + 1, tool.y + 41
    c.rect(sx - 1, sy - 3, tool.w + 1, th + 6, "shadow")
    for k in range(7):
        fx = sx + k * (tw + 2)
        thumb(c, fx, sy, max(round(START * BAR), f - (6 - k)))
        c.box(fx - 1, sy - 1, tw + 2, th + 2, "white" if k == 6 else "line")
    for hx in range(sx, sx + tool.w - 1, 4):
        c.rect(hx, sy - 3, 2, 1, "dim")
        c.rect(hx, sy + th + 2, 2, 1, "dim")

    # The cut, on the music's bar lines.
    tl = c.panel(0, top + 79, 320, bottom - top - 81, "THE CUT", color="white", sub="SHOTS LAID ON THE MUSIC'S BAR LINES",
                 right="150 BPM · A BAR = 96 FRAMES = 1.6 S", right_color="text")
    x0, unit = tl.x, (tl.w - 2) / (END - START)

    def X(bar):
        return tl.x + round((bar - START) * unit)

    ruler_y, pics_y, music_y = tl.y + 1, tl.y + 9, tl.y + 23
    head = X(f / BAR)
    for b in range(int(START), int(END) + 1):
        c.text(X(b) + 2, ruler_y, f"BAR {b}" if b < END else "", "dim")
    for k, (b, n, who, *_rest) in enumerate(SHOTS):
        a, z = X(b), X(b + n) - 1
        colour = SHOT_COLOURS[k]
        c.rect(a, pics_y, z - a, 11, c.dark(colour))
        lit = min(z, head) - a
        if lit > 0:
            c.rect(a, pics_y, lit, 11, colour)
        c.text(a + 3, pics_y + 3, who, "white")
    for col in range(tl.x, tl.x2 - 1):
        h = round(5 * wave(col - tl.x))
        c.vline(col, music_y + 5 - h, 2 * h + 1, c.light(AUDIO) if col < head else AUDIO)
    c.text(tl.x2, music_y + 13, "THE MUSIC, RENDERED OFFLINE FIRST", c.light(AUDIO), align="right")
    for b, n, *_ in SHOTS:
        c.vline(X(b), pics_y - 1, 13, "white")
    c.vline(X(END) - 1, pics_y - 1, 13, "white")
    for b in range(int(START), int(END) + 1):
        c.vline(X(b), music_y - 1, 13, "line")
    c.vline(head, ruler_y + 6, music_y + 13 - ruler_y - 6, c.light(TOOLS))
    c.text(tl.x, music_y + 13, "WHITE LINES: CUTS, ON A BAR OR HALF A BAR", "text")


export(draw, __file__, preset="wide", seconds=8, fps=20, seamless=True, poster=0.42)
