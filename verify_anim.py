#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json, os
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
OUT = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app\animtest"
os.makedirs(OUT, exist_ok=True)
TS = str(int(time.time()))
APP = "http://127.0.0.1:8100/index.html?v=" + TS
def j(o): return json.dumps(o, ensure_ascii=False)
SLOW = ("#board .pcimg.animating,#rpBoard .pcimg.animating{"
        "transition-duration:3s !important;transition-timing-function:linear !important}")
# stretch ONLY the 420ms safety-guard timeout so slow-motion can be observed fully
INIT = """
window.__errcap=[];
window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));
(function(){ const o=window.setTimeout;
  window.setTimeout=function(fn,d){ if(typeof d==='number'&&d>=400&&d<=500){ d=8000; }
    return o.apply(this,[fn,d]); };
})();
"""
PROBE = """(()=>{
  const b=document.querySelector('#board');
  const anim=b.querySelector('img.pcimg.animating');
  let ar=null;
  if(anim){const r=anim.getBoundingClientRect(); ar={sq:anim.closest('.sq').dataset.sq,
    left:Math.round(r.left),top:Math.round(r.top),tr:anim.style.transform,tx:getComputedStyle(anim).transform};}
  // duplicate detection: any two .pcimg whose rects overlap >50%
  const imgs=[...b.querySelectorAll('img.pcimg')].map(im=>{const r=im.getBoundingClientRect();
    return {sq:im.closest('.sq').dataset.sq,left:r.left,top:r.top,w:r.width,h:r.height};});
  let overlap=0;
  for(let i=0;i<imgs.length;i++)for(let k=i+1;k<imgs.length;k++){
    const a=imgs[i],b2=imgs[k];
    if(a.sq===b2.sq) continue;
    const ox=Math.max(0,Math.min(a.left+a.w,b2.left+b2.w)-Math.max(a.left,b2.left));
    const oy=Math.max(0,Math.min(a.top+a.h,b2.top+b2.h)-Math.max(a.top,b2.top));
    const inter=ox*oy, area=a.w*a.h;
    if(area>0 && inter/area>0.5) overlap++;
  }
  return {anim:ar, pieces:imgs.length, overlapPairs:overlap,
          animClass:anim?anim.className:null};
})()"""
res={}
with cdp.Tab(timeout=180) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APP, settle=2.0)
    t.eval("localStorage.clear()"); t.goto(APP, settle=2.0); time.sleep(0.4)
    t.eval("(()=>{const s=document.createElement('style');s.textContent=%s;document.head.appendChild(s);return 1;})()" % json.dumps(SLOW))
    def c(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()" % sq)
    def boardrect():
        return t.eval("(()=>{const r=document.querySelector('#board').getBoundingClientRect();return {x:r.left,y:r.top,w:r.width,h:r.height};})()")

    def capture_move(sel_sq,dest_sq,tag):
        br=boardrect()
        clip={"x":br["x"]-2,"y":br["y"]-2,"width":br["w"]+4,"height":br["h"]+4,"scale":2}
        c(sel_sq); time.sleep(0.06); c(dest_sq)
        frames=[]; prev=0.0
        for i,d in enumerate([0.02,0.35,0.8,1.4,2.2,2.9]):
            time.sleep(max(0,d-prev)); prev=d
            pr=t.eval(PROBE)
            path=os.path.join(OUT,f"{tag}-f{i}-{int(d*1000)}ms.png")
            r=t.cmd("Page.captureScreenshot", format="png", clip=clip)
            open(path,"wb").write(__import__("base64").b64decode(r["data"]))
            frames.append({"d":d,"probe":pr,"png":path})
        return frames

    res['frames_e4']=capture_move('e2','e4','fix-e4')
    time.sleep(3.2)
    res['animCount_after1']=t.eval("window.__chessDbg?window.__chessDbg.animCount:null")
    # capture move: 1...d5 then 2.exd5
    c('d7'); time.sleep(0.06); c('d5'); time.sleep(3.0)
    res['frames_exd5']=capture_move('e4','d5','fix-exd5')
    time.sleep(3.2)
    res['animCount_total']=t.eval("window.__chessDbg?window.__chessDbg.animCount:null")
    res['stuck_transform']=t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.transform&&i.style.transform!=='').length")
    res['stuck_willchange']=t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.willChange).length")
    res['animating_end']=t.eval("document.querySelectorAll('#board .pcimg.animating').length")
    res['caught_end']=t.eval("document.querySelectorAll('#board .pcimg.caught').length")
    res['ghosts']=t.eval("document.querySelectorAll('#boardWrap .ghost').length")
    res['errs']=t.eval("window.__errcap")

# compact print: per frame only anim rect + counts
summary={}
for key,frames in [('frames_e4',res.pop('frames_e4')),('frames_exd5',res.pop('frames_exd5'))]:
    summary[key]=[{"d":f["d"],"anim":f["probe"]["anim"],"pieces":f["probe"]["pieces"],
                   "overlap":f["probe"]["overlapPairs"],"cls":f["probe"]["animClass"],"png":os.path.basename(f["png"])} for f in frames]
print(j(summary))
print(j(res))
