import os, shutil, hashlib
SRC = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
DST = r"C:\Users\poxii\Desktop\Chess-SF19-เว็บแอพ"

os.makedirs(DST, exist_ok=True)
SKIP = {"get_lib.sh", "setup.py", "test_logic.mjs", "test_browser.py", "test_scan.py", "test_noauto.py",
        "test_pieces.py", "_appcheck.mjs", "meta.json", "make_delivery.py", "backup_github.sh"}
for f in ("shot-2p.png", "shot-sf.png", "shot-scan.png", "shot-scan2.png"):
    SKIP.add(f)
copied = []
for root, dirs, files in os.walk(SRC):
    rel = os.path.relpath(root, SRC)
    if rel.startswith("_") or rel.startswith(".git"):
        continue
    for f in files:
        if f in SKIP:
            continue
        s = os.path.join(root, f)
        d = os.path.join(DST, f) if rel == "." else os.path.join(DST, rel, f)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        copied.append(os.path.relpath(d, DST))

LAUNCHER = r'''@echo off
chcp 65001 >nul
title Chess Scan — เซิร์ฟเวอร์ (ปิดหน้าต่างนี้ = หยุด)
cd /d "%~dp0"
echo ==================================================
echo    Chess Scan — วิเคราะห์หมากรุก (Stockfish 19)
echo ==================================================
set "IP="
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /i "IPv4"') do (echo %%A | findstr "192.168" >nul && set "IP=%%A")
set "IP=%IP: =%"
echo.
echo    บนเครื่องนี้ :  http://localhost:8100
if defined IP echo    บน iPhone   :  http://%IP%:8100
echo.
echo    วิธีใช้บน iPhone: เปิด Safari ^> พิมพ์ที่อยู่บรรทัดบน
echo                      ^> ปุ่มแชร์ ^> "เพิ่มไปที่หน้าจอโฮม"
echo.
echo    *** อย่าปิดหน้าต่างนี้ ถ้ายังใช้อยู่ (ปิด = เซิร์ฟเวอร์หยุด) ***
echo.
start "" http://localhost:8100
python -m http.server 8100 --bind 0.0.0.0
pause
'''

README = """Chess Scan — วิเคราะห์หมากรุกด้วย Stockfish 19 (ใช้บน iPhone)
===========================================================

ทําไว้ใช้ตอนเล่นกับ "คน" — กดวิเคราะห์ แล้วมันโชว์ 3 ทางเดินที่ดีที่สุดให้เลือก

เปิดใช้ยังไง
------------
1. ดับเบิลคลิก "เปิดแอพหมากรุก.bat" -> จะเห็นที่อยู่ 2 บรรทัด
   - บนเครื่องนี้ : http://localhost:8100
   - บน iPhone   : http://<ไอพี-คอม>:8100
2. บน iPhone: ต่อ Wi-Fi วงเดียวกับคอม -> เปิด Safari -> พิมพ์ที่อยู่ในบรรทัดที่ 2
3. อยากได้เป็นไอคอนแอพ: ปุ่มแชร์ (สี่เหลี่ยมลูกศรขึ้น) -> "เพิ่มไปที่หน้าจอโฮม"
   (ตอนนี้ต้องเปิดคอมค้างไว้ ถ้าอยากใช้ตอนออกไปข้างนอกโดยไม่ต้องเปิดคอม = เอาแอพขึ้นเว็บ)

ใช้วิเคราะห์ยังไง
-----------------
- แตะหมาก -> แตะช่องปลายทาง = เดินหมาก (เดินได้ทั้งสองฝั่ง = จําลองเกมที่เล่นกับคน)
- กด "วิเคราะห์" = เอนจินคิดต่อเนื่อง อัปเดตให้เองทุกตา (กดอีกครั้ง = หยุด)
- แผงล่างโชว์ 3 ตัวเลือกที่ดีที่สุด พร้อมคะแนน (+ = ขาวได้เปรียบ, - = ดําได้เปรียบ)
- แตะแถวไหน = เดินตามนั้นทันที
- ลูกศรบนกระดาน: เขียว = อันดับ 1, ส้ม = 2, ฟ้า = 3
- แถบกลางจอ = คะแนนรวมของตําแหน่งปัจจุบัน
- ปุ่มอื่น: ย้อน / หมุนกระดาน (ไม่สลับเอง) / เกมใหม่ / คัดลอก PGN
- "ตั้งค่า" ล่างสุด: ความลึก (12/16/20/24) / จํานวนตัวเลือก (2-5) / วาง FEN เพื่อตั้งตําแหน่งเอง

เข้าป้อม
--------
แตะคิงแล้วแตะเรือ / แตะคิงแล้วแตะช่อง g1,c1 / ลากคิงไป 2 ช่อง (กฎตัดสินด้วย chess.js)

หมายเหตุ
--------
- ตัวเอนจินรันในมือถือเอง (WebAssembly) ไม่ได้ส่งข้อมูลออกไปไหน
- ตัวพัฒนา: E:\\Hermes_workbench\\50_research\\2026-10-10_chess-app
"""

open(os.path.join(DST, "เปิดแอพหมากรุก.bat"), "w", encoding="utf-8", newline="\r\n").write(LAUNCHER)
open(os.path.join(DST, "README.txt"), "w", encoding="utf-8").write(README)

print("คัดลอก", len(copied), "ไฟล์ ->", DST)
for f in sorted(copied):
    p = os.path.join(DST, f)
    print(f"   {os.path.getsize(p):>10,} B  {f}")
