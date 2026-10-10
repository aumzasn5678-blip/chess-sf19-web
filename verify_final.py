#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
APPF="http://127.0.0.1:8100/index.html?v="
def j(o): return json.dumps(o, ensure_ascii=False)
INIT="""window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));"""
with cdp.Tab(timeout=200) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APPF+str(int(time.time())), settle=2.0); t.eval("localStorage.clear()"); t.goto(APPF+str(int(time.time())), settle=2.2); time.sleep(0.7)
    def click(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()"%sq)
    # ---- T1: 10 moves incl 2 captures ----
    moves=[('e2','e4'),('e7','e5'),('g1','f3'),('b8','c6'),('f1','c4'),('g8','f6'),('d2','d3'),('f8','c5'),('f3','e5'),('c6','e5')]
    for f,to in moves:
        click(f); time.sleep(0.05); click(to); time.sleep(0.30)
    time.sleep(0.6)
    r={}
    r['ucis']=t.eval("window.__chessDbg.ucis")
    r['animCount']=t.eval("window.__chessDbg.animCount")
    r['fen']=t.eval("window.__chessDbg.fens[window.__chessDbg.fens.length-1]")
    # ---- T2: undo x2 / redo x2 ----
    t.eval("document.getElementById('bBack').click()"); time.sleep(0.25)
    t.eval("document.getElementById('bBack').click()"); time.sleep(0.35)
    r['ptr_undo']=t.eval("window.__chessDbg.ptr")
    t.eval("document.getElementById('bFwd').click()"); time.sleep(0.25)
    t.eval("document.getElementById('bFwd').click()"); time.sleep(0.35)
    r['ptr_redo']=t.eval("window.__chessDbg.ptr")
    # ---- T3: cleanliness ----
    r['animating']=t.eval("document.querySelectorAll('#board .pcimg.animating,#rpBoard .pcimg.animating').length")
    r['land_cells_after']=t.eval("document.querySelectorAll('#board .sq.land,#rpBoard .sq.land').length")
    r['stuck_transform']=t.eval("[...document.querySelectorAll('#board .pcimg,#rpBoard .pcimg')].filter(i=>i.style.transform&&i.style.transform!=='').length")
    r['stuck_inline_transition']=t.eval("[...document.querySelectorAll('#board .pcimg,#rpBoard .pcimg')].filter(i=>i.style.transition&&i.style.transition!=='').length")
    r['stuck_opacity']=t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.opacity&&i.style.opacity!=='').length")
    r['caught']=t.eval("document.querySelectorAll('#board .pcimg.caught').length")
    r['ghosts']=t.eval("document.querySelectorAll('#boardWrap .ghost,#rpBoardWrap .ghost').length")
    r['pieces']=t.eval("document.querySelectorAll('#board .pcimg').length")
    # ---- T4: anim OFF => instant (no land) ----
    t.eval("(()=>{const st=document.querySelectorAll('#board .sq');return 1;})()")
    # toggle anim off via settings if exposed: simulate by clearing animOn through a move then checking dev quickly is hard; instead check that with animOn default the pop happened
    # move 11 (to have a fresh move) and immediately check dest has land class
    click('g2'); time.sleep(0.05); click('g3')
    time.sleep(0.02)
    r['land_just_after_move']=t.eval("document.querySelectorAll('#board .sq.land').length")
    r['errs']=t.eval("window.__errcap")
    print(j(r))
