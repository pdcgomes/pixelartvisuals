"""Live system monitor loop: ticking clock, flickering core meters, scrolling charts, blinking LED, rising heat.

Animated version of dashboard.py. Readings change once a second like a real monitor, while the LED,
the dust and the charts move every frame. Everything loops seamlessly except the clock, which steps
back when the loop restarts.
"""

import math
import random
from pathlib import Path

from pixelkit import Rect, animate, blink

SECONDS, FPS = 4, 10
HOST, OS, ZONE = "SPARK-7C78", "UBUNTU 24.04 · LINUX 6.17 · AARCH64", "PDT"
CORES_BIG = [0.09, 0.09, 0.18, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09]
CORES_LITTLE = [0.18, 0.36, 0.09, 0.09, 0.09, 0.18, 0.09, 0.18, 0.09, 0.18]
MEMORY = [("GPU", 20.8, "lime"), ("APPS", 76.8, "orange"), ("CACHE", 19.2, "sky")]
MEM_TOTAL, SWAP, SWAP_TOTAL = 121.7, 9.2, 16.0
TEMPS = [("SOC", 48), ("GPU", 45), ("SSD", 43)]
GOLD = {"top": ["#f0d494", "#e7c381", "#d5ab69"], "left": "#d5ab69", "right": ["#d5ab69", "#b88d4a", "#8d6933"],
        "grille": "#5c4220", "edge": "#ffedb7", "dust": ["#e7c381", "#c39951", "#ff8d27"]}


def signal(t, period, waves, base, columns):
    """One sample per column of a pattern that repeats every `period` columns and scrolls left by
    exactly one period per loop, so the end of the loop meets its start."""
    return [base + sum(a * math.sin(2 * math.pi * (k * (i / period + t) + p)) for a, k, p in waves)
            for i in range(columns)]


def draw(c, t):
    tick = int(t * SECONDS)
    rnd = random.Random(tick)
    right = c.w - 4
    c.header(HOST, OS, font="large", mark="none", h=14)
    clock_w = c.text(right, 3, f"09:11:{17 + tick:02d}", "white", font="large", align="right")
    c.text(right - clock_w - 6, 4, ZONE, "dim", align="right")

    dev = c.panel(0, 15, 104, 107)
    box = c.iso_box(51, 26, 22, 20, 14, top=GOLD["top"], left=GOLD["left"], right=GOLD["right"],
                    edge=GOLD["edge"], corner=GOLD["edge"], shadow="shadow",
                    patterns={"left": ("grille", GOLD["grille"])})
    c.px(*box.right(17, 10), "lime.light" if blink(t, cycles=SECONDS, duty=0.6) else "lime.dark")
    c.rect(*box.right(14, 10), 2, 1, GOLD["grille"])
    for k in range(26):
        p = random.Random(100 + k)
        x, rise, cycles, start = 66 + p.randrange(34), 14 + p.randrange(8), p.choice((1, 2)), p.random()
        c.px(x + round(math.sin(2 * math.pi * (t * cycles + start)) * 1.5),
             40 - round(((t * cycles + start) % 1) * rise), p.choice(GOLD["dust"]))
    c.text(dev.cx, 92, "DGX SPARK", "white", font="large", align="center")
    c.text(dev.cx, 103, "GB10 GRACE BLACKWELL", "dim", align="center")
    c.text(dev.cx, 111, "UP 31D 17H 32M", "text", align="center")

    c.panel(105, 15, 215, 57, "CPU", color="cyan", sub="20 ARM CORES")
    loads = [[max(0.09, base + rnd.choice((-0.09, 0, 0, 0.09))) for base in group]
             for group in (CORES_BIG, CORES_LITTLE)]
    pct_w = c.text(right, 18, f"{10 + tick % 3 * 2}%", "cyan", font="large", align="right")
    c.text(right - pct_w - 5, 19, f"LOAD 1.{73 + tick * 4} 2.19 2.17", "text", align="right")
    for group, (row, label) in enumerate(zip(loads, ("X925 · 3.9 GHZ", "A725 · 2.8 GHZ"))):
        gx = 111 + group * 104
        for i, load in enumerate(row):
            c.seg_column(gx + i * 10, 29, 7, 32, load, "cyan", seg=2, gap=1)
        c.text(gx + 48, 64, label, "text", align="center")

    c.panel(105, 73, 215, 49, "GPU", color="lime", sub="NVIDIA GB10 · BLACKWELL")
    c.text(right, 76, "0%", "lime", font="large", align="right")
    for chart, values, col, lo, hi, fill in (
        (Rect(109, 85, 120, 15), signal(t, 40, [(0.6, 3, 0), (0.4, 7, 0.3)], 2.5, 120), "lime", 0, 12, None),
        (Rect(109, 102, 120, 15), signal(t, 60, [(1.5, 2, 0.1)], 19.5, 120), "gold", 0, 128, "gold.dark"),
    ):
        c.rect(*chart, "bg")
        c.grid(*chart, rows=2, cols=6)
        c.spark(*chart, values, col, fill=fill, lo=lo, hi=hi)
    c.kv(234, 86, right - 234, [("POWER", f"11.{4 + tick % 3} W", "gold"), ("TEMP", "45°C", "cyan"),
                                ("CLOCK", "2405 MHZ"), ("MEMORY", "20.8G"), ("PROGRAMS", "3")])

    used = sum(v for name, v, _ in MEMORY if name != "CACHE")
    c.panel(0, 123, 320, 27, "MEMORY", color="orange",
            sub=f"{used:.1f}G OF {MEM_TOTAL:.0f}G USED · ONE POOL FOR CPU AND GPU", right="SWAP", right_color="violet")
    c.stacked(4, 134, 252, 6, [(v, col) for _, v, col in MEMORY], total=MEM_TOTAL)
    c.meter(261, 134, 55, 6, SWAP / SWAP_TOTAL, "violet", rim=False)
    free = MEM_TOTAL - sum(v for _, v, _ in MEMORY)
    c.legend(4, 143, [(f"{n} {v:.1f}G", col) for n, v, col in MEMORY] + [(f"FREE {free:.1f}G", "raised")], gap=12)
    c.text(right, 143, f"{SWAP:.1f}G OF {SWAP_TOTAL:.1f}G", "text", align="right")

    c.panel(0, 151, 105, 29, "NET", color="sky", sub="ENP7S7")
    c.rect(4, 162, 62, 12, "bg")
    c.spark(4, 162, 62, 6, signal(t, 31, [(1.5, 2, 0), (1, 5, 0.2)], 7, 62), "violet.light", fill="violet.dark",
            lo=0, hi=10)
    c.spark(4, 168, 62, 6, signal(t, 31, [(1.2, 3, 0.5), (0.8, 6, 0)], 3, 62), "sky", fill="sky.dark", lo=0, hi=10)
    c.text(101, 162, f"↑{(218, 231, 205, 224)[tick]}K/S", "violet", align="right")
    c.text(101, 169, f"↓{(126, 119, 140, 131)[tick]}K/S", "sky", align="right")

    c.panel(106, 151, 106, 29, "DISK", color="gold", sub="440G OF 3.7T", right="12%", right_color="gold")
    c.meter(110, 163, 98, 4, 0.12, "gold", rim=False)
    c.text(110, 170, "R 0/S", "dim")
    c.text(208, 170, f"W {(360, 412, 288, 340)[tick]}K/S", "text", align="right")

    c.panel(213, 151, 107, 29)
    for i, (label, temp) in enumerate(TEMPS):
        tx = 217 + i * 34
        c.text(tx, 155, label, "dim")
        c.gauge(tx, 162, 30, temp / 100, "cyan")
        c.text(tx, 170, f"{temp}°C", "white")


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=SECONDS, fps=FPS, seamless=True)
