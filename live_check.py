import sys,time,json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
LIVE='https://aumzasn5678-blip.github.io/chess-sf19-web/index.html?live=%d'%int(time.time())
INIT='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));'
P=('(()=>{const c=document.querySelector(\'#board .sq[data-sq="e4"]\');if(!c)return null;'
   'const im=c.querySelector("img.pcimg:not(.caught)");const cr=c.getBoundingClientRect();'
   'let dev=null,sx=null;if(im){const r=im.getBoundingClientRect();'
   'dev=Math.round(Math.hypot((r.left+r.width/2)-(cr.left+cr.width/2),(r.top+r.height/2)-(cr.top+cr.height/2)));'
   'const m=getComputedStyle(im).transform.match(/matrix\\(([^)]+)\\)/);sx=m?+m[1].split(",")[0]:1;}'
   'return {dev:dev,sx:sx,land:c.classList.contains("land")};})()')
def c(t,sq): return t.eval('(()=>{const e=document.querySelector(\'#board .sq[data-sq="%s"]\');if(e)e.click();return 1;})()'%sq)
with cdp.Tab(timeout=200) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd('Page.addScriptToEvaluateOnNewDocument', source=INIT)
    t.goto(LIVE, settle=4.0); time.sleep(1.2)
    c(t,'e2'); time.sleep(0.06); c(t,'e4')
    samples=[]
    for i in range(8):
        samples.append(t.eval(P)); time.sleep(0.03)
    print('live_samples=',samples)
    # 2 more moves + undo/redo
    c(t,'e7'); time.sleep(0.05); c(t,'e5'); time.sleep(0.3)
    c(t,'g1'); time.sleep(0.05); c(t,'f3'); time.sleep(0.3)
    t.eval("document.getElementById('bBack').click()"); time.sleep(0.25)
    t.eval("document.getElementById('bFwd').click()"); time.sleep(0.25)
    print('ptr=',t.eval("window.__chessDbg?window.__chessDbg.ptr:null"))
    print('animCount=',t.eval("window.__chessDbg?window.__chessDbg.animCount:null"))
    print('stuck=',t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.transform&&i.style.transform!=='').length"))
    print('errs=',t.eval('window.__errcap'))
