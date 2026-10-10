import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_NOTICE = "(function(){var e=document.getElementById('notice');return e.className? (e.className+' >> '+e.textContent) : '(ไม่มี)';})()"
JS_GLOW   = "Array.from(document.querySelectorAll('.sq.warnk')).map(e=>e.dataset.sq).join(',') || '(ไม่มี)'"
def run(t, fen, v, label):
    t.goto("http://127.0.0.1:8100/index.html?v=%d" % v); time.sleep(6)
    t.eval("document.getElementById('fen').value='%s'; document.getElementById('bSet').onclick(); 1" % fen)
    time.sleep(0.8)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(13)
    print("== %s" % label)
    print("   notice :", t.eval(JS_NOTICE))
    print("   ออร่า  :", t.eval(JS_GLOW))
with cdp.Tab() as t:
    run(t, "4r3/8/8/8/8/2B5/8/4K3 w - - 0 1", 61, "ขาวติดรุก (มีบิชอปมาบังได้)")
    run(t, "4r3/8/8/8/8/8/8/4K3 w - - 0 1", 62, "ขาวติดรุก (ไม่มีตัวบัง)")
    run(t, "7k/8/8/8/8/8/6q1/7K b - - 0 1", 63, "ฝั่งล่าง(ขาว)กำลังจะถูกรุกฆาต -> แดง")
    run(t, "k7/8/2K5/8/8/8/8/7Q b - - 0 1", 64, "ฝั่งล่าง(ขาว)ขึ้น M ได้ -> เขียว")
    run(t, "4k3/8/8/8/8/8/8/qq1K4 w - - 0 1", 65, "ขาวเสียเปรียบหนักมาก")
    t.shot(D + r"\shot-v21.png")
