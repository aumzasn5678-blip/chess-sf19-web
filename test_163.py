import sys,time,json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
TS=int(time.time())
URL='http://127.0.0.1:8100/index.html?v=%d'%TS
def thai_count(s):
    return sum(1 for ch in s if '\u0e00'<=ch<='\u0e7f')

MEAS="""(()=>{const g=id=>{const e=document.getElementById(id);if(!e)return null;const r=e.getBoundingClientRect();return{top:Math.round(r.top),bottom:Math.round(r.bottom)};};
const row=g('bEdit')?document.getElementById('bEdit').parentElement:null;
const rowBottom=row?Math.round(row.getBoundingClientRect().bottom):null;
const posTop=document.getElementById('posPanel')?Math.round(document.getElementById('posPanel').getBoundingClientRect().top):null;
return {vw:innerWidth,scrollW:document.documentElement.scrollWidth,
 board:g('boardWrap'),eval:g('evalwrap'),depth:g('depthinfo'),status:g('status'),
 nav:g('bStart'),
 navTop:document.getElementById('bStart')?Math.round(document.getElementById('bStart').parentElement.getBoundingClientRect().top):null,
 rowBottom:rowBottom,posTop:posTop,
 depthText:document.getElementById('depthinfo').textContent.trim(),
 statusText:document.getElementById('status').textContent.trim()};})()"""

# scan lower zone (between edit/settings row bottom and posPanel top) for status words
LOWER="""(()=>{const row=document.getElementById('bEdit').parentElement;const rb=row.getBoundingClientRect().bottom;
const pt=document.getElementById('posPanel').getBoundingClientRect().top;let hits=[];let txt='';
document.querySelectorAll('body *').forEach(e=>{if(e.children.length)return;const r=e.getBoundingClientRect();if(r.height===0&&r.width===0)return;
if(r.top>=rb-1&&r.bottom<=pt+1){const s=(e.textContent||'').trim();if(s)txt+=s+' | ';if(/เพดาน|กำลังคิด/.test(s))hits.push(e.id||e.className||s.slice(0,40));}});
return {rb:Math.round(rb),pt:Math.round(pt),hits:hits,zoneText:txt.trim()};})()"""

def main():
    out={}
    with cdp.Tab(timeout=260) as t:
        t.cmd('Page.enable'); t.cmd('Runtime.enable')
        t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
        INIT='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));'
        t.cmd('Page.addScriptToEvaluateOnNewDocument', source=INIT)
        t.goto(URL, settle=4.0); time.sleep(1.0)
        # TH
        t.eval("document.querySelector(\"#langbtns .lang[data-lang='th']\").click()"); time.sleep(0.5)
        m0=t.eval(MEAS); out['th_initial']=m0
        out['th_overflow']=m0['scrollW']>m0['vw']
        # ---- run: sample both values ----
        t.eval("document.getElementById('bRun').click()")
        time.sleep(0.7)
        mid=t.eval(MEAS); out['mid_run']=mid
        out['mid_both_present']=('กำลังคิด' in mid['depthText']) and ('เพดาน' in mid['statusText'])
        out['mid_order']={'board_top':mid['board']['top'],'eval_bottom':mid['eval']['bottom'],
          'depth_top':mid['depth']['top'],'status_top':mid['status']['top'],'nav_top':mid['navTop']}
        s_depth=[]; s_status=[]
        for i in range(8):
            s_depth.append(t.eval("document.getElementById('depthinfo').textContent.trim()"))
            s_status.append(t.eval("document.getElementById('status').textContent.trim()"))
            time.sleep(0.55)
        out['depth_samples']=s_depth
        out['status_samples']=s_status
        out['depth_changed']=len(set(s_depth))>1
        out['status_changed']=len(set(s_status))>1
        m1=t.eval(MEAS); out['during_run']=m1
        # ---- (ข) order top values ----
        out['order']={
          'board_top':m1['board']['top'],'eval_top':m1['eval']['top'],'eval_bottom':m1['eval']['bottom'],
          'depth_top':m1['depth']['top'],'status_top':m1['status']['top'],'nav_top':m1['navTop']}
        out['depth_above_nav']=m1['depth']['top']<m1['navTop']
        out['status_above_nav']=m1['status']['top']<m1['navTop']
        out['depth_below_hp']=m1['depth']['top']>=m1['eval']['bottom']
        out['status_below_hp']=m1['status']['top']>=m1['eval']['bottom']
        out['status_adjacent_depth']=abs(m1['status']['top']-m1['depth']['bottom'])<=6
        out['both_present']=('กำลังคิด' in m1['depthText']) and ('เพดาน' in m1['statusText'])
        # ---- (ค) lower zone scan ----
        out['lower_zone']=t.eval(LOWER)
        out['lower_hits']=len(out['lower_zone']['hits'])
        t.eval("document.getElementById('bRun').click()"); time.sleep(0.4)  # stop
        # ---- confirm boxes don't cover board ----
        bb=t.eval(MEAS)['board']
        def box_top(js):
            return t.eval("(()=>{const e=%s;if(!e||getComputedStyle(e).display==='none')return null;const r=e.getBoundingClientRect();return{top:Math.round(r.top),bottom:Math.round(r.bottom)};})()"%js)
        t.eval("document.getElementById('bNewGame').click()"); time.sleep(0.3)
        cn=box_top("document.getElementById('confirmNew')")
        t.eval("document.getElementById('bNewYes').click()"); time.sleep(0.5)
        t.eval("document.getElementById('bUndo').click()"); time.sleep(0.4)
        cu=box_top("document.getElementById('confirmUndo')")
        t.eval("document.getElementById('bUndoNo').click()"); time.sleep(0.2)
        out['confirmNew']=cn; out['confirmUndo']=cu
        out['boxes_clear_board']=all(x is None or x['top']>=bb['bottom'] for x in [cn,cu]) and cn is not None and cu is not None
        # ---- update button bottom-most ----
        out['updRow_bottom']=t.eval("Math.round(document.getElementById('updRow').getBoundingClientRect().bottom)")
        out['docH']=t.eval("document.documentElement.scrollHeight")
        out['updRow_is_last']=t.eval("document.getElementById('updRow')===document.querySelector('#app>#updRow')")
        # ---- MAX_HIST ----
        out['max_hist_const']=t.eval("(typeof MAX_HIST!=='undefined'?MAX_HIST:null)")
        # ---- EN mode ----
        t.eval("(()=>{const b=document.querySelector('#langbtns .lang[data-lang=\\'en\\']');if(b)b.click();})()")
        time.sleep(0.6)
        out['en_thai_count']=thai_count(t.eval("document.body.innerText"))
        me=t.eval(MEAS); out['en_overflow']=me['scrollW']>me['vw']
        # EN run to check status text EN + no thai
        t.eval("document.getElementById('bRun').click()"); time.sleep(1.2)
        out['en_status_text']=t.eval("document.getElementById('status').textContent.trim()")
        out['en_depth_text']=t.eval("document.getElementById('depthinfo').textContent.trim()")
        out['en_run_scrollW']=t.eval("document.documentElement.scrollWidth")
        t.eval("document.getElementById('bRun').click()"); time.sleep(0.3)
        out['errors']=t.eval("window.__errcap")
    print(json.dumps(out, ensure_ascii=False, indent=1))

main()
