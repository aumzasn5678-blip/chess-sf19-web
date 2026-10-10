import sys, time
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
D = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
JS_TAGS = "Array.from(document.querySelectorAll('.sqtag')).map(e=>e.textContent).join(' | ')"
JS_TOAST= "document.getElementById('toast').classList.contains('show') ? document.getElementById('toast').textContent : '(ไม่ขึ้น)'"

with cdp.Tab() as t:
    t.goto("http://127.0.0.1:8100/index.html?v=30"); time.sleep(6)
    # 1) โหมดปกติ: ป้าย = แค่คะแนน + กล่องสี
    t.eval("document.getElementById('bRun').onclick(); 1"); time.sleep(9)
    print("1) ป้ายบนช่อง:", t.eval(JS_TAGS))
    print("   กล่องสี:", t.eval("""Array.from(document.querySelectorAll('.sqtag')).map(e=>e.className.replace('sqtag ','')).join(',')"""))
    # 2) เดินผิดกติกา -> toast
    t.eval("const s=document.getElementById('depth'); s.value=12; s.dispatchEvent(new Event('input')); 1")
    t.eval("document.querySelector('.sq[data-sq=\"e2\"]').onclick(); 1"); time.sleep(0.3)
    t.eval("document.querySelector('.sq[data-sq=\"e5\"]').onclick(); 1"); time.sleep(0.4)
    print("\n2) เดินผิดกติกา -> toast:", t.eval(JS_TOAST))
    # แตะหมากฝั่งที่ยังไม่ถึงตา
    t.eval("document.querySelector('.sq[data-sq=\"e7\"]').onclick(); 1"); time.sleep(0.4)
    print("   แตะหมากฝั่งตรงข้าม -> toast:", t.eval(JS_TOAST))
    # 3) กรณีถูกรุกฆาต: ดำเดิน แต่โดนบังคับรุกฆาต
    t.eval("document.getElementById('fen').value='7k/8/8/8/8/8/5Q2/6K1 b - - 0 1'; document.getElementById('bSet').onclick(); 1")
    time.sleep(1)
    if t.eval("document.getElementById('bRun').textContent.trim()") != "■ หยุด":
        t.eval("document.getElementById('bRun').onclick(); 1")
    time.sleep(12)
    print("\n3) กรณีดำถูกรุกฆาต:")
    print("   ป้าย (ควรเป็น +M..):", t.eval(JS_TAGS))
    print("   คิงดำ (h8) เรืองแสง:", t.eval("""(document.querySelector('.sq[data-sq="h8"]').className.match(/warnk/)?'มี warnk ✓':'ไม่มี ✗') + ' | ชั้น: '+document.querySelector('.sq[data-sq="h8"]').className"""))
    print("   status:", t.eval("document.getElementById('status').textContent"))
    print("   toast:", t.eval(JS_TOAST))
    t.shot(D + r"\shot-v17.png")
