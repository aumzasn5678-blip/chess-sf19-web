import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=22"); time.sleep(6)
    print("1) เริ่มเกม (ตาขาว):")
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(9)
    print("   แถว (ขาวเดิน):", t.eval("""Array.from(document.querySelectorAll('.pvrow')).map(r=>r.textContent.trim().replace(/\\s+/g,' ')).join(' | ')"""))
    print("   หลอด(ฝั่งล่าง=ขาว):", t.eval("document.getElementById('evaltxt').textContent"))
    # เดิน e4 -> ตาดำ
    d = t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq)[0]""")
    t.eval(f'document.querySelector(\'.sq[data-sq="{d}"]\').onclick(); 1'); time.sleep(11)
    print("\n2) หลังเดิน", d, "-> ตาดำ:")
    print("   แถว (ดำเดิน — ต้องเป็นลบ = ดำเสียเปรียบ, แถว 1 น้อยสุด):",
          t.eval("""Array.from(document.querySelectorAll('.pvrow')).map(r=>r.textContent.trim().replace(/\\s+/g,' ')).join(' | ')"""))
    print("   หลอด(ฝั่งล่าง=ขาว ยังนับขาว):", t.eval("document.getElementById('evaltxt').textContent"))
    print("   ป้ายบอก:", t.eval("document.getElementById('pvhint').textContent.trim()"))
    t.shot(D + r"\shot-v10.png")
