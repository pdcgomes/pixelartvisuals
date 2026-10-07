"""System dashboard: device illustration, LED core meters, line charts, memory map, gauges.

Recreates the DGX Spark reference. Swap the numbers for any "state of the machine" post.
"""

from pathlib import Path

from pixelkit import Canvas, Rect

HOST, OS = "SPARK-7C78", "UBUNTU 24.04 · LINUX 6.17 · AARCH64"
CLOCK, ZONE = "09:11:17", "PDT"
CORES_BIG = [0.09, 0.09, 0.18, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09]
CORES_LITTLE = [0.18, 0.36, 0.09, 0.09, 0.09, 0.18, 0.09, 0.18, 0.09, 0.18]
GPU_UTIL = [2, 3, 2, 2, 3, 2, 2, 2, 3, 2, 2, 2]
GPU_MEM = [18, 18, 19, 19, 20, 20, 20, 21, 21, 21, 21, 21]
MEMORY = [("GPU", 20.8, "lime"), ("APPS", 76.8, "orange"), ("CACHE", 19.2, "sky")]
MEM_TOTAL, SWAP, SWAP_TOTAL = 121.7, 9.2, 16.0
NET_UP = [5, 7, 6, 8, 7, 9, 6, 8, 7, 8, 9, 7, 8, 6, 9, 8]
NET_DOWN = [3, 2, 4, 3, 2, 3, 5, 2, 3, 2, 3, 4, 2, 3, 2, 6]
TEMPS = [("SOC", 48), ("GPU", 45), ("SSD", 43)]
GOLD = {"top": ["#f0d494", "#e7c381", "#d5ab69"], "left": "#d5ab69", "right": ["#d5ab69", "#b88d4a", "#8d6933"],
        "grille": "#5c4220", "edge": "#ffedb7", "dust": ["#e7c381", "#c39951", "#ff8d27"]}

c = Canvas(preset="wide")
RIGHT = c.w - 4  # right-aligned text ends at x - 1, matching panel padding
c.header(HOST, OS, font="large", mark="none", h=14)
clock_w = c.text(RIGHT, 3, CLOCK, "white", font="large", align="right")
c.text(RIGHT - clock_w - 6, 4, ZONE, "dim", align="right")

# Device panel: isometric box with a grille, a lid, a status LED and some warm dust.
dev = c.panel(0, 15, 104, 107)
box = c.iso_box(51, 26, 22, 20, 14, top=GOLD["top"], left=GOLD["left"], right=GOLD["right"],
                edge=GOLD["edge"], corner=GOLD["edge"], shadow="shadow",
                patterns={"left": ("grille", GOLD["grille"])})
c.px(*box.right(17, 10), "lime.light")
c.rect(*box.right(14, 10), 2, 1, GOLD["grille"])
c.sparkles(66, 17, 34, 22, 26, GOLD["dust"], seed=3, twinkle=0)
c.text(dev.cx, 92, "DGX SPARK", "white", font="large", align="center")
c.text(dev.cx, 103, "GB10 GRACE BLACKWELL", "dim", align="center")
c.text(dev.cx, 111, "UP 31D 17H 32M", "text", align="center")

# CPU: two clusters of LED columns.
cpu = c.panel(105, 15, 215, 57, "CPU", color="cyan", sub="20 ARM CORES")
pct_w = c.text(RIGHT, 18, "11%", "cyan", font="large", align="right")
c.text(RIGHT - pct_w - 5, 19, "LOAD 1.73 2.19 2.17", "text", align="right")
for group, (loads, label) in enumerate(((CORES_BIG, "X925 · 3.9 GHZ"), (CORES_LITTLE, "A725 · 2.8 GHZ"))):
    gx = 111 + group * 104
    for i, load in enumerate(loads):
        c.seg_column(gx + i * 10, 29, 7, 32, load, "cyan", seg=2, gap=1)
    c.text(gx + 48, 64, label, "text", align="center")

# GPU: two small line charts and a stat list.
gpu = c.panel(105, 73, 215, 49, "GPU", color="lime", sub="NVIDIA GB10 · BLACKWELL")
c.text(RIGHT, 76, "0%", "lime", font="large", align="right")
for chart, series, col, lo, hi in ((Rect(109, 85, 120, 15), GPU_UTIL, "lime", 0, 12),
                                   (Rect(109, 102, 120, 15), GPU_MEM, "gold", 0, 128)):
    c.rect(*chart, "bg")
    c.grid(*chart, rows=2, cols=6)
    c.spark(chart.x, chart.y, chart.w, chart.h, series, col, fill=c.dark(col) if col == "gold" else None,
            lo=lo, hi=hi)
c.kv(234, 86, RIGHT - 234, [("POWER", "11.5 W", "gold"), ("TEMP", "45°C", "cyan"), ("CLOCK", "2405 MHZ"),
                   ("MEMORY", "20.8G"), ("PROGRAMS", "3")])

# Memory: one pool shared by CPU and GPU, plus swap. Cache is reclaimable, so it isn't "used".
used = sum(v for name, v, _ in MEMORY if name != "CACHE")
c.panel(0, 123, 320, 27, "MEMORY", color="orange",
        sub=f"{used:.1f}G OF {MEM_TOTAL:.0f}G USED · ONE POOL FOR CPU AND GPU", right="SWAP", right_color="violet")
c.stacked(4, 134, 252, 6, [(v, col) for _, v, col in MEMORY], total=MEM_TOTAL)
c.meter(261, 134, 55, 6, SWAP / SWAP_TOTAL, "violet", rim=False)
free = MEM_TOTAL - sum(v for _, v, _ in MEMORY)
c.legend(4, 143, [(f"{n} {v:.1f}G", col) for n, v, col in MEMORY] + [(f"FREE {free:.1f}G", "raised")], gap=12)
c.text(RIGHT, 143, f"{SWAP:.1f}G OF {SWAP_TOTAL:.1f}G", "text", align="right")

# Bottom row: network, disk, temperatures.
c.panel(0, 151, 105, 29, "NET", color="sky", sub="ENP7S7")
c.rect(4, 162, 62, 12, "bg")
c.spark(4, 162, 62, 6, NET_UP, "violet.light", fill="violet.dark", lo=0, hi=10)
c.spark(4, 168, 62, 6, NET_DOWN, "sky", fill="sky.dark", lo=0, hi=10)
c.text(101, 162, "↑218K/S", "violet", align="right")
c.text(101, 169, "↓126K/S", "sky", align="right")

c.panel(106, 151, 106, 29, "DISK", color="gold", sub="440G OF 3.7T", right="12%", right_color="gold")
c.meter(110, 163, 98, 4, 0.12, "gold", rim=False)
c.text(110, 170, "R 0/S", "dim")
c.text(208, 170, "W 360K/S", "text", align="right")

c.panel(213, 151, 107, 29)
for i, (label, temp) in enumerate(TEMPS):
    tx = 217 + i * 34
    c.text(tx, 155, label, "dim")
    c.gauge(tx, 162, 30, temp / 100, "cyan")
    c.text(tx, 170, f"{temp}°C", "white")

c.save(Path(__file__).with_suffix(".png"))
