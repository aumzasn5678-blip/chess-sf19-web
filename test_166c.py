import sys, time, json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp

TS = int(time.time())
URL = 'http://127.0.0.1:8100/index.html?v=%d' % TS
START = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
GAMES = [{'id': 'g%d' % i, 'name': 'เกมทดสอบ %d' % i, 'savedAt': 1700000000000 + i * 60000,
          'fens': [START], 'ucis': ['e2e4', 'e7e5'], 'grades': ['best', 'good'], 'flipped': False} for i in (1, 2, 3)]
SEED = "try{localStorage.setItem('chessHist',JSON.stringify(%s));localStorage.setItem('chessHistSel','[]');}catch(e){}" % json.dumps(GAMES)
def thai(s): return sum(1 for ch in s if '\u0e00' <= ch <= '\u0e7f')

out = {}
with cdp.Tab(timeout=300) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd('Page.addScriptToEvaluateOnNewDocument', source=SEED)
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
    t.goto(URL, settle=3.5); time.sleep(1.0)
    t.eval("try{document.getElementById('bRun').click();}catch(e){}"); time.sleep(0.2)
    t.eval("document.getElementById('bHist').click()"); time.sleep(0.5)
    t.eval("document.getElementById('histSelect').click()"); time.sleep(0.4)
    t.eval("document.querySelectorAll('#histList .histItem')[0].click()"); time.sleep(0.15)
    t.eval("document.querySelectorAll('#histList .histItem')[1].click()"); time.sleep(0.25)
    # force THAI UI
    t.eval("document.querySelector(\"#langbtns .lang[data-lang='th']\").click()"); time.sleep(0.5)
    t.eval("document.getElementById('histSelect').click()"); time.sleep(0.3)   # exit+re-enter (selection cleared)
    t.eval("document.getElementById('histSelect').click()"); time.sleep(0.3)
    t.eval("document.querySelectorAll('#histList .histItem')[0].click()"); time.sleep(0.15)
    t.eval("document.querySelectorAll('#histList .histItem')[1].click()"); time.sleep(0.25)
    import base64
    # screenshot: select mode row
    shot1 = t.cmd('Page.captureScreenshot', format='png')['data']
    open('shot-166-selmode-th.png', 'wb').write(base64.b64decode(shot1))
    # TH texts
    out['th_delsel'] = t.eval("document.getElementById('histDelSel').textContent")
    out['th_confirm'] = None
    t.eval("document.getElementById('histDelSel').click()"); time.sleep(0.35)
    out['th_confirm'] = t.eval("document.getElementById('confirmDelSelMsg').textContent")
    shot2 = t.cmd('Page.captureScreenshot', format='png')['data']
    open('shot-166-confirmbox-th.png', 'wb').write(base64.b64decode(shot2))
    t.eval("document.getElementById('bDelSelNo').click()"); time.sleep(0.2)
    # EN
    t.eval("document.querySelector(\"#langbtns .lang[data-lang='en']\").click()"); time.sleep(0.5)
    out['en_delsel'] = t.eval("document.getElementById('histDelSel').textContent")
    t.eval("document.getElementById('histDelSel').click()"); time.sleep(0.3)
    out['en_confirm'] = t.eval("document.getElementById('confirmDelSelMsg').textContent")
    out['en_thai_in_histview_all'] = thai(t.eval("document.getElementById('histView').innerText"))
    out['en_thai_ui_only'] = thai(t.eval("(()=>{let s='';document.querySelectorAll('#histView button,#histView .cardtitle,#histView label').forEach(e=>s+=e.textContent);return s;})()"))
    # restore TH for screenshot naming sanity
    out['en_over_390'] = t.eval("(()=>({vw:innerWidth,sw:document.documentElement.scrollWidth,over:document.documentElement.scrollWidth>innerWidth+1}))()")
    t.eval("document.getElementById('bDelSelNo').click()"); time.sleep(0.2)
    out['errcap'] = t.eval("window.__errcap")
print(json.dumps(out, ensure_ascii=False, indent=1))
