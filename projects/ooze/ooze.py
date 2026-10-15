"""ooze in 30 seconds, for social posts (1280x720 MP4) and the README (a GIF at half the size). The
numbers are the made-up team of `ooze demo`, the one in ooze's screenshots.

    PYTHONPATH=skill/scripts python3 projects/ooze/ooze.py
    PYTHONPATH=skill/scripts python3 projects/ooze/ooze.py frames 3 9.5 14   # stills, for checking
"""

import math
import sys
from pathlib import Path

from PIL import Image

from pixelkit import Canvas, animate, ease_back, ease_in_out, ease_out, phase, reveal, stagger

HERE = Path(__file__).parent
TOP, BOTTOM = 13, 169  # the content between the header's rule and the footer's
WIPE = 0.9             # seconds the Slime takes to ooze one scene into the next

# The Slime's own colours, from badcoffee.dev's creature.png.
SLIME, SLIME_LIGHT, SLIME_DARK = "#04d6bd", "#6ee5bc", "#03a593"
INK, CREAM = "#02092c", "#fcf5e1"
SELECTION = "#283457"  # Tokyo Night's, as in ooze itself

SPRITE = Image.open(HERE / "slime.png").convert("RGBA")


def slime_image(big=False, blink=False):
    img = SPRITE.copy()
    if blink:
        # The eyes close: their whites take the outline's colour.
        px = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = px[x, y]
                if a and r > 200 and g > 200 and b > 180:
                    px[x, y] = (0x02, 0x09, 0x2C, 255)
    return img.resize((img.width * 2, img.height * 2), Image.NEAREST) if big else img


SLIMES = {(big, blink): slime_image(big, blink) for big in (False, True) for blink in (False, True)}


def slime(c, x, y, *, big=False, blink=False):
    c.image(SLIMES[(big, blink)], x, y, colors="keep")


def caption(c, s, title):
    c.text(8, 19, reveal(title, phase(s, 0.1, 0.6)), "white", font="large", scale=2, shadow="line")


def dot(c, x, y, col):
    c.rect(x, y + 1, 3, 3, col)


RING = [(1, 0), (2, 0), (3, 1), (3, 2), (2, 3), (1, 3), (0, 2), (0, 1)]


def spinner(c, x, y, s):
    """A build's spinner: a comet going round a ring of 8 pixels."""
    head = int(s * 14) % len(RING)
    for i, (dx, dy) in enumerate(RING):
        age = (head - i) % len(RING)
        if age < 3:
            c.px(x + dx, y + dy, ("blue.light", "blue", "blue.dark")[age])


def bars(c, x, base, values, top, h, *, w=4, gap=2, col=SLIME, light=SLIME_LIGHT, grow=None):
    for i, v in enumerate(values):
        g = 1.0 if grow is None else grow[i]
        bh = max(1 if v else 0, round(h * v / top * g))
        if bh:
            c.rect(x + i * (w + gap), base - bh, w, bh, col)
            c.hline(x + i * (w + gap), base - bh, w, light)


def deploy_row(c, r, y, s, glyph, project, env, when, what, *, what_col="text", live=None, selected=False):
    """A deployment, as ooze lists them: what it's doing, the project, where, when and what."""
    if selected:
        c.rect(r.x - 2, y - 2, r.w + 4, 9, SELECTION)
    if glyph == "spin":
        spinner(c, r.x, y, s)
    elif glyph:
        c.text(r.x, y, glyph, {"✓": "green", "×": "red"}[glyph])
    c.text(r.x + 8, y, project, "white")
    c.text(r.x + 64, y, env, "violet.light" if env == "PRODUCTION" else "dim")
    c.text(r.x + 112, y, when, "blue.light" if glyph == "spin" else "dim")
    c.text(r.x + 146, y, what, what_col)
    if live is not None and live > 0:
        lift = round((1 - ease_back(min(1, live))) * 3)
        c.tag(r.x + r.w, y - 2 + lift, "LIVE", "green", border="green.dark", align="right")


# ------------------------------------------------------------------ 1. who's online

MINUTES = [6, 7, 6, 8, 9, 8, 7, 9, 10, 9, 8, 10, 12, 11, 10, 12, 13, 12, 14, 13, 12, 14, 16, 15, 14, 17, 18, 16, 19,
           21, 20, 22, 24, 23, 25, 27, 26, 28]
PROJECTS = [("MOTH-RADIO", 34, 771, "green"), ("CAVE-NOTES", 4, 115, "green"), ("NIGHT-MARKET", 2, 124, "red")]
SPARKS = [[5, 6, 7, 6, 8, 9, 8, 10, 11, 10, 12, 14, 13, 15, 17, 16, 18, 20, 19, 22, 24, 23, 26, 25],
          [3, 2, 3, 4, 3, 2, 3, 3, 4, 3, 2, 4, 3, 3, 2, 3, 4, 3, 3, 4, 3, 2, 3, 3],
          [2, 3, 2, 2, 3, 2, 3, 3, 2, 2, 3, 2, 2, 3, 3, 2, 2, 3, 2, 3, 2, 2, 3, 2]]


def scene_online(c, p, s, d):
    caption(c, s + 0.6, "WHO'S ON YOUR SITES")  # titled from the first frame, which feeds show first
    q = c.panel(8, 44, 112, 62, "ONLINE NOW", color="cyan", sub="5 MIN")
    n = round(40 * ease_out(phase(s, 0.3, 1.6)))
    w = c.text(q.x, q.y + 2, str(n), SLIME, font="large", scale=3, shadow="dim")
    c.text(q.x + w + 5, q.y + 9, "VISITORS", "dim")
    c.text(q.x, q.y + 28, "TODAY 4,538 VISITORS", "text")
    c.text(q.x, q.y + 36, "8,124 PAGE VIEWS", "dim")

    r = c.panel(124, 44, 188, 62, "PAGE VIEWS A MINUTE", color="cyan", right="LAST 30 MIN", right_color="dim")
    shift = min(len(MINUTES) - 30, max(0, int((s - 1.9) / 0.5)))
    grow = [ease_out(stagger(phase(s, 0.2, 1.8), i, 30, overlap=0.85)) for i in range(30)]
    bars(c, r.x + 1, r.y + r.h, MINUTES[shift:shift + 30], max(MINUTES), 40, grow=grow)

    b = c.panel(8, 110, 304, 56, "PROJECTS", color="cyan", sub="BUSIEST FIRST")
    for i, (name, online, views, state) in enumerate(PROJECTS):
        shown = phase(s, 1.0 + i * 0.25, 1.3 + i * 0.25)
        if shown <= 0:
            continue
        y = b.y + 2 + i * 12
        dot(c, b.x, y, state)
        c.text(b.x + 7, y, name, "white")
        c.text(b.x + 112, y, f"{round(online * shown)} ONLINE", SLIME, align="right")
        spark = SPARKS[i]
        top = max(spark)
        for k, v in enumerate(spark[:round(len(spark) * shown)]):
            hh = max(1, round(7 * v / top))
            c.rect(b.x + 124 + k * 4, y + 6 - hh, 3, hh, SLIME if i == 0 else SLIME_DARK)
        c.text(b.x + b.w, y, f"{views} VIEWS/H", "text", align="right")


# ------------------------------------------------------------------ 2. deploys

LOG = [
    (0.2, "Cloning github.com/night-shift/moth-radio", "text"),
    (0.8, "Installing dependencies...", "text"),
    (1.4, 'Running "npm run build"', "text"),
    (2.2, "Compiled successfully in 18.2s", "text"),
    (2.9, "Deployment completed", "green.light"),
]
READY_AT = 3.1


def scene_deploys(c, p, s, d):
    caption(c, s, "DEPLOYS, AS THEY HAPPEN")
    r = c.panel(8, 44, 304, 48, "DEPLOYMENTS", color="sky", sub="EVERY PROJECT")
    if s < READY_AT:
        deploy_row(c, r, r.y + 2, s, "spin", "MOTH-RADIO", "PRODUCTION", f"0:{21 + int(s * 10):02d}", "TAGS ON EVERY NOTE")
    else:
        deploy_row(c, r, r.y + 2, s, "✓", "MOTH-RADIO", "PRODUCTION", "52 S", "TAGS ON EVERY NOTE",
                   live=phase(s, READY_AT, READY_AT + 0.3))
    if s > 0.5:
        deploy_row(c, r, r.y + 12, s, "×", "NIGHT-MARKET", "PRODUCTION", "5 MIN", "NPM RUN BUILD EXITED WITH 1",
                   what_col="red")
    if s > 0.8:
        deploy_row(c, r, r.y + 22, s, "✓", "CAVE-NOTES", "PREVIEW", "14 MIN", "TAGS ON EVERY NOTE")

    g = c.panel(8, 96, 304, 70, "BUILD LOG", color="sky", sub="MOTH-RADIO")
    shown = [(at, line, col) for at, line, col in LOG if s >= at]
    for k, (at, line, col) in enumerate(shown[-4:]):
        c.text(g.x, g.y + 1 + k * 11, reveal(line, phase(s, at, at + 0.4)), col, font="code")
    if s < READY_AT and int(s * 4) % 2 == 0:
        c.rect(g.x, g.y + 1 + min(len(shown), 4) * 11, 5, 8, "dim")


# ------------------------------------------------------------------ 3. spikes

SPIKE_BASE = [5, 6, 5, 7, 6, 5, 6, 7, 6, 5, 7, 6, 6, 7, 5, 6, 7, 6, 5, 6, 7, 6, 6, 7, 6, 5]
SPIKE = [24, 33, 41, 44, 38]


def scene_spike(c, p, s, d):
    caption(c, s, "SPIKES, AS THEY LAND")
    r = c.panel(8, 44, 196, 70, "MOTH-RADIO", color="cyan", sub="PAGE VIEWS A MINUTE")
    base = r.y + r.h
    top = max(SPIKE)
    bars(c, r.x + 1, base, SPIKE_BASE, top, 44, w=4, gap=2)
    jump = [ease_back(phase(s, 0.9 + k * 0.08, 1.3 + k * 0.08)) for k in range(len(SPIKE))]
    x0 = r.x + 1 + len(SPIKE_BASE) * 6
    for k, v in enumerate(SPIKE):
        h = round(44 * (6 + (v - 6) * jump[k]) / top)
        c.rect(x0 + k * 6, base - h, 4, h, "orange" if jump[k] > 0.2 else SLIME)
        c.hline(x0 + k * 6, base - h, 4, "orange.light" if jump[k] > 0.2 else SLIME_LIGHT)
    if s > 1.5:
        c.tag(r.x + r.w, r.y + 1, "4× ITS USUAL", "orange", border="orange.dark", align="right")

    f = c.panel(8, 118, 304, 48, "FEED", color="white")
    lines = [
        (1.3, "20:01", "↑", "teal", "MOTH-RADIO", "TRAFFIC 4× ITS USUAL · 204 VIEWS IN 5 MIN, 34 ONLINE", "text"),
        (2.7, "20:02", "!", "red", "GRIMOIRE-API", "5XX ON 7% OF 820 REQUESTS IN 5 MIN", "red.light"),
    ]
    for k, (at, when, glyph, gcol, who, what, col) in enumerate([line for line in lines if s >= line[0]]):
        y = f.y + 2 + k * 10
        c.text(f.x, y, when, "dim")
        c.text(f.x + 24, y, glyph, SLIME if gcol == "teal" else gcol)
        c.text(f.x + 30, y, who, "white")
        c.text(f.x + 84, y, reveal(what, phase(s, at, at + 0.5)), col)

    slide = ease_out(phase(s, 1.7, 2.2))
    if slide > 0:
        x = 322 - round((322 - 208) * slide)
        c.rect(x, 48, 104, 44, "panel")
        c.box(x, 48, 104, 44, SLIME_DARK)
        c.rect(x + 4, 52, 9, 9, SLIME)
        c.rect(x + 6, 54, 3, 3, CREAM)
        c.px(x + 7, 55, INK)
        if slide >= 1:
            c.text(x + 16, 54, "OOZE", "white")
            c.text(x + 100, 54, "NOW", "dim", align="right")
            c.text(x + 4, 66, "MOTH-RADIO:", "white")
            c.text(x + 4, 74, "TRAFFIC SPIKE", "white")
            c.text(x + 4, 83, "204 VIEWS IN 5 MIN", "dim")


# ------------------------------------------------------------------ 4. spend

SERVICES = [("DATA TRANSFER", 8.04), ("FLUID CPU", 6.25), ("EDGE REQUESTS", 4.12), ("BUILD MINUTES", 3.20),
            ("AI GATEWAY", 2.16)]
USAGE, CREDIT = 26.40, 20


def scene_spend(c, p, s, d):
    caption(c, s, "WHAT IT ALL COSTS")
    r = c.panel(8, 44, 196, 62, "BILLING", color="gold", sub="DAY 13 OF 31")
    usage = USAGE * ease_in_out(phase(s, 0.3, 2.1))
    share = usage / CREDIT
    col = "red" if share >= 1 else ("yellow" if share >= 0.75 else "green")
    w = c.text(r.x, r.y + 2, f"${usage:.2f}", col, font="large", scale=2, shadow="line")
    c.text(r.x + w + 4, r.y + 8, "OF $20 CREDIT", "text")
    if share >= 1:
        c.tag(r.x + r.w, r.y + 2, f"{share * 100:.0f}%", "red", border="red.dark", align="right")
    c.meter(r.x, r.y + 20, r.w, 6, min(1.0, share), col)
    if s > 2.3:
        c.text(r.x, r.y + 32, reveal("PROJECTED $68 BY 3 NOV · $48 OVER", phase(s, 2.3, 2.9)), "orange")

    v = c.panel(8, 110, 196, 56, "BY SERVICE", color="gold", right="THIS PERIOD", right_color="dim")
    for i, (name, cost) in enumerate(SERVICES):
        g = ease_out(stagger(phase(s, 0.6, 2.4), i, len(SERVICES), overlap=0.6))
        if g <= 0:
            continue
        y = v.y + i * 8
        c.text(v.x, y, name, "text")
        c.rect(v.x + 60, y, 92, 5, "raised")
        bw = round(92 * cost / SERVICES[0][1] * g)
        c.rect(v.x + 60, y, bw, 5, "gold")
        c.hline(v.x + 60, y, bw, "gold.light")
        c.text(v.x + v.w, y, f"${cost * g:.2f}", "white", align="right")

    q = c.panel(208, 44, 104, 62, "THE PLAN", color="gold")
    c.kv(q.x, q.y + 1, q.w, [("PRO PLAN", "$20/MO"), ("EXTRA SEAT", "$20/MO"), ("CREDIT", "$20/MO"),
                              ("AI GATEWAY", "$3.20 TODAY")], step=9)
    # Coins rise from the Slime as the meter fills.
    for k in range(7):
        life = (s * 0.9 + k / 7) % 1
        if s > 0.3 and life < 0.8:
            cx = 236 + (k * 11) % 40 + round(math.sin((s + k) * 3) * 2)
            cy = 140 - round(life * 26)
            c.circle(cx + 0.5, cy + 0.5, 1.5, "gold", outline="gold.dark")
    slime(c, 236, 138, blink=1.6 < s < 1.75)


# ------------------------------------------------------------------ 5. roll back

KEYS = [("↓", "SELECT", 0.7), ("B", "ROLL BACK", 1.3), ("Y", "CONFIRM", 3.0)]
ASK, DONE = 1.35, 3.05


def scene_rollback(c, p, s, d):
    caption(c, s, "ROLL BACK, IT ASKS FIRST")
    r = c.panel(8, 44, 304, 48, "DEPLOYMENTS", color="sky", sub="EVERY PROJECT")
    picked = 1 if s >= 0.7 else 0
    moved = phase(s, DONE + 0.15, DONE + 0.45)
    deploy_row(c, r, r.y + 2, s, "✓", "MOTH-RADIO", "PRODUCTION", "2 MIN", "TAGS ON EVERY NOTE",
               live=1 if moved <= 0 else None, selected=picked == 0)
    deploy_row(c, r, r.y + 12, s, "✓", "MOTH-RADIO", "PRODUCTION", "2 H", "RSS: ESCAPE AMPERSANDS",
               live=moved if moved > 0 else None, selected=picked == 1)
    deploy_row(c, r, r.y + 22, s, "✓", "CAVE-NOTES", "PRODUCTION", "5 H", "NIGHT MODE FOLLOWS THE SYSTEM", live=1)

    asking = ASK <= s < DONE
    if asking:
        pop = ease_back(phase(s, ASK, ASK + 0.2))
        h = max(3, round(42 * pop))
        y0 = 98 + (42 - h) // 2
        c.rect(24, y0, 272, h, "panel")
        c.box(24, y0, 272, h, "orange")
        if pop >= 1:
            c.text(32, 103, "ROLL MOTH-RADIO'S PRODUCTION BACK?", "orange", font="large")
            c.text(32, 117, "PRODUCTION MOVES BACK TO THIS DEPLOYMENT WITHIN SECONDS.", "text")
            c.spans(32, 128, [("Y", "orange"), (" ROLL BACK   ", "white"), ("ANY OTHER KEY LEAVES IT", "dim")])
    elif s >= DONE:
        c.text(12, 104, "✓", "green")
        c.text(18, 104, "MOTH-RADIO", "white")
        c.text(62, 104, reveal("ROLLED PRODUCTION BACK TO DPL_0B76F20", phase(s, DONE, DONE + 0.5)), "green.light")

    x = 12
    for key, what, at in KEYS:
        lit = at <= s < at + 0.35
        t = c.tag(x, 150, key, "bg" if lit else "white", fill="sky" if lit else "raised", border="sky.dark")
        x = t.x2 + 4 + c.text(t.x2 + 4, 152, what, "text") + 12


# ------------------------------------------------------------------ 6. get it

def scene_end(c, p, s, d):
    drop = ease_back(phase(s, 0.1, 0.7))
    c.chunky(214, 24 + round((1 - drop) * -40), "OOZE", ["#9ff3e2", SLIME, SLIME_DARK], scale=5, depth=3,
             side=["#037a6d", "#02524a"], light="#d4fbf3", dark=INK, outline="shadow")
    slime(c, 12, 26 + int(s * 2.5) % 2, big=True, blink=1.9 < s < 2.05)
    c.strip(118, 70, 190, 2, c.theme.series)
    c.text(160, 80, reveal("YOUR VERCEL PROJECTS, LIVE, IN A TERMINAL", phase(s, 0.5, 1.1)), "white", font="large",
           align="center")
    if s > 1.0:
        c.rect(18, 98, 284, 36, "panel")
        c.box(18, 98, 284, 36, "line")
        c.text(26, 102, "$", "green", font="code")
        c.text(36, 102, "cargo install --git \\", "white", font="code")
        c.text(36, 115, "https://github.com/pdcgomes/ooze", "sky.light", font="code")
    if s > 1.3:
        c.text(160, 142, "MIT · MACOS · LINUX · RUST", "dim", align="center")


SCENES = [
    (scene_online, 4.4),
    (scene_deploys, 5.0),
    (scene_spike, 4.4),
    (scene_spend, 4.6),
    (scene_rollback, 5.2),
    (scene_end, 3.2),
]
TOTAL = sum(d for _, d in SCENES)


def frame(c, i):
    c.header("OOZE", right="GITHUB.COM/PDCGOMES/OOZE")
    c.hline(0, BOTTOM + 1, c.w, "line")
    x0 = c.w // 2 - (len(SCENES) * 6 - 2) // 2
    for k in range(len(SCENES)):
        c.rect(x0 + k * 6, BOTTOM + 5, 4, 3, "white" if k == i else ("dim" if k < i else "raised"))


def goo(c, bx, local):
    """The curtain of slime between two scenes: wobbling, lit on its trailing side, inked on its edge."""
    for y in range(TOP, BOTTOM + 1):
        edge = bx + round(1.6 * math.sin(y * 0.33 + local * 14))
        c.rect(edge - 6, y, 6, 1, SLIME)
        c.px(edge - 5, y, SLIME_LIGHT if y % 3 else SLIME)
        c.px(edge, y, INK)
    # Drips left behind, hanging from the top.
    for k in range(5):
        x = bx - 10 - k * 9
        length = round((6 + (k * 7) % 11) * min(1, local / WIPE * 3))
        c.rect(x, TOP, 2, length, SLIME_DARK)
        c.px(x, TOP + length, SLIME_DARK)


def draw(c, t):
    s = t * TOTAL
    start = 0.0
    for i, (scene, d) in enumerate(SCENES):
        if s < start + d or i == len(SCENES) - 1:
            break
        start += d
    local = min(s - start, d)
    if i > 0 and local < WIPE:
        old_scene, old_d = SCENES[i - 1]
        old, new = c.sub(c.w, c.h), c.sub(c.w, c.h)
        old_scene(old, 1.0, old_d, old_d)
        scene(new, local / d, local, d)
        bx = round(-8 + ease_in_out(local / WIPE) * (c.w + 60))
        cut = max(0, min(c.w, bx))
        if cut:
            c.paste(new.img.crop((0, TOP, cut, BOTTOM + 1)), 0, TOP)
        if cut < c.w:
            c.paste(old.img.crop((cut, TOP, c.w, BOTTOM + 1)), cut, TOP)
        goo(c, bx, local)
        slime(c, bx - 30, BOTTOM - 23 + int(local * 14) % 2)
    else:
        scene(c, local / d, local, d)
    frame(c, i)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "frames":
        for at in sys.argv[2:]:
            c = Canvas(preset="wide")
            draw(c, float(at) / TOTAL)
            for note in c.check():
                print(f"warning ({at} s): {note}")
            c.save(Path("/tmp") / f"ooze-{at}.png", quiet=True)
            print(f"/tmp/ooze-{at}.png")
    else:
        # The GIF first: both write ooze-poster.png, and the poster should be the MP4's full size.
        animate(draw, HERE / "ooze.gif", preset="wide", seconds=TOTAL, fps=15, hold=3, scale=2)
        animate(draw, HERE / "ooze.mp4", preset="wide", seconds=TOTAL, fps=20, hold=3)
