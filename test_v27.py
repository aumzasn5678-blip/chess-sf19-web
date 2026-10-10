import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=121"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    print("ลำดับการวาด (ตัวหลัง = ทับตัวก่อน):")
    print("  เส้น   :", t.eval("""Array.from(document.querySelectorAll('#arrows line')).map(l=>l.getAttribute('stroke')).join(' -> ')"""))
    print("  วงกลม  :", t.eval("""Array.from(document.querySelectorAll('#arrows circle')).map(c=>c.getAttribute('fill')).join(' -> ')"""))
    print("  เลขในหัว:", t.eval("""Array.from(document.querySelectorAll('#arrows text')).map(c=>c.textContent).join(' -> ')"""))
    print("  notice  :", t.eval("(function(){var e=document.getElementById('notice');return e.className? e.className+' >> '+e.textContent:'(ไม่มี)';})()"))
    t.shot(D + r"\shot-v27.png")
