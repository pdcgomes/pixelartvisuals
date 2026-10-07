"""Charts and widgets, mixed into Canvas. Coordinates are logical pixels."""

from __future__ import annotations

import math

from .fonts import FONTS
from .geometry import Rect, split
from .theme import mix


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def alloc(total: int, fracs) -> list[int]:
    """Integer widths for fractions of `total`, largest remainder so they add up exactly."""
    raw = [total * f for f in fracs]
    sizes = [int(r) for r in raw]
    target = round(sum(raw))
    for i in sorted(range(len(raw)), key=lambda i: sizes[i] - raw[i])[: max(0, target - sum(sizes))]:
        sizes[i] += 1
    return sizes


def nice_max(v: float, ticks: int = 4) -> float:
    """Round an axis maximum up so each of `ticks` steps is 1, 2, 2.5 or 5 times a power of ten."""
    if v <= 0:
        return float(ticks)
    mag = 10 ** math.floor(math.log10(v / ticks))
    for m in (1, 2, 2.5, 5, 10):
        if m * mag * ticks >= v:
            return m * mag * ticks
    return 10 * mag * ticks


def bar_depth(w: int, slope: int = 2) -> int:
    """Default extrusion rows for a bar w px wide: a 15px bar gets 3 (a 6px side at slope 2)."""
    return max(1, int(w / (4 + slope) + 0.5))


def compact(v: float) -> str:
    """25000 -> 25K, 1500000 -> 1.5M."""
    for div, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(v) >= div:
            q = v / div
            return f"{q:.0f}{suffix}" if q == int(q) else f"{q:.1f}{suffix}"
    return f"{v:.0f}" if v == int(v) else f"{v:.1f}"


class Widgets:
    # bars --------------------------------------------------------------------

    def bar3d(self, x: int, base: int, w: int, h: int, color, *, depth=None, slope: int = 2, stripes: int = 5,
              shadow="shadow", rim: bool = True):
        """Striped column standing on row `base`; the front face fills base-h .. base-1 and x .. x+w-1.
        A lit top face and a dark side recede up-right, `slope` px across per px up (2 matches iso_box),
        for `depth` rows (auto from the width). The side adds depth*slope px on the right and the top
        adds depth rows above. depth=0 draws the flat style of the original reference.
        Returns the front face Rect."""
        if h <= 0:
            return Rect(x, base, w, 0)
        top = base - h
        dark, light = self.dark(color), self.light(color)
        deep = mix(self.rgb(dark), self.rgb("shadow"), 0.45)
        depth = bar_depth(w, slope) if depth is None else depth
        if depth <= 0:
            side = max(1, round(w / 9))
            rim_w = 2 if w >= 12 else 1
            if shadow is not None and h > 3:
                self.rect(x + w, top + 3, side, h - 3, shadow)
            self.rect(x, top, w, h, color)
            self.rect(x + w - side, top, side, h, dark)
            if stripes:
                for sy in range(top + 4, base - 1, stripes):
                    self.hline(x + rim_w, sy, w - rim_w - side, dark)
                    self.hline(x + w - side, sy, side, deep)
            if rim:
                self.rect(x, top, rim_w, h, light)
                self.rect(x, top, w, 2 if h >= 12 else 1, light)
            return Rect(x, top, w, h)
        side = depth * slope
        for j in range(side):
            if shadow is not None:
                self.rect(x + w + j, base - 1 - j // slope, 1, j // slope + 1, shadow)
            self.rect(x + w + j, top - j // slope, 1, h - 1, dark)
        for k in range(depth):
            self.rect(x + 1 + k * slope, top - 1 - k, w + slope - 1, 1, light)
        self.rect(x + 1, top - 1, w + slope - 1, 1, mix(self.rgb(light), (255, 255, 255), 0.45))
        self.rect(x, top, w, h, color)
        if stripes:
            for sy in range(top + 4, base - 1, stripes):
                self.hline(x + 1, sy, w - 1, dark)
                for j in range(side):
                    self.px(x + w + j, sy - j // slope - 1, deep)
        if rim:
            self.vline(x, top, h, light)
        return Rect(x, top, w, h)

    def bar_chart(self, x: int, y: int, w: int, h: int, values, *, colors=None, ymax=None, ticks: int = 4,
                  tick_fmt=compact, fmt=None, bar_w=None, depth=None, slope: int = 2, deltas: bool = False,
                  delta_fmt=None, labels: bool = True, xlabels=None, axis="line", grid="line",
                  tick_color="dim", value_color="white", stripes: int = 5, shadow="shadow", axis_w=None,
                  grow=1.0):
        """Vertical extruded bars with a dotted grid, tick labels, value labels, optional category
        labels under the axis (xlabels, drawn below y+h) and optional percentage-change tags
        between neighbours (bars narrow until the tags fit their gaps). Returns each bar's bounding
        Rect, extrusion included, so r.cx centres things under the bar and r.y is its top face.
        grow (one 0..1 or one per bar) animates an intro: layout stays fixed, bars rise, labels
        count up and a delta appears once both of its bars are fully grown."""
        n = len(values)
        colors = colors or [self.series(i) for i in range(n)]
        ymax = ymax or nice_max(max(values), ticks)
        fmt = fmt or self.num
        tick_labels = [tick_fmt(ymax * k / ticks) for k in range(ticks + 1)]
        aw = axis_w if axis_w is not None else max(self.measure(t) for t in tick_labels) + 6
        px0, pw = x + aw, w - aw
        base = y + h - 1
        ph = base - y
        for k in range(ticks + 1):
            gy = base - round(ph * k / ticks)
            if k == 0:
                self.hline(px0 - 2, base, pw + 2, axis)
            elif grid:
                self.dots(px0, gy, pw, grid)
            self.text(px0 - 4, gy - 2, tick_labels[k], tick_color, align="right")
        slots = split(px0, pw, n, 0)
        slot_w = min(s for _, s in slots)
        delta_fmt = delta_fmt or (lambda p: f"{p:+.0f}%")
        tags = [delta_fmt((values[i] / values[i - 1] - 1) * 100) if deltas and values[i - 1] else None
                for i in range(1, n)]
        tag_w = max((self.measure(t) + 6 for t in tags if t), default=0)
        bw = bar_w or max(3, round(slot_w * 0.55))
        d = bar_depth(bw, slope) if depth is None else depth
        while tag_w and not bar_w and bw > 3 and slot_w - bw - d * slope < tag_w + 2:
            bw -= 1
            d = bar_depth(bw, slope) if depth is None else depth
        side = d * slope
        grows = [clamp(g) for g in (grow if isinstance(grow, (list, tuple)) else [grow] * n)]
        rects = []
        for i, (v, g, (sx, sw)) in enumerate(zip(values, grows, slots)):
            bx = sx + (sw - bw - side) // 2
            front = self.bar3d(bx, base, bw, round(ph * v / ymax * g), colors[i], depth=d, slope=slope,
                               stripes=stripes, shadow=shadow)
            lift = d if front.h else 0
            r = Rect(bx, front.y - lift, bw + side, front.h + lift)
            rects.append(r)
            if labels and g > 0:
                self.text(r.cx, r.y - 7, fmt(v * g), value_color, align="center")
            if xlabels:
                self.text(r.cx, base + 3, xlabels[i], "text", align="center")
        for i, s in enumerate(tags, start=1):
            if s and min(grows[i - 1], grows[i]) >= 1:
                a, b = rects[i - 1], rects[i]
                self.tag((a.x2 + b.x) // 2, (a.y + b.y) // 2 - 4, s, self.light(colors[i]), align="center")
        return rects

    def hbars(self, x: int, y: int, w: int, items, *, colors=None, vmax=None, fmt=None, label_w=None,
              value_w=None, bar_h: int = 5, gap: int = 3, track="raised", label_color="text",
              value_color="white", rim: bool = True) -> int:
        """Ranking rows: label, bar, value. Items are (label, value) or (label, value, colour).
        Returns the y below the last row."""
        fmt = fmt or self.num
        labels = [str(it[0]) for it in items]
        vals = [it[1] for it in items]
        cols = [it[2] if len(it) > 2 else (colors[i % len(colors)] if colors else self.series(i))
                for i, it in enumerate(items)]
        lw = label_w if label_w is not None else max(self.measure(s) for s in labels) + 5
        vw = value_w if value_w is not None else max(self.measure(fmt(v)) for v in vals) + 4
        bx, bw = x + lw, w - lw - vw
        vmax = vmax or max(vals)
        ty = (bar_h - 5) // 2
        for i, (label, v, c) in enumerate(zip(labels, vals, cols)):
            ry = y + i * (bar_h + gap)
            self.text(x, ry + ty, label, label_color)
            self.rect(bx, ry, bw, bar_h, track)
            fw = round(bw * clamp(v / vmax)) if vmax else 0
            if fw:
                self.rect(bx, ry, fw, bar_h, c)
                if rim and bar_h >= 3:
                    self.hline(bx, ry, fw, self.light(c))
                    self.hline(bx, ry + bar_h - 1, fw, self.dark(c))
            self.text(x + w, ry + ty, fmt(v), value_color, align="right")
        return y + len(items) * (bar_h + gap) - gap

    # meters ------------------------------------------------------------------

    def meter(self, x: int, y: int, w: int, h: int, frac: float, color, *, track="raised", rim: bool = True) -> int:
        """Progress bar filled from the left. Returns the filled width."""
        self.rect(x, y, w, h, track)
        fw = round(w * clamp(frac))
        if fw:
            self.rect(x, y, fw, h, color)
            if rim and h >= 3:
                self.hline(x, y, fw, self.light(color))
        return fw

    def stacked(self, x: int, y: int, w: int, h: int, parts, *, total=None, track="raised", rim: bool = False):
        """Segmented bar: parts are (value, colour). The rest of `total` stays as track.
        Returns (x, width) per part."""
        total = total or sum(v for v, _ in parts)
        widths = alloc(w, [v / total for v, _ in parts])
        self.rect(x, y, w, h, track)
        out, pos = [], x
        for (_, c), pw in zip(parts, widths):
            self.rect(pos, y, pw, h, c)
            if rim and h >= 3:
                self.hline(pos, y, pw, self.light(c))
            out.append((pos, pw))
            pos += pw
        return out

    def tile(self, x: int, y: int, size: int, color, *, bevel: bool = True) -> None:
        """Bevelled square: light top-left, dark bottom-right. Neutral fills look sunken."""
        self.rect(x, y, size, size, color)
        if not bevel or size < 3:
            return
        neutral = color in ("raised", "panel", "bg", "line", "shadow")
        lit, deep = ("shadow", "line") if neutral else (self.light(color), self.dark(color))
        self.hline(x, y, size - 1, lit)
        self.vline(x, y, size - 1, lit)
        self.hline(x + 1, y + size - 1, size - 1, deep)
        self.vline(x + size - 1, y + 1, size - 1, deep)

    def waffle(self, x: int, y: int, parts, *, cols: int = 10, rows: int = 10, cell: int = 4, gap: int = 1,
               total=None, empty="raised", bevel: bool = True) -> list[int]:
        """Part-to-whole grid of tiles filled in reading order. Parts are (value, colour); whatever
        `total` leaves over stays `empty`. Returns the number of tiles per part."""
        n = cols * rows
        total = total or sum(v for v, _ in parts)
        counts = alloc(n, [v / total for v, _ in parts])
        fills = [col for (_, col), k in zip(parts, counts) for _ in range(k)]
        fills += [empty] * (n - len(fills))
        for i, col in enumerate(fills):
            r, k = divmod(i, cols)
            self.tile(x + k * (cell + gap), y + r * (cell + gap), cell, col, bevel=bevel)
        return counts

    def strip(self, x: int, y: int, w: int, h: int, colors) -> None:
        """Equal blocks of colour side by side (the rainbow rule under a hero number)."""
        pos = x
        for c, cw in zip(colors, alloc(w, [1 / len(colors)] * len(colors))):
            self.rect(pos, y, cw, h, c)
            pos += cw

    def seg_column(self, x: int, y: int, w: int, h: int, frac: float, color, *, seg: int = 1, gap: int = 1,
                   empty="raised", cap=None) -> int:
        """Vertical LED meter lit from the bottom. Returns the number of lit segments."""
        n = (h + gap) // (seg + gap)
        lit = round(clamp(frac) * n)
        for k in range(n):
            c = color if k < lit else empty
            if cap is not None and k == lit - 1:
                c = cap
            self.rect(x, y + h - seg - k * (seg + gap), w, seg, c)
        return lit

    def gauge(self, x: int, y: int, w: int, frac: float, color, *, h: int = 5, track="shadow", border="line") -> None:
        """Thermometer-style slider: a bulb on the left, a lighter stem to `frac`."""
        self.rect(x, y, w, h, track)
        self.box(x, y, w, h, border)
        stem = round((w - 4) * clamp(frac))
        self.rect(x + 3, y + 1, stem, h - 2, self.light(color))
        self.rect(x, y, 3, h, color)
        self.px(x + 1, y + 1, self.light(color))

    def spark(self, x: int, y: int, w: int, h: int, values, color, *, fill=None, lo=None, hi=None) -> list[int]:
        """Sparkline resampled to w columns; `fill` shades the area beneath. Returns the y per column."""
        vals = list(values)
        lo = min(vals) if lo is None else lo
        hi = max(vals) if hi is None else hi
        hi = lo + 1 if hi == lo else hi
        n = len(vals)
        ys = []
        for i in range(w):
            t = i * (n - 1) / (w - 1) if w > 1 and n > 1 else 0
            k = min(int(t), max(0, n - 2))
            v = vals[k] + (vals[k + 1] - vals[k]) * (t - k) if n > 1 else vals[0]
            ys.append(y + h - 1 - round(clamp((v - lo) / (hi - lo)) * (h - 1)))
        if fill is not None:
            for i, yy in enumerate(ys):
                self.rect(x + i, yy + 1, 1, y + h - 1 - yy, fill)
        for i in range(1, len(ys)):
            self.line(x + i - 1, ys[i - 1], x + i, ys[i], color)
        if len(ys) == 1:
            self.px(x, ys[0], color)
        return ys

    def grid(self, x: int, y: int, w: int, h: int, *, rows: int = 4, cols: int = 0, color="line",
             dotted: bool = True, step: int = 2) -> None:
        """Evenly spaced guide lines including the edges."""
        for j in range(rows + 1 if rows else 0):
            gy = y + round(j * (h - 1) / rows)
            if dotted:
                self.dots(x, gy, w, color, step)
            else:
                self.hline(x, gy, w, color)
        for i in range(cols + 1 if cols else 0):
            gx = x + round(i * (w - 1) / cols)
            if dotted:
                self.vdots(gx, y, h, color, step)
            else:
                self.vline(gx, y, h, color)

    # labels ------------------------------------------------------------------

    def tag(self, x: int, y: int, s, color="white", *, fill="panel", border="line", align: str = "left",
            pad: int = 2, font: str = "small"):
        """Boxed label (e.g. a +34% delta). y is the box top. Returns the box Rect."""
        cap = FONTS[font].cap
        w, h = self.measure(s, font) + 2 * pad + 2, cap + 4
        x0 = x - w // 2 if align == "center" else x - w if align == "right" else x
        self.rect(x0, y, w, h, fill)
        self.box(x0, y, w, h, border)
        self.text(x0 + 1 + pad, y + 2, s, color, font=font)
        return Rect(x0, y, w, h)

    def legend(self, x: int, y: int, items, *, color="text", gap: int = 6, swatch: int = 3,
               align: str = "left") -> int:
        """Swatch + label pairs on one line. Items are (label, colour). Returns total width."""
        widths = [swatch + 2 + self.measure(label) for label, _ in items]
        total = sum(widths) + gap * (len(items) - 1)
        pen = x - total if align == "right" else x - total // 2 if align == "center" else x
        for (label, c), iw in zip(items, widths):
            self.rect(pen, y + 1, swatch, swatch, c)
            self.text(pen + swatch + 2, y, label, color)
            pen += iw + gap
        return total

    def kv(self, x: int, y: int, w: int, items, *, label="dim", value="white", step: int = 7) -> int:
        """Stat list: dim labels on the left, values right-aligned. Items are (label, value[, colour])."""
        for i, (k, v, *rest) in enumerate(items):
            self.text(x, y + i * step, k, label)
            self.text(x + w, y + i * step, v, rest[0] if rest else value, align="right")
        return y + len(items) * step

    # icons -------------------------------------------------------------------

    def chip(self, x: int, y: int, w: int, h: int, label, color, *, cores: int = 0, outline="muted",
             fill="panel", pins="dim"):
        """Processor icon: pinned outline, label in the large face, optional grid of cores."""
        if pins is not None:
            self.dots(x + 2, y - 1, w - 3, pins)
            self.dots(x + 2, y + h, w - 3, pins)
            self.vdots(x - 1, y + 2, h - 3, pins)
            self.vdots(x + w, y + 2, h - 3, pins)
        self.rect(x, y, w, h, fill)
        self.box(x, y, w, h, outline)
        self.text(x + w // 2, y + 3, label, color, font="large", align="center")
        if cores:
            per_row = math.ceil(cores / 2)
            gx, gy = x + (w - (per_row * 3 - 1)) // 2, y + 12
            for k in range(cores):
                r, c = divmod(k, per_row)
                self.rect(gx + c * 3, gy + r * 3, 2, 2, self.light(color) if r == 0 else color)
        return Rect(x, y, w, h)

    # diagrams ----------------------------------------------------------------

    def dashes(self, x: int, y: int, length: int, color, *, vertical: bool = False, on: int = 2, off: int = 2) -> None:
        """Dashed line, `on` pixels drawn then `off` skipped, for boundaries."""
        for i in range(0, length, on + off):
            n = min(on, length - i)
            if vertical:
                self.vline(x, y + i, n, color)
            else:
                self.hline(x + i, y, n, color)

    def _segment(self, x0: int, y0: int, x1: int, y1: int, color, dotted: bool) -> None:
        vertical = x0 == x1
        start, n = (min(y0, y1), abs(y1 - y0) + 1) if vertical else (min(x0, x1), abs(x1 - x0) + 1)
        if dotted:
            self.dashes(x0 if vertical else start, start if vertical else y0, n, color, vertical=vertical,
                        on=1, off=1)
        elif vertical:
            self.vline(x0, start, n, color)
        else:
            self.hline(start, y0, n, color)

    def _head(self, x: int, y: int, direction: str, color) -> None:
        for k in range(3):
            if direction == "right":
                self.vline(x - k, y - k, 2 * k + 1, color)
            elif direction == "left":
                self.vline(x + k, y - k, 2 * k + 1, color)
            elif direction == "down":
                self.hline(x - k, y - k, 2 * k + 1, color)
            else:
                self.hline(x - k, y + k, 2 * k + 1, color)

    def arrow(self, x0: int, y0: int, x1: int, y1: int, color, *, dotted: bool = False, head: bool = True) -> None:
        """Horizontal or vertical arrow; the 3px head's tip sits on (x1, y1)."""
        if x0 != x1 and y0 != y1:
            raise ValueError("arrow() draws horizontal or vertical lines; use connect() for an elbow")
        self._segment(x0, y0, x1, y1, color, dotted)
        if head and (x0, y0) != (x1, y1):
            direction = ("right" if x1 > x0 else "left") if y0 == y1 else ("down" if y1 > y0 else "up")
            self._head(x1, y1, direction, color)

    def connect(self, a, b, color, *, via=None, ax=None, bx=None, side=None, label=None, label_color="dim",
                dotted: bool = False, head: bool = True) -> list[tuple[int, int]]:
        """Orthogonal elbow from Rect a's facing edge to Rect b's, ending in a head on b's edge.
        Vertical when one is above the other, otherwise horizontal. side="top" or "bottom" leaves
        and enters both boxes through that edge instead, a U-shaped run for boxes in the same row.
        `ax`/`bx` move the anchor along each edge (an x for vertical runs, a y for horizontal ones),
        `via` sets where the middle segment runs, and `label` sits beside it. Returns the corner
        points."""
        if side in ("top", "bottom"):
            sx, ex = (a.cx if ax is None else ax), (b.cx if bx is None else bx)
            if side == "bottom":
                sy, ey = a.y2, b.y2
                mid = max(a.y2, b.y2) + 5 if via is None else via
            else:
                sy, ey = a.y - 1, b.y - 1
                mid = min(a.y, b.y) - 6 if via is None else via
            pts = [(sx, sy), (sx, mid), (ex, mid), (ex, ey)]
        elif b.y >= a.y2 or a.y >= b.y2:
            down = b.y >= a.y2
            sx, ex = (a.cx if ax is None else ax), (b.cx if bx is None else bx)
            sy, ey = (a.y2, b.y - 1) if down else (a.y - 1, b.y2)
            mid = (sy + ey) // 2 if via is None else via
            pts = [(sx, sy), (sx, mid), (ex, mid), (ex, ey)]
        else:
            right = b.x >= a.x2
            sy, ey = (a.cy if ax is None else ax), (b.cy if bx is None else bx)
            sx, ex = (a.x2, b.x - 1) if right else (a.x - 1, b.x2)
            mid = (sx + ex) // 2 if via is None else via
            pts = [(sx, sy), (mid, sy), (mid, ey), (ex, ey)]
        pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:-1]):
            self._segment(x0, y0, x1, y1, color, dotted)
        if len(pts) > 1:
            (x0, y0), (x1, y1) = pts[-2], pts[-1]
            self.arrow(x0, y0, x1, y1, color, dotted=dotted, head=head)
        if label:
            (x0, y0), (x1, y1) = pts[len(pts) // 2 - 1], pts[len(pts) // 2]
            if y0 == y1:
                self.text((x0 + x1) // 2, y0 - 7, label, label_color, align="center")
            else:
                self.text(x0 + 3, (y0 + y1) // 2 - 2, label, label_color)
        return pts

    def bus(self, x: int, y: int, w: int, color, taps=(), *, thick: int = 2, heads: bool = True,
            dotted: bool = False):
        """A rail many parts connect to, instead of a line each. `taps` are Rects (or (Rect, x)
        pairs) above or below the rail; each gets a stub to it, with a head on the rail. Returns
        the rail's Rect."""
        self.rect(x, y, w, thick, color)
        for tap in taps:
            r, tx = (tap, tap.cx) if isinstance(tap, Rect) else tap
            if r.y2 <= y:
                self.arrow(tx, r.y2, tx, y - 1, color, dotted=dotted, head=heads)
            elif r.y >= y + thick:
                self.arrow(tx, r.y - 1, tx, y + thick, color, dotted=dotted, head=heads)
        return Rect(x, y, w, thick)

    def node(self, x: int, y: int, w: int, h: int, title, *, color="cyan", sub=None, badge=None,
             badge_color="dim", fill="panel", border="line", align: str = "left"):
        """A box for a module or component: border, accent band along the top, white title,
        optional dim subtitle and a small badge at the right of the title row. Registers itself
        so the overlap checks cover it. Returns its Rect."""
        r = Rect(x, y, w, h)
        self.claim(r, f"node {title!r}")
        self.rect(x, y, w, h, fill)
        self.box(x, y, w, h, border)
        self.hline(x + 1, y + 1, w - 2, color)
        ty = y + 4
        tx = x + w // 2 if align == "center" else x + 3
        self.text(tx, ty, title, "white", align=align)
        if sub:
            self.text(tx, ty + 7, sub, "dim", align=align)
        if badge:
            self.text(x + w - 3, ty, badge, badge_color, align="right")
        return r
