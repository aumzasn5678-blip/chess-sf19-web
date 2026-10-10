#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp

TS = str(int(time.time()))
APP = "http://127.0.0.1:8100/index.html?v=" + TS
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)
PGN = "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. d3 Nf6 5. Nc3 d6 6. Bg5 h6 7. Bxf6 Qxf6"

with cdp.Tab(timeout=300) as t:
    t.cmd("Page.enable")
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source="""
      window.__errcap=[]; window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
      window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));
    """)
    t.goto(APP, settle=2.0)
    t.eval("(async()=>{try{const rs=await navigator.serviceWorker.getRegistrations();for(const r of rs)await r.unregister();}catch(e){}try{const ks=await caches.keys();for(const k of ks)await caches.delete(k);}catch(e){}try{localStorage.clear();}catch(e){}return true;})()")
    time.sleep(0.6)
    t.goto(APP, settle=2.5)
    time.sleep(1.0)

    def c(sq): t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return true;})()" % sq)
    def all_graded():
        s = t.eval("(()=>{const g=window.__chessDbg.moveGrades;let nul=0;for(const x of g)if(!x)nul++;return g.length+'/'+nul;})()")
        L,N = s.split('/'); return int(N) == 0 and int(L) > 0

    print('PHASE g', flush=True)
    # ================= (ง) OPEN STATS OF A GAME WITH INCOMPLETE GRADES =================
    # import PGN to main -> grades empty; then save to history so we have an "old" game w/o grades
    t.eval("document.getElementById('pgnIn').value=%s" % json.dumps(PGN))
    t.click("#bImportPgn")
    time.sleep(0.3)
    res['after_import_ucisLen'] = t.eval("window.__chessDbg.ucisLen")
    # immediately save into history (with whatever grades exist at this instant)
    t.eval("localStorage.removeItem('chessHist')")
    t.click("#bSaveHist")
    time.sleep(0.2)
    res['hist_len'] = t.eval("window.__chessDbg.hist.length")
    res['hist0_grades_null_before'] = t.eval("(()=>{const g=window.__chessDbg.hist[0].grades;let n=0;for(const x of g)if(!x)n++;return n+'/'+g.length;})()")

    # wait for background main grading of the just-imported game (retroMainGame)
    t0=time.time()
    while time.time()-t0 < 60 and not all_graded(): time.sleep(0.3)
    res['main_import_bg_graded'] = all_graded()
    res['main_import_bg_s'] = round(time.time()-t0,2)

    # Now make an "old incomplete" game: create a second history entry with NO grades by importing into hist
    t.eval("document.getElementById('histPgn').value=%s" % json.dumps("1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. Bg5 Be7 5. e3 O-O 6. Nf3 h6 7. Bh4 b6"))
    t.click("#bHist")            # open history page
    time.sleep(0.4)
    t.click("#histImportBtn")    # import to history (grades null)
    time.sleep(0.5)
    res['hist_len_after_2nd'] = t.eval("window.__chessDbg.hist.length")

    # find the ungraded entry and open its stats; measure retro
    t.eval("(()=>{window.__g=window.__chessDbg.hist; return true;})()")
    idx = t.eval("(()=>{const h=window.__chessDbg.hist;for(let i=0;i<h.length;i++){let n=0;for(const x of (h[i].grades||[]))if(!x)n++;if(n>0)return i;}return -1;})()")
    res['ungraded_hist_index'] = idx
    if idx is not None and idx != -1:
        t.eval("(()=>{const it=document.querySelectorAll('#histList .histItem')[%d]; if(it){it.querySelectorAll('.histBtns button')[1].click();}return true;})()" % idx)
        # measure time until stats complete
        t0=time.time(); done=False
        for _ in range(200):
            txt = t.eval("document.getElementById('gradeProg').innerText")
            sums = t.eval("""(()=>{const cols=[...document.querySelectorAll('#statBody .statCol')];let o=[];cols.forEach(col=>{let sum=0;[...col.querySelectorAll('.statRow b')].forEach(b=>sum+=parseInt(b.innerText,10)||0);o.push(sum);});return o.join(',');})()""")
            if '✓' in txt or txt=='':
                # check completeness
                gm = t.eval("(()=>{const h=window.__chessDbg.hist[%d];let n=0;for(const x of (h.grades||[]))if(!x)n++;return (h.ucis||[]).length+'/'+n;})()" % idx)
                L,N = gm.split('/')
                if int(N)==0 and int(L)>0: done=True; break
            time.sleep(0.2)
        res['retro_stats_done'] = done
        res['retro_stats_s'] = round(time.time()-t0,2)
        res['retro_stats_sums'] = sums
        res['retro_stats_grades_after'] = t.eval("(()=>{const h=window.__chessDbg.hist[%d];return JSON.stringify(h.grades);})()" % idx)
        res['retro_prog_text'] = t.eval("document.getElementById('gradeProg').innerText")

        # (ฬ) CACHE: close and reopen stats - should be instant (no engine)
        t.click("#statClose"); time.sleep(0.3)
        t0=time.time()
        t.eval("(()=>{const it=document.querySelectorAll('#histList .histItem')[%d]; if(it){it.querySelectorAll('.histBtns button')[1].click();}return true;})()" % idx)
        time.sleep(0.6)
        res['reopen_prog_text'] = t.eval("document.getElementById('gradeProg').innerText")
        res['reopen_prog_hidden'] = t.eval("document.getElementById('gradeProg').style.display==='none'")
        res['reopen_s'] = round(time.time()-t0,2)
        t.shot(r"E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-156-retro.png")
        t.click("#statClose"); time.sleep(0.2)

        # stop-on-close test: reopen, wait a hair, close, then confirm queue stops growing
        t.eval("(()=>{const it=document.querySelectorAll('#histList .histItem')[%d]; if(it){it.querySelectorAll('.histBtns button')[1].click();}return true;})()" % idx)
        time.sleep(0.1)
        t.click("#statClose")
        time.sleep(0.5)
        res['queueLen_after_close'] = t.eval("window.__chessDbg.gradeQueueLen")

    print('PHASE k', flush=True); print('res-so-far', j(res), flush=True)
    # ================= (ค) RUN MODE: grades fast =================
    t.click("#histBack"); time.sleep(0.3)
    t.click("#bNewGame"); time.sleep(0.2); t.click("#bNewYes"); time.sleep(0.5)
    t.eval("localStorage.removeItem('chessGradeCache')")
    t.goto(APP, settle=2.5); time.sleep(0.8)
    t.click("#bRun")          # start analysis
    time.sleep(2.0)
    res['analyzing'] = t.eval("(()=>{try{return document.getElementById('bRun').classList.contains('on');}catch(e){return 'x';}})()")
    lat=[]
    runseq=[('e2','e4'),('e7','e5'),('g1','f3'),('b8','c6')]
    for f,to in runseq:
        c(f); time.sleep(0.05); c(to)
        t0=time.time()
        while time.time()-t0 < 8:
            g=t.eval("window.__chessDbg.moveGrades")
            if g and g[-1]: break
            time.sleep(0.05)
        lat.append(round((time.time()-t0)*1000))
    res['run_mode_grade_ms'] = lat
    res['run_mode_moveGrades'] = t.eval("window.__chessDbg.moveGrades")
    t.click("#bRun")          # stop
    res['errs'] = t.eval("window.__errcap")

import sys; print(j(res)); sys.stdout.flush()
