import sys,time
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
TS=int(time.time())
URL='http://127.0.0.1:8100/index.html?v=%d'%TS
with cdp.Tab(timeout=200) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.goto(URL, settle=4.0); time.sleep(1.0)
    t.eval("document.querySelector(\"#langbtns .lang[data-lang='th']\").click()")
    time.sleep(0.6)
    t.eval("document.getElementById('bRun').click()"); time.sleep(2.0)
    t.eval("document.getElementById('bRun').click()"); time.sleep(0.3)
    png=t.shot(path=r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-162-390-th-order.png')
    print('shot', png)
