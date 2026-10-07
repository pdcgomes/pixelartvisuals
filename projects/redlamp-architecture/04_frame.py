"""4/6 A frame in under 16 ms: one slider event's path through the threads, latest-wins, and the
main thread's measured load during a drag. Animated: a playhead sweeps the timeline."""

from pathlib import Path

from pixelkit import animate, phase
from series import API, ENGINE, GPU, UI, frame

MS, X0, SPAN = 9, 46, 16
REFRESH = 1000 / 120
LANES = [("MAIN", UI), ("RENDER", API), ("GPU", GPU), ("DISPLAY", UI)]
BUSY = [("ITER 2", 100, "muted"), ("OFF-MAIN", 54, "sky"), ("APPKIT", 34, ENGINE)]
SLOW = [("ITER 2", 157, "muted"), ("OFF-MAIN", 8, "sky"), ("APPKIT", 5, ENGINE)]


def X(ms: float) -> int:
    return X0 + round(ms * MS)


def draw(c, t):
    top, bottom = frame(c, 4, "A FRAME IN UNDER 16 MS",
                        "TIMELINE ILLUSTRATED AT FIT ON A 120 HZ DISPLAY. MAIN-THREAD FIGURES MEASURED WHILE "
                        "DRAGGING A SLIDER AT 120 EVENTS A SECOND, EVERY PANEL OPEN.")
    now = SPAN * phase(t, 0.0, 0.8)

    lanes = c.panel(0, top + 1, 206, 92, "ONE SLIDER EVENT", color=c.light(UI), sub="AT FIT")
    ly = {name: lanes.y + 2 + i * 13 for i, (name, _) in enumerate(LANES)}
    for name, accent in LANES:
        c.text(lanes.x, ly[name] + 1, name, c.light(accent) if accent != UI else "text")
        c.dots(X0, ly[name] + 3, X(SPAN) - X0, "line")
    axis_y = ly["DISPLAY"] + 12
    c.hline(X0, axis_y, X(SPAN) - X0 + 1, "line")
    for ms in range(0, SPAN + 1, 4):
        c.vline(X(ms), axis_y, 2, "dim")
        c.text(X(ms), axis_y + 4, f"{ms}" if ms < SPAN else "16 MS", "dim", align="center" if ms < SPAN else "right")
    for k in range(int(SPAN // REFRESH) + 1):
        c.vline(X(k * REFRESH), ly["DISPLAY"], 7, "dim")

    def bar(lane, start, end, colour):
        if now > start:
            c.rect(X(start), ly[lane], max(2, X(min(end, now)) - X(start)), 7, colour)

    bar("MAIN", 0, 0.17, c.light(UI))
    bar("RENDER", 0.17, 0.4, c.light(API))
    bar("GPU", 0.4, 3.4, GPU)
    bar("GPU", 0.4, 1.0, c.light(GPU))
    if now > 0:
        c.text(X(0) + 4, ly["MAIN"] + 1, "EVENT · 0.17 MS ITERATION", "white")
    if now > 0.4:
        c.text(X(0.4) + 4, ly["RENDER"] + 1, "REQUEST CROSSES ENGINEAPI", c.light(API))
    if now > 3.4:
        c.text(X(3.4) + 4, ly["GPU"] + 1, "RENDER 0.6–3 MS", c.light(GPU))
    if now >= REFRESH:
        c.rect(X(REFRESH), ly["DISPLAY"], X(REFRESH + 3) - X(REFRESH), 7, c.light(UI))
        c.text(X(REFRESH + 3) + 4, ly["DISPLAY"] + 1, "ON SCREEN", "white")
    if now < SPAN:
        c.vline(X(now), lanes.y, axis_y - lanes.y + 3, "white")

    wins = c.panel(0, lanes.y2 + 6, 206, bottom - lanes.y2 - 8, "LATEST WINS", color=c.light(API),
                   sub="A BURST RENDERS ONCE")
    chips = [("E1", "RENDERING"), ("E2", "REPLACED"), ("E3", "REPLACED"), ("E4", "RENDERS NEXT")]
    for i, (name, state) in enumerate(chips):
        p = phase(t, 0.1 + i * 0.15, 0.2 + i * 0.15)
        if p <= 0:
            continue
        cx = wins.x + i * 50
        replaced = state == "REPLACED" and t > 0.25 + i * 0.15
        colour = "dim" if replaced else c.light(GPU) if name == "E1" else "white"
        tag = c.tag(cx, wins.y, name, colour, border=GPU if name == "E1" else "line")
        if replaced:
            c.line(tag.x, tag.y2 - 1, tag.x2 - 1, tag.y, "red")
        label = "PENDING" if state == "REPLACED" and not replaced else state
        c.text(cx, wins.y + 12, label, "dim" if replaced else "text")

    load = c.panel(208, top + 1, 112, bottom - top - 3, "MAIN THREAD", color=c.light(ENGINE), sub="DURING A DRAG")
    c.text(load.x, load.y, "TIME BUSY", "white")
    end = c.hbars(load.x, load.y + 9, load.w, [(n, v, col) for n, v, col in BUSY], vmax=100,
                  fmt=lambda v: f"{v}%" if v == 100 else f"~{v}%", bar_h=5, gap=4, label_w=38)
    c.text(load.x, end + 9, "SLOWEST 5%", "white")
    end = c.hbars(load.x, end + 18, load.w, [(n, v, col) for n, v, col in SLOW], vmax=157,
                  fmt=lambda v: f"{v}MS" if v == 157 else f"~{v}MS", bar_h=5, gap=4, label_w=38)
    c.paragraph(load.x, end + 9, "ITERATION 2, THEN RENDERING OFF THE MAIN THREAD, THEN APPKIT PANELS THAT "
                "REDRAW ONLY WHAT CHANGED.", load.w, "dim")


animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=4, fps=20, hold=3)
