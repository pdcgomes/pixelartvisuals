"""Finance terminal: candlesticks with moving averages and volume, a watchlist with sparklines, a
portfolio donut and a ticker tape. Fictional tickers on a seeded random walk; the last candle is live."""

import math
import random
import zlib
from pathlib import Path

from pixelkit import Canvas, animate

CANDLES = 50
NAMES = ["PIXL", "LAMP", "BYTE", "CAFE", "SPRT", "GLYPH"]
HOLDINGS = [("PIXL", 38, "green"), ("LAMP", 24, "red"), ("BYTE", 18, "sky"), ("CASH", 20, "muted")]


def walk(seed, n, start, vol):
    rnd = random.Random(seed)
    price, out = start, []
    for _ in range(n):
        o = price
        c = max(1.0, o * (1 + rnd.gauss(0.002, vol)))
        h = max(o, c) * (1 + abs(rnd.gauss(0, vol / 2)))
        lo = min(o, c) * (1 - abs(rnd.gauss(0, vol / 2)))
        out.append((o, h, lo, c, rnd.randint(30, 100)))
        price = c
    return out


BARS = walk(7, CANDLES, 120.0, 0.018)
SERIES = {name: [b[3] for b in walk(zlib.crc32(name.encode()), 30, 40 + zlib.crc32(name.encode()) % 160, 0.02)]
          for name in NAMES[1:]}


def quotes(live):
    """(name, closes, last, % change) per ticker; PIXL follows the chart, live candle included."""
    out = []
    for name in NAMES:
        closes = [b[3] for b in BARS[:-1]] + [live] if name == "PIXL" else SERIES[name]
        out.append((name, closes, closes[-1], (closes[-1] - closes[0]) / closes[0] * 100))
    return out


def draw(c, t):
    c.rect(0, 0, 320, 180, "bg")
    o, h, lo, close, vol = BARS[-1]
    live = close * (1 + 0.006 * math.sin(2 * math.pi * t * 2) + 0.003 * math.sin(2 * math.pi * t * 5))
    bars = BARS[:-1] + [(o, max(h, live), min(lo, live), live, vol)]
    watch = quotes(live)
    _, closes, _, pct = watch[0]
    change = live - closes[0]

    c.text(4, 3, "$PIXL", "white", font="large")
    c.text(36, 4, "PIXEL INDUSTRIES · NASDAQ-ISH", "dim")
    up = change >= 0
    c.text(316, 3, f"{live:.2f}", "white", font="large", align="right")
    c.text(316, 13, f"{'▲' if up else '▼'} {change:+.2f} ({pct:+.2f}%)", "green.light" if up else "red.light",
           align="right")
    c.text(4, 13, "1D · 5M CANDLES · LIVE", "lime" if t * 4 % 1 < 0.5 else "lime.dark")

    chart = c.panel(0, 22, 222, 120, "PRICE", color="white", sub="MA20 · MA50 · VOLUME")
    c.spans(chart.x2, chart.y - 8, [("MA20 ", "gold"), ("MA50", "violet.light")], align="right")
    hi_p = max(b[1] for b in bars)
    lo_p = min(b[2] for b in bars)
    top, height = chart.y + 2, 70
    axis_x = chart.x2 - 22

    def Y(p):
        return top + round((hi_p - p) / (hi_p - lo_p) * (height - 1))

    for k in range(5):
        p = lo_p + (hi_p - lo_p) * k / 4
        c.dots(chart.x, Y(p), axis_x - chart.x, "line")
        if abs(Y(p) - Y(live)) > 7:
            c.text(chart.x2, Y(p) - 2, f"{p:.0f}", "dim", align="right")
    for i, (bo, bh, bl, bc, bv) in enumerate(bars):
        x = chart.x + i * 4
        rising = bc >= bo
        col = "green" if rising else "red"
        c.vline(x + 1, Y(bh), Y(bl) - Y(bh) + 1, c.dark(col) if i < CANDLES - 1 else "white")
        y0, y1 = sorted((Y(bo), Y(bc)))
        c.rect(x, y0, 3, max(1, y1 - y0 + 1), col if i < CANDLES - 1 else c.light(col))
        vh = round(bv / 100 * 16)
        c.rect(x, chart.y2 - vh, 3, vh, c.dark(col))
    for n, colour in ((20, "gold"), (50, "violet.light")):
        pts = []
        for i in range(len(bars)):
            window = [b[3] for b in bars[max(0, i - n + 1):i + 1]]
            if len(window) >= min(n, 10):
                pts.append((chart.x + i * 4 + 1, Y(sum(window) / len(window))))
        c.polyline(pts, colour)
    c.tag(axis_x + 1, Y(live) - 4, f"{live:.1f}", "white", fill="green.dark" if up else "red.dark", border=None)

    side = c.panel(224, 22, 96, 120, "WATCHLIST", color="white")
    for i, (name, closes, _, ch) in enumerate(watch):
        y = side.y + i * 9
        colour = "green" if ch >= 0 else "red"
        c.text(side.x, y, name, "white")
        c.spark(side.x + 26, y, 28, 5, closes, c.light(colour))
        c.text(side.x2, y, f"{ch:+.2f}%", c.light(colour), align="right")
    donut_y = side.y + 6 * 9 + 6
    c.text(side.x, donut_y, "PORTFOLIO", "dim")
    c.pie(side.x + 15, donut_y + 23, 14, [(v, col) for _, v, col in HOLDINGS], hole=0.5, sep="panel")
    for i, (name, v, col) in enumerate(HOLDINGS):
        c.rect(side.x + 36, donut_y + 9 + i * 7, 3, 3, col)
        c.text(side.x + 42, donut_y + 8 + i * 7, f"{name} {v}%", "text")

    tape = []
    for name, _, price, ch in watch:
        tape += [(f"{name} {price:.2f} {'▲' if ch >= 0 else '▼'}{abs(ch):.2f}%", "green.light" if ch >= 0 else "red.light"),
                 ("  ·  ", "dim")]
    widths = [c.measure(text) + 1 for text, _ in tape]
    tape_w = sum(widths)
    sub = Canvas(320, 9, theme=c.theme, bg="shadow")
    x = 2 - round(t * tape_w)
    while x < 320:
        for (text, colour), w in zip(tape, widths):
            sub.text(x, 2, text, colour, check=False)
            x += w
    c.img.paste(sub.img, (0, 145))

    c.footer("FICTIONAL TICKERS ON A SEEDED RANDOM WALK. NOT INVESTMENT ADVICE, NOT EVEN INVESTMENT.")


animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=4, fps=10, seamless=True)
