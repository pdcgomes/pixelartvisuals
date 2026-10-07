"""Stack the series into one tall poster, every image on the same pixel grid."""

from pathlib import Path

from PIL import Image

from pixelkit import load_theme

HERE = Path(__file__).resolve().parent
FILES = ["01_overview.png", "02_modules.png", "03_pipeline.png", "04_frame-poster.png", "05_edits.png",
         "06_models.png"]
EXPORT_SCALE, WIDTH, GAP, SCALE = 4, 480, 8, 3

tiles = []
for name in FILES:
    im = Image.open(HERE / name).convert("RGB")
    tiles.append(im.resize((im.width // EXPORT_SCALE, im.height // EXPORT_SCALE), Image.NEAREST))

bg = load_theme().rgb("shadow")
sheet = Image.new("RGB", (WIDTH + 2 * GAP, sum(t.height for t in tiles) + GAP * (len(tiles) + 1)), bg)
y = GAP
for tile in tiles:
    sheet.paste(tile, (GAP + (WIDTH - tile.width) // 2, y))
    y += tile.height + GAP

colors = sheet.getcolors(256)
big = sheet.resize((sheet.width * SCALE, sheet.height * SCALE), Image.NEAREST)
if colors:
    flat = [v for _, rgb in colors for v in rgb]
    pal = Image.new("P", (1, 1))
    pal.putpalette(flat + flat[:3] * (256 - len(colors)))
    big = big.quantize(palette=pal, dither=Image.Dither.NONE)
out = HERE / "poster.png"
big.save(out, optimize=True)
print(f"wrote {out} ({big.width}x{big.height}, {out.stat().st_size // 1024} KB)")
