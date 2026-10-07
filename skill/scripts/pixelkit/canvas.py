"""Canvas: a low-resolution image with pixel-exact drawing, text, layout and export."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from .art import Art
from .fonts import FONTS
from .geometry import BAYER4, PATTERNS, Rect
from .theme import Theme, load_theme
from .widgets import Widgets

# name: (logical width, logical height, export scale)
PRESETS = {
    "wide": (320, 180, 4),      # 16:9  -> 1280x720
    "standard": (320, 240, 4),  # 4:3   -> 1280x960
    "og": (400, 210, 3),        # social card -> 1200x630
    "square": (256, 256, 4),    # -> 1024x1024
    "portrait": (240, 320, 4),  # 3:4   -> 960x1280
    "banner": (400, 100, 3),    # post header strip -> 1200x300
    "hd": (480, 270, 4),        # dense 16:9 -> 1920x1080
}

class Canvas(Widgets, Art):
    """Draw at logical resolution; save() scales up with nearest-neighbour."""

    def __init__(self, w: int | None = None, h: int | None = None, *, preset: str = "wide",
                 theme=None, bg="bg", scale: int | None = None):
        preset_scale = None
        if w is None or h is None:
            if preset not in PRESETS:
                raise ValueError(f"unknown preset {preset!r}; choose from {', '.join(PRESETS)}")
            w, h, preset_scale = PRESETS[preset]
        self.theme = theme if isinstance(theme, Theme) else load_theme(theme)
        self.w, self.h = w, h
        self.scale = scale or preset_scale or self.theme.scale
        self.img = Image.new("RGB", (w, h), self.rgb(bg))
        self._draw = ImageDraw.Draw(self.img)
        self.texts: list[tuple[Rect, str]] = []
        self.regions: list[tuple[Rect, str]] = []
        self.notes: list[str] = []

    # colour ------------------------------------------------------------------

    @property
    def bounds(self) -> Rect:
        return Rect(0, 0, self.w, self.h)

    def rgb(self, color):
        return self.theme.rgb(color)

    def light(self, color):
        return self.theme.shade(color, "light")

    def dark(self, color):
        return self.theme.shade(color, "dark")

    def series(self, i: int) -> str:
        return self.theme.series_color(i)

    def num(self, value: float, decimals: int = 0) -> str:
        return self.theme.num(value, decimals)

    # primitives --------------------------------------------------------------

    def px(self, x: int, y: int, color) -> None:
        if color is not None and 0 <= x < self.w and 0 <= y < self.h:
            self.img.putpixel((x, y), self.rgb(color))

    def rect(self, x: int, y: int, w: int, h: int, color) -> None:
        if color is not None and w > 0 and h > 0:
            self._draw.rectangle((x, y, x + w - 1, y + h - 1), fill=self.rgb(color))

    def box(self, x: int, y: int, w: int, h: int, color) -> None:
        """1px outline."""
        if color is not None and w > 0 and h > 0:
            self._draw.rectangle((x, y, x + w - 1, y + h - 1), outline=self.rgb(color))

    def hline(self, x: int, y: int, w: int, color) -> None:
        self.rect(x, y, w, 1, color)

    def vline(self, x: int, y: int, h: int, color) -> None:
        self.rect(x, y, 1, h, color)

    def dots(self, x: int, y: int, w: int, color, step: int = 2) -> None:
        for i in range(0, w, step):
            self.px(x + i, y, color)

    def vdots(self, x: int, y: int, h: int, color, step: int = 2) -> None:
        for j in range(0, h, step):
            self.px(x, y + j, color)

    def line(self, x0: int, y0: int, x1: int, y1: int, color) -> None:
        """Bresenham line, no anti-aliasing."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, points, color) -> None:
        for (a, b), (c, d) in zip(points, points[1:]):
            self.line(a, b, c, d, color)

    def pattern(self, x: int, y: int, w: int, h: int, color, kind: str = "checker") -> None:
        """Ink the pixels of a repeating pattern (see PATTERNS); the rest stay as they are."""
        test, rgb = PATTERNS[kind], self.rgb(color)
        for j in range(max(0, y), min(self.h, y + h)):
            for i in range(max(0, x), min(self.w, x + w)):
                if test(i, j):
                    self.img.putpixel((i, j), rgb)

    def gradient(self, x: int, y: int, w: int, h: int, colors, *, vertical: bool = True) -> None:
        """Ordered-dither blend through a list of colours, top to bottom (or left to right)."""
        rgbs = [self.rgb(c) for c in colors]
        if len(rgbs) == 1:
            return self.rect(x, y, w, h, colors[0])
        n, span = len(rgbs) - 1, (h if vertical else w)
        for j in range(max(0, y), min(self.h, y + h)):
            for i in range(max(0, x), min(self.w, x + w)):
                pos = (((j - y) if vertical else (i - x)) + 0.5) / span * n
                k = min(int(pos), n - 1)
                hit = pos - k > (BAYER4[j % 4][i % 4] + 0.5) / 16
                self.img.putpixel((i, j), rgbs[k + 1] if hit else rgbs[k])

    # text --------------------------------------------------------------------

    def measure(self, s, font: str = "small", scale: int = 1) -> int:
        return FONTS[font].measure(s, scale)

    def text(self, x: int, y: int, s, color="text", *, font: str = "small", scale: int = 1,
             align: str = "left", shadow=None, shadow_offset: int = 1, outline=None, check: bool = True) -> int:
        """Draw text with its cap top at y; x is the left, centre or right edge per align. Returns width."""
        f = FONTS[font]
        norm = f.normalize(s)
        width = max(0, f.advance(norm) - f.tracking) * scale if norm else 0
        x0 = x - width // 2 if align == "center" else x - width if align == "right" else x
        passes = []
        if outline is not None:
            passes += [(outline, dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy]
        if shadow is not None:
            passes.append((shadow, shadow_offset, shadow_offset))
        passes.append((color, 0, 0))
        for col, ox, oy in passes:
            rgb = self.rgb(col)
            pen = x0
            for ch in norm:
                g = f.glyph(ch)
                for gx, gy in g.px:
                    px0, py0 = pen + gx * scale + ox, y + gy * scale + oy
                    self._draw.rectangle((px0, py0, px0 + scale - 1, py0 + scale - 1), fill=rgb)
                pen += (g.width + f.tracking) * scale
        if check and norm.strip():
            top, bot = f.ink_rows(norm)
            ext, drop = (1 if outline is not None else 0), (shadow_offset if shadow is not None else 0)
            self._note_text(Rect(x0 - ext, y + top * scale - ext, width + drop + 2 * ext,
                                 (bot - top) * scale + drop + 2 * ext), norm)
        return width

    def spans(self, x: int, y: int, parts, color="dim", *, font: str = "small", scale: int = 1,
              align: str = "left", shadow=None) -> int:
        """Multi-coloured run: parts are (text, colour) pairs or plain strings in `color`."""
        f = FONTS[font]
        items = [(f.normalize(p), color) if isinstance(p, str) else (f.normalize(p[0]), p[1]) for p in parts]
        full = "".join(t for t, _ in items)
        width = max(0, f.advance(full) - f.tracking) * scale if full else 0
        pen = x - width // 2 if align == "center" else x - width if align == "right" else x
        start = pen
        for t, col in items:
            self.text(pen, y, t, col, font=font, scale=scale, shadow=shadow, check=False)
            pen += f.advance(t, scale)
        if full.strip():
            top, bot = f.ink_rows(full)
            drop = 1 if shadow is not None else 0
            self._note_text(Rect(start, y + top * scale, width + drop, (bot - top) * scale + drop), full)
        return width

    def paragraph(self, x: int, y: int, s, w: int, color="text", *, font: str = "small", scale: int = 1,
                  line: int | None = None, align: str = "left") -> int:
        """Word-wrap into width w. Returns the y below the last line."""
        f = FONTS[font]
        step = (line or f.line_height(s)) * scale
        ax = x + w // 2 if align == "center" else x + w if align == "right" else x
        lines = f.wrap(s, w, scale)
        for i, ln in enumerate(lines):
            self.text(ax, y + i * step, ln, color, font=font, scale=scale, align=align)
        return y + len(lines) * step

    def _note_text(self, r: Rect, s: str) -> None:
        if not self.bounds.contains(r):
            self.notes.append(f"text runs off the canvas: {s!r} at {tuple(r)}")
        for other, t in self.texts:
            if r.x <= other.x2 and other.x <= r.x2 and r.y <= other.y2 and other.y <= r.y2:
                self.notes.append(f"text collides or touches: {t!r} and {s!r}")
        self.texts.append((r, s))

    def claim(self, r: Rect, name: str) -> None:
        """Register a layout region so the checks cover it. Regions may nest (a part inside a panel)
        but not partly overlap."""
        if not self.bounds.contains(r):
            self.notes.append(f"{name} runs off the canvas at {tuple(r)}")
        for other, n in self.regions:
            if r.intersects(other) and not (other.contains(r) or r.contains(other)):
                self.notes.append(f"{n} and {name} overlap")
        self.regions.append((r, name))

    # layout ------------------------------------------------------------------

    def mark(self, x: int, y: int, mark="stripes") -> tuple[int, int]:
        """The brand mark: stripes of the series colours, or a small PNG drawn at 1x."""
        if mark == "stripes":
            colors = self.theme.series[:6]
            for i, c in enumerate(colors):
                self.hline(x, y + i, 9, c)
            return 9, len(colors)
        return self.image(mark, x, y, colors="keep")

    def header(self, title, sub=None, right=None, *, font: str = "small", color="white", mark=None,
               h: int = 12, line="line", fill=None, pad: int = 4) -> int:
        """Top bar: optional mark, title, dim subtitle, right-aligned text, rule. Returns content top."""
        if fill is not None:
            self.rect(0, 0, self.w, h - 1, fill)
        f = FONTS[font]
        x = pad
        mark = self.theme.brand.get("mark", "stripes") if mark is None else mark
        if mark and mark != "none":
            mw, mh = self.mark(x, (h - 1 - 6) // 2, mark)
            x += mw + 4
        x += self.text(x, (h - 1 - f.cap) // 2, title, color, font=font)
        sy = (h - 1 - 5) // 2
        if sub:
            self.text(x + 6, sy, sub, "dim")
        if right is not None:
            self.spans(self.w - pad, sy, [right] if isinstance(right, str) else right, "dim", align="right")
        if line:
            self.hline(0, h - 1, self.w, line)
        self.claim(Rect(0, 0, self.w, h), "header")
        return h + 1

    def panel(self, x: int, y: int, w: int, h: int, title=None, *, color="cyan", sub=None, right=None,
              right_color="text", fill="panel", border="line", pad: int = 4) -> Rect:
        """Bordered box with an accent title, dim subtitle and right-aligned text. Returns the content rect."""
        self.claim(Rect(x, y, w, h), f"panel {title or sub!r}" if title or sub else "panel")
        self.rect(x, y, w, h, fill)
        self.box(x, y, w, h, border)
        top = y + pad
        if title or sub:
            parts = [(title, color)] if title else []
            if sub:
                parts.append(((" " if title else "") + sub, "dim"))
            self.spans(x + pad, top, parts)
            top += 5 + 3
        if right is not None:
            self.spans(x + w - pad, y + pad, [(right, right_color)] if isinstance(right, str) else right,
                       right_color, align="right")
        return Rect(x + pad, top, w - 2 * pad, y + h - pad - top)

    def footer(self, lines, *, color="dim", line="line", pad: int = 4, brand: bool = True) -> int:
        """Source notes along the bottom, wrapped, under a rule. Returns the rule's y: call it
        before laying out panels so they can end above it."""
        f = FONTS["small"]
        name = self.theme.brand.get("name", "") if brand else ""
        avail = self.w - 2 * pad - (self.measure(name) + 8 if name else 0)
        lines = [lines] if isinstance(lines, str) else list(lines)
        wrapped = [w for ln in lines for w in f.wrap(ln, avail)] or [""]
        step = f.line_height(" ".join(wrapped))
        top = self.h - pad - (len(wrapped) * step - (step - f.cap)) - 3 - 1
        if line:
            self.hline(0, top, self.w, line)
        for i, ln in enumerate(wrapped):
            self.text(pad, top + 4 + i * step, ln, color)
        if name:
            self.text(self.w - pad, top + 4, name, "muted", align="right")
        self.claim(Rect(0, top, self.w, self.h - top), "footer")
        return top

    # export ------------------------------------------------------------------

    def check(self) -> list[str]:
        notes = list(self.notes)
        for r, s in self.texts:
            for region, name in self.regions:
                if r.intersects(region) and not region.contains(r):
                    notes.append(f"text {s!r} crosses the edge of {name}")
        notes = list(dict.fromkeys(notes))
        for name, f in FONTS.items():
            if f.missing:
                notes.append(f"{name} font has no glyph for {''.join(sorted(f.missing))!r} (drawn as '?')")
        return notes

    def save(self, path, scale: int | None = None, *, quiet: bool = False) -> Path:
        """Write a PNG scaled up with nearest-neighbour; prints layout warnings."""
        s = scale or self.scale
        path = Path(path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        out = self.img.resize((self.w * s, self.h * s), Image.NEAREST)
        colors = self.img.getcolors(256)
        if colors:
            flat = [v for _, rgb in colors for v in rgb]
            pal = Image.new("P", (1, 1))
            pal.putpalette(flat + flat[:3] * (256 - len(colors)))
            out = out.quantize(palette=pal, dither=Image.Dither.NONE)
        out.save(path, optimize=True)
        if not quiet:
            for note in self.check():
                print("warning:", note)
            print(f"wrote {path} ({out.width}x{out.height}, {max(1, path.stat().st_size // 1024)} KB)")
        return path
