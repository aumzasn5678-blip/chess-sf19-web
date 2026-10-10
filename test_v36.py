import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=211"); time.sleep(6)
    print("engine:", t.eval("document.getElementById('sub').textContent"), "(แสดงว่าไม่มี error ตอนโหลด)")
    # วิเคราะห์ -> แตะช่องที่แนะนำให้ 'กิน' โดยไม่เลือกหมากก่อน ต้องเดินได้ ไม่สลับฝั่ง
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    print("ch่องแนะนำ:", t.eval("""Array.from(document.querySelectorAll('.sq')).filter(e=>e.querySelector('.sqtag')).map(e=>e.dataset.sq).join(',')"""))
    dest = t.eval("""Array.from(document.querySelectorAll('.sq')).filter(e=>e.querySelector('.sqtag')).map(e=>e.dataset.sq)[0]""")
    t.eval(f"document.querySelector('.sq[data-sq=\"{dest}\"]').onclick(); 1"); time.sleep(1.2)
    print("แตะช่องแนะนำ", dest, "-> log:", t.eval("document.getElementById('log').textContent").strip())
    print("   toast:", t.eval("document.getElementById('toast').classList.contains('show') ? document.getElementById('toast').textContent : '(ไม่ขึ้น — ถูกต้อง)'"))
    # ปุ่ม/คีย์
    print("\nสีปุ่ม รัน:", t.eval("getComputedStyle(document.getElementById('bRun')).backgroundColor"),
          "| ย้อน:", t.eval("getComputedStyle(document.getElementById('bBack')).backgroundColor"),
          "| เริ่มใหม่:", t.eval("getComputedStyle(document.getElementById('bNewGame')).backgroundColor"))
    print("สวิตช์อนิเมชัน:", t.eval("document.getElementById('animSel').value"))
    t.eval("const s=document.getElementById('animSel'); s.value='0'; s.dispatchEvent(new Event('change')); 1"); time.sleep(0.3)
    print("ปิดอนิเมชัน -> ค่า:", t.eval("document.getElementById('animSel').value"), "| เก็บใน localStorage:", t.eval("localStorage.getItem('chessAnim')"))
    t.eval("const s=document.getElementById('animSel'); s.value='1'; s.dispatchEvent(new Event('change')); 1"); time.sleep(0.3)
    t.eval("document.dispatchEvent(new KeyboardEvent('keydown',{key:'f',bubbles:true})); 1"); time.sleep(0.4)
    print("กด F (กลับหัว):", t.eval("""document.querySelector('.sq').dataset.sq"""))
    t.eval("document.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true})); 1"); time.sleep(0.4)
    print("กด N (เริ่มใหม่):", t.eval("getComputedStyle(document.getElementById('confirmNew')).display"))
    t.eval("document.getElementById('bNewNo').onclick(); 1")
    t.shot(D + r"\shot-v36.png")
