import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_N = "(function(){var e=document.getElementById('notice');return e.className? (e.className+' >> '+e.textContent) : '(ไม่มี)';})()"
JS_A = "Array.from(document.querySelectorAll('.sq')).filter(e=>e.className.match(/warn[ky]/)).map(e=>e.dataset.sq+':'+e.className.match(/warn[ky]/)[0]).join(', ') || '(ไม่มี)'"
def run(t, fen, v, label):
    t.goto("http://127.0.0.1:8100/index.html?v=%d" % v); time.sleep(6)
    t.eval("document.getElementById('fen').value='%s'; document.getElementById('bSet').onclick(); 1" % fen)
    time.sleep(0.8)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(13)
    print("== %s\n   notice: %s\n   ออร่า : %s" % (label, t.eval(JS_N), t.eval(JS_A)))
with cdp.Tab() as t:
    run(t, "4r1k1/8/8/8/8/2B5/8/4K3 w - - 0 1", 91, "ฝั่งเรา(ขาว)ติดรุก — บังได้ -> เหลือง")
    run(t, "4r1k1/8/8/8/8/8/8/4K3 w - - 0 1", 92, "ฝั่งเรา(ขาว)ติดรุก — บังไม่ได้ -> แดง")
    run(t, "4k3/8/8/8/8/8/8/4RK2 b - - 0 1", 93, "ฝั่งบน(ดำ)ติดรุก -> ไม่มีกล่อง, มีแต่ออร่า")
    t.shot(D + r"\shot-v24.png")
