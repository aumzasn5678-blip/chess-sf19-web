import sys, time, json, re
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp

THAI = re.compile(r'[\u0E00-\u0E7F]')
OUT = {}

SCAN_JS = r"""
(() => {
  const thai = /[\u0E00-\u0E7F]/;
  const hits = [];
  const push = (where, txt) => {
    const s = (txt||'').trim();
    if (s && thai.test(s)) hits.push(where + ' :: ' + s.replace(/\s+/g,' ').slice(0,120));
  };
  // visible text
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
  let n;
  while ((n = walker.nextNode())) {
    const el = n.parentElement;
    if (!el) continue;
    const tag = el.tagName;
    if (tag==='SCRIPT'||tag==='STYLE') continue;
    // visible?
    const st = getComputedStyle(el);
    if (st.display==='none' || st.visibility==='hidden') continue;
    push('text<' + tag.toLowerCase() + (el.id?('#'+el.id):'') + '>', n.nodeValue);
  }
  // placeholders, titles, aria-labels, values
  document.querySelectorAll('[placeholder]').forEach(e=>push('placeholder['+ (e.id||e.tagName) +']', e.getAttribute('placeholder')));
  document.querySelectorAll('[title]').forEach(e=>push('title['+ (e.id||e.tagName) +']', e.getAttribute('title')));
  document.querySelectorAll('[aria-label]').forEach(e=>push('aria-label['+ (e.id||e.tagName) +']', e.getAttribute('aria-label')));
  push('document.title', document.title);
  return hits;
})()
"""

with cdp.Tab() as t:
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=(
        "window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message)));"
    ))
    t.goto('http://127.0.0.1:8100/index.html' + '?v=121scan')
    time.sleep(6)
    # A) loading text check right after load (engine may still be booting) — poll quickly
    OUT['during_load_body_has_loading'] = t.eval("(/loading|กำลังโหลด/i).test(document.body.innerText||'')")
    OUT['during_load_any_loading_dom'] = t.eval("(()=>{const r=/loading|กำลังโหลด/i; let f=false; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let n; while((n=w.nextNode())){ if(r.test(n.nodeValue||'')) f=true; } document.querySelectorAll('[placeholder],[title]').forEach(e=>{ if(r.test(e.getAttribute('placeholder')||e.getAttribute('title')||'')) f=true; }); return f; })()")
    time.sleep(4)
    OUT['ready_body_has_loading'] = t.eval("(/loading|กำลังโหลด/i).test(document.body.innerText||'')")
    OUT['sub_text'] = t.eval("document.getElementById('sub').textContent")

    # reset lang to EN
    t.eval("(()=>{localStorage.clear();return 1})()")
    t.goto('http://127.0.0.1:8100/index.html' + '?v=121scan2')
    time.sleep(6)
    t.click('.lang[data-lang="en"]'); time.sleep(0.6)
    # open panels
    t.eval("(()=>{document.getElementById('settings').open=true;document.getElementById('posPanel').open=true;return 1})()")
    # run a short analysis so status/depthinfo/sqtag appear
    t.eval("(()=>{const d=document.getElementById('depth');d.value=8;d.dispatchEvent(new Event('input',{bubbles:true}));return 1})()")
    t.click('#bRun'); time.sleep(9)
    # toggle anim to produce a toast in EN
    t.click('#animBtn'); time.sleep(0.4)
    OUT['scan_before_stop'] = t.eval(SCAN_JS)
    OUT['toast_en'] = t.eval("document.getElementById('toast').textContent")
    OUT['status_en'] = t.eval("document.getElementById('status').textContent")
    OUT['depthinfo_en'] = t.eval("document.getElementById('depthinfo').textContent")
    # stop (produces "Stopped" status)
    t.eval("(()=>{const b=document.getElementById('bRun'); if(/Stop|■/.test(b.textContent)) b.click(); return 1})()")
    time.sleep(0.6)
    OUT['status_after_stop_en'] = t.eval("document.getElementById('status').textContent")
    # move a piece to make a move -> log has moves; also test empty-log message via new game
    t.click('#bNewGame'); time.sleep(0.3); t.click('#bNewYes'); time.sleep(0.5)
    OUT['log_text_en'] = t.eval("document.getElementById('log').innerText")
    OUT['status_after_newgame_en'] = t.eval("document.getElementById('status').textContent")
    # final full scan in EN
    OUT['scan_en_final'] = t.eval(SCAN_JS)
    OUT['errors'] = t.eval("window.__errs.slice()")
    t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v121-en-scan.png')

    # switch back to Thai, verify restored
    t.click('.lang[data-lang="th"]'); time.sleep(0.6)
    OUT['th_check_newgame'] = t.eval("document.getElementById('bNewGame').textContent")
    OUT['th_check_status'] = t.eval("document.getElementById('status').textContent")
    OUT['th_html_lang'] = t.eval("document.documentElement.lang")
    t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v121-th-restored.png')

print(json.dumps(OUT, ensure_ascii=False, indent=1))
