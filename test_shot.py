import sys, time, json, os
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp

URL = sys.argv[1]
OUT = os.path.abspath(sys.argv[2])

with cdp.Tab(timeout=150) as t:
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=1, mobile=True)
    t.goto(URL, settle=3)
    # open EDIT
    t.eval("(() => { const x=document.getElementById('bEdit'); if(x) x.click(); return !!x; })()")
    time.sleep(2)
    # clear existing pieces so we can place a clean set incl. black
    t.eval("(() => { const b=document.getElementById('editClear'); if(b) b.click(); return true; })()")
    time.sleep(0.4)
    # place a black queen, rook, king on d4/a1/h8 to prove black render
    for piece, sq in [('bq','d4'),('br','a1'),('bk','h8'),('bq','e5'),('wp','c3'),('wn','f6')]:
        t.eval(f"(() => {{ const b=document.querySelector('#editTray .traybtn[data-piece=\"{piece}\"]'); if(b) b.click(); return true; }})()")
        time.sleep(0.25)
        t.eval(f"(() => {{ const s=document.querySelector('#editBoard .sq[data-sq=\"{sq}\"]'); if(s) s.click(); return true; }})()")
        time.sleep(0.25)
    time.sleep(0.5)
    # scroll top so board+tray visible
    t.eval("document.getElementById('editView').scrollTop = 0")
    nw = t.eval("JSON.stringify([...document.querySelectorAll('#editBoard img')].map(i=>i.naturalWidth))")
    print("board img naturalWidths:", nw)
    r = t.cmd("Page.captureScreenshot", format="png", fromSurface=True)
    import base64
    open(OUT, "wb").write(base64.b64decode(r["data"]))
    print("SAVED", OUT, os.path.getsize(OUT), "bytes")
