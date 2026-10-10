#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_157c — อนิเมชันทุกตา (ไม่กดรัน/กดรัน/ลูกศร/โปรโมท) + กล่องยืนยันปุ่ม ◀"""
import sys, time, json
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
TS = str(int(time.time()))
APP = "http://127.0.0.1:8100/index.html?v=" + TS
OUT = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)

SAMPLER = r"""(()=>{window.__animseen=0;window.__rec2=true;
  const tick=()=>{if(!window.__rec2)return;
    const a=document.querySelector('#board .pcimg.animating');
    if(a && a.style.transform && a.style.transform.indexOf('translate(0px, 0px)')<0 && a.style.transform!=='') window.__animseen++;
    requestAnimationFrame(tick);};
  requestAnimationFrame(tick);return true;})()"""

with cdp.Tab(timeout=300) as t:
    t.cmd("Page.enable")
    t.cmd("Page.addScriptToEvaluateOnNewDocument", source=(
        "window.__errcap=[];window.addEventListener('error',e=>window.__errcap.push(String(e.message||e.error)));"
        "window.addEventListener('unhandledrejection',e=>window.__errcap.push('rej:'+String(e.reason)));"))

    def fresh(clear_ls=True):
        t.goto(APP, settle=2.0)
        t.eval("(async()=>{try{const rs=await navigator.serviceWorker.getRegistrations();for(const r of rs)await r.unregister();}catch(e){}"
               "try{const ks=await caches.keys();for(const k of ks)await caches.delete(k);}catch(e){}"
               + ("try{localStorage.clear();}catch(e){}" if clear_ls else "") + "return true;})()", await_promise=True)
        time.sleep(0.4); t.goto(APP, settle=2.0)
        t.wait("window.__chessDbg && window.__chessDbg.ready===true", timeout=20)
        t.eval(SAMPLER)

    def c(sq): return t.eval("(()=>{const e=document.querySelector('#board .sq[data-sq=\"%s\"]');if(e)e.click();return !!e;})()"%sq)
    def move(f,to): c(f); time.sleep(0.04); c(to)

    def key(code, keyname, vk):
        for typ in ("keyDown","keyUp"):
            t.cmd("Input.dispatchKeyEvent", type=typ, code=code, key=keyname, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk)
        time.sleep(0.15)

    # ===== อนิเมชัน: 8 ตา ไม่กดรัน =====
    fresh()
    seq8 = [('e2','e4'),('e7','e5'),('g1','f3'),('b8','c6'),('f1','c4'),('f8','c5'),('d2','d3'),('d7','d6')]
    okA = 0
    for f,to in seq8:
        a0 = t.eval("window.__chessDbg.animCount"); s0 = t.eval("window.__animseen")
        move(f,to); time.sleep(0.45)
        a1 = t.eval("window.__chessDbg.animCount"); s1 = t.eval("window.__animseen")
        if a1 - a0 >= 1 and s1 > s0: okA += 1
    res['A_noRun_anim_ok'] = "%d/8" % okA
    res['A_ghost'] = t.eval("document.querySelectorAll('#boardWrap .ghost').length")
    res['A_stuck_transform'] = t.eval("[...document.querySelectorAll('#board .pcimg')].filter(i=>i.style.transform && i.style.transform!=='').length")
    res['A_dup_pieces'] = t.eval("(()=>{let d=0;document.querySelectorAll('#board .sq').forEach(s=>{if(s.querySelectorAll('img.pcimg').length>1)d++;});return d;})()")

    # ===== อนิเมชัน: 8 ตา ขณะกดรัน =====
    fresh()
    t.click('#bRun'); time.sleep(1.2)
    seq8b = [('d2','d4'),('d7','d5'),('c2','c4'),('e7','e6'),('b1','c3'),('g8','f6'),('c1','g5'),('f8','e7')]
    okB = 0
    for f,to in seq8b:
        a0 = t.eval("window.__chessDbg.animCount"); s0 = t.eval("window.__animseen")
        move(f,to); time.sleep(0.45)
        a1 = t.eval("window.__chessDbg.animCount"); s1 = t.eval("window.__animseen")
        if a1 - a0 >= 1 and s1 > s0: okB += 1
    res['B_run_anim_ok'] = "%d/8" % okB
    res['B_run_still'] = t.eval("window.__chessDbg.run")
    res['B_ghost'] = t.eval("document.querySelectorAll('#boardWrap .ghost').length")
    t.click('#bRun'); time.sleep(0.3)

    # ===== อนิเมชัน: เดินจากช่องปลายลูกศร (sugTo) =====
    fresh()
    t.click('#bRun')
    t.wait("Object.keys(window.__chessDbg.sugTo).length>0", timeout=15)
    sug = t.eval("window.__chessDbg.sugTo")
    dest = list(sug.keys())[0]
    a0 = t.eval("window.__chessDbg.animCount")
    c(dest); time.sleep(0.5)
    a1 = t.eval("window.__chessDbg.animCount")
    res['C_arrow_dest'] = dest
    res['C_arrow_anim_delta'] = a1 - a0
    res['C_arrow_played'] = t.eval("window.__chessDbg.ucisLen")
    t.click('#bRun'); time.sleep(0.2)

    # ===== อนิเมชัน: โปรโมท =====
    fresh()
    t.eval("(()=>{const e=document.getElementById('fen');e.value='2n1k3/1P6/8/8/8/8/8/4K3 w - - 0 1';document.getElementById('bSet').click();return true;})()")
    time.sleep(0.4)
    a0 = t.eval("window.__chessDbg.animCount")
    c('b7'); time.sleep(0.15); c('b8'); time.sleep(0.3)
    res['D_promo_bar'] = t.eval("document.getElementById('promo').classList.contains('show')")
    t.eval("(()=>{const b=document.querySelector('#promo button[data-piece=\"q\"]');if(b)b.click();return !!b;})()")
    time.sleep(0.5)
    a1 = t.eval("window.__chessDbg.animCount")
    res['D_promo_anim_delta'] = a1 - a0
    res['D_promo_uci'] = t.eval("window.__chessDbg.ucis.slice(-1)[0]")
    res['D_ghost'] = t.eval("document.querySelectorAll('#boardWrap .ghost').length")
    t.shot(OUT+r"\shot-157c-promo.png")

    # ===== กล่องยืนยันปุ่ม ◀ =====
    fresh()
    # (ก) ยังไม่เคยเริ่มใหม่ → disabled, กดไม่ขึ้นกล่อง
    res['K_undo_disabled_fresh'] = t.eval("window.__chessDbg.undoDisabled")
    t.eval("(()=>{const b=document.getElementById('bUndo');b.click();return true;})()")
    time.sleep(0.3)
    res['K_undo_box_when_disabled'] = t.eval("getComputedStyle(document.getElementById('confirmUndo')).display")
    # เล่น 3 ตา แล้วเริ่มใหม่ (prevGame ถูกเก็บ) แล้วเล่น 1 ตาในเกมใหม่
    for f,to in [('e2','e4'),('e7','e5'),('g1','f3')]:
        move(f,to); time.sleep(0.3)
    ucis_before = t.eval("window.__chessDbg.ucisLen")
    t.click('#bNewGame'); time.sleep(0.3)
    res['K_newbox_open'] = t.eval("getComputedStyle(document.getElementById('confirmNew')).display")
    t.click('#bNewYes'); time.sleep(0.4)
    res['K_undo_enabled_after_new'] = t.eval("window.__chessDbg.undoDisabled")
    move('d2','d4'); time.sleep(0.4)
    # (ข) เปิดกล่อง undo + วัดสไตล์
    board_top_before = t.eval("document.getElementById('board').getBoundingClientRect().top")
    t.eval("(()=>{document.getElementById('bUndo').click();return true;})()")
    time.sleep(0.35)
    res['K_undobox_open'] = t.eval("getComputedStyle(document.getElementById('confirmUndo')).display")
    res['K_newbox_closed_when_undo'] = t.eval("getComputedStyle(document.getElementById('confirmNew')).display")
    def stylecmp():
        return t.eval("""(()=>{const n=document.getElementById('confirmNew'),u=document.getElementById('confirmUndo');
          const brn=getComputedStyle(n).borderTopColor, bru=getComputedStyle(u).borderTopColor;
          const yn=getComputedStyle(document.getElementById('bNewYes')),yu=getComputedStyle(document.getElementById('bUndoYes'));
          const nn=getComputedStyle(document.getElementById('bNewNo')),nu=getComputedStyle(document.getElementById('bUndoNo'));
          const ew=document.getElementById('evalwrap').getBoundingClientRect();
          const ur=u.getBoundingClientRect();
          const bt=document.getElementById('board').getBoundingClientRect().top;
          return JSON.stringify({border_n:brn,border_u:bru,yes_bg_n:yn.backgroundImage.slice(0,60),yes_bg_u:yu.backgroundImage.slice(0,60),
            yes_bc_n:yn.borderTopColor,yes_bc_u:yu.borderTopColor,no_bg_n:nn.backgroundImage.slice(0,60),no_bg_u:nu.backgroundImage.slice(0,60),
            no_bc_u:nu.borderTopColor, box_top:Math.round(ur.top), evalwrap_bottom:Math.round(ew.bottom), board_top:Math.round(bt),
            box_radius_u:getComputedStyle(u).borderTopLeftRadius, box_radius_n:getComputedStyle(n).borderTopLeftRadius,
            msg_u:document.getElementById('confirmUndoMsg').textContent});})()""")
    res['K_styles'] = stylecmp()
    board_top_after = t.eval("document.getElementById('board').getBoundingClientRect().top")
    res['K_board_push_delta'] = round(abs(board_top_after - board_top_before), 2)
    t.shot(OUT+r"\shot-157c-undobox-th.png")
    # (ฬ) Esc → ปิด, ไม่มีอะไรเปลี่ยน
    ptr_before = t.eval("window.__chessDbg.ptr"); uc_before = t.eval("window.__chessDbg.ucisLen")
    key("Escape","Escape",27)
    res['K_esc_closed'] = t.eval("getComputedStyle(document.getElementById('confirmUndo')).display")
    res['K_esc_unchanged'] = (t.eval("window.__chessDbg.ptr")==ptr_before and t.eval("window.__chessDbg.ucisLen")==uc_before)
    # (ค) Enter → ยืนยัน คืนเกมก่อนหน้า + bUndo กลับ disabled
    t.eval("(()=>{document.getElementById('bUndo').click();return true;})()")
    time.sleep(0.3)
    key("Enter","Enter",13)
    time.sleep(0.5)
    res['K_enter_restored_ucis'] = t.eval("window.__chessDbg.ucisLen")
    res['K_expected_restored'] = ucis_before
    res['K_undo_disabled_after'] = t.eval("window.__chessDbg.undoDisabled")
    res['K_box_closed_after_enter'] = t.eval("getComputedStyle(document.getElementById('confirmUndo')).display")

    # (ฬ) 390px + TH/EN ไม่ล้น — เตรียม prevGame ให้ปุ่ม ◀ ใช้ได้ แล้ววัดทั้งสองกล่อง
    move('e2','e4'); time.sleep(0.3)
    t.click('#bNewGame'); time.sleep(0.25); t.click('#bNewYes'); time.sleep(0.35)
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=1, mobile=True)
    time.sleep(0.4)
    def widthtest(bid):
        return t.eval("""(()=>{document.getElementById('%s').click();
          const u=document.getElementById('%s'==='bUndo'?'confirmUndo':'confirmNew');const r=u.getBoundingClientRect();
          return JSON.stringify({sw:document.documentElement.scrollWidth, open:getComputedStyle(u).display, box_right:Math.round(r.right), box_left:Math.round(r.left), vw:window.innerWidth});})()""" % (bid,bid))
    res['K_390_th_undo'] = widthtest('bUndo')
    t.shot(OUT+r"\shot-157c-390-th.png")
    key("Escape","Escape",27)
    res['K_390_th_new'] = widthtest('bNewGame')
    key("Escape","Escape",27)
    t.eval("(()=>{const b=document.querySelector('.lang[data-lang=\"en\"]');if(b)b.click();return !!b;})()")
    time.sleep(0.4)
    res['K_390_en_undo'] = widthtest('bUndo')
    res['K_undomsg_en'] = t.eval("document.getElementById('confirmUndoMsg').textContent")
    res['K_newmsg_en'] = t.eval("document.getElementById('confirmNewMsg').textContent")
    t.shot(OUT+r"\shot-157c-390-en.png")
    key("Escape","Escape",27)
    t.cmd("Emulation.clearDeviceMetricsOverride")
    res['errcap'] = t.eval("window.__errcap")
print(j(res))
