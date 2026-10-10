import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"

with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=16")
    time.sleep(6)
    print("engine:", t.eval("document.getElementById('sub').textContent"))
    t.eval("document.getElementById('bRun').onclick(); 1")
    time.sleep(9)
    print("[1] ปุ่มหลังกดรัน:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| status:", t.eval("document.getElementById('status').textContent"))
    print("    ช่องเป้าหมาย(แตะได้):", t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq).join(',')"""))

    # กดรันซ้ำ: ต้องไม่รีเซ็ตเป็น '▶ รัน' ทันที
    t.eval("document.getElementById('bRun').onclick(); 1")
    time.sleep(1)
    print("[2] กดรันซ้ำ 1 วิ -> ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"), "(ควรเป็น ■ หยุด)")
    time.sleep(9)
    print("    หลัง 9 วิ -> ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| status:", t.eval("document.getElementById('status').textContent"))

    # แตะช่องปลายทางที่แนะนำ = เดินเลย + มีอนิเมชัน
    dest = t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq)[0]""")
    res = t.eval(f"""(function(){{ document.querySelector('.sq[data-sq="{dest}"]').onclick();
        return JSON.stringify({{ghost: document.querySelectorAll('.ghost').length, log: document.getElementById('log').textContent.trim()}}); }})()""")
    print("\n[3] แตะช่องเป้าหมาย", dest, "->", res)
    time.sleep(0.6)
    print("    ghost หลังอนิเมชันจบ (ควรเหลือ 0):", t.eval("document.querySelectorAll('.ghost').length"))
    time.sleep(9)
    print("    หลัง 9 วิ — ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| status:", t.eval("document.getElementById('status').textContent"))
    print("    คำแนะนำชุดใหม่ (ของอีกฝ่าย):")
    print(t.eval("""Array.from(document.querySelectorAll('.pvrow')).map(r=>r.textContent.trim().replace(/\\s+/g,' ')).join('\\n')"""))
    print("    หลอด:", t.eval("document.getElementById('evaltxt').textContent"),
          "| ช่องเป้าหมายใหม่:", t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq).join(',')"""))
    t.shot(D + r"\shot-v6.png")
