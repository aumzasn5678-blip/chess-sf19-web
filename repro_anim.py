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
INIT="""window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));"""
# sample the animating piece transform distance (px from origin) every ~20ms
SAMPLE="""(()=>{const a=document.querySelector('#board .pcimg.animating');if(!a)return null;
 const cs=getComputedStyle(a);const m=cs.transform.match(/matrix\\(([^)]+)\\)/);
 if(!m)return {d:null};const p=m[1].split(',').map(Number);return {d:Math.hypot(p[4],p[5]),sq:a.closest('.sq').dataset.sq};})()"""
with cdp.Tab(timeout=180) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APP, settle=2.0)
    t.eval("localStorage.clear()"); t.goto(APP, settle=2.0); time.sleep(0.5)
    t.eval("(()=>{const s=document.createElement('style');s.textContent=%s;document.head.appendChild(s);return 1;})()"%json.dumps(SLOW))
    def click(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()"%sq)
    # full distance e2->e4
    full=t.eval("""(()=>{const a=document.querySelector('#board .sq[data-sq="e2"]').getBoundingClientRect();
      const b=document.querySelector('#board .sq[data-sq="e4"]').getBoundingClientRect();
      return Math.hypot(a.left-b.left,a.top-b.top);})()""")
    click('e2'); time.sleep(0.06)
    # inject render() calls every 350ms during the slide -> simulates async grade/analysis re-render
    t.eval("""window.__rr=[];window.__rt=setInterval(()=>{try{window.render&&window.render();window.__rr.push(performance.now());}catch(e){}},350);1""")
    click('e4')
    samples=[]; t0=time.time()
    while time.time()-t0 < 1.4:
        s=t.eval(SAMPLE); samples.append({"t":round((time.time()-t0)*1000),**(s or {"d":None})}); time.sleep(0.02)
    t.eval("clearInterval(window.__rt)")
    # count how many times dist went back UP after decreasing (teleport signature)
    tele=0; mind=1e9
    for s in samples:
        d=s.get("d")
        if d is None: continue
        if d>mind+5 and mind<full*0.7: tele+=1
        mind=min(mind,d)
    print("full_dist=%.1f"%full)
    print("render_calls_injected=",t.eval("window.__rr.length"))
    print("teleport_rebounds=",tele)
    print("dist_series=",[s.get("d") and round(s["d"]) for s in samples])
    print("errs=",t.eval("window.__errcap"))
