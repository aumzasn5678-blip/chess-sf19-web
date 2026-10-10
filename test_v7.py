import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=17"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1")   # กดรัน (ไม่กดปิด)
    time.sleep(9)
    print("A ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| status:", t.eval("document.getElementById('status').textContent"))
    dest = t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq)[0]""")
    t.eval(f'document.querySelector(\'.sq[data-sq="{dest}"]\').onclick(); 1')
    time.sleep(1)
    print("B หลังแตะ", dest, "-> ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| status:", t.eval("document.getElementById('status').textContent"),
          "| log:", t.eval("document.getElementById('log').textContent").strip())
    time.sleep(10)
    print("C หลัง 10 วิ -> ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| status:", t.eval("document.getElementById('status').textContent"))
    print("   คำแนะนำชุดใหม่:")
    print(t.eval("""Array.from(document.querySelectorAll('.pvrow')).map(r=>r.textContent.trim().replace(/\\s+/g,' ')).join('\\n')"""))
    print("   หลอด:", t.eval("document.getElementById('evaltxt').textContent"),
          "| tgt:", t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq).join(',')"""))
    t.shot(r"E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v7.png")
