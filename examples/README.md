# Showcase

Each script draws one piece with `pixelkit` and writes it beside itself: a PNG for a still, or a
GIF and a `-poster.png` for an animation. From the repository's root:

```bash
PYTHONPATH=skill/scripts python3 examples/bedroom.py
```

| Script | What it draws | Data |
| --- | --- | --- |
| `bedroom.py` | The sysop's bedroom, 1992: an isometric room, a BBS session on the CRT, a street fight on the TV | Made up |
| `tracker.py` | Pixeltrakker 8, a music tracker in the Amiga and M8 traditions | Made up |
| `fruitmusic.py` | Fruit Music, a Winamp-style player with an equaliser, playlist and album art | Made up |
| `daw.py` | Pixel Loops Studio, a pattern-based DAW | Made up |
| `finance.py` | A trading terminal for a fictional $PIXL | Made up |
| `hacker.py` | A film's hacking scene | Made up |
| `rpg.py` | A developer's RPG character sheet | Made up |
| `arcade.py` | An arcade's attract screen and hall of fame | Made up |
| `dungeon.py` | An isometric action RPG boss fight in the late-90s style: a necromancer, his raised skeletons and a towering fire demon in a torch-lit crypt, with loot, a tooltip, life and mana orbs and skill slots | Made up |
| `mmo.py` | An MMORPG raid: a molten fire lord in an orc canyon hold, with unit frames, a cast bar, minimap, quest tracker, chat and action bars | Made up |
| `city.py` | An isometric city builder in the mid-90s style: zones, roads with traffic, a smoking power plant, tools and RCI demand | Made up |
| `pirate.py` | A point-and-click adventure in the early-90s style: an isometric moonlit harbour, a ghostly captain, a verb grid and an inventory | Made up |
| `lounge.py` | A late-80s parser adventure, redrawn as an isometric neon lounge: a status bar, a narrator box and a typed command | Made up |
| `doom.py` | DOOM, redrawn in the kit: the title screen, the menus, the screen melt and a first-person walk into a tech-base hangar, raycast, with the status bar | Made up |
| `skyline.py` | The ten tallest buildings, to scale | CTBUH, completed buildings as of 2025 |
| `planets.py` | The planets to scale | NASA's mean diameters |
| `moon.py` | The moon's phases in October 2026 | Computed from the mean synodic month |
| `commits.py` | Redlamp's commits by day and hour | Its git log, 29 September to 7 October 2026 |

They use a few shapes the templates don't: `circle`, `sphere` and `polygon` in the kit's art, and
`pie`, `radar` and `heatmap` among its widgets. The six game screens are homages in the kit's style
with original names (only `doom.py` keeps its game's logo). They use the kit's effects (`particles`,
`darkness`, `glow`, `flicker`, `reflect`, `shimmer`, `heat`, `projectile`, `glyph`, `form`, `melt`),
its iso grid helpers (`iso_xy`, `iso_tile`, `iso_block`), the `Raycaster`, `chunky` title lettering,
sub-canvases (`sub`, `paste`) and HUD parts (`bevel`, `orb`, `cooldown`).
