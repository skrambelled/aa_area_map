import sqlite3, sys
c = sqlite3.connect(sys.argv[1])
rooms = {r[0]: r[1:] for r in c.execute("select id, sq_x, sq_y, name, exits from rooms")}
sqcount = {}
for r in rooms.values(): sqcount[(r[0], r[1])] = sqcount.get((r[0], r[1]), 0) + 1
area = {i for i, r in rooms.items() if sqcount[(r[0], r[1])] > 1}
adj = {i: set() for i in area}
for f, t in c.execute("select from_id, to_id from exits"):
    if f in area and t in area: adj[f].add(t); adj[t].add(f)
seen, comps = set(), []
for i in sorted(area):
    if i in seen: continue
    stack, comp = [i], []
    seen.add(i)
    while stack:
        x = stack.pop(); comp.append(x)
        for y in adj[x]:
            if y not in seen: seen.add(y); stack.append(y)
    comps.append(comp)
filt = sys.argv[2] if len(sys.argv) > 2 else ""
for comp in comps:
    names = [rooms[i][2] for i in comp]
    if filt and not any(filt in (n or "") for n in names): continue
    from collections import Counter
    cnt = Counter(f"{n} ({rooms[i][3]}) @{rooms[i][0]},{rooms[i][1]}" for i, n in zip(comp, names))
    print(f"component of {len(comp)} rooms:")
    for k, v in sorted(cnt.items()): print(f"   {v} x {k}")
