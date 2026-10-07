---
name: pixel-graphics
description: Creates pixel-art infographics, charts, dashboards, post covers and social cards in a retro low-resolution style (bitmap capitals, navy panels, rainbow accents, extruded striped bars, isometric devices) with a bundled Python kit that exports crisp nearest-neighbour PNGs and animated GIF, WebP or MP4. Use when the user asks for pixel-art or retro graphics, a chart, infographic, cover, social card or animated graphic for their blog or a post, or mentions pixelkit or the pixel style.
---

# Pixel graphics

Every graphic is drawn on a tiny logical canvas (320×180 by default) and exported with
nearest-neighbour scaling, so each logical pixel becomes a crisp 4×4 block. The kit is
`scripts/pixelkit` (Python 3.11+, Pillow, numpy); the brand lives in `theme.toml`.

## Quick start

```bash
PYTHONPATH=~/.cursor/skills/pixel-graphics/scripts python3 graphic.py
```

```python
from pathlib import Path
from pixelkit import Canvas

c = Canvas(preset="wide")                               # 320x180 -> 1280x720
bottom = c.footer("SOURCE: WHERE THE NUMBERS CAME FROM, DATE")  # returns its top y
top = c.header("SUBJECT · WHAT IT SHOWS", right="UNIT OR SOURCE")
p = c.panel(0, top + 1, 160, bottom - top - 3, "CPU", color="cyan", sub="20 CORES")
c.meter(p.x, p.y, p.w, 5, 0.42, "cyan")                 # p is the content Rect
c.save(Path(__file__).with_suffix(".png"))              # prints warnings, then the path
```

## Workflow

```
- [ ] 1. Decide the one message: the headline number or claim, and its source
- [ ] 2. Pick a preset and the closest example (look at its .png)
- [ ] 3. Copy that example next to where the image will live; replace the data at the top
- [ ] 4. Render and fix every printed warning
- [ ] 5. Open the PNG with the Read tool (for animations: the contact sheet, then the poster) and
        go through the review checklist
- [ ] 6. Deliver the PNG (or animation and poster) with its .py source and alt text
```

Keep `name.py` beside `name.png` so the graphic can be re-rendered later. If it is unclear where
the blog keeps images, ask; otherwise use `graphics/` in the current project.

| Example | Preset | Use it for |
|---------|--------|-----------|
| `examples/generations.py` | standard | Versions compared: hero multiple, striped bars with % deltas, icon row, spec table |
| `examples/dashboard.py` | wide | State of a machine or project: panels, LED columns, line charts, memory map, gauges, isometric device |
| `examples/ranking.py` | standard | Top-N lists: hero total, share bar, horizontal bars, small bar chart with day labels |
| `examples/waffle.py` | square | Parts of a whole: 10×10 waffle, group totals bracketed beside their rows, context row |
| `examples/cover.py` | og | Post covers and social cards: kicker, 2× title, rainbow rule, stats, device on an iso floor |
| `examples/generations_intro.py` | standard | Animated intro (GIF): bars rise in turn, values count up, deltas pop in, then hold |
| `examples/dashboard_live.py` | wide | Animated seamless loop (GIF): ticking readings, blinking LED, rising dust, scrolling charts |
| `examples/specimen.py` | standard | Catalogue of every glyph, colour and icon, and the common parts; check it before drawing something custom |

When no example uses the preset you need (portrait, banner, hd), start from the example whose
content is closest and re-flow it with `Rect.rows/cols/cut_*`; keep its spacing and colour roles.

| Preset | Logical | PNG |
|--------|---------|-----|
| `wide` | 320×180 | 1280×720 |
| `standard` | 320×240 | 1280×960 |
| `og` | 400×210 | 1200×630 (scale 3, social cards) |
| `square` | 256×256 | 1024×1024 |
| `portrait` | 240×320 | 960×1280 |
| `banner` | 400×100 | 1200×300 (scale 3) |
| `hd` | 480×270 | 1920×1080 (only for very dense dashboards) |

## Style rules

These are what make the output match the look; follow them unless the user asks otherwise.

**Grid and type**
- Integer logical pixels only. Never resize the exported PNG with smoothing.
- Two capitals-only fonts (text is upper-cased): `small` (3×5) for nearly everything, `large` (5×7)
  for titles, chip names and big values. Hero numbers: `font="large", scale=3, shadow="dim"`.
  Cover titles: `large` at `scale=2` with `shadow="line"`.
- Line steps: 7px for small, 10px for large; `paragraph()` adds room for accents (Portuguese works).
- Separate facts with `·`, ranges with `→` ("2020 → 2026"), rates with `↑ ↓`; mark footnotes with `×`.

**Colour roles**
- `bg` page, `panel` fill, `line` borders, axes and grids, `raised` empty tracks and LED segments,
  `shadow` cast shadows.
- Text: `white` headlines and values, `text` body, `dim` subtitles, axes and units, `muted` table labels.
- One accent per subject or series. Panel titles take the accent and the subtitle is dim (`panel(title,
  color=, sub=)`). Use `name.light` for rims and labels on dark backgrounds and `name.dark` for stripes,
  sides and area fills.
- Data colours come from the theme (`c.series(i)` follows `theme.series`). Hex values are fine for
  product illustrations such as the gold box.

**Layout**
- Call `footer()` first and lay panels out between the header's bottom and the footer's top.
- Leave 1–2px gutters between panels. Content sits 4px in from a panel's edge (3px clear of its
  border) and 12px below a titled panel's top; `panel()` returns that content `Rect`.
- Right-aligned text ends one pixel before its `x`, so `x = panel_x + panel_w - 4` mirrors the left
  padding. Use the same rule for hand-placed text.
- Build grids with `Rect.rows/cols/cut_*` and `split()` instead of hand arithmetic.
- Every number gets a unit. Footers cite the source and its date.
- When a hero block sits over a chart grid, clear the area behind it with `c.rect(..., "bg")`.

**Which part for which job**
- Comparing versions: `bar_chart(..., deltas=True)`. Bars are extruded at the isometric 2:1 slope,
  like `iso_box`; pass `depth=0` for the flat look of the original reference. Use the returned rects
  (`bar.cx`) to line up chips, labels and tables under each bar.
- Rankings `hbars`, parts of a whole `waffle` or `stacked` + `legend`, per-core loads `seg_column`,
  trends `grid` + `spark(fill=...)`, levels `meter` / `gauge`, stat lists `kv`, deltas `tag`,
  processors `chip`, bevelled swatches `tile`.

## Review checklist

- No warnings printed (text collisions, text crossing a panel edge, overlapping panels, off-canvas,
  missing glyphs).
- The headline reads at a glance; each accent means one thing; no stray colours.
- Nothing touches a border; padding is consistent; numbers in lists are right-aligned.
- Values carry units; the footer names the source and date.
- Covers and social cards: titles at `large` ×2 or bigger, because feeds show them about 500px wide.
- Animations: the contact sheet shows the intended motion, the final state holds long enough to
  read (2–3 s), nothing flickers by accident, and the file stays under about 1 MB.

## Animation

Put the drawing in `draw(c, t)` and pass it to `animate()`. Each frame is redrawn on the logical
grid, so motion stays pixel-exact, and every layout check runs on every frame.

```python
from pixelkit import animate, ease_out, stagger

def draw(c, t):                                          # t runs 0 -> 1
    grow = [ease_out(stagger(t, i, len(VALUES), end=0.8)) for i in range(len(VALUES))]
    c.bar_chart(0, 20, 314, 121, VALUES, deltas=True, grow=grow)   # rise, count up, then deltas

animate(draw, "chart.gif", preset="standard", seconds=2.4, fps=20, hold=3)
```

- Two patterns cover most posts. An intro builds the graphic and then holds it (`hold=3`; see
  `generations_intro.py`). An ambient loop (`seamless=True`; see `dashboard_live.py`) repeats
  without a jump when every motion completes whole cycles: `wave`, `blink`, scrolling by exactly
  one period, particles with whole-number cycles.
- Timing helpers: `phase(t, a, b)` gives progress through part of the timeline and `stagger` plays
  items one after another. `ease_out`, `ease_back` and `steps` set the feel, and `reveal(text, p)`
  types text in. Count numbers up with `value * p`.
- Let data settle: animate toward the final values and hold them long enough to read. Live readings
  change about once a second (`tick = int(t * seconds)`); only decoration (LEDs, dust, scrolling
  charts) moves every frame.
- Move whole pixels and swap colours. There are no alpha fades, so make things grow, pop, scroll,
  blink or type in.
- The extension picks the format. `.gif` plays everywhere. `.webp` (lossless) is several times
  smaller. `.mp4` suits social video, and loops on a page with `<video autoplay loop muted>`.
  `.png` writes APNG.
- Every call also writes `NAME-poster.png` (the final frame) for social cards, which can't animate,
  and prints the path of a contact sheet of sampled frames to review.
- 10–12 fps reads as retro and 20 as smooth growth. Keep loops to 2–6 s.

## Brand

`theme.toml` sets the palette, the series order, number separators, the brand name printed at the
right of footers and the header mark (`"stripes"`, `"none"` or a small PNG). Edit it to restyle every
future graphic. For a second look, copy the file and pass `Canvas(theme="path.toml")` or set
`PIXELKIT_THEME`.

## Illustrations

- Devices and objects: `iso_box` (faces take a colour or a list for a dithered gradient; textures
  `grille`, `slots`, `mesh`) plus `iso_floor` and `sparkles`. See `dashboard.py` and `cover.py`.
- Icons: `c.icon(x, y, name, colour)`. Small sprites: `c.sprite(x, y, ascii_art, {"a": "green"})`.
- Anything complex (people, scenes, logos): generate or find an image, then lock it to the palette
  with `python3 scripts/pixelate.py in.png out.png --width 80 --key --dither 0.4` and place it with
  `c.image("out.png", x, y, colors="keep")`. `c.image(path, x, y, w=80)` does the same in one step.

## On the blog

```css
img.pixel { image-rendering: pixelated; }
```

Show images at their exported size or a whole fraction of it (1280px wide at 640px), so pixel blocks
stay even.

## Reference

Full API with every signature, parameter and the theme format: [reference.md](reference.md).
After changing the kit or the theme, run `python3 scripts/selftest.py`: it checks the layout
warnings, confirms animations play back frame for frame, and re-renders every example.
