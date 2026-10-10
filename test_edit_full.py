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
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.goto(URL, settle=3)

    b = json.loads(t.eval(COLLECT))
    res['base'] = {k:b[k] for k in ('total','failed','editBoardImgs','trayImgs')}
    res['base_bad'] = b['bad']

    # open EDIT
    t.eval("(() => { const x=document.getElementById('bEdit'); if(x) x.click(); return !!x; })()")
    time.sleep(1.5)
    e = json.loads(t.eval(COLLECT))
    res['edit'] = {k:e[k] for k in ('total','failed','editBoardImgs','editBoardBad','trayImgs','trayBad','editShown')}
    res['edit_bad'] = e['bad']

    # place a BLACK queen on d4
    t.eval("(() => { const b=document.querySelector('#editTray .traybtn[data-piece=\"bq\"]'); if(b) b.click(); return !!b; })()")
    time.sleep(0.4)
    t.eval("(() => { const s=document.querySelector('#editBoard .sq[data-sq=\"d4\"]'); if(s) s.click(); return !!s; })()")
    time.sleep(0.4)
    res['after_place_black_q_d4'] = t.eval("(() => { const s=document.querySelector('#editBoard .sq[data-sq=\"d4\"] img'); return JSON.stringify({src: s&&s.getAttribute('src'), nw: s&&s.naturalWidth}); })()")

    # place a WHITE knight on e5
    t.eval("(() => { const b=document.querySelector('#editTray .traybtn[data-piece=\"wn\"]'); if(b) b.click(); return !!b; })()")
    time.sleep(0.3)
    t.eval("(() => { const s=document.querySelector('#editBoard .sq[data-sq=\"e5\"]'); if(s) s.click(); return !!s; })()")
    time.sleep(0.4)
    res['after_place_white_n_e5'] = t.eval("(() => { const s=document.querySelector('#editBoard .sq[data-sq=\"e5\"] img'); return JSON.stringify({src: s&&s.getAttribute('src'), nw: s&&s.naturalWidth}); })()")
    res['fen_after_place'] = t.eval("document.getElementById('editFen').value")

    # choose eraser, delete d4
    t.eval("(() => { const b=document.querySelector('#editTray .traybtn.erase'); if(b) b.click(); return !!b; })()")
    time.sleep(0.3)
    t.eval("(() => { const s=document.querySelector('#editBoard .sq[data-sq=\"d4\"]'); if(s) s.click(); return !!s; })()")
    time.sleep(0.4)
    res['d4_after_erase_has_img'] = t.eval("!!document.querySelector('#editBoard .sq[data-sq=\"d4\"] img')")

    try:
        t.shot(SHOT); res['shot'] = SHOT
    except Exception as ex:
        res['shot_err'] = str(ex)[:120]
    print("PARTIAL:", json.dumps(res, ensure_ascii=False))

    # clear board
    t.eval("(() => { const b=document.getElementById('editClear'); if(b) b.click(); return !!b; })()")
    time.sleep(0.4)
    res['board_after_clear'] = t.eval("document.querySelectorAll('#editBoard img').length")

    # back out then reopen and use position
    t.eval("(() => { const b=document.getElementById('editBack'); if(b) b.click(); return !!b; })()")
    time.sleep(0.3)
    res['edit_hidden_after_back'] = t.eval("!document.querySelector('#editView.show')")

print(json.dumps(res, ensure_ascii=False, indent=1))
