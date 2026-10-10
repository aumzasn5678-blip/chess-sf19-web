#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ทดสอบ: สลับภาษา TH<->EN ขณะเปิดกล่องสถิติ (#statView) หรือหน้า replay (#replayView) ค้างอยู่
ต้องเปลี่ยนภาษาทันที (อักษรไทย = 0 ในโหมด EN) โดยไม่ต้องปิดหน้า."""
import sys, time, json, os, re, subprocess
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp

TS = str(int(time.time()))
APP = "http://127.0.0.1:8100/index.html?v=" + TS
OUT = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
THAI = re.compile(r"[\u0E00-\u0E7F]")
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)

UNREG = """(async()=>{
  try{ if(navigator.serviceWorker){ const rs=await navigator.serviceWorker.getRegistrations(); await Promise.all(rs.map(r=>r.unregister())); } }catch(e){}
  try{ if(window.caches){ const ks=await caches.keys(); await Promise.all(ks.map(k=>caches.delete(k))); } }catch(e){}
  return true; })()"""

def scan(t, sel):
    txt = t.eval("(() => { const e=document.querySelector(%s); return e? e.innerText : ''; })()" % json.dumps(sel)) or ""
    hits = THAI.findall(txt)
    return {"thai": len(hits), "sample": "".join(hits[:12]), "len": len(txt), "head": txt[:100]}

def set_lang(t, code):
    t.eval("(() => { const b=[...document.querySelectorAll('.lang')].find(x=>x.dataset.lang===%s); if(b) b.click(); return !!b; })()" % json.dumps(code))
    time.sleep(0.25)

# build a couple of saved games by driving the app UI
def safe_shot(t, path):
    try:
        t.shot(path)
    except Exception as e:
        res.setdefault('shot_fail', []).append(os.path.basename(path) + ":" + type(e).__name__)

def build_games(t):
    t.eval("localStorage.removeItem('chessHist')")
    fresh(t)
    t.eval("document.getElementById('pgnIn').value='1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7'")
    t.click("#bImportPgn"); time.sleep(0.5)
    t.click("#bSaveHist"); time.sleep(0.4)                       # hist[0] flipped=false
    t.click("#bFlip"); time.sleep(0.3)                           # flip to black
    t.click("#bSaveHist"); time.sleep(0.4)                       # hist[0] flipped=true (unshift), hist[1]=false
    return t.eval("window.__chessDbg.hist.length")

def fresh(t):
    t.goto(APP + "&r=" + str(time.time()), settle=1.2)
    t.eval(UNREG, await_promise=True)

errors = []
with cdp.Tab() as t:
    t.cmd("Page.enable")
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source="""
      window.__errcap=[];
      window.addEventListener('error',e=>window.__errcap.push('err:'+String(e.message||e.error)));
      window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));""")

    t.eval("localStorage.setItem('chessLang','th')")
    res['games'] = build_games(t)

    # ================= (A) STATS BOX open, TH -> EN =================
    t.click("#bHist"); time.sleep(0.4)
    t.eval("(() => { const btns=[...document.querySelectorAll('#histList .histItem')]; return btns.length; })()")
    stats_cases = []
    n = t.eval("document.querySelectorAll('#histList .histItem').length")
    for idx in range(min(2, n)):
        # open stats for hist item idx
        t.click("#histBack"); time.sleep(0.2)
        t.click("#bHist"); time.sleep(0.3)
        t.eval("(() => { const it=document.querySelectorAll('#histList .histItem')[%d]; const bs=it.querySelectorAll('.histBtns button'); bs[1].click(); return true; })()" % idx)
        time.sleep(0.4)
        before = scan(t, "#statView")
        set_lang(t, "en")
        en = scan(t, "#statView")
        set_lang(t, "th")
        back = scan(t, "#statView")
        stats_cases.append({"idx": idx, "th_before": before["thai"], "en": en["thai"], "en_sample": en["sample"],
                            "en_head": en["head"], "th_back": back["thai"]})
        if idx == 0:
            safe_shot(t, os.path.join(OUT, "shot-153-stats-th.png"))
            set_lang(t, "en"); safe_shot(t, os.path.join(OUT, "shot-153-stats-en.png")); set_lang(t, "th")
        t.click("#statClose"); time.sleep(0.2)
    res['stats_cases'] = stats_cases

    # ================= (B) REPLAY open, TH -> EN =================
    t.click("#histBack"); time.sleep(0.2)
    t.click("#bHist"); time.sleep(0.3)
    t.eval("(() => { const it=document.querySelectorAll('#histList .histItem')[0]; const bs=it.querySelectorAll('.histBtns button'); bs[0].click(); return true; })()")  # histOpen
    time.sleep(0.5)
    res['rp_open_before'] = t.eval("document.getElementById('replayView').classList.contains('show')")
    before_rp = scan(t, "#replayView")
    set_lang(t, "en")
    en_rp = scan(t, "#replayView")
    res['rp_evalTag_en'] = t.eval("document.getElementById('rpEvalTag').textContent")
    res['rp_evalTagR_en'] = t.eval("document.getElementById('rpEvalTagR').textContent")
    res['rp_side_en'] = t.eval("document.getElementById('rpSide').innerText")
    safe_shot(t, os.path.join(OUT, "shot-153-replay-en.png"))
    set_lang(t, "th")
    back_rp = scan(t, "#replayView")
    res['replay_case'] = {"th_before": before_rp["thai"], "en": en_rp["thai"], "en_sample": en_rp["sample"],
                          "en_head": en_rp["head"], "th_back": back_rp["thai"]}
    t.click("#rpClose"); time.sleep(0.3)

    # ================= (C) other flows still work: main + hist + edit =================
    t.click("#histBack"); time.sleep(0.2)
    set_lang(t, "en")
    res['main_en'] = scan(t, "body")
    t.click("#bHist"); time.sleep(0.3)
    res['hist_en'] = scan(t, "#histView")
    t.click("#histBack"); time.sleep(0.2)
    t.click("#bEdit"); time.sleep(0.3)
    res['edit_en'] = scan(t, "#editView") if t.eval("!!document.getElementById('editView')") else None
    t.click("#editBack"); time.sleep(0.2)
    set_lang(t, "th")
    res['main_th'] = scan(t, "body")

    # ================= (D) reopen stats twice / animation toggle sanity =================
    t.click("#bStats") if t.eval("!!document.getElementById('bStats')") else None
    time.sleep(0.3)
    res['stats_reopen'] = t.eval("document.getElementById('statView').classList.contains('show')")
    set_lang(t, "en")
    res['stats_reopen_en'] = scan(t, "#statView")
    set_lang(t, "th")
    t.click("#statClose") if t.eval("!!document.getElementById('statClose')") else None
    time.sleep(0.2)

    res['errors'] = t.eval("window.__errcap")

print(j(res))
