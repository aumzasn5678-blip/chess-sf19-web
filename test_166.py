import sys, time, json, io, base64
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
from PIL import Image, ImageStat

TS = int(time.time())
URL = 'http://127.0.0.1:8100/index.html?v=%d' % TS
START = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
def game(i):
    return {'id': 'g%d' % i, 'name': 'เกม Test %d' % i, 'savedAt': 1700000000000 + i * 60000,
            'fens': [START], 'ucis': ['e2e4', 'e7e5'], 'grades': ['best', 'good'], 'flipped': False}
GAMES = [game(1), game(2), game(3)]
SEED = ("try{localStorage.setItem('chessHist',JSON.stringify(%s));"
        "localStorage.setItem('chessHistSel','[]');}catch(e){}") % json.dumps(GAMES)

def thai(s): return sum(1 for ch in s if '\u0e00' <= ch <= '\u0e7f')

JS_OVER = "(()=>({vw:innerWidth,sw:document.documentElement.scrollWidth,over:document.documentElement.scrollWidth>innerWidth+1}))()"
JS_CNT = "(()=>({games:(window.__chessDbg?window.__chessDbg.hist.length:'NO_DBG'),sel:(window.__chessDbg?window.__chessDbg.histSel.length:'-')}))()"
JS_DELSEL = ("(()=>{const b=document.getElementById('histDelSel');if(!b)return null;const cs=getComputedStyle(b);"
             "return {txt:b.textContent,disabled:b.disabled,bgimg:cs.backgroundImage.slice(0,70),bg:cs.backgroundColor,bc:cs.borderColor,col:cs.color};})()")
JS_BOX = ("(()=>{const b=document.getElementById('confirmDelSel');if(!b)return null;const cs=getComputedStyle(b);"
          "const msg=document.getElementById('confirmDelSelMsg');"
          "const y=getComputedStyle(document.getElementById('bDelSelYes')),n=getComputedStyle(document.getElementById('bDelSelNo'));"
          "return {disp:cs.display,borderColor:cs.borderColor,msg:msg?msg.textContent:null,"
          "yesBg:y.backgroundColor,yesImg:y.backgroundImage.slice(0,50),noBg:n.backgroundColor,noImg:n.backgroundImage.slice(0,50),"
          "top:Math.round(b.getBoundingClientRect().top)};})()")
JS_TOAST = "(()=>{const t=document.getElementById('toast');return {txt:t.textContent,show:t.classList.contains('show')};})()"

# audit every button in #histView: compare against a hidden probe (default button style)
JS_AUDIT = ("(()=>{const probe=document.createElement('button');probe.style.position='absolute';"
            "probe.style.visibility='hidden';document.body.appendChild(probe);"
            "const pc=getComputedStyle(probe);const DEFKEY=pc.backgroundImage+'|'+pc.backgroundColor+'|'+pc.borderColor;probe.remove();"
            "const out=[];document.querySelectorAll('#histView button').forEach(b=>{const cs=getComputedStyle(b);"
            "const key=cs.backgroundImage+'|'+cs.backgroundColor+'|'+cs.borderColor;"
            "out.push({id:b.id||('.'+(b.className.split(' ').filter(c=>c).join('.'))),txt:(b.textContent||'').slice(0,26),"
            "bgimg:cs.backgroundImage.slice(0,64),bg:cs.backgroundColor,bc:cs.borderColor,plain:(key===DEFKEY)});});"
            "return {defkey:DEFKEY.slice(0,64),out};})()")

def center(t, sel):
    return t.eval("(()=>{const e=document.querySelector(%s);if(!e)return null;const r=e.getBoundingClientRect();"
                  "return {x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};})()" % json.dumps(sel))

def key(t, name, code, vk):
    t.cmd('Input.dispatchKeyEvent', type='keyDown', key=name, code=code, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk)
    t.cmd('Input.dispatchKeyEvent', type='keyUp', key=name, code=code, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk)

out = {}

# ============ PART 1: delete-selected flow @ 390 ============
with cdp.Tab(timeout=300) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd('Page.addScriptToEvaluateOnNewDocument', source=SEED)
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
    t.goto(URL, settle=3.5); time.sleep(1.0)
    out['dbg_present'] = t.eval("typeof window.__chessDbg")
    # disable engine to avoid noise
    t.eval("try{document.getElementById('bRun')&&document.getElementById('bRun').click();}catch(e){}"); time.sleep(0.2)

    t.eval("document.getElementById('bHist').click()"); time.sleep(0.6)
    out['hist_open'] = t.eval("document.getElementById('histView').classList.contains('show')")
    out['pre_games'] = t.eval(JS_CNT)

    # enter select mode (clears selection)
    t.eval("document.getElementById('histSelect').click()"); time.sleep(0.45)
    out['d0_delsel_n0'] = t.eval(JS_DELSEL)                 # expect disabled, txt (0)
    out['d0_row_visible'] = t.eval("getComputedStyle(document.getElementById('histDelSel').closest('.selonly-row')).display")

    # select 2 games via cards
    t.eval("document.querySelectorAll('#histList .histItem')[0].click()"); time.sleep(0.15)
    t.eval("document.querySelectorAll('#histList .histItem')[1].click()"); time.sleep(0.25)
    out['d1_delsel_n2'] = t.eval(JS_DELSEL)                 # expect enabled, txt (2)
    out['d1_selcount'] = t.eval(JS_CNT)

    # click delete-selected -> confirm box
    t.eval("document.getElementById('histDelSel').click()"); time.sleep(0.3)
    out['d2_box'] = t.eval(JS_BOX)
    out['d2_games_still'] = t.eval(JS_CNT)

    # ESC = cancel, no deletion
    key(t, 'Escape', 'Escape', 27); time.sleep(0.35)
    out['d3_box_after_esc'] = t.eval(JS_BOX)
    out['d3_games_after_esc'] = t.eval(JS_CNT)

    # reopen + Enter = confirm
    t.eval("document.getElementById('histDelSel').click()"); time.sleep(0.3)
    out['d4_box_reopen'] = t.eval(JS_BOX)
    key(t, 'Enter', 'Enter', 13); time.sleep(0.5)
    out['d5_games_after_enter'] = t.eval(JS_CNT)
    out['d5_box_after_enter'] = t.eval(JS_BOX)
    out['d5_toast'] = t.eval(JS_TOAST)
    out['d5_delsel_after'] = t.eval(JS_DELSEL)              # back to 0 -> disabled

    # AUDIT colors of all #histView buttons
    out['audit'] = t.eval(JS_AUDIT)
    out['over_390_th'] = t.eval(JS_OVER)
    out['err_th'] = t.eval("window.__errcap")

# ============ PART 2: theme shift @ desktop ============
JS_STYLE = ("(()=>{const e=document.getElementById(%s);if(!e)return null;const c=getComputedStyle(e);"
            "return {bg:c.backgroundImage.slice(0,70),bc:c.borderColor,col:c.color};})()")
with cdp.Tab(timeout=300) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=1000, height=900, deviceScaleFactor=1, mobile=False)
    t.cmd('Page.addScriptToEvaluateOnNewDocument', source=SEED)
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
    t.goto(URL, settle=3.5); time.sleep(1.0)

    def apply_theme(cls):
        t.eval("(()=>{const b=document.body;b.classList.remove('theme-white','theme-bw','theme-brown','theme-green');if(%s)b.classList.add(%s);})()"
               % (json.dumps(cls) if cls else 'false', json.dumps(cls) if cls else '""'))
        time.sleep(0.25)

    theme_map = {'white(nibble)': 'theme-white', 'bw': 'theme-bw', 'brown': 'theme-brown', 'green': 'theme-green'}
    SELS = {'histExportAll(bOk)': 'histExportAll', 'histCopyAll(bTeal)': 'histCopyAll', 'histDelSel(bBad)': 'histDelSel'}
    out['theme_shift'] = {}
    for tname, cls in theme_map.items():
        apply_theme(cls)
        out['theme_shift'][tname] = {k: t.eval(JS_STYLE % json.dumps(v)) for k, v in SELS.items()}

    # hover test on desktop (semantic button) — border must stay semantic, bg brightness change via filter
    apply_theme('theme-white')
    t.eval("document.getElementById('bHist').click()"); time.sleep(0.5)
    t.eval("document.getElementById('histSelect').click()"); time.sleep(0.4)
    t.eval("document.querySelectorAll('#histList .histItem')[0].click()"); time.sleep(0.25)
    pt = center(t, '#histDelSel')
    t.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=2, y=2, button='none'); time.sleep(0.2)
    before = t.eval("(()=>{const c=getComputedStyle(document.getElementById('histDelSel'));return {bc:c.borderColor,fl:c.filter,tr:c.transform};})()")
    t.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=pt['x'], y=pt['y'], button='none'); time.sleep(0.35)
    after = t.eval("(()=>{const c=getComputedStyle(document.getElementById('histDelSel'));return {bc:c.borderColor,fl:c.filter,tr:c.transform};})()")
    out['hover_delsel'] = {'before': before, 'after': after, 'media': t.eval("({hover:matchMedia('(hover:hover)').matches,fine:matchMedia('(pointer:fine)').matches})")}
    # disabled has no hover: clear selection -> disabled
    t.eval("document.getElementById('histSelNone').click()"); time.sleep(0.3)
    out['disabled_state'] = t.eval("document.getElementById('histDelSel').disabled")
    pc = center(t, '#histDelSel')
    t.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=pc['x'], y=pc['y'], button='none'); time.sleep(0.3)
    out['hover_disabled'] = t.eval("(()=>{const c=getComputedStyle(document.getElementById('histDelSel'));return {fl:c.filter,op:c.opacity};})()")
    out['err_desktop'] = t.eval("window.__errcap")

print(json.dumps(out, ensure_ascii=False, indent=1))
