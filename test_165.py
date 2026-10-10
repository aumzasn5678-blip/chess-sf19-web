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
        "localStorage.setItem('chessHistSel',JSON.stringify(['g1']));}catch(e){}") % json.dumps(GAMES)

def thai(s): return sum(1 for ch in s if '\u0e00' <= ch <= '\u0e7f')
def mean_lum(b64):
    im = Image.open(io.BytesIO(base64.b64decode(b64))).convert('L')
    return round(ImageStat.Stat(im).mean[0], 2)

# JS helpers
JS_CNT_PICK = "(()=>{let n=0;document.querySelectorAll('#histList .histpick').forEach(p=>{const r=p.getBoundingClientRect();const cs=getComputedStyle(p);if(r.width>0&&r.height>0&&cs.display!=='none'&&cs.visibility!=='hidden')n++;});return {visible:n,cards:document.querySelectorAll('#histList .histItem').length};})()"
JS_STATE = "(()=>({sel:__chessDbg.histSel, mode:__chessDbg.histSelMode, selBtn:(document.getElementById('histSelect')||{}).textContent, act:(document.getElementById('histSelect')||{classList:{contains:()=>false}}).classList.contains('act'), statOpen:document.getElementById('statView').classList.contains('show')}))()"
JS_CARD_SEL = "(()=>{const its=document.querySelectorAll('#histList .histItem');return Array.from(its).map(i=>i.classList.contains('sel'));})()"
JS_OVER = "(()=>({vw:innerWidth,sw:document.documentElement.scrollWidth,over:document.documentElement.scrollWidth>innerWidth+1}))()"

def center(t, sel):
    return t.eval("(()=>{const e=document.querySelector(%s);if(!e)return null;const r=e.getBoundingClientRect();return {x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)};})()" % json.dumps(sel))

def real_click(t, x, y):
    t.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y, button='none')
    time.sleep(0.05)
    t.cmd('Input.dispatchMouseEvent', type='mousePressed', x=x, y=y, button='left', clickCount=1)
    t.cmd('Input.dispatchMouseEvent', type='mouseReleased', x=x, y=y, button='left', clickCount=1)

out = {}

# ============ PART 1: select mode @ 390px touch ============
with cdp.Tab(timeout=300) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd('Page.addScriptToEvaluateOnNewDocument', source=SEED)
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
    t.goto(URL, settle=3.5); time.sleep(1.0)

    t.eval("document.getElementById('bHist').click()"); time.sleep(0.6)
    out['t1_hist_open'] = t.eval("document.getElementById('histView').classList.contains('show')")
    out['t1_first_render'] = t.eval(JS_CNT_PICK)             # เกณฑ์ ข: visible ต้องเป็น 0
    out['t1_selbtn_label_th'] = t.eval("document.getElementById('histSelect').textContent")
    out['t1_seed_presel'] = t.eval(JS_STATE)['sel']           # selection เดิมจาก seed (g1) ควรมีก่อนกดเลือก
    out['t1_over_390_th'] = t.eval(JS_OVER)

    # กด 'เลือก'
    t.eval("document.getElementById('histSelect').click()"); time.sleep(0.45)
    out['t2_after_select'] = t.eval(JS_CNT_PICK)              # เกณฑ์ ค: visible = cards
    st = t.eval(JS_STATE); out['t2_state'] = st
    out['t2_card_sel'] = t.eval(JS_CARD_SEL)
    out['t2_has_pick_anim'] = t.eval("!!document.querySelector('#histView.picking')")  # picking อาจหมดอายุแล้ว; บันทึกเฉย ๆ

    # คลิกกลางการ์ด (ชื่อเกม) ของใบที่ 2 -> เลือก
    c = center(t, "#histList .histItem:nth-child(2) .histName")
    out['t3_click_pt'] = c
    real_click(t, c['x'], c['y']); time.sleep(0.3)
    out['t3_state'] = t.eval(JS_STATE)
    out['t3_card_sel'] = t.eval(JS_CARD_SEL)
    # คลิกซ้ำ -> ยกเลิก
    real_click(t, c['x'], c['y']); time.sleep(0.3)
    out['t4_state'] = t.eval(JS_STATE)
    out['t4_card_sel'] = t.eval(JS_CARD_SEL)

    # เลือกเกมที่ 1 ก่อน เพื่อทดสอบปุ่ม 'ดูสถิติ' ว่าไม่ใช่การเลือก
    c1 = center(t, "#histList .histItem:nth-child(1) .histName")
    real_click(t, c1['x'], c1['y']); time.sleep(0.25)
    out['t5_pre_state'] = t.eval(JS_STATE)
    # กดปุ่ม 'ดูสถิติ' ของการ์ดใบที่ 3 (ปุ่มที่ 2 ใน .histBtns)
    t.eval("document.querySelectorAll('#histList .histItem:nth-child(3) .histBtns button')[1].click()"); time.sleep(0.5)
    out['t6_after_stats'] = t.eval(JS_STATE)                  # statOpen ต้อง true, sel ต้องไม่เพิ่มขึ้น
    t.eval("document.getElementById('statClose').click()"); time.sleep(0.3)

    # ปุ่มส่งออก/คัดลอกที่เลือก ต้องเห็นเฉพาะในโหมด
    out['t7_selrow_inmode'] = t.eval("getComputedStyle(document.querySelector('.selonly-row')).display")
    out['t7_selall_inmode'] = t.eval("getComputedStyle(document.getElementById('histSelAll')).display")

    # กด 'เสร็จสิ้น' -> ออกโหมด
    t.eval("document.getElementById('histSelect').click()"); time.sleep(0.4)
    out['t8_after_done'] = t.eval(JS_CNT_PICK)
    out['t8_state'] = t.eval(JS_STATE)
    out['t8_selrow_out'] = t.eval("getComputedStyle(document.querySelector('.selonly-row')).display")
    out['t8_selall_out'] = t.eval("getComputedStyle(document.getElementById('histSelAll')).display")

    # ---- EN 390 ----
    t.eval("document.querySelector(\"#langbtns .lang[data-lang='en']\").click()"); time.sleep(0.6)
    out['t9_en_selbtn'] = t.eval("document.getElementById('histSelect').textContent")
    t.eval("document.getElementById('histSelect').click()"); time.sleep(0.4)
    out['t9_en_selbtn_mode'] = t.eval("document.getElementById('histSelect').textContent")
    out['t9_en_selall'] = t.eval("document.getElementById('histSelAll').textContent")
    out['t9_en_selnone'] = t.eval("document.getElementById('histSelNone').textContent")
    out['t9_en_over'] = t.eval(JS_OVER)
    out['t9_en_thai_in_histview'] = thai(t.eval("document.getElementById('histView').innerText"))
    t.eval("document.getElementById('histSelect').click()"); time.sleep(0.2)
    out['errors'] = t.eval("window.__errcap")

# ============ PART 2: hover @ desktop (real mouse) ============
BTNS = ['#bHist', '#bSaveHist', '#bRun', '#bTheme']
THEMES = ['', 'theme-bw', 'theme-brown']
JS_STYLE = ("(()=>{const e=document.querySelector(%s);if(!e)return null;const c=getComputedStyle(e);"
            "return {bg:c.backgroundColor,img:c.backgroundImage.slice(0,60),bc:c.borderColor,tr:c.transform,fl:c.filter};})()")
JS_HOVER_RULES = ("(()=>{let n=0,sel=[];for(const ss of document.styleSheets){let rs;try{rs=ss.cssRules}catch(e){continue}"
                  "for(const r of rs){const f=(x)=>{if(x.cssRules){for(const y of x.cssRules)f(y)}else if(x.selectorText&&x.selectorText.includes(':hover')&&x.selectorText.includes('button')){n++;sel.push(x.selectorText)}};f(r);}}return {n,sel:sel.slice(0,6)};})()")

with cdp.Tab(timeout=300) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=1000, height=820, deviceScaleFactor=1, mobile=False)
    t.cmd('Page.addScriptToEvaluateOnNewDocument', source=SEED)
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
    t.goto(URL, settle=3.5); time.sleep(1.0)
    out['hover_media'] = t.eval("({hover:matchMedia('(hover:hover)').matches, fine:matchMedia('(pointer:fine)').matches})")
    out['hover_rules'] = t.eval(JS_HOVER_RULES)

    def apply_theme(name):
        t.eval("(()=>{const b=document.body;b.className=b.className.replace(/theme-\\w+/g,'').trim();if(%s)b.classList.add(%s);})()" % (json.dumps(name) if name else 'false', json.dumps(name) if name else '""'))
        time.sleep(0.25)

    hover = {}
    for th in THEMES:
        apply_theme(th)
        key = th or 'default'
        hover[key] = {}
        for sel in BTNS:
            pt = center(t, sel)
            if not pt: continue
            # unhover first
            t.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=2, y=2, button='none'); time.sleep(0.25)
            before = t.eval(JS_STYLE % json.dumps(sel))
            shot_b = t.cmd('Page.captureScreenshot', format='png',
                           clip={'x': pt['x'] - 30, 'y': pt['y'] - 12, 'width': 60, 'height': 24, 'scale': 1})['data']
            t.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=pt['x'], y=pt['y'], button='none'); time.sleep(0.35)
            after = t.eval(JS_STYLE % json.dumps(sel))
            shot_a = t.cmd('Page.captureScreenshot', format='png',
                           clip={'x': pt['x'] - 30, 'y': pt['y'] - 12, 'width': 60, 'height': 24, 'scale': 1})['data']
            hover[key][sel] = {'before': before, 'after': after,
                               'lum_before': mean_lum(shot_b), 'lum_after': mean_lum(shot_a)}
    # unhover
    t.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=2, y=2, button='none'); time.sleep(0.2)
    # disabled button must not hover
    pt = center(t, '#bUndo')
    t.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=pt['x'], y=pt['y'], button='none'); time.sleep(0.3)
    out['hover_disabled_undo'] = t.eval(JS_STYLE % json.dumps('#bUndo'))
    out['hover_disabled_undo_flag'] = t.eval("document.getElementById('bUndo').disabled")
    out['hover_results'] = hover
    out['errors_desktop'] = t.eval("window.__errcap")

print(json.dumps(out, ensure_ascii=False, indent=1))
