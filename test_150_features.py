#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp

APP = "http://127.0.0.1:8100/index.html?v=150"
OUT = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
DL  = r"C:\Users\poxii\AppData\Local\Temp\chessdl"
os.makedirs(DL, exist_ok=True)
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)

BUILD = """
(async () => {
  const mod = await import('/lib/chess.js');
  const Chess = mod.Chess;
  function mk(name, savedAt, ucis, grades){
    const c=new Chess(); const f=[c.fen()];
    for(const u of ucis){ c.move({from:u.slice(0,2),to:u.slice(2,4),promotion:u[4]||'q'}); f.push(c.fen()); }
    return { id:'x'+savedAt, name:name, savedAt:savedAt, fens:f, ucis:ucis, grades:grades, flipped:false };
  }
  const m=['e2e4','e7e5','g1f3','b8c6'];
  const A=mk('Alpha', Date.now()-3000, m, ['brilliant','good','blunder','best']);
  const B=mk('Zeta',  Date.now()-9000, m, ['blunder','blunder','good','inaccuracy']);
  const C=mk('Beta',  Date.now()-6000, m, ['best','best','excellent','mistake']);
  localStorage.setItem('chessHist', JSON.stringify([A,B,C]));
  return true;
})()
"""

with cdp.Tab() as t:
    t.cmd("Page.enable")
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source="""
      window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
      window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));
    """)
    try: t.cmd("Page.setDownloadBehavior", behavior="allow", downloadPath=DL)
    except Exception as e: res['dl_behavior']=str(e)[:80]
    print('STEP load',flush=True); t.goto(APP, settle=2.0); time.sleep(0.8)
    print('STEP build',flush=True); t.eval(BUILD, await_promise=True)
    t.goto(APP+"&r=1", settle=1.5); time.sleep(0.6)

    # ---- open history ----
    print('STEP hist',flush=True); t.click("#bHist"); time.sleep(0.4)
    res['hist_count'] = t.eval("document.querySelectorAll('#histList .histItem').length")
    def names(): return t.eval("[...document.querySelectorAll('#histList .histName')].map(e=>e.textContent)")
    res['order_default'] = names()

    # ---- sort date_asc ----
    t.eval("(()=>{const s=document.getElementById('histSort');s.value='date_asc';s.dispatchEvent(new Event('change'));})()")
    time.sleep(0.3); res['order_date_asc'] = names()
    # blunder sort
    t.eval("(()=>{const s=document.getElementById('histSort');s.value='blunder';s.dispatchEvent(new Event('change'));})()")
    time.sleep(0.3); res['order_blunder'] = names()
    # name sort
    t.eval("(()=>{const s=document.getElementById('histSort');s.value='name';s.dispatchEvent(new Event('change'));})()")
    time.sleep(0.3); res['order_name'] = names()
    # search
    t.eval("(()=>{const i=document.getElementById('histSearch');i.value='et';i.dispatchEvent(new Event('input'));})()")
    time.sleep(0.3); res['search_et'] = names()
    t.eval("(()=>{const i=document.getElementById('histSearch');i.value='zzz';i.dispatchEvent(new Event('input'));})()")
    time.sleep(0.3); res['search_none'] = t.eval("document.getElementById('histList').innerText")
    t.eval("(()=>{const i=document.getElementById('histSearch');i.value='';i.dispatchEvent(new Event('input'));const s=document.getElementById('histSort');s.value='date_desc';s.dispatchEvent(new Event('change'));})()")
    time.sleep(0.3)

    print('STEP sortdone',flush=True)
    # ---- stats modal for game A (Alpha) ----
    t.eval("(()=>{const it=document.querySelector('#histList .histItem'); [...it.querySelectorAll('button')].find(b=>b.textContent.includes('สถิติ')||b.textContent.includes('stats')).click();})()")
    time.sleep(0.4)
    res['stats_open'] = t.eval("document.getElementById('statView').classList.contains('show')")
    res['stats_name'] = t.eval("document.getElementById('statName').textContent")
    res['stats_rows'] = t.eval("[...document.querySelectorAll('#statBody .statCol')].map(c=>c.innerText)")
    res['stats_acc'] = t.eval("[...document.querySelectorAll('#statBody .statAcc b')].map(b=>b.textContent)")
    res['stats_grade_icons'] = t.eval("document.querySelectorAll('#statBody .statRow img').length")
    res['stats_all_rows'] = t.eval("document.querySelectorAll('#statBody .statRow').length")
    pass  # shot disabled: t.shot(os.path.join(OUT, "shot-150-stats-th.png"))
    t.click("#statClose"); time.sleep(0.2)

    print('STEP stats',flush=True)
    # ---- copy PGN of a game ----
    t.eval("(()=>{const it=document.querySelector('#histList .histItem'); [...it.querySelectorAll('button')].find(b=>b.textContent.includes('คัดลอก PGN')).click();})()")
    time.sleep(0.3)
    res['copy_pgn'] = t.eval("document.getElementById('histPgnOut').value")

    print('STEP copy',flush=True)
    # ---- export all history ----
    t.click("#histExportAll"); time.sleep(0.6)
    allpgn = t.eval("document.getElementById('histPgnOut').value") or ""
    res['all_pgn_games'] = allpgn.count('[Event ')
    res['all_pgn_lines'] = len(allpgn.split('\n'))
    res['all_pgn_head'] = allpgn[:120]
    time.sleep(1.2)
    res['download_files'] = os.listdir(DL)

    print('STEP export',flush=True)
    # ---- replay keyboard shortcuts ----
    t.eval("(()=>{document.querySelector('#histList .histItem .histBtns button').click();})()")  # open replay (first btn)
    time.sleep(0.5)
    res['rp_open'] = t.eval("document.getElementById('replayView').classList.contains('show')")
    res['rp_delay_default'] = t.eval("window.__chessDbg.rpDelay")
    def key(code): t.eval("document.dispatchEvent(new KeyboardEvent('keydown',{code:%s,key:'',bubbles:true}))" % json.dumps(code)); time.sleep(0.15)
    key("ArrowRight"); key("ArrowRight")
    res['after_rr'] = t.eval("window.__chessDbg.rpPtr")
    key("ArrowLeft")
    res['after_rl'] = t.eval("window.__chessDbg.rpPtr")
    key("End"); res['after_end'] = t.eval("window.__chessDbg.rpPtr")
    key("Home"); res['after_home'] = t.eval("window.__chessDbg.rpPtr")
    key("Digit5"); res['delay_after_5'] = t.eval("window.__chessDbg.rpDelay")
    key("Digit0"); res['delay_after_0'] = t.eval("window.__chessDbg.rpDelay")
    key("Digit1"); res['delay_after_1'] = t.eval("window.__chessDbg.rpDelay")
    # Space toggles play
    key("Space"); time.sleep(0.2); res['space_playing'] = t.eval("window.__chessDbg.rpPlaying")
    key("Space"); time.sleep(0.2); res['space_stopped'] = t.eval("window.__chessDbg.rpPlaying")
    # slider
    t.eval("(()=>{const s=document.getElementById('rpDelay');s.value='3.5';s.dispatchEvent(new Event('input'));})()")
    time.sleep(0.2)
    res['slider_delay'] = t.eval("window.__chessDbg.rpDelay")
    res['slider_label'] = t.eval("document.getElementById('rpDelayv').textContent")
    # replay share/copy PGN
    t.click("#rpShare"); time.sleep(0.3)
    res['rp_copy_pgn'] = t.eval("document.getElementById('histPgnOut').value")
    # log has grade icons
    key("End"); time.sleep(0.2)
    res['rp_log_grade_icons'] = t.eval("document.querySelectorAll('#rpLog img.logg').length")
    res['rp_log_text'] = t.eval("document.getElementById('rpLog').innerText")
    pass  # shot disabled: t.shot(os.path.join(OUT, "shot-150-replay-th.png"))
    t.click("#rpClose"); time.sleep(0.2)

    print('STEP replay',flush=True)
    res['errs'] = t.eval("window.__errcap")

print(j(res))
