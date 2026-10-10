import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_OVER = "(function(){var o=document.getElementById('bigover');return o.classList.contains('show') ? (document.getElementById('bigbox').className+' >> '+document.getElementById('bigbox').textContent.trim()) : '(ไม่เด้ง)';})()"
def run(t, fen, v, label):
    t.goto("http://127.0.0.1:8100/index.html?v=%d" % v); time.sleep(6)
    t.eval("document.getElementById('fen').value='%s'; document.getElementById('bSet').onclick(); 1" % fen)
    time.sleep(1.2)
    print("== %s\n   %s" % (label, t.eval(JS_OVER)))
with cdp.Tab() as t:
    run(t, "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3", 171, "ฝั่งล่าง(ขาว) ถูกรุกฆาต -> ต้องเด้ง แพ้แล้ว")
    t.eval("document.getElementById('bigover').onclick(); 1"); time.sleep(0.4)
    print("   แตะปิด ->", t.eval(JS_OVER))
    run(t, "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4", 172, "ฝั่งบน(ดำ) ถูกรุกฆาต -> ต้องเด้ง ชนะแล้ว")
    t.shot(D + r"\shot-v32.png")
