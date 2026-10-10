import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=201"); time.sleep(6)
    print("engine:", t.eval("document.getElementById('sub').textContent"))
    # เดิน 2 ตา แล้วทดสอบ N (เริ่มใหม่) + ยืนยัน/ยกเลิก
    for a,b in [("e2","e4"),("e7","e5")]:
        t.eval(f"document.querySelector('.sq[data-sq=\"{a}\"]').onclick(); 1"); time.sleep(0.3)
        t.eval(f"document.querySelector('.sq[data-sq=\"{b}\"]').onclick(); 1"); time.sleep(0.4)
    print("log:", t.eval("document.getElementById('log').textContent").strip())
    t.eval("document.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true})); 1"); time.sleep(0.5)
    print("กด N -> ยืนยันโชว์ไหม:", t.eval("getComputedStyle(document.getElementById('confirmNew')).display"))
    print("   บังกระดานไหม:", t.eval("""(function(){var c=document.getElementById('confirmNew').getBoundingClientRect();
        var b=document.getElementById('board').getBoundingClientRect();
        return c.top >= b.bottom ? 'ไม่บัง ✓ (อยู่ใต้กระดาน)' : 'บัง ✗';})()"""))
    t.eval("document.getElementById('bNewNo').onclick(); 1"); time.sleep(0.4)
    print("กดยกเลิก -> display:", t.eval("getComputedStyle(document.getElementById('confirmNew')).display"),
          "| log ยังอยู่:", t.eval("document.getElementById('log').textContent").strip())
    t.eval("document.getElementById('bNewGame').onclick(); 1"); time.sleep(0.3)
    t.eval("document.getElementById('bNewYes').onclick(); 1"); time.sleep(0.6)
    print("กดยืนยัน -> log:", t.eval("document.getElementById('log').textContent").strip())
    # F = กลับหัว, G = รัน
    f1 = t.eval("""document.querySelector('.sq').dataset.sq""")
    t.eval("document.dispatchEvent(new KeyboardEvent('keydown',{key:'f',bubbles:true})); 1"); time.sleep(0.4)
    f2 = t.eval("""document.querySelector('.sq').dataset.sq""")
    print("กด F -> ช่องแรก:", f1, "->", f2, "|", "ทำงาน ✓" if f1!=f2 else "ไม่ทำงาน ✗")
    t.eval("document.dispatchEvent(new KeyboardEvent('keydown',{key:'g',bubbles:true})); 1"); time.sleep(1.5)
    print("กด G -> ปุ่มรัน:", t.eval("document.getElementById('bRun').textContent.trim()"))
    t.shot(D + r"\shot-v35.png")
