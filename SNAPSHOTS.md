# SNAPSHOTS

## snap-20261010-chess1 — 2026-10-10
- สร้างครั้งแรก: เว็บแอพหมากรุก + Stockfish 19 (wasm lite-single)
- เข้าป้อม 3 ทาง (แตะคิง→แตะเรือ / แตะช่อง / ลาก 2 ช่อง), กระดานหมุนเองเท่านั้น
- ฟีเจอร์: เล่นกับ SF19 (ระดับ 0-20, เวลาคิด 0.3-4 วิ), 2 คนเครื่องเดียว, ย้อน, PGN history, PWA + service worker
- ทดสอบ: node (กฎ O-O/O-O-O) + browser CDP (SF19 ตอบ e6/c5 จริง, เข้าป้อมผ่าน UI สำเร็จ)
- แก้บั๊กที่เจอตอนเทสต์: `tryMove({to: moveObject})` → `to: target.to`
