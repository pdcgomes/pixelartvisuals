"""Turn any image into a theme-locked pixel sprite for use with Canvas.image(..., colors="keep").

usage: pixelate.py IN OUT (--width W | --height H) [--colors a,b,c] [--dither 0..1] [--key] [--tol N]
                   [--preview N]
  --width/--height  target size in logical pixels (aspect ratio kept)
  --colors          restrict to these theme colour names (default: the whole theme)
  --dither          ordered-dither strength, 0 (flat) to 1 (strong)
  --key             make the flat background (sampled from the corners) transparent and trim to content;
                    generate art on a plain #FF00FF or white background for clean cut-outs
  --preview         also write OUT with @Nx before the extension, scaled up for viewing
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixelkit import load_theme, lock  # noqa: E402


def key_out(img: Image.Image, tol: int) -> Image.Image:
    a = np.asarray(img.convert("RGBA")).copy()
    corners = np.array([a[0, 0, :3], a[0, -1, :3], a[-1, 0, :3], a[-1, -1, :3]], dtype=int)
    bg = np.median(corners, axis=0)
    dist = np.abs(a[..., :3].astype(int) - bg).sum(axis=2)
    a[..., 3] = np.where(dist <= tol, 0, a[..., 3])
    out = Image.fromarray(a, "RGBA")
    box = out.getchannel("A").getbbox()
    return out.crop(box) if box else out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("dst")
    size = ap.add_mutually_exclusive_group(required=True)
    size.add_argument("--width", type=int)
    size.add_argument("--height", type=int)
    ap.add_argument("--colors", help="comma-separated theme colour names")
    ap.add_argument("--dither", type=float, default=0.0)
    ap.add_argument("--key", action="store_true")
    ap.add_argument("--tol", type=int, default=60)
    ap.add_argument("--preview", type=int, default=0)
    args = ap.parse_args()

    img = Image.open(args.src).convert("RGBA")
    if args.key:
        img = key_out(img, args.tol)
    w = args.width or round(img.width * args.height / img.height)
    h = args.height or round(img.height * args.width / img.width)
    img = img.resize((w, h), Image.BOX if w < img.width else Image.NEAREST)
    theme = load_theme()
    names = args.colors.split(",") if args.colors else None
    out = lock(img, theme.palette(names), dither=args.dither)
    dst = Path(args.dst)
    out.save(dst)
    print(f"wrote {dst} ({w}x{h})")
    if args.preview:
        big = dst.with_name(f"{dst.stem}@{args.preview}x{dst.suffix}")
        out.resize((w * args.preview, h * args.preview), Image.NEAREST).save(big)
        print(f"wrote {big}")


if __name__ == "__main__":
    main()
