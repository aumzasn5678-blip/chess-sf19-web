import sys, time, json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp

OUT={}
FEN="7k/P7/8/8/8/8/8/7K w - - 0 1"

def sqimg(t, s):
    return t.eval(f"(() => {{ const e=document.querySelector('#board .sq[data-sq=\"{s}\"] img'); return e? e.getAttribute('src') : null; }})()")

def setpos(t, fen):
    t.eval(f"(() => {{ const f=document.getElementById('fen'); f.value={json.dumps(fen)}; document.getElementById('bSet').click(); return 1; }})()")
    time.sleep(0.5)

def open_promo(t):
    t.eval("(() => { document.querySelector('#board .sq[data-sq=\"a7\"]').click(); return 1; })()"); time.sleep(0.4)
    t.eval("(() => { document.querySelector('#board .sq[data-sq=\"a8\"]').click(); return 1; })()"); time.sleep(0.5)

def key(t, k, code):
    t.eval(f"(() => {{ document.dispatchEvent(new KeyboardEvent('keydown',{{key:{json.dumps(k)},code:{json.dumps(code)},bubbles:true}})); return 1; }})()")
    time.sleep(0.5)

with cdp.Tab() as t:
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source="window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message)));")
    t.goto('http://127.0.0.1:8100/index.html?v=122promo'); time.sleep(6)
    t.eval("(()=>{localStorage.clear();return 1})()")
    t.goto('http://127.0.0.1:8100/index.html?v=122promo2'); time.sleep(6)

    # --- promo via keyboard 'r' (rook) ---
    setpos(t, FEN)
    open_promo(t)
    OUT['show_1'] = t.eval("document.getElementById('promo').classList.contains('show')")
    OUT['imgs'] = t.eval("[...document.querySelectorAll('#promo button img')].map(x=>x.getAttribute('src'))")
    OUT['aria_th'] = t.eval("[...document.querySelectorAll('#promo button')].map(x=>x.getAttribute('aria-label'))")
    OUT['bar_bg_default'] = t.eval("getComputedStyle(document.getElementById('promo')).backgroundColor")
    t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v122-promo-default.png')
    key(t,'r','KeyR')
    OUT['afterR_a8'] = sqimg(t,'a8')
    OUT['afterR_log'] = t.eval("document.getElementById('log').innerText")
    OUT['afterR_show'] = t.eval("document.getElementById('promo').classList.contains('show')")
    OUT['afterR_status'] = t.eval("document.getElementById('status').textContent")

    # --- promo via click bishop ---
    setpos(t, FEN); open_promo(t)
    t.eval("(() => { document.querySelector('#promo button[data-piece=\"b\"]').click(); return 1; })()"); time.sleep(0.6)
    OUT['afterB_a8'] = sqimg(t,'a8')
    OUT['afterB_log'] = t.eval("document.getElementById('log').innerText")

    # --- promo via click knight ---
    setpos(t, FEN); open_promo(t)
    t.eval("(() => { document.querySelector('#promo button[data-piece=\"n\"]').click(); return 1; })()"); time.sleep(0.6)
    OUT['afterN_a8'] = sqimg(t,'a8')
    OUT['afterN_log'] = t.eval("document.getElementById('log').innerText")

    # --- promo via click queen ---
    setpos(t, FEN); open_promo(t)
    t.eval("(() => { document.querySelector('#promo button[data-piece=\"q\"]').click(); return 1; })()"); time.sleep(0.6)
    OUT['afterQ_a8'] = sqimg(t,'a8')
    OUT['afterQ_log'] = t.eval("document.getElementById('log').innerText")

    # --- ESC cancels (no move) ---
    setpos(t, FEN); open_promo(t)
    key(t,'Escape','Escape')
    OUT['esc_show'] = t.eval("document.getElementById('promo').classList.contains('show')")
    OUT['esc_log'] = t.eval("document.getElementById('log').innerText")
    OUT['esc_a8'] = sqimg(t,'a8')

    # --- 'n' during promo must NOT open new-game confirm; picks knight ---
    setpos(t, FEN); open_promo(t)
    key(t,'n','KeyN')
    OUT['n_confirm_open'] = t.eval("getComputedStyle(document.getElementById('confirmNew')).display!=='none'")
    OUT['n_a8'] = sqimg(t,'a8')

    # --- EN labels ---
    t.eval("(()=>{document.getElementById('settings').open=true;return 1})()")
    t.click('.lang[data-lang="en"]'); time.sleep(0.6)
    setpos(t, FEN); open_promo(t)
    OUT['aria_en'] = t.eval("[...document.querySelectorAll('#promo button')].map(x=>x.getAttribute('aria-label'))")
    key(t,'q','KeyQ')
    OUT['en_afterQ_a8'] = sqimg(t,'a8')
    t.click('.lang[data-lang="th"]'); time.sleep(0.5)

    # --- theme colors ---
    t.eval("(()=>{document.getElementById('settings').open=false;return 1})()")
    # default theme (nibble -> theme-white) accent #4ea1f0
    OUT['bar_bg_white'] = t.eval("(()=>{return getComputedStyle(document.getElementById('promo')).backgroundColor})()")
    t.click('#bTheme'); time.sleep(0.4)   # -> bw
    setpos(t, FEN); open_promo(t)
    OUT['bar_bg_bw'] = t.eval("getComputedStyle(document.getElementById('promo')).backgroundColor")
    t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v122-promo-bw.png')
    t.eval("(()=>{document.querySelector('#promo button[data-piece=\"q\"]').click();return 1})()"); time.sleep(0.4)
    t.click('#bTheme'); time.sleep(0.4)   # -> brown
    setpos(t, FEN); open_promo(t)
    OUT['bar_bg_brown'] = t.eval("getComputedStyle(document.getElementById('promo')).backgroundColor")
    t.eval("(()=>{document.querySelector('#promo button[data-piece=\"q\"]').click();return 1})()"); time.sleep(0.3)
    t.click('#bTheme'); time.sleep(0.4)   # -> green
    setpos(t, FEN); open_promo(t)
    OUT['bar_bg_green'] = t.eval("getComputedStyle(document.getElementById('promo')).backgroundColor")
    t.eval("(()=>{document.querySelector('#promo button[data-piece=\"q\"]').click();return 1})()"); time.sleep(0.3)

    # --- overflow at 390 with promo open ---
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    setpos(t, FEN); open_promo(t)
    OUT['overflow_390_promo'] = t.eval("(()=>({iw:innerWidth, de:document.documentElement.scrollWidth, barW:document.getElementById('promo').getBoundingClientRect().width}))()")
    t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v122-promo-390.png')
    t.eval("(()=>{document.querySelector('#promo button[data-piece=\"q\"]').click();return 1})()"); time.sleep(0.3)

    OUT['errors'] = t.eval("window.__errs.slice()")

print(json.dumps(OUT, ensure_ascii=False, indent=1))
