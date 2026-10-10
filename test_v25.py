import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS = """Array.from(document.querySelectorAll('.sq')).filter(e=>e.querySelector('.sqtag'))
  .map(e=>e.dataset.sq+' -> '+Array.from(e.querySelectorAll('.sqtag')).map(t=>t.textContent+'('+t.className.replace(/sqtag ?/g,'')+',z'+t.style.zIndex+')').join(' & ')).join(' | ')"""
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=95"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    print("ช่อง+ป้าย:", t.eval(JS) or "(ไม่มี)")
    # ลองบังคับให้ 2 อันดับชนช่องเดียวกัน (จำลองด้วยการวาง FEN ที่มี 2 ตัวไปช่องเดียวได้)
    t.eval("document.getElementById('fen').value='6k1/8/8/8/8/8/8/R3K2R w KQ - 0 1'; document.getElementById('bSet').onclick(); 1")
    time.sleep(0.8)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    print("ช่อง+ป้าย (ตำแหน่งเรือคู่):", t.eval(JS) or "(ไม่มี)")
    t.shot(D + r"\shot-v25.png")
