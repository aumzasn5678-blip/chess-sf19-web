import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_TAGS = "Array.from(document.querySelectorAll('.sqtag')).map(e=>e.textContent).join(' | ')"
def fresh(t, fen, v):
    t.goto("http://127.0.0.1:8100/index.html?v=%d" % v); time.sleep(6)
    t.eval("document.getElementById('fen').value='%s'; document.getElementById('bSet').onclick(); 1" % fen)
    time.sleep(0.8)
    t.eval("document.getElementById('bRun').onclick(); 1")     # หน้าสด -> ปุ่มเป็น ▶ รัน แน่นอน
    time.sleep(13)

with cdp.Tab() as t:
    print("A) ขาวรุกฆาตใน 1-2 ตา:")
    fresh(t, "7k/8/6K1/8/8/8/8/6Q1 w - - 0 1", 41)
    print("   ป้าย:", t.eval(JS_TAGS), "| status:", t.eval("document.getElementById('status').textContent"))
    print("B) ดำเดินแต่โดนบังคับรุกฆาต (คิงดำควรเรืองแสง):")
    fresh(t, "k7/8/2K5/8/8/8/8/7Q b - - 0 1", 42)
    print("   ป้าย:", t.eval(JS_TAGS))
    print("   status:", t.eval("document.getElementById('status').textContent"))
    print("   คิงเรืองแสง:", t.eval("""Array.from(document.querySelectorAll('.sq.warnk')).map(e=>e.dataset.sq).join(',') || '(ไม่มี)'"""))
    print("   toast:", t.eval("document.getElementById('toast').classList.contains('show') ? document.getElementById('toast').textContent : '(ไม่ขึ้น)'"))
    print("C) ตำแหน่งที่ติดรุกอยู่ (ดำติดรุก, ขาวเดินไม่ได้เพราะ... ) ตั้งเป็นดำติดรุก:")
    fresh(t, "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1", 43)   # ดำติดรุก -> ควรขึ้นเตือน
    print("   ป้าย:", t.eval(JS_TAGS), "| status:", t.eval("document.getElementById('status').textContent"))
    print("   คิงเรืองแสง:", t.eval("""Array.from(document.querySelectorAll('.sq.warnk')).map(e=>e.dataset.sq).join(',') || '(ไม่มี)'"""))
    print("   toast:", t.eval("document.getElementById('toast').classList.contains('show') ? document.getElementById('toast').textContent : '(ไม่ขึ้น)'"))
    t.shot(D + r"\shot-v19.png")
