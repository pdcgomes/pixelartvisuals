"""sweep in 30 seconds, for social posts (1280x720 MP4). The numbers are the
made-up Mac of `sweep demo`.

    PYTHONPATH=skill/scripts python3 projects/sweep/sweep.py
"""

from pathlib import Path

from pixelkit import Rect, animate, ease_back, ease_in_out, ease_out, phase, reveal, stagger

TOP, BOTTOM = 13, 169  # the content between the header's rule and the footer's
WIPE = 0.8             # seconds the broom takes to sweep one scene into the next

DISK_GB = 1000
FREE_BEFORE = 38


def gb(v):
    return f"{v:.1f} GB" if v < 10 else f"{v:.0f} GB"


def severity(free):
    pct = free * 100 / DISK_GB
    if pct < 5 or free < 20:
        return "CRITICAL", "red"
    if pct < 15 or free < 50:
        return "LOW", "orange"
    return "OK", "green"


def caption(c, s, title):
    c.text(8, 19, reveal(title, phase(s, 0.1, 0.6)), "white", font="large", scale=2, shadow="line")


# ------------------------------------------------------------------ the broom

STRAW, STRAW_DARK, STRAW_LIGHT = "#e7c381", "#b88d4a", "#f0d494"
WOOD, WOOD_DARK, WOOD_LIGHT = "#a8763e", "#6e4a22", "#d5ab69"


def broom(c, x, base, h=112, lean=0):
    """A broom standing on row `base` with its bristles centred on x. `lean` moves the top of the
    handle sideways, in pixels."""
    neck = base - 30
    top = base - h
    for dx, col in ((-1, WOOD_DARK), (0, WOOD), (1, WOOD_LIGHT)):
        c.line(x + dx + lean, top, x + dx, neck, col)
    c.rect(x - 1 + lean - 1, top - 2, 5, 3, WOOD_DARK)
    c.rect(x - 5, neck, 11, 3, "red")
    c.hline(x - 5, neck, 11, "red.light")
    c.rect(x - 5, neck + 3, 11, 2, "red.dark")
    c.polygon([(x - 5, neck + 5), (x + 5, neck + 5), (x + 12, base), (x - 12, base)], fill=STRAW)
    for k in range(-10, 12, 3):
        c.line(x + k // 3, neck + 6, x + k, base - 1, STRAW_DARK)
    c.hline(x - 4, neck + 5, 9, STRAW_LIGHT)
    for k in range(-11, 12, 2):
        c.px(x + k, base, STRAW_DARK)


# ------------------------------------------------------------------ 1. the disk

def scene_disk(c, p, s, d):
    caption(c, s + 0.6, "YOUR DISK IS FULL")  # titled from the first frame, which feeds show first
    fill = ease_in_out(phase(s, 0.3, 2.2))
    free = 140 + (FREE_BEFORE - 140) * fill
    used = 1 - free / DISK_GB
    label, col = severity(free)
    alarm = label == "CRITICAL" and int(s * 4) % 2 == 0

    ox, oy, w, dd, hh = 60, 78, 24, 16, 10
    c.iso_floor(ox, oy + hh - 8, w + 8, dd + 8, step=4, color="raised")
    box = c.iso_box(ox, oy, w, dd, hh, top=["#c3c9d6", "#8c95ad"], left="#5d6981", right=["#4a5468", "#343b4d"],
                    edge="#f3f4f9", corner="#c3c9d6", shadow="shadow",
                    patterns={"left": ("slots", "#343b4d")})
    lx, ly = box.right(dd - 3, 4)
    c.rect(lx, ly, 2, 1, "red.light" if alarm else ("red.dark" if label == "CRITICAL" else "lime.light"))

    q = c.panel(130, 58, 182, 68, "MACINTOSH HD", color="sky", sub="1 TB")
    hero = c.text(q.x, q.y + 2, f"{used * 100:.0f}%", "white", font="large", scale=3, shadow="dim")
    c.text(q.x + hero + 5, q.y + 9, "USED", "dim")
    c.tag(q.x + q.w, q.y + 3, label, col if not alarm else "white", fill=f"{col}.dark" if alarm else "panel",
          border=col, align="right")
    c.meter(q.x, q.y + 30, q.w, 7, used, col)
    c.text(q.x, q.y + 42, f"{gb(free)} FREE", "text")


# ------------------------------------------------------------------ 2. the scan

FOUND = [
    ("AI MODELS", 0, 46.9),
    ("DOCKER DISK", 0, 32),
    ("XCODE BUILDS", 4.2, 9.4),
    ("BUILD OUTPUT", 8.5, 5.0),
    ("GIT WORKTREES", 11, 1.8),
    ("SCRATCH FOLDERS", 12, 0),
    ("TRASH", 0, 8.2),
    ("XCODE SUPPORT", 6.7, 1.1),
    ("SIMULATOR RUNTIMES", 0, 7.3),
    ("SIMULATORS", 4.0, 3.1),
    ("APP CACHES", 6.7, 0),
    ("TEMP FOLDERS", 6.4, 0),
    ("DOWNLOADS", 0, 6.1),
    ("PACKAGE CACHES", 0, 4.1),
]
SMALL_GB = 1.5  # logs, old extensions and Core ML caches, all Safe
SAFE_GB, REVIEW_GB, KEPT_GB = 61, 125, 83


def scene_scan(c, p, s, d):
    caption(c, s, "SWEEP FINDS THE JUNK")
    top = max(v + r for _, v, r in FOUND)
    found_safe = found_review = 0.0
    y = 46
    for i, (name, safe, review) in enumerate(FOUND):
        g = ease_out(stagger(s / d, i, len(FOUND), start=0.12, end=0.7, overlap=0.55))
        if g > 0:
            c.text(8, y, name, "text")
            c.rect(88, y, 96, 5, "raised")
            ws = round(96 * safe / top * g)
            wr = round(96 * review / top * g)
            c.rect(88, y, ws, 5, "green")
            c.rect(88 + ws, y, wr, 5, "yellow")
            if ws:
                c.hline(88, y, ws, "green.light")
            if wr:
                c.hline(88 + ws, y, wr, "yellow.light")
            c.text(214, y, gb((safe + review) * g), "white", align="right")
        found_safe += safe * g
        found_review += review * g
        y += 8
    more = phase(s / d, 0.7, 0.8)
    if more > 0:
        c.text(8, y + 1, "+ 3 MORE", "dim")
    found_safe += SMALL_GB * more

    r = c.panel(222, 46, 90, 62, "FOUND", color="white")
    c.text(r.x, r.y + 2, gb(found_safe + found_review), "white", font="large", scale=2, shadow="line")
    rows = [("SAFE", gb(found_safe), "green"), ("REVIEW", gb(found_review), "yellow"),
            ("KEPT", gb(KEPT_GB * phase(s / d, 0.12, 0.7)), "muted")]
    for k, (label, value, col) in enumerate(rows):
        yy = r.y + 22 + k * 10
        c.rect(r.x, yy + 1, 3, 3, col)
        c.text(r.x + 6, yy, label, col)
        c.text(r.x + r.w, yy, value, "white", align="right")


# ------------------------------------------------------------------ 3. the badges

BADGES = [
    ("SAFE", "green", "check", "COMES BACK ON ITS OWN", ("SPOTIFY CACHE", "2.8 GB"),
     [("✓", "APP NOT RUNNING"), ("✓", "IDLE 12 DAYS"), ("✓", "NOT IN USE")]),
    ("REVIEW", "yellow", "warn", "COSTS A DOWNLOAD", ("LLAMA3.1:70B", "40 GB"),
     [("✓", "NOT LOADED"), ("·", "PULLED 4 MONTHS AGO")]),
    ("KEPT", "muted", "lock", "IN USE", ("API-HOTFIX", "1.2 GB"),
     [("✓", "COMMITTED"), ("×", "EDITED 2 H AGO")]),
]
MARKS = {"✓": "green", "×": "red", "·": "dim"}


def scene_badges(c, p, s, d):
    caption(c, s, "SAFE, REVIEW OR KEPT")
    for i, (r, (title, col, icon, meaning, (item, size), checks)) in enumerate(
            zip(Rect(8, 50, 304, 84).cols(3, gap=4), BADGES)):
        opening = stagger(s / d, i, 3, start=0.12, end=0.42, overlap=0.4)
        if opening <= 0:
            continue
        c.panel(r.x, r.y, r.w, max(9, round(r.h * min(1, ease_out(opening)))), None)
        if opening < 1:
            continue
        x, y, w = r.x + 4, r.y + 5, r.w - 8
        ink = col if col != "muted" else "text"
        c.text(x, y, title, ink, font="large", scale=2, shadow="line")
        c.icon(x + w - 7, y + 3, icon, col)
        c.text(x, y + 20, meaning, "text")
        c.rect(x, y + 29, w, 11, "raised")
        c.text(x + 2, y + 32, item, "white")
        c.text(x + w - 1, y + 32, size, ink, align="right")
        shown = phase(s / d, 0.42 + i * 0.1, 0.6 + i * 0.1)
        for j, (mark, text) in enumerate(checks):
            if shown > (j + 0.5) / len(checks):
                c.text(x, y + 46 + j * 9, mark, MARKS[mark])
                c.text(x + 6, y + 46 + j * 9, text, "text")


# ------------------------------------------------------------------ 4. what deleting frees

def scene_sizes(c, p, s, d):
    caption(c, s, "WHAT DELETING FREES")
    n, private = 12, 2
    cell, gap = 9, 3
    x0 = 8
    c.text(x0, 50, "WORKTREE", "muted")
    c.text(x0, 80, "CLONE", "muted")
    a = phase(s, 0.5, 1.3)
    b = phase(s, 1.3, 2.1)
    for i in range(n):
        x = x0 + i * (cell + gap)
        if a > i / n:
            c.tile(x, 58, cell, "sky")
        if b > i / n:
            if i < n - private:
                c.vdots(x + cell // 2, 68, 19, "sky.dark")
                c.box(x, 88, cell, cell, "sky.dark")
            else:
                glow = 2.2 <= s < 2.9 and int(s * 5) % 2 == 0
                c.tile(x, 88, cell, "green.light" if glow else "green")
    if b >= 1:
        c.rect(x0, 106, 3, 3, "sky.dark")
        c.text(x0 + 6, 105, "SHARED: STAYS", "text")
        c.rect(x0, 115, 3, 3, "green")
        c.text(x0 + 6, 114, "ITS OWN: FREED", "text")

    r = c.panel(160, 50, 152, 48, "DELETING THE CLONE", color="white")
    du = phase(s, 2.1, 2.7)
    own = phase(s, 2.7, 3.3)
    if du > 0:
        c.text(r.x, r.y + 2, "DU", "dim")
        w = c.text(r.x + r.w, r.y + 1, gb(50 * ease_out(du)), "muted", font="large", align="right")
        if own >= 1:
            c.hline(r.x + r.w - w - 2, r.y + 4, w + 3, "red")
    if own > 0:
        c.text(r.x, r.y + 18, "SWEEP", "dim")
        c.text(r.x + r.w, r.y + 15, gb(8.3 * ease_out(own)), "green", font="large", scale=2, shadow="line",
               align="right")


# ------------------------------------------------------------------ 5. deleting

ROWS = [
    ("GIT WORKTREES", "SAFE", 11),
    ("BUILD OUTPUT", "SAFE", 8.5),
    ("SCRATCH FOLDERS", "SAFE", 12),
    ("XCODE FILES", "SAFE", 10.9),
    ("APP CACHES", "SAFE", 6.7),
    ("TEMP FOLDERS", "SAFE", 6.4),
    ("4 MORE KINDS", "SAFE", 5.5),
    ("DOCKER DISK", "REVIEW", 32),
    ("AN OLD AI MODEL", "REVIEW", 40),
]
BADGE_COLOUR = {"SAFE": "green", "REVIEW": "yellow"}
KEYS = [("A", "ALL SAFE", 0.8), ("SPACE", "MARK", 1.6), ("ENTER", "DELETE", 2.4), ("Y", "CONFIRM", 3.1)]


def scene_delete(c, p, s, d):
    caption(c, s, "DELETE WHAT YOU PICK")
    total = sum(v for _, _, v in ROWS)
    marked_at = [0.8 + 0.08 * i for i in range(7)] + [1.6, 1.95]
    gone_at = [3.3 + 0.15 * i for i in range(len(ROWS))]
    freed = sum(v * ease_out(phase(s, t0, t0 + 0.3)) for (_, _, v), t0 in zip(ROWS, gone_at))
    free = FREE_BEFORE + freed
    label, col = severity(free)

    q = c.panel(8, 50, 190, 112, "FOUND", color="sky")
    dialog = 2.4 <= s < 3.15
    marked = sum(size for (_, _, size), t_mark in zip(ROWS, marked_at) if s >= t_mark)
    for i, ((name, badge, size), t_mark, t_gone) in enumerate(zip(ROWS, marked_at, gone_at)):
        y = q.y + i * 9
        if dialog and 74 <= y <= 128:
            continue
        if s >= t_gone + 0.3:
            continue
        on = s >= t_mark
        bc = BADGE_COLOUR[badge]
        if s >= t_gone:
            c.text(q.x, y, "✓", "green")
        else:
            c.circle(q.x + 2.5, y + 2.5, 2.5, bc if on else "panel", outline=bc if on else "dim")
        c.text(q.x + 8, y, name, "white" if on else "text")
        c.text(q.x + 100, y, badge, bc)
        c.text(q.x + q.w, y, gb(size), "white" if on else "text", align="right")
        if s >= t_gone:
            c.dissolve(phase(s, t_gone, t_gone + 0.3), "panel", region=(q.x, y - 1, q.w, 8))
    if s < gone_at[0]:
        c.text(q.x, q.y + 86, f"MARKED {gb(marked)}" if marked else "NOTHING MARKED", "yellow" if marked else "dim")
    elif s >= gone_at[-1] + 0.3:
        c.text(q.cx, q.y + 36, f"FREED {gb(total)}", "green", font="large", scale=2, shadow="line", align="center")
    if dialog:
        pop = ease_back(phase(s, 2.4, 2.6))
        h = max(3, round(46 * pop))
        y0 = 78 + (46 - h) // 2
        c.rect(24, y0, 158, h, "panel")
        c.box(24, y0, 158, h, "red")
        if pop >= 1:
            c.text(30, 83, "DELETE THESE?", "red", font="large")
            c.text(30, 96, f"36 ITEMS · {gb(total)}", "white")
            c.text(30, 104, "CHECKED AGAIN FIRST", "dim")
            c.spans(30, 114, [("Y", "red"), (" DELETE   ", "text"), ("ANY KEY", "sky"), (" CANCEL", "text")])

    r = c.panel(202, 50, 110, 112, "MACINTOSH HD", color="sky", sub="1 TB")
    w = c.text(r.x, r.y + 2, f"{free:.0f} GB", "white", font="large", scale=2, shadow="line")
    c.text(r.x + w + 4, r.y + 9, "FREE", "dim")
    c.meter(r.x, r.y + 20, r.w, 5, 1 - free / DISK_GB, col)
    c.tag(r.x, r.y + 29, label, col, border=col)
    c.hline(r.x, r.y + 44, r.w, "line")
    for k, (key, what, at) in enumerate(KEYS):
        y = r.y + 49 + k * 12
        lit = at <= s < at + 0.35 or (key == "SPACE" and 1.95 <= s < 2.3)
        t = c.tag(r.x, y, key, "bg" if lit else "white", fill="sky" if lit else "raised", border="sky.dark")
        c.text(t.x2 + 4, y + 2, what, "text")


# ------------------------------------------------------------------ 6. get it

def scene_end(c, p, s, d):
    drop = ease_back(phase(s, 0.1, 0.7))
    c.chunky(178, 28 + round((1 - drop) * -40), "SWEEP", ["#9fd599", "#61bb46", "#3f752d"], scale=5, depth=3,
             side=["#3f752d", "#2b4f1f"], light="#d6f0cf", dark="#2b4f1f", outline="shadow")
    broom(c, 36, 80, h=58, lean=6)
    c.strip(78, 72, 200, 2, c.theme.series)
    c.text(178, 80, reveal("FIND AND DELETE JUNK ON YOUR MAC", phase(s, 0.5, 1.1)), "white", font="large",
           align="center")
    if s > 1.0:
        c.rect(18, 98, 284, 36, "panel")
        c.box(18, 98, 284, 36, "line")
        c.text(26, 102, "$", "green", font="code")
        c.text(36, 102, "cargo install --git \\", "white", font="code")
        c.text(36, 115, "https://github.com/pdcgomes/sweep", "sky.light", font="code")
    if s > 1.3:
        c.text(160, 142, "MIT · MACOS · RUST", "dim", align="center")


SCENES = [
    (scene_disk, 3.4),
    (scene_scan, 4.6),
    (scene_badges, 4.8),
    (scene_sizes, 4.4),
    (scene_delete, 6.4),
    (scene_end, 3.0),
]
TOTAL = sum(d for _, d in SCENES)


def frame(c, i):
    c.header("SWEEP", right="GITHUB.COM/PDCGOMES/SWEEP")
    c.hline(0, BOTTOM + 1, c.w, "line")
    x0 = c.w // 2 - (len(SCENES) * 6 - 2) // 2
    for k in range(len(SCENES)):
        c.rect(x0 + k * 6, BOTTOM + 5, 4, 3, "white" if k == i else ("dim" if k < i else "raised"))


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
        bx = round(-14 + ease_in_out(local / WIPE) * (c.w + 28))
        cut = max(0, min(c.w, bx))
        if cut:
            c.paste(new.img.crop((0, TOP, cut, BOTTOM + 1)), 0, TOP)
        if cut < c.w:
            c.paste(old.img.crop((cut, TOP, c.w, BOTTOM + 1)), cut, TOP)
        c.particles(bx + 10, BOTTOM - 20, 26, 18, local / WIPE, kind="dust", n=16, colors=["muted", "dim", "line"],
                    seed=3 + i)
        broom(c, bx, BOTTOM - 2 + (int(local * 16) % 2), lean=-8)
    else:
        scene(c, local / d, local, d)
    frame(c, i)


if __name__ == "__main__":
    animate(draw, Path(__file__).with_name("sweep.mp4"), preset="wide", seconds=TOTAL, fps=20, hold=3)
