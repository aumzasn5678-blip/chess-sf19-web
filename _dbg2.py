import sys,time,json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
APP='http://127.0.0.1:8100/index.html?v=%d'%(int(time.time()))
def c(t,sq): return t.eval('(()=>{const e=document.querySelector(\'#board .sq[data-sq="%s"]\');if(e)e.click();return 1;})()'%sq)
with cdp.Tab(timeout=120) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=1, mobile=True)
    t.goto(APP, settle=1.8); t.eval('localStorage.clear()'); t.goto(APP, settle=1.8); time.sleep(0.4)
    t.eval("(()=>{const s=document.createElement('style');s.textContent='#board .pcimg.animating{transition-duration:3s !important;transition-timing-function:linear !important}';document.head.appendChild(s);return 1;})()")
    c(t,'e2'); time.sleep(0.06); c(t,'e4')
    for i in range(12):
        r=t.eval("(()=>{const a=document.querySelector('#board .pcimg.animating');if(!a)return 'GONE';const cs=getComputedStyle(a);return {dur:cs.transitionDuration,prop:cs.transitionProperty,tr:cs.transform.match(/matrix\\(([^)]+)\\)/)?+cs.transform.match(/matrix\\(([^)]+)\\)/)[1].split(',')[0]:cs.transform};})()")
        print(i,r); time.sleep(0.03)
