import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_N = "(function(){var e=document.getElementById('notice');return e.className? (e.className+' >> '+e.textContent) : '(ไม่มี)';})()"
def run(t, fen, v, label):
    t.goto("http://127.0.0.1:8100/index.html?v=%d" % v); time.sleep(6)
    t.eval("document.getElementById('fen').value='%s'; document.getElementById('bSet').onclick(); 1" % fen)
    time.sleep(0.8)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(12)
    print("== %s\n   %s" % (label, t.eval(JS_N)))
with cdp.Tab() as t:
    run(t, "4k3/8/8/8/8/8/8/qq1K4 w - - 0 1", 101, "ฝั่งเราเสียเปรียบมาก/ใกล้โดน M -> ควรเป็นกรอบเทา แนะนำยอมแพ้")
    run(t, "4r1k1/8/8/8/8/2B5/8/4K3 w - - 0 1", 102, "ฝั่งเราติดรุก(บังได้) -> ยังต้องเป็นกรอบเหลือง")
    t.shot(D + r"\shot-v26.png")
