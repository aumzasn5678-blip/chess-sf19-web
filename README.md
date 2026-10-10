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
