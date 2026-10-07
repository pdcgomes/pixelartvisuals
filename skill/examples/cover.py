"""Post cover / social card (1200x630): kicker, big title, rainbow rule, stats, illustration, mini panel."""

from pathlib import Path

from pixelkit import Canvas

KICKER = "HARDWARE · FIELD NOTES"
TITLE = ["A MONTH WITH", "THE DGX SPARK"]
DECK = "ONE SMALL BOX, ONE POOL OF MEMORY FOR CPU AND GPU. WHAT IT IS GOOD AT AFTER 31 DAYS OF UPTIME."
STATS = [("20", "ARM CORES", "cyan"), ("122G", "SHARED MEMORY", "orange"), ("3.7T", "NVME", "gold")]
META = "7 OCT 2026 · 6 MIN READ"
GOLD = {"top": ["#f0d494", "#e7c381", "#d5ab69"], "left": "#d5ab69", "right": ["#d5ab69", "#b88d4a", "#8d6933"],
        "grille": "#5c4220", "edge": "#ffedb7", "dust": ["#e7c381", "#c39951", "#ff8d27"]}

c = Canvas(preset="og")
c.gradient(0, 130, c.w, 80, ["bg", "panel"])
c.sparkles(220, 0, c.w - 220, 60, 22, ["line", "dim"], seed=11, twinkle=0.1)

# Illustration first so the copy and the mini panel sit on top of it.
ox, oy, w, d, h, margin = 300, 66, 28, 24, 18, 12
c.iso_floor(ox, oy + h - 2 * margin, w + 2 * margin, d + 2 * margin, step=4, color="raised")
c.iso_floor(ox, oy + h - 2 * margin, w + 2 * margin, d + 2 * margin, step=4, color="line", dots=True)
box = c.iso_box(ox, oy, w, d, h, top=GOLD["top"], left=GOLD["left"], right=GOLD["right"],
                edge=GOLD["edge"], corner=GOLD["edge"], shadow="shadow",
                patterns={"left": ("grille", GOLD["grille"])})
c.px(*box.right(d - 3, 12), "lime.light")
c.rect(*box.right(d - 7, 12), 3, 1, GOLD["grille"])
c.sparkles(ox + 4, oy - 24, 44, 28, 30, GOLD["dust"], seed=3, twinkle=0)

p = c.panel(236, 162, 150, 34, "MEMORY", color="orange", sub="97.6G OF 122G")
c.stacked(p.x, p.y, p.w, 5, [(20.8, "lime"), (76.8, "orange"), (19.2, "sky")], total=121.7)
c.legend(p.x, p.y + 9, [("GPU", "lime"), ("APPS", "orange"), ("CACHE", "sky")], gap=8)

# Copy column.
x = 16
mark_w, _ = c.mark(x, 18)
c.text(x + mark_w + 5, 18, KICKER, "dim")
y = 34
for line in TITLE:
    c.text(x, y, line, "white", font="large", scale=2, shadow="line")
    y += 18
c.strip(x, y + 1, max(c.measure(t, "large", 2) for t in TITLE), 2, c.theme.series)
c.paragraph(x, y + 10, DECK, 196, "text")
sx = x
for value, label, col in STATS:
    vw = c.text(sx, 120, value, col, font="large", scale=2, shadow="line")
    lw = c.text(sx, 138, label, "dim")
    sx += max(vw, lw) + 16
brand = c.theme.brand.get("name", "")
c.hline(x, 178, 196, "line")
c.text(x, 186, META + (f" · {brand}" if brand else ""), "muted")

c.save(Path(__file__).with_suffix(".png"))
