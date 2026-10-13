"""10.2 The road to launch: every item left, and its state, at the game's commit 74e2f64 (16:00, 12 October).

A status board in five panels: what's done (with the time it merged on 12 October), what the
studio is running, what waits on Pedro's call, what only people can prove (Pedro, his friends and
his own ranked runs), and what hasn't started. The four counts sit at the bottom right. A seamless
loop: the running items' activity dots march, and the gold lights of what waits on Pedro blink.
Nothing else moves; every label is on screen throughout.

Numbers and states, and where they come from (alfamafighterturbo at 74e2f64 unless said):
- Done, by merge time on 12 October (`git log`): the mix polish 09:47 (43f475d), the logo Tejo with
  two entrances 11:18 (66ec920), a first visit under its 1.3 MB budget 07:24 (7a4b05b), the punch
  list's first fixes 01:37 and 01:51 (0fc7c62, e76d965; 01:51 shown, the later), the desktop builds
  for all three systems 16:00 (74e2f64, "Its first run, all three green").
- Running at 16:00: the desktop app's game changes (decisions.md, the producer's row of 12 October
  for M8's first two lanes; its branch's commits from 15:11, merged at 17:18, after 74e2f64), and
  the three trailers' storyboards (decisions.md, the producer's row of 12 October; the lane's brief
  at 15:25 in the trailer chat).
- Pedro's calls: player 2's keys on a laptop, the shoulds and coulds, the repository's size (the
  packed git history, 968 MB and mostly art, against GitHub's recommended 1 GB; polishing-phase.md,
  "The repository's size") and the
  balance for 19 October (docs/plans/2026-10-12-polishing-phase.md, "Your decisions this morning"
  3 to 5; the balance calls wanted by the Friday before, 16 October); network play on Linux, where
  the AppImage's WebKitGTK has no WebRTC (docs/plans/2026-10-08-steam-packaging.md, "The Linux
  build, and WebRTC": "the director's call"); the accounts for signing and Steam ("Signing and
  Steam: wired, and off until the director's accounts exist").
- To prove, with people: his full pass, about 3 hours (docs/plans/2026-10-11-first-full-pass.md,
  "Time"); a network test between two homes (polishing-phase.md, "Done when"); a real tournament
  night (first-full-pass.md: "Your first night with friends is their first real one"); ranked runs
  by a person (first-full-pass.md: "Your ranked runs are the leaderboards' first real check"; the
  first weekly close found no runs, polishing-phase.md).
- Not started: cutting the three trailers (decisions.md, the user's row of 12 October: storyboards
  first, "then the cuts"); Steam's store page and first upload (steam-packaging.md, "Left", and
  "Steps to ship" 4 and 9); the achievements' list (steam-packaging.md, "Still open"); the Mac App
  Store, "right after" Steam, and iOS and Google Play "later" (decisions.md, the user's M8 row of
  12 October).
- 5 done, 2 running, 10 waiting on Pedro, 5 not started: counted from the above.
"""

from pixelkit import Rect, blink
from series import DIRECTOR, PRODUCER, export, frame

DONE = [("THE PUNCH LIST'S FIRST FIXES", "01:51"), ("FIRST VISIT UNDER 1.3 MB", "07:24"),
        ("THE MUSIC'S MIX, POLISHED", "09:47"), ("THE LOGO: TEJO, TWO ENTRANCES", "11:18"),
        ("DESKTOP BUILDS, ALL THREE", "16:00")]
RUNNING = [("THE DESKTOP APP'S GAME CHANGES", ""), ("STORYBOARDS FOR 3 TRAILERS", "")]
CALLS = [("PLAYER 2'S KEYS ON A LAPTOP", ""), ("WHICH SHOULDS AND COULDS", ""),
         ("BALANCE CALLS FOR 19 OCT", "BY 16 OCT"), ("REPOSITORY SIZE", "968 MB"),
         ("NETWORK PLAY ON LINUX", "NO WEBRTC"), ("ACCOUNTS FOR SIGNING, STEAM", "")]
PROVE = [("PEDRO'S FULL PASS", "ABOUT 3 H"), ("A MATCH BETWEEN TWO HOMES", ""),
         ("A REAL TOURNAMENT NIGHT", ""), ("RANKED RUNS BY A PERSON", "")]
LATER = [("CUTTING THE THREE TRAILERS", ""), ("STEAM: STORE PAGE, UPLOAD", ""),
         ("THE ACHIEVEMENTS' LIST", ""), ("THE MAC APP STORE", "AFTER STEAM"), ("IOS AND GOOGLE PLAY", "LATER")]
STEP = 8
SECONDS = 4


def rows(c, r, items, t, kind):
    y = r.y + 1
    for i, (label, note) in enumerate(items):
        if kind == "done":
            c.tile(r.x, y, 5, "white")
            c.text(r.x + 8, y, label, "text")
            c.text(r.x2, y, note, "dim", align="right")
        elif kind == "running":
            c.tile(r.x, y, 5, PRODUCER)
            w = c.text(r.x + 8, y, label, "white")
            # Three dots marching after the label: one step each second.
            lit = int(t * SECONDS * 2 + i) % 3
            for k in range(3):
                c.rect(r.x + 8 + w + 3 + k * 3, y + 3, 2, 2, PRODUCER if k == lit else "raised")
        elif kind == "waiting":
            on = blink(t, cycles=SECONDS, duty=0.7, offset=i * 0.13)
            c.tile(r.x, y, 5, DIRECTOR if on else c.dark(DIRECTOR))
            c.text(r.x + 8, y, label, "text")
            if note:
                c.text(r.x2, y, note, "dim", align="right")
        else:
            c.tile(r.x, y, 5, "raised")
            c.text(r.x + 8, y, label, "dim")
            if note:
                c.text(r.x2, y, note, "muted", align="right")
        y += STEP


def tall(n):
    return 12 + n * STEP + 3


def draw(c, t):
    top, bottom = frame(c, 10, 2, "THE ROAD TO LAUNCH, 12 OCT 16:00",
                        "TIMES ARE WHEN EACH MERGED, 12 OCTOBER.")
    area = Rect(0, top + 1, c.w, bottom - top - 3)
    left, right = area.cols(2, gap=2)

    a, rest = left.cut_top(tall(len(DONE)), gap=2)
    b, d = rest.cut_top(tall(len(RUNNING)), gap=2)
    rows(c, c.panel(*a, "DONE", color="white", sub="MERGED, 12 OCT"), DONE, t, "done")
    rows(c, c.panel(*b, "RUNNING", color=PRODUCER, sub="THE STUDIO AT WORK"), RUNNING, t, "running")
    rows(c, c.panel(*d, "NOT STARTED", color="dim"), LATER, t, "later")

    e, rest = right.cut_top(tall(len(CALLS)), gap=2)
    f, g = rest.cut_top(tall(len(PROVE)), gap=2)
    rows(c, c.panel(*e, "WAITING ON PEDRO", color=DIRECTOR, sub="HIS CALLS"), CALLS, t, "waiting")
    rows(c, c.panel(*f, "TO PROVE, WITH PEOPLE", color=DIRECTOR, sub="PEDRO, FRIENDS"), PROVE, t, "waiting")

    s = c.panel(*g)
    counts = [(len(DONE), "DONE", "white"), (len(RUNNING), "RUNNING", PRODUCER),
              (len(CALLS) + len(PROVE), "ON PEDRO", DIRECTOR), (len(LATER), "NOT YET", "dim")]
    cells = s.cols(4, gap=2)
    for cell, (n, label, col) in zip(cells, counts):
        c.text(cell.cx, cell.y, f"{n}", col, font="large", align="center")
        c.text(cell.cx, cell.y + 10, label, "dim", align="center")


export(draw, __file__, preset="wide", seconds=SECONDS, fps=20, seamless=True, poster=0.0)
