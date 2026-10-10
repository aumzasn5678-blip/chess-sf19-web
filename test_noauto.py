import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"

with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html")
    time.sleep(6)
    print("หัวแอพ :", t.eval("document.querySelector('header h1').textContent.trim()"))
    print("engine :", t.eval("document.getElementById('sub').textContent"))

    # เปิดโหมดวิเคราะห์ต่อเนื่อง
    t.eval("document.getElementById('bRun').onclick(); 1")
    time.sleep(2)
    print("โหมด   :", t.eval("document.getElementById('bRun').textContent.trim()"))

    # เดินขาว 1 ตา แล้ว 'รอเฉยๆ' — ต้องไม่มีใครเดินแทน
    t.eval('document.querySelector(\'.sq[data-sq="e2"]\').onclick(); 1'); time.sleep(0.3)
    t.eval('document.querySelector(\'.sq[data-sq="e4"]\').onclick(); 1')
    for w in (3, 6, 10, 14):
        time.sleep(w if w == 3 else w - (w - 3 if w == 6 else (3 if w == 10 else 6)))
        mv = t.eval("document.getElementById('moves').textContent")
        print(f"   +{w}s moves = {mv!r}")
    print()
    print(">>> ผู้ใช้เดินแค่ e4 เอง · ฝั่งดำเดินเองหรือไม่:", "ไม่มี (ถูกต้อง ✓)" if t.eval("document.getElementById('moves').textContent").strip().endswith("e4") else "มีการเดินเอง ✗")
    print("แถวคำแนะนำ (ฝ่ายดำควรเดินอะไร):")
    print(t.eval("""Array.from(document.querySelectorAll('.pvrow')).map(r=>r.textContent.trim().replace(/\\s+/g,' ')).join('\\n')"""))
    t.shot(D + r"\shot-noauto.png")
