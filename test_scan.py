import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"

with cdp.Tab() as t:
    # ?v=3 = ข้าม cache ของ service worker
    t.goto("http://127.0.0.1:8099/index.html?v=3")
    time.sleep(6)
    print("แอพเวอร์ชัน:", t.eval("document.getElementById('bRun') ? 'ใหม่ (Chess Scan)' : 'เก่า ✗'"))
    print("engine  :", t.eval("document.getElementById('sub').textContent"))
    print("rows    :", t.eval("document.querySelectorAll('.pvrow').length"))

    for a, b in [("e2","e4"), ("e7","e5"), ("g1","f3")]:
        t.eval(f'document.querySelector(\'.sq[data-sq="{a}"]\').onclick(); 1'); time.sleep(0.25)
        t.eval(f'document.querySelector(\'.sq[data-sq="{b}"]\').onclick(); 1'); time.sleep(0.45)
    print("moves   :", t.eval("document.getElementById('moves').textContent"))

    t.eval("document.getElementById('bRun').onclick(); 1")
    time.sleep(14)
    print("\n--- 3 ตัวเลือกที่ดีที่สุด ---")
    print(t.eval("""Array.from(document.querySelectorAll('.pvrow')).map(r=>r.textContent.trim().replace(/\\s+/g,' ')).join('\\n')"""))
    print("arrows :", t.eval("document.querySelectorAll('#arrows line').length"),
          "| evalbar:", t.eval("document.getElementById('evaltxt').textContent"),
          "| status:", t.eval("document.getElementById('status').textContent"))
    t.shot(D + r"\shot-scan.png")

    before = t.eval("document.getElementById('moves').textContent")
    t.eval("document.querySelector('.pvrow').onclick(); 1")
    time.sleep(1.5)
    after = t.eval("document.getElementById('moves').textContent")
    print("\nแตะแถวที่ 1 = เดินตามคำแนะนำ")
    print("   ก่อน:", before)
    print("   หลัง:", after)
    print("   สำเร็จ:", before != after)
    t.shot(D + r"\shot-scan2.png")
