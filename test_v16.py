import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=29"); time.sleep(6)
    t.eval("document.getElementById('fen').value='7k/8/8/8/8/8/5Q2/6K1 w - - 0 1'; document.getElementById('bSet').onclick(); 1")
    time.sleep(1)
    print("ปุ่มก่อนรัน:", t.eval("document.getElementById('bRun').textContent.trim()"))
    t.eval("document.getElementById('bRun').onclick(); 1")   # เปิดรัน
    time.sleep(12)
    print("ป้ายบนช่อง (กรณีรุกฆาต):", t.eval("""Array.from(document.querySelectorAll('.sqtag')).map(e=>e.textContent).join(' | ')"""))
    print("หลอด:", t.eval("document.getElementById('evaltxt').textContent"),
          "| ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| ลึก:", t.eval("document.getElementById('depthinfo').textContent"))
    t.shot(D + r"\shot-v16.png")
