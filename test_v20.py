import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_NOTICE = "(function(){var e=document.getElementById('notice');return e.className? (e.className+': '+e.textContent) : '(ไม่มี)';})()"
JS_GLOW   = "Array.from(document.querySelectorAll('.sq.warnk')).map(e=>e.dataset.sq).join(',') || '(ไม่มี)'"
def run(t, fen, v, label):
    t.goto("http://127.0.0.1:8100/index.html?v=%d" % v); time.sleep(6)
    t.eval("document.getElementById('fen').value='%s'; document.getElementById('bSet').onclick(); 1" % fen)
    time.sleep(0.8)
    t.eval("document.getElementById('bRun').onclick(); 1")
    time.sleep(13)
    print("== %s" % label)
    print("   กระดาน(ล่าง):", t.eval("document.getElementById('evaltag').textContent"))
    print("   notice:", t.eval(JS_NOTICE))
    print("   คิงเรืองแสง:", t.eval(JS_GLOW))
with cdp.Tab() as t:
    # 1) เราถูก M -> แดง
    run(t, "k7/8/2K5/8/8/8/8/7Q b - - 0 1", 51, "ฝั่งล่าง(ขาว)เป็นฝ่ายได้เปรียบM? -> ต้องดูว่าล่างคือขาว")
    # 2) ติดรุกแบบไม่มีตัวบัง (คิงต้องหนี)
    run(t, "6k1/5ppp/8/8/8/8/8/R3K2R w - - 0 1", 52, "ปกติ (ไม่ติดรุก)")
    run(t, "4k3/8/8/8/8/8/8/R3K2R w - - 0 1", 53, "ขาวเดิน (ไม่ติดรุก)")
    run(t, "4k3/8/8/8/8/8/4r3/R3K2R w - - 0 1", 54, "ขาวติดรุกจากเรือดำ e2 (มีเรือ a1 มาบัง e1? ไม่ได้ ต้องหนี/กิน)")
    # 3) เสียเปรียบเยอะ (ไม่ M)
    run(t, "4k3/8/8/8/8/8/8/qq1K4 w - - 0 1", 55, "ขาวเสียเปรียบหนัก")
    t.shot(D + r"\shot-v20.png")
