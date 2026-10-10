#!/usr/bin/env bash
set -e
D="/e/Hermes_workbench/50_research/2026-10-10_chess-app"
mkdir -p "$D/lib"
cd "$D/lib"
echo "== meta (ไฟล์ single/lite) =="
curl -s -L "https://unpkg.com/stockfish@19.0.0/?meta" -o meta.json
python - <<'PY'
import json
d = json.load(open("meta.json"))
for f in d["files"]:
    p = f["path"]
    if p.startswith("/bin/") and ("lite-single" in p or p.endswith(".wasm")):
        print(f"  {f['size']:>12,}  {p}")
PY
echo
echo "== download =="
curl -s -L -o chess.js "https://unpkg.com/chess.js@1.4.0/dist/esm/chess.js"
curl -s -L -o sf19.js "https://unpkg.com/stockfish@19.0.0/bin/stockfish-19-lite-single.js"
curl -s -L -o sf19.wasm "https://unpkg.com/stockfish@19.0.0/bin/stockfish-19-lite-single.wasm"
ls -la
echo
echo "== ตรวจ =="
head -c 120 chess.js; echo
grep -o "stockfish[^\"']*\.wasm" sf19.js | head -3 || true
file sf19.wasm 2>/dev/null || head -c 8 sf19.wasm | xxd | head -1
