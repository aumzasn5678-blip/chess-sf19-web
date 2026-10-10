import sys, time, json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp

TS = int(time.time())
URL = 'http://127.0.0.1:8100/index.html?v=%d' % TS

JS_OVER = "(()=>({vw:innerWidth,sw:document.documentElement.scrollWidth,over:document.documentElement.scrollWidth>innerWidth+1}))()"

JS_MEASURE = """(()=>{
  const q=s=>document.querySelector(s);
  const rect=e=>{if(!e)return null;const r=e.getBoundingClientRect();return {l:Math.round(r.left),t:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height),r:Math.round(r.right),b:Math.round(r.bottom)};};
  const sum=q('#posPanel>summary .posBtn'), upd=q('#bUpdate'), card=q('#posPanel>.card'), det=q('#posPanel');
  const cs=e=>e?getComputedStyle(e):null;
  return {
    open: det?det.open:null,
    sum:rect(sum), upd:rect(upd), card:rect(card), det:rect(det),
    cardDisp: card?cs(card).display:null,
    updDisp: upd?cs(upd).display:null,
    updVis: upd?cs(upd).visibility:null
  };
})()"""

JS_CNT_UPDATE = """(()=>{
  const all=[...document.querySelectorAll('button')];
  const byText=all.filter(b=>(b.textContent||'').includes('อัปเดตแอพ'));
  const byId=document.querySelectorAll('#bUpdate');
  return {byText:byText.length, byId:byId.length, ids:all.filter(b=>b.id==='bUpdate').length,
          hits:byText.map(b=>b.id||b.className)};
})()"""

JS_BOX = """(()=>{const b=document.getElementById('confirmUpdate');if(!b)return null;const cs=getComputedStyle(b);
  const y=getComputedStyle(document.getElementById('bUpdateYes')),n=getComputedStyle(document.getElementById('bUpdateNo'));
  const msg=document.getElementById('confirmUpdateMsg');
  return {disp:cs.display,borderColor:cs.borderColor,msg:msg?msg.textContent:null,
    yesImg:y.backgroundImage.slice(0,60),yesBg:y.backgroundColor,noImg:n.backgroundImage.slice(0,60),noBg:n.backgroundColor,
    top:Math.round(b.getBoundingClientRect().top),w:Math.round(b.getBoundingClientRect().width)};})()"""

JS_STYLE_SUM = """(()=>{const e=document.querySelector('#posPanel>summary .posBtn');const c=getComputedStyle(e);
  return {img:c.backgroundImage.slice(0,70),col:c.color,bc:c.borderColor};})()"""
JS_STYLE_UPD = """(()=>{const e=document.getElementById('bUpdate');const c=getComputedStyle(e);
  return {img:c.backgroundImage.slice(0,70),col:c.color,bc:c.borderColor};})()"""

JS_ORDER = """(()=>{
  const ids=['boardWrap','evalwrap','depthinfo','bStart','posPanel','bUpdate','installCard'];
  const o={};ids.forEach(i=>{const e=document.getElementById(i);o[i]=e?Math.round(e.getBoundingClientRect().top):null;});
  return o;})()"""

JS_THAI_PANEL = """(()=>{const a=document.getElementById('bUpdate'),s=document.querySelector('#posPanel>summary .posBtn');
  const txt=(a?a.textContent:'')+(s?s.textContent:'');let n=0;for(const ch of txt){if(ch>='\\u0e00'&&ch<='\\u0e7f')n++;}
  return {txt:txt,n:n};})()"""

def key(t, name, code, vk):
    t.cmd('Input.dispatchKeyEvent', type='keyDown', key=name, code=code, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk)
    t.cmd('Input.dispatchKeyEvent', type='keyUp', key=name, code=code, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk)

out = {}

# ============ PART 1: layout @ 390 TH ============
with cdp.Tab(timeout=300) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source="try{localStorage.setItem('chessLang','th');localStorage.removeItem('chessHist');}catch(e){}")
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
    t.goto(URL, settle=3.5); time.sleep(1.0)
    try:
        t.eval("try{document.getElementById('bRun')&&document.getElementById('bRun').click();}catch(e){}")
    except Exception: pass
    time.sleep(0.2)

    out['m_closed'] = t.eval(JS_MEASURE)
    out['cnt_update'] = t.eval(JS_CNT_UPDATE)
    out['over_closed'] = t.eval(JS_OVER)
    out['style_sum'] = t.eval(JS_STYLE_SUM)
    out['style_upd'] = t.eval(JS_STYLE_UPD)
    out['order'] = t.eval(JS_ORDER)

    # click summary -> open
    t.eval("document.querySelector('#posPanel>summary').click()"); time.sleep(0.5)
    out['m_open'] = t.eval(JS_MEASURE)
    out['over_open'] = t.eval(JS_OVER)

    # click summary again -> closed, update still visible
    t.eval("document.querySelector('#posPanel>summary').click()"); time.sleep(0.4)
    out['m_reclosed'] = t.eval(JS_MEASURE)

    out['err_p1'] = t.eval("window.__errcap")

# ============ PART 2: update confirm + spy + navigation @ 390 TH ============
JS_SPY = """(()=>{
  try{localStorage.removeItem('__spy167');}catch(e){}
  window.__spy={unreg:0,cacheKeys:0,cacheDel:0};
  const save=()=>{try{localStorage.setItem('__spy167',JSON.stringify(window.__spy));}catch(e){}};save();
  try{ navigator.serviceWorker.getRegistrations=async()=>[{unregister:async()=>{window.__spy.unreg++;save();return true;}}]; }catch(e){}
  try{ Object.defineProperty(window,'caches',{configurable:true,value:{
        keys:async()=>{window.__spy.cacheKeys++;save();return ['k1','k2'];},
        delete:async(k)=>{window.__spy.cacheDel++;save();return true;}}}); }catch(e){}
  return true;})()"""

with cdp.Tab(timeout=300) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
    t.goto(URL, settle=3.5); time.sleep(1.0)
    url_before = t.eval("location.href")
    # open confirm via real click on the button
    t.eval("document.getElementById('bUpdate').click()"); time.sleep(0.4)
    out['box_open'] = t.eval(JS_BOX)
    out['panel_open_after_upd_click'] = t.eval("document.getElementById('posPanel').open")
    # ESC -> cancel, no reload
    key(t, 'Escape', 'Escape', 27); time.sleep(0.5)
    out['box_after_esc'] = t.eval(JS_BOX)
    out['url_after_esc'] = t.eval("location.href")
    out['url_before'] = url_before
    # install spy, reopen and confirm via Enter
    out['spy_installed'] = t.eval(JS_SPY)
    t.eval("document.getElementById('bUpdate').click()"); time.sleep(0.35)
    out['box_reopen'] = t.eval(JS_BOX)
    key(t, 'Enter', 'Enter', 13)
    time.sleep(3.0)
    out['spy'] = t.eval("localStorage.getItem('__spy167')")
    out['url_after_confirm'] = t.eval("location.href")
    out['err_p2'] = t.eval("window.__errcap")

# ============ PART 3: EN @ 390 ============
with cdp.Tab(timeout=300) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
    t.goto(URL, settle=3.5); time.sleep(1.0)
    t.eval("(()=>{const b=[...document.querySelectorAll('.lang')].find(x=>x.dataset.lang==='en');if(b)b.click();})()")
    time.sleep(0.6)
    out['m_en'] = t.eval(JS_MEASURE)
    out['thai_en'] = t.eval(JS_THAI_PANEL)
    out['over_en'] = t.eval(JS_OVER)
    out['err_p3'] = t.eval("window.__errcap")

# ============ PART 4: hover/disabled @ desktop ============
with cdp.Tab(timeout=300) as t:
    t.cmd('Page.enable'); t.cmd('Runtime.enable')
    t.cmd('Emulation.setDeviceMetricsOverride', width=1000, height=900, deviceScaleFactor=1, mobile=False)
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source="try{localStorage.setItem('chessLang','th');}catch(e){}")
    t.cmd('Page.addScriptToEvaluateOnNewDocument',
          source='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));')
    t.goto(URL, settle=3.5); time.sleep(1.0)
    t.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=2, y=2, button='none'); time.sleep(0.2)
    before = t.eval("(()=>{const c=getComputedStyle(document.getElementById('bUpdate'));return {fl:c.filter,tr:c.transform};})()")
    r = t.eval("(()=>{const e=document.getElementById('bUpdate');const b=e.getBoundingClientRect();return {x:Math.round(b.left+b.width/2),y:Math.round(b.top+b.height/2)};})()")
    t.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=r['x'], y=r['y'], button='none'); time.sleep(0.4)
    after = t.eval("(()=>{const c=getComputedStyle(document.getElementById('bUpdate'));return {fl:c.filter,tr:c.transform};})()")
    out['hover_update'] = {'before': before, 'after': after,
                           'media': t.eval("({hover:matchMedia('(hover:hover)').matches,fine:matchMedia('(pointer:fine)').matches})")}
    out['err_p4'] = t.eval("window.__errcap")

print(json.dumps(out, ensure_ascii=False, indent=1))
