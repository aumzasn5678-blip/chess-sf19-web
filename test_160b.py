#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
TS = str(int(time.time())); APP = "http://127.0.0.1:8100/index.html?v=" + TS
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)
with cdp.Tab(timeout=200) as t:
    t.cmd("Page.enable")
    for th in ("bw", "brown"):
        t.goto(APP, settle=2.0)
        t.eval("(async()=>{try{const rs=await navigator.serviceWorker.getRegistrations();for(const r of rs)await r.unregister();}catch(e){}try{const ks=await caches.keys();for(const k of ks)await caches.delete(k);}catch(e){}try{localStorage.clear();localStorage.setItem('chessTheme','%s');}catch(e){}return true;})()" % th, await_promise=True)
        time.sleep(0.3); t.goto(APP, settle=2.0)
        t.wait("window.__chessDbg && window.__chessDbg.ready===true", timeout=25)
        t.eval("(()=>{const b=document.querySelector('.lang[data-lang=\"th\"]');b.click();return true;})()"); time.sleep(0.3)
        res[th] = t.eval("""(()=>{const b=document.querySelector('.lang.on[data-lang="th"]');const s=getComputedStyle(b);
          const en=document.querySelector('.lang.on[data-lang="en"]');
          return JSON.stringify({bodyclass:document.body.className,bgi:s.backgroundImage.slice(0,70),col:s.color,
            en_on: en? en.dataset.lang:null});})()""")
print(j(res))
