"""9.1 Four proofs before a merge: a change that says it changes nothing else proves it on the pictures,
the sound, the simulation and the budgets, and only then goes into the game. The examples come
from different changes, and the budgets' from the check's full run on the finished game.

Moves: a packet (the change) leaves A CHANGE, runs down past the four proofs in turn, then across and
up into MERGED. Each proof's gate, border and example light as the packet passes it; MERGED lights
last, and the picture holds with everything lit.

Numbers, all from alfamafighterturbo at 74e2f64:
- The pictures: tools/frames.py hashes every frame of seeded fights and screens (its docstring).
  126,622 frames, every one identical, when the credits' Easter egg merged on 11 October
  (docs/plans/2026-10-11-credits-easter-egg-design.md, "The rest of the game unchanged"; decisions.md,
  11 October, the producer).
- The sound: tools/render_audio.py --compare renders both builds offline with the same seed and
  exits 1 if their difference peaks over -90 dBFS (its docstring). The combo callouts' four new
  sounds (FIRST ATTACK, REVERSAL...), 9 to 10 October: of the 256 other effects, 119 identical and the rest at most -136.5 dBFS apart
  (docs/studio/audio-bible.md 8.9; commit fc5a30b).
- The simulation: tools/fingerprints.ts folds every step's fingerprint of saved replays into one
  number a replay (its header). All 35 saved replays the same, step for step, for the Easter egg
  (the same design document).
- The budgets: tools/perf_check.py's pass-or-fail checks: download to the title at most 1.3 MB,
  pictures and data held at most 32 MB, JavaScript heap at most 20 MB, frame time under 8 ms at the
  95th percentile on a CPU four times slower (its docstring;
  docs/plans/2026-10-09-performance-and-resources.md). On 12 October the download had grown to
  1.390 MB and failed (perf_check 32 of 35, decisions.md, 12 October, the engine programmer), and was
  cut to 1.097 MB (the same document, "The download is back under its budget").
"""

from pixelkit import ease_in_out, phase
from series import ART, AUDIO, ENGINE, PRODUCER, QA, along, export, frame, packet

PROOFS = [
    # title, what it's called, accent, the pass line, how it's checked, an example
    ("THE PICTURES", "FRAME HASHES", ART, "PASS: EVERY FRAME THE SAME",
     "EVERY FRAME OF REPEATABLE FIGHTS AND SCREENS, HASHED BEFORE AND AFTER",
     "THE HIDDEN CREDITS, 11 OCT: 126,622 FRAMES, EVERY ONE IDENTICAL"),
    ("THE SOUND", "NULL TEST", AUDIO, "FAILS OVER −90 DBFS",
     "BOTH VERSIONS RENDER EACH SOUND; ONE, INVERTED, CANCELS THE OTHER",
     "4 NEW SOUNDS ADDED: IN THE 256 OTHERS, NOTHING OVER −136.5 DBFS"),
    ("THE SIMULATION", "FINGERPRINTS", ENGINE, "PASS: EVERY STEP THE SAME",
     "SAVED REPLAYS PLAYED ON BOTH; THE WHOLE STATE FINGERPRINTED EACH STEP",
     "THE HIDDEN CREDITS, 11 OCT: ALL 35 SAVED REPLAYS, STEP FOR STEP"),
    ("THE BUDGETS", "PERFORMANCE", QA, "PASS OR FAIL, EACH",
     "DOWNLOAD 1.3 MB · PICTURES 32 MB · SCRIPT MEMORY 20 MB · FRAME 8 MS",
     "12 OCT, FULL RUN ON THE GAME: DOWNLOAD 1.39 MB FAILED; CUT TO 1.10 MB"),
]

LANE_L, LANE_R = 12, 308
ROW_H, ROW_GAP = 26, 2
# The packet's timeline: it stops at each proof's gate in turn, then runs across and up to MERGED.
LEGS = [(0.03, 0.11), (0.17, 0.25), (0.31, 0.39), (0.45, 0.53), (0.59, 0.80)]


def travelled(t, stops):
    """How far along the route the packet is at t: eased between stops, still at each one."""
    d = 0
    for (a, b), (d0, d1) in zip(LEGS, zip([0] + stops, stops)):
        if t >= b:
            d = d1
        elif t > a:
            return d0 + (d1 - d0) * ease_in_out(phase(t, a, b))
    return d


def draw(c, t):
    top, bottom = frame(c, 9, 1, "FOUR PROOFS BEFORE A MERGE", "FRAME: 95 FRAMES IN 100 UNDER 8 MS, ON A CPU 4× SLOWER.")
    row_y = top + 25
    lane_y = row_y + 4 * (ROW_H + ROW_GAP) - ROW_GAP + 2
    start = top + 22
    route = [(LANE_L, start), (LANE_L, lane_y), (LANE_R, lane_y), (LANE_R, start)]
    total = sum(abs(x1 - x0) + abs(y1 - y0) for (x0, y0), (x1, y1) in zip(route, route[1:]))
    gates = [row_y + i * (ROW_H + ROW_GAP) + ROW_H // 2 for i in range(4)]
    gone = travelled(t, [g - start for g in gates] + [total])
    here = along(route, gone / total)

    merged = t >= LEGS[-1][1]
    change = c.node(4, top + 3, 104, 19, "A CHANGE", color="white", sub="SAYS NOTHING ELSE MOVES")
    done = c.node(212, top + 3, 104, 19, "MERGED", color="white" if merged else PRODUCER,
                  sub="INTO THE GAME", border="white" if merged else "line")
    c.text(160, top + 10, "EACH WITH A REAL EXAMPLE", "dim", align="center")

    c.vline(LANE_L, change.y2, lane_y - change.y2 + 1, "line")
    c.hline(LANE_L, lane_y, LANE_R - LANE_L + 1, "line")
    c.vline(LANE_R, done.y2, lane_y - done.y2 + 1, "line")
    c.arrow(LANE_R, lane_y, LANE_R, done.y2 + 1, "white" if merged else "line")

    for i, (title, kind, accent, rule, how, example) in enumerate(PROOFS):
        y = row_y + i * (ROW_H + ROW_GAP)
        gate_y = gates[i]
        lit = gone >= gate_y - start
        panel = c.panel(24, y, 278, ROW_H, title, color=c.light(accent), sub=kind,
                        right=rule, right_color="white" if lit else "dim", border=c.light(accent) if lit else "line")
        c.text(panel.x, panel.y, how, "text")
        c.text(panel.x, panel.y + 7, example, "white" if lit else "dim")
        c.rect(LANE_L - 4, gate_y - 4, 9, 9, accent if lit else "raised")
        c.box(LANE_L - 4, gate_y - 4, 9, 9, c.light(accent) if lit else "line")
        if lit:
            c.icon(LANE_L - 3, gate_y - 3, "check", "white")
        c.hline(LANE_L + 5, gate_y, panel.x - 4 - LANE_L - 5, c.light(accent) if lit else "line")

    if 0 < gone < total and t > LEGS[0][0]:
        packet(c, *here, "white")


export(draw, __file__, preset="wide", seconds=6, fps=20, hold=3, poster=1.0)
