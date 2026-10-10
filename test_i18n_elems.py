#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ตรวจเชิงลึก: 33 จุดที่เคยค้าง (statName/.statCol h4/.sgn/.statAcc/tiny/rpEvalTag)
+ animation toggle + hist filter + สลับหน้า ขณะสลับภาษา. + เก็บภาพ replay EN."""
import sys, time, json, os, re
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
TS = str(int(time.time()))
APP = "http://127.0.0.1:8100/index.html?v=" + TS
OUT = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
THAI = re.compile(r"[\u0E00-\u0E7F]")
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)
UNREG = """(async()=>{ try{ if(navigator.serviceWorker){const rs=await navigator.serviceWorker.getRegistrations();await Promise.all(rs.map(r=>r.unregister()));} }catch(e){}
 try{ if(window.caches){const ks=await caches.keys();await Promise.all(ks.map(k=>caches.delete(k)));} }catch(e){} return true; })()"""
def set_lang(t, code):
    t.eval("(()=>{const b=[...document.querySelectorAll('.lang')].find(x=>x.dataset.lang===%s); if(b)b.click(); return !!b;})()" % json.dumps(code)); time.sleep(0.3)
def thai(s): return len(THAI.findall(s or ""))

with cdp.Tab() as t:
    t.cmd("Page.enable")
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source="window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message)));window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));")
    t.goto(APP+"&x="+str(time.time()), settle=1.2); t.eval(UNREG, await_promise=True)
    t.eval("localStorage.setItem('chessLang','th'); localStorage.removeItem('chessHist')")
    t.goto(APP+"&y="+str(time.time()), settle=1.2)
    t.eval("document.getElementById('pgnIn').value='1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5'")
    t.click("#bImportPgn"); time.sleep(0.5)
    t.click("#bSaveHist"); time.sleep(0.4)
    t.click("#bFlip"); time.sleep(0.2); t.click("#bSaveHist"); time.sleep(0.4)

    # ---- stats: check the specific elements (EN) ----
    t.click("#bHist"); time.sleep(0.4)
    t.eval("(()=>{const it=document.querySelectorAll('#histList .histItem')[0]; it.querySelectorAll('.histBtns button')[1].click(); return true;})()")
    time.sleep(0.5)
    set_lang(t, "en")
    res['statName'] = t.eval("document.getElementById('statName').textContent")
    res['statCol_h4'] = t.eval("[...document.querySelectorAll('#statBody .statCol h4')].map(x=>x.textContent)")
    res['sgn_all'] = t.eval("[...document.querySelectorAll('#statBody .sgn')].map(x=>x.textContent)")
    res['statAcc'] = t.eval("document.querySelector('#statBody .statAcc') ? document.querySelector('#statBody .statAcc').innerText : null")
    res['tiny_all'] = t.eval("[...document.querySelectorAll('#statBody .tiny')].map(x=>x.textContent)")
    res['resPills'] = t.eval("[...document.querySelectorAll('#statBody .sidePill, #statBody .resPill')].map(x=>x.innerText)")
    res['statBody_thai_en'] = thai(t.eval("document.getElementById('statBody').innerText"))
    # stats: anim/other sanity - close and reopen
    t.click("#statClose"); time.sleep(0.2)
    t.click("#bStats"); time.sleep(0.4)
    res['stats_reopen_show'] = t.eval("document.getElementById('statView').classList.contains('show')")
    res['stats_reopen_thai_en'] = thai(t.eval("document.getElementById('statView').innerText"))
    t.click("#statClose"); time.sleep(0.2)

    # ---- replay: open from hist, toggle animation while TH, then switch lang ----
    t.click("#histBack"); time.sleep(0.2); t.click("#bHist"); time.sleep(0.3)
    t.eval("(()=>{const it=document.querySelectorAll('#histList .histItem')[0]; it.querySelectorAll('.histBtns button')[0].click(); return true;})()")
    time.sleep(0.5)
    set_lang(t, "th")
    # animation toggle in replay (rpAnim btn)
    an_before = t.eval("document.getElementById('rpAnim') ? document.getElementById('rpAnim').textContent : null")
    t.click("#rpAnim") if t.eval("!!document.getElementById('rpAnim')") else None
    time.sleep(0.3)
    set_lang(t, "en")
    res['rpAnim_en'] = t.eval("document.getElementById('rpAnim') ? document.getElementById('rpAnim').textContent : null")
    res['rpAnim_before'] = an_before
    res['replay_full_thai_en'] = thai(t.eval("document.getElementById('replayView').innerText"))
    res['replay_buttons_en'] = t.eval("[...document.querySelectorAll('#replayView button')].map(b=>b.textContent.trim()).slice(0,12)")
    # PV / eval tags
    res['rpEvalTag_en'] = t.eval("document.getElementById('rpEvalTag').textContent")
    res['rpEvalTagR_en'] = t.eval("document.getElementById('rpEvalTagR').textContent")
    res['rpName_en'] = t.eval("document.getElementById('rpName').textContent")
    try:
        t.shot(os.path.join(OUT, "shot-153-replay-en.png")); res['replay_shot']="ok"
    except Exception as e:
        res['replay_shot'] = "fail:"+type(e).__name__
    set_lang(t, "th")
    res['replay_full_thai_th'] = thai(t.eval("document.getElementById('replayView').innerText"))
    # advance replay a bit then switch lang again
    t.click("#rpFwd"); time.sleep(0.3); t.click("#rpFwd"); time.sleep(0.3)
    set_lang(t, "en")
    res['replay_after_fwd_thai_en'] = thai(t.eval("document.getElementById('replayView').innerText"))
    t.click("#rpClose"); time.sleep(0.3)

    # ---- hist filter/sort while switching lang ----
    t.click("#histBack"); time.sleep(0.2); t.click("#bHist"); time.sleep(0.3)
    t.eval("(()=>{const s=document.querySelector('#histView select'); if(s){s.value=s.options[1].value; s.dispatchEvent(new Event('change'));} return !!s;})()")
    time.sleep(0.3)
    res['hist_sort_thai_th'] = thai(t.eval("document.getElementById('histView').innerText"))
    set_lang(t, "en")
    res['hist_sort_thai_en'] = thai(t.eval("document.getElementById('histView').innerText"))
    t.click("#histBack"); time.sleep(0.2)

    res['errors'] = t.eval("window.__errcap")
print(j(res))
