import sys,time
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
TS=int(time.time())
URL='http://127.0.0.1:8100/index.html?v=%d'%TS
with cdp.Tab(timeout=200) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.goto(URL, settle=4.0); time.sleep(1.0)
    t.eval("document.querySelector(\"#langbtns .lang[data-lang='en']\").click()"); time.sleep(0.5)
    t.eval("document.getElementById('bRun').click()"); time.sleep(0.9)
    png=t.shot(path=r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-163-390-en-status.png')
    print('shot',png)
