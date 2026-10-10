import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_NOTICE = "(function(){var e=document.getElementById('notice');return e.className? (e.className+' >> '+e.textContent) : '(ไม่มี)';})()"
JS_GLOW   = "Array.from(document.querySelectorAll('.sq.warnk')).map(e=>e.dataset.sq).join(',') || '(ไม่มี)'"
JS_BAR    = "document.getElementById('evalfill').style.width + ' @' + document.getElementById('evaltxt').textContent"
def run(t, fen, v, label):
    t.goto("http://127.0.0.1:8100/index.html?v=%d" % v); time.sleep(6)
    t.eval("document.getElementById('fen').value='%s'; document.getElementById('bSet').onclick(); 1" % fen)
    time.sleep(0.8)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(13)
    print("== %s\n   notice: %s\n   ออร่า : %s\n   หลอด : %s" % (label, t.eval(JS_NOTICE), t.eval(JS_GLOW), t.eval(JS_BAR)))
with cdp.Tab() as t:
    run(t, "4r1k1/8/8/8/8/8/8/4K3 w - - 0 1", 81, "ฝั่งล่าง(ขาว) ติดรุก -> ต้องมีกล่องแดง")
    run(t, "4k3/8/8/8/8/8/8/4RK2 b - - 0 1", 82, "ฝั่งบน(ดำ) ติดรุก -> ไม่มีกล่อง มีแค่ออร่า")
    t.shot(D + r"\shot-v23.png")
