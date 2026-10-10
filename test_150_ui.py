#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os, re
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
APP = "http://127.0.0.1:8100/index.html?v=150"
OUT = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)
THAI = re.compile(r"[\u0E00-\u0E7F]")

OVERFLOW = """
(() => {
  const W = document.documentElement.clientWidth; const bad=[];
  document.querySelectorAll('*').forEach(el=>{
    const st=getComputedStyle(el); if(st.display==='none'||st.visibility==='hidden') return;
    const r=el.getBoundingClientRect(); if(r.width<=0&&r.height<=0) return;
    if(r.right>W+1.5 || r.left<-1.5){ bad.push((el.id?('#'+el.id):('.'+String(el.className).slice(0,24)))+' r='+Math.round(r.right)); }
  });
  return {W:W, docSW:document.documentElement.scrollWidth, bad:bad.slice(0,14), nbad:bad.length};
})()
"""

with cdp.Tab() as t:
    t.cmd("Page.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source="""
      window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
      window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));
    """)
    # ---- 51-game cap ----
    t.goto(APP, settle=1.5)
    t.eval("""(() => { const a=[]; for(let i=0;i<51;i++){ a.push({id:'k'+i,name:'G'+i,savedAt:(1000*1000+i),fens:['rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'],ucis:[],grades:[],flipped:false}); } localStorage.setItem('chessHist', JSON.stringify(a)); return a.length; })()""")
    t.goto(APP+"&cap=1", settle=1.5); time.sleep(0.5)
    res['cap_len'] = t.eval("window.__chessDbg.hist.length")
    res['cap_first'] = t.eval("window.__chessDbg.hist[0].name")
    res['cap_last'] = t.eval("window.__chessDbg.hist[window.__chessDbg.hist.length-1].name")
    res['cap_storage_len'] = t.eval("JSON.parse(localStorage.getItem('chessHist')).length")
    res['cap_dbg_getter'] = t.eval("typeof window.__chessDbg.hist")

    # ---- 390px overflow TH (main + hist + replay + stats) ----
    t.eval("localStorage.removeItem('chessHist')")
    t.goto(APP+"&th=1", settle=1.5); time.sleep(0.5)
    res['ov_main_th'] = t.eval(OVERFLOW)
    t.click("#bHist"); time.sleep(0.4)
    res['ov_hist_th'] = t.eval(OVERFLOW)
    t.click("#histBack"); time.sleep(0.3)
    # make a game then replay
    t.eval("document.getElementById('pgnIn').value='1. e4 e5 2. Nf3 Nc6 3. Bb5 a6'")
    t.click("#bImportPgn"); time.sleep(0.4)
    t.click("#bNewGame"); time.sleep(0.2); t.click("#bNewYes"); time.sleep(0.4)
    t.click("#bHist"); time.sleep(0.3)
    t.eval("document.querySelector('#histList .histItem .histBtns button').click()"); time.sleep(0.4)
    res['ov_replay_th'] = t.eval(OVERFLOW)
    t.shot(os.path.join(OUT,"shot-150-replay-th-390.png"))
    t.click("#rpStats"); time.sleep(0.4)
    res['ov_stats_th'] = t.eval(OVERFLOW)
    t.shot(os.path.join(OUT,"shot-150-stats-th-390.png"))
    t.click("#statClose"); time.sleep(0.2)

    # ---- theme colors (2+ themes) ----
    themes={}
    for i in range(4):
        themes[i] = t.eval("(() => { const cs=getComputedStyle(document.getElementById('bStats')); const hs=getComputedStyle(document.getElementById('bHist')); return {body:document.body.className, statColor:cs.color, histBg:hs.backgroundImage.slice(0,60)}; })()")
        t.eval("document.getElementById('bTheme').click()"); time.sleep(0.25)
    res['themes'] = themes
    # accuracy color inside stats across 2 themes
    acc_colors=[]
    for _ in range(2):
        t.eval("window.__openStats && 0")
        acc_colors.append(t.eval("(() => { const el=document.querySelector('#statBody .statAcc b'); return el?getComputedStyle(el).color:null; })()"))
        t.eval("document.getElementById('bTheme').click()"); time.sleep(0.2)
    res['acc_colors'] = acc_colors

    # ---- EN mode: no Thai leftover ----
    t.eval("document.getElementById('statClose').click()")
    t.eval("localStorage.setItem('chessLang','en')")
    t.goto(APP+"&en=1", settle=1.5); time.sleep(0.6)
    res['lang'] = t.eval("document.documentElement.lang")
    def visible_text(): return t.eval("document.body.innerText")
    t.click("#bHist"); time.sleep(0.3)
    txt_hist = t.eval("document.getElementById('histView').innerText")
    t.eval("document.querySelector('#histList .histItem .histBtns button').click()"); time.sleep(0.4)
    txt_replay = t.eval("document.getElementById('replayView').innerText")
    t.click("#rpStats"); time.sleep(0.3)
    txt_stats = t.eval("document.getElementById('statView').innerText")
    res['en_thai_hist'] = bool(THAI.search(txt_hist or ""))
    res['en_thai_replay'] = bool(THAI.search(txt_replay or ""))
    res['en_thai_stats'] = bool(THAI.search(txt_stats or ""))
    res['en_thai_hist_sample'] = (THAI.search(txt_hist or "").group(0) if THAI.search(txt_hist or "") else None)
    res['en_stats_text'] = txt_stats[:180]
    t.shot(os.path.join(OUT,"shot-150-stats-en-390.png"))
    t.click("#statClose"); time.sleep(0.2)
    t.click("#rpClose"); time.sleep(0.2)
    t.click("#histBack"); time.sleep(0.2)
    res['ov_main_en'] = t.eval(OVERFLOW)
    t.shot(os.path.join(OUT,"shot-150-main-en-390.png"))

    # ---- original features smoke ----
    t.eval("localStorage.setItem('chessLang','th')")
    t.goto(APP+"&sm=1", settle=1.5); time.sleep(0.5)
    res['smoke'] = t.eval("""(() => ({
       run: document.getElementById('bRun').textContent.trim(),
       arrows: !!document.getElementById('arrows'),
       edit: !!document.getElementById('bEdit'),
       posPanel: !!document.getElementById('posPanel'),
       settings: !!document.getElementById('settings'),
       installCardShown: getComputedStyle(document.getElementById('installCard')).display !== 'none',
       installBody: document.getElementById('installBody').textContent.slice(0,60),
       bInstallShown: getComputedStyle(document.getElementById('bInstall')).display !== 'none',
       manifest: !!document.querySelector('link[rel=manifest]')
    }))()""")
    t.click("#bEdit"); time.sleep(0.3)
    res['smoke_edit_open'] = t.eval("document.getElementById('editView').classList.contains('show')")
    t.click("#editBack"); time.sleep(0.2)
    # share link
    t.click("#bShare"); time.sleep(0.3)
    res['smoke_share'] = t.eval("document.body.dataset.lastShare ? document.body.dataset.lastShare.slice(0,60) : null")
    # persist current game (loadGame restore)
    t.eval("document.getElementById('pgnIn').value='1. d4 d5 2. c4 e6'")
    t.click("#bImportPgn"); time.sleep(0.4)
    t.goto(APP+"&restore=1", settle=1.5); time.sleep(0.5)
    res['smoke_restore_ucis'] = t.eval("window.__chessDbg.ucisLen")
    res['errs'] = t.eval("window.__errcap")

print(j(res))
