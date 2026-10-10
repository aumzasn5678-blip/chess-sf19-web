#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_157b — ยืนยันตัวนับเกรดไล่ขึ้นต่อตา (MutationObserver) + เกรดตาไม่ใช่ book"""
import sys, time, json
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
TS = str(int(time.time()))
APP = "http://127.0.0.1:8100/index.html?v=" + TS
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)

with cdp.Tab(timeout=200) as t:
    t.cmd("Page.enable")
    t.goto(APP, settle=2.0)
    t.eval("(async()=>{try{const rs=await navigator.serviceWorker.getRegistrations();for(const r of rs)await r.unregister();}catch(e){}"
           "try{const ks=await caches.keys();for(const k of ks)await caches.delete(k);}catch(e){}try{localStorage.clear();}catch(e){}return true;})()", await_promise=True)
    time.sleep(0.4)
    t.goto(APP, settle=2.0)
    t.wait("window.__chessDbg && window.__chessDbg.ready===true", timeout=20)

    # --- (ฬ) MutationObserver บน #gradeProg: จับทุกค่าที่ setProgText เขียนจริง ---
    t.eval("""(()=>{const g=new window.__dbgChess();const fens=[g.fen()];const ucis=[];
      for(const u of ['d2d4','g8f6','c2c4','e7e6','b1c3','f8b4','e2e3','e8g8']){g.move({from:u.slice(0,2),to:u.slice(2,4),promotion:'q'});ucis.push(u);fens.push(g.fen());}
      window.__oldGame={name:'old',fens:fens,ucis:ucis,grades:[]};
      window.__prog=[]; const el=document.getElementById('gradeProg');
      new MutationObserver(()=>{const tx=el.textContent.trim(); if(tx && (!window.__prog.length || window.__prog[window.__prog.length-1]!==tx)) window.__prog.push([Math.round(performance.now()),tx]);}).observe(el,{childList:true,characterData:true,subtree:true});
      return true;})()""")
    time.sleep(0.2)
    t.eval("window.__chessDbg.dbgOpenStats(window.__oldGame)")
    time.sleep(4.0)
    t0 = t.eval("window.__prog.length ? window.__prog[0][0] : 0")
    res['prog_seq'] = [(x[0]-t0, x[1]) for x in (t.eval("window.__prog") or [])]
    res['prog_equal_steps'] = t.eval("window.__prog.length")
    res['stat_grades'] = t.eval("(()=>{const g=window.__oldGame.grades;let n=0;for(const x of g)if(x)n++;return n+'/'+g.length;})()")
    res['stat_grades_list'] = t.eval("window.__oldGame.grades")
    t.eval("window.__chessDbg.dbgCloseStats()")

    # --- เกรดตาไม่ใช่ book (กลางเกม) ---
    t.goto(APP+"&z=1", settle=2.0)
    t.eval("(async()=>{try{localStorage.clear();}catch(e){}return true;})()", await_promise=True)
    t.goto(APP+"&z=2", settle=2.0)
    t.wait("window.__chessDbg && window.__chessDbg.ready===true", timeout=20)
    def c(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return !!e;})()"%sq)
    # Italian-ish, then a deliberately bad move to get non-book grades
    for f,to in [('e2','e4'),('e7','e5'),('g1','f3'),('b8','c6'),('f1','c4'),('f8','c5'),('d2','d3'),('g8','f6'),
                 ('b1','c3'),('d7','d6'),('c1','g5'),('h7','h6'),('g5','h4'),('g7','g5')]:
        c(f); time.sleep(0.03); c(to); time.sleep(0.35)
    t.wait("(()=>{const g=window.__chessDbg.moveGrades;return g.length>=14&&g.every(x=>!!x);})()", timeout=40)
    res['mid_grades'] = t.eval("window.__chessDbg.moveGrades")
    res['mid_perSide'] = t.eval("""(()=>{const u=window.__chessDbg.ucis;let w=0,b=0;for(let i=0;i<u.length;i++){i%2===0?w++:b++;}return JSON.stringify({moves:u.length,w:w,b:b});})()""")
    t.click('#bStats'); time.sleep(1.0)
    res['mid_stat_sums'] = t.eval("""(()=>{const cols=[...document.querySelectorAll('#statBody .statCol')];
      return JSON.stringify(cols.map(col=>{const h=col.querySelector('h4').innerText;
        let sum=0;[...col.querySelectorAll('.statRow')].forEach(r=>{sum+=parseInt(r.querySelector('b').innerText,10)||0;});return {head:h,sum:sum};}));})()""")
    res['errs'] = t.eval("window.__errcap || []")
    t.shot(r"E:\Hermes_workbench\50_research\2026-10-10_chess-app\shot-157-mid.png")
print(j(res))
