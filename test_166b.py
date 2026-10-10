import sys, time, json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp

TS = int(time.time())
URL = 'http://127.0.0.1:8100/index.html?v=%d' % TS
START = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
GAMES = [{'id': 'g%d' % i, 'name': 'gm%d' % i, 'savedAt': 1700000000000 + i * 60000,
          'fens': [START], 'ucis': ['e2e4', 'e7e5'], 'grades': ['best', 'good'], 'flipped': False} for i in (1, 2)]
SEED = "try{localStorage.setItem('chessHist',JSON.stringify(%s));}catch(e){}" % json.dumps(GAMES)

# audit visible buttons under a given root against the probe default-style; ignore hidden (display:none / 0-size)
JS_AUDIT = ("(()=>{const root=document.querySelector(%s)||document.body;"
            "const probe=document.createElement('button');probe.style.position='absolute';probe.style.visibility='hidden';"
            "root.appendChild(probe);const pc=getComputedStyle(probe);const DK=pc.backgroundImage+'|'+pc.backgroundColor+'|'+pc.borderColor;probe.remove();"
            "const out=[];root.querySelectorAll('button').forEach(b=>{const r=b.getBoundingClientRect();if(r.width<2)return;"
            "const cs=getComputedStyle(b);const key=cs.backgroundImage+'|'+cs.backgroundColor+'|'+cs.borderColor;"
            "if(key===DK)out.push({id:b.id||('.'+b.className.split(' ').filter(c=>c).join('.')),txt:(b.textContent||'').slice(0,24)});});"
            "return {total:root.querySelectorAll('button').length, plain:out};})()")

out = {}
with cdp.Tab(timeout=300) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=1000, height=900, deviceScaleFactor=1, mobile=False)
    t.cmd('Page.addScriptToEvaluateOnNewDocument', source=SEED)
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
    t.goto(URL, settle=3.5); time.sleep(1.0)
    t.eval("try{document.getElementById('bRun').click();}catch(e){}"); time.sleep(0.2)

    # settings panel open
    t.eval("document.getElementById('bSettings').click()"); time.sleep(0.3)
    out['settings'] = t.eval(JS_AUDIT % json.dumps('#settings'))
    out['app_main'] = t.eval(JS_AUDIT % json.dumps('#app'))
    t.eval("document.getElementById('bSettings').click()"); time.sleep(0.2)

    # EDIT view
    t.eval("document.getElementById('bEdit').click()"); time.sleep(0.6)
    out['edit_open'] = t.eval("document.getElementById('editView').classList.contains('show')")
    out['edit'] = t.eval(JS_AUDIT % json.dumps('#editView'))
    t.eval("document.getElementById('editBack').click()"); time.sleep(0.4)

    # replay view (via history -> open replay)
    t.eval("document.getElementById('bHist').click()"); time.sleep(0.5)
    t.eval("document.querySelectorAll('#histList .histBtns button')[0].click()"); time.sleep(0.9)
    out['replay_open'] = t.eval("document.getElementById('replayView').classList.contains('show')")
    out['replay'] = t.eval(JS_AUDIT % json.dumps('#replayView'))
    t.eval("document.getElementById('rpClose').click()"); time.sleep(0.3)

    out['errcap'] = t.eval("window.__errcap")

print(json.dumps(out, ensure_ascii=False, indent=1))
