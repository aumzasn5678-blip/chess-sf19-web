import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"

with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=6")
    time.sleep(6)
    print("หัวแอพ :", t.eval("document.querySelector('header h1').textContent.trim()"))
    print("engine :", t.eval("document.getElementById('sub').textContent"))
    print("รูปหมากบนกระดาน :", t.eval("document.querySelectorAll('.sq img.pcimg').length"), "(ควรเป็น 32)")
    print("รูปโหลดครบไหม :", t.eval("""Array.from(document.querySelectorAll('.sq img.pcimg')).every(i=>i.complete && i.naturalWidth>0)"""))
    print("ตัวอย่าง src     :", t.eval("""Array.from(new Set(Array.from(document.querySelectorAll('.sq img.pcimg')).map(i=>i.getAttribute('src')))).slice(0,4).join(', ')"""))

    # เปิดวิเคราะห์ แล้วเดินเองฝั่งเดียว — รอ 12 วิ ห้ามมีใครเดินแทน
    t.eval("document.getElementById('bRun').onclick(); 1")
    time.sleep(2)
    t.eval('document.querySelector(\'.sq[data-sq="d2"]\').onclick(); 1'); time.sleep(0.3)
    t.eval('document.querySelector(\'.sq[data-sq="d4"]\').onclick(); 1')
    time.sleep(12)
    mv = t.eval("document.getElementById('moves').textContent").strip()
    print("\nหลังเดิน d4 + รอ 12 วิ (โหมดวิเคราะห์เปิดอยู่):", repr(mv))
    print("ฝั่งตรงข้ามเดินเองไหม:", "ไม่ (ถูกต้อง ✓)" if mv.endswith("d4") else "เดินเอง ✗")
    print("\nแถวคำแนะนำ:")
    print(t.eval("""Array.from(document.querySelectorAll('.pvrow')).map(r=>r.textContent.trim().replace(/\\s+/g,' ')).join('\\n')"""))
    t.shot(D + r"\shot-pieces.png")
