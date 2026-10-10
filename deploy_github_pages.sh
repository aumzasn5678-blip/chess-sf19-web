#!/usr/bin/env bash
set -e
cd "E:/Hermes_workbench/50_research/2026-10-10_chess-app"
R="aumzasn5678-blip/chess-sf19-web"

echo "=== 1) เอาไฟล์เอนจินเข้า repo (เว็บต้องใช้) ==="
cat > .gitignore <<'EOF'
lib/meta.json
_appcheck.mjs
shot-*.png
__pycache__/
EOF
git add -A
git -c user.name="Hermes Agent" -c user.email="agent@local" commit -q -m "snap-20261010-chess39: ใส่ lib/ (stockfish wasm + chess.js) เข้า repo เพื่อขึ้นเว็บ" || true
git tag -f snap-20261010-chess39 >/dev/null
git push -q origin main
git push -f -q origin snap-20261010-chess39
echo "  ไฟล์ที่ tracked ใน repo:"; git ls-files | head -20

echo "=== 2) เปิด repo เป็น public ==="
gh repo edit "$R" --visibility public --accept-visibility-change-consequences >/dev/null 2>&1 || echo "  (แก้ visibility ไม่ได้/ไม่ต้อง)"
gh repo view "$R" --json visibility,url 2>/dev/null

echo "=== 3) เปิด GitHub Pages ==="
gh api -X POST "repos/$R/pages" -f 'source[branch]=main' -f 'source[path]=/' >/dev/null 2>&1 || \
gh api -X PUT "repos/$R/pages" -f 'source[branch]=main' -f 'source[path]=/' >/dev/null 2>&1 || echo "  (Pages อาจเปิดอยู่แล้ว)"
gh api "repos/$R/pages" 2>/dev/null | head -c 400; echo

echo "=== 4) รอ Pages build แล้วทดสอบ ==="
sleep 30
for i in 1 2 3 4 5; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 15 "https://aumzasn5678-blip.github.io/chess-sf19-web/")
  echo "  ลองครั้งที่ $i -> index: $code"
  [ "$code" = "200" ] && break
  sleep 20
done
curl -s -o /dev/null -w "  index.html : %{http_code}\n" -L --max-time 15 "https://aumzasn5678-blip.github.io/chess-sf19-web/index.html"
curl -s -o /dev/null -w "  stockfish.wasm: %{http_code} (%{size_download} bytes)\n" -L --max-time 25 "https://aumzasn5678-blip.github.io/chess-sf19-web/lib/stockfish.wasm"
curl -s -o /dev/null -w "  chess.js : %{http_code}\n" -L --max-time 15 "https://aumzasn5678-blip.github.io/chess-sf19-web/lib/chess.js"
curl -s -o /dev/null -w "  pieces/K.png: %{http_code}\n" -L --max-time 15 "https://aumzasn5678-blip.github.io/chess-sf19-web/pieces/K.png"
curl -s -o /dev/null -w "  sw.js : %{http_code}\n" -L --max-time 15 "https://aumzasn5678-blip.github.io/chess-sf19-web/sw.js"
echo "=== URL ==="
gh api "repos/$R/pages" --jq '.html_url' 2>/dev/null || echo "https://aumzasn5678-blip.github.io/chess-sf19-web/"
