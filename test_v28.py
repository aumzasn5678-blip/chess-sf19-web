import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_T = "Array.from(document.querySelectorAll('.sqtag')).map(e=>e.textContent+'@'+e.parentElement.dataset.sq).join(' ')"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=131"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    print("1) หลังวิเคราะห์   :", t.eval(JS_T))
    t.eval("document.querySelector('.sq[data-sq=\"a5\"]').onclick(); 1"); time.sleep(0.5)   # กดช่องอื่น
    print("2) กดช่องอื่น(a5)  :", t.eval(JS_T))
    t.eval("document.querySelector('.sq[data-sq=\"a5\"]').onclick(); 1"); time.sleep(0.5)
    print("3) กดซ้ำอีกที      :", t.eval(JS_T))
    t.eval("document.querySelector('.sq[data-sq=\"e2\"]').onclick(); 1"); time.sleep(0.5)    # เลือกหมาก
    print("4) เลือกหมาก(e2)   :", t.eval(JS_T))
    t.eval("document.getElementById('bFlip').onclick(); 1"); time.sleep(0.5)
    print("5) กดกลับหัว       :", t.eval(JS_T))
    t.eval("document.getElementById('bFlip').onclick(); 1"); time.sleep(0.3)
    print("   กดกลับคืน      :", t.eval(JS_T))
    t.shot(D + r"\shot-v28.png")
