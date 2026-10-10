import sys,time,json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
TS=int(time.time())
URL='http://127.0.0.1:8100/index.html?v=%d'%TS
THAI=[chr(c) for c in range(0x0E00,0x0E60)]
def thai_count(s):
    return sum(1 for ch in s if '\u0e00'<=ch<='\u0e7f')

MEAS=("""(()=>{const g=id=>{const e=document.getElementById(id);if(!e)return null;const r=e.getBoundingClientRect();return{top:Math.round(r.top),bottom:Math.round(r.bottom),left:Math.round(r.left),right:Math.round(r.right)};};
const nav=g('bStart');const nw=document.getElementById('bStart');const navTop=nw?Math.round(nw.parentElement.getBoundingClientRect().top):null;
const bw=g('boardWrap'),ev=g('evalwrap'),di=g('depthinfo');
return {vw:innerWidth,docW:document.documentElement.clientWidth,scrollW:document.documentElement.scrollWidth,
 board:bw,eval:ev,depth:di,navTop:navTop,
 evalText:(document.getElementById('evaltxt')?document.getElementById('evaltxt').textContent:''),
 evalTag:(document.getElementById('evaltag')?document.getElementById('evaltag').textContent:''),
 evalTagr:(document.getElementById('evaltagr')?document.getElementById('evaltagr').textContent:''),
 depthText:(document.getElementById('depthinfo')?document.getElementById('depthinfo').textContent.trim():''),
 updBottom:(document.getElementById('updRow')?Math.round(document.getElementById('updRow').getBoundingClientRect().bottom):null),
 docH:document.documentElement.scrollHeight};})()""")

THAI_SCAN="""(()=>{let c=0;document.querySelectorAll('body *').forEach(e=>{if(e.children.length===0&&e.textContent){c+=(e.textContent.match(/[\\u0e00-\\u0e7f]/g)||[]).length;}});return c;})()"""

def main():
    out={}
    with cdp.Tab(timeout=250) as t:
        t.cmd('Page.enable'); t.cmd('Runtime.enable')
        t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
        INIT='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));'
        t.cmd('Page.addScriptToEvaluateOnNewDocument', source=INIT)
        t.goto(URL, settle=4.0); time.sleep(1.0)
        m=t.eval(MEAS); out['th390_initial']=m
        # ---- (ก) order check ----
        order_ok = (m['board'] and m['eval'] and m['depth'] and m['navTop'] is not None
                    and m['board']['top']<m['eval']['top']<m['depth']['top']<m['navTop'])
        out['order_ok']=order_ok
        out['no_overlap_depth_vs_eval'] = m['depth']['top']>=m['eval']['bottom']
        out['no_overlap_eval_vs_board'] = m['eval']['top']>=m['board']['bottom']
        out['no_overflow_390_th'] = m['scrollW']<=m['vw']
        # ---- run + realtime depthinfo ----
        t.eval("document.getElementById('bRun').click()")
        samples=[]
        for i in range(10):
            samples.append(t.eval("document.getElementById('depthinfo').textContent.trim()"))
            time.sleep(0.5)
        out['depthinfo_samples']=samples
        out['depthinfo_changed']= len(set(samples))>1
        # HP bar content during run
        hp=t.eval(MEAS); out['during_run']={'evalText':hp['evalText'],'evalTag':hp['evalTag'],'evalTagr':hp['evalTagr'],'depthText':hp['depthText']}
        t.eval("document.getElementById('bRun').click()"); time.sleep(0.5)  # stop
        # ---- confirm boxes not covering board ----
        bb=t.eval(MEAS)['board']
        def box_top(jscall):
            return t.eval("(()=>{const e=%s;if(!e||getComputedStyle(e).display==='none')return null;const r=e.getBoundingClientRect();return{top:Math.round(r.top),bottom:Math.round(r.bottom)};})()"%jscall)
        t.eval("document.getElementById('bNewGame').click()"); time.sleep(0.3)
        cn=box_top("document.getElementById('confirmNew')"); out['confirmNew']=cn
        t.eval("document.getElementById('bNewYes').click()"); time.sleep(0.4)  # starts new game, sets prevGame
        # undo box (needs prevGame)
        out['bUndo_disabled']=t.eval("document.getElementById('bUndo').disabled")
        t.eval("document.getElementById('bUndo').click()"); time.sleep(0.4)
        cu=box_top("document.getElementById('confirmUndo')"); out['confirmUndo']=cu
        t.eval("document.getElementById('bUndoNo').click()"); time.sleep(0.2)
        t.eval("document.getElementById('bUpdate').click()"); time.sleep(0.3)
        cup=box_top("document.getElementById('confirmUpdate')"); out['confirmUpdate']=cup
        out['boxes_clear_board']=all(x is None or x['top']>=bb['bottom'] for x in [cn,cu,cup]) and cn is not None and cu is not None
        # Esc closes update box, no reload
        t.eval("window.__preUpd=1;")
        t.cmd('Input.dispatchKeyEvent', type='keyDown', key='Escape', code='Escape', windowsVirtualKeyCode=27)
        t.cmd('Input.dispatchKeyEvent', type='keyUp', key='Escape', code='Escape', windowsVirtualKeyCode=27)
        time.sleep(0.4)
        out['esc_closed_update']= t.eval("getComputedStyle(document.getElementById('confirmUpdate')).display")=='none'
        out['esc_no_reload']= t.eval("window.__preUpd")==1
        out['update_btn_bottom']= None
        # ---- update button anchor (bottom-most row) ----
        out['updRow_bottom']=t.eval("Math.round(document.getElementById('updRow').getBoundingClientRect().bottom)")
        out['docH']=t.eval("document.documentElement.scrollHeight")
        out['updRow_is_last']=t.eval("document.getElementById('updRow')===document.getElementById('app').lastElementChild||document.getElementById('updRow')===document.querySelector('#app>#updRow')")
        # ---- MAX_HIST=100 ----
        t.eval("""(()=>{const a=[];for(let i=0;i<101;i++)a.push({id:'z'+i,name:'g'+i,savedAt:Date.now(),fens:['x'],ucis:['x'],grades:[null]});localStorage.setItem('chessHist',JSON.stringify(a));return a.length;})()""")
        t.goto(URL, settle=3.0); time.sleep(0.8)
        out['hist_after_101']=len(json.loads(t.eval("localStorage.getItem('chessHist')")))
        out['hist_var_len']=t.eval("(typeof hist!=='undefined'?hist.length:null)")
        out['max_hist_const']=t.eval("(typeof MAX_HIST!=='undefined'?MAX_HIST:null)")
        t.eval("localStorage.removeItem('chessHist');localStorage.removeItem('chessHistSel');")
        # ---- EN mode: no Thai chars ----
        t.eval("try{localStorage.setItem('chessLang','en');}catch(e){}")
        # find lang key used; try clicking lang button instead
        t.eval("(()=>{const b=document.querySelector('#langbtns .lang[data-lang=\\'en\\']');if(b)b.click();})()")
        time.sleep(0.6)
        en_thai=thai_count(t.eval("document.body.innerText"))
        out['en_thai_count']=en_thai
        out['lang']=t.eval("(typeof lang!=='undefined'?lang:null)")
        em=t.eval(MEAS); out['en_overflow']=em['scrollW']>em['vw']
        # ---- errors ----
        out['errors']=t.eval("window.__errcap")
        # ---- update reload check (LAST, navigates away) ----
        t.eval("document.getElementById('bUpdate').click()"); time.sleep(0.3)
        t.eval("document.getElementById('bUpdateYes').click()")
        time.sleep(3.0)
        out['after_update_url']=t.eval("location.href")
        out['after_update_has_v']= '?v=' in (t.eval("location.href") or '')
    print(json.dumps(out, ensure_ascii=False, indent=1))

main()
