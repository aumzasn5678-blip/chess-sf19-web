#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time, json
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
APPF="http://127.0.0.1:8100/index.html?v="
def j(o): return json.dumps(o, ensure_ascii=False)
INIT="""window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));
window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));"""
with cdp.Tab(timeout=200) as t:
    t.cmd("Page.enable"); t.cmd("Runtime.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=INIT)
    t.goto(APPF+str(int(time.time())), settle=2.0); t.eval("localStorage.clear()"); t.goto(APPF+str(int(time.time())), settle=2.2); time.sleep(0.7)
    def click(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return 1;})()"%sq)
    def btn(idv): return t.eval("(()=>{const e=document.getElementById('%s');if(e)e.click();return !!e;})()"%idv)
    # play a few moves so hist/stats have content
    for f,to in [('e2','e4'),('e7','e5'),('g1','f3'),('b8','c6')]:
        click(f); time.sleep(0.05); click(to); time.sleep(0.3)
    time.sleep(0.4)
    out={}
    out['bHist']=btn('bHist'); time.sleep(0.5)
    out['histOpen']=t.eval("(()=>{const e=document.getElementById('histView');return e?e.classList.contains('show'):null;})()")
    t.eval("(()=>{const c=document.getElementById('histClose')||document.querySelector('#histView .close');if(c)c.click();return 1;})()"); time.sleep(0.3)
    out['bStats']=btn('bStats'); time.sleep(0.6)
    out['statsOpen']=t.eval("(()=>{const e=document.getElementById('statView');return e?e.classList.contains('show'):null;})()")
    t.eval("(()=>{const c=document.getElementById('statClose')||document.querySelector('#statView .close');if(c)c.click();return 1;})()"); time.sleep(0.3)
    out['bEdit']=btn('bEdit'); time.sleep(0.5)
    out['editOpen']=t.eval("(()=>{const e=document.getElementById('editView');return e?e.classList.contains('show'):null;})()")
    t.eval("(()=>{const c=document.getElementById('editClose')||document.querySelector('#editView .close');if(c)c.click();return 1;})()"); time.sleep(0.3)
    out['flip']=t.eval("(()=>{const e=document.getElementById('bFlip');if(e){e.click();return true;}return false;})()"); time.sleep(0.3)
    t.eval("(()=>{const e=document.getElementById('bFlip');if(e)e.click();return 1;})()"); time.sleep(0.3)
    # move after all that + undo/redo
    click('g2'); time.sleep(0.05); click('g3'); time.sleep(0.3)
    t.eval("document.getElementById('bBack').click()"); time.sleep(0.25)
    t.eval("document.getElementById('bFwd').click()"); time.sleep(0.25)
    out['animCount']=t.eval("window.__chessDbg.animCount")
    out['ptr']=t.eval("window.__chessDbg.ptr")
    out['stuck']=t.eval("[...document.querySelectorAll('#board .pcimg,#rpBoard .pcimg')].filter(i=>i.style.transform&&i.style.transform!=='').length")
    out['ghosts']=t.eval("document.querySelectorAll('#boardWrap .ghost,#rpBoardWrap .ghost').length")
    out['pieces']=t.eval("document.querySelectorAll('#board .pcimg').length")
    out['errs']=t.eval("window.__errcap")
    print(j(out))
