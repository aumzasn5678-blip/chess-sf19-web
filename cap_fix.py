#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os, base64
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
OUT=r"E:\Hermes_workbench\50_research\2026-10-10_chess-app\animtest"
os.makedirs(OUT, exist_ok=True)
TS=str(int(time.time())); APP="http://127.0.0.1:8100/index.html?v="+TS
def j(o): return json.dumps(o, ensure_ascii=False)
INIT="""window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
(function(){const o=window.setTimeout;window.setTimeout=function(fn,d){if(typeof d==='number'&&d>=350&&d<=500)d=9000;return o.apply(this,[fn,d]);};})();"""
def probe(dest,origin):
    return ("""(function(){const D="%s",O="%s";
 const cb=document.querySelector('#board .sq[data-sq="'+D+'"]');const cr=cb.getBoundingClientRect();
 const ccx=cr.left+cr.width/2, ccy=cr.top+cr.height/2;
 const im=cb.querySelector('img.pcimg:not(.caught)');
 let dev=null,sx=null;
 if(im){const r=im.getBoundingClientRect();dev=Math.round(Math.hypot((r.left+r.width/2)-ccx,(r.top+r.height/2)-ccy));const m=getComputedStyle(im).transform.match(/matrix\\(([^)]+)\\)/);sx=m?+m[1].split(',')[0]:1;}
 let maxoff=0;
 for(const im2 of document.querySelectorAll('#board .pcimg:not(.caught)')){const c=im2.closest('.sq').getBoundingClientRect();const rr=im2.getBoundingClientRect();
  const d=Math.hypot((rr.left+rr.width/2)-(c.left+c.width/2),(rr.top+rr.height/2)-(c.top+c.height/2));if(d>maxoff)maxoff=Math.round(d);}
 const ob=document.querySelector('#board .sq[data-sq="'+O+'"]');const originEmpty=!ob.querySelector('img.pcimg:not(.caught)');
 return {dev:dev,sx:sx,maxoff:maxoff,originEmpty:originEmpty,pieces:document.querySelectorAll('#board .pcimg').length};})()""")%(dest,origin)
def shot(t,clip,name):
    r=t.cmd("Page.captureScreenshot",format="png",clip=clip)
    p=os.path.join(OUT,name); open(p,"wb").write(base64.b64decode(r["data"])); return p
with cdp.Tab(timeout=180) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APP, settle=2.0); t.eval("localStorage.clear()"); t.goto(APP, settle=2.0); time.sleep(0.6)
    def click(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()"%sq)
    br=t.eval("(()=>{const r=document.querySelector('#board').getBoundingClientRect();return {x:r.left,y:r.top,w:r.width,h:r.height};})()")
    clip={"x":br["x"]-2,"y":br["y"]-2,"width":br["w"]+4,"height":br["h"]+4,"scale":1}
    # ================= A: numeric proof, real speed, NO screenshots =================
    t.eval("(()=>{const s=document.createElement('style');s.textContent='#board .pcimg.animating{transition-duration:.45s !important}';document.head.appendChild(s);return 1;})()")
    P=probe('e4','e2')
    click('e2'); time.sleep(0.06); click('e4')
    t0=time.time(); nums=[]
    while time.time()-t0<0.6: nums.append((round((time.time()-t0)*1000),t.eval(P))); time.sleep(0.02)
    print("A1 pop e2e4  (ms,dev,scale,maxoff,originEmpty):",[(m,n['dev'],n['sx'],n['maxoff'],n['originEmpty']) for m,n in nums])
    a_ok = all(n['dev']==0 and n['maxoff']==0 for m,n in nums) and any((n['sx'] or 1)<0.8 for m,n in nums) and all(n['originEmpty'] for m,n in nums)
    print("A1 no_teleport(dev&maxoff always 0) + origin_empty + started_shrunk =",a_ok)
    time.sleep(0.5)
    # A2 pop with mid re-render (white move e2-e4, then mid-anim click to force render)
    click('e2'); time.sleep(0.06); click('e4')
    t0=time.time(); nums2=[]; fired=False
    while time.time()-t0<0.6:
        ms=round((time.time()-t0)*1000)
        if not fired and ms>=150: click('a8'); fired=True
        nums2.append((ms,t.eval(P))); time.sleep(0.02)
    print("A2 pop + mid-render: (ms,dev,maxoff):",[(m,n['dev'],n['maxoff']) for m,n in nums2])
    a2_ok=all(n['dev']==0 and n['maxoff']==0 for m,n in nums2)
    print("A2 no_teleport_despite_mid_render =",a2_ok)
    # ================= B: slow-mo proof screenshots (>=5 frames) =================
    t.eval("(()=>{const s=document.createElement('style');s.textContent='#board .pcimg.animating{transition-duration:2.6s !important;transition-timing-function:linear !important}';document.head.appendChild(s);return 1;})()")
    click('e2'); time.sleep(0.06); click('e4')
    t0=time.time(); shotn=0; seq=[]
    while shotn<7 and time.time()-t0<3.0:
        s=shot(t,clip,f"proof-fix-e4-{shotn}.png"); seq.append(t.eval(P)); shotn+=1; time.sleep(0.15)
    print("B proof shots=",shotn,"dev_series=",[s['dev'] for s in seq],"scale_series=",[s['sx'] for s in seq])
    # mid-render slow-mo variant
    time.sleep(0.4)
    click('d2'); time.sleep(0.06); click('d4')  # still white? after e4 it's black -> use non-move to avoid illegal
    print("note: B used white e2e4 only; extra variants below")
    print("errs=",t.eval("window.__errcap"))
