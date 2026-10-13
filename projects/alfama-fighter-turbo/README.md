# Making Alfama Fighter Turbo, in pictures

The diagrams for [Making Alfama Fighter Turbo](https://badcoffee.dev/devlog), a ten-part devlog on
badcoffee.dev about an arcade fighting game set in Lisbon, made in nine days (4 to 12 October 2026)
by one person and a studio of AI agents in Cursor. Every fact comes from the game's repository at
commit `74e2f64` (12 October 2026, 16:00), and each image names its source in the footer.

## How the series is drawn

- `series.py` holds what every image shares: the header with the badcoffee gremlin as its mark,
  the footer citing the source with BADCOFFEE.DEV at the right, one colour per role in the studio
  (gold for the director, cyan for the producer, red for art, violet for audio, green for the
  engine, blue for QA, sky for the network, lime for tools), and `along()` and `packet()` for a
  message moving along a path.
- `PP-N_name.py` is image N of part PP. Each draws `draw(c, t)` and calls `export()`, which writes
  `PP-N_name.gif` and a still `PP-N_name-poster.png` beside it.
- Nothing is built up and torn down: every label stays on screen while something moves through
  the picture, so a reader can stop and read it. One idea per image.
- Labels are written for someone who has never seen the project: no milestone numbers or internal
  names unless the post explains them.

```bash
cd projects/alfama-fighter-turbo
export PYTHONPATH=../../skill/scripts
for f in [0-9][0-9]-*.py; do python3 "$f"; done
```

badcoffee.dev copies the renders into `public/media/devlog/<post>/` with
`tools/media/import.py --only devlog`, which records each file's source and hash.

## The images

Each script's docstring lists the sources behind every number it draws.

### Part 1: How I built an arcade fighting game in nine days with AI agents

In [the post](https://badcoffee.dev/devlog/nine-days-of-alfama-fighter-turbo).

- `01-1_nine-days.gif`: Nine days, row by row: what each part of Alfama Fighter Turbo had by the end of each day, 4 to 12 October 2026, with the commits made each day underneath.
- `01-2_numbers.gif`: What nine days added up to: the counts from Alfama Fighter Turbo's repository at its last commit of 12 October, and the art kept in the repository against what the game ships.

### Part 2: A game studio made of agents

In [the post](https://badcoffee.dev/devlog/a-game-studio-made-of-agents).

- `02-1_cast.gif`: The cast: Pedro, the director, at the top; the producer below him as the one line between him and the studio; and the ten roles the producer briefs, in five columns, each with who reviews its work. Animated, a seamless loop: a request goes from Pedro to the producer, a brief goes down to the animators, their work goes up to the art director's check against the art bible, and the report comes back up through the producer to Pedro, each node lighting as it passes; the six steps beside the top light in turn. The reviewers are the studio plan's; in practice the leads' reviews were checks against the bibles and the producer looked at every lane's previews itself (studio-model.md, The cast and Quality).
- `02-2_memory.gif`: The studio's memory: the documents every brief points at (the design document, the studio plan, the six bibles, the decisions log, the feature designs and the prompts kept beside the pictures), a lane that reads them and writes back, and what happens when a bible and the decisions log disagree. Animated, a seamless loop: a lane reads the bibles, then the decisions log; the example below shows the log winning over the art bible; the lane works, then writes its as-built note back into a bible.
- `02-3_plan.gif`: How the plan grew: the fifteen milestones of the studio's plan in their five phases, by their plain names, and the day each was added. Six came in the first plan, written on the morning of 5 October from Pedro's ask; the other nine were his ideas, added on 6, 7, 9 and 10 October. Animated, an intro that holds: a playhead sweeps the days from 5 to 10 October, and each milestone lights in its phase as the playhead passes the time it was added, with the count climbing to 15.

### Part 3: Street Fighter II, set in Lisbon

In [the post](https://badcoffee.dev/devlog/street-fighter-ii-set-in-lisbon).

- `03-1_route.gif`: The arcade's route across Lisbon: the ten stages pinned on a map of the city, each numbered in the order the single-player arcade visits them, with the list of stops and who waits at each beside it. Animated: a tram travels the dashed route stop to stop in the arcade's order, each stop's tile filling and its row in the list lighting as it arrives, from the Bairro Alto to the bridge and then Santa Catarina for the boss; the whole route stays drawn throughout, then the last frame holds.
- `03-2_drawings.gif`: Drawings per character: how many separate drawings one fighter takes at the density of Street Fighter II Turbo, of our plan, of Street Fighter Alpha, of Street Fighter III, and what Street Fighter III really had. Five extruded bars on one scale up to 1,200, so the plan's 155 sits beside SF3's 700 to 1,200. Animated: the bars rise in turn and their values count up, then the chart holds.
- `03-3_heights.gif`: The roster by height: the eight fighters, tallest first, each with his fighting-game archetype, his standing height drawn at the game's own scale (one pixel here is one pixel in the game) and his jump, against the 112 px ceiling for anyone with the standard jump; Adamastor, the boss, at 130 px below them, the one who never jumps. A prop that stands higher than the head (A Padeira's bread shovel, A Varina's basket, Zé Povinho's hat) is a darker extension of the bar. Animated: the ceiling and the labels are there from the start, the bars grow in turn and their heights count up, then it holds.

### Part 4: Lanes, night shifts and a board I can read

In [the post](https://badcoffee.dev/devlog/lanes-night-shifts-and-a-board).

- `04-1_lane.gif`: A lane's life: the ten steps one piece of work went through, from the producer picking it to the producer answering its questions, and below them the same lane in git: the bridge stage's lane on the night of 7 to 8 October, cut from main, merging main into itself twice while other lanes landed, then merged clean.
- `04-2_night.gif`: The night of six lanes, 7 to 8 October: each lane a row on a time axis from 23:40 to 06:15, its bar from the moment the producer launched it to the moment it was merged into main, with the times it merged main into itself marked on it, and its merge dropping into main. Pedro's two messages bracket the night.
- `04-3_commits.gif`: When the game was made: all 1,548 commits of the nine days as a day-by-hour heatmap, with each hour's total above it and each day's total beside it. The busiest hour of the day was the one after midnight.

### Part 5: Drawing fighters with an image generator

In [the post](https://badcoffee.dev/devlog/drawing-fighters-with-an-image-generator).

- `05-1_pipeline.gif`: From a generated sheet to a sprite in the game: the stations a fighter's drawing passes through, and what each one checks or does. The model sheet, picked by the director from three designs, sits above them: it's the reference every sheet is drawn from, the stance the drift check compares with, and the picture the palette is fitted from.
- `05-2_memory.gif`: Where the memory went: the nine fighters' drawings on disk, as the game first held them once loaded, and as SF2 held its own, at their sizes on one scale. Beside them, what each pixel cost in memory, and the fighters' pictures the game measured itself holding at the arcade's last fight, before and after.
- `05-3_boiling.gif`: More drawings, more boiling: O Fadista's stance and heavy punch at three densities (A, the game's drawings; B, about twice as many; C, Metal Slug's density), and how much of each change between drawings is redrawn rather than moved. In the stance every change redraws about the same 680 pixels, so twice the drawings is twice the boiling a second. In the heavy punch, where the poses are far apart, each change boils less as drawings are added, but a second it still rises.

### Part 6: Fado played by an arcade band

In [the post](https://badcoffee.dev/devlog/fado-played-by-an-arcade-band).

- `06-1_conductor.gif`: The match conducts the band: one stage theme's four layers as tracker rows, bar by bar, through an example first round and an example final round on Alfama's theme.
- `06-2_compressors.gif`: The band's compressors, before and after the mix polish of 12 October: how far they held the music down and how much that hold moved, as two gain-reduction meters with their traces.

### Part 7: One player: the arcade, training and the credits

In [the post](https://badcoffee.dev/devlog/the-arcade-training-and-the-credits).

- `07-1_arcade.gif`: The screens and an arcade run: from the boot card through the attract demo, the title and the menu into the arcade, whose loop is the map of Lisbon, the VS screen, the fight and the winner's quote, then the next fight; a second player's start cuts in with HERE COMES A NEW CHALLENGER!, and the winner of that best of three carries on the run.
- `07-2_combo.gif`: What a combo is worth: the attract demo's combo, O Fadista's jump-in heavy kick, crouching medium kick and Capa Negra (three turns of his cape, one hit a turn), scored hit by hit. Each hit is worth its damage x 100 x the combo's multiplier, and the multiplier counts the moves linked so far, not the hits, so the cape's three turns are one move: 1,300 + 1,600 + 3 x 1,500 = 7,400, where the same five hits at x1 would be 3,600.
- `07-3_credits.gif`: The credits on the medley's bars: the scene at the Pastelaria Paraíso is timed to its music, a long medley of 74 bars at 100 BPM (a bar 2.4 s, 2 min 58 s in all). Each fighter walks in on his own bar, the band opening out of the pastelaria's radio into the room for his turn; between the visits the radio plays while the friends talk. Twice the tram 28 crosses the window, and while it covers the glass the light outside jumps on (gold to sunset, sunset to dusk), so the time cut is never seen. On bar 73 the shutter starts down, and on bar 74 it's closed with THE END on it.

### Part 8: Playing together: online matches, ranked runs and tournaments

In [the post](https://badcoffee.dev/devlog/playing-together).

- `08-1_rollback.gif`: Rollback, step by step: two games of one network match, each playing its own player's presses at once and guessing the other's by repeating the last one it has. The friend's inputs reach your game three steps late; while he walks, the guesses are right and nothing happens. When he punches at step 5 the news reaches your game at step 8: the three steps it guessed wrong (5, 6 and 7) are struck through, the game goes back to step 5 and plays 5 to 8 again before it draws the next frame, and carries on guessing his new input. His game's guesses of you were right all along, so it plays nothing again.
- `08-2_talks.gif`: Who talks to whom: the two players' browsers, the Vercel functions (the matchmaker, the ICE servers' function, the ranked services) with the key-value store they keep their state in, and on Cloudflare the TURN relay and the tournament room. The matchmaker hears one offer and one answer; after that the two browsers send each other their inputs directly, or through the relay when their networks can't connect. Ranked runs and matches go to Vercel; a tournament night is one socket a game to the room. The only line between the two clouds is the ICE function asking Cloudflare for the relay's short-lived credentials; the room calls no other service.
- `08-3_playback.gif`: A score the server plays back: a ranked run from its token to the boards. The server issues a token (the seed the CPU plays with, the fights in order, the build, the time); the run is played on the device with the CPU seeded from it; only player 1's inputs go back, with the score the game reached; the server's cheap checks come first, then it plays the inputs through the game's own simulation, fight by fight, its own CPU answering from the seed; its score is the score, and a score or a fight's fingerprint that differs is refused and flagged. The run goes on this week's boards, and each closed week's champions go into the hall of fame.

### Part 9: Tools as reviewers

In [the post](https://badcoffee.dev/devlog/tools-as-reviewers).

- `09-1_proofs.gif`: Four proofs before a merge: a change that says it changes nothing else proves it on the pictures, the sound, the simulation and the budgets, and only then goes into the game. The examples come from different changes, and the budgets' from the check's full run on the finished game.
- `09-2_matrix.gif`: The balance lab's matchup matrix: the hard CPU playing itself with every pair of the eight fighters you can pick, as a heatmap of the row fighter's share of wins, with each fighter's overall share beside his row.
- `09-3_filming.gif`: Filming the game a frame at a time: the trailer tool steps the game's own loop exactly 1/60 s per frame and grabs each picture, the music is rendered offline, and the montage cuts land on the music's bar lines.

### Part 10: Polishing, and what's next

In [the post](https://badcoffee.dev/devlog/polishing-and-whats-next).

- `10-1_punch-list.gif`: The punch list filling in: the 24 items a fresh-eyes review found, the night they were fixed.
- `10-2_road-to-launch.gif`: The road to launch: every item left, and its state, at the game's commit 74e2f64 (16:00, 12 October).
