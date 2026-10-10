#!/usr/bin/env bash
set -e
D="E:/Hermes_workbench/50_research/2026-10-10_chess-app"
cd "$D"

cat > .gitignore <<'EOF'
# ของที่ดึงมาจากภายนอก (ไม่ใช่ผลงานเรา) — กู้คืนได้ด้วย get_lib.sh
lib/stockfish.js
lib/stockfish.wasm
lib/chess.js
lib/meta.json
# ไฟล์ทดสอบ/ภาพชั่วคราว
_appcheck.mjs
shot-*.png
__pycache__/
EOF

cat > README.md <<'EOF'
# Chess — Stockfish 19 (เว็บแอพสำหรับ iPhone)

หมากรุกเล่นกับ Stockfish 19 ทำใช้เอง — จุดที่ตั้งใจแก้จากแอพเดิม: **เข้าป้อมได้แน่นอน** และ **กระดานไม่สลับหัวเอง**

## เปิดใช้
```bash
python -m http.server 8099 --bind 0.0.0.0
```
แล้วเปิด `http://<ไอพีเครื่อง>:8099` บน iPhone → แชร์ → เพิ่มไปที่หน้าจอโฮม

## เอนจิน
Stockfish 19 บิลด์ `lite-single` (wasm ~1.8 MB) — ดึงไฟล์ด้วย `bash get_lib.sh`
(แหล่ง: npm `stockfish@19.0.0` และ `chess.js@1.4.0`)

## เข้าป้อม (3 ทาง)
แตะคิงแล้วแตะเรือ · แตะคิงแล้วแตะช่อง g1/c1/g8/c8 · ลากคิงไป 2 ช่อง — กฎตัดสินด้วย chess.js

## ทดสอบอัตโนมัติ
- `node test_logic.mjs` — กฎเข้าป้อม (O-O / O-O-O) + syntax ของสคริปต์ใน index.html
- `python test_browser.py` — ขับ Chrome (CDP) เปิดแอพจริง: เรนเดอร์ 64 ช่อง, SF19 ตอบ bestmove, เข้าป้อมผ่าน UI
EOF

cat > SNAPSHOTS.md <<'EOF'
# SNAPSHOTS

## snap-20261010-chess1 — 2026-10-10
- สร้างครั้งแรก: เว็บแอพหมากรุก + Stockfish 19 (wasm lite-single)
- เข้าป้อม 3 ทาง (แตะคิง→แตะเรือ / แตะช่อง / ลาก 2 ช่อง), กระดานหมุนเองเท่านั้น
- ฟีเจอร์: เล่นกับ SF19 (ระดับ 0-20, เวลาคิด 0.3-4 วิ), 2 คนเครื่องเดียว, ย้อน, PGN history, PWA + service worker
- ทดสอบ: node (กฎ O-O/O-O-O) + browser CDP (SF19 ตอบ e6/c5 จริง, เข้าป้อมผ่าน UI สำเร็จ)
- แก้บั๊กที่เจอตอนเทสต์: `tryMove({to: moveObject})` → `to: target.to`
EOF

git init -q 2>/dev/null || true
git add -A
git -c user.name="Hermes Agent" -c user.email="agent@local" commit -q -m "snap-20261010-chess1: เว็บแอพหมากรุก + Stockfish 19 (เข้าp้อม 3 ทาง, กระดานไม่สลับเอง)" || echo "(ไม่มีอะไรใหม่)"
git tag -f snap-20261010-chess1 >/dev/null
git branch -M main

if gh repo view aumzasn5678-blip/chess-sf19-web >/dev/null 2>&1; then
  echo "repo มีอยู่แล้ว → push snapshot ต่อ"
else
  gh repo create chess-sf19-web --private --source=. --remote=origin --description "Chess web app (PWA) with Stockfish 19 — personal use" >/dev/null
  echo "สร้าง repo ใหม่ (private)"
fi
git remote get-url origin >/dev/null 2>&1 || git remote add origin https://github.com/aumzasn5678-blip/chess-sf19-web.git
git push -u origin main -q && git push -f origin snap-20261010-chess1 -q
echo "---"
gh repo view aumzasn5678-blip/chess-sf19-web --json name,visibility,url,pushedAt 2>/dev/null
echo "--- commit ---"
git log --oneline -3
