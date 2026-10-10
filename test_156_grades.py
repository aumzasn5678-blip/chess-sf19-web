#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp

TS = str(int(time.time()))
APP = "http://127.0.0.1:8100/index.html?v=" + TS
OUT = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)

MOVES = [('e2','e4'),('e7','e5'),('g1','f3'),('b8','c6'),('f1','c4'),('f8','c5'),
         ('d2','d3'),('g8','f6'),('b1','c3'),('d7','d6'),('c1','g5'),('h7','h6'),
         ('g5','f6'),('d8','f6')]

with cdp.Tab(timeout=300) as t:
    t.cmd("Page.enable")
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source="""
      window.__errcap=[];
      window.addEventListener('error', e=>window.__errcap.push(String(e.message||e.error)));
      window.addEventListener('unhandledrejection', e=>window.__errcap.push('rej:'+String(e.reason)));
    """)
    t.goto(APP, settle=2.0)
    # clear SW + caches + localStorage, then reload fresh
    t.eval("(async()=>{try{const rs=await navigator.serviceWorker.getRegistrations();for(const r of rs)await r.unregister();}catch(e){}"
           "try{const ks=await caches.keys();for(const k of ks)await caches.delete(k);}catch(e){}"
           "try{localStorage.clear();}catch(e){} return true;})()")
    time.sleep(0.6)
    t.goto(APP, settle=2.5)
    time.sleep(0.8)
    res['engineReady'] = t.eval("!!(window.__chessDbg)")

    def click_sq(sq):
        return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(!e)return false;e.click();return true;})()" % sq)

    # ---- (ข) play 14 plies WITHOUT pressing run ----
    t.eval("(()=>{window.__t0=performance.now();return true;})()")
    for f,to in MOVES:
        click_sq(f); time.sleep(0.05); click_sq(to); time.sleep(0.30)
    res['ucisLen_played'] = t.eval("window.__chessDbg.ucisLen")

    t0 = time.time()
    full = False
    for _ in range(400):  # up to 120s
        n = t.eval("(()=>{const g=window.__chessDbg.moveGrades;let c=0;for(const x of g)if(x)c++;return [c,g.length].join('/');})()")
        if n.split('/')[0] == n.split('/')[1] and n.split('/')[0] != '0':
            full = True; break
        time.sleep(0.3)
    res['queue_full_all_graded'] = full
    res['queue_wait_s'] = round(time.time()-t0, 2)
    res['moveGrades'] = t.eval("window.__chessDbg.moveGrades")
    res['graded_counts'] = t.eval("(()=>{const g=window.__chessDbg.moveGrades;const c={};let nul=0;for(const x of g){if(x)c[x]=(c[x]||0)+1;else nul++;}return JSON.stringify({counts:c,nulls:nul,len:g.length});})()")
    res['board_gradico'] = t.eval("document.querySelectorAll('#board .gradico').length")
    res['log_logg_icons'] = t.eval("document.querySelectorAll('#log img.logg').length")
    res['log_text'] = t.eval("document.getElementById('log').innerText")
    res['cacheSize'] = t.eval("window.__chessDbg.gradeCacheSize")

    # ---- (ข) open stats box, read per-side totals ----
    t.click("#bStats")
    time.sleep(0.5)
    def stat_sums():
        return t.eval("""(()=>{const cols=[...document.querySelectorAll('#statBody .statCol')];
          const out=[];cols.forEach(col=>{const h=col.querySelector('h4').innerText;
            let sum=0;[...col.querySelectorAll('.statRow')].forEach(r=>{const b=r.querySelector('b');sum+=parseInt(b.innerText,10)||0;});
            out.push({head:h,sum:sum});});return JSON.stringify(out);})()""")
    res['stat_sums'] = stat_sums()
    res['gradeProg_text'] = t.eval("document.getElementById('gradeProg').innerText")
    t.shot(os.path.join(OUT, "shot-156-stats.png"))
    t.click("#statClose")
    time.sleep(0.3)

    # ---- (ฬ/D) redo-truncation: back 2 plies then play a DIFFERENT move ----
    t.click("#bBack"); time.sleep(0.2)
    t.click("#bBack"); time.sleep(0.3)
    res['ptr_after_back2'] = t.eval("window.__chessDbg.ptr")
    res['ucisLen_after_back2'] = t.eval("window.__chessDbg.ucisLen")
    click_sq('c4'); time.sleep(0.05); click_sq('b5'); time.sleep(0.4)   # 7.Bb5 (different from 7.d3 line)
    t0 = time.time()
    for _ in range(80):
        g = t.eval("window.__chessDbg.moveGrades")
        if len(g) >= 13 and g[12]:
            break
        time.sleep(0.2)
    res['redo_ucisLen'] = t.eval("window.__chessDbg.ucisLen")
    res['redo_moveGrades_len'] = t.eval("window.__chessDbg.moveGrades.length")
    res['redo_last_uci'] = t.eval("window.__chessDbg.ucis[window.__chessDbg.ucisLen-1]")
    res['redo_last_grade'] = t.eval("window.__chessDbg.moveGrades[window.__chessDbg.moveGrades.length-1]")
    res['redo_newgrade_ms'] = round((time.time()-t0)*1000)
    res['redo_board_gradico_sq'] = t.eval("(()=>{const e=document.querySelector('#board .gradico');return e? e.parentElement.dataset.sq : null;})()")
    res['redo_board_gradico_grade'] = t.eval("(()=>{const e=document.querySelector('#board .gradico');return e? e.dataset.grade : null;})()")

    # ---- (ฬ/cache) re-import the SAME 14-ply game via replay and time the retro (cache) ----
    t.eval("document.getElementById('bReplay')?false:false")
    pgn = "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. d3 Nf6 5. Nc3 d6 6. Bg5 h6 7. Bxf6 Qxf6"
    # open replay view via history? use rpImport directly after opening hist->replay not needed; call retroReplay path:
    res['cacheSize_before_reimport'] = t.eval("window.__chessDbg.gradeCacheSize")

    res['errs'] = t.eval("window.__errcap")

# ---- ghost / animation checks in a separate quick pass ----
with cdp.Tab(timeout=180) as t2:
    t2.goto(APP, settle=2.0)
    t2.eval("localStorage.clear()")
    t2.goto(APP, settle=2.5)
    time.sleep(0.6)
    def c2(sq): t2.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return true;})()" % sq)
    # rapid 5 moves
    rapid = [('d2','d4'),('d7','d5'),('g1','f3'),('g8','f6'),('c2','c4')]
    for f,to in rapid:
        c2(f); c2(to)
    time.sleep(0.15)
    res['ghost_during_rapid'] = t2.eval("document.querySelectorAll('#boardWrap .ghost, #rpBoardWrap .ghost').length")
    res['animating_during_rapid'] = t2.eval("document.querySelectorAll('#board .pcimg.animating').length")
    time.sleep(1.2)
    res['ghost_after_settle'] = t2.eval("document.querySelectorAll('#boardWrap .ghost, #rpBoardWrap .ghost').length")
    res['animating_after_settle'] = t2.eval("document.querySelectorAll('#board .pcimg.animating').length")
    res['transform_stuck'] = t2.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.transform && i.style.transform!=='').length")
    # capture fade single-piece: play a capturing move and sample pieces in dest cell
    # make a capture: from start-ish; use current position after 5 plies, play cxd5
    c2('c4'); time.sleep(0.05); c2('d5'); time.sleep(0.06)
    res['dest_cell_imgs'] = t2.eval("(()=>{const c=document.querySelector('#board .sq[data-sq=\"d5\"]');return c? c.querySelectorAll('img').length : -1;})()")
    res['caught_imgs'] = t2.eval("document.querySelectorAll('#board .pcimg.caught').length")
    t2.shot(os.path.join(OUT, "shot-156-anim.png"))
    time.sleep(1.0)
    res['ghost_after_capture'] = t2.eval("document.querySelectorAll('#boardWrap .ghost').length")
    res['caught_after'] = t2.eval("document.querySelectorAll('#board .pcimg.caught').length")

print(j(res))
