import sys,time
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
TS=int(time.time())
URL='https://aumzasn5678-blip.github.io/chess-sf19-web/index.html?v=%d'%TS
with cdp.Tab(timeout=200) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.goto(URL, settle=5.0); time.sleep(1.5)
    r=t.eval("(()=>{const g=id=>Math.round(document.getElementById(id).getBoundingClientRect().top);return {board:g('boardWrap'),eval:g('evalwrap'),depth:g('depthinfo'),nav:Math.round(document.getElementById('bStart').parentElement.getBoundingClientRect().top),order:g('boardWrap')<g('evalwrap')&&g('evalwrap')<g('depthinfo')&&g('depthinfo')<Math.round(document.getElementById('bStart').parentElement.getBoundingClientRect().top)};})()")
    print('LIVE',r)
