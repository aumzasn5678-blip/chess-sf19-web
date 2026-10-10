import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp

D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8099/index.html")
    time.sleep(5)
    print("squares:", t.eval("document.querySelectorAll('.sq').length"))
    print("status :", t.eval("document.getElementById('status').textContent"))
    print("engine :", t.eval("document.getElementById('sub').textContent"))

    # --- โหมด 2 คน + เดินไปถึงจังหวะเข้าป้อม ---
    t.eval("document.getElementById('mode').value='2p'; document.getElementById('bNew').onclick(); 1")
    time.sleep(0.5)
    for a, b in [("e2","e4"),("e7","e5"),("g1","f3"),("b8","c6"),("f1","c4"),("f8","c5")]:
        t.eval(f'document.querySelector(\'.sq[data-sq="{a}"]\').onclick(); document.querySelector(\'.sq[data-sq="{b}"]\').onclick(); 1')
        time.sleep(0.25)
    print("\nmoves after 6:", t.eval("document.getElementById('moves').textContent"))
    dots = t.eval("""document.querySelector('.sq[data-sq="e1"]').onclick();
      Array.from(document.querySelectorAll('.sq')).filter(e=>e.classList.contains('mv')||e.classList.contains('cap')).map(e=>e.dataset.sq).join(',')""")
    print("แตะคิง e1 -> ช่องที่ไปได้:", dots)
    after = t.eval("""document.querySelector('.sq[data-sq="h1"]').onclick(); document.getElementById('moves').textContent""")
    print("แตะเรือ h1 -> moves:", after)
    print("เข้าป้อมสำเร็จ:", "O-O" in (after or ""))
    t.shot(D + r"\shot-2p.png")

    # --- โหมดเล่นกับ Stockfish ---
    t.eval("document.getElementById('mode').value='sf'; document.getElementById('side').value='w'; document.getElementById('bNew').onclick(); 1")
    time.sleep(5)
    print("\n[SF] engine:", t.eval("document.getElementById('sub').textContent"))
    t.eval('document.querySelector(\'.sq[data-sq="e2"]\').onclick(); document.querySelector(\'.sq[data-sq="e4"]\').onclick(); 1')
    time.sleep(8)
    print("[SF] moves:", t.eval("document.getElementById('moves').textContent"))
    print("[SF] status:", t.eval("document.getElementById('status').textContent"))
    print("[SF] engine:", t.eval("document.getElementById('sub').textContent"))
    t.shot(D + r"\shot-sf.png")
