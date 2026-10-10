import sys, time, json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
URL = 'http://127.0.0.1:8100/index.html'
res = {}
def sq(t,s):
    t.eval(f"(() => {{ const e=document.querySelector('#board .sq[data-sq=\"{s}\"]'); if(e) e.click(); return true; }})()")
with cdp.Tab(timeout=180) as t:
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=1, mobile=True)
    t.goto(URL, settle=3)
    t.eval("(() => { try{localStorage.clear();}catch(e){} return true; })()")
    t.goto(URL, settle=3)
    sq(t,'e2'); time.sleep(0.3); sq(t,'e4'); time.sleep(3)
    sq(t,'e7'); time.sleep(0.3); sq(t,'e5'); time.sleep(3)
    sq(t,'g1'); time.sleep(0.3); sq(t,'f3'); time.sleep(4)
    res['g390'] = json.loads(t.eval("(() => JSON.stringify([...document.querySelectorAll('#board .gradico')].map(e=>e.parentElement.dataset.sq)))()"))
    res['overflow'] = t.eval("(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)()")
    res['shot1'] = t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-142-390-grades.png')
    # theme toggle
    res['theme_ok'] = t.eval("(() => { const b=document.getElementById('bTheme'); b.click(); return document.documentElement.getAttribute('data-theme')||'x'; })()")
    # EDIT open/close
    t.eval("(() => { document.getElementById('bEdit').click(); return true; })()")
    time.sleep(0.8)
    res['edit_open'] = t.eval("(() => !!document.querySelector('#editView.show'))()")
    res['edit_overflow'] = t.eval("(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)()")
    res['shot2'] = t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-142-390-edit.png')
print(json.dumps(res, ensure_ascii=False, indent=1))
