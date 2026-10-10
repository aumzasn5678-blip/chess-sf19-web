#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
TS=str(int(time.time())); APP="http://127.0.0.1:8100/index.html?v="+TS
def j(o): return json.dumps(o, ensure_ascii=False)
SLOW=("#board .pcimg.animating,#rpBoard .pcimg.animating{transition-duration:.9s !important}")
INIT="""window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));"""
# transform of animating piece (+ any translate) + duplicate/ghost detectors
SAMPLE="""(()=>{const b=document.querySelector('#board');
 const a=b.querySelector('img.pcimg.animating');
 let t=null;if(a){const cs=getComputedStyle(a);const m=cs.transform.match(/matrix\\(([^)]+)\\)/);
  const p=m?m[1].split(',').map(Number):[1,0,0,1,0,0];t={sq:a.closest('.sq').dataset.sq,tx:Math.round(p[4]),ty:Math.round(p[5]),sx:+p[0].toFixed(3),a:1};}
 const n=b.querySelectorAll('img.pcimg').length;
 // overlap pairs
 const imgs=[...b.querySelectorAll('img.pcimg')].map(im=>{const r=im.getBoundingClientRect();return {sq:im.closest('.sq').dataset.sq,l:r.left,t:r.top,w:r.width,h:r.height};});
 let ov=0;for(let i=0;i<imgs.length;i++)for(let k=i+1;k<imgs.length;k++){const A=imgs[i],B=imgs[k];if(A.sq===B.sq)continue;
  const ox=Math.max(0,Math.min(A.l+A.w,B.l+B.w)-Math.max(A.l,B.l)),oy=Math.max(0,Math.min(A.t+A.h,B.t+B.h)-Math.max(A.t,B.t));
  if(A.w*A.h>0&&ox*oy/(A.w*A.h)>0.5)ov++;}
 return {t:t,pieces:n,ov:ov};})()"""
with cdp.Tab(timeout=180) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APP, settle=2.0); t.eval("localStorage.clear()"); t.goto(APP, settle=2.0); time.sleep(0.6)
    t.eval("(()=>{const s=document.createElement('style');s.textContent=%s;document.head.appendChild(s);return 1;})()"%json.dumps(SLOW))
    def click(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()"%sq)
    # ---- test A: pop has NO translate; re-render mid-anim must not teleport ----
    click('e2'); time.sleep(0.06); click('e4')
    t0=time.time(); log=[]; fired=False
    while time.time()-t0<1.2:
        ms=(time.time()-t0)*1000
        if not fired and ms>=250: click('a8'); fired=True; log.append({"ms":round(ms),"EVENT":"mid re-render"})
        s=t.eval(SAMPLE); log.append({"ms":round(ms),"tr":s.get('t'),"pieces":s['pieces'],"ov":s['ov']}); time.sleep(0.02)
    tyvals=[e.get('tr')['ty'] for e in log if e.get('tr')]
    sxvals=[e.get('tr')['sx'] for e in log if e.get('tr')]
    A_ok = (all(v==0 for v in tyvals)) and (min(sxvals)<0.75) and (max(sxvals)>0.98) and (max(e.get('ov',0) for e in log)==0)
    print("A translate_ty_values=",tyvals)
    print("A scale_sx_values=",sxvals)
    print("A pop_ok(no_teleport,single)=",A_ok)
    # ---- test B: 10 moves incl 2 captures, undo/redo, replay ----
    moves=[('e2','e4'),('e7','e5'),('g1','f3'),('b8','c6'),('f1','c4'),('g8','f6'),('d2','d3'),('f8','c5'),('f3','e5'),('c6','e5')]
    for f,to in moves:
        click(f); time.sleep(0.05); click(to); time.sleep(0.35)
    time.sleep(0.5)
    d=t.eval("window.__chessDbg")
    out={}
    out['ucis']=t.eval("window.__chessDbg.ucis")
    out['animCount']=t.eval("window.__chessDbg.animCount")
    out['lastFen']=t.eval("window.__chessDbg.fens[window.__chessDbg.fens.length-1]")
    # undo x2, redo x2 via buttons
    t.eval("document.getElementById('bBack').click()"); time.sleep(0.2)
    t.eval("document.getElementById('bBack').click()"); time.sleep(0.3)
    out['ptr_after_undo']=t.eval("window.__chessDbg.ptr")
    t.eval("document.getElementById('bFwd').click()"); time.sleep(0.2)
    t.eval("document.getElementById('bFwd').click()"); time.sleep(0.3)
    out['ptr_after_redo']=t.eval("window.__chessDbg.ptr")
    # stuck / ghosts
    out['stuck_transform']=t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.transform&&i.style.transform!=='').length")
    out['stuck_willchange']=t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.willChange).length")
    out['stuck_opacity']=t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.opacity&&i.style.opacity!=='').length")
    out['animating_end']=t.eval("document.querySelectorAll('#board .pcimg.animating').length")
    out['caught_end']=t.eval("document.querySelectorAll('#board .pcimg.caught').length")
    out['ghosts']=t.eval("document.querySelectorAll('#boardWrap .ghost,#rpBoardWrap .ghost').length")
    out['errs']=t.eval("window.__errcap")
    print("B=",j(out))
