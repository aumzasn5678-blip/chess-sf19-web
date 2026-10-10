#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os, base64
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
OUT=r"E:\Hermes_workbench\50_research\2026-10-10_chess-app\animtest"
os.makedirs(OUT, exist_ok=True)
TS=str(int(time.time())); APP="http://127.0.0.1:8100/index.html?v="+TS
def j(o): return json.dumps(o, ensure_ascii=False)
SLOW=("#board .pcimg.animating{transition-duration:3s !important;transition-timing-function:linear !important}")
INIT="""window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));"""
SAMPLE="""(()=>{const b=document.querySelector('#board');
 return [...b.querySelectorAll('img.pcimg')].map(im=>{const cs=getComputedStyle(im);const m=cs.transform.match(/matrix\\(([^)]+)\\)/);
  const p=m?m[1].split(',').map(Number):[1,0,0,1,0,0];
  return {sq:im.closest('.sq').dataset.sq,tx:Math.round(p[4]),ty:Math.round(p[5]),a:im.classList.contains('animating')?1:0};})
  .filter(o=>o.tx!==0||o.ty!==0||o.a);})()"""
with cdp.Tab(timeout=180) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APP, settle=2.0); t.eval("localStorage.clear()"); t.goto(APP, settle=2.0); time.sleep(0.5)
    t.eval("(()=>{const s=document.createElement('style');s.textContent=%s;document.head.appendChild(s);return 1;})()"%json.dumps(SLOW))
    br=t.eval("(()=>{const r=document.querySelector('#board').getBoundingClientRect();return {x:r.left,y:r.top,w:r.width,h:r.height};})()")
    clip={"x":br["x"]-2,"y":br["y"]-2,"width":br["w"]+4,"height":br["h"]+4,"scale":2}
    def click(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()"%sq)
    click('e2'); time.sleep(0.06)
    t.eval("""window.__rr=0;window.__rt=setInterval(()=>{try{window.render&&window.render();window.__rr++;}catch(e){}},350);1""")
    click('e4')
    log=[]; t0=time.time(); shots=0
    while time.time()-t0 < 1.5:
        ms=round((time.time()-t0)*1000)
        s=t.eval(SAMPLE)
        log.append({"t":ms,"els":s})
        if ms in (30,120,300,420,700,1000) or (shots<6 and len(log)>1):
            pass
        time.sleep(0.025)
    t.eval("clearInterval(window.__rt)")
    for e in log: print(json.dumps(e,ensure_ascii=False))
    print("render_injected=",t.eval("window.__rr"),"errs=",t.eval("window.__errcap"))
