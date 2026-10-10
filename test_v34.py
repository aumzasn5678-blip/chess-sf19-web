import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=191"); time.sleep(6)
    print("หลอดความลึก --p =", t.eval("document.getElementById('depth').style.getPropertyValue('--p')"),
          "| ป้าย:", t.eval("document.getElementById('depthv').textContent"))
    t.eval("const s=document.getElementById('depth'); s.value=8; s.dispatchEvent(new Event('input')); 1"); time.sleep(0.4)
    print("ลากเป็น 8   --p =", t.eval("document.getElementById('depth').style.getPropertyValue('--p')"),
          "| ป้าย:", t.eval("document.getElementById('depthv').textContent"))
    # ทดสอบคีย์บอร์ด: เดิน 2 ตา แล้วกดลูกศรซ้าย
    for a,b in [("e2","e4"),("e7","e5")]:
        t.eval(f"document.querySelector('.sq[data-sq=\"{a}\"]').onclick(); 1"); time.sleep(0.3)
        t.eval(f"document.querySelector('.sq[data-sq=\"{b}\"]').onclick(); 1"); time.sleep(0.4)
    print("\nlog ก่อนกดลูกศร:", t.eval("document.getElementById('log').textContent").strip())
    t.eval("document.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true})); 1"); time.sleep(0.6)
    print("กด ← :", t.eval("document.getElementById('log').textContent").strip())
    t.eval("document.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true})); 1"); time.sleep(0.6)
    print("กด → :", t.eval("document.getElementById('log').textContent").strip())
    t.shot(D + r"\shot-v34.png")
