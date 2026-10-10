import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_DEPTH = "document.getElementById('depthinfo').textContent"
JS_ROW1  = "(document.querySelector('.pvrow .mv')||{}).textContent||'-'"
JS_ARROWS= "document.querySelectorAll('#arrows line').length"

with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=26"); time.sleep(6)
    t.eval("const s=document.getElementById('depth'); s.value=20; s.dispatchEvent(new Event('input')); 1")
    time.sleep(0.4)
    print("ตั้งความลึก 20 · ป้าย:", t.eval(JS_DEPTH))
    t.eval("document.getElementById('bRun').onclick(); 1")
    for i in range(6):
        time.sleep(1.6)
        print("  t+%.1fs | %r | แถว1: %s | ลูกศร: %s" % (
            1.6*(i+1), t.eval(JS_DEPTH), t.eval(JS_ROW1), t.eval(JS_ARROWS)))
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(1)
    print("กดหยุด -> ป้าย:", t.eval(JS_DEPTH), "| ลูกศร:", t.eval(JS_ARROWS))
    t.shot(D + r"\shot-v13.png")
