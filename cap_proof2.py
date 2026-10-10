#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os, base64
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
OUT=r"E:\Hermes_workbench\50_research\2026-10-10_chess-app\animtest"
os.makedirs(OUT, exist_ok=True)
APPF="http://127.0.0.1:8100/index.html?v="
INIT="""window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));"""
PROBE="""(()=>{const a=document.querySelector('#board .pcimg.animating');
 const cb=document.querySelector('#board .sq[data-sq="e4"]');const cr=cb.getBoundingClientRect();const ccx=cr.left+cr.width/2,ccy=cr.top+cr.height/2;
 const im=cb.querySelector('img.pcimg:not(.caught)');let dev=null,sx=null;
 if(im){const r=im.getBoundingClientRect();dev=Math.round(Math.hypot((r.left+r.width/2)-ccx,(r.top+r.height/2)-ccy));const m=getComputedStyle(im).transform.match(/matrix\\(([^)]+)\\)/);sx=m?+m[1].split(',')[0]:1;}
 let maxoff=0;for(const i of document.querySelectorAll('#board .pcimg:not(.caught)')){const c=i.closest('.sq').getBoundingClientRect();const rr=i.getBoundingClientRect();
  const d=Math.hypot((rr.left+rr.width/2)-(c.left+c.width/2),(rr.top+rr.height/2)-(c.top+c.height/2));if(d>maxoff)maxoff=Math.round(d);}
 return {live:!!a,dev:dev,sx:sx,maxoff:maxoff,pieces:document.querySelectorAll('#board .pcimg').length};})()"""
with cdp.Tab(timeout=180) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=1, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APPF+str(int(time.time())), settle=2.0); t.eval("localStorage.clear()"); t.goto(APPF+str(int(time.time())), settle=2.2); time.sleep(0.6)
    # stretch the pop to 2s (only duration matters)
    t.eval("(()=>{const s=document.createElement('style');s.textContent='#board .pcimg.animating{transition-duration:2s !important;transition-timing-function:linear !important}';document.head.appendChild(s);return 1;})()")
    br=t.eval("(()=>{const r=document.querySelector('#board').getBoundingClientRect();return {x:r.left,y:r.top,w:r.width,h:r.height};})()")
    clip={"x":br["x"]-2,"y":br["y"]-2,"width":br["w"]+4,"height":br["h"]+4,"scale":1}
    def click(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()"%sq)
    click('e2'); time.sleep(0.08); click('e4')
    t0=time.time(); n=0; seq=[]
    while n<8 and (time.time()-t0)<2.2:
        ms=round((time.time()-t0)*1000)
        pr=t.eval(PROBE)
        r=t.cmd("Page.captureScreenshot",format="jpeg",quality=80,clip=clip)
        p=os.path.join(OUT,f"proof2-{n}.jpg"); open(p,"wb").write(base64.b64decode(r["data"]))
        seq.append((ms,pr)); n+=1
    for m,s in seq: print(m,s)
    print("errs=",t.eval("window.__errcap"))
