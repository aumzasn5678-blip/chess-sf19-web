import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=18"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(9)
    print("A รัน -> ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| ลูกศร:", t.eval("document.querySelectorAll('#arrows line').length"),
          "| tgt:", t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq).join(',')"""))
    # แตะช่องเป้าหมาย -> เดินเอง + re-analyze อัตโนมัติ (โหมดรันค้าง)
    d1 = t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq)[0]""")
    g = t.eval(f"""(function(){{document.querySelector('.sq[data-sq="{d1}"]').onclick();
        return document.querySelectorAll('.ghost').length;}})()""")
    print("B แตะ", d1, "-> ghost(อนิเมชัน):", g, "| log:", t.eval("document.getElementById('log').textContent").strip(),
          "| ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"))
    time.sleep(10)
    print("C หลัง 10 วิ -> ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| ลูกศร:", t.eval("document.querySelectorAll('#arrows line').length"),
          "| แถว:", t.eval("document.querySelectorAll('.pvrow').length"),
          "| tgt:", t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq).join(',')"""))
    # กดหยุด -> ลูกศรต้องหาย
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(1.5)
    print("D กดหยุด -> ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| ลูกศร:", t.eval("document.querySelectorAll('#arrows line').length"), "(ควรเป็น 0)",
          "| tgt:", t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq).join(',')"""),
          "| หลอดยังอยู่:", t.eval("document.getElementById('evaltxt').textContent"))
    t.shot(D + r"\shot-v8.png")
