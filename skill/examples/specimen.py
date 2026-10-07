"""Type, palette, icon and widget specimen for the current theme."""

from pathlib import Path

from pixelkit import ICONS, Canvas

c = Canvas(preset="standard")
y = c.header("PIXELKIT · TYPE, COLOUR & PARTS", right=[("THEME ", "dim"), (c.theme.name.upper(), "text")])
bottom = c.footer("EVERY GLYPH, COLOUR, ICON AND PART IN THE KIT · RESTYLE THEM ALL IN THEME.TOML")

small = c.panel(4, y + 2, 312, 42, "SMALL", color="cyan", sub="3×5 · BODY, LABELS, VALUES")
c.text(small.x, small.y, "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789", "white")
c.text(small.x, small.y + 7, ".,:;!?'\"-+=*%/\\()[]{}<>_|^~#$&@ · • … → ← ↑ ↓ ° × ± ≈ ≤ ≥ ■ ▲ ▼ ✓ € £ —", "text")
c.text(small.x, small.y + 16, "ÁÀÂÃ ÉÊ Í ÓÔÕ ÚÜ ÇÑ · PÃO, CAFÉ E AÇÚCAR", "gold")

large = c.panel(4, small.y2 + 6, 312, 52, "LARGE", color="lime", sub="5×7 · TITLES, CHIP NAMES, BIG VALUES")
c.text(large.x, large.y, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "white", font="large")
c.text(large.x, large.y + 10, "0123456789 .,:;!?-+=%/()<>#$&@ → ↑ ↓ ° × ≈ ≤ ≥ € £", "text", font="large")
c.text(large.x, large.y + 22, "SÃO JOÃO · AÇÚCAR", "gold", font="large")

hero = c.panel(4, large.y2 + 6, 120, 52, "HERO", color="orange", sub="LARGE ×3 + SHADOW")
c.text(hero.x, hero.y + 2, "3.4X", "white", font="large", scale=3, shadow="dim")
c.strip(hero.x, hero.y + 26, 66, 2, c.theme.series)

pal = c.panel(126, large.y2 + 6, 190, 52, "PALETTE", color="violet", sub="BASE / LIGHT / DARK")
for i, name in enumerate(["shadow", "bg", "panel", "raised", "line", "dim", "muted", "text", "white"]):
    c.rect(pal.x + i * 6, pal.y, 5, 5, name)
    c.box(pal.x + i * 6, pal.y, 5, 5, "line")
for i, name in enumerate(c.theme.accents):
    x = pal.x + i * 9
    c.rect(x, pal.y + 9, 8, 6, name)
    c.rect(x, pal.y + 15, 8, 3, name + ".light")
    c.rect(x, pal.y + 18, 8, 3, name + ".dark")
x = pal.x
for i, name in enumerate(ICONS):
    w, h = c.icon(x, pal.y + 33 - len(ICONS[name].split("/")), name, c.series(i))
    x += w + 2

top = hero.y2 + 6
parts = c.panel(4, top, 312, bottom - 2 - top, "PARTS", color="gold", sub="BARS · METERS · LINES · LABELS")
base = parts.y2
for i, h in enumerate((16, 26, 36)):
    c.bar3d(parts.x + i * 16, base, 10, h, c.series(i))
for i, f in enumerate((0.3, 0.8, 0.5, 1.0, 0.2, 0.6, 0.4, 0.9)):
    c.seg_column(parts.x + 50 + i * 6, parts.y + 2, 4, parts.h - 2, f, "cyan", seg=1, gap=1)
c.chip(parts.x + 100, parts.y + 2, 26, 21, "M1", "green", cores=8)
c.tag(parts.x + 113, parts.y + 27, "+34%", "blue.light", align="center")
mx = parts.x + 136
c.meter(mx, parts.y + 2, 60, 5, 0.42, "gold")
c.stacked(mx, parts.y + 11, 60, 5, [(2, "lime"), (5, "orange"), (2, "sky")], total=10)
c.gauge(mx, parts.y + 20, 60, 0.35, "cyan")
c.legend(mx, parts.y + 30, [("GPU", "lime"), ("APPS", "orange"), ("FREE", "raised")])
sx = parts.x + 204
c.grid(sx, parts.y + 2, 50, 22, rows=2, cols=4)
wave = [3, 5, 4, 8, 6, 9, 7, 12, 10, 9, 13, 11, 14]
c.spark(sx, parts.y + 4, 50, 20, wave, "violet.light", fill="violet.dark", lo=0, hi=16)
c.spark(sx, parts.y + 4, 50, 20, [v * 0.5 for v in wave], "sky", lo=0, hi=16)
c.kv(parts.x + 258, parts.y + 2, 46, [("POWER", "11.5W", "gold"), ("TEMP", "45°C", "cyan"),
                                      ("CLOCK", "2405"), ("UP", "31D")])

c.save(Path(__file__).with_suffix(".png"))
