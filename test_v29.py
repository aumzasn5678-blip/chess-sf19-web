import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_TOAST = "document.getElementById('toast').classList.contains('show') ? document.getElementById('toast').textContent : '(ไม่ขึ้น)'"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=141"); time.sleep(6)
    # หมากถูกตรึง: ขาว Ke1 + N e2 + เรือดำ e8 (อัศวินขยับไม่ได้เพราะคิงจะถูกรุก)
    t.eval("document.getElementById('fen').value='4r1k1/8/8/8/8/8/4N3/4K3 w - - 0 1'; document.getElementById('bSet').onclick(); 1")
    time.sleep(0.8)
    t.eval("document.querySelector('.sq[data-sq=\"e2\"]').onclick(); 1"); time.sleep(0.6)
    print("แตะหมากที่ถูกตรึง (e2, ฝั่งเรา) ->", t.eval(JS_TOAST))
    # ตรวจว่าหมากที่เดินได้ปกติไม่ขึ้นเตือน (เบี้ย c2 ของขาว)
    t.eval("document.getElementById('fen').value='4r1k1/8/8/8/8/8/4N3/2P1K3 w - - 0 1'; document.getElementById('bSet').onclick(); 1")
    time.sleep(0.8)
    t.eval("document.querySelector('.sq[data-sq=\"c2\"]').onclick(); 1"); time.sleep(0.6)
    print("แตะเบี้ยที่เดินได้ (c2) ->", t.eval(JS_TOAST), "(ควรไม่ขึ้นเตือน / เป็นการเลือกหมาก)")
    t.shot(D + r"\shot-v29.png")
