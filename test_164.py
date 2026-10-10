import sys,time,json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp
TS=int(time.time())
URL='http://127.0.0.1:8100/index.html?v=%d'%TS
def thai_count(s):
    return sum(1 for ch in s if '\u0e00'<=ch<='\u0e7f')

# lower zone = between parent row of #bEdit (bottom) and #posPanel (top)
LOWER="""(()=>{const row=document.getElementById('bEdit').parentElement;const rb=row.getBoundingClientRect().bottom;
const pt=document.getElementById('posPanel').getBoundingClientRect().top;let hits=[];let txt='';
document.querySelectorAll('body *').forEach(e=>{if(e.children.length)return;const r=e.getBoundingClientRect();if(r.height===0&&r.width===0)return;
if(r.top>=rb-1&&r.bottom<=pt+1){const s=(e.textContent||'').trim();if(s)txt+=s+' | ';if(/เพดาน|กำลังคิด|หยุดแล้ว|ตั้งตำแหน่ง|นำเข้าสำเร็จ|จำนวนตัวเลือก|สลับ|ตั้งตาว่า|Status|Stopped|Analysis/.test(s))hits.push((e.id?('#'+e.id):'')+' '+s.slice(0,50));}});
return {rb:Math.round(rb),pt:Math.round(pt),hits:hits,zoneText:txt.trim()};})()"""

ZONE="""(()=>{const hp=document.getElementById('evalwrap').getBoundingClientRect();const d=document.getElementById('depthinfo').getBoundingClientRect();const s=document.getElementById('status').getBoundingClientRect();const nav=document.getElementById('bStart').parentElement.getBoundingClientRect();
return {hp_top:Math.round(hp.top),hp_bottom:Math.round(hp.bottom),depth_top:Math.round(d.top),depth_bottom:Math.round(d.bottom),status_top:Math.round(s.top),status_bottom:Math.round(s.bottom),nav_top:Math.round(nav.top),
 statusText:document.getElementById('status').textContent.trim(),depthText:document.getElementById('depthinfo').textContent.trim()};})()"""

def main():
    out={}
    with cdp.Tab(timeout=280) as t:
        t.cmd('Page.enable'); t.cmd('Runtime.enable')
        t.cmd('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
        INIT='window.__errcap=[];window.addEventListener("error",e=>window.__errcap.push(String(e.message||e.error)));'
        t.cmd('Page.addScriptToEvaluateOnNewDocument', source=INIT)
        t.goto(URL, settle=4.0); time.sleep(1.0)
        t.eval("document.querySelector(\"#langbtns .lang[data-lang='th']\").click()"); time.sleep(0.5)
        ev={}

        def snap(name):
            lz=t.eval(LOWER); z=t.eval(ZONE)
            ev[name]={'lower_hits':len(lz['hits']),'hits':lz['hits'],'zoneText':lz['zoneText'],
                      'status':z['statusText'],'depth':z['depthText']}
            return lz

        snap('initial')
        # 1) run
        t.eval("document.getElementById('bRun').click()"); time.sleep(0.7)
        snap('running')
        # 2) stop mid-run
        t.eval("document.getElementById('bRun').click()"); time.sleep(0.5)
        lz_stop=snap('stopped')
        out['stopped_has_stopped_word']=('หยุดแล้ว' in t.eval("document.getElementById('status').textContent"))
        # 3) move a piece e2-e4
        t.eval("(()=>{const s=[...document.getElementById('board').children];const e=s.find(x=>x.dataset.sq==='e2');if(e)e.click();})()"); time.sleep(0.2)
        t.eval("(()=>{const s=[...document.getElementById('board').children];const e=s.find(x=>x.dataset.sq==='e4');if(e)e.click();})()"); time.sleep(0.4)
        snap('after_move')
        # 4) nav: start + forward
        t.eval("document.getElementById('bStart').click()"); time.sleep(0.3); snap('nav_start')
        t.eval("document.getElementById('bFwd').click()"); time.sleep(0.3); snap('nav_fwd')
        # 5) flip
        t.eval("document.getElementById('bFlip').click()"); time.sleep(0.3); snap('flip')
        # 6) FEN set
        t.eval("document.getElementById('fen').value='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'"); time.sleep(0.1)
        t.eval("document.getElementById('bSet').click()"); time.sleep(0.4); snap('set_fen')
        # 7) PGN import
        pgn="1. e4 e5 2. Nf3 Nc6 3. Bb5 a6"
        t.eval("(()=>{const p=document.getElementById('pgnIn');p.value=%s;})()"%json.dumps(pgn))
        time.sleep(0.1)
        t.eval("document.getElementById('bImportPgn').click()"); time.sleep(0.5); snap('import_pgn')
        # 8) npv change
        t.eval("(()=>{const b=document.querySelector('#npvbtns .npv[data-npv=\"2\"]');if(b)b.click();})()"); time.sleep(0.3); snap('npv')

        out['events']=ev
        allhits=sum(v['lower_hits'] for v in ev.values())
        out['total_lower_hits']=allhits
        out['zone']=t.eval(ZONE)
        # geometry assertions
        z=out['zone']
        out['status_below_hp']=z['status_top']>=z['hp_bottom']
        out['depth_below_hp']=z['depth_top']>=z['hp_bottom']
        out['status_above_nav']=z['status_top']<z['nav_top']
        out['depth_above_nav']=z['depth_top']<z['nav_top']
        # 390 overflow TH
        out['th_overflow']=t.eval("document.documentElement.scrollWidth>innerWidth")
        # EN
        t.eval("(()=>{const b=document.querySelector('#langbtns .lang[data-lang=\\'en\\']');if(b)b.click();})()"); time.sleep(0.6)
        out['en_thai_count']=thai_count(t.eval("document.body.innerText"))
        t.eval("document.getElementById('bRun').click()"); time.sleep(0.8)
        ez=t.eval(ZONE); out['en_running_status']=ez['statusText']; out['en_running_depth']=ez['depthText']
        out['en_status_has_thai']=thai_count(ez['statusText'])
        out['en_overflow']=t.eval("document.documentElement.scrollWidth>innerWidth")
        t.eval("document.getElementById('bRun').click()"); time.sleep(0.3)
        out['errors']=t.eval("window.__errcap")
    print(json.dumps(out, ensure_ascii=False, indent=1))

main()
