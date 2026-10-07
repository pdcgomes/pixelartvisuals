# pixelkit reference

All coordinates are logical pixels (before export scaling). Sizes are inclusive of borders, so a
`rect(0, 0, 10, 5, ...)` covers columns 0–9 and rows 0–4.

Colours can be a theme name (`"panel"`, `"green"`, `"green.light"`, `"green.dark"`), a hex string
(`"#e7c381"`) or an RGB tuple. `None` skips the drawing.

## Contents
- Canvas and colour helpers
- Primitives
- Text
- Layout
- Charts and widgets
- Diagrams
- Illustration
- Animation
- Export and checks
- Theme file
- pixelate.py
- Module helpers

## Canvas and colour helpers

`Canvas(w=None, h=None, *, preset="wide", theme=None, bg="bg", scale=None)`
- Give `w, h` for a custom size, otherwise the preset decides size and export scale.
- `theme`: a path to a theme file or a `Theme`; defaults to `PIXELKIT_THEME` or the skill's `theme.toml`.
- Attributes: `w`, `h`, `scale`, `theme`, `img` (the 1× PIL image), `bounds` (a `Rect`).

`rgb(c)`, `light(c)`, `dark(c)` (shade names for accents, mixed shades for anything else),
`series(i)` (the i-th colour of `theme.series`, cycling), `num(value, decimals=0)` (theme separators).

## Primitives

| Call | Draws |
|------|-------|
| `px(x, y, c)` | one pixel |
| `rect(x, y, w, h, c)` | filled rectangle |
| `box(x, y, w, h, c)` | 1px outline |
| `hline(x, y, w, c)` / `vline(x, y, h, c)` | 1px lines |
| `dots(x, y, w, c, step=2)` / `vdots(x, y, h, c, step=2)` | dotted lines |
| `line(x0, y0, x1, y1, c)` | Bresenham line, no anti-aliasing |
| `polyline(points, c)` | connected lines |
| `pattern(x, y, w, h, c, kind="checker")` | inks pattern pixels only: `checker`, `sparse`, `dense`, `hlines`, `vlines`, `diagonal`, `mesh`, `grille`, `slots`, `grain` |
| `gradient(x, y, w, h, colors, vertical=True)` | ordered-dither blend through a list of colours |

## Text

`text(x, y, s, color="text", *, font="small", scale=1, align="left", shadow=None, shadow_offset=1, outline=None, check=True) -> width`
- `y` is the cap top. `x` is the left edge, the centre, or the right edge depending on `align`.
  The right edge is exclusive, so right-aligned text ends at `x - 1`.
- `font`: `"small"` (cap height 5, line step 7) or `"large"` (cap 7, step 10). Accented capitals use 2px
  above the cap and cedillas 2px below.
- `shadow` draws the text again offset by `shadow_offset` logical pixels; `outline` rings every pixel.
- Text is upper-cased. Smart quotes, the minus sign and non-breaking spaces are normalised. Missing
  glyphs draw as `?` and are reported on save.

`spans(x, y, parts, color="dim", *, font="small", scale=1, align="left", shadow=None) -> width`
- `parts` mixes `(text, colour)` pairs and plain strings in `color`:
  `c.spans(x, y, [("CPU", "cyan"), " 20 ARM CORES"])`.

`paragraph(x, y, s, w, color="text", *, font="small", scale=1, line=None, align="left") -> next y`
- Word-wraps to width `w`; `"\n"` forces a break. The line step grows by 2 when the text has accents.

`measure(s, font="small", scale=1) -> width`

Glyphs: A–Z, 0–9, `. , : ; ! ? ' " ` - + = * % / \ ( ) [ ] { } < > _ | ^ ~ # $ & @`,
`· • … → ← ↑ ↓ ° × ± ≈ ≤ ≥ ■ ▲ ▼ ✓ € £ — –`, and ÁÀÂÃÄ ÉÈÊË ÍÌÎÏ ÓÒÔÕÖ ÚÙÛÜ Ç Ñ.

## Layout

`header(title, sub=None, right=None, *, font="small", color="white", mark=None, h=12, line="line", fill=None, pad=4) -> content top`
- Mark (theme default), title, dim `sub`, right-aligned `right` (a string or spans), and a rule on row
  `h - 1`. Use `font="large", h=14, mark="none"` for the dashboard look; draw extra right-side items
  (a clock in the large font) yourself.

`panel(x, y, w, h, title=None, *, color="cyan", sub=None, right=None, right_color="text", fill="panel", border="line", pad=4) -> Rect`
- Fill, 1px border, accent title plus dim subtitle at `(x + pad, y + pad)`, and `right` (a string or
  spans) right-aligned on the same row. Returns the content rect, which starts 12px below the top when
  there's a title.

`footer(lines, *, color="dim", line="line", pad=4, brand=True) -> rule y`
- Wraps `lines` (a string or a list) across the width, draws a rule above them, and puts
  `theme.brand.name` at the right when it's set. Call it before laying out panels.

`mark(x, y, mark="stripes") -> (w, h)`: the brand mark: 9×6 series stripes, a
`(sprite rows, colour map)` pair (`projects/redlamp-architecture/series.py` has an example), or
a PNG at 1×. `header(mark=...)` takes the same values.

`Rect(x, y, w, h)`: a NamedTuple, so `c.rect(*r, "panel")` works.
- `x2`, `y2` (exclusive), `cx`, `cy`
- `intersects(r)`, `contains(r)`
- `inset(dx, dy=None)`
- `cols(n_or_weights, gap=2)`, `rows(n_or_weights, gap=2)`: lists of Rects
- `cut_top(h, gap=0)`, `cut_bottom`, `cut_left`, `cut_right`: return `(piece, rest)`

`split(start, length, n_or_weights, gap=0) -> [(pos, size)]`: integer sizes that add up exactly.

`claim(rect, name)`: registers a custom region so the checks cover it; panels, the header and the
footer register themselves. Regions may nest (a hand-drawn part inside a panel); only partial
overlaps are reported. Text that crosses a claimed region's edge is reported too.

## Charts and widgets

`bar3d(x, base, w, h, color, *, depth=None, slope=2, stripes=5, shadow="shadow", rim=True) -> Rect`
- An extruded column standing on row `base`. The front face fills `base - h .. base - 1` and
  `x .. x + w - 1`, with stripes every `stripes` px and a light left rim. A lit top face adds `depth`
  rows above it, and a dark striped side adds `depth * slope` px to its right, both receding
  up-right. Slope 2 matches `iso_box`. `shadow` fills the floor under the receding side.
- `depth=None` picks about `w / 6` rows (`bar_depth`); `depth=0` draws the flat reference style,
  which has a dark right edge and a cast shadow instead.
- Returns the front face.

`bar_chart(x, y, w, h, values, *, colors=None, ymax=None, ticks=4, tick_fmt=compact, fmt=None, bar_w=None, depth=None, slope=2, deltas=False, delta_fmt=None, labels=True, xlabels=None, axis="line", grid="line", tick_color="dim", value_color="white", stripes=5, shadow="shadow", axis_w=None, grow=1.0) -> [Rect]`
- The axis line is row `y + h - 1`, and `ymax` (rounded up to a nice value by default) maps to the
  front top at row `y`. The top face and the value label stack `depth + 7` px above the bar, so leave
  that room above `y` for the tallest one.
- Bars take 55% of their slot unless `bar_w` is set. With `deltas=True` they narrow until each %
  change tag fits its gap with 1px clear. `xlabels` draw 3px under the axis.
- Returns each bar's bounding Rect including the extrusion: `r.cx` centres things under the bar,
  `r.y` is the top of its top face and `r.x2` its right edge.
- `grow`: one fraction or one per bar, for intros. The layout comes from the final values, bars rise
  to their share, value labels count up, and a delta appears once both of its bars reach 1.

`hbars(x, y, w, items, *, colors=None, vmax=None, fmt=None, label_w=None, value_w=None, bar_h=5, gap=3, track="raised", label_color="text", value_color="white", rim=True) -> y below`
- `items`: `(label, value)` or `(label, value, colour)`. Labels sit left, values right-aligned at
  `x + w`, and bars fill the middle against a track.

`meter(x, y, w, h, frac, color, *, track="raised", rim=True) -> filled width`

`stacked(x, y, w, h, parts, *, total=None, track="raised", rim=False) -> [(x, w)]`: `parts` are `(value, colour)`.

`strip(x, y, w, h, colors)`: equal blocks side by side (the rainbow rule).

`tile(x, y, size, color, *, bevel=True)`: a bevelled square (light top-left, dark bottom-right).
Neutral fills such as `raised` look sunken.

`waffle(x, y, parts, *, cols=10, rows=10, cell=4, gap=1, total=None, empty="raised", bevel=True) -> [tiles per part]`
- `parts` are `(value, colour)`. Tiles fill in reading order, and whatever `total` leaves over
  stays `empty`. The grid is `cols * (cell + gap) - gap` wide.

`seg_column(x, y, w, h, frac, color, *, seg=1, gap=1, empty="raised", cap=None) -> lit`: an LED column lit from the bottom.

`gauge(x, y, w, frac, color, *, h=5, track="shadow", border="line")`: a thermometer slider.

`spark(x, y, w, h, values, color, *, fill=None, lo=None, hi=None) -> [y per column]`: resampled to `w` columns.

`grid(x, y, w, h, *, rows=4, cols=0, color="line", dotted=True, step=2)`: guides including the edges.

`tag(x, y, s, color="white", *, fill="panel", border="line", align="left", pad=2, font="small") -> Rect`: a boxed label 9px tall; `y` is the box top.

`legend(x, y, items, *, color="text", gap=6, swatch=3, align="left") -> width`: `items` are `(label, colour)`.

`kv(x, y, w, items, *, label="dim", value="white", step=7) -> y below`: `items` are `(label, value[, colour])`.

`chip(x, y, w, h, label, color, *, cores=0, outline="muted", fill="panel", pins="dim") -> Rect`
- A pinned processor outline with `label` in the large font; with `cores`, it adds two rows of 2×2
  squares (needs `h >= 20`). Pins sit 1px outside the box.

## Diagrams

Boxes joined by lines, for architecture and flow diagrams. `examples/diagram.py` uses every part.

`node(x, y, w, h, title, *, color="cyan", sub=None, badge=None, badge_color="dim", fill="panel", border="line", align="left") -> Rect`
- A box with a 1px border, a 1px accent band along the top, a white title 4px from the top, an
  optional dim subtitle 7px below it, and an optional badge right-aligned on the title row.
- Use `h=12` for a title only and `h=19` with a subtitle.
- Registers itself as a region: overlapping nodes, and titles too long for their box, are
  reported.

`connect(a, b, color, *, via=None, ax=None, bx=None, side=None, label=None, label_color="dim", dotted=False, head=True) -> [points]`
- An orthogonal elbow from Rect `a`'s facing edge to Rect `b`'s, ending in a head just outside
  `b`. The run is vertical when one Rect is above the other, horizontal otherwise.
- `side="top"` or `"bottom"` leaves and enters both boxes through that edge: a U-shaped run for
  boxes in the same row. Give several such runs different `via` lanes so they don't overlap.
- `ax` and `bx` move the anchors along the edges (an x for vertical runs, a y for horizontal
  ones), so several lines can leave one box apart.
- `via` puts the middle segment in a chosen gutter, and `label` sits beside that segment.
- Returns the corner points.

`arrow(x0, y0, x1, y1, color, *, dotted=False, head=True)`: a straight horizontal or vertical
arrow whose 3px head's tip sits on `(x1, y1)`. Diagonal arrows raise `ValueError`.

`bus(x, y, w, color, taps=(), *, thick=2, heads=True, dotted=False) -> Rect`: a rail that many
parts connect to instead of a line each, such as a shared dependency. `taps` are Rects, or
`(Rect, x)` pairs, above or below the rail. Each gets a stub with its head on the rail.

`dashes(x, y, length, color, *, vertical=False, on=2, off=2)`: a dashed line, for boundaries
such as a process or sandbox edge.

Routing tips:
- Lay nodes out in rows by layer, and route connectors through the gutters between rows with
  `via`.
- Draw the most shared dependency as a `bus`.
- Use `dotted=True` for optional or runtime links and solid lines for build-time ones.
- Lines aren't collision-checked, so look at the PNG for crossings.

## Illustration

`sprite(x, y, art, colors, *, scale=1, flip=False) -> (w, h)`
- `art` is a multi-line string or a list of rows. Each character maps through `colors`; `.` and spaces
  are transparent.

`icon(x, y, name, color, *, scale=1) -> (w, h)`
- `ICONS`: bolt, heart, star, clock, check, cross, note, play, warn, cpu, temp, disc, invader, up,
  down, file, folder, package, lock.

`iso_box(x, y, w, d, h, *, top, left, right, edge=None, corner=None, outline=None, shadow=None, patterns=None) -> Iso`
- `(x, y)` is the back corner of the top face. `w` units run down-right and `d` units down-left (2px
  across and 1px down per unit); the sides are `h` px tall. On screen the box is `2(w + d)` wide and
  `w + d + h` tall.
- Each face takes a colour, or a list of colours for a dithered left-to-right gradient.
  `patterns={"left": ("grille", colour)}` textures a face along its slant, 1px in from the edges.
- `edge` lights the front rims of the top face, `corner` the vertical front edge, and `shadow` drops
  the footprint down-right.
- `Iso.top(u, v)`, `Iso.left(u, b)` and `Iso.right(v, b)` return screen points for details (LEDs,
  ports, labels). `b` counts pixels down a side face. `Iso.bounds` is the bounding Rect.
- `h=0` with `left=None, right=None` draws only a top face, which works as an inset lid or tile.

`iso_floor(x, y, w, d, *, step=4, color="line", dots=False) -> Iso`
- An isometric grid in iso_box coordinates. To centre a `w×d×h` box on a floor with margin `m`, use
  floor apex `(x, y + h - 2m)` and size `(w + 2m, d + 2m)`. Keep sizes multiples of `step` so the
  box edges land on grid lines.

`sparkles(x, y, w, h, n, colors, *, seed=7, twinkle=0.12)`: scattered pixels; `twinkle` is the share drawn as plus-shaped glints.

`image(src, x, y, w=None, h=None, *, colors=None, dither=0.0, alpha=128) -> (w, h)`
- Resizes (box filter when shrinking) and locks the image to the theme palette in Oklab. `colors`
  takes a list of names to restrict the palette, or `"keep"` to paste a pre-pixelated sprite as it is.
  Alpha below `alpha` is transparent.

## Animation

`animate(draw, path, *, seconds=2.0, fps=20, hold=0.0, seamless=False, poster=None, scale=None, quiet=False, **canvas) -> Path`
- Calls `draw(c, t)` on a fresh `Canvas(**canvas)` for each of `round(seconds * fps)` frames, with
  `t` running from 0 to 1. `canvas` takes the usual Canvas arguments (`preset`, `w`, `h`, `theme`,
  `bg`).
- `seamless=True` drops the t=1 frame so periodic motion loops without repeating a frame. `hold`
  keeps the last frame on screen for extra seconds before the loop restarts. The file loops forever.
- The extension picks the format: `.gif` (one shared palette), `.webp` (lossless), `.png` (APNG) or
  `.mp4` (H.264 through ffmpeg; odd sizes get a 1px pad). Identical consecutive frames merge and
  unchanged areas aren't re-stored, so files stay small.
- Also writes `NAME-poster.png` beside the output: the frame at `t=poster`, the last by default. It
  prints the path of a contact sheet in the temp folder (`pixelkit/NAME.frames.png`) with up to 9
  sampled frames labelled by index and t; open it to review the motion.
- Runs `check()` on every frame and prints each distinct warning once, with the first frame it
  appeared in.

Timing helpers (all take and return plain floats):

| Helper | Gives |
|--------|-------|
| `phase(t, start, end)` | progress through a window of the timeline, clamped to 0..1 |
| `stagger(t, i, n, *, start=0, end=1, overlap=0.5)` | progress of item `i` of `n` in turn; `overlap` 0 is strictly one after another, 1 all together |
| `ease_out(p)`, `ease_in_out(p)`, `ease_back(p, overshoot=1.70158)` | easing curves; `ease_back` overshoots then settles |
| `steps(p, n)` | progress in `n` jumps, for a mechanical feel |
| `wave(t, cycles=1, offset=0)` | a 0..1 oscillation, seamless with whole `cycles` |
| `blink(t, cycles=1, duty=0.5, offset=0)` | on/off, on for the first `duty` share of each cycle |
| `reveal(text, p)` | the first share `p` of a string (typewriter) |
| `lerp(a, b, p)`, `clamp01(v)` | interpolation and clamping |

Seamless loops: give every moving element a whole number of cycles over the loop. Scroll a periodic
signal by exactly one period (`dashboard_live.py` has a `signal()` helper), and seed randomness
per tick (`random.Random(int(t * seconds))`) so readings change once a second instead of every
frame.

## Export and checks

`save(path, scale=None, *, quiet=False) -> Path`
- Nearest-neighbour upscale (preset scale by default), written as a palette PNG. Prints each warning
  from `check()` and then the path, size and file size.

`check() -> [str]` reports:
- text overlapping or touching other text in any direction. Boxes cover the real ink: accents,
  descenders, shadows and outlines.
- text crossing the edge of a panel, the header, the footer or a claimed region
- regions partly overlapping (panels, the header and the footer included)
- anything running off the canvas
- missing glyphs

Parts that aren't text (bars, icons, sprites) aren't collision-checked. Look at the PNG.

## Theme file

```toml
name = "navy"
scale = 4                                  # default export scale
series = ["green", "yellow", "orange", "red", "purple", "blue"]
thousands = ","                            # Canvas.num() separators
decimal = "."

[brand]
name = ""                                  # printed at the right of footers when set
mark = "stripes"                           # "stripes", "none" or a path to a small PNG

[colors]                                   # neutrals: shadow bg panel raised line dim muted text white
bg = "#0a0e15"

[accents]                                  # each gets name, name.light, name.dark
green = { base = "#61bb46", dark = "#3f752d", light = "#9fd599" }
```

Accents in the default theme: green, yellow, orange, red, purple, blue (the series), and cyan, lime,
sky, violet, gold. A missing `dark` or `light` is mixed automatically.

## pixelate.py

```bash
python3 scripts/pixelate.py IN OUT (--width W | --height H) [--colors a,b,c] [--dither 0..1] [--key] [--tol 60] [--preview 4]
```
- Resizes to the logical size and locks the result to the theme palette.
- `--key` makes the flat background (sampled from the corners) transparent and trims to the content.
  Generate art on plain magenta or white for clean cut-outs.
- `--preview N` also writes an upscaled copy for viewing.

## Module helpers

- `compact(v)`: 25000 → "25K"
- `nice_max(v, ticks=4)`: a rounded axis maximum
- `bar_depth(w, slope=2)`: the default extrusion for a bar `w` px wide
- `lock(img, palette, dither=0, alpha=128)`: palette locking for PIL images
- `load_theme(path=None)`
- `FONTS["small" | "large"]`: `.measure()`, `.wrap()`, `.line_height()`
- `PRESETS`, `PATTERNS`, `ICONS`
