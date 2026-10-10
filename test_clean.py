import sys, time, json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp

URL = sys.argv[1]
SHOT = sys.argv[2]

COLLECT = r"""(() => {
  const rows = [...document.querySelectorAll('img')].map(im => ({cls: im.className, src: im.getAttribute('src'), nw: im.naturalWidth}));
  const bad = rows.filter(r => r.nw === 0);
  const eb = [...document.querySelectorAll('#editBoard img')];
  const tr = [...document.querySelectorAll('#editTray img')];
  return JSON.stringify({total: rows.length, failed: bad.length, bad,
    editBoardImgs: eb.length, editBoardBad: eb.filter(i=>i.naturalWidth===0).length,
    trayImgs: tr.length, trayBad: tr.filter(i=>i.naturalWidth===0).length,
    editShown: !!document.querySelector('#editView.show')});
})()"""

res = {}
with cdp.Tab() as t:
    t.cmd("Network.setCacheDisabled", cacheDisabled=True)
    t.goto(URL, settle=2)
    # purge SW + caches
    t.eval("navigator.serviceWorker.getRegistrations().then(rs=>Promise.all(rs.map(r=>r.unregister())))", await_promise=True)
    t.eval("caches.keys().then(ks=>Promise.all(ks.map(k=>caches.delete(k))))", await_promise=True)
    time.sleep(1)
    # hard reload
    t.goto(URL, settle=4)
    b = json.loads(t.eval(COLLECT))
    res['base'] = {k:b[k] for k in ('total','failed')}
    res['base_bad'] = b['bad']

    t.eval("(() => { const x=document.getElementById('bEdit'); if(x) x.click(); return !!x; })()")
    time.sleep(1.5)
    e = json.loads(t.eval(COLLECT))
    res['edit'] = {k:e[k] for k in ('total','failed','editBoardImgs','editBoardBad','trayImgs','trayBad')}
    res['edit_bad'] = e['bad']

    # sw state
    res['sw_controlled'] = t.eval("!!navigator.serviceWorker.controller")
    res['sw_regs'] = t.eval("navigator.serviceWorker.getRegistrations().then(rs=>rs.length)", await_promise=True)

    try:
        t.shot(SHOT); res['shot'] = SHOT
    except Exception as ex:
        res['shot_err'] = str(ex)[:120]

print(json.dumps(res, ensure_ascii=False, indent=1))
