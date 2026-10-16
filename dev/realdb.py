# Python sqlite3 behind the Lua sqlite3 API the plugin uses.
import sqlite3
def install(lua, path):
    conn = sqlite3.connect(path, isolation_level=None)
    def py_exec(sql):
        # like lsqlite3's db:exec: report failure as a return code, never raise
        try:
            conn.executescript(sql) if sql.strip().upper() not in ("BEGIN", "COMMIT") else conn.execute(sql)
            return 0
        except sqlite3.Error:
            return 1
    def py_run(sql, args):
        conn.execute(sql, [None if args[i] == "\x00NULL" else args[i] for i in range(1, len(args) + 1)] if args else [])
    def py_rows(sql):
        cur = conn.execute(sql)
        cols = [d[0] for d in cur.description]
        return lua.table_from([lua.table_from({k: v for k, v in zip(cols, r) if v is not None}) for r in cur.fetchall()])
    g = lua.globals()
    g.py_exec, g.py_run, g.py_rows = py_exec, py_run, py_rows
    lua.execute(r'''
    sqlite3 = { open = function()
      return {
        exec = function(self, sql) return py_exec(sql) end,
        prepare = function(self, sql)
          local args
          return {
            bind_values = function(st, ...) args = { n = select("#", ...), ... } end,
            step = function() local t = {} for i = 1, args.n do t[i] = args[i] == nil and "\0NULL" or args[i] end; py_run(sql, t) end,
            reset = function() end, finalize = function() end,
          }
        end,
        nrows = function(self, sql)
          local rows = py_rows(sql)
          local i = 0
          return function()
            i = i + 1
            return rows[i]
          end
        end,
        errmsg = function() return "" end, close = function() end,
      }
    end }
    ''')
