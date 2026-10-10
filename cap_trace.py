#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
APPF="http://127.0.0.1:8100/index.html?v="
INIT=r"""
window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
window.__tl=[]; window.__mark=null; window.__redraws=0; window.__t0=0;
// sampler every animation frame
(function(){
  const board=()=>document.querySelector('#board');
  let lastNode=null;
  function tick(){
    const b=board();
    if(b){
      const a=b.querySelector('img.pcimg.animating');
      // detect full re-render: the img at destination node identity changes
      const e4=b.querySelector('.sq[data-sq="e4"] img.pcimg:not(.caught)');
      let dev=null,sx=null;
      if(e4){const cb=b.querySelector('.sq[data-sq="e4"]');const cr=cb.getBoundingClientRect();const r=e4.getBoundingClientRect();
        dev=Math.round(Math.hypot((r.left+r.width/2)-(cr.left+cr.width/2),(r.top+r.height/2)-(cr.top+cr.height/2)));
        const m=getComputedStyle(e4).transform.match(/matrix\(([^)]+)\)/);sx=m?+m[1].split(',')[0]:1;}
      if(e4!==lastNode){ if(lastNode) window.__redraws++; lastNode=e4; if(e4) e4.__id=Math.random().toString(36).slice(2,7); }
      window.__tl.push({t:Math.round(performance.now()-(window.__t0||performance.now())), live:!!a, dev:dev, sx:sx,
        id:e4?e4.__id:null, kids:b.children.length});
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
    t.eval("(()=>{const s=document.createElement('style');s.textContent='#board .pcimg.animating{transition-duration:3s !important;transition-timing-function:linear !important}';document.head.appendChild(s);return 1;})()")
    def click(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()"%sq)
    t.eval("window.__tl=[];window.__t0=performance.now()")
    click('e2'); time.sleep(0.08); click('e4')
    time.sleep(1.2)
    tl=t.eval("window.__tl.filter(x=>x.t<700)")
    print("redraws(identity changes)=",t.eval("window.__redraws"))
    for x in tl: print(x)
    print("errs=",t.eval("window.__errcap"))
