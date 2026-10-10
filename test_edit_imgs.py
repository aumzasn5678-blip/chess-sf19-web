import sys, time, json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8100/index.html"
SHOT = sys.argv[2] if len(sys.argv) > 2 else "shot-edit-test.png"

COLLECT = r"""(() => {
  const imgs = [...document.querySelectorAll('img')];
  const rows = imgs.map(im => ({cls: im.className, src: im.getAttribute('src'), nw: im.naturalWidth, w: im.width}));
  const inEditBoard = [...document.querySelectorAll('#editBoard img')];
  const inTray = [...document.querySelectorAll('#editTray img')];
  const bad = rows.filter(r => r.nw === 0);
  return JSON.stringify({
    total: rows.length,
    failed: bad.length,
    bad: bad,
    editBoardImgs: inEditBoard.length,
    editBoardBad: inEditBoard.filter(i=>i.naturalWidth===0).length,
    trayImgs: inTray.length,
    trayBad: inTray.filter(i=>i.naturalWidth===0).length,
    editShown: !!document.querySelector('#editView.show'),
    all: rows
  });
})()"""

with cdp.Tab() as t:
    t.goto(URL, settle=3)
    # list 404 resources
    time.sleep(1)
    base = json.loads(t.eval(COLLECT))
    print("=== BASE (analysis mode) ===")
    print(json.dumps({k: base[k] for k in ('total','failed','editBoardImgs','editBoardBad','trayImgs','trayBad','editShown')}, ensure_ascii=False))
    print("bad base:", json.dumps(base['bad'], ensure_ascii=False))

    # open EDIT
    t.eval("(() => { const b=document.getElementById('bEdit'); if(b) b.click(); return !!b; })()")
    time.sleep(1.5)
    ed = json.loads(t.eval(COLLECT))
    print("=== EDIT mode ===")
    print(json.dumps({k: ed[k] for k in ('total','failed','editBoardImgs','editBoardBad','trayImgs','trayBad','editShown')}, ensure_ascii=False))
    print("bad edit:", json.dumps(ed['bad'], ensure_ascii=False))

    # which piece srcs in tray / board
    print("tray srcs:", t.eval("JSON.stringify([...document.querySelectorAll('#editTray img')].map(i=>i.getAttribute('src')))"))
    print("board black srcs:", t.eval("JSON.stringify([...document.querySelectorAll('#editBoard img')].map(i=>i.getAttribute('src')).filter(s=>s.includes('_')))"))

    t.shot(SHOT)
    print("shot:", SHOT)
