#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os, base64
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
OUT=r"E:\Hermes_workbench\50_research\2026-10-10_chess-app\animtest"
os.makedirs(OUT, exist_ok=True)
APPF="http://127.0.0.1:8100/index.html?v="
INIT=r"""
window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
window.__tl=[];
(function(){
  const dest='e4';
  function tick(){
    const b=document.querySelector('#board');
    if(b){
      const cell=b.querySelector('.sq[data-sq="'+dest+'"]');
      const img=cell?cell.querySelector('img.pcimg:not(.caught)'):null;
      let dev=null,sx=null,land=cell?cell.classList.contains('land'):null;
      if(img){const r=img.getBoundingClientRect();const cr=cell.getBoundingClientRect();
        dev=Math.round(Math.hypot((r.left+r.width/2)-(cr.left+cr.width/2),(r.top+r.height/2)-(cr.top+cr.height/2)));
        const m=getComputedStyle(img).transform.match(/matrix\(([^)]+)\)/);sx=m?+m[1].split(',')[0]:1;}
      window.__tl.push({t:Math.round(performance.now()),dev:dev,sx:sx,land:land});
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
"""
with cdp.Tab(timeout=200) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=1, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APPF+str(int(time.time())), settle=2.0); t.eval("localStorage.clear()"); t.goto(APPF+str(int(time.time())), settle=2.2); time.sleep(0.6)
    # slow the CSS keyframe animation so >=5 frames are captured; and block engine to remove interference
    t.cmd("Network.enable"); t.cmd("Network.setBlockedURLs", urls=["*stockfish.js*","*stockfish.wasm*"])
    t.eval("(()=>{const s=document.createElement('style');s.textContent='.sq.land img.pcimg:not(.caught){animation-duration:2.2s !important}';document.head.appendChild(s);return 1;})()")
    br=t.eval("(()=>{const r=document.querySelector('#board').getBoundingClientRect();return {x:r.left,y:r.top,w:r.width,h:r.height};})()")
    clip={"x":br["x"]-2,"y":br["y"]-2,"width":br["w"]+4,"height":br["h"]+4,"scale":1}
    def click(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()"%sq)
    t.eval("window.__tl=[];")
    click('e2'); time.sleep(0.08); click('e4')
    time.sleep(2.4)
    tl=t.eval("window.__tl")
    # keep only frames around the move (dev not null) and dedupe by scale change
    fr=[x for x in tl if x['dev'] is not None]
    print("total_frames_with_piece=",len(fr))
    print("first 30:",[(x['t'],x['dev'],round(x['sx'],3),x['land']) for x in fr[:30]])
    print("distinct scales=",sorted(set(round(x['sx'],2) for x in fr)))
    print("dev set=",sorted(set(x['dev'] for x in fr)))
    print("errs=",t.eval("window.__errcap"))
