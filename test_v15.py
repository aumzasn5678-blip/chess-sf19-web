import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=28"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    print("ป้ายบนช่อง:", t.eval("""Array.from(document.querySelectorAll('.sqtag')).map(e=>e.textContent).join(' | ')"""))
    print("คลาส/สีพื้นป้าย:", t.eval("""Array.from(document.querySelectorAll('.sqtag')).map(e=>e.className.replace('sqtag ','')+':'+getComputedStyle(e).backgroundColor).join(' | ')"""))
    print("สีตัวอักษร/หนา:", t.eval("""(function(){const e=document.querySelector('.sqtag');const c=getComputedStyle(e);return c.color+' · w'+c.fontWeight+' · '+c.fontSize;})()"""))
    t.shot(D + r"\shot-v15.png")
    # ทดสอบกรณีรุกฆาต (M) — ตั้ง FEN ควีน+คิง vs คิง
    t.eval("document.getElementById('fen').value='7k/8/8/8/8/8/5Q2/6K1 w - - 0 1'; document.getElementById('bSet').onclick(); 1")
    time.sleep(1)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    print("กรณีรุกฆาต -> ป้าย:", t.eval("""Array.from(document.querySelectorAll('.sqtag')).map(e=>e.textContent).join(' | ')"""))
    print("หลอด:", t.eval("document.getElementById('evaltxt').textContent"), "| status:", t.eval("document.getElementById('status').textContent"))
    t.shot(D + r"\shot-v16.png")
