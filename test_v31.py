import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_TOAST = "document.getElementById('toast').classList.contains('show') ? document.getElementById('toast').textContent : '(ไม่ขึ้น)'"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=161"); time.sleep(6)
    # ตำแหน่งคล้ายในภาพ: 1.e4 e5 + ควีนดำ h5 (คิวขาวยังไม่ถูกเช็ค)
    t.eval("document.getElementById('fen').value='rnb1kbnr/pppp1ppp/8/4p2q/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2'; document.getElementById('bSet').onclick(); 1")
    time.sleep(0.8)
    t.eval("document.querySelector('.sq[data-sq=\"h5\"]').onclick(); 1"); time.sleep(0.8)
    print("แตะควีนดำ h5 (ตาขาว) ->", t.eval(JS_TOAST))
    print("  ตอนนี้ตา:", t.eval("document.getElementById('bTurn').textContent"),
          "| หมากที่เลือก:", t.eval("""(document.querySelector('.sq.sel')||{dataset:{}}).dataset.sq || '(ไม่มี)'"""))
    # ต่อด้วยการเดินจริงของควีนดำ h5->h2 (กินเบี้ย) ต้องเดินได้
    t.eval("document.querySelector('.sq[data-sq=\"h2\"]').onclick(); 1"); time.sleep(1)
    print("  เดิน h5->h2 (กินเบี้ย h2) -> log:", t.eval("document.getElementById('log').textContent").strip())
    t.shot(D + r"\shot-v31.png")
