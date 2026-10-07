"""Animation: call draw(c, t) on a fresh Canvas for evenly spaced t and export GIF, APNG, WebP or MP4.

Timing helpers map the global progress t (0 -> 1) onto per-element progress p (0 -> 1).
"""

from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from .canvas import Canvas


def clamp01(v: float) -> float:
    return 0.0 if v < 0 else 1.0 if v > 1 else v


def lerp(a: float, b: float, p: float) -> float:
    return a + (b - a) * p


def phase(t: float, start: float, end: float) -> float:
    """Progress through the window [start, end] of the timeline, clamped to 0..1."""
    if end <= start:
        return float(t >= start)
    return clamp01((t - start) / (end - start))


def stagger(t: float, i: int, n: int, *, start: float = 0.0, end: float = 1.0, overlap: float = 0.5) -> float:
    """Progress of item i of n when their windows are spread over [start, end].
    overlap 0 plays them one after another, 1 plays them all together."""
    if n <= 1:
        return phase(t, start, end)
    span = (end - start) / (n - (n - 1) * overlap)
    begin = start + i * span * (1 - overlap)
    return phase(t, begin, begin + span)


def ease_out(p: float) -> float:
    """Fast start, gentle landing (cubic)."""
    return 1 - (1 - p) ** 3


def ease_in_out(p: float) -> float:
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


def ease_back(p: float, overshoot: float = 1.70158) -> float:
    """Overshoots the target slightly, then settles: good for things popping in."""
    return 1 + (overshoot + 1) * (p - 1) ** 3 + overshoot * (p - 1) ** 2


def steps(p: float, n: int) -> float:
    """Quantise progress into n jumps, for a mechanical, frame-by-frame feel."""
    return min(1.0, math.floor(p * n) / n)


def wave(t: float, cycles: float = 1, offset: float = 0.0) -> float:
    """0..1 oscillation; loops seamlessly when cycles is a whole number."""
    return 0.5 - 0.5 * math.cos(2 * math.pi * (cycles * t + offset))


def blink(t: float, cycles: float = 1, duty: float = 0.5, offset: float = 0.0) -> bool:
    """On for the first `duty` share of each of `cycles` periods."""
    return (cycles * t + offset) % 1 < duty


def reveal(text: str, p: float) -> str:
    """The first share p of a string, for typewriter text."""
    return text[: round(len(text) * clamp01(p))]


def _palette(images: list[Image.Image]) -> Image.Image | None:
    seen: dict = {}
    for im in images:
        for _, rgb in im.getcolors(im.width * im.height):
            seen.setdefault(rgb, None)
    if len(seen) > 256:
        return None
    flat = [v for rgb in seen for v in rgb]
    pal = Image.new("P", (1, 1))
    pal.putpalette(flat + flat[:3] * (256 - len(seen)))
    return pal


def _sheet(frames: list[Canvas], ts: list[float], path: Path, cells: int = 9) -> Path:
    picks = sorted({round(k * (len(frames) - 1) / (cells - 1)) for k in range(cells)})
    first = frames[0]
    tiles = []
    for i in picks:
        tile = Canvas(first.w, first.h + 9, theme=first.theme, bg="shadow")
        tile.img.paste(frames[i].img, (0, 9))
        tile.text(2, 2, f"#{i}  T={ts[i]:.2f}", "white", check=False)
        tiles.append(tile.img.resize((tile.w * 2, tile.h * 2), Image.NEAREST))
    cols = 3
    tw, th = tiles[0].size
    sheet = Image.new("RGB", (cols * tw + (cols - 1) * 8, -(-len(tiles) // cols) * (th + 8) - 8), (255, 255, 255))
    for k, tile in enumerate(tiles):
        sheet.paste(tile, ((k % cols) * (tw + 8), (k // cols) * (th + 8)))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    return path


def animate(draw, path, *, seconds: float = 2.0, fps: float = 20, hold: float = 0.0, seamless: bool = False,
            poster: float | None = None, scale: int | None = None, quiet: bool = False, **canvas) -> Path:
    """Render draw(c, t) on a fresh Canvas(**canvas) for each frame and save by extension:
    .gif, .webp (lossless), .png (APNG) or .mp4 (needs ffmpeg).

    t runs from 0 to 1 over `seconds`; with seamless=True the final t=1 frame is dropped so periodic
    motion loops without a repeated frame. `hold` keeps the last frame up for extra seconds before
    the loop restarts. Also writes NAME-poster.png beside the animation (the frame at t=poster,
    default the last) and a contact sheet of sampled frames in the temp folder for review."""
    path = Path(path).expanduser()
    n = max(2, round(seconds * fps))
    ts = [i / n if seamless else i / (n - 1) for i in range(n)]
    frames: list[Canvas] = []
    notes: dict[str, int] = {}
    for i, t in enumerate(ts):
        c = Canvas(**canvas)
        draw(c, t)
        for note in c.check():
            notes.setdefault(note, i)
        frames.append(c)
    s = scale or frames[0].scale
    big = [c.img.resize((c.w * s, c.h * s), Image.NEAREST) for c in frames]
    step = 1000 / fps
    durations = [round(step * (i + 1)) - round(step * i) for i in range(n)]
    durations[-1] += round(hold * 1000)
    path.parent.mkdir(parents=True, exist_ok=True)
    ext = path.suffix.lower()
    if ext in (".gif", ".png"):
        pal = _palette([c.img for c in frames])
        if pal is None:
            notes.setdefault("more than 256 colours across frames; the GIF palette was approximated", 0)
            paletted = [im.quantize(256, dither=Image.Dither.NONE) for im in big]
        else:
            paletted = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in big]
        paletted[0].save(path, save_all=True, append_images=paletted[1:], duration=durations, loop=0)
    elif ext == ".webp":
        big[0].save(path, save_all=True, append_images=big[1:], duration=durations, loop=0, lossless=True,
                    method=4)
    elif ext == ".mp4":
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError("MP4 export needs ffmpeg on PATH; save as .gif or .webp instead")
        with tempfile.TemporaryDirectory() as tmp:
            for i, im in enumerate(big):
                im.save(Path(tmp) / f"{i:05d}.png")
            filters = "pad=ceil(iw/2)*2:ceil(ih/2)*2" + (f",tpad=stop_mode=clone:stop_duration={hold}" if hold else "")
            subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-framerate", str(fps),
                            "-i", str(Path(tmp) / "%05d.png"), "-vf", filters, "-c:v", "libx264",
                            "-pix_fmt", "yuv420p", "-crf", "16", "-tune", "animation",
                            "-movflags", "+faststart", str(path)], check=True)
    else:
        raise ValueError(f"unsupported animation format {ext!r}; use .gif, .webp, .png or .mp4")
    k = n - 1 if poster is None else round(clamp01(poster) * (n - 1))
    still = path.with_name(f"{path.stem}-poster.png")
    frames[k].save(still, s, quiet=True)
    sheet = _sheet(frames, ts, Path(tempfile.gettempdir()) / "pixelkit" / f"{path.stem}.frames.png")
    if not quiet:
        for note, i in notes.items():
            print(f"warning (frame {i}): {note}")
        total = sum(durations) / 1000
        w, h = big[0].size
        if ext == ".mp4":
            w, h = w + w % 2, h + h % 2
        print(f"wrote {path} ({w}x{h}, {n} frames, {total:.1f} s, {max(1, path.stat().st_size // 1024)} KB)")
        print(f"poster {still}")
        print(f"frames {sheet}")
    return path
