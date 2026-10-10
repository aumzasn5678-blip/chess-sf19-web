import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
def tap(t, sq): t.eval(f'document.querySelector(\'.sq[data-sq="{sq}"]\').onclick(); 1')

with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=14")
    time.sleep(6)
    print("engine :", t.eval("document.getElementById('sub').textContent"))
    print("ปุ่ม    :", t.eval("""['bRun','bBack','bFwd','bFlip','bTurn'].map(i=>document.getElementById(i).textContent.trim()).join(' | ')"""))
    print("สไลเดอร์:", t.eval("document.getElementById('depth').type + ' min=' + document.getElementById('depth').min + ' max=' + document.getElementById('depth').max + ' now=' + document.getElementById('depth').value + ' | ' + document.getElementById('depthv').textContent"))
    print("ปุ่มตัวเลือก:", t.eval("""Array.from(document.querySelectorAll('.npv')).map(b=>b.dataset.npv+(b.classList.contains('on')?'*':'')).join(' ')"""))

    # ปรับความลึก = 14 -> เวลาควรเป็น ≈7.8วิ
    t.eval("const s=document.getElementById('depth'); s.value=14; s.dispatchEvent(new Event('input')); 1")
    time.sleep(0.4)
    print("หลังลากเป็น 14:", t.eval("document.getElementById('depthv').textContent"))

    # เลือก 2 ตัวเลือก
    t.eval("document.querySelector('.npv[data-npv=\"2\"]').onclick(); 1"); time.sleep(0.4)
    print("หลังกด 2:", t.eval("""Array.from(document.querySelectorAll('.npv')).map(b=>b.dataset.npv+(b.classList.contains('on')?'*':'')).join(' ')"""))

    for a,b in [("e2","e4"),("e7","e5")]:
        tap(t,a); time.sleep(0.25); tap(t,b); time.sleep(0.4)
    print("\nlog:", t.eval("document.getElementById('log').textContent").strip(), "| ตา:", t.eval("document.getElementById('bTurn').textContent"))

    t.eval("document.getElementById('bRun').onclick(); 1")
    time.sleep(12)
    print("แถวคำแนะนำ (ควรได้ 2 แถว):")
    print(t.eval("""Array.from(document.querySelectorAll('.pvrow')).map(r=>r.textContent.trim().replace(/\\s+/g,' ')).join('\\n')"""))
    print("หลอด:", t.eval("document.getElementById('evaltxt').textContent"),
          "| ป้ายซ้าย/ขวา:", t.eval("document.getElementById('evaltag').textContent+' / '+document.getElementById('evaltagr').textContent"))
    print("status:", t.eval("document.getElementById('status').textContent"))

    # ย้อน/ไปข้างหน้า
    t.eval("document.getElementById('bBack').onclick(); 1"); time.sleep(0.4)
    print("\nย้อนกลับ ->", repr(t.eval("document.getElementById('log').textContent").strip()))
    t.eval("document.getElementById('bFwd').onclick(); 1"); time.sleep(0.4)
    print("ไปข้างหน้า ->", repr(t.eval("document.getElementById('log').textContent").strip()))

    # กลับหัว -> หลอดสลับซ้ายขวา + เลือก 3 ตัวเลือกคืน
    t.eval("document.querySelector('.npv[data-npv=\"3\"]').onclick(); 1")
    t.eval("document.getElementById('bFlip').onclick(); 1"); time.sleep(0.5)
    print("\nกลับหัว -> หลอด:", t.eval("document.getElementById('evalhalf').style.background").replace('linear-gradient(to right, ','').replace(')',''))
    print("ป้าย:", t.eval("document.getElementById('evaltag').textContent+' / '+document.getElementById('evaltagr').textContent"))
    t.shot(D + r"\shot-v4.png")
