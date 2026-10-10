#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_160 — เลือกหลายเกม+PGN ที่เลือก · ลบประวัติทั้งหมด (แดง+ยืนยัน) · ปุ่มไทยเหลือง"""
import sys, time, json
sys.path.insert(0, r"C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts")
import cdp
TS = str(int(time.time()))
APP = "http://127.0.0.1:8100/index.html?v=" + TS
OUT = r"E:\Hermes_workbench\50_research\2026-10-10_chess-app"
res = {}
def j(o): return json.dumps(o, ensure_ascii=False)

PGN3 = ("[Event \"Test A\"]\n[Site \"t\"]\n[Date \"2026.10.10\"]\n[White \"?\"]\n[Black \"?\"]\n[Result \"*\"]\n\n1. e4 e5 2. Nf3 Nc6 *\n\n"
        "[Event \"Test B\"]\n[Site \"t\"]\n[Date \"2026.10.10\"]\n[White \"?\"]\n[Black \"?\"]\n[Result \"*\"]\n\n1. d4 d5 2. c4 e6 *\n\n"
        "[Event \"Test C\"]\n[Site \"t\"]\n[Date \"2026.10.10\"]\n[White \"?\"]\n[Black \"?\"]\n[Result \"*\"]\n\n1. e4 c5 2. Nf3 d6 *\n")

with cdp.Tab(timeout=420) as t:
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
        t.wait("window.__chessDbg && window.__chessDbg.ready===true", timeout=25)

    def key(code, keyname, vk):
        for typ in ("keyDown", "keyUp"):
            t.cmd("Input.dispatchKeyEvent", type=typ, code=code, key=keyname, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk)
        time.sleep(0.2)

    def import3():
        t.eval("(()=>{document.getElementById('histPgn').value=%s;return true;})()" % j(PGN3))
        t.click('#histImportBtn'); time.sleep(0.8)

    def opendel():
        t.eval("(()=>{document.getElementById('histDelAll').click();return true;})()"); time.sleep(0.35)

    # ===== (ก) fresh + เปิดประวัติ + นำเข้า 3 เกม =====
    fresh()
    t.click('#bHist'); time.sleep(0.5)
    import3()
    res['A_hist_len'] = t.eval("window.__chessDbg.hist.length")
    res['A_cards'] = t.eval("document.querySelectorAll('#histList .histItem').length")
    res['A_checkboxes'] = t.eval("document.querySelectorAll('#histList .histpick input[type=checkbox]').length")
    res['A_checkbox_h'] = t.eval("(()=>{const c=document.querySelector('#histList .histpick input');return c?c.getBoundingClientRect().height:null;})()")
    res['A_export_btn_before'] = t.eval("document.getElementById('histExportSel').textContent")
    res['A_export_btn_disabled_before'] = t.eval("document.getElementById('histExportSel').disabled")

    # ===== (ข) ติ๊ก 2 เกม → ไฮไลท์ + ปุ่ม (2) =====
    t.eval("(()=>{const cbs=document.querySelectorAll('#histList .histpick input');cbs[0].click();cbs[1].click();return true;})()")
    time.sleep(0.35)
    res['B_sel_size'] = t.eval("window.__chessDbg.histSel.length")
    res['B_sel_cards'] = t.eval("document.querySelectorAll('#histList .histItem.sel').length")
    res['B_border'] = t.eval("""(()=>{const el=document.querySelector('#histList .histItem.sel');if(!el)return null;
      const s=getComputedStyle(el);return JSON.stringify({w:s.borderTopWidth,c:s.borderTopColor,bs:s.boxShadow.slice(0,70),bg:s.backgroundImage.slice(0,110)});})()""")
    res['B_export_btn'] = t.eval("document.getElementById('histExportSel').textContent")
    res['B_export_disabled'] = t.eval("document.getElementById('histExportSel').disabled")
    res['B_copy_btn'] = t.eval("document.getElementById('histCopySel').textContent")
    t.shot(OUT + r"\shot-160-sel-th.png")

    # การเลือกคงอยู่เมื่อค้นหา/เรียงใหม่
    t.eval("(()=>{const s=document.getElementById('histSearch');s.value='Test';s.dispatchEvent(new Event('input'));return true;})()")
    time.sleep(0.2)
    t.eval("(()=>{const s=document.getElementById('histSort');s.value='name';s.dispatchEvent(new Event('change'));return true;})()")
    time.sleep(0.2)
    res['B_sel_after_filter_sort'] = t.eval("window.__chessDbg.histSel.length")
    res['B_sel_cards_after'] = t.eval("document.querySelectorAll('#histList .histItem.sel').length")
    t.eval("(()=>{const s=document.getElementById('histSearch');s.value='';s.dispatchEvent(new Event('input'));const z=document.getElementById('histSort');z.value='date_desc';z.dispatchEvent(new Event('change'));return true;})()")
    time.sleep(0.2)

    # ===== (ค) ส่งออก PGN ที่เลือก → นับ [Event] + นำกลับเข้านำเข้าได้ =====
    t.eval("(()=>{document.getElementById('histExportSel').click();return true;})()")
    time.sleep(0.5)
    pgn = t.eval("document.getElementById('histPgnOut').value")
    res['C_exported_event_count'] = pgn.count('[Event')
    res['C_exported_has_2'] = (pgn.count('[Event') == 2)
    res['C_exported_head'] = pgn[:80]
    # นำกลับเข้านำเข้า (ควรได้ +2 เกม)
    before = t.eval("window.__chessDbg.hist.length")
    t.eval("(()=>{document.getElementById('histPgn').value=%s;return true;})()" % j(pgn))
    t.click('#histImportBtn'); time.sleep(0.8)
    res['C_import_back_added'] = t.eval("window.__chessDbg.hist.length") - before
    # คัดลอกที่เลือก → เขียนลง histPgnOut เหมือนกัน
    t.eval("(()=>{document.getElementById('histCopySel').click();return true;})()")
    time.sleep(0.4)
    res['C_copy_event_count'] = t.eval("document.getElementById('histPgnOut').value").count('[Event')
    # คืนค่า: ลบประวัติ + นำเข้า 3 เกมใหม่เพื่อเทสต์ถัดไป
    t.eval("(()=>{window.__chessDbg;return true;})()")

    # ===== (ฬ) เลือกทั้งหมด / ล้างที่เลือก =====
    t.eval("(()=>{document.getElementById('histSelAll').click();return true;})()"); time.sleep(0.3)
    res['D_selall_n'] = t.eval("window.__chessDbg.histSel.length")
    res['D_selall_total'] = t.eval("window.__chessDbg.hist.length")
    res['D_selall_btn'] = t.eval("document.getElementById('histExportSel').textContent")
    t.eval("(()=>{document.getElementById('histSelNone').click();return true;})()"); time.sleep(0.3)
    res['D_selnone_n'] = t.eval("window.__chessDbg.histSel.length")
    res['D_selnone_disabled'] = t.eval("document.getElementById('histExportSel').disabled")

    # ===== (ฬ) ลบประวัติทั้งหมด =====
    opendel()
    res['E_box_display'] = t.eval("getComputedStyle(document.getElementById('confirmDelAll')).display")
    res['E_box_rect'] = t.eval("(()=>{const r=document.getElementById('confirmDelAll').getBoundingClientRect();return JSON.stringify({l:Math.round(r.left),r:Math.round(r.right),w:Math.round(r.width),vw:window.innerWidth});})()")
    res['E_styles'] = t.eval("""(()=>{const b=document.getElementById('confirmDelAll');const s=getComputedStyle(b);
      const y=getComputedStyle(document.getElementById('bDelAllYes'));const n=getComputedStyle(document.getElementById('bDelAllNo'));
      return JSON.stringify({border:s.borderTopColor,bw:s.borderTopWidth,yes_bg:y.backgroundImage.slice(0,60),yes_bc:y.borderTopColor,
        no_bg:n.backgroundImage.slice(0,60),no_bc:n.borderTopColor,msg:document.getElementById('confirmDelAllMsg').textContent});})()""")
    t.shot(OUT + r"\shot-160-delbox-th.png")
    # Esc = ไม่ลบ
    n_before = t.eval("window.__chessDbg.hist.length")
    key("Escape", "Escape", 27)
    res['E_esc_closed'] = t.eval("getComputedStyle(document.getElementById('confirmDelAll')).display")
    res['E_esc_hist_unchanged'] = (t.eval("window.__chessDbg.hist.length") == n_before)
    # Enter = ลบจริง
    opendel()
    key("Enter", "Enter", 13)
    time.sleep(0.5)
    res['E_enter_hist_len'] = t.eval("window.__chessDbg.hist.length")
    res['E_enter_sel_len'] = t.eval("window.__chessDbg.histSel.length")
    res['E_enter_box_closed'] = t.eval("getComputedStyle(document.getElementById('confirmDelAll')).display")
    res['E_enter_count_text'] = t.eval("document.getElementById('histCount').textContent")
    res['E_toast'] = t.eval("document.getElementById('toast').textContent")

    # ===== (ฉ) ปุ่มไทยเหลือง 2 ธีม =====
    def langcolor():
        return t.eval("""(()=>{const b=document.querySelector('.lang.on[data-lang="th"]');if(!b)return null;const s=getComputedStyle(b);
          return JSON.stringify({cls:b.className,bg:s.backgroundColor,bgi:s.backgroundImage.slice(0,70),col:s.color});})()""")
    t.eval("(()=>{const b=document.querySelector('.lang[data-lang=\"th\"]');b.click();return true;})()"); time.sleep(0.3)
    res['F_nibble'] = langcolor()
    res['F_nibble_themeclass'] = t.eval("document.body.className")
    # สลับธีม white → ยังเหลือง
    t.eval("localStorage.setItem('chessTheme','white')"); fresh(clear_ls=False)
    t.eval("(()=>{const b=document.querySelector('.lang[data-lang=\"th\"]');b.click();return true;})()"); time.sleep(0.3)
    res['F_white'] = langcolor()
    res['F_white_themeclass'] = t.eval("document.body.className")
    t.eval("localStorage.setItem('chessTheme','nibble')")

    # ===== (ช) 390px TH/EN ไม่ล้น + EN ไม่มีอักษรไทย =====
    fresh(clear_ls=False)
    t.click('#bHist'); time.sleep(0.4)
    import3()
    t.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=1, mobile=True)
    time.sleep(0.4)
    res['G_390_th'] = t.eval("""(()=>{const h=document.getElementById('histView');const box=document.getElementById('confirmDelAll');
      document.getElementById('histDelAll').click();
      const r=box.getBoundingClientRect();
      return JSON.stringify({sw:document.documentElement.scrollWidth, vw:window.innerWidth, box_l:Math.round(r.left), box_r:Math.round(r.right)});})()""")
    t.shot(OUT + r"\shot-160-390-th.png")
    key("Escape", "Escape", 27)
    # สลับ EN
    t.eval("(()=>{const b=document.querySelector('.lang[data-lang=\"en\"]');b.click();return true;})()"); time.sleep(0.5)
    t.eval("(()=>{document.getElementById('histDelAll').click();return true;})()"); time.sleep(0.3)
    res['G_390_en'] = t.eval("""(()=>{const box=document.getElementById('confirmDelAll');const r=box.getBoundingClientRect();
      return JSON.stringify({sw:document.documentElement.scrollWidth, vw:window.innerWidth, box_l:Math.round(r.left), box_r:Math.round(r.right)});})()""")
    res['G_en_export_btn'] = t.eval("document.getElementById('histExportSel').textContent")
    res['G_en_delall_btn'] = t.eval("document.getElementById('histDelAll').textContent")
    res['G_en_msg'] = t.eval("document.getElementById('confirmDelAllMsg').textContent")
    res['G_en_thai_in_hist'] = t.eval("(()=>{const s=document.getElementById('histView').innerText;const m=s.match(/[\\u0E00-\\u0E7F]/g);return m?m.join(''):'';})()")
    t.shot(OUT + r"\shot-160-390-en.png")
    key("Escape", "Escape", 27)
    t.cmd("Emulation.clearDeviceMetricsOverride")

    res['errcap'] = t.eval("window.__errcap")
print(j(res))
