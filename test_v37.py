import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
def key(t, code, k):
    t.eval("document.dispatchEvent(new KeyboardEvent('keydown',{code:'%s',key:'%s',bubbles:true})); 1" % (code, k))
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=231"); time.sleep(6)
    print("1) คีย์บอร์ดด้วย e.code (เลย์เอาต์ไทยก็ต้องได้):")
    f1 = t.eval("document.querySelector('.sq').dataset.sq")
    key(t,'KeyF','ฟ'); time.sleep(0.4)
    print("   KeyF -> ช่องแรก:", f1, "->", t.eval("document.querySelector('.sq').dataset.sq"))
    key(t,'KeyN','น'); time.sleep(0.4)
    print("   KeyN -> confirm:", t.eval("getComputedStyle(document.getElementById('confirmNew')).display"))
    t.eval("document.getElementById('bNewNo').onclick(); 1"); time.sleep(0.3)
    key(t,'KeyG','เ'); time.sleep(1.5)
    print("   KeyG -> ปุ่มรัน:", t.eval("document.getElementById('bRun').textContent.trim()"))
    t.eval("if(document.getElementById('bRun').textContent.includes('หยุด')) document.getElementById('bRun').onclick(); 1")
    print("\n2) ปุ่มอนิเมชัน (กดเดียวสลับ):", t.eval("document.getElementById('animBtn').textContent"))
    t.eval("document.getElementById('animBtn').onclick(); 1"); time.sleep(0.3)
    print("   กด -> ", t.eval("document.getElementById('animBtn').textContent"), "| localStorage:", t.eval("localStorage.getItem('chessAnim')"))
    t.eval("document.getElementById('animBtn').onclick(); 1"); time.sleep(0.3)
    print("   กดอีก -> ", t.eval("document.getElementById('animBtn').textContent"))
    print("\n3) ล็อกตา (แตะหมากฝั่งตรงข้ามต้องไม่สลับตา):")
    t.eval("document.getElementById('bNew').click(); 1"); time.sleep(0.6)
    t.eval("document.querySelector('.sq[data-sq=\"e2\"]').onclick(); 1"); time.sleep(0.3)
    t.eval("document.querySelector('.sq[data-sq=\"e4\"]').onclick(); 1"); time.sleep(0.6)
    before = t.eval("document.getElementById('log').textContent").strip()
    t.eval("document.querySelector('.sq[data-sq=\"d2\"]').onclick(); 1"); time.sleep(0.6)
    print("   ก่อน/หลังแตะเบี้ยขาว(d2) ตอนตาดำ -> log:", before, "/", t.eval("document.getElementById('log').textContent").strip(),
          "| toast:", t.eval("document.getElementById('toast').classList.contains('show') ? document.getElementById('toast').textContent : '(ไม่ขึ้น ✓)'"))
    t.shot(D + r"\shot-v38.png")
