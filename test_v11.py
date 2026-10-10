import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=24"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    print("ลูกศร:", t.eval("document.querySelectorAll('#arrows polygon').length"), "เส้น ·",
          "วงกลมหัว:", t.eval("document.querySelectorAll('#arrows circle').length"),
          "· เลขในหัว:", t.eval("""Array.from(document.querySelectorAll('#arrows text')).map(e=>e.textContent).join('')"""))
    print("สี polygon:", t.eval("""Array.from(document.querySelectorAll('#arrows polygon')).map(p=>p.getAttribute('fill')).join(',')"""))
    print("สีวงกลม:", t.eval("""Array.from(document.querySelectorAll('#arrows circle')).map(p=>p.getAttribute('fill')).join(',')"""))
    # วัดความกว้าง 'หาง' ของทั้ง 3 เส้น ว่ามีกี่หน่วย (เท่ากันไหม)
    print("ความกว้างส่วนหาง (หน่วย viewBox):", t.eval("""Array.from(document.querySelectorAll('#arrows polygon')).map(p=>{
        const a=p.getAttribute('points').trim().split(' ').map(s=>s.split(',').map(Number));
        const w=Math.hypot(a[0][0]-a[3][0], a[0][1]-a[3][1]);
        return w.toFixed(2);}).join(' | ')"""))
    print("ความกว้างตรงหัว:", t.eval("""Array.from(document.querySelectorAll('#arrows polygon')).map(p=>{
        const a=p.getAttribute('points').trim().split(' ').map(s=>s.split(',').map(Number));
        const w=Math.hypot(a[1][0]-a[2][0], a[1][1]-a[2][1]);
        return w.toFixed(2);}).join(' | ')"""))
    t.shot(D + r"\shot-v11.png")
