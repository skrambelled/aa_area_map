#!/bin/sh
# Downloads the lupa wheel (bundles Lua 5.1) from PyPI and unpacks it into
# dev/lupa/pylib, for harness.py and luacheck.py. No pip needed.
cd "$(dirname "$0")" || exit 1
mkdir -p lupa && cd lupa || exit 1
PYTAG=$(python3 -c 'import sys; print(f"cp{sys.version_info[0]}{sys.version_info[1]}")')
URL=$(curl -s https://pypi.org/pypi/lupa/json | python3 -c "
import json, sys
for u in json.load(sys.stdin)['urls']:
    f = u['filename']
    if '$PYTAG' in f and 'manylinux' in f and 'x86_64' in f:
        print(u['url']); break")
[ -n "$URL" ] || { echo "no lupa wheel found for $PYTAG"; exit 1; }
curl -sLo lupa.whl "$URL" && python3 -m zipfile -e lupa.whl pylib && echo "lupa unpacked into $(pwd)/pylib"
