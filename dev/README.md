# area_map dev tools

Offline testing for `area_map.xml`: runs the plugin's Lua outside MUSHclient
(via lupa) against game transcripts, with stand-ins for the MUSHclient API.

Setup once: `./get_lupa.sh`

- `python3 luacheck.py ../area_map.xml` -- syntax check
- `python3 harness.py ../area_map.xml tx/<file>.txt [--log] [--realdb] [--debug] [--trace] [--render] [--ids]`
  - plain transcripts: a lowercase line right after a `nnn/nnn:nnn>` prompt is a command
  - a line starting with `amap` runs that plugin command (e.g. `amap irregular`); `<enter>` sends an empty line
  - `--log`: MUSHclient log format (prompt ends with the `X:[x]Y:[y]` line)
  - `--realdb`: real SQLite (`dev/area_map.db`, delete it first for a fresh map)
  - `--debug` / `--trace`: print `amap debug` / trace lines per move
  - `--render`: writes `draw.mvg`; turn it into a picture with
    `magick -size WxH xc:black -draw "$(cat draw.mvg)" map.png`
    (strip `stroke-dasharray 1 0 ` and use `2,2` for dashes first)
  - `--click=N`: click the Nth unusual-exit line after the replay
  - `--pan=dx,dy` (with --render): drag the map background by that many pixels first
  - `--var=last_room=N`: start centred on room N (render a copy of the real db); WF_W / WF_H env set the window size; ALLNOTES=1 prints every plugin note
- `python3 components.py area_map.db [name filter]` -- connected pieces of an area
- `python3 consistency2.py area_map.db [name filter]` -- grid check: contradicting
  exits, two rooms in one cell, grid rows/columns mixing squares (0 everywhere
  for a true-grid area like Burnham Wood)

Regression set (`tx/`): brief_town, brief_gate, dalair, loop, library,
uneven_keep_irr (8 rooms), uneven_corridors (9 rooms, corridors kept apart),
misread (chat/pwho/alignment lines ignored: 2 rooms),
aliases (`--realdb`: listing over a --More-- page, `ep` exit renamed to `enter portal`, peer ignored),
drakhiya / drakhiya_irr (`--log --realdb`: blue door from Tantallon is a teleport, 28 Drakhiya rooms either way),
drakhiya2_irr (`--log --realdb`: 39 rooms, guards recognised; drakhiya2 without the flag duplicates heavily and should print the irregular hint with ALLNOTES=1),
resume (`--log --realdb --var=last_room=1138` on a copy of the real db minus room 1148: "picked up from room #1138"),
subarea (`amap boundary` / `amap subarea` commands, ALLNOTES=1)
(plain); overland, reallog, burnham*, hobbitat, tantallon, portal, cavern,
darkmaze2 (`--log`). Expected: Burnham replays have 0 problems in
consistency2; Hobbitat keeps its two "A road running through the village"
rooms separate; Tantallon keeps two "Main Street (e,n,s,w)".

To debug a real walk, copy the user's `../area_map.db` and read its `trace`
table (check the `build` column first -- the user often hasn't reloaded).
