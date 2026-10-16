import re, sys
import os as _os
# lupa (Lua in Python) is unpacked by get_lupa.sh into dev/lupa/pylib.
sys.path.insert(0, _os.environ.get("LUPA_PATH", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "lupa", "pylib")))
from lupa import lua51

rt = lua51.LuaRuntime()
compile_ = rt.eval("function(src, name) local f, err = loadstring(src, name); return err end")
ok = True
for path in sys.argv[1:]:
    src = open(path, encoding="utf-8", errors="replace").read()
    if path.endswith(".xml"):
        m = re.search(r"<script>\s*<!\[CDATA\[(.*?)\]\]>", src, re.S)
        if not m:
            print(path, ": no script"); continue
        # keep line numbers aligned with the xml file
        prefix = src[:m.start(1)].count("\n")
        src = "\n" * prefix + m.group(1)
    err = compile_(src, "@" + path)
    if err:
        ok = False
        print(err)
    else:
        print(path, "OK")
sys.exit(0 if ok else 1)
