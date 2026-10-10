import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_TOAST = "document.getElementById('toast').classList.contains('show') ? document.getElementById('toast').textContent : '(ไม่ขึ้น)'"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=151"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    print("หลอดครึ่งซ้าย/ขวา:", t.eval("document.getElementById('evalhalf').style.background"))
    print("แถบสีฝั่งล่าง:", t.eval("document.getElementById('evalfill').style.background"),
          "| กว้าง :", t.eval("document.getElementById('evalfill').style.width"),
          "| เลข :", t.eval("document.getElementById('evaltxt').textContent"),
          "| เส้นกลาง :", t.eval("document.getElementById('evalmid').style.left + ' ' + getComputedStyle(document.getElementById('evalmid')).width"))
    # เลือกเบี้ย e2 แล้วแตะช่องที่ไปไม่ได้ (a5) -> ต้องไม่ขึ้นเตือนใด ๆ
    t.eval("document.querySelector('.sq[data-sq=\"e2\"]').onclick(); 1"); time.sleep(0.4)
    t.eval("document.querySelector('.sq[data-sq=\"a5\"]').onclick(); 1"); time.sleep(0.6)
    print("\nเลือก e2 แล้วแตะ a5 ->", t.eval(JS_TOAST), "(ต้องเป็น '(ไม่ขึ้น)')")
    t.shot(D + r"\shot-v30.png")
