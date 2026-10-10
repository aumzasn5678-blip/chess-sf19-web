import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=25"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    print("เส้นลำลูกศร:", t.eval("document.querySelectorAll('#arrows line').length"),
          "| วงกลมหัว:", t.eval("document.querySelectorAll('#arrows circle').length"),
          "| เลขในหัว:", t.eval("""Array.from(document.querySelectorAll('#arrows text')).map(e=>e.textContent).join('')"""))
    print("สีเส้น:", t.eval("""Array.from(document.querySelectorAll('#arrows line')).map(l=>l.getAttribute('stroke')).join(',')"""))
    print("สีวงกลม:", t.eval("""Array.from(document.querySelectorAll('#arrows circle')).map(c=>c.getAttribute('fill')).join(',')"""))
    print("สีเลข:", t.eval("""Array.from(document.querySelectorAll('#arrows text')).map(c=>c.getAttribute('fill')).join(',')"""))
    print("ความหนาเส้น:", t.eval("""Array.from(document.querySelectorAll('#arrows line')).map(l=>l.getAttribute('stroke-width')).join(',')"""),
          "(ต้องเท่ากันทุกเส้น)")
    print("รัศมีวงกลม:", t.eval("""Array.from(document.querySelectorAll('#arrows circle')).map(c=>c.getAttribute('r')).join(',')"""))
    t.shot(D + r"\shot-v12.png")
