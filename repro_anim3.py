#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
TS=str(int(time.time())); APP="http://127.0.0.1:8100/index.html?v="+TS
def j(o): return json.dumps(o, ensure_ascii=False)
SLOW=("#board .pcimg.animating{transition-duration:1.5s !important;transition-timing-function:linear !important}")
INIT="""window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
(function(){const o=window.setTimeout;window.setTimeout=function(fn,d){if(typeof d==='number'&&d>=400&&d<=500)d=9000;return o.apply(this,[fn,d]);};})();"""
SAMPLE="""(()=>{const b=document.querySelector('#board');
 return [...b.querySelectorAll('img.pcimg')].map(im=>{const cs=getComputedStyle(im);const m=cs.transform.match(/matrix\\(([^)]+)\\)/);
  const p=m?m[1].split(',').map(Number):[1,0,0,1,0,0];
  return {sq:im.closest('.sq').dataset.sq,ty:Math.round(p[5]||0),a:im.classList.contains('animating')?1:0};})
  .filter(o=>o.ty!==0||o.a);})()"""
with cdp.Tab(timeout=180) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APP, settle=2.0); t.eval("localStorage.clear()"); t.goto(APP, settle=2.0); time.sleep(0.5)
    t.eval("(()=>{const s=document.createElement('style');s.textContent=%s;document.head.appendChild(s);return 1;})()"%json.dumps(SLOW))
    def click(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()"%sq)
    click('e2'); time.sleep(0.06); click('e4')
    t0=time.time(); done=False; log=[]
    while time.time()-t0 < 2.2:
        ms=(time.time()-t0)*1000
        if not done and ms>=400:   # inject ONE render mid-slide (~27% through 1.5s)
            t.eval("window.render&&window.render()"); done=True; log.append({"t":round(ms),"EVENT":"render()"})
        s=t.eval(SAMPLE); log.append({"t":round(ms),"els":s}); time.sleep(0.03)
    for e in log: print(json.dumps(e,ensure_ascii=False))
    print("errs=",t.eval("window.__errcap"))
