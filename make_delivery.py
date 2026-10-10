import os, shutil, hashlib
SRC = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
DST = r"C:\Users\poxii\Desktop\Chess-SF19-เว็บแอพ"

os.makedirs(DST, exist_ok=True)
# คัดลอกตัวแอพ (ยกเว้นไฟล์เทสต์/สคริปต์ดึงของ)
SKIP = {"get_lib.sh", "setup.py", "test_logic.mjs", "test_browser.py", "_appcheck.mjs", "meta.json",
        "shot-2p.png", "shot-sf.png"}
copied = []
for root, dirs, files in os.walk(SRC):
    rel = os.path.relpath(root, SRC)
    if rel.startswith("_"):
        continue
    for f in files:
        if f in SKIP:
            continue
        s = os.path.join(root, f)
        d = os.path.join(DST, rel, f) if rel != "." else os.path.join(DST, f)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        copied.append(os.path.relpath(d, DST))

LAUNCHER = r'''@echo off
chcp 65001 >nul
title Chess SF19 — เซิร์ฟเวอร์ (ปิดหน้าต่างนี้ = หยุด)
cd /d "%~dp0"
echo ==================================================
echo    หมากรุก Stockfish 19  —  เปิดใช้บน iPhone
echo ==================================================
set "IP="
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /i "IPv4"') do (echo %%A | findstr "192.168" >nul && set "IP=%%A")
set "IP=%IP: =%"
echo.
echo    บนเครื่องนี้ :  http://localhost:8099
if defined IP echo    บน iPhone   :  http://%IP%:8099
echo.
echo    วิธีใช้บน iPhone: เปิด Safari ^> พิมพ์ที่อยู่ข้างบน
echo                      ^> ปุ่มแชร์ ^> "เพิ่มไปที่หน้าจอโฮม"
echo.
echo    *** อย่าปิดหน้าต่างนี้ ถ้ายังเล่นอยู่ (ปิด = เซิร์ฟเวอร์หยุด) ***
echo.
start "" http://localhost:8099
python -m http.server 8099 --bind 0.0.0.0
pause
'''

README = """หมากรุก Stockfish 19 (เว็บแอพ) — ใช้บน iPhone
================================================

เปิดใช้ยังไง
------------
1. ต่อคอมไว้ (ไม่ต้องเล่นบนคอมก็ได้)
2. ดับเบิลคลิก "เปิดแอพหมากรุก.bat"  → จะเห็นที่อยู่ 2 บรรทัด
   - บนเครื่องนี้ : http://localhost:8099
   - บน iPhone   : http://<ไอพี-คอม>:8099
3. บน iPhone: ต่อ Wi-Fi วงเดียวกับคอม → เปิด Safari → พิมพ์ที่อยู่ในบรรทัดที่ 2
4. อยากได้เป็นไอคอนแอพ: ปุ่มแชร์ (สี่เหลี่ยมลูกศรขึ้น) → "เพิ่มไปที่หน้าจอโฮม"

ใช้ยังไง
--------
- แตะหมาก → จุดฟ้า = ช่องที่เดินได้ → แตะช่องปลายทาง
- เข้าป้อม ได้ 3 ทาง: แตะคิงแล้วแตะเรือ / แตะคิงแล้วแตะช่อง g1,c1,g8,c8 / ลากคิงไป 2 ช่อง
- ปุ่ม "↻ หมุนกระดาน" = หมุนมุมมองเอง (กระดานไม่สลับเอง)
- โหมด: เล่นกับ Stockfish 19 หรือ 2 คนเครื่องเดียว
- ระดับ SF 0-20 (0=อ่อนสุด 20=แรงสุด) · เวลาคิดต่อตา 0.3-4 วิ

ปิดยังไง
--------
ปิดหน้าต่าง .bat = เซิร์ฟเวอร์หยุด (แอพบน iPhone จะเปิดไม่ได้จนกว่าจะเปิดใหม่)

หมายเหตุ
--------
- ใช้งานออฟไลน์เต็มรูปแบบ (ไม่ต้องเปิดคอม) ต้องเอาแอพไปวางบนเว็บ (https) — บอกได้ เดี๋ยวทำให้
- ไฟล์ทั้งหมดอยู่ในโฟลเดอร์นี้ (index.html + lib/ ตัวเอนจิน Stockfish 19)
- ตัวสำเนาที่ใช้พัฒนา: E:\\Hermes_workbench\\50_research\\2026-10-10_chess-app
"""

open(os.path.join(DST, "เปิดแอพหมากรุก.bat"), "w", encoding="utf-8", newline="\r\n").write(LAUNCHER)
open(os.path.join(DST, "README.txt"), "w", encoding="utf-8").write(README)

print("คัดลอก", len(copied), "ไฟล์ ->", DST)
for f in sorted(copied):
    p = os.path.join(DST, f)
    print(f"   {os.path.getsize(p):>10,} B  {f}")
print("\nไฟล์ควบคุม:")
for f in ("เปิดแอพหมากรุก.bat", "README.txt"):
    p = os.path.join(DST, f)
    print(f"   {os.path.getsize(p):>10,} B  {f}  md5={hashlib.md5(open(p,'rb').read()).hexdigest()[:12]}")
