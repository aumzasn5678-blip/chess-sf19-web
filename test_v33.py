import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=181"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    dest = t.eval("""Array.from(document.querySelectorAll('.sq')).filter(e=>e.querySelector('.sqtag')).map(e=>e.dataset.sq)[0]""")
    print("ช่องที่แนะนำ (แตะได้เลย):", t.eval("""Array.from(document.querySelectorAll('.sq')).filter(e=>e.querySelector('.sqtag')).map(e=>e.dataset.sq).join(',')"""))
    print("ก่อนแตะ log:", t.eval("document.getElementById('log').textContent").strip())
    t.eval(f"document.querySelector('.sq[data-sq=\"{dest}\"]').onclick(); 1")
    time.sleep(1.2)
    print("แตะ", dest, "(ไม่เลือกหมากก่อน) -> log:", t.eval("document.getElementById('log').textContent").strip())
    print("  มีการเดินจริง:", "✓" if t.eval("document.getElementById('log').textContent").strip() != "— ยังไม่มีการเดิน —" else "✗")
    t.shot(D + r"\shot-v33.png")
