import sys, time, json
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"

with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=15")
    time.sleep(6)
    print("engine:", t.eval("document.getElementById('sub').textContent"))
    t.eval("document.getElementById('bRun').onclick(); 1")
    time.sleep(9)
    print("\n[1] หลังกดรัน 9 วิ — ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| status:", t.eval("document.getElementById('status').textContent"))
    print("    แถว:", t.eval("document.querySelectorAll('.pvrow').length"),
          "| ช่องเป้าหมาย(แตะได้เลย):", t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq).join(',')"""))

    # กดรันซ้ำอีกครั้ง — ต้องไม่รีเซ็ตกลับเป็น 'กดรันใหม่' ทันที
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(4)
    print("\n[2] กดรันซ้ำ 4 วิ — ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| status:", t.eval("document.getElementById('status').textContent"))
    time.sleep(7)
    print("    อีก 7 วิ — ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| status:", t.eval("document.getElementById('status').textContent"))

    # แตะช่องปลายทางที่แนะนำ = เดินเลย ไม่ต้องเลือกหมากก่อน
    dest = t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq)[0]""")
    print("\n[3] แตะช่องเป้าหมาย:", dest)
    t.eval(f'document.querySelector(\'.sq[data-sq="{dest}"]\').onclick(); 1')
    time.sleep(2)
    print("    log:", t.eval("document.getElementById('log').textContent").strip())
    print("    ปุ่ม:", t.eval("document.getElementById('bRun').textContent.trim()"),
          "| status:", t.eval("document.getElementById('status').textContent"))
    time.sleep(8)
    print("    หลัง 8 วิ (ควรได้คำแนะนำชุดใหม่ของอีกฝ่าย):")
    print(t.eval("""Array.from(document.querySelectorAll('.pvrow')).map(r=>r.textContent.trim().replace(/\\s+/g,' ')).join('\\n')"""))
    print("    ทิศทาง: eval =", t.eval("document.getElementById('evaltxt').textContent"),
          "| ช่องเป้าหมายใหม่:", t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq).join(',')"""))
    t.shot(D + r"\shot-v5.png")
