# area_map

Automapper for Ancient Anguish: maps the rooms you walk through inside each
overland map square (towns, dungeons, forests) and draws them in a window.

## Requires

- MUSHclient
- The **mush_windows** plugin, installed first. It provides the window and
  reads your prompt, so run `wf_prompt_setup` once (your prompt must include
  `|XCOORD|` and `|YCOORD|`).

## Install

1. MUSHclient → **File → Plugins... → Add**
2. Select `area_map.xml`
3. **Close**

Then just walk around. Brief and verbose mode both work, and you can switch
between them.

## The map

- Orange box: the room you're in. An area that spans several squares is drawn
  as one map.
- Overland map tiles aren't drawn (a square with only one mapped room counts
  as overland), apart from the one you're standing on. A new area's first
  room appears once a second room in its square is mapped.
- Short grey stubs: exits you haven't taken yet.
- Red bar across an exit: a door, open or closed.
- Green dotted line, or a green dot in the corner: a hidden or non-compass
  exit (`jump down`, `enter`, `ep`). Any command that moves you to a room in
  the same or a neighbouring square is saved as one; one that takes you
  further (a blue door to the other side of the world), `recall` and other
  teleports aren't.
- Green lines under the map: the unusual exits from the room you're in, one
  per line, as the command and where it leads (e.g. `enter ring -> Inside a
  fairy ring`), including unlisted compass exits and listed ones not yet
  tried. Click a line to send that command.
- White triangles: up and down exits. Yellow dot: the room has a note.
- Very dark grey box: a dark room ("A dark room."). Dark rooms all look the
  same, so they're tracked only by the path you walk; they fill in once seen
  lit.
- Hover a room for its details, left-click to print them, right-click to add
  a note or delete it.
- Drag the map's background to pan it; it re-centres on you when you move to
  another room. An exit to a room outside the window still shows, running
  off the edge toward it.

The **FORGET** button at the top right opens a menu with the forget commands
below (this room, this area, nearby squares, this square).

## Commands

- `amap`: status
- `amap debug`: what was read from the last bit of output, and why the
  plugin decided what it did. Use it if the map goes wrong.
- `amap trace`: print a line per move showing the command, the room numbers
  (`#from -> #to`), the square, what was seen, and what the plugin decided,
  including any rooms merged. Every move is also saved in `area_map.db`
  (table `trace`), on or off. Turn it on before a walk you want to report.
- `amap ids`: show room numbers on the map, to match them against the trace
- `amap irregular`: mark the square you're in as irregular (type it again to
  undo). Use it for areas whose rooms don't fit a grid: a long hall beside a
  row of small rooms, or a way around that takes more steps on one side than
  the other. See below.
- `amap spread <1-4>`: how many cells one step takes when drawing irregular
  areas (default 2). More gives uneven parts room to fit without crowding;
  fewer fits more of the area on screen.
- `amap boundary <exit>`: mark an exit from the room you're in as a sub-area
  boundary, both ways (again to unmark); `amap boundary` lists them. See
  below.
- `amap subarea <name>`: name the sub-area you're in (`none` clears it);
  `amap subarea` says which one you're in.
- `amap show` / `amap hide` (or Ctrl+Shift+W)
- `amap forget room`: delete the room you're in
- `amap forget area`: delete the area you're standing in: every room connected
  to yours, across all its squares, leaving overland tiles and other areas alone
- `amap forget near [n]`: delete area rooms in squares within `n` of yours
  (default 1, so your square and the 8 around it); overland tiles are kept
- `amap forget square`: delete every room in the current square

Each of these tells you how many rooms and which squares, and asks first.

Rooms are saved in `area_map.db` next to the plugin.

## Game aliases and nicknames

The plugin sees what you type, but the game expands its own aliases, so `ep`
means nothing until it's known to be `enter portal`. Type `alias` and `nick`
once (page through every `--More--`) and the plugin learns both lists; it
keeps them in `area_map.db` and picks up new ones as you define them (also
inside `do ...`). Then every command is read through them: `>name`, `$*`,
`$@`, `$1` and `do a, b, c` work as in the game. Hidden exits are saved
under the real command (`enter portal`), and ones saved under an alias name
before are renamed. `peer` (and an alias for it) never moves you on the map.
Type `alias` / `nick` again after big changes so removed ones are forgotten.

## Irregular areas

Normally rooms sit on a grid: one step east is one cell east, and walking
around a block brings you back to a room the grid already knows. Some areas
aren't built like that, and there the grid puts rooms in the wrong place, so
coming back around a loop maps the room you return to a second time.

Stand in such an area and type `amap irregular`. (When the plugin can see
that it mapped a room twice on a loop the grid can't close, it suggests
this itself, once per square.) For that square:

- Rooms are matched by the paths between them instead of grid spots. A room
  mapped twice is merged as soon as the two copies share an exit that leads
  to the same place (or to rooms that look the same), and one of the rooms
  involved is the only one like it nearby. Copies made before you typed the
  command are merged at once where that's provable.
- Until then a room can briefly appear twice: when you come into it through an
  exit it hasn't used yet and leave by another one it hasn't used.
- The map stretches to fit: the whole area is fitted at once, every exit
  wanting its room a step away on the line of its direction (a `ne` street
  stays diagonal). Where a loop doesn't add up, exits are drawn longer
  rather than shorter, spread evenly, and no room sits on another exit's
  line, and rooms are nudged so exits of unrelated rooms don't cross where
  that's possible. It's drawn spread out, two cells per step (`amap spread`), so
  uneven parts have room. The layout is kept until the map changes, so it
  looks the same from every room and only the view moves as you walk.

Don't use it for true grids of look-alike rooms (like Burnham Wood): those
need the grid to tell the rooms apart.

## Sub-areas

Some places hold a part built at a different scale, like the palace inside
Drakhiya: six rooms across where the city around it has three. No single
drawing fits both. Mark the exits into such a part as boundaries, and each
side is drawn on its own:

    amap boundary w        (standing at Palace Gates)
    amap boundary e        (standing at Servants' Entrance)
    amap subarea Palace    (standing anywhere inside, optional)

This is optional; an irregular square already stretches to fit. A
sub-area is everything you can walk to without crossing a boundary, so
rooms you find in it later belong to it automatically. A boundary exit is
drawn as a short pink stub with a dot, and listed under the map with where
it leads (`w -> Palace Courtyard  [Palace]`). The status line shows the
name of the sub-area you're in. Matching rooms isn't affected.

## Builds

Every room and exit is stamped with the plugin build that last confirmed it:
creating it, or walking through it again. When a new build fixes a mapping
bug that could have saved wrong rooms or exits, it raises its minimum trusted
build. On load, area rooms not confirmed since then are removed so they get
remapped correctly as you walk, after the database is copied to
`area_map-before-<build>.db`. Overland tiles and rooms with notes are always
kept. `amap` shows the current build and how many rooms it has confirmed.
