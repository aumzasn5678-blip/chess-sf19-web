import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
JS_TAGS = "Array.from(document.querySelectorAll('.sqtag')).map(e=>e.textContent).join(' | ')"
def setfen(t, fen):
    t.eval("document.getElementById('fen').value='%s'; document.getElementById('bSet').onclick(); 1" % fen)
    time.sleep(1)
    if t.eval("document.getElementById('bRun').textContent.trim()") != "■ หยุด":
        t.eval("document.getElementById('bRun').onclick(); 1")
    time.sleep(12)

with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=31"); time.sleep(6)
    print("A) ขาวจะรุกฆาตใน 1 ตา (Qg7#) — ควรขึ้น +M1:")
    setfen(t, "7k/8/6K1/8/8/8/8/6Q1 w - - 0 1")
    print("   ป้าย:", t.eval(JS_TAGS), "| status:", t.eval("document.getElementById('status').textContent"))
    print("B) ดำเดิน แต่โดนบังคับรุกฆาต — คิงดำควรเรืองแสงแดง:")
    setfen(t, "k7/8/2K5/8/8/8/8/7Q b - - 0 1")
    print("   ป้าย:", t.eval(JS_TAGS))
    print("   status:", t.eval("document.getElementById('status').textContent"))
    print("   คิงที่เรืองแสง:", t.eval("""Array.from(document.querySelectorAll('.sq.warnk')).map(e=>e.dataset.sq).join(',') || '(ไม่มี)'"""))
    print("   toast:", t.eval("document.getElementById('toast').classList.contains('show') ? document.getElementById('toast').textContent : '(ไม่ขึ้น)'"))
    print("C) ตั้งตำแหน่งที่ติดรุกอยู่ (ควรเตือน 'ติดรุก'):")
    setfen(t, "7k/6Q1/6K1/8/8/8/8/8 w - - 0 1")
    print("   ป้าย:", t.eval(JS_TAGS), "| status:", t.eval("document.getElementById('status').textContent"))
    t.shot(r"E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v18.png")
