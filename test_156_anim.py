#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp

TS = str(int(time.time()))
APP = "http://127.0.0.1:8100/index.html?v=" + TS
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)

with cdp.Tab(timeout=180) as t:
    t.cmd("Page.enable")
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source="""
      window.__errcap=[]; window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
      window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));
    """)
    t.goto(APP, settle=2.0)
    t.eval("localStorage.clear()")
    t.goto(APP, settle=2.5)
    time.sleep(0.6)
    def c(sq): t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return true;})()" % sq)

    # Capture scenario: 1.e4 d5 2.exd5 (white pawn captures d5 pawn)
    c('e2'); time.sleep(0.06); c('e4'); time.sleep(0.25)
    c('d7'); time.sleep(0.06); c('d5'); time.sleep(0.25)
    # now play exd5 capture and sample IMMEDIATELY (mid-animation)
    c('e4'); time.sleep(0.06); c('d5')
    res['dest_imgs_mid'] = t.eval("(()=>{const x=document.querySelector('#board .sq[data-sq=\"d5\"]');return x?x.querySelectorAll('img').length:-1;})()")
    res['animating_mid'] = t.eval("document.querySelectorAll('#board .pcimg.animating').length")
    res['caught_mid'] = t.eval("document.querySelectorAll('#board .pcimg.caught').length")
    res['ghost_mid'] = t.eval("document.querySelectorAll('#boardWrap .ghost, #rpBoardWrap .ghost').length")
    res['transition_prop'] = t.eval("(()=>{const e=document.querySelector('#board .pcimg.animating');return e?getComputedStyle(e).transitionProperty+' '+getComputedStyle(e).transitionDuration+' '+getComputedStyle(e).transitionTimingFunction:null;})()")
    res['anim_transform'] = t.eval("(()=>{const e=document.querySelector('#board .pcimg.animating');return e?e.style.transform:null;})()")
    time.sleep(0.12)
    res['dest_imgs_120ms'] = t.eval("(()=>{const x=document.querySelector('#board .sq[data-sq=\"d5\"]');return x?x.querySelectorAll('img').length:-1;})()")
    res['caught_120ms'] = t.eval("document.querySelectorAll('#board .pcimg.caught').length")
    time.sleep(0.6)
    res['dest_imgs_end'] = t.eval("(()=>{const x=document.querySelector('#board .sq[data-sq=\"d5\"]');return x?x.querySelectorAll('img').length:-1;})()")
    res['ghost_end'] = t.eval("document.querySelectorAll('#boardWrap .ghost, #rpBoardWrap .ghost').length")
    res['animating_end'] = t.eval("document.querySelectorAll('#board .pcimg.animating').length")
    res['caught_end'] = t.eval("document.querySelectorAll('#board .pcimg.caught').length")
    res['transform_stuck_end'] = t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.transform&&i.style.transform!=='').length")

    # rapid 5 moves back-to-back, then check no leftovers
    seq = [('g1','f3'),('g8','f6'),('b1','c3'),('b8','c6'),('f1','c4')]
    for f,to in seq:
        c(f); c(to)
    time.sleep(0.25)
    res['ghost_after_rapid'] = t.eval("document.querySelectorAll('#boardWrap .ghost, #rpBoardWrap .ghost').length")
    res['animating_after_rapid'] = t.eval("document.querySelectorAll('#board .pcimg.animating').length")
    time.sleep(1.2)
    res['animating_settled'] = t.eval("document.querySelectorAll('#board .pcimg.animating').length")
    res['transform_stuck_settled'] = t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.transform&&i.style.transform!=='').length")

    # animation OFF => no ghost/transform at all
    t.eval("(()=>{const b=document.getElementById('animBtn');if(b)b.click();return true;})()")
    res['animOn_after_toggle'] = t.eval("(()=>{try{return document.getElementById('animBtn').classList.contains('on3');}catch(e){return 'x';}})()")
    c('c4'); time.sleep(0.06); c('c5')  # some move; may be illegal depending turn -> just check no ghost
    res['ghost_animoff'] = t.eval("document.querySelectorAll('#boardWrap .ghost').length")
    res['animating_animoff'] = t.eval("document.querySelectorAll('#board .pcimg.animating').length")
    res['errs'] = t.eval("window.__errcap")

print(j(res))
