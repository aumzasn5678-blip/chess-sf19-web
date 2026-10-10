import sys, time, json, re
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
TS = int(time.time())
URL = 'http://127.0.0.1:8100/index.html?v=%d' % TS
SW = r'กำลังคิด|เพดาน|พร้อม|ลึก|หยุดแล้ว|เกมใหม่|Thinking|Ready|depth|cap|Stopped|New game'
COUNT = """(()=>{const w=%s;const ev=document.getElementById('evalwrap').getBoundingClientRect();
 const navT=document.getElementById('bStart').parentElement.getBoundingClientRect().top;const vis=[];
 document.querySelectorAll('body *').forEach(e=>{if(e.children.length)return;const r=e.getBoundingClientRect();
  if(r.width===0&&r.height===0)return;const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')return;
  if(r.bottom<ev.bottom-2||r.top>navT+2)return;const s=(e.textContent||'').trim();if(!s)return;
  if(!new RegExp(w,'i').test(s))return;vis.push({id:e.id||null,txt:s});});
 return {n:vis.length,items:vis,vw:innerWidth,scrollW:document.documentElement.scrollWidth};})()""" % json.dumps(SW)
def txt(t): return t.eval("document.getElementById('depthinfo').textContent.trim()")
def thai(s): return sum(1 for ch in s if '\u0e00' <= ch <= '\u0e7f')

out = {}
with cdp.Tab(timeout=260) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
    t.goto(URL, settle=4.0); time.sleep(1.5)
    t.eval("document.querySelector(\"#langbtns .lang[data-lang='th']\").click()"); time.sleep(0.5)
    out['th_boot_text'] = txt(t); c = t.eval(COUNT); out['th_boot_count'] = c['n']; out['th_boot_items'] = c['items']

    # EN thinking (fresh, no pending flash)
    t.eval("(()=>{const b=document.querySelector('#langbtns .lang[data-lang=\\'en\\']');if(b)b.click();})()"); time.sleep(3.0)
    t.eval("document.getElementById('bRun').click()")
    en = []
    for i in range(7):
        time.sleep(0.6); en.append(txt(t))
    out['en_thinking_samples'] = en
    out['en_thinking_match'] = [bool(re.match(r'^Thinking… \d+/20 · cap [\d.]+s$', s)) for s in en]
    out['en_thinking_thai'] = [thai(s) for s in en]
    ce = t.eval(COUNT); out['en_count'] = ce['n']; out['en_items'] = ce['items']; out['en_overflow'] = ce['scrollW'] > ce['vw']
    t.eval("document.getElementById('bRun').click()"); time.sleep(0.3)
    out['en_stop'] = txt(t)
    back = None
    for i in range(10):
        time.sleep(0.4); v = txt(t)
        if re.match(r'^Ready · depth \d+$', v): back = round(0.3 + (i+1)*0.4, 2); out['en_back_text'] = v; break
    out['en_back_after_s'] = back
    out['en_ready_len'] = len(txt(t)); out['en_ready_thai'] = thai(txt(t))

    # TH flash event via real UI: new game confirm -> 'เกมใหม่'
    t.eval("document.querySelector(\"#langbtns .lang[data-lang='th']\").click()"); time.sleep(3.0)
    t.eval("document.getElementById('bNewGame').click()"); time.sleep(0.4)
    t.eval("document.getElementById('bNewYes').click()"); time.sleep(0.5)
    out['th_flash_newgame'] = txt(t); out['th_flash_thai'] = thai(txt(t))
    cf = t.eval(COUNT); out['th_flash_count'] = cf['n']; out['th_flash_overflow'] = cf['scrollW'] > cf['vw']
    time.sleep(3.2)
    out['th_flash_returned'] = txt(t)
    out['th_after_len'] = len(txt(t))
    out['errors'] = t.eval("window.__errcap")
print(json.dumps(out, ensure_ascii=False, indent=1))
