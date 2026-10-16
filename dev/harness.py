"""Runs area_map.xml's script outside MUSHclient against a transcript.

Usage: harness.py <area_map.xml> <transcript>... [--debug]
Transcript: game output as pasted; a line right after a prompt line ("...>")
that starts lowercase is treated as a command you typed.
"""
import re, sys, os
import os as _os
# lupa (Lua in Python) is unpacked by get_lupa.sh into dev/lupa/pylib.
sys.path.insert(0, _os.environ.get("LUPA_PATH", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "lupa", "pylib")))
from lupa import lua51

args = [a for a in sys.argv[1:] if not a.startswith("--")]
show_debug = "--debug" in sys.argv
LOG_MODE = "--log" in sys.argv
KNOWN_CMD = re.compile(r"^(n|s|e|w|ne|nw|se|sw|u|d|north|south|east|west|northeast|northwest|southeast|southwest|up|down|l|look|search|enter|out|o [a-z]+|close [a-z]+)$")
xml, transcripts = args[0], args[1:]
src = open(xml).read()
m = re.search(r"<script>\s*<!\[CDATA\[(.*?)\]\]>", src, re.S)
prefix = src[:m.start(1)].count("\n")
script = "\n" * prefix + m.group(1)

lua = lua51.LuaRuntime(unpack_returned_tuples=True)
g = lua.globals()

PROMPT_LINES = ["^.*?$", r"^.*?/.*?:.*?>$", r"^X:\[(-?\d+)\]Y:\[(-?\d+)\]$"]
scratch = os.path.dirname(os.path.abspath(__file__))

def pymatch(pattern, s):
    return re.search(pattern, s) is not None
g.pymatch = pymatch
g.PROMPT_TEXT = "\n".join(PROMPT_LINES) + "\n3"
g.SCRATCH = scratch + "/"
g.ALLNOTES = bool(os.environ.get("ALLNOTES"))

lua.execute(r'''
notes = {}
function ColourNote(a, b, msg) notes[#notes + 1] = msg; if a == 'gray' or ALLNOTES then print(msg) end end
function GetPluginID() return "self" end
function GetPluginInfo(id, n)
  if n == 20 then return SCRATCH end
  if n == 17 then return true end
end
function IsPluginInstalled() return true end
function EnablePlugin() end
function LoadPlugin() end
vars = { aids_reset = "x" }   -- the one-time switch-off of trace/ids already done
function GetVariable(k) return vars[k] end
function SetVariable(k, v) vars[k] = v end
function CallPlugin(id, fn)
  if fn == "MW_GetPromptLines" then return 0, PROMPT_TEXT end
  if fn == "MW_GetPosition" then return 0, "0,0" end
  return 0
end
rex = { new = function(p) return { match = function(self, s) if pymatch(p, s) then return 1 end return nil end } end }
bit = { band = function(a, b) return 0 end }
miniwin = { cursor_hand = 0, hotspot_got_rh_mouse = 0x20 }
utils = { timer = os.clock, msgbox = function(msg) print('msgbox: ' .. msg) return 'yes' end }
drawCalls = 0
function WindowText(win, font, text) drawCalls = drawCalls + 1; return #text * 7 end
function Execute(cmd) print("EXECUTE: " .. cmd) end
mouse = {}
function WindowInfo(win, n) return mouse[n] or 0 end
for _, name in ipairs{ "WindowLine", "WindowRectOp", "WindowPolygon", "WindowAddHotspot", "WindowFont", "WindowDragHandler" } do
  _G[name] = function(...) drawCalls = drawCalls + 1 end
end
function WindowFontInfo() return 12 end
function WindowTextWidth(win, font, text) return #text * 7 end
function WindowMenu(win, x, y, items) print('menu at ' .. x .. ',' .. y .. ': ' .. items) return MENU_CHOICE or '' end
-- in-memory sqlite stand-in: just checks the calls are well-formed
sqlite3 = { open = function()
  return {
    exec = function() return 0 end,
    prepare = function(self, sql) return { bind_values = function() end, step = function() end, reset = function() end, finalize = function() end } end,
    nrows = function() return function() return nil end end,
    errmsg = function() return "" end,
    close = function() end,
  }
end }
''')

# winframe stand-in: redraw runs on_draw + on_hotspots
open(os.path.join(scratch, "winframe.lua"), "w").write(r'''
local M = {}
function M.new(cfg)
  local self = { win = "amap", content_w = tonumber(os.getenv("WF_W") or 300), content_h = tonumber(os.getenv("WF_H") or 220) }
  function self:contentTop() return 20 end
  function self:redraw() cfg.on_draw(self.content_w, self.content_h); cfg.on_hotspots(self.content_w, self.content_h) end
  function self:repaintContent() cfg.on_draw(self.content_w, self.content_h) end
  function self:show() self:redraw() end
  function self:hide() end
  function self:bringToFront() end
  return self
end
return M
''')

if "--realdb" in sys.argv:
    import realdb
    realdb.install(lua, os.path.join(scratch, "area_map.db"))
lua.execute(script)
if "--trace" in sys.argv:
    g.SetVariable("trace", "1")
if "--ids" in sys.argv:
    g.SetVariable("show_ids", "1")
for a in sys.argv:
    if a.startswith("--var="):
        k, v = a[6:].split("=", 1)
        g.SetVariable(k, v)
g.OnPluginInstall()

def run(path):
    lines = open(path).read().split("\n")
    i = 0
    after_prompt = True
    while i < len(lines):
        line = lines[i]
        i += 1
        if line == "":
            continue
        mc = re.match(r"^X:\[(-?\d+)\]Y:\[(-?\d+)\]$", line)
        if LOG_MODE and mc:
            g.OnPluginLineReceived(line)
            g.OnPluginBroadcast(1, "26a4ca2758d503d86efe902e", "mush_windows", mc.group(1) + "," + mc.group(2))
        if (not LOG_MODE and re.match(r"^\d+/\d+:\d+>$", line)) or (LOG_MODE and mc):
            if not LOG_MODE:
                g.OnPluginLineReceived(line)
                g.OnPluginLineReceived("X:[0]Y:[0]")
                g.OnPluginBroadcast(1, "26a4ca2758d503d86efe902e", "mush_windows", "0,0")
            if show_debug:
                g.notes = lua.table()
                g.AmapCommand("amap_cmd", "amap debug", lua.table_from({1: "debug"}))
                notes = g.notes
                for k in range(1, len(notes) + 1):
                    print("   ", notes[k])
            after_prompt = True
            continue
        if line == "<enter>":
            # an empty line sent (e.g. paging on at --More--)
            print(">> <enter>")
            g.OnPluginSent("")
            continue
        if line.startswith("amap ") or line == "amap":
            # a plugin command typed mid-walk (the alias, not sent to the game)
            print(">>", line)
            lua.execute('notes = {}')
            arg = line[5:]
            g.AmapCommand("amap_cmd", line, lua.table_from({1: arg}))
            notes = g.notes
            for k in range(1, len(notes) + 1):
                print("   ", notes[k])
            continue
        if (after_prompt and line[0].islower()) or KNOWN_CMD.match(line):
            print(">>", line)
            g.OnPluginSent(line)
            after_prompt = LOG_MODE  # typed-ahead commands echo back to back
            continue
        g.OnPluginLineReceived(line)
        after_prompt = False
    # final summary
    g.notes = lua.table()

for t in transcripts:
    print("=====", t)
    run(t)
lua.execute('''
local count = 0
notes = {}
AmapCommand("amap_cmd", "amap", { "" })
for _, n in ipairs(notes) do print(n) end
print("draw calls: " .. drawCalls)
''')
for a in sys.argv:
    if a.startswith("--cmd="):
        c = a[6:]
        lua.execute('notes = {}')
        g.AmapCommand("amap_cmd", "amap " + c, lua.table_from({1: c}))
        notes = g.notes
        for k in range(1, len(notes) + 1):
            print(notes[k])
for a in sys.argv:
    if a.startswith("--menu="):
        g.MENU_CHOICE = a[7:]
        lua.execute('notes = {}')
        g.AmapForgetMenu(0, "amap_btn_forget")
        notes = g.notes
        for k in range(1, len(notes) + 1):
            print(notes[k])
for a in sys.argv:
    if a.startswith("--click="):
        lua.execute('AmapCommand("amap_cmd", "amap show", { "show" })')
        g.AmapSpecialClick(0, "amap_special_" + a[8:])
if "--render" in sys.argv:
    lua.execute(open(os.path.join(scratch, "render.lua")).read())
    lua.execute('AmapCommand("amap_cmd", "amap show", { "show" })')
    for a in sys.argv:
        if a.startswith("--pan="):
            # drag the map background by dx,dy pixels, keep only the final draw
            dx, dy = (int(v) for v in a[6:].split(","))
            lua.execute(f"""
              mouse[14], mouse[15] = 100, 100        -- relative to the map window
              mouse[17], mouse[18] = 700, 400        -- relative to the output window
              AmapPanDown(0, "zzz_amap_pan")
              mouse[17], mouse[18] = 700 + ({dx}), 400 + ({dy})
              AmapPanMove(0, "zzz_amap_pan")
              ops = {{}}
              AmapPanRelease(0, "zzz_amap_pan")
            """)
    ops = g.ops
    with open(os.path.join(scratch, "draw.mvg"), "w") as f:
        for k in range(1, len(ops) + 1):
            f.write(ops[k] + "\n")

