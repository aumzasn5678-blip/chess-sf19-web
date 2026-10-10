import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=20"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(9)
    print("A เริ่ม (ตาขาว) ลูกศร:", t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq).join(',')"""))
    # เดิน d4 (แตะกรอบเป้าหมาย)
    d1 = t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq)[0]""")
    t.eval(f'document.querySelector(\'.sq[data-sq="{d1}"]\').onclick(); 1'); time.sleep(10)
    print("B เดิน", d1, "-> ลูกศร(ตาดำ):", t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq).join(',')"""))
    # กดย้อนกลับ
    t.eval("document.getElementById('bBack').onclick(); 1"); time.sleep(0.8)
    print("C กดย้อนกลับทันที -> ลูกศร:", t.eval("document.querySelectorAll('#arrows line').length"),
          "| log:", t.eval("document.getElementById('log').textContent").strip(),
          "| status:", t.eval("document.getElementById('status').textContent"))
    time.sleep(10)
    print("D หลัง 10 วิ -> ลูกศร:", t.eval("document.querySelectorAll('#arrows line').length"),
          "(ควรกลับมา 3) | tgt:", t.eval("""Array.from(document.querySelectorAll('.sq.tgt')).map(e=>e.dataset.sq).join(',')"""),
          "| status:", t.eval("document.getElementById('status').textContent"))
    # กดหยุด แล้วย้อนกลับอีกที -> ต้องไม่มีลูกศรค้าง
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(1)
    t.eval("document.getElementById('bFwd').onclick(); 1"); time.sleep(1)
    print("E หยุด+ไปข้างหน้า -> ลูกศร:", t.eval("document.querySelectorAll('#arrows line').length"), "(ควร 0)",
          "| ลูกศรค้างของเก่า:", t.eval("""document.querySelectorAll('.sq.tgt').length"""))
    t.shot(r"E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v9.png")
