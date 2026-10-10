import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=27"); time.sleep(6)
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(10)
    print("แผงตัวเลือก (ต้องถูกซ่อน):", t.eval("document.getElementById('pv').offsetParent === null ? 'ซ่อนแล้ว ✓' : 'ยังโชว์ ✗'"))
    print("ช่องที่มีกรอบสี:", t.eval("""Array.from(document.querySelectorAll('.sq')).filter(e=>e.className.match(/tgt[123]/)).map(e=>e.dataset.sq+':'+e.className.match(/tgt[123]/)[0]).join(' | ')"""))
    print("ข้อความมุมขวาบนช่อง:", t.eval("""Array.from(document.querySelectorAll('.sqtag')).map(e=>e.textContent).join(' | ')"""))
    print("สีข้อความ/ตัวหนา:", t.eval("""(function(){const e=document.querySelector('.sqtag'); if(!e) return '-';
        const c=getComputedStyle(e); return c.color+' · weight '+c.fontWeight+' · '+c.fontSize;})()"""))
    print("ลูกศร: หนา", t.eval("""Array.from(document.querySelectorAll('#arrows line')).map(l=>l.getAttribute('stroke-width')).join(',')"""),
          "| รัศมี", t.eval("""Array.from(document.querySelectorAll('#arrows circle')).map(c=>c.getAttribute('r')).join(',')"""),
          "| ฟอนต์เลขในหัว", t.eval("""Array.from(document.querySelectorAll('#arrows text')).map(c=>c.getAttribute('font-size')+'/'+c.getAttribute('font-weight')).join(',')"""))
    t.shot(D + r"\shot-v14.png")
