import sys, time, json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp

OUT = {}
SEL = {
 'sub':'#sub','bBack':'#bBack','bFwd':'#bFwd','bNewGame':'#bNewGame','bFlip':'#bFlip',
 'bTheme':'#bTheme','bRun':'#bRun','sumSettings':'#settings>summary','sumPos':'#posPanel>summary',
 'lblProfile':'#settings label[data-i18n="lblProfile"]','profQuick':'.prof[data-prof="quick"]',
 'profNormal':'.prof[data-prof="normal"]','profDeep':'.prof[data-prof="deep"]',
 'lblDepth':'label[data-i18n="lblDepth"]','lblNpv':'label[data-i18n="lblNpv"]',
 'lblSize':'label[data-i18n="lblSize"]','lblElo':'label[data-i18n="lblElo"]','lblLang':'label[data-i18n="lblLang"]',
 'sizeSmall':'.size[data-size="small"]','sizeMedium':'.size[data-size="medium"]','sizeLarge':'.size[data-size="large"]',
 'animBtn':'#animBtn','hideBtn':'#hideBtn','bPaste':'#bPaste','bSet':'#bSet','bCopy':'#bCopy','bCopyFen':'#bCopyFen',
 'elov':'#elov','profv':'#profv','evaltag':'#evaltag','evaltagr':'#evaltagr','bNewYes':'#bNewYes','bNewNo':'#bNewNo',
}
HINT = {'profhint':'#profhint','depthhint':'#depthhint','fenhint':'#fenhint','footer':'.tiny[data-i18n-html="footerHint"]','confirmMsg':'#confirmNew .inner span'}

def snap(t):
    out = {}
    for k, sel in SEL.items():
        out[k] = t.eval(f"(() => {{ const e=document.querySelector({json.dumps(sel)}); return e? e.textContent.trim() : null; }})()")
    out['fen_ph'] = t.eval("(() => { const e=document.getElementById('fen'); return e? e.placeholder : null; })()")
    for k, sel in HINT.items():
        out[k] = t.eval(f"(() => {{ const e=document.querySelector({json.dumps(sel)}); return e? e.innerText.trim().slice(0,90) : null; }})()")
    out['html_lang'] = t.eval("document.documentElement.lang")
    return out

with cdp.Tab() as t:
    # capture JS errors before any script runs on new documents
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=(
        "window.__errs=[];"
        "window.addEventListener('error', e=>window.__errs.push(String(e.message)));"
        "window.addEventListener('unhandledrejection', e=>window.__errs.push('rej:'+String(e.reason)));"
    ))
    t.goto('http://127.0.0.1:8100/index.html?v=120lang')
    time.sleep(7)
    t.eval("(() => { localStorage.clear(); return 1; })()")
    t.goto('http://127.0.0.1:8100/index.html?v=120lang2')
    time.sleep(7)

    OUT['errors_after_load'] = t.eval("window.__errs ? window.__errs.slice() : ['no-collector']")
    OUT['engine_sub_th'] = t.eval("document.getElementById('sub').textContent")
    OUT['lang_default'] = t.eval("document.documentElement.lang")
    OUT['ls_lang_default'] = t.eval("localStorage.getItem('chessLang')")

    # open panels so hints are laid out
    t.eval("(() => { document.getElementById('settings').open=true; document.getElementById('posPanel').open=true; return 1; })()")
    time.sleep(0.5)
    OUT['th_snapshot'] = snap(t)

    # --- switch to English ---
    t.click('.lang[data-lang="en"]')
    time.sleep(0.8)
    OUT['errors_after_en'] = t.eval("window.__errs.slice()")
    OUT['ls_after_en'] = t.eval("localStorage.getItem('chessLang')")
    OUT['en_btn_on'] = t.eval("(() => { const b=document.querySelector('.lang[data-lang=\"en\"]'); const s=getComputedStyle(b); return {on:b.classList.contains('on'), bg:s.backgroundColor}; })()")
    OUT['th_btn_off'] = t.eval("(() => { const b=document.querySelector('.lang[data-lang=\"th\"]'); const s=getComputedStyle(b); return {on:b.classList.contains('on'), bg:s.backgroundColor}; })()")
    OUT['en_snapshot'] = snap(t)
    t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v120-en-settings.png')

    # --- toast in English (anim toggle) ---
    t.click('#animBtn'); time.sleep(0.4)
    OUT['toast_anim_en'] = t.eval("document.getElementById('toast').textContent")
    t.click('#animBtn'); time.sleep(0.3)
    # theme button toast in English
    t.click('#bTheme'); time.sleep(0.4)
    OUT['toast_theme_en'] = t.eval("document.getElementById('toast').textContent")
    OUT['theme_btn_en'] = t.eval("document.getElementById('bTheme').textContent")

    # --- reload persists English ---
    t.goto('http://127.0.0.1:8100/index.html?v=120lang3')
    time.sleep(7)
    OUT['reload_lang'] = t.eval("document.documentElement.lang")
    OUT['reload_newgame_text'] = t.eval("document.getElementById('bNewGame').textContent")
    OUT['reload_en_btn_on'] = t.eval("document.querySelector('.lang[data-lang=\"en\"]').classList.contains('on')")
    OUT['sub_after_reload'] = t.eval("document.getElementById('sub').textContent")

    # --- feature check: play a move so a line/arrow appears, low depth ---
    t.eval("(() => { document.getElementById('settings').open=true; return 1; })()")
    t.eval("(() => { const d=document.getElementById('depth'); d.value=8; d.dispatchEvent(new Event('input',{bubbles:true})); return 1; })()")
    t.click('#bRun'); time.sleep(9)
    OUT['bRun_text_running_or_stopped'] = t.eval("document.getElementById('bRun').textContent")
    OUT['status_en'] = t.eval("document.getElementById('status').textContent")
    OUT['depthinfo_en'] = t.eval("document.getElementById('depthinfo').textContent")
    OUT['pvtags_en'] = t.eval("(() => { const n=[...document.querySelectorAll('.sqtag')].map(x=>x.textContent); const best=[...document.querySelectorAll('.sqtag')].map(x=>x.textContent).find(x=>x==='Best'); return {count:n.length, anyBest: !!best, sample:n.slice(0,4)}; })()")
    OUT['arrows_count'] = t.eval("document.getElementById('arrows').childElementCount")
    t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v120-en-analysis.png')
    # stop
    t.eval("(() => { const b=document.getElementById('bRun'); if(b.textContent.indexOf('Stop')>=0||b.textContent.indexOf('■')>=0) b.click(); return 1; })()")
    time.sleep(0.5)

    # --- undo / new game feature ---
    t.click('#bNewGame'); time.sleep(0.3)
    t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v120-en-confirm.png')
    OUT['confirm_text_en'] = t.eval("document.querySelector('#confirmNew .inner span').textContent")
    OUT['confirm_yes_en'] = t.eval("document.getElementById('bNewYes').textContent")
    t.click('#bNewYes'); time.sleep(0.4)
    OUT['undo_enabled_after_newgame'] = t.eval("!document.getElementById('bUndo').disabled")
    OUT['status_after_newgame_en'] = t.eval("document.getElementById('status').textContent")
    t.click('#bUndo'); time.sleep(0.4)
    OUT['status_after_undo_en'] = t.eval("document.getElementById('status').textContent")

    # --- switch back to Thai ---
    t.click('.lang[data-lang="th"]'); time.sleep(0.8)
    OUT['errors_after_th'] = t.eval("window.__errs.slice()")
    OUT['th_restored_snapshot'] = snap(t)
    OUT['ls_after_th'] = t.eval("localStorage.getItem('chessLang')")
    t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v120-th-settings.png')

    # --- overflow check at 390px, both languages ---
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    time.sleep(0.6)
    t.eval("(() => { document.getElementById('settings').open=true; document.getElementById('posPanel').open=true; return 1; })()")
    time.sleep(0.4)
    OUT['overflow_th'] = t.eval("(() => ({iw:window.innerWidth, de:document.documentElement.scrollWidth, body:document.body.scrollWidth}))()")
    t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v120-390-th.png')
    t.click('.lang[data-lang="en"]'); time.sleep(0.8)
    OUT['overflow_en'] = t.eval("(() => ({iw:window.innerWidth, de:document.documentElement.scrollWidth, body:document.body.scrollWidth}))()")
    t.shot(r'E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-v120-390-en.png')
    # any element wider than viewport?
    OUT['wide_elems_en'] = t.eval("(() => { const w=window.innerWidth; const bad=[]; document.querySelectorAll('#app *').forEach(e=>{ if(e.getBoundingClientRect().width>w+1) bad.push(e.id||e.className||e.tagName); }); return bad.slice(0,10); })()")
    t.click('.lang[data-lang="th"]'); time.sleep(0.6)
    OUT['wide_elems_th'] = t.eval("(() => { const w=window.innerWidth; const bad=[]; document.querySelectorAll('#app *').forEach(e=>{ if(e.getBoundingClientRect().width>w+1) bad.push(e.id||e.className||e.tagName); }); return bad.slice(0,10); })()")
    OUT['final_errors'] = t.eval("window.__errs.slice()")

print(json.dumps(OUT, ensure_ascii=False, indent=1))
