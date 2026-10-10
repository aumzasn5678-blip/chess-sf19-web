#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp

APP = "http://127.0.0.1:8100/index.html?v=150"
OUT = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
res = {}

def j(o): return json.dumps(o, ensure_ascii=False)

with cdp.Tab() as t:
    t.cmd("Page.enable")
    # capture window errors + console errors early
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source="""
      window.__errcap = [];
      window.addEventListener('error', e => window.__errcap.push(String(e.message||e.error)));
      window.addEventListener('unhandledrejection', e => window.__errcap.push('rej:'+String(e.reason)));
    """)
    t.goto(APP, settle=2.0)
    time.sleep(1.0)

    res['errs_initial'] = t.eval("window.__errcap")
    res['dbg'] = t.eval("!!window.__chessDbg")
    res['board_sq'] = t.eval("document.querySelectorAll('#board .sq').length")
    res['has_bHist'] = t.eval("!!document.getElementById('bHist')")
    res['has_replayView'] = t.eval("!!document.getElementById('replayView')")

    # --- B: import a 4-ply PGN into main game ---
    t.eval("document.getElementById('pgnIn').value='1. e4 e5 2. Nf3 Nc6'")
    t.click("#bImportPgn")
    time.sleep(0.5)
    res['ucisLen_afterImport'] = t.eval("window.__chessDbg.ucisLen")

    # clear any history first for a clean count
    t.eval("localStorage.removeItem('chessHist')")

    # --- C: new game (confirm) -> auto-save into history ---
    t.click("#bNewGame")
    time.sleep(0.3)
    t.click("#bNewYes")
    time.sleep(0.6)
    res['hist_len_after_newgame'] = t.eval("window.__chessDbg.hist.length")
    res['hist_first'] = t.eval("(() => { const h=window.__chessDbg.hist[0]; return h?{name:h.name, savedAt:h.savedAt, ucis:h.ucis.length, fens:h.fens.length, grades:h.grades.length}:null; })()")
    res['ucisLen_after_newgame'] = t.eval("window.__chessDbg.ucisLen")

    # --- D: open history page and read the item ---
    t.click("#bHist")
    time.sleep(0.4)
    res['hist_open'] = t.eval("document.getElementById('histView').classList.contains('show')")
    res['hist_list_text'] = t.eval("document.getElementById('histList').innerText")
    res['hist_count_text'] = t.eval("document.getElementById('histCount').innerText")
    res['hist_items'] = t.eval("document.querySelectorAll('#histList .histItem').length")
    t.shot(os.path.join(OUT, "shot-150-hist-th.png"))

    # --- E: open replay ---
    t.click("#histList .histItem .histBtns button")   # first button = open
    time.sleep(0.5)
    res['replay_open'] = t.eval("document.getElementById('replayView').classList.contains('show')")
    res['rpUcisLen'] = t.eval("window.__chessDbg.rpUcisLen")
    res['rpPtr0'] = t.eval("window.__chessDbg.rpPtr")
    res['rp_log_initial'] = t.eval("document.getElementById('rpLog').innerText")

    # --- F: autoplay at delay 3 (but set to 1 to be fast for measuring step growth) ---
    t.eval("window.__rp = window.__chessDbg.rpPtr")
    # press play, sample ptr growth
    t.click("#rpRun")
    time.sleep(0.4)
    res['rpPlaying_after_play'] = t.eval("window.__chessDbg.rpPlaying")
    time.sleep(1.4)
    res['rpPtr_mid'] = t.eval("window.__chessDbg.rpPtr")
    res['rp_log_mid'] = t.eval("document.getElementById('rpLog').innerText")
    # stop mid-way (test ฬ stop)
    t.click("#rpRun")
    time.sleep(0.3)
    p1 = t.eval("window.__chessDbg.rpPtr")
    time.sleep(1.5)
    p2 = t.eval("window.__chessDbg.rpPtr")
    res['stop_ptr_frozen'] = (p1 == p2)
    res['stop_playing'] = t.eval("window.__chessDbg.rpPlaying")
    res['stop_p1p2'] = [p1, p2]

    # --- speed: set delay 1, restart, measure to completion ---
    t.click("#rpRestart")   # restart -> plays again from 0
    time.sleep(0.2)
    res['restart_playing'] = t.eval("window.__chessDbg.rpPlaying")
    res['restart_ptr_soon'] = t.eval("window.__chessDbg.rpPtr")
    # set speed to 1 while playing
    t.eval("(()=>{const s=document.getElementById('rpDelay');s.value='1';s.dispatchEvent(new Event('input'));})()")
    res['rpDelay'] = t.eval("window.__chessDbg.rpDelay")
    t0 = time.time()
    done = False
    for _ in range(80):
        if t.eval("window.__chessDbg.rpPtr") >= t.eval("window.__chessDbg.rpUcisLen"):
            done = True; break
        time.sleep(0.15)
    res['replay_done'] = done
    res['replay_time_1s'] = round(time.time()-t0, 2)
    res['rpPtr_end'] = t.eval("window.__chessDbg.rpPtr")
    res['rp_playing_end'] = t.eval("window.__chessDbg.rpPlaying")
    res['rp_log_end'] = t.eval("document.getElementById('rpLog').innerText")
    res['rp_grades_icons_in_log'] = t.eval("document.querySelectorAll('#rpLog img.logg').length")
    t.shot(os.path.join(OUT, "shot-150-replay-ok-th.png"))

    res['errs_final'] = t.eval("window.__errcap")

print(j(res))
