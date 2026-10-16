-- replaces the no-op Window* stubs with ones that record ImageMagick draw ops
ops = {}
local function rgb(c) return string.format("#%02x%02x%02x", c % 256, math.floor(c / 256) % 256, math.floor(c / 65536) % 256) end
function WindowRectOp(win, action, l, t, r, b, c1)
  if action == 2 then ops[#ops+1] = string.format("fill %s stroke none rectangle %d,%d %d,%d", rgb(c1), l, t, r - 1, b - 1)
  elseif action == 1 then ops[#ops+1] = string.format("fill none stroke %s stroke-width 1 rectangle %d,%d %d,%d", rgb(c1), l, t, r - 1, b - 1) end
end
function WindowLine(win, x1, y1, x2, y2, c, style, w)
  ops[#ops+1] = string.format("fill none stroke %s stroke-width %d %s line %d,%d %d,%d", rgb(c), w, style == 2 and "stroke-dasharray 2 2" or "stroke-dasharray 1 0", x1, y1, x2, y2)
end
function WindowPolygon(win, pts, pen, ps, pw, brush)
  ops[#ops+1] = string.format("fill %s stroke none polygon %s", rgb(brush), pts:gsub(",(%-?%d+),", ",%1 "))
end
function WindowText(win, font, text, l, t, r, b, c)
  ops[#ops+1] = string.format("fill %s stroke none font-size 11 text %d,%d '%s'", rgb(c), l, t + 10, (text:gsub("'", "")))
  return #text * 7
end

function WindowTextWidth(win, font, text) return #text * 7 end
