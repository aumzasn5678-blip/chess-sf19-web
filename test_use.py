import sys, time, json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp

URL = sys.argv[1]
res = {}
with cdp.Tab(timeout=120) as t:
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=1, mobile=True)
    t.goto(URL, settle=3)
    t.eval("(() => { const x=document.getElementById('bEdit'); if(x) x.click(); return !!x; })()")
    time.sleep(1.2)
    # clear and build a position with black pieces
    t.eval("(() => { document.getElementById('editClear').click(); return true; })()")
    time.sleep(0.3)
    for piece, sq in [('bk','e8'),('bq','d8'),('bq','d5'),('br','a8'),('wk','e1'),('wp','e4')]:
        t.eval(f"(() => {{ document.querySelector('#editTray .traybtn[data-piece=\"{piece}\"]').click(); return true; }})()")
        time.sleep(0.2)
        t.eval(f"(() => {{ document.querySelector('#editBoard .sq[data-sq=\"{sq}\"]').click(); return true; }})()")
        time.sleep(0.2)
    res['edit_fen'] = t.eval("document.getElementById('editFen').value")
    # click "use this position"
    t.eval("(() => { document.getElementById('editUse').click(); return true; })()")
    time.sleep(1.0)
    res['edit_hidden'] = t.eval("!document.querySelector('#editView.show')")
    res['main_piece_imgs'] = t.eval("document.querySelectorAll('#board img.pcimg').length")
    res['main_black_imgs'] = t.eval("[...document.querySelectorAll('#board img.pcimg')].filter(i=>i.getAttribute('src').includes('_')).length")
    res['main_failed'] = t.eval("[...document.querySelectorAll('#board img')].filter(i=>i.naturalWidth===0).length")
    res['main_black_srcs'] = t.eval("JSON.stringify([...document.querySelectorAll('#board img.pcimg')].map(i=>i.getAttribute('src')).filter(s=>s.includes('_')))")
    # legend icon imgs loaded?
    res['legend_icons'] = t.eval("(() => { const a=[...document.querySelectorAll('img[src^=\"icons/\"]')]; return JSON.stringify({total:a.length, failed:a.filter(i=>i.naturalWidth===0).length}); })()")
print(json.dumps(res, ensure_ascii=False, indent=1))
