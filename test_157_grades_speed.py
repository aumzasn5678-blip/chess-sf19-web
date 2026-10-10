#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_157 — วัดเวลาไอคอนเกรดขึ้นเร็วต่อตา (placeholder ทันที + หัวคิว + งบ 250ms + ไม่ขึ้นเป็นชุด)"""
import sys, time, json, os
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp

TS = str(int(time.time()))
APP = "http://127.0.0.1:8100/index.html?v=" + TS
OUT = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)

ARM = r"""(()=>{window.__ev=[];window.__rec=true;window.__last=null;
  const snap=()=>{const b=document.querySelector('#board .gradico');
    const bst=b?(b.classList.contains('pending')?'pending':'grade'):'none';
    const bp=b?String(b.dataset.ply):'';
    const bg=b?(b.dataset.grade||''):'';
    const ln=document.querySelectorAll('#log img.logg').length;
    const gp=(document.getElementById('gradeProg')||{}).textContent||'';
    const sc=document.querySelectorAll('#statBody .statRow b').length;
    const se=(window.__chessDbg?String(window.__chessDbg.searching):'?');
    return bst+'|'+bp+'|'+bg+'|'+ln+'|'+gp+'|'+sc+'|'+se;};
  const tick=()=>{if(!window.__rec)return;const s=snap();
    if(s!==window.__last){window.__ev.push({t:performance.now(),s:s});window.__last=s;}
    requestAnimationFrame(tick);};
  requestAnimationFrame(tick); return true;})()"""

REC = r"""(()=>{window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));window.__rec=false;return true;})()"""

with cdp.Tab(timeout=300) as t:
    t.cmd("Page.enable")
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=REC)

    def fresh(clear_ls=True):
        t.goto(APP, settle=2.0)
        t.eval("(async()=>{try{const rs=await navigator.serviceWorker.getRegistrations();for(const r of rs)await r.unregister();}catch(e){}"
               "try{const ks=await caches.keys();for(const k of ks)await caches.delete(k);}catch(e){}"
               + ("try{localStorage.clear();}catch(e){}" if clear_ls else "")
               + "return true;})()", await_promise=True)
        time.sleep(0.4)
        t.goto(APP, settle=2.0)
        t.wait("window.__chessDbg && window.__chessDbg.ready===true", timeout=20)

    def clickn(sq):
        return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return !!e;})()" % sq)

    def move(frm, to, times=True):
        clickn(frm)
        if times:
            t.eval("(()=>{window.__tc=performance.now();const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return !!e;})()" % to)
        else:
            clickn(to)

    def read_ev():
        return t.eval("window.__ev") or []

    def interpret(ev, tc_key=None):
        """คืน (placeholder_ms, grade_ms) ของการเดินล่าสุด — เทียบก'Tc ที่ตั้งในหน้า'."""
        out = {}
        tc = t.eval("window.__tc")
        pend = next((e for e in ev if e['s'].split('|')[0] == 'pending'), None)
        grad = next((e for e in ev if e['s'].split('|')[0] == 'grade'), None)
        if pend and tc: out['placeholder_ms'] = round(pend['t'] - tc)
        if grad and tc: out['grade_ms'] = round(grad['t'] - tc)
        return out

    # ============ (ก) เดิน 1 ตา ไม่กดรัน ============
    fresh(clear_ls=True)
    res['errs_after_load'] = t.eval("window.__errcap")
    t.eval(ARM)
    time.sleep(0.3)
    t.eval("window.__ev=[];window.__last=null;")
    move('e2', 'e4')
    time.sleep(2.0)
    evA = read_ev()
    res['A_events'] = [(round(e['t']), e['s']) for e in evA]
    tc = t.eval("window.__tc")
    pend = next((e for e in evA if e['s'].split('|')[0] == 'pending'), None)
    grad = next((e for e in evA if e['s'].split('|')[0] == 'grade'), None)
    res['A_placeholder_ms'] = round(pend['t'] - tc) if pend else None
    res['A_grade_ms'] = round(grad['t'] - tc) if grad else None
    res['A_grade'] = grad['s'].split('|')[2] if grad else None
    res['A_placeholder_before_grade'] = bool(pend and grad and pend['t'] <= grad['t'])
    res['A_cacheSize'] = t.eval("window.__chessDbg.gradeCacheSize")

    # ---- (แคช) ย้อนกลับแล้วเดินตาเดิมอีกครั้ง → ต้องขึ้นทันที ----
    t.click('#bBack'); time.sleep(0.25)
    t.eval(ARM); t.eval("window.__ev=[];window.__last=null;")
    move('e2', 'e4')
    time.sleep(0.6)
    evC = read_ev()
    tc = t.eval("window.__tc")
    grad = next((e for e in evC if e['s'].split('|')[0] == 'grade'), None)
    res['C_cache_grade_ms'] = round(grad['t'] - tc) if grad else None
    res['C_cache_immediate'] = bool(grad and (grad['t'] - tc) < 120)

    # ============ (ข) เดินติดกัน 5 ตาเร็ว ๆ ไม่กดรัน ============
    fresh(clear_ls=True)
    t.eval(ARM)
    time.sleep(0.3)
    t.eval("window.__ev=[];window.__last=null;")
    rapid = [('d2', 'd4'), ('d7', 'd5'), ('c2', 'c4'), ('e7', 'e6'), ('b1', 'c3')]
    for f, to in rapid:
        move(f, to, times=False)
        time.sleep(0.08)
    time.sleep(3.0)
    evB = read_ev()
    res['B_events'] = [(round(e['t']), e['s']) for e in evB]
    # ลำดับเวลาที่ log icon ไล่ขึ้น 1..5 (เทียบกับ event แรก)
    t0 = evB[0]['t'] if evB else 0
    logsteps = []
    for e in evB:
        ln = int(e['s'].split('|')[3])
        if ln and (not logsteps or logsteps[-1][1] != ln):
            logsteps.append((round(e['t'] - t0), ln))
    res['B_log_icon_timeline_ms'] = logsteps
    res['B_moveGrades'] = t.eval("window.__chessDbg.moveGrades")
    res['B_all_graded'] = all(t.eval("window.__chessDbg.moveGrades"))
    res['B_no_burst'] = (len(logsteps) >= 4)
    res['B_gap_max_ms'] = max([logsteps[i+1][0]-logsteps[i][0] for i in range(len(logsteps)-1)] or [0])

    # ============ (ค) กดรันค้าง แล้วเดินตานอก PV ============
    fresh(clear_ls=True)
    t.eval(ARM)
    t.click('#bRun')
    time.sleep(1.5)
    res['D_searching_before'] = t.eval("window.__chessDbg.searching")
    res['D_run_before'] = t.eval("window.__chessDbg.run")
    t.eval("window.__ev=[];window.__last=null;")
    move('a2', 'a3')
    # เฝ้าดู timeline การกลับมาทำงานของ analysis
    time.sleep(0.35)
    res['D_at350_searching'] = t.eval("window.__chessDbg.searching")
    time.sleep(0.8)
    res['D_at1150_searching'] = t.eval("window.__chessDbg.searching")
    res['D_at1150_run'] = t.eval("window.__chessDbg.run")
    time.sleep(0.8)
    evD = read_ev()
    res['D_events'] = [(round(e['t']), e['s']) for e in evD]
    tc = t.eval("window.__tc")
    pend = next((e for e in evD if e['s'].split('|')[0] == 'pending'), None)
    grad = next((e for e in evD if e['s'].split('|')[0] == 'grade'), None)
    res['D_placeholder_ms'] = round(pend['t'] - tc) if pend else None
    res['D_grade_ms'] = round(grad['t'] - tc) if grad else None
    res['D_searching_after'] = t.eval("window.__chessDbg.searching")
    res['D_depthinfo'] = t.eval("(document.getElementById('depthinfo')||{}).innerText")
    res['D_grade'] = t.eval("window.__chessDbg.moveGrades[0]")
    t.shot(os.path.join(OUT, "shot-157-run-grade.png"))
    t.click('#bRun')  # stop
    time.sleep(0.3)

    # ============ (ฬ) กล่องสถิติเกมเก่า เกรดขาด → ตัวนับ + ไอคอนไล่ขึ้น ============
    fresh(clear_ls=True)
    t.eval("""(()=>{const C=window.__dbgChess;const g=new C();const fens=[g.fen()];const ucis=[];
      for(const u of ['d2d4','d7d5','c2c4','e7e6','b1c3','g8f6']){g.move({from:u.slice(0,2),to:u.slice(2,4),promotion:'q'});ucis.push(u);fens.push(g.fen());}
      window.__oldGame={name:'old-test',fens:fens,ucis:ucis,grades:[]};return true;})()""")
    t.eval(ARM)
    time.sleep(0.2)
    t.eval("window.__ev=[];window.__last=null;")
    t.eval("window.__chessDbg.dbgOpenStats(window.__oldGame)")
    time.sleep(3.5)
    evE = read_ev()
    res['E_events'] = [(round(e['t']), e['s']) for e in evE]
    t0 = evE[0]['t'] if evE else 0
    progsteps = []
    for e in evE:
        gp = e['s'].split('|')[4]
        if gp and (not progsteps or progsteps[-1][1] != gp):
            progsteps.append((round(e['t'] - t0), gp))
    res['E_progress_timeline'] = progsteps
    res['E_incremental'] = len(progsteps) >= 3
    res['E_final_progress'] = t.eval("(document.getElementById('gradeProg')||{}).textContent")
    res['E_stat_grades'] = t.eval("(()=>{const g=window.__oldGame.grades;let n=0;for(const x of g)if(x)n++;return n+'/'+g.length;})()")
    res['E_stat_sums'] = t.eval("""(()=>{const cols=[...document.querySelectorAll('#statBody .statCol')];
      return JSON.stringify(cols.map(col=>{const h=col.querySelector('h4').innerText;
        let sum=0;[...col.querySelectorAll('.statRow')].forEach(r=>{sum+=parseInt(r.querySelector('b').innerText,10)||0;});return {head:h,sum:sum};}));})()""")
    t.shot(os.path.join(OUT, "shot-157-stats.png"))
    t.eval("window.__chessDbg.dbgCloseStats()")
    time.sleep(0.3)

    # ============ per-side sums (เกมหลัก) ============
    fresh(clear_ls=True)
    for f, to in [('e2', 'e4'), ('e7', 'e5'), ('g1', 'f3'), ('b8', 'c6'), ('f1', 'c4'), ('f8', 'c5')]:
        move(f, to, times=False); time.sleep(0.25)
    t.wait("(()=>{const g=window.__chessDbg.moveGrades;return g.length>=6&&g.every(x=>!!x);})()", timeout=30)
    res['F_moveGrades'] = t.eval("window.__chessDbg.moveGrades")
    res['F_perSide'] = t.eval("""(()=>{const u=window.__chessDbg.ucis;let w=0,b=0;
      for(let i=0;i<u.length;i++){ if(i%2===0)w++; else b++; }
      return JSON.stringify({moves:u.length,w:w,b:b});})()""")
    t.click('#bStats'); time.sleep(1.0)
    res['F_stat_sums'] = t.eval("""(()=>{const cols=[...document.querySelectorAll('#statBody .statCol')];
      return JSON.stringify(cols.map(col=>{const h=col.querySelector('h4').innerText;
        let sum=0;[...col.querySelectorAll('.statRow')].forEach(r=>{sum+=parseInt(r.querySelector('b').innerText,10)||0;});return {head:h,sum:sum};}));})()""")
    res['F_errs'] = t.eval("window.__errcap")

print(j(res))
