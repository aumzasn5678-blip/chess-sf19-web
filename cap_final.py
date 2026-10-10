#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os, base64
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
OUT=r"E:\Hermes_workbench\50_research\2026-10-10_chess-app\animtest"
os.makedirs(OUT, exist_ok=True)
APPF="http://127.0.0.1:8100/index.html?v="
INIT="""window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));"""
def run(t,tag,mid):
    t.goto(APPF+str(int(time.time()*1000)), settle=2.0); time.sleep(0.5)
    t.cmd("Network.enable"); t.cmd("Network.setBlockedURLs", urls=["*stockfish.js*","*stockfish.wasm*"])
    # stretch the CSS keyframe pop so 6 screenshots cover it
    t.eval("(()=>{const s=document.createElement('style');s.textContent='.sq.land img.pcimg:not(.caught){animation-duration:5s !important}';document.head.appendChild(s);return 1;})()")
    br=t.eval("(()=>{const r=document.querySelector('#board').getBoundingClientRect();return {x:r.left,y:r.top,w:r.width,h:r.height};})()")
    clip={"x":br["x"]-2,"y":br["y"]-2,"width":br["w"]+4,"height":br["h"]+4,"scale":1}
    def click(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()"%sq)
    click('e2'); time.sleep(0.08); click('e4')
    N=6; seq=[]
    for i in range(N):
        if mid and i==2: click('a8')     # force a re-render mid-pop
        r=t.cmd("Page.captureScreenshot",format="jpeg",quality=85,clip=clip)
        p=os.path.join(OUT,f"final-{tag}-{i}.jpg"); open(p,"wb").write(base64.b64decode(r["data"]))
        pr=t.eval("(()=>{const c=document.querySelector('#board .sq[data-sq=\"e4\"]');const im=c.querySelector('img.pcimg:not(.caught)');const cr=c.getBoundingClientRect();const rr=im.getBoundingClientRect();return {dev:Math.round(Math.hypot((rr.left+rr.width/2)-(cr.left+cr.width/2),(rr.top+rr.height/2)-(cr.top+cr.height/2))),land:c.classList.contains('land')};})()")
        seq.append((os.path.basename(p),pr))
    return seq
with cdp.Tab(timeout=260) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=1, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APPF+str(int(time.time())), settle=2.0); t.eval("localStorage.clear()"); time.sleep(0.3)
    print("plain:",run(t,"plain",False))
    print("midrender:",run(t,"midrender",True))
    print("errs=",t.eval("window.__errcap"))
