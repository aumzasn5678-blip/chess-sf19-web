import sys, time, json, re
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
TS = int(time.time())
URL = 'http://127.0.0.1:8100/index.html?v=%d' % TS

STATUSWORD = r'กำลังคิด|เพดาน|พร้อม|ลึก|หยุดแล้ว|Thinking|Ready|depth|cap|Stopped|Moved|Lines|Profile|Position set|New game|Restored'

COUNT = """(()=>{
 const w=%s;
 const ev=document.getElementById('evalwrap').getBoundingClientRect();
 const navT=document.getElementById('bStart').parentElement.getBoundingClientRect().top;
 const vis=[];
 document.querySelectorAll('body *').forEach(e=>{
   if(e.children.length) return;
   const r=e.getBoundingClientRect();
   if(r.width===0&&r.height===0) return;
   const cs=getComputedStyle(e);
   if(cs.display==='none'||cs.visibility==='hidden'||cs.opacity==='0') return;
   if(r.bottom<ev.bottom-2) return;      // ต้องอยู่ใต้หลอด HP
   if(r.top>navT+2) return;              // และเหนือแถวปุ่มนำทาง
   const s=(e.textContent||'').trim();
   if(!s) return;
   if(!new RegExp(w,'i').test(s)) return;
   vis.push({id:e.id||null,cls:e.className||null,txt:s});
 });
 return {n:vis.length, items:vis,
   depthinfoVisible:(()=>{const e=document.getElementById('depthinfo');const r=e.getBoundingClientRect();return r.height>0&&r.width>0&&getComputedStyle(e).display!=='none';})(),
   statusHidden:getComputedStyle(document.getElementById('status')).display,
   vw:innerWidth, scrollW:document.documentElement.scrollWidth};})()""" % json.dumps(STATUSWORD)

def txt(t):
    return t.eval("document.getElementById('depthinfo').textContent.trim()")

def thai_count(s):
    return sum(1 for ch in s if '\u0e00' <= ch <= '\u0e7f')

def main():
    out = {}
    with cdp.Tab(timeout=260) as t:
        t.cmd('Page.enable'); t.cmd('Runtime.enable')
        t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
        t.cmd('Page.addScriptToEvaluateOnNewDocument',
              source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
        t.goto(URL, settle=4.0); time.sleep(1.2)
        t.eval("document.querySelector(\"#langbtns .lang[data-lang='th']\").click()"); time.sleep(0.5)

        out['th_ready_initial'] = txt(t)
        c = t.eval(COUNT); out['th_count_visible'] = c['n']; out['th_visible_items'] = c['items']
        out['depthinfo_visible'] = c['depthinfoVisible']; out['status_css'] = c['statusHidden']
        out['th_overflow'] = c['scrollW'] > c['vw']

        # ---- run ----
        t.eval("document.getElementById('bRun').click()")
        samples = []
        for i in range(8):
            time.sleep(0.7)
            samples.append(txt(t))
        out['th_thinking_samples'] = samples
        think_re = re.compile(r'^กำลังคิด… \d+/\d+ · เพดาน [\d.]+ วิ$')
        out['th_thinking_match'] = [bool(think_re.match(s)) for s in samples]
        mid = t.eval(COUNT); out['th_count_during_run'] = mid['n']; out['th_items_during_run'] = mid['items']
        out['th_depth_rising'] = len(set(samples)) > 1

        # ---- stop (bRun toggles to stop) ----
        t.eval("document.getElementById('bRun').click()")
        time.sleep(0.35)
        s_after_stop = txt(t); out['th_after_stop_t035'] = s_after_stop
        back = None
        for i in range(10):
            time.sleep(0.4)
            v = txt(t)
            if re.match(r'^พร้อม · ลึก \d+$', v):
                back = round(0.35 + (i + 1) * 0.4, 2); out['th_back_text'] = v; break
        out['th_back_after_s'] = back
        out['th_count_after_stop'] = t.eval(COUNT)['n']
        out['th_ready_len'] = len(txt(t))
        out['th_ready_dup_luek'] = txt(t).count('ลึก')

        # ---- event flash other than stop: move a piece (e2e4) ----
        try:
            t.eval("(()=>{const a=document.querySelector(\"#board [data-sq='e2']\");if(a)a.click();})()"); time.sleep(0.3)
            t.eval("(()=>{const a=document.querySelector(\"#board [data-sq='e4']\");if(a)a.click();})()"); time.sleep(0.4)
            out['th_after_move'] = txt(t)
            time.sleep(3.0)
            out['th_after_move_autoreturn'] = txt(t)
        except Exception as e:
            out['th_move_err'] = str(e)

        # ---- EN ----
        t.eval("(()=>{const b=document.querySelector('#langbtns .lang[data-lang=\\'en\\']');if(b)b.click();})()")
        time.sleep(0.6)
        out['en_ready'] = txt(t)
        out['en_ready_thai'] = thai_count(txt(t))
        c2 = t.eval(COUNT); out['en_ready_count'] = c2['n']; out['en_overflow_ready'] = c2['scrollW'] > c2['vw']
        t.eval("document.getElementById('bRun').click()"); time.sleep(1.6)
        out['en_thinking'] = txt(t)
        out['en_thinking_thai'] = thai_count(txt(t))
        c3 = t.eval(COUNT); out['en_thinking_count'] = c3['n']
        out['en_overflow_thinking'] = c3['scrollW'] > c3['vw']
        out['en_ready_len'] = len(out['en_ready'])
        out['en_thinking_len'] = len(out['en_thinking'])
        t.eval("document.getElementById('bRun').click()"); time.sleep(0.4)
        out['en_after_stop'] = txt(t)
        time.sleep(3.0)
        out['en_back'] = txt(t)

        # ---- other invariants ----
        out['max_hist'] = t.eval("(typeof MAX_HIST!=='undefined'?MAX_HIST:null)")
        out['order'] = t.eval("""(()=>{const g=id=>Math.round(document.getElementById(id).getBoundingClientRect().top);
          return {board:g('boardWrap'),hp:g('evalwrap'),line:g('depthinfo'),nav:Math.round(document.getElementById('bStart').parentElement.getBoundingClientRect().top)};})()""")
        out['errors'] = t.eval("window.__errcap")
    print(json.dumps(out, ensure_ascii=False, indent=1))

main()
