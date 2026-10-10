import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
def tap(t, sq): t.eval(f'document.querySelector(\'.sq[data-sq="{sq}"]\').onclick(); 1')

with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=11")
    time.sleep(6)
    print("engine :", t.eval("document.getElementById('sub').textContent"))
    print("ปุ่ม    :", t.eval("""['bRun','bBack','bFwd','bFlip','bTurn'].map(i=>document.getElementById(i)?document.getElementById(i).textContent.trim():'MISSING').join(' | ')"""))
    print("รูปหมาก:", t.eval("document.querySelectorAll('.sq img.pcimg').length"))
    print("หลอด   :", t.eval("""document.getElementById('evalhalf').style.background.replace(/\\s+/g,' ')"""))
    print("ค่าในหลอด:", t.eval("document.getElementById('evaltxt').textContent"), "| ป้ายซ้าย/ขวา:",
          t.eval("document.getElementById('evaltag').textContent + ' / ' + document.getElementById('evaltagr').textContent"))

    # เดิน 2 ตา (ทั้งสองฝั่งเอง)
    for a,b in [("e2","e4"),("e7","e5"),("g1","f3")]:
        tap(t,a); time.sleep(0.25); tap(t,b); time.sleep(0.4)
    print("\nlog บันทึกการเดิน:", t.eval("document.getElementById('log').textContent").strip())
    print("ตาปัจจุบัน:", t.eval("document.getElementById('bTurn').textContent"))

    # กดรัน
    t.eval("document.getElementById('bRun').onclick(); 1")
    time.sleep(10)
    print("\nแถวคำแนะนำ:")
    print(t.eval("""Array.from(document.querySelectorAll('.pvrow')).map(r=>r.textContent.trim().replace(/\\s+/g,' ')).join('\\n')"""))
    print("หลอดคะแนน :", t.eval("document.getElementById('evaltxt').textContent"),
          "| fill left/width:", t.eval("document.getElementById('evalfill').style.left + ' / ' + document.getElementById('evalfill').style.width"))
    print("ลูกศร:", t.eval("document.querySelectorAll('#arrows line').length"), "| status:", t.eval("document.getElementById('status').textContent"))

    # ย้อนกลับ / ไปข้างหน้า
    t.eval("document.getElementById('bBack').onclick(); 1"); time.sleep(0.4)
    back = t.eval("document.getElementById('log').textContent").strip()
    t.eval("document.getElementById('bFwd').onclick(); 1"); time.sleep(0.4)
    fwd = t.eval("document.getElementById('log').textContent").strip()
    print("\nย้อนกลับ ->", repr(back), "\nไปข้างหน้า ->", repr(fwd))

    # กลับหัว -> หลอดต้องสลับซ้าย/ขวา
    t.eval("document.getElementById('bFlip').onclick(); 1"); time.sleep(0.5)
    print("\nกลับหัว -> หลอด:", t.eval("""document.getElementById('evalhalf').style.background.replace(/\\s+/g,' ')"""),
          "| ป้าย:", t.eval("document.getElementById('evaltag').textContent + ' / ' + document.getElementById('evaltagr').textContent"))
    print("ตอนนี้บอร์ดมี img:", t.eval("document.querySelectorAll('.sq img.pcimg').length"))
    t.shot(D + r"\shot-v3.png")
