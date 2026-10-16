# Lays out each Burnham piece by its compass exits and reports problems:
# contradicting exits, two rooms in one cell, or a grid row/column whose
# rooms disagree about their square's Y/X.
import sqlite3, sys
from collections import deque
D = {'n': (0,-1), 's': (0,1), 'e': (1,0), 'w': (-1,0), 'ne': (1,-1), 'nw': (-1,-1), 'se': (1,1), 'sw': (-1,1)}
c = sqlite3.connect(sys.argv[1])
filt = sys.argv[2] if len(sys.argv) > 2 else 'Burnham'
rooms = {r[0]: r[1:] for r in c.execute("select id, sq_x, sq_y, name from rooms")}
area = {i for i, r in rooms.items() if filt in (r[2] or '')}
links = {}
for f, cmd, t in c.execute("select from_id, cmd, to_id from exits"):
    if f in area and t in area and cmd in D: links.setdefault(f, []).append((cmd, t))
problems = 0
seen = set()
for start in sorted(area):
    if start in seen: continue
    pos = {start: (0, 0)}; q = deque([start]); seen.add(start)
    bad = 0
    while q:
        a = q.popleft()
        for cmd, b in links.get(a, []):
            p = (pos[a][0] + D[cmd][0], pos[a][1] + D[cmd][1])
            if b not in pos: pos[b] = p; seen.add(b); q.append(b)
            elif pos[b] != p: bad += 1
    cells, rowsY, colsX = {}, {}, {}
    for r, p in pos.items():
        cells.setdefault(p, []).append(r)
        rowsY.setdefault(p[1], set()).add(rooms[r][1])
        colsX.setdefault(p[0], set()).add(rooms[r][0])
    clash = sum(1 for v in cells.values() if len(v) > 1)
    badrows = sum(1 for v in rowsY.values() if len(v) > 1)
    badcols = sum(1 for v in colsX.values() if len(v) > 1)
    problems += bad + clash + badrows + badcols
    print(f"piece #{start}: {len(pos)} rooms; {bad} contradicting exits, {clash} clashes, {badrows} mixed rows, {badcols} mixed columns")
sys.exit(1 if problems else 0)
