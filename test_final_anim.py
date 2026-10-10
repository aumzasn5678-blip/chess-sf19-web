#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
TS=str(int(time.time()))
APP="http://127.0.0.1:8100/index.html?v="+TS
def j(o): return json.dumps(o, ensure_ascii=False)
INIT="""
window.__errcap=[];
window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));
"""
PROBE="""(()=>{
  const b=document.querySelector('#board');
  const a=b.querySelector('img.pcimg.animating');
  let ar=null; let dx=null,dist=null;
  if(a){const r=a.getBoundingClientRect();const cs=getComputedStyle(a);
    const m=cs.transform.match(/matrix\\(([^)]+)\\)/);
    ar={sq:a.closest('.sq').dataset.sq,left:Math.round(r.left),top:Math.round(r.top)};
    if(m){const p=m[1].split(',').map(Number);dx={tx:p[4],ty:p[5]};dist=Math.hypot(p[4],p[5]);}}
  // overlap detection like before
  const imgs=[...b.querySelectorAll('img.pcimg')].map(im=>{const r=im.getBoundingClientRect();
    return {sq:im.closest('.sq').dataset.sq,left:r.left,top:r.top,w:r.width,h:r.height};});
  let ov=0;
  for(let i=0;i<imgs.length;i++)for(let k=i+1;k<imgs.length;k++){
    const A=imgs[i],B=imgs[k]; if(A.sq===B.sq)continue;
    const ox=Math.max(0,Math.min(A.left+A.w,B.left+B.w)-Math.max(A.left,B.left));
    const oy=Math.max(0,Math.min(A.top+A.h,B.top+B.h)-Math.max(A.top,B.top));
    if(A.w*A.h>0 && ox*oy/(A.w*A.h)>0.5) ov++;}
  return {anim:ar,dx:dx,dist:dist,pieces:imgs.length,overlap:ov};
})()"""
with cdp.Tab(timeout=180) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APP, settle=2.0)
    t.eval("localStorage.clear()"); t.goto(APP, settle=2.0); time.sleep(0.6)
    def c(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()" % sq)
    # square centers to know destination rect (via data-sq cells)
    def cellrect(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');const r=e.getBoundingClientRect();return {l:Math.round(r.left),t:Math.round(r.top)};})()"%sq)

    moves=[('e2','e4'),('e7','e5'),('g1','f3'),('b8','c6'),('f1','c4'),('g8','f6'),
           ('d2','d3'),('f8','c5'),('f3','e5'),('c6','e5')]  # last two = captures
    results=[]
    for idx,(f,to) in enumerate(moves):
        src=cellrect(f); dst=cellrect(to)
        c(f); time.sleep(0.05); c(to)
        pr=t.eval(PROBE)   # sample immediately (first animation frame)
        # expected: anim dist ~= full distance, and if 'to' is a knight/capture the piece cell is 'to'
        full=((src['l']-dst['l'])**2+(src['t']-dst['t'])**2)**0.5
        frac = (pr['dist']/full) if (pr['dist'] is not None and full>0) else None
        results.append({"ply":idx+1,"mv":f+to,"anim_sq":pr['anim']['sq'] if pr['anim'] else None,
                        "at_dest_cell":(pr['anim']['sq']==to) if pr['anim'] else None,
                        "dist":round(pr['dist'],1) if pr['dist'] is not None else None,
                        "full":round(full,1),"frac_from_source":round(frac,2) if frac is not None else None,
                        "pieces":pr['pieces'],"overlap":pr['overlap']})
        time.sleep(0.55)
    out={}
    out['moves']=results
    out['ucis']=t.eval("window.__chessDbg?window.__chessDbg.ucis:null")
    out['animCount']=t.eval("window.__chessDbg?window.__chessDbg.animCount:null")
    time.sleep(1.0)
    out['stuck_transform']=t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.transform&&i.style.transform!=='').length")
    out['stuck_willchange']=t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.willChange).length")
    out['animating_end']=t.eval("document.querySelectorAll('#board .pcimg.animating').length")
    out['caught_end']=t.eval("document.querySelectorAll('#board .pcimg.caught').length")
    out['ghosts']=t.eval("document.querySelectorAll('#boardWrap .ghost,#rpBoardWrap .ghost').length")
    out['pieces_final']=t.eval("document.querySelectorAll('#board .pcimg').length")
    out['errs']=t.eval("window.__errcap")
    print(j(out))
